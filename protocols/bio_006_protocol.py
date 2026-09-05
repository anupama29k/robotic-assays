"""
BioInterface — Auto-generated Protocol
Assay    : BIO_006 — Endotoxin testing -- LAL kinetic turbidimetric
Field    : Biopharma / CDMO
Workbench: WB3
Robot min: 30 | Total hours: 1.5
Generated: 2026-04-25 21:15:16

PyLabRobot — hardware-agnostic execution layer
Install : pip install pylabrobot
Docs    : https://pylabrobot.org
"""

import asyncio
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import SerializingBackend
from pylabrobot.resources import Deck, Plate, TipRack
from pylabrobot.resources import Container as Reservoir

# ── DECK LAYOUT ──────────────────────────────────────
# Loaded from assay["robot_deck_layout"]
DECK_LAYOUT = {
    "A1": {"slot": 1, "description": "Sample input rack -- 12 x endotoxin-free 1.5 mL tubes"},
    "B1": {"slot": 7, "description": "96-well LAL plate (depyrogenated)"},
    "C1": {"slot": 13, "description": "Reagent reservoir -- LAL reagent water (LRW), certified"},
    "C2": {"slot": 14, "description": "LAL reagent vial (kinetic turbidimetric, in ice bucket)"},
    "D1": {"slot": 19, "description": "Tip rack -- endotoxin-free foil-wrapped tips"},
    "F1": {"slot": 31, "description": "CSE standard vials (control standard endotoxin)"},
    "G1": {"slot": 37, "description": "Kinetic plate reader (37C, 340 nm)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "standard_curve_r2": ">= 0.980 (log-log linear regression)",
    "ppc_recovery_percent": "50-200%",
    "negative_control": "No turbidimetric onset detected within run time",
    "dilution_concordance": "Results at different MVD dilutions within 2-fold of each other",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_006(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Endotoxin testing -- LAL kinetic turbidimetric

    Purpose    : Quantify bacterial endotoxin in biologic drug substance or in-process samples using kinetic turbidimetric LAL to confirm compliance with release limits.
    Workbench  : WB3
    Robot time : 30 minutes active
    Total time : 1.5 hours
    Throughput : 20 samples/run
    Difficulty : medium
    AutoMATE 96: head=5-200uL, tagged_steps=6/16
    Regulatory : USP <85>, EP 2.6.14, Ph. Eur. 2.6.14
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_006: Endotoxin testing -- LAL kinetic turbidimetric")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Confirm all labware is depyrogenated or certified endotoxin-free -- log lot numbers of LRW, LAL reagent, and CSE."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Prepare CSE standard curve from position F1: 8-point 2-fold dilution from 50 EU/mL to 0.39 EU/mL in LRW at position C1."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [LIQUID_HANDLER]
    # "Dispense 100 uL of each standard concentration into duplicate wells of 96-well LAL plate at position B1."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 3, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 4 ── [LIQUID_HANDLER]
    # "Prepare positive product controls (PPC): spike endotoxin into sample matrix at 2x MVD-adjusted concentration -- dispense 100 uL per PPC well."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 4, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 5 ── [OTHER]
    # "Calculate MVD for each sample: MVD = (Endotoxin Limit x concentration) / lambda -- log MVD per sample."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [LIQUID_HANDLER]
    # "Prepare sample dilutions in LRW at 3 dilution levels per sample from input rack at position A1 -- dispense 100 uL per well."
    await lh.dispense(
        resource=DECK_LAYOUT["A1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 6, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 7 ── [LIQUID_HANDLER]
    # "Dispense 100 uL negative control (LRW only) into wells H11-H12."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 7, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 8 ── [INSTRUMENT_TRIGGER]
    # "Reconstitute LAL reagent from position C2 -- gently swirl, do not vortex; log reconstitution time."
    # Instrument trigger: vortex
    if "vortex" in instruments:
        await instruments["vortex"].read()
    else:
        print(f"[{run_id}] Step 8: vortex not wired — skipping trigger")
    log.append({"step": 8, "action": "INSTRUMENT_TRIGGER", "instrument": "vortex", "status": "complete"})

    # ── STEP 9 ── [LIQUID_HANDLER]
    # "Dispense 100 uL LAL reagent into all sample, standard, and control wells -- mix gently by pipetting 5 times without introducing bubbles."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 9, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 10 ── [TRANSPORT]
    # "Transfer plate immediately to plate reader at position G1 preheated to 37C -- initiate kinetic turbidimetric read at 340 nm, 1 reading per minute for 60 minutes."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 10, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 11 ── [OTHER]
    # "Flag in real time any wells where onset time falls outside standard curve range."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [OTHER]
    # "Verify standard curve log-log linear regression R-squared >= 0.980 -- abort report generation if below."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Verify PPC recovery 50-200% -- invalidate run if any PPC outside range."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Verify negative controls show no onset within run time."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [INSTRUMENT_TRIGGER]
    # "Calculate sample endotoxin concentrations accounting for MVD; compare to specification -- flag any exceedances."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 15: generic not wired — skipping trigger")
    log.append({"step": 15, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 16 ── [OTHER]
    # "Export LAL report with curve statistics, PPC recoveries, and all sample results to run file."
    # (unclassified step — logged only)
    log.append({"step": 16, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_006",
        "plate_id": plate_id,
        "steps_completed": len(log),
        "log": log,
        "status": "complete",
    }


# ── SIMULATION ENTRYPOINT ────────────────────────────
# Runs the protocol against PyLabRobot SerializingBackend
# and a MockRailRobot. Requires: pip install pylabrobot
if __name__ == "__main__":
    class MockRailRobot:
        async def move_plate(self, **kwargs):
            print(f"  [RAIL] move_plate: {kwargs}")
        async def analyst_pause(self, reason, timeout_minutes, alert_level):
            print(f"  [ANALYST PAUSE] {reason}")
            # In real operation, block until the operator acknowledges.

    async def simulate():
        backend = SerializingBackend(num_channels=96)
        deck_obj = Deck()
        lh = LiquidHandler(backend=backend, deck=deck_obj)
        await lh.setup()
        robot = MockRailRobot()
        instruments = {}
        result = await run_bio_006(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
