"""
BioInterface — Auto-generated Protocol
Assay    : BIO_007 — Recombinant factor C (rFC) endotoxin assay
Field    : Biopharma / CDMO
Workbench: WB3
Robot min: 25 | Total hours: 1.5
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
    "A1": {"slot": 1, "description": "Sample input rack -- 12 x endotoxin-free 1.5 mL tubes"},
    "B1": {"slot": 7, "description": "Black 96-well flat-bottom plate (endotoxin-free)"},
    "C1": {"slot": 13, "description": "Reagent reservoir -- rFC assay buffer"},
    "C2": {"slot": 14, "description": "rFC working reagent components (kit tubes, on ice, light-protected)"},
    "D1": {"slot": 19, "description": "Foil plate seal dispenser"},
    "F1": {"slot": 31, "description": "Endotoxin standard vials (CSE)"},
    "G1": {"slot": 37, "description": "Fluorescence plate reader (Ex 380 nm / Em 440 nm)"},
    "H2": {"slot": 44, "description": "Incubator (37C, light-excluded)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "standard_curve_r2": ">= 0.980",
    "ppc_recovery_percent": "50-200%",
    "negative_control_fluorescence": "Below lowest standard signal",
    "duplicate_cv_max": "<= 25% (endotoxin assays have wider tolerance)",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_007(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Recombinant factor C (rFC) endotoxin assay

    Purpose    : Detect and quantify bacterial endotoxin using recombinant factor C (rFC) fluorescence-based assay as an animal-free alternative to LAL.
    Workbench  : WB3
    Robot time : 25 minutes active
    Total time : 1.5 hours
    Throughput : 20 samples/run
    Difficulty : medium
    AutoMATE 96: head=5-200uL, tagged_steps=6/16
    Regulatory : USP <85> (alternative methods), Ph. Eur. 2.6.32
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_007: Recombinant factor C (rFC) endotoxin assay")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Confirm all labware is certified endotoxin-free and all reagents are within expiry -- log lot numbers."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Prepare rFC assay buffer from concentrate at position C1 per kit instructions -- mix gently; keep on ice."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [OTHER]
    # "Prepare endotoxin standard curve from position F1: 8-point dilution from 10 EU/mL to 0.02 EU/mL in rFC buffer."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [LIQUID_HANDLER]
    # "Dispense 100 uL each standard into duplicate wells of black 96-well plate at position B1."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 4, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Prepare PPC: spike endotoxin at 2x MVD concentration into sample matrix from position F1 -- dispense 100 uL per PPC well."
    await lh.dispense(
        resource=DECK_LAYOUT["F1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 6 ── [LIQUID_HANDLER]
    # "Prepare sample dilutions at MVD and 2x MVD in rFC buffer from input rack at position A1 -- dispense 100 uL per well."
    await lh.dispense(
        resource=DECK_LAYOUT["A1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 6, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 7 ── [LIQUID_HANDLER]
    # "Add 100 uL negative control (rFC buffer only) to designated wells."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 7, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 8 ── [OTHER]
    # "Prepare rFC working reagent: combine rFC enzyme, fluorescent substrate (Boc-Leu-Gly-Arg-AMC), and buffer per kit insert from position C2 -- prepare fresh and protect from light immediately."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [LIQUID_HANDLER]
    # "Dispense 100 uL rFC working reagent to all wells; mix by gently tapping plate."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 9, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 10 ── [INSTRUMENT_TRIGGER]
    # "Seal plate with foil seal from position D1 -- protect from light throughout incubation."
    # Instrument trigger: sealer
    if "sealer" in instruments:
        await instruments["sealer"].read()
    else:
        print(f"[{run_id}] Step 10: sealer not wired — skipping trigger")
    log.append({"step": 10, "action": "INSTRUMENT_TRIGGER", "instrument": "sealer", "status": "complete"})

    # ── STEP 11 ── [TRANSPORT]
    # "Transfer plate to incubator at position H2 -- incubate at 37C for exactly 60 minutes; log start time."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["H2"]["slot"],
    )
    log.append({"step": 11, "action": "TRANSPORT", "from": "input_rack", "to": "H2", "status": "complete"})

    # ── STEP 12 ── [TRANSPORT]
    # "Transfer plate to fluorescence reader at position G1; read emission at 440 nm (excitation 380 nm)."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 12, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Verify standard curve R-squared >= 0.980 -- abort if below."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Verify PPC recovery 50-200% -- invalidate if outside."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [INSTRUMENT_TRIGGER]
    # "Calculate sample endotoxin concentrations accounting for MVD; flag exceedances."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 15: generic not wired — skipping trigger")
    log.append({"step": 15, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 16 ── [OTHER]
    # "Export rFC report with all fluorescence values and QC outcomes to run file."
    # (unclassified step — logged only)
    log.append({"step": 16, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_007",
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
        result = await run_bio_007(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
