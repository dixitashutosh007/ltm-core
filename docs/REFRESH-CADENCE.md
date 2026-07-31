# CIS Tech Advisory — Refresh cadence

**Scope:** covers **Sovereign Screen** (16 regimes), **Data Residency & Jurisdiction Audit / DR&J** (10 regulations), **FinOps Value Case** (4 benchmark sources + BFSI modifiers) and **FinOps Maturity Screen** (44 questions across 5 stages, aligned to FinOps Framework references). Every framework or regulation change is reviewed at least quarterly; every change is logged in the corresponding tool's customer-facing changelog page.

## Sovereign Screen

Regulations move. Static knowledge bases drift. This document sets the schedule and the ownership that keep the Sovereign Screen accurate for real customers.

## Owner

**Ashutosh Dixit** — `ashutosh.dixit@ltm.com`

The named owner is responsible for:

1. Running each quarterly review below.
2. Signing off on framework version bumps (as per `docs/LEGAL-REVIEW.md`).
3. Nominating and briefing a deputy for scheduled leave.
4. Escalating any material change that can't wait for the next quarter.

## Review cadence

**Minimum:** every calendar quarter. Recommended dates: **1 Feb / 1 May / 1 Aug / 1 Nov**.

**Out-of-cycle triggers** — do a full review immediately when any of the following happen, not the next quarter:

- New or withdrawn EU Commission adequacy decision (particularly around the EU-US DPF or UK-US Data Bridge).
- CJEU judgment affecting GDPR Chapter V (a "Schrems III"-style ruling).
- New DORA CTPP designation by the ESAs.
- AI Act commencement milestone (see Art. 113 timeline).
- New DUAA 2025 commencement order in the UK.
- Announced enforcement action against LTM by any supervisor.

## What each review must check

### 1. Regulatory currency

Confirm each regime's `legal_reference` still matches the currently-in-force instrument. Check:

- **DORA (Reg. (EU) 2022/2554)** — RTS/ITS still current; incident-reporting timing unchanged.
- **NIS2 (Dir. (EU) 2022/2555)** — national transposition (any Member State materially in delay?).
- **UK Op Res (FCA PS21/3; PRA SS2/21)** — post-March 2025 supervisory expectations.
- **UK CTP (FSMA 2023; FCA PS24/16; PRA PS16/24)** — first HMT designations announced?
- **EU GDPR (Reg. (EU) 2016/679)** — EDPB Guidelines updates; any Art. 4/Ch. V CJEU rulings.
- **UK GDPR / DPA 2018 / PECR / DUAA 2025** — DUAA 2025 commencement orders (phased).
- **Transfer & jurisdictional** — DPF adequacy status; any listed US recipient audit failures; UK-US Data Bridge status.
- **EU AI Act (Reg. (EU) 2024/1689)** — Art. 113 phased commencement (prohibitions 2 Feb 2025; GPAI 2 Aug 2025; high-risk Chapter III 2 Aug 2026; obligations for high-risk under Annex II 2 Aug 2027). AI Office publications.
- **EU Data Act (Reg. (EU) 2023/2854)** — 12 Sept 2025 application; switching provisions phased.
- **UK AI advisory** — new ICO AI guidance versions; FCA AI update refreshes; PRA/BoE SS updates.
- **MiCA (Reg. (EU) 2023/1114)** — first-wave authorisations; ESMA RTS/ITS updates.
- **EUCS** — ENISA scheme adoption status.
- **PSD2 / PSD3+PSR** — PSD3 Directive / PSR Regulation trilogue outcome and adoption dates.
- **CRR / CRD** — CRR3/CRD6 implementation timing; EBA outsourcing GL updates.
- **Solvency II** — Solvency II 2020 Review implementation (Directive amendments); EIOPA guideline refreshes.
- **eIDAS 2** — Wallet ARF version updates; national wallet rollouts.

### 2. Source-URL health

Run the automated check:

```bash
python scripts/check-sources.py
```

Every URL in every regime's `sources[]` should return HTTP 2xx. 4xx / 5xx must be replaced with a current URL (or the source dropped).

The GitHub Actions workflow `.github/workflows/source-url-health.yml` runs this monthly automatically; a red run is the trigger for an out-of-cycle content check.

### 3. Question coverage

For each new regulatory development, decide:

- Does an existing question capture the fact this rule needs? If yes, note it in the review log and continue.
- If no, propose a new question or `fact_value` mapping and route through the staging → sign-off → prod flow.

### 4. Reader feedback triage

Review the last quarter's inbound feedback (via the in-tool feedback pill or Contact Us) for:

- Reported inaccuracies in a specific rationale.
- Repeated confusion about a specific label or scoring.
- Requests to add / clarify a regime.

Log every item; act on the actionable ones.

## Review log (Sovereign Screen)

Every review — even a "nothing to change" one — is logged here so the audit trail shows the framework was checked, not just left alone.

| Date | Owner | Notes | Framework version after review |
|---|---|---|---|
| 2026-07-30 | Ashutosh Dixit | Baseline. All 16 regimes cited to primary sources. All 5 previously-dead facts wired (except `sovereign_offering_status` which is used for readiness scoring). Source-URL health check to be automated. | v1.3.0 |

---

## Data Residency & Jurisdiction Audit (DR&J)

Same owner, same 48-hour SLA. Same quarterly cadence dates (1 Feb / 1 May / 1 Aug / 1 Nov).

### DR&J-specific out-of-cycle triggers

- EDPB or ICO guidance update on transfer mechanisms (DPF, SCCs, TIA).
- Commerce Department update to the DPF Program list (recipient certifications).
- New EU Data Act commencement milestone (switching provisions phase in through 2027).
- New EIOPA cloud outsourcing guidelines (EIOPA-BoS updates).
- New EBA outsourcing / ICT guidelines updates.
- FCA / PRA operational-resilience or CTP supervisory publications.
- Any HM Treasury CTP designation.

### Review log (DR&J)

| Date | Owner | Notes | Framework version after review |
|---|---|---|---|
| 2026-07-31 | Ashutosh Dixit | Baseline. 10 regulations, 35 questions, all with sources[] citations. Ships with DPF adequacy handling, UK Op Res / UK CTP / EU Data Act / UK AI advisory regimes, GPAI question, EUCS Basic tier, DORA RTS 4h/72h/1-month cadence. RAG algorithm now correctly reports "not answered" when questions unanswered. | v1.3.0 |

---

---

## FinOps Value Case (FVC)

Same owner, same 48-hour SLA. Same quarterly cadence dates (1 Feb / 1 May / 1 Aug / 1 Nov).

The FVC differs from Sovereign Screen and DR&J: it opines on financial opportunity, not regulation. The equivalent of "regulatory currency" for FVC is **benchmark currency** — the industry waste-rate anchors it uses must remain valid.

### FVC-specific out-of-cycle triggers

- New **Flexera State of the Cloud** annual release (typically Q1/Q2).
- New **FinOps Foundation State of FinOps** annual release.
- New **Harness Cloud Cost Management** report or equivalent (waste-floor anchor).
- Material change in the LTM engagement dataset feeding the BFSI directional modifiers (`bfsi_modifiers.factors`).
- Any customer challenge to a specific waste-band figure — reproduce the calculation, verify the anchor, respond.

### What each FVC review must check

- **Benchmark currency.** Each entry in `meta.benchmarks.sources[]` still points at the current version of the named report; note the release year and n-size.
- **BFSI modifier factors.** Rationales still hold (regulatory testing, DR duplication, residency, lift-and-shift, change control, commitment conservatism). Adjust `pts` values only against demonstrable engagement data — never speculatively.
- **Waste band boundaries.** `waste_model.bands[]` low/high pairs still straddle the multi-year 27–32% band and the Harness 21% floor at the correct capability tiers.
- **Currency list.** `meta.currencies[]` covers the currencies used by active customers. FX is not converted — the currency selector renames the symbol only; document this.
- **Sector gate.** BFSI uplift fires only when `sector_class === "bfsi"` (post-Phase 1). Verify the report basis line reflects the customer's classification.
- **Placeholder-asset audit.** Confirm no `status:"placeholder"` entries in `meta.case_studies[]` or `meta.brochure` reach a customer.

### Review log (FVC)

| Date | Owner | Notes | Framework version after review |
|---|---|---|---|
| 2026-07-31 | Ashutosh Dixit | Baseline + Phase 1 (BFSI sector gate, currency freeze, "not financial advice" disclaimer append, framework stamp on cover). 29 questions, 5 signals, 4 waste bands + BFSI uplift with capability-scaled ceiling. **Ship-blocker outstanding:** 3 case studies + brochure are placeholder PDFs — must be resolved (real PDFs or drop sections) before next customer demo. | v1.0.1 |

---

## FinOps Maturity Screen (FMS)

Same owner, same 48-hour SLA. Same quarterly cadence dates (1 Feb / 1 May / 1 Aug / 1 Nov).

The FMS is a maturity screen aligned to FinOps Framework references. It uses the FinOps mark under a non-affiliation notice (per Phase 1), so the trademark position must remain accurate at every review.

### FMS-specific out-of-cycle triggers

- New **FinOps Framework** version release by the FinOps Foundation (changes to Crawl / Walk / Run stage definitions or capability domains).
- New **FinOps Foundation State of FinOps** annual release (practitioner-signal shifts that could reweight critical questions).
- Any material change to the FinOps Foundation's trademark or brand-guidelines position — refresh the non-affiliation notice.
- Reported inaccuracy in a stage's gating, or a customer challenge to a specific critical-question threshold.

### What each FMS review must check

- **Framework alignment.** The 5 stages (Chaos → Informed → Optimised → Automated → Transparent) still map cleanly onto FinOps Framework capabilities. Note any new capability we should add a question for.
- **Trademark position.** `meta.disclaimer` still carries the non-affiliation notice: *"Aligned to FinOps Framework references. Not an official FinOps Foundation assessment or certification. 'FinOps' is a trademark of the FinOps Foundation."*
- **Critical-question gates.** Each stage's 3–4 criticals still represent hard prerequisites (not "nice to haves"). Verify `crit_min` cutoffs still make partial-credit answers a legitimate stage-fail signal, not a surprise.
- **Domain balance.** 44 questions across 5 domains — governance 8, visibility 12, optimisation 10, automation 5, culture 9. Rebalance only with cause.
- **Remediation strings.** Each `remediation` string is still a concrete next step; no rot from renamed cloud features (e.g., "Cost Explorer", "Cost Details").

### Review log (FMS)

| Date | Owner | Notes | Framework version after review |
|---|---|---|---|
| 2026-07-31 | Ashutosh Dixit | Baseline + Phase 1 (FinOps Foundation TM non-affiliation notice, C1 reframed from MFA/security to account-ownership + access model, framework stamp on cover). 44 questions, 5 stages, 17 criticals, 5 capability domains. Contiguous-stage progression + critical-question gate verified working. | v1.0.1 |

---

## Escalation

- **Legal question** about a specific rationale: reply on the relevant `docs/LEGAL-REVIEW.md` thread with the text quoted.
- **Suspected legally-wrong output in prod**: invoke `docs/ROLLBACK.md` immediately (protect the customer), then debate the fix on staging.
- **New regulation that can't wait**: out-of-cycle review + Phase-1-style patch → staging → sign-off → prod, same workflow.
- **Trademark position challenge** (FMS): treat as legal-review priority — refresh the non-affiliation notice text and redeploy inside the SLA.
