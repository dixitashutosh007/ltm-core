#!/usr/bin/env python3
"""FinOps Maturity Screen — Phase 3 patch (hygiene).

Implements the 3 Phase 3 items from docs/FMS-REVIEW.md §5:

  P3.1  C2 middle option reworded for pass-fail clarity.
  P3.2  meta.sources[] added citing FinOps Foundation Framework +
        industry references; rendered as clickable list in Method.
  P3.3  Confidence indicator (Reasonable / Moderate / Low) driven by
        answered/44 ratio, rendered as a chip in the report header
        stats. Mirrors FVC confidence pattern.

Idempotent. Stacks on top of FMS P1 + P2.
"""
import argparse, json, pathlib, re, sys

FILE = pathlib.Path(
    "/home/user/ltm-core/FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html"
)

# ---------------------------------------------------------------------------
# P3.1 — C2 middle option reworded
# ---------------------------------------------------------------------------
EDIT_C2 = (
    r'{label:\"Exported, but partial or manual\",score:55}',
    r'{label:\"Exported, but partial or manual (does not yet cover all providers / accounts)\",score:55}',
)

# ---------------------------------------------------------------------------
# P3.2 — meta.sources[] insertion. Anchor: right after gating_note, before
# the domains array.
# ---------------------------------------------------------------------------
EDIT_SOURCES = (
    r'gating_note:\"Maturity is the highest stage passed with all preceding stages also passed. A stage passes only when its weighted score meets the threshold and every critical question meets the critical minimum — criticals are structural prerequisites, so a high average cannot compensate for a missing foundation.\",\n    domains:',
    r'gating_note:\"Maturity is the highest stage passed with all preceding stages also passed. A stage passes only when its weighted score meets the threshold and every critical question meets the critical minimum — criticals are structural prerequisites, so a high average cannot compensate for a missing foundation.\",\n    sources:[\n      {name:\"FinOps Foundation — FinOps Framework\",url:\"https://www.finops.org/framework/\"},\n      {name:\"FinOps Foundation — State of FinOps 2026\",url:\"https://www.finops.org/insights/state-of-finops/\"},\n      {name:\"Flexera State of the Cloud (industry practice reference)\",url:\"https://info.flexera.com/CM-REPORT-State-of-the-Cloud\"}\n    ],\n    domains:',
)

# ---------------------------------------------------------------------------
# P3.2b — Render sources in the Method section of the report.
# Anchor: "Framework last reviewed '+esc(kb.meta.last_reviewed)+'.</p></div>"
# Insert a sources block right before the closing </p></div> of the Method
# section.
# ---------------------------------------------------------------------------
EDIT_METHOD_SOURCES = (
    r"score and weighted by question. Framework last reviewed '+esc(kb.meta.last_reviewed)+'.<\u002Fp><\u002Fdiv>'",
    r"score and weighted by question. Framework last reviewed '+esc(kb.meta.last_reviewed)+'.<\u002Fp>'\n    +(kb.meta.sources&&kb.meta.sources.length?'<div style=\"margin-top:14px;padding-top:12px;border-top:1px solid #ECECEC;font-size:12.5px;color:#5B5B5B\"><b style=\"color:#282828\">Sources.</b> '+kb.meta.sources.map(function(s){return '<a href=\"'+esc(s.url)+'\" target=\"_blank\" rel=\"noopener\" style=\"color:#e5412f;text-decoration:underline;text-underline-offset:2px\">'+esc(s.name)+'<\u002Fa>';}).join(' &middot; ')+'<\u002Fdiv>':'')+'<\u002Fdiv>'",
)

# ---------------------------------------------------------------------------
# P3.3 — Confidence indicator
# ---------------------------------------------------------------------------
# 3a — new confidenceLabel() function after overallScore().
EDIT_CONFIDENCE_FN = (
    r"function overallScore(kb,answers){\n  let t=0,w=0;\n  kb.questions.forEach(q=>{ const s=qScore(q,answers[q.id]); if(s===null) return;\n    const ww=q.weight||1; t+=s*ww; w+=ww; });\n  return w?Math.round(t/w):null;\n}",
    r"function overallScore(kb,answers){\n  let t=0,w=0;\n  kb.questions.forEach(q=>{ const s=qScore(q,answers[q.id]); if(s===null) return;\n    const ww=q.weight||1; t+=s*ww; w+=ww; });\n  return w?Math.round(t/w):null;\n}\nfunction confidenceLabel(kb,answers){\n  const total=kb.questions.length;\n  const answered=kb.questions.filter(q=>answers[q.id]!==undefined).length;\n  const scored=kb.questions.filter(q=>qScore(q,answers[q.id])!==null).length;\n  const ratio=total?scored/total:0;\n  if(ratio>=0.75) return {label:\"Reasonable confidence\",color:\"#35754D\",answered:answered,scored:scored};\n  if(ratio>=0.50) return {label:\"Moderate confidence\",color:\"#B26A00\",answered:answered,scored:scored};\n  return {label:\"Low confidence\",color:\"#FF5E4F\",answered:answered,scored:scored};\n}",
)

# 3b — Render confidence chip alongside the "Critical blockers" span in
# the repstat header of the report.
EDIT_CONF_RENDER = (
    r"+'<span>Critical blockers <b>'+blockers+'<\u002Fb><\u002Fspan><\u002Fdiv><\u002Fdiv>'",
    r"+'<span>Critical blockers <b>'+blockers+'<\u002Fb><\u002Fspan>'\n    +(function(){var cf=confidenceLabel(kb,S.answers); return '<span style=\"background:'+cf.color+'22;color:'+cf.color+';border:1px solid '+cf.color+'55;padding:3px 10px;border-radius:12px;font-size:11.5px;font-weight:600;letter-spacing:.02em\">'+cf.label+'<\u002Fspan>';})()\n    +'<\u002Fdiv><\u002Fdiv>'",
)

EDITS = [
    ("P3.1 C2 middle option reworded", EDIT_C2),
    ("P3.2a meta.sources[] insertion", EDIT_SOURCES),
    ("P3.2b Method section renders sources", EDIT_METHOD_SOURCES),
    ("P3.3a confidenceLabel() function", EDIT_CONFIDENCE_FN),
    ("P3.3b Confidence chip in report header", EDIT_CONF_RENDER),
]

POST_MARKERS = {
    "P3.1 C2 middle option reworded": r'(does not yet cover all providers / accounts)',
    "P3.2a meta.sources[] insertion": r'FinOps Foundation — FinOps Framework',
    "P3.2b Method section renders sources": r'Sources.</b>',
    "P3.3a confidenceLabel() function": r'function confidenceLabel(kb,answers)',
    "P3.3b Confidence chip in report header": r'var cf=confidenceLabel(kb,S.answers)',
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
        # P1/P2 markers still present
        (r'is a trademark of the FinOps Foundation', "P1 TM"),
        (r'account-ownership and access model that supports cost governance', "P1 C1"),
        (r'Culture & engineering behaviour', "P2 culture"),
        (r'"__DK__"\) return null', "P2 DK short-circuit"),
        (r'function blindSpots', "P2 blindSpots"),
        # P3 markers
        (r'\(does not yet cover all providers / accounts\)', "P3.1 C2 reword"),
        (r'FinOps Foundation — FinOps Framework', "P3.2a sources"),
        (r'finops\.org/framework/', "P3.2a url"),
        (r'<b style="color:#282828">Sources\.</b>', "P3.2b Method render"),
        (r'function confidenceLabel', "P3.3a fn"),
        (r'var cf=confidenceLabel\(kb,S\.answers\)', "P3.3b chip render"),
    ]
    missing = [lbl for pat, lbl in checks if not re.search(pat, decoded)]
    if missing:
        raise SystemExit("\n  ✗ semantic check failed: " + ", ".join(missing))


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
    semantic_check(data); print("  ✓ semantic markers present")
    if args.dry_run:
        print("\n  (dry run — file not written)"); return 0
    FILE.write_text(data)
    print(f"\n  size delta: {len(data)-before:+d} bytes  ({applied} edits)")
    return 0 if applied else 1


if __name__ == "__main__":
    sys.exit(main())
