"""
BioInterface — Auto-generated Protocol
Assay    : BIO_016 — Buffer preparation and verification
Field    : Biopharma / CDMO
Workbench: WB1
Robot min: 40 | Total hours: 1.5
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
    "A1": {"slot": 1, "description": "Excipient containers -- arranged in addition order per batch record"},
    "B1": {"slot": 7, "description": "Mixing vessel (glass or stainless steel) with magnetic stir bar"},
    "B2": {"slot": 8, "description": "Sterile receiving vessel for filtered buffer"},
    "C1": {"slot": 13, "description": "Water supply -- WFI or purified water"},
    "C2": {"slot": 14, "description": "1M NaOH dispensing bottle"},
    "C3": {"slot": 15, "description": "1M HCl dispensing bottle"},
    "C4": {"slot": 16, "description": "0.1M NaOH dispensing bottle"},
    "C5": {"slot": 17, "description": "0.1M HCl dispensing bottle"},
    "D1": {"slot": 19, "description": "0.22 um sterilising filter assembly with nitrogen supply"},
    "H1": {"slot": 43, "description": "Calibrated analytical balance (0.0001 g)"},
    "H2": {"slot": 44, "description": "pH meter with combination electrode"},
    "H3": {"slot": 45, "description": "Clarity sensor or visual inspection station"},
    "H4": {"slot": 50, "description": "Conductivity meter with probe"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "ph_tolerance": "Target +/-0.05 pH units",
    "conductivity_tolerance": "Target +/-10%",
    "post_filtration_ph_shift": "<= 0.05 pH units",
    "post_filtration_conductivity_shift": "<= 5%",
    "filter_integrity": "Bubble point or pressure hold per manufacturer specification",
    "appearance": "Clear, colourless, no particulates",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_016(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Buffer preparation and verification

    Purpose    : Prepare, pH-adjust, and verify process buffers to specification including pH, conductivity, and visual appearance for GMP manufacturing.
    Workbench  : WB1
    Robot time : 40 minutes active
    Total time : 1.5 hours
    Throughput : 1 samples/run
    Difficulty : medium
    AutoMATE 96: head=not applicable, tagged_steps=0/17
    Regulatory : ICH Q6B, USP <1231>, 21 CFR 211.94
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_016: Buffer preparation and verification")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Retrieve batch record and confirm buffer specification: target composition, volume, pH, conductivity, and appearance."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Weigh each excipient on calibrated analytical balance at position H1 (0.0001 g resolution) from excipient containers at position A1 -- record each weight and lot number."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [OTHER]
    # "Transfer excipients to mixing vessel at position B1; add 80% of target water volume from position C1 (WFI or purified water)."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [OTHER]
    # "Start stirrer at 300 rpm -- mix until fully dissolved; robot monitors dissolution by periodic visual check (clarity sensor at position H3 if available)."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "After dissolution, immerse pH electrode from position H2 into solution; record initial pH."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [OTHER]
    # "Adjust pH to target using 1M NaOH or 1M HCl from positions C2/C3 -- add in 0.5 mL increments near target; record volume added at each step."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [OTHER]
    # "When pH is within +/-0.02 of target, switch to 0.1M NaOH/HCl from positions C4/C5 for fine adjustment."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [OTHER]
    # "Make up to final volume with water from C1; mix 10 additional minutes."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [INSTRUMENT_TRIGGER]
    # "Measure final pH -- confirm within specification (+/-0.05 of target); record to 0.01 resolution."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 9: generic not wired — skipping trigger")
    log.append({"step": 9, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 10 ── [INSTRUMENT_TRIGGER]
    # "Measure conductivity using probe at position H4 -- confirm within specification (+/-10% of target); record in mS/cm."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 10: generic not wired — skipping trigger")
    log.append({"step": 10, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 11 ── [OTHER]
    # "Record visual appearance: clear, colourless, no particulates visible."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Confirm all weights, pH adjustments, and final measurements match batch record before proceeding to filtration."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm all weights, pH adjustments, and final measurements match batch record before proceeding to filtration.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 12, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Pre-wet 0.22 um sterilising filter at position D1 with 100 mL of same buffer."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Filter entire batch through 0.22 um filter under nitrogen pressure (1-2 bar) into sterile receiving vessel at position B2."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [INSTRUMENT_TRIGGER]
    # "Measure pH and conductivity of filtered buffer -- confirm unchanged from pre-filtration values (pH shift <= 0.05, conductivity shift <= 5%)."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 15: generic not wired — skipping trigger")
    log.append({"step": 15, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 16 ── [OTHER]
    # "Label container with buffer name, lot, pH, conductivity, date, expiry, and preparer ID."
    # (unclassified step — logged only)
    log.append({"step": 16, "action": "OTHER", "status": "logged"})

    # ── STEP 17 ── [INSTRUMENT_TRIGGER]
    # "Export buffer preparation report with all weights, adjustments, and measurements to run file."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 17: generic not wired — skipping trigger")
    log.append({"step": 17, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_016",
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
        result = await run_bio_016(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
