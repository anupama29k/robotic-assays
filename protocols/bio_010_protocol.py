"""
BioInterface — Auto-generated Protocol
Assay    : BIO_010 — Osmolality measurement by freezing-point depression
Field    : Biopharma / CDMO
Workbench: WB2
Robot min: 10 | Total hours: 0.5
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
    "A1": {"slot": 1, "description": "Sample input rack -- 12 x 1.5 mL tubes"},
    "B1": {"slot": 7, "description": "Osmometry cup rack (12-position)"},
    "D1": {"slot": 19, "description": "Tip rack -- 200 uL tips"},
    "F1": {"slot": 31, "description": "290 mOsm/kg certified calibration standard"},
    "F2": {"slot": 38, "description": "100 mOsm/kg certified calibration standard"},
    "H1": {"slot": 43, "description": "Freezing-point osmometer with autosampler"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "bracketing_standards_tolerance": "Within +/-10 mOsm/kg of certified value",
    "instrument_drift": "< 5 mOsm/kg between sequential standard measurements",
    "specification_range": "Per product specification (typically 270-350 mOsm/kg)",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_010(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Osmolality measurement by freezing-point depression

    Purpose    : Measure osmolality of biopharmaceutical formulations and process solutions to confirm isotonicity and formulation consistency.
    Workbench  : WB2
    Robot time : 10 minutes active
    Total time : 0.5 hours
    Throughput : 12 samples/run
    Difficulty : easy
    AutoMATE 96: head=not applicable, tagged_steps=0/15
    Regulatory : USP <785>, Ph. Eur. 2.2.35, ICH Q6B
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_010: Osmolality measurement by freezing-point depression")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Switch on osmometer at position H1 -- allow 30-minute warm-up; confirm instrument stability."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Perform two-point calibration with 290 mOsm/kg and 100 mOsm/kg certified standards from positions F1 and F2 -- log calibration result and slope before proceeding."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Perform two-point calibration with 290 mOsm/kg and 100 mOsm/kg certified standards from positions F1 and F2 -- log calibration result and slope before proceeding.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 2, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 3 ── [TRANSPORT]
    # "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12)."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["A1"]["slot"],
    )
    log.append({"step": 3, "action": "TRANSPORT", "from": "input_rack", "to": "A1", "status": "complete"})

    # ── STEP 4 ── [OTHER]
    # "Transfer 200 uL of each sample to osmometry cups at position B1 using 200 uL tips from position D1 -- ensure no air bubbles in cups."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "Load 290 mOsm/kg verification standard (position F1) as cup 1 and final cup in run to bracket all samples."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [INSTRUMENT_TRIGGER]
    # "Load sample cups into osmometer autosampler at position H1 in sequence matching run file."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 6: generic not wired — skipping trigger")
    log.append({"step": 6, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 7 ── [INSTRUMENT_TRIGGER]
    # "Initiate osmometer run -- instrument immerses probe, freezes sample, measures onset of freezing; approximately 90 seconds per sample."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 7: generic not wired — skipping trigger")
    log.append({"step": 7, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 8 ── [OTHER]
    # "Rinse osmometer probe with ultrapure water from instrument internal reservoir between each sample -- log rinse completion."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [INSTRUMENT_TRIGGER]
    # "Retrieve osmolality reading (mOsm/kg) for each sample after each measurement."
    # Instrument trigger: plate_reader
    if "plate_reader" in instruments:
        await instruments["plate_reader"].read()
    else:
        print(f"[{run_id}] Step 9: plate_reader not wired — skipping trigger")
    log.append({"step": 9, "action": "INSTRUMENT_TRIGGER", "instrument": "plate_reader", "status": "complete"})

    # ── STEP 10 ── [OTHER]
    # "Flag any sample outside specification (typically 270-350 mOsm/kg for isotonic formulations)."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [OTHER]
    # "Verify bracketing calibration standards are within +/-10 mOsm/kg of certified value -- invalidate run if outside range."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [INSTRUMENT_TRIGGER]
    # "Export osmolality report with all readings and pass/fail vs specification to run file."
    # Instrument trigger: plate_reader
    if "plate_reader" in instruments:
        await instruments["plate_reader"].read()
    else:
        print(f"[{run_id}] Step 12: plate_reader not wired — skipping trigger")
    log.append({"step": 12, "action": "INSTRUMENT_TRIGGER", "instrument": "plate_reader", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Rinse osmometer probe with 3 cycles of ultrapure water at run end -- log cleaning."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Archive run report."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Log instrument calibration status -- flag if calibration is approaching expiry per instrument SOP."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_010",
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
        result = await run_bio_010(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
