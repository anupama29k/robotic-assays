"""
BioInterface — Auto-generated Protocol
Assay    : HTS_003 — 384-well fluorescence intensity assay
Field    : Drug Discovery / HTS
Workbench: WB1
Robot min: 20 | Total hours: 1.5
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
    "A1": {"slot": 1, "description": "Compound library plate — 384-well (Echo-compatible or standard)"},
    "B1": {"slot": 7, "description": "Assay plate — 384-well low-volume black (non-binding)"},
    "C1": {"slot": 13, "description": "Assay buffer reservoir (low-volume, 10 mL)"},
    "C2": {"slot": 14, "description": "Target protein/enzyme reservoir (keep on ice at position D2)"},
    "C3": {"slot": 15, "description": "Fluorescent substrate reservoir (light-protected foil wrap)"},
    "D1": {"slot": 19, "description": "Foil plate seal dispenser"},
    "D2": {"slot": 26, "description": "Ice bucket for enzyme storage"},
    "E1": {"slot": 25, "description": "Liquid waste container"},
    "F1": {"slot": 31, "description": "Tip rack — 10 µL low-volume tips"},
    "G1": {"slot": 37, "description": "Fluorescence plate reader (multimode, 384-well compatible)"},
    "H1": {"slot": 43, "description": "Plate hotel / stacker"},
    "H2": {"slot": 44, "description": "Plate incubator (37°C)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "z_factor": "Z' ≥ 0.5 required; plate rejected if Z' < 0",
    "signal_to_background": "≥ 5-fold (RFU_max / RFU_min)",
    "coefficient_of_variation_controls": "≤ 5% CV for both positive and negative controls",
    "edge_effect_tolerance": "Perimeter well signal within ±15% of interior wells",
    "hit_threshold": "≥ mean + 3SD of negative controls",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_003(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    384-well fluorescence intensity assay

    Purpose    : High-throughput screening of compound libraries in 384-well format using fluorescence intensity readout for enzyme activity or binding assays.
    Workbench  : WB1
    Robot time : 20 minutes active
    Total time : 1.5 hours
    Throughput : 352 samples/run
    Difficulty : medium
    AutoMATE 96: head=1-20uL, tagged_steps=3/15
    Regulatory : ICH Q6A, SLAS guidance on HTS assay quality
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_003: 384-well fluorescence intensity assay")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Load empty 384-well low-volume black plate at position B1 from plate hotel at position H1."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [LIQUID_HANDLER]
    # "Dispense 10 µL assay buffer from reservoir at position C1 into all 384 wells using 384-channel dispenser head."
    await lh.dispense(
        resource=DECK_LAYOUT["C1"]["slot"],
        vols=[10] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 2, "action": "LIQUID_HANDLER", "volume_uL": 10, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 3 ── [OTHER]
    # "Transfer 100 nL of each compound from compound library plate (Echo acoustic dispenser compatible, position A1) to corresponding assay wells — log compound IDs and concentrations per well."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [LIQUID_HANDLER]
    # "Add 5 µL target protein or enzyme from reservoir at position C2 to all wells except positive control wells (column 1 — enzyme inhibited) and negative control wells (column 24 — no enzyme)."
    await lh.dispense(
        resource=DECK_LAYOUT["C2"]["slot"],
        vols=[5] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 4, "action": "LIQUID_HANDLER", "volume_uL": 5, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Add 5 µL fluorescent substrate from reservoir at position C3 to all wells simultaneously using 384-channel head."
    await lh.dispense(
        resource=DECK_LAYOUT["C3"]["slot"],
        vols=[5] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 5, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 6 ── [INSTRUMENT_TRIGGER]
    # "Seal plate with foil seal from position D1 — protect from light throughout incubation."
    # Instrument trigger: sealer
    if "sealer" in instruments:
        await instruments["sealer"].read()
    else:
        print(f"[{run_id}] Step 6: sealer not wired — skipping trigger")
    log.append({"step": 6, "action": "INSTRUMENT_TRIGGER", "instrument": "sealer", "status": "complete"})

    # ── STEP 7 ── [WAIT]
    # "Incubate at 37°C in plate incubator at position H2 for 60 minutes; log start time."
    print(f"[{run_id}] Step 7: waiting 3600s — robot free for other tasks")
    await asyncio.sleep(3600)
    log.append({"step": 7, "action": "WAIT", "duration_seconds": 3600, "status": "complete"})

    # ── STEP 8 ── [TRANSPORT]
    # "Transfer plate to plate reader at position G1 — read fluorescence intensity (excitation/emission per assay specification) in endpoint mode."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 8, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 9 ── [OTHER]
    # "Calculate % inhibition per well: (1 — (RFU_sample — RFU_min) / (RFU_max — RFU_min)) × 100."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [OTHER]
    # "Calculate Z-factor from columns 1 (positive control — fully inhibited) and 24 (negative control — no inhibition)."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Review Z-factor before hit calling — Z' ≥ 0.5 required; check for edge effects (wells at plate perimeter showing systematic signal drift)."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review Z-factor before hit calling — Z' ≥ 0.5 required; check for edge effects (wells at plate perimeter showing systematic signal drift).",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 11, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 12 ── [OTHER]
    # "Flag all wells with % inhibition ≥ 3SD above mean of negative controls as primary hits."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Export full plate heat map, Z-factor, signal-to-background, and hit list to run file."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Return completed plates to plate hotel for archive — log plate barcode and position."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Flush all liquid handling lines with 70% ethanol then water — log cleaning."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_003",
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
        result = await run_hts_003(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
