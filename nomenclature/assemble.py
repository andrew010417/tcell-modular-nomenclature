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


def generate_nomenclature(record: TCellRecord) -> NomenclatureResult:
    migration = classify_migration(record.markers)
    migration_sub = classify_migration_subscript(
        migration.code, record.migration_evidence, record.migration_evidence_note
    )
    differentiation = classify_differentiation(
        record.markers, record.differentiation_override, record.differentiation_override_note
    )
    antigen = classify_antigen(record.antigen_status, record.antigen_note)

    lineage = (record.lineage or "").strip()
    function = (record.function or "").strip()
    location = (record.location or "").strip()

    core = "T" + function + migration.code + migration_sub.code + differentiation.code + differentiation.subscript + antigen.code

    parts = [p for p in (location, lineage) if p]
    parts.append(core)
    nomenclature = " ".join(parts)

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
