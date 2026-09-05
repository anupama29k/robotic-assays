"""
BioInterface — Auto-generated Protocol
Assay    : HTS_001 — Compound serial dilution — 96-well format
Field    : Drug Discovery / HTS
Workbench: WB1
Robot min: 25 | Total hours: 0.5
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
    "A1": {"slot": 1, "description": "Compound source plate — 96-well, stock concentrations"},
    "B1": {"slot": 7, "description": "Dilution plate — 96-well U-bottom, non-binding"},
    "B2": {"slot": 8, "description": "Assay destination plate — 96-well"},
    "C1": {"slot": 13, "description": "Diluent reservoir — DMSO or assay buffer (50 mL)"},
    "D1": {"slot": 19, "description": "Adhesive plate seal dispenser"},
    "E1": {"slot": 25, "description": "Tip waste and liquid waste container"},
    "F1": {"slot": 31, "description": "Tip rack — 10 µL filtered tips (low-retention)"},
    "F2": {"slot": 38, "description": "Tip rack — 200 µL filtered tips"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "dmso_final_concentration": "≤ 0.1% v/v in assay well",
    "dilution_factor_verification": "Spectrophotometric check within ±15% of expected",
    "tip_change_compliance": "New tips for every column transfer — no carryover tolerance",
    "concentration_range_coverage": "Minimum 8 points spanning 3 log units",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_001(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Compound serial dilution — 96-well format

    Purpose    : Prepare accurate 2-fold, 3-fold, or 10-fold serial dilutions of test compounds in 96-well format for dose-response screening.
    Workbench  : WB1
    Robot time : 25 minutes active
    Total time : 0.5 hours
    Throughput : 80 samples/run
    Difficulty : easy
    AutoMATE 96: head=5-200uL, tagged_steps=5/15
    Regulatory : ICH Q3C (residual solvents), FDA guidance on HTS assay development
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_001: Compound serial dilution — 96-well format")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Load compound source plate (stock concentrations) from input rack at position A1 — confirm plate map is loaded in run file before starting."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [LIQUID_HANDLER]
    # "Load dilution plate (96-well, non-binding, U-bottom) at position B1 — pre-dispense 90 µL DMSO or assay buffer from reservoir at position C1 into all wells except column 1."
    await lh.dispense(
        resource=DECK_LAYOUT["C1"]["slot"],
        vols=[90] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 2, "action": "LIQUID_HANDLER", "volume_uL": 90, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 3 ── [LIQUID_HANDLER]
    # "Transfer 10 µL compound from each well in column 1 of source plate to column 1 of dilution plate — mix 10 times by pipetting; change tips between compounds."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[10] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 3, "action": "LIQUID_HANDLER", "volume_uL": 10, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 4 ── [LIQUID_HANDLER]
    # "Aspirate 10 µL from column 1 of dilution plate and dispense into column 2 — mix 10 times; discard tips."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[10] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 4, "action": "LIQUID_HANDLER", "volume_uL": 10, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Repeat serial transfer across columns 2 through 11 — change tips between each column transfer to prevent carryover."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[10] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 10, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 6 ── [OTHER]
    # "Column 12 receives diluent only — this is the vehicle control (0% compound, 100% DMSO/buffer)."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [OTHER]
    # "Verify dilution factor is consistent: spot-check column 1 and column 6 by UV absorbance at 280 nm if compound absorbs — log verification result."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Confirm DMSO concentration in final assay wells does not exceed 0.1% v/v — calculate from stock concentration and dilution factor before proceeding."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm DMSO concentration in final assay wells does not exceed 0.1% v/v — calculate from stock concentration and dilution factor before proceeding.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 8, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 9 ── [INSTRUMENT_TRIGGER]
    # "Seal dilution plate with adhesive film from position D1."
    # Instrument trigger: sealer
    if "sealer" in instruments:
        await instruments["sealer"].read()
    else:
        print(f"[{run_id}] Step 9: sealer not wired — skipping trigger")
    log.append({"step": 9, "action": "INSTRUMENT_TRIGGER", "instrument": "sealer", "status": "complete"})

    # ── STEP 10 ── [LIQUID_HANDLER]
    # "Transfer 10 µL from each well of dilution plate to assay plate at position B2 — maintain well-to-well correspondence per plate map."
    await lh.dispense(
        resource=DECK_LAYOUT["B2"]["slot"],
        vols=[10] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 10, "action": "LIQUID_HANDLER", "volume_uL": 10, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 11 ── [OTHER]
    # "Log final concentration range per compound to run file — top concentration, bottom concentration, dilution factor, number of points."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [OTHER]
    # "Export dilution plate map and concentration table to run file."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Store any remaining dilution plate at 4°C if immediate use is not planned — log storage time."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Discard tips and waste to appropriate containers at position E1."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Flag any wells where compound precipitate is visible — log for solubility investigation."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_001",
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
        result = await run_hts_001(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
