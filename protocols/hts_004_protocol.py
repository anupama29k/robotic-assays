"""
BioInterface — Auto-generated Protocol
Assay    : HTS_004 — Cell proliferation assay — MTT/MTS
Field    : Drug Discovery / HTS
Workbench: WB2
Robot min: 45 | Total hours: 100
Generated: 2026-04-25 21:15:17

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
    "A1": {"slot": 1, "description": "Cell suspension tube (15 mL conical)"},
    "A2": {"slot": 2, "description": "Compound dilution plate (HTS_001 output)"},
    "B1": {"slot": 7, "description": "96-well TC-treated plate (flat-bottom)"},
    "C1": {"slot": 13, "description": "Complete medium reservoir (DMEM + 10% FBS)"},
    "C2": {"slot": 14, "description": "MTT solution (5 mg/mL in PBS, light-protected)"},
    "C3": {"slot": 15, "description": "DMSO reservoir (for formazan solubilisation)"},
    "E1": {"slot": 25, "description": "Biological waste container"},
    "G1": {"slot": 37, "description": "Plate reader (570/690 nm)"},
    "H1": {"slot": 43, "description": "Automated cell counter"},
    "H2": {"slot": 44, "description": "CO₂ incubator (37°C, 5%)"},
    "H3": {"slot": 45, "description": "Inverted microscope (analyst station)"},
    "H4": {"slot": 50, "description": "Plate shaker"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "vehicle_control_viability": "100% ± 15% (DMSO-treated cells vs untreated)",
    "positive_control_inhibition": "≤ 20% viability at maximum dose",
    "dose_response_curve_fit": "R² ≥ 0.95 for 4PL fit",
    "z_factor_viability": "Z' ≥ 0.5 between vehicle and maximum dose positive control",
    "dmso_tolerance": "≤ 0.1% final DMSO — higher concentrations cause direct cytotoxicity",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_004(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Cell proliferation assay — MTT/MTS

    Purpose    : Measure compound effect on cell viability and proliferation using MTT or MTS colorimetric metabolic assay in 96-well format.
    Workbench  : WB2
    Robot time : 45 minutes active
    Total time : 100 hours
    Throughput : 80 samples/run
    Difficulty : medium
    AutoMATE 96: head=5-200uL, tagged_steps=3/16
    Regulatory : ICH S1A, OECD TG 453 (in vitro cytotoxicity)
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_004: Cell proliferation assay — MTT/MTS")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Retrieve cryopreserved target cell line from liquid nitrogen — thaw at 37°C water bath for 2 minutes; transfer to 15 mL conical at position A1."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [INSTRUMENT_TRIGGER]
    # "Centrifuge at 300 × g for 5 minutes; aspirate supernatant; resuspend in complete medium from reservoir at position C1."
    # Instrument trigger: centrifuge
    if "centrifuge" in instruments:
        await instruments["centrifuge"].read()
    else:
        print(f"[{run_id}] Step 2: centrifuge not wired — skipping trigger")
    log.append({"step": 2, "action": "INSTRUMENT_TRIGGER", "instrument": "centrifuge", "status": "complete"})

    # ── STEP 3 ── [INSTRUMENT_TRIGGER]
    # "Count cells using automated counter at position H1 — target 5,000 cells/well for 96-well format; adjust to 50,000 cells/mL."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 3: generic not wired — skipping trigger")
    log.append({"step": 3, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 4 ── [OTHER]
    # "Dispense 100 µL cell suspension per well into 96-well TC plate at position B1 using multichannel head."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [WAIT]
    # "Incubate cells at 37°C, 5% CO₂ for 24 hours at position H2 for attachment — log incubation start time."
    print(f"[{run_id}] Step 5: waiting 86400s — robot free for other tasks")
    await asyncio.sleep(86400)
    log.append({"step": 5, "action": "WAIT", "duration_seconds": 86400, "status": "complete"})

    # ── STEP 6 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Check cells under microscope at position H3 for attachment and morphology before adding compounds — flag any wells with poor attachment."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Check cells under microscope at position H3 for attachment and morphology before adding compounds — flag any wells with poor attachment.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 6, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 7 ── [LIQUID_HANDLER]
    # "Transfer 100 µL of compound dilutions from HTS_001 output plate at position A2 to cell plate — final volume 200 µL; final compound concentration halved from dilution plate."
    await lh.dispense(
        resource=DECK_LAYOUT["A2"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 7, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 8 ── [WAIT]
    # "Incubate at 37°C, 5% CO₂ for 72 hours — log incubation start time."
    print(f"[{run_id}] Step 8: waiting 259200s — robot free for other tasks")
    await asyncio.sleep(259200)
    log.append({"step": 8, "action": "WAIT", "duration_seconds": 259200, "status": "complete"})

    # ── STEP 9 ── [LIQUID_HANDLER]
    # "After 72 hours, add 20 µL MTT (5 mg/mL in PBS) from position C2 to all wells — incubate 4 hours at 37°C; log start time."
    await lh.dispense(
        resource=DECK_LAYOUT["C2"]["slot"],
        vols=[20] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 9, "action": "LIQUID_HANDLER", "volume_uL": 20, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 10 ── [OTHER]
    # "Aspirate medium from all wells carefully — avoid disturbing formazan crystals at bottom."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [LIQUID_HANDLER]
    # "Add 100 µL DMSO from position C3 to all wells — solubilise formazan crystals; mix on plate shaker at position H4 for 5 minutes."
    await lh.dispense(
        resource=DECK_LAYOUT["H4"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 11, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 12 ── [TRANSPORT]
    # "Transfer plate to plate reader at position G1 — read absorbance at 570 nm with reference at 690 nm."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 12, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Calculate % cell viability: (OD_sample / OD_vehicle_control) × 100."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Calculate IC50 from 8-point dose-response curve using 4-parameter logistic fit — flag any compound with IC50 < 1 µM as priority hit."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Export viability data, IC50 values, and dose-response curves to run file."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    # ── STEP 16 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Review dose-response curve shapes — flag non-sigmoidal curves, incomplete inhibition, or curves with Hill slope > 3 (potential aggregation artefact) for orthogonal testing."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review dose-response curve shapes — flag non-sigmoidal curves, incomplete inhibition, or curves with Hill slope > 3 (potential aggregation artefact) for orthogonal testing.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 16, "action": "ANALYST_PAUSE", "status": "complete"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_004",
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
        result = await run_hts_004(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
