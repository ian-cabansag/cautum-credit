# Codex execution playbook · copy one prompt at a time

**Start by extracting this repository ZIP and opening that folder as the active Codex workspace.** You do not need to paste the whole prior chat into Codex. `AGENTS.md`, README and docs are the persistent context; tell Codex to read them first. Prompts are sequential, best run with a commit/diff review after each phase. Don't give AI unrestricted authority over any medical/financial records.

## Prompt 0 — onboard Codex (FIRST MESSAGE)

```text
You are joining a founder-led venture called CAUTUM CREDIT. This workspace is its canonical repository. First read AGENTS.md, README.md, and EVERY file in docs/, in particular PRODUCT.md, UNDERWRITING.md, ARCHITECTURE.md, SECURITY.md, ROADMAP.md, VALIDATION.md, BRAND.md, COMPETITION.md and MGT409.md. Summarize your understanding in a short engineering plan. Do not delete or replace the working starter. Run the existing tests and identify the actual current behavior. Do not claim a feature works unless you test it. Take care of the founder's sole ownership and premium visual direction. Do not use patient-level data or real PHI. No autonomous credit decisions and no invented traction or model success. Tell me which tasks have unverified assumptions and ask before making irreversible changes. First produce a dated baseline QA note in docs/CODEX_BASELINE.md with factual test results.
```

## Prompt 1 — start, run, and inspect

```text
Please launch the FastAPI app using the documented one-process local command, perform a fresh-clone style setup and test all API routes using the synthetic CSV. Use a browser automation tool if present to inspect desktop and mobile widths. Actually CLICK navigation, upload, ledger borrower rows, policy sliders/apply/reset, search, JSON/CSV export, offline memo and error toasts. Fix every failing interaction, console error, or obvious accessibility issue; preserve the brand. Document actual commands and observed results in docs/QA_RESULTS.md. Run python -m pytest -q. Do not attempt AI calls until a key is legitimately configured.
```

## Prompt 2 — prove the credit math before more features

```text
Act as a skeptical healthcare ABL underwriter. Read docs/UNDERWRITING.md. Refactor the existing engine only where needed to clarify the full bridges from gross to net allowed to modeled collectible to lender-policy collateral to indicative base. Expose all multipliers, actual rates and reason codes in an easily auditable per-cohort view, and add reconciliation to cents between display rows and summary totals. Write independent golden-case tests and invariant/property tests for zero, upper-bound, policy sensitivity, failed rows, unusual contracts, and portfolio aggregation. Add a data dictionary and formula glossary. Avoid implying the policy is lender-standard. Do NOT develop default scores without validated outcome labels. Keep policy version and analysis hash stable for identical inputs.
```

## Prompt 3 — make the interface exquisite, not decorative

```text
Become design director and front-end engineer for an institutional-quality healthcare credit intelligence platform. Follow docs/BRAND.md. Critique every screen against premium private banking dashboards, financial terminal information hierarchy, and intuitive audit workflows. Improve typography, whitespace, charts, responsiveness, accessible contrast/focus states, skeleton/loading/empty/error states, and microinteractions. Keep EXACT numerical wiring to backend. No fake time-series charts, trends, badges, synthetic claims presented as real, giant emojis or generic AI gradients. Preserve a calm forest-green and bone-white editorial system; make every screen screenshot-ready for a real lender demo. Inspect at 1440px, 1024px, 768px and 390px; prove all controls work. Only add libraries if justified, and maintain a one-command class demo.
```

## Prompt 4 — credible mapping and ingestion

```text
Design the next aggregate A/R import/mapping flow for a healthcare lender. Continue to prohibit actual PHI and patient identifiers. Support validated variations in SAFE, permissioned aggregate payer, provider and aging columns, pre-upload column preview, clear missing-field mapping, row-level error report and reconciliation of gross. Do not silently infer incompatible denominators. Introduce a mapping stage that cannot accidentally pass extra columns/free text to backend or LLM. Build tests for malicious names, Excel formula injection, oversized/duplicate inputs, nulls, unexpected columns, possible patient identifiers and ambiguous payer labels. Do not claim HIPAA de-identification is automatic.
```

## Prompt 5 — ledger, exceptions, borrowing-base certificate

```text
Build lender-grade portfolio review around the current deterministic engine: filter/sort/slice multi-borrower exposure, drilldown into every policy exception with exact source cohort, policy factor and reason, show waterfall from gross to base, and export a human-readable BORROWING BASE CERTIFICATE explicitly marked illustrative. Display which data assumptions and eligibility decisions still need lender approval. Add signed-off 'to review' placeholders WITHOUT faking an authenticated approval. Keep current UI responsive and test exports for formula injection and rounding fidelity.
```

## Prompt 6 — actual AI tools, quality gates, and measurements

```text
Read all guardrails, then improve the AI analyst into a genuine bounded read-only tool-use agent ONLY if justified. Give the model tool access to curated functions get_portfolio_summary, get_borrower_flags, get_policy and get_calculation_evidence; do not give raw upload access, secrets, write tools, shell, browsing or approval authority. Cap tool turns and tokens; use strict structured response, no numeric re-calculation, and reject claims not grounded in the authoritative engine. Separate deterministic baseline from generated analysis in UI. Log real input/cached/output token usage, latency and failures, and make costs configurable based on verified model/provider rates. If you cannot verify Portkey gpt-6-luna's endpoint/features without an authorized key, mark the exact uncertainty. Tests must include prompt injection, malformed model responses, refusals, timeouts, hallucinated numbers and budget exhaustion.
```

## Prompt 7 — two-period surveillance

```text
Introduce synthetic T0 and T1 portfolio snapshots and a deterministic cohort roll-forward with reconciliation. The user should see actual changes in aging, concentration, denials and borrowing-base headroom; alerts should explain deltas. Preserve snapshot provenance, stable borrower IDs, import dates and policy version. Never hallucinate trends from a single period. Write deterministic adversarial tests for rows that drop out, renamed payers, mixed reporting dates, policy changes, and restatements. Make a visually refined surveillance view backed by real computed deltas.
```

## Prompt 8 — honest demonstration and proof

```text
Prepare a 2–3 minute screen demo using ONLY the reproducible synthetic portfolio. Capture true app screenshots, successful and failed runs, screenshots of policy change and parser rejection. Use tests/benchmark script to report actual runtime. Draft a separate interview guide and record empty fields for a genuine pilot lender, not fabricated testimonials. Add a repeatable checklist of how to measure analyst time saved and exact formula agreement with independent spreadsheets. Every metric must be marked actual/estimated/not yet tested.
```

## Prompt 9 — build the full course package from evidence (AFTER tests)

```text
Use https://zlisto.github.io/mgt_409_fa26/project_requirements.html and docs/MGT409.md. Read the REAL working repo and validation output. Upgrade deliverables/report.html to a beautiful, self-contained 10–15 printed-page report with required sections in exact order: title/links, motivation, honest competitor mapping, actual agents/tools, one traced run, measured tokenomics, working safety defense, actual impact evidence, limitations and roadmap. Build deliverables/slides.html with no more than 10 elegant reveal.js slides. Embed actual screenshots in both HTML files (base64 if needed) so double-click works. NEVER invent token counts, dollar prices, screenshots, human tester comments, time saved, or production capabilities. If data is unavailable, leave clearly labeled empty evidence fields and give me a concise measurement request. Verify print page count, all local assets and slide keyboard navigation.
```

## Prompt 10 — commercial architecture review

```text
Conduct a serious red-team technical and legal-feasibility architecture review, using docs/SECURITY.md and UNDERWRITING.md. List all blockers to ever handling real data: security, HIPAA/BAA, non-PHI rights, cyber liability, Medicare/Medicaid assignments, payer contracting, UCC perfection/enforceability, borrower consents, state law, audit trails, payments/lockbox control, model risk and lender governance. Do not claim legal determinations. Produce a prioritized architecture RFC and product security roadmap before coding enterprise features. Keep current app localhost only and prohibit deployment of real data.
```

## Prompt 11 — product market validation, not vanity

```text
Role-play a skeptical healthcare specialty lender investment committee, a provider CFO, and an enterprise procurement lead. Review our product/competitors honestly. Give me the top 15 reasons they would reject this product and the smallest measurable experiments to de-risk them. Do not praise the idea without evidence. Propose an initial narrow ICP and paid design partnership offer, with hypotheses explicitly labeled rather than invented price, pipeline, signed clients, or proof. Update docs/VALIDATION.md and ROADMAP.md only with objectively justified decisions. Preserve a credible lender-first positioning and our sole-founder path.
```

## Prompt 12 — release discipline

```text
Do a production-quality PRE-PILOT RELEASE REVIEW. Verify from a clean clone, install and test, run all browser interactions and exports, inspect responsive views, dependency and secret scan, code quality, data validation, error paths and audit rounding. Produce a release manifest of tested and untested features, known risks and exact run instructions. Pin approved dependencies, prepare a non-PHI demonstration deployment only if its security boundaries are appropriate. Do not conflate a successful demo with production authorization, legal underwriting, clinical impact or market adoption.
```

## What Codex should never do
- Claim to run in the background, claim tasks succeeded without logs, or invent access to user accounts.
- Rewrite the whole app into a dependency-heavy full-stack framework without need and regression tests.
- Replace a legitimate lender credit expert with a fictional risk score, or hide assumptions.
- Treat gross A/R, collectible amount, *financeable eligible* collateral and legally enforceable liens as interchangeable.
- Transform class report placeholders into fake measured token costs/user feedback.
- Use patient names/identifiers or upload real healthcare files to an unreviewed model.
