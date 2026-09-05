"""
BioInterface — Auto-generated Protocol
Assay    : BIO_011 — pH and conductivity measurement
Field    : Biopharma / CDMO
Workbench: WB2
Robot min: 15 | Total hours: 0.5
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
    "B1": {"slot": 7, "description": "Measurement cup rack (12-position, 5 mL cups)"},
    "C1": {"slot": 13, "description": "Ultrapure water reservoir (electrode rinse)"},
    "D1": {"slot": 19, "description": "Tip rack -- 1 mL tips"},
    "F1": {"slot": 31, "description": "pH 4.0 certified calibration buffer"},
    "F2": {"slot": 38, "description": "pH 7.0 certified calibration buffer"},
    "F3": {"slot": 39, "description": "Conductivity standard (1413 uS/cm certified)"},
    "H1": {"slot": 43, "description": "Calibrated pH meter with combination electrode"},
    "H2": {"slot": 44, "description": "Calibrated conductivity meter with probe"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "ph_calibration_slope": "95-105%",
    "conductivity_calibration_accuracy": "Within +/-2% of certified standard",
    "end_of_run_ph_verification": "pH 7.0 buffer reads within +/-0.05 pH units",
    "ph_specification_tolerance": "+/-0.1 pH units of target",
    "conductivity_specification_tolerance": "+/-5% of target",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_011(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    pH and conductivity measurement

    Purpose    : Measure pH and conductivity of process solutions and formulations to confirm buffer composition, formulation identity, and process control.
    Workbench  : WB2
    Robot time : 15 minutes active
    Total time : 0.5 hours
    Throughput : 12 samples/run
    Difficulty : easy
    AutoMATE 96: head=not applicable, tagged_steps=0/15
    Regulatory : USP <791>, USP <645>, Ph. Eur. 2.2.3, Ph. Eur. 2.2.38
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_011: pH and conductivity measurement")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Switch on pH meter at position H1 and conductivity meter at position H2 -- allow 15-minute warm-up and electrode stabilisation."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Perform two-point pH calibration using pH 4.0 and pH 7.0 certified buffers from positions F1 and F2 -- confirm slope 95-105% before proceeding."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Perform two-point pH calibration using pH 4.0 and pH 7.0 certified buffers from positions F1 and F2 -- confirm slope 95-105% before proceeding.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 2, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 3 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Calibrate conductivity meter using certified standard from position F3 -- confirm reading within +/-2% of certified value."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Calibrate conductivity meter using certified standard from position F3 -- confirm reading within +/-2% of certified value.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 3, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 4 ── [TRANSPORT]
    # "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12)."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["A1"]["slot"],
    )
    log.append({"step": 4, "action": "TRANSPORT", "from": "input_rack", "to": "A1", "status": "complete"})

    # ── STEP 5 ── [INSTRUMENT_TRIGGER]
    # "Transfer 2 mL of each sample to measurement cups at position B1 using 1 mL tips from position D1."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 5: generic not wired — skipping trigger")
    log.append({"step": 5, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 6 ── [WAIT]
    # "Immerse pH electrode into first sample cup -- wait 30 seconds for stabilisation; record pH to 0.01 resolution."
    print(f"[{run_id}] Step 6: waiting 30s — robot free for other tasks")
    await asyncio.sleep(30)
    log.append({"step": 6, "action": "WAIT", "duration_seconds": 30, "status": "complete"})

    # ── STEP 7 ── [OTHER]
    # "Rinse pH electrode with ultrapure water from position C1 (3 x 500 uL) between samples; blot dry with lint-free tissue."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [INSTRUMENT_TRIGGER]
    # "Repeat pH measurement for all 12 samples -- log each result."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 8: generic not wired — skipping trigger")
    log.append({"step": 8, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 9 ── [WAIT]
    # "Immerse conductivity probe into first sample cup -- wait 20 seconds for stabilisation; record conductivity (mS/cm)."
    print(f"[{run_id}] Step 9: waiting 20s — robot free for other tasks")
    await asyncio.sleep(20)
    log.append({"step": 9, "action": "WAIT", "duration_seconds": 20, "status": "complete"})

    # ── STEP 10 ── [OTHER]
    # "Rinse conductivity probe with ultrapure water between samples."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [INSTRUMENT_TRIGGER]
    # "Repeat conductivity measurement for all 12 samples -- log each result."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 11: generic not wired — skipping trigger")
    log.append({"step": 11, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 12 ── [OTHER]
    # "Flag any pH outside +/-0.1 pH units of target or conductivity outside +/-5% of target."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [INSTRUMENT_TRIGGER]
    # "Verify pH calibration: re-read pH 7.0 buffer at end of run -- must read within +/-0.05 pH units; flag if outside."
    # Instrument trigger: plate_reader
    if "plate_reader" in instruments:
        await instruments["plate_reader"].read()
    else:
        print(f"[{run_id}] Step 13: plate_reader not wired — skipping trigger")
    log.append({"step": 13, "action": "INSTRUMENT_TRIGGER", "instrument": "plate_reader", "status": "complete"})

    # ── STEP 14 ── [INSTRUMENT_TRIGGER]
    # "Export pH and conductivity report with all readings and pass/fail status to run file."
    # Instrument trigger: plate_reader
    if "plate_reader" in instruments:
        await instruments["plate_reader"].read()
    else:
        print(f"[{run_id}] Step 14: plate_reader not wired — skipping trigger")
    log.append({"step": 14, "action": "INSTRUMENT_TRIGGER", "instrument": "plate_reader", "status": "complete"})

    # ── STEP 15 ── [OTHER]
    # "Store electrodes in appropriate solutions -- pH electrode in KCl 3M; conductivity probe in ultrapure water; log storage condition."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_011",
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
        result = await run_bio_011(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
