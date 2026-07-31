# CIS Tech Advisory — Accelerator Write-up for Sales & Leadership

**To:** Sales team, Leadership
**From:** CIS Tech Advisory
**Purpose:** Cascade and review the four accelerators below. Please share feedback on positioning, target buyer, and go-to-market motion.

Four accelerators are ready for field use. Two sit under the **Digital Sovereignty** pillar and two under **FinOps / Cloud Financial Management**. Each is a self-contained, browser-based tool (single HTML file, no data leaves the browser) that produces a consulting-grade PDF for the customer.

---

## 1. Digital Sovereignty Screening (Sovereign Screen)

- **Name:** Sovereign Screen — Digital Sovereignty Screening
- **Short description:** A short, structured screen that tells a UK/EU business which digital-sovereignty laws apply to it and how ready it is against them. Positions the message: *"Where your data lives is not who can reach it — physical residency is the easy half; jurisdictional reach is the half that gets missed."*
- **How we present it to the customer:**
  - **Primary:** Free assessment (self-serve, indicative mode) — lead-gen at the top of the funnel.
  - **Secondary:** Sales-team-driven / Consulting-led (extended, facilitated mode) — used in discovery workshops to qualify a Data Residency & Jurisdiction Audit engagement.
- **Key features:**
  - Two tiers — Indicative (self-serve) and Extended (facilitated).
  - Triage across UK & EU sovereignty regimes (GDPR, NIS2, DORA, EU AI Act, EUCS, UK GDPR).
  - Sector-aware (initial content set tuned for financial services).
  - Guided questionnaire, progress rail, and branded report cover with the customer's logo.
  - Editable question bank — content can be versioned, exported, and swapped per sector without a code change.
- **URL:** https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen.html
- **What problem it solves:**
  - Most clients conflate data residency with data sovereignty and are blind to extraterritorial reach (e.g. US CLOUD Act on EU-hosted workloads).
  - Boards want a one-page answer to *"are we exposed?"* before funding a full audit.
  - Gives Sales a **60-second qualifying conversation** and a warm hand-off into the deeper Jurisdiction Audit.
  - Creates a repeatable, branded artefact instead of ad-hoc discovery decks.

---

## 2. Digital Sovereignty — Data Residency & Jurisdiction Audit

- **Name:** Data Residency & Jurisdiction Audit
- **Short description:** A regulator-aware, deep-dive assessment of where the client's data physically lives, who processes it, and whether that stands up to the regulations reshaping European enterprise architecture — GDPR, NIS2, DORA, the EU AI Act, EUCS and UK GDPR.
- **How we present it to the customer:**
  - **Primary:** Consulting-lead assessment — delivered as a paid, time-boxed engagement by CIS Tech Advisory.
  - **Secondary:** Sales-team-driven demo / walk-through to justify the engagement after a Sovereign Screen surfaces exposure.
- **Key features:**
  - Regulator-aware — every finding cites the specific Article / requirement it maps to.
  - Risk-graded — RAG status per regulation plus a business-vs-regulatory heat map.
  - Structured across 8 domains (scope, data flows, cloud sovereignty & assurance, sub-processors, transfers, etc.).
  - Phased roadmap — comprehensive strategy plus task-level remediation steps (Phase 1 / 2 / 3).
  - Board-ready PDF export — cover page, findings, remediation, disclaimer — consulting-grade output.
  - Configurable question bank (drawer-managed) so the same tool serves multiple sectors.
- **URL:** https://ltm-core.s3.us-east-1.amazonaws.com/Data-Residency-Jurisdiction-Audit.html
- **What problem it solves:**
  - Clients cannot demonstrate to regulators (or their own boards) that they know where regulated data sits and who can reach it.
  - Sub-processor sprawl silently moves data across jurisdictions with no owner tracking it.
  - Hyperscaler defaults quietly re-introduce transfer risk after adequacy work is "done".
  - Gives CIS Tech Advisory a **repeatable, IP-backed engagement** (fixed scope, fixed price, fixed deliverable) instead of a bespoke assessment every time.
  - Direct up-sell path into remediation, cloud landing-zone re-architecture, and sovereign-cloud migrations.

---

## 3. FinOps Value Case ("Do you need FinOps?")

- **Name:** FinOps Value Case
- **Short description:** An 8-minute qualification assessment that establishes whether a client has a material, quantifiable cloud cost problem — and roughly what it is worth. Anchored on the Flexera benchmark that **~29% of cloud spend is wasted** and the message: *"You are already paying for FinOps. Just not getting it."*
- **How we present it to the customer:**
  - **Primary:** Free assessment (self-assessment) — top-of-funnel lead magnet on the LTM site and in outbound campaigns.
  - **Secondary:** Sales-team-driven in a first-meeting to produce a live £ / $ number the CFO can react to.
- **Key features:**
  - Not a maturity score — outputs a **defensible monetary value case** the client can take to Finance.
  - Multi-currency support and industry-benchmark anchoring (Flexera 2026 State of the Cloud, n=753).
  - Branded, downloadable value-case report with organisation logo and respondent attribution.
  - ~8 minutes, no data leaves the browser — safe to run in a live customer meeting.
  - Configurable question bank so benchmarks and thresholds can be refreshed each year.
- **URL:** http://ltm-core.s3-website-us-east-1.amazonaws.com/finops-value-case.html
- **What problem it solves:**
  - Customers know cloud is expensive but cannot put a number on the waste — every FinOps conversation stalls at "prove it".
  - Sales needs a fast, defensible qualification step before pitching a full FinOps engagement.
  - Converts a vague "we should probably look at cloud costs" into a **quantified opportunity** and a natural next step (Maturity Assessment → Consulting engagement).
  - Bypasses the classic objection *"we already have dashboards"* by separating visibility from control.

---

## 4. FinOps Maturity Assessment

- **Name:** FinOps Maturity Screen — Cloud Financial Management Accelerator
- **Short description:** A staged assessment of cloud financial maturity — where the client actually sits today, what is blocking the next stage, and the sequence of moves that gets them there. Positioning line: *"Spend visibility is not spend control."*
- **How we present it to the customer:**
  - **Primary:** Consulting-lead assessment — run by CIS Tech Advisory as a facilitated workshop.
  - **Secondary:** Self-assessment mode available for prospects and existing accounts to seed the conversation.
- **Key features:**
  - Five-stage FinOps maturity model with **gating logic** — foundations cannot be skipped by scoring well elsewhere.
  - ~15 minutes, ~5 stages of questions with a branded report.
  - Identifies the *specific* blocker to the next maturity stage (not a generic score).
  - Configurable question bank (`finops-qbank-2026-05-08.json`) — content can be refreshed as the FinOps Foundation framework evolves.
  - Consulting-grade PDF with staged maturity view, gaps, and recommended sequence of interventions.
- **URL:** http://ltm-core.s3-website-us-east-1.amazonaws.com/finops-screen.html
- **What problem it solves:**
  - Clients over-invest in tooling and dashboards while the underlying **ownership, defaults, and accountability** stay broken — savings leak from the same gap year after year.
  - Executives want a defensible baseline and a "what next" answer, not another benchmark deck.
  - Natural follow-on from the FinOps Value Case: **Value Case sizes the prize → Maturity Assessment sequences the work** → CIS Tech Advisory delivers it.
  - Gives Sales and Delivery a shared, evidence-based view to scope Phase 1 engagements.

---

## Accelerator flow (how they stack together)

- **Digital Sovereignty pillar:** *Sovereign Screen* (free triage) → *Data Residency & Jurisdiction Audit* (paid consulting engagement) → remediation / sovereign-cloud migration.
- **FinOps pillar:** *FinOps Value Case* (free, quantifies the £/$ prize) → *FinOps Maturity Assessment* (facilitated, sequences the work) → FinOps operating-model build-out and optimisation delivery.

## Requested feedback from Sales & Leadership

1. Does the positioning line for each accelerator resonate with the buyers you are talking to?
2. Are we pricing the free / paid split correctly, or should any of these shift?
3. Which sectors should we prioritise for the next round of question-bank tailoring?
4. Any named accounts where we should pilot these in the next 30 days?

Please reply with comments inline, or drop time on my calendar for a 20-minute walk-through of any of the four tools.
