"""
BioInterface — Auto-generated Protocol
Assay    : HTS_011 — SPR chip loading — surface plasmon resonance
Field    : Drug Discovery / HTS
Workbench: WB1
Robot min: 120 | Total hours: 3
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
    "A1": {"slot": 1, "description": "pH scouting plate — protein at pH 4.0, 4.5, 5.0, 5.5"},
    "A2": {"slot": 2, "description": "Reference compound dilution series (known binder)"},
    "A3": {"slot": 3, "description": "Compound library plate for screening"},
    "C1": {"slot": 13, "description": "HBS-EP+ running buffer reservoir"},
    "C2": {"slot": 14, "description": "EDC solution (200 mM in water)"},
    "C3": {"slot": 15, "description": "NHS solution (50 mM in water)"},
    "C4": {"slot": 16, "description": "Target protein in immobilisation buffer"},
    "C5": {"slot": 17, "description": "Ethanolamine quench solution (1M pH 8.5)"},
    "H1": {"slot": 43, "description": "SPR instrument (Biacore T200 or equivalent)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "immobilisation_level_ru": "3,000–10,000 RU (MW-dependent; Rmax = 100–200 RU target for small molecules)",
    "chip_stability_drift": "< 1% RU drift per hour after immobilisation",
    "reference_compound_kd": "Within 2-fold of published/historical KD value",
    "chip_lifetime": "Replace chip after > 200 compound injections or if baseline drift > 5 RU/min",
    "regeneration_efficiency": "≥ 95% baseline recovery after each compound injection",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_011(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    SPR chip loading — surface plasmon resonance

    Purpose    : Prepare and load target protein onto SPR sensor chip for direct binding measurements of compound affinity (KD) and kinetics (kon, koff).
    Workbench  : WB1
    Robot time : 120 minutes active
    Total time : 3 hours
    Throughput : 1 samples/run
    Difficulty : complex
    AutoMATE 96: head=5-200uL, tagged_steps=2/15
    Regulatory : ICH Q6B (for biologic drugs), FDA guidance on binding assays
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_011: SPR chip loading — surface plasmon resonance")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "Prime SPR instrument (Biacore T200 or equivalent) at position H1 with HBS-EP+ running buffer from position C1 — run 3 prime cycles; confirm baseline < 5 RU drift per minute."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Prepare amine coupling reagents: mix equal volumes EDC (200 mM) and NHS (50 mM) from positions C2 and C3 — use immediately; prepare fresh."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [OTHER]
    # "Activate chip surface: inject EDC/NHS mixture at 10 µL/min for 7 minutes — log activation start time."
    # (unclassified step — logged only)
    log.append({"step": 3, "action": "OTHER", "status": "logged"})

    # ── STEP 4 ── [OTHER]
    # "Prepare target protein at 50–100 µg/mL in sodium acetate pH 4.5–5.5 immobilisation buffer from position C4 — determine optimal pH by pH scouting (pH 4.0, 4.5, 5.0, 5.5 tested at position A1)."
    # (unclassified step — logged only)
    log.append({"step": 4, "action": "OTHER", "status": "logged"})

    # ── STEP 5 ── [OTHER]
    # "Inject target protein at 10 µL/min until target immobilisation level reached (typically 3,000–10,000 RU depending on MW and assay format)."
    # (unclassified step — logged only)
    log.append({"step": 5, "action": "OTHER", "status": "logged"})

    # ── STEP 6 ── [OTHER]
    # "Quench remaining activated groups with 1M ethanolamine pH 8.5 from position C5 — inject at 10 µL/min for 7 minutes."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [OTHER]
    # "Confirm immobilisation level: log final RU on active flow cell and reference flow cell (no protein, ethanolamine-blocked only)."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [OTHER]
    # "Run stability test: inject running buffer for 30 minutes — confirm < 1% RU drift per hour from baseline."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Review immobilisation level — if RU is outside target range (too low: insufficient signal; too high: mass transport limitation), repeat chip activation or adjust protein concentration."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review immobilisation level — if RU is outside target range (too low: insufficient signal; too high: mass transport limitation), repeat chip activation or adjust protein concentration.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 9, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 10 ── [OTHER]
    # "Load compound injection sequence: prepare 8-point concentration series of reference compound (known binder) from position A2 as chip validation."
    # (unclassified step — logged only)
    log.append({"step": 10, "action": "OTHER", "status": "logged"})

    # ── STEP 11 ── [OTHER]
    # "Run reference compound binding: confirm KD within 2-fold of published value — log validation result."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [OTHER]
    # "If chip passes validation, proceed to compound library injection at position A3."
    # (unclassified step — logged only)
    log.append({"step": 12, "action": "OTHER", "status": "logged"})

    # ── STEP 13 ── [OTHER]
    # "Log chip ID, immobilisation date, protein lot, immobilisation level, and validation KD to run file."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Store chip at 4°C in running buffer if not in immediate use — log storage."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [OTHER]
    # "Export SPR chip preparation report to run file."
    # (unclassified step — logged only)
    log.append({"step": 15, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "HTS_011",
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
        result = await run_hts_011(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
