"""Unit tests.

Only two of the cases below (test_liver_cd8_disseminated_unknown_recency and
test_cd8_disseminated_resident_exhausted_progenitor_persistent) come verbatim
from the worked examples given in the project brief (representing the kind
of example found in the paper's Table 7). The rest are additional MVP
logic-coverage tests authored for this implementation, since the full paper
table text was not available while building this program.
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


def test_naive_migration_unknown_when_cd62l_not_measured():
    markers = blank_markers()
    markers["CCR7"] = "+"
    markers["CD45RA"] = "+"
    markers["CD95"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    # CCR7+ alone (CD62L not measured) cannot confirm S, and no marker was
    # found negative, so migration must fall back to U.
    assert result.migration == "U"
    assert result.differentiation == "N"


def test_migration_both_unmeasured_is_u():
    record = TCellRecord(markers=blank_markers())
    result = generate_nomenclature(record)
    assert result.migration == "U"
    assert "both not measured" in result.rationale


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
    markers = blank_markers()
    markers["CD62L"] = "+"
    markers["CCR7"] = "+"
    record = TCellRecord(markers=markers, migration_evidence="R", migration_evidence_note="irrelevant")
    result = generate_nomenclature(record)
    assert result.migration == "S"
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


def test_anergic_requires_user_override():
    markers = blank_markers()
    record = TCellRecord(markers=markers, differentiation_override="G", differentiation_override_note="Functional assay: no IL-2 production upon restimulation.")
    result = generate_nomenclature(record)
    assert result.differentiation == "G"
    assert "override" in result.rationale.lower()


def test_no_markers_no_lineage_gives_bare_t():
    record = TCellRecord()
    result = generate_nomenclature(record)
    assert result.nomenclature == "TU"  # migration defaults to U, everything else blank


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
