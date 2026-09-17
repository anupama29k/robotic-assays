# Acceptance criteria: the structured schema

Every assay in this library states its acceptance criteria twice, on purpose.

```python
"acceptance_criteria": {                    # prose — for a scientist
    "standard_curve_r2": ">= 0.998",
},
"acceptance_criteria_structured": [         # data — for a validator
    {"key": "standard_curve_r2", "criterion_type": "curve_r2", "scope": "plate",
     "applies_to": "standard", "min": 0.998, "max": None, "unit": None,
     "display": ">= 0.998",
     "source": "Method default (project-defined); ICH Q2(R2) requires linearity be demonstrated without fixing a threshold",
     "source_type": "project_defined", "machine_scorable": True},
],
```

The prose form is authoritative for humans and is never rewritten or removed, so
every consumer that reads this library today keeps working. The structured form
restates the same rule as data. `validate_library.py` enforces the contract and
warns when a structured key has no prose counterpart, which is how typos surface.

## Why this exists

Until version 2.1 the criteria were prose only. That is the right format for
someone reading a protocol and the wrong one for a machine scoring a plate: a
downstream service had to hand-transcribe numbers out of English, which does not
scale, cannot be audited, and quietly loses the distinction between a regulatory
limit and somebody's house default.

## The three fields that carry the design

**`scope`** — is this criterion scored per `well`, per `plate`, or per `run`?
"OD must be 0.1–3.5" is a well question. "Curve R² ≥ 0.98" is a plate question:
it needs every standard well at once. "System suitability RSD ≤ 2.0%" is a run
question. Without this field a validator cannot tell which criteria it is even
capable of evaluating, and will silently skip or wrongly apply the rest.

**`applies_to`** — which well role the criterion judges: `sample`, `blank`,
`standard`, `positive_control`, `negative_control`, `qc`, `reference_standard`,
or `all`. Roles routinely invert a verdict. A qPCR no-template control passes by
*not* amplifying: the Cq of 38 that condemns a sample vindicates an NTC. Leaving
that implied in a criterion's name is how validators end up failing healthy
plates.

**`source_type`** — what kind of authority a number carries:

| value | meaning |
|---|---|
| `regulatory` | a normative document (ICH, USP, Ph. Eur., ISO, ENCODE) |
| `vendor_guidance` | kit insert, instrument specification, application note |
| `community_convention` | widely used, no normative source — say so |
| `project_defined` | this library's own default; defensible, not sourced |
| `instrument_physics` | bounded by what the detector can actually produce |

This field exists because of two findings from building `field_06`:

- The qPCR efficiency window of **90–110%** is cited almost universally as a
  MIQE requirement. MIQE does not state it. MIQE requires that efficiency be
  *reported*. The 90–110% window is Bio-Rad application guidance — real and
  useful, and not regulatory.
- **USP \<621\>** defines *how* to calculate resolution, tailing and plate count
  and requires that system suitability be established. It sets no universal
  numeric limits; those belong to each monograph or validated method. The
  familiar R ≥ 2.0 / T ≤ 2.0 / RSD ≤ 2.0% defaults are house defaults.

A library that labels both of those `regulatory` is lying by compression. The
current distribution across the library is printed by `validate_library.py`.

## `min` / `max`, not an operator grammar

Bounds are expressed as `min` and `max`, either of which may be `None` for a
one-sided rule. This deliberately mirrors the shape a validator already uses, so
a consumer needs no translation layer — it reads `min`/`max` and applies them.
A criterion that cannot be reduced to bounds (a melt-curve shape, an appearance
check) sets `machine_scorable: False`, leaves both bounds `None`, and keeps its
`display` string. It stays documented without pretending to be scorable.

## `well_roles`

A per-assay map from role to the rule that role is held to:

```python
"well_roles": {
    "sample":           {"min": 10.0, "max": 35.0, "unit": "Cq"},
    "negative_control": {"min": 40.0, "max": None, "unit": "Cq",
                         "note": "INVERTED — passes by not amplifying"},
    "standard":         {"skip": True,
                         "note": "Calibrators define the curve; scored by the plate criteria"},
}
```

`skip: True` marks a role that is not judged against a range at all. Calibrators
are the clearest case: they do not fall inside the acceptance range, they *are*
the range, and they are scored collectively by the plate-scoped curve criteria.

A consumer holding a plate map of `{well: role}` can apply these rules directly.

## Adding or updating an assay

1. Write the prose `acceptance_criteria` first — it is what a scientist reads.
2. Restate each entry in `acceptance_criteria_structured`, one structured
   criterion per prose key, in the same order.
3. For every number, name its `source` and choose the honest `source_type`.
   If there is no external source, `project_defined` is the correct answer and
   a better one than a citation that does not say what it is claimed to say.
4. Add `well_roles` if the assay has blanks, standards or controls.
5. Run `python3 validate_library.py`. It exits non-zero on any error.

New modules are discovered by glob (`field_*.py`), not from a hardcoded list —
a hardcoded list broke a downstream consumer the day this repository deleted its
v1 biopharma file. Drop a new field file in and it is picked up.
