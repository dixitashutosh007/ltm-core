# Data Residency & Jurisdiction Audit — v1 Review

**File reviewed:** `Digital Sovereignty Data Residency Jurisdiction Audit/LTM-Data Residency & Jurisdiction Audit.html`
**Sibling reviewed for readability:** `Unformatted-Data-Residency-Jurisdiction-Audit.html` (114 KB; content-identical to the bundled version, verified by extracting the compressed JS payload)
**Framework version (per KB `meta.version`):** 1.0.0
**Framework `updated`:** 2026-07
**Live URL:** https://ltm-core.s3.us-east-1.amazonaws.com/Data-Residency-Jurisdiction-Audit.html

**Reviewer disclosure.** Content review by a technical reviewer, not a legal opinion. Every claim about a specific regulation is a pointer to the primary source, not an interpretation for a specific customer.

**Method.** Full `const BANK` object extracted from the unformatted sibling; bundled version's compressed JS payload decompressed and diffed against unformatted to confirm same content. Every question, option, finding, and applicability rule was walked; the engine (`collectFindingsForQuestion`, `collectAllFindings`, `ragForRegulation`, `postureScore`, `postureLabel`, `businessImpactBand`, `questionApplies`, `autoSelectRegs`) was read end-to-end.

---

## 0. What the tool is

A structured, regulator-aware data-residency assessment for UK & EU enterprises. Walks 11 sections (A–K) covering entity classification, data inventory, location, transfers, third parties, resilience, AI, cloud sovereignty, governance, incident reporting and target outcomes. 29 questions across 6 regulations.

**Inventory:**

| Metric | Value |
|---|---|
| Regulations covered | 6 (GDPR, UK GDPR, NIS2, DORA, EU AI Act, EUCS) |
| Sectors | 14 |
| Sections | 11 |
| Questions | 29 |
| Sources per regulation | Legal reference cited in each regulation object, but **no `sources:[{name,url}]` array** — cf. Sovereign Screen where every regime carries authoritative URLs |
| Report render | 3-phase remediation model (Stop the exposure → Architect target state → Embed & differentiate) |

---

## 1. What's good

The tool is materially well-crafted:

- **29 questions each with detailed `findings[]`** — every finding has an article citation, severity, title, detail, remedy, and step-by-step actions. Substantially more granular than Sovereign Screen v1.
- **Post-Schrems II awareness is baked in** — the SCC / TIA / supplementary measures pattern is correctly stated at Q_D1 and Q_D2.
- **CLOUD Act framing correct** — Q_H1 rationale explicitly distinguishes operator jurisdiction from data-centre location.
- **Matrix question C2** — per-data-category × per-location matrix is a clever mechanic for capturing the residency picture in one question.
- **Backup residency (F1)** is called out — often the largest hidden exposure in real estates.
- **AI compute location (G2)** is framed as a "blind spot" — accurate.
- **Three-phase remediation model** (Phase 1 stop / Phase 2 architect / Phase 3 embed) is a sound way to sequence findings.
- **Disclaimer text is strong** — *"advisory guidance … not a legal opinion. Specific interpretations of GDPR, NIS2, DORA, the EU AI Act, EUCS and UK data protection law should be confirmed with qualified counsel and your competent supervisory authority."*
- **NIS2 fines quoted correctly** — €10m/2% for essential entities (Art. 34(4)), €7m/1.4% for important entities (Art. 34(5)).
- **Engine architecture** — `questionApplies` filter + `collectFindingsForQuestion` per-answer accumulation + `ragForRegulation` RAG per regulation is a clean design.

---

## 2. Legal-accuracy defects (HIGH priority)

These change a customer-visible answer or produce a legally-wrong output.

### 2.1 No DPF adequacy handling for US transfers

Q_D1 (transfers) offers "SCCs / IDTA with safeguards" as the only mechanism for restricted transfers; Q_C2 matrix treats `us-cloud` as `critical` regardless of DPF certification; Q_F1 treats US backup as `critical`; Q_G2 treats US AI compute as `critical`.

The **EU-US Data Privacy Framework** (Commission Implementing Decision (EU) 2023/1795, effective 10 July 2023) provides adequacy for DPF-certified US recipients. The **UK-US Data Bridge** (October 2023, extending the DPF for UK-relevant data) is a mirror. A customer using a DPF-certified US processor is **not** in the SCC/TIA world — they're on adequacy.

Same defect Sovereign Screen had at v1. **Same fix pattern applies:** add a Q_DPFCERT-style follow-up when US hosting/transfer is selected; grade `certified` as informational; grade `SCCs/BCRs` as medium (TIA required); grade `no mechanism` as critical.

**Legal impact:** DPF-certified US hosting is currently over-flagged as critical.

### 2.2 Q_C1 has no "Google Cloud — EU regions only" option

Q_C1 asymmetric on providers:

- AWS: two options — "EU regions only" (positive) and "includes non-EU regions" (high severity)
- Azure: two options — "EU regions only" (positive) and "includes non-EU regions" (high severity)
- **GCP: single option** — "Google Cloud" (high severity — flagged as "US-operated hyperscaler in use")

A customer running entirely in GCP `europe-west*` regions gets a high-severity finding purely because they picked "Google Cloud" — the tool has no way to record that they are EU-locked. This is a **systemic false-positive** for every GCP-EU customer.

**Fix:** split GCP into "GCP — EU regions only" and "GCP — includes non-EU regions", identical treatment to AWS/Azure.

### 2.3 Missing regime blocks for FS customers doing residency audits

A UK-based FS firm running the DR&J Audit receives no finding for:

- **UK Operational Resilience** (FCA PS21/3; PRA SS2/21) — impact-tolerance mapping and outsourcing rules materially affect data-location decisions
- **UK Critical Third Parties regime** (FSMA 2023 Part 9; FCA PS24/16; PRA PS16/24)
- **EU Data Act** (Regulation (EU) 2023/2854) — the switching / non-personal-data-access rules are *directly* about data residency and jurisdictional access
- **UK AI regulatory approach** (ICO / FCA / PRA SS1/23) — a UK-only firm using high-risk AI gets zero AI-regime output

**Impact:** the tool is titled "Data Residency & Jurisdiction Audit" but omits three regimes (Data Act, UK Op Res, UK CTP) that directly govern data-location and jurisdictional-access questions for FS customers.

### 2.4 Q_H1 "US-with-sovereign-boundary" scores medium without evidence

Q_H1 option `us-eubound` (US operator with EU 'sovereign' boundary) scores `medium` and produces a finding saying "sovereign-boundary offerings reduce but do not eliminate jurisdictional exposure". Correct in principle. But there's **no follow-up asking which controls are in place** — EU-only personnel, customer-held keys (HYOK), contractual anti-disclosure clauses, EU-only sub-processor list, local operating entity.

Same false-pass mechanic Sovereign Screen had; **same fix pattern applies:** conditional follow-up multi-select on `us-eubound` gathering the specific control set.

---

## 3. Legal-accuracy defects (MEDIUM priority)

### 3.1 Q_C1 missing several US-HQ providers

Q_C1 enumerates AWS / Azure / GCP / sovereign / on-prem / colo. Missing: **Oracle Cloud, IBM Cloud, Salesforce / Heroku, Snowflake, Databricks**. Any customer running on these US-HQ providers has to shoe-horn their choice into "colo" or leave the question blank — same CLOUD Act detection gap Sovereign Screen had at v1.

### 3.2 Q_C2 matrix rows don't mirror Q_B1

Q_B1 asks about 7 data categories (pii / special / financial / behavioural / aitraining / proprietary / government). Q_C2 matrix (per-category-per-location) has only 4 rows: pii / special / financial / behavioural. **AI training data** and **government/classified data** — both flagged as critical severity in Q_B1 — have no per-location row.

**Result:** a customer holding classified data can't record where it lives, and the report loses the residency picture for the most sensitive category.

### 3.3 Q_C2 matrix missing UK column

Columns are: EU-only / EU + encrypted non-EU backup / US non-EU cloud / multi-region global / unknown. **UK hosting is a distinct case** — EU→UK is currently adequate (Commission adequacy decision 2021, subject to periodic review), and UK→EU is also adequate. A customer hosting in the UK for EU data doesn't fit any column cleanly.

### 3.4 Q_A2 DORA financial entity list is thin

Q_A2 offers: credit / invest+asset+trading combined / insurer+reinsurer+IORP combined / other-fin / na. DORA Art. 2(1) enumerates ~20 categories; the combined options work for triage but miss:

- Payment institutions and EMIs (they're catchall under "other-fin")
- CASPs (also "other-fin")
- CCPs, CSDs, trading venues — merged into "invest"
- Credit rating agencies, benchmark administrators, securitisation and trade repositories, data reporting service providers, crowdfunding — all "other-fin"

**Impact:** proportionate obligation calls are directional rather than accurate for specialised firms.

### 3.5 `ragForRegulation` "green" doesn't distinguish "no data" from "actually clean"

The `ragForRegulation` function returns `green` when `assessed && no material findings`. `assessed` is `some active question references the regulation`. Since every regulation is referenced by at least one question, `assessed` is nearly always true after auto-select.

**Result:** a customer who skips half the assessment sees "green" for regulations whose questions they didn't answer. Should also check `> 0 questions answered per regulation`.

### 3.6 `postureScore` weights are un-calibrated per question

The score is `100 – Σ(severity_weight)` with weights `{critical:26, high:13, medium:5, low:1}`. No cap per question. A multi-select answer set (e.g., Q_B1) can push 5+ findings from one question. Two problems:

- No stated basis for the weights (why 26? why 13?).
- Multi-select questions can produce order-of-magnitude larger score impacts than single-select ones.

**Not a legal defect** — just uneven scoring. Consider capping severity contribution per question, or documenting the weight rationale.

### 3.7 Q_F2 misses "financial data → banking secrecy" anchor

Q_B1's `financial` option cites DORA Art. 5 as the anchor for financial data. DORA doesn't make financial data itself high-risk — DORA applies to financial *entities* regardless of what they process. The stronger anchor for financial data specifically is national **banking secrecy** rules (e.g., §275 of the German BGB, French CMF, etc.) and PCI DSS for card data.

**Small legal inaccuracy** — the finding text says "financial data feeds critical functions" which is a stretch as a DORA Art. 5 anchor.

---

## 4. Legal-accuracy defects (LOW priority — accuracy nits)

- **Q_G1** doesn't distinguish GPAI (Art. 51+ obligations) from Annex III high-risk AI. Same gap Sovereign Screen v1 had.
- **Q_G1** lists "health" as an Annex III trigger. Annex III item 5(c) is specifically **life and health insurance risk assessment and pricing**, not health data processing generally. As worded, could over-scope.
- **Q_H2** offers "High / Substantial / None" for EUCS assurance level — missing "Basic" (the third level of EUCS).
- **Q_J1** describes DORA reporting as "its own major-incident timeline" — could cite the RTS-specific 4h/72h/1-month cadence (Commission Delegated Regulation on incident reporting under DORA Art. 20).
- **No `sources:[{name,url}]` array** on each regulation object — cf. Sovereign Screen where 89 URLs across 16 regimes point at EUR-Lex / legislation.gov.uk / regulators. DR&J's `regulations` array cites the ELI-style reference ("Regulation (EU) 2016/679") but not a link. Customers can't click through to authority.
- **Meta `updated:"2026-07"`** — should be a more specific date (2026-07-30 like Sovereign Screen after Phase 0), and should be surfaced on the report cover.
- **No framework version stamp on the report cover** (unlike Sovereign Screen post-Phase-0).

---

## 5. What's genuinely missing (coverage extensions)

Ranked by relevance to a UK/EU FS customer running a data-residency audit:

| Missing | Priority | Why it belongs in a residency tool |
|---|---|---|
| **EU Data Act** (Reg. (EU) 2023/2854) | **High** | Directly governs cloud switching, portability, and unlawful third-country access to non-personal data held in the EU. Residency-critical. |
| **UK Op Res** (FCA PS21/3; PRA SS2/21) | **High** | For any UK FS customer — impact tolerances shape which data can leave the UK |
| **UK CTP regime** (FSMA 2023 Part 9) | **High** | CTPP designations directly affect residency architecture |
| **DPF adequacy** (Comm. Impl. Dec. 2023/1795) + **UK-US Data Bridge** | **High** | See §2.1 |
| **UK AI regulatory approach** (ICO / FCA / PRA SS1/23) | Medium | For UK AI compute residency questions |
| **DORA subcontracting RTS** (Comm. Del. Reg. 2025/532) | Medium | Data-location transparency in DORA supply chains |
| **NIS2 governance obligations** (Art. 20 personal-liability angle) | Low-Medium | Currently referenced but not extended to management-body training obligations |
| **MiFID II / AIFMD / Solvency II outsourcing** | Low | Adjacent, more for the CIS Tech Advisory portfolio than for DR&J specifically |

---

## 6. Structural / algorithmic issues

- **§3.5** `ragForRegulation` — "green" when no answers were given.
- **§3.6** `postureScore` — per-question deduction cap missing.
- **`autoSelectRegs`** only adds, never removes when the customer deselects a sector. Small UX quirk.
- **`businessImpactBand`** uses only Q_B1. Narrow input to a high-level output; not a defect, just under-utilised evidence.
- **Findings deduplication** — `collectAllFindings` doesn't dedupe. Two questions both surfacing a GDPR Art. 30 finding produce two findings and two deductions. Sometimes appropriate, sometimes double-counting. Consider deduping by `{reg, article, title}` before deducting.

---

## 7. Consolidated must-fix list — ranked

Ranked by customer-impact risk (highest first):

| # | Item | Class | Effort |
|---|---|---|---|
| 1 | Q_D1 / Q_C2 / Q_F1 / Q_G2 — add DPF adequacy handling | Legal accuracy | 90 min |
| 2 | Q_C1 — split GCP into EU-only vs. includes-non-EU | Legal accuracy | 15 min |
| 3 | Add EU Data Act regulation block | Coverage | 60 min |
| 4 | Add UK Op Res + UK CTP regulation blocks | Coverage | 60 min |
| 5 | Q_H1 — add controls follow-up when "US-with-sovereign-boundary" picked | Legal accuracy | 30 min |
| 6 | Q_C1 — add Oracle / IBM / Salesforce / Snowflake / Databricks | Coverage | 20 min |
| 7 | Q_C2 — add rows for aitraining + government; add UK column | Coverage | 30 min |
| 8 | Add `sources:[{name,url}]` array to each regulation | Traceability | 60 min |
| 9 | Fix `ragForRegulation` to require answered questions, not just referenced | Algorithm | 20 min |
| 10 | Add framework version + last_reviewed date to `meta` + report cover | Traceability | 30 min |
| 11 | Q_G1 — split GPAI from Annex III high-risk AI | Legal accuracy | 30 min |
| 12 | Q_A2 — expand DORA entity list to include payment/EMI/CASP/CCP separately | Nuance | 30 min |
| 13 | Q_H2 — add "Basic" assurance level | Nuance | 5 min |
| 14 | Q_G1 — correct "health" wording to Annex III item 5(c) (life/health insurance) | Legal precision | 10 min |
| 15 | Q_J1 — cite DORA RTS 4h/72h/1-month | Nuance | 15 min |
| 16 | Add UK AI advisory regulation block | Coverage | 40 min |
| 17 | Q_B1 — replace DORA Art. 5 anchor on `financial` option | Legal precision | 10 min |
| 18 | `postureScore` — cap per-question deduction, or document weight rationale | Algorithm | 30 min |
| 19 | Add Contact Us + feedback overlay (same as Sovereign Screen) | UX | 5 min (existing script) |

---

## 8. Comparison to Sovereign Screen (post-roadmap state)

Same customer base, different tool. Where DR&J is behind:

| Dimension | Sovereign Screen (v1.3.0) | DR&J Audit (v1.0.0) |
|---|---|---|
| Regulations | 16 | 6 |
| Source URLs cited | 89 | 0 |
| DPF adequacy handling | ✓ | ✗ |
| Framework version + review date stamp | ✓ | ✗ |
| Customer-facing changelog | ✓ | ✗ |
| Grade labels renamed for reader clarity | ✓ | n/a (uses severity, not grade — labels are fine) |
| Feedback pill | ✓ | ✓ (P4.4 overlay applies to DR&J too) |
| Contact Us overlay | ✓ | ✓ (same overlay) |
| GCP EU-only option | ✓ (via Q_HYPER text listing) | ✗ (systemic false-positive) |
| GPAI question | ✓ (Q_GPAI + Art. 51+ rules) | ✗ |
| Micro / small / medium proportionality | ✓ (DORA Art. 16 + UK Op Res) | n/a (DR&J doesn't ask company size) |

DR&J is substantively earlier-stage than Sovereign Screen is today. Several of the same defects the Sovereign Screen roadmap fixed (DPF adequacy, controls follow-up, missing regimes, framework version stamp, source citations) are open here.

---

## 9. Recommendation

Same phased approach as Sovereign Screen. The infrastructure is already built and reusable — patch scripts with `json_safety_check` and `js_structure_check`, staging → sign-off → prod flow, legal-review log, refresh cadence.

Estimated shape:

**Phase 1 (legal defensibility — ships prod first)**
Items #1, #2, #5 from §7 + start of #3 (Data Act block). ~4–5 hours of work + legal sign-off. Fixes the customer-visible defective outputs.

**Phase 2 (screening completeness)**
Items #6, #7, #11, #12, #13, #14, #15. ~4 hours. Additive; no output changes.

**Phase 3 (regime coverage)**
Items #3 (Data Act), #4 (UK Op Res + UK CTP), #16 (UK AI). ~6 hours. Additive.

**Phase 4 (ongoing)**
Items #8 (sources), #10 (version stamp), #9 (rag fix), #18 (score cap), plus refresh cadence + changelog. ~4 hours + ongoing.

**Not urgent enough to hold Phase 1 for:** none.

If you approve, I'll build Phase 1 to staging using the same pattern we used for Sovereign Screen (patch script, staging-only deploy, sign-off request referencing SHA). Total time to Phase 1 in prod: ~1 working day including your sign-off.
