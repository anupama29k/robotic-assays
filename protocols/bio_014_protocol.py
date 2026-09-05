"""
BioInterface — Auto-generated Protocol
Assay    : BIO_014 — SDS-PAGE and gel imaging
Field    : Biopharma / CDMO
Workbench: WB1
Robot min: 30 | Total hours: 2.5
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
    "A9": {"slot": 0, "description": "PCR tube strip rack -- sample preparation"},
    "B1": {"slot": 7, "description": "Pre-cast gel storage (4-12% Bis-Tris NuPAGE gel)"},
    "C1": {"slot": 13, "description": "LDS sample buffer reservoir"},
    "C2": {"slot": 14, "description": "DTT reducing agent tube"},
    "C3": {"slot": 15, "description": "Non-reducing sample buffer reservoir"},
    "C4": {"slot": 16, "description": "MES SDS running buffer reservoir"},
    "C5": {"slot": 17, "description": "SimplyBlue Coomassie stain"},
    "D1": {"slot": 19, "description": "Gel-loading tips (10 uL, narrow bore)"},
    "F1": {"slot": 31, "description": "MW ladder tube (pre-stained protein standard)"},
    "G1": {"slot": 37, "description": "Gel imaging system (white light)"},
    "H1": {"slot": 43, "description": "Heat block (70C)"},
    "H2": {"slot": 44, "description": "Gel electrophoresis tank with power supply"},
    "H3": {"slot": 45, "description": "Staining tray on orbital shaker"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "mw_ladder_resolution": "All bands clearly resolved with expected MW migration",
    "reduced_mab_hc": "Band at ~50 kDa (heavy chain)",
    "reduced_mab_lc": "Band at ~25 kDa (light chain)",
    "non_reduced_mab_intact": "Band at ~150 kDa (intact IgG)",
    "purity_by_densitometry": ">= 95% in main bands (product-specific)",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_014(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    SDS-PAGE and gel imaging

    Purpose    : Assess molecular weight, purity, and structural integrity under reducing and non-reducing conditions using SDS-PAGE with Coomassie or silver staining.
    Workbench  : WB1
    Robot time : 30 minutes active
    Total time : 2.5 hours
    Throughput : 10 samples/run
    Difficulty : medium
    AutoMATE 96: head=not applicable, tagged_steps=0/16
    Regulatory : ICH Q6B, ICH Q2(R2)
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_014: SDS-PAGE and gel imaging")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Prepare reducing samples: mix sample + LDS sample buffer + reducing agent (DTT) from positions C1, C2, C3 in PCR tubes at position A9 -- target 2-5 ug protein per lane."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Prepare non-reducing samples: mix sample + LDS sample buffer (no DTT) in separate PCR tubes."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [OTHER]
    # "Heat reducing samples at 70C for 10 minutes in heat block at position H1 -- log start/end times; non-reducing samples remain at room temperature."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [OTHER]
    # "Cool reducing samples to room temperature -- 5 minutes minimum."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "Remove pre-cast gel (4-12% Bis-Tris) from position B1; rinse wells 3x with running buffer from position C4 using multichannel."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [OTHER]
    # "Load 10 uL MW ladder (position F1) into lane 1 and last lane using 10 uL gel-loading tips from position D1."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [OTHER]
    # "Load 10-15 uL each sample into designated lanes per lane map loaded at run start -- dispense at bottom of well slowly."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [OTHER]
    # "Log lane assignments with sample IDs, reducing/non-reducing designation, and load volumes."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [OTHER]
    # "Assemble gel cassette into electrophoresis tank at position H2; fill with MES SDS running buffer from position C4."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [OTHER]
    # "Connect to power supply -- run at 200V constant for 35 minutes; robot monitors run completion."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Check dye front has reached bottom of gel before stopping run."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Check dye front has reached bottom of gel before stopping run.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 11, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 12 ── [OTHER]
    # "Remove gel from cassette; transfer to staining tray at position H3."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [WAIT]
    # "Stain: add SimplyBlue Coomassie stain from position C5; incubate 1 hour on orbital shaker."
    print(f"[{run_id}] Step 13: waiting 3600s — robot free for other tasks")
    await asyncio.sleep(3600)
    log.append({"step": 13, "action": "WAIT", "duration_seconds": 3600, "status": "complete"})

    # ── STEP 14 ── [OTHER]
    # "Destain: rinse 3x with ultrapure water; leave in water until background is clear."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Transfer gel to gel imaging system at position G1 -- capture white-light image."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    # ── STEP 16 ── [OTHER]
    # "Export gel image to run file; log band pattern observations per lane."
    # (unclassified step — logged only)
    log.append({"step": 16, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_014",
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
        result = await run_bio_014(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
