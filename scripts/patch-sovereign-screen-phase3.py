#!/usr/bin/env python3
"""Sovereign Screen — Phase 3 patch (new regime coverage).

Additive. Each regime is an independent block appended to KB.regimes[]
with matching readiness questions appended to KB.questions.

  P3.1  EUCS  — EU Cybersecurity Certification Scheme for Cloud Services
  P3.2  PSD2 / PSD3+PSR — Payment Services
  P3.3  CRR / CRD + EBA cloud outsourcing guidelines (banks)
  P3.4  Solvency II (insurers)
  P3.5  eIDAS 2 — EU Digital Identity Wallet

Idempotent. Same guards as Phase 1/2.
"""
import argparse
import json
import pathlib
import re
import sys

FILE = pathlib.Path("/home/user/ltm-core/Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html")

# --------------------------------------------------------------------------
# End-of-regimes anchor: the closing "]" of MiCA (last regime added in P1)
# followed by "\n  ],\n  sections:[" which starts the sections array.
# --------------------------------------------------------------------------
REGIMES_END_ANCHOR = (
    r'readiness_dimensions:[{id:\"mica_authorisation\",name:\"MiCA authorisation and governance\",weight:1.0}]}\n  ],'
)

# Five new regime blocks.
NEW_REGIMES = (
    # ---- P3.1 EUCS ----
    r',\n\n    {id:\"eu_eucs\", name:\"EUCS — EU Cybersecurity Certification for Cloud Services\", '
    r'short:\"EU · cloud assurance certification\", '
    r'legal_reference:\"Regulation (EU) 2019/881 (Cybersecurity Act); EUCS scheme (ENISA)\", '
    r'jurisdiction:\"EU\", '
    r'sources:['
    r'{name:\"Regulation (EU) 2019/881 (Cybersecurity Act) — EUR-Lex\",url:\"https://eur-lex.europa.eu/eli/reg/2019/881/oj\"},'
    r'{name:\"ENISA — EUCS candidate scheme\",url:\"https://www.enisa.europa.eu/topics/certification/eucs-cloud-services-scheme\"},'
    r'{name:\"ENISA — Cloud certification landscape\",url:\"https://www.enisa.europa.eu/topics/cloud-and-big-data/cloud-security\"}], '
    r'weight:0.05,\n'
    r'     applicability_rules:['
    r'{when:{all:[{fact:\"entity_role\",op:\"eq\",value:\"ict_provider_to_finance\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"advisory\",rationale:\"For cloud and ICT providers serving the EU financial sector: EUCS certification (once adopted) will offer a common EU-wide assurance framework with three levels — Basic, Substantial and High. Financial-sector customers will increasingly ask for the level appropriate to workload sensitivity. Track ENISA adoption and, where relevant, prepare for certification.\"},'
    r'{when:{all:[{fact:\"entity_role\",op:\"eq\",value:\"financial_entity\"},{any:[{fact:\"uses_us_hyperscaler\",op:\"is_true\"},{fact:\"cloud_provider_hq\",op:\"includes_any\",value:[\"US\",\"Other\"]}]}]},grade:\"advisory\",rationale:\"For EU financial firms sourcing cloud from providers outside the EU: EUCS certification is expected to inform procurement and DORA third-party risk assessments. Consider requiring EUCS-certified providers (or equivalent EU-boundary assurance) for critical and important workloads; align contractual clauses to the target assurance level.\"}'
    r'],\n'
    r'     obligations:['
    r'\"(Providers, once EUCS is adopted) Obtain and maintain EUCS certification at the assurance level required by target customers\",'
    r'\"(Customers) Reflect EUCS assurance requirements in procurement, DORA third-party risk assessments and contractual clauses\",'
    r'\"Align sovereignty controls (data location, key custody, personnel jurisdiction) with the assurance level\"'
    r'],\n'
    r'     readiness_dimensions:[{id:\"eucs_alignment\",name:\"EUCS alignment / procurement readiness\",weight:1.0}]}'

    # ---- P3.2 PSD2 / PSD3 + PSR ----
    r',\n\n    {id:\"eu_psd\", name:\"PSD2 / PSD3 + PSR (Payment Services)\", '
    r'short:\"EU · payment services\", '
    r'legal_reference:\"Directive (EU) 2015/2366 (PSD2); PSD3 and PSR (in EU legislative process)\", '
    r'jurisdiction:\"EU\", '
    r'sources:['
    r'{name:\"Directive (EU) 2015/2366 (PSD2) — EUR-Lex\",url:\"https://eur-lex.europa.eu/eli/dir/2015/2366/oj\"},'
    r'{name:\"EBA — PSD2 hub\",url:\"https://www.eba.europa.eu/regulation-and-policy/payment-services-and-electronic-money\"},'
    r'{name:\"European Commission — PSD3 / PSR proposals\",url:\"https://finance.ec.europa.eu/regulation-and-supervision/financial-services-legislation/implementing-and-delegated-acts/payment-services-directive-3-and-payment-services-regulation_en\"}], '
    r'weight:0.10,\n'
    r'     applicability_rules:['
    r'{when:{all:[{fact:\"fin_entity_type\",op:\"in\",value:[\"payment_institution\",\"emi\",\"credit_institution\"]},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"applies\",rationale:\"PSD2 applies to payment institutions, e-money institutions and credit institutions providing payment services in the EU. Core obligations: strong customer authentication (SCA under EBA RTS 2018/389), access-to-account for AIS / PIS, incident reporting, complaints handling. PSD3 (Directive) and PSR (Regulation) are progressing through the EU legislative process; track transposition timelines and prepare for the shift from Directive to Regulation for uniform application.\"}'
    r'],\n'
    r'     obligations:['
    r'\"Strong customer authentication (SCA) per EBA RTS (Commission Delegated Regulation 2018/389)\",'
    r'\"Access-to-account for authorised third-party providers (AIS, PIS)\",'
    r'\"Major operational and security incident reporting to home NCA within statutory windows\",'
    r'\"Complaints handling and consumer protection obligations\",'
    r'\"Governance and internal-control arrangements proportionate to size and complexity\",'
    r'\"(On PSD3/PSR entry into force) Enhanced fraud liability, expanded SCA scope, open-finance groundwork\"'
    r'],\n'
    r'     readiness_dimensions:[{id:\"psd_compliance\",name:\"PSD2 compliance and PSD3/PSR readiness\",weight:1.0}]}'

    # ---- P3.3 CRR / CRD + EBA cloud outsourcing ----
    r',\n\n    {id:\"eu_crr_crd\", name:\"CRR / CRD + EBA cloud outsourcing guidelines\", '
    r'short:\"EU · banks: prudential + cloud outsourcing\", '
    r'legal_reference:\"Regulation (EU) 575/2013 (CRR); Directive 2013/36/EU (CRD); EBA/GL/2019/02 (Outsourcing); EBA/GL/2019/04 (ICT and security risk)\", '
    r'jurisdiction:\"EU\", '
    r'sources:['
    r'{name:\"Regulation (EU) 575/2013 (CRR) — EUR-Lex\",url:\"https://eur-lex.europa.eu/eli/reg/2013/575/oj\"},'
    r'{name:\"Directive 2013/36/EU (CRD IV, as amended) — EUR-Lex\",url:\"https://eur-lex.europa.eu/eli/dir/2013/36/oj\"},'
    r'{name:\"EBA/GL/2019/02 — Outsourcing arrangements\",url:\"https://www.eba.europa.eu/regulation-and-policy/internal-governance/guidelines-on-outsourcing-arrangements\"},'
    r'{name:\"EBA/GL/2019/04 — ICT and security risk management\",url:\"https://www.eba.europa.eu/regulation-and-policy/internal-governance/guidelines-on-ict-and-security-risk-management\"}], '
    r'weight:0.10,\n'
    r'     applicability_rules:['
    r'{when:{all:[{fact:\"fin_entity_type\",op:\"eq\",value:\"credit_institution\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"applies\",rationale:\"EU credit institutions are subject to CRR/CRD prudential framework (capital, liquidity, leverage, governance) and, for outsourcing to third parties (including cloud), the EBA Guidelines on Outsourcing (2019/02) and ICT & Security Risk (2019/04). These predate DORA and continue alongside it — outsourcing pre-approval / notification thresholds, register of outsourcing arrangements, exit and business continuity requirements. DORA is lex specialis for ICT-risk aspects (Art. 1(2)) but does not disapply CRR/CRD governance.\"}'
    r'],\n'
    r'     obligations:['
    r'\"CRR / CRD prudential framework: capital, liquidity, leverage, large exposures\",'
    r'\"Governance and internal control (CRD Art. 74) with three lines of defence\",'
    r'\"EBA outsourcing framework: written agreements, register of outsourcing arrangements, prior notification to competent authority for critical / important functions\",'
    r'\"EBA ICT and security risk: governance, IS strategy, ICT operations, project & change management, incident management\",'
    r'\"Business continuity, exit planning and audit rights for material outsourcing\"'
    r'],\n'
    r'     readiness_dimensions:[{id:\"crr_governance\",name:\"CRR/CRD governance & EBA outsourcing readiness\",weight:1.0}]}'

    # ---- P3.4 Solvency II ----
    r',\n\n    {id:\"eu_solvency2\", name:\"Solvency II\", '
    r'short:\"EU · insurers: prudential + outsourcing\", '
    r'legal_reference:\"Directive 2009/138/EC; Commission Delegated Regulation (EU) 2015/35 (esp. Art. 274 outsourcing)\", '
    r'jurisdiction:\"EU\", '
    r'sources:['
    r'{name:\"Directive 2009/138/EC (Solvency II) — EUR-Lex\",url:\"https://eur-lex.europa.eu/eli/dir/2009/138/oj\"},'
    r'{name:\"Commission Delegated Regulation (EU) 2015/35 — EUR-Lex\",url:\"https://eur-lex.europa.eu/eli/reg_del/2015/35/oj\"},'
    r'{name:\"EIOPA — Solvency II\",url:\"https://www.eiopa.europa.eu/browse/regulation-and-policy/solvency-ii_en\"},'
    r'{name:\"EIOPA — Guidelines on outsourcing to cloud service providers (EIOPA-BoS-20-002)\",url:\"https://www.eiopa.europa.eu/publications/guidelines-outsourcing-cloud-service-providers_en\"}], '
    r'weight:0.10,\n'
    r'     applicability_rules:['
    r'{when:{all:[{fact:\"fin_entity_type\",op:\"in\",value:[\"insurer\",\"insurance_intermediary\"]},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"applies\",rationale:\"EU insurers and reinsurers are subject to Solvency II: three-pillar framework (capital, governance, disclosure). Article 274 of the Delegated Regulation governs outsourcing of critical or important functions, including cloud outsourcing. EIOPA Guidelines on outsourcing to cloud service providers (BoS-20-002) set expectations for pre-outsourcing analysis, contractual content, monitoring, exit and sub-outsourcing. DORA is lex specialis for ICT-risk aspects but Solvency II governance and outsourcing rules continue to apply.\"}'
    r'],\n'
    r'     obligations:['
    r'\"Solvency II three-pillar framework: quantitative capital (SCR/MCR), governance (system of governance, ORSA), disclosure (SFCR, RSR)\",'
    r'\"Outsourcing of critical / important functions (Art. 274 Del. Reg.): pre-outsourcing analysis, notification to supervisor, written agreement, monitoring\",'
    r'\"EIOPA cloud outsourcing guidelines: risk assessment, contractual content (audit rights, exit, sub-outsourcing), ongoing monitoring\",'
    r'\"Business continuity and exit strategy for material cloud arrangements\"'
    r'],\n'
    r'     readiness_dimensions:[{id:\"solvency2_governance\",name:\"Solvency II governance & cloud outsourcing readiness\",weight:1.0}]}'

    # ---- P3.5 eIDAS 2 ----
    r',\n\n    {id:\"eu_eidas2\", name:\"eIDAS 2 — EU Digital Identity Wallet\", '
    r'short:\"EU · digital identity\", '
    r'legal_reference:\"Regulation (EU) 2024/1183 (amending Regulation (EU) 910/2014)\", '
    r'jurisdiction:\"EU\", '
    r'sources:['
    r'{name:\"Regulation (EU) 2024/1183 (eIDAS 2) — EUR-Lex\",url:\"https://eur-lex.europa.eu/eli/reg/2024/1183/oj\"},'
    r'{name:\"European Commission — European Digital Identity\",url:\"https://digital-strategy.ec.europa.eu/en/policies/eudi-regulation\"},'
    r'{name:\"European Digital Identity Wallet Architecture Reference Framework (ARF)\",url:\"https://github.com/eu-digital-identity-wallet/architecture-and-reference-framework\"}], '
    r'weight:0.05,\n'
    r'     applicability_rules:['
    r'{when:{all:[{fact:\"entity_role\",op:\"eq\",value:\"financial_entity\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"advisory\",rationale:\"eIDAS 2 obliges Member States to issue an EU Digital Identity Wallet by end-2026, and requires very large online platforms — plus a defined set of relying parties, explicitly including EU financial institutions and payment service providers — to accept the Wallet for authentication and identification. Prepare KYC / onboarding flows to accept Wallet-based identity attestations and to interoperate with the Architecture Reference Framework (ARF).\"},'
    r'{when:{all:[{fact:\"entity_role\",op:\"eq\",value:\"ict_provider_to_finance\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]},grade:\"advisory\",rationale:\"ICT providers building identity, onboarding or authentication capabilities for EU financial customers should track eIDAS 2 wallet compatibility, qualified trust service (QTSP) roles and the evolving Architecture Reference Framework.\"}'
    r'],\n'
    r'     obligations:['
    r'\"(Financial firms as relying parties) Accept EU Digital Identity Wallet for authentication and identification where required by the Regulation\",'
    r'\"Interoperate with the European Digital Identity Wallet Architecture Reference Framework (ARF)\",'
    r'\"Where acting as a trust service provider: comply with QTSP obligations under eIDAS as amended\",'
    r'\"Update KYC / onboarding and authentication flows to consume Wallet-issued attestations\"'
    r'],\n'
    r'     readiness_dimensions:[{id:\"eidas2_wallet_readiness\",name:\"eIDAS 2 Wallet acceptance readiness\",weight:1.0}]}'

    # Close: preserve the trailing "]"
    r'\n  ],'
)

# --------------------------------------------------------------------------
# New readiness questions for each new regime — inserted right after QR_MICA
# (last readiness question added in Phase 1), before Q2_PRIORITY.
# --------------------------------------------------------------------------
QR_MICA_TAIL_ANCHOR = (
    r'readiness:{regime:\"eu_mica\",dimension:\"mica_authorisation\"}},\n    {id:\"Q2_PRIORITY\"'
)
QR_MICA_TAIL_INSERT = (
    r'readiness:{regime:\"eu_mica\",dimension:\"mica_authorisation\"}}'
    # QR_EUCS
    r',\n    {id:\"QR_EUCS\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", '
    r'shown_if:{any:[{fact:\"entity_role\",op:\"eq\",value:\"ict_provider_to_finance\"},{all:[{fact:\"entity_role\",op:\"eq\",value:\"financial_entity\"},{any:[{fact:\"uses_us_hyperscaler\",op:\"is_true\"},{fact:\"cloud_provider_hq\",op:\"includes_any\",value:[\"US\",\"Other\"]}]}]}]}, '
    r'text:\"How aligned is your cloud procurement and DORA third-party risk process with the EUCS (EU Cybersecurity Certification Scheme for Cloud Services) assurance-level framework — Basic / Substantial / High?\", '
    r'readiness:{regime:\"eu_eucs\",dimension:\"eucs_alignment\"}}'
    # QR_PSD
    r',\n    {id:\"QR_PSD\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", '
    r'shown_if:{all:[{fact:\"fin_entity_type\",op:\"in\",value:[\"payment_institution\",\"emi\",\"credit_institution\"]},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]}, '
    r'text:\"How mature is your PSD2 compliance and PSD3 / PSR readiness — SCA controls, AIS/PIS access, incident reporting, complaints handling, monitoring of legislative changes?\", '
    r'readiness:{regime:\"eu_psd\",dimension:\"psd_compliance\"}}'
    # QR_CRR
    r',\n    {id:\"QR_CRR\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", '
    r'shown_if:{all:[{fact:\"fin_entity_type\",op:\"eq\",value:\"credit_institution\"},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]}, '
    r'text:\"How mature is your CRR/CRD governance and EBA outsourcing / ICT & security risk framework (register of outsourcing arrangements, pre-approval, exit planning, business continuity)?\", '
    r'readiness:{regime:\"eu_crr_crd\",dimension:\"crr_governance\"}}'
    # QR_SOLV
    r',\n    {id:\"QR_SOLV\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", '
    r'shown_if:{all:[{fact:\"fin_entity_type\",op:\"in\",value:[\"insurer\",\"insurance_intermediary\"]},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]}, '
    r'text:\"How mature is your Solvency II governance and cloud outsourcing framework (Art. 274 Del. Reg. requirements, EIOPA cloud outsourcing guidelines, monitoring and exit)?\", '
    r'readiness:{regime:\"eu_solvency2\",dimension:\"solvency2_governance\"}}'
    # QR_EIDAS2
    r',\n    {id:\"QR_EIDAS2\", category:\"resilience_posture\", tier:1, answer_type:\"rating_1_5\", '
    r'shown_if:{all:[{any:[{fact:\"entity_role\",op:\"eq\",value:\"financial_entity\"},{fact:\"entity_role\",op:\"eq\",value:\"ict_provider_to_finance\"}]},{any:[{fact:\"establishment_eu\",op:\"is_true\"},{fact:\"offers_services_eu\",op:\"is_true\"}]}]}, '
    r'text:\"How ready are your KYC / onboarding / authentication flows to accept the EU Digital Identity Wallet under eIDAS 2 (by end-2026 for financial-sector relying parties)?\", '
    r'readiness:{regime:\"eu_eidas2\",dimension:\"eidas2_wallet_readiness\"}}'
    # then original Q2_PRIORITY marker
    r',\n    {id:\"Q2_PRIORITY\"'
)


EDITS = [
    ("Five new regime blocks appended", (REGIMES_END_ANCHOR,
                                          REGIMES_END_ANCHOR.replace(r'\n  ],', NEW_REGIMES))),
]

INSERTIONS = [
    ("5 readiness questions after QR_MICA", QR_MICA_TAIL_ANCHOR, QR_MICA_TAIL_INSERT, 'QR_EUCS'),
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
                f"\n  ✗ {tag} JSON invalid after Phase 3 patch: {e}\n"
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
        (r'regimes:\[\s*,', "empty leading comma in regimes:[]"),
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
            print(f"  = {label}: already present ({marker})")
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
