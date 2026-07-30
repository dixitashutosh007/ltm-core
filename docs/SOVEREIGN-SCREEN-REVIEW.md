# Sovereign Screen — Deep Review

**File reviewed:** `Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html`
**Vertical / phase (per tool):** Financial services · UK & EU · Phase 1
**Schema version (per tool):** `0.1.0`
**Framework last-reviewed date (per tool):** 2026-07-21
**Live URL:** https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen.html

**Method.** Full knowledge base (`meta`, `facts`, `regimes`, `sections`, `questions`) and the JS rules engine (`leaf`, `evalCond`, `computeFacts`, `assess`, `computeReadiness`) were extracted from the bundle. Rule references for every declared fact were counted programmatically. Every regime's `applicability_rules` was checked against the actual regulation text I have knowledge of.

**Reviewer disclosure.** This is a content review by a technical reviewer, not a legal opinion. Any regulatory-references check below should be re-confirmed with your Legal / Compliance function before public release.

---

## 1. What's there — the overall design

**Facts collected (20):** `entity_role`, `fin_entity_type`, `establishment_eu`, `establishment_uk`, `eu_member_state_count`, `offers_services_eu`, `offers_services_uk`, `processes_personal_data`, `data_subjects_geo`, `special_category_data`, `data_volume_band`, `data_hosting_location`, `cloud_provider_hq`, `uses_us_hyperscaler`, `sovereign_offering_status`, `company_size`, `uses_high_risk_ai`, `uses_other_ai`, `is_or_uses_designated_ctp`, `ict_concentration_risk`.

**Regimes covered (9):**

| # | Regime | Legal reference | Weight |
|---|---|---|---|
| 1 | DORA | Regulation (EU) 2022/2554 | 0.30 |
| 2 | NIS2 (residual) | Directive (EU) 2022/2555 | 0.05 |
| 3 | UK Operational Resilience | FCA PS21/3; PRA SS2/21 | 0.20 |
| 4 | UK Critical Third Parties | FSMA 2023; FCA PS24/16 / PRA PS16/24 | 0.05 |
| 5 | EU GDPR | Regulation (EU) 2016/679 | 0.15 |
| 6 | UK GDPR / DPA 2018 / PECR / DUAA 2025 | UK GDPR; DPA 2018 | 0.10 |
| 7 | Transfer & jurisdictional exposure | GDPR Ch. V; US CLOUD Act; EU Data Act | 0.15 |
| 8 | EU AI Act | Regulation (EU) 2024/1689 | 0.10 |
| 9 | EU Data Act | Regulation (EU) 2023/2854 | 0.05 |

**Sections (9):** Organisation → Footprint → Data → Hosting & cloud → Scale → Technology → Third parties → Readiness → Governance.

**Engine.**
- Facts computed by iterating questions and merging `fact_value` per selected option (2 passes to allow forward-referenced `shown_if`).
- Regime rules evaluated as `all` / `any` / `not` composites over `leaf(fact, op, value)` predicates.
- Grade precedence: `applies > likely_confirm > partial > needs_legal_review > advisory > not_applicable`.
- Readiness: 1-5 ratings normalised to 0-100, then weighted by dimension within regime, then by regime weight for overall.

**On design merit — this is well-built.** The rules engine is composable, the fact-value model with two-pass computation is correct, and the DORA/NIS2 lex specialis handling is legally aware. The findings below are content and coverage issues, not engine defects.

---

## 2. Required questions — coverage gaps

### 2a. Questions asked but never used ("dead facts")

Programmatic check: five declared facts are captured from the user but referenced by **zero** applicability rules. They currently do nothing.

| Fact | Question that writes it | Rule refs |
|---|---|---|
| `eu_member_state_count` | Q_MSTATES | **0** |
| `special_category_data` | Q_SCD | **0** |
| `data_volume_band` | Q_VOL | **0** |
| `company_size` | Q_SIZE | **0** |
| `sovereign_offering_status` | Q_SOVOFFER (used for readiness score only) | **0** applicability |

**Impact:** the user answers these questions expecting them to matter — they don't affect any regime call. Two of them (`special_category_data`, `company_size`) *should* matter:

- **`special_category_data`** should sharpen the EU GDPR grade (Art. 9 conditions), trigger a DPIA advisory (Art. 35), and often trigger a DPO requirement (Art. 37(1)(c)).
- **`company_size`** should surface **DORA microenterprise simplified regime** (Art. 16) and **UK Op Res proportionality**. Under DORA a microenterprise's ICT risk framework can be significantly lighter — a large-bank readout is wrong for them.
- **`data_volume_band`** and **`eu_member_state_count`** are triage-only signals that could be dropped, or used to modulate DPO/lead-authority language.

**Recommendation:** either wire these into rules, or drop the questions to save the user time.

### 2b. Regimes / obligations that aren't screened at all

For a **financial-services** sovereignty screen (UK & EU), the following are conspicuously absent:

| Missing regime | Why it matters here |
|---|---|
| **EU Cybersecurity Certification Scheme for Cloud Services (EUCS)** | The scheme's "High" assurance level bakes in sovereignty-adjacent controls. A "sovereign cloud" screen without EUCS is missing the actual certification story. |
| **MiCA — Regulation (EU) 2023/1114** | Q_FINTYPE lists CASP explicitly. If the user picks CASP, they get DORA + GDPR + AI Act calls but **no MiCA call**. That's the primary MiCA use case. |
| **PSD2 / (draft) PSD3 + PSR** | Payment institutions and EMIs (both in Q_FINTYPE) have PSD2 outsourcing and incident obligations that intersect with cloud choice. |
| **CRR / CRD (banking) outsourcing framework + EBA/EIOPA guidelines on ICT & security risk** | Cloud outsourcing rules for banks and insurers pre-date DORA and continue alongside it. |
| **Solvency II (insurance) outsourcing rules** | Same as above for insurers. |
| **EU-US Data Privacy Framework (DPF, July 2023) + UK-US Data Bridge (Oct 2023)** | The tool treats EU→US personal-data hosting as `needs_legal_review`. That is right for a non-DPF-certified recipient — but if the recipient is DPF-certified, an adequacy decision applies. Not asking is the difference between "you're compliant" and "you have a Schrems-III risk." |
| **eIDAS 2 — Regulation (EU) 2024/1183** | EU Digital Identity Wallet framework. Highly relevant to financial-services digital identity and onboarding. |
| **UK-side AI regulation** | The UK has a **principles-based, regulator-led** AI approach (ICO, FCA guidance, etc.) — not an EU-AI-Act analogue. A user with `establishment_uk:true` and `uses_high_risk_ai:true` gets **no** AI regime call today. |
| **US federal / state regimes for `Q_DSGEO includes US`** | If a user selects US data subjects, no US regime fires (GLBA, state privacy laws like CCPA/CPRA, HIPAA where relevant). Tool should either add a light US layer or explicitly note "US not covered — L2 engagement." |

### 2c. Missing questions inside existing regimes

- **DORA CTP-side question.** Q_CTP asks *"Are you or do you depend on"* a CTP jointly. Split into two — the obligations bind the provider, the *dependency* concentration is a customer-side item.
- **DORA subsector modulation.** No question for "significant institution" status (which changes TLPT scope under Art. 26).
- **UK Op Res.** No question about *whether* important business services have been identified (only QR_IBS — a readiness rating, not a fact input).
- **Sovereign controls follow-up.** Q_SOVOFFER `"Yes"` scores 100 with no evidence question. Should be followed by a multi-select: EU-only operations personnel, customer-held keys (HYOK), contractual protection against extraterritorial disclosure, EU-only subprocessor list, local operating entity.
- **CLOUD Act specifics.** The tool references CLOUD Act but not FISA §702 / EO 12333 / EO 14086 — the fuller US extraterritorial picture that underlies DPF adequacy.
- **AI Act — GPAI question.** No question for use of general-purpose AI models (Art. 51+) — a distinct obligation regime from Annex III high-risk.
- **AI Act — biometric KYC.** Not asked. Annex III item 1 covers biometric identification. FS uses biometric KYC pervasively.
- **AI Act — employment.** Annex III item 4 (recruitment / performance management AI) is common in FS HR and would trigger high-risk obligations. Not asked.

---

## 3. Answers mapped correctly?

### 3a. Q_AI classification is over- and under-scoped

Q_AI option "Insurance risk assessment or pricing" writes `uses_high_risk_ai:true`.

**AI Act Annex III item 5(c)** (Regulation (EU) 2024/1689) reads:
> AI systems intended to be used for **risk assessment and pricing in relation to natural persons in the case of life and health insurance**.

So **motor, property, marine, commercial-lines** insurance risk/pricing is **not** Annex III item 5(c). The tool flags it as high-risk regardless. Non-life insurers running the tool will get a false-positive high-risk AI Act obligation call.

**Fix:** split into "Life or health insurance risk/pricing" (→ high-risk) vs. "Non-life insurance risk/pricing" (→ other AI). Or ask a follow-up.

### 3b. "Detailed financial" data mis-classified as special-category

Q_SCD: *"Do you process special-category or highly sensitive data (**biometric, health, detailed financial**)?"* → writes `special_category_data`.

GDPR **Art. 9(1) special categories** are: racial or ethnic origin; political opinions; religious or philosophical beliefs; trade-union membership; genetic data; biometric data (for uniquely identifying a natural person); data concerning health; data concerning a natural person's sex life or sexual orientation.

**Financial data is NOT an Art. 9 special category.** It's ordinary personal data. It may be more *commercially* sensitive and can attract sector-specific rules (banking secrecy, PCI DSS), but conflating it with Art. 9 is a legal mis-classification.

**Fix:** remove "detailed financial" from the Q_SCD prompt. If the intent is to capture financial-data sensitivity, do it as a separate question with a separate fact (`sensitive_financial_data`) that could then drive a PCI DSS or banking-secrecy note.

### 3c. Q_HYPER under-detects US hyperscaler exposure

Q_HYPER text: *"Do you rely on a US-headquartered hyperscaler (AWS, Microsoft Azure, Google Cloud) for material workloads?"*

Oracle Cloud (US-headquartered) is not in the list. If a customer runs on Oracle Cloud and answers *No* to this, they set `uses_us_hyperscaler = false`, which suppresses the CLOUD Act / jurisdictional-exposure rule (`data_transfer_jurisdiction` regime, first applicability rule requires `uses_us_hyperscaler:true` OR `cloud_provider_hq includes US`).

Q_CLOUDHQ *does* ask for provider HQ and can catch this — but only if the user is diligent about ticking "US-headquartered" for Oracle. Many won't.

**Fix:** either expand the AWS/Azure/GCP list (add Oracle, IBM Cloud, Salesforce/Heroku), or make Q_HYPER a boolean over provider HQ jurisdiction rather than an enumerated brand list.

### 3d. `sovereign_offering_status:"yes"` → readiness 100 with no evidence

Q_SOVOFFER: *"Are those workloads on a sovereign / EU-boundary offering with contractual and operational controls against foreign access?"* → *"Yes — sovereign offering with controls"* scores 100 for the `jurisdiction_control` readiness dimension.

**Problem:** no follow-up asks *which* controls. A customer who is on AWS European Sovereign Cloud (real thing, real controls) and a customer who has just relabelled a Frankfurt region as "our sovereign cloud" both score 100.

**Fix:** conditional follow-up multi-select on `sovereign_offering_status:"yes"`:
- EU-only operations personnel
- Customer-held encryption keys (HYOK)
- Contractual protection against extraterritorial disclosure requests
- Sub-processor list limited to EU-jurisdiction entities
- Local operating entity with local jurisdiction of dispute resolution

Score 100 only if ≥ 3 of 5 selected; otherwise scale (100 × selected/5).

### 3e. "Unknown" answers silently drop out

For Q_CTP, `is_or_uses_designated_ctp:"unknown"` doesn't trigger the CTP rule (rule requires `eq:"yes"`). "Unknown" is neither `yes` nor `no` and produces no output — a customer who genuinely doesn't know their CTP dependency gets a silently clean regime call.

**Fix:** an `unknown` answer on a critical question should raise a `needs_legal_review` grade with the rationale *"CTP dependency not established — treat as an open finding."*

---

## 4. Legal validity — regime-by-regime check

### DORA (Regulation (EU) 2022/2554) — ✅ substantially correct

- Applicability rule: financial entity ∈ 16 categories × EU establishment or offers-services ∈ EU → `applies`. Matches Art. 2(1). ✓
- Q_FINTYPE list matches DORA Art. 2(1) categories well.
- **Missing DORA categories:** administrators of critical benchmarks; securitisation repositories; trade repositories; data reporting service providers; account information service providers (AISPs, though PSD2-registered). Ancillary insurance intermediaries are excluded — worth noting.
- **Incident-reporting timelines:** tool says *"Major-incident reporting within tight timelines (~4h after classification)"*. Under the RTS on incident reporting (Commission Delegated Regulation on incident classification / reporting), the initial notification is 4 hours after classification as major, intermediate within 72 hours, final within one month. Tool wording is directionally correct but only quotes the initial. **Consider adding the 72h / 1-month cadence.**
- **CTP designation claim:** *"19 designated as of Nov 2025, incl. AWS, Azure, Google Cloud, IBM, Bloomberg."* The ESAs' designation process began in 2024 with implementing acts on criteria. Point-in-time counts age fast — **the "19" number should be dated with a "as of <date>" caveat, or dropped** and replaced with "several major cloud, network and market-data providers designated to date."
- **Microenterprise regime (Art. 16) not surfaced** — see §2a.

### NIS2 (Directive (EU) 2022/2555) — residual handling — ✅

- Tool uses lex specialis carve-out per DORA Art. 1(2) / NIS2 Art. 4. ✓
- Only assigns `partial` grade — appropriate. ✓
- Residual obligations text ("Corporate cyber hygiene, cross-sector cooperation, member-state registration") is a fair summary. ✓
- **Missing:** NIS2 governance requirements (Art. 20) — management-body accountability including trainings and personal-liability exposure — apply to financial entities as they are not fully covered by DORA. Worth noting.

### UK Operational Resilience (FCA PS21/3; PRA SS2/21) — ✅

- Fires on `financial_entity AND establishment_uk`. Correct.
- Obligations correctly reference important business services, impact tolerances, mapping/testing, self-assessment, outsourcing/third-party. ✓
- **Missing:** the Bank of England / PRA SS1/21 on operational resilience (companion to SS2/21). And FG16/5 on outsourcing continues to apply for many firms.
- **March 2025 deadline** (firms must be able to remain within tolerances for severe-but-plausible scenarios) — worth calling out as *"post-deadline: regulators now expecting evidence."*

### UK Critical Third Parties (FSMA 2023; FCA PS24/16 / PRA PS16/24) — ✅

- Correct reference to FSMA 2023 CTP powers and the joint FCA/PRA/BoE oversight regime. ✓
- Six Fundamental Rules reference is correct. ✓
- **Wording nit:** tool says *"HM Treasury designates"* — designation power sits with HM Treasury on recommendation of the regulators; text is fine but could be sharpened.

### EU GDPR (Regulation (EU) 2016/679) — ✅ but see 4a below

- Art. 3 extraterritoriality: correctly encoded (establishment OR offers services OR data subjects in EU). ✓
- Chapter V transfer restrictions cited. ✓
- Art. 9 special categories cited. ✓
- **Issue in Q_SCD** — see §3b (financial data is not Art. 9).

### UK GDPR / DPA 2018 / PECR / DUAA 2025 — ✅

- Reference to Data (Use and Access) Act 2025 (DUAA) with phased amendments is up to date. ✓
- Correct extraterritoriality mirror of GDPR Art. 3. ✓

### Transfer & jurisdictional exposure — ⚠ over-flags US transfers

Rule 2: `processes_personal_data AND data_subjects_geo includes EU AND data_hosting_location includes US or Other` → `needs_legal_review`, rationale *"EU personal data hosted outside the EEA in a non-adequate jurisdiction needs a valid Chapter V transfer mechanism (adequacy / SCCs + TIA). Note: UK hosting is covered by EU–UK adequacy…"*

**The US IS adequate for DPF-certified recipients** since the July 10, 2023 EU-US Data Privacy Framework adequacy decision. A customer using a DPF-certified US processor should not automatically be flagged as needing legal review — they *may* be relying on adequacy validly.

**Fix:** ask a follow-up when US hosting is selected: *"Is your US-based recipient certified under the EU-US Data Privacy Framework?"* — Yes → advisory (Schrems-III risk exists but adequacy currently applies), No / unknown → needs_legal_review.

**Same logic for UK-to-US** via the UK-US Data Bridge (October 2023).

### EU AI Act (Regulation (EU) 2024/1689) — ⚠ over-scopes and mis-quotes penalties

- **"Insurance risk assessment or pricing" is over-scoped** — see §3a. Annex III item 5(c) is life/health only.
- **Penalty quote:** tool says *"Penalties reach 7% of global turnover."* Art. 99 tiers:
  - Up to **€35m or 7% of global turnover** — for **prohibited practices** (Art. 5).
  - Up to **€15m or 3%** — for non-compliance with most other obligations (including high-risk).
  - Up to **€7.5m or 1%** — for supplying incorrect/incomplete/misleading information.
  So "7%" is the ceiling for prohibited-practices violations, not for high-risk system violations. **Fix the penalty text.**
- **Timeline missing:** high-risk-system obligations under Chapter III start applying from **2 August 2026** (Art. 113(c)). Prohibitions from **2 February 2025**. Worth surfacing since the timeline is what makes advisory action time-sensitive.
- **GPAI missing:** no path in the tool for a customer that uses general-purpose AI models (Art. 51+ obligations for GPAI providers, transparency for downstream users). Financial services commonly deploy off-the-shelf GPAI — this should be asked.

### EU Data Act (Regulation (EU) 2023/2854) — ⚠ over-applied

- Applicability rule fires for essentially *anyone with EU nexus and any cloud provider*. This is too broad.
- Data Act Chapter VIII (cloud switching / interoperability) obligations bind **providers of data processing services** offered in the EU. **Customers** benefit from these rights but generally aren't the ones with obligations (except in narrow B2B data-sharing settings). The tool grades this as `likely_confirm` for a customer, which may be misread as *"you have Data Act obligations."*
- **Effective dates missing:** main applicability from **12 September 2025**; some cloud-switching provisions phased in later.
- **Fix:** split the rule into "customer-side rights" (advisory) vs. "provider-side obligations" (likely_confirm — fires only if `entity_role:"ict_provider_to_finance"`).

---

## 5. Score / output logic

**Grade precedence:** `applies > likely_confirm > partial > needs_legal_review > advisory > not_applicable`.

**Concern:** `needs_legal_review` (index 3) outranks `advisory` (index 4). That's semantically odd for a UI — the current sort puts a `needs_legal_review` regime **above** an `advisory` regime in the report, which reads to a customer as *"legal-review issues are more severe than advisory findings"* even though the label `needs_legal_review` is descriptive of *what to do next*, not severity. A customer may reasonably interpret it as the tool telling them they're closer to a violation.

**Recommendation:** either

- rename the labels so severity is unambiguous (`applies`, `likely_applies`, `partial_applies`, `depends_confirm_with_counsel`, `advisory_only`, `not_applicable`), **or**
- separate a **severity axis** (definite / likely / partial / not applicable) from an **action axis** (confirm with counsel / advisory only / no action).

**Regime weights sum to 1.15**, not 1.0. The `computeReadiness` implementation normalises by the actually-used weight sum (`oacc / owsum`), so the overall score isn't mathematically wrong — but it's visually confusing and makes the "these weights represent proportion of overall" reading incorrect. **Normalise the declared weights so they sum to 1.0.**

**Micro-issue:** the maturity spine `note` field is honest about placeholders — *"Middle three labels are placeholders — reconcile with the LTM Digital Sovereignty deck."* This is a developer TODO leaking into the KB. Reconcile or remove.

---

## 6. Legal-validity summary — must-fix before public release

Ranked by risk of a customer reading a legally-wrong conclusion:

| # | Finding | Where | Fix |
|---|---|---|---|
| 1 | "Detailed financial" mis-labelled as GDPR Art. 9 special category | Q_SCD | Drop the phrase; if needed, add a separate `sensitive_financial_data` fact |
| 2 | AI Act "7% penalty" text applies only to prohibited practices | `eu_ai_act.obligations` | Rewrite with tiered penalties |
| 3 | Insurance AI over-scoped as Annex III (should be life/health only) | Q_AI option "Insurance risk/pricing" | Split into life/health vs. non-life |
| 4 | EU→US personal-data hosting always `needs_legal_review`, ignoring DPF adequacy | `data_transfer_jurisdiction` rule 2 | Add DPF-certification follow-up |
| 5 | Q_SOVOFFER `"Yes"` → readiness 100 without evidence | Q_SOVOFFER | Add controls follow-up |
| 6 | Oracle Cloud (US-HQ) evades CLOUD Act detection unless Q_CLOUDHQ ticked | Q_HYPER wording | Expand list or make provider-HQ-driven |
| 7 | UK-based `uses_high_risk_ai:true` gets zero AI regime call | AI Act only covers EU | Add a UK principles-based advisory |
| 8 | CASP entities get no MiCA call | Missing regime | Add MiCA regime |
| 9 | DORA CTP number "19 as of Nov 2025" is undated in-tool | DORA CTP rule rationale | Add "as of <date>" or drop the count |
| 10 | Data Act over-applied to customers | `eu_data_act` rule | Split customer vs. provider obligations |
| 11 | Grade `needs_legal_review` ranks above `advisory` — reads as more severe | precedence + labels | Rename labels or separate severity from action |
| 12 | Five facts captured but never used (`eu_member_state_count`, `special_category_data`, `data_volume_band`, `company_size`, `sovereign_offering_status`) | Rules engine | Either wire into rules or drop the questions |
| 13 | Microenterprise DORA-lite regime (Art. 16) not surfaced | Needs `company_size` wired | Add rule: `company_size:"micro"` → DORA note re Art. 16 |
| 14 | "Unknown" answers silently drop out on critical questions | Q_CTP; potentially others | Treat unknown as `needs_legal_review` |
| 15 | Placeholder text in maturity spine (`"reconcile with the LTM Digital Sovereignty deck"`) leaks into KB | `meta.maturity_spine.note` | Remove or replace |

---

## 7. Coverage-gap summary — regimes missing

| Missing | Priority |
|---|---|
| EU-US DPF / UK-US Data Bridge check for transfer rule | **High** — changes the answer, not just the rationale |
| MiCA for CASP entities | **High** — Q_FINTYPE includes CASP explicitly |
| EUCS (cloud certification) | **Medium** — central to "sovereign cloud" story |
| PSD2 / PSD3 for payment institutions & EMIs | **Medium** |
| CRR/CRD + EBA guidelines on ICT outsourcing (banks) | **Medium** |
| Solvency II outsourcing (insurers) | **Medium** |
| UK AI regulatory approach (ICO/FCA principles) | **Medium** |
| eIDAS 2 (EU Digital Identity Wallet) | Low-Medium |
| US / state regimes when `data_subjects_geo` includes US | Low — either add a light layer or explicitly scope out |

---

## 8. Positives worth keeping

- The **rules engine** (`leaf` / `evalCond` / `computeFacts` / two-pass evaluation) is clean and correct.
- **DORA Art. 2 entity list** in Q_FINTYPE is comprehensive and accurate.
- **NIS2 residual** handling using lex specialis is a rare and correct move.
- **CLOUD Act framing** ("residency ≠ sovereignty") is the right message and clearly stated.
- **Disclaimer** already carries "*Not legal advice. Applicability depends on specific facts and should be confirmed with qualified counsel.*" — well-drafted.
- **Readiness computation** correctly normalises 1-5 ratings to 0-100 and only counts regimes that are `applies/likely_confirm/partial`.
- **Grade precedence** design (pick strongest fired rule per regime, then sort regimes by grade) is well-architected — even though the specific ordering of `needs_legal_review` vs. `advisory` needs revisiting (§5).

---

## 9. Suggested sequence

1. **Immediate content fixes (no engine change):** items #1, #2, #9, #15 above. Pure text edits inside `KB.meta` and `KB.regimes[*].obligations`.
2. **Answer-mapping fixes:** items #3, #5, #6. Add options and follow-up questions.
3. **New rules for existing facts:** items #12, #13, #14. Requires editing `applicability_rules` blocks.
4. **New regime blocks:** items #7, #8 and Coverage-gap regimes. Each is a new object in `KB.regimes[]` with the same shape as existing ones.
5. **Precedence/label review:** item #11 — small refactor with UX + legal review.
6. **Legal sign-off** on the final KB before it goes public.

Given the file is a **bundled single-page HTML** and JSX source is out of scope (per your instruction), all of the above are string edits inside the embedded `const DEFAULT_KB = {...}` block. That block is at offset ~7.35 MB in the file but is straight JavaScript object literal — safe to edit with targeted replacements.
