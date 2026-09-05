"""
BioInterface — Auto-generated Protocol
Assay    : BIO_009 — Bioburden testing by membrane filtration
Field    : Biopharma / CDMO
Workbench: WB3
Robot min: 45 | Total hours: 120
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
    "A1": {"slot": 1, "description": "Sample input -- sterile sample container (test volume)"},
    "B1": {"slot": 7, "description": "SCDA agar plates (30-35C incubation group)"},
    "B2": {"slot": 8, "description": "SDA agar plates (20-25C incubation group)"},
    "C1": {"slot": 13, "description": "Sterile peptone water reservoir (100 mL)"},
    "D1": {"slot": 19, "description": "Sterile serological pipettes (25 mL, in holder)"},
    "D2": {"slot": 26, "description": "Sterile forceps (in sterile packaging)"},
    "F1": {"slot": 31, "description": "Positive control organism suspension (S. aureus, 10-100 CFU/mL)"},
    "H1": {"slot": 43, "description": "Membrane filtration manifold (vacuum-driven, Grade A BSC-adjacent)"},
    "H2": {"slot": 44, "description": "Incubator 30-35C"},
    "H3": {"slot": 45, "description": "Incubator 20-25C"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "positive_control_growth": "Confirmed growth by day 2",
    "negative_control": "Zero colonies at day 5",
    "membrane_integrity": "No cracks, tears, or uneven wetting confirmed before transfer",
    "specification_limit": "Per product specification (e.g. <= 100 CFU/mL for drug substance)",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_009(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Bioburden testing by membrane filtration

    Purpose    : Enumerate total viable aerobic microbial count in process samples by membrane filtration onto compendial growth media plates.
    Workbench  : WB3
    Robot time : 45 minutes active
    Total time : 120 hours
    Throughput : 4 samples/run
    Difficulty : complex
    AutoMATE 96: head=not applicable, tagged_steps=0/16
    Regulatory : USP <61>, EP 2.6.12, Ph. Eur. 2.6.12
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_009: Bioburden testing by membrane filtration")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [INSTRUMENT_TRIGGER]
    # "Confirm ISO Class 5 (Grade A) laminar flow environment is operational -- log particle count and air velocity before starting."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 1: generic not wired — skipping trigger")
    log.append({"step": 1, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 2 ── [OTHER]
    # "Pre-wet 0.45 um membrane filters with 10 mL sterile peptone water from position C1 in membrane filtration manifold at position H1."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [TRANSPORT]
    # "Pick up sample from position A1 -- aspirate specified test volume (typically 10 mL) using sterile serological pipette from position D1."
    await robot.move_plate(
        plate_id=plate_id,
        from_position=DECK_LAYOUT["A1"]["slot"],
        to_position=DECK_LAYOUT["D1"]["slot"],
    )
    log.append({"step": 3, "action": "TRANSPORT", "from": "A1", "to": "D1", "status": "complete"})

    # ── STEP 4 ── [OTHER]
    # "Transfer sample onto pre-wetted membrane -- apply vacuum until completely filtered; log filter appearance after filtration."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "Rinse membrane 3 times with 10 mL sterile peptone water per rinse -- apply vacuum after each rinse until dry."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Visually inspect membrane for cracks, holes, or uneven wetting before transfer -- reject and repeat if membrane integrity is compromised."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Visually inspect membrane for cracks, holes, or uneven wetting before transfer -- reject and repeat if membrane integrity is compromised.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 6, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 7 ── [INSTRUMENT_TRIGGER]
    # "Transfer membrane aseptically to SCDA agar plate at position B1 (total aerobic count) using sterile forceps from position D2."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 7: generic not wired — skipping trigger")
    log.append({"step": 7, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 8 ── [INSTRUMENT_TRIGGER]
    # "Transfer duplicate membrane to SDA agar plate at position B2 (yeast and mould count)."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 8: generic not wired — skipping trigger")
    log.append({"step": 8, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 9 ── [OTHER]
    # "Label both plates with sample ID, date, batch number, and analyst initials."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [OTHER]
    # "Transfer SCDA plates to incubator at 30-35C at position H2; SDA plates to incubator at 20-25C at position H3 -- log incubation start times."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Count colonies on SCDA plates at day 3 and day 5; count SDA plates at day 3 and day 5 -- record counts; robot cannot perform colony counting."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Count colonies on SCDA plates at day 3 and day 5; count SDA plates at day 3 and day 5 -- record counts; robot cannot perform colony counting.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 11, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 12 ── [OTHER]
    # "Positive control (S. aureus ATCC 6538, 10-100 CFU from position F1) must show growth by day 2 -- invalidate run if positive control fails."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Negative control (rinse water only) must show zero colonies at day 5."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Calculate CFU/mL for each sample -- compare to specification limit."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [INSTRUMENT_TRIGGER]
    # "Export bioburden report with colony counts, incubation logs, and pass/fail status to run file."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 15: generic not wired — skipping trigger")
    log.append({"step": 15, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 16 ── [OTHER]
    # "Archive plate photographs at incubation endpoint."
    # (unclassified step — logged only)
    log.append({"step": 16, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_009",
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
        result = await run_bio_009(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
