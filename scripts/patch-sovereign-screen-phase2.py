#!/usr/bin/env python3
"""Sovereign Screen — Phase 2 patch (screening completeness).

Additive changes only — no existing regime call changes.

  P2.1  New Q_GPAI + AI Act Art. 51+ downstream-user rule
  P2.2  New Q_BIOMETRIC → uses_high_risk_ai (Annex III item 1)
  P2.3  New Q_EMPAI     → uses_high_risk_ai (Annex III item 4)
  P2.4  Wire company_size → DORA Art. 16 simplified regime rule
  P2.5  Wire special_category_data → GDPR DPIA/DPO advisory (EU+UK)
  P2.6  Wire company_size → UK Op Res proportionality advisory
  P2.7  Wire eu_member_state_count → GDPR one-stop-shop advisory
  P2.8  Wire data_volume_band → DPIA / Art. 30 records advisory

Idempotent. Same guards as Phase 1: json_safety_check + js_structure_check.

Deploys to sovereign-screen-staging.html only.
"""
import argparse
import json
import pathlib
import re
import sys

FILE = pathlib.Path("/home/user/ltm-core/Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html")

# ---------------------------------------------------------------------------
# EDITS — mutate existing strings (append new applicability rules or facts)
# ---------------------------------------------------------------------------

# P2.4 — DORA regime: add Art. 16 microenterprise rule at the end of
# applicability_rules. Anchor is the very last rule (added in P1.7) ending
# with the "ESAs register" phrase and the closing "\n     ],".
DORA_ANCHOR = (
    r'For an ICT provider serving finance, own designation status as a CTPP is a foundational determination — it changes whether direct ESA oversight applies. Confirm designation status via home NCA and ESAs register.\"}\n     ],'
)
DORA_INSERT = (
    r'For an ICT provider serving finance, own designation status as a CTPP is a foundational determination — it changes whether direct ESA oversight applies. Confirm designation status via home NCA and ESAs register.\"}'
    r',\n       {when:{all:[{fact:\"entity_role\",op:\"eq\",value:\"financial_entity\"},{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"company_size\",op:\"eq\",value:\"micro\"}]},grade:\"advisory\",rationale:\"Microenterprise (defined as <10 staff AND ≤ EUR 2m turnover or balance-sheet total, per Commission Recommendation 2003/361/EC): DORA Art. 16 provides a simplified ICT risk-management framework. Core duties (ICT risk management, major-incident reporting, third-party ICT risk, business continuity) still apply but at proportionate scale. Governance, board involvement, and full RTS/ITS-driven controls are relaxed.\"}'
    r'\n     ],'
)

# P2.6 — UK Op Res: add proportionality rule. Anchor is the current single
# rule ending with "PS21/3, SS2/21)."}] (no newline before ]).
UKOPRES_ANCHOR = (
    r'FCA/PRA-regulated firms and FMIs must meet UK operational-resilience and outsourcing/third-party-risk rules (PS21/3, SS2/21).\"}]'
)
UKOPRES_INSERT = (
    r'FCA/PRA-regulated firms and FMIs must meet UK operational-resilience and outsourcing/third-party-risk rules (PS21/3, SS2/21).\"}'
    r',{when:{all:[{fact:\"entity_role\",op:\"eq\",value:\"financial_entity\"},{fact:\"establishment_uk\",op:\"is_true\"},{fact:\"company_size\",op:\"in\",value:[\"micro\",\"small\"]}]},grade:\"advisory\",rationale:\"UK operational-resilience expectations are proportionate to firm size and business-model complexity. Smaller firms are not exempt from FCA PS21/3 and PRA SS2/21, but impact-tolerance setting, mapping and scenario-testing scope are calibrated to the firm. Confirm categorisation and expected evidence with your FCA / PRA supervisor.\"}]'
)

# P2.5 / P2.7 / P2.8 — EU GDPR: add Art. 9 special-category rule +
# one-stop-shop rule + large-scale processing rule.
# Anchor: the current single rule ending with "Chapter V transfer
# restrictions and Art. 9 conditions."}].
EUGDPR_ANCHOR = (
    r'Processing personal data with an EU establishment, or targeting/monitoring individuals in the EU, engages GDPR (Art. 3) — including Chapter V transfer restrictions and Art. 9 conditions.\"}]'
)
EUGDPR_INSERT = (
    r'Processing personal data with an EU establishment, or targeting/monitoring individuals in the EU, engages GDPR (Art. 3) — including Chapter V transfer restrictions and Art. 9 conditions.\"}'
    # P2.5 — Art. 9 special-category → DPIA/DPO
    r',{when:{all:[{fact:\"processes_personal_data\",op:\"is_true\"},{fact:\"special_category_data\",op:\"is_true\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"},{fact:\"data_subjects_geo\",op:\"includes_any\",value:[\"EU\"]}]}]},grade:\"needs_legal_review\",rationale:\"Processing special-category personal data (GDPR Art. 9(1)) requires an Art. 9(2) condition in addition to an Art. 6 lawful basis, plus supplementary safeguards. Large-scale processing typically triggers a Data Protection Impact Assessment (Art. 35(3)(b)) and Data Protection Officer designation (Art. 37(1)(c)). See EDPB Guidelines on DPIA (WP 248 rev.01) and your national DPA lists.\"}'
    # P2.7 — one-stop-shop
    r',{when:{all:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"eu_member_state_count\",op:\"gte\",value:2},{fact:\"processes_personal_data\",op:\"is_true\"}]},grade:\"advisory\",rationale:\"Cross-border processing across two or more EU Member States engages the one-stop-shop mechanism (GDPR Art. 56): identify your lead supervisory authority via main-establishment analysis. Cooperation and consistency procedures apply under Arts. 60–63. See EDPB Guidelines 8/2022 on identifying a controller or processor lead supervisory authority.\"}'
    # P2.8 — large-scale processing → DPIA / Art. 30 / DPO
    r',{when:{all:[{fact:\"processes_personal_data\",op:\"is_true\"},{fact:\"data_volume_band\",op:\"in\",value:[\"1m_10m\",\"over_10m\"]},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"},{fact:\"data_subjects_geo\",op:\"includes_any\",value:[\"EU\"]}]}]},grade:\"advisory\",rationale:\"Large-scale personal-data processing (typically >1 million records) engages Art. 30 records-of-processing at proportionate scale, is likely to require a DPIA under Art. 35 (WP 248 rev.01 large-scale threshold), and where core activities involve regular and systematic monitoring, triggers a DPO under Art. 37(1)(b).\"}]'
)

# P2.5 mirror for UK GDPR — Art. 9 special category (UK)
UKGDPR_ANCHOR = (
    r'Processing personal data with a UK establishment, or targeting/monitoring individuals in the UK, engages the UK GDPR / DPA 2018 (and PECR). Track phased DUAA 2025 changes.\"}]'
)
UKGDPR_INSERT = (
    r'Processing personal data with a UK establishment, or targeting/monitoring individuals in the UK, engages the UK GDPR / DPA 2018 (and PECR). Track phased DUAA 2025 changes.\"}'
    r',{when:{all:[{fact:\"processes_personal_data\",op:\"is_true\"},{fact:\"special_category_data\",op:\"is_true\"},{any:[{fact:\"establishment_uk\",op:\"is_true\"},{fact:\"offers_services_uk\",op:\"is_true\"},{fact:\"data_subjects_geo\",op:\"includes_any\",value:[\"UK\"]}]}]},grade:\"needs_legal_review\",rationale:\"Under UK GDPR / DPA 2018, processing special-category data requires an Art. 9(2) condition. For most conditions, a corresponding Schedule 1 DPA 2018 condition and appropriate policy document are also required (e.g., substantial-public-interest condition). Large-scale processing typically triggers DPIA and DPO obligations. See ICO guidance on special-category data.\"}]'
)

# P2.1 — EU AI Act: add two Art. 51+ GPAI rules (downstream user + provider)
EUAIACT_ANCHOR = (
    r'Non-high-risk AI may still carry transparency and/or GPAI obligations depending on the system. Confirm classification.\"}\n     ],'
)
EUAIACT_INSERT = (
    r'Non-high-risk AI may still carry transparency and/or GPAI obligations depending on the system. Confirm classification.\"}'
    # GPAI downstream user
    r',\n       {when:{all:[{fact:\"gpai_role\",op:\"eq\",value:\"downstream_user\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"advisory\",rationale:\"Downstream users of general-purpose AI (GPAI) models placed on the EU market: primary Chapter V obligations (Arts. 51–56) fall on the GPAI provider, but downstream users must integrate the provider transparency documentation, respect copyright policy, and ensure their use case does not turn a general model into an Annex III high-risk system without corresponding controls.\"}'
    # GPAI provider
    r',\n       {when:{all:[{fact:\"gpai_role\",op:\"eq\",value:\"provider\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"applies\",rationale:\"Providers of GPAI models placed on the EU market are subject to Chapter V of the AI Act (Arts. 51–56): technical documentation, transparency to downstream deployers, EU copyright compliance policy, publication of a training-data summary, and cooperation with the AI Office. Providers of systemic-risk GPAI (compute threshold under Art. 51(2)) additionally owe model-evaluation, adversarial-testing, cybersecurity and serious-incident-reporting duties. Applies from 2 August 2025 for GPAI provisions.\"}'
    # GPAI deployer/integrator
    r',\n       {when:{all:[{fact:\"gpai_role\",op:\"eq\",value:\"deployer_integrator\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"advisory\",rationale:\"Firms embedding third-party GPAI into products they place on the EU market may be treated as providers of the resulting AI system when they place it under their own name (Art. 25). Assess whether provider obligations attach to the integrated system, in addition to the base-model provider obligations.\"}'
    r'\n     ],'
)

# Add gpai_role to the facts array (hygiene)
FACTS_ANCHOR = r'{key:\"ict_concentration_risk\"},{key:\"us_dpf_cert_status\"}\n  ],'
FACTS_INSERT = r'{key:\"ict_concentration_risk\"},{key:\"us_dpf_cert_status\"},{key:\"gpai_role\"}\n  ],'

EDITS = [
    ("P2.4 DORA Art. 16 microenterprise rule",        (DORA_ANCHOR, DORA_INSERT)),
    ("P2.6 UK Op Res proportionality rule",           (UKOPRES_ANCHOR, UKOPRES_INSERT)),
    ("P2.5 + P2.7 + P2.8 EU GDPR rules",              (EUGDPR_ANCHOR, EUGDPR_INSERT)),
    ("P2.5 UK GDPR special-category rule",            (UKGDPR_ANCHOR, UKGDPR_INSERT)),
    ("P2.1 EU AI Act GPAI Art. 51+ rules",            (EUAIACT_ANCHOR, EUAIACT_INSERT)),
    ("Facts array +gpai_role",                        (FACTS_ANCHOR, FACTS_INSERT)),
]

# ---------------------------------------------------------------------------
# INSERTIONS — new questions after Q_AI (before Q_CTP)
# ---------------------------------------------------------------------------
# Anchor: Q_AI's "None of these" closing option + newline + Q_CTP opening
QAI_TAIL_ANCHOR = (
    r'{label:\"None of these\",fact_value:{}}]},\n    {id:\"Q_CTP\"'
)
QAI_TAIL_INSERT = (
    r'{label:\"None of these\",fact_value:{}}]}'
    # Q_BIOMETRIC (single_select Yes/No so fact_value merge OR-s correctly)
    r',\n    {id:\"Q_BIOMETRIC\", category:\"technology_use\", tier:1, answer_type:\"single_select\", '
    r'text:\"Do you use biometric identification or categorisation of natural persons (facial recognition, fingerprint, voice) for KYC, authentication, fraud prevention or workforce access?\", '
    r'hint:\"Biometric identification of persons is Annex III item 1 of the EU AI Act — high-risk regardless of business function.\", '
    r'options:[{label:\"Yes\",fact_value:{uses_high_risk_ai:true}},{label:\"No\",fact_value:{}}]}'
    # Q_EMPAI (single_select Yes/No)
    r',\n    {id:\"Q_EMPAI\", category:\"technology_use\", tier:1, answer_type:\"single_select\", '
    r'text:\"Do you use AI or automated decision systems in recruitment, work allocation, promotion, or performance evaluation of staff?\", '
    r'hint:\"Employment-related AI is Annex III item 4 of the EU AI Act — high-risk regardless of business function.\", '
    r'options:[{label:\"Yes\",fact_value:{uses_high_risk_ai:true}},{label:\"No\",fact_value:{}}]}'
    # Q_GPAI (single_select role)
    r',\n    {id:\"Q_GPAI\", category:\"technology_use\", tier:1, answer_type:\"single_select\", '
    r'shown_if:{any:[{fact:\"uses_high_risk_ai\",op:\"is_true\"},{fact:\"uses_other_ai\",op:\"is_true\"}]}, '
    r'text:\"Do you use or provide any general-purpose AI (GPAI) model in production?\", '
    r'hint:\"GPAI = large-scale foundation models such as LLMs or image generators. Different EU AI Act obligations attach depending on your role (Chapter V, Arts. 51–56).\", '
    r'options:['
    r'{label:\"Yes — we deploy GPAI models built by third parties (downstream user)\",fact_value:{gpai_role:\"downstream_user\"}},'
    r'{label:\"Yes — we develop and provide our own GPAI models\",fact_value:{gpai_role:\"provider\"}},'
    r'{label:\"Yes — we embed / integrate third-party GPAI into products or services we sell\",fact_value:{gpai_role:\"deployer_integrator\"}},'
    r'{label:\"No — we do not use GPAI\",fact_value:{gpai_role:\"none\"}}]}'
    # then the original Q_CTP marker
    r',\n    {id:\"Q_CTP\"'
)

INSERTIONS = [
    ("Q_BIOMETRIC / Q_EMPAI / Q_GPAI questions", QAI_TAIL_ANCHOR, QAI_TAIL_INSERT, 'Q_BIOMETRIC'),
]


def json_safety_check(data: str) -> None:
    for tag in ('__bundler/manifest', '__bundler/template', '__bundler/ext_resources'):
        m = re.search(r'<script type="'+re.escape(tag)+r'">', data)
        if not m:
            continue
        end = data.find('</script>', m.end())
        payload = data[m.end():end]
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            ctx = payload[max(0, e.pos-80):e.pos+80]
            raise SystemExit(
                f"\n  ✗ {tag} JSON invalid after Phase 2 patch: {e}\n"
                f"    context: {ctx!r}\n"
                f"    REFUSING TO SAVE.")


def js_structure_check(data: str) -> None:
    m = re.search(r'<script type="__bundler/template">', data)
    if not m:
        return
    end = data.find('</script>', m.end())
    payload = data[m.end():end]
    decoded = json.loads(payload)
    text = decoded if isinstance(decoded, str) else json.dumps(decoded)

    for pat, msg in [
        (r'options:\[\s*,', "empty leading comma in options:[]"),
        (r'options:\[\s*\]', "empty options:[] array"),
        (r'applicability_rules:\[\s*,', "empty leading comma in applicability_rules"),
        (r'applicability_rules:\[\s*\]', "empty applicability_rules"),
    ]:
        m2 = re.search(pat, text)
        if m2:
            ctx = text[max(0, m2.start()-80):m2.end()+80]
            raise SystemExit(
                f"\n  ✗ JS structure defect: {msg}\n    at: {ctx!r}\n    REFUSING TO SAVE.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = FILE.read_text(encoding="utf-8")
    before_len = len(data)
    applied = 0

    print("--- EDITS ---")
    for label, (old, new) in EDITS:
        if old not in data:
            if new in data:
                print(f"  = {label}: already applied")
                continue
            print(f"  ! {label}: OLD NOT FOUND")
            continue
        data = data.replace(old, new, 1)
        applied += 1
        print(f"  ✓ {label}")

    print("\n--- INSERTIONS ---")
    for label, anchor, replacement, marker in INSERTIONS:
        if marker in data:
            print(f"  = {label}: already present ({marker} found)")
            continue
        if anchor not in data:
            print(f"  ! {label}: ANCHOR NOT FOUND")
            continue
        data = data.replace(anchor, replacement, 1)
        applied += 1
        print(f"  ✓ {label}")

    print()
    json_safety_check(data)
    print("  ✓ all bundler payloads parse as valid JSON")
    js_structure_check(data)
    print("  ✓ no truncated arrays / orphan-comma defects")

    if args.dry_run:
        print("\n  (dry run — file not written)")
        return 0

    FILE.write_text(data, encoding="utf-8")
    print(f"\n  file: {FILE}")
    print(f"  size delta: {len(data) - before_len:+d} bytes  ({applied} edits/insertions)")
    return 0 if applied else 1


if __name__ == "__main__":
    sys.exit(main())
