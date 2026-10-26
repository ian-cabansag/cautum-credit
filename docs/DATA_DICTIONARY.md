# Aggregate data contract and formula glossary · v0.2

Synthetic cohorts only in this local prototype. A permitted aggregate-only export still needs independent privacy/data-rights review before commercial use. No automatic de-identification claim. Missing, ambiguous and extra fields fail closed.

| Input | Unit / denominator | Contract |
|---|---|---|
| provider | organizational borrower label | 2–70 permitted characters; consistent exact spelling; no patient labels |
| payer | organizational payer label | one consistent label and payer taxonomy; no identifiers |
| payer_type | enumeration | Commercial / Medicare / Medicaid only; do not infer from name |
| aging_bucket | days since an agreed but currently unspecified aging origin | 0-30 / 31-60 / 61-90 / 91+; aging-origin convention needs lender agreement |
| gross_ar | USD billed cohort balance | finite, nonnegative, ≤6 decimals; portfolio gross >0 and ≤$1T; not verified collectible cash |
| contractual_adjustment_rate | reduction / gross billed amount | [0,1], ≤6 decimals; not a percentage string |
| historical_collection_factor | realization / allowed amount before modeled denial haircut | [0,1], ≤6 decimals; assumed independent of denial loss |
| denial_rate | independent modeled loss / pre-denial modeled realization | [0,1], ≤6 decimals; source definition must be reconciled; not confirmed denied dollars |

One row per provider/payer/aging cohort, duplicate matching ignores case. Labels differing only by case are rejected rather than split into different entities. A payer cannot have conflicting payer_type values. Maximum 2,500 rows / 2,000,000 file bytes. USD only. No FX or mixed-currency support.

## Formula and rounding
N = G × (1 − contractual adjustment). E = N × collection × (1 − denial). C = E × aging × payer. B = C × advance.

N: modeled allowed. E: modeled collectible, not validated recoveries. C: policy-adjusted collateral, historically named eligible_collateral in the API; it does not establish legal eligibility. B: illustrative base before unmodeled reserves and outstandings, not net undrawn availability or approved funding.

Engine v0.2 computes each stage independently from the full-precision input chain in a 64-digit Decimal context. Each cohort stage is rounded ROUND_HALF_UP to cents. Portfolio, borrower, payer and aging monetary views sum those cohort cents. It does **not** feed rounded N into E or round only the aggregate. This deliberately changes some displayed v0.1 totals. Difference from unrounded stage is explicit in each trace row. Sub-cent gross is preserved in inputs_exact; weighted rates use original gross. Monetary stage reductions use displayed cent amounts so the bridge reconciles exactly. A lender must approve this convention before any real use.

Audit supplies original input strings, every applied multiplier, unrounded stage amounts, cent adjustments, cohort ID, formula, engine version and policy ID. JSON amounts_exact / summary_exact preserve monetary strings. Existing numeric fields remain for frontend compatibility; sum exact monetary strings in downstream reconciliation.

Policy ID hashes canonical exact parameter strings. Analysis ID hashes canonical input evidence, policy and engine version; input order and equivalent Decimal formatting do not change it. IDs are reproducible checksums, not signatures or immutable audit storage. An engine version change intentionally changes the ID. No policy approval workflow is implemented.

## Review flags
Denial = gross-weighted input denial rate; aging = original 91+ gross / original gross; concentration = largest payer original gross / original gross; advanceability = summed rounded base / original gross. Comparisons use full Decimal rates (strict > or <, not rounded display rates). Trace supplies observed_exact, threshold_exact, comparator and source cohort IDs. Review status counts rule breaches; it is not a risk grade or default score.

## Unassessed gates
Legal eligibility: unreviewed. Reserves: not modeled. Outstandings: not supplied. Net availability: null. Approval: to review, no authenticated sign-off. No value of zero is substituted for missing reserves, debt or legal exclusions. Denial/collection independence is unvalidated and may double count loss. No recovery calibration or credit authority is implied.

## Explicit alias mapping
The import review accepts these exact aliases, in any order, only when all eight semantic fields are present exactly once: borrower→provider, payer_name→payer, payer_class→payer_type, age_band→aging_bucket, billed_ar_usd→gross_ar, contract_adjustment→contractual_adjustment_rate, collection_factor_pre_denial→historical_collection_factor, modeled_denial_rate→denial_rate. Canonical headers also work. Ambiguous collection_rate and extra columns are rejected; no arbitrary user mapping can relabel a monetary column as a rate. Local preview displays only whitelisted headers, cohort count and exact gross; it does not echo organizational labels. Confirmation sends the original synthetic file and explicit mapping to the local server, which independently revalidates it. Import evidence records source-byte SHA-256, byte length and mapping, without storing raw bytes. Analysis ID identifies normalized economics; import source hash distinguishes file representations. Accepted rows are all-or-nothing; the first invalid logical CSV record reports its row number. This is a bounded alias review, not a general spreadsheet ETL tool.

## v0.4 comparison evidence

Change Desk adds a review ID binding method version, before/after analysis IDs, snapshot hashes and policy ID. Each contribution uses the original full Decimal chain at a fixed counterfactual step and then cohort HALF_UP cents. Balance, contract adjustment, collection and denial replace in that order; later inputs receive interaction effects. Added/removed cohorts are separate. Original identities, input strings, factors, stage amounts, formulas and questions remain in the exported source pair. The review ID is a checksum, not approval evidence. See CHANGE_DESK.md; no causal loss, actual migration, cash collection, net availability or legal eligibility is inferred.
