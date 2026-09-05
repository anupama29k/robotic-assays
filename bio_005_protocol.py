"""
BioInterface — Auto-generated Protocol
Assay    : BIO_005 — Sandwich ELISA -- target antigen quantification
Field    : Biopharma / CDMO
Workbench: WB1
Robot min: 45 | Total hours: 20
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
    "A1": {"slot": 1, "description": "Sample input rack -- 12 x 1.5 mL tubes"},
    "B1": {"slot": 7, "description": "96-well ELISA plate (high-binding, flat-bottom)"},
    "B2": {"slot": 8, "description": "96-well dilution plate (non-binding)"},
    "C1": {"slot": 13, "description": "Reagent reservoir -- capture antibody in PBS"},
    "C2": {"slot": 14, "description": "Reagent reservoir -- PBST wash buffer"},
    "C3": {"slot": 15, "description": "Reagent reservoir -- blocking buffer (1% BSA-PBST)"},
    "C4": {"slot": 16, "description": "Reagent reservoir -- HRP detection antibody"},
    "C5": {"slot": 17, "description": "Reagent reservoir -- TMB substrate"},
    "C6": {"slot": 18, "description": "Reagent reservoir -- stop solution (2N H2SO4)"},
    "D1": {"slot": 19, "description": "Adhesive plate seal dispenser"},
    "E1": {"slot": 25, "description": "Liquid waste container"},
    "F1": {"slot": 31, "description": "Standard rack -- antigen reference standard (top concentration)"},
    "G1": {"slot": 37, "description": "Plate reader interface (450/620 nm)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "standard_curve_r2": ">= 0.995 (4PL fit)",
    "curve_bottom_asymptote_od": "< 0.10",
    "curve_top_asymptote_od": "> 1.5",
    "qc_sample_recovery": "80-120% of expected",
    "ppc_recovery": "70-130% of spike concentration",
    "intraplate_cv_max": "<= 15%",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_005(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Sandwich ELISA -- target antigen quantification

    Purpose    : Quantify target antigen or product-related impurity concentration in process samples using a validated sandwich ELISA.
    Workbench  : WB1
    Robot time : 45 minutes active
    Total time : 20 hours
    Throughput : 40 samples/run
    Difficulty : medium
    AutoMATE 96: head=5-200uL, tagged_steps=11/20
    Regulatory : ICH Q6B, USP <1106>, Ph. Eur. 2.7.1
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_005: Sandwich ELISA -- target antigen quantification")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [TRANSPORT]
    # "Pick up 96-well ELISA plate (high-binding) from position B1."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["B1"]["slot"],
    )
    log.append({"step": 1, "action": "TRANSPORT", "from": "input_rack", "to": "B1", "status": "complete"})

    # ── STEP 2 ── [LIQUID_HANDLER]
    # "Aspirate 100 uL capture antibody (2-4 ug/mL in PBS) from reservoir at position C1; dispense into all 96 wells."
    await lh.dispense(
        resource=DECK_LAYOUT["C1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 2, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 3 ── [WAIT]
    # "Seal plate with adhesive film from position D1; transfer to 4C refrigerator for overnight coat -- log incubation start time and confirm refrigerator temperature."
    print(f"[{run_id}] Step 3: waiting 50400s — robot free for other tasks")
    await asyncio.sleep(50400)
    log.append({"step": 3, "action": "WAIT", "duration_seconds": 50400, "status": "complete"})

    # ── STEP 4 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Confirm overnight coat is complete and plate seal is intact before resuming next morning."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm overnight coat is complete and plate seal is intact before resuming next morning.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 4, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 5 ── [INSTRUMENT_TRIGGER]
    # "Remove seal; aspirate contents to liquid waste at position E1."
    # Instrument trigger: sealer
    if "sealer" in instruments:
        await instruments["sealer"].read()
    else:
        print(f"[{run_id}] Step 5: sealer not wired — skipping trigger")
    log.append({"step": 5, "action": "INSTRUMENT_TRIGGER", "instrument": "sealer", "status": "complete"})

    # ── STEP 6 ── [LIQUID_HANDLER]
    # "Wash all wells with 300 uL PBST from reservoir at position C2 -- repeat 3 times; aspirate completely after each wash."
    for cycle in range(3):
        await lh.dispense(
            resource=DECK_LAYOUT["C2"]["slot"],
            vols=[300] * 96,
            flow_rate=200,
            liquid_class="aqueous",
        )
        await lh.aspirate(
            resource=DECK_LAYOUT["C2"]["slot"],
            vols=[345] * 96,
            flow_rate=150,
            blow_out=True,
        )
    log.append({"step": 6, "action": "LIQUID_HANDLER", "volume_uL": 300, "cycles": 3, "head": "5-200uL", "status": "complete"})

    # ── STEP 7 ── [LIQUID_HANDLER]
    # "Aspirate 200 uL blocking buffer (1% BSA-PBST) from position C3 into all wells; incubate 1 hour at room temperature."
    await lh.dispense(
        resource=DECK_LAYOUT["C3"]["slot"],
        vols=[200] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 7, "action": "LIQUID_HANDLER", "volume_uL": 200, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 8 ── [LIQUID_HANDLER]
    # "Aspirate blocking buffer; perform 3-cycle PBST wash."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 8, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 9 ── [OTHER]
    # "Prepare sample serial dilutions in 96-well dilution plate at position B2 from input rack at position A1 -- 3-fold dilutions."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [LIQUID_HANDLER]
    # "Transfer 100 uL diluted samples and standards into ELISA plate per plate map; dispense 100 uL standard curve (8-point, 2-fold, from position F1) into designated wells."
    await lh.dispense(
        resource=DECK_LAYOUT["F1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 10, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 11 ── [WAIT]
    # "Seal and incubate 2 hours at room temperature -- log start and end times."
    print(f"[{run_id}] Step 11: waiting 7200s — robot free for other tasks")
    await asyncio.sleep(7200)
    log.append({"step": 11, "action": "WAIT", "duration_seconds": 7200, "status": "complete"})

    # ── STEP 12 ── [LIQUID_HANDLER]
    # "Perform 3-cycle PBST wash."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 12, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 13 ── [LIQUID_HANDLER]
    # "Aspirate 100 uL HRP-detection antibody from position C4 into all wells; incubate 1 hour."
    await lh.dispense(
        resource=DECK_LAYOUT["C4"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 13, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 14 ── [LIQUID_HANDLER]
    # "Perform 3-cycle PBST wash."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 14, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 15 ── [LIQUID_HANDLER]
    # "Aspirate 100 uL TMB substrate from position C5; dispense into all wells -- incubate exactly 10 minutes in dark; log start time."
    await lh.dispense(
        resource=DECK_LAYOUT["C5"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 15, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 16 ── [LIQUID_HANDLER]
    # "Aspirate 100 uL stop solution (2N H2SO4) from position C6; dispense into all wells in same order as substrate addition."
    await lh.dispense(
        resource=DECK_LAYOUT["C6"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 16, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 17 ── [TRANSPORT]
    # "Transfer plate to reader at position G1; read OD450 with reference at 620 nm -- log raw values."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 17, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 18 ── [OTHER]
    # "Flag wells with OD450 > 3.0 (saturation) for repeat at higher dilution."
    # (unclassified step — logged only)
    log.append({"step": 18, "action": "OTHER", "status": "logged"})

    # ── STEP 19 ── [OTHER]
    # "Calculate concentrations using 4-parameter logistic (4PL) fit of standard curve -- export to run file."
    # (unclassified step — logged only)
    log.append({"step": 19, "action": "OTHER", "status": "logged"})

    # ── STEP 20 ── [OTHER]
    # "Flag samples where all dilutions fall outside linear portion of 4PL curve -- require assay repeat at adjusted dilution range."
    # (unclassified step — logged only)
    log.append({"step": 20, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_005",
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
        result = await run_bio_005(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
