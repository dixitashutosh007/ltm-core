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
| 2026-07-30 | 0 — Guardrails | *(pending, see below)* | Ashutosh Dixit | *pending* | Staging URL: https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen-staging.html |

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
