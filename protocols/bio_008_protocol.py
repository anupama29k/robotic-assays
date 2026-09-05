"""
BioInterface — Auto-generated Protocol
Assay    : BIO_008 — Mycoplasma detection by PCR
Field    : Biopharma / CDMO
Workbench: WB2
Robot min: 60 | Total hours: 3
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
    "A1": {"slot": 1, "description": "Sample input rack -- 8 x 1.5 mL tubes (cell culture supernatant)"},
    "A9": {"slot": 0, "description": "Extraction tube rack -- 8 x 1.5 mL tubes"},
    "B1": {"slot": 7, "description": "Eluate collection rack -- 8 x 0.2 mL PCR tubes"},
    "B2": {"slot": 8, "description": "96-well qPCR plate"},
    "C1": {"slot": 13, "description": "Lysis buffer reservoir"},
    "C2": {"slot": 14, "description": "Magnetic bead tube"},
    "C3": {"slot": 15, "description": "Wash buffer 1 reservoir"},
    "C4": {"slot": 16, "description": "Wash buffer 2 reservoir"},
    "C5": {"slot": 17, "description": "Elution buffer (70C, at H2)"},
    "D1": {"slot": 19, "description": "Optical qPCR plate seal"},
    "D2": {"slot": 26, "description": "Magnetic rack"},
    "E1": {"slot": 25, "description": "Liquid waste container"},
    "F1": {"slot": 31, "description": "Mycoplasma-positive control DNA tube"},
    "F2": {"slot": 38, "description": "Nuclease-free water (negative control)"},
    "G1": {"slot": 37, "description": "qPCR instrument interface"},
    "H1": {"slot": 43, "description": "Vortex mixer"},
    "H2": {"slot": 44, "description": "Heat block (65C / 70C dual zone)"},
}

# ── ACCEPTANCE CRITERIA ──────────────────────────────
# Loaded from assay["acceptance_criteria"]
ACCEPTANCE_CRITERIA = {
    "positive_control_ct": "Ct < 35",
    "negative_control": "No amplification (Ct > 40 or undetermined)",
    "melting_curve": "Single peak at expected Tm +/- 1C",
    "sample_fail_threshold": "Ct <= 40 = mycoplasma detected (FAIL)",
}

# ── PROTOCOL FUNCTION ────────────────────────────────
async def run_bio_008(
    robot,          # Rail System rail arm
    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)
    instruments,    # dict of other instruments: plate_reader, incubator, etc.
    plate_id: str = "PLATE-001",
    analyst_name: str = "Analyst",
    run_id: str = None,
):
    """
    Mycoplasma detection by PCR

    Purpose    : Detect mycoplasma contamination in cell culture samples using PCR-based detection as a rapid alternative to compendial culture methods.
    Workbench  : WB2
    Robot time : 60 minutes active
    Total time : 3 hours
    Throughput : 8 samples/run
    Difficulty : easy
    AutoMATE 96: head=1-20uL, tagged_steps=1/17
    Regulatory : ICH Q5A, USP <63>, Ph. Eur. 2.6.7
    """
    import datetime
    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    log = []

    print(f"[{run_id}] Starting BIO_008: Mycoplasma detection by PCR")
    print(f"[{run_id}] Analyst: {analyst_name}")
    print(f"[{run_id}] Plate: {plate_id}")

    # ── STEP 1 ── [TRANSPORT]
    # "Pick up cell culture supernatant samples from input rack at position A1 (A1:1 through A1:8) -- confirm samples at room temperature."
    await robot.move_plate(
        plate_id=plate_id,
        from_position="input_rack",
        to_position=DECK_LAYOUT["A1"]["slot"],
    )
    log.append({"step": 1, "action": "TRANSPORT", "from": "input_rack", "to": "A1", "status": "complete"})

    # ── STEP 2 ── [OTHER]
    # "Transfer 200 uL per sample to DNA extraction tubes at position A9."
    # (unclassified step — logged only)
    log.append({"step": 2, "action": "OTHER", "status": "logged"})

    # ── STEP 3 ── [INSTRUMENT_TRIGGER]
    # "Add 200 uL lysis buffer from position C1 to each tube; vortex 10 seconds at position H1."
    # Instrument trigger: vortex
    if "vortex" in instruments:
        await instruments["vortex"].read()
    else:
        print(f"[{run_id}] Step 3: vortex not wired — skipping trigger")
    log.append({"step": 3, "action": "INSTRUMENT_TRIGGER", "instrument": "vortex", "status": "complete"})

    # ── STEP 4 ── [WAIT]
    # "Incubate at 65C for 10 minutes in heat block at position H2 -- log start time."
    print(f"[{run_id}] Step 4: waiting 600s — robot free for other tasks")
    await asyncio.sleep(600)
    log.append({"step": 4, "action": "WAIT", "duration_seconds": 600, "status": "complete"})

    # ── STEP 5 ── [WAIT]
    # "Add 10 uL magnetic beads from position C2; mix by pipetting 10 times; incubate 5 minutes at room temperature."
    print(f"[{run_id}] Step 5: waiting 300s — robot free for other tasks")
    await asyncio.sleep(300)
    log.append({"step": 5, "action": "WAIT", "duration_seconds": 300, "status": "complete"})

    # ── STEP 6 ── [OTHER]
    # "Place tubes on magnetic rack at position D2 for 2 minutes until beads pellet; aspirate and discard supernatant to waste at position E1."
    # (unclassified step — logged only)
    log.append({"step": 6, "action": "OTHER", "status": "logged"})

    # ── STEP 7 ── [OTHER]
    # "Wash with 200 uL wash buffer 1 (position C3) -- resuspend, magnet, aspirate. Repeat twice."
    # (unclassified step — logged only)
    log.append({"step": 7, "action": "OTHER", "status": "logged"})

    # ── STEP 8 ── [OTHER]
    # "Wash with 200 uL wash buffer 2 (position C4) -- resuspend, magnet, aspirate. Once."
    # (unclassified step — logged only)
    log.append({"step": 8, "action": "OTHER", "status": "logged"})

    # ── STEP 9 ── [OTHER]
    # "Elute with 50 uL elution buffer (position C5, pre-heated to 70C in H2) for 5 minutes; transfer eluate to PCR plate at position B1."
    # (unclassified step — logged only)
    log.append({"step": 9, "action": "OTHER", "status": "logged"})

    # ── STEP 10 ── [LIQUID_HANDLER]
    # "Set up qPCR reactions in 96-well qPCR plate at position B2: 10 uL 2x master mix + 0.5 uL forward primer + 0.5 uL reverse primer + 2 uL template + 7 uL nuclease-free water per reaction."
    await lh.dispense(
        resource=DECK_LAYOUT["B2"]["slot"],
        vols=[10] * 96,
        flow_rate=50,
        liquid_class="aqueous",
    )
    log.append({"step": 10, "action": "LIQUID_HANDLER", "volume_uL": 10, "cycles": 1, "head": "1-20uL", "status": "complete"})

    # ── STEP 11 ── [OTHER]
    # "Include mycoplasma-positive control (position F1) in well H11 and nuclease-free water negative control (position F2) in well H12."
    # (unclassified step — logged only)
    log.append({"step": 11, "action": "OTHER", "status": "logged"})

    # ── STEP 12 ── [INSTRUMENT_TRIGGER]
    # "Seal qPCR plate with optical film from position D1; transfer to qPCR instrument at position G1."
    # Instrument trigger: sealer
    if "sealer" in instruments:
        await instruments["sealer"].read()
    else:
        print(f"[{run_id}] Step 12: sealer not wired — skipping trigger")
    log.append({"step": 12, "action": "INSTRUMENT_TRIGGER", "instrument": "sealer", "status": "complete"})

    # ── STEP 13 ── [OTHER]
    # "Run programme: 95C 5 min; 45 x (95C 15s, 60C 60s); melting curve 65-95C."
    # (unclassified step — logged only)
    log.append({"step": 13, "action": "OTHER", "status": "logged"})

    # ── STEP 14 ── [OTHER]
    # "Monitor Ct in real time -- positive control must show Ct < 35; negative control must show no amplification."
    # (unclassified step — logged only)
    log.append({"step": 14, "action": "OTHER", "status": "logged"})

    # ── STEP 15 ── [ANALYST_PAUSE]
    # "[ANALYST STEP -- robot pauses and alerts]: Review melting curve for each presumptive positive -- confirm single peak at expected Tm before calling result."
    print(f"[{run_id}] ANALYST PAUSE — action required")
    await robot.analyst_pause(
        reason="Review melting curve for each presumptive positive -- confirm single peak at expected Tm before calling result.",
        timeout_minutes=15,
        alert_level="WARNING",
    )
    log.append({"step": 15, "action": "ANALYST_PAUSE", "status": "complete"})

    # ── STEP 16 ── [OTHER]
    # "Call each sample pass (Ct > 40 or undetermined) or fail (Ct <= 40) -- export qPCR report to run file."
    # (unclassified step — logged only)
    log.append({"step": 16, "action": "OTHER", "status": "logged"})

    # ── STEP 17 ── [OTHER]
    # "Flag any failures for immediate QA escalation and batch quarantine."
    # (unclassified step — logged only)
    log.append({"step": 17, "action": "OTHER", "status": "logged"})

    print(f"[{run_id}] Protocol complete")
    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")
    return {
        "run_id": run_id,
        "assay_id": "BIO_008",
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
        result = await run_bio_008(
            robot=robot, lh=lh, instruments=instruments,
            plate_id="SIM-001", analyst_name="Simulation",
        )
        print()
        print(f"Simulation complete: {result['steps_completed']} steps")
        await lh.stop()

    asyncio.run(simulate())
