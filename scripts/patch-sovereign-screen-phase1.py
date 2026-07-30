#!/usr/bin/env python3
"""Sovereign Screen — Phase 1 patch (legal defensibility).

Implements the 8 Phase 1 items from docs/SOVEREIGN-SCREEN-ROADMAP.md:

  P1.1  DPF adequacy follow-up + split transfer/jurisdictional rule
  P1.2  Q_SOVOFFER controls follow-up (fix false-pass 100)
  P1.3  Widen Q_HYPER to cover all US-HQ providers
  P1.4  Add UK AI advisory regime + QR_UKAI
  P1.5  Add MiCA regime + QR_MICA
  P1.6  Relabel grades (needs_legal_review → confirm_with_counsel;
                       advisory → informational). IDs kept.
  P1.7  Q_CTP "unknown" escalation on DORA CTP rule
  P1.8  Widen QR_UKCTP shown_if to include ict_provider_to_finance

Idempotent: each edit checks whether it has already been applied.

Deploys to sovereign-screen-staging.html only. Prod (sovereign-screen.html)
is untouched by this script.

JSON-escape reminder: the template payload is JSON-encoded, so only these
escapes are legal: backslash-quote, backslash-backslash, backslash-slash,
backslash-b, backslash-f, backslash-n, backslash-r, backslash-t, and the
backslash-u hex-quad form. NEVER use backslash-apostrophe — the loader
will crash with "Bad escaped character in JSON". The json_safety_check()
guard verifies before writing.
"""
import argparse
import json
import pathlib
import re
import sys

FILE = pathlib.Path("/home/user/ltm-core/Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html")
MARKER = "P1_PATCHED_v1"          # global idempotency marker (unused text)
Q_DPFCERT_MARKER = 'QR_DPFCERT'   # not used; we'll check by Q id presence
DPF_QID = 'Q_DPFCERT'
SOVCTRL_QID = 'QR_SOVCTRL'
UKAI_QID = 'QR_UKAI'
MICA_QID = 'QR_MICA'
UK_AI_REGIME_ID = 'uk_ai_advisory'
MICA_REGIME_ID = 'eu_mica'

# ---------------------------------------------------------------------------
# P1.3 Widen Q_HYPER text
# ---------------------------------------------------------------------------
EDIT_QHYPER = (
    r'text:\"Do you rely on a US-headquartered hyperscaler (AWS, Microsoft Azure, Google Cloud) for material workloads?\"',
    r'text:\"Do you rely on any US-headquartered cloud, SaaS or infrastructure provider for material workloads? Includes AWS, Microsoft Azure, Google Cloud, Oracle Cloud, IBM Cloud, Salesforce / Heroku, Snowflake, Databricks and other US-HQ providers — jurisdiction, not brand, drives CLOUD Act reach.\"',
)

# ---------------------------------------------------------------------------
# P1.2 Q_SOVOFFER "Yes" score 100 -> 70 (baseline claim, no evidence)
# ---------------------------------------------------------------------------
EDIT_QSOVOFFER = (
    r'{label:\"Yes — sovereign offering with controls\",fact_value:{sovereign_offering_status:\"yes\"},score:100}',
    r'{label:\"Yes — sovereign offering, controls claimed\",fact_value:{sovereign_offering_status:\"yes\"},score:70}',
)

# ---------------------------------------------------------------------------
# P1.6 Relabel grades (IDs preserved; only display labels change)
# ---------------------------------------------------------------------------
EDIT_GRADES = (
    r'grades:{applies:\"Applies\", likely_confirm:\"Likely — confirm\", partial:\"Partial\", needs_legal_review:\"Needs legal review\", advisory:\"Advisory\", not_applicable:\"Not applicable\"}',
    r'grades:{applies:\"Applies\", likely_confirm:\"Likely — confirm\", partial:\"Partial applicability\", needs_legal_review:\"Confirm with counsel\", advisory:\"Informational\", not_applicable:\"Not applicable\"}',
)

# ---------------------------------------------------------------------------
# P1.8 Widen QR_UKCTP shown_if
# ---------------------------------------------------------------------------
EDIT_QRUKCTP = (
    r'{id:\"QR_UKCTP\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", shown_if:{all:[{fact:\"entity_role\",op:\"eq\",value:\"financial_entity\"},{fact:\"establishment_uk\",op:\"is_true\"}]}',
    r'{id:\"QR_UKCTP\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", shown_if:{any:[{all:[{fact:\"entity_role\",op:\"eq\",value:\"financial_entity\"},{fact:\"establishment_uk\",op:\"is_true\"}]},{fact:\"entity_role\",op:\"eq\",value:\"ict_provider_to_finance\"}]}',
)

# ---------------------------------------------------------------------------
# P1.1 Split transfer/jurisdictional Rule 2 into DPF-aware rules
# ---------------------------------------------------------------------------
# Current second rule of data_transfer_jurisdiction:
EDIT_TRANSFER_RULE = (
    r'{when:{all:[{fact:\"data_subjects_geo\",op:\"includes_any\",value:[\"EU\"]},{fact:\"data_hosting_location\",op:\"includes_any\",value:[\"US\",\"Other\"]}]},grade:\"needs_legal_review\",rationale:\"EU personal data hosted outside the EEA in a non-adequate jurisdiction needs a valid Chapter V transfer mechanism (adequacy / SCCs + TIA). Note: UK hosting is covered by EU→UK adequacy and is not itself a transfer violation.\"}',
    # Replaced with three rules covering DPF adequacy explicitly:
    r'{when:{all:[{fact:\"data_subjects_geo\",op:\"includes_any\",value:[\"EU\"]},{fact:\"data_hosting_location\",op:\"includes_any\",value:[\"US\"]},{any:[{fact:\"us_dpf_cert_status\",op:\"eq\",value:\"certified\"},{fact:\"us_dpf_cert_status\",op:\"eq\",value:\"eu_only\"}]}]},grade:\"advisory\",rationale:\"EU personal data transferred to a US recipient certified under the EU-US Data Privacy Framework benefits from Commission Implementing Decision (EU) 2023/1795 adequacy (10 July 2023). Reconfirm the recipient DPF certification status periodically — a future CJEU challenge remains possible.\"}'
    r',{when:{all:[{fact:\"data_subjects_geo\",op:\"includes_any\",value:[\"EU\"]},{fact:\"data_hosting_location\",op:\"includes_any\",value:[\"US\"]},{any:[{fact:\"us_dpf_cert_status\",op:\"eq\",value:\"other_mechanism\"},{fact:\"us_dpf_cert_status\",op:\"eq\",value:\"unknown\"}]}]},grade:\"needs_legal_review\",rationale:\"EU personal data hosted in the US without DPF adequacy relies on SCCs / BCRs plus a Transfer Impact Assessment (Schrems II). Confirm the TIA covers current US surveillance law (FISA §702, EO 12333, EO 14086) and that supplementary measures are in place.\"}'
    r',{when:{all:[{fact:\"data_subjects_geo\",op:\"includes_any\",value:[\"EU\"]},{fact:\"data_hosting_location\",op:\"includes_any\",value:[\"Other\"]}]},grade:\"needs_legal_review\",rationale:\"EU personal data hosted outside the EEA in a jurisdiction without an EU adequacy decision needs a valid Chapter V transfer mechanism (adequacy, SCCs, BCRs, derogations) plus a TIA. Note: UK hosting is covered by EU→UK adequacy and is not itself a transfer violation.\"}',
)

# ---------------------------------------------------------------------------
# P1.7 Q_CTP "unknown" escalation — add 2 new applicability rules to DORA
# ---------------------------------------------------------------------------
# Anchor: the last CTP applicability rule, just before its closing "]"
DORA_ANCHOR = r'consult the ESAs register for the current list.\"}\n     ],'
DORA_INSERT = (
    r'consult the ESAs register for the current list.\"}'
    # NEW: unknown for financial entities
    r',\n       {when:{all:[{fact:\"entity_role\",op:\"eq\",value:\"financial_entity\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]},{fact:\"is_or_uses_designated_ctp\",op:\"eq\",value:\"unknown\"}]},grade:\"needs_legal_review\",rationale:\"CTPP dependency status has not been established. For a DORA-in-scope financial entity, whether a critical / important function depends on a designated CTPP is a foundational determination — the classification directly affects concentration-risk treatment, exit-strategy planning and Register of Information obligations. Confirm with counsel and the provider.\"}'
    # NEW: unknown for ICT providers
    r',\n       {when:{all:[{fact:\"entity_role\",op:\"eq\",value:\"ict_provider_to_finance\"},{fact:\"is_or_uses_designated_ctp\",op:\"eq\",value:\"unknown\"}]},grade:\"needs_legal_review\",rationale:\"For an ICT provider serving finance, own designation status as a CTPP is a foundational determination — it changes whether direct ESA oversight applies. Confirm designation status via home NCA and ESAs register.\"}'
    r'\n     ],'
)

# ---------------------------------------------------------------------------
# P1.1 Add Q_DPFCERT question — inserted right after Q_SOVOFFER
# P1.2 Add QR_SOVCTRL follow-up — inserted right after QR_TRANSFER (with new Qs)
# P1.4 Add QR_UKAI question
# P1.5 Add QR_MICA question
# ---------------------------------------------------------------------------
# Insert Q_DPFCERT after Q_SOVOFFER
ANCHOR_QDPF = (
    r'{label:\"Yes — sovereign offering, controls claimed\",fact_value:{sovereign_offering_status:\"yes\"},score:70},'
    r'{label:\"Partially\",fact_value:{sovereign_offering_status:\"partial\"},score:50},'
    r'{label:\"No — standard commercial region\",fact_value:{sovereign_offering_status:\"no\"},score:0},'
    # NOTE: file contains a plain apostrophe (Don't), not backslash-apostrophe.
    r'{label:\"Don' + "'" + r't know\",fact_value:{sovereign_offering_status:\"unknown\"},score:0}]}'
)
# Insert Q_DPFCERT after Q_SOVOFFER (before Q_SIZE).
# Replacement must include the entire ANCHOR content unchanged, followed by
# the new question — since str.replace() overwrites the whole match.
INSERT_QDPF = (
    ANCHOR_QDPF
    + r',\n    {id:\"Q_DPFCERT\", category:\"hosting_and_cloud\", tier:1, answer_type:\"single_select\", allow_not_applicable:true, '
    + r'shown_if:{fact:\"data_hosting_location\",op:\"includes_any\",value:[\"US\"]}, '
    + r'text:\"Is your US-based recipient certified under the EU-US Data Privacy Framework (July 2023 adequacy) and/or covered by the UK-US Data Bridge extension (October 2023)?\", '
    + r'hint:\"DPF certification changes the analysis materially. Recipients on commerce.gov Data Privacy Framework Program list benefit from an EU adequacy decision; UK-established firms can additionally rely on the UK Extension to the DPF.\", '
    + r'options:['
    + r'{label:\"Yes — certified under the EU-US DPF (and UK Extension where UK-relevant)\",fact_value:{us_dpf_cert_status:\"certified\"}},'
    + r'{label:\"Partial — DPF-certified for EU only, not UK Extension\",fact_value:{us_dpf_cert_status:\"eu_only\"}},'
    + r'{label:\"No — relying on SCCs, BCRs or another Chapter V mechanism\",fact_value:{us_dpf_cert_status:\"other_mechanism\"}},'
    + r'{label:\"No mechanism / unknown\",fact_value:{us_dpf_cert_status:\"unknown\"}}]}'
)

# Insert QR_SOVCTRL, QR_UKAI, QR_MICA after QR_DATA_ACT (before Q2_PRIORITY)
ANCHOR_NEW_QS = r'readiness:{regime:\"eu_data_act\",dimension:\"portability_switching\"}},\n    {id:\"Q2_PRIORITY\"'
INSERT_NEW_QS = (
    r'readiness:{regime:\"eu_data_act\",dimension:\"portability_switching\"}}'
    # QR_SOVCTRL — sovereign-controls maturity, tagged to jurisdiction_control
    r',\n    {id:\"QR_SOVCTRL\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", '
    r'shown_if:{fact:\"sovereign_offering_status\",op:\"eq\",value:\"yes\"}, '
    r'text:\"How mature and evidenced are the sovereignty controls behind that offering — contractual protection against extraterritorial disclosure, customer-held encryption keys (HYOK), EU-only operations personnel, sub-processor limits, local operating entity?\", '
    r'readiness:{regime:\"data_transfer_jurisdiction\",dimension:\"jurisdiction_control\"}}'
    # QR_UKAI — UK AI principles alignment
    r',\n    {id:\"QR_UKAI\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", '
    r'shown_if:{all:[{any:[{fact:\"uses_high_risk_ai\",op:\"is_true\"},{fact:\"uses_other_ai\",op:\"is_true\"}]},{fact:\"establishment_uk\",op:\"is_true\"}]}, '
    r'text:\"How aligned is your AI governance with UK principles-based expectations (ICO guidance on AI and data protection, FCA supervisory expectations, PRA/BoE supervisory statement SS1/23 on AI and machine learning in financial services)?\", '
    r'readiness:{regime:\"uk_ai_advisory\",dimension:\"uk_ai_governance\"}}'
    # QR_MICA — MiCA authorisation & governance
    r',\n    {id:\"QR_MICA\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", '
    r'shown_if:{all:[{fact:\"fin_entity_type\",op:\"eq\",value:\"casp_crypto\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]}, '
    r'text:\"How mature is your MiCA authorisation status and governance framework (home-NCA authorisation, prudential and organisational requirements, safeguarding of client funds, market-abuse and conduct-of-business rules)?\", '
    r'readiness:{regime:\"eu_mica\",dimension:\"mica_authorisation\"}}'
    r',\n    {id:\"Q2_PRIORITY\"'
)

# ---------------------------------------------------------------------------
# P1.4 UK AI advisory regime block
# P1.5 MiCA regime block
# ---------------------------------------------------------------------------
ANCHOR_REGIMES_END = r'{id:\"portability_switching\",name:\"Portability & switching readiness\",weight:1.0}]}\n  ],'
INSERT_REGIMES = (
    r'{id:\"portability_switching\",name:\"Portability & switching readiness\",weight:1.0}]}'
    # ---- UK AI advisory regime ----
    r',\n\n    {id:\"uk_ai_advisory\", name:\"UK AI regulatory approach (principles-based)\", '
    r'short:\"UK · ICO / FCA / PRA principles\", '
    r'legal_reference:\"ICO Guidance on AI and data protection; FCA AI update; PRA/BoE SS1/23\", '
    r'jurisdiction:\"UK\", '
    r'sources:['
    r'{name:\"ICO — Guidance on AI and data protection\",url:\"https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/\"},'
    r'{name:\"FCA — AI update (April 2024)\",url:\"https://www.fca.org.uk/publications/corporate-documents/our-approach-artificial-intelligence\"},'
    r'{name:\"PRA / Bank of England SS1/23 — Model risk management for AI/ML\",url:\"https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss\"},'
    r'{name:\"UK Government — A pro-innovation approach to AI regulation\",url:\"https://www.gov.uk/government/publications/ai-regulation-a-pro-innovation-approach\"}], '
    r'weight:0.05,\n'
    r'     applicability_rules:['
    r'{when:{all:[{any:[{fact:\"uses_high_risk_ai\",op:\"is_true\"},{fact:\"uses_other_ai\",op:\"is_true\"}]},{fact:\"establishment_uk\",op:\"is_true\"}]},grade:\"advisory\",rationale:\"The UK operates a principles-based, regulator-led approach to AI rather than a UK equivalent of the EU AI Act. Applicable material includes the ICO Guidance on AI and data protection, FCA supervisory expectations for AI in regulated activities, and PRA/BoE SS1/23 on model risk management for AI/ML. Confirm applicable principles per use case; expect further UK regulatory evolution.\"}'
    r'],\n'
    r'     obligations:['
    r'\"Alignment with ICO Guidance on AI and data protection (fairness, transparency, DPIA where required, individual rights)\",'
    r'\"FCA supervisory expectations for AI use in regulated activities (consumer duty, senior manager accountability)\",'
    r'\"PRA/BoE SS1/23 for banks and insurers using AI/ML in prudentially significant areas (model risk governance)\",'
    r'\"Board-level accountability and end-to-end model risk management\"'
    r'],\n'
    r'     readiness_dimensions:[{id:\"uk_ai_governance\",name:\"UK AI governance and principles alignment\",weight:1.0}]}'
    # ---- MiCA regime ----
    r',\n\n    {id:\"eu_mica\", name:\"MiCA — Markets in Crypto-Assets\", '
    r'short:\"EU · crypto-asset service providers\", '
    r'legal_reference:\"Regulation (EU) 2023/1114\", '
    r'jurisdiction:\"EU\", '
    r'sources:['
    r'{name:\"Regulation (EU) 2023/1114 (MiCA) — EUR-Lex\",url:\"https://eur-lex.europa.eu/eli/reg/2023/1114/oj\"},'
    r'{name:\"ESMA — Markets in Crypto-Assets (MiCA)\",url:\"https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica\"},'
    r'{name:\"EBA — MiCAR guidelines\",url:\"https://www.eba.europa.eu/regulation-and-policy/markets-crypto-assets\"}], '
    r'weight:0.10,\n'
    r'     applicability_rules:['
    r'{when:{all:[{fact:\"fin_entity_type\",op:\"eq\",value:\"casp_crypto\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"applies\",rationale:\"Crypto-Asset Service Providers offering services in the EU require MiCA authorisation from their home National Competent Authority and are subject to prudential, organisational, conduct-of-business and market-integrity obligations. Full application from 30 December 2024; asset-referenced token / e-money token rules apply from 30 June 2024.\"},'
    r'{when:{all:[{fact:\"fin_entity_type\",op:\"eq\",value:\"casp_crypto\"},{not:{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}}]},grade:\"advisory\",rationale:\"CASP without EU nexus falls outside MiCA scope today, but reverse-solicitation limits and marketing rules can bring EU-facing activity in scope quickly. Reassess if EU customer base grows.\"}'
    r'],\n'
    r'     obligations:['
    r'\"MiCA authorisation from home NCA (or notification for certain existing regulated firms under Art. 60)\",'
    r'\"Prudential, organisational and governance requirements (own funds, business continuity, outsourcing)\",'
    r'\"Safeguarding of clients funds and crypto-assets (segregation, custody rules)\",'
    r'\"Market abuse and integrity obligations (insider dealing, market manipulation)\",'
    r'\"Conduct-of-business, transparency, complaints handling\",'
    r'\"White paper obligations for token issuers (asset-referenced / e-money tokens)\"'
    r'],\n'
    r'     readiness_dimensions:[{id:\"mica_authorisation\",name:\"MiCA authorisation and governance\",weight:1.0}]}'
    r'\n  ],'
)

# ---------------------------------------------------------------------------
# Facts declaration — add the two new facts introduced above (hygiene)
# ---------------------------------------------------------------------------
EDIT_FACTS = (
    r'{key:\"ict_concentration_risk\"}\n  ],',
    r'{key:\"ict_concentration_risk\"},{key:\"us_dpf_cert_status\"}\n  ],',
)

EDITS = [
    ("P1.3 Q_HYPER widened", EDIT_QHYPER),
    ("P1.2 Q_SOVOFFER Yes score 100→70", EDIT_QSOVOFFER),
    ("P1.6 Grades relabeled", EDIT_GRADES),
    ("P1.8 QR_UKCTP widened", EDIT_QRUKCTP),
    ("P1.1 Transfer rule split (DPF-aware)", EDIT_TRANSFER_RULE),
    ("P1.7 DORA CTP unknown-answer paths", (DORA_ANCHOR, DORA_INSERT)),
    ("Facts array +us_dpf_cert_status", EDIT_FACTS),
]

INSERTIONS = [
    ("Q_DPFCERT question", ANCHOR_QDPF, INSERT_QDPF, DPF_QID),
    ("QR_SOVCTRL / QR_UKAI / QR_MICA questions", ANCHOR_NEW_QS, INSERT_NEW_QS, SOVCTRL_QID),
    # Marker uses the regime's `id:"..."` form — that only appears in the
    # regime block itself, not in questions that reference the regime by
    # name inside a readiness tag.
    ("uk_ai_advisory + eu_mica regimes", ANCHOR_REGIMES_END, INSERT_REGIMES,
     r'id:\"uk_ai_advisory\"'),
]


def json_safety_check(data: str) -> None:
    """Refuse to save if any <script type='__bundler/...'> payload
    stops parsing as JSON. Would otherwise crash the loader on the
    live site with "Bad escaped character in JSON"."""
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
                f"\n  ✗ {tag} JSON invalid after Phase 1 patch: {e}\n"
                f"    context: {ctx!r}\n"
                f"    REFUSING TO SAVE — investigate and adjust the replacements.")


def js_structure_check(data: str) -> None:
    """Cheap semantic guard: decode the template payload and look for
    known signs of a broken JS object — truncated arrays, orphan commas
    at the start of an array. Not a full JS parser; catches the class
    of accidents where an INSERT replacement accidentally overwrote the
    anchor content instead of appending to it."""
    m = re.search(r'<script type="__bundler/template">', data)
    if not m:
        return
    end = data.find('</script>', m.end())
    payload = data[m.end():end]
    decoded = json.loads(payload)
    text = decoded if isinstance(decoded, str) else json.dumps(decoded)

    bad_patterns = [
        (r'options:\[\s*,', "empty leading comma in an options:[] array"),
        (r'options:\[\s*\]', "empty options:[] array"),
        (r'applicability_rules:\[\s*,', "empty leading comma in applicability_rules"),
        (r'readiness_dimensions:\[\s*,', "empty leading comma in readiness_dimensions"),
    ]
    for pat, msg in bad_patterns:
        if re.search(pat, text):
            m2 = re.search(pat, text)
            ctx = text[max(0, m2.start()-80):m2.end()+80]
            raise SystemExit(
                f"\n  ✗ JS structure defect: {msg}\n"
                f"    at: {ctx!r}\n"
                f"    REFUSING TO SAVE — an INSERT probably overwrote its anchor.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Apply edits in memory and run JSON check; do not write file.")
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
            print(f"  ! {label}: OLD NOT FOUND — adjust anchor")
            continue
        data = data.replace(old, new, 1)
        applied += 1
        print(f"  ✓ {label}")

    print("\n--- INSERTIONS ---")
    for label, anchor, replacement, marker_qid in INSERTIONS:
        if marker_qid in data:
            print(f"  = {label}: already present ({marker_qid} found)")
            continue
        if anchor not in data:
            print(f"  ! {label}: ANCHOR NOT FOUND — adjust")
            continue
        data = data.replace(anchor, replacement, 1)
        applied += 1
        print(f"  ✓ {label}")

    print()
    json_safety_check(data)
    print("  ✓ all bundler payloads still parse as valid JSON")
    js_structure_check(data)
    print("  ✓ no truncated arrays / orphan-comma structural defects")

    if args.dry_run:
        print("\n  (dry run — file not written)")
        return 0

    FILE.write_text(data, encoding="utf-8")
    print(f"\n  file: {FILE}")
    print(f"  size delta: {len(data) - before_len:+d} bytes  ({applied} edits/insertions)")
    return 0 if applied else 1


if __name__ == "__main__":
    sys.exit(main())
