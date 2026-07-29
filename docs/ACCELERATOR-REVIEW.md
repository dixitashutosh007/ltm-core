# LTM CIS Tech Advisory — Accelerator Review

**Scope:** Technical and legal validation of the four customer-facing HTML accelerators, plus a standard disclaimer block and Contact Us / lead-capture design.

**Reviewer:** Content review only — this report is not a legal opinion. Any regulatory-references check below should be confirmed with your Legal / Compliance function before public release.

**Files reviewed:**
- `finops-value-case/FinOps Value Case (LTM).html`
- `FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html`
- `Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html`
- `Digital Sovereignty Data Residency Jurisdiction Audit/LTM-Data Residency & Jurisdiction Audit.html`

**Method:** Each accelerator is a minified single-file bundle. Question banks were extracted directly from the JavaScript state (`questions:[...]`) inside each bundle, decoded from `\u` escapes.

---

## 1. FinOps Value Case

**What it does:** Pre-maturity qualification. Sizes the money-at-stake from cloud spend, anchored to published waste benchmarks, to answer "do we need FinOps?".

### Strengths

- **Signals-based weighted scoring** (`visibility`, `predictability`, `value`, `ownership`) is well-structured — each question carries `signals:[{id,w}]` weights, not just a flat score.
- **"Don't know" is scored, not skipped** — an honest design that prevents inflated results.
- **Clear estate-shape questions (E1–E6)** feed the calculation transparently (`cloud_share`, `migration_ahead` factors are visible).
- Existing disclaimer is honest about being **indicative**: *"Indicative estimate based on self-reported inputs and published industry benchmarks. Figures illustrate the scale of opportunity and are not a guarantee of savings."*

### Issues / recommended fixes

| # | Issue | Recommendation |
|---|---|---|
| 1 | The **waste-rate benchmarks** used to size opportunity are not cited in-tool. The template JSON says *"LTIMindtree directional adjustment — replace with engagement data"* which is honest, but the customer-facing output does not surface the source. | Add a footnote to the report cover: *"Waste-rate anchors sourced from Flexera State of the Cloud 2024 and FinOps Foundation State of FinOps. Sector modifiers are LTIMindtree directional adjustments."* |
| 2 | Currency handling: slider is unbounded in units (default 2 000 000, max 100 000 000) with **no currency label**. A UK/EU user could read this as GBP or EUR when the calculation implicitly treats it as USD. | Add explicit currency selector (USD / GBP / EUR / INR) and label the slider suffix. |
| 3 | Q E2 lists Oracle Cloud as `hyper:false` but Oracle is a hyperscaler by any commercial definition. | Change `hyper:true` for Oracle Cloud (or reclassify what `hyper` means and rename the flag). |
| 4 | No explicit **not-financial-advice** language. The tool outputs dollar figures that a CFO could reasonably read as a savings commitment. | Add to standard disclaimer: *"Indicative and directional only. Not a commitment, quote or financial advice."* |
| 5 | No **currency / date-stamp** on report output. | Show `Assessment framework v1.0 · generated <date> · currency = X` on the cover of the generated report. |

### Not-legal-advice risk

**Low.** The tool speaks in financial-opportunity terms, not regulatory ones. The only recommendation is to strengthen the "indicative, not a commitment" language.

---

## 2. FinOps Maturity Screen

**What it does:** Rapid, capability-level read of FinOps practice against a five-stage maturity model (Chaos → Informed → Optimised → Strategic → Automated), with Crawl-Walk-Run remediation.

### Strengths

- **Explicit five-stage model** aligns to the FinOps Foundation Framework (stages: Crawl / Walk / Run — the tool's Chaos / Informed / Optimised / Strategic / Automated is a reasonable extension).
- **Weighted, critical-flagged questions** — critical items (root MFA, billing export, account ownership) can drag a stage score, which is correct behaviour.
- **Domain-tagged questions** (governance / visibility / culture) allow radar-chart output.
- **Remediation string per question** is a very good design — every negative answer produces a concrete next step.

### Issues / recommended fixes

| # | Issue | Recommendation |
|---|---|---|
| 1 | **No visible disclaimer at all** in the extracted state or output. | Add the standard disclaimer block. This is the biggest single gap. |
| 2 | The tool positions itself as *"inspired by the FinOps Foundation's five-stage maturity model"* in marketing copy, but the in-tool report does not explicitly disclaim: *"Not an official FinOps Foundation Certified Practitioner assessment."* Using the FinOps Foundation's name in a scoring tool without that disclaimer risks a trademark issue. | Add: *"Aligned to FinOps Framework v2024 references. Not an official FinOps Foundation assessment or certification. 'FinOps' is a trademark of the FinOps Foundation."* |
| 3 | Question **C1** ("Is MFA enforced on root / master accounts…") is a **security-control question**, not a FinOps question. If it fails, the customer may reasonably infer they have a security finding from an LTM tool. This is a claim we don't want to make in a free assessment. | Reframe as a FinOps-adjacent question ("Is there an account-ownership and access model that supports cost governance?") or move it to a separate "Foundations" section clearly labelled *"foundational IT controls, not a security audit"*. |
| 4 | Question **C4** ("Does the finance team have read-only access to cloud billing consoles…") — the option scoring is fine but the remediation string *"Grant finance read-only billing access…"* assumes RBAC configuration the customer may not own. Should soften. | *"Work with your cloud platform team to grant finance read-only billing / cost console access."* |
| 5 | Weights (2, 1.5, 1) are not defined anywhere in the visible output; a customer cannot see why they scored what they did. | Add an "About the score" panel at the end: total possible per stage, weighting rules, critical-question rule ("any red critical caps the stage score at 60"). |
| 6 | **Framework version + review date** not visible in output. | Show `Framework v1.0 · reviewed <date>` on the report cover. |

### Not-legal-advice risk

**Low → Medium.** The trademark exposure for the "FinOps" mark is real. Recommended fix in row 2 above resolves it.

---

## 3. Sovereign Screen (finance vertical)

**What it does:** Fast, board-ready read on sovereignty exposure across seven lenses (strategic, jurisdictional, data, cloud, data-centre, AI, operational resilience). Rules-engine style with conditional questions.

### Strengths

- **Existing disclaimer is strong and legally aware:** *"Indicative triage / applicability screening. Not legal advice. Applicability depends on specific facts and should be confirmed with qualified counsel."*
- **Fact-value model with `shown_if` conditional logic** — good rules-engine design; irrelevant questions don't appear.
- **DORA entity types are correctly enumerated** (credit institution, IORP pension fund, CASP, AIFM, CCP, etc.) — this matches Article 2 of Regulation (EU) 2022/2554.
- **Provider HQ ≠ data location** distinction is correctly surfaced (hint on Q_CLOUDHQ). This is the single most-misunderstood point in EU sovereignty discussions and the tool gets it right.
- **`Q_SOVOFFER`** correctly distinguishes a sovereign / EU-boundary offering with contractual + operational controls from a standard commercial region — this is the CLOUD Act awareness that most competing tools miss.

### Issues / recommended fixes

| # | Issue | Recommendation |
|---|---|---|
| 1 | Size band "Micro (<10 staff, ≤ €2m)" uses the **EU Commission Recommendation 2003/361/EC** definition of micro-enterprise. Correct, but the tool should note the source, and confirm the threshold applies to *turnover or balance-sheet total*, not headcount alone. | Add source cite in tooltip: *"EU Commission Rec. 2003/361/EC — headcount AND (turnover ≤ €2m OR balance sheet ≤ €2m)."* |
| 2 | `Q_SOVOFFER` scores "Yes — sovereign offering with controls" as **100** without asking *which* controls. A customer could self-declare 100 without having, for example, EU-only support personnel, keys held outside the provider's home jurisdiction, or contractual protection against foreign disclosure requests. | Add a follow-up multi-select: *"Which controls are contractually in place?"* covering: EU-only operations personnel; customer-held encryption keys (HYOK); contractual protection vs. extraterritorial disclosure; local operating entity with local jurisdiction; sub-processor list restricted to EU. Only 100 if the customer selects at least 3. |
| 3 | The output uses the term "**foreign-access risk**" — accurate but a lay reader may interpret it as espionage / hostile access. In legal terms this is *lawful access by a foreign authority under its home jurisdiction* (CLOUD Act, FISA 702, etc.). | Expand tooltip on the term: *"Lawful access by a foreign authority under its home law — e.g., US CLOUD Act, FISA 702, executive orders. Not hostile / unauthorised access."* |
| 4 | The Sovereign Screen is **finance-vertical** (knowledge-base file: `ds-knowledge-base.finance.json`). The public tool does not clearly say which vertical it applies to. A healthcare user could reasonably expect it to cover HIPAA / EHDS and be misled. | Show a "Vertical: Financial Services (EU/UK)" chip prominently on the cover and homepage. Add a sector selector on first screen (grey-out other verticals as "coming soon" if not yet built). |
| 5 | US regulations (CLOUD Act, FISA 702) are implicit; not named in the visible output. | Add to the "Foreign access risk" explainer: *"Relevant US statutes: CLOUD Act (2018), FISA §702, Executive Order 14086."* |

### Not-legal-advice risk

**Medium.** The tool already carries the correct disclaimer. The residual risk is (a) DORA/GDPR interpretation drift over time (regulatory landscape changes) and (b) the row 2 issue where a self-declared "yes with controls" could produce a false-negative sovereignty rating. Recommend adding *"Framework last reviewed <date>. Regulations evolve — reconfirm with counsel."* to the disclaimer.

---

## 4. Data Residency & Jurisdiction Audit (DR&J)

**What it does:** L2 sovereignty offering — detailed assessment against DORA, NIS2, GDPR, UK GDPR, EU AI Act, EUCS, focused on where data lives, moves and is processed. Eleven sections (A–K), ~ full mapping across regulations × sectors × workloads.

*Note: the LTM-branded file is 9 MB with the content packed inside a compressed bundler. Content was reviewed from the sibling `Unformatted-Data-Residency-Jurisdiction-Audit.html` (114 KB), which shares the same `BANK` structure.*

### Strengths

- **Strongest disclaimer of the four:** *"This assessment provides advisory guidance to support architecture and governance decisions. It is not a legal opinion. Specific interpretations of GDPR, NIS2, DORA, the EU AI Act, EUCS and UK data protection law should be confirmed with qualified counsel and your competent supervisory authority."* — model text for the other three to follow.
- **Regulation citations are precise and correct:**
  - GDPR — Regulation (EU) 2016/679 ✓
  - NIS2 — Directive (EU) 2022/2555 ✓
  - DORA — Regulation (EU) 2022/2554 ✓
  - EU AI Act — Regulation (EU) 2024/1689 ✓
  - EUCS — EU Cybersecurity Certification Scheme for Cloud Services ✓
  - UK GDPR & DPA 2018 ✓
- **Article-level references** (e.g., *"NIS2 Art. 3, Annexes I–II"*) — this is the correct level of citation for a diagnostic tool.
- **Sector list is accurate to NIS2 Annexes I / II** (essential vs. important entities). All the high-criticality sectors (finserv, energy, water, transport, digital infrastructure, health) are correctly flagged `high:true`.
- **Section coverage is comprehensive** (11 sections spanning scope, inventory, location, transfers, vendors, resilience, AI, cloud, governance, incident, outcomes).
- **Schrems II awareness** is baked in — the international-transfers section explicitly references transfer impact assessments.

### Issues / recommended fixes

| # | Issue | Recommendation |
|---|---|---|
| 1 | Regulatory scope is **EU/UK only**. A US, APAC or LATAM enterprise using the tool could infer they are compliant when in fact HIPAA / GLBA / CCPA / DPDPA (India) / PIPL (China) / PDPA (Singapore) / APRA (Australia) etc. are not assessed. | Add scope banner at top of report: *"Scope: EU + UK regulatory perimeter. Non-EU jurisdictions (US federal & state, India DPDPA, PIPL, PDPA, APRA, LGPD, etc.) are out of scope for this assessment. Contact us for a broader jurisdictional review."* |
| 2 | The **EU AI Act** section treats AI risk as one dimension. In reality the Act has three separate obligation regimes: prohibited practices (Art. 5), high-risk systems (Annex III), and general-purpose AI models (Art. 51+). A single boolean/score obscures this. | Split the AI section (G) into three sub-sections keyed by classification. Add tooltip: *"AI Act obligations differ sharply by classification — high-risk (Annex III) triggers data-governance duties under Art. 10 that low-risk systems do not."* |
| 3 | Some questions probe for information that may be **subject to legal privilege** (e.g., current investigations, whistleblower reports, pending regulator correspondence). If a customer answers freely and later a dispute arises, that self-reported data could be discoverable. | Add before those questions: *"You may choose 'Prefer not to say' for any question. This tool stores answers only in your browser; no data leaves your device unless you contact us."* |
| 4 | The regulation list is presented as though exhaustive. It is not — sector-specific rules (PSD2, MiFID II, CRR/CRD for banking; Solvency II for insurance; MDR/IVDR for medical devices; DSA/DMA for platforms; eIDAS 2 for identity) are not covered. | Add: *"Additional sector-specific regulations (PSD2, MiFID II, Solvency II, MDR/IVDR, DSA/DMA, eIDAS 2, etc.) are not assessed by this tool. Contact us for a full regulatory mapping."* |
| 5 | The framework `updated: "2026-07"` is set as a future date. Either this is a placeholder or intentional forward-dating; either way it looks incorrect at time of publishing. | Set to actual last-review date; add a rule that any date reaching the current calendar month triggers a "review overdue" flag. |
| 6 | **Where does data go when the user answers questions?** The tool appears to be browser-only (single-file HTML) but the customer has no way to verify this. | Add explicit privacy note under the disclaimer: *"All answers are stored only in your browser. Nothing is transmitted to LTM unless you click 'Contact Us'. Clear your browser storage to remove."* |

### Not-legal-advice risk

**Low.** Existing disclaimer is strong, citations are accurate, tone is diagnostic not prescriptive. Row 2 (AI Act sub-classification) is the most material technical fix.

---

## 5. Cross-cutting findings

| # | Issue | Applies to | Recommendation |
|---|---|---|---|
| A | **Disclaimer inconsistency.** Only Sovereign Screen and DR&J carry "not legal advice" language. FinOps Value Case says "not a guarantee of savings" (financial-slant equivalent). FinOps Maturity has no visible disclaimer. | All 4 | Adopt the standard disclaimer block (below) across all four, with the vertical-specific line adjusted per tool. |
| B | **No lead-capture / Contact Us.** No accelerator captures who the customer is or gives them a one-click way to reach LTM. Every session is anonymous and unrecoverable. | All 4 | Add Contact Us in header (persistent) and at end of report. Text-based email (mailto:) pre-filled with report essentials — see snippet below. |
| C | **No framework versioning shown in output.** | 3 of 4 (DR&J has it) | Show `Framework v<x> · reviewed <YYYY-MM>` on report cover for all four. |
| D | **No privacy note** telling the customer that answers stay in-browser. Sensitive information (spend, jurisdictions, AI use cases) is being entered without explicit assurance. | All 4 | Add a one-line privacy note under the disclaimer: *"All answers are stored only in your browser. Nothing is sent to LTM unless you use Contact Us."* |
| E | **No FinOps Foundation trademark disclaimer** in FinOps Maturity Screen (positioned as inspired by their model). | FinOps Maturity | Add: *"'FinOps' is a trademark of the FinOps Foundation. This tool is not an official FinOps Foundation assessment."* |
| F | **Currency handling** for money-in inputs is implicit / unlabelled. | FinOps Value Case | Currency selector (USD/GBP/EUR/INR) on first estate question. |
| G | **Vertical/sector scope** is not surfaced. Finance-vertical tools should say so. | Sovereign Screen (finance KB), FinOps Value Case (BFSI modifiers in template) | Show sector chip prominently on cover. |
| H | **Bundled deployment is fragile.** These are compressed single-file bundles from a custom bundler. Any content change today requires rebuilding from source. The React/JSX source only exists for Sovereign Screen (`SovereignScreen.jsx`). | All 4 | Recover source for FinOps Value Case, FinOps Maturity, DR&J Audit into the repo — otherwise every fix is a rebuild-and-repack. |

---

## 6. What is missing (per your prompt)

**Explicitly missing across the set:**

1. **Lead-capture mechanism.** No customer has a way to be contacted after using a free assessment. Every free-tool session is currently a lost lead.
2. **Persistent Contact Us in header** — required per your brief.
3. **End-of-report Contact Us that emails LTM with the report essentials pre-filled** — required per your brief. Implemented as a `mailto:` (see snippet).
4. **Privacy note** that answers are browser-only.
5. **Currency selector** (FinOps Value Case).
6. **Sector/vertical selector or chip** (Sovereign Screen).
7. **Framework version + review date on report cover** (three of four).
8. **AI Act sub-classification** (DR&J).
9. **Recovered source code** for three of the four bundled tools — currently only Sovereign Screen has editable React source in the repo. Without source we're patching around bundles.
10. **Analytics / usage measurement.** No way to know how many customers use the tools, drop off where, or convert.

---

## 7. Standard disclaimer block (adopt across all 4)

See `docs/snippets/standard-disclaimer.html`. Copy the block into each accelerator (or use the injection script — see §8). The block is written to satisfy the strictest of the four (DR&J's legal-adjacent language) so it works everywhere.

**Text (plain):**

> **This is a preliminary, indicative assessment.** It uses self-reported inputs and published industry references to give a directional read. It is **not** legal, tax, financial or regulatory advice, and it is **not** a commitment, quote or guarantee of outcomes. Specific interpretations of regulations (GDPR, NIS2, DORA, EU AI Act, EUCS, UK data protection law and any sector-specific rules) should be confirmed with qualified counsel and, where relevant, your competent supervisory authority. Framework references evolve — reconfirm dates before relying on any figure.
>
> **Your privacy.** All answers are stored only in your browser. Nothing is transmitted to LTM unless you click *Contact Us*.
>
> **For a scoped engagement**, use the Contact Us button — a member of our CIS Tech Advisory team will reach out to walk through your report.

---

## 8. Contact Us design (text-based email, no attachments)

**Header (persistent):** small "Contact Us" pill in the top-right, always visible while the assessment is in progress.

**End-of-report (primary CTA):** a full-width Contact Us panel that appears once the customer generates their report. Clicking it opens the user's default mail client (mailto:) with:

- **To:** `ashutosh.dixit@ltm.com`
- **Subject:** `CIS Tech Advisory — <Accelerator name> — <Customer name if entered>`
- **Body (pre-filled, editable before send):**
  ```
  Hi Ashutosh,

  I've just completed the <Accelerator name> assessment on the LTM CIS
  Tech Advisory site and would like to walk through the results.

  My details:
    Name:    <customer name>
    Company: <customer company>
    Role:    <customer role>
    Email:   <customer email>
    Phone:   <optional>

  Report essentials (from the tool):
    Assessment:      <accelerator name>
    Framework:       <framework version + review date>
    Generated:       <ISO date/time>
    Headline score:  <score / stage / band>
    Top signals:     <top 3 findings in one line each>
    My priority:     <top-of-mind ask>

  Please get in touch to set up a 30-minute readout.

  Thanks,
  <customer name>
  ```

The customer reviews the drafted email in their mail client, edits if needed, and sends with one click. No attachment (per your instruction). The report itself is separately downloadable as a PDF from the same panel.

See `docs/snippets/contact-us.html` for the reference implementation and `scripts/inject-contact-us.py` for the safe overlay script that adds it to each of the four bundled accelerators without touching their internals.

---

## 9. Recommended sequence

1. **Now:** Apply overlay injection script — adds Contact Us + disclaimer to all four bundles today, without needing source.
2. **Next 2 weeks:** Recover React/JSX source for FinOps Value Case, FinOps Maturity, DR&J Audit into the repo. Fix in-source: FinOps Foundation TM disclaimer, hyperscaler classification, AI Act sub-classification, currency selector, sector chip. Rebuild.
3. **Next 4 weeks:** Legal sign-off on the standard disclaimer text (10-min review by counsel).
4. **Ongoing:** Framework refresh cadence — set a quarterly review calendar for the four accelerators; regulations change (EU AI Act obligations phase in through 2026, DORA in enforcement, NIS2 transposition still landing in member states).
