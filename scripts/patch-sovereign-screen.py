#!/usr/bin/env python3
"""Apply legal-accuracy fixes to the Sovereign Screen KB (in-place, on the
bundled single-file HTML). Idempotent — safe to re-run. All edits target
literal strings inside the embedded const DEFAULT_KB block.

Fixes (matches items #1, #2, #3, #9 in docs/SOVEREIGN-SCREEN-REVIEW.md):
  1. Q_SCD — remove "detailed financial" from the Art. 9 special-category
     question wording (financial data is not an Art. 9 category).
  2. EU AI Act rationale — replace the misquoted "7% of global turnover"
     penalty with tiered penalties per Art. 99.
  3. Q_AI — split "Insurance risk assessment or pricing" into life/health
     (Annex III item 5(c) high-risk) vs. non-life (other AI).
  4. DORA CTP rationale — drop the point-in-time "19 designated as of
     Nov 2025" count and replace with date-agnostic language.

Additionally: inject a `sources:[...]` array into every regime block so
the tool can render authoritative citations, and update the meta
disclaimer/last_reviewed date.
"""
import pathlib, re, sys

FILE = pathlib.Path("/home/user/ltm-core/Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html")

# All strings use bundle-native escaping (\" for JS-inside-HTML).
EDITS = [
    # --- FIX 1: Q_SCD wording ---
    (
        r'text:\"Do you process special-category or highly sensitive data (biometric, health, detailed financial)?\"',
        r'text:\"Do you process special-category personal data as defined in GDPR Article 9 (biometric data used for identification, health, genetic, racial/ethnic, political, religious, trade-union, sex-life)?\"',
    ),

    # --- FIX 2: AI Act penalty text ---
    (
        r'triggering risk management, data governance, transparency, human oversight and conformity obligations. Penalties reach 7% of global turnover.',
        r'triggering risk management, data governance, transparency, human oversight and conformity obligations. Penalties are tiered (Art. 99): up to EUR 35m or 7% of global turnover for prohibited practices (Art. 5); up to EUR 15m or 3% for other non-compliance (including high-risk system violations); up to EUR 7.5m or 1% for supplying incorrect information.',
    ),

    # --- FIX 3: Q_AI insurance split ---
    (
        r'{label:\"Insurance risk assessment or pricing\",fact_value:{uses_high_risk_ai:true}},{label:\"Fraud detection or operational automation\",fact_value:{uses_other_ai:true}}',
        r'{label:\"Life or health insurance risk assessment or pricing\",fact_value:{uses_high_risk_ai:true}},{label:\"Non-life insurance risk assessment or pricing (motor, property, commercial lines)\",fact_value:{uses_other_ai:true}},{label:\"Fraud detection or operational automation\",fact_value:{uses_other_ai:true}}',
    ),

    # --- FIX 4: DORA CTP designation count ---
    # NOTE: the template payload is JSON-encoded; the only escapes JSON
    # accepts are \" \\ \/ \b \f \n \r \t \uXXXX. Do NOT put \' or any
    # other non-JSON escape into replacement text — it will crash the
    # bundler with "Bad escaped character in JSON". Use plain apostrophes
    # or drop them.
    (
        r'ICT providers to finance can be designated Critical ICT Third-Party Providers under direct ESA oversight (19 designated as of Nov 2025, incl. AWS, Azure, Google Cloud, IBM, Bloomberg).',
        r'ICT providers to finance can be designated Critical ICT Third-Party Providers (CTPPs) under direct ESA oversight (DORA Art. 31). The first tranche of designations includes major hyperscalers and market-data providers; consult the ESAs register for the current list.',
    ),

    # --- Update meta last_reviewed + disclaimer clarity ---
    (
        r'last_reviewed:\"2026-07-21\"',
        r'last_reviewed:\"2026-07-30\"',
    ),
    (
        r'disclaimer:\"Indicative triage / applicability screening. Not legal advice. Applicability depends on specific facts and should be confirmed with qualified counsel.\"',
        r'disclaimer:\"Preliminary, indicative triage. Not legal advice. All regime calls depend on specific facts and must be confirmed with qualified counsel and, where relevant, your competent supervisory authority. See the Sources & Methodology section of the report for the authoritative references behind each regime.\"',
    ),

    # --- Placeholder-note cleanup (item #15) ---
    (
        r'note:\"Middle three labels are placeholders â reconcile with the LTM Digital Sovereignty deck.\", stages:',
        r'note:\"Five-stage maturity spine ranging from Reactive to Sovereign-by-Design.\", stages:',
    ),
]

# --- Sources per regime ---
# Injected as: sources:[{name:"...",url:"..."}, ...] appended inside each regime block,
# right after the legal_reference field.
SOURCES = {
    "dora": [
        ("Regulation (EU) 2022/2554 (DORA) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2022/2554/oj"),
        ("DORA — European Commission", "https://finance.ec.europa.eu/regulation-and-supervision/financial-services-legislation/implementing-and-delegated-acts/digital-operational-resilience-act_en"),
        ("Joint ESAs — DORA guidance", "https://www.eba.europa.eu/regulation-and-policy/digital-operational-resilience-act-dora"),
    ],
    "nis2_residual": [
        ("Directive (EU) 2022/2555 (NIS2) — EUR-Lex", "https://eur-lex.europa.eu/eli/dir/2022/2555/oj"),
        ("NIS2 — ENISA", "https://www.enisa.europa.eu/topics/nis-directive"),
    ],
    "uk_opres": [
        ("FCA PS21/3 — Building operational resilience", "https://www.fca.org.uk/publications/policy-statements/ps21-3-building-operational-resilience"),
        ("PRA SS2/21 — Operational resilience", "https://www.bankofengland.co.uk/prudential-regulation/publication/2021/march/operational-resilience-impact-tolerances-for-important-business-services-ss"),
        ("Bank of England — Operational resilience", "https://www.bankofengland.co.uk/prudential-regulation/regulation/operational-resilience"),
    ],
    "uk_ctp": [
        ("FSMA 2023 — Critical Third Parties provisions (Part 9)", "https://www.legislation.gov.uk/ukpga/2023/29/contents"),
        ("FCA PS24/16 — Operational resilience: Critical Third Parties", "https://www.fca.org.uk/publications/policy-statements/ps24-16-operational-resilience-critical-third-parties"),
        ("PRA PS16/24 — CTPs to the UK financial sector", "https://www.bankofengland.co.uk/prudential-regulation/publication/2024/november/operational-resilience-critical-third-parties-to-the-uk-financial-sector"),
    ],
    "eu_gdpr": [
        ("Regulation (EU) 2016/679 (GDPR) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2016/679/oj"),
        ("EDPB — European Data Protection Board", "https://edpb.europa.eu/edpb_en"),
        ("EU-US Data Privacy Framework — European Commission", "https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/eu-us-data-privacy-framework_en"),
    ],
    "uk_gdpr": [
        ("UK GDPR — legislation.gov.uk (retained)", "https://www.legislation.gov.uk/eur/2016/679/contents"),
        ("Data Protection Act 2018", "https://www.legislation.gov.uk/ukpga/2018/12/contents"),
        ("PECR (Privacy and Electronic Communications Regulations 2003)", "https://www.legislation.gov.uk/uksi/2003/2426/contents"),
        ("Data (Use and Access) Act 2025", "https://www.legislation.gov.uk/ukpga/2025/18"),
        ("ICO — Information Commissioner Office", "https://ico.org.uk/"),
    ],
    "data_transfer_jurisdiction": [
        ("GDPR Chapter V (international transfers) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2016/679/oj"),
        ("US CLOUD Act — DOJ overview", "https://www.justice.gov/criminal/criminal-oia/cloud-act"),
        ("EDPB — Schrems II recommendations on supplementary measures", "https://edpb.europa.eu/our-work-tools/our-documents/recommendations/recommendations-012020-measures-supplement-transfer_en"),
        ("EU-US Data Privacy Framework — European Commission", "https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/eu-us-data-privacy-framework_en"),
    ],
    "eu_ai_act": [
        ("Regulation (EU) 2024/1689 (AI Act) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"),
        ("EU AI Act — European Commission", "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai"),
        ("AI Act penalties (Art. 99)", "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689"),
    ],
    "eu_data_act": [
        ("Regulation (EU) 2023/2854 (Data Act) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2023/2854/oj"),
        ("EU Data Act — European Commission", "https://digital-strategy.ec.europa.eu/en/policies/data-act"),
    ],
}

def build_sources_snippet(regime_id: str) -> str:
    if regime_id not in SOURCES:
        return ""
    items = ",".join(
        r'{{name:\"{n}\",url:\"{u}\"}}'.format(n=name, u=url)
        for name, url in SOURCES[regime_id]
    )
    return r"sources:[" + items + r"], "

def inject_sources(data: str) -> tuple[str, int]:
    """Insert `sources:[...]` into each regime block, right after its
    `jurisdiction:"..."` field. Idempotent — skips if already present."""
    injected = 0
    for regime_id in SOURCES:
        # Match: {id:"<regime_id>", ..., jurisdiction:"...",  (until the next comma+space)
        pat = re.compile(
            r'(\{id:\\"' + re.escape(regime_id) + r'\\".*?jurisdiction:\\"[^\\]+\\", )',
            re.DOTALL,
        )
        m = pat.search(data)
        if not m:
            print(f"  ! could not locate regime block: {regime_id}")
            continue
        # Already patched?
        window = data[m.start():m.start()+2000]
        if r'sources:[{name:\"' in window[:len(m.group(1))+40]:
            continue
        snippet = build_sources_snippet(regime_id)
        data = data[:m.end()] + snippet + data[m.end():]
        injected += 1
    return data, injected

def json_safety_check(data: str) -> None:
    """After edits, verify each <script type='__bundler/...'> payload
    still parses as JSON. Fail loud if not — the bundler will refuse to
    unpack, showing 'Bad escaped character in JSON' on the home screen."""
    import json, re
    for tag in ('__bundler/manifest', '__bundler/template', '__bundler/ext_resources'):
        m = re.search(r'<script type="'+re.escape(tag)+r'">', data)
        if not m:
            continue
        end = data.find('</script>', m.end())
        payload = data[m.end():end]
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            ctx = payload[max(0, e.pos-60):e.pos+60]
            raise SystemExit(f"\n  ✗ {tag} JSON invalid after patch: {e}\n    context: {ctx!r}\n    REFUSING TO SAVE — restore from git and adjust replacements.")

def main() -> int:
    data = FILE.read_text(encoding="utf-8")
    before_len = len(data)
    changed = 0
    for old, new in EDITS:
        if old not in data:
            if new in data:
                print(f"  = already applied: {old[:60]!r}")
                continue
            print(f"  ! NOT FOUND: {old[:80]!r}")
            continue
        data = data.replace(old, new, 1)
        changed += 1
        print(f"  ✓ patched: {old[:60]!r}")
    data, injected = inject_sources(data)
    print(f"  sources injected into {injected} regime(s)")
    json_safety_check(data)
    print("  ✓ all bundler payloads still parse as valid JSON")
    FILE.write_text(data, encoding="utf-8")
    print(f"\n  file: {FILE}")
    print(f"  size delta: {len(data)-before_len:+d} bytes")
    return 0 if changed or injected else 1

if __name__ == "__main__":
    sys.exit(main())
