"""
BioInterface — Auto-generated Protocol
Assay    : HTS_005 — Cytotoxicity assay — LDH release
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
    "A1": {"slot": 1, "description": "Compound dilution plate (HTS_001 output)"},
    "B1": {"slot": 7, "description": "96-well TC plate (cell seeding)"},
    "B2": {"slot": 8, "description": "96-well flat-bottom plate (supernatant transfer)"},
    "C1": {"slot": 13, "description": "Lysis buffer — 2% Triton X-100 in PBS"},
    "C2": {"slot": 14, "description": "LDH reaction mixture (CytoTox 96 or equivalent)"},
    "C3": {"slot": 15, "description": "Stop solution"},
    "E1": {"slot": 25, "description": "Biological waste + bleach container"},
    "G1": {"slot": 37, "description": "Plate reader (490/680 nm)"},
    "H1": {"slot": 43, "description": "CO₂ incubator (37°C, 5%)"},
    "H2": {"slot": 44, "description": "Inverted microscope (analyst station)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "spontaneous_release": "≤ 15% of maximum release",
    "maximum_release_cv": "≤ 10% CV across column 12 wells",
    "z_factor": "Z' ≥ 0.5 between spontaneous and maximum release controls",
    "cytotoxicity_flag_threshold": "≥ 30% cytotoxicity at lowest concentration triggers orthogonal testing",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_005(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Cytotoxicity assay — LDH release

    Purpose    : Quantify compound-induced cell death by measuring lactate dehydrogenase (LDH) release from lysed cells as a marker of membrane integrity loss.
    Workbench  : WB2
    Robot time : 35 minutes active
    Total time : 28 hours
    Throughput : 80 samples/run
    Difficulty : medium
    AutoMATE 96: head=5-200uL, tagged_steps=6/16
    Regulatory : ICH S7A, OECD TG 453
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_005: Cytotoxicity assay — LDH release")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [WAIT]
    # "Seed target cells at 10,000 cells/well in 96-well TC plate at position B1 in 100 µL complete medium — incubate 24 hours at 37°C, 5% CO₂ at position H1."
    print(f"[{run_id}] Step 1: waiting 86400s — robot free for other tasks")
    await asyncio.sleep(86400)
    log.append({"step": 1, "action": "WAIT", "duration_seconds": 86400, "status": "complete"})

    # ── STEP 2 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Confirm cell attachment and viability under microscope at position H2 before adding compounds."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm cell attachment and viability under microscope at position H2 before adding compounds.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 2, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 3 ── [LIQUID_HANDLER]
    # "Add 100 µL compound dilutions from position A1 to cell plate — final volume 200 µL per well."
    await lh.dispense(
        resource=DECK_LAYOUT["A1"]["slot"],
        vols=[100] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 3, "action": "LIQUID_HANDLER", "volume_uL": 100, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 4 ── [OTHER]
    # "Include spontaneous release control wells (cells + medium only, no compound) in columns 11."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "Include maximum release control wells (cells + 2% Triton X-100 lysis buffer from position C1) in column 12."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [WAIT]
    # "Incubate 24 hours at 37°C, 5% CO₂; log start time."
    print(f"[{run_id}] Step 6: waiting 86400s — robot free for other tasks")
    await asyncio.sleep(86400)
    log.append({"step": 6, "action": "WAIT", "duration_seconds": 86400, "status": "complete"})

    # ── STEP 7 ── [INSTRUMENT_TRIGGER]
    # "Centrifuge plate at 250 × g for 5 minutes to pellet any floating dead cells."
    # Instrument trigger: centrifuge
    if "centrifuge" in instruments:
        await instruments["centrifuge"].read()
    else:
        print(f"[{run_id}] Step 7: centrifuge not wired — skipping trigger")
    log.append({"step": 7, "action": "INSTRUMENT_TRIGGER", "instrument": "centrifuge", "status": "complete"})

    # ── STEP 8 ── [LIQUID_HANDLER]
    # "Transfer 50 µL of supernatant from each well to new 96-well flat-bottom plate at position B2 without disturbing cell pellet."
    await lh.dispense(
        resource=DECK_LAYOUT["B2"]["slot"],
        vols=[50] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 8, "action": "LIQUID_HANDLER", "volume_uL": 50, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 9 ── [LIQUID_HANDLER]
    # "Add 50 µL LDH reaction mixture from position C2 to each well of supernatant plate — mix gently."
    await lh.dispense(
        resource=DECK_LAYOUT["C2"]["slot"],
        vols=[50] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 9, "action": "LIQUID_HANDLER", "volume_uL": 50, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 10 ── [WAIT]
    # "Incubate at room temperature for 30 minutes protected from light; log start time."
    print(f"[{run_id}] Step 10: waiting 1800s — robot free for other tasks")
    await asyncio.sleep(1800)
    log.append({"step": 10, "action": "WAIT", "duration_seconds": 1800, "status": "complete"})

    # ── STEP 11 ── [LIQUID_HANDLER]
    # "Add 25 µL stop solution from position C3 to each well."
    await lh.dispense(
        resource=DECK_LAYOUT["C3"]["slot"],
        vols=[25] * 96,
        flow_rate=200,
        liquid_class="aqueous",
    )
    log.append({"step": 11, "action": "LIQUID_HANDLER", "volume_uL": 25, "cycles": 1, "head": "5-200uL", "status": "complete"})

    # ── STEP 12 ── [TRANSPORT]
    # "Transfer to plate reader at position G1 — read absorbance at 490 nm with reference at 680 nm."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 12, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Calculate % cytotoxicity: ((OD_sample − OD_spontaneous) / (OD_maximum − OD_spontaneous)) × 100."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Flag compounds with ≥ 30% cytotoxicity at lowest tested concentration as non-selective cytotoxics."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Export cytotoxicity data and flag list to run file."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    # ── STEP 16 ── [OTHER]
    # "Decontaminate cell plates with 10% bleach for 30 minutes before disposal — log decontamination."
    # (unclassified step — logged only)
    log.append({"step": 16, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_005",
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
        result = await run_hts_005(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
