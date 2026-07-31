# CIS Tech Advisory — Refresh cadence

**Scope:** covers both **Sovereign Screen** (16 regimes) and **Data Residency & Jurisdiction Audit / DR&J** (10 regulations). Every regulation is reviewed at least quarterly; every framework change is logged in the corresponding tool's changelog page.

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

## Escalation

- **Legal question** about a specific rationale: reply on the relevant `docs/LEGAL-REVIEW.md` thread with the text quoted.
- **Suspected legally-wrong output in prod**: invoke `docs/ROLLBACK.md` immediately (protect the customer), then debate the fix on staging.
- **New regulation that can't wait**: out-of-cycle review + Phase-1-style patch → staging → sign-off → prod, same workflow.
