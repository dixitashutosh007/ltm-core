#!/usr/bin/env python3
"""Inject a uniform boot loader overlay into all 4 CIS Tech Advisory
accelerator HTML bundles.

Design (minimal, on-brand):
  - 1.0s coral progress bar under the LTM mark + accelerator name
  - Dark ink backdrop, single centred column
  - Dissolves out via 300ms opacity fade after the page's own scripts
    have painted the intro screen
  - Pure HTML + <style> + <script> — no external deps, no font swap,
    no framework
  - Injected as a self-contained <div id="ltm-boot"> immediately after
    <body>; the accelerator's own DOM sits underneath and paints while
    the loader is on top
  - Adds ~1.8 KB per tool, no runtime cost after the fade completes
    (the loader element is removed from the DOM)

Idempotent: skips if the marker `id="ltm-boot"` is already present.
Applies to plain HTML files — none of these 4 tools has an
add-then-run bundler for THIS overlay (the __bundler/template is
loaded async; the boot loader lives at the OUTER document layer, so
JSON-safety concerns don't apply to it).
"""
import argparse, pathlib, re, sys

TARGETS = [
    (pathlib.Path("/home/user/ltm-core/Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html"),
     "Sovereign Screen", "Board-ready sovereignty triage in under 8 minutes"),
    (pathlib.Path("/home/user/ltm-core/Digital Sovereignty Data Residency Jurisdiction Audit/LTM-Data Residency & Jurisdiction Audit.html"),
     "Data Residency & Jurisdiction Audit", "Where data lives, moves and is processed — jurisdiction-ready"),
    (pathlib.Path("/home/user/ltm-core/finops-value-case/FinOps Value Case (LTM).html"),
     "FinOps Value Case", "The unrealised value at stake in your cloud estate"),
    (pathlib.Path("/home/user/ltm-core/FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html"),
     "FinOps Maturity Screen", "A staged read of your FinOps practice, board to engineering"),
]

# Marker in the injected block so re-runs are no-ops
MARKER = 'id="ltm-boot"'

BOOT_TEMPLATE = '''<div id="ltm-boot" role="status" aria-label="Loading assessment">
  <style>
    #ltm-boot {{
      position: fixed; inset: 0; z-index: 99999;
      background: #141414; color: #ffffff;
      display: flex; align-items: center; justify-content: center;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, "Helvetica Neue", sans-serif;
      opacity: 1; transition: opacity 320ms ease-out;
    }}
    #ltm-boot .ltm-boot-inner {{
      max-width: 460px; width: min(88vw, 460px);
      display: flex; flex-direction: column; align-items: center; gap: 22px;
      padding: 32px;
    }}
    #ltm-boot .ltm-boot-brand {{
      display: flex; align-items: center; gap: 14px;
    }}
    #ltm-boot .ltm-boot-brand img {{
      height: 32px; width: auto; filter: brightness(0) invert(1);
    }}
    #ltm-boot .ltm-boot-brand .div {{
      width: 1px; height: 26px; background: rgba(255,255,255,0.25);
    }}
    #ltm-boot .ltm-boot-brand .sub {{
      font-size: 0.85rem; font-weight: 600; letter-spacing: 0.02em;
      color: rgba(255,255,255,0.9);
    }}
    #ltm-boot .ltm-boot-tool {{
      font-family: 'Archivo', -apple-system, "Segoe UI", sans-serif;
      font-size: 1.35rem; font-weight: 700; line-height: 1.2;
      text-align: center; margin-top: 4px;
    }}
    #ltm-boot .ltm-boot-tag {{
      font-size: 0.85rem; color: rgba(255,255,255,0.7);
      text-align: center; max-width: 40ch;
    }}
    #ltm-boot .ltm-boot-track {{
      width: 100%; height: 3px; background: rgba(255,255,255,0.12);
      border-radius: 3px; overflow: hidden;
    }}
    #ltm-boot .ltm-boot-bar {{
      height: 100%; width: 0%; background: #ff5e4f;
      transition: width 900ms cubic-bezier(0.4, 0, 0.2, 1);
    }}
    #ltm-boot.ltm-boot-out {{ opacity: 0; pointer-events: none; }}
    @media (prefers-reduced-motion: reduce) {{
      #ltm-boot .ltm-boot-bar {{ transition: none; width: 100% !important; }}
      #ltm-boot {{ transition: none; }}
    }}
  </style>
  <div class="ltm-boot-inner">
    <div class="ltm-boot-brand">
      <img src="https://www.ltm.com/content/dam/ltimcorporatewebsite/refresh-images/LTM-Logo.svg" alt="LTM" />
      <span class="div"></span>
      <span class="sub">CIS Tech Advisory</span>
    </div>
    <div class="ltm-boot-tool">{tool_name}</div>
    <div class="ltm-boot-tag">{tool_tag}</div>
    <div class="ltm-boot-track"><div class="ltm-boot-bar"></div></div>
  </div>
  <script>
    (function(){{
      var el = document.getElementById('ltm-boot');
      if (!el) return;
      var bar = el.querySelector('.ltm-boot-bar');
      /* fill in two steps so it looks like progress, not a fixed 1s bar */
      requestAnimationFrame(function(){{ bar.style.width = '55%'; }});
      setTimeout(function(){{ bar.style.width = '100%'; }}, 550);
      /* Fade out once the underlying app has had a chance to paint */
      function done(){{
        el.classList.add('ltm-boot-out');
        setTimeout(function(){{ if (el && el.parentNode) el.parentNode.removeChild(el); }}, 400);
      }}
      var minShow = 1050; /* keep visible ~1s for the polish moment */
      var start = performance.now();
      function whenReady(){{
        var wait = Math.max(0, minShow - (performance.now() - start));
        setTimeout(done, wait);
      }}
      if (document.readyState === 'complete') whenReady();
      else window.addEventListener('load', whenReady, {{ once: true }});
    }})();
  </script>
</div>
'''


def inject(path: pathlib.Path, tool_name: str, tool_tag: str) -> tuple[bool, int]:
    """Return (applied, delta_bytes)."""
    data = path.read_text()
    if MARKER in data:
        return False, 0
    m = re.search(r'<body[^>]*>', data)
    if not m:
        raise SystemExit(f"  ! {path.name}: no <body> tag — cannot inject")
    block = BOOT_TEMPLATE.format(tool_name=tool_name, tool_tag=tool_tag)
    new = data[:m.end()] + "\n" + block + data[m.end():]
    delta = len(new) - len(data)
    path.write_text(new)
    return True, delta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    total = 0
    for path, name, tag in TARGETS:
        if args.dry_run:
            data = path.read_text()
            present = MARKER in data
            print(f"  {'=' if present else '+'} {name}: {'already applied' if present else 'would inject'}")
            continue
        applied, delta = inject(path, name, tag)
        if applied:
            print(f"  ✓ {name}: {delta:+d} bytes")
            total += 1
        else:
            print(f"  = {name}: already applied")
    if not args.dry_run:
        print(f"\n=== {total} of {len(TARGETS)} files updated ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
