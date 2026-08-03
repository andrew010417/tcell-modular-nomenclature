"""Interactive command-line flow: ask for markers/metadata for one T cell
population at a time, print the resulting nomenclature + audit report, and
optionally repeat for more populations / save everything to CSV.

Markers are asked in logical groups (migration, naive/memory, activation,
exhaustion, exhaustion subtype), each with a one-line explanation of what
the group determines and what each marker means — so a user doesn't need to
already have the 13-marker panel memorized.
"""
from __future__ import annotations

import csv
from typing import List

from .assemble import generate_nomenclature
from .models import MARKER_DESCRIPTIONS, MARKER_GROUPS, MARKER_NAMES, TCellRecord, normalize_marker_value

_DIVIDER = "-" * 60


def _prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"{text}{suffix}: ").strip()
    return raw if raw else default


def _prompt_yes_no(text: str, default_no: bool = True) -> bool:
    default = "N" if default_no else "Y"
    raw = _prompt(f"{text} (y/n)", default)
    return raw.strip().upper().startswith("Y")


def _prompt_marker(name: str) -> str:
    description = MARKER_DESCRIPTIONS.get(name, "")
    while True:
        raw = input(f"  {name} [{description}]\n    + / - / (Enter = not measured): ").strip()
        if raw == "":
            return "NA"
        value = normalize_marker_value(raw)
        if value == "NA" and raw.upper() not in ("NA", "N/A", "U", "UNKNOWN"):
            print(f"    '{raw}' not recognized as +/- -> treated as not measured (NA).")
        return value


def _print_intro() -> None:
    print(_DIVIDER)
    print("T cell modular nomenclature — interactive mode")
    print(_DIVIDER)
    print(
        "For each marker you'll be asked to type '+', '-', or just press Enter\n"
        "if it wasn't measured. Markers you skip are never guessed at — the\n"
        "corresponding part of the name is simply left blank/'U', with a note\n"
        "in the report explaining why."
    )


def collect_record_interactively() -> TCellRecord:
    print("\n" + _DIVIDER)
    print("New T cell population")
    print(_DIVIDER)
    label = _prompt("Sample / population label (optional)")
    location = _prompt("Tissue / anatomical location, e.g. 'Liver' (optional)")
    lineage = _prompt("Lineage, e.g. 'CD8+' (optional)")
    function = _prompt("Function, e.g. 'TH1' (optional)")

    print(f"\n{_DIVIDER}\nMarker gating results\n{_DIVIDER}")
    markers = {}
    for group_title, group_markers, group_note in MARKER_GROUPS:
        print(f"\n> {group_title}")
        print(f"  ({group_note})")
        for name in group_markers:
            markers[name] = _prompt_marker(name)

    record = TCellRecord(
        label=label, location=location, lineage=lineage, function=function, markers=markers
    )

    # Migration subscript is only meaningful once migration is known to be
    # 'D'; compute it now just to decide whether to prompt.
    from .slots import classify_migration

    migration_preview = classify_migration(markers)
    if migration_preview.code == "D":
        print(f"\n> Migration was classified as D (disseminated): {migration_preview.rationale}")
        print(
            "  D alone just means 'not confirmed to enter lymph nodes'. If you have extra\n"
            "  assay evidence (e.g. parabiosis, recirculation study), you can add a subscript:\n"
            "    B = isolated from blood, no further evidence\n"
            "    W = widespread recirculation confirmed (non-HEV route)\n"
            "    R = tissue residency confirmed"
        )
        if _prompt_yes_no("  Add a migration subscript?"):
            while True:
                letter = _prompt("    Subscript letter (B/W/R)").strip().upper()
                if letter in ("B", "W", "R"):
                    break
                print(f"    '{letter}' isn't one of B/W/R — try again.")
            record.migration_evidence = letter
            record.migration_evidence_note = _prompt("    Justification / assay evidence")

    print(
        "\n> Differentiation state override\n"
        "  Anergic (G) is a functional definition and can't be read off markers —\n"
        "  it's only ever set here, by you, with a justification."
    )
    if _prompt_yes_no("  Manually set/override the differentiation state?"):
        record.differentiation_override = _prompt("    Differentiation code (e.g. 'G')")
        record.differentiation_override_note = _prompt("    Justification")

    print(
        "\n> Antigen status\n"
        "  This can never be read from markers — it depends on your experimental\n"
        "  design (e.g. is the infection/tumor still present?). Leave blank if you\n"
        "  don't want to make a claim either way."
    )
    while True:
        antigen = _prompt("  Antigen status: '+' persistent, '0' cleared, blank = not asserted", "")
        if antigen in ("", "+", "0"):
            break
        print(f"    '{antigen}' isn't one of '+', '0', or blank — try again.")
    record.antigen_status = antigen
    if antigen:
        record.antigen_note = _prompt("    Justification for antigen status")

    return record


def _print_result(result) -> None:
    print("\n" + _DIVIDER)
    print(f"NOMENCLATURE: {result.nomenclature}")
    print(_DIVIDER)
    print("Slot-by-slot breakdown:")
    print(f"  Lineage         : {result.lineage or '(not given)'}")
    print(f"  Function        : {result.function or '(not given)'}")
    print(f"  Migration       : {result.migration or '(not given)'}{' ' + result.migration_subscript if result.migration_subscript else ''}")
    print(f"  Differentiation : {result.differentiation or '(not assigned)'}{result.differentiation_subscript}")
    print(f"  Antigen status  : {result.antigen or '(not asserted)'}")
    print("\nWhy (audit trail — check this before trusting the name):")
    for line in result.rationale.split("\n"):
        print(f"  {line}")


def run_interactive() -> None:
    _print_intro()
    records: List[TCellRecord] = []
    while True:
        record = collect_record_interactively()
        result = generate_nomenclature(record)
        _print_result(result)
        records.append(record)

        if not _prompt_yes_no("\nAdd another population?"):
            break

    if _prompt_yes_no("\nSave all results to a CSV file?"):
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
