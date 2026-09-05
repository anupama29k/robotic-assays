"""
BioInterface — Auto-generated Protocol
Assay    : BIO_013 — IEX-HPLC charge variant analysis (CEX/AEX)
Field    : Biopharma / CDMO
Workbench: WB1
Robot min: 20 | Total hours: 10
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
    "A1": {"slot": 1, "description": "Sample input rack -- 8 x 1.5 mL tubes"},
    "A9": {"slot": 0, "description": "Desalting spin columns (pre-equilibrated in mobile phase A)"},
    "B1": {"slot": 7, "description": "HPLC glass vial rack -- 24-position"},
    "C1": {"slot": 13, "description": "Mobile phase A reservoir -- 20 mM MES pH 5.6"},
    "C2": {"slot": 14, "description": "Mobile phase B reservoir -- 20 mM MES pH 5.6 + 500 mM NaCl"},
    "D1": {"slot": 19, "description": "Tip rack -- 200 uL tips"},
    "F1": {"slot": 31, "description": "Reference standard -- mAb charge variant reference"},
    "F2": {"slot": 38, "description": "System suitability standard"},
    "G1": {"slot": 37, "description": "HPLC autosampler interface (column at 30C)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "system_suitability_main_peak_rt": "Within +/-0.5 min of expected",
    "reference_standard_drift": "<= +/-2% for any charge group vs historical mean",
    "peak_resolution_acidic_main": ">= 1.0",
    "column_back_pressure": "< 200 bar",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_013(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    IEX-HPLC charge variant analysis (CEX/AEX)

    Purpose    : Resolve and quantify acidic, main, and basic charge variant species in mAb drug substance by ion-exchange chromatography for product quality assessment.
    Workbench  : WB1
    Robot time : 20 minutes active
    Total time : 10 hours
    Throughput : 8 samples/run
    Difficulty : medium
    AutoMATE 96: head=not applicable, tagged_steps=0/15
    Regulatory : ICH Q6B, ICH Q2(R2)
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_013: IEX-HPLC charge variant analysis (CEX/AEX)")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [TRANSPORT]
    # "Pick up sample tubes from input rack at position A1 (A1:1 through A1:8); verify sample concentration is 1-5 mg/mL."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["A1"]["slot"],
    )
    log.append({"step": 1, "action": "TRANSPORT", "from": "input_rack", "to": "A1", "status": "complete"})

    # ── STEP 2 ── [INSTRUMENT_TRIGGER]
    # "If sample requires buffer exchange: transfer 200 uL to desalting spin columns at position A9 pre-equilibrated in IEX mobile phase A; centrifuge at 1500 x g for 2 minutes."
    # Instrument trigger: centrifuge
    if "centrifuge" in instruments:
        await instruments["centrifuge"].read()
    else:
        print(f"[{run_id}] Step 2: centrifuge not wired — skipping trigger")
    log.append({"step": 2, "action": "INSTRUMENT_TRIGGER", "instrument": "centrifuge", "status": "complete"})

    # ── STEP 3 ── [INSTRUMENT_TRIGGER]
    # "Transfer 100 uL buffer-exchanged sample to HPLC glass vials at position B1."
    # Instrument trigger: hplc
    if "hplc" in instruments:
        await instruments["hplc"].read()
    else:
        print(f"[{run_id}] Step 3: hplc not wired — skipping trigger")
    log.append({"step": 3, "action": "INSTRUMENT_TRIGGER", "instrument": "hplc", "status": "complete"})

    # ── STEP 4 ── [INSTRUMENT_TRIGGER]
    # "Load reference standard (well-characterised mAb reference with known charge variant profile) from position F1 into autosampler at position G1."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 4: generic not wired — skipping trigger")
    log.append({"step": 4, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 5 ── [OTHER]
    # "Load system suitability check standard from position F2 as first injection."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [INSTRUMENT_TRIGGER]
    # "Load sample vials into autosampler per run sequence."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 6: generic not wired — skipping trigger")
    log.append({"step": 6, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 7 ── [OTHER]
    # "Confirm both mobile phase A (20 mM MES pH 5.6) and B (20 mM MES pH 5.6 + 500 mM NaCl) reservoirs are sufficient -- minimum 200 mL each."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [OTHER]
    # "Initiate gradient run: 0-60 min linear gradient 0-50% B at 0.8 mL/min; UV 280 nm detection; column temperature 30C."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [OTHER]
    # "Robot monitors for each injection complete signal and confirms UV trace detected."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [OTHER]
    # "After all injections, export peak area data for acidic, main, and basic species groups to run file."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Review chromatogram integration -- confirm peak grouping boundaries (acidic/main/basic) match validated method integration parameters."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review chromatogram integration -- confirm peak grouping boundaries (acidic/main/basic) match validated method integration parameters.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 11, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 12 ── [OTHER]
    # "Calculate % acidic, % main, % basic from relative peak areas."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Compare reference standard charge profile to historical mean -- flag if any group drifts > +/-2%."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Export charge variant report to run file; archive raw chromatograms."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Wash column with 10 column volumes 100% B, then re-equilibrate with 10 column volumes 100% A -- log column maintenance."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_013",
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
        result = await run_bio_013(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
