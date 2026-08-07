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
        "nav_single": "단일 샘플 입력",
        "nav_batch": "CSV 일괄 처리",
        "heading": "T세포 모듈형 명명법 생성기",
        "subtitle": (
            "Lineage · Function · Migration · Differentiation state · Antigen status, "
            "이렇게 근거가 확인된 항목만 조합해서 이름을 만듭니다. "
            "마커 근거가 없는 항목은 추측하지 않고 그냥 비워 둡니다."
        ),
        "footer": (
            "Choi Lab · Masopust 등, \"Guidelines for T cell nomenclature\", "
            "Nat Rev Immunol (2026) 기준"
        ),
        "feature_marker": "🔬 13개 마커로 자동 판정",
        "feature_rationale": "📝 판정 근거를 항목별로 항상 표시",
        "feature_batch": "📄 단일 입력 + CSV 일괄 처리",
        "feature_i18n": "🌐 한국어 / English 지원",
        # single-record form
        "section_identity": "샘플 기본 정보",
        "label_label": "샘플 이름",
        "label_location": "조직 / 위치",
        "label_lineage": "Lineage",
        "label_function": "Function",
        "placeholder_optional": "선택 입력",
        "placeholder_location": "예: Liver",
        "placeholder_lineage": "예: CD8+",
        "placeholder_function": "예: TH1",
        "marker_choice_pos": "+",
        "marker_choice_neg": "-",
        "marker_choice_na": "측정 안 됨",
        "section_migration_override": "Migration 상태 직접 지정 (선택)",
        "note_migration_override": (
            "아래 마커만으로 S 또는 D를 확정하기 어려우면 이 항목은 기본적으로 비워 둡니다. "
            "논문에서도 migration을 선택 항목으로 다루기 때문에, 근거가 부족하다고 해서 "
            "'U'를 자동으로 채우지는 않습니다. 'U'라고 명시하고 싶거나 마커 판정과 다른 "
            "S/D를 직접 주장하고 싶을 때만 여기서 지정해 주세요."
        ),
        "label_migration_override_code": "Migration 코드",
        "option_migration_none": "(직접 지정하지 않음 — 마커 판정 결과만 사용)",
        "option_migration_s": "S — 2차 림프 기관 진입 가능",
        "option_migration_d": "D — 파종성",
        "option_migration_u": "U — 이동 상태 불명 (명시적으로 주장)",
        "section_migration_sub": "Migration 아래첨자",
        "note_migration_sub": (
            "마커만으로는 판단할 수 없는 항목입니다. 추가로 확인된 분석적 근거가 있을 때만 "
            "지정해 주세요. 어떤 조합이 가능한지는 위 Migration 판정 결과에 따라 달라집니다 — "
            "B는 S/D/U 어디에나, W는 S/D에만, R은 D에만 붙일 수 있습니다."
        ),
        "label_evidence_code": "근거 코드",
        "option_none": "(없음)",
        "option_b": "B — 혈액에서만 확인됨",
        "option_w": "W — 광범위 재순환 확인됨",
        "option_r": "R — 조직 상주성 확인됨",
        "label_justification": "근거 설명",
        "placeholder_migration_note": "예: parabiosis로 조직 상주성 확인",
        "section_diff_override": "Differentiation 상태 직접 지정 (선택)",
        "note_diff_override": (
            "Anergic(G)은 기능적으로 정의되는 상태라 마커만으로는 판단할 수 없습니다. "
            "해당된다고 판단되면 근거와 함께 여기서 직접 지정해 주세요."
        ),
        "label_override_code": "지정할 코드",
        "placeholder_override_code": "예: G",
        "section_antigen": "Antigen 상태",
        "note_antigen": "마커만으로는 알 수 없는 항목입니다. 실험 설계를 바탕으로 직접 판단해서 입력해 주세요.",
        "antigen_not_asserted": "주장 안 함",
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
        "result_not_assigned": "(판정 안 됨)",
        "result_not_asserted": "(주장 안 됨)",
        "rationale_summary": "이렇게 판정된 이유 (결과를 그대로 믿지 말고 확인해 보세요)",
        # hero "quick start" card (index page)
        "hero_what_title": "이 도구는 무엇을 하나요?",
        "hero_what_body": (
            "유세포분석(flow cytometry) 마커 값을 +, -, 미측정 중 하나로 입력하면, "
            "근거가 확인된 항목만 채워서 T세포 이름을 만들어 줍니다. 근거가 없는 항목은 "
            "추측하지 않고 비워 두기 때문에, 아래에서 '왜 이렇게 판정됐는지'를 항상 직접 "
            "확인하실 수 있습니다."
        ),
        "hero_try_title": "T세포 마커를 잘 모르신다면? 예시로 먼저 체험해 보세요",
        "hero_example_naive": "예시 1 불러오기 — Naive CD4+",
        "hero_example_naive_desc": "→ 결과: CD4+ TSN",
        "hero_example_exhausted": "예시 2 불러오기 — 소진 전구체 CD8+",
        "hero_example_exhausted_desc": "→ 결과: CD8+ TDRXp+",
        "hero_example_hint": (
            "버튼을 누르면 아래 폼에 값이 자동으로 채워지고 결과와 판정 근거가 바로 나타납니다. "
            "마커 이름에 마우스를 올리면 설명이 뜨니 참고해서, 값을 직접 바꿔가며 결과가 어떻게 "
            "달라지는지 실험해 보세요."
        ),
        "citation": "출처: Masopust 등, “Guidelines for T cell nomenclature”, Nat Rev Immunol (2026)",
        "btn_reset": "초기화",
        # batch page
        "batch_heading": "CSV 일괄 처리",
        "batch_intro_pre": "샘플 목록이 담긴 CSV를 업로드하면 ",
        "batch_intro_post": " 컬럼이 추가된 파일을 받을 수 있습니다. 어떤 컬럼을 써야 할지 모르겠다면 먼저 ",
        "batch_template_link": "템플릿을 다운로드",
        "batch_template_suffix": "해서 형식과 예시 2개를 먼저 확인해 보세요.",
        "batch_choose_file": "CSV 파일 선택…",
        "batch_submit": "처리 후 다운로드",
        "batch_columns_summary": "컬럼 설명",
        "batch_columns_intro": (
            "모든 컬럼은 선택 사항입니다 (대소문자나 공백·밑줄·하이픈 차이는 무시하고 인식합니다). "
            "마커 컬럼이 없으면 모든 행에서 '측정 안 됨'으로 처리됩니다."
        ),
        "batch_columns_markers": "마커 컬럼:",
        "batch_columns_meta": "메타데이터 컬럼:",
        "batch_no_file": "업로드할 CSV 파일을 선택해 주세요.",
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
        "feature_marker": "🔬 Auto-classifies from 13 markers",
        "feature_rationale": "📝 Rationale always shown per slot",
        "feature_batch": "📄 Single entry + batch CSV",
        "feature_i18n": "🌐 Korean / English",
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
        "section_migration_override": "Migration override (optional)",
        "note_migration_override": "If the markers below don't clearly support S or D, this slot is left blank by default — per the paper, migration is an optional descriptor, and lack of evidence doesn't force a 'U'. Only set this if you want to explicitly assert 'U' (or an S/D that differs from the markers) as a claim.",
        "label_migration_override_code": "Migration code",
        "option_migration_none": "(no override — use marker evidence only)",
        "option_migration_s": "S — can enter secondary lymphoid organs",
        "option_migration_d": "D — disseminated",
        "option_migration_u": "U — migration unknown (explicit claim)",
        "section_migration_sub": "Migration subscript",
        "note_migration_sub": "Never inferred from markers — only set this if you have explicit additional assay evidence. Which combinations are valid depends on the Migration result above: B applies to S/D/U, W applies to S/D, R applies to D only.",
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
        "citation": "Source: Masopust et al., “Guidelines for T cell nomenclature”, Nat Rev Immunol (2026)",
        "btn_reset": "Reset",
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
