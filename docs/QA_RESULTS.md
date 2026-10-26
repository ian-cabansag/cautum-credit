# QA results · 2026-10-25

## Prompt 1 · runtime and interactions
Python 3.12 virtual environment, real loopback Uvicorn, actual IAB browser, no intercepted network responses.

- After focused fixes, `.venv/bin/python -m pytest -q`: **23 passed, 1 warning in 0.21s**. Existing 21 tests preserved. Added public asset/docs routes and invalid mode, missing file, extension, malformed policy and complete flagged-provider count.
- Browser confirms failed upload retains SYNTHETIC DATA, old accepted analysis and policy, with explicit `Last accepted analysis retained` status. Invalid input is not used by later memo requests.
- Offline brief succeeds after rejected upload, reports 8 flagged providers with first 4 named. Copy produced real clipboard text and Save JSON generated a download. AI button disabled when no configured provider.
- Earlier baseline run confirmed navigation, borrower keyboard selection/search, advance 80→70/reset, audit/analysis downloads. Accepted template upload exercised after repairs. No console warn/error entries in baseline.
- Controls lock during calculations/memos; source file and policy commit only after successful backend response. New analysis clears old memo attribution. Unmatched search now has visible empty state.
- Remaining: full responsive and contrast checks in Prompt 3, exact trace reconciliation in Prompt 2. No live AI invocation or commercial-data validation.

The starter remains the same FastAPI + static frontend architecture. No public deployment, external messages, financing actions or real patient data.

## Prompt 2 · financial evidence
- `.venv/bin/python -m pytest -q`: **34 passed, 1 warning in 0.29s**. Independent 1000→800→648→615.60→492.48 golden case; half-cent rounding; full-loss/zero/$1T cases; canonical policy/hash equivalence; 60 seeded portfolios with independent 80-digit Decimal reference, sensitivity, monotonic bridge and exact aggregation; label/taxonomy conflicts and upload bounds.
- Live browser shows 1,934,634.00→1,298,648.31→1,158,846.52→952,251.44→761,801.19 bridge. Selected Atlantic/Aetna/0–30 cohort reveals all original rates, factor multipliers, formula, IDs, reasons and rounding details. Browser error/warn log query empty.
- Initial new equivalence test failed because unrounded Decimal strings retained trailing zeroes. Canonical serialization fixed it before commit; equivalent values and reordered rows now hash identically.
- New cent convention changes expected/collateral aggregates relative to v0.1; no change to modeled economic factors. Legacy baseline response remains preserved for comparison. See DATA_DICTIONARY.md.

## Prompt 3 · interface refinement
- Reduced decorative hero to a concise operating note; put calculation bridge ahead of charts; clarified modeled/illustrative labels. Added readable small-screen navigation, skip link, focus/current-page state, stronger text contrast, reduced-motion and forced-color CSS support, and explicit session-date/source-vintage distinction.
- Real browser visited **all four screens at 1440, 1024, 768 and 390px** (16 measured combinations). Every document scrollWidth equaled viewport width. Tables intentionally scroll within their containers. Desktop and 390px screenshots inspected; overview screenshots saved at all four sizes in docs/evidence/overview-*.jpg.
- `.venv/bin/python -m pytest -q`: **34 passed, 1 warning in 0.31s**. No numerical changes in this phase. Formula selection/browser evidence verified in Prompt 2; full interaction regression repeated at release. Forced-color and screen-reader assistive technology support is implemented but not certified or tested with actual assistive software.

## Prompt 4 · aggregate import review
- **41 passed, 1 warning in 0.30s**. Alias/order equivalence tested through parser and HTTP, plus incomplete/semantically invalid mappings, unknown columns and ambiguous denominators. Existing malicious/PHI-marker/size/duplicate/null/rate tests retained. Formula-prefix organization labels now rejected even for +/− prefixes.
- Actual 390px browser preview of reordered safe aliases showed 2 cohorts, exact $150,000 gross and all eight field meanings before upload. Confirmation produced gross 150,000.00 → allowed 112,500.00 → collectible 101,887.50 → policy-adjusted 100,248.75 → illustrative base 80,199.00. Memo generation exercised with accepted mapping. No live/non-synthetic files used.
- Scope is deliberately documented safe aliases; no inferred payer class or historical-rate denominator, arbitrary column dropping, PHI detection claim or integration success claim. Failures report the first invalid logical row, not a persisted error-file store.

## Prompt 5 · lender review and certificate
- **43 passed, 1 warning in 0.35s**. Certificate tests verify borrower-scoped cent totals, pending legal/reserve/outstanding decisions, invalid borrower rejection, HTTP download and HTML escaping.
- Actual browser filtered to High attention, sorted by denial rate, selected Meridian by Enter, scoped trace to its 24/192 cohorts and opened exception-linked original calculation evidence. Certificate download succeeded from a fresh server calculation of accepted input/policy, rather than client-supplied monetary totals.
- Ledger search/status/sort operate together; selected trace export scope is explicit. HTML certificate includes policy/analysis/engine IDs, full cohort cents, exact policy and exception ratios. Reporting vintage remains not supplied. Approval/owner/counsel fields are TO REVIEW, unauthenticated. No outstandings or reserves are silently treated as zero.

## Prompt 6 · AI boundary
**56 passed, 1 warning in 0.73s**; mocked tests only. See AI_EVALUATION.md for exact conditional scope, rejected outputs, read-only boundary, telemetry and pricing semantics. Live model/gateway tests remain unverified. No tool-calling agent added without justification or evaluation.

## Prompt 7 · two fictional periods
- **61 passed, 1 warning in 0.79s**. Added reproducibility, exact bridges, added/removed cohorts, explicit/unmapped payer renames, mixed/same dates, policy mismatch, restated revisions and HTTP contract cases.
- Real browser confirmed gross change −34,530.37 and illustrative base change −24,306.09; observed synthetic aging/denial deltas displayed with provenance. Mobile 390px document width 390. Study JSON download succeeded. No headroom, cash receipts or live-trend claims.

## Prompt 8–9 · demonstration and artifacts
Real screenshots and 30 engine / 20 loopback HTTP benchmark measurements are recorded in DEMO.md and evidence/benchmark.json. Nine reveal.js slides passed actual arrow-key traversal and viewport-content checks. Report has 12 bounded browser sections and embedded images. Exact native browser print pagination remains a manual check, as documented in COURSE_EVIDENCE.md. No live-model or user-impact evidence invented. Tests remain **61 passed** at this checkpoint.

## Prompt 10 · architecture review
RFC_001_PREPILOT_ARCHITECTURE.md records prioritized technical, privacy/data-rights, healthcare reimbursement, UCC/contract/cash-control, governance and operational blockers. Primary HHS/eCFR/UCC materials reviewed October 25, 2026. No transaction-specific legal conclusion. Concrete multipart-spooling and localhost cross-origin gaps identified for Prompt 12 remediation. No enterprise platform or real-data deployment attempted.

## Prompt 11 · commercial validation
COMMERCIAL_VALIDATION.md contains 15 explicitly hypothetical rejection reasons across credit committee, provider CFO and procurement, each paired with a measurable experiment. Proposed ICP and scoped paid design partnership are hypotheses with price and pipeline unclaimed. VALIDATION/ROADMAP distinguish shipped technical proof from still-open external gates. No customer interviews or outreach fabricated or sent.

## Prompt 12 · final release review
- Final working and clean-clone suites: **66 passed**, one recorded Starlette TestClient deprecation warning. Clean clone run 1.22s. Ruff check + format, pip check and deterministic dataset/artifact regeneration passed; generation left no Git diff. Fresh locked dependency install succeeded in a separate venv.
- Real clean-clone server at port 8002 returned verified routes, exact analysis/sensitivity, deterministic memo, scoped certificate and study. Cross-origin and Host rejections confirmed over actual HTTP. Missing-key AI returned explicit 503; no upstream request. JSON evidence: clean-clone-run.json.
- All five screens checked at four required widths (20 measurements), no horizontal page overflow. Final browser verified accepted/rejected/canceled imports, complete slider changes and reset, filters/sorting, native Enter borrower selection, scope reset on new source, downloads, clipboard, template and real Swagger reference. Console error/warn logs empty.
- A real final slider pass exposed 12.3% binary floating residue causing strict policy rejection. rates.js normalization fixed it; standalone check verifies **610** slider positions and invalid cases. Final combined scenario applied every changed rate successfully.
- Actual downloaded Meridian trace has 24 rows summing $66,889.51, identical to scoped certificate. All 41 original source files remain byte-identical to starter commit.
- Pinned dependency advisory scan found no known vulnerabilities; limited tracked-text secret scan found no matches. Whole-request cap, >1MiB in-memory spool test, hostile Origin/Host and .env precedence tests now cover the RFC's local boundary findings.
- RELEASE_MANIFEST.md lists tested scope and unresolved live AI, external lender/user, legal/security, platform and print checks. This remains a local synthetic pre-pilot release, with no public deployment or real-data authorization.
