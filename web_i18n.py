"""UI-chrome translations for the Flask web app only.

This is presentational text for page layout, navigation, form labels, and
buttons — not the nomenclature classification wording (that lives alongside
the logic in nomenclature/slots.py and nomenclature/assemble.py, via each
function's `lang` argument). Two languages are supported: "ko" (default) and
"en".
"""
from __future__ import annotations

DEFAULT_LANG = "ko"
SUPPORTED_LANGS = ("ko", "en")

UI_TEXT = {
    "ko": {
        "site_title": "T세포 모듈형 명명법 생성기",
        "nav_single": "단일 population",
        "nav_batch": "배치 CSV",
        "heading": "T세포 모듈형 명명법 생성기",
        "subtitle": (
            "독립적으로 근거가 확인된 슬롯들로부터 이름을 조합합니다 — Lineage · Function · "
            "Migration · Differentiation state · Antigen status. 마커 근거가 없는 슬롯은 "
            "추측하지 않고 비워 둡니다."
        ),
        "footer": (
            "Choi Lab · Masopust et al., \"Guidelines for T cell nomenclature\", "
            "Nat Rev Immunol (2026) 기반"
        ),
        # single-record form
        "section_identity": "Population 식별 정보",
        "label_label": "샘플 / population 라벨",
        "label_location": "조직 / 위치",
        "label_lineage": "Lineage",
        "label_function": "Function",
        "placeholder_optional": "선택 사항",
        "placeholder_location": "예: Liver",
        "placeholder_lineage": "예: CD8+",
        "placeholder_function": "예: TH1",
        "marker_choice_pos": "+",
        "marker_choice_neg": "-",
        "marker_choice_na": "측정 안 됨",
        "section_migration_sub": "이동 아래첨자 (migration이 'D'일 때만 적용)",
        "note_migration_sub": "마커로부터 추론되지 않습니다 — 추가 분석적 근거가 명확히 있을 때만 지정하세요.",
        "label_evidence_code": "근거 코드",
        "option_none": "(없음)",
        "option_b": "B — 혈액에서만 확인",
        "option_w": "W — 광범위 재순환 확인됨",
        "option_r": "R — 조직 상주성 확인됨",
        "label_justification": "근거 / 정당화",
        "placeholder_migration_note": "예: Parabiosis로 조직 상주성 확인",
        "section_diff_override": "Differentiation 재정의",
        "note_diff_override": "Anergic(G)은 기능적으로 정의되며 마커로 읽을 수 없습니다 — 해당하는 경우 근거와 함께 여기서 지정하세요.",
        "label_override_code": "재정의 코드",
        "placeholder_override_code": "예: G",
        "section_antigen": "항원(Antigen) 상태",
        "note_antigen": "마커로부터 추론되지 않습니다 — 실험 설계에 따라 직접 판단해 입력하세요.",
        "antigen_not_asserted": "주장하지 않음",
        "antigen_persistent": "+ 지속",
        "antigen_cleared": "0 소실",
        "placeholder_antigen_note": "예: 만성 LCMV 감염 모델",
        "btn_generate": "명명법 생성",
        "result_lineage": "Lineage",
        "result_function": "Function",
        "result_migration": "Migration",
        "result_differentiation": "Differentiation",
        "result_antigen": "Antigen 상태",
        "result_not_given": "(입력 없음)",
        "result_not_assigned": "(할당되지 않음)",
        "result_not_asserted": "(주장되지 않음)",
        "rationale_summary": "왜 이렇게 나왔나 (감사 추적 — 신뢰하기 전에 확인하세요)",
        # hero "quick start" card (index page)
        "hero_what_title": "이 도구는 무엇을 하나요?",
        "hero_what_body": (
            "유세포분석(flow cytometry) 마커의 +/-/미측정 값을 입력하면, 근거가 있는 슬롯만 "
            "채워서 T세포 이름을 조합해줍니다. 마커가 없으면 추측하지 않고 비워 둡니다 — "
            "그래서 아래 감사 추적에서 '왜 이렇게 판정됐는지'를 항상 확인할 수 있습니다."
        ),
        "hero_try_title": "T세포 마커를 잘 모르신다면? 예시로 먼저 체험해보세요",
        "hero_example_naive": "예시 1 불러오기 — Naive CD4+",
        "hero_example_naive_desc": "→ 결과: CD4+ TSN",
        "hero_example_exhausted": "예시 2 불러오기 — 소진 전구체 CD8+",
        "hero_example_exhausted_desc": "→ 결과: CD8+ TDRXp+",
        "hero_example_hint": "버튼을 누르면 아래 폼에 값이 자동으로 채워지고 결과와 판정 근거가 바로 나타납니다. 각 마커 옆의 설명(마우스를 올리면 보임)을 참고해 직접 값을 바꿔보며 결과가 어떻게 달라지는지 실험해보세요.",
        # batch page
        "batch_heading": "배치 CSV 모드",
        "batch_intro_pre": "샘플/population CSV를 업로드하면 ",
        "batch_intro_post": " 컬럼이 추가된 동일한 파일을 받을 수 있습니다. 어떤 컬럼을 써야 할지 모르시겠다면, 먼저 ",
        "batch_template_link": "템플릿을 다운로드",
        "batch_template_suffix": "해서 예상 형식과 두 가지 예시를 확인해보세요.",
        "batch_choose_file": "CSV 파일 선택…",
        "batch_submit": "처리 후 다운로드",
        "batch_columns_summary": "컬럼 참고",
        "batch_columns_intro": "모든 컬럼은 선택 사항입니다 (대소문자, 공백/밑줄/하이픈 무시하고 매칭). 없는 마커 컬럼은 모든 행에서 '측정 안 됨'으로 처리됩니다.",
        "batch_columns_markers": "마커 컬럼:",
        "batch_columns_meta": "메타데이터 컬럼:",
        "batch_no_file": "업로드할 CSV 파일을 선택해주세요.",
        "lang_toggle_ko": "한국어",
        "lang_toggle_en": "English",
    },
    "en": {
        "site_title": "T cell modular nomenclature generator",
        "nav_single": "Single population",
        "nav_batch": "Batch CSV",
        "heading": "T cell modular nomenclature generator",
        "subtitle": (
            "Composes a name from independently-evidenced slots — Lineage · Function · "
            "Migration · Differentiation state · Antigen status. A slot with no supporting "
            "marker data is left blank, never guessed."
        ),
        "footer": (
            "Choi Lab · based on Masopust et al., \"Guidelines for T cell nomenclature\", "
            "Nat Rev Immunol (2026)"
        ),
        "section_identity": "Population identity",
        "label_label": "Sample / population label",
        "label_location": "Tissue / location",
        "label_lineage": "Lineage",
        "label_function": "Function",
        "placeholder_optional": "optional",
        "placeholder_location": "e.g. Liver",
        "placeholder_lineage": "e.g. CD8+",
        "placeholder_function": "e.g. TH1",
        "marker_choice_pos": "+",
        "marker_choice_neg": "-",
        "marker_choice_na": "not measured",
        "section_migration_sub": "Migration subscript (only applies if migration comes out \"D\")",
        "note_migration_sub": "Never inferred from markers — only set this if you have explicit additional assay evidence.",
        "label_evidence_code": "Evidence code",
        "option_none": "(none)",
        "option_b": "B — blood only",
        "option_w": "W — widespread recirculation confirmed",
        "option_r": "R — tissue residency confirmed",
        "label_justification": "Justification",
        "placeholder_migration_note": "e.g. Parabiosis confirms tissue residency",
        "section_diff_override": "Differentiation override",
        "note_diff_override": "Anergic (G) is functionally defined and can't be read off markers — set it here with a justification if applicable.",
        "label_override_code": "Override code",
        "placeholder_override_code": "e.g. G",
        "section_antigen": "Antigen status",
        "note_antigen": "Never inferred from markers — depends on your experimental design.",
        "antigen_not_asserted": "not asserted",
        "antigen_persistent": "+ persistent",
        "antigen_cleared": "0 cleared",
        "placeholder_antigen_note": "e.g. Chronic LCMV infection model",
        "btn_generate": "Generate nomenclature",
        "result_lineage": "Lineage",
        "result_function": "Function",
        "result_migration": "Migration",
        "result_differentiation": "Differentiation",
        "result_antigen": "Antigen status",
        "result_not_given": "(not given)",
        "result_not_assigned": "(not assigned)",
        "result_not_asserted": "(not asserted)",
        "rationale_summary": "Why (audit trail — check this before trusting the name)",
        "hero_what_title": "What does this tool do?",
        "hero_what_body": (
            "Enter flow-cytometry marker calls (+/-/not measured) and it composes a T cell "
            "name from only the slots that have direct evidence — nothing is guessed. "
            "That's why the audit trail below always explains exactly why each part of the "
            "name was called the way it was."
        ),
        "hero_try_title": "New to T cell markers? Try a worked example first",
        "hero_example_naive": "Load example 1 — Naive CD4+",
        "hero_example_naive_desc": "→ result: CD4+ TSN",
        "hero_example_exhausted": "Load example 2 — Exhausted progenitor CD8+",
        "hero_example_exhausted_desc": "→ result: CD8+ TDRXp+",
        "hero_example_hint": "Clicking a button fills in the form below and shows the result plus its audit trail right away. Hover a marker for what it means, then try changing values yourself to see how the result changes.",
        "batch_heading": "Batch CSV mode",
        "batch_intro_pre": "Upload a CSV of samples/populations and get back the same file with ",
        "batch_intro_post": " columns appended. Not sure what columns to use? ",
        "batch_template_link": "Download the template",
        "batch_template_suffix": " first to see the expected layout and two worked examples.",
        "batch_choose_file": "Choose a CSV file…",
        "batch_submit": "Process & download",
        "batch_columns_summary": "Column reference",
        "batch_columns_intro": "All columns are optional (matched case-insensitively, ignoring spaces/underscores/hyphens). Missing marker columns are treated as not-measured for every row.",
        "batch_columns_markers": "Marker columns:",
        "batch_columns_meta": "Metadata columns:",
        "batch_no_file": "Please choose a CSV file to upload.",
        "lang_toggle_ko": "한국어",
        "lang_toggle_en": "English",
    },
}


def get_lang(requested: str | None) -> str:
    return requested if requested in SUPPORTED_LANGS else DEFAULT_LANG
