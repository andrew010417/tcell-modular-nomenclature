"""Data structures shared across the nomenclature package.

Based on the modular T cell nomenclature proposed in:
Masopust et al., "Guidelines for T cell nomenclature", Nat Rev Immunol (2026).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

# Flow-cytometry markers this MVP knows how to interpret. Values are
# categorical: '+' (positive), '-' (negative), 'NA' (not measured).
#
# NOTE (scope): only categorical (+/-/NA) flow gating calls are handled here.
# Continuous scRNA-seq expression values would need a threshold/binarization
# step before they could be fed into classify_* below; that is out of scope
# for this MVP and intentionally left as a future extension point.
MARKER_NAMES = [
    "CD62L", "CCR7",           # migration
    "CD45RA", "CD45RO", "CD95",  # naive/memory
    "CD69", "CD25",            # recent activation
    "PD1", "TOX",              # exhaustion / chronic stimulation
    "TCF1", "SLAMF6", "TIM3", "CD101",  # exhaustion progenitor/terminal
    "KLRG1", "CD127", "CD27",  # activated/memory progenitor-terminal (Ap/At/Mp)
]

# One-line, plain-language meaning for each marker — shown in the CLI so
# users don't need to already have the marker panel memorized.
MARKER_DESCRIPTIONS = {
    "CD62L": "L-selectin. Needed to enter lymph nodes through HEVs.",
    "CCR7": "Chemokine receptor that guides homing to lymph nodes.",
    "CD45RA": "Isoform typically seen on naive (and some terminally-differentiated) T cells.",
    "CD45RO": "Isoform typically seen on memory T cells.",
    "CD95": "Fas. Used to separate true naive cells from stem-cell memory cells.",
    "CD69": "Early marker of recent TCR/cytokine activation.",
    "CD25": "IL-2 receptor alpha chain; induced by recent activation.",
    "PD1": "Inhibitory receptor induced by chronic antigen stimulation.",
    "TOX": "Transcription factor that drives the exhaustion program.",
    "TCF1": "Transcription factor that maintains stem-like/progenitor exhausted cells.",
    "SLAMF6": "Surface marker associated with progenitor exhausted cells.",
    "TIM3": "Surface marker associated with terminally exhausted cells.",
    "CD101": "Surface marker associated with terminally exhausted cells.",
    "KLRG1": "Killer cell lectin-like receptor; marks short-lived terminal effector cells.",
    "CD127": "IL-7 receptor alpha; lost on short-lived effectors, retained on memory-precursor/stem-like cells.",
    "CD27": "Co-stimulatory receptor retained on memory-precursor and stem-cell memory cells.",
}

# Markers grouped by which nomenclature slot they inform, with a short
# blurb per group — used to walk the CLI user through the panel in a
# logical order instead of one flat list of 13 abbreviations.
MARKER_GROUPS = [
    ("Migration (CD62L / CCR7)", ["CD62L", "CCR7"], "Determines S (can enter lymph nodes) vs D (disseminated)."),
    ("Naive vs. memory (CD45RA / CD45RO / CD95)", ["CD45RA", "CD45RO", "CD95"], "Determines the Naive (N) call."),
    ("Recent activation (CD69 / CD25)", ["CD69", "CD25"], "Determines the Activated (A) call, together with PD1/TOX below."),
    ("Chronic stimulation / exhaustion (PD1 / TOX)", ["PD1", "TOX"], "PD1+ and TOX+ together determine the Exhausted (X) call."),
    ("Exhaustion subtype (TCF1 / SLAMF6 / TIM3 / CD101)", ["TCF1", "SLAMF6", "TIM3", "CD101"], "Only relevant if X was called above — splits it into progenitor (p) or terminal (t)."),
    ("Activated/memory subtype (KLRG1 / CD127 / CD27)", ["KLRG1", "CD127", "CD27"], "Refines Activated into progenitor (Ap) / terminal (At), and Memory into stem-cell-like progenitor (Mp)."),
]

# Korean translations of the display-only text above (marker descriptions,
# group titles/notes). Purely presentational — used by the web UI; the
# classification logic in slots.py is keyed on MARKER_NAMES, not on these.
MARKER_DESCRIPTIONS_KO = {
    "CD62L": "L-셀렉틴. HEV를 통해 림프절로 진입하는 데 필요합니다.",
    "CCR7": "림프절로의 귀소(homing)를 유도하는 케모카인 수용체입니다.",
    "CD45RA": "naive T세포(및 일부 최종분화 T세포)에서 흔히 나타나는 이소형입니다.",
    "CD45RO": "memory T세포에서 흔히 나타나는 이소형입니다.",
    "CD95": "Fas. 진성 naive 세포와 줄기세포 유사 memory 세포를 구분합니다.",
    "CD69": "최근 TCR/사이토카인 활성화의 초기 마커입니다.",
    "CD25": "IL-2 수용체 알파 사슬로, 최근 활성화에 의해 유도됩니다.",
    "PD1": "만성 항원 자극에 의해 유도되는 억제성 수용체입니다.",
    "TOX": "소진(exhaustion) 프로그램을 유도하는 전사인자입니다.",
    "TCF1": "줄기세포 유사/전구체 소진 세포를 유지시키는 전사인자입니다.",
    "SLAMF6": "전구체 소진 세포와 관련된 표면 마커입니다.",
    "TIM3": "말단 소진 세포와 관련된 표면 마커입니다.",
    "CD101": "말단 소진 세포와 관련된 표면 마커입니다.",
    "KLRG1": "단명 말단 이펙터 세포에서 발현되는 killer cell lectin-like receptor입니다.",
    "CD127": "IL-7 수용체 알파 사슬. 단명 이펙터 세포에서는 소실되고, memory-precursor·줄기세포 유사 세포에서는 유지됩니다.",
    "CD27": "memory-precursor 세포와 줄기세포 유사 memory 세포에서 유지되는 공동자극 수용체입니다.",
}

MARKER_GROUPS_KO = [
    ("이동 (CD62L / CCR7)", ["CD62L", "CCR7"], "S(림프절 진입 가능)와 D(파종성)를 구분합니다."),
    ("Naive · Memory 구분 (CD45RA / CD45RO / CD95)", ["CD45RA", "CD45RO", "CD95"], "Naive(N) 판정에 사용됩니다."),
    ("최근 활성화 (CD69 / CD25)", ["CD69", "CD25"], "아래 PD1/TOX와 함께 Activated(A) 판정에 사용됩니다."),
    ("만성 자극 / 소진 (PD1 / TOX)", ["PD1", "TOX"], "PD1+이면서 TOX+이면 Exhausted(X)로 판정됩니다."),
    ("소진 하위유형 (TCF1 / SLAMF6 / TIM3 / CD101)", ["TCF1", "SLAMF6", "TIM3", "CD101"], "위에서 X로 판정된 경우에만 의미가 있으며, progenitor(p)와 terminal(t)로 세분화합니다."),
    ("활성화/메모리 하위유형 (KLRG1 / CD127 / CD27)", ["KLRG1", "CD127", "CD27"], "Activated를 progenitor(Ap)·terminal(At)로, Memory를 줄기세포 유사 progenitor(Mp)로 세분화합니다."),
]

MARKER_DESCRIPTIONS_I18N = {"en": MARKER_DESCRIPTIONS, "ko": MARKER_DESCRIPTIONS_KO}
MARKER_GROUPS_I18N = {"en": MARKER_GROUPS, "ko": MARKER_GROUPS_KO}

_POS = {"+", "POS", "POSITIVE", "TRUE", "1"}
_NEG = {"-", "NEG", "NEGATIVE", "FALSE", "0"}
_NA = {"NA", "N/A", "", "UNKNOWN", "U", "NONE", "NOT MEASURED", "NOTMEASURED"}


def normalize_marker_value(value: Optional[str]) -> str:
    """Normalize a raw marker value to one of '+', '-', 'NA'.

    Anything not recognized as clearly positive or negative is treated as
    'NA' (not measured) — silence is a legitimate result, guessing is not.
    """
    if value is None:
        return "NA"
    v = str(value).strip().upper()
    if v in _POS:
        return "+"
    if v in _NEG:
        return "-"
    return "NA"


def get_marker(markers: Dict[str, str], name: str) -> str:
    """Look up a marker's normalized state, defaulting to 'NA' if absent."""
    return normalize_marker_value(markers.get(name))


@dataclass
class SlotResult:
    """Outcome of classifying a single nomenclature slot (or subscript)."""
    code: str = ""
    subscript: str = ""
    rationale: str = ""


@dataclass
class TCellRecord:
    """One sample / cell population to be named.

    `lineage` and `function` are free-text, user-supplied (module slots 1-2).
    `markers` drives the marker-based slots (migration, differentiation).
    The remaining fields are explicit user assertions that are never inferred
    from markers, per the nomenclature's over-claim-avoidance principle.
    """
    label: str = ""
    location: str = ""
    lineage: str = ""
    function: str = ""
    markers: Dict[str, str] = field(default_factory=dict)

    # Migration (S/D/U) is normally marker-derived, but per the paper
    # migration is an optional descriptor: if CD62L/CCR7 don't clearly
    # support S or D, the slot is left blank rather than defaulting to 'U'.
    # 'U' itself is only ever produced via this explicit user assertion
    # (mirroring how 'G' anergic can only be set via differentiation_override).
    migration_override: Optional[str] = None        # 'S' | 'D' | 'U'
    migration_override_note: str = ""

    # Migration subscript validity depends on the migration code (B: S/D/U,
    # W: S/D, R: D only) and is never inferred from markers — only set from
    # explicit user-supplied evidence.
    migration_evidence: Optional[str] = None       # 'B' | 'W' | 'R'
    migration_evidence_note: str = ""

    # Differentiation override lets the user assert 'G' (anergic), which
    # cannot be determined from markers alone.
    differentiation_override: Optional[str] = None
    differentiation_override_note: str = ""

    # Antigen status is never marker-derived — user assertion only.
    antigen_status: str = ""                        # '+' | '0' | ''
    antigen_note: str = ""


@dataclass
class NomenclatureResult:
    nomenclature: str
    label: str
    location: str
    lineage: str
    function: str
    migration: str
    migration_subscript: str
    differentiation: str
    differentiation_subscript: str
    antigen: str
    rationale: str
