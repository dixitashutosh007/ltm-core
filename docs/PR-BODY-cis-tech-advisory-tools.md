# LTM CIS Tech Advisory — 4 accelerators to defensible-in-prod

Delivers a full technical + legal review, phased fixes, sign-off, and prod deployment of the four customer-facing CIS Tech Advisory tools — plus the infrastructure (staging pipeline, refresh cadence, source-URL health-check, changelog, TOS) needed to keep them defensible over time.

## What shipped to prod

| Accelerator | Framework | Live URL |
|---|---|---|
| **Sovereign Screen** | v1.3.0 · 16 regimes · 47 questions · 89 sourced URLs | [`/sovereign-screen.html`](https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen.html) |
| **Data Residency & Jurisdiction Audit** | v1.3.0 · 10 regulations · 35 questions · 32 sourced URLs | [`/Data-Residency-Jurisdiction-Audit.html`](https://ltm-core.s3.us-east-1.amazonaws.com/Data-Residency-Jurisdiction-Audit.html) |
| **FinOps Value Case** | v1.0.3 · 29 questions · 4 benchmark sources · BFSI sector gate | [`/finops-value-case.html`](https://ltm-core.s3.us-east-1.amazonaws.com/finops-value-case.html) |
| **FinOps Maturity Screen** | v1.0.3 · 44 questions · 5 stages · 17 criticals · 5 domains | [`/finops-screen.html`](https://ltm-core.s3.us-east-1.amazonaws.com/finops-screen.html) |

## What the customer sees on every tool

- **"Not legal / financial advice"** disclaimer in the report + right-rail Contact Us tab + feedback pill (v3 overlay)
- **`Framework v1.x.y · reviewed <date>`** stamp on every generated report cover — every output is traceable back to a specific build
- **Customer-facing changelog page** per tool with every release, scope and sign-off owner ([SoS](https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen-changelog.html) · [DR&J](https://ltm-core.s3.us-east-1.amazonaws.com/dr-j-changelog.html) · [FVC](https://ltm-core.s3.us-east-1.amazonaws.com/finops-value-case-changelog.html) · [FMS](https://ltm-core.s3.us-east-1.amazonaws.com/finops-maturity-changelog.html))
- **Terms of Use** ([live](https://ltm-core.s3.us-east-1.amazonaws.com/terms-of-use.html)) covering ownership, permitted / prohibited use, no-warranty, governing law (India, non-exclusive jurisdiction). Copyright banner in HTML source, JS source, and in-tool disclaimer popover — three layers of visible ownership assertion.

## Governance you can rely on

- **`docs/LEGAL-REVIEW.md`** — 12 sign-off rows, each cites the git SHA of the promoted build. Ashutosh Dixit named legal owner with 48-hour SLA.
- **`docs/REFRESH-CADENCE.md`** — quarterly review cadence (1 Feb / May / Aug / Nov) for all four tools, with tool-specific out-of-cycle triggers (adequacy decisions, Schrems-style rulings, DORA CTP designations, new Flexera / State of FinOps releases, new FinOps Framework versions).
- **`docs/ROLLBACK.md`** — 3-command rollback runbook if a promotion goes wrong.
- **`.github/workflows/source-url-health.yml`** — runs `scripts/check-sources.py` monthly; a red run triggers an out-of-cycle content review.
- **Bundled-patch infrastructure** — 9 idempotent phase-patch scripts (`scripts/patch-*.py`) with 3 layers of guards (JSON payload validity, `node --check` on inline scripts, semantic marker sweep). Every patch dry-runs before writing.

## Numbers

- **33 commits** across ~7 days
- **4 accelerators** reviewed end-to-end
- **4 deep-review documents** (`docs/*-REVIEW.md`, ~250 lines each)
- **12 phase patches** applied to prod (Sovereign Screen P0–P4 · DR&J P1–P4 + hotfix · FVC P1–P3 · FMS P1–P3 · Tier 1 code protection)
- **12 legal sign-offs** logged
- **1 customer-facing outage** on DR&J (raw-string `\n` bug in a patch script) — root-caused, hotfixed same-day, prevention (`js_syntax_check`) back-ported to all patch scripts
- **~700 KB** deployed per full push (`deploy-s3.py --target both`, 22 uploads)

## What's outstanding — needs the practice, not the code

1. **AWS deploy key rotation** — the access key used during the session should be rotated (in-chat exposure).
2. **Real case study + brochure PDFs** for FVC — framework already gates placeholders; drop the PDFs and flip `status:"placeholder"` → `"published"`.
3. **Analytics (P4.5)** — DPO-gated. Cookie / consent story needs DPO sign-off before build.
4. **Formal copyright registration** — UK Copyright Service (~£40) and India Copyright Office (~₹500) — cheap enforcement insurance on top of the TOS position.

## Next natural triggers

- **1 Aug 2026** — first quarterly refresh under the cadence
- **Any adequacy / CJEU / commencement event** — out-of-cycle trigger per REFRESH-CADENCE.md
- **Customer feedback** via the in-tool pill or Contact Us — 48-hour SLA
- **New accelerator** in the CIS Tech Advisory line — same phased pattern is reusable
- **Product decision on Tier 2** (server-side scoring engine) — real IP protection if / when a competitor lifts the framework or the tools become a revenue product rather than lead-gen

---

_Every claim above is checkable in `docs/LEGAL-REVIEW.md`, the four `docs/*-REVIEW.md` documents, and the tool changelog pages. Nothing was promoted to prod without a sign-off row referencing the exact SHA._
