#!/usr/bin/env python3
"""DR&J Audit — Phase 2 patch (screening completeness).

Additive changes only — no existing regulation call or finding is
altered in meaning; wording refinements and new options/questions.

  P2.1  Q_C1 add Oracle / IBM Cloud / Salesforce / Snowflake / Databricks
  P2.2  Q_C2 matrix: mirror B1 rows (add aitraining + government) +
        add UK-only column
  P2.3  Q_A2 add payment-institution/EMI and CASP-crypto options
  P2.4  Q_G1 fix "health" wording; add Q_G3 for GPAI role
  P2.5  Q_H2 add EUCS Basic assurance level
  P2.6  Q_J1 cite DORA RTS (Comm. Del. Reg. 2025/301) 4h/72h/1-month
  P2.7  Q_B1 refine financial-data anchor rationale

Same bundler-patch mechanics as Phase 1: extract gzipped JS from the
manifest, apply edits, gzip back, semantic check, staging only.
"""
import argparse
import base64
import gzip
import json
import pathlib
import re
import sys

BUNDLED = pathlib.Path("/home/user/ltm-core/Digital Sovereignty Data Residency Jurisdiction Audit/LTM-Data Residency & Jurisdiction Audit.html")
UNFORMATTED = pathlib.Path("/home/user/ltm-core/Digital Sovereignty Data Residency Jurisdiction Audit/Unformatted-Data-Residency-Jurisdiction-Audit.html")
JS_UUID = "d2614d21-bb06-46c7-aaeb-e4693103acbd"

# ---------------------------------------------------------------------------
# P2.1 — Q_C1: insert 7 new provider options after gcp-global, before sovereign
# ---------------------------------------------------------------------------
EDIT_C1_PROVIDERS = (
    'value:"gcp-global", label:"Google Cloud — includes non-EU regions", sev:"high",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"high",title:"GCP workloads in non-EU regions",detail:"Non-EU GCP regions processing personal data create restricted transfers and potential CLOUD Act exposure via a US-controlled operator.",phase:1,remedy:"Region-lock personal-data workloads to EU GCP regions.",steps:["Audit GCP region configuration","Apply Organization Policy to restrict region deployment","Migrate non-compliant workloads"]}]},\n'
    '        { value:"sovereign"',

    'value:"gcp-global", label:"Google Cloud — includes non-EU regions", sev:"high",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"high",title:"GCP workloads in non-EU regions",detail:"Non-EU GCP regions processing personal data create restricted transfers and potential CLOUD Act exposure via a US-controlled operator.",phase:1,remedy:"Region-lock personal-data workloads to EU GCP regions.",steps:["Audit GCP region configuration","Apply Organization Policy to restrict region deployment","Migrate non-compliant workloads"]}]},\n'
    '        { value:"oracle-eu", label:"Oracle Cloud — EU regions only", sev:"low",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"low",title:"US-HQ operator in use (Oracle Cloud) — even EU-only",detail:"Oracle Cloud EU regions constrain data location, but operator jurisdiction remains the United States; extraterritorial access risk under the CLOUD Act should still be assessed at the workload level.",phase:2,remedy:"Assess CLOUD Act residual risk for the most sensitive workloads.",steps:["Confirm all Oracle Cloud regions are EU","Assess residual CLOUD Act exposure for the most sensitive workloads","Consider EU-controlled alternatives for highest tier"]}]},\n'
    '        { value:"oracle-global", label:"Oracle Cloud — includes non-EU regions", sev:"high",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"high",title:"Oracle Cloud workloads in non-EU regions",detail:"Non-EU Oracle Cloud regions processing personal data create restricted transfers and CLOUD Act exposure via a US-controlled operator.",phase:1,remedy:"Region-lock personal-data workloads to EU Oracle Cloud regions.",steps:["Audit Oracle Cloud region configuration","Restrict provisioning to EU regions","Migrate non-compliant workloads"]}]},\n'
    '        { value:"ibm-eu", label:"IBM Cloud — EU regions only", sev:"low",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"low",title:"US-HQ operator in use (IBM Cloud) — even EU-only",detail:"IBM Cloud EU regions constrain data location, but operator jurisdiction remains the United States; assess residual extraterritorial access risk.",phase:2,remedy:"Confirm region residency and assess CLOUD Act residual risk.",steps:["Confirm all IBM Cloud regions are EU","Assess residual CLOUD Act exposure for the most sensitive workloads"]}]},\n'
    '        { value:"ibm-global", label:"IBM Cloud — includes non-EU regions", sev:"high",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"high",title:"IBM Cloud workloads in non-EU regions",detail:"Non-EU IBM Cloud regions processing personal data create restricted transfers and CLOUD Act exposure via a US-controlled operator.",phase:1,remedy:"Region-lock personal-data workloads to EU IBM Cloud regions.",steps:["Audit IBM Cloud region configuration","Restrict provisioning to EU regions","Migrate non-compliant workloads"]}]},\n'
    '        { value:"salesforce", label:"Salesforce / Heroku (US-controlled)", sev:"medium",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"medium",title:"Salesforce / Heroku is a US-HQ SaaS operator",detail:"Salesforce and Heroku operate under US jurisdiction; even EU-hosted tenants remain within CLOUD Act reach via the operator. Assess supplementary measures and data residency clauses.",phase:2,remedy:"Confirm EU hosting, tenant isolation and DPF certification (if applicable).",steps:["Confirm EU data residency for the Salesforce org","Check Salesforce DPF-list entry","Add supplementary encryption for sensitive fields"]}]},\n'
    '        { value:"snowflake", label:"Snowflake (US-HQ, region-selectable)", sev:"medium",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"medium",title:"Snowflake — US-HQ operator, region matters",detail:"Snowflake supports EU regions but is a US-HQ operator; region selection alone does not remove CLOUD Act exposure.",phase:2,remedy:"Confirm EU region + assess CLOUD Act residual risk.",steps:["Confirm Snowflake account region is EU","Enable customer-managed encryption keys where available","Assess DPF certification and supplementary measures"]}]},\n'
    '        { value:"databricks", label:"Databricks (US-HQ, region-selectable)", sev:"medium",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"medium",title:"Databricks — US-HQ operator, region matters",detail:"Databricks supports EU regions but is a US-HQ operator; region selection alone does not remove CLOUD Act exposure — relevant especially for training-data workloads.",phase:2,remedy:"Confirm EU region and assess CLOUD Act residual risk; consider EU-controlled ML platforms for the most sensitive workloads.",steps:["Confirm Databricks workspace region is EU","Assess CLOUD Act residual risk","Evaluate sovereign alternatives for the most sensitive workloads"]}]},\n'
    '        { value:"sovereign"',
)

# ---------------------------------------------------------------------------
# P2.2a — Q_C2 rows: add aitraining + government rows
# ---------------------------------------------------------------------------
EDIT_C2_ROWS = (
    'rows:[\n'
    '        { id:"pii", label:"Personal data" },\n'
    '        { id:"special", label:"Special-category data" },\n'
    '        { id:"financial", label:"Financial data" },\n'
    '        { id:"behavioural", label:"Behavioural / analytics data" }\n'
    '      ],',

    'rows:[\n'
    '        { id:"pii", label:"Personal data" },\n'
    '        { id:"special", label:"Special-category data" },\n'
    '        { id:"financial", label:"Financial data" },\n'
    '        { id:"behavioural", label:"Behavioural / analytics data" },\n'
    '        { id:"aitraining", label:"AI / ML training data" },\n'
    '        { id:"government", label:"Government / classified / restricted data" }\n'
    '      ],',
)

# ---------------------------------------------------------------------------
# P2.2b — Q_C2 cols: add uk-only column
# ---------------------------------------------------------------------------
EDIT_C2_UK_COL = (
    'cols:[\n'
    '        { id:"eu-only", label:"EU region only", sev:"positive" },\n'
    '        { id:"eu-backup", label:"EU + encrypted non-EU backup", sev:"low" },\n'
    '        { id:"us-dpf", label:"US cloud with DPF-certified processor", sev:"low" },\n'
    '        { id:"us-cloud", label:"US / non-EU cloud (no DPF)", sev:"critical" },\n'
    '        { id:"multi", label:"Multi-region global", sev:"high" },\n'
    '        { id:"unknown", label:"Unknown", sev:"high" }\n'
    '      ],',

    'cols:[\n'
    '        { id:"eu-only", label:"EU region only", sev:"positive" },\n'
    '        { id:"uk-only", label:"UK region only", sev:"positive" },\n'
    '        { id:"eu-backup", label:"EU + encrypted non-EU backup", sev:"low" },\n'
    '        { id:"us-dpf", label:"US cloud with DPF-certified processor", sev:"low" },\n'
    '        { id:"us-cloud", label:"US / non-EU cloud (no DPF)", sev:"critical" },\n'
    '        { id:"multi", label:"Multi-region global", sev:"high" },\n'
    '        { id:"unknown", label:"Unknown", sev:"high" }\n'
    '      ],',
)

# ---------------------------------------------------------------------------
# P2.3 — Q_A2: insert payment-emi and casp-crypto options after "other-fin"
# ---------------------------------------------------------------------------
EDIT_A2_ENTITIES = (
    '{ value:"other-fin", label:"Other financial entity (payment/e-money, crypto, crowdfunding, etc.)", sev:"medium", findings:[{reg:"dora",a:"Art. 2",severity:"medium",title:"DORA proportionality applies",detail:"Smaller or specialised financial entities benefit from a proportionate regime but core ICT risk and third-party obligations still apply.",phase:2,remedy:"Confirm which proportionality carve-outs apply and document the rationale.",steps:["Confirm entity type and any simplified regime","Document proportionality decisions"]}]},',

    '{ value:"payment-emi", label:"Payment institution / e-money institution (PI / EMI)", sev:"high",\n'
    '          findings:[{reg:"dora",a:"Art. 2, 5–15",severity:"high",title:"DORA ICT framework + PSD2 obligations",detail:"PIs and EMIs fall in DORA scope and simultaneously carry PSD2 obligations (SCA, AIS/PIS access, incident reporting to competent authority). ICT third-party risk, register of information and contractual clauses apply.",phase:1,remedy:"Ensure the DORA framework is in place alongside PSD2 operational and outsourcing controls.",steps:["Confirm DORA ICT risk framework covers PSD2 processes","Verify SCA and incident-reporting readiness","Register ICT third-party arrangements including data locations"]}]},\n'
    '        { value:"casp", label:"Crypto-asset service provider (CASP)", sev:"high",\n'
    '          findings:[{reg:"dora",a:"Art. 2, 5–15",severity:"high",title:"DORA applies to CASPs + MiCA authorisation",detail:"MiCA-authorised CASPs providing services in the EU are DORA-in-scope. ICT risk management, third-party arrangements and resilience testing apply alongside MiCA prudential and safeguarding rules.",phase:1,remedy:"Align DORA ICT framework with MiCA authorisation and safeguarding requirements.",steps:["Confirm DORA framework is fit for a MiCA-authorised firm","Cover crypto-custody arrangements as ICT third-party arrangements","Include CASP-specific scenarios in resilience testing"]}]},\n'
    '        { value:"other-fin", label:"Other financial entity (crowdfunding, credit rating agency, benchmark administrator, etc.)", sev:"medium", findings:[{reg:"dora",a:"Art. 2",severity:"medium",title:"DORA proportionality applies",detail:"Smaller or specialised financial entities benefit from a proportionate regime but core ICT risk and third-party obligations still apply.",phase:2,remedy:"Confirm which proportionality carve-outs apply and document the rationale.",steps:["Confirm entity type and any simplified regime","Document proportionality decisions"]}]},',
)

# ---------------------------------------------------------------------------
# P2.4a — Q_G1: fix "health" wording in the highrisk option
# ---------------------------------------------------------------------------
EDIT_G1_WORDING = (
    '{ value:"highrisk", label:"Yes — high-risk AI (e.g. credit, health, employment, biometrics)", sev:"high", findings:[{reg:"aiact",a:"Art. 10, 12",severity:"high",title:"High-risk AI data-governance obligations",detail:"High-risk AI must meet Art. 10 data-governance requirements — relevant, representative, error-checked datasets with documented provenance — plus record-keeping and human oversight.",phase:1,remedy:"Implement AI Act data-governance controls and confirm training residency.",steps:["Classify AI systems against Annex III high-risk categories","Implement data-governance and provenance controls (Art. 10)","Confirm training/validation environments reside in approved regions","Establish record-keeping and human-oversight measures"]}]}',

    '{ value:"highrisk", label:"Yes — high-risk AI (e.g. credit scoring, life/health insurance pricing, employment/HR AI, biometric identification)", sev:"high", findings:[{reg:"aiact",a:"Art. 10, 12; Annex III items 1, 4, 5(b), 5(c)",severity:"high",title:"High-risk AI data-governance obligations",detail:"Annex III of the AI Act enumerates high-risk categories including biometric identification (item 1), employment/workforce management (item 4), creditworthiness (item 5(b)), and life/health insurance risk-and-pricing (item 5(c)). High-risk AI must meet Art. 10 data-governance requirements — relevant, representative, error-checked datasets with documented provenance — plus record-keeping and human oversight.",phase:1,remedy:"Implement AI Act data-governance controls and confirm training residency.",steps:["Classify AI systems against Annex III high-risk categories","Implement data-governance and provenance controls (Art. 10)","Confirm training/validation environments reside in approved regions","Establish record-keeping and human-oversight measures"]}]}',
)

# ---------------------------------------------------------------------------
# P2.4b — Insert Q_G3 (GPAI role) after Q_G2, before section H comment
# ---------------------------------------------------------------------------
INSERT_QG3_ANCHOR = '/* ============ H. CLOUD SOVEREIGNTY & ASSURANCE ============ */'
INSERT_QG3 = (
    '{\n'
    '      id:"G3", section:"ai", type:"single", text:"Do you use, embed or provide any general-purpose AI (GPAI) model in production (e.g. LLMs, foundation models)?",\n'
    '      help:"GPAI obligations under EU AI Act Chapter V (Arts. 51–56) attach differently depending on your role — provider, downstream user, or integrator.",\n'
    '      refs:[{reg:"aiact",a:"Chapter V, Arts. 51–56"}], appliesTo:{regulations:["aiact"]},\n'
    '      options:[\n'
    '        { value:"none", label:"No — we do not use GPAI", sev:"positive", findings:[]},\n'
    '        { value:"downstream", label:"Yes — we deploy third-party GPAI (downstream user)", sev:"low",\n'
    '          findings:[{reg:"aiact",a:"Art. 51–56",severity:"low",title:"GPAI downstream-user obligations",detail:"Downstream users of GPAI benefit from the transparency documentation provided by the GPAI provider, must respect copyright policy, and must ensure their use case does not silently turn a general model into an Annex III high-risk system without corresponding controls.",phase:2,remedy:"Integrate GPAI provider transparency documentation into your AI governance.",steps:["Obtain and archive GPAI provider transparency documentation","Ensure your use case does not create an unclassified high-risk system","Track EU AI Office guidance updates"]}]},\n'
    '        { value:"provider", label:"Yes — we develop / provide our own GPAI models placed on the EU market", sev:"high",\n'
    '          findings:[{reg:"aiact",a:"Art. 51–56",severity:"high",title:"GPAI provider obligations apply",detail:"Providers of GPAI models placed on the EU market are subject to Chapter V: technical documentation, transparency to downstream deployers, EU copyright compliance policy, publication of a training-data summary, cooperation with the AI Office. Systemic-risk GPAI (compute threshold under Art. 51(2)) owes additional model-evaluation, adversarial-testing and incident-reporting duties. GPAI provisions apply from 2 August 2025.",phase:1,remedy:"Stand up a GPAI compliance programme covering documentation, transparency, copyright and cooperation.",steps:["Produce technical documentation per AI Office template","Publish training-data summary","Adopt an EU copyright compliance policy","If systemic-risk: model evaluation, adversarial testing, cybersecurity, incident reporting"]}]},\n'
    '        { value:"integrator", label:"Yes — we embed third-party GPAI into products or services we sell", sev:"medium",\n'
    '          findings:[{reg:"aiact",a:"Art. 25",severity:"medium",title:"Integrator may become provider under Art. 25",detail:"Firms placing an AI system on the market under their own name may be treated as providers of the resulting system (Art. 25 — provider substitution). Assess whether provider-level obligations attach to the integrated system in addition to base-model provider obligations.",phase:2,remedy:"Assess Art. 25 provider-substitution risk for each integrated GPAI product.",steps:["Map each product embedding third-party GPAI","Determine if you place the system under your own name","Adopt provider-level obligations where applicable"]}]}\n'
    '      ]\n'
    '    },\n'
    '\n'
    '    /* ============ H. CLOUD SOVEREIGNTY & ASSURANCE ============ */'
)

# ---------------------------------------------------------------------------
# P2.5 — Q_H2: insert "Basic" between "substantial" and "none"
# ---------------------------------------------------------------------------
EDIT_H2_BASIC = (
    '{ value:"substantial", label:"Yes — Substantial assurance", sev:"low", findings:[{reg:"eucs",a:"Assurance",severity:"low",title:"Substantial assurance in place",detail:"Substantial assurance suits many workloads; the most sensitive or sovereignty-critical data may warrant High.",phase:3,remedy:"Confirm the assurance level matches your highest data classification.",steps:["Map workloads to required assurance levels","Escalate the most sensitive workloads to High where needed"]}]},',

    '{ value:"substantial", label:"Yes — Substantial assurance", sev:"low", findings:[{reg:"eucs",a:"Assurance",severity:"low",title:"Substantial assurance in place",detail:"Substantial assurance suits many workloads; the most sensitive or sovereignty-critical data may warrant High.",phase:3,remedy:"Confirm the assurance level matches your highest data classification.",steps:["Map workloads to required assurance levels","Escalate the most sensitive workloads to High where needed"]}]},\n'
    '        { value:"basic", label:"Yes — Basic assurance", sev:"medium",\n'
    '          findings:[{reg:"eucs",a:"Assurance — Basic",severity:"medium",title:"Basic assurance may under-serve regulated workloads",detail:"EUCS Basic covers low-sensitivity workloads. Regulated data — especially personal, financial, or special-category — typically requires Substantial or High assurance for defensibility.",phase:2,remedy:"Match assurance level to workload sensitivity; escalate regulated workloads above Basic.",steps:["Identify workloads currently on Basic-assured platforms","Reclassify per data sensitivity","Migrate or contract for Substantial or High assurance where needed"]}]},',
)

# ---------------------------------------------------------------------------
# P2.6 — Q_J1: cite DORA RTS 4h/72h/1-month cadence
# ---------------------------------------------------------------------------
EDIT_J1_RTS = (
    'refs:[{reg:"gdpr",a:"Art. 33"},{reg:"nis2",a:"Art. 23"},{reg:"dora",a:"Art. 19"}],',
    'refs:[{reg:"gdpr",a:"Art. 33"},{reg:"nis2",a:"Art. 23"},{reg:"dora",a:"Art. 19; Comm. Del. Reg. (EU) 2025/301 (initial 4h / intermediate 72h / final 1 month)"}],',
)
EDIT_J1_HELP = (
    'help:"GDPR requires notification within 72 hours; NIS2 requires an early warning within 24 hours and a full report within 72; DORA has its own major-incident timeline.",',
    'help:"GDPR requires notification within 72 hours; NIS2 requires an early warning within 24 hours and a full report within 72; DORA (via Commission Delegated Regulation (EU) 2025/301) requires initial notification within 4 hours of classifying an incident as major, an intermediate report within 72 hours, and a final report within 1 month.",',
)

# ---------------------------------------------------------------------------
# P2.7 — Q_B1: refine financial-data anchor
# ---------------------------------------------------------------------------
EDIT_B1_FINANCIAL = (
    '{ value:"financial", label:"Financial / transactional data (accounts, payments, cards)", sev:"high",\n'
    '          findings:[{reg:"dora",a:"Art. 5",severity:"high",title:"Financial data increases resilience obligations",detail:"Financial and payment data feeds critical functions; its residency and availability are central to DORA operational resilience.",phase:1,remedy:"Treat financial data stores as supporting critical or important functions.",steps:["Classify financial data stores by criticality","Confirm resilience and residency for each"]}]},',

    '{ value:"financial", label:"Financial / transactional data (accounts, payments, cards)", sev:"high",\n'
    '          findings:[{reg:"dora",a:"Art. 3 (definitions), Art. 5",severity:"high",title:"Financial data supports critical or important functions",detail:"Financial and payment data typically supports critical or important functions under DORA — its residency and availability drive operational-resilience obligations, ICT third-party clauses and the register of information. National banking-secrecy rules and, for card data, PCI DSS impose additional obligations.",phase:1,remedy:"Treat financial data stores as supporting critical or important functions; confirm PCI DSS scope for card data.",steps:["Classify financial data stores by criticality","Confirm PCI DSS scope for cardholder data","Confirm resilience and residency for each store"]}]},',
)

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
EDITS = [
    ("P2.1  Q_C1 add Oracle/IBM/Salesforce/Snowflake/Databricks", EDIT_C1_PROVIDERS),
    ("P2.2a Q_C2 rows +aitraining +government",                     EDIT_C2_ROWS),
    ("P2.2b Q_C2 add UK column",                                    EDIT_C2_UK_COL),
    ("P2.3  Q_A2 add payment-emi + casp options",                   EDIT_A2_ENTITIES),
    ("P2.4a Q_G1 fix health wording + Annex III items cited",       EDIT_G1_WORDING),
    ("P2.5  Q_H2 add Basic assurance option",                       EDIT_H2_BASIC),
    ("P2.6a Q_J1 refs cite DORA RTS 2025/301",                      EDIT_J1_RTS),
    ("P2.6b Q_J1 help text expanded",                               EDIT_J1_HELP),
    ("P2.7  Q_B1 financial anchor refined",                         EDIT_B1_FINANCIAL),
]

INSERTIONS = [
    ("P2.4b Q_G3 GPAI role question", INSERT_QG3_ANCHOR, INSERT_QG3, 'id:"G3"'),
]


def apply_edits(js: str) -> tuple[str, int]:
    applied = 0
    for label, (old, new) in EDITS:
        if old not in js:
            if new in js:
                print(f"  = {label}: already applied")
                continue
            print(f"  ! {label}: OLD NOT FOUND")
            continue
        js = js.replace(old, new, 1)
        applied += 1
        print(f"  ✓ {label}")
    for label, anchor, replacement, marker in INSERTIONS:
        if marker in js:
            print(f"  = {label}: already present ({marker})")
            continue
        if anchor not in js:
            print(f"  ! {label}: ANCHOR NOT FOUND")
            continue
        js = js.replace(anchor, replacement, 1)
        applied += 1
        print(f"  ✓ {label}")
    return js, applied


def semantic_check(js: str) -> None:
    if 'var BANK = {' not in js and 'const BANK = {' not in js:
        raise SystemExit("  ✗ BANK object missing — REFUSING TO SAVE")
    for needle, label in [
        ('value:"oracle-eu"',      'Q_C1 Oracle EU option'),
        ('value:"ibm-eu"',         'Q_C1 IBM Cloud EU option'),
        ('value:"salesforce"',     'Q_C1 Salesforce option'),
        ('value:"snowflake"',      'Q_C1 Snowflake option'),
        ('value:"databricks"',     'Q_C1 Databricks option'),
        ('id:"aitraining"',        'Q_C2 aitraining row'),
        ('id:"government"',        'Q_C2 government row'),
        ('id:"uk-only"',           'Q_C2 UK column'),
        ('value:"payment-emi"',    'Q_A2 payment-EMI option'),
        ('value:"casp"',           'Q_A2 CASP option'),
        ('life/health insurance pricing', 'Q_G1 wording fix'),
        ('id:"G3"',                'Q_G3 GPAI question'),
        ('value:"basic"',          'Q_H2 Basic assurance'),
        ('Comm. Del. Reg. (EU) 2025/301', 'Q_J1 DORA RTS reference'),
        ('PCI DSS scope',          'Q_B1 financial anchor refined'),
    ]:
        if needle not in js:
            raise SystemExit(f"  ✗ semantic check failed — missing: {label}   (needle {needle!r})")
    n_regs = len(re.findall(r'\{\s*id:"[a-z0-9_]+",\s*name:"[^"]+",\s*full:"', js))
    n_qs = len(re.findall(r'\bid:"[A-Z]\d+"', js))
    print(f"  ✓ semantic check OK ({n_regs} regulations, {n_qs} questions)")


def patch_bundled(path: pathlib.Path, dry_run: bool) -> int:
    raw = path.read_text(encoding="utf-8")
    m = re.search(r'<script type="__bundler/manifest">', raw)
    if not m:
        raise SystemExit(f"  ✗ manifest not found in {path}")
    end_tag = raw.find('</script>', m.end())
    manifest = json.loads(raw[m.end():end_tag])
    entry = manifest[JS_UUID]
    js = gzip.decompress(base64.b64decode(entry['data'])).decode('utf-8')
    js, applied = apply_edits(js)
    semantic_check(js)
    if dry_run:
        print(f"  (dry run — {path.name} not written)")
        return applied
    new_bytes = gzip.compress(js.encode('utf-8'))
    manifest[JS_UUID]['data'] = base64.b64encode(new_bytes).decode('ascii')
    new_manifest_str = json.dumps(manifest, separators=(',', ':'))
    new_raw = raw[:m.end()] + new_manifest_str + raw[end_tag:]
    path.write_text(new_raw, encoding="utf-8")
    print(f"  ✓ bundled rewritten: {path.name}  ({len(new_raw)-len(raw):+d} bytes)")
    return applied


def patch_unformatted(path: pathlib.Path, dry_run: bool) -> int:
    raw = path.read_text(encoding="utf-8")
    js, applied = apply_edits(raw)
    semantic_check(js)
    if dry_run:
        print(f"  (dry run — {path.name} not written)")
        return applied
    path.write_text(js, encoding="utf-8")
    print(f"  ✓ unformatted rewritten: {path.name}  ({len(js)-len(raw):+d} bytes)")
    return applied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=== UNFORMATTED ===")
    a1 = patch_unformatted(UNFORMATTED, args.dry_run)
    print("\n=== BUNDLED ===")
    a2 = patch_bundled(BUNDLED, args.dry_run)
    print(f"\nTotal edits applied: {a1 + a2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
