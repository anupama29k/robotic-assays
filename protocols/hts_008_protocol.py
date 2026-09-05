"""
BioInterface — Auto-generated Protocol
Assay    : HTS_008 — AlphaScreen bead proximity assay
Field    : Drug Discovery / HTS
Workbench: WB1
Robot min: 30 | Total hours: 6
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
    "A1": {"slot": 1, "description": "Compound dilution plate (AlphaScreen-compatible, 384-well)"},
    "B1": {"slot": 7, "description": "384-well white OptiPlate (PerkinElmer)"},
    "C1": {"slot": 13, "description": "Alpha assay buffer reservoir"},
    "C2": {"slot": 14, "description": "Bait protein solution (light-protected)"},
    "C3": {"slot": 15, "description": "Acceptor beads + prey protein complex (light-protected)"},
    "C4": {"slot": 16, "description": "Donor beads — streptavidin-coated (light-protected)"},
    "D1": {"slot": 19, "description": "Foil plate seal dispenser"},
    "E1": {"slot": 25, "description": "Waste container"},
    "G1": {"slot": 37, "description": "AlphaScreen-compatible plate reader (EnVision or PHERAstar)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "z_factor": "Z' ≥ 0.5",
    "alpha_signal_window": "Positive/negative control ratio ≥ 5-fold",
    "hook_effect_check": "Run bead titration experiment — hook effect (signal drop at high bead concentration) must not affect assay window",
    "light_protection_compliance": "Any plate exposed to light must be discarded — no exceptions",
    "hit_threshold": "≥ 50% inhibition at primary screening concentration",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_hts_008(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    AlphaScreen bead proximity assay

    Purpose    : Detect and quantify protein-protein interactions using AlphaScreen bead proximity technology; screen for small molecule disruptors of the interaction.
    Workbench  : WB1
    Robot time : 30 minutes active
    Total time : 6 hours
    Throughput : 352 samples/run
    Difficulty : complex
    AutoMATE 96: head=1-20uL, tagged_steps=4/15
    Regulatory : ICH Q6A
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting HTS_008: AlphaScreen bead proximity assay")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [OTHER]
    # "All AlphaScreen steps must be performed under green safe light (< 600 nm) — confirm green filter is installed on bench lighting before starting."
    # (unclassified step — logged only)
    log.append({"step": 1, "action": "OTHER", "status": "logged"})

    # ── STEP 2 ── [OTHER]
    # "Pre-dilute streptavidin-coated donor beads and protein A-coated acceptor beads to 20 µg/mL in Alpha assay buffer (HEPES pH 7.4, 0.1% BSA, 0.01% Tween) from position C1."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [LIQUID_HANDLER]
    # "Dispense 5 µL compound dilutions from position A1 into 384-well white OptiPlate at position B1."
    await lh.dispense(
        resource=DECK_LAYOUT["B1"]["slot"],
        vols=[5] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 3, "action": "LIQUID_HANDLER", "volume_uL": 5, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 4 ── [LIQUID_HANDLER]
    # "Add 5 µL biotinylated bait protein (His-tagged or GST-tagged partner) from position C2 — mix gently; incubate 30 minutes at room temperature."
    await lh.dispense(
        resource=DECK_LAYOUT["C2"]["slot"],
        vols=[5] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 4, "action": "LIQUID_HANDLER", "volume_uL": 5, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 5 ── [LIQUID_HANDLER]
    # "Add 5 µL acceptor beads (protein A-coated, bound to anti-tag antibody + prey protein complex) from position C3 in dim light — mix gently."
    await lh.dispense(
        resource=DECK_LAYOUT["C3"]["slot"],
        vols=[5] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 5, "action": "LIQUID_HANDLER", "volume_uL": 5, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 6 ── [INSTRUMENT_TRIGGER]
    # "Seal plate immediately with foil seal from position D1 — no further light exposure."
    # Instrument trigger: sealer
    if "sealer" in instruments:
        await instruments["sealer"].read()
    else:
        print(f"[{run_id}] Step 6: sealer not wired — skipping trigger")
    log.append({"step": 6, "action": "INSTRUMENT_TRIGGER", "instrument": "sealer", "status": "complete"})

    # ── STEP 7 ── [WAIT]
    # "Incubate 1 hour at room temperature in the dark."
    print(f"[{run_id}] Step 7: waiting 3600s — robot free for other tasks")
    await asyncio.sleep(3600)
    log.append({"step": 7, "action": "WAIT", "duration_seconds": 3600, "status": "complete"})

    # ── STEP 8 ── [LIQUID_HANDLER]
    # "Add 5 µL donor beads (streptavidin-coated) from position C4 — mix gently in dim light."
    await lh.dispense(
        resource=DECK_LAYOUT["C4"]["slot"],
        vols=[5] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 8, "action": "LIQUID_HANDLER", "volume_uL": 5, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 9 ── [INSTRUMENT_TRIGGER]
    # "Seal plate again with fresh foil seal."
    # Instrument trigger: sealer
    if "sealer" in instruments:
        await instruments["sealer"].read()
    else:
        print(f"[{run_id}] Step 9: sealer not wired — skipping trigger")
    log.append({"step": 9, "action": "INSTRUMENT_TRIGGER", "instrument": "sealer", "status": "complete"})

    # ── STEP 10 ── [WAIT]
    # "Incubate 4 hours at room temperature in the dark (or overnight at 4°C); log start time."
    print(f"[{run_id}] Step 10: waiting 50400s — robot free for other tasks")
    await asyncio.sleep(50400)
    log.append({"step": 10, "action": "WAIT", "duration_seconds": 50400, "status": "complete"})

    # ── STEP 11 ── [ANALYST_PAUSE]
    # "[ANALYST STEP — robot pauses and alerts]: Confirm plate has been completely protected from light — any light exposure after bead addition permanently quenches AlphaScreen signal."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Confirm plate has been completely protected from light — any light exposure after bead addition permanently quenches AlphaScreen signal.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 11, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 12 ── [TRANSPORT]
    # "Transfer plate to AlphaScreen reader at position G1 — read in AlphaScreen mode (laser excitation 680 nm, emission 615 nm)."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["G1"]["slot"],
    )
    log.append({"step": 12, "action": "TRANSPORT", "from": "input_rack", "to": "G1", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Calculate % inhibition from known disruptor positive control (column 1) and DMSO vehicle (column 24)."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Calculate Z-factor from control wells."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [INSTRUMENT_TRIGGER]
    # "Export Alpha signal counts, % inhibition, Z-factor, and hit list to run file."
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
        "assay_id": "HTS_008",
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
        result = await run_hts_008(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
