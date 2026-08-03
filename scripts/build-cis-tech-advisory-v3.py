#!/usr/bin/env python3
"""Build LTM-CIS-Tech-Advisory-v3.html from v2.

Adds Enterprise IT Strategy as pillar 01 (3 offerings), inserts 2 new
Digital Sovereignty offerings, appends 1 new AI Infusion offering.
Preserves existing HTML/CSS conventions and offering copy verbatim.
"""
import pathlib, re, sys

SRC = pathlib.Path("/home/user/ltm-core/LTM CIS Tech Advisory v2.html")
DST = pathlib.Path("/home/user/ltm-core/LTM-CIS-Tech-Advisory-v3.html")

s = SRC.read_text()

# ---------------------------------------------------------------------------
# 1. Title + meta description — reflect four pillars
# ---------------------------------------------------------------------------
s = s.replace(
    '<meta name="description" content="CIS Tech Advisory — advisory-led services for public cloud, digital sovereignty and AI infusion. It\'s time to Out Create." />',
    '<meta name="description" content="CIS Tech Advisory — advisory-led services across enterprise IT strategy, public cloud, digital sovereignty and AI infusion. It\'s time to Out Create." />',
)

# ---------------------------------------------------------------------------
# 2. Site nav — prepend IT Strategy link
# ---------------------------------------------------------------------------
s = s.replace(
    '    <nav class="site-nav" aria-label="Primary">\n'
    '      <a href="#panel-cloud">Public Cloud</a>\n'
    '      <a href="#panel-sov">Sovereignty</a>\n'
    '      <a href="#panel-ai">AI Infusion</a>\n'
    '      <a href="#accelerators">Accelerators</a>\n'
    '      <a href="#thought">Insights</a>\n'
    '    </nav>',
    '    <nav class="site-nav" aria-label="Primary">\n'
    '      <a href="#panel-strategy">IT Strategy</a>\n'
    '      <a href="#panel-cloud">Public Cloud</a>\n'
    '      <a href="#panel-sov">Sovereignty</a>\n'
    '      <a href="#panel-ai">AI Infusion</a>\n'
    '      <a href="#accelerators">Accelerators</a>\n'
    '      <a href="#thought">Insights</a>\n'
    '    </nav>',
)

# ---------------------------------------------------------------------------
# 3. Hero pillar count 03 → 04
# ---------------------------------------------------------------------------
s = s.replace(
    '    <div class="hero-index" aria-hidden="true">\n      <span class="num">03</span>\n      <span class="label">Live Advisory<br />Pillars</span>\n    </div>',
    '    <div class="hero-index" aria-hidden="true">\n      <span class="num">04</span>\n      <span class="label">Live Advisory<br />Pillars</span>\n    </div>',
)

# ---------------------------------------------------------------------------
# 4. Tabs — insert IT Strategy as first tab, renumber, flip default selection
# ---------------------------------------------------------------------------
s = s.replace(
    '<div class="tabs" role="tablist" aria-label="CIS Tech Advisory offerings">\n'
    '  <div class="tabs-inner">\n'
    '    <button role="tab" id="tab-cloud" aria-controls="panel-cloud" aria-selected="true" class="tab-btn" data-tab="cloud">\n'
    '      <span class="tab-num">01</span> Public Cloud\n'
    '    </button>\n'
    '    <button role="tab" id="tab-sov" aria-controls="panel-sov" aria-selected="false" tabindex="-1" class="tab-btn" data-tab="sov">\n'
    '      <span class="tab-num">02</span> Digital Sovereignty\n'
    '    </button>\n'
    '    <button role="tab" id="tab-ai" aria-controls="panel-ai" aria-selected="false" tabindex="-1" class="tab-btn" data-tab="ai">\n'
    '      <span class="tab-num">03</span> AI Infusion\n'
    '    </button>\n'
    '  </div>\n'
    '</div>',
    '<div class="tabs" role="tablist" aria-label="CIS Tech Advisory offerings">\n'
    '  <div class="tabs-inner">\n'
    '    <button role="tab" id="tab-strategy" aria-controls="panel-strategy" aria-selected="true" class="tab-btn" data-tab="strategy">\n'
    '      <span class="tab-num">01</span> IT Strategy\n'
    '    </button>\n'
    '    <button role="tab" id="tab-cloud" aria-controls="panel-cloud" aria-selected="false" tabindex="-1" class="tab-btn" data-tab="cloud">\n'
    '      <span class="tab-num">02</span> Public Cloud\n'
    '    </button>\n'
    '    <button role="tab" id="tab-sov" aria-controls="panel-sov" aria-selected="false" tabindex="-1" class="tab-btn" data-tab="sov">\n'
    '      <span class="tab-num">03</span> Digital Sovereignty\n'
    '    </button>\n'
    '    <button role="tab" id="tab-ai" aria-controls="panel-ai" aria-selected="false" tabindex="-1" class="tab-btn" data-tab="ai">\n'
    '      <span class="tab-num">04</span> AI Infusion\n'
    '    </button>\n'
    '  </div>\n'
    '</div>',
)

# ---------------------------------------------------------------------------
# 5. panel-cloud must now default-hidden (Strategy takes the visible slot)
# ---------------------------------------------------------------------------
s = s.replace(
    '<section id="panel-cloud" role="tabpanel" aria-labelledby="tab-cloud" aria-hidden="false" class="tab-panel">',
    '<section id="panel-cloud" role="tabpanel" aria-labelledby="tab-cloud" aria-hidden="true" class="tab-panel">',
)

# ---------------------------------------------------------------------------
# 6. Insert new panel-strategy BEFORE panel-cloud
# ---------------------------------------------------------------------------
STRATEGY_PANEL = '''<!-- ENTERPRISE IT STRATEGY -->
<section id="panel-strategy" role="tabpanel" aria-labelledby="tab-strategy" aria-hidden="false" class="tab-panel">
  <div class="tab-intro">
    <div class="tab-intro-inner">
      <div class="tab-intro-label">Enterprise IT Strategy · Out Line the horizon</div>
      <p>IT strategy is where the board conversation actually starts — the 3–5 year direction, the operating model that will support it, and the debt that will hold it back. Advisory that sets the horizon, designs the organisation to reach it, and quantifies the technical debt to be paid down along the way — the front door through which cloud, sovereignty and AI decisions all connect.</p>
    </div>
  </div>
  <div class="offerings"><div class="offerings-inner">

    <article class="offering">
      <div class="offering-visual">
        <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Horizon arc with three milestones">
          <rect width="400" height="300" fill="#f4f4f3"/>
          <path d="M40 240 Q200 40, 360 240" fill="none" stroke="#141414" stroke-width="1.5" opacity="0.4"/>
          <circle cx="120" cy="165" r="10" fill="#141414"/>
          <circle cx="200" cy="90" r="12" fill="#ff5e4f"/>
          <circle cx="280" cy="165" r="10" fill="#ffb4ac"/>
          <line x1="40" y1="260" x2="360" y2="260" stroke="#141414" stroke-width="1" opacity="0.3"/>
        </svg>
      </div>
      <div class="offering-content">
        <h3>IT for the Future</h3>
        <ul>
          <li>Sets a 3–5 year IT vision anchored to enterprise strategy, competitive position and the business ambition the board has actually signed off</li>
          <li>Maps current-state capability, cost, architecture and talent posture against the technology moves the business will demand — not the moves IT would prefer</li>
          <li>Defines an integrated capability roadmap across cloud, data, AI, security, workplace and platform — replacing siloed technology plans that never reconcile</li>
          <li>Sequences investment across horizons — protect, transform and disrupt — with funding envelopes, dependency logic and clear exit criteria per horizon</li>
          <li>Delivers a board-endorsable IT strategy and portfolio the CIO can defend, fund and adjust as the regulatory, economic and AI environment shifts</li>
        </ul>
      </div>
    </article>

    <article class="offering reverse">
      <div class="offering-visual">
        <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Operating model organisation chart">
          <rect width="400" height="300" fill="#f4f4f3"/>
          <rect x="160" y="55" width="80" height="40" fill="#141414"/>
          <line x1="200" y1="95" x2="200" y2="120" stroke="#141414" stroke-width="1.5" opacity="0.5"/>
          <line x1="90" y1="120" x2="310" y2="120" stroke="#141414" stroke-width="1.5" opacity="0.5"/>
          <line x1="90" y1="120" x2="90" y2="145" stroke="#141414" stroke-width="1.5" opacity="0.5"/>
          <line x1="200" y1="120" x2="200" y2="145" stroke="#141414" stroke-width="1.5" opacity="0.5"/>
          <line x1="310" y1="120" x2="310" y2="145" stroke="#141414" stroke-width="1.5" opacity="0.5"/>
          <rect x="55" y="145" width="70" height="36" fill="#ffb4ac"/>
          <rect x="165" y="145" width="70" height="36" fill="#ff5e4f"/>
          <rect x="275" y="145" width="70" height="36" fill="#ffb4ac"/>
          <rect x="55" y="205" width="70" height="36" fill="#141414" opacity="0.55"/>
          <rect x="165" y="205" width="70" height="36" fill="#141414" opacity="0.55"/>
          <rect x="275" y="205" width="70" height="36" fill="#141414" opacity="0.55"/>
        </svg>
      </div>
      <div class="offering-content">
        <h3>Target Operating Model</h3>
        <ul>
          <li>Designs the target operating model end-to-end — capability model, organisation structure, roles, RACI and governance forums</li>
          <li>Establishes decision rights and escalation paths across product, platform, security, FinOps, data and sourcing functions</li>
          <li>Defines the sourcing model — insourced, managed service, partner and hyperscaler — with clear ownership boundaries and no accidental grey zones</li>
          <li>Aligns run-and-change cadence, KPIs and value tracking so the operating model is measurable, not just organisational theatre</li>
          <li>Delivers a mobilisable TOM blueprint, transition plan and first-100-day operating cadence the CxO team can execute against in a 6–12 week engagement</li>
        </ul>
      </div>
    </article>

    <article class="offering">
      <div class="offering-visual">
        <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Technical debt portfolio bars">
          <rect width="400" height="300" fill="#f4f4f3"/>
          <line x1="40" y1="260" x2="360" y2="260" stroke="#141414" stroke-width="1" opacity="0.3"/>
          <rect x="70"  y="140" width="40" height="120" fill="#141414" opacity="0.65"/>
          <rect x="70"  y="110" width="40" height="30"  fill="#ff5e4f"/>
          <rect x="140" y="170" width="40" height="90"  fill="#141414" opacity="0.55"/>
          <rect x="140" y="150" width="40" height="20"  fill="#ffb4ac"/>
          <rect x="210" y="90"  width="40" height="170" fill="#141414" opacity="0.75"/>
          <rect x="210" y="60"  width="40" height="30"  fill="#ff5e4f"/>
          <rect x="280" y="190" width="40" height="70"  fill="#141414" opacity="0.5"/>
          <rect x="280" y="175" width="40" height="15"  fill="#ffb4ac"/>
        </svg>
      </div>
      <div class="offering-content">
        <h3>Technical Debt Portfolio Assessment</h3>
        <ul>
          <li>Quantifies technical debt across infrastructure, applications and data — translating silent risk into hard cash, change velocity and resilience impact</li>
          <li>Categorises debt by driver — deferred upgrades, unsupported stacks, architectural drift, data quality and integration sprawl — so paydown targets the root cause, not the symptom</li>
          <li>Prioritises paydown by business criticality, risk exposure and modernisation ROI — not by loudest voice, oldest ticket or nearest audit</li>
          <li>Reframes debt paydown as a portfolio investment case, not a hidden cost line the CFO writes off each year</li>
          <li>Delivers a costed, sequenced paydown plan and board narrative that unlocks funding for work the business has been quietly deferring</li>
        </ul>
      </div>
    </article>

  </div></div>
</section>

<!-- PUBLIC CLOUD -->
'''
s = s.replace('<!-- PUBLIC CLOUD -->\n', STRATEGY_PANEL)

# ---------------------------------------------------------------------------
# 7. Digital Sovereignty — insert two new offerings
#    After "Quick Sovereignty Posture Assessment" (position 1) → insert
#    "Cross-Border Data Strategy" (position 2), which shifts positions 2/3/4
#    of the existing 4 cards down by one and flips their .reverse alternation.
#    After "Regulatory Alignment & Exit Strategy" → append "Sovereign AI
#    Readiness".
# ---------------------------------------------------------------------------

CROSS_BORDER_CARD = '''    <article class="offering reverse">
      <div class="offering-visual">
        <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cross-border data flow between regions">
          <rect width="400" height="300" fill="#f4f4f3"/>
          <circle cx="105" cy="150" r="55" fill="none" stroke="#141414" stroke-width="1.5" opacity="0.55"/>
          <circle cx="295" cy="150" r="55" fill="none" stroke="#141414" stroke-width="1.5" opacity="0.55"/>
          <circle cx="105" cy="150" r="14" fill="#141414"/>
          <circle cx="295" cy="150" r="14" fill="#ff5e4f"/>
          <path d="M160 130 Q200 90, 240 130" fill="none" stroke="#ff5e4f" stroke-width="2" stroke-dasharray="5 4"/>
          <path d="M240 170 Q200 210, 160 170" fill="none" stroke="#141414" stroke-width="2" opacity="0.55" stroke-dasharray="5 4"/>
          <polygon points="235,126 245,132 233,138" fill="#ff5e4f"/>
          <polygon points="165,174 155,168 167,162" fill="#141414" opacity="0.55"/>
        </svg>
      </div>
      <div class="offering-content">
        <h3>Cross-Border Data Strategy</h3>
        <ul>
          <li>Maps where data actually resides, moves and is processed across the estate — down to the workload, dataset and third-party flow</li>
          <li>Assesses transfer mechanisms in place — SCCs, adequacy decisions, BCRs and derogations — against current data flows and target jurisdictions</li>
          <li>Surfaces flows exposed to Schrems II, EU–US Data Privacy Framework instability and unrecorded cross-border processing that the DPO cannot currently defend</li>
          <li>Sets out architectural options for multi-region operations — from regional isolation and selective repatriation to sovereign-zone and split-processing patterns</li>
          <li>Delivers a defensible cross-border position and 90-day action list — often the fastest, most fundable entry point into a broader sovereignty programme</li>
        </ul>
      </div>
    </article>

'''

SOVEREIGN_AI_CARD = '''    <article class="offering reverse">
      <div class="offering-visual">
        <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sovereign AI stack across jurisdictions">
          <rect width="400" height="300" fill="#f4f4f3"/>
          <rect x="60"  y="205" width="280" height="45" fill="#141414" opacity="0.85"/>
          <rect x="80"  y="150" width="240" height="45" fill="#141414" opacity="0.6"/>
          <rect x="100" y="95"  width="200" height="45" fill="#ffb4ac" opacity="0.85"/>
          <circle cx="200" cy="60" r="16" fill="#ff5e4f"/>
          <line x1="80"  y1="80" x2="80"  y2="260" stroke="#141414" stroke-width="1" opacity="0.35" stroke-dasharray="3 3"/>
          <line x1="320" y1="80" x2="320" y2="260" stroke="#141414" stroke-width="1" opacity="0.35" stroke-dasharray="3 3"/>
        </svg>
      </div>
      <div class="offering-content">
        <h3>Sovereign AI Readiness</h3>
        <ul>
          <li>Assesses model hosting geography, inference footprint and data movement against sovereignty exposure and EU AI Act obligations</li>
          <li>Traces training data provenance, licensing and IP exposure across foundation, fine-tuned and retrieval-augmented models in use</li>
          <li>Reviews sovereign inference options — from in-region hyperscaler zones to sovereign cloud, EU-based specialists and on-premise stacks — against use-case criticality</li>
          <li>Establishes the audit-trail, technical documentation and human-oversight practices needed for high-risk AI systems from August 2026 onward</li>
          <li>Produces a sovereign-AI readiness scorecard and target-state pattern the CIO, CISO, DPO and legal function can jointly back</li>
        </ul>
      </div>
    </article>

'''

# Anchor: existing "Sovereignty Readiness Assessment" card starts with
# <article class="offering reverse"> right after Quick Sovereignty. We
# insert Cross-Border BEFORE it, then flip the .reverse alternation on
# the three shifted cards so the zigzag rhythm survives.

# 7a — insert Cross-Border Data Strategy BEFORE the existing "Sovereignty Readiness Assessment"
SOV_INSERT_ANCHOR = (
    '    <article class="offering reverse">\n'
    '      <div class="offering-visual">\n'
    '        <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Risk register grid">'
)
assert SOV_INSERT_ANCHOR in s, "Cross-Border insert anchor not found"
s = s.replace(SOV_INSERT_ANCHOR, CROSS_BORDER_CARD + SOV_INSERT_ANCHOR, 1)

# 7b — flip .reverse on the three shifted existing cards.
# After insert, position sequence in panel-sov is:
#   1 Quick Sovereignty (offering)          — unchanged, no reverse
#   2 Cross-Border Data (offering reverse)  — new
#   3 Sovereignty Readiness (was reverse)   — becomes (no reverse)
#   4 App Portfolio Mapping (was no)        — becomes (reverse)
#   5 Regulatory Alignment (was reverse)    — becomes (no reverse)
#   6 Sovereign AI Readiness (offering reverse) — new
# Do this by matching each card's <h3> as an in-context anchor.

def flip_reverse(text: str, h3_marker: str, want_reverse: bool) -> str:
    """Toggle whether the card containing <h3>h3_marker</h3> uses
    class='offering reverse' or class='offering'."""
    # Find the h3 first, then walk backward to find the enclosing <article>.
    hpos = text.find(h3_marker)
    if hpos < 0:
        raise SystemExit(f"h3 marker not found: {h3_marker!r}")
    art_open = text.rfind('<article class=', 0, hpos)
    if art_open < 0:
        raise SystemExit(f"<article ... > not found before {h3_marker!r}")
    tag_end = text.find('>', art_open)
    old_tag = text[art_open:tag_end + 1]
    new_tag = ('<article class="offering reverse">' if want_reverse
               else '<article class="offering">')
    if old_tag == new_tag:
        return text  # already correct
    return text[:art_open] + new_tag + text[tag_end + 1:]

s = flip_reverse(s, "<h3>Sovereignty Readiness Assessment</h3>", want_reverse=False)
s = flip_reverse(s, "<h3>Application Portfolio Mapping &amp; Roadmap</h3>", want_reverse=True)
s = flip_reverse(s, "<h3>Regulatory Alignment &amp; Exit Strategy</h3>", want_reverse=False)

# 7c — append Sovereign AI Readiness AFTER "Regulatory Alignment & Exit Strategy" card
# Anchor: the </article> that closes Reg Alignment, followed by the
# "  </div></div>\n</section>" closing the panel-sov offerings block.
SOV_APPEND_ANCHOR = (
    '          <li>Produces evidence and narrative that stands up to regulator, auditor and board scrutiny</li>\n'
    '        </ul>\n'
    '      </div>\n'
    '    </article>\n'
    '\n'
    '  </div></div>\n'
    '</section>\n'
    '\n'
    '<!-- AI INFUSION -->'
)
assert SOV_APPEND_ANCHOR in s, "Sovereign AI append anchor not found"
s = s.replace(
    SOV_APPEND_ANCHOR,
    ('          <li>Produces evidence and narrative that stands up to regulator, auditor and board scrutiny</li>\n'
     '        </ul>\n'
     '      </div>\n'
     '    </article>\n'
     '\n'
     + SOV_APPEND_ANCHOR.split('</article>\n\n', 1)[1].replace(
         '  </div></div>\n</section>',
         SOVEREIGN_AI_CARD + '  </div></div>\n</section>', 1)),
    1,
)

# ---------------------------------------------------------------------------
# 8. AI Infusion — append TokenOps card as final offering
# ---------------------------------------------------------------------------
TOKENOPS_CARD = '''    <article class="offering">
      <div class="offering-visual">
        <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Token flow throttled by governance">
          <rect width="400" height="300" fill="#f4f4f3"/>
          <g stroke="#141414" stroke-width="1" opacity="0.3">
            <line x1="40" y1="260" x2="360" y2="260"/><line x1="40" y1="260" x2="40" y2="40"/>
          </g>
          <path d="M40 240 Q90 100, 200 70 T360 60" fill="none" stroke="#141414" stroke-width="2" stroke-dasharray="5 4" opacity="0.55"/>
          <path d="M40 240 Q90 200, 200 175 T360 155" fill="none" stroke="#ff5e4f" stroke-width="2.5"/>
          <circle cx="200" cy="175" r="8" fill="#ff5e4f"/>
          <line x1="200" y1="55" x2="200" y2="260" stroke="#141414" stroke-width="1" opacity="0.4" stroke-dasharray="3 3"/>
          <text x="205" y="70" fill="#141414" opacity="0.55" font-family="Inter,sans-serif" font-size="10">quota</text>
        </svg>
      </div>
      <div class="offering-content">
        <h3>TokenOps · GenAI Consumption Governance</h3>
        <ul>
          <li>Establishes cost visibility across tokens, inference calls, embeddings, agent runs and vector operations — the unit metrics FinOps was not built for</li>
          <li>Implements quota, rate-limit and tenancy controls that prevent runaway spend before it reaches the CFO's radar</li>
          <li>Defines model-selection governance — when to route to a frontier model, a smaller open-weight model, an internal fine-tune or a cached response</li>
          <li>Builds per-use-case unit economics — cost per resolved ticket, per generated artefact, per agent action — the business will actually recognise</li>
          <li>Delivers a TokenOps blueprint and operating cadence that puts GenAI consumption under the same discipline as cloud spend — before the bill forces the conversation</li>
        </ul>
      </div>
    </article>

'''

AI_APPEND_ANCHOR = (
    '          <li>Prepares the organisation for AI cost governance to become a board-level metric</li>\n'
    '        </ul>\n'
    '      </div>\n'
    '    </article>\n'
    '\n'
    '  </div></div>\n'
    '</section>\n'
    '\n'
    '\n'
    '<!-- Accelerators -->'
)
assert AI_APPEND_ANCHOR in s, "TokenOps append anchor not found"
s = s.replace(
    AI_APPEND_ANCHOR,
    ('          <li>Prepares the organisation for AI cost governance to become a board-level metric</li>\n'
     '        </ul>\n'
     '      </div>\n'
     '    </article>\n'
     '\n'
     + TOKENOPS_CARD
     + '  </div></div>\n</section>\n\n\n<!-- Accelerators -->'),
    1,
)

DST.write_text(s)
print(f"wrote {DST}")
print(f"size delta vs v2: {len(s) - len(SRC.read_text()):+d} bytes")
print(f"total size: {len(s)} bytes")

# Quick sanity checks
checks = [
    ("panel-strategy", 'id="panel-strategy"'),
    ("tab-strategy", 'id="tab-strategy"'),
    ("IT Strategy nav link", 'href="#panel-strategy">IT Strategy'),
    ("04 Live Pillars", '<span class="num">04</span>'),
    ("Strategy tab num 01", '<span class="tab-num">01</span> IT Strategy'),
    ("Cloud tab num 02", '<span class="tab-num">02</span> Public Cloud'),
    ("Sov tab num 03", '<span class="tab-num">03</span> Digital Sovereignty'),
    ("AI tab num 04", '<span class="tab-num">04</span> AI Infusion'),
    ("Cloud panel now hidden", 'id="panel-cloud" role="tabpanel" aria-labelledby="tab-cloud" aria-hidden="true"'),
    ("Strategy panel visible", 'id="panel-strategy" role="tabpanel" aria-labelledby="tab-strategy" aria-hidden="false"'),
    ("New: IT for the Future", "<h3>IT for the Future</h3>"),
    ("New: Target Operating Model", "<h3>Target Operating Model</h3>"),
    ("New: Technical Debt", "<h3>Technical Debt Portfolio Assessment</h3>"),
    ("New: Cross-Border Data Strategy", "<h3>Cross-Border Data Strategy</h3>"),
    ("New: Sovereign AI Readiness", "<h3>Sovereign AI Readiness</h3>"),
    ("New: TokenOps", "<h3>TokenOps · GenAI Consumption Governance</h3>"),
]
missing = [lbl for lbl, pat in checks if pat not in s]
if missing:
    raise SystemExit("SANITY FAIL: " + ", ".join(missing))
print(f"  ✓ {len(checks)} sanity checks passed")
