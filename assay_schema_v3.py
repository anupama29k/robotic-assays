"""
assay_schema_v3.py — Multi-instrument execution-plan schema.

Adds a structured `protocol_steps_v3` representation that orchestrators
(UniteLabs, Rail System, Hamilton Venus, PyLabRobot) can consume.
Legacy `robot_steps` strings on the existing 30 assays are parsed
on the fly via `parse_legacy_step` — no schema migration required.
"""

from typing import Literal, TypedDict

try:
    from typing import NotRequired  # py 3.11+
except ImportError:
    from typing_extensions import NotRequired

import re


StepType = Literal[
    "dispense", "aspirate", "transfer", "mix",
    "thermocycle", "magnetic_separation",
    "centrifuge", "incubate", "read",
    "wait", "analyst", "vacuum_filtration",
    "shake", "pierce_seal",
    "transport",  # explicit plate transition between instruments
]

InstrumentType = Literal[
    "liquid_handler", "thermocycler",
    "magnetic_separator", "centrifuge",
    "incubator", "plate_reader",
    "fragment_analyzer", "fluorometer",
    "vacuum_manifold", "shaker",
    "plate_sealer", "analyst",
    "robotic_arm", "rail_robot", "scheduler",
]


class ProtocolStepV3(TypedDict):
    step_number: int
    step_type: StepType
    instrument: InstrumentType
    instrument_id: NotRequired[str]
    description: str
    parameters: dict
    duration_seconds: int
    depends_on: NotRequired[list]
    automation_difficulty: NotRequired[Literal["trivial", "moderate", "complex"]]
    notes: NotRequired[str]


# === Helper functions for legacy → v3 conversion ===

def parse_legacy_step(step_str: str, step_number: int) -> dict:
    """Convert a legacy robot_steps string into a structured ProtocolStepV3.

    Pattern-matches keywords (centrifuge, thermocycle, incubate, magnet,
    read, mix, aspirate, dispense) and extracts numeric parameters
    (rpm, duration, temperature, wavelength, volume) via regex. Falls
    back to "dispense" / "liquid_handler" for unrecognized step text,
    or "analyst" if the original step contains the [ANALYST STEP] marker.
    """
    s = step_str.strip()
    is_analyst = "[ANALYST STEP" in s
    s_clean = s.replace("[ANALYST STEP", "").replace("]", "", 1).strip()
    s_lower = (
        s_clean.lower()
        .replace('×', 'x')      # U+00D7 multiplication sign
        .replace('μ', 'u')      # U+03BC Greek small letter mu
        .replace('µ', 'u')      # U+00B5 micro sign
    )

    step = {
        "step_number": step_number,
        "step_type": "analyst" if is_analyst else "dispense",
        "instrument": "analyst" if is_analyst else "liquid_handler",
        "description": s_clean[:240],
        "parameters": {},
        "duration_seconds": 30,
    }

    if "centrifuge" in s_lower:
        step["step_type"] = "centrifuge"
        step["instrument"] = "centrifuge"
        rpm_match = re.search(r"(\d[\d,]*)\s*(?:rpm|x\s*g)", s_lower)
        if rpm_match:
            rpm_str = rpm_match.group(1).replace(",", "")
            step["parameters"]["rpm"] = int(rpm_str)
        time_match = re.search(r"(\d+)\s*(min|minute|sec|second)", s_lower)
        if time_match:
            val = int(time_match.group(1))
            unit = time_match.group(2)
            secs = val * 60 if "min" in unit else val
            step["parameters"]["duration_seconds"] = secs
            step["duration_seconds"] = secs

    elif "thermocycle" in s_lower or "incubate" in s_lower or "incubation" in s_lower:
        if "thermocycle" in s_lower:
            step["step_type"] = "thermocycle"
            step["instrument"] = "thermocycler"
        else:
            step["step_type"] = "incubate"
            step["instrument"] = "incubator"
        temp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:°|deg|c\b)", s_lower)
        if temp_match:
            step["parameters"]["temperature_C"] = float(temp_match.group(1))
        time_match = re.search(r"(\d+)\s*(min|minute|hour|sec)", s_lower)
        if time_match:
            val = int(time_match.group(1))
            unit = time_match.group(2)
            if "hour" in unit:
                secs = val * 3600
            elif "min" in unit:
                secs = val * 60
            else:
                secs = val
            step["parameters"]["duration_seconds"] = secs
            step["duration_seconds"] = secs

    elif "magnet" in s_lower:
        step["step_type"] = "magnetic_separation"
        step["instrument"] = "magnetic_separator"

    elif (("read" in s_lower or "od" in s_lower) and
          ("absorbance" in s_lower or "fluorescence" in s_lower
           or "luminescence" in s_lower or "od" in s_lower
           or "nm" in s_lower)):
        step["step_type"] = "read"
        step["instrument"] = "plate_reader"
        wl_match = re.search(r"(\d+)\s*nm", s_lower)
        if wl_match:
            step["parameters"]["wavelength_nm"] = int(wl_match.group(1))

    elif "mix" in s_lower or "vortex" in s_lower:
        step["step_type"] = "mix"
        step["instrument"] = "liquid_handler"
        rpm_match = re.search(r"(\d[\d,]*)\s*rpm", s_lower)
        if rpm_match:
            rpm_str = rpm_match.group(1).replace(",", "")
            step["parameters"]["rpm"] = int(rpm_str)

    elif "seal" in s_lower:
        step["step_type"] = "pierce_seal"
        step["instrument"] = "plate_sealer"

    elif "filter" in s_lower or "vacuum" in s_lower:
        step["step_type"] = "vacuum_filtration"
        step["instrument"] = "vacuum_manifold"

    elif "shake" in s_lower or "shaker" in s_lower:
        step["step_type"] = "shake"
        step["instrument"] = "shaker"

    elif "aspirate" in s_lower:
        step["step_type"] = "aspirate"
        step["instrument"] = "liquid_handler"
        vol_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:ul|µl|microliter)", s_lower)
        if vol_match:
            step["parameters"]["volume_uL"] = float(vol_match.group(1))

    elif "dispense" in s_lower or "transfer" in s_lower or "add " in s_lower:
        step["step_type"] = "transfer" if "transfer" in s_lower else "dispense"
        step["instrument"] = "liquid_handler"
        vol_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:ul|µl|microliter)", s_lower)
        if vol_match:
            step["parameters"]["volume_uL"] = float(vol_match.group(1))

    return step


def convert_legacy_assay_to_v3(legacy_assay: dict) -> list:
    """Convert a v2 assay's robot_steps into a list of ProtocolStepV3."""
    legacy_steps = legacy_assay.get("robot_steps", [])
    return [parse_legacy_step(s, i) for i, s in enumerate(legacy_steps, 1)]


def estimate_total_duration(protocol_steps: list) -> int:
    """Estimate total protocol duration in seconds.
    Sums sequential durations; parallelism handled by orchestrator at runtime.
    """
    return sum(s.get("duration_seconds", 30) for s in protocol_steps)


def list_required_instruments(protocol_steps: list) -> list:
    """Extract unique non-analyst instruments from a step list."""
    instruments = set()
    for step in protocol_steps:
        inst = step.get("instrument")
        if inst and inst != "analyst":
            instruments.add(inst)
    return sorted(instruments)


def inject_transport_steps(
    protocol_steps: list,
    deployment_context: str = "manual",
) -> list:
    """Inject explicit transport steps between phases where the
    instrument changes.

    deployment_context: 'manual' | 'robotic_arm' | 'rail_robot' | 'scheduler'
    """
    if not protocol_steps:
        return []

    transport_instrument = {
        "manual": "analyst",
        "robotic_arm": "robotic_arm",
        "rail_robot": "rail_robot",
        "scheduler": "scheduler",
    }.get(deployment_context, "analyst")

    transport_duration = {
        "manual": 60,
        "robotic_arm": 30,
        "rail_robot": 20,
        "scheduler": 25,
    }.get(deployment_context, 60)

    transport_description_template = {
        "manual": "[ANALYST STEP] Manually transfer plate from {src} to {dst}",
        "robotic_arm": "Robotic arm transport: pick from {src}, deliver to {dst}",
        "rail_robot": "Rail robot transport: move plate from {src} to {dst}",
        "scheduler": "Scheduler dispatches transport: {src} -> {dst}",
    }.get(deployment_context, "Transport plate from {src} to {dst}")

    enriched = []
    next_step_num = 1

    for i, step in enumerate(protocol_steps):
        new_step = dict(step)
        new_step["step_number"] = next_step_num
        enriched.append(new_step)
        next_step_num += 1

        if i + 1 < len(protocol_steps):
            current_inst = step["instrument"]
            next_inst = protocol_steps[i + 1]["instrument"]

            # Skip if same instrument or either side is analyst pause
            if (current_inst != next_inst
                    and current_inst != "analyst"
                    and next_inst != "analyst"):
                transport_step = {
                    "step_number": next_step_num,
                    "step_type": "transport",
                    "instrument": transport_instrument,
                    "description": transport_description_template.format(
                        src=current_inst, dst=next_inst
                    ),
                    "parameters": {
                        "source_instrument": current_inst,
                        "destination_instrument": next_inst,
                        "deployment_context": deployment_context,
                    },
                    "duration_seconds": transport_duration,
                    "automation_difficulty": (
                        "trivial" if deployment_context != "manual" else "moderate"
                    ),
                    "notes": (
                        f"Auto-injected transport step for {deployment_context} deployment"
                    ),
                }
                enriched.append(transport_step)
                next_step_num += 1

    return enriched
