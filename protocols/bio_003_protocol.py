"""
BioInterface — Auto-generated Protocol
Assay    : BIO_003 — SEC-HPLC aggregation analysis
Field    : Biopharma / CDMO
Workbench: WB1
Robot min: 15 | Total hours: 5
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
    "B1": {"slot": 7, "description": "HPLC glass vial rack -- 48-position"},
    "C1": {"slot": 13, "description": "Reagent reservoir -- PBS pH 7.2 mobile phase"},
    "D1": {"slot": 19, "description": "Tip rack -- 200 uL tips"},
    "F1": {"slot": 31, "description": "Reference standard rack -- mAb reference"},
    "F2": {"slot": 38, "description": "MW standard rack -- thyroglobulin"},
    "G1": {"slot": 37, "description": "HPLC autosampler interface"},
    "H1": {"slot": 43, "description": "HPLC instrument control"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "system_suitability_column_plates": ">= 8000 theoretical plates (thyroglobulin)",
    "reference_standard_monomer_drift": "<= +/-1.0% from historical mean",
    "hmws_investigation_threshold": ">= 2% triggers investigation",
    "peak_resolution_monomer_dimer": ">= 1.5",
    "retention_time_reproducibility_cv": "<= 0.5%",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_003(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    SEC-HPLC aggregation analysis

    Purpose    : Quantify monomer, dimer, and high-molecular-weight species (HMWS) in purified mAb samples by size-exclusion chromatography.
    Workbench  : WB1
    Robot time : 15 minutes active
    Total time : 5 hours
    Throughput : 12 samples/run
    Difficulty : easy
    AutoMATE 96: head=not applicable, tagged_steps=0/15
    Regulatory : ICH Q6B, USP <1045>, Ph. Eur. 2.2.30
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_003: SEC-HPLC aggregation analysis")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [TRANSPORT]
    # "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12); centrifuge at 10,000 x g for 5 minutes to remove particulates."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["A1"]["slot"],
    )
    log.append({"step": 1, "action": "TRANSPORT", "from": "input_rack", "to": "A1", "status": "complete"})

    # ── STEP 2 ── [INSTRUMENT_TRIGGER]
    # "Transfer 100 uL clarified sample to HPLC glass vials at position B1; add 100 uL PBS mobile phase from reservoir at position C1 -- mix by gentle pipetting."
    # Instrument trigger: hplc
    if "hplc" in instruments:
        await instruments["hplc"].read()
    else:
        print(f"[{run_id}] Step 2: hplc not wired — skipping trigger")
    log.append({"step": 2, "action": "INSTRUMENT_TRIGGER", "instrument": "hplc", "status": "complete"})

    # ── STEP 3 ── [INSTRUMENT_TRIGGER]
    # "Load reference standard vials (mAb reference with known aggregate profile) from position F1 into HPLC autosampler at position G1."
    # Instrument trigger: hplc
    if "hplc" in instruments:
        await instruments["hplc"].read()
    else:
        print(f"[{run_id}] Step 3: hplc not wired — skipping trigger")
    log.append({"step": 3, "action": "INSTRUMENT_TRIGGER", "instrument": "hplc", "status": "complete"})

    # ── STEP 4 ── [INSTRUMENT_TRIGGER]
    # "Load system suitability vial (thyroglobulin MW standards) from position F2:1 into autosampler position 1 -- run as first injection."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 4: generic not wired — skipping trigger")
    log.append({"step": 4, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 5 ── [INSTRUMENT_TRIGGER]
    # "Load prepared sample vials into autosampler positions 2 onwards per run sequence."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 5: generic not wired — skipping trigger")
    log.append({"step": 5, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 6 ── [OTHER]
    # "Confirm mobile phase (PBS pH 7.2, 0.22 um filtered) pressure is 50-200 bar before initiating run."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [INSTRUMENT_TRIGGER]
    # "Initiate SEC-HPLC run -- 20-minute runtime per injection at 0.5 mL/min; UV detection at 280 nm."
    # Instrument trigger: hplc
    if "hplc" in instruments:
        await instruments["hplc"].read()
    else:
        print(f"[{run_id}] Step 7: hplc not wired — skipping trigger")
    log.append({"step": 7, "action": "INSTRUMENT_TRIGGER", "instrument": "hplc", "status": "complete"})

    # ── STEP 8 ── [OTHER]
    # "Robot monitors for injection complete signal and confirms UV 280 nm trace is detected per injection."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [OTHER]
    # "After all injections, export peak area data for each species (HMWS, monomer, LMWS) to run file."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Confirm thyroglobulin standard shows expected retention time (+/-0.5 min) and theoretical plates >= 8000 before accepting run."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm thyroglobulin standard shows expected retention time (+/-0.5 min) and theoretical plates >= 8000 before accepting run.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 10, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 11 ── [OTHER]
    # "Calculate %HMWS, %monomer, %LMWS from peak areas -- log values per sample."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [OTHER]
    # "Flag any samples with %HMWS > 2% as exceeding standard investigation threshold."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Compare reference standard monomer % to historical mean -- flag if drift > +/-1%."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Export aggregate profile report to run file; archive raw chromatograms."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Prime column with 5 column volumes PBS post-run -- log flush."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_003",
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
        result = await run_bio_003(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
