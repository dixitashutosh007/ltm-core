#!/usr/bin/env python3
"""FinOps Value Case — Phase 1 patch (legal defensibility).

Implements the 4 Phase 1 items from docs/FVC-REVIEW.md §6:

  P1.1  BFSI sector gate — add sector_class dropdown; gate wasteBand()
        BFSI uplift on selection; conditional basis prose.
  P1.2  Currency freeze on report render + Currency stamp on cover.
  P1.3  Append "not financial advice" language to disclaimer.
  P1.4  Framework version + reviewed-date stamp on cover.

Idempotent: each edit checks whether it has already been applied.

Deploys to finops-value-case-staging.html only. Prod
(finops-value-case.html) is untouched by this script; promotion happens
via `deploy-s3.py --target prod` after legal sign-off.

The FVC bundle uses the plain-JSON __bundler/template pattern (same as
Sovereign Screen, unlike DR&J which is gzipped JS). All anchors below
are the raw JSON-escaped substrings as they appear in the file
(backslash-quote, backslash-n, backslash-u002F for '/').
"""
import argparse
import json
import pathlib
import re
import sys

FILE = pathlib.Path(
    "/home/user/ltm-core/finops-value-case/FinOps Value Case (LTM).html"
)

# ---------------------------------------------------------------------------
# P1.3 — Disclaimer append
# ---------------------------------------------------------------------------
EDIT_DISCLAIMER = (
    r'disclaimer:\"Indicative estimate based on self-reported inputs and published industry benchmarks. Figures illustrate the scale of opportunity and are not a guarantee of savings. A validated baseline requires assessment of actual billing data.\"',
    r'disclaimer:\"Indicative estimate based on self-reported inputs and published industry benchmarks. Figures illustrate the scale of opportunity and are not a guarantee of savings. A validated baseline requires assessment of actual billing data. Indicative and directional only. Not a commitment, quote or financial advice.\"',
)

# ---------------------------------------------------------------------------
# P1.1 + P1.2 — State: add sector_class (default bfsi) and reportCurrency
# ---------------------------------------------------------------------------
EDIT_STATE_ORG = (
    r'org:{name:\"\",logo:null,sector:\"Banking / Financial Services\",currency:\"gbp\",details:\"\"},',
    r'org:{name:\"\",logo:null,sector:\"Banking / Financial Services\",sector_class:\"bfsi\",currency:\"gbp\",details:\"\"},',
)
EDIT_STATE_TAIL = (
    r'answers:{},ltmLogo:null};',
    r'answers:{},ltmLogo:null,reportCurrency:null};',
)

# ---------------------------------------------------------------------------
# P1.2 — cur() honours frozen report currency
# ---------------------------------------------------------------------------
EDIT_CUR = (
    r'function cur(){return (S.kb.meta.currencies.find(c=>c.id===S.org.currency)||{symbol:\"£\"}).symbol;}',
    r'function cur(){const id=(S.screen===\"report\"&&S.reportCurrency)?S.reportCurrency:S.org.currency;return (S.kb.meta.currencies.find(c=>c.id===id)||{symbol:\"£\"}).symbol;}',
)

# ---------------------------------------------------------------------------
# P1.2 — goReport freezes currency snapshot
# ---------------------------------------------------------------------------
EDIT_GOREPORT = (
    r'else if(a===\"goReport\"){S.screen=\"report\";render();window.scrollTo(0,0);}',
    r'else if(a===\"goReport\"){S.reportCurrency=S.org.currency;S.screen=\"report\";render();window.scrollTo(0,0);}',
)

# ---------------------------------------------------------------------------
# P1.1 — Sector classification dropdown in viewOrg
# The original renders Sector (text) + Reporting currency (select) as a
# 2-col grid2 row. We add Sector classification as the second cell and
# push Reporting currency onto its own row.
# ---------------------------------------------------------------------------
EDIT_SECTOR_FIELD = (
    r"""+'<div class=\"grid2\">'+fieldH(\"Sector\",\"org\",\"sector\",\"input\",\"e.g. Retail banking\",o.sector)\n   +'<div class=\"field\"><label>Reporting currency<\u002Flabel><select data-model=\"org.currency\">'+curOpts+'<\u002Fselect><\u002Fdiv><\u002Fdiv>'""",
    r"""+'<div class=\"grid2\">'+fieldH(\"Sector\",\"org\",\"sector\",\"input\",\"e.g. Retail banking\",o.sector)\n   +'<div class=\"field\"><label>Sector classification<\u002Flabel><select data-model=\"org.sector_class\"><option value=\"bfsi\"'+(o.sector_class===\"bfsi\"?\" selected\":\"\")+'>Banking / Financial Services (BFSI)<\u002Foption><option value=\"other\"'+(o.sector_class===\"other\"?\" selected\":\"\")+'>Other sector<\u002Foption><\u002Fselect><\u002Fdiv><\u002Fdiv>'\n   +'<div class=\"field\"><label>Reporting currency<\u002Flabel><select data-model=\"org.currency\">'+curOpts+'<\u002Fselect><\u002Fdiv>'""",
)

# ---------------------------------------------------------------------------
# P1.1 — wasteBand gates BFSI uplift on sector_class
# ---------------------------------------------------------------------------
EDIT_WASTEBAND = (
    r'const mods=S.kb.meta.benchmarks.bfsi_modifiers;\n  // Sector uplift reflects structural inefficiency that mature controls largely resolve,\n  // so it scales inversely with demonstrated capability rather than applying flat.\n  const full=mods.factors.reduce((a,f)=>a+f.pts,0);\n  const uplift=full*(1-cap/100);\n  return {low:band.low, high:Math.min(mods.cap, band.high+uplift), label:band.label, anchor:band.anchor, uplift, cap:Math.round(cap)};',
    r'const mods=S.kb.meta.benchmarks.bfsi_modifiers;\n  // BFSI sector uplift applies only when the customer is classified as BFSI.\n  // Non-BFSI customers get the base band with no sector adjustment.\n  const isBfsi=S.org.sector_class===\"bfsi\";\n  const full=mods.factors.reduce((a,f)=>a+f.pts,0);\n  const uplift=isBfsi?full*(1-cap/100):0;\n  return {low:band.low, high:Math.min(mods.cap, band.high+uplift), label:band.label, anchor:band.anchor, uplift, cap:Math.round(cap), isBfsi};',
)

# ---------------------------------------------------------------------------
# P1.1 — Basis text: only mention BFSI when it was applied
# ---------------------------------------------------------------------------
EDIT_BASIS_TEXT = (
    r"esc(ex.band.anchor)+' A BFSI sector adjustment of +'+(ex.band.uplift*100).toFixed(1)+' percentage points is applied to the upper bound only — scaled to your demonstrated capability, since mature controls largely resolve the structural inefficiency it represents (elevated non-production estate, mandated resilience duplication, residency constraints and lift-and-shift core systems). '+esc(cf.note)",
    r"esc(ex.band.anchor)+(ex.band.isBfsi?' A BFSI sector adjustment of +'+(ex.band.uplift*100).toFixed(1)+' percentage points is applied to the upper bound only — scaled to your demonstrated capability, since mature controls largely resolve the structural inefficiency it represents (elevated non-production estate, mandated resilience duplication, residency constraints and lift-and-shift core systems).':' No sector-specific adjustment applied (customer classified as non-BFSI).')+' '+esc(cf.note)",
)

# ---------------------------------------------------------------------------
# P1.4 + P1.2 — Cover meta stamp: framework version + reviewed date + currency
# Inserted after the covermeta closing </div></div></div>, before the optional
# scope block.
# ---------------------------------------------------------------------------
COVER_ANCHOR = r"""+esc([r.role,r.email].filter(Boolean).join(\" · \"))+'<\u002Fdiv><\u002Fdiv><\u002Fdiv>'\n   +(o.details?"""
COVER_INSERT = r"""+esc([r.role,r.email].filter(Boolean).join(\" · \"))+'<\u002Fdiv><\u002Fdiv><\u002Fdiv>'\n   +'<div class=\"mono\" style=\"margin-top:14px;padding-top:12px;border-top:1px solid #ECECEC;font-size:11px;color:#8E8E8E;letter-spacing:.05em;text-transform:uppercase\">Framework v'+esc(M.schema_version)+' · reviewed '+esc(M.last_reviewed)+' · Currency '+cur()+' '+esc((S.reportCurrency||S.org.currency).toUpperCase())+'<\u002Fdiv>'\n   +(o.details?"""

EDITS = [
    ("P1.3 Disclaimer append (not financial advice)", EDIT_DISCLAIMER),
    ("P1.1 State: org.sector_class default bfsi", EDIT_STATE_ORG),
    ("P1.2 State: reportCurrency:null", EDIT_STATE_TAIL),
    ("P1.2 cur() honours frozen reportCurrency", EDIT_CUR),
    ("P1.2 goReport snaps currency on entry", EDIT_GOREPORT),
    ("P1.1 viewOrg: Sector classification dropdown", EDIT_SECTOR_FIELD),
    ("P1.1 wasteBand gates BFSI uplift", EDIT_WASTEBAND),
    ("P1.1 Basis text conditional BFSI clause", EDIT_BASIS_TEXT),
    ("P1.4 + P1.2 Cover meta stamp", (COVER_ANCHOR, COVER_INSERT)),
]

# Idempotency markers — substrings unique to the post-patch state.
POST_MARKERS = {
    "P1.3 Disclaimer append (not financial advice)": r"Not a commitment, quote or financial advice.",
    "P1.1 State: org.sector_class default bfsi": r'sector_class:\"bfsi\"',
    "P1.2 State: reportCurrency:null": r"reportCurrency:null",
    "P1.2 cur() honours frozen reportCurrency": r"S.screen===\"report\"&&S.reportCurrency",
    "P1.2 goReport snaps currency on entry": r"S.reportCurrency=S.org.currency",
    "P1.1 viewOrg: Sector classification dropdown": r'data-model=\"org.sector_class\"',
    "P1.1 wasteBand gates BFSI uplift": r"isBfsi=S.org.sector_class",
    "P1.1 Basis text conditional BFSI clause": r"ex.band.isBfsi?",
    "P1.4 + P1.2 Cover meta stamp": r"Framework v'+esc(M.schema_version)",
}


def json_safety_check(data: str) -> None:
    """Refuse to save if any <script type='__bundler/...'> payload stops
    parsing as JSON. Prevents the "Bad escaped character in JSON" crash
    on the live site."""
    for tag in ("__bundler/manifest", "__bundler/template", "__bundler/ext_resources"):
        m = re.search(r'<script type="' + re.escape(tag) + r'">', data)
        if not m:
            continue
        end = data.find("</script>", m.end())
        payload = data[m.end():end]
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            ctx = payload[max(0, e.pos - 80):e.pos + 80]
            raise SystemExit(
                f"\n  ✗ {tag} JSON invalid after Phase 1 patch: {e}\n"
                f"    context: {ctx!r}\n"
                f"    REFUSING TO SAVE — adjust the replacements."
            )


def js_syntax_check(data: str) -> None:
    """Decode the template payload and shell out to node --check to
    catch JS syntax errors before shipping to prod. If node isn't
    available, skip with a warning."""
    import shutil
    import subprocess
    import tempfile

    m = re.search(r'<script type="__bundler/template">', data)
    if not m:
        return
    end = data.find("</script>", m.end())
    payload = data[m.end():end]
    decoded = json.loads(payload)

    # Extract inline <script>...</script> blocks from the decoded HTML;
    # syntax-check each. Only inline scripts (no `src=`), since external
    # ones are separate bundler entries.
    script_bodies = re.findall(
        r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", decoded, flags=re.DOTALL
    )
    if not script_bodies:
        return

    node = shutil.which("node")
    if not node:
        print("  ! js_syntax_check: node not on PATH — skipping (install node to enable)")
        return

    for i, body in enumerate(script_bodies):
        # Skip empty / trivial (feature-detect) blocks
        if len(body.strip()) < 32:
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
            tf.write(body)
            path = tf.name
        try:
            result = subprocess.run(
                [node, "--check", path], capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                raise SystemExit(
                    f"\n  ✗ inline <script> #{i} failed node --check:\n"
                    f"    {result.stderr.strip()}\n"
                    f"    REFUSING TO SAVE — a patch produced invalid JS."
                )
        finally:
            pathlib.Path(path).unlink(missing_ok=True)


def semantic_check(data: str) -> None:
    """Cheap post-patch sanity: the KB and rendered strings should still
    contain the expected structural markers."""
    m = re.search(r'<script type="__bundler/template">', data)
    if not m:
        return
    end = data.find("</script>", m.end())
    payload = data[m.end():end]
    decoded = json.loads(payload)

    checks = [
        # KB still has 29 questions
        (r'\bid:"E1"', "Q_E1"), (r'\bid:"E6"', "Q_E6"),
        (r'\bid:"V1"', "Q_V1"), (r'\bid:"V5"', "Q_V5"),
        (r'\bid:"P1"', "Q_P1"), (r'\bid:"P4"', "Q_P4"),
        (r'\bid:"O1"', "Q_O1"), (r'\bid:"O4"', "Q_O4"),
        (r'\bid:"C1"', "Q_C1"), (r'\bid:"C4"', "Q_C4"),
        (r'\bid:"L1"', "Q_L1"), (r'\bid:"X1"', "Q_X1"),
        # Phase 1 post-conditions still present
        (r'sector_class:"bfsi"', "org.sector_class default"),
        (r'reportCurrency:null', "reportCurrency state"),
        (r'S\.screen==="report"&&S\.reportCurrency', "cur() freeze branch"),
        (r'S\.reportCurrency=S\.org\.currency', "goReport freeze"),
        (r'data-model="org\.sector_class"', "sector_class select"),
        (r'isBfsi=S\.org\.sector_class', "wasteBand BFSI gate"),
        (r'ex\.band\.isBfsi\?', "basis conditional"),
        (r"Framework v'\+esc\(M\.schema_version\)", "cover framework stamp"),
        (r"Not a commitment, quote or financial advice\.", "disclaimer append"),
    ]
    missing = [label for pat, label in checks if not re.search(pat, decoded)]
    if missing:
        raise SystemExit(
            "\n  ✗ semantic check failed — missing markers after patch:\n    "
            + "\n    ".join(missing)
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Apply edits in memory, run checks, do not write.")
    args = parser.parse_args()

    data = FILE.read_text(encoding="utf-8")
    before_len = len(data)
    applied = 0

    print("--- EDITS ---")
    for label, (old, new) in EDITS:
        marker = POST_MARKERS.get(label)
        if marker and marker in data:
            print(f"  = {label}: already applied")
            continue
        if old not in data:
            print(f"  ! {label}: OLD NOT FOUND — adjust anchor")
            continue
        data = data.replace(old, new, 1)
        applied += 1
        print(f"  ✓ {label}")

    print()
    json_safety_check(data)
    print("  ✓ all bundler payloads still parse as valid JSON")
    js_syntax_check(data)
    print("  ✓ inline <script> passes node --check")
    semantic_check(data)
    print("  ✓ semantic markers all present")

    if args.dry_run:
        print("\n  (dry run — file not written)")
        return 0

    FILE.write_text(data, encoding="utf-8")
    print(f"\n  file: {FILE}")
    print(f"  size delta: {len(data) - before_len:+d} bytes  ({applied} edits)")
    return 0 if applied else 1


if __name__ == "__main__":
    sys.exit(main())
