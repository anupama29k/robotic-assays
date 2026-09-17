# assay_criteria_schema.py
# Robotic Assays — the acceptance-criteria contract
# Builder: Anu Kozhiyalam
#
# WHY THIS FILE EXISTS
# -------------------
# Until now every acceptance criterion in this library was a prose string:
#     "standard_curve_r2": ">= 0.998"
#     "qc_sample_recovery": "85-115% of known concentration"
# Prose is right for a scientist reading a protocol and wrong for a machine
# scoring a plate. Downstream consumers (results-bridge, deck planners, the
# AI layer) had to hand-transcribe numbers out of English, which does not
# scale and cannot be audited.
#
# This module defines a STRUCTURED form that lives ALONGSIDE the prose --
# `acceptance_criteria` is never removed or rewritten, so nothing that reads
# this library today can break. New entries carry both from birth; existing
# entries gain the structured block one at a time.
#
# THREE IDEAS CARRY THE WHOLE DESIGN
# ----------------------------------
# 1. SCOPE -- a criterion is scored per well, per plate, or per run.
#    "OD must be 0.1-3.5" is a WELL question. "Curve R-squared >= 0.98" is a
#    PLATE question: it needs every standard well at once. Without this field
#    a validator cannot tell which criteria it is even able to evaluate.
#
# 2. APPLIES_TO -- which well role a criterion judges. A blank and a sample
#    are held to opposite standards; encoding the role makes that explicit
#    instead of leaving it implied by the criterion's name.
#
# 3. SOURCE_TYPE -- what kind of authority a number has. Discovered while
#    building this file: the qPCR efficiency window of 90-110% is almost
#    universally cited as a MIQE requirement, and MIQE does not say it --
#    MIQE requires that efficiency be REPORTED. The 90-110% window is vendor
#    application guidance. Likewise USP <621> defines how to CALCULATE
#    resolution and tailing but leaves the limits to each monograph. A
#    library that silently labels both "regulatory" is lying by compression.

# ---------------------------------------------------------------- vocabulary

CRITERION_TYPES = {
    # curve / fit quality (always plate-scoped)
    "curve_r2",              # coefficient of determination of the calibration fit
    "curve_efficiency",      # amplification efficiency, % (qPCR)
    "curve_slope",           # fit slope, where the slope itself is specified
    "curve_fit_model",       # linear / 4PL / quadratic requirement
    "linear_range",          # orders of magnitude or concentration span covered
    # precision / reproducibility
    "replicate_cv",          # %CV across technical replicates
    "replicate_sd",          # absolute SD across replicates (Cq, for instance)
    # controls
    "blank_max",             # upper bound on a blank/background well
    "control_response",      # a control must land in a stated window
    "recovery",              # % recovery of a known-concentration QC
    "signal_to_background",  # fold ratio, max over min
    "signal_window",         # absolute separation between high and low controls
    "z_factor",              # Zhang Z' -- assay quality for screening
    "carryover",             # signal in a blank after a high standard
    # per-sample chemistry
    "concentration_range",   # the ordinary min/max a sample must fall within
    "purity_ratio",          # A260/A280 and friends
    "yield",                 # absolute amount recovered
    "calibration_accuracy",  # % of nominal for a calibrator or standard
    # chromatography / instrument health
    "retention_time",
    "peak_shape",            # tailing / symmetry factor
    "resolution",            # separation between adjacent peaks
    "column_efficiency",     # theoretical plates
    "pressure",
    # qualitative
    "appearance",
    "contamination_check",
    "other",
}

SCOPES = {
    "well",   # scored one row at a time -- what validate_rows already does
    "plate",  # needs a group of wells together (a curve, a CV, a Z')
    "run",    # spans the whole run or several plates (system suitability, trend)
}

ROLES = {
    "all",
    "sample",
    "blank",              # reagent / buffer / media blank
    "standard",           # calibrator defining a curve
    "positive_control",
    "negative_control",   # NTC and friends -- passes by NOT responding
    "qc",                 # known-concentration check sample
    "reference_standard",
}

SOURCE_TYPES = {
    "regulatory",           # ICH, USP, Ph. Eur., ISO, ENCODE -- a normative document
    "vendor_guidance",      # kit insert, instrument spec sheet, application note
    "community_convention", # widely used, no normative source -- say so out loud
    "project_defined",      # this library's own default; defensible, not sourced
    "instrument_physics",   # bounded by what the detector can produce
}

# Keys every structured criterion carries. `min`/`max` mirror the shape a
# validator already uses (either may be None for a one-sided rule), so a
# consumer needs no translation layer.
REQUIRED_KEYS = {
    "key", "criterion_type", "scope", "applies_to",
    "min", "max", "unit", "display", "source", "source_type", "machine_scorable",
}


def validate_criterion(c, where=""):
    """Return a list of problems with one structured criterion. Empty == valid."""
    problems = []
    missing = REQUIRED_KEYS - set(c)
    if missing:
        problems.append(f"{where}: missing keys {sorted(missing)}")
    if c.get("criterion_type") not in CRITERION_TYPES:
        problems.append(f"{where}: unknown criterion_type {c.get('criterion_type')!r}")
    if c.get("scope") not in SCOPES:
        problems.append(f"{where}: unknown scope {c.get('scope')!r}")
    if c.get("applies_to") not in ROLES:
        problems.append(f"{where}: unknown applies_to {c.get('applies_to')!r}")
    if c.get("source_type") not in SOURCE_TYPES:
        problems.append(f"{where}: unknown source_type {c.get('source_type')!r}")
    lo, hi = c.get("min"), c.get("max")
    if c.get("machine_scorable"):
        if lo is None and hi is None:
            problems.append(f"{where}: machine_scorable but neither min nor max set")
        if lo is not None and hi is not None and lo > hi:
            problems.append(f"{where}: min {lo} > max {hi}")
    else:
        if lo is not None or hi is not None:
            problems.append(f"{where}: not machine_scorable yet carries min/max")
    if not c.get("display"):
        problems.append(f"{where}: empty display string (humans read this one)")
    if not c.get("source"):
        problems.append(f"{where}: empty source -- every number names its authority")
    return problems


def validate_well_roles(roles, where=""):
    """Return a list of problems with one well_roles block. Empty == valid."""
    problems = []
    if not isinstance(roles, dict):
        return [f"{where}: well_roles must be a dict of role -> rule"]
    for role, rule in roles.items():
        if role not in ROLES:
            problems.append(f"{where}: unknown role {role!r}")
        if not isinstance(rule, dict):
            problems.append(f"{where}.{role}: rule must be a dict")
            continue
        if rule.get("skip"):
            continue  # a skipped role needs no bounds
        if rule.get("min") is None and rule.get("max") is None:
            problems.append(f"{where}.{role}: no min, no max, not skipped")
        lo, hi = rule.get("min"), rule.get("max")
        if lo is not None and hi is not None and lo > hi:
            problems.append(f"{where}.{role}: min {lo} > max {hi}")
    return problems
