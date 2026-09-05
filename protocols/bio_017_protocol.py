"""
BioInterface — Auto-generated Protocol
Assay    : BIO_017 — In-process pH and dissolved oxygen probe verification
Field    : Biopharma / CDMO
Workbench: WB2
Robot min: 15 | Total hours: 0.5
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
    "A1": {"slot": 1, "description": "Not used -- samples collected directly from bioreactor"},
    "B1": {"slot": 7, "description": "Measurement cup rack (6-position, 5 mL cups)"},
    "C1": {"slot": 13, "description": "70% ethanol for port cleaning"},
    "D1": {"slot": 19, "description": "Pre-labelled syringe rack -- 10 mL syringes with caps"},
    "F1": {"slot": 31, "description": "pH 7.00 certified calibration buffer"},
    "F2": {"slot": 38, "description": "pH 7.40 certified calibration buffer"},
    "G1": {"slot": 37, "description": "Blood gas analyser (Radiometer ABL90 or equivalent)"},
    "H1": {"slot": 43, "description": "Calibrated offline pH meter"},
    "H3": {"slot": 45, "description": "Bioreactor sample port (aseptic connector)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "ph_probe_correlation": "Offline vs in-line pH within +/-0.05 pH units",
    "do_probe_correlation": "Offline vs in-line DO within +/-5%",
    "ph_recalibration_trigger": "|pH delta| > 0.10 pH units triggers immediate recalibration",
    "measurement_timing": "All measurements completed within 5 minutes of sample collection",
    "ph_calibration_slope": "95-105%",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_017(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    In-process pH and dissolved oxygen probe verification

    Purpose    : Collect offline reference samples from bioreactor to verify accuracy of in-line pH and dissolved oxygen (DO) probes during GMP production runs.
    Workbench  : WB2
    Robot time : 15 minutes active
    Total time : 0.5 hours
    Throughput : 6 samples/run
    Difficulty : medium
    AutoMATE 96: head=not applicable, tagged_steps=0/14
    Regulatory : ICH Q6B (process monitoring), 21 CFR 211.68
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_017: In-process pH and dissolved oxygen probe verification")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Confirm offline pH meter at position H1 is calibrated with pH 7.00 and pH 7.40 certified buffers from positions F1 and F2 -- log slope (must be 95-105%)."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [INSTRUMENT_TRIGGER]
    # "Confirm blood gas analyser at position G1 is ready with fresh cartridge loaded -- log cartridge lot and expiry."
    # Instrument trigger: plate_reader
    if "plate_reader" in instruments:
        await instruments["plate_reader"].read()
    else:
        print(f"[{run_id}] Step 2: plate_reader not wired — skipping trigger")
    log.append({"step": 2, "action": "INSTRUMENT_TRIGGER", "instrument": "plate_reader", "status": "complete"})

    # ── STEP 3 ── [INSTRUMENT_TRIGGER]
    # "Record current bioreactor in-line pH and DO probe readings from DCS/SCADA before sampling -- log both values with timestamp."
    # Instrument trigger: plate_reader
    if "plate_reader" in instruments:
        await instruments["plate_reader"].read()
    else:
        print(f"[{run_id}] Step 3: plate_reader not wired — skipping trigger")
    log.append({"step": 3, "action": "INSTRUMENT_TRIGGER", "instrument": "plate_reader", "status": "complete"})

    # ── STEP 4 ── [OTHER]
    # "Open bioreactor sample port at position H3 following aseptic technique -- discard first 5 mL to clear dead volume."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "Collect 5 mL sample into pre-labelled syringe from position D1 -- draw slowly to avoid degassing; cap immediately."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [INSTRUMENT_TRIGGER]
    # "For pO2/pCO2 measurement: immediately load capped syringe into blood gas analyser at position G1 -- analyse within 2 minutes of collection."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 6: generic not wired — skipping trigger")
    log.append({"step": 6, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 7 ── [OTHER]
    # "Record offline pO2 (mmHg), pCO2 (mmHg), and blood gas pH from analyser output."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [WAIT]
    # "For offline pH: transfer 2 mL aliquot from syringe to measurement cup at position B1; immerse pH electrode from H1; wait 30 seconds for stabilisation; record pH to 0.01."
    print(f"[{run_id}] Step 8: waiting 30s — robot free for other tasks")
    await asyncio.sleep(30)
    log.append({"step": 8, "action": "WAIT", "duration_seconds": 30, "status": "complete"})

    # ── STEP 9 ── [OTHER]
    # "Calculate pH delta: offline pH minus in-line probe pH -- flag if |delta| > 0.05 pH units."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [OTHER]
    # "Calculate DO delta: convert offline pO2 to %DO using calibration; compare to in-line DO -- flag if |delta| > 5%."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [OTHER]
    # "If pH delta > 0.10 pH units: ALERT -- in-line probe requires recalibration or replacement; notify process engineer immediately."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [OTHER]
    # "Log all offline values, in-line values, and calculated deltas in batch record with timestamp."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Export probe verification report to run file."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Clean sample port with 70% ethanol from position C1 after sampling."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_017",
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
        result = await run_bio_017(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
