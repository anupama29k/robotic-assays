"""
BioInterface — Auto-generated Protocol
Assay    : HTS_007 — HTRF TR-FRET homogeneous binding assay
Field    : Drug Discovery / HTS
Workbench: WB1
Robot min: 20 | Total hours: 2.5
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
    "A1": {"slot": 1, "description": "Compound source plate (384-well or Echo-compatible)"},
    "B1": {"slot": 7, "description": "384-well white low-volume plate (non-binding)"},
    "C1": {"slot": 13, "description": "Donor-labelled protein reservoir (light-protected, on ice)"},
    "C2": {"slot": 14, "description": "Acceptor-labelled tracer reservoir (light-protected, on ice)"},
    "D1": {"slot": 19, "description": "Foil plate seal dispenser"},
    "D2": {"slot": 26, "description": "Ice bucket for protein/tracer storage"},
    "E1": {"slot": 25, "description": "Liquid waste container"},
    "G1": {"slot": 37, "description": "HTRF-compatible TR-FRET plate reader (337/620/665 nm)"},
    "H1": {"slot": 43, "description": "Plate hotel/stacker"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "z_factor": "Z' ≥ 0.5 (HTRF assays often achieve Z' > 0.7 — flag if below 0.5)",
    "signal_window": "HTRF ratio max/min ratio ≥ 2 (delta ratio ≥ 2,000)",
    "cv_controls": "≤ 10% CV across both maximum and minimum FRET control wells",
    "compound_fluorescence_check": "Flag wells with emission 665 nm > 2× mean — potential fluorescent compound interference",
    "hit_threshold": "≥ 50% displacement at screening concentration",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_007(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    HTRF TR-FRET homogeneous binding assay

    Purpose    : Measure compound displacement of labelled ligand from target protein using homogeneous time-resolved FRET (HTRF) in 384-well format without wash steps.
    Workbench  : WB1
    Robot time : 20 minutes active
    Total time : 2.5 hours
    Throughput : 352 samples/run
    Difficulty : medium
    AutoMATE 96: head=1-20uL, tagged_steps=3/15
    Regulatory : ICH Q6A
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_007: HTRF TR-FRET homogeneous binding assay")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Pre-warm all HTRF reagents to room temperature for 30 minutes before use — log temperature equilibration start."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Load 384-well white low-volume plate at position B1 from plate hotel at position H1."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [LIQUID_HANDLER]
    # "Dispense 5 µL compound dilutions from compound source at position A1 to each assay well using 384-channel nanolitre dispenser."
    await lh.dispense(
        resource=DECK_LAYOUT["A1"]["slot"],
        vols=[5] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 3, "action": "LIQUID_HANDLER", "volume_uL": 5, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 4 ── [LIQUID_HANDLER]
    # "Add 5 µL donor-labelled target protein (Eu-cryptate or Tb-labelled) from reservoir at position C1 to all wells."
    await lh.dispense(
        resource=DECK_LAYOUT["C1"]["slot"],
        vols=[5] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 4, "action": "LIQUID_HANDLER", "volume_uL": 5, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Add 5 µL acceptor-labelled tracer (d2-labelled ligand) from reservoir at position C2 to all wells."
    await lh.dispense(
        resource=DECK_LAYOUT["C2"]["slot"],
        vols=[5] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 5, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 6 ── [INSTRUMENT_TRIGGER]
    # "Seal plate with foil seal from position D1 — protect from light immediately."
    # Instrument trigger: sealer
    if "sealer" in instruments:
        await instruments["sealer"].read()
    else:
        print(f"[{run_id}] Step 6: sealer not wired — skipping trigger")
    log.append({"step": 6, "action": "INSTRUMENT_TRIGGER", "instrument": "sealer", "status": "complete"})

    # ── STEP 7 ── [WAIT]
    # "Incubate at room temperature for 2 hours (or overnight at 4°C for tighter binders); log start time."
    print(f"[{run_id}] Step 7: waiting 50400s — robot free for other tasks")
    await asyncio.sleep(50400)
    log.append({"step": 7, "action": "WAIT", "duration_seconds": 50400, "status": "complete"})

    # ── STEP 8 ── [TRANSPORT]
    # "Transfer plate to HTRF-compatible plate reader at position G1 — read in time-resolved fluorescence mode: excitation 337 nm, emission 620 nm (donor) and 665 nm (acceptor); delay 50 µs; integration 200 µs."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 8, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 9 ── [OTHER]
    # "Calculate HTRF ratio: (emission 665 nm / emission 620 nm) × 10,000 per well."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [OTHER]
    # "Calculate % inhibition: (1 — (HTRF_sample — HTRF_min) / (HTRF_max − HTRF_min)) × 100."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [OTHER]
    # "Calculate Z-factor from maximum FRET (no inhibitor, column 1) and minimum FRET (competing unlabelled ligand, column 24) controls."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Review TR-FRET ratio distribution — confirm no fluorescence interference from compound library (some compounds are intrinsically fluorescent at 665 nm and cause false positives)."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review TR-FRET ratio distribution — confirm no fluorescence interference from compound library (some compounds are intrinsically fluorescent at 665 nm and cause false positives).",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 12, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Flag wells with HTRF ratio ≥ 3SD above assay window as potential false positives from fluorescent compounds."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Flag compounds with ≥ 50% displacement as primary hits."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Export HTRF ratios, % displacement, Z-factor, and hit list to run file."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_007",
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
        result = await run_hts_007(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
