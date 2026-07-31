#!/usr/bin/env python3
"""DR&J Audit — Phase 3 patch (UK AI advisory regime).

Small, additive:

  P3.1  Add `ukai` regulation to regulations[]
        Extend autoSelectRegs() to derive ukai from UK footprint
        Add Q_G4 question in section G (AI), appliesTo:["ukai"]

Same gzipped-JS patch mechanics as Phases 1/2.
"""
import argparse, base64, gzip, json, pathlib, re, sys

BUNDLED = pathlib.Path("/home/user/ltm-core/Digital Sovereignty Data Residency Jurisdiction Audit/LTM-Data Residency & Jurisdiction Audit.html")
UNFORMATTED = pathlib.Path("/home/user/ltm-core/Digital Sovereignty Data Residency Jurisdiction Audit/Unformatted-Data-Residency-Jurisdiction-Audit.html")
JS_UUID = "d2614d21-bb06-46c7-aaeb-e4693103acbd"

# P3.1a — Add ukai regulation after ukctp (last one added in Phase 1)
EDIT_ADD_UKAI = (
    '{ id:"ukctp",   name:"UK CTP",       full:"Financial Services and Markets Act 2023, Part 9; FCA PS24/16; PRA PS16/24", tag:"UK · CTP oversight", desc:"HM Treasury designations of Critical Third Parties to the UK financial sector; joint FCA / PRA / BoE oversight; six Fundamental Rules." }\n  ],',

    '{ id:"ukctp",   name:"UK CTP",       full:"Financial Services and Markets Act 2023, Part 9; FCA PS24/16; PRA PS16/24", tag:"UK · CTP oversight", desc:"HM Treasury designations of Critical Third Parties to the UK financial sector; joint FCA / PRA / BoE oversight; six Fundamental Rules." },\n'
    '    { id:"ukai",    name:"UK AI approach", full:"ICO Guidance on AI and data protection; FCA AI update; PRA/BoE SS1/23 (Model risk management for AI/ML)", tag:"UK · principles-based AI regulation", desc:"UK operates a principles-based, regulator-led approach to AI rather than a UK equivalent of the EU AI Act. ICO guidance on AI and data protection, FCA supervisory expectations for AI in regulated activities, and PRA/BoE SS1/23 on model risk management for AI/ML apply. Track further UK regulatory evolution." }\n  ],'
)

# P3.1b — Auto-select ukai on UK footprint
EDIT_AUTOSELECT_UKAI = (
    "if(/UK/.test(fp)) { auto.add('ukgdpr'); auto.add('ukopres'); auto.add('ukctp'); }",
    "if(/UK/.test(fp)) { auto.add('ukgdpr'); auto.add('ukopres'); auto.add('ukctp'); auto.add('ukai'); }",
)

# P3.1c — Add Q_G4 UK AI question after Q_G3, before section H comment.
# Q_G3 was inserted in Phase 2 just before section H. Anchor: Q_G3's closing "}
# ]}" followed by ",\n\n    /* ============ H." — insert Q_G4 in between.
INSERT_QG4_ANCHOR = 'appliesTo:{regulations:["aiact"]},\n      options:[\n        { value:"none", label:"No — we do not use GPAI", sev:"positive", findings:[]}'
# We won't use the anchor approach for insertion because Q_G3 has multiple option blocks;
# safer to anchor on Q_G3's last option (integrator) closing "]}", "}", "},", followed by
# the section H comment.

# Approach: find the closing of Q_G3 by locating the specific integrator finding text,
# then find the "]},\n    },\n\n    /* ============ H." pattern.
INSERT_QG4_MARKER = 'id:"G4"'
INSERT_QG4_TEXT_ANCHOR = (
    '"Adopt provider-level obligations where applicable"]}]}\n'
    '      ]\n'
    '    },\n'
    '\n'
    '    /* ============ H. CLOUD SOVEREIGNTY & ASSURANCE ============ */'
)
INSERT_QG4_TEXT_REPLACEMENT = (
    '"Adopt provider-level obligations where applicable"]}]}\n'
    '      ]\n'
    '    },\n'
    '    {\n'
    '      id:"G4", section:"ai", type:"single", text:"For UK-established firms using AI/ML: how aligned is your AI governance with UK principles-based expectations (ICO / FCA / PRA)?",\n'
    '      help:"The UK follows a principles-based, regulator-led AI approach. ICO guidance on AI and data protection, FCA supervisory expectations for AI in regulated activities, and PRA/BoE SS1/23 on model risk management for AI/ML apply.",\n'
    '      refs:[{reg:"ukai",a:"ICO AI guidance; FCA AI update; PRA/BoE SS1/23"}], appliesTo:{regulations:["ukai"]},\n'
    '      options:[\n'
    '        { value:"aligned", label:"Yes — governance evidenced against ICO / FCA / PRA principles", sev:"positive", findings:[]},\n'
    '        { value:"partial", label:"Partial — awareness of ICO / FCA / PRA expectations, evidence incomplete", sev:"medium",\n'
    '          findings:[{reg:"ukai",a:"ICO / FCA / PRA principles",severity:"medium",title:"UK AI governance evidence incomplete",detail:"Principles-based expectations still require evidence — DPIAs for AI processing (ICO), consumer-duty and senior-manager accountability (FCA), and model risk governance (PRA/BoE SS1/23). Partial alignment is a common finding; document controls end-to-end.",phase:2,remedy:"Close the evidence gaps against each supervisor guideline.",steps:["Complete DPIAs for AI processing personal data (ICO)","Document FCA-relevant AI governance for regulated activities","Adopt SS1/23 model risk management framework for material AI/ML"]}]},\n'
    '        { value:"none", label:"No — UK AI governance not established", sev:"high",\n'
    '          findings:[{reg:"ukai",a:"ICO / FCA / PRA principles",severity:"high",title:"UK AI governance not established",detail:"Absence of AI governance in a UK-regulated firm exposes the firm to ICO enforcement on data-protection aspects and to FCA/PRA supervisory action for regulated activities. PRA/BoE SS1/23 is now the reference framework for banks and insurers on AI/ML model risk.",phase:1,remedy:"Stand up an AI governance framework aligned to the three UK supervisory streams.",steps:["Establish an AI governance forum with named executive owner","Complete DPIAs for AI processing (ICO)","Adopt SS1/23 model risk management principles","Align to FCA senior-manager accountability and consumer duty"]}]},\n'
    '        { value:"na", label:"Not applicable (no UK establishment or no AI use)", sev:"positive", findings:[] }\n'
    '      ]\n'
    '    },\n'
    '\n'
    '    /* ============ H. CLOUD SOVEREIGNTY & ASSURANCE ============ */'
)

# P3.1d — Add ukai to finserv / insurance sector.regs so any FS firm sees it
EDIT_FINSERV_UKAI = (
    'regs:["dora","gdpr","nis2","ukopres","ukctp","dataact"] },',
    'regs:["dora","gdpr","nis2","ukopres","ukctp","dataact","ukai"] },',
)

EDITS = [
    ("P3.1a Add ukai regulation",              EDIT_ADD_UKAI),
    ("P3.1b autoSelectRegs +ukai on UK",       EDIT_AUTOSELECT_UKAI),
    ("P3.1d finserv/insurance sector.regs +ukai (replace_all)",
     (EDIT_FINSERV_UKAI[0], EDIT_FINSERV_UKAI[1])),
]

INSERTIONS = [
    ("P3.1c Q_G4 UK AI question", INSERT_QG4_TEXT_ANCHOR, INSERT_QG4_TEXT_REPLACEMENT, INSERT_QG4_MARKER),
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
        # For the sector.regs edit, replace ALL occurrences (finserv + insurance both match)
        if 'sector.regs' in label:
            n_before = js.count(old)
            js = js.replace(old, new)  # replace all
            applied += 1
            print(f"  ✓ {label} ({n_before} occurrence(s))")
        else:
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
        raise SystemExit("  ✗ BANK missing")
    for needle, label in [
        ('id:"ukai"',       'ukai regulation'),
        ('id:"G4"',         'Q_G4 UK AI question'),
        ("auto.add('ukai')",'autoSelect ukai'),
        ('SS1/23',          'PRA/BoE SS1/23 reference'),
    ]:
        if needle not in js:
            raise SystemExit(f"  ✗ semantic check failed — missing: {label}")
    n_regs = len(re.findall(r'\{\s*id:"[a-z0-9_]+",\s*name:"[^"]+",\s*full:"', js))
    n_qs = len(re.findall(r'\bid:"[A-Z]\d+"', js))
    print(f"  ✓ semantic check OK ({n_regs} regulations, {n_qs} questions)")


def patch_bundled(path, dry_run):
    raw = path.read_text(encoding="utf-8")
    m = re.search(r'<script type="__bundler/manifest">', raw)
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
    print(f"  ✓ bundled rewritten ({len(new_raw)-len(raw):+d} bytes)")
    return applied


def patch_unformatted(path, dry_run):
    raw = path.read_text(encoding="utf-8")
    js, applied = apply_edits(raw)
    semantic_check(js)
    if dry_run:
        print(f"  (dry run — {path.name} not written)")
        return applied
    path.write_text(js, encoding="utf-8")
    print(f"  ✓ unformatted rewritten ({len(js)-len(raw):+d} bytes)")
    return applied


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    print("=== UNFORMATTED ==="); a1 = patch_unformatted(UNFORMATTED, args.dry_run)
    print("\n=== BUNDLED ==="); a2 = patch_bundled(BUNDLED, args.dry_run)
    print(f"\nTotal: {a1+a2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
