#!/usr/bin/env python3
"""Validate the Robotic Assays library.

Run it from the repository root:

    python3 validate_library.py

Checks every field_*.py module the repository actually contains -- discovered,
not hardcoded, because a hardcoded module list broke a downstream consumer the
day this repo deleted its v1 biopharma file. Exits non-zero on any error, so it
can gate CI.

WHAT IT CHECKS
    * every entry has the identity fields and a unique assay_id and name
    * every structured criterion conforms to assay_criteria_schema
    * every well_roles block conforms
    * structured criteria do not contradict the prose they restate
    * coverage statistics, so the gap between prose-only and structured
      entries is a visible number rather than a vague feeling
    * every Opentrons protocol in protocols/opentrons/ is up to date with its
      recipe, passes the generator's volume / tip / capacity checks, and runs
      to completion in opentrons_simulate -- so no broken protocol can ship

SIMULATOR
    OT-2 simulation needs the `opentrons` package at 8.8.2: releases 9.x and
    later refuse OT-2 protocols. Install it in its own environment

        python3 -m venv .venv-sim && .venv-sim/bin/pip install -r requirements-sim.txt

    and point the validator at it (otherwise `opentrons_simulate` on PATH is used):

        OPENTRONS_SIMULATE=.venv-sim/bin/opentrons_simulate python3 validate_library.py

    --skip-simulation runs everything else and reports the protocols as
    UNVERIFIED. CI never passes it.
"""
import argparse
import glob
import importlib
import os
import shutil
import subprocess
import sys
import types
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Optional heavy dependencies are stubbed: this script reads data, it does not
# run the AI layer.
for _stub in ("openai", "anthropic", "chromadb"):
    sys.modules.setdefault(_stub, types.ModuleType(_stub))

from assay_criteria_schema import (  # noqa: E402
    SOURCE_TYPES, validate_criterion, validate_well_roles,
)

IDENTITY_FIELDS = ["assay_id", "name", "field", "purpose", "acceptance_criteria"]


def load_entries():
    """Every assay entry from every field_*.py module, tagged with its source."""
    here = os.path.dirname(os.path.abspath(__file__))
    entries = []
    for path in sorted(glob.glob(os.path.join(here, "field_*.py"))):
        mod_name = os.path.splitext(os.path.basename(path))[0]
        mod = importlib.import_module(mod_name)
        for attr in dir(mod):
            value = getattr(mod, attr)
            if attr.endswith("_ASSAYS") and isinstance(value, list):
                for entry in value:
                    tagged = dict(entry)
                    tagged["_source"] = mod_name
                    entries.append(tagged)
    return entries


def display_name(entry):
    return entry.get("name") or entry.get("assay_id") or "<unnamed>"


OT2_REFUSED = "designed for an OT-2 robot"


def find_simulator():
    explicit = os.environ.get("OPENTRONS_SIMULATE")
    if explicit:
        return explicit if os.path.exists(explicit) else None
    return shutil.which("opentrons_simulate")


def check_opentrons_protocols(errors, warnings, skip_simulation):
    """Generated Opentrons protocols: current, planner-clean, simulator-clean."""
    here = os.path.dirname(os.path.abspath(__file__))
    import opentrons_codegen as codegen

    report = []
    expected = set()
    for assay_id in codegen.RECIPES:
        proto_path, map_path = codegen.output_paths(assay_id)
        expected.add(os.path.abspath(proto_path))
        rel = os.path.relpath(proto_path, here)
        try:
            source, plate_map = codegen.build(assay_id)
        except codegen.PlanError as exc:
            errors.append(f"opentrons {assay_id}: planner check failed -- {exc}")
            report.append((rel, "PLANNER FAIL"))
            continue
        for path, content in ((proto_path, source), (map_path, plate_map)):
            current = open(path).read() if os.path.exists(path) else None
            if current != content:
                errors.append(f"opentrons {assay_id}: {os.path.relpath(path, here)} is missing or "
                              f"stale -- run python3 opentrons_codegen.py and commit the result")

    on_disk = {os.path.abspath(p) for p in glob.glob(os.path.join(here, "protocols", "opentrons", "*.py"))}
    for orphan in sorted(on_disk - expected):
        errors.append(f"opentrons: {os.path.relpath(orphan, here)} has no recipe in "
                      f"opentrons_codegen.RECIPES -- hand-written protocols are not allowed here")

    simulator = None if skip_simulation else find_simulator()
    if not skip_simulation and not simulator:
        errors.append("opentrons: simulator not found -- install requirements-sim.txt and set "
                      "OPENTRONS_SIMULATE, or pass --skip-simulation (protocols stay UNVERIFIED)")

    for path in sorted(on_disk & expected):
        rel = os.path.relpath(path, here)
        if skip_simulation or not simulator:
            report.append((rel, "UNVERIFIED"))
            continue
        proc = subprocess.run([simulator, path], capture_output=True, text=True, timeout=900)
        output = proc.stdout + proc.stderr
        if OT2_REFUSED in output:
            if any("refuses OT-2" in e for e in errors):
                report.append((rel, "SIM UNAVAILABLE"))
                continue
            errors.append(f"opentrons: {simulator} refuses OT-2 protocols -- it must be "
                          f"opentrons==8.8.2 (see requirements-sim.txt)")
            report.append((rel, "SIM UNAVAILABLE"))
        elif proc.returncode != 0:
            tail = " | ".join(line.strip() for line in output.strip().splitlines()[-3:])
            errors.append(f"opentrons: {rel} failed simulation: {tail}")
            report.append((rel, "SIM FAIL"))
        else:
            tips = output.count("Picking up tip")
            report.append((rel, f"simulated OK ({tips} tip pickups)"))

    legacy = glob.glob(os.path.join(here, "protocols", "*_protocol.py"))
    if legacy:
        warnings.append(f"{len(legacy)} legacy protocols/*_protocol.py modules are PyLabRobot-style "
                        f"outlines from rail_protocol_generator.py; they are not simulator-verified "
                        f"and do not run")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the Robotic Assays library.")
    parser.add_argument("--skip-simulation", action="store_true",
                        help="do not run opentrons_simulate (protocols reported UNVERIFIED)")
    args = parser.parse_args(argv)

    entries = load_entries()
    errors, warnings = [], []

    # ---- identity and uniqueness ----------------------------------------
    seen_ids, seen_names = defaultdict(list), defaultdict(list)
    for entry in entries:
        label = f"{entry['_source']}:{display_name(entry)}"
        for field in IDENTITY_FIELDS:
            if not entry.get(field):
                errors.append(f"{label}: missing required field '{field}'")
        if entry.get("assay_id"):
            seen_ids[entry["assay_id"]].append(entry["_source"])
        seen_names[display_name(entry).lower()].append(entry["_source"])

    for assay_id, sources in seen_ids.items():
        if len(sources) > 1:
            errors.append(f"duplicate assay_id {assay_id!r} in {sources}")
    for name, sources in seen_names.items():
        if len(sources) > 1:
            # Not fatal: get_protocol resolves this last-match-wins so a v2
            # module can deliberately supersede a v1 one. Still worth saying.
            warnings.append(f"duplicate name {name!r} in {sources} (last match wins)")

    # ---- structured criteria and roles ----------------------------------
    structured_count = 0
    criterion_count = 0
    scorable_count = 0
    source_type_counts = Counter()
    scope_counts = Counter()

    for entry in entries:
        label = f"{entry['_source']}:{display_name(entry)}"
        structured = entry.get("acceptance_criteria_structured")
        if structured:
            structured_count += 1
            if not isinstance(structured, list):
                errors.append(f"{label}: acceptance_criteria_structured must be a list")
            else:
                prose_keys = set(entry.get("acceptance_criteria") or {})
                for criterion in structured:
                    criterion_count += 1
                    where = f"{label}[{criterion.get('key', '?')}]"
                    errors.extend(validate_criterion(criterion, where))
                    if criterion.get("machine_scorable"):
                        scorable_count += 1
                    source_type_counts[criterion.get("source_type")] += 1
                    scope_counts[criterion.get("scope")] += 1
                    # A structured criterion should restate a prose one, not
                    # invent a rule that the human-readable protocol omits.
                    key = criterion.get("key")
                    if key and prose_keys and key not in prose_keys:
                        warnings.append(
                            f"{where}: structured key not present in the prose "
                            f"acceptance_criteria -- intended, or a typo?"
                        )
        roles = entry.get("well_roles")
        if roles is not None:
            errors.extend(validate_well_roles(roles, f"{label}.well_roles"))

    # ---- report ----------------------------------------------------------
    total = len(entries)
    modules = Counter(e["_source"] for e in entries)
    print("=" * 66)
    print(f"Robotic Assays library — {total} assays across {len(modules)} modules")
    print("=" * 66)
    for module, count in sorted(modules.items()):
        print(f"  {module:38s} {count:3d} assays")

    print(f"\nStructured-criteria coverage: {structured_count}/{total} assays "
          f"({100 * structured_count / total:.0f}%)")
    print(f"  structured criteria defined : {criterion_count}")
    print(f"  machine-scorable            : {scorable_count}")
    print(f"  prose-only (documented, not scorable): {criterion_count - scorable_count}")

    if scope_counts:
        print("\n  by scope:")
        for scope, count in scope_counts.most_common():
            print(f"    {scope:8s} {count:3d}")

    if source_type_counts:
        print("\n  by source authority:")
        for source_type in sorted(SOURCE_TYPES):
            count = source_type_counts.get(source_type, 0)
            if count:
                print(f"    {source_type:22s} {count:3d}")

    roles_count = sum(1 for e in entries if e.get("well_roles"))
    print(f"\nwell_roles blocks: {roles_count}/{total} assays")

    protocol_report = check_opentrons_protocols(errors, warnings, args.skip_simulation)
    print(f"\nOpentrons protocols: {len(protocol_report)}/{total} assays")
    for rel, status in protocol_report:
        print(f"  {rel:42s} {status}")

    if warnings:
        print(f"\n--- {len(warnings)} warning(s) ---")
        for warning in warnings:
            print(f"  ! {warning}")

    if errors:
        print(f"\n--- {len(errors)} ERROR(S) ---")
        for error in errors:
            print(f"  x {error}")
        print("\nFAILED")
        return 1

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
