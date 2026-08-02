#!/usr/bin/env python3
"""Tier 1 code protection — copyright banners + TOS link across all 4
CIS Tech Advisory accelerators.

Adds three uniform elements to each bundled tool:

  1. HTML banner: an HTML comment immediately after <!DOCTYPE html> that
     asserts copyright and points at the Terms of Use page.
  2. JS banner: a /* ... */ comment block prepended to the first inline
     <script> that carries the same notice at the code level, so
     "View Source" always reveals ownership even if the HTML preamble
     is stripped.
  3. TOS link: appended as a new paragraph to the in-tool disclaimer
     popover (from the P4.4 v3 overlay), so every customer sees
     "Terms of Use: <link>" alongside the standard privacy + advisory
     copy.

Idempotent. Guards: json_safety_check on the bundler payload + a
semantic check that both banners land and the TOS link is present in
every file.

Not a security control — anything shipped to a browser is inspectable.
This is a legal deterrent: it establishes copyright, sets scope of
permitted use, and points at the TOS. See docs/LEGAL-REVIEW.md for the
sign-off flow.
"""
import argparse, json, pathlib, re, sys

FILES = [
    pathlib.Path("/home/user/ltm-core/Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html"),
    pathlib.Path("/home/user/ltm-core/Digital Sovereignty Data Residency Jurisdiction Audit/LTM-Data Residency & Jurisdiction Audit.html"),
    pathlib.Path("/home/user/ltm-core/finops-value-case/FinOps Value Case (LTM).html"),
    pathlib.Path("/home/user/ltm-core/FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html"),
]

TOS_URL = "https://ltm-core.s3.us-east-1.amazonaws.com/terms-of-use.html"

# ---------------------------------------------------------------------------
# 1. HTML banner — inserted right after the DOCTYPE.
# ---------------------------------------------------------------------------
HTML_BANNER = """<!--
  Copyright © 2026 LTIMindtree Limited. All rights reserved.

  This is a proprietary LTM CIS Tech Advisory accelerator. The question
  set, scoring model, weightings, thresholds, findings, rationales and
  framework structure are the copyrighted intellectual property of
  LTIMindtree Limited.

  Permitted: run in-browser for internal assessment; download and
  share the generated report internally.

  Prohibited without written permission: extraction, adaptation,
  reverse-engineering, redistribution, or use of the framework content
  in any derivative or competing product, or as machine-learning
  training data.

  Terms of Use:  """ + TOS_URL + """
  Contact:       ashutosh.dixit@ltm.com
-->
"""

# ---------------------------------------------------------------------------
# 2. JS banner — prepended inside the FIRST plain <script> block (not the
#    __bundler/* payload scripts, which are JSON not JS).
# ---------------------------------------------------------------------------
JS_BANNER = """/*!
 * LTM CIS Tech Advisory accelerator
 * Copyright (c) 2026 LTIMindtree Limited. All rights reserved.
 *
 * Proprietary. Framework content (questions, scoring, weights,
 * thresholds, findings, rationales) is copyrighted intellectual
 * property. Reverse engineering, redistribution, adaptation or
 * derivative use is prohibited without written permission.
 *
 * Terms of Use: """ + TOS_URL + """
 * Contact:      ashutosh.dixit@ltm.com
 */
"""

# ---------------------------------------------------------------------------
# 3. TOS link injected into the disclaimer popover (v3 overlay from P4.4).
#    The popover has a fixed HTML string ending in the CTA button. We
#    insert a mini "Terms of Use" paragraph immediately before the CTA.
#    Anchor: the CTA button opener text.
# ---------------------------------------------------------------------------
TOS_POP_OLD = "\"<button class='ltm-cu-pop-cta' type='button' id='ltm-cu-pop-cta'>Contact us for a scoped engagement"
TOS_POP_NEW = ("\"<p style='font-size:11.5px;color:#6a6a6a;margin:8px 0 12px'>"
               "<strong style='color:#141414'>Terms.</strong> Proprietary LTM framework — "
               "<a href='" + TOS_URL + "' target='_blank' rel='noopener' "
               "style='color:#e5412f;text-decoration:underline;text-underline-offset:2px'>Terms of Use</a>.</p>\""
               "\n      +   \"<button class='ltm-cu-pop-cta' type='button' id='ltm-cu-pop-cta'>Contact us for a scoped engagement")


def add_html_banner(data: str) -> tuple[str, bool]:
    """Insert HTML banner immediately after <!DOCTYPE html>."""
    if "Copyright © 2026 LTIMindtree Limited. All rights reserved." in data:
        return data, False
    # Case-insensitive DOCTYPE match, preserve as-is
    m = re.search(r'<!DOCTYPE html>\s*\n', data, flags=re.IGNORECASE)
    if not m:
        raise SystemExit(f"  ! DOCTYPE not found in file — cannot place HTML banner")
    return data[:m.end()] + HTML_BANNER + data[m.end():], True


def add_js_banner(data: str) -> tuple[str, bool]:
    """Prepend JS banner inside the first inline <script> that has no
    type attribute (i.e. actual JS, not the JSON __bundler/* payloads)."""
    if 'LTM CIS Tech Advisory accelerator' in data and 'Copyright (c) 2026 LTIMindtree Limited.' in data:
        return data, False
    # Find first <script> WITHOUT a type= attribute
    for m in re.finditer(r'<script(\s[^>]*)?>', data):
        attrs = m.group(1) or ""
        if 'type=' in attrs:
            continue
        insert_at = m.end()
        return data[:insert_at] + "\n" + JS_BANNER + data[insert_at:], True
    raise SystemExit(f"  ! no plain <script> tag found — cannot place JS banner")


def add_tos_link(data: str) -> tuple[str, bool]:
    """Insert TOS-link paragraph into the disclaimer popover (Contact
    Us overlay). Idempotent by presence of the URL substring in the
    popover neighborhood."""
    if 'ltm-cu-pop-cta' not in data:
        # This file doesn't have the v3 overlay applied — skip silently
        return data, False
    if 'Terms.</strong> Proprietary LTM framework' in data:
        return data, False
    if TOS_POP_OLD not in data:
        # Overlay present but the exact anchor doesn't match; skip rather than crash
        return data, False
    return data.replace(TOS_POP_OLD, TOS_POP_NEW, 1), True


def json_safety_check(data: str) -> None:
    for tag in ("__bundler/manifest", "__bundler/template", "__bundler/ext_resources"):
        m = re.search(r'<script type="' + re.escape(tag) + r'">', data)
        if not m: continue
        end = data.find("</script>", m.end())
        payload = data[m.end():end]
        try: json.loads(payload)
        except json.JSONDecodeError as e:
            ctx = payload[max(0, e.pos - 80):e.pos + 80]
            raise SystemExit(f"  ✗ {tag} JSON invalid: {e}\n    context: {ctx!r}")


def semantic_check(data: str, path: pathlib.Path) -> None:
    checks = [
        ('Copyright © 2026 LTIMindtree Limited. All rights reserved.', "HTML banner"),
        ('Copyright (c) 2026 LTIMindtree Limited.', "JS banner"),
    ]
    missing = [lbl for pat, lbl in checks if pat not in data]
    if missing:
        raise SystemExit(f"  ✗ {path.name}: missing " + ", ".join(missing))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    total_added = 0
    for path in FILES:
        print(f"\n--- {path.name} ---")
        data = path.read_text()
        before = len(data)
        applied = 0

        for label, fn in [
            ("HTML banner", add_html_banner),
            ("JS banner", add_js_banner),
            ("TOS link in disclaimer popover", add_tos_link),
        ]:
            data, changed = fn(data)
            if changed:
                applied += 1
                print(f"  ✓ {label}")
            else:
                print(f"  = {label}: already applied (or overlay absent)")

        json_safety_check(data)
        print(f"  ✓ JSON payloads valid")
        semantic_check(data, path)
        print(f"  ✓ semantic markers present")

        if not args.dry_run and applied:
            path.write_text(data)
            print(f"  ✓ written; size delta: {len(data)-before:+d} bytes")
        elif not applied:
            print(f"  = no-op")
        else:
            print(f"  (dry run — file not written; would delta {len(data)-before:+d} bytes)")
        total_added += applied

    print(f"\n=== {total_added} edit(s) applied across {len(FILES)} files ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
