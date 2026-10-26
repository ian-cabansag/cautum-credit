# Change Desk · v0.4

Purpose: help a lender reviewer reconstruct a periodic change from accepted aggregate source evidence. The previous view reconciled total balances but left the reviewer to reconstruct input effects elsewhere. This view provides dollar contributions, a borrower queue, paired original inputs, counterfactual steps, source-owner questions and a server-generated standalone evidence packet.

## Three relatable constructed examples

| Example | Source change | Default-policy result | Question to investigate |
|---|---|---|---|
| Community clinic: more receivables, less modeled backing | Gross $100,000 → $120,000; 0–30 balance $80,000 → $60,000; 91+ $20,000 → $60,000 | Base $43,776 → $32,832; **−$10,944** | Which balance buckets changed? Do not infer migration of individual claims or collections. |
| Imaging practice: same billing, changed denial assumption | Gross $100,000 unchanged; denial input 5% → 15% | Base $54,720 → $48,960; **−$5,760** | What supports the changed rate, and does the collection factor already contain that loss? |
| Therapy group: explicitly mapped payer rename | $50,000 unchanged; new payer label, same stable payer ID | Base **$27,360 unchanged** | Verify identity continuity; never infer it from similar names. |

These are fictional examples constructed to explain a workflow, not customer stories or observed financial impact. All factors are the existing unvalidated illustrative policy. The raw CSVs and identity manifests can be downloaded from each example. Changing policy recomputes both periods and changes the dollar answers.

## Attribution contract

Continuing identities match explicit borrower ID + payer ID + age bucket. Both snapshots must use one policy and ordered, distinct reporting dates. Taxonomy changes and duplicate identities reject. Same-period restatements are not period movements. Mapped renames preserve continuity; unmatched identities remain additions/removals, not paid or aged claims.

For each continuing cohort, start with its opening original input chain. Replace gross, contract adjustment, collection and denial inputs in that fixed order. Calculate the full Decimal chain at each step and round that cohort's base HALF_UP to cents. The difference between adjacent rounded counterfactual values is the factor contribution. Additions/removals contribute their entire closing/negative opening base separately. Sum cohort cents by borrower and portfolio. Every level must reconcile; otherwise the comparison rejects.

This is **order-dependent model attribution**, not Shapley attribution, causal explanation, measured losses, cash reconciliation or legal collateral assessment. Interaction effects belong to the later input. Zero unexplained model delta confirms arithmetic only. No new risk prediction or lender-standard policy factor was introduced.

## Input and export boundaries

POST /api/surveillance defaults to bundled fixtures. Named example IDs select only the fixed constructed cases. To upload a pair, supply opening/closing CSVs, both strict JSON identity manifests and synthetic=true. Partial pairs, mixed example/upload requests, duplicate/extra manifest keys, invalid dates, unknown CSV fields, taxonomy conflicts and unacknowledged synthetic scope reject. Manifests are limited to 32 KiB each; the existing whole-request cap applies; combined source rows are limited to 2,500. No fuzzy identity inference. Raw bytes are read in memory and not intentionally persisted or sent to AI.

The UI retains the last accepted comparison and its export sources after failure. Search and materiality filter the queue; exports explicitly use the full comparison or selected borrower. HTML packets are recalculated by the server from validated sources, not accepted client monetary amounts. Packets include original inputs, formulas, driver steps, source SHA-256, snapshot/analysis/policy/review IDs and open diligence questions. No authenticated sign-off, write tool or lending action exists.

## Evidence and interpretation

Independent golden arithmetic and 64 seeded one-cohort paired cases use an exact Fraction calculator to check the Decimal implementation. The bundled 192-identity change is −$24,306.09: balance contribution −$22,854.10 and denial-assumption contribution −$1,451.99. These are software/calculation results, not a user's time saved or a clinic's recovered cash.

The founder has no independent tester available at this checkpoint. The earlier founder observation remains unchanged and predates this feature. The reviewer kit prepares future uncoached observations; it contains no invented participants or results.

## Primary workflow grounding

The OCC's Asset-Based Lending handbook (v1.1 with March 2025 updates) describes close collateral monitoring and reconciliation in ABL. This supports investigating the workflow; it does not validate Cautum, its factor assumptions or a healthcare transaction. Source: https://www.occ.gov/publications-and-resources/publications/comptrollers-handbook/files/asset-based-lending/pub-ch-asset-based-lending.pdf . Accessed October 25, 2026.

Forbes' own methodology emphasizes achievements, scale, inventiveness and impact, and states there is no guaranteed route to selection. A better prototype is not proof of those commercial outcomes. Source: https://www.forbes.com/sites/zoyahasan/2025/12/02/how-we-make-the-forbes-under-30-list/ . Accessed October 25, 2026. No nomination, award eligibility or endorsement is claimed.
