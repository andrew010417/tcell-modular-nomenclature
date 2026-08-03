"""Interactive command-line flow: ask for markers/metadata for one T cell
population at a time, print the resulting nomenclature + audit report, and
optionally repeat for more populations / save everything to CSV.
"""
from __future__ import annotations

import csv
import sys
from typing import List

from .assemble import generate_nomenclature
from .models import MARKER_NAMES, TCellRecord, normalize_marker_value


def _prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"{text}{suffix}: ").strip()
    return raw if raw else default


def _prompt_marker(name: str) -> str:
    while True:
        raw = input(f"  {name} (+ / - / blank=not measured): ").strip()
        if raw == "":
            return "NA"
        value = normalize_marker_value(raw)
        if raw.upper() not in ("+", "-", "NA") and value == "NA" and raw.upper() not in ("NA",):
            print(f"    Unrecognized value '{raw}' -> treated as not measured (NA).")
        return value


def collect_record_interactively() -> TCellRecord:
    print("\n--- New T cell population ---")
    label = _prompt("Sample / population label (optional)")
    location = _prompt("Tissue / anatomical location (optional)")
    lineage = _prompt("Lineage, e.g. 'CD8+' (optional)")
    function = _prompt("Function, e.g. 'TH1' (optional)")

    print("Enter marker gating results (press Enter to leave a marker as not measured):")
    markers = {name: _prompt_marker(name) for name in MARKER_NAMES}

    record = TCellRecord(
        label=label, location=location, lineage=lineage, function=function, markers=markers
    )

    # Migration subscript is only meaningful once migration is known to be
    # 'D'; compute it now just to decide whether to prompt.
    from .slots import classify_migration

    migration_preview = classify_migration(markers)
    if migration_preview.code == "D":
        print(f"(Migration classified as D: {migration_preview.rationale})")
        wants_sub = _prompt("Provide migration subscript evidence B/W/R? (y/N)", "N")
        if wants_sub.strip().upper().startswith("Y"):
            record.migration_evidence = _prompt("  Subscript (B=blood, W=widespread, R=resident)")
            record.migration_evidence_note = _prompt("  Justification / assay evidence")

    wants_override = _prompt("Manually override differentiation state (e.g. 'G' for anergic)? (y/N)", "N")
    if wants_override.strip().upper().startswith("Y"):
        record.differentiation_override = _prompt("  Differentiation override code")
        record.differentiation_override_note = _prompt("  Justification")

    antigen = _prompt("Antigen status: '+' persistent, '0' cleared, blank = not asserted", "")
    record.antigen_status = antigen
    if antigen:
        record.antigen_note = _prompt("  Justification for antigen status")

    return record


def run_interactive() -> None:
    records: List[TCellRecord] = []
    while True:
        record = collect_record_interactively()
        result = generate_nomenclature(record)

        print("\n=== Result ===")
        print(f"Nomenclature: {result.nomenclature}")
        print("Rationale:")
        print(result.rationale)
        records.append(record)

        again = _prompt("\nAdd another population? (y/N)", "N")
        if not again.strip().upper().startswith("Y"):
            break

    save = _prompt("\nSave all results to a CSV file? (y/N)", "N")
    if save.strip().upper().startswith("Y"):
        out_path = _prompt("Output CSV path", "nomenclature_output.csv")
        _write_records_csv(records, out_path)
        print(f"Saved {len(records)} record(s) to {out_path}")


def _write_records_csv(records: List[TCellRecord], out_path: str) -> None:
    fieldnames = (
        ["label", "location", "lineage", "function"]
        + MARKER_NAMES
        + [
            "migration_evidence",
            "migration_evidence_note",
            "differentiation_override",
            "differentiation_override_note",
            "antigen_status",
            "antigen_note",
            "nomenclature",
            "migration",
            "migration_subscript",
            "differentiation",
            "differentiation_subscript",
            "antigen",
            "rationale",
        ]
    )
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            result = generate_nomenclature(record)
            row = {
                "label": record.label,
                "location": record.location,
                "lineage": record.lineage,
                "function": record.function,
                **record.markers,
                "migration_evidence": record.migration_evidence or "",
                "migration_evidence_note": record.migration_evidence_note,
                "differentiation_override": record.differentiation_override or "",
                "differentiation_override_note": record.differentiation_override_note,
                "antigen_status": record.antigen_status,
                "antigen_note": record.antigen_note,
                "nomenclature": result.nomenclature,
                "migration": result.migration,
                "migration_subscript": result.migration_subscript,
                "differentiation": result.differentiation,
                "differentiation_subscript": result.differentiation_subscript,
                "antigen": result.antigen,
                "rationale": result.rationale.replace("\n", " | "),
            }
            writer.writerow(row)


if __name__ == "__main__":
    run_interactive()
