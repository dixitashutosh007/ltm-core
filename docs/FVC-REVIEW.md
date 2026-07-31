# FinOps Value Case — v1 Review

**File reviewed:** `finops-value-case/FinOps Value Case (LTM).html`
**Framework version (per KB `meta.schema_version`):** 1.0.0
**KB `meta.last_reviewed`:** 2026-07-22
**Live URL:** https://ltm-core.s3.us-east-1.amazonaws.com/finops-value-case.html
**Staging URL:** https://ltm-core.s3.us-east-1.amazonaws.com/finops-value-case-staging.html

**Reviewer disclosure.** Technical + framework-integrity review. This is not a financial-advice opinion; every claim about a benchmark points at the published source, not an interpretation for a specific customer.

**Method.** `DEFAULT_KB` extracted from the bundled HTML (offset 165 809, 24 596 bytes). Full `questions[]`, `sections[]`, `meta` (signals, waste_model, benchmarks, verdict_bands, service_areas, case_studies, brochure, disclaimer) walked. Scoring engine read end-to-end: `qScore`, `signalScores`, `blindSpots`, `annualSpend`, `growth`, `urgencyIndex`, `gapIndex`, `needIndex`, `wasteBand`, `exposure`, `verdict`, `confidence`, `recommendedServices`, `relevantCaseStudies`.

---

## 0. What the tool is

A pre-maturity **qualification** instrument — sizes the unrealised value at stake from cloud waste so a customer can decide whether a formal FinOps engagement is worth commissioning. Not a maturity assessment (that's a separate tool). Output is a value-case PDF with a money range, verdict, blind-spot list, weakest-signal narrative, LTM service triggers and case-study picks.

**Inventory:**

| Metric | Value |
|---|---|
| Sections | 6 (estate, visibility, predictability, ownership, controls, value) |
| Questions | 29 |
| Answer formats | 10 (card_select, multi_select_logo, single_select, multi_select, boolean_dk, rating_1_5, slider_percent, slider_signed, slider_currency, allocation_100, drag_order, open_text) |
| Scoring signals | 5 (visibility 0.22, control 0.22, predictability 0.20, ownership 0.20, value 0.16) |
| Waste model | 4 capability bands + BFSI uplift, capped at 45% |
| Verdict bands | 4 (monitor / foundations / material / urgent) |
| Service areas | 7 |
| Case studies | 3 |
| Benchmark sources | 4 (Flexera '26, Flexera multi-year '19–'26, Harness '25, FinOps Foundation '26) |
| Currencies | 4 (GBP default, USD, EUR, INR) |
| Disclaimer | Present — "Indicative … not a guarantee of savings" |
| Framework version stamp on report | **No** |
| Currency stamp on report | **No (currency re-denominates live from `S.org.currency`)** |
| Source URLs on benchmarks | **No — labels + notes only** |

---

## 1. What's good

The tool is substantially better-constructed than a typical value-case calculator:

- **Signal-weighted scoring is honest.** Each question declares `signals:[{id,w}]`. The weighted mean per signal excludes questions that don't touch it. No fake "score everything" behaviour.
- **`"Don't know"` is a first-class answer.** `boolean_dk` and `allow_dk` sliders let users decline. DK contributes 0 to scoring, and — importantly — feeds `blindSpots()` which renders a distinct "Your blind spots" section on the report with an explanatory line per unknown (`dk_blind`). This is the design a value case *should* have.
- **Waste bands are cited to real sources.** Flexera 2026 State of the Cloud (n=753), Flexera multi-year 27–32% band 2019–2026, Harness Cloud Cost Management 2025 (21% floor), FinOps Foundation State of FinOps 2026. Not a made-up 30%.
- **`bfsi_modifiers.editable:true` and `honesty_note`** explicitly disclose that published waste benchmarks are cross-industry, and that the BFSI uplift is an LTM directional adjustment — not a published sector waste rate. This is the correct way to acknowledge the limit of the evidence.
- **BFSI uplift scales inversely with capability** — `wasteBand()` computes `uplift = full*(1-cap/100)`, so a customer with mature controls gets no BFSI penalty. The `basis` text on the report explains this. Not a flat sector penalty.
- **Confidence label is derived from blind-spot count**, not asserted. Low / Moderate / Reasonable with an explanatory note. Prevents over-selling directional numbers.
- **Three-year cumulative exposure** applies growth compounding (`s*=(1+g)` per year). Growth clamped to ≥0 for the 3-year figure so a shrinking estate doesn't project savings you already promised Finance.
- **`needIndex = 0.6·gap + 0.4·urgency`** — a defensible split. Gap comes from the weighted mean of `(100 − signal)` × signal weight; urgency comes from growth rate, migration-ahead, journey stage, historical bill-explanation events, budget variance, and multi-hyperscaler footprint.
- **Money not calculable when `E3=DK`** — cover shows *"An organisation that cannot state its cloud spend cannot govern it."* Excellent framing; better than silently defaulting.
- **Report basis line** on the money box explains: capability band, sector uplift in pts, why the uplift scales, and reproduces the confidence note. A CFO can audit the number back to the answers.
- **`concern_map` on Q_C4 re-orders the recommended service areas** by the customer's stated concern ranking. Small but well-done.
- **Existing disclaimer** — *"Indicative estimate based on self-reported inputs and published industry benchmarks. Figures illustrate the scale of opportunity and are not a guarantee of savings. A validated baseline requires assessment of actual billing data."* Honest.

---

## 2. Legal / labelling defects (HIGH priority)

These change a customer-visible figure, misdirect a Finance reader, or expose LTM to a mis-selling argument.

### 2.1 BFSI uplift applies regardless of the sector the user typed

`S.org.sector` is a **free-text input** (defaults to "Banking / Financial Services"). `wasteBand()` unconditionally applies `M.benchmarks.bfsi_modifiers` — the six BFSI factors (elevated non-prod estate, mandated DR duplication, residency constraints, lift-and-shift core systems, extended change control, conservative commitments) — with no check that the customer is actually in BFSI. A retailer who overwrites "Banking / Financial Services" with "Retail" still gets the BFSI uplift on the upper-band figure **and** the report basis line still reads *"A BFSI sector adjustment of +X percentage points is applied…"*.

**Impact:** every non-BFSI customer gets a BFSI-sector figure with BFSI justification prose. The number and the narrative are both wrong for them.

**Fix:** either (a) constrain sector to a dropdown of {BFSI, non-BFSI} and gate the uplift, or (b) rename the factors and prose to be sector-agnostic ("regulated-industry considerations") and only assert BFSI when a sector chip is picked. Recommend (a); it's the honest fix.

### 2.2 No currency stamp on the report cover — figures re-denominate live

`money()` reads `S.org.currency` at render time. If the user completes the assessment in GBP, opens the report, then switches currency in the Bank / Org screen, every figure — the money box, the 3-year cumulative, the "£2.0m" spend anchor in the basis line — silently re-denominates against the unchanged raw spend value. A £2m estimate becomes $2m or ₹2m by clicking a dropdown.

**Impact:** a report exported at t=0 in GBP and re-opened at t=1 after a currency change no longer matches its own numbers. This is a legitimate mis-quoting risk.

**Fix:** freeze `currency` (and the resolved symbol) onto the report at the moment `viewReport()` first renders it, or when the PDF is printed. Show `Currency: £ GBP` on the cover meta block.

### 2.3 No "not financial advice" language in the disclaimer

Current: *"Not a guarantee of savings."* A CFO reading `£340k – £580k unrealised value · next 12 months` in a range on an LTM-branded PDF may reasonably treat it as a savings quote — the exact reading the current wording tries to prevent, but doesn't say plainly.

**Fix:** append to the disclaimer: *"Indicative and directional only. Not a commitment, quote or financial advice."*

### 2.4 No framework version / review date on the report cover

`meta.schema_version` ("1.0.0") and `meta.last_reviewed` ("2026-07-22") exist in the KB but neither renders on the report. DR&J and Sovereign Screen both now stamp `v1.3.0 · framework reviewed <date>` on the cover after Phase 4. FVC is the last of the three still without.

**Fix:** show `Framework v1.0.0 · reviewed 2026-07-22 · currency GBP` on the cover meta block.

### 2.5 Oracle Cloud is `hyper:false` in Q_E2

Q_E2 options: AWS (`hyper:true`), Azure (`hyper:true`), Google Cloud (`hyper:true`), **Oracle Cloud (`hyper:false`)**, Private / hosted (`hyper:false`), Not yet decided (`hyper:false`).

Two consequences:

1. `urgencyIndex()` counts `hyper` platforms — if a user picks AWS + Oracle, the code sees `h=1` and does not fire the multi-hyperscaler +8 urgency penalty (which requires `h>=2`). That's a false negative on urgency.
2. Oracle Cloud is a US-HQ hyperscaler by any commercial definition (Gartner's IaaS + PaaS Magic Quadrant treats it as such) and carries the same CLOUD Act footprint as the other three. Flagging it as non-hyperscaler is inconsistent.

**Fix:** set Oracle Cloud `hyper:true`. Consider adding IBM Cloud too if it's likely to appear in customer estates — currently no option.

---

## 3. Framework / scoring defects (MEDIUM priority)

These affect defensibility of the number, not correctness of a specific customer's answer.

### 3.1 Benchmark sources have no URLs

`meta.benchmarks.sources[]` is `{label, note}` — no `url`. The report renders the labels + notes at the bottom under "Basis and sources", but a reviewer cannot click through to the primary source. DR&J P4.1 added `sources:[{name,url}]` on all 10 regulations for exactly this auditability. FVC should mirror.

**Fix:** add `url:` to each of the 4 sources (Flexera 2026 report page; Harness 2025 report page; FinOps Foundation State of FinOps 2026 page).

### 3.2 `wasteBand()` uses only two of five signals for capability

`cap = mean(visibility, control)`. Predictability, ownership, value do not influence the band. That's a deliberate simplification — visibility and control are the signals most directly tied to waste — but it's non-obvious. A customer with excellent ownership and value but weak visibility and control could reasonably ask why their band didn't move.

**Fix (choose one):** document it in the "Basis" line ("Waste band is a function of visibility and control — the two signals most directly tied to unrealised savings"), or widen `cap` to the weighted mean of all five.

### 3.3 `allocation_100` scores even when total ≠ 100

Q_O2 UI shows *"Total: X / 100 — adjust to reach 100"* but `qScore()` computes the score regardless. If the user leaves it at 80 or 120, they still get an ownership-signal contribution. The `nobody`-bucket penalty (`sc=100-nb*1.6`) is still driven by the raw `nobody` value, so a 40-in-a-total-of-80 nobody bucket scores the same as 40-in-a-total-of-100.

**Fix:** `qScore()` returns `null` (i.e., "not answered") when the allocation total is not 100, matching the UI.

### 3.4 `signal.weight` not used for signal aggregation, only for `gapIndex`

`signalScores()` produces per-signal weighted means using the per-question `signals[].w` weights. The `meta.signals[].weight` (0.22, 0.20, etc.) is *only* used by `gapIndex()` to weight signals when averaging (100 − signal) values. The report renders signals as bars with no indication of their weight; a signal with weight 0.16 (value) and weight 0.22 (visibility) render identically. A finance reader looking at signals of 60 across the board doesn't know that visibility drives the number more than value does.

**Fix:** either show the weight next to each signal bar (`Cost visibility · weight 22%`), or drop the difference — 20/22 is close enough that per-signal weighting is nearly a rounding effect.

### 3.5 `verdict_bands` narrative doesn't reference the money figure

Verdict bands narrate "material exposure" / "urgent" in generic terms. They don't reference the money box. A customer with a £200k need-index=90 gets the same "urgent — spend running substantially ahead of control" prose as one with £20m need-index=90. The Sovereign Screen and DR&J both bind the verdict prose to the customer's own answers via `shown_if` — FVC could too.

**Nice-to-have:** parametrise the verdict narrative with `£X–£Y` from `exposure()` when calculable.

---

## 4. Content / ship-blocker defects (BLOCKER before customer use)

### 4.1 All 3 case studies are `status:"placeholder"`

`meta.case_studies[]` — every entry has `status:"placeholder"` and points at `assets/case-studies/PLACEHOLDER-*.pdf`. The report renders these on the cover with a red **PLACEHOLDER PDF** chip. `dl` action toasts *"Placeholder — drop the approved PDF at …"* rather than downloading.

This is fine for internal review; **not fine for a live customer-facing tool**. The tool is deployed to prod. A prospect opening it right now sees three PLACEHOLDER PDF chips on their value case.

**Fix:** either (a) drop the case-studies section on the report until real PDFs land, or (b) source three real case-study PDFs and update the KB to `status:"published"`. Ship-blocker either way.

### 4.2 The LTM FinOps Services brochure is also placeholder

`meta.brochure` — `status:"placeholder"`, `file:"assets/PLACEHOLDER-ltm-finops-brochure.pdf"`. Same PLACEHOLDER PDF chip on the "Next step" block.

**Fix:** attach the real brochure PDF. Same posture as 4.1 — deploy blocker.

### 4.3 `urgencyIndex()` reads `growth` as unbounded and uncapped upstream

Q_E5 slider goes from `-25%` to `+200%`. `urgencyIndex()` line: `if(g>30) u += Math.min(28, (g-30)*0.22)` — capped at 28 pts. Fine as a stand-alone. But there is no floor for negative growth: a customer shrinking spend at -25% skips this branch entirely, contributing 0 (not a negative). That's correct behaviour (shrinking spend shouldn't add urgency) but should be verified against intent.

*(Not a defect — just noted for the roadmap.)*

---

## 5. Small correctness / polish items (LOW priority)

- **`clone()` uses `JSON.parse(JSON.stringify(o))`** — fine here, KB is JSON-safe. No defect.
- **`money(0)`** returns "£0" (falls through the k/m/bn branches). OK.
- **Slider `logVal` / `logPos`** — logarithmic spend slider with `Math.round(exp(...)/10000)*10000` snapping. Steps=60, min=50k, max=100m — resolution is fine (implied ~1.13x per step at the low end, ~1.13x at the high end).
- **`P1` (`slider_percent`) with `invert:true`** — score = 100 − ((v − 0)/(60 − 0))·100. Verified: v=15% → 75, v=60% → 0. Correct.
- **`E4` migration_ahead is used both in urgency and for value framing** but only urgency actually consumes it (`u += (o.migration_ahead||0) * 18`). Fine.
- **Report section numbering** (`bs.length?4:3`, `bs.length?5:4`, …) — hand-cranked numbering that shifts when blind-spots present/absent. Prone to drift if new sections are added. Consider a numbered array pattern.
- **`recommendedServices()` may return 0 items** for a very capable customer; the empty-state text (*"No service area triggered … A short validation review against billing data is still worthwhile"*) is present and honest.
- **Feedback pill + Contact Us overlay + standard disclaimer** — already applied in the P4.4 v3 overlay across all four accelerators. Confirm on the current bundle before shipping any FVC change.
- **INR is offered as a reporting currency** — `£`/`$`/`€`/`₹`. Fine, but no FX conversion — the raw spend value is treated as denominated in whatever currency is displayed. If the user enters 200,000,000 with `INR` set, that's ₹200m ≈ $2.4m — very different waste values. That's intentional (unit-consistent) but should be surfaced: **the currency selector renames the symbol; it does not convert**.

---

## 6. Proposed remediation plan (phased, staging → sign-off → prod)

Same workflow as Sovereign Screen and DR&J. Each phase to staging first, legal sign-off referencing SHA, then prod. No content changes hit prod without sign-off.

### Phase 1 — Legal defensibility (4 items)

1. **BFSI sector gate** — replace free-text sector with dropdown `{BFSI, non-BFSI}`; gate the uplift and the basis-line prose accordingly. (§2.1)
2. **Currency freeze on report render** — snapshot `S.org.currency` into the exported report state; render `Currency: £ GBP` on the cover meta block. (§2.2)
3. **Disclaimer append** — *"Indicative and directional only. Not a commitment, quote or financial advice."* (§2.3)
4. **Framework version + review-date stamp on cover** — `Framework v1.0.0 · reviewed 2026-07-22`. (§2.4)

### Phase 2 — Scoring / content correctness (3 items)

5. **Oracle Cloud → `hyper:true`** in Q_E2. (§2.5)
6. **`sources:[].url`** on all 4 benchmark sources. (§3.1)
7. **`allocation_100`** returns `null` when total ≠ 100. (§3.3)

### Phase 3 — Ship-blockers before next customer demo

8. **Replace all 3 placeholder case-study PDFs** (or drop the section pending). (§4.1)
9. **Replace placeholder brochure PDF** (or drop). (§4.2)

### Phase 4 — Ongoing hygiene

10. **Add FVC to `REFRESH-CADENCE.md`** with the same 1 Feb / 1 May / 1 Aug / 1 Nov cadence. Add benchmark-refresh trigger: any new Flexera State of the Cloud release.
11. **Customer-facing changelog page** (`finops-value-case-changelog.html`), mirroring the DR&J and Sovereign Screen pattern.
12. **`ragForRegulation`-equivalent** — verify the report handles the "very few questions answered" case cleanly. (Confidence text does already downgrade to "Low confidence" when `answered<12`; verified in `confidence()`.)

Nice-to-have (defer to Phase 5 or drop):

- Widen `wasteBand` capability to a weighted mean of all 5 signals (§3.2).
- Parametrise verdict narratives with the money figure (§3.5).
- Surface signal weights on the report bars (§3.4).
- FX conversion on currency change (behaviour clarification, §5).

---

## 7. Not-financial-advice risk assessment

**Medium.** The tool outputs money ranges in an LTM-branded PDF. The current disclaimer language *"not a guarantee of savings"* is honest but incomplete for a Finance audience. Phase 1 items 2 (currency freeze), 3 (disclaimer) and 4 (framework stamp) collectively bring this to **Low**. Phase 1 item 1 (BFSI gate) closes the *"you told my Retail company I have BFSI waste factors"* argument.

Post-Phase 3, this tool is defensible to hand to a UK/EU customer.

---

## 8. Comparison to Sovereign Screen and DR&J (post-Phase 4)

| Feature | Sovereign Screen v1.3.0 | DR&J v1.3.0 | **FVC v1.0.0** |
|---|---|---|---|
| Framework version on cover | ✅ | ✅ | ❌ |
| Reviewed-date on cover | ✅ | ✅ | ❌ |
| Currency stamp on cover | n/a | n/a | ❌ |
| Sources with URLs | ✅ (89 URLs across 16 regimes) | ✅ (32 URLs across 10 regulations) | ❌ (4 sources, no URLs) |
| Standard disclaimer overlay | ✅ | ✅ | ✅ |
| Contact Us right-rail tab | ✅ | ✅ | ✅ |
| Feedback pill (mailto) | ✅ | ✅ | ✅ |
| Customer-facing changelog | ✅ | ✅ | ❌ |
| Quarterly refresh entry | ✅ | ✅ | ❌ |
| Placeholder assets | none | none | **3 case studies + 1 brochure** |
| "Not legal advice" / "not financial advice" | ✅ | ✅ | ⚠ *("not a guarantee of savings" only)* |
| Sector gating | n/a (finance-only tool) | free text | **free text with unconditional BFSI uplift** |

---

## Appendix A — Question inventory (29)

| ID | Section | Format | Signals | DK | Question (abbrev.) |
|---|---|---|---|---|---|
| E1 | estate | card_select | — | | Infrastructure today |
| E2 | estate | multi_select_logo | — | | Cloud platforms |
| E3 | estate | slider_currency | — | ✓ | Annual cloud spend |
| E4 | estate | single_select | — | | Cloud journey stage |
| E5 | estate | slider_signed | — | | 12-mo spend change |
| E6 | estate | slider_percent | — | | Remaining migration % |
| V1 | visibility | single_select | visibility ×2 | ✓ | Cost attribution capability |
| V2 | visibility | slider_percent | visibility ×1.5 | ✓ | Tag coverage |
| V3 | visibility | single_select | visibility ×1.5 | | Time-to-answer "why up?" |
| V4 | visibility | boolean_dk | visibility ×1, value ×1 | ✓ | Cost per unit known? |
| V5 | visibility | multi_select | visibility ×1.5 | | Regular scheduled reports |
| P1 | predictability | slider_percent (invert) | predictability ×2 | ✓ | Actual vs budget variance |
| P2 | predictability | single_select | predictability ×1.5 | | Unexpected bill explanations |
| P3 | predictability | rating_1_5 | predictability ×1.5 | | Forecast confidence |
| P4 | predictability | single_select | predictability ×1, ownership ×1 | | Who explains the bill |
| O1 | ownership | single_select | ownership ×2 | | Formal accountability |
| O2 | ownership | allocation_100 | ownership ×2 | | Where responsibility sits |
| O3 | ownership | rating_1_5 | ownership ×1.5 | | Engineer cost-awareness |
| O4 | ownership | boolean_dk | ownership ×1 | ✓ | Cost in objectives |
| C1 | controls | multi_select | control ×2 | | Cost controls in live use |
| C2 | controls | slider_percent | control ×1.5 | ✓ | Commitment coverage |
| C3 | controls | single_select | control ×1.5 | | Last systematic decomm |
| C4 | controls | drag_order | — | | Concern ranking (concern_map) |
| L1 | value | single_select | value ×2 | | Board-level value demo |
| L2 | value | single_select | value ×1.5 | ✓ | Business case realised |
| L3 | value | rating_1_5 | value ×1 | | Comfort answering Finance |
| L4 | value | multi_select | — | | Good outcome in 12 months |
| X1 | value | open_text | — | | Additional notes |

**Total scoring questions:** 24 of 29 (E1–E6 estate-shape only feed calculation, not signals; C4 drives service ordering; L4 shapes recommendations; X1 free text).

---

## Appendix B — Files touched by this review

- Read: `finops-value-case/FinOps Value Case (LTM).html`
- Read: `docs/ACCELERATOR-REVIEW.md` (prior surface review)
- Read: `docs/DR-J-REVIEW.md` (for structural parity)
- Written: `docs/FVC-REVIEW.md` (this file)
- **No** patch scripts written yet — remediation phases in §6 will be scripted after user approval, same workflow as Sovereign Screen / DR&J.
