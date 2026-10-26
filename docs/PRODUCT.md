# Product blueprint · Cautum Credit

## North star
**Make healthcare receivables legible, comparable and monitorable to the capital providers who finance them.** Position as independent lender-side credit policy and portfolio surveillance infrastructure, rather than a provider-facing cash advance calculator. Business-level technology outcome: faster first-pass reviews, fewer spreadsheet reconciliation errors, earlier detection of collateral deterioration; each must be proved in pilots.

## Customer and buyer
Primary: specialty healthcare asset-based lenders, private-credit funds with provider-receivables exposure, bank specialty lending teams and portfolio managers. Roles: analyst imports A/R roll-forward, underwriter defines approved eligibility policy, PM watches exceptions, risk approver documents review. Secondary counterpart: provider CFO / RCM team who exports an aggregated schedule, not patient records.

## Jobs to be done
1. Normalize a messy but properly sanitized provider aging/payer export.
2. Explain where gross A/R disappears during collectibility and eligibility analysis.
3. Calculate borrower borrowing-base availability under a known version of lender policy.
4. Compare exposure across providers, payers, vintages and periodic snapshots.
5. Surface material collateral-policy breaches with source evidence.
6. Generate a memo that distinguishes facts, assumptions, unresolved questions and approvals.

## Wedge
`Upload → reconcile → apply policy → explain base → surface exceptions → committee brief`. Initially export-only, no claims integration. Designed for **lenders with multiple borrowers**, unlike a generic clinic receivables dashboard. The defensible moat is not an LLM prompt; it may become workflow integration, vetted payer-specific recovery histories, transparent policy-as-code, adjudication-to-remittance provenance and proprietary performance feedback data obtained with consent.

## Pilot acceptance
One authorized lender analyst can import a **synthetic or independently confirmed non-PHI aggregate** sample, find a discrepancy, reproduce exact calculations and review an exception with minimal intervention. True success requires independent comparison to their reference spreadsheet, agreement on a policy convention, reproducible results and an improvement demonstrated by observation.

## Business model hypotheses (NOT validated)
- Lender B2B platform subscription, tiered by portfolios/borrrowers reviewed or monitored.
- One-time implementation/data mapping and migration services.
- Optional enterprise controls and data feeds later.
Not factoring, not borrower origination fees, not selling patient data, and not charging a share of funded loans in this v0.1.

## Long-term mission
More accurate, transparent collateral assessment **may** help lenders price/structure capital and providers keep services available; do not imply measurable health access impact without a causally credible study. The eventual capital-markets path (portfolio aggregation, institutional credit, securitization-like infrastructure) depends on collateral legal feasibility, performance, financing counterparties, data rights and regulation.

## What NOT to build first
Fancy conversation sidebar, generic AI chatbot, live EHR integrations, directly initiating loans, yield predictions from uncalibrated data, automated credit approval, Medicare receivables purchases, patient dashboards, gamified badges, blockchain-based claims ownership, paper-only pitch with fabricated traction.

## Killer demo in 90 seconds
1. Load eight fictional borrowers. Show gross-to-base waterfall.
2. Select the high-attention borrower and inspect triggers.
3. Change advance rate 80% → 70% and show exact base sensitivity with constant eligible collateral.
4. Download trace CSV.
5. Generate deterministic credit brief; optionally real structured AI risk commentary with token usage, if a tested key exists.
6. Show a failed upload containing patient_name or hostile formula as evidence of safety.

## v0.4 workflow expansion

A reviewer can now start with “what changed between these two schedules?” and reconstruct the answer in Change Desk. The wedge extends to explicit same-policy variance explanation and a source-backed handoff packet. Constructed cases make the job understandable to a clinic finance operator and a lender: more receivables with less modeled backing, a changed denial input, or a deliberately mapped payer rename. The current kit makes independent review possible without founder coaching; no such independent review has occurred.
