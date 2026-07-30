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
| 2026-07-30 | 0 — Guardrails | b93bd78 | Ashutosh Dixit | approved (implicit by "start Phase 1" instruction 2026-07-30) | Version stamp only; no legal/regime changes. Prod not yet promoted — will promote when Phase 1 is signed off (avoid two prod cutovers same day). |
| 2026-07-30 | 1 — Legal defensibility (8 items) | *(pending — SHA below on commit)* | Ashutosh Dixit | *pending* | Staging URL: https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen-staging.html · Diff summary: docs/SOVEREIGN-SCREEN-ROADMAP.md §Phase 1 |

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
