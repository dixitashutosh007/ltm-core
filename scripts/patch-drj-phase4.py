#!/usr/bin/env python3
"""DR&J Audit — Phase 4 patch (ongoing / hygiene).

Additive changes plus one algorithm fix.

  P4.1  Add sources:[{name,url}] arrays to all 10 regulations
  P4.2  Bump BANK.meta.version 1.0.0 → 1.3.0; updated → 2026-07-31;
        add framework stamp to coverBlock() report cover
  P4.3  Fix ragForRegulation: return grey when a regulation is
        referenced but no question about it has been answered
        (currently returns green misleadingly)

Same guards as prior phases: semantic + JS-syntax check.
"""
import argparse, base64, gzip, json, pathlib, re, sys

BUNDLED = pathlib.Path("/home/user/ltm-core/Digital Sovereignty Data Residency Jurisdiction Audit/LTM-Data Residency & Jurisdiction Audit.html")
UNFORMATTED = pathlib.Path("/home/user/ltm-core/Digital Sovereignty Data Residency Jurisdiction Audit/Unformatted-Data-Residency-Jurisdiction-Audit.html")
JS_UUID = "d2614d21-bb06-46c7-aaeb-e4693103acbd"

# ---------------------------------------------------------------------------
# P4.1 — sources per regulation. Each edit appends ", sources:[…]" before the
# regulation's closing "}", identified by the unique final "desc:" text.
# ---------------------------------------------------------------------------
SOURCES = {
    "gdpr": [
        ("Regulation (EU) 2016/679 (GDPR) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2016/679/oj"),
        ("EDPB — European Data Protection Board",     "https://edpb.europa.eu/edpb_en"),
        ("EU-US Data Privacy Framework — Commission", "https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/eu-us-data-privacy-framework_en"),
    ],
    "ukgdpr": [
        ("UK GDPR — legislation.gov.uk (retained)", "https://www.legislation.gov.uk/eur/2016/679/contents"),
        ("Data Protection Act 2018",                 "https://www.legislation.gov.uk/ukpga/2018/12/contents"),
        ("PECR (SI 2003/2426)",                      "https://www.legislation.gov.uk/uksi/2003/2426/contents"),
        ("Data (Use and Access) Act 2025",           "https://www.legislation.gov.uk/ukpga/2025/18"),
        ("ICO",                                       "https://ico.org.uk/"),
    ],
    "nis2": [
        ("Directive (EU) 2022/2555 (NIS2) — EUR-Lex", "https://eur-lex.europa.eu/eli/dir/2022/2555/oj"),
        ("ENISA — NIS Directive hub",                 "https://www.enisa.europa.eu/topics/nis-directive"),
    ],
    "dora": [
        ("Regulation (EU) 2022/2554 (DORA) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2022/2554/oj"),
        ("Commission — DORA implementing acts",        "https://finance.ec.europa.eu/regulation-and-supervision/financial-services-legislation/implementing-and-delegated-acts/digital-operational-resilience-act_en"),
        ("EBA — DORA hub",                             "https://www.eba.europa.eu/regulation-and-policy/digital-operational-resilience-act-dora"),
    ],
    "aiact": [
        ("Regulation (EU) 2024/1689 (AI Act) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"),
        ("Commission — EU AI Act",                       "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai"),
    ],
    "eucs": [
        ("Regulation (EU) 2019/881 (Cybersecurity Act) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2019/881/oj"),
        ("ENISA — EUCS candidate scheme",                          "https://www.enisa.europa.eu/topics/certification/eucs-cloud-services-scheme"),
    ],
    "dataact": [
        ("Regulation (EU) 2023/2854 (Data Act) — EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2023/2854/oj"),
        ("Commission — EU Data Act",                       "https://digital-strategy.ec.europa.eu/en/policies/data-act"),
    ],
    "ukopres": [
        ("FCA PS21/3 — Building operational resilience", "https://www.fca.org.uk/publications/policy-statements/ps21-3-building-operational-resilience"),
        ("PRA SS2/21 — Operational resilience",          "https://www.bankofengland.co.uk/prudential-regulation/publication/2021/march/operational-resilience-impact-tolerances-for-important-business-services-ss"),
        ("Bank of England — Operational resilience",     "https://www.bankofengland.co.uk/prudential-regulation/regulation/operational-resilience"),
    ],
    "ukctp": [
        ("FSMA 2023 — Critical Third Parties (Part 9)", "https://www.legislation.gov.uk/ukpga/2023/29/contents"),
        ("FCA PS24/16 — Operational resilience: CTPs",  "https://www.fca.org.uk/publications/policy-statements/ps24-16-operational-resilience-critical-third-parties"),
        ("PRA PS16/24 — CTPs to the UK financial sector","https://www.bankofengland.co.uk/prudential-regulation/publication/2024/november/operational-resilience-critical-third-parties-to-the-uk-financial-sector"),
    ],
    "ukai": [
        ("ICO — Guidance on AI and data protection", "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/"),
        ("FCA — AI update",                          "https://www.fca.org.uk/publications/corporate-documents/our-approach-artificial-intelligence"),
        ("PRA / Bank of England SS1/23 — Model risk", "https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss"),
        ("UK Government — Pro-innovation approach to AI", "https://www.gov.uk/government/publications/ai-regulation-a-pro-innovation-approach"),
    ],
}

# Each regulation's line ends with `desc:"..." }` (with no comma before the
# closing `}` because it's the last field). We'll match up to the final `}`
# and inject `, sources:[…]` right before it.
# Format used in the file per regulation:
#   { id:"...", name:"...", full:"...", tag:"...", desc:"..." }
# We locate each regulation by its unique `id:"…"` and match to the closing brace.

def build_source_edits():
    """Return list of (old, new) tuples for each regulation."""
    edits = []
    for rid, src_list in SOURCES.items():
        # Build the sources array string
        items = ",".join(f'{{name:"{n}",url:"{u}"}}' for n, u in src_list)
        # The precise "old" pattern per regulation: matches from `desc:"…"` through the
        # closing `}` and up to the trailing `,` (or `}`) delimiter. Since each
        # regulation is followed by `,` or a closing array bracket, we anchor on the
        # `id:"…"` + `desc` + `}` pattern uniquely.
        # We use a regex-friendly replacement below in apply_edits.
        edits.append((rid, items))
    return edits


REGEX_SOURCE_INJECT = re.compile(
    r'(\{\s*id:"(?P<rid>[a-z0-9_]+)"[^{}]*?desc:"[^"]*"\s*)(\})',
    re.DOTALL,
)


def inject_sources(js: str, source_edits) -> tuple[str, int]:
    src_map = dict(source_edits)  # rid -> items string
    applied = 0
    def repl(m):
        nonlocal applied
        rid = m.group('rid')
        if rid not in src_map:
            return m.group(0)
        # Skip if this regulation already has a sources: field
        if 'sources:[{name:' in m.group(1):
            return m.group(0)
        items = src_map[rid]
        applied += 1
        return m.group(1) + f', sources:[{items}]' + m.group(3)
    new_js = REGEX_SOURCE_INJECT.sub(repl, js)
    return new_js, applied

# ---------------------------------------------------------------------------
# P4.2 — Version bump + report cover framework stamp
# ---------------------------------------------------------------------------
EDIT_META = (
    'version: "1.0.0",\n    profile: "rules-engine",\n    delivery: "single-file-html",\n    updated: "2026-07",',
    'version: "1.3.0",\n    profile: "rules-engine",\n    delivery: "single-file-html",\n    updated: "2026-07-31",',
)

# Add a small framework stamp to the coverBlock — inject a line after the eyebrow
EDIT_COVER_STAMP = (
    '<div class="eyebrow">CIS Tech Advisory · Digital Sovereignty</div>\n'
    '    <h1 style="font-size:34px;margin:6px 0 10px">Data Residency &amp; Jurisdiction Audit</h1>',

    '<div class="eyebrow">CIS Tech Advisory · Digital Sovereignty</div>\n'
    '    <h1 style="font-size:34px;margin:6px 0 10px">Data Residency &amp; Jurisdiction Audit</h1>\n'
    '    <div class="mono" style="font-size:11px;color:var(--ink3);letter-spacing:.08em;margin:-2px 0 8px">FRAMEWORK v${BANK.meta.version} · REVIEWED ${BANK.meta.updated}</div>',
)

# ---------------------------------------------------------------------------
# P4.3 — ragForRegulation fix: require answered questions for green
# ---------------------------------------------------------------------------
EDIT_RAG = (
    'function ragForRegulation(regId, findings){\n'
    '  const rf=findings.filter(f=>f.reg===regId);\n'
    '  const assessed=STATE.activeQuestions.some(q=>(q.refs||[]).some(r=>r.reg===regId) || (q.appliesTo&&(q.appliesTo.regulations||[]).includes(regId)));\n'
    '  if(rf.some(f=>f.severity===\'critical\'||f.severity===\'high\')) return {rag:\'red\', status:\'Non-compliant\', count:rf.length};\n'
    '  if(rf.some(f=>f.severity===\'medium\')) return {rag:\'amber\', status:\'Partial — action required\', count:rf.length};\n'
    '  if(assessed) return {rag:\'green\', status:\'No material gaps found\', count:rf.length};\n'
    '  return {rag:\'grey\', status:\'Not assessed\', count:0};\n'
    '}',

    'function ragForRegulation(regId, findings){\n'
    '  const rf=findings.filter(f=>f.reg===regId);\n'
    '  // Answered = at least one active question referencing this regulation HAS an answer.\n'
    '  const answered=STATE.activeQuestions.some(q=>{\n'
    '    const refs=(q.refs||[]).some(r=>r.reg===regId) || (q.appliesTo&&(q.appliesTo.regulations||[]).includes(regId));\n'
    '    return refs && STATE.answers[q.id]!==undefined;\n'
    '  });\n'
    '  if(rf.some(f=>f.severity===\'critical\'||f.severity===\'high\')) return {rag:\'red\', status:\'Non-compliant\', count:rf.length};\n'
    '  if(rf.some(f=>f.severity===\'medium\')) return {rag:\'amber\', status:\'Partial — action required\', count:rf.length};\n'
    '  if(answered) return {rag:\'green\', status:\'No material gaps found\', count:rf.length};\n'
    '  return {rag:\'grey\', status:\'Not answered — cannot assess\', count:0};\n'
    '}',
)

EDITS = [
    ("P4.2a Bump meta.version 1.0.0 → 1.3.0 + updated 2026-07-31", EDIT_META),
    ("P4.2b Add framework stamp to cover block",                    EDIT_COVER_STAMP),
    ("P4.3  ragForRegulation: require answered questions",          EDIT_RAG),
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
    # Sources injection is regex-based
    js, n = inject_sources(js, build_source_edits())
    if n:
        print(f"  ✓ P4.1  sources[] injected into {n} regulations")
        applied += 1
    else:
        print(f"  = P4.1  sources: already present on all regulations")
    return js, applied


def semantic_check(js: str) -> None:
    # JS-syntax guard: raw-string \n bug protection
    bad = re.findall(r'\\n\s+id:"', js)
    if bad:
        raise SystemExit(f"  ✗ JS SYNTAX BUG: {len(bad)} literal '\\n id:\"' occurrence(s). REFUSING TO SAVE.")
    for needle, label in [
        ('version: "1.3.0"', 'version bumped'),
        ('updated: "2026-07-31"', 'updated date'),
        ('FRAMEWORK v${BANK.meta.version}', 'cover framework stamp'),
        ('Not answered — cannot assess', 'ragForRegulation fix'),
    ]:
        if needle not in js:
            raise SystemExit(f"  ✗ semantic check failed — missing: {label}")
    # Every regulation has a sources array now — check a 3000-char window
    # after each `id:"<rid>"` for the sources marker (regulation blocks
    # sit within the same short region of the file).
    missing = []
    for rid in SOURCES.keys():
        i = js.find(f'id:"{rid}"')
        if i < 0:
            missing.append(f"{rid} (id not found)"); continue
        window = js[i:i+3000]
        # window must contain sources:[{name: before the NEXT regulation id
        next_reg = re.search(r',\s*\{\s*id:"[a-z0-9_]+",\s*name:', window[10:])
        end = 10 + next_reg.start() if next_reg else len(window)
        if 'sources:[{name:' not in window[:end]:
            missing.append(f"{rid} (no sources[] in first {end} chars)")
    if missing:
        raise SystemExit(f"  ✗ regulations without sources[]: {missing}")
    print(f"  ✓ semantic check OK (all {len(SOURCES)} regulations carry sources[])")


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
    new_raw = raw[:m.end()] + json.dumps(manifest, separators=(',', ':')) + raw[end_tag:]
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
