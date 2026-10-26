# The underwriting policy, version 0.1 (illustrative only)

These inputs originated as educational prototype assumptions, not from a lender credit manual, proprietary payer performance dataset, or a professional valuation standard.

| Parameter | Demonstration value |
|---|---:|
| Advance rate | 80% |
| 0–30 day aging factor | 100% |
| 31–60 aging factor | 95% |
| 61–90 aging factor | 80% |
| 91+ aging factor | 0% |
| Commercial payer factor | 100% |
| Medicare payer factor | 90% |
| Medicaid payer factor | 80% |
| Weighted denial alert | >9% |
| 91+ gross A/R alert | >12.2% |
| Top payer gross concentration alert | >21.5% |
| Borrowing base / gross A/R alert | <45% |

For row `i`:

```text
N_i = G_i × (1 − contract_adj_i)
E_i = N_i × historical_collection_factor_i × (1 − denial_rate_i)
C_i = E_i × aging_factor_i × payer_factor_i
B_i = C_i × advance_rate
```

`N`: synthetic net allowed, `E`: illustrative expected collectible, `C`: illustrative risk-adjusted eligible collateral, `B`: illustrative borrowing base. The values are not independently verified collections or legally enforceable collateral. A/R can include nonmonetary valuation distortions, aged or unbilled balances, recoupments, contractual carveouts, offsets and other disputes.

### Particularly important danger: double counting
If `historical_collection_factor` is a realized historical collection rate that **already includes denied/unpaid claims**, multiply-by-(1−denial) double penalizes the same loss. Before a real pilot, define all numerators/denominators explicitly, backtest with remittance history, separate authorization/initial denial/final denial and appeal recoveries, and use an empirically fitted collection model (with uncertainty bands) if justified. NEVER claim the example 80% represents how a real healthcare lender advances.

### Why no formal 'risk score'
No validated default probabilities, historical actual collections, recovery labels, borrower financial statements, cash controls, liens, covenants or legal assignments are in v0.1. Therefore a 'credit score' would be marketing, not science. Current product has literal rule breaches and 'Within policy / Watch / High attention' as a **review queue**, not credit grades.

### Legal eligibility gate not implemented
Borrowing-base eligibility is not the same as right to pledge, purchase, assign, collect, enforce, or redirect payer funds. Commercial, Medicare, Medicaid and managed plan arrangements have distinct program/contract restrictions, and security-interest laws do not automatically confer payer enforcement rights. In particular, CMS manual guidance restricts Medicare receivable purchases and sets rules for payment-to-bank structures. Retain specialist lender/healthcare counsel before any live arrangement. Sources: https://www.cms.gov/Regulations-and-Guidance/Guidance/Transmittals/Downloads/R213CP.pdf ; https://www.law.cornell.edu/ucc/9/9-408 ; https://www.duanemorris.com/articles/health_care_finance_transactions_security_interests_commercial_governmental_receivables_0117.html

### Questions for an experienced credit officer
- What exactly is eligible (billed/unbilled, aged, disputed, government payers, self-pay, appeals, recoupments)?
- What reserves/limits, holdbacks, concentration and dilution blocks apply, and at which hierarchical level?
- What is the waterfall from billed charges to allowed amounts to actual collectible cash?
- How does lender consent/documentation/legal enforceability change by program and geography?
- How are initial/final denials, appeals, cash receipts and contractual allowances separately captured?
- Who approves exceptions? How are overrides and policy effective dates controlled?

## v0.2 engineering convention (2026-10-25)
The original economic assumptions above remain illustrative. Cohort stages now round independently HALF_UP to cents before aggregation, with exact inputs, unrounded stages and explicit adjustments retained. See DATA_DICTIONARY.md. Summary includes net allowed and the complete gross-to-base bridge. Policy content has a reproducible ID, separate from its editable descriptive name. Legal eligibility, reserves, outstandings and net availability are explicitly unassessed. No policy factor has been calibrated or lender-approved by this change.
