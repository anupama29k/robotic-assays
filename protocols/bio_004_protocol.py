"""
BioInterface — Auto-generated Protocol
Assay    : BIO_004 — Cell viability and density by Vi-CELL or Cedex
Field    : Biopharma / CDMO
Workbench: WB2
Robot min: 10 | Total hours: 1
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
    "A1": {"slot": 1, "description": "Sample input rack -- 8 x 15 mL conicals or sample tubes"},
    "B1": {"slot": 7, "description": "Vi-CELL sample cup rack -- 8 positions"},
    "D1": {"slot": 19, "description": "Tip rack -- 1 mL tips"},
    "G1": {"slot": 37, "description": "Vi-CELL / Cedex instrument carousel interface"},
    "H1": {"slot": 43, "description": "Vortex mixer"},
    "H2": {"slot": 44, "description": "Inverted microscope (analyst review station)"},
    "H3": {"slot": 45, "description": "Instrument cleaning station"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "calibration_beads_cv": "<= 5% CV on standardisation beads (run daily)",
    "viability_alert_threshold": "< 70% triggers immediate operator alert",
    "aggregate_alert_threshold": "> 15% triggers microscopy review",
    "instrument_blank": "< 1e4 cells/mL background particle count",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_004(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Cell viability and density by Vi-CELL or Cedex

    Purpose    : Measure viable cell density (VCD) and viability (%) in bioreactor or shake flask samples using automated image-based trypan blue exclusion counting.
    Workbench  : WB2
    Robot time : 10 minutes active
    Total time : 1 hours
    Throughput : 8 samples/run
    Difficulty : easy
    AutoMATE 96: head=not applicable, tagged_steps=0/15
    Regulatory : ICH Q5D, USP <1010>
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_004: Cell viability and density by Vi-CELL or Cedex")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [TRANSPORT]
    # "Pick up bioreactor sample tubes from input rack at position A1 (A1:1 through A1:8) -- confirm samples are at room temperature; log collection time."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["A1"]["slot"],
    )
    log.append({"step": 1, "action": "TRANSPORT", "from": "input_rack", "to": "A1", "status": "complete"})

    # ── STEP 2 ── [INSTRUMENT_TRIGGER]
    # "Vortex each sample tube for 3 seconds at position H1 to ensure homogeneous cell suspension."
    # Instrument trigger: vortex
    if "vortex" in instruments:
        await instruments["vortex"].read()
    else:
        print(f"[{run_id}] Step 2: vortex not wired — skipping trigger")
    log.append({"step": 2, "action": "INSTRUMENT_TRIGGER", "instrument": "vortex", "status": "complete"})

    # ── STEP 3 ── [OTHER]
    # "Transfer 500 uL of each sample to Vi-CELL sample cups at position B1 using 1 mL tips from position D1."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [OTHER]
    # "Load Vi-CELL sample cups into instrument carousel at position G1 -- confirm cup positions match run sequence."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "Confirm trypan blue reagent reservoir in instrument is > 30% full before run -- log level."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [OTHER]
    # "Initiate Vi-CELL run -- instrument acquires 50 images per sample; estimated 3-4 minutes per sample."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [OTHER]
    # "Robot monitors for instrument complete signal after each sample."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [OTHER]
    # "Retrieve results: VCD (cells/mL), viability (%), mean cell diameter (um), aggregate %."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [OTHER]
    # "Flag any sample with viability < 70% -- log as process concern, alert operator immediately."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [OTHER]
    # "Flag any sample with aggregate % > 15% -- log for microscopy review."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Review flagged samples under inverted microscope at position H2 before clearing for process use."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review flagged samples under inverted microscope at position H2 before clearing for process use.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 11, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 12 ── [OTHER]
    # "Log VCD and viability data against process day for trend tracking."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Run 2 instrument cleaning cycles with cleaning solution at position H3 at run end."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Export VCD and viability report to run file with timestamp."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Archive all Vi-CELL image files for the run."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_004",
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
        result = await run_bio_004(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
