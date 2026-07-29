#!/usr/bin/env python3
"""Inject a persistent Contact Us overlay + standard disclaimer strip
into each LTM accelerator HTML bundle, without touching the bundled app.

The overlay is a self-contained <script> block inserted just before the
closing </head>. It waits for the bundler to finish unpacking (removal
of #__bundler_loading / #__bundler_thumbnail) and then appends:

  - a floating "Contact Us" pill (top-right, always visible)
  - a bottom disclaimer strip
  - a modal that pre-fills a mailto: to ashutosh.dixit@ltm.com with
    customer details + report essentials

Idempotent — running twice does not duplicate the block. Marker string:
LTM_CONTACT_OVERLAY_v1.
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGETS = [
    ("finops-value-case/FinOps Value Case (LTM).html", "FinOps Value Case", "v1.0 · Aug 2026"),
    ("FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html", "FinOps Maturity Screen", "v1.0 · Aug 2026"),
    ("Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html", "Sovereign Compass", "v1.0 · Aug 2026 · Financial Services"),
    ("Digital Sovereignty Data Residency Jurisdiction Audit/LTM-Data Residency & Jurisdiction Audit.html", "Data Residency & Jurisdiction Audit", "v1.0 · Aug 2026"),
]
MARKER = "LTM_CONTACT_OVERLAY_v1"

def snippet(accelerator: str, framework: str) -> str:
    # single-line escape of the double-quote-containing constants
    return f"""<!-- {MARKER} -->
<script>
(function () {{
  if (window.__LTM_CU_INJECTED) return; window.__LTM_CU_INJECTED = true;
  var CFG = {{
    to: "ashutosh.dixit@ltm.com",
    accelerator: {accelerator!r},
    framework: {framework!r}
  }};
  var state = {{ report: null }};

  var css = ""
    + ".ltm-cu-pill{{position:fixed;top:12px;right:14px;z-index:2147483000;font:600 12px/1 Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;letter-spacing:.04em;padding:9px 14px;border-radius:999px;background:#ff5e4f;color:#fff;border:0;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.18)}}"
    + ".ltm-cu-pill:hover{{background:#e5412f}}"
    + ".ltm-cu-strip{{position:fixed;left:0;right:0;bottom:0;z-index:2147482999;background:#f7f5f2;border-top:3px solid #ff5e4f;color:#4a4a4a;font:400 12px/1.5 Inter,-apple-system,sans-serif;padding:10px 16px 10px 16px;display:flex;gap:14px;align-items:center;justify-content:space-between;box-shadow:0 -2px 10px rgba(0,0,0,.06)}}"
    + ".ltm-cu-strip .ltm-cu-strip-text{{max-width:calc(100% - 190px)}}"
    + ".ltm-cu-strip strong{{color:#141414}}"
    + ".ltm-cu-strip a{{color:#e5412f;text-decoration:none;border-bottom:1px solid rgba(229,65,47,.35)}}"
    + ".ltm-cu-strip button{{background:#141414;color:#fff;border:0;font:600 11px/1 Inter,sans-serif;padding:7px 12px;border-radius:6px;cursor:pointer;flex:none}}"
    + ".ltm-cu-strip button:hover{{background:#000}}"
    + ".ltm-cu-modal{{border:0;border-radius:10px;padding:0;width:min(560px,94vw);box-shadow:0 20px 60px rgba(0,0,0,.25);font:400 14px/1.5 Inter,-apple-system,sans-serif;color:#141414}}"
    + ".ltm-cu-modal::backdrop{{background:rgba(0,0,0,.45)}}"
    + ".ltm-cu-modal header{{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid #ececec}}"
    + ".ltm-cu-modal header strong{{font-size:15px}}"
    + ".ltm-cu-modal header button{{background:none;border:0;font-size:22px;cursor:pointer;color:#666}}"
    + ".ltm-cu-body{{padding:16px 18px;display:grid;gap:10px;max-height:60vh;overflow:auto}}"
    + ".ltm-cu-body label{{display:grid;gap:4px;font-size:12px;color:#555}}"
    + ".ltm-cu-body input,.ltm-cu-body textarea{{font:400 14px/1.4 Inter,sans-serif;padding:8px 10px;border:1px solid #d9d9d9;border-radius:6px;color:#141414;background:#fff}}"
    + ".ltm-cu-body .row{{display:grid;gap:10px;grid-template-columns:1fr 1fr}}"
    + ".ltm-cu-note{{font-size:11.5px;color:#666;background:#f7f5f2;padding:10px 12px;border-radius:6px;line-height:1.5}}"
    + ".ltm-cu-modal footer{{display:flex;justify-content:flex-end;gap:8px;padding:12px 18px;border-top:1px solid #ececec;background:#fafafa}}"
    + ".ltm-cu-modal footer button{{font:600 13px/1 Inter,sans-serif;padding:9px 14px;border-radius:6px;cursor:pointer;border:1px solid transparent}}"
    + ".ltm-cu-btn-cancel{{background:#fff;border-color:#d9d9d9;color:#444}}"
    + ".ltm-cu-btn-send{{background:#ff5e4f;color:#fff}}"
    + ".ltm-cu-btn-send:hover{{background:#e5412f}}"
    + "@media (max-width:640px){{.ltm-cu-body .row{{grid-template-columns:1fr}}.ltm-cu-strip{{flex-direction:column;align-items:flex-start;gap:8px}}.ltm-cu-strip .ltm-cu-strip-text{{max-width:100%}}}}";

  function inject() {{
    if (document.getElementById("ltm-cu-pill")) return;
    var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

    var pill = document.createElement("button");
    pill.id = "ltm-cu-pill"; pill.className = "ltm-cu-pill"; pill.type = "button";
    pill.textContent = "Contact Us";
    pill.onclick = open;
    document.body.appendChild(pill);

    var strip = document.createElement("div");
    strip.className = "ltm-cu-strip"; strip.setAttribute("role","note");
    strip.innerHTML =
      "<div class='ltm-cu-strip-text'><strong>Preliminary, indicative assessment.</strong> "
      + "Self-reported inputs and published references only. <strong>Not</strong> legal, tax, financial or regulatory advice "
      + "and <strong>not</strong> a commitment. Confirm interpretations of GDPR, NIS2, DORA, EU AI Act, EUCS and UK data protection law with qualified counsel. "
      + "Answers stay in your browser — nothing is sent to LTM unless you use Contact Us."
      + "</div><button type='button'>Contact Us for a scoped engagement</button>";
    strip.querySelector("button").onclick = open;
    document.body.appendChild(strip);
    document.body.style.paddingBottom = (Math.max(96, parseInt(getComputedStyle(document.body).paddingBottom)||0)) + "px";

    var dlg = document.createElement("dialog");
    dlg.id = "ltm-cu-modal"; dlg.className = "ltm-cu-modal";
    dlg.innerHTML =
      "<form method='dialog'>"
      + "<header><strong>Contact CIS Tech Advisory</strong><button value='cancel' aria-label='Close' type='button' id='ltm-cu-close'>×</button></header>"
      + "<div class='ltm-cu-body'>"
      +   "<div class='ltm-cu-note'>We'll draft an email to <strong>ashutosh.dixit@ltm.com</strong> with your details and a short summary of your report. You can review and edit it in your email app before sending.</div>"
      +   "<div class='row'><label>Your name<input name='name' required></label><label>Company<input name='company' required></label></div>"
      +   "<div class='row'><label>Role<input name='role'></label><label>Work email<input type='email' name='email' required></label></div>"
      +   "<label>Phone (optional)<input name='phone'></label>"
      +   "<label>What would you most like to discuss?<textarea name='priority' rows='3' placeholder='e.g. how to prioritise the top 3 findings'></textarea></label>"
      + "</div>"
      + "<footer><button type='button' class='ltm-cu-btn-cancel' id='ltm-cu-cancel'>Cancel</button>"
      +   "<button type='submit' class='ltm-cu-btn-send' id='ltm-cu-send'>Open in email app</button></footer>"
      + "</form>";
    document.body.appendChild(dlg);
    dlg.querySelector("#ltm-cu-close").onclick = function(){{dlg.close();}};
    dlg.querySelector("#ltm-cu-cancel").onclick = function(){{dlg.close();}};
    dlg.querySelector("form").addEventListener("submit", function(ev){{
      ev.preventDefault();
      var fd = new FormData(ev.target);
      var r = state.report || {{}};
      var lines = [
        "Hi Ashutosh,","",
        "I've just completed the " + CFG.accelerator + " assessment on the LTM CIS Tech Advisory site and would like to walk through the results.","",
        "My details:",
        "  Name:    " + (fd.get("name")||""),
        "  Company: " + (fd.get("company")||""),
        "  Role:    " + (fd.get("role")||"—"),
        "  Email:   " + (fd.get("email")||""),
        "  Phone:   " + (fd.get("phone")||"—"),
        "",
        "Report essentials (from the tool):",
        "  Assessment:      " + CFG.accelerator,
        "  Framework:       " + CFG.framework,
        "  Generated:       " + new Date().toISOString(),
        "  Headline:        " + (r.headline || "not generated yet"),
        "  Top signals:     " + ((r.topSignals||[]).join(" | ") || "—"),
        "  My priority:     " + (fd.get("priority")||"—"),
        "",
        "Please get in touch to set up a 30-minute readout.","",
        "Thanks,", (fd.get("name")||"")
      ];
      var subject = "CIS Tech Advisory — " + CFG.accelerator + " — " + (fd.get("company")||"");
      var href = "mailto:" + encodeURIComponent(CFG.to) + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\\n"));
      window.location.href = href;
      dlg.close();
    }});

    // expose so the accelerator can push report essentials
    window.LTM = window.LTM || {{}};
    window.LTM.contactUs = {{
      open: open,
      setReport: function(r){{ state.report = r; }},
      configure: function(c){{ if (c) Object.assign(CFG, c); }}
    }};
  }}

  function open(){{
    var m = document.getElementById("ltm-cu-modal");
    if (m && typeof m.showModal === "function") m.showModal();
    else if (m) m.setAttribute("open","");
  }}

  // Wait for the bundler to finish unpacking before injecting
  function ready(){{
    var loading = document.getElementById("__bundler_loading");
    var thumb   = document.getElementById("__bundler_thumbnail");
    if (loading || thumb){{ return setTimeout(ready, 250); }}
    inject();
  }}
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready);
  else ready();
}})();
</script>
"""

def patch(path: pathlib.Path, accelerator: str, framework: str) -> str:
    data = path.read_text(encoding="utf-8")
    if MARKER in data:
        return "skipped (already patched)"
    block = snippet(accelerator, framework)
    if "</head>" not in data:
        return "SKIPPED: no </head> found"
    new = data.replace("</head>", block + "</head>", 1)
    path.write_text(new, encoding="utf-8")
    return f"patched (+{len(block)} bytes)"

def main() -> int:
    for rel, name, fw in TARGETS:
        p = ROOT / rel
        if not p.exists():
            print(f"  ! missing: {rel}")
            continue
        print(f"  {rel}\n      → {patch(p, name, fw)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
