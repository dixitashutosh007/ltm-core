# Sovereign Screen — Changelog

The source of truth for all framework changes. Every update is signed off by a named LTM legal-review owner before it reaches customers.

The customer-facing version of this page lives at
https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen-changelog.html
and is generated from this file.

---

## Framework v1.3.0 — 2026-07-30

**5 new regime blocks** added covering EU-specific rules for banks, insurers, payment institutions, cloud providers and digital identity. Each block includes primary-source citations and a matching readiness question.

- **EUCS** — EU Cybersecurity Certification for Cloud Services. Advisory-grade regime for EU financial firms sourcing non-EU cloud, and for cloud providers considering certification. Sources: Regulation (EU) 2019/881, ENISA EUCS scheme.
- **PSD2 / PSD3+PSR** — Payment Services. Applies to payment institutions, EMIs and credit institutions with EU nexus. Covers SCA, AIS/PIS access, incident reporting, and forward-looking PSD3/PSR readiness. Sources: Directive (EU) 2015/2366, EBA PSD2 hub, Commission PSD3/PSR proposals.
- **CRR / CRD + EBA cloud outsourcing** — Banks. Applies to credit institutions with EU nexus. Covers the prudential framework and the EBA outsourcing guidelines (EBA/GL/2019/02) plus ICT & security risk (EBA/GL/2019/04). Sources: EUR-Lex CRR + CRD, EBA guidelines.
- **Solvency II** — Insurers. Applies to insurers and intermediaries with EU nexus. Covers the three-pillar framework and Article 274 outsourcing (Del. Reg. 2015/35) plus EIOPA cloud outsourcing guidelines (BoS-20-002). Sources: EUR-Lex Solvency II + Delegated Regulation, EIOPA.
- **eIDAS 2** — EU Digital Identity Wallet. Advisory-grade for EU financial firms and their ICT providers, preparing for Wallet-acceptance obligations by end-2026. Sources: Regulation (EU) 2024/1183, European Commission EUDI page, Architecture Reference Framework.

**Inventory after this release:** 16 regimes, 47 questions, 22 facts. All 16 regimes have authoritative source citations.

Legal-review sign-off: Ashutosh Dixit (ashutosh.dixit@ltm.com).

---

## Framework v1.2.0 — 2026-07-30

**Screening completeness — 3 new questions + 7 new rules** wiring 4 previously-unused facts. Additive — no existing regime call was changed.

- **New question `Q_BIOMETRIC`** — biometric identification / verification of natural persons in KYC, auth, fraud prevention, or workforce access. Sets `uses_high_risk_ai = true` (AI Act Annex III item 1). Fills a critical gap for FS firms using biometric KYC.
- **New question `Q_EMPAI`** — AI in recruitment, work allocation, promotion, performance evaluation. Sets `uses_high_risk_ai = true` (Annex III item 4).
- **New question `Q_GPAI`** — role in relation to general-purpose AI models (downstream user / provider / integrator / none). Feeds three new AI Act Chapter V rules.
- **DORA Art. 16 microenterprise regime** wired to `company_size`. Reports the DORA simplified regime for micro EU financial entities (< 10 staff and ≤ €2m turnover or balance-sheet total, per Commission Recommendation 2003/361/EC).
- **GDPR Art. 9 special-category rule (EU + UK mirror)** wired to `special_category_data`. Adds DPIA (Art. 35), DPO (Art. 37(1)(c)), and Schedule 1 DPA 2018 references.
- **UK Op Res proportionality rule** wired to `company_size` in [micro, small] + UK financial entity.
- **GDPR one-stop-shop rule** wired to `eu_member_state_count >= 2`. Cites Art. 56 and EDPB Guidelines 8/2022.
- **GDPR large-scale processing rule** wired to `data_volume_band` in [1m_10m, over_10m]. Cites Art. 30, Art. 35, Art. 37(1)(b), and WP 248 rev.01.

**Inventory after this release:** 11 regimes, 42 questions, 22 facts (only 1 remains applicability-unused, down from 5).

Legal-review sign-off: Ashutosh Dixit.

---

## Framework v1.1.0 — 2026-07-30

**Legal-defensibility fixes.** Eight items in the v2 review that changed customer-visible output.

- **DPF adequacy handling** — new `Q_DPFCERT` follow-up when data is hosted in the US. The transfer / jurisdictional rule now splits by DPF certification status. DPF-certified recipients → *Informational* (Commission Implementing Decision (EU) 2023/1795 adequacy applies). Non-certified / unknown → *Confirm with counsel* (Schrems II / FISA §702 / EO 14086 rationale).
- **Q_SOVOFFER controls follow-up** — "Yes — sovereign offering" score reduced from 100 to 70 (baseline claim). New `QR_SOVCTRL` rating captures the evidence side; averaged with the claim, this eliminates the flagship-dimension false-pass.
- **Q_HYPER widened** — now explicitly names Oracle Cloud, IBM Cloud, Salesforce/Heroku, Snowflake, Databricks alongside AWS/Azure/GCP.
- **UK AI advisory regime** — new regime block citing ICO AI guidance, FCA supervisory expectations, PRA/BoE SS1/23.
- **MiCA regime** — new regime block for crypto-asset service providers (CASPs) with EU nexus. Regulation (EU) 2023/1114.
- **Grade labels relabelled** — `needs_legal_review` → **Confirm with counsel**; `advisory` → **Informational**. Removes the "more severe" misread of a legal-review flag.
- **Q_CTP "unknown" escalation** — an "I don't know" answer on CTP dependency now surfaces as *Confirm with counsel* rather than silently dropping out.
- **QR_UKCTP widened** — ICT-provider entities now see the UK CTP readiness question.

Legal-review sign-off: Ashutosh Dixit.

---

## Framework v1.0.0 — 2026-07-30

Baseline release after the initial legal-content review.

- Framework version stamp added to every report (currently v1.0.0).
- Meta disclaimer updated to point customers at the sources / methodology section.
- Placeholder-note TODO leaking into the KB removed.

Legal-review sign-off: Ashutosh Dixit.

---

## Earlier

Content-only fixes for legal accuracy (Q_SCD wording, AI Act penalty tiers, insurance AI split, DORA CTP designation count) and authoritative source citations for every regime (EUR-Lex, legislation.gov.uk, FCA, PRA, BoE, EBA, ENISA, European Commission, EDPB, DOJ, ICO). Delivered as a set of atomic patches with a JSON-safety guard that refuses to save when the bundler payload would stop parsing.

---

## About this changelog

**Refresh cadence.** Every regulation change (new adequacy decision, EU AI Act phased commencement, DUAA 2025 commencement orders, CJEU rulings) is tracked in `docs/REFRESH-CADENCE.md`. Named owner: Ashutosh Dixit. Quarterly reviews at minimum.

**Every entry cites primary sources** (EUR-Lex, legislation.gov.uk) or the standing supervisory authority (FCA, PRA, EBA, ENISA, EDPB, EIOPA, ICO, European Commission, DOJ). No blog posts, no vendor whitepapers, no LLM-generated summaries as authorities.

**Nothing is legal advice.** The disclaimer on every report page applies to everything here.
