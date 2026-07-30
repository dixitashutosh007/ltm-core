# Sovereign Screen — Review v2 (post-patch)

**File reviewed:** `Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html`
**Live URL:** https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen.html
**KB `last_reviewed`:** 2026-07-30 (post-patch)
**Compares against:** `docs/SOVEREIGN-SCREEN-REVIEW.md` (v1, 15 must-fix items)

**Reviewer disclosure.** Content review by a technical reviewer, not a legal opinion. Any regulatory-references check below should be re-confirmed with your Legal / Compliance function before public release.

**Method (fresh extraction).** Full `__bundler/template` payload was JSON-decoded and the current `DEFAULT_KB` re-extracted. Fact-usage counted programmatically. Every regime's applicability rules and every new readiness question's `shown_if` predicate was checked against the fact graph.

---

## 0. Current shape of the KB

| Metric | v1 (30 Jul) | v2 (now) | Delta |
|---|---|---|---|
| Regimes | 9 | 9 | — |
| Questions | 27 | **35** | +8 (all readiness) |
| Facts declared | 20 | 20 | — |
| Facts actually used in applicability rules | 15 | 15 | — |
| Facts captured but unused (dead facts) | 5 | 5 | — |
| Readiness-tagged questions | 10 | **18** | +8 |
| Regimes with ≥1 readiness question | 3 of 9 | **9 of 9** | +6 |
| Regime `sources:[{name,url}]` arrays | 0 | **9 of 9** | +9 |

---

## 1. Fixes verified from v1 (delta since last review)

| v1 # | Fix | Verified now |
|---|---|---|
| 1 | Q_SCD wording no longer labels "detailed financial" as GDPR Art. 9 | ✅ Now reads *"special-category personal data as defined in GDPR Article 9 (biometric data used for identification, health, genetic, racial/ethnic, political, religious, trade-union, sex-life)"* |
| 2 | AI Act penalty text tiered per Art. 99 | ✅ Now reads *"€35m or 7% for prohibited practices; €15m or 3% for other non-compliance (including high-risk); €7.5m or 1% for supplying incorrect information"* |
| 3 | Q_AI insurance split into life/health vs. non-life | ✅ Two separate options now — life/health → high-risk, non-life → other |
| 9 | DORA CTP number "19 as of Nov 2025" removed | ✅ Now cites DORA Art. 31 + ESAs register (no undated point-in-time count) |
| 15 | Placeholder "reconcile with the LTM Digital Sovereignty deck" TODO leaking | ✅ Removed |
| — | Regime sources | ✅ **All 9 regimes** now carry a `sources:[{name,url}]` array with EUR-Lex / legislation.gov.uk / FCA / PRA / BoE / EBA / ENISA / Commission / EDPB / DOJ / ICO links |
| — | 6 regimes had zero readiness questions ("Not yet scored" was structural) | ✅ 8 new questions added, all 9 regimes now scorable; each shown_if mirrors the regime's own applicability |
| — | Bundler JSON-parse crash from earlier fix | ✅ Fixed and permanently guarded by `json_safety_check()` in patch script |

---

## 2. Items still open from v1 (not fixed yet)

| v1 # | Finding | Status |
|---|---|---|
| 4 | EU→US personal-data hosting always `needs_legal_review`, ignoring DPF adequacy | **OPEN** |
| 5 | Q_SOVOFFER `"Yes"` scores 100 without a controls follow-up | **OPEN** |
| 6 | Oracle Cloud (US-HQ) evades CLOUD Act detection | **OPEN** |
| 7 | UK-based `uses_high_risk_ai:true` gets zero AI regime call | **OPEN** |
| 8 | CASP entities get no MiCA call | **OPEN** |
| 10 | Data Act over-applied to customers | **OPEN** |
| 11 | Grade `needs_legal_review` ranks above `advisory` | **OPEN** |
| 12 | Five facts captured but never used in rules (`eu_member_state_count`, `special_category_data`, `data_volume_band`, `company_size`, `sovereign_offering_status`) | **OPEN** (fact usage counts unchanged) |
| 13 | Microenterprise DORA Art. 16 lighter regime not surfaced | **OPEN** |
| 14 | "Unknown" answers silently drop out on critical questions (Q_CTP) | **OPEN** |

**Six of the fifteen v1 items are fixed; nine remain open.** The remaining ones split into two clusters:

- **Cluster A — content edits** (v1 #4, #5, #7, #10, #14): pure text/rule edits inside `DEFAULT_KB`. Each is roughly the same size as the fixes already shipped.
- **Cluster B — new regimes / new logic** (v1 #6, #8, #11, #12, #13): each needs a small new regime block or wiring an existing fact into a new applicability rule.

---

## 3. New review — questions, answers, mappings, algorithm

### 3.1 Required questions — is everything there now?

**Fact coverage — unchanged from v1.** All 20 declared facts are still captured. The 5 dead facts flagged in v1 are still captured but unused. Not a regression.

**Question count — 35 total.** Broken down:

- **Screening questions (17):** Q_ROLE through Q_CONC — the fact-writers
- **Readiness questions — v1 set (7):** QR_GOV, QR_INC, QR_TEST, QR_TPR, QR_IBS, QR_SOV, QR_TRANSFER
- **Readiness questions — v2 additions (8):** QR_NIS2, QR_UKCTP, QR_EUDP_GOV, QR_EUDP_TRANSFER, QR_UKDP, QR_AI_DGOV, QR_AI_CTRL, QR_DATA_ACT
- **Tier-2 governance (3):** Q2_PRIORITY, Q2_CONTEXT, Q2_EXIT

**New required questions I'd add (not currently present):**

1. **DPF certification follow-up** — when the customer selects "US" as `data_hosting_location`, a follow-up: *"Is your US-based recipient certified under the EU-US Data Privacy Framework?"* (Yes → adequacy applies → `advisory`; No/Unknown → `needs_legal_review`).
2. **Sovereign-controls detail** — when `sovereign_offering_status:"yes"`, a multi-select follow-up: *"Which sovereignty controls are contractually in place?"* (EU-only ops personnel; customer-held keys / HYOK; contractual anti-disclosure clause; EU-only sub-processor list; local operating entity). Score `100` only if ≥ 3 selected; otherwise scale.
3. **GPAI question** — *"Do you use any general-purpose AI model (e.g., a large language model provider) in production?"* → triggers a distinct AI Act Art. 51+ obligation call for downstream users.
4. **Biometric-KYC question** — *"Do you use biometric identification / verification of natural persons (facial recognition, fingerprint, voice) in KYC or authentication?"* → Annex III item 1 high-risk.
5. **Employment-AI question** — *"Do you use AI in recruitment, promotion, work allocation or performance evaluation of staff?"* → Annex III item 4 high-risk.
6. **Microenterprise gate** — *"Are you a microenterprise (<10 staff AND ≤ €2m turnover / balance sheet)?"* — activates DORA Art. 16 simplified-regime note when true.
7. **Non-EU/UK sector regime probe** — when `data_subjects_geo` includes US or Other, prompt: *"Do you also need coverage of non-EU/UK regimes (e.g., US federal + state privacy laws, India DPDPA, PIPL, PDPA, APRA)? — This tool covers UK+EU only; contact us for a broader scope."*

### 3.2 Are answers mapped correctly?

**Corrected since v1:**

- ✅ Q_AI insurance split — non-life no longer over-scoped as Annex III
- ✅ Q_SCD Art. 9 categorisation is legally accurate

**Still incorrect / risky (unchanged from v1):**

- **Q_HYPER** still enumerates AWS/Azure/GCP only — Oracle/IBM Cloud/Salesforce all US-HQ but evade `uses_us_hyperscaler:true` unless the user also ticks "US-headquartered" in Q_CLOUDHQ.
- **Q_SOVOFFER "Yes"** still awards `score:100` on `jurisdiction_control` with zero evidence.
- **Q_CTP "unknown"** still silently produces no rule fire (should escalate to `needs_legal_review`).
- **Q_AI multi-select merge behaviour** — Verified: `mergeFacts` correctly OR-s booleans across selected options (so ticking both credit-scoring and life-insurance sets `uses_high_risk_ai:true` once). ✓ correct.

**New answer-mapping issue I noticed this pass:**

- **`sovereign_offering_status:"yes"`** conflates two very different scenarios. AWS European Sovereign Cloud (real sovereignty controls at platform level) and a customer running in eu-central-1 with a services-agreement clause are both awardable "Yes". A one-line follow-up would distinguish them. This is a variation of v1 #5 — flagged again because it directly affects the `jurisdiction_control` readiness dimension which is now weighted 0.6 in the `data_transfer_jurisdiction` regime.

### 3.3 Are all Acts / compliance mapped correctly?

**Regime accuracy re-verified after patches:**

| Regime | Legal reference in KB | Correct? |
|---|---|---|
| DORA | Regulation (EU) 2022/2554 | ✅ Correct. Q_FINTYPE list matches Art. 2(1). |
| NIS2 residual | Directive (EU) 2022/2555 | ✅ Correct. Lex specialis handling via DORA Art. 1(2) / NIS2 Art. 4. |
| UK Op Res | FCA PS21/3; PRA SS2/21 | ✅ Correct. |
| UK CTP | FSMA 2023; FCA PS24/16 / PRA PS16/24 | ✅ Correct. |
| EU GDPR | Regulation (EU) 2016/679 | ✅ Correct. |
| UK GDPR | UK GDPR; DPA 2018; PECR; DUAA 2025 | ✅ Correct. |
| Transfer & jurisdictional | GDPR Ch. V; US CLOUD Act; EU Data Act | ⚠ **DPF adequacy still not asked** (v1 #4). |
| EU AI Act | Regulation (EU) 2024/1689 | ✅ Correct. Penalty tiers now accurate per Art. 99. |
| EU Data Act | Regulation (EU) 2023/2854 | ⚠ **Still overbroad on customer side** (v1 #10). |

**Regimes still absent (per v1 §7 — unchanged):**

- **MiCA** (Regulation (EU) 2023/1114) — Q_FINTYPE lists CASP but no MiCA rule fires
- **PSD2 / (draft) PSD3+PSR** — payment institutions & EMIs in Q_FINTYPE
- **CRR/CRD + EBA cloud outsourcing guidelines** — banks
- **Solvency II outsourcing** — insurers
- **EU-US DPF / UK-US Data Bridge** — as a distinct adequacy check
- **UK AI regulatory approach** (ICO / FCA principles) — UK high-risk-AI users get zero output
- **EUCS** — cloud certification
- **eIDAS 2** (Regulation (EU) 2024/1183)

### 3.4 Legal validity of the output algorithm

I re-read the JS engine (`leaf` → `evalCond` → `computeFacts` → `assess` → `computeReadiness`) end-to-end. Design is unchanged from v1 and remains correct:

- **Two-pass fact computation** handles forward-referenced `shown_if` predicates.
- **`assess()`** picks the strongest fired rule per regime by precedence, then sorts regimes by grade.
- **`computeReadiness()`**:
  - Only scores regimes graded `applies` / `likely_confirm` / `partial` — semantically correct (don't tell someone how "ready" they are for a regime they're not in scope of).
  - Weights dimensions within regime, then regimes across the overall score.
  - Now that all 9 regimes have readiness questions, the "Not yet scored" fallback only fires when the customer genuinely skipped the readiness section — no longer structural.

**Legal-validity risks still present** (from v1, unchanged):

- **Grade precedence semantics** (v1 #11) — `needs_legal_review` (index 3) still outranks `advisory` (index 4). Report reader may interpret as "more severe" when it's actually a description of *action*, not severity. Not a legal defect per se, but a reader-comprehension risk on a legal-adjacent tool.
- **Regime weights** sum to 1.15 (declared) but the engine normalises by actually-used weight sum — mathematically correct, visually misleading if someone reads the KB.

**New legal-validity observation from this pass:**

- **QR_EUDP_TRANSFER wording** (new question I added) asks about *"Chapter V transfer-mechanism coverage (adequacy, SCCs, BCRs, TIAs)"* — which is factually accurate. But if the customer answers "5 — fully mature," the tool still doesn't check whether *the mechanism they're relying on for US transfers is DPF adequacy vs. SCCs* — so a false-positive on transfer maturity is possible for anyone claiming maturity but relying on a mechanism that a future Schrems ruling could invalidate. This isn't a defect I introduced — it's the same underlying gap as v1 #4. Fixing that gap fixes this too.

---

## 4. New issues surfaced by this pass (v2-only findings)

### 4.1 New readiness questions — completeness check

The 8 new questions cover every regime × dimension pair that was previously unscored. Predicates verified:

| Q | Fires for | Cross-check |
|---|---|---|
| QR_NIS2 | Financial entity AND EU establishment | Matches NIS2-residual applicability (which needs the same predicates for lex specialis to bite) — ✅ |
| QR_UKCTP | Financial entity AND UK establishment | Matches uk_ctp applicability path 2 — ✅. But path 1 (`entity_role:"ict_provider_to_finance"`) is NOT covered — an ICT provider that could be designated a CTP under UK rules does not see QR_UKCTP. **Minor gap — worth adding `or ict_provider_to_finance` to QR_UKCTP shown_if.** |
| QR_EUDP_GOV / QR_EUDP_TRANSFER | Processes PD AND (EU establishment OR offers-services-EU OR data_subjects_geo=EU) | Matches EU GDPR applicability exactly — ✅ |
| QR_UKDP | Processes PD AND (UK establishment OR offers-services-UK OR data_subjects_geo=UK) | Matches UK GDPR applicability exactly — ✅ |
| QR_AI_DGOV | (uses_high_risk_ai OR uses_other_ai) AND (EU establishment OR offers-services-EU) | Matches EU AI Act applicability — ✅ |
| QR_AI_CTRL | uses_high_risk_ai AND (EU establishment OR offers-services-EU) | Correctly scoped narrower — only high-risk users see this — ✅ |
| QR_DATA_ACT | entity_role = ict_provider_to_finance | Correctly provider-side only — ✅ |

**Small refinement:** QR_UKCTP should include the ICT-provider path as an alternative in its `shown_if`.

### 4.2 UK-side AI question path

QR_AI_DGOV and QR_AI_CTRL are correctly EU-scoped (they mirror EU AI Act applicability). But a UK-only firm using high-risk AI still has:
- No AI Act call (EU AI Act only fires with EU nexus)
- No AI readiness question shown
- Zero AI output on the report

This is the same as v1 #7 — the tool has no UK AI regime. Now with UK readiness questions in place for GDPR / CTP, the AI omission is more visible. Options:

- **Minimal:** add a UK AI advisory regime with 1 rule (`uses_high_risk_ai AND establishment_uk` → advisory pointing at ICO / FCA principles). Score readiness via a QR_UKAI question.
- **Fuller:** add a UK AI regime block modelled on the ICO's *"Guidance on AI and data protection"* + FCA CP24 / DP5 material.

### 4.3 Question ordering / user experience

35 questions is now on the high side for a "quick triage." Concrete: a large EU-and-UK bank using both high-risk and other AI, EU + UK data subjects, US hosting, and third-party cloud will see something like **28 questions** by the time all `shown_if` predicates fire. Two mitigations:

- Add an "Assessment progress" bar keyed on visible-question count (currently just section chips).
- Consider splitting readiness into a distinct section that shows only after screening is complete — currently the categories are mixed in a single section header ("Readiness").

Neither is a legal issue; both improve completion rate on the free tool.

### 4.4 Precedence label review — restatement of v1 #11

I re-read the report render (`viewReport`). It sorts fired regimes by the grade precedence. A regime graded `needs_legal_review` therefore appears **above** a regime graded `advisory` in the visible report. Users reasonably read top-of-list as *"most important"*. The label `needs_legal_review` sounds legally scarier than `advisory`. The tool means "confirm with counsel"; the user reads "you have a legal problem."

Cheapest fix: rename `needs_legal_review` → `confirm_with_counsel` and `advisory` → `informational` (or `heads_up`). Semantics preserved, reader interpretation aligned to intent. Better fix: split severity axis (definite / likely / partial / informational) from action axis (confirm / no action).

---

## 5. Consolidated must-fix (v2 = v1 remaining + new)

Ranked by risk of a customer reading a legally-wrong or misleading conclusion:

| # | Item | Origin | Priority |
|---|---|---|---|
| 1 | EU→US personal-data hosting always `needs_legal_review`, ignoring DPF adequacy | v1 #4 | **High** — changes the answer |
| 2 | Q_SOVOFFER `"Yes"` → readiness 100 without controls follow-up | v1 #5 | **High** — false-pass on flagship dimension |
| 3 | Oracle / IBM Cloud / other US-HQ providers evade `uses_us_hyperscaler` detection | v1 #6 | **High** — customer under-flagged |
| 4 | UK high-risk AI users see zero AI regime | v1 #7 | **High** — silent gap |
| 5 | CASP entities → no MiCA call | v1 #8 | **High** — Q_FINTYPE offers CASP explicitly |
| 6 | Data Act overbroad on customer side | v1 #10 | Medium |
| 7 | Grade `needs_legal_review` reads as "more severe" than `advisory` | v1 #11 | Medium |
| 8 | 5 dead facts still declared but unused | v1 #12 | Medium — either wire in or drop |
| 9 | Microenterprise DORA Art. 16 not surfaced | v1 #13 | Medium |
| 10 | "Unknown" on Q_CTP silently drops out | v1 #14 | Medium |
| 11 | QR_UKCTP shown_if omits `ict_provider_to_finance` path | new v2 | Low — small predicate widen |
| 12 | Missing regimes: EUCS, MiCA, PSD2/3, CRR/CRD, Solvency II, eIDAS 2, UK AI, DPF/UK-US Data Bridge | v1 §7 (unchanged) | High for MiCA/DPF/UK-AI; Medium for the rest |
| 13 | Missing screening questions: DPF cert, sovereign-controls detail, GPAI, biometric KYC, employment AI, microenterprise gate | new v2 | High for DPF/sovereign-controls/GPAI; Medium for the rest |

---

## 6. Positives — what's now genuinely good

- **Every regime call is now source-cited** — the `sources:[{name,url}]` array on all 9 regimes points to EUR-Lex / legislation.gov.uk / the actual supervisor. A customer can click through to primary authority for any conclusion.
- **All 9 regimes are scorable** — the "Not yet scored" fallback is now behavioural (user skipped), not structural (regime lacked questions).
- **Legal-accuracy defects surfaced in v1 are cleanly resolved** — Q_SCD, AI Act penalties, insurance AI classification, DORA CTP count.
- **Bundler patch pipeline is now self-guarding** — `json_safety_check()` prevents the class of failure that crashed the home screen last iteration.
- **Rules engine remains clean** — composable `all`/`any`/`not`, two-pass fact computation, weighted dimension → regime → overall roll-up. No changes needed.
- **Disclaimer + sources footer** — the meta disclaimer now points customers to the Sources & Methodology section for authoritative references; this is the model wording for the other three accelerators to adopt.

---

## 7. Suggested next action

The top-5 must-fix items in §5 are all bundle-safe string edits, all covered by the existing `json_safety_check()` guard, and together would move the tool from *"basically right, some legal gaps"* to *"legally defensible for public release"*:

1. Add DPF-certification follow-up question + widen the transfer-jurisdiction rule.
2. Add Q_SOVOFFER controls follow-up.
3. Widen Q_HYPER (or replace the enumeration with an HQ-jurisdiction question).
4. Add UK AI advisory regime + QR_UKAI readiness question.
5. Add MiCA regime block + rule for `fin_entity_type:"casp_crypto"`.

Estimated size: same as the v2 patches (8 questions, adds ~5 KB to the file). I can implement all five in one atomic patch if you give the go-ahead.
