"""
Run Data Ingestion module for BioInterface.

Provides:
- File format detection
- Pluggable parser registry
- Storage of raw + parsed results to Supabase
- Acceptance criteria evaluation
"""

import os
import base64
from datetime import datetime
from supabase import create_client


# === Format detection ===

def detect_file_format(
    file_name: str,
    file_content: str = None
) -> str:
    """Identify the file format from name + content peek."""
    name_lower = file_name.lower()

    if name_lower.endswith('.csv'):
        # Sniff content for the most-specific format first.
        # TapeStation > Qubit > generic CSV.
        if file_content:
            content_peek = file_content.lower()[:2000]

            tapestation_signals = [
                'tapestation',
                'average size',
                'average_size_bp',
                '% in region',
                'percent in region',
                'region [bp]',
                'region [%]',
            ]
            # Smear-UNIQUE signals only. Compact Region Tables also
            # carry "From [bp]" / "To [bp]" columns to describe the
            # single integration region, so those tokens alone are
            # not sufficient to classify as smear. Smear is identified
            # by "% Total" (total-of-library fraction per region) or
            # an explicit "smear region" / "smear_region" header.
            smear_signals = [
                '% total',
                'percent total',
                'total [%]',
                'smear region',
                'smear_region',
            ]
            if any(sig in content_peek for sig in smear_signals):
                return 'tapestation_csv_smear'
            if any(sig in content_peek for sig in tapestation_signals):
                return 'tapestation_csv_compact'

            qubit_signals = [
                'qubit',
                'concentration',
                'sample conc',
                'original sample conc',
                'ng/ul',
                'ng/µl',
                'dsdna hs',
                'dsdna br',
                'ssdna',
                'rna hs',
                'rna br',
            ]
            if any(sig in content_peek for sig in qubit_signals):
                return 'qubit_csv'
        return 'generic_csv'

    if name_lower.endswith(('.xls', '.xlsx')):
        # Filename hints first (cheap)
        if 'tapestation' in name_lower or 'tape station' in name_lower:
            return 'tapestation_excel_compact'
        if 'tecan' in name_lower or 'spark' in name_lower:
            return 'tecan_excel'
        if 'bmg' in name_lower or 'clariostar' in name_lower:
            return 'bmg_excel'
        if 'pherastar' in name_lower or 'omega' in name_lower:
            return 'bmg_excel'
        if 'magellan' in name_lower:
            return 'tecan_excel'

        # Content peek — labs rename files, so the filename alone is
        # unreliable. Look for vendor signatures in the first 20 rows.
        try:
            from openpyxl import load_workbook
            from io import BytesIO
            raw_bytes = _coerce_to_bytes(file_content)
            if raw_bytes is None:
                return 'plate_reader_excel'
            wb = load_workbook(
                BytesIO(raw_bytes),
                read_only=True,
                data_only=True,
            )
            sheet = wb.active
            peek_text_parts = []
            for row_idx, row in enumerate(
                sheet.iter_rows(max_row=20, values_only=True)
            ):
                for cell in row:
                    if cell is not None:
                        peek_text_parts.append(str(cell).lower())
            wb.close()
            peek_text = " ".join(peek_text_parts)
            if (
                'tapestation' in peek_text
                or 'average size' in peek_text
                or '% in region' in peek_text
            ):
                return 'tapestation_excel_compact'
            if 'tecan' in peek_text or 'magellan' in peek_text:
                return 'tecan_excel'
            if (
                'bmg' in peek_text
                or 'clariostar' in peek_text
                or 'pherastar' in peek_text
                or 'mars data' in peek_text
            ):
                return 'bmg_excel'
        except Exception:
            # Best-effort peek; fall through to generic on any failure.
            pass

        return 'plate_reader_excel'

    if name_lower.endswith('.ome'):
        return 'tapestation_ome'

    if name_lower.endswith('.ckb'):
        return 'hamilton_ckb'

    if name_lower.endswith('.json'):
        if 'illumina' in name_lower or 'sequencing' in name_lower:
            return 'illumina_metrics'
        return 'json_results'

    if name_lower.endswith('.txt'):
        return 'text_log'

    return 'unknown'


# === Parser registry ===

_parser_registry = {}


def register_parser(file_format: str):
    """Decorator to register a parser function."""
    def wrapper(fn):
        _parser_registry[file_format] = fn
        return fn
    return wrapper


def parse_uploaded_file(
    file_name: str,
    file_content: str,
    expected_format: str = None
) -> dict:
    """Route to the appropriate parser. Returns dict with:
    - success: bool
    - results: list of run_result records ready for insert
    - error: str if failed
    """
    fmt = expected_format or detect_file_format(
        file_name, file_content
    )

    parser = _parser_registry.get(fmt)
    if parser is None:
        return {
            "success": False,
            "results": [],
            "error": (
                f"No parser registered for format: {fmt}. "
                f"Available: {list(_parser_registry.keys())}"
            ),
            "format_detected": fmt,
        }

    try:
        results = parser(file_content)
        return {
            "success": True,
            "results": results,
            "error": None,
            "format_detected": fmt,
        }
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "error": str(e),
            "format_detected": fmt,
        }


# === Built-in parsers ===

# Canonical concentration unit for storage. All Qubit values are converted
# to ng/µL so downstream acceptance-criteria evaluation can compare apples
# to apples. Pull this out as a constant so future parsers reuse it.
CONCENTRATION_CANONICAL_UNIT = "ng/uL"


def _normalize_micro(s: str) -> str:
    """Replace µ / μ / mu glyphs with ASCII 'u' for unit matching."""
    return s.replace("µ", "u").replace("μ", "u")


def _convert_to_ng_per_ul(value: float, raw_units: str) -> float:
    """Convert (value, units) → ng/µL. Returns the value unchanged
    when units are unrecognised so the caller can still display
    something sensible."""
    u = _normalize_micro(raw_units.lower().strip())
    # Strip whitespace and common separators
    u = u.replace(" ", "").replace(".", "")
    if u in ("ng/ul", "ng/ul.", "ngul"):
        return value
    if u in ("ng/ml", "ngml"):
        return value / 1000.0
    if u in ("ug/ml", "ugml"):
        # 1 µg/mL = 1 ng/µL
        return value
    if u in ("ug/ul", "ugul"):
        # 1 µg/µL = 1000 ng/µL
        return value * 1000.0
    if u in ("pg/ul", "pgul"):
        return value / 1000.0
    if u in ("mg/ml", "mgml"):
        return value
    return value


@register_parser("qubit_csv")
def parse_qubit_csv(content: str) -> list:
    """Parse Qubit fluorometer CSV exports into run_result records.

    Handles common Qubit 2.0 / 3.0 / 4.0 export shapes by locating the
    header row and mapping any of the variant column names:

        sample id    : "Sample ID" | "Sample Name" | "Test Name"
        concentration: "Original Sample Conc." | "Conc." | "Concentration"
        units        : "Units"

    Returns a list of dicts with sample_id, measurement_type='concentration',
    value (canonical ng/µL), units, raw_value, raw_units. Rows whose
    concentration is non-numeric (e.g. "Out of range") are skipped, not
    raised — Qubit happily emits these for failed wells.
    """
    import csv
    import io

    if not content or not content.strip():
        raise ValueError("Empty CSV")

    # Strip UTF-8 BOM if present (Qubit Windows exports often carry one)
    if content.startswith("﻿"):
        content = content[1:]

    # Sniff delimiter on the first ~2 KB
    sample = content[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel  # fall back to comma

    reader = csv.reader(io.StringIO(content), dialect)
    rows = [r for r in reader if r and any(c.strip() for c in r)]
    if not rows:
        raise ValueError("CSV contains no data rows")

    # Header row detection — scan first 10 rows for sample/conc tokens.
    # A real header row is multi-column; single-cell rows (the title
    # preamble Qubit exports like "Qubit dsDNA HS Assay - Sample
    # Concentration Report") must NOT match even though their text
    # contains the tokens.
    header_idx = None
    for i, row in enumerate(rows[:10]):
        if len(row) < 2:
            continue
        joined = " ".join(c.strip().lower() for c in row)
        if ("sample" in joined or "test" in joined) and "conc" in joined:
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(
            "Could not locate Qubit header row "
            "(expected a multi-column header with 'Sample' and 'Conc')"
        )

    headers = [c.strip() for c in rows[header_idx]]
    headers_lower = [h.lower() for h in headers]

    def _find_col(candidates):
        # Exact match wins over substring; iterate candidates in priority
        for cand in candidates:
            for i, h in enumerate(headers_lower):
                if h == cand:
                    return i
        for cand in candidates:
            for i, h in enumerate(headers_lower):
                if cand in h:
                    return i
        return None

    sample_col = _find_col(
        ["sample id", "sample name", "test name", "sample"]
    )
    # Prefer the back-calculated "Original Sample Conc." over the raw
    # "Conc." column, since that's the value scientists actually compare
    # against acceptance criteria.
    conc_col = _find_col(
        [
            "original sample conc.",
            "original sample conc",
            "concentration",
            "conc.",
            "conc",
        ]
    )
    units_col = _find_col(["units", "unit"])

    if sample_col is None or conc_col is None:
        raise ValueError(
            f"Required Qubit columns not found. "
            f"Saw headers: {headers}"
        )

    results = []
    skipped = 0
    for row in rows[header_idx + 1:]:
        if not row or all(not c.strip() for c in row):
            continue
        if len(row) <= max(sample_col, conc_col):
            continue

        sample_id = row[sample_col].strip()
        raw_val = row[conc_col].strip()
        raw_units = ""
        if units_col is not None and len(row) > units_col:
            raw_units = row[units_col].strip()
        if not raw_units:
            raw_units = CONCENTRATION_CANONICAL_UNIT

        if not sample_id or not raw_val:
            skipped += 1
            continue

        # Strip thousands separators, surrounding whitespace, stray '*'
        cleaned = raw_val.replace(",", "").replace("*", "").strip()
        try:
            value_num = float(cleaned)
        except ValueError:
            # Qubit emits "Out of range" / "Too low" — log silently and
            # move on rather than failing the whole upload.
            skipped += 1
            continue

        canonical = _convert_to_ng_per_ul(value_num, raw_units)

        # Shape matches the run_results table from Chunk 1:
        #   result_type / instrument / sample_id / well_position
        #   / measurements (jsonb) / pass_fail / acceptance_criteria_met
        #   / notes
        # pass_fail and acceptance_criteria_met are filled in later by
        # evaluate_and_enrich_results once the assay's criteria are
        # known.
        results.append({
            "result_type": "library_quantification",
            "instrument": "qubit_fluorometer",
            "sample_id": sample_id,
            "well_position": None,
            "measurements": {
                "concentration_ng_per_uL": canonical,
                "units": CONCENTRATION_CANONICAL_UNIT,
                "raw_value": value_num,
                "raw_units": raw_units,
            },
            "pass_fail": None,
            "acceptance_criteria_met": None,
            "notes": None,
        })

    if not results:
        raise ValueError(
            f"No usable rows in Qubit CSV (skipped {skipped} rows)"
        )

    return results


# === Plate-reader Excel parsers (Tecan / BMG / generic) ===

# Standard 96-well plate row labels. 384-well plates would need A-P;
# add a second table if/when we support those.
_PLATE_ROW_LABELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


def _coerce_to_bytes(file_content) -> bytes:
    """Accept either raw bytes, base64-encoded text, or latin-1-decoded
    text (the shape the Streamlit page handler currently passes for
    binary uploads). Returns the underlying bytes, or None if the input
    is empty/unusable.

    The order matters: bytes pass through, then we try base64 (works
    for any DB-persisted content), then latin-1 (always reversible
    because latin-1 is a 1:1 0x00-0xFF mapping).
    """
    if file_content is None:
        return None
    if isinstance(file_content, (bytes, bytearray)):
        return bytes(file_content)
    if isinstance(file_content, str):
        try:
            return base64.b64decode(file_content, validate=True)
        except Exception:
            return file_content.encode('latin-1', errors='replace')
    return None


def _scan_plate_metadata(all_rows, default_instrument: str) -> dict:
    """Pull instrument / wavelength / measurement type out of the first
    25 rows of an Excel export. Shared by Tecan and BMG parsers because
    both vendors emit metadata in roughly the same shape — labelled
    free text in the first dozen rows above the plate grid."""
    import re as _re
    metadata = {
        "instrument": default_instrument,
        "wavelength_nm": None,
        "emission_nm": None,
        "measurement_type": "absorbance",
        "protocol_name": None,
    }
    for row in all_rows[:25]:
        if row is None:
            continue
        row_text = " ".join(
            str(c).lower() if c is not None else "" for c in row
        )
        if "pherastar" in row_text:
            metadata["instrument"] = "bmg_pherastar"
        if (
            "wavelength" in row_text
            or "ex/em" in row_text
            or "excitation" in row_text
            or "emission" in row_text
        ):
            wl_matches = _re.findall(r"(\d{3,4})\s*nm", row_text)
            if wl_matches:
                metadata["wavelength_nm"] = int(wl_matches[0])
                if len(wl_matches) > 1:
                    metadata["emission_nm"] = int(wl_matches[1])
        if (
            "fluorescence" in row_text
            or "ex/em" in row_text
            or ("excitation" in row_text and "emission" in row_text)
        ):
            metadata["measurement_type"] = "fluorescence"
        elif "luminescence" in row_text:
            metadata["measurement_type"] = "luminescence"
        if "protocol" in row_text:
            for c in row:
                if c is None:
                    continue
                s = str(c).strip()
                if 5 < len(s) < 80 and s.lower() not in (
                    "protocol", "protocol name:", "protocol name"
                ):
                    metadata["protocol_name"] = s
                    break
    return metadata


def _locate_plate_start(all_rows) -> int:
    """Find the index of the row that starts a standard 8x12 plate
    block — first cell is the literal letter 'A', second cell is
    numeric. Returns None if not found."""
    for i, row in enumerate(all_rows):
        if row is None or len(row) < 2:
            continue
        first_cell = row[0]
        if first_cell is None:
            continue
        if str(first_cell).strip().upper() == "A":
            try:
                float(row[1])
                return i
            except (TypeError, ValueError):
                continue
    return None


def _load_workbook_rows(file_content):
    """Decode the upload, open the workbook, return (rows, sheet_name).
    Raises ValueError with a useful message on bad input."""
    from openpyxl import load_workbook
    from io import BytesIO
    raw_bytes = _coerce_to_bytes(file_content)
    if not raw_bytes:
        raise ValueError("Empty Excel upload")
    wb = load_workbook(BytesIO(raw_bytes), read_only=True, data_only=True)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    sheet_name = sheet.title
    wb.close()
    return rows, sheet_name


def _emit_plate_results(
    all_rows,
    plate_start_idx: int,
    metadata: dict,
    note: str,
) -> list:
    """Walk an 8x12 plate block starting at `plate_start_idx` and emit
    one record per non-empty well. Shared between Tecan / BMG / generic
    parsers since the plate-grid shape is identical across vendors."""
    results = []
    for r_idx, row_label in enumerate(_PLATE_ROW_LABELS):
        if plate_start_idx + r_idx >= len(all_rows):
            break
        row = all_rows[plate_start_idx + r_idx]
        if row is None:
            continue
        for c_idx in range(1, 13):
            if c_idx >= len(row):
                break
            cell = row[c_idx]
            if cell is None or cell == '':
                continue
            try:
                value = float(cell)
            except (TypeError, ValueError):
                continue

            well = f"{row_label}{c_idx}"
            # Use the semantic measurement_type as the key (e.g.
            # "absorbance") so the evaluator can match criteria like
            # "absorbance_range" via substring hints.
            measurement_key = metadata["measurement_type"]
            measurement_payload = {
                measurement_key: value,
                "wavelength_nm": metadata.get("wavelength_nm"),
                "measurement_type": metadata["measurement_type"],
            }
            if metadata.get("emission_nm") is not None:
                measurement_payload["emission_nm"] = metadata["emission_nm"]
            if metadata.get("protocol_name"):
                measurement_payload["protocol_name"] = metadata["protocol_name"]

            results.append({
                "result_type": (
                    "plate_read_" + metadata["measurement_type"]
                ),
                "instrument": metadata["instrument"],
                "sample_id": well,
                "well_position": well,
                "measurements": measurement_payload,
                "pass_fail": None,
                "acceptance_criteria_met": None,
                "notes": note,
            })
    return results


@register_parser("tecan_excel")
def parse_tecan_excel(file_content) -> list:
    """Parse Tecan Spark / Infinite plate reader Excel export
    (Magellan software). Tecan exports a metadata preamble in the
    first ~15 rows, then either an 8x12 plate grid or a per-well list.
    Tries the grid first; falls back to per-well rows."""
    all_rows, _ = _load_workbook_rows(file_content)
    metadata = _scan_plate_metadata(all_rows, default_instrument="tecan_spark")

    plate_start = _locate_plate_start(all_rows)
    if plate_start is not None:
        results = _emit_plate_results(
            all_rows,
            plate_start,
            metadata,
            note=f"Tecan {metadata['measurement_type']} read",
        )
        if results:
            return results

    # Fallback: well-by-well layout (one row per well)
    return _parse_tecan_wellbyrow(all_rows, metadata)


def _parse_tecan_wellbyrow(all_rows, metadata: dict) -> list:
    """Fallback for Tecan exports that list one well per row instead
    of as an 8x12 grid."""
    header_idx = None
    for i, row in enumerate(all_rows[:30]):
        if row is None:
            continue
        row_text = " ".join(
            str(c).lower() if c is not None else "" for c in row
        )
        if "well" in row_text and ("value" in row_text or "data" in row_text):
            header_idx = i
            break
    if header_idx is None:
        return []

    header = [
        str(c).lower() if c is not None else ""
        for c in all_rows[header_idx]
    ]
    well_col = None
    value_col = None
    for ci, h in enumerate(header):
        if "well" in h and well_col is None:
            well_col = ci
        if ("value" in h or "data" in h or "od" in h) and value_col is None:
            value_col = ci
    if well_col is None or value_col is None:
        return []

    results = []
    for row in all_rows[header_idx + 1:]:
        if row is None or len(row) <= max(well_col, value_col):
            continue
        well_id = row[well_col]
        value = row[value_col]
        if well_id is None or value is None:
            continue
        try:
            v = float(value)
        except (TypeError, ValueError):
            continue
        measurement_key = metadata["measurement_type"]
        results.append({
            "result_type": "plate_read_" + metadata["measurement_type"],
            "instrument": metadata["instrument"],
            "sample_id": str(well_id),
            "well_position": str(well_id),
            "measurements": {
                measurement_key: v,
                "wavelength_nm": metadata.get("wavelength_nm"),
                "measurement_type": metadata["measurement_type"],
            },
            "pass_fail": None,
            "acceptance_criteria_met": None,
            "notes": f"Tecan {metadata['measurement_type']} read",
        })
    return results


@register_parser("bmg_excel")
def parse_bmg_excel(file_content) -> list:
    """Parse BMG ClariOstar / PHERAstar Excel export (MARS Data
    Analysis software). Same preamble + 8x12 plate grid shape as
    Tecan; the metadata scanner promotes the instrument label to
    bmg_pherastar when it sees that string."""
    all_rows, _ = _load_workbook_rows(file_content)
    metadata = _scan_plate_metadata(all_rows, default_instrument="bmg_clariostar")

    plate_start = _locate_plate_start(all_rows)
    if plate_start is None:
        return []

    return _emit_plate_results(
        all_rows,
        plate_start,
        metadata,
        note=f"BMG {metadata['measurement_type']} read",
    )


@register_parser("plate_reader_excel")
def parse_generic_plate_excel(file_content) -> list:
    """Generic fallback for unbranded plate-reader Excel files. We
    don't know the wavelength or fluorophore, so the record carries
    just the raw value tagged as absorbance."""
    all_rows, _ = _load_workbook_rows(file_content)
    plate_start = _locate_plate_start(all_rows)
    if plate_start is None:
        return []
    metadata = {
        "instrument": "unknown_plate_reader",
        "wavelength_nm": None,
        "measurement_type": "absorbance",
    }
    return _emit_plate_results(
        all_rows,
        plate_start,
        metadata,
        note="Generic plate reader Excel",
    )


# === Agilent TapeStation parsers ===

# Token-based column finder used across all TapeStation parsers. Given
# a header row (lowercased) and a list of candidate substrings,
# returns the first column index that contains any of them.
def _find_column(header_lower: list, *candidates: str):
    for cand in candidates:
        for i, h in enumerate(header_lower):
            if cand in h:
                return i
    return None


def _maybe_float(cell) -> float:
    """TapeStation puts 'N/A' / blanks in cells when a peak couldn't
    be called. Return float or None — caller decides what to do."""
    if cell is None:
        return None
    s = str(cell).strip()
    if not s or s.upper() in ("N/A", "NA", "NAN", "-"):
        return None
    s = s.replace(",", "")
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _read_csv_rows(content: str):
    """Sniff delimiter and return list-of-list rows (preserving
    original strings)."""
    import csv
    import io
    if content.startswith("﻿"):
        content = content[1:]
    sample = content[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    reader = csv.reader(io.StringIO(content), dialect)
    return [r for r in reader if r and any(c.strip() for c in r)]


def _find_header_idx(rows, *required_tokens):
    """Scan first 10 rows for a header containing every required
    token (case-insensitive substring). Returns row index or None."""
    for i, row in enumerate(rows[:10]):
        if len(row) < 2:
            continue
        joined = " ".join(c.strip().lower() for c in row)
        if all(t.lower() in joined for t in required_tokens):
            return i
    return None


@register_parser("tapestation_csv_compact")
def parse_tapestation_csv_compact(content: str) -> list:
    """Agilent TapeStation compact summary CSV: one row per sample
    with concentration, average size, and percent-in-region columns.

    Skips rows where the concentration or size cell is N/A (TapeStation
    emits that when no main peak could be called)."""
    rows = _read_csv_rows(content)
    header_idx = _find_header_idx(rows, "size")
    if header_idx is None:
        # Fall back to looser detection — at least a sample column
        header_idx = _find_header_idx(rows, "sample")
    if header_idx is None:
        raise ValueError("Could not locate TapeStation header row")

    header_lower = [c.strip().lower() for c in rows[header_idx]]
    sample_col = _find_column(
        header_lower, "sample description", "sample", "well"
    )
    conc_col = _find_column(
        header_lower, "conc.", "concentration", "conc "
    )
    size_col = _find_column(
        header_lower, "average size", "size [bp]", "avg size"
    )
    region_col = _find_column(
        header_lower, "% in region", "percent in region", "region [%]"
    )
    # Compact Region Tables also expose the from/to bounds of the
    # single integration region. Capture them as flat scalars so the
    # downstream UI / queries can show the region the summary was
    # computed over, without dragging in the smear array shape.
    from_col = _find_column(
        header_lower, "from [bp]", "from_bp"
    )
    to_col = _find_column(
        header_lower, "to [bp]", "to_bp"
    )

    if sample_col is None or size_col is None:
        raise ValueError(
            f"Required TapeStation columns not found. "
            f"Saw headers: {[c for c in rows[header_idx]]}"
        )

    results = []
    skipped = 0
    for row in rows[header_idx + 1:]:
        if not row or all(not c.strip() for c in row):
            continue
        if len(row) <= max(sample_col, size_col):
            continue
        sample_id = row[sample_col].strip() if row[sample_col] else ""
        if not sample_id:
            skipped += 1
            continue
        size_val = _maybe_float(row[size_col])
        conc_val = (
            _maybe_float(row[conc_col])
            if conc_col is not None and len(row) > conc_col
            else None
        )
        region_val = (
            _maybe_float(row[region_col])
            if region_col is not None and len(row) > region_col
            else None
        )
        from_val = (
            _maybe_float(row[from_col])
            if from_col is not None and len(row) > from_col
            else None
        )
        to_val = (
            _maybe_float(row[to_col])
            if to_col is not None and len(row) > to_col
            else None
        )
        # Skip rows where the primary measurements are all missing
        # (TapeStation's "N/A" rows for failed samples)
        if size_val is None and conc_val is None:
            skipped += 1
            continue

        measurements = {}
        if conc_val is not None:
            measurements["concentration_ng_per_uL"] = conc_val
            measurements["units"] = "ng/uL"
        if size_val is not None:
            measurements["average_size_bp"] = size_val
        if region_val is not None:
            measurements["percent_in_region"] = region_val
        if from_val is not None:
            measurements["region_from_bp"] = from_val
        if to_val is not None:
            measurements["region_to_bp"] = to_val

        results.append({
            "result_type": "fragment_size_analysis",
            "instrument": "agilent_tapestation",
            "sample_id": sample_id,
            "well_position": None,
            "measurements": measurements,
            "pass_fail": None,
            "acceptance_criteria_met": None,
            "notes": "TapeStation compact summary",
        })

    if not results:
        raise ValueError(
            f"No usable TapeStation rows (skipped {skipped})"
        )
    return results


@register_parser("tapestation_csv_smear")
def parse_tapestation_csv_smear(content: str) -> list:
    """Agilent TapeStation smear-analysis CSV: multiple rows per
    sample, one per smear region (from_bp/to_bp/% total). Aggregates
    by sample, emits one record per sample with measurements.smear_regions
    as a list of region dicts."""
    rows = _read_csv_rows(content)
    header_idx = _find_header_idx(rows, "from")
    if header_idx is None:
        raise ValueError(
            "Could not locate TapeStation smear header row "
            "(expected 'From [bp]' column)"
        )

    header_lower = [c.strip().lower() for c in rows[header_idx]]
    sample_col = _find_column(header_lower, "sample", "well")
    from_col = _find_column(header_lower, "from")
    to_col = _find_column(header_lower, "to ", "to[", "to_")
    if to_col is None:
        # Fall back to whatever 'to' column exists
        to_col = _find_column(header_lower, "to")
    pct_col = _find_column(header_lower, "% total", "percent", "pct")
    size_col = _find_column(header_lower, "average size", "size [bp]")
    conc_col = _find_column(header_lower, "conc.", "concentration")

    if sample_col is None or from_col is None or to_col is None:
        raise ValueError(
            f"Required TapeStation smear columns not found. "
            f"Saw headers: {[c for c in rows[header_idx]]}"
        )

    # Group regions by sample, preserving input order
    samples_in_order = []
    grouped = {}
    for row in rows[header_idx + 1:]:
        if not row or all(not c.strip() for c in row):
            continue
        if len(row) <= max(sample_col, from_col, to_col):
            continue
        sid = row[sample_col].strip() if row[sample_col] else ""
        if not sid:
            continue
        from_bp = _maybe_float(row[from_col])
        to_bp = _maybe_float(row[to_col])
        if from_bp is None or to_bp is None:
            continue
        region = {"from_bp": from_bp, "to_bp": to_bp}
        if pct_col is not None and len(row) > pct_col:
            pct = _maybe_float(row[pct_col])
            if pct is not None:
                region["pct_total"] = pct
        if size_col is not None and len(row) > size_col:
            sz = _maybe_float(row[size_col])
            if sz is not None:
                region["average_size_bp"] = sz
        if conc_col is not None and len(row) > conc_col:
            cv = _maybe_float(row[conc_col])
            if cv is not None:
                region["concentration_ng_per_uL"] = cv
        if sid not in grouped:
            grouped[sid] = []
            samples_in_order.append(sid)
        grouped[sid].append(region)

    if not grouped:
        raise ValueError("No usable smear regions in TapeStation CSV")

    results = []
    for sid in samples_in_order:
        regions = grouped[sid]

        # Compute sample-level summary scalars from the per-region
        # rows so the evaluator can match standard criteria like
        # concentration_ng_per_uL and average_size_bp without needing
        # to crack open the smear_regions array.
        confs = [r.get("concentration_ng_per_uL") for r in regions
                 if r.get("concentration_ng_per_uL") is not None]
        pcts = [r.get("pct_total") for r in regions
                if r.get("pct_total") is not None]
        sizes_with_pct = [
            (r.get("average_size_bp"), r.get("pct_total"))
            for r in regions
            if r.get("average_size_bp") is not None
            and r.get("pct_total") is not None
        ]
        plain_sizes = [r.get("average_size_bp") for r in regions
                       if r.get("average_size_bp") is not None]

        measurements = {
            "smear_regions": regions,
            "region_count": len(regions),
            "units": "ng/uL",
        }
        # Library-level concentration = sum across regions (regions
        # partition the library by size, so concentrations add).
        if confs:
            measurements["concentration_ng_per_uL"] = round(sum(confs), 3)
        # Weighted-average fragment size by % total when possible;
        # otherwise simple average across regions.
        if sizes_with_pct and sum(p for _, p in sizes_with_pct) > 0:
            weighted = sum(s * p for s, p in sizes_with_pct)
            total_pct = sum(p for _, p in sizes_with_pct)
            measurements["average_size_bp"] = round(weighted / total_pct, 1)
        elif plain_sizes:
            measurements["average_size_bp"] = round(
                sum(plain_sizes) / len(plain_sizes), 1
            )

        results.append({
            "result_type": "fragment_smear_analysis",
            "instrument": "agilent_tapestation",
            "sample_id": sid,
            "well_position": None,
            "measurements": measurements,
            "pass_fail": None,
            "acceptance_criteria_met": None,
            "notes": "TapeStation smear analysis",
        })
    return results


@register_parser("tapestation_excel_compact")
def parse_tapestation_excel_compact(file_content) -> list:
    """Excel variant of the TapeStation compact summary. Reads cells
    via openpyxl, rebuilds the text rows, and delegates to the CSV
    compact parser to avoid duplicating the column-mapping logic."""
    all_rows, _ = _load_workbook_rows(file_content)
    # Re-flatten to CSV text so we reuse parse_tapestation_csv_compact's
    # header detection + column finding. Each cell becomes a CSV field;
    # we go through csv.writer to handle commas / quoting correctly.
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf)
    for row in all_rows:
        if row is None:
            continue
        writer.writerow(
            ["" if c is None else str(c) for c in row]
        )
    csv_text = buf.getvalue()
    return parse_tapestation_csv_compact(csv_text)


@register_parser("tapestation_ome")
def parse_tapestation_ome(file_content) -> list:
    """Stub for Agilent .ome archives. These are proprietary
    zip-wrapped formats; full extraction (gel image + electropherogram
    + per-well calls) is not yet implemented. For malformed/truncated
    uploads we surface a clear error so the UI doesn't crash."""
    import zipfile
    from io import BytesIO
    raw_bytes = _coerce_to_bytes(file_content)
    if not raw_bytes:
        raise ValueError("Empty .ome upload")
    try:
        with zipfile.ZipFile(BytesIO(raw_bytes)) as zf:
            names = zf.namelist()
    except zipfile.BadZipFile as e:
        raise ValueError(
            f"Not a valid Agilent .ome archive (zip read failed): {e}"
        )
    raise NotImplementedError(
        f".ome parsing is not yet implemented. Archive contains "
        f"{len(names)} entries: {names[:5]}{'...' if len(names) > 5 else ''}"
    )


# === Storage ===

def _get_supabase():
    return create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY"),
    )


def store_uploaded_file(
    pipeline_run_id: str,
    file_name: str,
    file_content,
    file_format: str,
    is_binary: bool = False,
) -> dict:
    """Insert raw file into run_data_uploads table.
    Returns the inserted record."""
    sb = _get_supabase()

    payload = {
        "pipeline_run_id": pipeline_run_id,
        "file_name": file_name,
        "file_format": file_format,
        "file_size_bytes": len(file_content),
        "parse_status": "pending",
    }

    if is_binary:
        # Encode binary content to base64
        if isinstance(file_content, bytes):
            payload["raw_content_b64"] = base64.b64encode(
                file_content
            ).decode('ascii')
        else:
            payload["raw_content_b64"] = file_content
    else:
        payload["raw_content"] = file_content

    result = sb.table("run_data_uploads").insert(
        payload
    ).execute()
    return result.data[0]


def store_parsed_results(
    pipeline_run_id: str,
    upload_id: int,
    parsed_results: list,
) -> int:
    """Insert parsed result records. Returns count inserted."""
    if not parsed_results:
        return 0

    sb = _get_supabase()

    # Tag each with the run+upload IDs
    for r in parsed_results:
        r["pipeline_run_id"] = pipeline_run_id
        r["upload_id"] = upload_id

    result = sb.table("run_results").insert(
        parsed_results
    ).execute()
    return len(result.data) if result.data else 0


def update_upload_status(
    upload_id: int,
    status: str,
    error: str = None,
):
    """Mark an upload as parsed or failed."""
    sb = _get_supabase()
    payload = {"parse_status": status}
    if error:
        payload["parse_error"] = error
    sb.table("run_data_uploads").update(payload).eq(
        "id", upload_id
    ).execute()


# === Acceptance criteria evaluation ===

def evaluate_acceptance_criteria(
    measurements: dict,
    criteria: dict,
) -> dict:
    """Compare measurements against acceptance_criteria field
    on the assay. Returns dict mapping criterion → pass/fail.

    criteria format from assay schema:
        {
            "library_concentration_ng_per_uL": ">5",
            "fragment_size_distribution_bp": "300-500",
            "primer_dimer_pct": "<5"
        }
    """
    results = {}

    for criterion, rule in criteria.items():
        actual = measurements.get(criterion)
        if actual is None:
            results[criterion] = {
                "actual": None,
                "rule": rule,
                "passed": None,
                "note": "Not measured",
            }
            continue

        passed = None
        try:
            import re as _re_eval
            rule_str = str(rule).strip()
            actual_f = float(actual)

            # Range with optional trailing text: "0.5 - 50 ng/uL acceptable..."
            m_range = _re_eval.match(
                r"^\s*([-+]?\d*\.?\d+)\s*[-–]\s*([-+]?\d*\.?\d+)",
                rule_str,
            )
            # Threshold: ">5", ">= 0.7", "< 30 %"
            m_thresh = _re_eval.match(
                r"^\s*(>=|<=|>|<|=)\s*([-+]?\d*\.?\d+)",
                rule_str,
            )

            if m_thresh:
                op, val = m_thresh.group(1), float(m_thresh.group(2))
                if op == ">=":
                    passed = actual_f >= val
                elif op == ">":
                    passed = actual_f > val
                elif op == "<=":
                    passed = actual_f <= val
                elif op == "<":
                    passed = actual_f < val
                elif op == "=":
                    passed = abs(actual_f - val) < 0.01
            elif m_range:
                lo, hi = float(m_range.group(1)), float(m_range.group(2))
                passed = lo <= actual_f <= hi
        except (ValueError, TypeError):
            passed = None

        results[criterion] = {
            "actual": actual,
            "rule": rule,
            "passed": passed,
            "note": "" if passed is not None else "Could not evaluate",
        }

    return results


def compute_overall_pass_fail(criteria_results: dict) -> str:
    """Roll up criteria-level results into overall verdict."""
    if not criteria_results:
        return "not_evaluated"

    statuses = [r["passed"] for r in criteria_results.values()]
    if all(s is True for s in statuses):
        return "pass"
    if any(s is False for s in statuses):
        return "fail"
    if any(s is None for s in statuses):
        return "partial"
    return "not_evaluated"


# Substring hints used to match a measurement key (inside the record's
# measurements jsonb) to an acceptance-criterion key. Case-insensitive
# substring match on both sides. Add an entry here when a new parser
# emits a new measurement key family.
MEASUREMENT_KEY_TO_CRITERIA_HINTS = {
    "concentration":     ("concentration", "conc"),
    "absorbance":        ("absorbance", "od", "a450", "a280", "a260"),
    "fluorescence":      ("fluorescence", "fluor", "rfu"),
    "luminescence":      ("luminescence", "lumin", "rlu"),
    # TapeStation / Fragment Analyzer: criteria like
    # "fragment_size_distribution_bp", "insert_size_range" should map
    # back to per-sample average_size_bp measurements.
    "size":              ("size", "fragment_size", "insert_size", "size_dist"),
    "percent_in_region": ("percent_in_region", "% region", "region_pct"),
}


def _hints_for_measurement_key(mkey: str) -> tuple:
    mkey_lower = mkey.lower()
    for family, hints in MEASUREMENT_KEY_TO_CRITERIA_HINTS.items():
        if family in mkey_lower:
            return hints
    return (mkey_lower,)


def evaluate_and_enrich_results(
    records: list,
    criteria: dict,
) -> list:
    """For each record, find acceptance criteria that apply to one of
    its numeric measurements (via substring hints), evaluate them, then
    write `pass_fail` and `acceptance_criteria_met` back onto the record
    so they land in the run_results row when stored.

    Returns the same list, mutated in place. `acceptance_criteria_met`
    becomes a list of dicts: [{criterion, rule, passed, measurement_key,
    value}]. `pass_fail` becomes one of: 'pass' | 'fail' | 'partial' |
    'not_evaluated'.
    """
    for r in records:
        measurements = r.get("measurements") or {}
        criterion_results = []
        for cname, rule in (criteria or {}).items():
            cname_lower = str(cname).lower()
            # Find the first numeric measurement whose key family matches
            # this criterion's name via the hint table.
            for mkey, mval in measurements.items():
                if not isinstance(mval, (int, float)):
                    continue
                hints = _hints_for_measurement_key(mkey)
                if any(h in cname_lower for h in hints):
                    single = evaluate_acceptance_criteria(
                        {cname: mval}, {cname: rule}
                    )[cname]
                    criterion_results.append({
                        "criterion": cname,
                        "rule": rule,
                        "passed": single["passed"],
                        "measurement_key": mkey,
                        "value": mval,
                    })
                    break  # one measurement per criterion

        if not criterion_results:
            r["pass_fail"] = "not_evaluated"
            r["acceptance_criteria_met"] = None
        else:
            statuses = [c["passed"] for c in criterion_results]
            if all(s is True for s in statuses):
                r["pass_fail"] = "pass"
            elif any(s is False for s in statuses):
                r["pass_fail"] = "fail"
            elif all(s is None for s in statuses):
                r["pass_fail"] = "not_evaluated"
            else:
                r["pass_fail"] = "partial"
            r["acceptance_criteria_met"] = criterion_results

    return records


# Backwards-compat alias — kept so older callers don't break, but new
# code should use evaluate_and_enrich_results.
def evaluate_results_against_criteria(parsed_results, criteria):
    """Deprecated: use evaluate_and_enrich_results. Returns display rows
    derived from the enriched records for legacy UI code."""
    evaluate_and_enrich_results(parsed_results, criteria)
    out = []
    for r in parsed_results:
        measurements = r.get("measurements") or {}
        primary_val = next(
            (v for v in measurements.values() if isinstance(v, (int, float))),
            None,
        )
        out.append({
            "sample_id": r.get("sample_id"),
            "measurement_type": r.get("result_type"),
            "value": primary_val,
            "units": measurements.get("units"),
            "criterion_results": r.get("acceptance_criteria_met") or [],
            "overall": r.get("pass_fail") or "not_evaluated",
        })
    return out
