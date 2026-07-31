# FinOps Maturity Screen — v1 Review

**File reviewed:** `FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html`
**Framework version (per KB `meta.schema_version`):** 1.0.0
**KB `meta.last_reviewed`:** 2026-07-22
**Live URL:** https://ltm-core.s3.us-east-1.amazonaws.com/finops-screen.html
**Staging URL:** https://ltm-core.s3.us-east-1.amazonaws.com/finops-screen-staging.html

**Reviewer disclosure.** Technical + framework-integrity review. This is not a legal opinion; the trademark note below is a flag for counsel, not a determination.

**Method.** `DEFAULT_KB` extracted from the `__bundler/template` payload (JSON-quoted, same pattern as FVC and Sovereign Screen). Full `questions[]`, `meta.stages[]`, `meta.domains[]` walked. Scoring engine read end-to-end: `qScore`, `stageQuestions`, `stageScore`, `stageCriticals`, `stageStatus`, `maturity`, `overallScore`, `domainScores`, `buildRoadmap`, `viewReport`.

---

## 0. What the tool is

A staged **FinOps maturity screen** — walks the customer through 44 questions across 5 stages (Chaos → Informed → Optimised → Automated → Transparent), scores each, applies both a weighted threshold and a critical-question gate per stage, and returns the highest **contiguous** stage passed. Output is a report PDF with a maturity gauge, per-stage table, capability-by-domain bars, a narrative, and a 3-horizon prioritised remediation plan.

**Inventory:**

| Metric | Value |
|---|---|
| Stages | 5 (Chaos, Informed, Optimised, Automated, Transparent) |
| Domains | 5 (governance, visibility, optimization, automation, culture) |
| Questions | 44 (Chaos 8, Informed 9, Optimised 10, Automated 9, Transparent 8) |
| Critical questions | 17 (must meet stage `crit_min` for the stage to pass) |
| Answer formats | 6 (single_select ×26, boolean ×6, range ×6, rating_1_5 ×4, multi_select ×1, drag_order ×1) |
| Scoring | Weighted mean per stage; overall = weighted mean across all questions |
| Roadmap | 3 horizons — short (critical this stage / next), mid (next stage), long (further) |
| Disclaimer | Present — "Indicative maturity screen … prioritise action, not certify compliance or guarantee savings" |
| Framework version on cover | **No** (present in Method paragraph at bottom of report only) |
| Reviewed-date on cover | **No** (present in Method paragraph) |
| Sources / attributions | **No** — framework derivation not cited |
| FinOps Foundation TM disclaimer | **No** |
| Placeholder assets | None (this tool ships no PDFs — clean) |
| Contact Us / feedback overlay | Present (P4.4 v3 overlay applied) |

---

## 1. What's good

The engine and framework are well-constructed and materially better than the surface review suggested:

- **Contiguous-stage progression is correct.** `maturity()` walks stages 1→N and stops at the first non-pass, so a customer cannot show "Stage 4 automated" while failing Stage 2 informed. That's the right semantics for a maturity model.
- **Critical-question gate is real.** `stageStatus` requires both `score >= threshold` AND every critical question `>= crit_min`. A high average cannot compensate for a missing foundational control. The `meta.gating_note` prose reflects this and renders in the Method section — customers can see why they didn't pass.
- **Every question carries a `remediation` string.** These are concrete, not generic — "block or auto-tag non-compliant resources at creation" (A1), "put rightsizing into the sprint cadence with tracked completion" (O2). The report's 3-horizon plan is built directly from these strings ordered by `(critical, weight, gapSize)` — a solid ranking.
- **`drag_order` (O10) is scored via ideal-distance.** Not "not scored, just informational" — the qScore branch computes normalised bubble-distance from `ideal` order, capped to 0–100. Non-trivial and correct.
- **Domain rollup is honest.** `domainScores()` computes weighted means per domain; unanswered domains render "—" instead of 0. Same discipline as Sovereign Screen's RAG-not-answered fix.
- **Range questions with `invert:true`** (O3 orphaned storage, A4 forecast variance, T6 waste %) score correctly — the lower the raw value, the higher the score. Verified: T6 at raw 5% → normalised score ≈ 83.
- **Weighted overall is defensible.** `overallScore` is a single weighted mean across the entire 44-question bank, independent of stage gating — gives a companion figure to the stage headline.
- **Stage narrative parametrises the count of critical blockers.** *"There are N critical controls outstanding — until these are in place, spend data cannot be trusted enough to act on."* Not generic; changes with the customer's answers.
- **Boolean scoring is binary 0/100.** No "sort of yes" fudge. Matches customer intuition.
- **Existing disclaimer is honest.** *"Indicative maturity screen based on self-reported inputs. Scores reflect the responses given and are intended to prioritise action, not to certify compliance or guarantee savings."*
- **Sensible defaults on every threshold:** Chaos 60 / Informed 65 / Optimised 70 / Automated 75 / Transparent 80 — progressive, not flat, reflecting that later stages should demand more.

---

## 2. Legal / labelling defects (HIGH priority)

### 2.1 No FinOps Foundation trademark disclaimer

The tool is titled **"FinOps Maturity Assessment"** (`meta.framework:"FinOps Maturity Assessment"`) and mirrors the FinOps Framework's Crawl / Walk / Run progression via its Chaos → Informed → Optimised → Automated → Transparent stages. "FinOps" is a trademark of the FinOps Foundation. There is no attribution note or non-affiliation disclaimer anywhere in the report.

**Impact:** Using the FinOps mark in a branded assessment tool without a non-affiliation notice is a legitimate trademark risk. It's the kind of thing that gets flagged the first time the FinOps Foundation runs a routine marketplace sweep.

**Fix:** append to `meta.disclaimer` (or the Method section):

> *"Aligned to FinOps Framework references. Not an official FinOps Foundation assessment or certification. 'FinOps' is a trademark of the FinOps Foundation."*

This is the same wording pattern the ACCELERATOR-REVIEW.md flagged three weeks ago; it has not landed.

### 2.2 C1 is a security question, not a FinOps question

`C1` is a Chaos-stage, `critical:true`, `weight:2` question asking *"Is MFA enforced on root / master accounts, with access control policies applied across all accounts?"*

Consequences:

- A customer with MFA gaps who passes every other Chaos question can be told they failed Stage 1 on the strength of a security-posture answer. Because Chaos gates every subsequent stage (contiguous progression), they show **maturity = below Stage 1** irrespective of the rest of their FinOps practice.
- The `remediation` string ("Enforce MFA on all root and privileged accounts and apply baseline access-control policy org-wide") is a real security recommendation issued by an LTM-branded tool. A customer could reasonably infer they've received a security finding from LTM.

**Fix (choose one):**

- **A** — Reframe as *"Does an account-ownership and access-control model exist that supports cost governance? (e.g., named account owners, principle of least privilege on billing consoles.)"* — keeps the intent (foundational account hygiene) without asserting a security posture.
- **B** — Keep C1 as-is but relabel the stage-1 section explicitly *"Foundational IT controls (not a security audit — see your CISO for that)."*

Recommend A: it makes C1 a real FinOps question that still gates Stage 1.

### 2.3 Framework version + reviewed date not on the cover

`schema_version:"1.0.0"` and `last_reviewed:"2026-07-22"` exist and the reviewed date renders in the report's Method paragraph. But the cover meta block shows only `PREPARED <date>` — the framework version doesn't appear anywhere on the report cover.

DR&J v1.3.0 and Sovereign Screen v1.3.0 both stamp `Framework v1.x.y · reviewed <date>` on the cover. FMS is the only tool where you have to scroll to page 3 to see which version of the framework you're looking at.

**Fix:** add a mono-type line to the covermeta block: `Framework v1.0.0 · reviewed 2026-07-22`. Same shape as the FVC Phase 1 cover stamp we just shipped.

### 2.4 C4 remediation over-scopes the customer's RBAC

`C4` remediation: *"Grant finance read-only billing access so cost conversations start from shared data."*

The customer completing the assessment may not own AWS Organizations / Azure AD role assignment — that's often a separate central platform team. The remediation reads as an instruction the respondent can execute.

**Fix:** *"Work with your cloud platform team to grant finance read-only billing / cost console access."* Small change; same intent.

---

## 3. Framework / scoring defects (MEDIUM priority)

### 3.1 Domain labels overlap — "Governance & accountability" vs "Culture & accountability"

`meta.domains[]`:

- `governance` → "Governance & accountability"
- `culture` → "Culture & accountability"

Both labels end "& accountability". The data model is clean (each question has one `domain`), but a reader looking at two domain bars labelled "…& accountability" cannot easily tell them apart. The report renders both bars in the "Capability by domain" section side-by-side.

**Fix:** rename `culture` label to "Culture & engineering behaviour" (or "Culture & practice"). The `governance` label carries the accountability weight; culture should carry the behavioural weight.

### 3.2 O10 `ideal` order is not a defensible answer key

O10 asks the customer to rank 5 cost levers by delivered value in *their* environment. But `qScore` bubble-distance-scores it against a fixed `ideal:[commitment, rightsizing, waste, storage, architecture]` — i.e., we tell every customer their environment should have delivered value in that specific order, and we deduct maturity marks against the ideal.

There is no basis for a fixed universal ordering — a data-platform-heavy customer legitimately gets more from storage lifecycle than commitment discounts, and their ranking will differ. Either:

- **A** — Make O10 unscored (informational only, drives the roadmap emphasis but not the maturity number). The `remediation` string is already couched informationally ("Revisit under-exploited levers…"), so this is consistent.
- **B** — Score only against the *top* 2 items (customer's top-2 lever match against the ideal top-2), not the full order.

Recommend A: prevents dinging a customer for having an unusual estate.

### 3.3 `boolean` DK is absent

FVC and DR&J both offer `boolean_dk` for questions where "don't know" is a legitimate answer. FMS `boolean` questions (C3, C4, I6, O7, A7, T4) return only true/false, so a respondent who genuinely doesn't know is forced to guess. Guessed "no" scores 0 and can push a critical below `crit_min`. Guessed "yes" scores 100 and can inflate a stage.

**Fix:** add `boolean_dk` scoring (yes=100, no=0, dk=null → excluded from the mean but flagged in a blind-spots list on the report, same pattern as FVC).

### 3.4 `multi_select` (C8) with no `exclusive:true` for "none"

`C8` asks *"Which foundational cost artefacts exist today?"* with 4 options (consolidated billing / account inventory / cost baseline / contract owner) each worth 25. There is no "None of these" exclusive option — a respondent who has none must simply not select any, which the UI reads as "not answered" (multi_select empty → qScore returns 0, but the stage engine only excludes when `a===undefined`; an empty selection would need to be explicitly recorded).

**Fix:** add `{label:"None of these",score:0,exclusive:true}` to C8. Mirrors the FVC V5 / C1 pattern.

### 3.5 Stage-1 (Chaos) `crit_min:70` requires C2 to score ≥70 to pass

`C2` (billing export) is critical with 3 non-zero options: 100 / 55 / 20 / 0. Only the top option (100) clears `crit_min:70`. So a customer with "exported, but partial or manual" scores 55, fails the crit, and is stuck below Stage 1 — regardless of everything else.

That's arguably intentional (billing export is a hard prerequisite for FinOps), but the option's plain text sounds like partial credit and the customer will be surprised when partial-credit fails outright. Either:

- **A** — Adjust the middle option's score to 75 (still below "fully automated" but clears the crit).
- **B** — Reword the option to make the pass/fail more explicit: *"Exported, but partial or manual (does not yet cover all providers / accounts)"*.

Recommend B: keeps scoring integrity, better explains the fail to the customer.

### 3.6 No overall confidence indicator based on answered count

FVC computes `confidence()` from `blindSpots().length` and `answered<12` → Low / Moderate / Reasonable label on the report. FMS doesn't. A report generated with 12 answered out of 44 questions renders exactly the same confidence framing as one with all 44 answered. The `answered` count is displayed as *"Questions answered N/44"* but there's no label calibrating how much weight to put on the maturity call.

**Nice-to-have:** import the FVC confidence pattern.

---

## 4. Content / polish items (LOW priority)

- **Sources / framework attribution** — the framework is derived from FinOps Foundation and general industry practice. No `sources:[]` array cites this. Should be added for §2.1 attribution and for auditability, mirroring DR&J P4.1.
- **Currency-agnostic tool** — no money-in / money-out. No currency stamp needed. This is fine.
- **Range question suffixes** are consistent ("%"). Good.
- **`rating_1_5` labels** — every rating question has distinct labels (I8, O8, T5, T7); no placeholder labels like "1 / 2 / 3". Good.
- **Feedback pill + Contact Us right-rail + standard disclaimer overlay** already applied (v3 overlay); no change needed.
- **`export CSV`** on the question bank tab — verified path present.
- **`import JSON`** — the KB replacement is checked for `meta` + `questions[]` presence but not deeper — a malformed import can render an unusable tool. That's a Bank-page (admin) risk, not customer-facing. Fine.

---

## 5. Proposed remediation plan (phased, staging → sign-off → prod)

Same workflow as the other three accelerators.

### Phase 1 — Legal defensibility (3 items)

1. **FinOps Foundation TM disclaimer** appended to `meta.disclaimer`. (§2.1)
2. **C1 reframed** as an account-ownership / access-model FinOps question, dropping the MFA / security framing. (§2.2)
3. **Framework version + reviewed date on cover** — mono-type line in covermeta block. (§2.3)

### Phase 2 — Scoring / content correctness (5 items)

4. **C4 remediation softened** ("work with your cloud platform team…"). (§2.4)
5. **Domain label rename** — culture → "Culture & engineering behaviour". (§3.1)
6. **O10 unscored** — drag_order for prioritisation, not maturity. (§3.2)
7. **`boolean_dk`** added to C3, C4, I6, O7, A7, T4 (+ blind-spots list on the report). (§3.3)
8. **C8 "None of these" exclusive option.** (§3.4)

### Phase 3 — Additive hygiene (3 items)

9. **C2 middle option reworded** for pass-fail clarity. (§3.5)
10. **`sources:[]`** attributing FinOps Foundation Framework + industry references. (§4 / §2.1)
11. **Confidence indicator** on the report driven by `answered / 44`. (§3.6)

### Phase 4 — Ongoing

12. **Customer-facing changelog** page (`finops-maturity-changelog.html`), mirroring DR&J and Sovereign Screen.
13. **Add FMS to `REFRESH-CADENCE.md`** with the same 1 Feb / 1 May / 1 Aug / 1 Nov cadence. Triggers: new FinOps Framework release, new FinOps Foundation State of FinOps report.

---

## 6. Not-legal-advice risk assessment

**Medium — trademark, not legal-advice.** The tool doesn't opine on regulation, so GDPR / DORA / AI Act interpretations don't feature. The material risk is (a) the FinOps Foundation trademark used without a non-affiliation notice, and (b) the security-question-in-a-FinOps-tool framing that could position an MFA gap as an LTM-issued security finding.

Post-Phase 1, both drop to **Low**.

---

## 7. Comparison to the other three accelerators (post-Phase 4 elsewhere)

| Feature | Sovereign Screen v1.3.0 | DR&J v1.3.0 | FVC v1.0.0 (P1 patched) | **FMS v1.0.0** |
|---|---|---|---|---|
| Framework version on cover | ✅ | ✅ | ✅ (P1) | ❌ |
| Reviewed-date on cover | ✅ | ✅ | ✅ (P1) | ❌ (present in Method only) |
| Sources / URLs | ✅ | ✅ | ❌ | ❌ |
| Standard disclaimer overlay | ✅ | ✅ | ✅ | ✅ |
| Contact Us right-rail tab | ✅ | ✅ | ✅ | ✅ |
| Feedback pill (mailto) | ✅ | ✅ | ✅ | ✅ |
| "Don't know" scored explicitly | ✅ | ✅ | ✅ | ❌ (boolean is binary) |
| Customer-facing changelog | ✅ | ✅ | ❌ | ❌ |
| Quarterly refresh entry | ✅ | ✅ | ❌ | ❌ |
| Placeholder assets | none | none | 4 (P3 blocks) | none |
| Domain / signal labels distinct | ✅ | n/a | ✅ | ❌ ("& accountability" ×2) |
| Trademark disclaimer where relevant | n/a | n/a | n/a | ❌ (FinOps mark) |

---

## Appendix A — Stage / question map

| Stage | Threshold | Crit min | Questions | Criticals |
|---|---|---|---|---|
| 1 · Chaos | 60 | 70 | 8 (C1–C8) | C1, C2, C4, C5 (4) |
| 2 · Informed | 65 | 70 | 9 (I1–I9) | I1, I2, I8 (3) |
| 3 · Optimised | 70 | 75 | 10 (O1–O10) | O1, O2, O5 (3) |
| 4 · Automated | 75 | 75 | 9 (A1–A9) | A1, A4, A6 (3) |
| 5 · Transparent | 80 | 80 | 8 (T1–T8) | T1, T2, T3, T6 (4) |

**Domain distribution across 44 Qs:** governance 8, visibility 12, optimization 10, automation 5, culture 9.

---

## Appendix B — Files touched by this review

- Read: `FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html`
- Read: `docs/ACCELERATOR-REVIEW.md` (prior surface review, §2)
- Read: `docs/DR-J-REVIEW.md`, `docs/FVC-REVIEW.md` (structural parity)
- Written: `docs/FMS-REVIEW.md` (this file)
- **No** patch scripts written yet — remediation phases in §5 will be scripted after user approval, same workflow as Sovereign Screen / DR&J / FVC.
