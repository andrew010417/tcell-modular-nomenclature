"""Marker (and user-assertion) based classification for each nomenclature slot.

Guiding rule throughout this module: a slot is only assigned a definite code
when the evidence explicitly supports it. Missing markers never get guessed
at — they simply leave the slot unassigned ('' or 'U', depending on what the
nomenclature defines for "unknown" in that slot) and the reason is recorded
in the returned rationale so a human can audit the call.

Every classify_* function takes an optional `lang` ("en" default, or "ko")
that only changes the wording of the returned rationale text — the
classification logic itself is identical in both languages. `lang` defaults
to "en" everywhere so existing callers (CLI, CSV batch, tests) are unaffected.
"""
from __future__ import annotations

from typing import Dict, Optional

from .models import SlotResult, get_marker

VALID_MIGRATION_SUBSCRIPTS = {"B", "W", "R"}
_MIGRATION_SUBSCRIPT_LABELS = {
    "en": {
        "B": "blood (isolated from blood, no additional migration evidence)",
        "W": "widespread (non-HEV recirculation confirmed)",
        "R": "resident (tissue residency confirmed, e.g. parabiosis/transplant/TCR-seq comparison)",
    },
    "ko": {
        "B": "혈액 (혈액에서만 분리, 추가 이동 근거 없음)",
        "W": "광범위 (비-HEV 경로 재순환 확인됨)",
        "R": "상주 (조직 상주성 확인됨, 예: parabiosis/이식/TCR-seq 비교)",
    },
}


def classify_migration(markers: Dict[str, str], lang: str = "en") -> SlotResult:
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
        rationale = (
            "S: CD62L+ 및 CCR7+ (둘 다 양성 확인됨) -> 2차 림프 기관으로 진입 가능."
            if lang == "ko"
            else "S: CD62L+ and CCR7+ (both confirmed positive) -> can enter secondary lymphoid organs."
        )
        return SlotResult(code="S", rationale=rationale)

    if cd62l == "-" or ccr7 == "-":
        negs = [n for n, v in (("CD62L", cd62l), ("CCR7", ccr7)) if v == "-"]
        rationale = (
            f"D: {', '.join(negs)} 음성 확인됨 -> 파종성(HEV를 통한 진입 불가)."
            if lang == "ko"
            else f"D: {', '.join(negs)} confirmed negative -> disseminated, cannot enter via HEV."
        )
        return SlotResult(code="D", rationale=rationale)

    if cd62l == "NA" and ccr7 == "NA":
        rationale = (
            "U: CD62L과 CCR7 모두 측정되지 않음."
            if lang == "ko"
            else "U: CD62L and CCR7 both not measured."
        )
        return SlotResult(code="U", rationale=rationale)

    rationale = (
        f"U: S 또는 D를 확정할 근거 부족 (CD62L={cd62l}, CCR7={ccr7}); "
        "일부만 측정되었고 음성으로 확인된 마커가 없음."
        if lang == "ko"
        else (
            f"U: insufficient evidence to confirm S or D (CD62L={cd62l}, CCR7={ccr7}); "
            "only partially measured and neither marker was found negative."
        )
    )
    return SlotResult(code="U", rationale=rationale)


def classify_migration_subscript(
    migration_code: str,
    evidence: Optional[str],
    note: str = "",
    lang: str = "en",
) -> SlotResult:
    """B / W / R subscript. Only applicable when migration == 'D', and only
    ever set from an explicit user assertion + justification — never inferred
    from markers, since the subscript is itself a claim about additional
    assay evidence (parabiosis, recirculation studies, etc.).
    """
    if migration_code != "D":
        if evidence:
            rationale = (
                f"이동 아래첨자 '{evidence}'는 무시됨: migration='D'일 때만 적용 가능 "
                f"(계산된 migration은 '{migration_code}')."
                if lang == "ko"
                else (
                    f"Migration subscript '{evidence}' ignored: only applicable when "
                    f"migration='D' (computed migration was '{migration_code}')."
                )
            )
            return SlotResult(rationale=rationale)
        return SlotResult(rationale="")

    if not evidence:
        rationale = (
            "이동 아래첨자 없음: migration='D'로 확인되었지만 사용자가 명시적인 B/W/R 근거를 "
            "제공하지 않음."
            if lang == "ko"
            else (
                "No migration subscript assigned: migration='D' confirmed, but the user "
                "did not supply explicit B/W/R evidence."
            )
        )
        return SlotResult(rationale=rationale)

    code = evidence.strip().upper()
    if code not in VALID_MIGRATION_SUBSCRIPTS:
        raise ValueError(
            f"Invalid migration_evidence '{evidence}'; must be one of {sorted(VALID_MIGRATION_SUBSCRIPTS)} or empty."
        )

    label = _MIGRATION_SUBSCRIPT_LABELS["ko" if lang == "ko" else "en"][code]
    justification = note.strip() if note else ("(근거 메모 없음)" if lang == "ko" else "(no justification note provided)")
    rationale = (
        f"{code}: 사용자 지정 {label}. 근거: {justification}"
        if lang == "ko"
        else f"{code}: user-asserted {label}. Justification: {justification}"
    )
    return SlotResult(code=code, rationale=rationale)


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


def _exhaustion_subscript(m: Dict[str, str], lang: str = "en"):
    tcf1, slamf6, tim3, cd101 = (get_marker(m, k) for k in ("TCF1", "SLAMF6", "TIM3", "CD101"))
    if tcf1 == "+" and slamf6 == "+" and tim3 == "-":
        rationale = (
            "p: TCF1+, SLAMF6+, TIM3- (전구체 소진, progenitor exhausted)."
            if lang == "ko"
            else "p: TCF1+, SLAMF6+, TIM3- (progenitor exhausted)."
        )
        return SlotResult(code="p", rationale=rationale)
    if tcf1 == "-" and slamf6 == "-" and tim3 == "+" and cd101 == "+":
        rationale = (
            "t: TCF1-, SLAMF6-, TIM3+, CD101+ (말단 소진, terminal exhausted)."
            if lang == "ko"
            else "t: TCF1-, SLAMF6-, TIM3+, CD101+ (terminal exhausted)."
        )
        return SlotResult(code="t", rationale=rationale)
    rationale = (
        f"소진 아래첨자 없음: progenitor(p) 또는 terminal(t) 기준을 모두 충족하지 않음 "
        f"(TCF1={tcf1}, SLAMF6={slamf6}, TIM3={tim3}, CD101={cd101})."
        if lang == "ko"
        else (
            f"no exhaustion subscript: criteria for progenitor (p) or terminal (t) not both met "
            f"(TCF1={tcf1}, SLAMF6={slamf6}, TIM3={tim3}, CD101={cd101})."
        )
    )
    return SlotResult(code="", rationale=rationale)


def classify_differentiation(
    markers: Dict[str, str],
    override: Optional[str] = None,
    override_note: str = "",
    lang: str = "en",
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
        justification = override_note.strip() if override_note else ("(제공되지 않음)" if lang == "ko" else "(none provided)")
        rationale = (
            f"사용자 재정의: differentiation을 '{code}'로 수동 설정함. 근거: {justification}"
            if lang == "ko"
            else f"User override: differentiation manually set to '{code}'. Justification: {justification}"
        )
        return SlotResult(code=code, rationale=rationale)

    x_ok, x_detail = _exhausted_match(markers)
    n_ok, n_detail = _naive_match(markers)
    a_ok, a_detail = _activated_match(markers)
    m_ok, m_detail = _memory_match(markers)

    matched_codes = [c for c, ok in (("X", x_ok), ("N", n_ok), ("A", a_ok), ("M", m_ok)) if ok]
    conflict_note = ""
    if len(matched_codes) > 1:
        conflict_note = (
            f" [충돌 경고: 입력 데이터가 {', '.join(matched_codes)}를 동시에 충족함; "
            "우선순위 X>N>A>M 을 적용해 하나를 선택함 — 입력값의 모순 여부를 확인하세요.]"
            if lang == "ko"
            else (
                f" [CONFLICT WARNING: input data simultaneously satisfies {', '.join(matched_codes)}; "
                "priority order X>N>A>M was applied to pick one — check the input for contradictions.]"
            )
        )

    if x_ok:
        sub = _exhaustion_subscript(markers, lang=lang)
        prefix = f"X: 소진(exhaustion) 기준 충족 ({x_detail})." if lang == "ko" else f"X: exhaustion criteria met ({x_detail})."
        rationale = f"{prefix} {sub.rationale}{conflict_note}"
        return SlotResult(code="X", subscript=sub.code, rationale=rationale)
    if n_ok:
        rationale = (
            f"N: naive 기준 충족 ({n_detail}).{conflict_note}"
            if lang == "ko"
            else f"N: naive criteria met ({n_detail}).{conflict_note}"
        )
        return SlotResult(code="N", rationale=rationale)
    if a_ok:
        rationale = (
            f"A: 활성화(activated) 기준 충족 ({a_detail}).{conflict_note}"
            if lang == "ko"
            else f"A: activated criteria met ({a_detail}).{conflict_note}"
        )
        return SlotResult(code="A", rationale=rationale)
    if m_ok:
        rationale = (
            f"M: memory 기준 충족 ({m_detail}).{conflict_note}"
            if lang == "ko"
            else f"M: memory criteria met ({m_detail}).{conflict_note}"
        )
        return SlotResult(code="M", rationale=rationale)

    rationale = (
        "Differentiation 상태 미할당: N, A, M, X 중 어느 것도 확정할 마커 근거가 부족함. "
        f"(X 확인: {x_detail} | N 확인: {n_detail} | A 확인: {a_detail} | M 확인: {m_detail})"
        if lang == "ko"
        else (
            "No differentiation state assigned: insufficient marker evidence to confirm N, A, M, or X. "
            f"(X check: {x_detail} | N check: {n_detail} | A check: {a_detail} | M check: {m_detail})"
        )
    )
    return SlotResult(code="", rationale=rationale)


VALID_ANTIGEN_STATUSES = {"", "+", "0"}


def classify_antigen(status: str, note: str = "", lang: str = "en") -> SlotResult:
    """Antigen status is never inferred from markers — user assertion only."""
    status = (status or "").strip()
    if status not in VALID_ANTIGEN_STATUSES:
        raise ValueError(f"Invalid antigen_status '{status}'; must be '+', '0', or '' (blank).")

    if status == "":
        rationale = (
            "항원(antigen) 상태는 사용자에 의해 주장되지 않음 (별도 주장 없음)."
            if lang == "ko"
            else "Antigen status not asserted by user (no claim made)."
        )
        return SlotResult(code="", rationale=rationale)

    justification = note.strip() if note else ("(근거 메모 없음)" if lang == "ko" else "(no justification note provided)")
    if lang == "ko":
        meaning = "지속 항원, persistent antigen" if status == "+" else "항원 소실/무관, cleared or not relevant"
        rationale = f"'{status}' ({meaning}) — 사용자 주장. 근거: {justification}"
    else:
        meaning = "persistent antigen" if status == "+" else "antigen cleared / not relevant"
        rationale = f"'{status}' ({meaning}) — user-asserted. Justification: {justification}"
    return SlotResult(code=status, rationale=rationale)
