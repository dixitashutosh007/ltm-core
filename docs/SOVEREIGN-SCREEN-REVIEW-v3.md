# Sovereign Screen — Review v3 (post-roadmap)

**File reviewed:** `Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html`
**Live URL:** https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen.html
**Framework version:** v1.3.0 (as displayed on the report cover)
**Compares against:** v1 review (`SOVEREIGN-SCREEN-REVIEW.md`) — 15 must-fix items; v2 review (`SOVEREIGN-SCREEN-REVIEW-v2.md`) — 13 items ranked

**Reviewer disclosure.** Content review by a technical reviewer, not a legal opinion. Every claim about a specific regulation is a pointer to the primary source, not an interpretation for a specific customer.

**Method (fresh extraction).** Full `__bundler/template` payload was JSON-decoded and the current `DEFAULT_KB` re-extracted. Fact-usage counted programmatically. Every regime's applicability rules and every readiness question's `shown_if` predicate was re-checked. Grade-label rendering path traced from `assess()` output through `viewReport()`.

---

## 0. State of the KB

| Metric | v1 (30 Jul, before roadmap) | v3 (now, roadmap complete) | Δ |
|---|---|---|---|
| Regimes | 9 | **16** | +7 |
| Applicability rules (total) | ~14 | **36** | +22 |
| Questions | 27 | **47** | +20 |
| Facts declared | 20 | 22 | +2 |
| Facts actually used in rules | 15 | **22** | +7 (all now used) |
| **Dead facts** | **5** | **0** | ✓ |
| Regimes with `sources:[]` | 0 | **16 of 16** | ✓ |
| Total source URLs cited | 0 | **89** | — |
| Regimes with ≥ 1 readiness question | 3 of 9 | **16 of 16** | ✓ |

---

## 1. v1 + v2 findings — final disposition

Cross-referenced against the ranked v2 must-fix list (13 items):

| # | v2 finding | Status now |
|---|---|---|
| 1 | EU→US always `needs_legal_review`, ignoring DPF adequacy | ✅ **Fixed** (Phase 1) — Q_DPFCERT + rule split |
| 2 | Q_SOVOFFER "Yes" → readiness 100 without evidence | ✅ **Fixed** (Phase 1) — score 100 → 70 + QR_SOVCTRL averaged |
| 3 | Oracle / IBM Cloud evade CLOUD Act detection | ⚠ **Partially fixed** — Q_HYPER text now names them, but it remains a boolean; a user answering "No" thinking of AWS but running on Oracle still under-detects. See §3.1 below. |
| 4 | UK high-risk AI users get zero AI regime | ✅ **Fixed** (Phase 1) — `uk_ai_advisory` regime + QR_UKAI |
| 5 | CASP → no MiCA call | ✅ **Fixed** (Phase 1) — `eu_mica` regime + QR_MICA |
| 6 | Data Act overbroad on customer side | ⚠ **Partially fixed** — the Data Act rule now says "confirm customer vs provider obligations" but the grade is still `likely_confirm` regardless. Could split. Low priority. |
| 7 | Grade `needs_legal_review` reads as "more severe" than `advisory` | ✅ **Fixed** (Phase 1) — labels renamed to "Confirm with counsel" / "Informational". Verified: report render (`kb.meta.grades[rr.grade]`) uses the renamed labels. |
| 8 | 5 dead facts | ✅ **Fixed** (Phase 2) — all 22 facts now used (0 dead) |
| 9 | Microenterprise DORA Art. 16 not surfaced | ✅ **Fixed** (Phase 2) — DORA Art. 16 rule wired to `company_size:micro` |
| 10 | "Unknown" on Q_CTP silently drops out | ✅ **Fixed** (Phase 1) — two new DORA CTP rules on unknown → `confirm_with_counsel` |
| 11 | QR_UKCTP `shown_if` omits ICT-provider path | ✅ **Fixed** (Phase 1) — predicate widened |
| 12 | Missing regimes: EUCS, MiCA, PSD2/3, CRR/CRD, Solvency II, eIDAS 2, UK AI, DPF/UK-US Data Bridge | ✅ **All added** — MiCA + UK AI in Phase 1; DPF check in Phase 1; EUCS, PSD2/3, CRR/CRD, Solvency II, eIDAS 2 in Phase 3. |
| 13 | Missing screening Qs: DPF cert, sovereign-controls detail, GPAI, biometric KYC, employment AI, microenterprise gate | ✅ **All added** — Q_DPFCERT + QR_SOVCTRL (Phase 1); Q_BIOMETRIC + Q_EMPAI + Q_GPAI (Phase 2); microenterprise handled via existing Q_SIZE now wired. |

**14 of 15 v1 items closed. 13 of 13 v2 items closed (2 partial, 11 full).**

---

## 2. What's genuinely good now

- **Every regime call points to a primary source.** 89 URLs across 16 regimes, all EUR-Lex / legislation.gov.uk or the standing supervisor (FCA, PRA, BoE, EBA, EIOPA, ENISA, EDPB, European Commission, DOJ, ICO). Zero blog / analyst / LLM-summary citations.
- **Zero dead facts.** Every fact captured from the user affects at least one applicability rule.
- **All 16 regimes are scorable** — no more "Not yet scored" fallback for structural reasons; readiness now spans the whole KB.
- **DPF adequacy is handled explicitly.** The tool now distinguishes DPF-certified US recipients (informational) from SCC/BCR reliance (confirm with counsel), matching the current legal state.
- **Grade labels convey action, not severity.** "Confirm with counsel" and "Informational" now read correctly; verified via the render code path.
- **Framework version stamp** on every report + a customer-facing changelog page. Any customer question can be traced back to a specific framework build.
- **Guarded patch pipeline.** `json_safety_check()` + `js_structure_check()` in the patch scripts caught 2 real bugs during development (a `\'` escape crash and a truncated-array replacement). Both guards remain in place.
- **Ownership + cadence documented.** `docs/REFRESH-CADENCE.md` names you as owner with a 1 Feb / 1 May / 1 Aug / 1 Nov schedule and explicit out-of-cycle triggers.
- **Live monthly source-URL health check** (`.github/workflows/source-url-health.yml`).
- **Rollback runbook** for the one scenario nobody wants to be figuring out in the moment.

---

## 3. Residual technical issues

### 3.1 Q_HYPER is still a boolean

The text now names Oracle Cloud / IBM Cloud / Salesforce / Snowflake / Databricks alongside AWS/Azure/GCP, which closes the *description* gap. But a customer running on Oracle who reads the question and mentally maps "hyperscaler" to only the Big-3 can still answer "No" and evade `uses_us_hyperscaler=true`.

**Fix (bundle patch, ~30 min):** convert Q_HYPER to a `multi_select` listing each provider explicitly (with fact_value `uses_us_hyperscaler:true` on any US-HQ pick). Keeps the same downstream logic; removes the interpretation gap.

### 3.2 Q_GPAI `shown_if` too narrow

Q_GPAI is currently `shown_if:{any:[uses_high_risk_ai OR uses_other_ai]}`. But a customer using only GPAI (e.g., a small firm using an LLM chatbot for customer service) may answer:
- Q_AI = "None of these"
- Q_BIOMETRIC = "No"
- Q_EMPAI = "No"

… and Q_GPAI never appears. The GPAI provisions (AI Act Arts. 51–56) can attach without any Annex III use.

**Fix:** drop the `shown_if` from Q_GPAI (or widen to always show if EU nexus). Adds one question to some customers who currently see none — worth the coverage.

### 3.3 UK→US transfer still unnamed

Q_DPFCERT captures DPF status including the UK-US Data Bridge as a follow-up. But the transfer/jurisdictional regime's rules only fire on `data_subjects_geo includes EU`. If a UK-only firm hosts data in the US, no rule captures the UK-US Data Bridge angle.

**Fix:** add two mirror rules to the transfer/jurisdictional regime for `data_subjects_geo includes UK` + US hosting + DPF cert status. Low volume of affected customers but non-zero.

### 3.4 Q_SIZE micro definition is ambiguously worded

The option reads "Micro (<10 staff, ≤ €2m)". The exact EU definition (Commission Rec. 2003/361/EC): staff headcount < 10 **AND** (annual turnover ≤ €2m **OR** balance-sheet total ≤ €2m). "≤ €2m" as written could be either turnover or balance sheet, but the "or" isn't obvious to a casual reader.

**Fix:** re-word to "Micro (< 10 staff AND turnover ≤ €2m OR balance sheet ≤ €2m)". The DORA Art. 16 *rationale* is already correct; only the question label needs the clarification.

### 3.5 Regime weights sum to 1.70

Individual weights per regime range from 0.05 to 0.30, summing to **1.70** — not 1.0. The engine normalises by `owsum` so the overall readiness score is still correct. But if the KB is read as documentation (e.g., "why does DORA get 30% of the score?"), the weights don't tell that story.

**Fix (cosmetic):** rescale so weights sum to 1.0. Zero functional impact. Only worth doing if the weights ever get surfaced to customers or reviewers.

### 3.6 Data Act rule doesn't split provider vs customer

The `eu_data_act` regime fires `likely_confirm` for any EU nexus + any cloud provider. The rationale text says "confirm customer vs provider obligations" — honest, but the grade doesn't reflect that most customers of cloud have downstream rights, not upstream obligations.

**Fix:** split into two rules — provider (`ict_provider_to_finance`) → `likely_confirm`; customer (financial entity using cloud) → `informational` with rationale focused on switching-rights and non-personal-data-access safeguards benefiting the customer.

---

## 4. Residual coverage gaps

Ordered by likely customer impact for a UK/EU FS audience:

| Missing | Whom it would affect | Priority for the vertical |
|---|---|---|
| **MiFID II / MiFIR** | Investment firms (in Q_FINTYPE), and any FS firm running trading / order-execution AI | Medium — DORA already covers ops-resilience; MiFID II covers conduct/trading-venue rules |
| **AIFMD** | AIFMs (in Q_FINTYPE) | Medium — DORA covers ICT, but AIFMD conduct/governance are separate |
| **UCITS Directive** | UCITS management companies (in Q_FINTYPE) | Medium |
| **IORP II Directive** | Pension funds (in Q_FINTYPE) | Medium |
| **EMIR** | CCPs / trading venues / any firm doing derivatives clearing | Medium |
| **CSDR** | CSDs (in Q_FINTYPE) | Low-Medium |
| **CRR3** (Regulation (EU) 2024/1623) | Banks — recent CRR amendment | Low — CRR block already cites 575/2013 which CRR3 amends; a note added to obligations would suffice |
| **DORA subcontracting RTS** (Comm. Del. Reg. 2025/532) | DORA-in-scope firms outsourcing to CTPPs | Low — obligations text could add a line |
| **DORA incident reporting RTS** (Comm. Del. Reg. 2025/301) | All DORA-in-scope firms | Low — already captured directionally as "~4h/72h/1 month" |
| **UK FCA Consumer Duty** | All UK FS firms serving retail | Low-Medium — supervisory expectation, not a sovereignty topic |
| **CRD6** | Banks — companion to CRR3 | Low |
| **Solvency II 2020 Review Directive** | Insurers | Low |

None are legal-defensibility defects; they're coverage extensions for a broader tool. The tool's declared scope is UK & EU **sovereignty**, and it does that well for the entity types it captures. Broader FS-regulatory coverage is arguably an "L2 tool" scope.

---

## 5. Residual legal-validity concerns

Small, non-blocking. Ranked by risk of misleading a customer:

### 5.1 Wording drift on time-sensitive facts

Several rationales reference dates that will age:

- **AI Act commencement dates** (Art. 113): "Chapter III applies from 2 August 2026", "GPAI provisions from 2 August 2025". These are correct today but should be flipped to past tense as they pass, otherwise the tool reads as "will apply" when it already does.
- **DUAA 2025 commencement**: text says "Track phased DUAA 2025 changes." Vague on purpose — but once the phased dates land in commencement orders, be specific.
- **eIDAS 2**: text says "by end-2026". Update as the Member State roll-outs land.

**Handling:** these are exactly the items the quarterly refresh (Phase 4) is designed to catch. Add explicit checklist items in `docs/REFRESH-CADENCE.md`.

### 5.2 "Consult the ESAs register" is a directive without a link

The DORA CTP rationale says "consult the ESAs register for the current list" but doesn't hyperlink. The `sources:[]` array on DORA does include the ESAs' policy hub. Consider extending the rationale text with the exact register URL when the ESAs publish it.

### 5.3 The GPAI "provider" rule may over-scope

The GPAI "provider" rule fires on `gpai_role:"provider" AND EU nexus` → `applies`. But not every organisation that trains a model is a *GPAI* provider under AI Act Art. 3(63) — GPAI requires "general-purpose" characteristics (broad range of distinct tasks). A firm training a domain-specific model isn't a GPAI provider.

**Fix:** add a hint in Q_GPAI clarifying the AI Act's GPAI definition; or split "provider" into "narrow / domain model" vs "general-purpose foundation model".

### 5.4 UK Op Res proportionality rule doesn't distinguish "small" from "simple"

The rule fires on `company_size in [micro, small]` and points at proportionality. UK Op Res proportionality is more nuanced — the FCA also looks at business-model *complexity*, not just headcount. Firm-size-only is directionally correct but incomplete.

**Fix:** minor rationale tweak clarifying that supervisors also look at complexity, not just size band.

### 5.5 Contact-Us mailto captures a personal email

The Contact Us modal collects Name / Company / Role / Email / Phone / Priority and dumps them into a `mailto:` body. That's personal data being drafted client-side into an email the user then sends themselves. Not a GDPR event for LTM per se (the transmission is user-initiated), but:

- The privacy note we surface says "Nothing is transmitted to LTM unless you use Contact Us." Accurate.
- We should be explicit that once the user clicks Send in their mail app, LTM becomes the controller of that data and processes it under the CIS Tech Advisory privacy notice.

**Fix:** add one line above the modal footer: *"By sending, you're providing your details to LTM CIS Tech Advisory for follow-up. See our privacy notice."* Link to the LTM privacy notice.

---

## 6. New v3 findings (previously unlisted)

- **Q_SIZE ambiguous wording** (§3.4) — small
- **Q_HYPER still boolean** despite widened text (§3.1) — medium
- **Q_GPAI predicate too narrow** for GPAI-only customers (§3.2) — medium
- **UK→US transfer angle not modelled** (§3.3) — medium
- **GPAI provider rule doesn't check the AI Act's "general-purpose" threshold** (§5.3) — small-medium
- **Contact Us modal privacy line** could be sharper about controller transition (§5.5) — small
- **Regime weights don't sum to 1.0** (§3.5) — cosmetic

---

## 7. Consolidated fix list — post-roadmap

Nothing here is a live legal defect. All are quality / coverage improvements. Ranked by impact for a UK/EU FS customer:

| # | Fix | Effort | Class |
|---|---|---|---|
| 1 | Q_HYPER boolean → multi_select over specific providers | 30 min | Answer-mapping robustness |
| 2 | Q_GPAI: drop `shown_if` (or broaden to "any EU nexus") | 10 min | Coverage |
| 3 | UK→US transfer rules mirror EU rules on `data_subjects_geo includes UK` | 30 min | Coverage |
| 4 | Q_SIZE micro option: reword to remove AND/OR ambiguity | 5 min | Wording |
| 5 | Data Act rule: split provider vs. customer | 20 min | Signal quality |
| 6 | Add MiFID II regime block | 60 min | New regime |
| 7 | Add AIFMD / UCITS / IORP II regime blocks | 3 × 40 min | New regimes |
| 8 | Add CRR3 note to existing CRR/CRD block | 15 min | Currency |
| 9 | Add DORA subcontracting RTS note to DORA obligations | 15 min | Currency |
| 10 | Rescale regime weights to sum to 1.0 | 15 min | Cosmetic |
| 11 | Contact Us modal: add "By sending…" privacy line | 10 min | UX / privacy hygiene |
| 12 | AI Act rationales: switch tense as commencement dates pass | Quarterly | Refresh-driven |
| 13 | GPAI "provider" rule: refine per AI Act Art. 3(63) | 20 min | Legal precision |
| 14 | ESAs register: hyperlink DORA CTP rationale to the live register when ESAs publish one | Small | Currency |

Everything above is bundle-safe (`DEFAULT_KB` edits) and covered by `json_safety_check()` + `js_structure_check()`.

---

## 8. Recommendation

**Ship no changes yet.** The tool is in materially good shape for a live UK/EU FS audience. Every v1/v2 legal-defensibility defect is closed; every regime is source-cited; every fact is used; every regime is scorable.

Recommend:
- **Next 30 days:** watch feedback (via the new pill) and analytics-gated telemetry (once DPO cleared). Real user data will re-rank the fix list.
- **1 August 2026 quarterly refresh:** work through items #1, #2, #3, #4, #10, #11 from §7 — the cheap ones that reduce residual customer confusion. Total effort ≈ 2 hours.
- **Q4 2026:** consider MiFID II / AIFMD / UCITS / IORP II if customer profile justifies (§7 items 6–7).

**No legal defect is currently live in production that warrants an out-of-cycle patch.** All 5 outstanding v2 must-fix items and all P4.5 analytics work are on scheduled or gated paths.
