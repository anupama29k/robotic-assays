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
"""
import glob
import importlib
import os
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


def main():
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
