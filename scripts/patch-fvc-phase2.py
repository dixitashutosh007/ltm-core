#!/usr/bin/env python3
"""FinOps Value Case — Phase 2 patch (scoring / content correctness).

Implements the 3 Phase 2 items from docs/FVC-REVIEW.md §6:

  P2.1  Oracle Cloud reclassified hyper:true in Q_E2.
  P2.2  url: added to all 4 meta.benchmarks.sources[] entries.
  P2.3  allocation_100 qScore returns null when the total is not 100.

Idempotent. Stacks cleanly on top of Phase 1 (SHA 4fb8c2f).
"""
import argparse, json, pathlib, re, sys

FILE = pathlib.Path(
    "/home/user/ltm-core/finops-value-case/FinOps Value Case (LTM).html"
)

# P2.1 — Oracle Cloud hyper:false → true
EDIT_ORACLE = (
    r'{label:\"Oracle Cloud\",hyper:false}',
    r'{label:\"Oracle Cloud\",hyper:true}',
)

# P2.2 — sources[] URL enrichment. Each edit inserts a url: field between
# label: and note: on one specific source. Anchors are the full label
# clause so we can't collide with other {label:...} appearances.
EDIT_SRC_FLEXERA2026 = (
    r'{label:\"Flexera 2026 State of the Cloud Report (n=753, March 2026)\",note:',
    r'{label:\"Flexera 2026 State of the Cloud Report (n=753, March 2026)\",url:\"https://info.flexera.com/CM-REPORT-State-of-the-Cloud\",note:',
)
EDIT_SRC_FLEXERA_MY = (
    r'{label:\"Flexera State of the Cloud, multi-year (2019–2026)\",note:',
    r'{label:\"Flexera State of the Cloud, multi-year (2019–2026)\",url:\"https://info.flexera.com/CM-REPORT-State-of-the-Cloud\",note:',
)
EDIT_SRC_HARNESS = (
    r'{label:\"Harness Cloud Cost Management Report (2025)\",note:',
    r'{label:\"Harness Cloud Cost Management Report (2025)\",url:\"https://www.harness.io/whitepapers/cloud-cost-management-report\",note:',
)
EDIT_SRC_FINOPSF = (
    r'{label:\"FinOps Foundation, State of FinOps 2026\",note:',
    r'{label:\"FinOps Foundation, State of FinOps 2026\",url:\"https://www.finops.org/insights/state-of-finops/\",note:',
)

# P2.3 — allocation_100 qScore: refuse to score when total ≠ 100.
EDIT_ALLOC = (
    r'case \"allocation_100\":{const nb=(a&&a.nobody)||0;\n      let sc=100-nb*1.6;\n      const vals=Object.values(a||{});const mx=Math.max(...vals,0);\n      if(mx>70)sc-=(mx-70)*0.6;\n      return Math.max(0,Math.min(100,Math.round(sc)));}',
    r'case \"allocation_100\":{const vals=Object.values(a||{});const total=vals.reduce((x,y)=>x+y,0);\n      if(total!==100)return null;\n      const nb=(a&&a.nobody)||0;\n      let sc=100-nb*1.6;\n      const mx=Math.max(...vals,0);\n      if(mx>70)sc-=(mx-70)*0.6;\n      return Math.max(0,Math.min(100,Math.round(sc)));}',
)

EDITS = [
    ("P2.1 Oracle Cloud hyper:true", EDIT_ORACLE),
    ("P2.2a Flexera 2026 url", EDIT_SRC_FLEXERA2026),
    ("P2.2b Flexera multi-year url", EDIT_SRC_FLEXERA_MY),
    ("P2.2c Harness url", EDIT_SRC_HARNESS),
    ("P2.2d FinOps Foundation url", EDIT_SRC_FINOPSF),
    ("P2.3 allocation_100 null when total != 100", EDIT_ALLOC),
]

POST_MARKERS = {
    "P2.1 Oracle Cloud hyper:true": r'{label:\"Oracle Cloud\",hyper:true}',
    "P2.2a Flexera 2026 url": r'info.flexera.com/CM-REPORT-State-of-the-Cloud\",note:\"Wasted IaaS/PaaS',
    "P2.2b Flexera multi-year url": r'info.flexera.com/CM-REPORT-State-of-the-Cloud\",note:\"Estimated waste',
    "P2.2c Harness url": r'harness.io/whitepapers/cloud-cost-management-report',
    "P2.2d FinOps Foundation url": r'finops.org/insights/state-of-finops/',
    "P2.3 allocation_100 null when total != 100": r'if(total!==100)return null;',
}


def json_safety_check(data: str) -> None:
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
                f"\n  ✗ {tag} JSON invalid: {e}\n    context: {ctx!r}\n    REFUSING TO SAVE"
            )


def js_syntax_check(data: str) -> None:
    import shutil, subprocess, tempfile
    m = re.search(r'<script type="__bundler/template">', data)
    if not m: return
    end = data.find("</script>", m.end())
    decoded = json.loads(data[m.end():end])
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", decoded, flags=re.DOTALL)
    node = shutil.which("node")
    if not node:
        print("  ! node not on PATH — skipping JS syntax check"); return
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
        # Phase 1 markers still present
        (r'sector_class:"bfsi"', "P1 sector_class"),
        (r'S\.reportCurrency=S\.org\.currency', "P1 currency freeze"),
        (r'Not a commitment, quote or financial advice', "P1 disclaimer"),
        (r"Framework v'\+esc\(M\.schema_version\)", "P1 cover stamp"),
        # Phase 2 markers
        (r'{label:"Oracle Cloud",hyper:true}', "P2.1 Oracle"),
        (r'info\.flexera\.com/CM-REPORT-State-of-the-Cloud', "P2.2 Flexera url"),
        (r'harness\.io/whitepapers/cloud-cost-management-report', "P2.2 Harness url"),
        (r'finops\.org/insights/state-of-finops/', "P2.2 FinOps url"),
        (r'if\(total!==100\)return null;', "P2.3 alloc null"),
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
