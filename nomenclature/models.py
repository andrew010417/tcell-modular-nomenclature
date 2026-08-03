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
]

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

    # Migration subscript (B/W/R) is only applicable when migration == 'D',
    # and only if the user explicitly supplies supporting evidence.
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
