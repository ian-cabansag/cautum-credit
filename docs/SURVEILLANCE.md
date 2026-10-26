# Synthetic surveillance contract · 2026-10-25

Bundled synthetic T0 (fictional 2026-08-31) and T1 (fictional 2026-09-30) are regenerated with `python -m scripts.generate_snapshots`. T0 uses the starter portfolio. T1 decreases non-91+ balances by 3%, increases 91+ balances by 8%, and adds 2 percentage points of modeled denial rate to Meridian. These are fixture construction rules, not empirical recovery or deterioration estimates.

Each manifest includes snapshot ID, one reporting date, revision, explicit stable borrower/payer IDs and source description. Imported-at is null because these are bundled fixtures, not historical client uploads. Source hashes and snapshot hashes preserve lineage; no signed archive or persistent time series exists. Current applied policy is used for both snapshots. API comparison rejects differing policy IDs, non-ordered/same-period dates, mixed-date manifests, unmapped renames, identity duplicates and payer taxonomy changes. Restated revisions are explicitly flagged. Source CSV cannot include row-level reporting dates or extra fields under the aggregate contract.

Matching uses explicit borrower ID + payer ID + aging bucket. An unmapped renamed payer fails; a deliberate rename sharing an explicit stable ID is marked. Labels are never fuzzily merged. Cohort balance movement is not proof of aging migration or cash receipts. Added/removed cohorts are separately classified, not silently treated as paid. Opening + continuing deltas + added + removed = closing, independently for gross and illustrative base. Monetary deltas use exact cohort cents. Ratio deltas use six-decimal displayed summary ratios. Headroom is null because debt outstandings/reserves are absent.

Actual bundled comparison: gross $1,934,634.00 → $1,900,103.63, delta −$34,530.37; illustrative base $761,801.19 → $737,495.10, delta −$24,306.09. No user impact or actual collections inferred.

This study is separate from imported portfolio analysis. Production multi-snapshot imports, remittance reconciliation, restatement approvals, historical identity governance and policy-change decomposition remain future work.

## Current v0.4 extension

The earlier fixture-only statement is historical. Change Desk now accepts bounded constructed snapshot pairs with explicit strict identity manifests, same-policy enforcement and ordered dates. It adds exact fixed-order model-driver attribution, borrower queues, source-pair inspection and server-generated evidence packets. Three small relatable examples and all original sources are included. See CHANGE_DESK.md for the precise method, input limits and non-causal interpretation. No operational client data, remittance reconciliation, policy-change decomposition or authenticated approvals are introduced.
