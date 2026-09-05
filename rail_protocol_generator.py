"""
rail_protocol_generator.py
BioInterface — PyLabRobot protocol generator.

Takes any assay dict from field_01_biopharma_v2.BIOPHARMA_ASSAYS or
field_04_drug_discovery_hts_v2.HTS_ASSAYS and emits an executable
PyLabRobot-style Python module.
"""

import datetime
import os
import re
from typing import Dict, List, Tuple


# ═══════════════════════════════════════════════════════════════════
# DECK POSITION MAP — logical id -> physical slot number
# ═══════════════════════════════════════════════════════════════════

DECK_SLOT_MAP = {
    "A1": 1,  "A2": 2,  "A3": 3,  "A4": 4,  "A5": 5,  "A6": 6,
    "B1": 7,  "B2": 8,  "B3": 9,  "B4": 10, "B5": 11, "B6": 12,
    "C1": 13, "C2": 14, "C3": 15, "C4": 16, "C5": 17, "C6": 18,
    "C7": 19, "C8": 20, "C9": 21,
    "D1": 19, "D2": 26, "D3": 27, "D4": 28, "D5": 29, "D6": 30,
    "E1": 25, "E2": 32, "E3": 33,
    "F1": 31, "F2": 38, "F3": 39,
    "G1": 37, "G2": 44,
    "H1": 43, "H2": 44, "H3": 45, "H4": 50, "H5": 51,
}


# ═══════════════════════════════════════════════════════════════════
# STEP CLASSIFIER
# ═══════════════════════════════════════════════════════════════════

TRANSPORT_KEYWORDS = (
    "transport", "transfer plate", "move plate", "pick up plate",
    "load plate", "retrieve plate", "return plate", "place plate",
    "transfer to plate reader", "transfer to incubator", "transfer to reader",
    "pick up", "pick_up", "load plate from", "take plate",
)

LIQUID_KEYWORDS = (
    "dispense", "aspirate", "add ", "transfer", "pipette", "mix", "dilute",
    "wash", "resuspend", "elute",
)

WAIT_KEYWORDS = ("incubate", "overnight", "wait")

INSTRUMENT_KEYWORDS = (
    "plate reader", "centrifuge", "seal", "read", "measure", "count",
    "autosampler", "hplc", "vortex",
)

# Head-specific default flow rates (uL/sec)
FLOW_RATE_BY_HEAD = {
    "1-20uL":     50,
    "5-200uL":    200,
    "100-1000uL": 500,
    "not applicable": 200,
}


def _extract_duration_seconds(text: str) -> int:
    """Parse 'X minutes', 'X hours', 'X seconds', ranges, or 'overnight'."""
    lower = text.lower()
    if "overnight" in lower:
        return 14 * 3600
    range_min = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*minute", lower)
    if range_min:
        return int(range_min.group(2)) * 60
    range_hr = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*hour", lower)
    if range_hr:
        return int(range_hr.group(2)) * 3600
    min_match = re.search(r"(\d+)\s*minute", lower)
    if min_match:
        return int(min_match.group(1)) * 60
    hr_match = re.search(r"(\d+)\s*hour", lower)
    if hr_match:
        return int(hr_match.group(1)) * 3600
    sec_match = re.search(r"(\d+)\s*second", lower)
    if sec_match:
        return int(sec_match.group(1))
    return 0


def _extract_positions(text: str) -> List[str]:
    """Pick 'position X#' and standalone '[A-H][0-9]' tokens from the step text."""
    positions = re.findall(r"position\s+([A-H][0-9]+)", text, re.IGNORECASE)
    if not positions:
        positions = re.findall(r"\b([A-H][0-9])\b", text)
    return [p.upper() for p in positions]


def _extract_volume_uL(text: str) -> int:
    """Return the first volume in uL. Accepts 'µL', 'uL', 'mL' (→ * 1000)."""
    ml_match = re.search(r"(\d+(?:\.\d+)?)\s*mL\b", text)
    if ml_match:
        return int(float(ml_match.group(1)) * 1000)
    ul_match = re.search(r"(\d+)\s*(?:µ|u|µ)L\b", text, re.IGNORECASE)
    if ul_match:
        return int(ul_match.group(1))
    nl_match = re.search(r"(\d+)\s*nL\b", text)
    if nl_match:
        return max(1, int(int(nl_match.group(1)) / 1000))  # sub-uL floors at 1
    return 0


def classify_step(step_text: str, step_num: int, automate_steps: List[int]) -> Tuple[str, Dict]:
    """
    Return (action_type, metadata) for one step.

    Priority: ANALYST_PAUSE first (explicit marker), then TRANSPORT,
    then LIQUID_HANDLER (must be tagged as AutoMATE), then WAIT,
    then INSTRUMENT_TRIGGER, else OTHER.
    """
    text = step_text.lower()
    meta: Dict = {}

    # 1. ANALYST_PAUSE — explicit marker wins
    if "[analyst step" in text:
        reason_match = re.search(r"\[analyst step[^\]]*\]:?\s*(.+)", step_text, re.IGNORECASE)
        meta["reason"] = (reason_match.group(1).strip() if reason_match else step_text)[:200]
        return "ANALYST_PAUSE", meta

    # 2. TRANSPORT
    if any(kw in text for kw in TRANSPORT_KEYWORDS):
        positions = _extract_positions(step_text)
        if len(positions) >= 2:
            meta["from_pos"], meta["to_pos"] = positions[0], positions[1]
        elif positions:
            meta["to_pos"] = positions[0]
        return "TRANSPORT", meta

    # 3. LIQUID_HANDLER — must be in automate_96_steps
    if step_num in automate_steps and any(kw in text for kw in LIQUID_KEYWORDS):
        vol = _extract_volume_uL(step_text)
        if vol:
            meta["volume_uL"] = vol
        positions = _extract_positions(step_text)
        if len(positions) >= 2:
            meta["from_pos"], meta["to_pos"] = positions[0], positions[1]
        elif positions:
            meta["to_pos"] = positions[0]
        cycles = re.search(r"(\d+)\s*(?:times|cycles?)", text)
        if cycles and ("wash" in text or "repeat" in text):
            meta["cycles"] = int(cycles.group(1))
        return "LIQUID_HANDLER", meta

    # 4. WAIT
    if any(kw in text for kw in WAIT_KEYWORDS):
        meta["duration_seconds"] = _extract_duration_seconds(step_text)
        return "WAIT", meta

    # 5. INSTRUMENT_TRIGGER
    if any(kw in text for kw in INSTRUMENT_KEYWORDS):
        if "reader" in text or "read" in text:
            meta["instrument"] = "plate_reader"
        elif "centrifuge" in text:
            meta["instrument"] = "centrifuge"
        elif "seal" in text:
            meta["instrument"] = "sealer"
        elif "hplc" in text:
            meta["instrument"] = "hplc"
        elif "vortex" in text:
            meta["instrument"] = "vortex"
        else:
            meta["instrument"] = "generic"
        return "INSTRUMENT_TRIGGER", meta

    return "OTHER", meta


# ═══════════════════════════════════════════════════════════════════
# CODEGEN — one block per classified step
# ═══════════════════════════════════════════════════════════════════

def _py_str(s: str, max_len: int = 200) -> str:
    """Return a string safe to embed inside a Python double-quoted literal."""
    s = str(s)
    s = s.replace("\\", "\\\\").replace('"', "'").replace("\n", " ").replace("\r", " ")
    return s[:max_len]


def _slot_for(pos: str) -> str:
    if pos in DECK_SLOT_MAP:
        return f'DECK_LAYOUT["{pos}"]["slot"]'
    return f'"{pos}"  # position not in standard deck map'


def _codegen_action(step_num: int, action: str, meta: Dict, assay: Dict) -> str:
    indent = "    "
    lines: List[str] = []

    if action == "ANALYST_PAUSE":
        reason = _py_str(meta.get("reason", "Analyst verification required"))
        lines.append(f'{indent}print(f"[{{run_id}}] ANALYST PAUSE — action required")')
        lines.append(f'{indent}await robot.analyst_pause(')
        lines.append(f'{indent}    reason="{reason}",')
        lines.append(f'{indent}    timeout_minutes=15,')
        lines.append(f'{indent}    alert_level="WARNING",')
        lines.append(f'{indent})')
        lines.append(f'{indent}log.append({{"step": {step_num}, "action": "ANALYST_PAUSE", "status": "complete"}})')

    elif action == "TRANSPORT":
        from_pos = meta.get("from_pos", "input_rack")
        to_pos = meta.get("to_pos", "B1")
        from_code = _slot_for(from_pos) if from_pos in DECK_SLOT_MAP else f'"{from_pos}"'
        to_code = _slot_for(to_pos) if to_pos in DECK_SLOT_MAP else f'"{to_pos}"'
        lines.append(f'{indent}await robot.move_plate(')
        lines.append(f'{indent}    plate_id=plate_id,')
        lines.append(f'{indent}    from_position={from_code},')
        lines.append(f'{indent}    to_position={to_code},')
        lines.append(f'{indent})')
        lines.append(f'{indent}log.append({{"step": {step_num}, "action": "TRANSPORT", "from": "{from_pos}", "to": "{to_pos}", "status": "complete"}})')

    elif action == "LIQUID_HANDLER":
        volume = meta.get("volume_uL") or assay.get("sample_volume_uL") or 100
        cycles = meta.get("cycles", 1)
        head = assay.get("automate_96_head", "5-200uL")
        flow_rate = FLOW_RATE_BY_HEAD.get(head, 200)
        to_pos = meta.get("to_pos", "B1")
        target = _slot_for(to_pos) if to_pos in DECK_SLOT_MAP else 'DECK_LAYOUT["B1"]["slot"]'
        if cycles > 1:
            lines.append(f'{indent}for cycle in range({cycles}):')
            lines.append(f'{indent}    await lh.dispense(')
            lines.append(f'{indent}        resource={target},')
            lines.append(f'{indent}        vols=[{volume}] * 96,')
            lines.append(f'{indent}        flow_rate={flow_rate},')
            lines.append(f'{indent}        liquid_class="aqueous",')
            lines.append(f'{indent}    )')
            lines.append(f'{indent}    await lh.aspirate(')
            lines.append(f'{indent}        resource={target},')
            lines.append(f'{indent}        vols=[{int(volume * 1.15)}] * 96,')
            lines.append(f'{indent}        flow_rate={int(flow_rate * 0.75)},')
            lines.append(f'{indent}        blow_out=True,')
            lines.append(f'{indent}    )')
        else:
            lines.append(f'{indent}await lh.dispense(')
            lines.append(f'{indent}    resource={target},')
            lines.append(f'{indent}    vols=[{volume}] * 96,')
            lines.append(f'{indent}    flow_rate={flow_rate},')
            lines.append(f'{indent}    liquid_class="aqueous",')
            lines.append(f'{indent})')
        lines.append(f'{indent}log.append({{"step": {step_num}, "action": "LIQUID_HANDLER", "volume_uL": {volume}, "cycles": {cycles}, "head": "{head}", "status": "complete"}})')

    elif action == "WAIT":
        sec = meta.get("duration_seconds", 0)
        lines.append(f'{indent}print(f"[{{run_id}}] Step {step_num}: waiting {sec}s — robot free for other tasks")')
        lines.append(f'{indent}await asyncio.sleep({sec})')
        lines.append(f'{indent}log.append({{"step": {step_num}, "action": "WAIT", "duration_seconds": {sec}, "status": "complete"}})')

    elif action == "INSTRUMENT_TRIGGER":
        inst = meta.get("instrument", "generic")
        lines.append(f'{indent}# Instrument trigger: {inst}')
        lines.append(f'{indent}if "{inst}" in instruments:')
        lines.append(f'{indent}    await instruments["{inst}"].read()')
        lines.append(f'{indent}else:')
        lines.append(f'{indent}    print(f"[{{run_id}}] Step {step_num}: {inst} not wired — skipping trigger")')
        lines.append(f'{indent}log.append({{"step": {step_num}, "action": "INSTRUMENT_TRIGGER", "instrument": "{inst}", "status": "complete"}})')

    else:  # OTHER
        lines.append(f'{indent}# (unclassified step — logged only)')
        lines.append(f'{indent}log.append({{"step": {step_num}, "action": "OTHER", "status": "logged"}})')

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ═══════════════════════════════════════════════════════════════════

def generate_protocol(assay: Dict) -> str:
    """
    Produce a PyLabRobot-style Python module for a single assay.
    Returns the source code as a string (no files written).
    """
    aid = assay["assay_id"]
    aid_lower = aid.lower()
    name = assay.get("name", aid)
    field = assay.get("field", "")
    workbench = assay.get("workbench_id", "N/A")
    robot_min = assay.get("robot_active_minutes", 0)
    total_hrs = assay.get("total_assay_duration_hours", 0)
    purpose = assay.get("purpose", "")
    throughput = assay.get("throughput_samples_per_run", 0)
    difficulty = assay.get("automation_difficulty", "easy")
    regulatory = ", ".join(assay.get("regulatory", []))
    head = assay.get("automate_96_head", "not applicable")

    deck = assay.get("robot_deck_layout", {}) or {}
    automate_steps = assay.get("automate_96_steps", []) or []
    ac = assay.get("acceptance_criteria", {}) or {}
    steps = assay.get("robot_steps", []) or []

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    out: List[str] = []

    # Header
    out.append('"""')
    out.append(f'BioInterface — Auto-generated Protocol')
    out.append(f'Assay    : {aid} — {_py_str(name, 120)}')
    out.append(f'Field    : {field}')
    out.append(f'Workbench: {workbench}')
    out.append(f'Robot min: {robot_min} | Total hours: {total_hrs}')
    out.append(f'Generated: {now}')
    out.append('')
    out.append('PyLabRobot — hardware-agnostic execution layer')
    out.append('Install : pip install pylabrobot')
    out.append('Docs    : https://pylabrobot.org')
    out.append('"""')
    out.append('')
    out.append('import asyncio')
    out.append('from pylabrobot.liquid_handling import LiquidHandler')
    out.append('from pylabrobot.liquid_handling.backends import SerializingBackend')
    out.append('from pylabrobot.resources import Deck, Plate, TipRack')
    out.append('from pylabrobot.resources import Container as Reservoir')
    out.append('')

    # Deck layout
    out.append('# ── DECK LAYOUT ──────────────────────────────────────')
    out.append('# Loaded from assay["robot_deck_layout"]')
    out.append('DECK_LAYOUT = {')
    for pos, desc in deck.items():
        slot = DECK_SLOT_MAP.get(pos, 0)
        out.append(f'    "{pos}": {{"slot": {slot}, "description": "{_py_str(desc)}"}},')
    out.append('}')
    out.append('')

    # Acceptance criteria
    out.append('# ── ACCEPTANCE CRITERIA ──────────────────────────────')
    out.append('# Loaded from assay["acceptance_criteria"]')
    out.append('ACCEPTANCE_CRITERIA = {')
    for k, v in ac.items():
        out.append(f'    "{k}": "{_py_str(v)}",')
    out.append('}')
    out.append('')

    # Function signature + docstring
    out.append('# ── PROTOCOL FUNCTION ────────────────────────────────')
    out.append(f'async def run_{aid_lower}(')
    out.append('    robot,          # Rail System rail arm')
    out.append('    lh,             # PyLabRobot LiquidHandler (AutoMATE 96 or similar)')
    out.append('    instruments,    # dict of other instruments: plate_reader, incubator, etc.')
    out.append('    plate_id: str = "PLATE-001",')
    out.append('    analyst_name: str = "Analyst",')
    out.append('    run_id: str = None,')
    out.append('):')
    out.append('    """')
    out.append(f'    {_py_str(name, 100)}')
    out.append('')
    out.append(f'    Purpose    : {_py_str(purpose, 200)}')
    out.append(f'    Workbench  : {workbench}')
    out.append(f'    Robot time : {robot_min} minutes active')
    out.append(f'    Total time : {total_hrs} hours')
    out.append(f'    Throughput : {throughput} samples/run')
    out.append(f'    Difficulty : {difficulty}')
    out.append(f'    AutoMATE 96: head={head}, tagged_steps={len(automate_steps)}/{len(steps)}')
    out.append(f'    Regulatory : {_py_str(regulatory, 150)}')
    out.append('    """')
    out.append('    import datetime')
    out.append('    run_id = run_id or f"RUN-{datetime.datetime.now():%Y%m%d-%H%M%S}"')
    out.append('    log = []')
    out.append('')
    out.append(f'    print(f"[{{run_id}}] Starting {aid}: {_py_str(name, 80)}")')
    out.append('    print(f"[{run_id}] Analyst: {analyst_name}")')
    out.append('    print(f"[{run_id}] Plate: {plate_id}")')
    out.append('')

    # Per-step codegen
    counts = {k: 0 for k in ("TRANSPORT", "LIQUID_HANDLER", "WAIT", "ANALYST_PAUSE", "INSTRUMENT_TRIGGER", "OTHER")}
    for i, step in enumerate(steps, 1):
        action, meta = classify_step(step, i, automate_steps)
        counts[action] = counts.get(action, 0) + 1
        out.append(f'    # ── STEP {i} ── [{action}]')
        out.append(f'    # "{_py_str(step, 240)}"')
        out.append(_codegen_action(i, action, meta, assay))
        out.append('')

    # Return / closer
    out.append('    print(f"[{run_id}] Protocol complete")')
    out.append('    print(f"[{run_id}] Acceptance criteria to verify: {ACCEPTANCE_CRITERIA}")')
    out.append('    return {')
    out.append('        "run_id": run_id,')
    out.append(f'        "assay_id": "{aid}",')
    out.append('        "plate_id": plate_id,')
    out.append('        "steps_completed": len(log),')
    out.append('        "log": log,')
    out.append('        "status": "complete",')
    out.append('    }')
    out.append('')
    out.append('')

    # Simulation entrypoint
    out.append('# ── SIMULATION ENTRYPOINT ────────────────────────────')
    out.append('# Runs the protocol against PyLabRobot SerializingBackend')
    out.append('# and a MockRailRobot. Requires: pip install pylabrobot')
    out.append('if __name__ == "__main__":')
    out.append('    class MockRailRobot:')
    out.append('        async def move_plate(self, **kwargs):')
    out.append('            print(f"  [RAIL] move_plate: {kwargs}")')
    out.append('        async def analyst_pause(self, reason, timeout_minutes, alert_level):')
    out.append('            print(f"  [ANALYST PAUSE] {reason}")')
    out.append('            # In real operation, block until the operator acknowledges.')
    out.append('')
    out.append('    async def simulate():')
    out.append('        backend = SerializingBackend(num_channels=96)')
    out.append('        deck_obj = Deck()')
    out.append('        lh = LiquidHandler(backend=backend, deck=deck_obj)')
    out.append('        await lh.setup()')
    out.append('        robot = MockRailRobot()')
    out.append('        instruments = {}')
    out.append(f'        result = await run_{aid_lower}(')
    out.append('            robot=robot, lh=lh, instruments=instruments,')
    out.append('            plate_id="SIM-001", analyst_name="Simulation",')
    out.append('        )')
    out.append('        print()')
    out.append('        print(f"Simulation complete: {result[\'steps_completed\']} steps")')
    out.append('        await lh.stop()')
    out.append('')
    out.append('    asyncio.run(simulate())')
    out.append('')

    # Stash classification counts as module attribute (used by callers)
    src = "\n".join(out)
    generate_protocol.last_counts = counts  # type: ignore[attr-defined]
    return src


# ═══════════════════════════════════════════════════════════════════
# BATCH GENERATOR
# ═══════════════════════════════════════════════════════════════════

def generate_all_protocols(output_dir: str = "protocols/") -> List[str]:
    """
    Generate protocol .py files for every assay in both field libraries.
    Returns list of generated file paths. Also stores per-type counts
    on generate_all_protocols.last_counts and .failures.
    """
    from field_01_biopharma_v2 import BIOPHARMA_ASSAYS
    try:
        from field_04_drug_discovery_hts_v2 import HTS_ASSAYS
    except ImportError:
        HTS_ASSAYS = []

    os.makedirs(output_dir, exist_ok=True)

    totals = {k: 0 for k in ("TRANSPORT", "LIQUID_HANDLER", "WAIT", "ANALYST_PAUSE", "INSTRUMENT_TRIGGER", "OTHER")}
    generated: List[str] = []
    failures: List[Tuple[str, str]] = []

    for assay in BIOPHARMA_ASSAYS + HTS_ASSAYS:
        aid = assay["assay_id"]
        try:
            src = generate_protocol(assay)
            # Verify the generated source parses — protects against silent codegen bugs
            compile(src, f"<generated:{aid}>", "exec")
            path = os.path.join(output_dir, f"{aid.lower()}_protocol.py")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(src)
            generated.append(path)
            step_counts = getattr(generate_protocol, "last_counts", {})
            for k, v in step_counts.items():
                totals[k] = totals.get(k, 0) + v
        except Exception as e:
            failures.append((aid, f"{type(e).__name__}: {e}"))

    generate_all_protocols.last_counts = totals          # type: ignore[attr-defined]
    generate_all_protocols.failures = failures           # type: ignore[attr-defined]
    return generated


# ═══════════════════════════════════════════════════════════════════
# MULTI-INSTRUMENT EXECUTION PLAN (v3 schema bridge)
# ═══════════════════════════════════════════════════════════════════

def generate_execution_plan(
    assay: dict,
    deployment_context: str = "manual",
    inject_transport: bool = True,
) -> dict:
    """Generate a structured multi-instrument execution plan with
    optional explicit transport steps.

    Args:
        assay: The assay dict
        deployment_context: 'manual' | 'robotic_arm' | 'rail_robot' | 'scheduler'
        inject_transport: If True, inserts explicit transport steps
            between instrument transitions
    """
    from assay_schema_v3 import (
        convert_legacy_assay_to_v3,
        estimate_total_duration,
        list_required_instruments,
        inject_transport_steps,
    )

    # Use v3 steps if available, otherwise convert legacy
    if assay.get("protocol_steps_v3"):
        steps = list(assay["protocol_steps_v3"])
    else:
        steps = convert_legacy_assay_to_v3(assay)

    if inject_transport:
        steps = inject_transport_steps(steps, deployment_context)

    # Group steps into phases by instrument transitions
    phases = []
    current_phase = None
    for step in steps:
        inst = step["instrument"]
        if current_phase is None or current_phase["instrument"] != inst:
            if current_phase:
                phases.append(current_phase)
            current_phase = {
                "phase_number": len(phases) + 1,
                "instrument": inst,
                "steps": [],
            }
        current_phase["steps"].append(step)
    if current_phase:
        phases.append(current_phase)

    total_duration_seconds = estimate_total_duration(steps)
    transport_count = sum(1 for s in steps if s["step_type"] == "transport")

    return {
        "protocol_name": assay.get("name", "Unknown"),
        "assay_id": assay.get("assay_id", ""),
        "field": assay.get("field", ""),
        "deployment_context": deployment_context,
        "total_duration_minutes": round(total_duration_seconds / 60, 1),
        "instruments_required": list_required_instruments(steps),
        "transport_steps_count": transport_count,
        "execution_phases": phases,
        "all_steps": steps,
        "regulatory_references": assay.get("regulatory", []),
        "acceptance_criteria": assay.get("acceptance_criteria", {}),
        "format_version": "v3.1",
    }


def export_execution_plan_json(
    assay: dict,
    deployment_context: str = "manual",
) -> str:
    """Export execution plan as a formatted JSON string."""
    import json as _json
    return _json.dumps(
        generate_execution_plan(assay, deployment_context=deployment_context),
        indent=2,
    )


def generate_orchestrator_code(
    assay: dict,
    target: str = "unitelabs",
    deployment_context: str = "manual",
    deck_config: dict = None,
) -> str:
    """Generate Python code for a specific orchestrator,
    optionally injecting deck context.

    target: 'unitelabs' | 'rail_system' | 'hamilton_venus' | 'pylabrobot'
    """
    deck_preamble = ""
    if deck_config and deck_config.get("positions"):
        try:
            from deck_designer import deck_to_pylabrobot_setup
            deck_preamble = (
                "\n# === Deck configuration (from BioInterface Deck Designer) ===\n"
                + deck_to_pylabrobot_setup(
                    deck_config["positions"],
                    deck_config.get("deck_type", "hamilton_star_16pos"),
                )
                + "\n# === End deck config ===\n\n"
            )
        except Exception:
            deck_preamble = ""

    if target == "pylabrobot":
        return deck_preamble + generate_protocol(assay)

    plan = generate_execution_plan(assay, deployment_context=deployment_context)

    if target == "opentrons":
        # Native Opentrons Protocol API (https://docs.opentrons.com/v2/)
        ot_lines = [
            f"# Opentrons Protocol API for {plan['protocol_name']}",
            f"# Generated by BioInterface (assay {plan['assay_id']})",
            f"# Total duration: {plan['total_duration_minutes']} min",
            f"# Instruments: {', '.join(plan['instruments_required'])}",
            "",
            "from opentrons import protocol_api",
            "",
            "metadata = {",
            f'    "protocolName": "{plan["protocol_name"]}",',
            '    "author": "BioInterface",',
            f'    "description": "{plan["assay_id"]} — auto-generated",',
            '    "apiLevel": "2.13",',
            "}",
            "",
            "def run(protocol: protocol_api.ProtocolContext):",
            '    """Auto-generated Opentrons protocol. Verify deck setup before running."""',
            "",
            "    # ── Labware (adjust slot numbers + part numbers per your deck) ──",
            "    tiprack_200 = protocol.load_labware('opentrons_96_tiprack_200ul', 1)",
            "    tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', 4)",
            "    sample_plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 2)",
            "    reagent_reservoir = protocol.load_labware('nest_12_reservoir_15ml', 3)",
            "    output_plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 5)",
            "",
            "    # ── Modules ──",
        ]

        # Insert module loads conditionally based on instruments_required
        if "thermocycler" in plan["instruments_required"]:
            ot_lines.append(
                "    thermocycler = protocol.load_module('thermocycler module gen2')"
            )
            ot_lines.append(
                "    tc_plate = thermocycler.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')"
            )
        if "magnetic_separator" in plan["instruments_required"]:
            ot_lines.append(
                "    magnetic_module = protocol.load_module('magnetic module gen2', 6)"
            )
            ot_lines.append(
                "    mag_plate = magnetic_module.load_labware('nest_96_wellplate_2ml_deep')"
            )
        if "shaker" in plan["instruments_required"]:
            ot_lines.append(
                "    heater_shaker = protocol.load_module('heaterShakerModuleV1', 7)"
            )

        ot_lines.extend([
            "",
            "    # ── Pipettes ──",
            "    p200_multi = protocol.load_instrument(",
            "        'p300_multi_gen2', 'left', tip_racks=[tiprack_200]",
            "    )",
            "    p20_single = protocol.load_instrument(",
            "        'p20_single_gen2', 'right', tip_racks=[tiprack_20]",
            "    )",
            "",
            "    # ── Steps ──",
        ])

        for phase in plan["execution_phases"]:
            ot_lines.append(
                f"    # === Phase {phase['phase_number']}: {phase['instrument']} ==="
            )
            for step in phase["steps"]:
                params = step.get("parameters", {})
                inst = step["instrument"]
                stype = step["step_type"]
                desc = step.get("description", "")[:100]
                ot_lines.append(f"    # Step {step['step_number']}: {desc}")

                if inst == "liquid_handler":
                    if stype == "dispense":
                        vol = params.get("volume_uL", 100)
                        ot_lines.append(
                            f"    p200_multi.transfer({vol}, "
                            f"reagent_reservoir['A1'], sample_plate.columns())"
                        )
                    elif stype == "aspirate":
                        vol = params.get("volume_uL", 100)
                        ot_lines.append(
                            f"    # aspirate {vol} uL — adjust source/dest"
                        )
                        ot_lines.append(
                            f"    p200_multi.transfer({vol}, "
                            f"sample_plate.columns(), output_plate.columns())"
                        )
                    elif stype == "transfer":
                        vol = params.get("volume_uL", 50)
                        ot_lines.append(
                            f"    p200_multi.transfer({vol}, "
                            f"sample_plate.columns(), output_plate.columns(), new_tip='always')"
                        )
                    elif stype == "mix":
                        cycles = params.get("cycles", 5)
                        ot_lines.append(
                            f"    for col in sample_plate.columns():"
                        )
                        ot_lines.append(
                            f"        p200_multi.pick_up_tip()"
                        )
                        ot_lines.append(
                            f"        p200_multi.mix({cycles}, 50, col[0])"
                        )
                        ot_lines.append(
                            f"        p200_multi.drop_tip()"
                        )
                elif inst == "thermocycler":
                    if stype == "thermocycle":
                        temp = params.get("temperature_C", 25)
                        dur_min = params.get(
                            "duration_minutes",
                            step.get("duration_seconds", 60) // 60,
                        )
                        ot_lines.append(
                            f"    thermocycler.set_block_temperature({temp}, "
                            f"hold_time_minutes={dur_min})"
                        )
                    elif stype == "incubate":
                        temp = params.get("temperature_C", 25)
                        ot_lines.append(
                            f"    thermocycler.set_block_temperature({temp})"
                        )
                elif inst == "magnetic_separator":
                    dur_s = step.get("duration_seconds", 60)
                    ot_lines.append("    magnetic_module.engage()")
                    ot_lines.append(f"    protocol.delay(seconds={dur_s})")
                elif inst == "shaker":
                    rpm = params.get("rpm", 1500)
                    dur_s = step.get("duration_seconds", 30)
                    ot_lines.append(
                        f"    heater_shaker.set_and_wait_for_shake_speed({rpm})"
                    )
                    ot_lines.append(f"    protocol.delay(seconds={dur_s})")
                    ot_lines.append("    heater_shaker.deactivate_shaker()")
                elif inst == "incubator":
                    dur_s = step.get("duration_seconds", 60)
                    ot_lines.append(
                        f"    protocol.delay(seconds={dur_s})  # passive incubation"
                    )
                elif inst == "fluorometer" or inst == "plate_reader":
                    ot_lines.append(
                        f"    # External instrument: {inst} — analyst-mediated read"
                    )
                elif inst == "analyst":
                    ot_lines.append(
                        f"    protocol.pause('{desc.replace(chr(39), chr(34))}')"
                    )
                else:
                    ot_lines.append(f"    # (unmapped: {inst} / {stype})")
                ot_lines.append("")

        ot_lines.append("    # ── End of protocol ──")
        return deck_preamble + "\n".join(ot_lines)

    if target in ("unitelabs", "rail_system"):
        banner = (
            "Rail System protocol"
            if target == "rail_system"
            else "UniteLabs protocol"
        )

        lines = [
            f"# {banner} for {plan['protocol_name']}",
            f"# Generated by BioInterface (assay {plan['assay_id']})",
            f"# Total duration: {plan['total_duration_minutes']} min",
            f"# Instruments: {', '.join(plan['instruments_required'])}",
            "",
            "from unitelabs.automate import Workflow, Connect",
            "import asyncio",
            "",
            "async def run_protocol(connect: Connect):",
            f'    """Execute {plan["assay_id"]}: {plan["protocol_name"]}"""',
            f'    workflow = Workflow(name="{plan["protocol_name"]}")',
            "",
        ]

        for phase in plan["execution_phases"]:
            lines.append(
                f"    # === Phase {phase['phase_number']}: "
                f"{phase['instrument']} ==="
            )
            for step in phase["steps"]:
                lines.append(
                    f"    # Step {step['step_number']}: "
                    f"{step['description'][:100]}"
                )
                params = step.get("parameters", {})
                inst = step["instrument"]
                stype = step["step_type"]
                if inst == "liquid_handler":
                    if stype == "dispense":
                        vol = params.get("volume_uL", "VOLUME")
                        lines.append(
                            f"    await connect.liquid_handler.dispense(volume={vol})"
                        )
                    elif stype == "aspirate":
                        vol = params.get("volume_uL", "VOLUME")
                        lines.append(
                            f"    await connect.liquid_handler.aspirate(volume={vol})"
                        )
                    elif stype == "mix":
                        rpm = params.get("rpm", 400)
                        lines.append(
                            f"    await connect.liquid_handler.mix(rpm={rpm})"
                        )
                    elif stype == "transfer":
                        vol = params.get("volume_uL", "VOLUME")
                        lines.append(
                            f"    await connect.liquid_handler.transfer(volume={vol})"
                        )
                elif inst == "thermocycler":
                    temp = params.get("temperature_C", 25)
                    dur = step.get("duration_seconds", 60)
                    lines.append(
                        f"    await connect.thermocycler.incubate(temp={temp}, duration={dur})"
                    )
                elif inst == "magnetic_separator":
                    dur = step.get("duration_seconds", 60)
                    lines.append(
                        f"    await connect.magnet.engage(duration={dur})"
                    )
                elif inst == "centrifuge":
                    rpm = params.get("rpm", 2000)
                    dur = step.get("duration_seconds", 60)
                    lines.append(
                        f"    await connect.centrifuge.spin(rpm={rpm}, duration={dur})"
                    )
                elif inst == "incubator":
                    temp = params.get("temperature_C", 37)
                    dur = step.get("duration_seconds", 60)
                    lines.append(
                        f"    await connect.incubator.hold(temp={temp}, duration={dur})"
                    )
                elif inst == "plate_reader":
                    wl = params.get("wavelength_nm", 450)
                    lines.append(
                        f"    await connect.plate_reader.read_absorbance(wavelength={wl})"
                    )
                elif inst == "shaker":
                    rpm = params.get("rpm", 400)
                    dur = step.get("duration_seconds", 60)
                    lines.append(
                        f"    await connect.shaker.run(rpm={rpm}, duration={dur})"
                    )
                elif inst == "vacuum_manifold":
                    lines.append(
                        f"    await connect.vacuum.apply(duration={step.get('duration_seconds', 60)})"
                    )
                elif inst == "plate_sealer":
                    lines.append("    await connect.plate_sealer.seal()")
                elif inst in ("robotic_arm", "rail_robot", "scheduler"):
                    src = params.get("source_instrument", "unknown")
                    dst = params.get("destination_instrument", "unknown")
                    if inst == "robotic_arm":
                        lines.append(
                            f"    await connect.robotic_arm.transfer("
                            f"source='{src}', destination='{dst}')"
                        )
                    elif inst == "rail_robot":
                        lines.append(
                            f"    await connect.rail.move_plate("
                            f"from_position='{src}', to_position='{dst}')"
                        )
                    else:  # scheduler
                        lines.append(
                            f"    await connect.scheduler.dispatch_move("
                            f"source='{src}', destination='{dst}')"
                        )
                elif inst == "analyst":
                    if stype == "transport":
                        src = params.get("source_instrument", "unknown")
                        dst = params.get("destination_instrument", "unknown")
                        lines.append(
                            f"    # ANALYST: manually transfer plate from {src} to {dst}"
                        )
                        lines.append(
                            f"    await connect.analyst.pause("
                            f'message="Move plate from {src} to {dst}")'
                        )
                    else:
                        lines.append(
                            f"    await connect.analyst.pause("
                            f'reason="{step["description"][:60]}")'
                        )
                else:
                    lines.append(f"    # (unmapped instrument: {inst})")
                lines.append("")

        lines.extend([
            "    await workflow.execute()",
            "    return workflow.results",
            "",
            'if __name__ == "__main__":',
            "    connect = Connect.from_env()",
            "    asyncio.run(run_protocol(connect))",
        ])
        return deck_preamble + "\n".join(lines)

    return f"# Unsupported target: {target}"


# ═══════════════════════════════════════════════════════════════════
# CLI — generate BIO_005 as a demo and summarise
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from field_01_biopharma_v2 import BIOPHARMA_ASSAYS

    bio_005 = next(a for a in BIOPHARMA_ASSAYS if a["assay_id"] == "BIO_005")
    src = generate_protocol(bio_005)

    out_path = "bio_005_protocol.py"
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(src)

    # Parse-check
    compile(src, out_path, "exec")

    counts = getattr(generate_protocol, "last_counts", {})
    total_steps = sum(counts.values())

    print("=" * 60)
    print(f"Generated: {out_path} ({len(src.splitlines())} lines)")
    print(f"Assay    : {bio_005['assay_id']} — {bio_005['name']}")
    print("=" * 60)
    print("Step classification:")
    for k, v in counts.items():
        if v:
            print(f"  {k:20} {v:3}")
    print(f"  {'TOTAL':20} {total_steps:3}")
    print()
    print("Run `python bio_005_protocol.py` to simulate (requires pylabrobot).")
