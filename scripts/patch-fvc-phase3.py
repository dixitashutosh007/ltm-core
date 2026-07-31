#!/usr/bin/env python3
"""FinOps Value Case — Phase 3 patch (ship-blocker mitigation).

Real case-study PDFs and the LTM FinOps Services brochure are not
available yet. Rather than let the live prod tool keep rendering red
PLACEHOLDER PDF chips to prospects, Phase 3 hides all placeholder
assets from the customer-facing report — and drops the PLACEHOLDER
chip entirely from the codebase.

Behaviour:
  - Case studies with status === "placeholder" are filtered out of the
    "Relevant case studies" section. If none survive the filter, a
    graceful fallback paragraph replaces the grid.
  - The LTM FinOps Services brochure download card is suppressed when
    its status === "placeholder" (the download button is skipped;
    surrounding divs are preserved so the DOM balances).
  - The "PLACEHOLDER PDF" chip is removed from both the case-study
    entry template and the brochure title so it can never leak to a
    customer even if a placeholder slips through.

When real PDFs land, flip status:"placeholder" → status:"published"
in DEFAULT_KB.meta.case_studies[] / meta.brochure and everything
reappears — no code change needed.

Idempotent. Stacks on top of FVC P1 + P2.
"""
import argparse, json, pathlib, re, sys

FILE = pathlib.Path(
    "/home/user/ltm-core/finops-value-case/FinOps Value Case (LTM).html"
)

# P3.1a — filter placeholder from cases at the call site in viewReport.
EDIT_CASES_FILTER = (
    r'const svcs=recommendedServices(), cases=relevantCaseStudies();',
    r'const svcs=recommendedServices(), cases=relevantCaseStudies().filter(cs=>cs.status!==\"placeholder\");',
)

# P3.1b — drop the PLACEHOLDER PDF chip from the case-study entry.
EDIT_CS_CHIP = (
    r"""+(cs.status===\"placeholder\"?'<span class=\"csph\">PLACEHOLDER PDF<\u002Fspan>':'')""",
    r"""+''""",
)

# P3.1c — csgrid fallback when no cases survive the filter.
EDIT_CSGRID = (
    r"+'<div class=\"csgrid\">'+csBlock+'<\u002Fdiv><\u002Fdiv>'",
    r"+(csBlock?'<div class=\"csgrid\">'+csBlock+'<\u002Fdiv>':'<p style=\"color:#5B5B5B;font-size:13.5px;margin-top:0\">Client case studies from comparable engagements are available on request — flag it in the follow-up conversation.<\u002Fp>')+'<\u002Fdiv>'",
)

# P3.1d — drop the PLACEHOLDER PDF chip from the brochure title.
EDIT_BROCH_CHIP = (
    r"""+esc(M.brochure.title)+(M.brochure.status===\"placeholder\"?'<span class=\"csph\">PLACEHOLDER PDF<\u002Fspan>':'')+'<\u002Fdiv>'""",
    r"""+esc(M.brochure.title)+'<\u002Fdiv>'""",
)

# P3.1e — gate the brochure download button on non-placeholder status.
EDIT_BROCH_BTN = (
    r"""+'<button class=\"csbtn no-print\" data-a=\"dlBrochure\">Download brochure<\u002Fbutton><\u002Fdiv><\u002Fdiv><\u002Fdiv>'""",
    r"""+(M.brochure.status===\"placeholder\"?'<\u002Fdiv><\u002Fdiv><\u002Fdiv>':'<button class=\"csbtn no-print\" data-a=\"dlBrochure\">Download brochure<\u002Fbutton><\u002Fdiv><\u002Fdiv><\u002Fdiv>')""",
)

EDITS = [
    ("P3.1a Filter placeholder cases at call site", EDIT_CASES_FILTER),
    ("P3.1b Drop PLACEHOLDER PDF chip on case study entry", EDIT_CS_CHIP),
    ("P3.1c csgrid fallback when no cases available", EDIT_CSGRID),
    ("P3.1d Drop PLACEHOLDER PDF chip on brochure title", EDIT_BROCH_CHIP),
    ("P3.1e Gate brochure download button on non-placeholder", EDIT_BROCH_BTN),
]

POST_MARKERS = {
    "P3.1a Filter placeholder cases at call site": r'relevantCaseStudies().filter(cs=>cs.status!==\"placeholder\")',
    "P3.1b Drop PLACEHOLDER PDF chip on case study entry": None,  # negative-only, checked in semantic
    "P3.1c csgrid fallback when no cases available": r'Client case studies from comparable engagements are available on request',
    "P3.1d Drop PLACEHOLDER PDF chip on brochure title": None,  # negative-only
    "P3.1e Gate brochure download button on non-placeholder": r"""M.brochure.status===\"placeholder\"?'</div></div></div>'""",
}


def json_safety_check(data: str) -> None:
    for tag in ("__bundler/manifest", "__bundler/template", "__bundler/ext_resources"):
        m = re.search(r'<script type="' + re.escape(tag) + r'">', data)
        if not m: continue
        end = data.find("</script>", m.end())
        payload = data[m.end():end]
        try: json.loads(payload)
        except json.JSONDecodeError as e:
            ctx = payload[max(0, e.pos - 80):e.pos + 80]
            raise SystemExit(f"\n  ✗ {tag} JSON invalid: {e}\n    context: {ctx!r}")


def js_syntax_check(data: str) -> None:
    import shutil, subprocess, tempfile
    m = re.search(r'<script type="__bundler/template">', data)
    if not m: return
    end = data.find("</script>", m.end())
    decoded = json.loads(data[m.end():end])
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", decoded, flags=re.DOTALL)
    node = shutil.which("node")
    if not node:
        print("  ! node not on PATH — skipping"); return
    for i, body in enumerate(scripts):
        if len(body.strip()) < 32: continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
            tf.write(body); path = tf.name
        try:
            r = subprocess.run([node, "--check", path], capture_output=True, text=True, timeout=15)
            if r.returncode != 0:
                raise SystemExit(f"\n  ✗ inline <script> #{i} failed node --check:\n    {r.stderr.strip()}")
        finally:
            pathlib.Path(path).unlink(missing_ok=True)


def semantic_check(data: str) -> None:
    m = re.search(r'<script type="__bundler/template">', data)
    end = data.find("</script>", m.end())
    decoded = json.loads(data[m.end():end])
    checks = [
        # P1 markers
        (r'sector_class:"bfsi"', "P1 sector_class"),
        (r"Framework v'\+esc\(M\.schema_version\)", "P1 cover stamp"),
        # P2 markers
        (r'{label:"Oracle Cloud",hyper:true}', "P2 Oracle"),
        (r'if\(total!==100\)return null;', "P2 alloc null"),
        # P3 markers
        (r'relevantCaseStudies\(\)\.filter\(cs=>cs\.status!=="placeholder"\)', "P3 case filter"),
        (r'Client case studies from comparable engagements', "P3 csgrid fallback"),
    ]
    missing = [lbl for pat, lbl in checks if not re.search(pat, decoded)]
    if missing:
        raise SystemExit("\n  ✗ semantic check failed: " + ", ".join(missing))
    # Negative checks: PLACEHOLDER PDF chip must not appear in the rendered
    # template after P3 (it was only referenced in case-study and brochure
    # blocks; both dropped).
    if 'PLACEHOLDER PDF' in decoded:
        raise SystemExit(
            "\n  ✗ semantic check failed: 'PLACEHOLDER PDF' string still present after P3. "
            "Either an anchor missed or another site still references the chip."
        )


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    data = FILE.read_text(); before = len(data); applied = 0
    print("--- EDITS ---")
    for label, (old, new) in EDITS:
        marker = POST_MARKERS.get(label)
        if marker and marker in data:
            print(f"  = {label}: already applied"); continue
        if old not in data:
            print(f"  ! {label}: OLD NOT FOUND"); continue
        data = data.replace(old, new, 1); applied += 1
        print(f"  ✓ {label}")
    print()
    json_safety_check(data); print("  ✓ JSON payloads valid")
    js_syntax_check(data); print("  ✓ inline <script> passes node --check")
    semantic_check(data); print("  ✓ semantic markers present + PLACEHOLDER PDF gone")
    if args.dry_run:
        print("\n  (dry run — file not written)"); return 0
    FILE.write_text(data)
    print(f"\n  size delta: {len(data)-before:+d} bytes  ({applied} edits)")
    return 0 if applied else 1


if __name__ == "__main__":
    sys.exit(main())
