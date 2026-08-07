"""Assembles per-slot classifications into the final nomenclature string
and a human-readable audit report.

Format (validated against the two worked examples in the project brief):

    [Location] [Lineage] T[Function][Migration][MigSub][Diff][DiffSub][Antigen]

  "CD8+ TDRXp+"      -> lineage=CD8+, migration=D, migsub=R, diff=X, diffsub=p, antigen=+
  "Liver CD8+ TD"    -> location=Liver, lineage=CD8+, migration=D, diff='' (unassigned)

`Location` is not one of the paper's 5 module slots, but the examples
include an anatomical-site prefix, so it is supported as an optional
free-text label placed before Lineage.
"""
from __future__ import annotations

from .models import NomenclatureResult, TCellRecord
from .slots import (
    classify_antigen,
    classify_differentiation,
    classify_migration,
    classify_migration_subscript,
)


def generate_nomenclature(record: TCellRecord, lang: str = "en") -> NomenclatureResult:
    migration = classify_migration(record.markers, lang=lang)
    migration_sub = classify_migration_subscript(
        migration.code, record.migration_evidence, record.migration_evidence_note, lang=lang
    )
    differentiation = classify_differentiation(
        record.markers, record.differentiation_override, record.differentiation_override_note, lang=lang
    )
    antigen = classify_antigen(record.antigen_status, record.antigen_note, lang=lang)

    lineage = (record.lineage or "").strip()
    function = (record.function or "").strip()
    location = (record.location or "").strip()

    core = "T" + function + migration.code + migration_sub.code + differentiation.code + differentiation.subscript + antigen.code

    parts = [p for p in (location, lineage) if p]
    parts.append(core)
    nomenclature = " ".join(parts)

    if lang == "ko":
        rationale_lines = [
            f"- 이동(Migration): {migration.rationale}",
            f"- 이동 아래첨자: {migration_sub.rationale}" if migration_sub.rationale else None,
            f"- 분화 상태(Differentiation): {differentiation.rationale}",
            f"- 항원 상태(Antigen): {antigen.rationale}",
        ]
    else:
        rationale_lines = [
            f"- Migration: {migration.rationale}",
            f"- Migration subscript: {migration_sub.rationale}" if migration_sub.rationale else None,
            f"- Differentiation: {differentiation.rationale}",
            f"- Antigen status: {antigen.rationale}",
        ]
    rationale = "\n".join(line for line in rationale_lines if line)

    return NomenclatureResult(
        nomenclature=nomenclature,
        label=record.label,
        location=location,
        lineage=lineage,
        function=function,
        migration=migration.code,
        migration_subscript=migration_sub.code,
        differentiation=differentiation.code,
        differentiation_subscript=differentiation.subscript,
        antigen=antigen.code,
        rationale=rationale,
    )
