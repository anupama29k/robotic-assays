"""
BioInterface — Auto-generated Protocol
Assay    : HTS_006 — Caspase 3/7 apoptosis assay
Field    : Drug Discovery / HTS
Workbench: WB2
Robot min: 30 | Total hours: 26
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
    "A1": {"slot": 1, "description": "Compound dilution plate (HTS_001 output)"},
    "B1": {"slot": 7, "description": "96-well white TC-treated plate (cells)"},
    "C1": {"slot": 13, "description": "Caspase-Glo 3/7 reagent (Promega, reconstituted)"},
    "E1": {"slot": 25, "description": "Biological waste + bleach container"},
    "F1": {"slot": 31, "description": "Staurosporine positive control (1 µM in complete medium)"},
    "F2": {"slot": 38, "description": "DMSO vehicle control"},
    "G1": {"slot": 37, "description": "Luminescence plate reader (no filter)"},
    "H1": {"slot": 43, "description": "CO₂ incubator (37°C, 5%)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "positive_control_fold_induction": "≥ 10-fold caspase induction vs vehicle (staurosporine 1 µM)",
    "vehicle_control_cv": "≤ 15% CV",
    "z_factor": "Z' ≥ 0.5 between staurosporine and DMSO controls",
    "hit_threshold": "≥ 2-fold caspase induction vs vehicle control",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_006(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Caspase 3/7 apoptosis assay

    Purpose    : Measure caspase 3/7 activity as a quantitative marker of apoptosis induction in compound-treated cells using a luminescent substrate.
    Workbench  : WB2
    Robot time : 30 minutes active
    Total time : 26 hours
    Throughput : 80 samples/run
    Difficulty : medium
    AutoMATE 96: head=5-200uL, tagged_steps=4/15
    Regulatory : ICH S7A
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_006: Caspase 3/7 apoptosis assay")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [WAIT]
    # "Seed target cells at 5,000 cells/well in 96-well white TC plate at position B1 in 100 µL complete medium — incubate 24 hours at 37°C, 5% CO₂."
    print(f"[{run_id}] Step 1: waiting 86400s — robot free for other tasks")
    await asyncio.sleep(86400)
    log.append({"step": 1, "action": "WAIT", "duration_seconds": 86400, "status": "complete"})

    # ── STEP 2 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Confirm cell viability and morphology under microscope before adding compounds."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm cell viability and morphology under microscope before adding compounds.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 2, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 3 ── [LIQUID_HANDLER]
    # "Add 50 µL compound dilutions from position A1 to cell plate — incubate 18–24 hours at 37°C, 5% CO₂; log start time."
    await lh.dispense(
        resource=DECK_LAYOUT["A1"]["slot"],
        vols=[50] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 3, "action": "LIQUID_HANDLER", "volume_uL": 50, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 4 ── [TRANSPORT]
    # "Remove plates from incubator at position H1 and equilibrate to room temperature for 30 minutes."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["H1"]["slot"],
    )
    log.append({"step": 4, "action": "TRANSPORT", "from": "input_rack", "to": "H1", "status": "complete"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Add 100 µL Caspase-Glo 3/7 reagent from position C1 (one volume per volume of cell medium) to all wells."
    await lh.dispense(
        resource=DECK_LAYOUT["C1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 6 ── [LIQUID_HANDLER]
    # "Mix contents by pipetting 5 times — do not use plate shaker (causes foaming that disrupts luminescence)."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 6, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 7 ── [WAIT]
    # "Incubate at room temperature for 30 minutes in the dark — log start time."
    print(f"[{run_id}] Step 7: waiting 1800s — robot free for other tasks")
    await asyncio.sleep(1800)
    log.append({"step": 7, "action": "WAIT", "duration_seconds": 1800, "status": "complete"})

    # ── STEP 8 ── [TRANSPORT]
    # "Transfer plate to luminescence reader at position G1 — read luminescence (no filter, integration time 0.5–1 s per well)."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 8, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 9 ── [OTHER]
    # "Include staurosporine positive control (known apoptosis inducer, 1 µM, position F1) and DMSO vehicle control (column 12)."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [OTHER]
    # "Calculate fold-induction of caspase activity: RLU_sample / RLU_vehicle_control."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [OTHER]
    # "Flag compounds showing ≥ 2-fold caspase induction as apoptosis inducers."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Cross-reference caspase hits with LDH cytotoxicity data from HTS_005 — distinguish apoptotic from necrotic cell death before advancing hits."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Cross-reference caspase hits with LDH cytotoxicity data from HTS_005 — distinguish apoptotic from necrotic cell death before advancing hits.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 12, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Export luminescence data, fold-induction values, and hit list to run file."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Decontaminate plates with 10% bleach — log decontamination."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Archive run file and flag any wells with background luminescence > 2× blank."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_006",
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
        result = await run_hts_006(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
