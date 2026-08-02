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
| 2026-07-31 | **DR&J** HOTFIX — Phase 1 raw-string \n bug | d0ab99a | Ashutosh Dixit | approved retroactively ("hotfix confirmed OK" 2026-07-31) | Customer-reported outage: JS SyntaxError on tool load. Root cause: patch-drj-phase1.py INSERT_QD3/QF5/QH3/QI3 used raw strings (r'…') that put literal \n into the JS body. All Phase 1/2/3 rebuilt with the fix in place. js_syntax_check guard now in Phase 1/2/3 patch scripts. |
| 2026-07-31 | **DR&J** 4 — Ongoing / hygiene (5 items) | b50f3bd | Ashutosh Dixit | approved ("Approved, pls go ahead and implement" 2026-07-31) | sources:[{name,url}] on all 10 regulations (32 URLs); framework version stamp on report cover; ragForRegulation fix; customer-facing changelog page; DR&J added to REFRESH-CADENCE.md. Promoted to prod 2026-07-31. **DR&J ROADMAP COMPLETE.** |
| 2026-07-31 | **FVC** 1+2+3 — Legal defensibility + scoring correctness + ship-blocker mitigation (14 items, 4 phases) | 29d49d6 | Ashutosh Dixit | approved ("Signing off for both FVC and FMS to Prod" 2026-07-31) | **Phase 1** (SHA 4fb8c2f): BFSI sector gate (dropdown + wasteBand gate + basis prose), currency freeze on report render + Currency stamp on cover, "not financial advice" appended to disclaimer, framework v1.0.3 + reviewed date on cover. **Phase 2**: Oracle Cloud → hyper:true (Q_E2), url: on all 4 meta.benchmarks.sources[] (Flexera 2026 + multi-year + Harness 2025 + FinOps Foundation SoF 2026), allocation_100 returns null when total ≠ 100. **Phase 3**: PLACEHOLDER PDF chip removed from codebase entirely; case_studies filtered to non-placeholder with graceful fallback paragraph; brochure download card gated on non-placeholder status (surfaces automatically when real PDFs land + status flipped to "published"). Bumped schema_version → 1.0.3. Customer changelog + REFRESH-CADENCE entry already landed via P4 (SHA a868a85). Promoted to prod 2026-07-31 16:45:48 UTC (both prod + staging keys). Framework v1.0.3 confirmed live at https://ltm-core.s3.us-east-1.amazonaws.com/finops-value-case.html · PLACEHOLDER PDF chip count = 0. **FVC ROADMAP COMPLETE** (bar the outstanding real-PDF asset drop, which is a content task not a code task). |
| 2026-07-31 | **FMS** 1+2+3 — Legal defensibility + scoring correctness + hygiene (11 items, 4 phases) | 29d49d6 | Ashutosh Dixit | approved ("Signing off for both FVC and FMS to Prod" 2026-07-31) | **Phase 1** (SHA bc5c472): FinOps Foundation non-affiliation notice + TM attribution appended to disclaimer; C1 reframed from MFA/security-posture question to account-ownership + access-model FinOps question (dropped the security-finding-from-LTM risk); framework v1.0.3 + reviewed date on cover. **Phase 2**: C4 remediation + allow_dk (softens RBAC over-scope); culture domain relabelled "Culture & engineering behaviour" (disambiguates from Governance); O10 drag_order unscored:true (informational only, doesn't penalise legitimate estate variance); C8 gains "None of these" exclusive option; boolean_dk (`allow_dk:true` + `dk_blind`) on 6 questions (C3, C4, I6, O7, A7, T4) with a new Blind spots report section listing every Unsure answer + its narrative. Uses "Unsure" label to sidestep JSON backslash-apostrophe crash. **Phase 3**: C2 middle option reworded ("does not yet cover all providers / accounts") for pass-fail clarity at Chaos crit_min:70; meta.sources[] citing FinOps Foundation Framework + State of FinOps + Flexera, rendered as clickable list in Method section; confidenceLabel() function + Reasonable/Moderate/Low chip in report header driven by scored/total ratio. Bumped schema_version → 1.0.3. Customer changelog + REFRESH-CADENCE entry already landed via P4 (SHA a868a85). Promoted to prod 2026-07-31 16:45:48 UTC (both prod + staging keys). Framework v1.0.3 confirmed live at https://ltm-core.s3.us-east-1.amazonaws.com/finops-screen.html. **FMS ROADMAP COMPLETE.** |

| 2026-07-31 | **Tier 1 code protection** — copyright banners + TOS across all 4 accelerators | *(commit on push)* | Ashutosh Dixit | approved ("Lets execute" 2026-07-31) | HTML comment banner + JS `/*! */` banner asserting LTIMindtree Limited copyright, permitted / prohibited use scope, and pointer to Terms of Use — applied uniformly to Sovereign Screen, DR&J, FVC, FMS. In-tool disclaimer popover gains a "Terms." row with a live TOS link so every customer sees the position without needing to inspect source. New `terms-of-use.html` page (coral+ink themed, mirrors changelog visual language) covers ownership, permitted use, prohibited use (extraction / reverse-engineering / redistribution / ML training data / notice removal), advisory-nature disclaimer, no-warranty, limitation of liability, privacy, changes-to-terms, and governing law (India, non-exclusive jurisdiction in Mumbai courts). Not a security control — anything shipped to a browser is inspectable — this is a legal deterrent that establishes copyright and scopes permitted use. Deployed 2026-07-31 to prod + staging (22/22 uploads). Smoke-tested: LTIMindtree copyright text present in all 4 bundled tools; TOS link present in the disclaimer popover of all 4; terms-of-use.html serves HTTP 200. |

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
