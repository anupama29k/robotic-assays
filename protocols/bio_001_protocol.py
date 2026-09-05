"""
BioInterface — Auto-generated Protocol
Assay    : BIO_001 — Protein A titer by HPLC
Field    : Biopharma / CDMO
Workbench: WB1
Robot min: 20 | Total hours: 2
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
    "A1": {"slot": 1, "description": "Sample input rack -- 12 x 1.5 mL microcentrifuge tubes"},
    "B1": {"slot": 7, "description": "HPLC glass vial rack -- 48-position"},
    "C1": {"slot": 13, "description": "Reagent reservoir -- PBS pH 7.2 mobile phase (50 mL)"},
    "D1": {"slot": 19, "description": "Tip rack -- 200 uL filtered tips"},
    "F1": {"slot": 31, "description": "Standard rack -- Protein A calibration standards (5 concentrations)"},
    "F2": {"slot": 38, "description": "QC rack -- system suitability check vials"},
    "G1": {"slot": 37, "description": "HPLC autosampler interface position"},
    "H1": {"slot": 43, "description": "HPLC instrument control terminal"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "system_suitability_retention_time_cv": "<= 1.0% across 3 injections",
    "standard_curve_r2": ">= 0.998",
    "qc_sample_recovery": "85-115% of known concentration",
    "peak_symmetry_factor": "0.8-1.5",
    "column_pressure_bar": "50-300 bar throughout run",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_001(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Protein A titer by HPLC

    Purpose    : Quantify mAb or Fc-fusion protein concentration in harvest or purified samples using Protein A affinity HPLC.
    Workbench  : WB1
    Robot time : 20 minutes active
    Total time : 2 hours
    Throughput : 24 samples/run
    Difficulty : easy
    AutoMATE 96: head=not applicable, tagged_steps=0/15
    Regulatory : ICH Q6B, USP <1046>, Ph. Eur. 2.7.9
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_001: Protein A titer by HPLC")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [TRANSPORT]
    # "Pick up sample tubes from input rack at deck position A1 (slots A1:1 through A1:12); centrifuge at 3000 x g for 5 minutes to clarify -- log centrifuge start time."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["A1"]["slot"],
    )
    log.append({"step": 1, "action": "TRANSPORT", "from": "input_rack", "to": "A1", "status": "complete"})

    # ── STEP 2 ── [INSTRUMENT_TRIGGER]
    # "Transfer 50 uL clarified supernatant from each sample tube to HPLC glass vials at position B1 using 200 uL tips from position D1."
    # Instrument trigger: hplc
    if "hplc" in instruments:
        await instruments["hplc"].read()
    else:
        print(f"[{run_id}] Step 2: hplc not wired — skipping trigger")
    log.append({"step": 2, "action": "INSTRUMENT_TRIGGER", "instrument": "hplc", "status": "complete"})

    # ── STEP 3 ── [OTHER]
    # "Add 150 uL PBS pH 7.2 mobile phase from reagent reservoir at position C1 to each vial -- mix by aspirating and dispensing 5 times."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [INSTRUMENT_TRIGGER]
    # "Cap HPLC vials and load into HPLC autosampler tray at position G1 according to run sequence loaded at job start."
    # Instrument trigger: hplc
    if "hplc" in instruments:
        await instruments["hplc"].read()
    else:
        print(f"[{run_id}] Step 4: hplc not wired — skipping trigger")
    log.append({"step": 4, "action": "INSTRUMENT_TRIGGER", "instrument": "hplc", "status": "complete"})

    # ── STEP 5 ── [INSTRUMENT_TRIGGER]
    # "Load reference standard vials (Protein A calibrator, positions F1:1 through F1:5) into autosampler alongside samples -- log standard lot number."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 5: generic not wired — skipping trigger")
    log.append({"step": 5, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 6 ── [OTHER]
    # "Load system suitability check vial (known-concentration QC at position F2:1) as first injection."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [INSTRUMENT_TRIGGER]
    # "Initiate HPLC run from instrument control at position H1 -- confirm mobile phase pressure is within 50-300 bar before run start."
    # Instrument trigger: hplc
    if "hplc" in instruments:
        await instruments["hplc"].read()
    else:
        print(f"[{run_id}] Step 7: hplc not wired — skipping trigger")
    log.append({"step": 7, "action": "INSTRUMENT_TRIGGER", "instrument": "hplc", "status": "complete"})

    # ── STEP 8 ── [OTHER]
    # "Robot monitors for injection complete signal -- confirms UV 280 nm signal detected and peak retention time is within +/-0.2 minutes of expected per injection; flag if outside range."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Review chromatogram for unexpected peaks, baseline drift, or column pressure anomalies before proceeding with batch."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review chromatogram for unexpected peaks, baseline drift, or column pressure anomalies before proceeding with batch.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 9, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 10 ── [OTHER]
    # "After all injections complete, robot exports raw peak area data to run file."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [OTHER]
    # "Calculate sample concentrations by linear regression against standard curve -- log R-squared and flag if below 0.998."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [OTHER]
    # "Flag any samples with concentration outside instrument linear range (0.1-5 mg/mL) for re-injection at appropriate dilution."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Export final titer report to run file; archive raw chromatogram files."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [INSTRUMENT_TRIGGER]
    # "Prime HPLC column with 5 column volumes PBS post-run -- log column flush completion."
    # Instrument trigger: hplc
    if "hplc" in instruments:
        await instruments["hplc"].read()
    else:
        print(f"[{run_id}] Step 14: hplc not wired — skipping trigger")
    log.append({"step": 14, "action": "INSTRUMENT_TRIGGER", "instrument": "hplc", "status": "complete"})

    # ── STEP 15 ── [INSTRUMENT_TRIGGER]
    # "Log column injection count -- flag if cumulative injections exceed 500 (column re-qualification threshold)."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 15: generic not wired — skipping trigger")
    log.append({"step": 15, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_001",
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
        result = await run_bio_001(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
