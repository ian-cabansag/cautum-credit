# Product roadmap · credible ambition, controlled sequencing

## Now: v0.1 · Proof of mechanism
**Already included in repo:** one-process UI, synthetic cohorts, strict CSV, policy factors, Decimal arithmetic, portfolio metrics, exceptions, audit trace, what-if inputs, offline memo, optional structured AI, API/test suite.
**Not yet proven:** model vendor integration using a real key, product-market fit, security review, lender-grade accuracy, commercial dataset ingestion, ROI, paid demand.

## Gate 1: v0.2 · Reconciliation and evidence
1. Give the user a column mapping wizard for many **permitted aggregate-only** export formats, with strict allowlist and no hidden data collection.
2. Build an explicit bridge: billed charges → estimated allowed → collectible → reserves → legal eligibility → net borrowing base. Clarify discount dependencies.
3. Separate administrative eligibility from financeability/legal review statuses rather than labeling all haircut-adjusted balances 'eligible.'
4. Make policy parameters versioned and diffable; test deterministic golden portfolios and exact cent reconciliation.
5. Add reconciliation against synthetic payment remittances and time-series cohort history.
6. Add safe reproducible exports and a browser-visible calculation formula explorer.
7. Review interface with 2–3 practicing lenders to identify blockers; collect measured, honest feedback.

## Gate 2: v0.3 · Lender pilot
1. Define mutually approved non-PHI data contract and data dictionary; document permission and legal classification.
2. Configurable lender rules for exclusions, disputed claims, debtor concentrations, borrower/obligor limits, reserves, netting, dilution and outstandings.
3. Per-borrower borrowing base certificates and rolling month-over-month watchlists.
4. Signed approvals, exceptions with evidence, analyst ownership and immutable event audit trail.
5. Fine-grained provider/borrower/payer data lineage and quality score that reveals missingness rather than masking it.
6. Evidence-driven calibration on historical outcomes to eliminate double counting; account for uncertainty, off-balance exposures and policy changes.
7. Pilot review of borrower-level or permitted aggregate data with lender and healthcare counsel.

## Gate 3: v1.0 · Enterprise deployment
**Only after security/privacy and finance counsel gates**: organization identity, RBAC, tenant isolation, safe file ingest, data retention, encryption, model gateway and policy guardrails, approved BAAs if applicable, signed provenance, monitoring and on-call security response. Deploy on privacy-appropriate infrastructure; do not use bare FastAPI public demo for real data.

## Gate 4: v2+ · Network and structured finance hypothesis
Consent-based cross-lender credit 'passport' of provider receivable portfolios; standards for evidence/eligibility; collateral and covenant monitoring; independently verified cash realization curves; data sharing agreements; portfolio aggregation and warehouse reporting. Examine whether broad market demand can sustain lender SaaS. **Securitization, CLO-like structures or direct financing remain remote options**, not MVP features. They require specialized securities, banking, healthcare, licensing, assignment, custody and servicing counsel and real institutional counterparties.

## 90-day founder discipline (relative periods, not promises)
Weeks 1–2: run UI acceptance test, 10 buyer conversations, document painful steps.
Weeks 3–4: instrument workflow timings; build 2 lender-specific golden datasets; reject weak features.
Weeks 5–8: land one permissions-cleared design partnership with specified accuracy outcomes.
Weeks 9–12: deliver one working monthly certificate / exception review, evaluate willingness to pay and security gate.

## Metrics worth tracking
Buyer discovery conversion; active reviewers per lender; import success without engineer; percentage of line items reconciled; minutes to first reliable borrowing base; analyst override frequency; incident rate; alerts confirmed; paid retention; legal/compliance costs; model error and token spend. Do **not** cite hallucinated AUM, ARR, financing volume or patient access impact.

## 2026-10-25 status correction after sequenced development
The v0.1 “now” list above is the supplied historical baseline. Local v0.2 technical additions now include cohort-cent reconciliation, complete factor evidence, content-based policy IDs/diffs, constrained alias preview, scoped certificates and two-period synthetic comparison. Policy approvals are not authenticated or immutable; aliases do not constitute general commercial ETL; snapshots do not reconcile remittances. Optional AI now selects bounded existing evidence with deterministic wording and still has no verified live integration.

External Gate 1 lender review, data rights, independent calibration and remittance reconciliation remain open. Gate 2 design partnership and all enterprise/security/legal gates remain open. No objective customer evidence supports advancing these gates. Next commercial experiment is the narrow synthetic review described in COMMERCIAL_VALIDATION.md, with permission and actual measurement before any price/ROI claim.

## Current v0.4 checkpoint

Live Portkey and token evidence was completed in v0.3; the earlier no-live-AI statement is historical. v0.4 adds Change Desk, bounded constructed-pair uploads, exact fixed-order variance contributions, paired original sources, source-owner questions, server-generated packets and three relatable worked cases. An offline reviewer kit is ready. These engineering steps do not close independent lender, commercial, data-rights or enterprise gates. The founder currently has no independent tester available. See IMPACT_LEDGER.md for measured versus unmeasured value.
