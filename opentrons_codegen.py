#!/usr/bin/env python3
"""Opentrons OT-2 protocol generator for the Robotic Assays library.

Compiles library assays into real Opentrons Python Protocol API v2 protocols
(load_labware, load_instrument, pick_up_tip, aspirate, dispense, ...) that run
in `opentrons_simulate` and on an OT-2, plus a Results Bridge plate map.

    python3 opentrons_codegen.py            # write every recipe to protocols/opentrons/
    python3 opentrons_codegen.py --check    # exit 1 if any committed file is stale

WHY A PLANNER, NOT A TEMPLATE
    The earlier generator (rail_protocol_generator.py) turned each prose step
    into one call. That produced code with no tips, no aspirations and wrong
    targets. Here every assay is a *recipe*: plate map, reagents and liquid
    moves written once against a Plan object. The Plan emits the Opentrons code
    AND checks, at generation time, the things a simulator does not:

      * every well stays within its labware's rated volume
      * every reservoir is filled within capacity, including dead volume;
        wash buffer and waste trigger a refill / empty pause instead of overflowing
      * tip racks are not over-drawn
      * every volume is within the pipette's range
      * the volumes the recipe uses still appear in the library's robot_steps,
        so a library edit cannot silently diverge from the code

    `opentrons_simulate` then checks the code itself. validate_library.py runs both.

SCOPE
    Research use only. The OT-2 is not 21 CFR Part 11 compliant; a protocol that
    passes simulation is *verified code*, not a validated method. Liquid classes,
    residual volumes after aspiration and assay performance must still be
    measured on the client's robot with the client's reagents.
"""
import argparse
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "protocols", "opentrons")
API_LEVEL = "2.20"

LABWARE_CAPACITY_UL = {
    "corning_96_wellplate_360ul_flat": 360,
    "nest_96_wellplate_2ml_deep": 2000,
    "nest_12_reservoir_15ml": 15000,
    "nest_1_reservoir_195ml": 195000,
    "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap": 1500,
}
# Conservative unusable volume left in a reservoir well when a multichannel
# can no longer aspirate cleanly. Measure on the client's deck and update.
DEAD_VOLUME_UL = {
    "nest_12_reservoir_15ml": 1000,
    "nest_1_reservoir_195ml": 10000,
    "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap": 50,
    "nest_96_wellplate_2ml_deep": 30,
}
PIPETTE_RANGE_UL = {"p300_single_gen2": (20, 300), "p300_multi_gen2": (20, 300)}
TIP_MAX_UL = 300
ROWS = "ABCDEFGH"


class PlanError(Exception):
    pass


class Plan:
    """Accumulates Opentrons code and enforces volume / tip / capacity rules."""

    def __init__(self, assay, protocol_name, description):
        self.assay = assay
        self.protocol_name = protocol_name
        self.description = description
        self.labware = {}          # var -> (load_name, slot, label)
        self.pipettes = {}         # var -> (model, mount, [tiprack vars])
        self.body = []             # emitted code lines (inside run())
        self.well_vol = defaultdict(float)   # (var, well) -> µL
        self.pools = {}            # name -> pool dict
        self.tips_used = defaultdict(int)    # tiprack var -> tips consumed
        self.fixed_tip_columns = {}          # tiprack var reserved for return_tip reuse
        self.used_volumes = set()
        self.plate_map = {}
        self.operator_notes = []

    # ---- deck ------------------------------------------------------------
    def load(self, var, load_name, slot, label):
        self.labware[var] = (load_name, slot, label)

    def pipette(self, var, model, mount, tipracks):
        self.pipettes[var] = (model, mount, tipracks)

    def pool(self, name, var, wells, refill_pause=None):
        """A reagent supply. `wells` are filled in order; the plan records how
        much each must be filled with. refill_pause=True lets a single-well
        bulk reservoir be refilled mid-run instead of over-filled."""
        load_name = self.labware[var][0]
        self.pools[name] = {
            "var": var, "wells": list(wells), "idx": 0, "load_name": load_name,
            "cap": LABWARE_CAPACITY_UL[load_name],
            "dead": DEAD_VOLUME_UL.get(load_name, 0),
            "draw": defaultdict(float), "refill_pause": refill_pause,
            "refills": 0, "peak": defaultdict(float),
        }

    def waste(self, name, var):
        load_name = self.labware[var][0]
        self.pools[name] = {
            "var": var, "wells": ["A1"], "idx": 0, "load_name": load_name,
            "cap": LABWARE_CAPACITY_UL[load_name], "dead": 0, "waste": True,
            "fill": 0.0, "empties": 0,
        }

    # ---- checks ----------------------------------------------------------
    def _check_pipette(self, pip, vol):
        lo, hi = PIPETTE_RANGE_UL[self.pipettes[pip][0]]
        if not lo <= vol <= hi:
            raise PlanError(f"{vol} uL outside {self.pipettes[pip][0]} range {lo}-{hi}")
        self.used_volumes.add(vol)

    def _add(self, var, well, vol):
        key = (var, well)
        self.well_vol[key] += vol
        cap = LABWARE_CAPACITY_UL[self.labware[var][0]]
        if self.well_vol[key] > cap:
            raise PlanError(f"{var} {well} would hold {self.well_vol[key]:.0f} uL > {cap} uL")

    def _take(self, var, well, vol):
        key = (var, well)
        self.well_vol[key] -= vol
        if self.well_vol[key] < -1e-6:
            raise PlanError(f"{var} {well}: aspirating {vol} uL from {self.well_vol[key] + vol:.0f} uL")

    def _tip(self, pip, n=1):
        racks = self.pipettes[pip][2]
        self.tips_used[tuple(racks)] += n
        if self.tips_used[tuple(racks)] > 96 * len(racks):
            raise PlanError(f"{pip} needs more than {96 * len(racks)} tips from {racks}")

    def _draw(self, pool_name, vol):
        """Reserve `vol` from a pool; returns the code expression for its well."""
        p = self.pools[pool_name]
        usable = p["cap"] - p["dead"]
        while True:
            well = p["wells"][p["idx"]]
            if p["draw"][well] + vol <= usable:
                p["draw"][well] += vol
                p["peak"][well] = max(p["peak"][well], p["draw"][well])
                return f'{p["var"]}["{well}"]'
            if p["idx"] + 1 < len(p["wells"]):
                p["idx"] += 1
                continue
            if p["refill_pause"]:
                self.comment(f"{pool_name}: reservoir low")
                self.pause(f"Refill {pool_name} ({self.labware[p['var']][2]}) to "
                           f"{p['cap'] / 1000:.0f} mL (full), then resume.")
                p["refills"] += 1
                p["draw"][well] = 0.0
                continue
            raise PlanError(f"pool {pool_name!r} exhausted; add wells")

    def _waste(self, name, vol):
        w = self.pools[name]
        if w["fill"] + vol > w["cap"] * 0.9:   # keep 10% headroom against splashing
            self.pause(f"Empty the liquid waste reservoir ({self.labware[w['var']][2]}) "
                       f"and return it to the deck, then resume.")
            w["fill"] = 0.0
            w["empties"] += 1
        w["fill"] += vol
        return f'{w["var"]}["A1"]'

    # ---- emitted primitives ---------------------------------------------
    def emit(self, line=""):
        self.body.append(line)

    def comment(self, text):
        self.emit(f"protocol.comment({text!r})")

    def pause(self, text):
        self.emit(f"protocol.pause({text!r})")

    def delay(self, minutes, why):
        self.emit(f"protocol.delay(minutes={minutes}, msg={why!r})")

    def add_reagent_to_columns(self, pip, pool_name, dest_var, columns, vol):
        """Multichannel: one tip column, aspirate from the pool, dispense at the
        top of each destination column (no contact, so the tips can be reused)."""
        self._check_pipette(pip, vol)
        self._tip(pip, 8)
        self.emit(f"{pip}.pick_up_tip()")
        for col in columns:
            src = self._draw(pool_name, vol * 8)
            for r in ROWS:
                self._add(dest_var, f"{r}{col}", vol)
            self.emit(f"{pip}.aspirate({vol}, {src})")
            self.emit(f'{pip}.dispense({vol}, {dest_var}["A{col}"].top(-1))')
            self.emit(f'{pip}.blow_out({dest_var}["A{col}"].top())')
        self.emit(f"{pip}.drop_tip()")

    def remove_from_columns(self, pip, src_var, columns, vol, waste_name, tiprack_var):
        """Multichannel: aspirate each column's liquid to waste with that column's
        dedicated tips from `tiprack_var`, returned and reused for later removals
        of the same column only (same wells -> no cross-column carryover)."""
        self._check_pipette(pip, vol)
        self.fixed_tip_columns[tiprack_var] = True
        self.emit(f"{pip}.flow_rate.aspirate = 50")
        for col in columns:
            for r in ROWS:
                self._take(src_var, f"{r}{col}", vol)
            dst = self._waste(waste_name, vol * 8)
            self.emit(f'{pip}.pick_up_tip({tiprack_var}["A{col}"])')
            self.emit(f'{pip}.aspirate({vol}, {src_var}["A{col}"].bottom(0.5))')
            self.emit(f"{pip}.dispense({vol}, {dst}.top())")
            self.emit(f"{pip}.blow_out({dst}.top())")
            self.emit(f"{pip}.return_tip()")
        self.emit(f"{pip}.flow_rate.aspirate = 92.86")

    def _reserve(self, waste_name, waste_vol, pool_name=None, pool_vol=0.0):
        """Before a block that empties wells, make sure waste and wash buffer can
        absorb the WHOLE block. Any empty/refill pause then happens while wells
        are still full; a pause between columns would let aspirated wells dry."""
        w = self.pools[waste_name]
        if waste_vol > w["cap"] * 0.9:
            raise PlanError(f"block needs {waste_vol / 1000:.0f} mL waste; reservoir too small")
        if w["fill"] + waste_vol > w["cap"] * 0.9:
            self.pause(f"Empty the liquid waste reservoir ({self.labware[w['var']][2]}) "
                       f"and return it to the deck, then resume.")
            w["fill"] = 0.0
            w["empties"] += 1
        if pool_name:
            p = self.pools[pool_name]
            usable = p["cap"] - p["dead"]
            well = p["wells"][p["idx"]]
            if pool_vol > usable:
                raise PlanError(f"block needs {pool_vol / 1000:.0f} mL {pool_name}; reservoir too small")
            if p["draw"][well] + pool_vol > usable:
                if not p["refill_pause"]:
                    raise PlanError(f"pool {pool_name!r} cannot supply a {pool_vol / 1000:.0f} mL block")
                self.pause(f"Refill {pool_name} ({self.labware[p['var']][2]}) to "
                           f"{p['cap'] / 1000:.0f} mL (full), then resume.")
                p["refills"] += 1
                p["draw"][well] = 0.0

    def remove_then_wash(self, pip, plate_var, columns, liquid_vol, wash_vol, cycles,
                         wash_pool, waste_name, removal_rack):
        """Remove the current liquid, then wash. Capacity for the whole block is
        reserved first so the plate is never left part-emptied waiting on an operator."""
        n_wells = 8 * len(list(columns))
        self._reserve(waste_name, n_wells * (liquid_vol + wash_vol * cycles),
                      wash_pool, n_wells * wash_vol * cycles)
        self.remove_from_columns(pip, plate_var, columns, liquid_vol, waste_name, removal_rack)
        self.wash(pip, plate_var, columns, wash_vol, cycles, wash_pool, waste_name, removal_rack)

    def wash(self, pip, dest_var, columns, vol, cycles, wash_pool, waste_name, removal_rack):
        for i in range(cycles):
            self.comment(f"Wash cycle {i + 1}/{cycles}")
            self.add_reagent_to_columns(pip, wash_pool, dest_var, columns, vol)
            self.remove_from_columns(pip, dest_var, columns, vol, waste_name, removal_rack)

    def transfer_single(self, pip, src, dests, vol, mix_after=None, new_tip=True):
        """Single-channel transfer. `src` and each dest are (var, well).
        One aspiration per destination (no multi-dispense) for accuracy."""
        self._check_pipette(pip, vol)
        if new_tip:
            self._tip(pip)
            self.emit(f"{pip}.pick_up_tip()")
        for dvar, dwell in dests:
            self._take(*src, vol)
            self._add(dvar, dwell, vol)
            self.emit(f'{pip}.aspirate({vol}, {src[0]}["{src[1]}"])')
            self.emit(f'{pip}.dispense({vol}, {dvar}["{dwell}"])')
            if mix_after:
                n, mv = mix_after
                self.emit(f'{pip}.mix({n}, {mv}, {dvar}["{dwell}"])')
        if new_tip:
            self.emit(f"{pip}.drop_tip()")

    def dispense_from_pool_single(self, pip, pool_name, dests, vol):
        """Single-channel diluent dispense from a reservoir, one tip."""
        self._check_pipette(pip, vol)
        self._tip(pip)
        self.emit(f"{pip}.pick_up_tip()")
        for dvar, dwell in dests:
            src = self._draw(pool_name, vol)
            self._add(dvar, dwell, vol)
            self.emit(f"{pip}.aspirate({vol}, {src})")
            self.emit(f'{pip}.dispense({vol}, {dvar}["{dwell}"].top(-2))')
        self.emit(f"{pip}.drop_tip()")

    def transfer_column(self, pip, src_var, src_col, dests, vol, mix_before=None):
        """Multichannel column -> one or more columns, one tip column."""
        self._check_pipette(pip, vol)
        self._tip(pip, 8)
        self.emit(f"{pip}.pick_up_tip()")
        if mix_before:
            n, mv = mix_before
            self.emit(f'{pip}.mix({n}, {mv}, {src_var}["A{src_col}"])')
        for dvar, dcol in dests:
            for r in ROWS:
                self._take(src_var, f"{r}{src_col}", vol)
                self._add(dvar, f"{r}{dcol}", vol)
            self.emit(f'{pip}.aspirate({vol}, {src_var}["A{src_col}"])')
            self.emit(f'{pip}.dispense({vol}, {dvar}["A{dcol}"])')
            self.emit(f'{pip}.blow_out({dvar}["A{dcol}"].top())')
        self.emit(f"{pip}.drop_tip()")

    def seed(self, var, well, vol):
        """Liquid the operator places on the deck before the run."""
        self._add(var, well, vol)

    # ---- library drift guard --------------------------------------------
    def require_library_volumes(self, volumes):
        text = " ".join(self.assay.get("robot_steps", []))
        missing = [v for v in volumes if f"{v} uL" not in text and f"{v} µL" not in text]
        if missing:
            raise PlanError(
                f"{self.assay['assay_id']}: recipe volumes {missing} no longer appear in the "
                f"library robot_steps -- update the recipe or the library together")

    # ---- output ----------------------------------------------------------
    def fill_sheet(self):
        lines = []
        for name, p in self.pools.items():
            if p.get("waste"):
                lines.append(f"{name}: {self.labware[p['var']][2]} -- start empty "
                             f"(emptied {p['empties']}x mid-run)")
                continue
            for well in p["wells"]:
                if p["peak"].get(well):
                    fill = p["peak"][well] + p["dead"]
                    extra = f", refilled {p['refills']}x" if p["refills"] else ""
                    lines.append(f"{name}: slot {self.labware[p['var']][1]} {well} -> "
                                 f"{fill / 1000:.2f} mL (incl. {p['dead'] / 1000:.1f} mL dead{extra})")
        return lines

    def render(self, source_note):
        a = self.assay
        out = []
        out.append('"""')
        out.append(f"{a['assay_id']} -- {a['name']}")
        out.append("Opentrons OT-2 protocol generated by opentrons_codegen.py -- DO NOT EDIT BY HAND.")
        out.append("Regenerate with: python3 opentrons_codegen.py")
        out.append("")
        out.append("Research use only. Passing opentrons_simulate verifies the code, not the method:")
        out.append("liquid classes, residual volumes and assay performance must be measured on the")
        out.append("client's robot. The OT-2 is not 21 CFR Part 11 compliant.")
        out.append("")
        out.append(f"Regulatory references (library): {', '.join(a.get('regulatory', []))}")
        out.append("")
        out.append("DECK")
        for var, (ln, slot, label) in sorted(self.labware.items(), key=lambda kv: int(kv[1][1])):
            out.append(f"  slot {slot:>2}: {label} [{ln}]")
        out.append("")
        out.append("FILL BEFORE RUN (computed by the planner)")
        for line in self.fill_sheet():
            out.append(f"  {line}")
        out.append("")
        out.append("OPERATOR NOTES")
        for note in self.operator_notes:
            out.append(f"  - {note}")
        out.append("")
        out.append("LIBRARY RECONCILIATION")
        for note in source_note:
            out.append(f"  - {note}")
        out.append("")
        out.append("ACCEPTANCE CRITERIA (scored on instrument exports by Results Bridge, not by the robot)")
        for k, v in a.get("acceptance_criteria", {}).items():
            out.append(f"  {k}: {v}")
        out.append('"""')
        out.append("")
        out.append("metadata = {")
        out.append(f"    \"protocolName\": {self.protocol_name!r},")
        out.append(f"    \"author\": \"Robotic Assays library ({a['assay_id']})\",")
        out.append(f"    \"description\": {self.description!r},")
        out.append("}")
        out.append(f'requirements = {{"robotType": "OT-2", "apiLevel": "{API_LEVEL}"}}')
        out.append("")
        out.append("")
        out.append("def run(protocol):")
        for var, (ln, slot, label) in sorted(self.labware.items(), key=lambda kv: int(kv[1][1])):
            out.append(f"    {var} = protocol.load_labware({ln!r}, {slot}, {label!r})")
        for var, (model, mount, racks) in self.pipettes.items():
            out.append(f"    {var} = protocol.load_instrument({model!r}, {mount!r}, "
                       f"tip_racks=[{', '.join(racks)}])")
        out.append("")
        for line in self.body:
            out.append(f"    {line}" if line else "")
        out.append("")
        return "\n".join(out)


# ═══════════════════════════════════════════════════════════════════════
# Plate maps (Results Bridge format: {well: role})
# ═══════════════════════════════════════════════════════════════════════

def standards_and_duplicate_samples(n_samples):
    """Cols 1-2: 8-point standard in duplicate (H = 0 = blank).
    Cols 3-12: samples in duplicate, sample i -> row i%8 of col pair 3+2*(i//8)."""
    if n_samples > 40:
        raise PlanError("this layout holds at most 40 samples in duplicate")
    pm = {}
    for c in (1, 2):
        for i, r in enumerate(ROWS):
            pm[f"{r}{c}"] = "blank" if r == "H" else "standard"
    for i in range(n_samples):
        col = 3 + 2 * (i // 8)
        for c in (col, col + 1):
            pm[f"{ROWS[i % 8]}{c}"] = "sample"
    return pm


def sample_tube(i):
    """Sample i (0-39) -> (rack var, well) across two 24-tube racks."""
    rack = "samples_1" if i < 24 else "samples_2"
    j = i % 24
    return rack, f"{'ABCD'[j % 4]}{j // 4 + 1}"


# ═══════════════════════════════════════════════════════════════════════
# Recipes
# ═══════════════════════════════════════════════════════════════════════

def recipe_bio_002(assay):
    """BCA protein assay -- 40 samples in duplicate + 8-point standard in duplicate."""
    n = 40
    p = Plan(assay, "BIO_002 BCA protein concentration assay (OT-2)",
             "BSA standard series, 40 samples in duplicate, 200 uL working reagent")
    p.require_library_volumes([25, 200])

    p.load("plate", "corning_96_wellplate_360ul_flat", 1, "BCA assay plate (clear flat-bottom)")
    p.load("stds", "nest_96_wellplate_2ml_deep", 2, "Standard dilution plate")
    p.load("reagents", "nest_12_reservoir_15ml", 3, "Reagents: PBS A1, BCA WR A2-A3")
    p.load("samples_1", "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 4, "Samples 1-24")
    p.load("samples_2", "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 5,
           "Samples 25-40; BSA 2 mg/mL stock in D6")
    p.load("tips_s", "opentrons_96_tiprack_300ul", 7, "Tips, single-channel")
    p.load("tips_m", "opentrons_96_tiprack_300ul", 8, "Tips, multichannel")
    p.pipette("single", "p300_single_gen2", "left", ["tips_s"])
    p.pipette("multi", "p300_multi_gen2", "right", ["tips_m"])
    p.pool("PBS", "reagents", ["A1"])
    p.pool("BCA working reagent", "reagents", ["A2", "A3"])

    for i in range(n):
        p.seed(*sample_tube(i), 100)
    p.seed("samples_2", "D6", 400)
    p.plate_map = standards_and_duplicate_samples(n)

    p.comment("Standards: 2000 -> 31.25 ug/mL 2-fold (7 points) + 0 ug/mL blank, column 1 of slot 2")
    p.dispense_from_pool_single("single", "PBS", [("stds", f"{r}1") for r in "BCDEFGH"], 150)
    p.transfer_single("single", ("samples_2", "D6"), [("stds", "A1")], 300)
    for a, b in zip("ABCDEF", "BCDEFG"):
        p.transfer_single("single", ("stds", f"{a}1"), [("stds", f"{b}1")], 150, mix_after=(5, 100))
    # Equalise G1 to 150 uL so every standard well holds the same volume.
    p._tip("single")
    p._take("stds", "G1", 150)
    p.emit("single.pick_up_tip()")
    p.emit('single.aspirate(150, stds["G1"])')
    p.emit("single.drop_tip()")

    p.comment("Standards -> plate columns 1 and 2, 25 uL each")
    p.transfer_column("multi", "stds", 1, [("plate", 1), ("plate", 2)], 25, mix_before=(3, 100))

    p.comment("Samples -> duplicate wells, 25 uL each")
    for i in range(n):
        col = 3 + 2 * (i // 8)
        row = ROWS[i % 8]
        p.transfer_single("single", sample_tube(i), [("plate", f"{row}{col}"), ("plate", f"{row}{col + 1}")], 25)

    p.comment("BCA working reagent, 200 uL to all wells")
    p.add_reagent_to_columns("multi", "BCA working reagent", "plate", range(1, 13), 200)

    p.pause("Seal the plate, incubate 37 C for exactly 30 min, equilibrate 5 min to room "
            "temperature, read OD562. Upload the reader export to Results Bridge "
            "(assay PROT_002_bca_od562) with plate_maps/BIO_002_plate_map.json.")

    p.operator_notes = [
        "Prepare BCA working reagent 50:1 (A:B) off-deck immediately before the run and split "
        "between reservoir wells A2 and A3 at the volumes above.",
        "Load >= 100 uL of each sample; tube positions run A1, B1, C1, D1, A2 ... per rack.",
        "Check sample buffers for BCA interferents (DTT > 1 mM, beta-mercaptoethanol, "
        "EDTA > 10 mM) BEFORE the run -- the library's analyst check is moved forward so no "
        "reagent is spent on an invalid plate.",
    ]
    notes = [
        "Library lists 40 samples in duplicate + 8 standards in duplicate + 2 blanks (H11-H12) = 98 "
        "wells; this layout uses the 0 ug/mL standard (H1-H2) as the blank so it fits 96.",
        "Library says '8-point 2000 -> 31.25 ug/mL'; that range is 7 two-fold points. The 8th point "
        "is 0 ug/mL.",
        "Library mixes working reagent on deck in a 15 mL conical; 96 x 200 uL + 10% is ~21 mL, "
        "which exceeds the tube, and a 50:1 on-deck mix is imprecise. WR is premixed off-deck.",
        "Library steps 10-14 (blank subtraction, curve fit, interpolation, range flags, export) are "
        "data analysis, not robot actions; they are done on the reader export.",
        "Library criterion 'linear R2 >= 0.995' over 31-2000 ug/mL is usually not met by BCA, which "
        "is curvilinear across this range; consider a quadratic or 4PL fit.",
    ]
    return p, notes


def recipe_bio_005(assay):
    """Sandwich ELISA -- coat (day 1), block / samples / detection / read (day 2)."""
    n = 40
    p = Plan(assay, "BIO_005 Sandwich ELISA (OT-2)",
             "Coat, block, 8-point standard + 40 samples (1:3) in duplicate, HRP, TMB, stop")
    p.require_library_volumes([100, 300, 200])

    p.load("plate", "corning_96_wellplate_360ul_flat", 1, "ELISA plate (high-binding flat-bottom)")
    p.load("dil", "nest_96_wellplate_2ml_deep", 2, "Dilution plate")
    p.load("reagents", "nest_12_reservoir_15ml", 3,
           "Reagents: capture A1, block/diluent A2-A4, HRP A5, TMB A6, stop A7")
    p.load("samples_1", "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 4, "Samples 1-24")
    p.load("samples_2", "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 5,
           "Samples 25-40; top standard in D6")
    p.load("pbst", "nest_1_reservoir_195ml", 6, "PBST wash buffer")
    p.load("tips_s", "opentrons_96_tiprack_300ul", 7, "Tips, single-channel")
    p.load("tips_m", "opentrons_96_tiprack_300ul", 8, "Tips, multichannel reagents")
    p.load("waste_res", "nest_1_reservoir_195ml", 9, "Liquid waste")
    p.load("tips_rm", "opentrons_96_tiprack_300ul", 10, "Tips, per-column removal (reused)")
    p.load("tips_m2", "opentrons_96_tiprack_300ul", 11, "Tips, multichannel reagents (2)")
    p.pipette("single", "p300_single_gen2", "left", ["tips_s"])
    p.pipette("multi", "p300_multi_gen2", "right", ["tips_m", "tips_m2"])
    p.pool("capture antibody", "reagents", ["A1"])
    p.pool("blocking buffer", "reagents", ["A2", "A3", "A4"])
    p.pool("HRP detection antibody", "reagents", ["A5"])
    p.pool("TMB", "reagents", ["A6"])
    p.pool("stop solution", "reagents", ["A7"])
    p.pool("PBST", "pbst", ["A1"], refill_pause=True)
    p.waste("waste", "waste_res")

    for i in range(n):
        p.seed(*sample_tube(i), 150)
    p.seed("samples_2", "D6", 600)
    p.plate_map = standards_and_duplicate_samples(n)
    cols = range(1, 13)

    # ---- day 1 -----------------------------------------------------------
    p.comment("DAY 1 -- coat")
    p.add_reagent_to_columns("multi", "capture antibody", "plate", cols, 100)
    p.pause("Seal the plate and incubate overnight at 4 C (log start time and fridge temperature). "
            "Next day: return the unsealed plate to slot 1 and resume.")

    # ---- day 2 -----------------------------------------------------------
    p.comment("DAY 2 -- remove coat, wash x3")
    p.remove_then_wash("multi", "plate", cols, 100, 300, 3, "PBST", "waste", "tips_rm")

    p.comment("Block 200 uL; standards and sample dilutions are prepared during the block")
    p.add_reagent_to_columns("multi", "blocking buffer", "plate", cols, 200)

    p.comment("Standards: 8-point 2-fold in dilution plate column 1 (H1 = 0 = blank)")
    p.dispense_from_pool_single("single", "blocking buffer", [("dil", f"{r}1") for r in "BCDEFGH"], 250)
    p.transfer_single("single", ("samples_2", "D6"), [("dil", "A1")], 250)
    p.transfer_single("single", ("samples_2", "D6"), [("dil", "A1")], 250)
    for a, b in zip("ABCDEF", "BCDEFG"):
        p.transfer_single("single", ("dil", f"{a}1"), [("dil", f"{b}1")], 250, mix_after=(5, 200))
    p._tip("single")
    p._take("dil", "G1", 250)
    p.emit("single.pick_up_tip()")
    p.emit('single.aspirate(250, dil["G1"])')
    p.emit("single.drop_tip()")

    p.comment("Samples 1:3 in blocking buffer, dilution plate columns 3-7")
    p.add_reagent_to_columns("multi", "blocking buffer", "dil", range(3, 8), 200)
    for i in range(n):
        p.transfer_single("single", sample_tube(i), [("dil", f"{ROWS[i % 8]}{3 + i // 8}")], 100,
                          mix_after=(5, 200))
    p.delay(60, "Block >= 60 min at room temperature (dilution prep time adds to this)")

    p.remove_then_wash("multi", "plate", cols, 200, 300, 3, "PBST", "waste", "tips_rm")

    p.comment("Standards -> cols 1-2; samples -> duplicate column pairs; 100 uL")
    p.transfer_column("multi", "dil", 1, [("plate", 1), ("plate", 2)], 100, mix_before=(3, 200))
    for k in range(5):
        p.transfer_column("multi", "dil", 3 + k, [("plate", 3 + 2 * k), ("plate", 4 + 2 * k)], 100,
                          mix_before=(3, 200))
    p.delay(120, "Sample incubation 2 h at room temperature")

    p.remove_then_wash("multi", "plate", cols, 100, 300, 3, "PBST", "waste", "tips_rm")

    p.comment("HRP detection antibody 100 uL")
    p.add_reagent_to_columns("multi", "HRP detection antibody", "plate", cols, 100)
    p.delay(60, "Detection antibody 1 h at room temperature")
    p.remove_then_wash("multi", "plate", cols, 100, 300, 3, "PBST", "waste", "tips_rm")

    p.comment("TMB 100 uL -- columns 1->12; protect from light")
    p.add_reagent_to_columns("multi", "TMB", "plate", cols, 100)
    p.delay(10, "TMB development exactly 10 min (timed from first column)")
    p.comment("Stop solution 100 uL in the same column order as TMB")
    p.add_reagent_to_columns("multi", "stop solution", "plate", cols, 100)
    p.pause("Read OD450 with 620 nm reference within 30 min. Upload the reader export to Results "
            "Bridge (assay ELISA_001_tmb_endpoint) with plate_maps/BIO_005_plate_map.json.")

    p.operator_notes = [
        "Top standard (>= 600 uL) in slot 5 D6; >= 150 uL of each sample, positions A1, B1, C1, D1, A2 ...",
        "The OT-2 deck is open: dim the room lights or cover the plate during TMB development.",
        "Per-column removal tips (slot 10) are reused across removals of the SAME column only, "
        "so no liquid moves between columns. Replace that rack between runs.",
        "Residual volume left after each removal is not modelled; measure it during validation "
        "and adjust the aspirate height (bottom(0.5)) if wells are not emptied.",
        "Wash-buffer refill and waste-emptying pauses are inserted automatically, always BEFORE a "
        "remove-and-wash block so wells are never left part-emptied; the preceding incubation "
        "runs a few minutes long while you service the reservoirs.",
    ]
    notes = [
        "Library: 40 samples with '3-fold serial dilutions' do not fit one plate in duplicate "
        "alongside the standard curve; this recipe runs each sample at a single 1:3 dilution.",
        "Library step 'aspirate contents to liquid waste at E1' and 3-cycle washes are implemented "
        "on-deck with a 195 mL PBST reservoir (slot 6) and a 195 mL waste reservoir (slot 9).",
        "Library steps 18-20 (saturation flag, 4PL fit, out-of-range flag) are data analysis on "
        "the reader export, not robot actions.",
    ]
    return p, notes


RECIPES = {
    "BIO_002": recipe_bio_002,
    "BIO_005": recipe_bio_005,
}


# ═══════════════════════════════════════════════════════════════════════
# Driver
# ═══════════════════════════════════════════════════════════════════════

def library_entry(assay_id):
    sys.path.insert(0, HERE)
    import importlib, glob
    found = None
    for path in sorted(glob.glob(os.path.join(HERE, "field_*.py"))):
        mod = importlib.import_module(os.path.splitext(os.path.basename(path))[0])
        for attr in dir(mod):
            val = getattr(mod, attr)
            if attr.endswith("_ASSAYS") and isinstance(val, list):
                for e in val:
                    if e.get("assay_id") == assay_id:
                        found = e
    if not found:
        raise PlanError(f"{assay_id} not found in the library")
    return found


def output_paths(assay_id):
    base = assay_id.lower()
    return (os.path.join(OUT_DIR, f"{base}_ot2.py"),
            os.path.join(OUT_DIR, "plate_maps", f"{assay_id}_plate_map.json"))


def build(assay_id):
    """Return (protocol_source, plate_map_json) for one recipe. Raises PlanError."""
    plan, notes = RECIPES[assay_id](library_entry(assay_id))
    source = plan.render(notes)
    plate_map = json.dumps(dict(sorted(plan.plate_map.items(),
                                       key=lambda kv: (int(kv[0][1:]), kv[0][0]))), indent=2) + "\n"
    return source, plate_map


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="fail if committed files are stale")
    args = ap.parse_args(argv)
    stale = []
    for assay_id in RECIPES:
        source, plate_map = build(assay_id)
        proto_path, map_path = output_paths(assay_id)
        for path, content in ((proto_path, source), (map_path, plate_map)):
            current = open(path).read() if os.path.exists(path) else None
            if args.check:
                if current != content:
                    stale.append(os.path.relpath(path, HERE))
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as fh:
                    fh.write(content)
                print(f"wrote {os.path.relpath(path, HERE)}")
    if stale:
        print("stale generated files (run python3 opentrons_codegen.py):")
        for s in stale:
            print(f"  {s}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
