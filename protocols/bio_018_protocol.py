"""
BioInterface — Auto-generated Protocol
Assay    : BIO_018 — Cell culture media preparation and QC
Field    : Biopharma / CDMO
Workbench: WB3
Robot min: 60 | Total hours: 2
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
    "A1": {"slot": 1, "description": "Media base container (powder or liquid concentrate, from cold storage)"},
    "A2": {"slot": 2, "description": "Supplement rack -- L-glutamine, sodium bicarbonate, additional additives"},
    "A3": {"slot": 3, "description": "FBS container (if required, from -20C thawed to RT)"},
    "B1": {"slot": 7, "description": "Sterile mixing vessel with magnetic stir bar"},
    "B2": {"slot": 8, "description": "Sterile receiving vessel for filtered media"},
    "C1": {"slot": 13, "description": "WFI or cell culture-grade water supply"},
    "C2": {"slot": 14, "description": "NaOH for pH adjustment (1M and 0.1M)"},
    "D1": {"slot": 19, "description": "0.22 um sterilising filter assembly"},
    "F1": {"slot": 31, "description": "TSB sterility broth tube"},
    "F2": {"slot": 38, "description": "Thioglycolate sterility broth tube"},
    "H1": {"slot": 43, "description": "Biological safety cabinet (certified, Grade A)"},
    "H2": {"slot": 44, "description": "Calibrated pH meter"},
    "H3": {"slot": 45, "description": "Calibrated osmometer"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "ph_range": "7.0-7.4",
    "osmolality_range": "280-320 mOsm/kg",
    "osmolality_cv": "<= 2% across triplicate readings",
    "appearance": "Clear, straw-coloured, no turbidity or particulates",
    "sterility_14day": "No turbidity in TSB or thioglycolate broth at 14 days",
    "post_filtration_ph_shift": "<= 0.05 pH units",
    "post_filtration_osmolality_shift": "<= 5 mOsm/kg",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_018(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Cell culture media preparation and QC

    Purpose    : Prepare cell culture media from powder or liquid concentrates, supplement, sterile filter, and perform quality control testing before use in GMP bioreactor operations.
    Workbench  : WB3
    Robot time : 60 minutes active
    Total time : 2 hours
    Throughput : 1 samples/run
    Difficulty : complex
    AutoMATE 96: head=not applicable, tagged_steps=0/21
    Regulatory : ICH Q6B, USP <1085>, 21 CFR 211
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_018: Cell culture media preparation and QC")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Retrieve media batch record and confirm formulation: base media, supplements, target volume, pH, osmolality specifications."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Confirm biological safety cabinet at position H1 is running and certified for aseptic work -- log BSC serial number."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [OTHER]
    # "Retrieve powdered or liquid media base from cold storage at position A1 -- verify lot number and expiry date; log both."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [OTHER]
    # "For powdered media: add 80% target volume WFI from position C1 to sterile mixing vessel at position B1; start stirrer."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "Add powdered media slowly while stirring at 300 rpm -- stir for 30 minutes until fully dissolved; robot monitors dissolution."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [OTHER]
    # "Add supplements in specified order from position A2: L-glutamine (200 mM stock), sodium bicarbonate (7.5% stock), additional supplements per specification -- log each lot number and volume."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [OTHER]
    # "If serum required: add FBS from position A3 at specified percentage -- calculate volume; log lot number and volume."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [INSTRUMENT_TRIGGER]
    # "Adjust pH to 7.0-7.4 using NaOH from position C2 -- add in 0.5 mL increments; measure with pH electrode at position H2 between additions."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 8: generic not wired — skipping trigger")
    log.append({"step": 8, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 9 ── [OTHER]
    # "Make up to final volume with WFI from position C1; mix additional 10 minutes."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [INSTRUMENT_TRIGGER]
    # "Measure pH at position H2 -- must be 7.0-7.4; record to 0.01."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 10: generic not wired — skipping trigger")
    log.append({"step": 10, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 11 ── [INSTRUMENT_TRIGGER]
    # "Measure osmolality at position H3 in triplicate -- must be 280-320 mOsm/kg; record mean and CV."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 11: generic not wired — skipping trigger")
    log.append({"step": 11, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 12 ── [OTHER]
    # "Observe appearance: must be clear, straw-coloured (with phenol red); any turbidity or unusual colour is grounds for rejection."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Confirm pH, osmolality, and appearance meet specification before proceeding to filtration."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm pH, osmolality, and appearance meet specification before proceeding to filtration.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 13, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 14 ── [OTHER]
    # "Pre-wet 0.22 um sterilising filter at position D1 with 100 mL of same media."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Filter entire batch through 0.22 um filter into sterile receiving vessel at position B2 under nitrogen pressure."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    # ── STEP 16 ── [OTHER]
    # "Aseptically remove 10 mL sample from filtered media -- transfer to TSB broth tube at position F1 and thioglycolate broth tube at position F2 for sterility testing."
    # (unclassified step — logged only)
    log.append({"step": 16, "action": "OTHER", "status": "logged"})

    # ── STEP 17 ── [WAIT]
    # "Incubate sterility tubes: TSB at 20-25C and thioglycolate at 30-35C for 14 days -- robot logs incubation start; analyst inspects daily."
    print(f"[{run_id}] Step 17: waiting 0s — robot free for other tasks")
    await asyncio.sleep(0)
    log.append({"step": 17, "action": "WAIT", "duration_seconds": 0, "status": "complete"})

    # ── STEP 18 ── [INSTRUMENT_TRIGGER]
    # "Measure pH and osmolality of filtered media -- confirm unchanged from pre-filtration values."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 18: generic not wired — skipping trigger")
    log.append({"step": 18, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 19 ── [OTHER]
    # "Label container with media name, lot, date, expiry (30 days at 2-8C), pH, osmolality, preparer."
    # (unclassified step — logged only)
    log.append({"step": 19, "action": "OTHER", "status": "logged"})

    # ── STEP 20 ── [OTHER]
    # "Transfer to 2-8C storage; log storage location."
    # (unclassified step — logged only)
    log.append({"step": 20, "action": "OTHER", "status": "logged"})

    # ── STEP 21 ── [INSTRUMENT_TRIGGER]
    # "Export media preparation report with all measurements, component lot numbers, and sterility test initiation to run file."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 21: generic not wired — skipping trigger")
    log.append({"step": 21, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_018",
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
        result = await run_bio_018(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
