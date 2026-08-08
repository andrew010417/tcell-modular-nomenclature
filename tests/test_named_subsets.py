"""Cross-checks against named subsets from Tables 1-6 of Masopust et al.,
"Guidelines for T cell nomenclature", Nat Rev Immunol 26:298-313 (2026).

tests/test_table7.py already reproduces worked examples from the paper's
own Table 7 (modular nomenclature output). This file goes a level deeper:
it takes the *existing-nomenclature* marker definitions the paper gives for
well-known named subsets (TCM, TEM, TEMRA, TRM, TSCM in Table 4; SLEC/MPEC
in Table 2; TPEX/TEX-int/TEX-term in Table 5) and checks that feeding those
exact marker profiles into this program's modular classifier produces the
code the paper itself says that subset should map to.

Each test's docstring quotes the paper's marker list for that subset
(human column, since that's what this program's 13+3-marker panel is
modeled on) and only sets the markers that are also in this program's
panel — markers from the paper's list that aren't in our panel (e.g.
CX3CR1, T-bet, granzyme B, BCL6, CXCR5) are noted but left unmeasured,
consistent with this program's own design principle: a slot is never
guessed at from a marker we didn't ask about.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nomenclature.models import MARKER_NAMES, TCellRecord
from nomenclature.assemble import generate_nomenclature


def blank_markers():
    return {m: "NA" for m in MARKER_NAMES}


# --- Table 4: memory T cell subsets ----------------------------------------

def test_tcm_maps_to_s_plus_m():
    # Table 4, TCM (human): CD62L+, CCR7+; other markers CD27+, CX3CR1-,
    # CD45RO+, CD45RA-. (CX3CR1 isn't in our panel.) CD69-/CD25- supplied
    # here to reflect a resting (not recently activated) central memory
    # cell, since the base M check requires them explicitly negative.
    # This is also literally Table 7's own comparison row: "CD8+ TCM cell"
    # -> modular "CD8+ TSM".
    markers = blank_markers()
    markers["CD62L"] = "+"
    markers["CCR7"] = "+"
    markers["CD45RO"] = "+"
    markers["CD45RA"] = "-"
    markers["CD27"] = "+"
    markers["CD69"] = "-"
    markers["CD25"] = "-"
    record = TCellRecord(lineage="CD8+", markers=markers)
    result = generate_nomenclature(record)
    assert result.migration == "S"
    assert result.differentiation == "M"
    assert result.nomenclature == "CD8+ TSM"


def test_tem_maps_to_d_plus_m():
    # Table 4, TEM (human): CCR7-, CD45RA- (other: CD62L-, though "cell
    # surface CD62L may get altered during processing" per the paper's own
    # caveat). The Migration prose section explicitly states D "broadly
    # includes what is currently referred to as TEM, TPM and TRM".
    markers = blank_markers()
    markers["CCR7"] = "-"
    markers["CD62L"] = "-"
    markers["CD45RA"] = "-"
    markers["CD69"] = "-"
    markers["CD25"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.migration == "D"
    assert result.differentiation == "M"


def test_temra_migration_d_but_differentiation_left_unassigned():
    # Table 4, TEMRA (human): CCR7-, CD45RA+ (not applicable to mice).
    # CD45RA+ makes this marker profile look naive-ish, but CCR7- rules out
    # N (which requires CCR7+), and CD45RA+ (rather than CD45RO+/CD45RA-)
    # doesn't satisfy this program's base memory check either. Rather than
    # guess between "it's kind of like naive" and "it's kind of like
    # memory", the tool correctly leaves differentiation blank -- exactly
    # the over-claim-avoidance behavior the program is designed around.
    markers = blank_markers()
    markers["CCR7"] = "-"
    markers["CD45RA"] = "+"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.migration == "D"
    assert result.differentiation == ""


def test_trm_migration_d_subscript_requires_explicit_residency_evidence():
    # Table 4, TRM (human): KLF2low, CD69+, CD62L-, CCR7- (also CD103+,
    # TCF1low, CD49a+, CD101+, CXCR6+ -- KLF2/CD103/CD49a/CXCR6 aren't in
    # our panel). The paper is explicit that TRM markers are "imperfect"
    # and that residency claims need dedicated assays (organ transplant,
    # parabiosis, photoconversion, TCR-seq comparison) -- so CD69+ alone
    # should NOT auto-produce an R subscript, and shouldn't force a
    # differentiation call either.
    markers = blank_markers()
    markers["CD69"] = "+"
    markers["CD62L"] = "-"
    markers["CCR7"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.migration == "D"
    assert result.migration_subscript == ""  # no residency assay evidence supplied
    assert result.differentiation == ""

    # Only once that assay evidence is explicitly supplied does R appear.
    record.migration_evidence = "R"
    record.migration_evidence_note = "Parabiosis: minimal equilibration confirms residency."
    result_with_evidence = generate_nomenclature(record)
    assert result_with_evidence.migration_subscript == "R"


def test_tscm_maps_to_memory_progenitor_subscript():
    # Table 4, TSCM (human): CD95+, CCR7+, CD27+, CD28+, CD45RA+, Eomes-.
    # (CD28/Eomes aren't in our panel.) The paper notes "TSCM share many
    # markers with naive T cells" -- CD95 is specifically what tells them
    # apart here (naive requires CD95-), which this asserts explicitly.
    # CD62L isn't part of the paper's human TSCM marker list, so it's left
    # unmeasured -- migration is correctly left blank rather than guessed.
    markers = blank_markers()
    markers["CD95"] = "+"
    markers["CCR7"] = "+"
    markers["CD27"] = "+"
    markers["CD45RA"] = "+"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.migration == ""
    assert result.differentiation == "M"
    assert result.differentiation_subscript == "p"


# --- Table 2: activated/effector CD8+ T cell subsets ------------------------

def test_slec_maps_to_activated_terminal_subscript():
    # Table 2, SLEC / terminal effector (TE) cell -- the marker pair common
    # to both the human and mouse columns: KLRG1+, CD127low.
    markers = blank_markers()
    markers["KLRG1"] = "+"
    markers["CD127"] = "-"
    record = TCellRecord(lineage="CD8+", markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "A"
    assert result.differentiation_subscript == "t"
    assert result.nomenclature == "CD8+ TAt"


def test_mpec_maps_to_activated_progenitor_subscript():
    # Table 2, MPEC / memory precursor cell (mouse, since "lacking
    # universally accepted proxy markers" in humans per the paper):
    # CD127+, CD27+, KLRG1low, TCF1+ (also T-betint, CD62L+/-, CX3CR1-,
    # CXCR3+ -- not in our panel).
    markers = blank_markers()
    markers["CD127"] = "+"
    markers["CD27"] = "+"
    markers["KLRG1"] = "-"
    markers["TCF1"] = "+"
    record = TCellRecord(lineage="CD8+", markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "A"
    assert result.differentiation_subscript == "p"
    assert result.nomenclature == "CD8+ TAp"


# --- Table 5: T cell exhaustion subsets --------------------------------------

def test_tpex_maps_to_exhausted_progenitor_subscript():
    # Table 5, TPEX (human): PD-1+, TOX+, TCF1+, BCL6+, SLAMF6+, CXCR3+,
    # LEF1+, CD28+, CD73+, XCL1+, CXCR5+, TIM3-, CD39-, CX3CR1lo/int,
    # granzyme B- (only PD1/TOX/TCF1/SLAMF6/TIM3 are in our panel). The
    # paper states in prose: "exhausted progenitors, currently referred to
    # as TPEX, would be called Xp".
    markers = blank_markers()
    markers["PD1"] = "+"
    markers["TOX"] = "+"
    markers["TCF1"] = "+"
    markers["SLAMF6"] = "+"
    markers["TIM3"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "X"
    assert result.differentiation_subscript == "p"


def test_tex_term_maps_to_exhausted_terminal_subscript():
    # Table 5, TEX-term (human): PD-1+, TOX+, TIM3+, granzyme B+, CD39+,
    # 2B4+, CD101+, TCF1-, SLAMF6-, CX3CR1-, CXCR3- (only PD1/TOX/TIM3/
    # CD101/TCF1/SLAMF6 are in our panel). Notably CD101 is POSITIVE here,
    # which is what distinguishes TEX-term from TEX-int below.
    markers = blank_markers()
    markers["PD1"] = "+"
    markers["TOX"] = "+"
    markers["TIM3"] = "+"
    markers["CD101"] = "+"
    markers["TCF1"] = "-"
    markers["SLAMF6"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "X"
    assert result.differentiation_subscript == "t"


def test_tex_int_is_exhausted_but_neither_progenitor_nor_terminal():
    # Table 5, TEX-int / TEX-eff (human): PD-1+, TOX+, TIM3+, T-bet+,
    # granzyme B+, perforin+, IFNγ+, CX3CR1+, TCF1-, SLAMF6-, CD101- (only
    # PD1/TOX/TIM3/TCF1/SLAMF6/CD101 are in our panel). CD101- is what
    # distinguishes this transitional state from TEX-term (CD101+) above.
    # The paper doesn't map this intermediate/transitional state to a
    # p or t subscript, and this program correctly doesn't invent one:
    # X is called, but with no subscript.
    markers = blank_markers()
    markers["PD1"] = "+"
    markers["TOX"] = "+"
    markers["TIM3"] = "+"
    markers["TCF1"] = "-"
    markers["SLAMF6"] = "-"
    markers["CD101"] = "-"
    record = TCellRecord(markers=markers)
    result = generate_nomenclature(record)
    assert result.differentiation == "X"
    assert result.differentiation_subscript == ""


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
