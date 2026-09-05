"""
BioInterface — SynBioBeta Demo
Three-section demonstration for automation companies.

The narrative: a domain-rich assay dict (section 1) compiles to an
executable PyLabRobot protocol (section 2) via a small, transparent
set of field -> code mappings (section 3). No LLM in the loop; the
dict itself is the specification.
"""

import sys
import textwrap

# Force UTF-8 stdout so unicode box-drawing chars in the generated
# protocol render on Windows cp1252 terminals.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

from field_01_biopharma_v2 import BIOPHARMA_ASSAYS
from rail_protocol_generator import generate_protocol, classify_step


BIO_005 = next(a for a in BIOPHARMA_ASSAYS if a["assay_id"] == "BIO_005")


def _rule(char: str = "=", width: int = 70) -> str:
    return char * width


# ───────────────────────────────────────────────────────────────────
# SECTION 1 — THE ASSAY DICT (domain knowledge layer)
# ───────────────────────────────────────────────────────────────────
print(_rule())
print("SECTION 1 — ASSAY DICT (domain knowledge layer)")
print(_rule())
print(f"Assay ID   : {BIO_005['assay_id']}")
print(f"Name       : {BIO_005['name']}")
print(f"Field      : {BIO_005['field']}")
print(f"Workbench  : {BIO_005['workbench_id']}")
print(f"Purpose    : {BIO_005['purpose']}")
print(f"Regulatory : {', '.join(BIO_005['regulatory'])}")
print(f"Throughput : {BIO_005['throughput_samples_per_run']} samples/run")
print(f"Robot time : {BIO_005['robot_active_minutes']} minutes active, "
      f"{BIO_005['total_assay_duration_hours']} hours total")
print(f"Difficulty : {BIO_005['automation_difficulty']}")
print()

print("robot_steps (first 5 of {}):".format(len(BIO_005["robot_steps"])))
for i, step in enumerate(BIO_005["robot_steps"][:5], 1):
    wrapped = textwrap.fill(step, width=68, subsequent_indent="        ")
    print(f"  {i:2}. {wrapped}")
print("  ... ({} more steps)".format(len(BIO_005["robot_steps"]) - 5))
print()

print(f"automate_96_steps  : {BIO_005['automate_96_steps']}")
print(f"automate_96_head   : {BIO_005['automate_96_head']}")
print(f"automate_96_head_change: {BIO_005['automate_96_head_change']}")
print()

print("robot_deck_layout:")
for pos, desc in BIO_005["robot_deck_layout"].items():
    print(f"  [{pos:3}] {desc}")
print()

print("acceptance_criteria:")
for k, v in BIO_005["acceptance_criteria"].items():
    print(f"  {k:35} {v}")
print()

print("instrument_assignment:")
for bucket, positions in BIO_005["instrument_assignment"].items():
    print(f"  {bucket:12} {positions}")
print()


# ───────────────────────────────────────────────────────────────────
# SECTION 2 — THE GENERATED PROTOCOL
# ───────────────────────────────────────────────────────────────────
print(_rule())
print("SECTION 2 — GENERATED PYLABROBOT PROTOCOL")
print(_rule())

source = generate_protocol(BIO_005)
lines = source.splitlines()
print(f"Generated protocol: {len(lines)} lines of Python.")
print(f"(Showing first 50 lines — full module written on demand to "
      f"bio_005_protocol.py)\n")

for i, line in enumerate(lines[:50], 1):
    print(f"  {i:3}  {line}")
print(f"  ... ({len(lines) - 50} more lines)")
print()


# ───────────────────────────────────────────────────────────────────
# SECTION 3 — THE MAPPING TABLE
# ───────────────────────────────────────────────────────────────────
print(_rule())
print("SECTION 3 — ASSAY FIELD → PROTOCOL LINE MAPPING")
print(_rule())
print("Every section of the generated Python traces back to a specific")
print("field in the assay dict. No code is invented; the dict IS the spec.")
print()

mappings = [
    ('assay["assay_id"]',
     'function name — async def run_{assay_id_lower}(...)'),
    ('assay["name"], assay["purpose"]',
     'docstring of the protocol function'),
    ('assay["workbench_id"], assay["regulatory"]',
     'docstring metadata lines'),
    ('assay["robot_deck_layout"]',
     'DECK_LAYOUT dict — one entry per deck position, slot number '
     'resolved via DECK_SLOT_MAP'),
    ('assay["acceptance_criteria"]',
     'ACCEPTANCE_CRITERIA dict — printed at protocol end for verification'),
    ('assay["robot_steps"][i]',
     'comment line above each generated step block'),
    ('assay["automate_96_steps"]',
     'gates LIQUID_HANDLER classification — only tagged steps emit '
     'lh.dispense() / lh.aspirate() calls'),
    ('assay["automate_96_head"]',
     'selects flow_rate in dispense calls '
     '(1-20uL → 50, 5-200uL → 200, 100-1000uL → 500 µL/s)'),
    ('classify_step() on each step text',
     'chooses code template: TRANSPORT / LIQUID_HANDLER / WAIT / '
     'ANALYST_PAUSE / INSTRUMENT_TRIGGER / OTHER'),
    ('"[ANALYST STEP" marker in step text',
     'emits await robot.analyst_pause(reason=..., timeout_minutes=15)'),
    ('regex extraction of "X minutes/hours/overnight"',
     'populates the seconds argument of await asyncio.sleep(N)'),
    ('regex extraction of "N µL" or "N mL" in step text',
     'populates vols=[N] * 96 in lh.dispense()'),
    ('regex extraction of "N times" / "N cycles" + "wash"',
     'wraps dispense+aspirate in for cycle in range(N): loop'),
]

col_width = 44
for src, dst in mappings:
    src_wrapped = textwrap.wrap(src, width=col_width) or [""]
    dst_wrapped = textwrap.wrap(dst, width=68 - col_width) or [""]
    rows = max(len(src_wrapped), len(dst_wrapped))
    for r in range(rows):
        left = src_wrapped[r] if r < len(src_wrapped) else ""
        right = dst_wrapped[r] if r < len(dst_wrapped) else ""
        connector = " →  " if r == 0 else "    "
        print(f"  {left:<{col_width}}{connector}{right}")
    print()

# Step-level classification table
print(f"Step-level classification for {BIO_005['assay_id']} "
      f"({len(BIO_005['robot_steps'])} steps):")
print(f"  {'#':>3}  {'CLASS':<20}  step excerpt")
print(f"  {'-'*3}  {'-'*20}  {'-'*40}")
automate = BIO_005["automate_96_steps"]
for i, step in enumerate(BIO_005["robot_steps"], 1):
    action, _meta = classify_step(step, i, automate)
    excerpt = textwrap.shorten(step, width=60, placeholder="…")
    print(f"  {i:>3}  {action:<20}  {excerpt}")
print()

print(_rule())
print("Demo complete. The generator is deterministic, offline, and")
print("auditable — every line of the protocol ties to a dict field.")
print(_rule())
