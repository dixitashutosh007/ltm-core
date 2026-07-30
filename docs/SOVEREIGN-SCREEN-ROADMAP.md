# Sovereign Screen — Phased fix & improvement plan

**Context.** The tool is now live at https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen.html and being promoted to UK/EU customers. Any output a customer sees is now a public LTM claim. Every change from here needs a defensible reason and a rollback path — not a "we'll fix it if someone notices."

**Guiding principles for this roadmap:**
1. **No customer gets a legally-wrong output.** Legal-defensibility fixes ship before completeness fixes.
2. **Each phase is independently deployable and rollback-able** via `git revert` + `python scripts/deploy-s3.py`.
3. **Legal sign-off is a gate**, not a courtesy — every phase has an explicit review point before it hits production S3.
4. **Additive changes over replace-changes** wherever possible, so a bad regime addition doesn't break correct existing ones.
5. **We measure what we ship** — analytics and feedback are part of the plan, not an afterthought.

**Approvals model.** I don't ship any of this without your go-ahead per phase. Each phase below has an explicit "Go / No-go" gate you need to confirm.

---

## Phase 0 — Guardrails (before any content change)

**Why first.** The tool is live. If Phase 1 introduces a defect we can't roll back cleanly, customer sessions will see a broken assessment. Fix the safety net before touching the content.

**Deliverables:**

1. **Staging S3 key** — deploy every candidate change to `s3://ltm-core/sovereign-screen-staging.html` first (add to `deploy.config.json`). Prod key `sovereign-screen.html` only receives promoted, signed-off builds.
2. **Version stamp on the report cover** — display `Framework v<n>.<n> · reviewed YYYY-MM-DD` prominently. Customers and internal reviewers need to be able to say "which version generated this report."
3. **Rollback runbook** — a 5-line `docs/ROLLBACK.md` covering the two commands: `git revert <sha>` + `python scripts/deploy-s3.py`. The S3 key doesn't have versioning enabled today — verify or enable.
4. **Legal-owner assignment** — a named person on the LTM Legal side who signs off content before each phase promotes to prod. Cadence: async review, 48-hr SLA.

**Duration:** 1–2 days.
**Risk:** low. All infrastructure work.
**Go/no-go gate:** legal owner named + staging URL live.

---

## Phase 1 — Legal defensibility (the five that change customer output)

**Why now.** These are the items from the v2 review where the tool today produces a **wrong or misleading legal conclusion**. Every hour they stay in prod is a hour of customer sessions with defective output.

**Scope — the five (all bundle-safe `DEFAULT_KB` edits):**

| # | Fix | Wrong output today |
|---|---|---|
| 1 | Add DPF-certification follow-up when Q_HOSTLOC includes US; split the transfer/jurisdictional rule accordingly | EU→US flows currently *always* graded `needs_legal_review` even when DPF adequacy applies |
| 2 | Add controls follow-up on Q_SOVOFFER=Yes; only score readiness 100 if ≥3 of 5 controls selected | Any customer self-declaring "yes" gets max readiness on the flagship jurisdiction_control dimension |
| 3 | Widen Q_HYPER (or replace with an HQ-jurisdiction question) so Oracle / IBM Cloud / Salesforce trigger `uses_us_hyperscaler` | US-HQ providers outside the Big-3 evade CLOUD Act detection |
| 4 | Add UK AI advisory regime (ICO / FCA principles-based) + a UK AI-readiness question | UK high-risk-AI users currently get zero AI regime output |
| 5 | Add MiCA regime block; rule fires on `fin_entity_type:"casp_crypto"` | Q_FINTYPE offers CASP explicitly but no MiCA is called out |

**Also in this phase — reader-clarity fixes:**

6. Rename `needs_legal_review` → `confirm_with_counsel` and `advisory` → `informational`; keep precedence order but relabel so top-of-report doesn't read as "most severe" when it means "confirm."
7. Q_CTP `"unknown"` → treat as `confirm_with_counsel` on the DORA CTP rule rather than silently drop out.
8. Widen QR_UKCTP `shown_if` to include the `ict_provider_to_finance` path.

**Deliverables:**
- One atomic patch (`scripts/patch-sovereign-screen-phase1.py`) with the 8 items above and `json_safety_check()` in place.
- Regression test: capture the report output for 5 representative customer profiles (UK bank; EU bank; EU insurer using non-life AI pricing; ICT provider designated CTP; CASP crypto) before and after the patch; diff — verify no regressions in the 4 fixed regime calls, and verify the 5 target defects flip to correct behaviour.
- Updated regime source citations for MiCA + UK AI advisory.

**Duration:** 2–3 days (patch + tests + legal review + promote).
**Risk:** medium — changes customer-visible output. Rollback path: revert commit + re-sync.
**Go/no-go gate:** Legal sign-off on the 8 changed rationales + the 5 profile diffs.

---

## Phase 2 — Screening completeness (additive; no output changes)

**Why after Phase 1.** These add coverage without changing anything the tool already outputs correctly. They can be reviewed and shipped in smaller batches.

**Scope:**

| Item | What it adds | Regime it feeds |
|---|---|---|
| GPAI question | *"Do you use a general-purpose AI model in production?"* | New rule on EU AI Act (Art. 51+ downstream-user obligations) |
| Biometric KYC question | *"Do you use biometric identification / verification of natural persons in KYC or authentication?"* | Sets `uses_high_risk_ai:true` (Annex III item 1) |
| Employment AI question | *"Do you use AI in recruitment, work allocation, performance evaluation?"* | Sets `uses_high_risk_ai:true` (Annex III item 4) |
| Microenterprise gate | New Q using `company_size:"micro"` + supplementary EU-establishment context | Activates DORA Art. 16 simplified-regime advisory |
| Wire `special_category_data` fact | Rule on EU GDPR: special category → DPIA / DPO advisories (Art. 35 / 37(1)(c)) | EU GDPR |
| Wire `company_size` fact | Rule on DORA Art. 16 microenterprise; rule on UK Op Res proportionality | DORA + UK Op Res |
| Drop `eu_member_state_count`, `data_volume_band` if not used by end of phase | Or wire them; either way remove dead-fact surface | — |

**Deliverables:**
- New questions in `DEFAULT_KB` with correct `shown_if` predicates that mirror the receiving regime's applicability.
- Rules wiring dead facts into applicability where useful; question dropped where not.
- Report cover updated to show *"n questions asked · <regime count> regimes assessed"* so completeness is visible to the customer.

**Duration:** 3–5 days.
**Risk:** low — additive. Existing regime calls unchanged.
**Go/no-go gate:** Legal sign-off on the new AI-Annex-III language + microenterprise advisory text.

---

## Phase 3 — New regime coverage (additive; each an independent block)

**Why last of the content phases.** Each is a new object added to `KB.regimes[]` with the same shape as existing ones. Independent of other regimes' output. Can be sequenced individually — ship the ones with highest customer impact first.

**Sequenced by impact for a UK/EU FS audience:**

| Order | Regime | Legal reference | Likely customer % who trigger it |
|---|---|---|---|
| 3.1 | **EUCS** (Cloud certification) | EU Cybersecurity Act framework | High for any customer picking "sovereign cloud" — central to the tool's narrative |
| 3.2 | **PSD2 / PSD3 + PSR** | Directive (EU) 2015/2366; (draft) PSD3 / PSR | Every payment institution & EMI in Q_FINTYPE |
| 3.3 | **CRR / CRD outsourcing + EBA guidelines on ICT & cloud** | CRR/CRD framework; EBA/GL/2019/02 outsourcing; EBA/GL/2019/04 ICT & security risk | Every credit institution |
| 3.4 | **Solvency II outsourcing** | Directive 2009/138/EC + Delegated Regulation 2015/35, Art. 274 | Every insurer / reinsurer |
| 3.5 | **eIDAS 2 (EU Digital Identity Wallet)** | Regulation (EU) 2024/1183 | Directly relevant to any FS firm doing customer onboarding — advisory-grade |

**Each regime block includes:** `id`, `name`, `short`, `legal_reference`, `jurisdiction`, `weight` (recompute weight normalization at end of phase), `applicability_rules`, `obligations`, `readiness_dimensions`, `sources`, and at least one readiness question.

**Deliverables per sub-phase:** one patch script per regime, ship to staging, legal review, promote.

**Duration:** 2 weeks (5 regimes × ~2 days each).
**Risk:** low — additive. The only cross-regime risk is if a new regime double-counts an obligation already covered elsewhere (e.g., PSD2 vs. DORA outsourcing) — mitigate with an explicit "primary / supplementary" flag on the rationale.
**Go/no-go gate:** Legal sign-off per regime.

---

## Phase 4 — Ongoing (analytics, feedback, refresh cadence)

**Why part of the plan.** Without these, we won't know if the tool is helping customers, we won't hear when regulations change, and we won't catch the day a source URL goes 404.

**Deliverables:**

1. **Anonymous analytics** — inject a lightweight tracker (Plausible / self-hosted) that captures: assessment started, section reached, regimes fired, report generated, Contact Us clicked. No PII. Behind a cookie-consent notice (GDPR — we're on the tool ourselves).
2. **In-tool feedback** — small "Was this useful?" thumbs at the end of the report; captures a free-text field if thumbs-down.
3. **Refresh calendar** — quarterly review by a named owner: check DORA CTPP designations (ESAs), AI Act phased commencement (Art. 113), DUAA 2025 commencement orders, adequacy decisions, CJEU rulings on Chapter V. Output: `docs/SOVEREIGN-SCREEN-CHANGELOG.md` entry + framework version bump.
4. **Source-URL health check** — CI job that HTTP-HEADs every `sources[].url` monthly; flags 4xx/5xx.
5. **Framework version display** — every report shows `Framework v<n>.<n>.<n> · reviewed <date>` so a customer can quote it back to us when they raise a question 6 months later.
6. **Public changelog** — every framework version bump documented in a customer-visible changelog on the same S3 bucket. Builds trust that regulations *are* being tracked.

**Duration:** 1 week to set up, then a recurring quarterly obligation.
**Risk:** low.
**Go/no-go gate:** analytics cookie/consent story reviewed by DPO before it ships.

---

## Cross-phase — legal review model

For each phase to reach prod, the following need to happen:

1. **I ship to staging** — `s3://ltm-core/sovereign-screen-staging.html`.
2. **You (or nominated legal owner) reviews** — text of new rationales, obligations, sources, and the 5 representative profile outputs.
3. **You sign off in writing** — email/Slack acknowledgement referencing the git SHA.
4. **I promote to prod** — same patch script, `--target prod` flag, publishes to `sovereign-screen.html`.

The legal review of Phase 1 is the biggest — 8 items to check. Phases 2–4 are smaller (2–5 items each).

---

## Rough timeline (working days)

| Phase | Days | Cumulative |
|---|---|---|
| 0 — Guardrails | 1–2 | 1–2 |
| 1 — Legal defensibility (5+3 items) | 2–3 | 3–5 |
| 2 — Screening completeness | 3–5 | 6–10 |
| 3 — New regime coverage (5 blocks × ~2 days) | 8–12 | 14–22 |
| 4 — Analytics + refresh setup | 5 | 19–27 |

**~4–5 weeks end-to-end** if legal review keeps its 48-hour SLA. Phase 1 hits prod in the first week — that's when customer risk drops materially.

---

## Immediate ask

Please respond with:

1. **Legal owner assignment** — who at LTM is signing off? (Name + email; I'll route staging URLs and diffs to them.)
2. **Green light on Phase 0** — start guardrails now, or wait?
3. **Any phase you want re-sequenced** — e.g., if MiCA (currently Phase 1 #5) is urgent for a specific customer, we can pull it forward alone; if EUCS is a marketing-critical regime for a launch event, we can promote it out of Phase 3.

Once I have those, I'll start Phase 0 the same day.
