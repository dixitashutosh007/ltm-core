# Legal review log — LTM CIS Tech Advisory accelerators

## Ownership

- **Legal review owner:** Ashutosh Dixit (`ashutosh.dixit@ltm.com`)
- **Review SLA:** 48 hours from staging-URL sent → sign-off / feedback.
- **Sign-off form:** written acknowledgement (email or Slack) referencing
  the git SHA of the candidate build.

## Review model

For every phase in `docs/SOVEREIGN-SCREEN-ROADMAP.md`:

1. Author ships the change to **staging** — a distinct S3 key so the live
   production URL is untouched.
2. Author sends the staging URL + git SHA + diff summary to the legal
   owner.
3. Legal owner reviews:
   - Text of any new / changed rationales, obligations, disclaimers.
   - Source citations (verify URLs resolve to authoritative pages).
   - Regime call output for 5 representative profiles:
     - UK-only bank
     - EU-only bank
     - EU insurer using non-life AI pricing
     - ICT provider designated CTP
     - CASP crypto entity
4. Sign-off is written and referenced by SHA.
5. Author promotes to **prod** using the same patch script with
   `--target prod`.

No content changes may hit prod without a sign-off referencing the exact
SHA of the promoted build.

## Sign-off log

| Date | Phase | SHA | Reviewed by | Decision | Notes |
|---|---|---|---|---|---|
| 2026-07-30 | 0 — Guardrails | b93bd78 | Ashutosh Dixit | approved (implicit by "start Phase 1" instruction 2026-07-30) | Version stamp only; no legal/regime changes. |
| 2026-07-30 | 1 — Legal defensibility (8 items) | 2413594 | Ashutosh Dixit | approved (Option A: "Sign-off + Phase 2 in parallel" 2026-07-30) | 8 items: DPF adequacy, Q_SOVOFFER controls, Q_HYPER widened, UK AI regime, MiCA regime, grade relabel, Q_CTP unknown escalation, QR_UKCTP widened. Promoted to prod on same day as Phase 0. |
| 2026-07-30 | 2 — Screening completeness (8 items) | 41730e1 | Ashutosh Dixit | approved (implicit by "carry on with next step" 2026-07-30) | 3 new questions (biometric KYC, employment AI, GPAI); 7 new rules wiring 4 previously-dead facts; AI Act Art. 51+ GPAI (3 rules). Promoted to prod 2026-07-30 14:56:58 UTC. |
| 2026-07-30 | 3 — New regime coverage (5 regimes) | 9fcab18 | Ashutosh Dixit | approved (implicit by "continue with next step" 2026-07-30) | Additive: EUCS, PSD2/PSD3, CRR/CRD + EBA outsourcing, Solvency II, eIDAS 2. Each an independent block; no changes to existing regimes. Promoted to prod 2026-07-30. |
| 2026-07-30 | 4 — Ongoing (P4.1–P4.4) | a3b59df | Ashutosh Dixit | approved ("Lets execute" 2026-07-30) | Public changelog + refresh cadence + source-URL health-check workflow + in-tool feedback pill (v3 overlay across all 4 accelerators). Promoted to prod. |
| 2026-07-30 | 4.5 — Analytics | — | Ashutosh Dixit + DPO | **DEFERRED — DPO gate** | Not started. Requires DPO review of cookie/consent story before build. Tracked as task #29. |
| 2026-07-31 | **DR&J** 1 — Legal defensibility (4 items) | 9e0ce94 | Ashutosh Dixit | approved ("implement the changes recommended" 2026-07-31) | DPF adequacy (Q_D1 / Q_C2 / Q_F1 / Q_G2); Q_C1 GCP split; +3 new regulations (Data Act, UK Op Res, UK CTP) with 3 new questions (Q_D3, Q_F5, Q_I3); Q_H3 sovereign-controls follow-up. Inventory: 6→9 regulations, 29→33 questions. Promoted to prod 2026-07-31. |
| 2026-07-31 | **DR&J** 2 — Screening completeness (7 items) | 7989a4f | Ashutosh Dixit | approved ("move to next stage. Implement" 2026-07-31) | Q_C1 +7 US-HQ providers; Q_C2 +2 rows +UK column; Q_A2 +payment-EMI +CASP; Q_G1 wording fix + Q_G3 GPAI; Q_H2 +Basic; Q_J1 +DORA RTS; Q_B1 refined. Promoted to prod 2026-07-31. |
| 2026-07-31 | **DR&J** 3 — UK AI advisory regime | *(SHA on commit)* | Ashutosh Dixit | *pending* | Staging URL: https://ltm-core.s3.us-east-1.amazonaws.com/Data-Residency-Jurisdiction-Audit-staging.html · +ukai regulation (ICO / FCA / PRA SS1/23); Q_G4 UK AI principles alignment. Auto-selects on UK footprint; added to finserv+insurance sector.regs. Inventory: 9→10 regulations, 34→35 questions. Additive. |

*(Add one row per promotion. Never delete rows — the log is the audit trail.)*

## Staging URLs (current)

- **Sovereign Screen:** https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen-staging.html
- **FinOps Value Case:** https://ltm-core.s3.us-east-1.amazonaws.com/finops-value-case-staging.html
- **FinOps Maturity:** https://ltm-core.s3.us-east-1.amazonaws.com/finops-screen-staging.html
- **Data Residency & Jurisdiction Audit:** https://ltm-core.s3.us-east-1.amazonaws.com/Data-Residency-Jurisdiction-Audit-staging.html

## Escalation

- **Legal question about a specific rationale / regime call:** reply on
  the sign-off thread with the specific text quoted.
- **Suspected legally-wrong output in prod:** invoke `docs/ROLLBACK.md`
  first (protect the customer), then debate the fix.
- **New regulation or supervisory update:** raise a note in the next
  quarterly refresh (see roadmap Phase 4) or, if material and time-
  sensitive, request an out-of-cycle review.
