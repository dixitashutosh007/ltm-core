#!/usr/bin/env python3
"""DR&J Audit — Phase 1 patch (legal defensibility).

Implements the 4 highest-priority items from docs/DR-J-REVIEW.md:

  P1.1  DPF adequacy handling: Q_D1 (transfers), Q_C2 matrix (new
        us-dpf column + cellFindings), Q_F1 (backups), Q_G2 (AI compute)
  P1.2  Q_C1: split GCP into EU-only vs. includes-non-EU
  P1.3  Add EU Data Act, UK Op Res, UK CTP regulation blocks + one
        question each; wire into sector.regs and autoSelectRegs()
  P1.4  Q_H3: sovereign-controls follow-up (multi_select) — fixes the
        Q_H1 false-pass

Bundle structure:
  DR&J's KB lives in a gzip-compressed application/javascript entry
  inside <script type="__bundler/manifest">. This script:
    1. Extracts the manifest JSON
    2. Locates the JS entry (mime=application/javascript, compressed=true)
    3. base64-decodes + gunzips its data
    4. Applies text edits to the JS (the `var BANK = {...}` block)
    5. gzip-encodes + base64s back
    6. Rewrites the manifest JSON in the HTML
    7. Runs a semantic check: BANK sections/regulations/questions
       inventory matches expected post-patch counts.
  Also applies the same text edits to the readable sibling
  Unformatted-Data-Residency-Jurisdiction-Audit.html so the two stay
  in sync.

Idempotent — each edit checks whether it's already applied.

Deploys to *-staging.html only.
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
# All edits target the JS source of the BANK object. Each is (old, new).
# ---------------------------------------------------------------------------

# P1.2 — Q_C1: split GCP.  Uses REAL newlines (not r-string \n literals).
EDIT_GCP = (
    '{ value:"gcp", label:"Google Cloud", sev:"high",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"high",title:"US-operated hyperscaler in use",detail:"Default GCP configurations may replicate or process outside the EU; operator jurisdiction is the United States.",phase:2,remedy:"Confirm region residency and data-processing terms.",steps:["Confirm GCP region and residency settings","Review data-processing amendment terms"]}]}',

    '{ value:"gcp-eu", label:"Google Cloud — EU regions only", sev:"positive", findings:[]},\n'
    '        { value:"gcp-global", label:"Google Cloud — includes non-EU regions", sev:"high",\n'
    '          findings:[{reg:"gdpr",a:"Art. 44",severity:"high",title:"GCP workloads in non-EU regions",detail:"Non-EU GCP regions processing personal data create restricted transfers and potential CLOUD Act exposure via a US-controlled operator.",phase:1,remedy:"Region-lock personal-data workloads to EU GCP regions.",steps:["Audit GCP region configuration","Apply Organization Policy to restrict region deployment","Migrate non-compliant workloads"]}]}',
)

# P1.1a — Q_D1: add DPF option before "nomech"
EDIT_D1_DPF = (
    '{ value:"sccs", label:"Yes, under SCCs / IDTA with safeguards", sev:"medium", findings:[{reg:"gdpr",a:"Art. 46",severity:"medium",title:"Transfers rely on SCCs — verify supplementary measures",detail:"Post-Schrems II, SCCs alone are insufficient; a transfer impact assessment and supplementary measures are required, especially for US transfers.",phase:2,remedy:"Confirm a TIA and supplementary technical measures exist for each SCC transfer.",steps:["Confirm SCCs are the current (2021) modules","Complete a transfer impact assessment per destination","Implement supplementary measures (e.g. encryption with EU-held keys)"]}]},',

    '{ value:"sccs", label:"Yes, under SCCs / IDTA with safeguards", sev:"medium", findings:[{reg:"gdpr",a:"Art. 46",severity:"medium",title:"Transfers rely on SCCs — verify supplementary measures",detail:"Post-Schrems II, SCCs alone are insufficient; a transfer impact assessment and supplementary measures are required, especially for US transfers.",phase:2,remedy:"Confirm a TIA and supplementary technical measures exist for each SCC transfer.",steps:["Confirm SCCs are the current (2021) modules","Complete a transfer impact assessment per destination","Implement supplementary measures (e.g. encryption with EU-held keys)"]}]},\n'
    '        { value:"sccs-dpf", label:"Yes — to US recipients certified under the EU-US Data Privacy Framework (DPF)", sev:"low", findings:[{reg:"gdpr",a:"Art. 45",severity:"low",title:"Transfers relying on EU-US DPF adequacy",detail:"US recipients certified under the EU-US Data Privacy Framework (Commission Implementing Decision (EU) 2023/1795, 10 July 2023) benefit from adequacy. Reconfirm the recipient DPF certification periodically — a future CJEU challenge remains possible; UK-established firms can additionally rely on the UK-US Data Bridge extension (October 2023).",phase:2,remedy:"Maintain the DPF certification check and a fallback (SCCs + TIA) in case adequacy lapses.",steps:["Verify each US recipient on the DPF Program list at commerce.gov","Document reliance on DPF adequacy in your RoPA","Prepare SCC + TIA fallback documentation"]}]},'
)

# P1.1b — Q_C2 matrix: add us-dpf column
EDIT_C2_COLS = (
    'cols:[\n'
    '        { id:"eu-only", label:"EU region only", sev:"positive" },\n'
    '        { id:"eu-backup", label:"EU + encrypted non-EU backup", sev:"low" },\n'
    '        { id:"us-cloud", label:"US / non-EU cloud", sev:"critical" },\n'
    '        { id:"multi", label:"Multi-region global", sev:"high" },\n'
    '        { id:"unknown", label:"Unknown", sev:"high" }\n'
    '      ],',

    'cols:[\n'
    '        { id:"eu-only", label:"EU region only", sev:"positive" },\n'
    '        { id:"eu-backup", label:"EU + encrypted non-EU backup", sev:"low" },\n'
    '        { id:"us-dpf", label:"US cloud with DPF-certified processor", sev:"low" },\n'
    '        { id:"us-cloud", label:"US / non-EU cloud (no DPF)", sev:"critical" },\n'
    '        { id:"multi", label:"Multi-region global", sev:"high" },\n'
    '        { id:"unknown", label:"Unknown", sev:"high" }\n'
    '      ],',
)

# P1.1c — Q_C2 matrix: add us-dpf cellFinding
EDIT_C2_CELLFINDINGS = (
    '"unknown":{reg:"gdpr",a:"Art. 30",severity:"high",title:"Location of {row} is unknown",detail:"You cannot demonstrate compliance for data whose location you cannot state. This is a visibility gap that must be closed first.",phase:1,remedy:"Run data discovery to locate {rowlower}.",steps:["Run automated data discovery for {rowlower}","Record findings in the RoPA"]},',

    '"unknown":{reg:"gdpr",a:"Art. 30",severity:"high",title:"Location of {row} is unknown",detail:"You cannot demonstrate compliance for data whose location you cannot state. This is a visibility gap that must be closed first.",phase:1,remedy:"Run data discovery to locate {rowlower}.",steps:["Run automated data discovery for {rowlower}","Record findings in the RoPA"]},\n'
    '        "us-dpf":{reg:"gdpr",a:"Art. 45",severity:"low",title:"{row} transferred to a DPF-certified US processor",detail:"Transfers of {rowlower} to US recipients certified under the EU-US Data Privacy Framework benefit from adequacy. Schrems-III risk remains open — reconfirm certification periodically.",phase:2,remedy:"Verify DPF certification and maintain SCC + TIA fallback for {rowlower}.",steps:["Verify recipient on commerce.gov Data Privacy Framework Program list","Document DPF reliance in the RoPA","Maintain SCC fallback"]},',
)

# P1.1d — Q_F1: split "us" and add "us-dpf"
EDIT_F1_DPF = (
    '{ value:"us", label:"US / non-EU based backup", sev:"critical", findings:[{reg:"gdpr",a:"Art. 32, 44",severity:"critical",title:"Backups stored in a non-EU jurisdiction",detail:"Non-EU backups replicate every residency and transfer exposure of the primary, often silently and at full data volume.",phase:1,remedy:"Region-lock backups to the EU as an immediate action.",steps:["Reconfigure backup targets to EU regions","Purge or migrate existing non-EU backup copies","Verify retention/deletion of migrated copies"]}]},',

    '{ value:"us-dpf", label:"US-based, with DPF-certified backup provider", sev:"low", findings:[{reg:"gdpr",a:"Art. 45",severity:"low",title:"US backup relying on DPF adequacy",detail:"Backups stored with a DPF-certified US recipient rely on adequacy; the backup is still a transfer and DPF certification must be maintained and reconfirmed periodically.",phase:2,remedy:"Verify and monitor the backup provider DPF certification status.",steps:["Verify the backup provider on commerce.gov Data Privacy Framework Program list","Document reliance in the RoPA","Maintain SCC fallback in case adequacy lapses"]}]},\n'
    '        { value:"us", label:"US / non-EU based backup (no DPF)", sev:"critical", findings:[{reg:"gdpr",a:"Art. 32, 44",severity:"critical",title:"Backups stored in a non-EU jurisdiction",detail:"Non-EU backups replicate every residency and transfer exposure of the primary, often silently and at full data volume. Without DPF adequacy or another Chapter V mechanism, this is a direct GDPR breach.",phase:1,remedy:"Region-lock backups to the EU as an immediate action, or move to a DPF-certified provider.",steps:["Reconfigure backup targets to EU regions","Purge or migrate existing non-EU backup copies","Verify retention/deletion of migrated copies"]}]},',
)

# P1.1e — Q_G2: split "us" and add "us-dpf"
EDIT_G2_DPF = (
    '{ value:"us", label:"Primarily US / non-EU compute", sev:"critical", findings:[{reg:"gdpr",a:"Art. 44",severity:"critical",title:"AI compute located outside the EU",detail:"Running training/inference on sensitive data in non-EU regions is a restricted transfer at scale, frequently undocumented, and may breach DORA and the AI Act simultaneously.",phase:1,remedy:"Repatriate sensitive AI compute to the EU or an approved sovereign platform.",steps:["Identify all non-EU AI compute touching sensitive data","Migrate to EU / sovereign ML platforms","Implement provenance tracking for training data"]}]},',

    '{ value:"us-dpf", label:"Primarily US / non-EU compute, with DPF-certified provider", sev:"medium", findings:[{reg:"gdpr",a:"Art. 45",severity:"medium",title:"AI compute at DPF-certified US provider",detail:"Running training/inference on sensitive data at a DPF-certified US recipient benefits from adequacy; residual Schrems-III risk plus DORA and AI Act residency and record-keeping obligations still apply.",phase:2,remedy:"Verify DPF certification and add AI-specific contractual controls; consider sovereign alternatives for the most sensitive workloads.",steps:["Verify the AI compute provider on commerce.gov Data Privacy Framework Program list","Add AI-specific data-protection and data-provenance terms","Consider EU sovereign AI compute for the most sensitive workloads"]}]},\n'
    '        { value:"us", label:"Primarily US / non-EU compute (no DPF)", sev:"critical", findings:[{reg:"gdpr",a:"Art. 44",severity:"critical",title:"AI compute located outside the EU",detail:"Running training/inference on sensitive data in non-EU regions without a valid Chapter V mechanism is a restricted transfer at scale, frequently undocumented, and may breach DORA and the AI Act simultaneously.",phase:1,remedy:"Repatriate sensitive AI compute to the EU or an approved sovereign platform, or move to a DPF-certified provider.",steps:["Identify all non-EU AI compute touching sensitive data","Migrate to EU / sovereign ML platforms","Implement provenance tracking for training data"]}]},',
)

# P1.3a — Add 3 regulation entries after "eucs" entry
REGULATIONS_ANCHOR = (
    '{ id:"eucs",   name:"EUCS",        full:"EU Cybersecurity Certification Scheme for Cloud Services", tag:"EU · Cloud assurance", desc:"Assurance levels (Basic/Substantial/High) and sovereignty-related requirements for cloud services." }\n  ],'
)
REGULATIONS_INSERT = (
    '{ id:"eucs",   name:"EUCS",        full:"EU Cybersecurity Certification Scheme for Cloud Services", tag:"EU · Cloud assurance", desc:"Assurance levels (Basic/Substantial/High) and sovereignty-related requirements for cloud services." },\n'
    '    { id:"dataact", name:"EU Data Act",  full:"Regulation (EU) 2023/2854 on harmonised rules on fair access to and use of data", tag:"EU · cloud switching & non-personal data access", desc:"Cloud switching and portability obligations for data-processing services; safeguards against unlawful third-country access to non-personal data held in the EU. Applies from 12 September 2025; switching provisions phased." },\n'
    '    { id:"ukopres", name:"UK Op Res",    full:"FCA PS21/3; PRA SS2/21 — Operational Resilience", tag:"UK · financial services resilience", desc:"Impact tolerances for important business services, mapping, scenario testing, self-assessment and outsourcing / third-party risk expectations." },\n'
    '    { id:"ukctp",   name:"UK CTP",       full:"Financial Services and Markets Act 2023, Part 9; FCA PS24/16; PRA PS16/24", tag:"UK · CTP oversight", desc:"HM Treasury designations of Critical Third Parties to the UK financial sector; joint FCA / PRA / BoE oversight; six Fundamental Rules." }\n  ],'
)

# P1.3b — Update finserv sector.regs to include ukopres/ukctp/dataact
EDIT_FINSERV_REGS = (
    r'{ id:"finserv",   name:"Banking & capital markets", high:true,  regs:["dora","gdpr","nis2"] },',
    r'{ id:"finserv",   name:"Banking & capital markets", high:true,  regs:["dora","gdpr","nis2","ukopres","ukctp","dataact"] },',
)

# P1.3c — Update insurance sector.regs
EDIT_INSURANCE_REGS = (
    r'{ id:"insurance", name:"Insurance & pensions",       high:true,  regs:["dora","gdpr","nis2"] },',
    r'{ id:"insurance", name:"Insurance & pensions",       high:true,  regs:["dora","gdpr","nis2","ukopres","ukctp","dataact"] },',
)

# P1.3d — Update diginfra sector.regs to include dataact (cloud providers)
EDIT_DIGINFRA_REGS = (
    r'{ id:"diginfra",  name:"Digital infrastructure / cloud", high:true, regs:["nis2","eucs","gdpr"] },',
    r'{ id:"diginfra",  name:"Digital infrastructure / cloud", high:true, regs:["nis2","eucs","gdpr","dataact"] },',
)

# P1.3e — Extend autoSelectRegs() to add UK and Data Act based on footprint
EDIT_AUTOSELECT = (
    "const fp=document.getElementById('org-footprint').value||'';\n"
    "  if(/UK/.test(fp)) auto.add('ukgdpr');\n"
    "  if(fp) auto.add('gdpr');",

    "const fp=document.getElementById('org-footprint').value||'';\n"
    "  if(/UK/.test(fp)) { auto.add('ukgdpr'); auto.add('ukopres'); auto.add('ukctp'); }\n"
    "  if(fp) { auto.add('gdpr'); auto.add('dataact'); }",
)

# ---------------------------------------------------------------------------
# INSERTIONS — new questions
# ---------------------------------------------------------------------------

# P1.3 — Q_D3 (Data Act) — insert after Q_D2, before section E comment
INSERT_QD3_ANCHOR = r'/* ============ E. THIRD-PARTY PROCESSORS & ICT SUPPLY CHAIN ============ */'
INSERT_QD3 = (
    r'{\n      id:"D3", section:"transfers", type:"single", text:"Do you rely on any cloud or data-processing service that would be subject to EU Data Act switching / portability obligations?",\n      help:"The Data Act (Regulation (EU) 2023/2854) applies from 12 September 2025; cloud switching provisions phase in later. Providers and their customers both have roles.",\n      refs:[{reg:"dataact",a:"Chapter VIII"}], appliesTo:{regulations:["dataact"]},\n      options:[\n        { value:"customer", label:"Yes — as a customer of cloud / data-processing services", sev:"low",\n          findings:[{reg:"dataact",a:"Chapter VIII",severity:"low",title:"Data Act switching rights available",detail:"As a customer, the Data Act grants you rights to switch and port data between providers on transparent terms; ensure your contracts reflect these rights.",phase:2,remedy:"Review provider contracts for Data Act switching / portability terms.",steps:["Confirm contract includes Data Act switching provisions","Verify functional-equivalence obligations","Track upcoming Data Act commencement milestones"]}]},\n        { value:"provider", label:"Yes — as a provider of cloud / data-processing services", sev:"high",\n          findings:[{reg:"dataact",a:"Chapter VIII",severity:"high",title:"Data Act provider obligations apply",detail:"As a provider, you must facilitate customer switching, ensure portability of exportable data, meet contractual-fairness rules, and safeguard against unlawful third-country access to non-personal data held in the EU.",phase:1,remedy:"Build a Data Act compliance programme covering switching, portability and non-personal-data access safeguards.",steps:["Document switching / portability procedures","Update customer contracts for Data Act terms","Implement safeguards against unlawful third-country access to non-personal data"]}]},\n        { value:"na", label:"Not applicable / EU Data Act not in scope", sev:"positive", findings:[] }\n      ]\n    },\n\n    /* ============ E. THIRD-PARTY PROCESSORS & ICT SUPPLY CHAIN ============ */'
)

# P1.3 — Q_F5 (UK Op Res) — insert before section G comment
INSERT_QF5_ANCHOR = r'/* ============ G. AI SYSTEMS & DATA GOVERNANCE ============ */'
INSERT_QF5 = (
    r'{\n      id:"F5", section:"resilience", type:"single", text:"For UK-regulated financial firms: are impact tolerances set for important business services (UK Operational Resilience)?",\n      help:"FCA PS21/3 and PRA SS2/21 require identification of important business services, impact tolerances, mapping and scenario testing. Since March 2025, firms must be able to remain within tolerances for severe-but-plausible scenarios.",\n      refs:[{reg:"ukopres",a:"FCA PS21/3; PRA SS2/21"}], appliesTo:{regulations:["ukopres"]},\n      options:[\n        { value:"yes", label:"Yes — impact tolerances set, mapping and testing complete", sev:"positive", findings:[]},\n        { value:"partial", label:"Partial — tolerances set but mapping / testing incomplete", sev:"medium",\n          findings:[{reg:"ukopres",a:"FCA PS21/3",severity:"medium",title:"UK Op Res mapping / testing incomplete",detail:"Impact tolerances without complete mapping and scenario testing cannot be shown to be defensible against a severe-but-plausible disruption. Post-March 2025 supervisory expectations require evidence.",phase:2,remedy:"Complete mapping of important business services and scenario testing.",steps:["Complete mapping to underlying resources incl. ICT and data locations","Run severe-but-plausible scenario tests","Update the self-assessment document"]}]},\n        { value:"no", label:"No — not yet established", sev:"high",\n          findings:[{reg:"ukopres",a:"PRA SS2/21",severity:"high",title:"UK operational-resilience framework not established",detail:"Post-March 2025, the FCA and PRA expect firms to be able to demonstrate they can remain within impact tolerances for important business services. Absence is a material gap.",phase:1,remedy:"Stand up the UK Op Res framework as a priority.",steps:["Identify important business services","Set impact tolerances","Map underlying resources","Design and run scenario tests","Produce the self-assessment"]}]},\n        { value:"na", label:"Not applicable (non-UK / non-FS)", sev:"positive", findings:[] }\n      ]\n    },\n\n    /* ============ G. AI SYSTEMS & DATA GOVERNANCE ============ */'
)

# P1.4 + P1.3 — Q_H3 (sovereign controls) + Q_I3 (UK CTP) — insert both before section I / J respectively
INSERT_QH3_ANCHOR = r'/* ============ I. GOVERNANCE, CONTRACTS & AUDIT RIGHTS ============ */'
INSERT_QH3 = (
    r'{\n      id:"H3", section:"cloud", type:"multi", text:"For any \'sovereign-boundary\' or EU-controlled cloud offering, which controls are contractually and operationally in place?",\n      help:"An offering marketed as \'sovereign\' but without contractual, operational and cryptographic controls is not sovereign in a legal sense. This question fires the evidence side of Q_H1.",\n      refs:[{reg:"eucs",a:"Sovereignty"},{reg:"gdpr",a:"Art. 32, 44"}],\n      options:[\n        { value:"eu-personnel", label:"EU-only operations personnel (customer support and platform operators are EU nationals)", sev:"positive", findings:[]},\n        { value:"hyok", label:"Customer-held encryption keys (HYOK / EU-controlled KMS)", sev:"positive", findings:[]},\n        { value:"antidisclosure", label:"Contractual protection against extraterritorial disclosure requests (e.g. CLOUD Act, FISA §702)", sev:"positive", findings:[]},\n        { value:"eu-subprocessors", label:"Sub-processor list restricted to EU-jurisdiction entities", sev:"positive", findings:[]},\n        { value:"local-entity", label:"Local operating entity with EU jurisdiction of dispute resolution", sev:"positive", findings:[]},\n        { value:"none", label:"None of the above / not documented", sev:"high",\n          findings:[{reg:"eucs",a:"Sovereignty",severity:"high",title:"Sovereign offering claimed without documented controls",detail:"An offering marketed as \'sovereign\' but without documented EU-personnel operations, customer-held keys, anti-disclosure clauses or sub-processor limits is not sovereign in a legal sense — CLOUD Act and other extraterritorial exposures remain.",phase:1,remedy:"Document each sovereignty control contractually or select a genuinely sovereign platform.",steps:["Request contractual evidence for each sovereignty claim","Verify EU-personnel operations model","Confirm key custody arrangements","Restrict sub-processor list to EU jurisdictions"]}]}\n      ]\n    },\n\n    /* ============ I. GOVERNANCE, CONTRACTS & AUDIT RIGHTS ============ */'
)

INSERT_QI3_ANCHOR = r'/* ============ J. INCIDENT DETECTION & REPORTING ============ */'
INSERT_QI3 = (
    r'{\n      id:"I3", section:"governance", type:"single", text:"For UK-regulated financial firms: do you rely on providers that may be designated Critical Third Parties (CTPs) under FSMA 2023?",\n      help:"HM Treasury (on recommendation of FCA / PRA / BoE) designates CTPs. Designated CTPs are subject to six Fundamental Rules and joint FCA / PRA / BoE oversight. The rules bind the provider, but your own resilience accountability is undiminished.",\n      refs:[{reg:"ukctp",a:"FSMA 2023 Part 9; FCA PS24/16; PRA PS16/24"}], appliesTo:{regulations:["ukctp"]},\n      options:[\n        { value:"yes", label:"Yes — we rely on likely / designated CTPs and understand our own residual duties", sev:"low",\n          findings:[{reg:"ukctp",a:"FSMA 2023 Part 9",severity:"low",title:"CTP dependency identified and managed",detail:"CTP designations bind the provider under FCA / PRA / BoE oversight, but your own outsourcing, resilience and exit-planning duties are undiminished. Maintain governance directly.",phase:2,remedy:"Maintain outsourcing governance and exit-plan readiness for CTP arrangements.",steps:["Identify all critical arrangements with likely CTPs","Confirm outsourcing controls remain in place","Update exit plans and concentration-risk analysis"]}]},\n        { value:"unsure", label:"Unsure — CTP status of key providers not established", sev:"medium",\n          findings:[{reg:"ukctp",a:"FSMA 2023",severity:"medium",title:"CTP dependency status unclear",detail:"Not knowing which of your providers is (or may be) a designated CTP prevents effective concentration-risk and exit-plan design.",phase:2,remedy:"Establish which providers are likely CTPs and plan accordingly.",steps:["List providers supporting important business services","Assess likelihood of CTP designation via HM Treasury","Refresh concentration-risk analysis"]}]},\n        { value:"no", label:"No — no material CTP dependencies", sev:"positive", findings:[]},\n        { value:"na", label:"Not applicable (non-UK / non-FS)", sev:"positive", findings:[] }\n      ]\n    },\n\n    /* ============ J. INCIDENT DETECTION & REPORTING ============ */'
)

EDITS = [
    ("P1.2  Q_C1 GCP split",                 EDIT_GCP),
    ("P1.1a Q_D1 DPF option",                EDIT_D1_DPF),
    ("P1.1b Q_C2 matrix us-dpf column",      EDIT_C2_COLS),
    ("P1.1c Q_C2 matrix us-dpf cellFinding", EDIT_C2_CELLFINDINGS),
    ("P1.1d Q_F1 us-dpf split",              EDIT_F1_DPF),
    ("P1.1e Q_G2 us-dpf split",              EDIT_G2_DPF),
    ("P1.3a Add Data Act + UK Op Res + UK CTP to regulations[]", (REGULATIONS_ANCHOR, REGULATIONS_INSERT)),
    ("P1.3b finserv sector.regs",            EDIT_FINSERV_REGS),
    ("P1.3c insurance sector.regs",          EDIT_INSURANCE_REGS),
    ("P1.3d diginfra sector.regs",           EDIT_DIGINFRA_REGS),
    ("P1.3e autoSelectRegs() extended",      EDIT_AUTOSELECT),
]

INSERTIONS = [
    ("P1.3 Q_D3 Data Act question",              INSERT_QD3_ANCHOR, INSERT_QD3, r'id:"D3"'),
    ("P1.3 Q_F5 UK Op Res question",             INSERT_QF5_ANCHOR, INSERT_QF5, r'id:"F5"'),
    ("P1.4 Q_H3 sovereign-controls follow-up",   INSERT_QH3_ANCHOR, INSERT_QH3, r'id:"H3"'),
    ("P1.3 Q_I3 UK CTP question",                INSERT_QI3_ANCHOR, INSERT_QI3, r'id:"I3"'),
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
    # BANK must still open + close, regulations must include the 3 new ones,
    # questions must include D3/F5/H3/I3.
    if 'var BANK = {' not in js and 'const BANK = {' not in js:
        raise SystemExit("  ✗ BANK object no longer present — REFUSING TO SAVE")
    for needle, label in [
        ('id:"dataact"', 'Data Act regulation'),
        ('id:"ukopres"', 'UK Op Res regulation'),
        ('id:"ukctp"',   'UK CTP regulation'),
        ('id:"D3"',      'Q_D3 Data Act question'),
        ('id:"F5"',      'Q_F5 UK Op Res question'),
        ('id:"H3"',      'Q_H3 sovereign controls'),
        ('id:"I3"',      'Q_I3 UK CTP question'),
        ('value:"gcp-eu"',   'Q_C1 GCP EU option'),
        ('value:"gcp-global"','Q_C1 GCP global option'),
        ('value:"sccs-dpf"', 'Q_D1 DPF option'),
        ('id:"us-dpf"',      'Q_C2 us-dpf column'),
        ('"us-dpf":{reg:"gdpr"', 'Q_C2 us-dpf cellFinding'),
        ('value:"us-dpf"',       'Q_F1 / Q_G2 us-dpf option'),
    ]:
        if needle not in js:
            raise SystemExit(f"  ✗ semantic check failed — missing: {label}   (needle {needle!r})")
    # Regime count: 6 original + 3 new = 9. IDs include digits (nis2) so use [a-z0-9_]+.
    n_regs = len(re.findall(r'\{\s*id:"[a-z0-9_]+",\s*name:"[^"]+",\s*full:"', js))
    if n_regs < 9:
        raise SystemExit(f"  ✗ semantic check failed — expected ≥ 9 regulations, found {n_regs}")
    # Question count: 29 original + 4 new = 33
    n_qs = len(re.findall(r'\bid:"[A-Z]\d+"', js))
    if n_qs < 33:
        raise SystemExit(f"  ✗ semantic check failed — expected ≥ 33 questions, found {n_qs}")
    print(f"  ✓ semantic check OK ({n_regs} regulations, {n_qs} questions)")


def patch_bundled(path: pathlib.Path, dry_run: bool) -> int:
    raw = path.read_text(encoding="utf-8")
    m = re.search(r'<script type="__bundler/manifest">', raw)
    if not m:
        raise SystemExit(f"  ✗ manifest not found in {path}")
    end_tag = raw.find('</script>', m.end())
    manifest_str = raw[m.end():end_tag]
    manifest = json.loads(manifest_str)
    entry = manifest[JS_UUID]
    js = gzip.decompress(base64.b64decode(entry['data'])).decode('utf-8')

    js, applied = apply_edits(js)
    semantic_check(js)

    if dry_run:
        print(f"  (dry run — {path.name} not written)")
        return applied

    # Recompress and re-encode
    new_bytes = gzip.compress(js.encode('utf-8'))
    manifest[JS_UUID]['data'] = base64.b64encode(new_bytes).decode('ascii')
    new_manifest_str = json.dumps(manifest, separators=(',', ':'))
    new_raw = raw[:m.end()] + new_manifest_str + raw[end_tag:]
    path.write_text(new_raw, encoding="utf-8")
    print(f"  ✓ bundled file rewritten: {path.name}  ({len(new_raw)-len(raw):+d} bytes)")
    return applied


def patch_unformatted(path: pathlib.Path, dry_run: bool) -> int:
    raw = path.read_text(encoding="utf-8")
    js, applied = apply_edits(raw)
    semantic_check(js)
    if dry_run:
        print(f"  (dry run — {path.name} not written)")
        return applied
    path.write_text(js, encoding="utf-8")
    print(f"  ✓ unformatted file rewritten: {path.name}  ({len(js)-len(raw):+d} bytes)")
    return applied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=== UNFORMATTED (readable sibling) ===")
    a1 = patch_unformatted(UNFORMATTED, args.dry_run)
    print(f"\n=== BUNDLED (LTM production build) ===")
    a2 = patch_bundled(BUNDLED, args.dry_run)
    print(f"\nTotal edits applied: {a1 + a2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
