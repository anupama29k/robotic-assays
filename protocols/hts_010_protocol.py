"""
BioInterface — Auto-generated Protocol
Assay    : HTS_010 — Reporter gene assay — luciferase
Field    : Drug Discovery / HTS
Workbench: WB2
Robot min: 35 | Total hours: 28
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
    "A1": {"slot": 1, "description": "Cell suspension tube (15 mL conical)"},
    "A2": {"slot": 2, "description": "Compound dilution plate (HTS_001 output)"},
    "B1": {"slot": 7, "description": "96-well white TC plate (cells)"},
    "C1": {"slot": 13, "description": "Luciferase detection reagent (ONE-Glo or Bright-Glo, Promega)"},
    "E1": {"slot": 25, "description": "Biological waste + bleach"},
    "F1": {"slot": 31, "description": "Agonist positive control solution"},
    "F2": {"slot": 38, "description": "DMSO vehicle control"},
    "G1": {"slot": 37, "description": "Luminescence plate reader"},
    "H1": {"slot": 43, "description": "CO₂ incubator (37°C, 5%)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "agonist_fold_induction": "≥ 5-fold over vehicle control",
    "z_factor": "Z' ≥ 0.5 between agonist maximum and vehicle basal",
    "vehicle_control_cv": "≤ 15% CV",
    "signal_stability": "Luminescence reading within 10 minutes of reagent addition (Bright-Glo decays rapidly)",
    "cytotoxicity_counter_screen": "All hits must be counter-screened with HTS_005 LDH assay",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_010(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Reporter gene assay — luciferase

    Purpose    : Measure compound effect on transcriptional activity of a target promoter using stably or transiently transfected luciferase reporter cells.
    Workbench  : WB2
    Robot time : 35 minutes active
    Total time : 28 hours
    Throughput : 80 samples/run
    Difficulty : medium
    AutoMATE 96: head=5-200uL, tagged_steps=3/16
    Regulatory : ICH S7A, FDA guidance on reporter gene assays
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_010: Reporter gene assay — luciferase")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Retrieve reporter cell line from liquid nitrogen — thaw and resuspend in complete medium at position A1."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [INSTRUMENT_TRIGGER]
    # "Count cells and dilute to 200,000 cells/mL in complete medium — dispense 100 µL per well (20,000 cells/well) into 96-well white TC plate at position B1."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 2: generic not wired — skipping trigger")
    log.append({"step": 2, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 3 ── [WAIT]
    # "Incubate 24 hours at 37°C, 5% CO₂ at position H1 for attachment; log start time."
    print(f"[{run_id}] Step 3: waiting 86400s — robot free for other tasks")
    await asyncio.sleep(86400)
    log.append({"step": 3, "action": "WAIT", "duration_seconds": 86400, "status": "complete"})

    # ── STEP 4 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Confirm cell density and morphology under microscope — reporter cells must be at 60–70% confluency for optimal signal."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm cell density and morphology under microscope — reporter cells must be at 60–70% confluency for optimal signal.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 4, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Add 100 µL compound dilutions from position A2 to cell plate — include agonist positive control (known pathway activator, position F1) and DMSO vehicle control (column 12)."
    await lh.dispense(
        resource=DECK_LAYOUT["F1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 6 ── [WAIT]
    # "Incubate 18–24 hours at 37°C, 5% CO₂; log start time."
    print(f"[{run_id}] Step 6: waiting 86400s — robot free for other tasks")
    await asyncio.sleep(86400)
    log.append({"step": 6, "action": "WAIT", "duration_seconds": 86400, "status": "complete"})

    # ── STEP 7 ── [OTHER]
    # "Remove medium carefully by aspiration — leave cells intact."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [LIQUID_HANDLER]
    # "Add 100 µL ONE-Glo or Bright-Glo luciferase reagent from position C1 to all wells."
    await lh.dispense(
        resource=DECK_LAYOUT["C1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 8, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 9 ── [WAIT]
    # "Incubate at room temperature for 3 minutes — cells lyse and luciferase reacts with substrate."
    print(f"[{run_id}] Step 9: waiting 180s — robot free for other tasks")
    await asyncio.sleep(180)
    log.append({"step": 9, "action": "WAIT", "duration_seconds": 180, "status": "complete"})

    # ── STEP 10 ── [TRANSPORT]
    # "Transfer plate to luminescence reader at position G1 — read within 10 minutes of reagent addition (signal decays rapidly with Bright-Glo)."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 10, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 11 ── [OTHER]
    # "Calculate fold-induction: RLU_sample / RLU_vehicle_control."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [OTHER]
    # "For inhibitor screens: calculate % inhibition relative to agonist-stimulated positive control."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Calculate Z-factor from agonist-stimulated (maximum signal) and vehicle (basal signal) controls."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Check fold-induction of agonist control (should be ≥ 5-fold) — low fold-induction indicates poor assay window or cell health issues."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Check fold-induction of agonist control (should be ≥ 5-fold) — low fold-induction indicates poor assay window or cell health issues.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 14, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 15 ── [OTHER]
    # "Export luminescence data, fold-induction, Z-factor, and hit list to run file."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    # ── STEP 16 ── [OTHER]
    # "Decontaminate plates with 10% bleach before disposal — log decontamination."
    # (unclassified step — logged only)
    log.append({"step": 16, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_010",
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
        result = await run_hts_010(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
