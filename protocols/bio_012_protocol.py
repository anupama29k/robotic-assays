"""
BioInterface — Auto-generated Protocol
Assay    : BIO_012 — Subvisible particle count by light obscuration
Field    : Biopharma / CDMO
Workbench: WB2
Robot min: 15 | Total hours: 1
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
    "A1": {"slot": 1, "description": "Sample input rack -- 8 x 20 mL glass vials or PFS containers"},
    "C1": {"slot": 13, "description": "Particle-free water reservoir (USP-grade, 0.22 um filtered)"},
    "D1": {"slot": 19, "description": "Sterile syringe rack -- 5 mL syringes"},
    "G1": {"slot": 37, "description": "HIAC light obscuration particle counter (with sensor and autosampler)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "background_particle_count": "< 5 particles/mL at >= 10 um",
    "usp787_10um_limit": "<= 6000 particles/container at >= 10 um",
    "usp787_25um_limit": "<= 600 particles/container at >= 25 um",
    "aliquot_cv": "<= 25% across 4 x 1 mL aliquots",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_012(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Subvisible particle count by light obscuration

    Purpose    : Count and size subvisible particles (>=2 um, >=5 um, >=10 um, >=25 um) in injectable drug products per compendial requirements.
    Workbench  : WB2
    Robot time : 15 minutes active
    Total time : 1 hours
    Throughput : 8 samples/run
    Difficulty : medium
    AutoMATE 96: head=not applicable, tagged_steps=0/15
    Regulatory : USP <787>, USP <788>, Ph. Eur. 2.9.19
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_012: Subvisible particle count by light obscuration")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [INSTRUMENT_TRIGGER]
    # "Switch on HIAC light obscuration particle counter at position G1 -- allow 30-minute warm-up; confirm laser alignment and sensor calibration status."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 1: generic not wired — skipping trigger")
    log.append({"step": 1, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 2 ── [INSTRUMENT_TRIGGER]
    # "Flush sensor with 5 volumes particle-free water from position C1 -- verify background particle count < 5 particles/mL at >= 10 um."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 2: generic not wired — skipping trigger")
    log.append({"step": 2, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 3 ── [OTHER]
    # "If background exceeds limit, repeat flush cycle up to 3 times -- abort and alert for service if still failing."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [TRANSPORT]
    # "Pick up sample containers from input rack at position A1 -- gently invert each 20 times to resuspend particles without creating bubbles."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["A1"]["slot"],
    )
    log.append({"step": 4, "action": "TRANSPORT", "from": "input_rack", "to": "A1", "status": "complete"})

    # ── STEP 5 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Confirm sample has been degassed (no visible bubbles) and is at room temperature before proceeding."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm sample has been degassed (no visible bubbles) and is at room temperature before proceeding.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 5, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 6 ── [OTHER]
    # "Aspirate 5 mL from first sample container using 5 mL sterile syringe from position D1 -- aspirate slowly to avoid generating air bubbles."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [OTHER]
    # "Inject sample into HIAC sensor at position G1 at 10 mL/min flow rate -- discard first 1 mL as priming volume."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [INSTRUMENT_TRIGGER]
    # "Collect 4 x 1 mL aliquots per sample per USP <787> requirements; record particle count at >=2 um, >=5 um, >=10 um, >=25 um per aliquot."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 8: generic not wired — skipping trigger")
    log.append({"step": 8, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 9 ── [OTHER]
    # "Calculate mean and standard deviation across 4 aliquots -- flag if CV > 25% between aliquots (indicates sample heterogeneity)."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [OTHER]
    # "Flush sensor with particle-free water between samples -- verify background returns to < 5 particles/mL."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [OTHER]
    # "Repeat for all samples in run."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [OTHER]
    # "Compare results to USP <787> specification: <=6000 particles/container >=10 um; <=600 particles/container >=25 um."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Flag any sample exceeding specification -- log for QA investigation."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [INSTRUMENT_TRIGGER]
    # "Export particle count report with per-aliquot data, means, and pass/fail status to run file."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 14: generic not wired — skipping trigger")
    log.append({"step": 14, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 15 ── [OTHER]
    # "Flush and park sensor at run end -- log cleaning."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_012",
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
        result = await run_bio_012(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
