"""
BioInterface — Auto-generated Protocol
Assay    : HTS_012 — Dose-response curve setup and IC50 determination
Field    : Drug Discovery / HTS
Workbench: WB1
Robot min: 45 | Total hours: 4
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
    "A1": {"slot": 1, "description": "Hit compound source plate (confirmed HTS hits, DMSO stocks)"},
    "B1": {"slot": 7, "description": "Dose-response dilution plate (96-well, 10-point series)"},
    "B2": {"slot": 8, "description": "Assay plate (format matches primary assay used)"},
    "C1": {"slot": 13, "description": "Assay-specific reagents (loaded per primary assay protocol)"},
    "D1": {"slot": 19, "description": "Adhesive plate seal"},
    "F1": {"slot": 31, "description": "Reference standard compound (known IC50)"},
    "F2": {"slot": 38, "description": "DMSO vehicle control"},
    "G1": {"slot": 37, "description": "Plate reader (mode matches primary assay detection)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "curve_fit_r2": ">= 0.95 for 4PL fit",
    "reference_standard_ic50": "Within 3-fold of historical IC50 value",
    "hill_slope_range": "0.5–2.0 (typical for single-site competitive inhibitors); > 3 triggers aggregation counter-screen",
    "bottom_asymptote": "<= 20% (complete inhibition at top concentration preferred)",
    "ligand_efficiency_flag": "LE >= 0.3 = priority lead",
    "pains_filter": "All hits screened against PAINS catalogue before advancing",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_012(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Dose-response curve setup and IC50 determination

    Purpose    : Generate complete dose-response profiles for confirmed hits and calculate IC50, Hill slope, and curve parameters using 4-parameter logistic (4PL) regression.
    Workbench  : WB1
    Robot time : 45 minutes active
    Total time : 4 hours
    Throughput : 8 samples/run
    Difficulty : medium
    AutoMATE 96: head=5-200uL, tagged_steps=1/15
    Regulatory : ICH Q6A, FDA guidance on IC50 determination
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_012: Dose-response curve setup and IC50 determination")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Retrieve confirmed hit compound list from HTS primary screen run file — load into robot run file as source plate map."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Prepare 10-point 3-fold serial dilution series for each hit compound from 100 µM top concentration using HTS_001 serial dilution protocol — target final assay concentrations: 30 µM to 0.5 nM."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [OTHER]
    # "Run each hit through the relevant primary assay (HTS_002 through HTS_010 depending on target) in triplicate — log assay ID used for confirmation."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [OTHER]
    # "Include reference standard compound (known IC50, from position F1) on every dose-response plate as assay performance control."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "Collect raw response data (absorbance, fluorescence, luminescence, or HTRF ratio) for all 10 concentrations x 3 replicates per compound."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [OTHER]
    # "Fit 4-parameter logistic (4PL) model to each compound dose-response data: Y = Bottom + (Top-Bottom)/(1+(IC50/X)^HillSlope)."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [OTHER]
    # "Extract IC50, Hill slope, top asymptote, and bottom asymptote for each compound — log all 4 parameters."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [OTHER]
    # "Flag compounds where: Hill slope > 3 (potential aggregation); bottom asymptote > 30% (incomplete inhibition); R2 < 0.95 (poor curve fit); IC50 outside dilution range (curve not fully defined)."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Review flagged curves manually — compounds with Hill slope > 3 require counter-screening with detergent (0.01% Triton X-100) to test for aggregation-based inhibition."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review flagged curves manually — compounds with Hill slope > 3 require counter-screening with detergent (0.01% Triton X-100) to test for aggregation-based inhibition.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 9, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 10 ── [OTHER]
    # "Run PAINS filter on all confirmed hits — flag any compound matching known pan-assay interference structural alerts."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [OTHER]
    # "Rank confirmed hits by IC50 value — export ranked hit list with full curve parameters to run file."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [INSTRUMENT_TRIGGER]
    # "For each confirmed hit, calculate ligand efficiency: LE = (1.37 x pIC50) / HAC (heavy atom count)."
    # Instrument trigger: generic
    if "generic" in instruments:
        await instruments["generic"].read()
    else:
        print(f"[{run_id}] Step 12: generic not wired — skipping trigger")
    log.append({"step": 12, "action": "INSTRUMENT_TRIGGER", "instrument": "generic", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Flag hits with LE >= 0.3 as priority leads for medicinal chemistry."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Export complete dose-response dataset including raw data, fitted parameters, LE values, and PAINS flags."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Archive dose-response curves as PDF plate images in run file."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_012",
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
        result = await run_hts_012(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
