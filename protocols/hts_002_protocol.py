"""
BioInterface — Auto-generated Protocol
Assay    : HTS_002 — 96-well ELISA — target binding / inhibition assay
Field    : Drug Discovery / HTS
Workbench: WB1
Robot min: 40 | Total hours: 4
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
    "A1": {"slot": 1, "description": "Compound dilution plate (HTS_001 output)"},
    "B1": {"slot": 7, "description": "Pre-coated ELISA plate (96-well, high-binding)"},
    "C1": {"slot": 13, "description": "PBST wash buffer reservoir (100 mL)"},
    "C2": {"slot": 14, "description": "Blocking buffer reservoir — 3% BSA-PBST"},
    "C3": {"slot": 15, "description": "Labelled ligand reservoir"},
    "C4": {"slot": 16, "description": "HRP-streptavidin conjugate reservoir"},
    "C5": {"slot": 17, "description": "TMB substrate reservoir"},
    "C6": {"slot": 18, "description": "Stop solution reservoir — 2N H₂SO₄"},
    "D1": {"slot": 19, "description": "Adhesive plate seal dispenser"},
    "E1": {"slot": 25, "description": "Liquid waste container"},
    "F1": {"slot": 31, "description": "Positive control — known inhibitor (reference compound)"},
    "F2": {"slot": 38, "description": "Negative control — DMSO vehicle"},
    "G1": {"slot": 37, "description": "Plate reader interface (450/620 nm)"},
    "H1": {"slot": 43, "description": "Rocking platform mixer"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "z_factor": "Z' ≥ 0.5 (excellent); 0–0.5 marginal (flag); < 0 invalid (reject plate)",
    "signal_to_background": "≥ 3-fold (OD_max / OD_nonspecific)",
    "positive_control_inhibition": "≥ 80% inhibition",
    "negative_control_cv": "≤ 10% CV across vehicle control wells",
    "hit_threshold": "≥ 50% inhibition (primary screen); confirm at ≥ 3 concentrations",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_002(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    96-well ELISA — target binding / inhibition assay

    Purpose    : Screen compound libraries for inhibition or modulation of a target protein-ligand interaction using a competitive or sandwich ELISA format.
    Workbench  : WB1
    Robot time : 40 minutes active
    Total time : 4 hours
    Throughput : 80 samples/run
    Difficulty : medium
    AutoMATE 96: head=5-200uL, tagged_steps=10/18
    Regulatory : ICH Q6A, FDA guidance on bioanalytical method validation
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_002: 96-well ELISA — target binding / inhibition assay")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [TRANSPORT]
    # "Pick up pre-coated 96-well ELISA plate (target protein, 4 µg/mL overnight coat) from position B1."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["B1"]["slot"],
    )
    log.append({"step": 1, "action": "TRANSPORT", "from": "input_rack", "to": "B1", "status": "complete"})

    # ── STEP 2 ── [LIQUID_HANDLER]
    # "Wash plate 3 times with 300 µL PBST from reservoir at position C1 — aspirate completely after each wash."
    for cycle in range(3):
        await lh.dispense(
            resource=DECK_LAYOUT["C1"]["slot"],
            vols=[300] * 96,
            flow_rate=200,
            liquid_class="aqueous",
        )
        await lh.aspirate(
            resource=DECK_LAYOUT["C1"]["slot"],
            vols=[345] * 96,
            flow_rate=150,
            blow_out=True,
        )
    log.append({"step": 2, "action": "LIQUID_HANDLER", "volume_uL": 300, "cycles": 3, "head": "5-200uL", "status": "complete"})

    # ── STEP 3 ── [LIQUID_HANDLER]
    # "Add 200 µL blocking buffer (3% BSA-PBST) from position C2 to all wells — incubate 60 minutes at room temperature; log start time."
    await lh.dispense(
        resource=DECK_LAYOUT["C2"]["slot"],
        vols=[200] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 3, "action": "LIQUID_HANDLER", "volume_uL": 200, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 4 ── [LIQUID_HANDLER]
    # "Wash plate 3 times with PBST."
    for cycle in range(3):
        await lh.dispense(
            resource=DECK_LAYOUT["B1"]["slot"],
            vols=[100] * 96,
            flow_rate=200,
            liquid_class="aqueous",
        )
        await lh.aspirate(
            resource=DECK_LAYOUT["B1"]["slot"],
            vols=[114] * 96,
            flow_rate=150,
            blow_out=True,
        )
    log.append({"step": 4, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 3, "head": "5-200uL", "status": "complete"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Transfer 50 µL of each compound dilution from dilution plate (HTS_001 output) at position A1 to corresponding ELISA plate wells."
    await lh.dispense(
        resource=DECK_LAYOUT["A1"]["slot"],
        vols=[50] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 50, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 6 ── [LIQUID_HANDLER]
    # "Add 50 µL labelled ligand (biotinylated or fluorescent) from position C3 to all wells — mix gently."
    await lh.dispense(
        resource=DECK_LAYOUT["C3"]["slot"],
        vols=[50] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 6, "action": "LIQUID_HANDLER", "volume_uL": 50, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 7 ── [WAIT]
    # "Incubate 90 minutes at room temperature with gentle agitation on rocker at position H1; log start time."
    print(f"[{run_id}] Step 7: waiting 5400s — robot free for other tasks")
    await asyncio.sleep(5400)
    log.append({"step": 7, "action": "WAIT", "duration_seconds": 5400, "status": "complete"})

    # ── STEP 8 ── [LIQUID_HANDLER]
    # "Wash plate 5 times with PBST — thorough washing is critical for signal-to-noise."
    for cycle in range(5):
        await lh.dispense(
            resource=DECK_LAYOUT["B1"]["slot"],
            vols=[100] * 96,
            flow_rate=200,
            liquid_class="aqueous",
        )
        await lh.aspirate(
            resource=DECK_LAYOUT["B1"]["slot"],
            vols=[114] * 96,
            flow_rate=150,
            blow_out=True,
        )
    log.append({"step": 8, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 5, "head": "5-200uL", "status": "complete"})

    # ── STEP 9 ── [LIQUID_HANDLER]
    # "Add 100 µL HRP-streptavidin (1:5000) from position C4 to all wells — incubate 30 minutes."
    await lh.dispense(
        resource=DECK_LAYOUT["C4"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 9, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 10 ── [LIQUID_HANDLER]
    # "Wash plate 5 times with PBST."
    for cycle in range(5):
        await lh.dispense(
            resource=DECK_LAYOUT["B1"]["slot"],
            vols=[100] * 96,
            flow_rate=200,
            liquid_class="aqueous",
        )
        await lh.aspirate(
            resource=DECK_LAYOUT["B1"]["slot"],
            vols=[114] * 96,
            flow_rate=150,
            blow_out=True,
        )
    log.append({"step": 10, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 5, "head": "5-200uL", "status": "complete"})

    # ── STEP 11 ── [LIQUID_HANDLER]
    # "Add 100 µL TMB substrate from position C5 — develop exactly 10 minutes in dark; log start time."
    await lh.dispense(
        resource=DECK_LAYOUT["C5"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 11, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 12 ── [LIQUID_HANDLER]
    # "Add 100 µL stop solution (2N H₂SO₄) from position C6 in same order as substrate addition."
    await lh.dispense(
        resource=DECK_LAYOUT["C6"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 12, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 13 ── [TRANSPORT]
    # "Transfer plate to plate reader at position G1 — read OD450 with reference at 620 nm; log raw values."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 13, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 14 ── [OTHER]
    # "Calculate % inhibition per well: (1 — (OD_sample — OD_nonspecific) / (OD_max — OD_nonspecific)) × 100."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Calculate Z-factor from positive (known inhibitor, position F1) and negative (DMSO vehicle, column 12) controls."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    # ── STEP 16 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Review Z-factor — if Z' < 0.5 the plate is marginal; if Z' < 0 the plate is invalid. Do not proceed with hit calling on invalid plates."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review Z-factor — if Z' < 0.5 the plate is marginal; if Z' < 0 the plate is invalid. Do not proceed with hit calling on invalid plates.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 16, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 17 ── [OTHER]
    # "Flag all wells with % inhibition ≥ 50% as primary hits — export hit list to run file."
    # (unclassified step — logged only)
    log.append({"step": 17, "action": "OTHER", "status": "logged"})

    # ── STEP 18 ── [OTHER]
    # "Export full plate data with Z-factor, signal-to-background, and all raw OD values."
    # (unclassified step — logged only)
    log.append({"step": 18, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_002",
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
        result = await run_hts_002(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
