"""
BioInterface — Auto-generated Protocol
Assay    : HTS_009 — Kinase activity assay — ADP-Glo luminescent
Field    : Drug Discovery / HTS
Workbench: WB1
Robot min: 25 | Total hours: 3
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
    "A1": {"slot": 1, "description": "Compound dilution plate (384-well)"},
    "B1": {"slot": 7, "description": "384-well white low-volume plate"},
    "C1": {"slot": 13, "description": "Tris buffer pH 7.5"},
    "C2": {"slot": 14, "description": "MgCl₂ solution"},
    "C3": {"slot": 15, "description": "BSA solution"},
    "C4": {"slot": 16, "description": "DTT solution"},
    "C5": {"slot": 17, "description": "Peptide substrate (kinase-specific)"},
    "C6": {"slot": 18, "description": "ATP solution (Km concentration)"},
    "C7": {"slot": 19, "description": "Kinase enzyme solution (on ice at D2)"},
    "C8": {"slot": 20, "description": "ADP-Glo reagent (Promega)"},
    "C9": {"slot": 21, "description": "Kinase Detection reagent (Promega)"},
    "D2": {"slot": 26, "description": "Ice bucket"},
    "G1": {"slot": 37, "description": "Luminescence plate reader"},
    "H1": {"slot": 43, "description": "Plate incubator (37°C)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "z_factor": "Z' ≥ 0.5 between full activity and full inhibition controls",
    "signal_window": "≥ 5-fold RLU difference between vehicle and no-enzyme controls",
    "atp_conversion": "≥ 20% and ≤ 80% substrate conversion in vehicle control (linear range)",
    "positive_control_inhibition": "≥ 90% inhibition by known ATP-competitive inhibitor",
    "hit_threshold": "≥ 50% inhibition at primary screening concentration",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_009(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Kinase activity assay — ADP-Glo luminescent

    Purpose    : Measure kinase inhibitor potency by quantifying ADP produced during the phosphorylation reaction using a coupled luminescent assay (ADP-Glo).
    Workbench  : WB1
    Robot time : 25 minutes active
    Total time : 3 hours
    Throughput : 352 samples/run
    Difficulty : medium
    AutoMATE 96: head=1-20uL, tagged_steps=5/15
    Regulatory : ICH Q6A, Eurofins kinase selectivity panel standards
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_009: Kinase activity assay — ADP-Glo luminescent")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Prepare kinase reaction buffer: 40 mM Tris pH 7.5, 20 mM MgCl₂, 0.1 mg/mL BSA, 50 µM DTT from reagents at positions C1–C4 — prepare fresh, keep on ice."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Prepare substrate/ATP mixture: peptide substrate at Km concentration + ATP at Km concentration in kinase buffer from positions C5 and C6."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [LIQUID_HANDLER]
    # "Dispense 2 µL compound dilutions from position A1 into 384-well white low-volume plate at position B1."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[2] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 3, "action": "LIQUID_HANDLER", "volume_uL": 2, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 4 ── [LIQUID_HANDLER]
    # "Add 2 µL kinase enzyme solution (at 2× Km) from position C7 (on ice) to all wells except no-enzyme controls (column 24)."
    await lh.dispense(
        resource=DECK_LAYOUT["C7"]["slot"],
        vols=[2] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 4, "action": "LIQUID_HANDLER", "volume_uL": 2, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Add 2 µL substrate/ATP mixture to all wells — mix by tapping plate."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[2] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 2, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 6 ── [WAIT]
    # "Incubate kinase reaction at 37°C for 60 minutes at position H1; log start time."
    print(f"[{run_id}] Step 6: waiting 3600s — robot free for other tasks")
    await asyncio.sleep(3600)
    log.append({"step": 6, "action": "WAIT", "duration_seconds": 3600, "status": "complete"})

    # ── STEP 7 ── [LIQUID_HANDLER]
    # "Add 4 µL ADP-Glo reagent from position C8 to all wells — this depletes remaining ATP."
    await lh.dispense(
        resource=DECK_LAYOUT["C8"]["slot"],
        vols=[4] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 7, "action": "LIQUID_HANDLER", "volume_uL": 4, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 8 ── [WAIT]
    # "Incubate at room temperature for 40 minutes; log start time."
    print(f"[{run_id}] Step 8: waiting 2400s — robot free for other tasks")
    await asyncio.sleep(2400)
    log.append({"step": 8, "action": "WAIT", "duration_seconds": 2400, "status": "complete"})

    # ── STEP 9 ── [LIQUID_HANDLER]
    # "Add 8 µL Kinase Detection reagent from position C9 to all wells — converts ADP to ATP which drives luciferase reaction."
    await lh.dispense(
        resource=DECK_LAYOUT["C9"]["slot"],
        vols=[8] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 9, "action": "LIQUID_HANDLER", "volume_uL": 8, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 10 ── [WAIT]
    # "Incubate at room temperature for 30 minutes; log start time."
    print(f"[{run_id}] Step 10: waiting 1800s — robot free for other tasks")
    await asyncio.sleep(1800)
    log.append({"step": 10, "action": "WAIT", "duration_seconds": 1800, "status": "complete"})

    # ── STEP 11 ── [TRANSPORT]
    # "Transfer plate to luminescence reader at position G1 — read luminescence (no filter, 1 s integration)."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 11, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 12 ── [OTHER]
    # "Calculate % inhibition: (1 — (RLU_sample − RLU_no_enzyme) / (RLU_DMSO − RLU_no_enzyme)) × 100."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Calculate Z-factor from DMSO vehicle (full activity) and staurosporine positive control (full inhibition)."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Review Z-factor and confirm assay window > 5-fold signal between vehicle and maximum inhibition before calling hits."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review Z-factor and confirm assay window > 5-fold signal between vehicle and maximum inhibition before calling hits.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 14, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 15 ── [OTHER]
    # "Export luminescence data, % inhibition, Z-factor, and IC50 values to run file."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_009",
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
        result = await run_hts_009(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
