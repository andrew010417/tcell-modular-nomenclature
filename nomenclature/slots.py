"""Marker (and user-assertion) based classification for each nomenclature slot.

Guiding rule throughout this module: a slot is only assigned a definite code
when the evidence explicitly supports it. Missing markers never get guessed
at — they simply leave the slot unassigned ('' or 'U', depending on what the
nomenclature defines for "unknown" in that slot) and the reason is recorded
in the returned rationale so a human can audit the call.
"""
from __future__ import annotations

from typing import Dict, Optional

from .models import SlotResult, get_marker

VALID_MIGRATION_SUBSCRIPTS = {"B", "W", "R"}
_MIGRATION_SUBSCRIPT_LABELS = {
    "B": "blood (isolated from blood, no additional migration evidence)",
    "W": "widespread (non-HEV recirculation confirmed)",
    "R": "resident (tissue residency confirmed, e.g. parabiosis/transplant/TCR-seq comparison)",
}


def classify_migration(markers: Dict[str, str]) -> SlotResult:
    """S / D / U per CD62L and CCR7.

    S: CD62L+ AND CCR7+
    D: CD62L- and/or CCR7- (at least one confirmed negative)
    U: neither marker measured, OR only one is measured and it is positive
       (i.e. there isn't enough evidence to confirm either S or D — this
       partial-data case is an explicit extension beyond the paper's literal
       "both unmeasured" definition of U, made to keep the over-claim-avoidance
       principle consistent; confirmed with the user).
    """
    cd62l = get_marker(markers, "CD62L")
    ccr7 = get_marker(markers, "CCR7")

    if cd62l == "+" and ccr7 == "+":
        return SlotResult(
            code="S",
            rationale=f"S: CD62L+ and CCR7+ (both confirmed positive) -> can enter secondary lymphoid organs.",
        )

    if cd62l == "-" or ccr7 == "-":
        negs = [n for n, v in (("CD62L", cd62l), ("CCR7", ccr7)) if v == "-"]
        return SlotResult(
            code="D",
            rationale=f"D: {', '.join(negs)} confirmed negative -> disseminated, cannot enter via HEV.",
        )

    if cd62l == "NA" and ccr7 == "NA":
        return SlotResult(
            code="U",
            rationale="U: CD62L and CCR7 both not measured.",
        )

    return SlotResult(
        code="U",
        rationale=(
            f"U: insufficient evidence to confirm S or D (CD62L={cd62l}, CCR7={ccr7}); "
            "only partially measured and neither marker was found negative."
        ),
    )


def classify_migration_subscript(
    migration_code: str,
    evidence: Optional[str],
    note: str = "",
) -> SlotResult:
    """B / W / R subscript. Only applicable when migration == 'D', and only
    ever set from an explicit user assertion + justification — never inferred
    from markers, since the subscript is itself a claim about additional
    assay evidence (parabiosis, recirculation studies, etc.).
    """
    if migration_code != "D":
        if evidence:
            return SlotResult(
                rationale=(
                    f"Migration subscript '{evidence}' ignored: only applicable when "
                    f"migration='D' (computed migration was '{migration_code}')."
                )
            )
        return SlotResult(rationale="")

    if not evidence:
        return SlotResult(
            rationale=(
                "No migration subscript assigned: migration='D' confirmed, but the user "
                "did not supply explicit B/W/R evidence."
            )
        )

    code = evidence.strip().upper()
    if code not in VALID_MIGRATION_SUBSCRIPTS:
        raise ValueError(
            f"Invalid migration_evidence '{evidence}'; must be one of {sorted(VALID_MIGRATION_SUBSCRIPTS)} or empty."
        )

    label = _MIGRATION_SUBSCRIPT_LABELS[code]
    justification = note.strip() if note else "(no justification note provided)"
    return SlotResult(
        code=code,
        rationale=f"{code}: user-asserted {label}. Justification: {justification}",
    )


def _naive_match(m: Dict[str, str]):
    ccr7, ra, ro, cd95 = (get_marker(m, k) for k in ("CCR7", "CD45RA", "CD45RO", "CD95"))
    matched = ccr7 == "+" and (ra == "+" or ro == "-") and cd95 == "-"
    return matched, f"CCR7={ccr7}, CD45RA={ra}, CD45RO={ro}, CD95={cd95}"


def _activated_match(m: Dict[str, str]):
    cd69, cd25, pd1, tox = (get_marker(m, k) for k in ("CD69", "CD25", "PD1", "TOX"))
    matched = (cd69 == "+" or cd25 == "+") and pd1 == "-" and tox == "-"
    return matched, f"CD69={cd69}, CD25={cd25}, PD1={pd1}, TOX={tox}"


def _memory_match(m: Dict[str, str]):
    ro, ra, cd69, cd25 = (get_marker(m, k) for k in ("CD45RO", "CD45RA", "CD69", "CD25"))
    matched = (ro == "+" or ra == "-") and cd69 == "-" and cd25 == "-"
    return matched, f"CD45RO={ro}, CD45RA={ra}, CD69={cd69}, CD25={cd25}"


def _exhausted_match(m: Dict[str, str]):
    pd1, tox = get_marker(m, "PD1"), get_marker(m, "TOX")
    matched = pd1 == "+" and tox == "+"
    return matched, f"PD1={pd1}, TOX={tox}"


def _exhaustion_subscript(m: Dict[str, str]):
    tcf1, slamf6, tim3, cd101 = (get_marker(m, k) for k in ("TCF1", "SLAMF6", "TIM3", "CD101"))
    if tcf1 == "+" and slamf6 == "+" and tim3 == "-":
        return SlotResult(code="p", rationale=f"p: TCF1+, SLAMF6+, TIM3- (progenitor exhausted).")
    if tcf1 == "-" and slamf6 == "-" and tim3 == "+" and cd101 == "+":
        return SlotResult(code="t", rationale=f"t: TCF1-, SLAMF6-, TIM3+, CD101+ (terminal exhausted).")
    return SlotResult(
        code="",
        rationale=(
            f"no exhaustion subscript: criteria for progenitor (p) or terminal (t) not both met "
            f"(TCF1={tcf1}, SLAMF6={slamf6}, TIM3={tim3}, CD101={cd101})."
        ),
    )


def classify_differentiation(
    markers: Dict[str, str],
    override: Optional[str] = None,
    override_note: str = "",
) -> SlotResult:
    """N / A / M / X(+p/t subscript) / G.

    G (anergic) is functionally defined and cannot be determined from
    markers, so it is only ever set via explicit user override.

    Priority when marker data would satisfy more than one category
    (contradictory/unusual input): X > N > A > M. Any such conflict is
    called out explicitly in the rationale rather than silently resolved.
    """
    if override:
        code = override.strip().upper()
        justification = override_note.strip() if override_note else "(none provided)"
        return SlotResult(
            code=code,
            rationale=f"User override: differentiation manually set to '{code}'. Justification: {justification}",
        )

    x_ok, x_detail = _exhausted_match(markers)
    n_ok, n_detail = _naive_match(markers)
    a_ok, a_detail = _activated_match(markers)
    m_ok, m_detail = _memory_match(markers)

    matched_codes = [c for c, ok in (("X", x_ok), ("N", n_ok), ("A", a_ok), ("M", m_ok)) if ok]
    conflict_note = ""
    if len(matched_codes) > 1:
        conflict_note = (
            f" [CONFLICT WARNING: input data simultaneously satisfies {', '.join(matched_codes)}; "
            "priority order X>N>A>M was applied to pick one — check the input for contradictions.]"
        )

    if x_ok:
        sub = _exhaustion_subscript(markers)
        rationale = f"X: exhaustion criteria met ({x_detail}). {sub.rationale}{conflict_note}"
        return SlotResult(code="X", subscript=sub.code, rationale=rationale)
    if n_ok:
        return SlotResult(code="N", rationale=f"N: naive criteria met ({n_detail}).{conflict_note}")
    if a_ok:
        return SlotResult(code="A", rationale=f"A: activated criteria met ({a_detail}).{conflict_note}")
    if m_ok:
        return SlotResult(code="M", rationale=f"M: memory criteria met ({m_detail}).{conflict_note}")

    return SlotResult(
        code="",
        rationale=(
            "No differentiation state assigned: insufficient marker evidence to confirm N, A, M, or X. "
            f"(X check: {x_detail} | N check: {n_detail} | A check: {a_detail} | M check: {m_detail})"
        ),
    )


VALID_ANTIGEN_STATUSES = {"", "+", "0"}


def classify_antigen(status: str, note: str = "") -> SlotResult:
    """Antigen status is never inferred from markers — user assertion only."""
    status = (status or "").strip()
    if status not in VALID_ANTIGEN_STATUSES:
        raise ValueError(f"Invalid antigen_status '{status}'; must be '+', '0', or '' (blank).")

    if status == "":
        return SlotResult(code="", rationale="Antigen status not asserted by user (no claim made).")

    justification = note.strip() if note else "(no justification note provided)"
    meaning = "persistent antigen" if status == "+" else "antigen cleared / not relevant"
    return SlotResult(
        code=status,
        rationale=f"'{status}' ({meaning}) — user-asserted. Justification: {justification}",
    )
