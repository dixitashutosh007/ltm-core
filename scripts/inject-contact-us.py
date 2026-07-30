#!/usr/bin/env python3
"""Inject a Contact Us tab (vertical, right-rail) and a collapsible
disclaimer chip into each LTM accelerator HTML bundle. The overlay is a
self-contained <script> block inserted just before the closing </head>.

Placement chosen to avoid all in-app UI:
  - Contact Us tab: vertical, right edge, mid-page. Rotated text.
    Won't collide with the app's sticky top bar or bottom controls.
  - Disclaimer: small chip bottom-left ("⚠ Disclaimer"). Click expands
    a popover with the full text + a Contact Us button.

Idempotent — running twice does not duplicate. Removes any prior v1 or
v2 block before inserting the current one, so re-runs cleanly replace.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGETS = [
    ("finops-value-case/FinOps Value Case (LTM).html", "FinOps Value Case", "v1.0 · Aug 2026"),
    ("FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html", "FinOps Maturity Screen", "v1.0 · Aug 2026"),
    ("Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html", "Sovereign Compass", "v1.0 · Aug 2026 · Financial Services"),
    ("Digital Sovereignty Data Residency Jurisdiction Audit/LTM-Data Residency & Jurisdiction Audit.html", "Data Residency & Jurisdiction Audit", "v1.0 · Aug 2026"),
]
MARKER = "LTM_CONTACT_OVERLAY_v2"
OLD_MARKERS = ("LTM_CONTACT_OVERLAY_v1", "LTM_CONTACT_OVERLAY_v2")

def snippet(accelerator: str, framework: str) -> str:
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
    /* Vertical right-rail Contact Us tab — sits mid-page, out of top/bottom bar range */
    + ".ltm-cu-tab{{position:fixed;right:0;top:50%;transform:translate(0,-50%);z-index:2147483000;"
    + "background:#ff5e4f;color:#fff;border:0;cursor:pointer;"
    + "font:600 12px/1 Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
    + "letter-spacing:.14em;text-transform:uppercase;"
    + "padding:14px 10px;border-radius:8px 0 0 8px;"
    + "writing-mode:vertical-rl;box-shadow:-2px 2px 12px rgba(0,0,0,.18);"
    + "transition:background .15s ease,padding .15s ease}}"
    + ".ltm-cu-tab:hover{{background:#e5412f;padding-right:14px}}"
    + ".ltm-cu-tab .ltm-cu-tab-icon{{display:inline-block;margin-bottom:6px;transform:rotate(180deg);font-size:14px}}"

    /* Collapsible disclaimer chip — bottom-left, out of the way */
    + ".ltm-cu-chip{{position:fixed;left:14px;bottom:14px;z-index:2147482999;"
    + "background:#141414;color:#fff;border:0;cursor:pointer;"
    + "font:600 11px/1 Inter,-apple-system,sans-serif;letter-spacing:.08em;text-transform:uppercase;"
    + "padding:9px 12px 9px 10px;border-radius:999px;box-shadow:0 3px 12px rgba(0,0,0,.22);"
    + "display:inline-flex;align-items:center;gap:6px}}"
    + ".ltm-cu-chip:hover{{background:#000}}"
    + ".ltm-cu-chip .ltm-cu-chip-dot{{width:8px;height:8px;border-radius:50%;background:#ff5e4f;flex:none}}"

    /* Disclaimer popover — anchored above the chip */
    + ".ltm-cu-pop{{position:fixed;left:14px;bottom:56px;z-index:2147482999;"
    + "width:min(420px,calc(100vw - 28px));background:#fff;border:1px solid #ececec;"
    + "border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.22);"
    + "font:400 12.5px/1.55 Inter,-apple-system,sans-serif;color:#4a4a4a;"
    + "display:none}}"
    + ".ltm-cu-pop.open{{display:block}}"
    + ".ltm-cu-pop-hd{{display:flex;align-items:center;justify-content:space-between;"
    + "padding:12px 14px;border-bottom:1px solid #ececec}}"
    + ".ltm-cu-pop-hd strong{{color:#141414;font-size:12px;letter-spacing:.1em;text-transform:uppercase}}"
    + ".ltm-cu-pop-hd button{{background:none;border:0;font-size:20px;color:#666;cursor:pointer;line-height:1}}"
    + ".ltm-cu-pop-body{{padding:14px}}"
    + ".ltm-cu-pop-body p{{margin:0 0 8px}}"
    + ".ltm-cu-pop-body p:last-of-type{{margin:0}}"
    + ".ltm-cu-pop-body strong{{color:#141414}}"
    + ".ltm-cu-pop-cta{{margin-top:12px;background:#ff5e4f;color:#fff;border:0;cursor:pointer;"
    + "font:600 12px/1 Inter,sans-serif;padding:9px 14px;border-radius:6px;display:inline-block}}"
    + ".ltm-cu-pop-cta:hover{{background:#e5412f}}"

    /* Modal — contact form */
    + ".ltm-cu-modal{{border:0;border-radius:10px;padding:0;width:min(560px,94vw);"
    + "box-shadow:0 20px 60px rgba(0,0,0,.25);font:400 14px/1.5 Inter,-apple-system,sans-serif;color:#141414}}"
    + ".ltm-cu-modal::backdrop{{background:rgba(0,0,0,.45)}}"
    + ".ltm-cu-modal header{{display:flex;align-items:center;justify-content:space-between;"
    + "padding:14px 18px;border-bottom:1px solid #ececec}}"
    + ".ltm-cu-modal header strong{{font-size:15px}}"
    + ".ltm-cu-modal header button{{background:none;border:0;font-size:22px;cursor:pointer;color:#666}}"
    + ".ltm-cu-body{{padding:16px 18px;display:grid;gap:10px;max-height:60vh;overflow:auto}}"
    + ".ltm-cu-body label{{display:grid;gap:4px;font-size:12px;color:#555}}"
    + ".ltm-cu-body input,.ltm-cu-body textarea{{font:400 14px/1.4 Inter,sans-serif;"
    + "padding:8px 10px;border:1px solid #d9d9d9;border-radius:6px;color:#141414;background:#fff}}"
    + ".ltm-cu-body .row{{display:grid;gap:10px;grid-template-columns:1fr 1fr}}"
    + ".ltm-cu-note{{font-size:11.5px;color:#666;background:#f7f5f2;padding:10px 12px;border-radius:6px;line-height:1.5}}"
    + ".ltm-cu-modal footer{{display:flex;justify-content:flex-end;gap:8px;"
    + "padding:12px 18px;border-top:1px solid #ececec;background:#fafafa}}"
    + ".ltm-cu-modal footer button{{font:600 13px/1 Inter,sans-serif;padding:9px 14px;"
    + "border-radius:6px;cursor:pointer;border:1px solid transparent}}"
    + ".ltm-cu-btn-cancel{{background:#fff;border-color:#d9d9d9;color:#444}}"
    + ".ltm-cu-btn-send{{background:#ff5e4f;color:#fff}}"
    + ".ltm-cu-btn-send:hover{{background:#e5412f}}"

    + "@media (max-width:640px){{"
    +   ".ltm-cu-tab{{padding:12px 8px;font-size:11px}}"
    +   ".ltm-cu-body .row{{grid-template-columns:1fr}}"
    +   ".ltm-cu-pop{{left:8px;right:8px;bottom:52px;width:auto}}"
    + "}}"
    + "@media print{{"
    +   ".ltm-cu-tab,.ltm-cu-chip,.ltm-cu-pop,.ltm-cu-modal{{display:none !important}}"
    + "}}";

  function inject() {{
    if (document.getElementById("ltm-cu-tab")) return;
    var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

    /* Contact Us tab (vertical, right-rail) */
    var tab = document.createElement("button");
    tab.id = "ltm-cu-tab"; tab.className = "ltm-cu-tab"; tab.type = "button";
    tab.setAttribute("aria-label", "Contact CIS Tech Advisory");
    tab.innerHTML = "<span class='ltm-cu-tab-icon'>✉</span>Contact Us";
    tab.onclick = openModal;
    document.body.appendChild(tab);

    /* Disclaimer chip (bottom-left) */
    var chip = document.createElement("button");
    chip.id = "ltm-cu-chip"; chip.className = "ltm-cu-chip"; chip.type = "button";
    chip.setAttribute("aria-expanded", "false");
    chip.innerHTML = "<span class='ltm-cu-chip-dot'></span>Disclaimer";
    document.body.appendChild(chip);

    /* Disclaimer popover */
    var pop = document.createElement("div");
    pop.id = "ltm-cu-pop"; pop.className = "ltm-cu-pop";
    pop.setAttribute("role", "dialog"); pop.setAttribute("aria-label", "Assessment disclaimer");
    pop.innerHTML =
      "<div class='ltm-cu-pop-hd'><strong>Important — please read</strong>"
      + "<button type='button' aria-label='Close' id='ltm-cu-pop-close'>×</button></div>"
      + "<div class='ltm-cu-pop-body'>"
      +   "<p><strong>This is a preliminary, indicative assessment.</strong> It uses self-reported inputs and published references to give a directional read.</p>"
      +   "<p>It is <strong>not</strong> legal, tax, financial or regulatory advice, and <strong>not</strong> a commitment, quote or guarantee of outcomes.</p>"
      +   "<p>Specific interpretations of regulations (GDPR, NIS2, DORA, EU AI Act, EUCS, UK data protection law and any sector-specific rules) should be confirmed with qualified counsel and, where relevant, your competent supervisory authority.</p>"
      +   "<p><strong>Your privacy.</strong> All answers stay in your browser. Nothing is transmitted to LTM unless you use Contact Us.</p>"
      +   "<button class='ltm-cu-pop-cta' type='button' id='ltm-cu-pop-cta'>Contact us for a scoped engagement →</button>"
      + "</div>";
    document.body.appendChild(pop);
    chip.onclick = function(){{
      var isOpen = pop.classList.toggle("open");
      chip.setAttribute("aria-expanded", isOpen ? "true" : "false");
    }};
    pop.querySelector("#ltm-cu-pop-close").onclick = function(){{ pop.classList.remove("open"); chip.setAttribute("aria-expanded","false"); }};
    pop.querySelector("#ltm-cu-pop-cta").onclick = function(){{ pop.classList.remove("open"); openModal(); }};

    /* Contact modal */
    var dlg = document.createElement("dialog");
    dlg.id = "ltm-cu-modal"; dlg.className = "ltm-cu-modal";
    dlg.innerHTML =
      "<form method='dialog'>"
      + "<header><strong>Contact CIS Tech Advisory</strong>"
      +   "<button value='cancel' aria-label='Close' type='button' id='ltm-cu-close'>×</button></header>"
      + "<div class='ltm-cu-body'>"
      +   "<div class='ltm-cu-note'>We'll draft an email to <strong>ashutosh.dixit@ltm.com</strong> with your details and a short summary of your report. You can review and edit it in your email app before sending.</div>"
      +   "<div class='row'><label>Your name<input name='name' required></label>"
      +     "<label>Company<input name='company' required></label></div>"
      +   "<div class='row'><label>Role<input name='role'></label>"
      +     "<label>Work email<input type='email' name='email' required></label></div>"
      +   "<label>Phone (optional)<input name='phone'></label>"
      +   "<label>What would you most like to discuss?"
      +     "<textarea name='priority' rows='3' placeholder='e.g. how to prioritise the top 3 findings'></textarea></label>"
      + "</div>"
      + "<footer>"
      +   "<button type='button' class='ltm-cu-btn-cancel' id='ltm-cu-cancel'>Cancel</button>"
      +   "<button type='submit' class='ltm-cu-btn-send' id='ltm-cu-send'>Open in email app</button>"
      + "</footer></form>";
    document.body.appendChild(dlg);
    dlg.querySelector("#ltm-cu-close").onclick = function(){{ dlg.close(); }};
    dlg.querySelector("#ltm-cu-cancel").onclick = function(){{ dlg.close(); }};
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
      var href = "mailto:" + encodeURIComponent(CFG.to)
        + "?subject=" + encodeURIComponent(subject)
        + "&body=" + encodeURIComponent(lines.join("\\n"));
      window.location.href = href;
      dlg.close();
    }});

    /* Close popover on outside click */
    document.addEventListener("click", function(ev){{
      if (!pop.classList.contains("open")) return;
      if (pop.contains(ev.target) || chip.contains(ev.target)) return;
      pop.classList.remove("open"); chip.setAttribute("aria-expanded","false");
    }});

    /* Expose for accelerator to push report data */
    window.LTM = window.LTM || {{}};
    window.LTM.contactUs = {{
      open: openModal,
      setReport: function(r){{ state.report = r; }},
      configure: function(c){{ if (c) Object.assign(CFG, c); }}
    }};
  }}

  function openModal(){{
    var m = document.getElementById("ltm-cu-modal");
    if (m && typeof m.showModal === "function") m.showModal();
    else if (m) m.setAttribute("open","");
  }}

  /* Wait for the bundler shell to finish unpacking */
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

def strip_prior(data: str) -> str:
    """Remove any earlier v1/v2 injection block cleanly."""
    for marker in OLD_MARKERS:
        pat = re.compile(r"<!-- " + re.escape(marker) + r" -->\s*<script>[\s\S]*?</script>\s*", re.M)
        data = pat.sub("", data)
    return data

def patch(path: pathlib.Path, accelerator: str, framework: str) -> str:
    data = path.read_text(encoding="utf-8")
    before = len(data)
    data = strip_prior(data)
    if "</head>" not in data:
        return "SKIPPED: no </head> found"
    block = snippet(accelerator, framework)
    data = data.replace("</head>", block + "</head>", 1)
    path.write_text(data, encoding="utf-8")
    delta = len(data) - before
    return f"patched ({'{:+d}'.format(delta)} bytes)"

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
