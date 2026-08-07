"""Unit tests.

Four cases come verbatim from Table 7 of Masopust et al., "Guidelines for
T cell nomenclature", Nat Rev Immunol 26:298-313 (2026):
test_liver_cd8_disseminated_unknown_recency ("Liver CD8+ TD"),
test_cd8_disseminated_resident_exhausted_progenitor_persistent
("CD8+ TDRXp+"), test_migration_subscript_b_valid_on_unknown_migration
("CD8+ TUBM"), and test_migration_subscript_w_valid_on_secondary_lymphoid
(the paper's prose "SW" example). The rest are additional logic-coverage
tests authored for this implementation.
"""
import csv
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nomenclature.models import MARKER_NAMES, TCellRecord
from nomenclature.assemble import generate_nomenclature
from nomenclature.csv_batch import process_csv


def blank_markers():
    return {m: "NA" for m in MARKER_NAMES}


def test_liver_cd8_disseminated_unknown_recency():
    # "CD45RA+CCR7- CD8+ T cell isolated from the liver, migration properties
    # unknown, recency of activation unknown" -> "Liver CD8+ TD"
    markers = blank_markers()
    markers["CD45RA"] = "+"
    markers["CCR7"] = "-"
    record = TCellRecord(location="Liver", lineage="CD8+", markers=markers)
    result = generate_nomenclature(record)
    assert result.nomenclature == "Liver CD8+ TD"
    assert result.migration == "D"
    assert result.migration_subscript == ""
    assert result.differentiation == ""


def test_cd8_disseminated_resident_exhausted_progenitor_persistent():
    # "CD8+ TDRXp+": D (disseminated) + R (resident, user-asserted) +
    # X (exhausted) + p (progenitor subscript) + '+' (persistent antigen)
    markers = blank_markers()
    markers["CCR7"] = "-"
    markers["PD1"] = "+"
    markers["TOX"] = "+"
    markers["TCF1"] = "+"
    markers["SLAMF6"] = "+"
    markers["TIM3"] = "-"
    record = TCellRecord(
        lineage="CD8+",
        markers=markers,
        migration_evidence="R",
        migration_evidence_note="Parabiosis confirms tissue residency.",
        antigen_status="+",
        antigen_note="Chronic infection model, antigen persists.",
    )
    result = generate_nomenclature(record)
    assert result.nomenclature == "CD8+ TDRXp+"


def test_naive_full_markers():
    markers = blank_markers()
    markers["CD62L"] = "+"
    markers["CCR7"] = "+"
    markers["CD45RA"] = "+"
    markers["CD95"] = "-"
    record = TCellRecord(lineage="CD4+", markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "N"
    assert result.nomenclature == "CD4+ TSN"


def test_naive_migration_blank_when_cd62l_not_measured():
    # CCR7+ alone (CD62L not measured) cannot confirm S, and no marker was
    # found negative, so migration is left blank rather than defaulted to
    # 'U' — mirrors the paper's own Box 2 "CD4+ TN" example, where a known
    # CD62L+ result still isn't enough to assert a migration claim.
    markers = blank_markers()
    markers["CCR7"] = "+"
    markers["CD45RA"] = "+"
    markers["CD95"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.migration == ""
    assert result.differentiation == "N"


def test_migration_both_unmeasured_is_blank_not_u():
    # Table 7's own "no further characterization" example renders as plain
    # "CD4+ T cell" (no U) — U is never a silent default here.
    record = TCellRecord(markers=blank_markers())
    result = generate_nomenclature(record)
    assert result.migration == ""
    assert "left blank" in result.rationale


def test_migration_override_asserts_u_explicitly():
    record = TCellRecord(
        markers=blank_markers(),
        migration_override="U",
        migration_override_note="Homing receptors not assessed in this experiment.",
    )
    result = generate_nomenclature(record)
    assert result.migration == "U"
    assert "user-asserted" in result.rationale


def test_migration_secondary_lymphoid():
    markers = blank_markers()
    markers["CD62L"] = "+"
    markers["CCR7"] = "+"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.migration == "S"


def test_migration_subscript_ignored_without_evidence():
    markers = blank_markers()
    markers["CCR7"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.migration == "D"
    assert result.migration_subscript == ""


def test_migration_subscript_ignored_when_not_disseminated():
    # R is only ever valid on D (Masopust et al. 2026, "Migration properties").
    markers = blank_markers()
    markers["CD62L"] = "+"
    markers["CCR7"] = "+"
    record = TCellRecord(markers=markers, migration_evidence="R", migration_evidence_note="irrelevant")
    result = generate_nomenclature(record)
    assert result.migration == "S"
    assert result.migration_subscript == ""
    assert "ignored" in result.rationale


def test_migration_subscript_b_valid_on_unknown_migration():
    # "CD8+ TUBM" is a worked example straight from the paper's Table 7:
    # blood-drawn, migration otherwise unmeasured (explicitly asserted 'U'),
    # memory.
    record = TCellRecord(
        lineage="CD8+",
        markers=blank_markers(),
        migration_override="U",
        migration_override_note="Migration properties not assessed",
        migration_evidence="B",
        migration_evidence_note="Isolated from blood",
        differentiation_override="M",
        differentiation_override_note="Claimed memory cell",
    )
    result = generate_nomenclature(record)
    assert result.migration == "U"
    assert result.migration_subscript == "B"
    assert result.nomenclature == "CD8+ TUBM"


def test_migration_subscript_w_valid_on_secondary_lymphoid():
    # Paper's prose example: a CD62L+/CCR7+ cell that also recirculates
    # through non-lymphoid tissue would be "SW".
    markers = blank_markers()
    markers["CD62L"] = "+"
    markers["CCR7"] = "+"
    record = TCellRecord(markers=markers, migration_evidence="W", migration_evidence_note="Recirculation confirmed")
    result = generate_nomenclature(record)
    assert result.migration == "S"
    assert result.migration_subscript == "W"


def test_migration_subscript_w_ignored_on_unknown_migration():
    # W is only valid on S or D, not U.
    record = TCellRecord(
        markers=blank_markers(),
        migration_override="U",
        migration_override_note="explicit unknown claim",
        migration_evidence="W",
        migration_evidence_note="irrelevant",
    )
    result = generate_nomenclature(record)
    assert result.migration == "U"
    assert result.migration_subscript == ""
    assert "ignored" in result.rationale


def test_exhaustion_terminal_subscript():
    markers = blank_markers()
    markers["PD1"] = "+"
    markers["TOX"] = "+"
    markers["TCF1"] = "-"
    markers["SLAMF6"] = "-"
    markers["TIM3"] = "+"
    markers["CD101"] = "+"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "X"
    assert result.differentiation_subscript == "t"


def test_activated_terminal_subscript_slec():
    # At (short-lived terminal effector / SLEC), per Table 2: KLRG1+, CD127-.
    markers = blank_markers()
    markers["KLRG1"] = "+"
    markers["CD127"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "A"
    assert result.differentiation_subscript == "t"


def test_activated_progenitor_subscript_mpec():
    # Ap (memory precursor effector / MPEC), per Table 2: KLRG1-, CD127+,
    # CD27+, TCF1+.
    markers = blank_markers()
    markers["KLRG1"] = "-"
    markers["CD127"] = "+"
    markers["CD27"] = "+"
    markers["TCF1"] = "+"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "A"
    assert result.differentiation_subscript == "p"


def test_memory_progenitor_subscript_tscm():
    # Mp (stem-cell memory / TSCM), per Table 4: CD95+, CCR7+, CD27+.
    # Notably CD45RA+ (naive-like) rather than CD45RO+, so this would fail
    # the base memory check — Mp is an independent path into 'M'.
    markers = blank_markers()
    markers["CD95"] = "+"
    markers["CCR7"] = "+"
    markers["CD27"] = "+"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "M"
    assert result.differentiation_subscript == "p"


def test_anergic_requires_user_override():
    markers = blank_markers()
    record = TCellRecord(markers=markers, differentiation_override="G", differentiation_override_note="Functional assay: no IL-2 production upon restimulation.")
    result = generate_nomenclature(record)
    assert result.differentiation == "G"
    assert "override" in result.rationale.lower()


def test_no_markers_no_lineage_gives_bare_t():
    record = TCellRecord()
    result = generate_nomenclature(record)
    assert result.nomenclature == "T"  # everything optional and unmeasured -> nothing appended


def test_antigen_status_never_inferred_from_markers():
    markers = blank_markers()
    markers["PD1"] = "+"
    markers["TOX"] = "+"
    record = TCellRecord(markers=markers)  # no antigen_status given
    result = generate_nomenclature(record)
    assert result.antigen == ""
    assert "not asserted" in result.rationale


def test_invalid_antigen_status_raises():
    record = TCellRecord(antigen_status="weird")
    try:
        generate_nomenclature(record)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_differentiation_conflict_is_flagged():
    # Contrived, biologically inconsistent input: satisfies both N and M
    # criteria at once (CD45RA+ and CD45RO+ both asserted positive).
    markers = blank_markers()
    markers["CCR7"] = "+"
    markers["CD45RA"] = "+"
    markers["CD95"] = "-"
    markers["CD45RO"] = "+"
    markers["CD69"] = "-"
    markers["CD25"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "N"  # priority order picks N over M
    assert "CONFLICT WARNING" in result.rationale


def test_csv_batch_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "in.csv")
        out_path = os.path.join(tmp, "out.csv")
        with open(in_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["sample_id", "location", "lineage", "CD45RA", "CCR7"])
            writer.writerow(["S1", "Liver", "CD8+", "+", "-"])
        n = process_csv(in_path, out_path)
        assert n == 1
        with open(out_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert rows[0]["nomenclature"] == "Liver CD8+ TD"
        assert rows[0]["sample_id"] == "S1"  # original columns preserved


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
