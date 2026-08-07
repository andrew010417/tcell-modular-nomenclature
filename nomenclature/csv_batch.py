"""Batch mode: read a CSV of samples/populations, add nomenclature columns,
write the result out.

Expected columns (all optional, matched case-insensitively and ignoring
spaces/underscores/hyphens):
  - marker columns named after any entry in MARKER_NAMES (e.g. CD62L, CCR7,
    PD-1, ...), values '+' / '-' / blank(or 'NA') -- missing columns are
    simply treated as not-measured for every row.
  - metadata columns: label, location, lineage, function,
    migration_override, migration_override_note,
    migration_evidence, migration_evidence_note,
    differentiation_override, differentiation_override_note,
    antigen_status, antigen_note
"""
from __future__ import annotations

import csv
from typing import Dict, List

from .assemble import generate_nomenclature
from .models import MARKER_NAMES, TCellRecord

META_FIELDS = [
    "label",
    "location",
    "lineage",
    "function",
    "migration_override",
    "migration_override_note",
    "migration_evidence",
    "migration_evidence_note",
    "differentiation_override",
    "differentiation_override_note",
    "antigen_status",
    "antigen_note",
]


def _normalize_header(h: str) -> str:
    return h.strip().upper().replace(" ", "").replace("_", "").replace("-", "")


def _build_header_map(fieldnames: List[str]) -> Dict[str, str]:
    """normalized-name -> actual CSV column name, for known marker/meta fields."""
    known = {_normalize_header(n): n for n in MARKER_NAMES}
    known.update({_normalize_header(n): n for n in META_FIELDS})
    header_map: Dict[str, str] = {}
    for actual in fieldnames:
        norm = _normalize_header(actual)
        if norm in known:
            header_map[norm] = actual
    return header_map


def _row_to_record(row: Dict[str, str], header_map: Dict[str, str]) -> TCellRecord:
    def meta(field: str) -> str:
        col = header_map.get(_normalize_header(field))
        return (row.get(col, "") or "").strip() if col else ""

    markers = {}
    for marker in MARKER_NAMES:
        col = header_map.get(_normalize_header(marker))
        markers[marker] = row.get(col, "") if col else "NA"

    return TCellRecord(
        label=meta("label"),
        location=meta("location"),
        lineage=meta("lineage"),
        function=meta("function"),
        markers=markers,
        migration_override=meta("migration_override") or None,
        migration_override_note=meta("migration_override_note"),
        migration_evidence=meta("migration_evidence") or None,
        migration_evidence_note=meta("migration_evidence_note"),
        differentiation_override=meta("differentiation_override") or None,
        differentiation_override_note=meta("differentiation_override_note"),
        antigen_status=meta("antigen_status"),
        antigen_note=meta("antigen_note"),
    )


def process_csv(input_path: str, output_path: str, lang: str = "en") -> int:
    """Read `input_path`, append nomenclature columns, write to `output_path`.

    Returns the number of rows processed.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    header_map = _build_header_map(fieldnames)
    unmatched_markers = [m for m in MARKER_NAMES if _normalize_header(m) not in header_map]
    if unmatched_markers:
        print(
            "Note: no column found for these markers, treated as not-measured for all rows: "
            + ", ".join(unmatched_markers)
        )

    new_cols = [
        "nomenclature",
        "migration",
        "migration_subscript",
        "differentiation",
        "differentiation_subscript",
        "antigen",
        "rationale",
    ]
    out_fieldnames = list(fieldnames) + [c for c in new_cols if c not in fieldnames]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        for row in rows:
            record = _row_to_record(row, header_map)
            result = generate_nomenclature(record, lang=lang)
            out_row = dict(row)
            out_row["nomenclature"] = result.nomenclature
            out_row["migration"] = result.migration
            out_row["migration_subscript"] = result.migration_subscript
            out_row["differentiation"] = result.differentiation
            out_row["differentiation_subscript"] = result.differentiation_subscript
            out_row["antigen"] = result.antigen
            out_row["rationale"] = result.rationale.replace("\n", " | ")
            writer.writerow(out_row)

    return len(rows)
