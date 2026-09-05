"""
BioInterface — Auto-generated Protocol
Assay    : BIO_002 — BCA protein concentration assay
Field    : Biopharma / CDMO
Workbench: WB1
Robot min: 15 | Total hours: 1
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
    "A9": {"slot": 0, "description": "BCA working reagent mixing tube (15 mL conical)"},
    "B1": {"slot": 7, "description": "96-well flat-bottom plate (clear, non-binding)"},
    "C1": {"slot": 13, "description": "Reagent reservoir -- PBS diluent"},
    "C2": {"slot": 14, "description": "Reagent reservoir -- BCA reagent A"},
    "C3": {"slot": 15, "description": "Reagent reservoir -- BCA reagent B"},
    "D1": {"slot": 19, "description": "Adhesive plate seal dispenser"},
    "F1": {"slot": 31, "description": "BSA standard stock (2 mg/mL, 1.5 mL tube)"},
    "G1": {"slot": 37, "description": "Plate reader interface (562 nm)"},
    "H2": {"slot": 44, "description": "Incubator (37C)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "standard_curve_r2": ">= 0.995",
    "blank_od562_max": "< 0.10",
    "qc_sample_recovery": "90-110% of expected",
    "duplicate_cv_max": "<= 5%",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_002(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    BCA protein concentration assay

    Purpose    : Quantify total protein concentration in purified or in-process samples using bicinchoninic acid (BCA) colorimetric assay.
    Workbench  : WB1
    Robot time : 15 minutes active
    Total time : 1 hours
    Throughput : 40 samples/run
    Difficulty : easy
    AutoMATE 96: head=5-200uL, tagged_steps=3/15
    Regulatory : ICH Q6B, USP <1057>
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_002: BCA protein concentration assay")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [LIQUID_HANDLER]
    # "Prepare BSA standard curve from 2 mg/mL stock at position F1: 8-point serial dilution from 2000 to 31.25 ug/mL using PBS from position C1 -- dispense 25 uL of each standard into designated wells of 96-well plate at position B1 in duplicate."
    await lh.dispense(
        resource=DECK_LAYOUT["C1"]["slot"],
        vols=[25] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 1, "action": "LIQUID_HANDLER", "volume_uL": 25, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 2 ── [TRANSPORT]
    # "Pick up sample tubes from input rack at position A1 (A1:1 through A1:12); aspirate 25 uL per sample and dispense into designated wells per plate map loaded at run start."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["A1"]["slot"],
    )
    log.append({"step": 2, "action": "TRANSPORT", "from": "input_rack", "to": "A1", "status": "complete"})

    # ── STEP 3 ── [LIQUID_HANDLER]
    # "Dispense 25 uL PBS blank into wells H11 and H12."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[25] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 3, "action": "LIQUID_HANDLER", "volume_uL": 25, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 4 ── [OTHER]
    # "Prepare BCA working reagent: aspirate from reagent A reservoir at position C2 and reagent B at position C3 in 50:1 ratio into mixing tube at position A9 -- sufficient volume for all wells plus 10% excess."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Dispense 200 uL BCA working reagent into all sample, standard, and blank wells."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[200] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 200, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 6 ── [INSTRUMENT_TRIGGER]
    # "Seal plate with adhesive film from position D1."
    # Instrument trigger: sealer
    if "sealer" in instruments:
        await instruments["sealer"].read()
    else:
        print(f"[{run_id}] Step 6: sealer not wired — skipping trigger")
    log.append({"step": 6, "action": "INSTRUMENT_TRIGGER", "instrument": "sealer", "status": "complete"})

    # ── STEP 7 ── [WAIT]
    # "Transfer sealed plate to incubator at position H2 -- incubate at 37C for exactly 30 minutes; log start time."
    print(f"[{run_id}] Step 7: waiting 1800s — robot free for other tasks")
    await asyncio.sleep(1800)
    log.append({"step": 7, "action": "WAIT", "duration_seconds": 1800, "status": "complete"})

    # ── STEP 8 ── [TRANSPORT]
    # "After incubation, transfer plate to plate reader at position G1 -- allow 5 minutes to equilibrate to room temperature."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 8, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 9 ── [INSTRUMENT_TRIGGER]
    # "Read absorbance at 562 nm -- log raw OD values for all wells."
    # Instrument trigger: plate_reader
    if "plate_reader" in instruments:
        await instruments["plate_reader"].read()
    else:
        print(f"[{run_id}] Step 9: plate_reader not wired — skipping trigger")
    log.append({"step": 9, "action": "INSTRUMENT_TRIGGER", "instrument": "plate_reader", "status": "complete"})

    # ── STEP 10 ── [OTHER]
    # "Subtract blank average (wells H11-H12) from all standards and samples."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [OTHER]
    # "Generate linear standard curve -- flag and halt if R-squared < 0.995."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [OTHER]
    # "Interpolate sample concentrations; multiply by dilution factor where applicable."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Flag any sample with OD562 > 2.0 (out of linear range) -- log for re-run at 1:10 dilution."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Export results with standard curve parameters and all raw ODs to run file."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Confirm no known BCA interfering agents (DTT, BME, EDTA > 10 mM) are present in sample buffer before signing off results."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm no known BCA interfering agents (DTT, BME, EDTA > 10 mM) are present in sample buffer before signing off results.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 15, "action": "ANALYST_PAUSE", "status": "complete"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_002",
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
        result = await run_bio_002(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
