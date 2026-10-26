# Cautum Credit

**Policy intelligence for healthcare receivables-backed credit.**

By Ian Cabansag · [GitHub](https://github.com/ian-cabansag/cautum-credit) · MGT 409 · v0.4.0

A working lender-side, synthetic-data pre-pilot demonstration. Cautum is a sole-founder software venture, not a lender, receivables purchaser, credit rating agency or validated underwriting model. No patient data or real healthcare files are permitted. Real deployment remains subject to independent lender, privacy/security and legal gates.

## Run locally

Python 3.10+ is required. This release was actually tested with Python 3.12.14 on macOS arm64. Other Python/platform combinations have not been run here. If `python3` is 3.9, choose an installed Python 3.12 interpreter rather than using it.

```sh
git clone https://github.com/ian-cabansag/cautum-credit.git
cd cautum-credit
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn cautum.api:app --host 127.0.0.1 --port 8000
```

On Windows use `.venv\Scripts\Activate.ps1` after creating the environment. Dependencies are exact tested pins in requirements.lock; development pins are separate. A successful install is not a security attestation. Keep host **127.0.0.1**. Do not expose this unprotected demo publicly.

Open **http://127.0.0.1:8000**. The included fictional portfolio auto-loads, with no secret or external service needed. A local course demo uses the same command; `--reload` is optional during development. See docs/RELEASE_MANIFEST.md for clean-clone results and known limits.

Fresh v0.4 verification from the public GitHub clone on the tested host: **18.48 seconds** to healthy runtime with a new environment and pip cache disabled; **30.89 seconds** including 107 tests, HTTP checks, a real AI tool review and reproducible artifact generation. Git and Python were already installed. Raw receipt: docs/evidence/remote-clone-v04.json. Other hosts and prerequisite installation were not timed.

## Demonstrated capabilities

- Eight fictional borrowers, 192 payer/aging cohorts, deterministic Decimal gross-to-base bridge.
- Strict eight-field CSV plus explicit documented safe aliases and local preview. Missing, extra, duplicate, incompatible or ambiguous fields fail closed. No field is silently discarded.
- Cohort HALF_UP cents that reconcile across portfolio, borrowers and exposure views. Full original inputs, multipliers, reason codes, unrounded amounts and adjustments are inspectable.
- Borrower search/status filters/sorting, exception-to-cohort evidence, scoped trace CSV, analysis JSON and **illustrative** HTML certificates.
- Policy scenarios with an explicit applied policy fingerprint/diff. Failed requests preserve accepted source and results; busy controls lock.
- Deterministic credit brief with zero model calls. A bounded AI investigator chooses borrowers, calls the real read_review_evidence function tool, and selects inspected evidence IDs. Financial wording remains deterministic. Course Portkey / gpt-6-luna was exercised live; see docs/AI_EVALUATION.md.
- Separate two-period synthetic study with exact balance bridges, explicit identity maps and provenance. It does not establish cash receipts, migration attribution or net availability.
- Responsive interface inspected at 1440/1024/768/390px; real localhost interactions and evidence screenshots recorded in docs/QA_RESULTS.md.

**Not implemented or validated:** real-data permission, recovery calibration, lender-approved policy, legal eligibility, reserves/outstandings/net undrawn availability, authenticated approvals, tenant security, durable audit storage, claims/EHR/banking integrations, independent user time savings, paid adoption or compliance attestation.

## Start with a relatable lender question

Open **Changes → Explore a lender question**. All examples are constructed, with source CSVs and explicit identity maps:

- A community clinic reports $20,000 more receivables, while the illustrative base falls $10,944 because the balance mix changes under the default policy.
- An imaging practice reports unchanged billing, while a changed denial assumption lowers the model base $5,760. Review the rate definition and potential double counting.
- A therapy group's payer changes its label. An explicit stable identity map preserves the same $27,360 modeled base.

The new **Change Desk** reconciles fixed-order input contributions to source-cohort cents, ranks borrower changes, filters by materiality, opens paired original inputs and exports a server-generated review packet. Uploading a constructed pair requires both eight-field CSVs, two strict identity manifests and synthetic-only confirmation. Both periods use the same applied policy. Failed imports retain the accepted comparison and its export sources. Contributions explain model changes, not causal losses or actual cash receipts.

Use the **worked examples and reviewer kit** link in Changes, or open `deliverables/reviewer-kit/START_HERE.html`. The portable kit includes original sources, worked packets, independently asserted reference answers and an empty future-review feedback template. No independent tester has completed this upgrade. Rebuild it with `python -m scripts.build_reviewer_kit`.

## CSV contract

```csv
provider,payer,payer_type,aging_bucket,gross_ar,contractual_adjustment_rate,historical_collection_factor,denial_rate
```

One organizational provider/payer/aging cohort per row. Payer types: Commercial, Medicare, Medicaid. Aging: 0-30, 31-60, 61-90, 91+. USD gross is nonnegative; rates are ratios [0,1] with at most six decimal places. Maximum 2,500 rows, 2,000,000 file bytes and $1T original portfolio gross. Duplicate/case-conflicting labels and inconsistent payer taxonomy are rejected. Weighted collection/denial definitions need independent agreement.

Use cautum/static/sample-template.csv. See docs/DATA_DICTIONARY.md for exact safe aliases and rate denominators. The first invalid logical CSV row reports its row number. Browser preview is a bounded alias review, not general spreadsheet ETL or a PHI detector. Removing identifiers does not itself establish de-identification.

## Financial convention

```text
N = Gross × (1 − contractual adjustment)
E = N × historical collection factor × (1 − denial rate)
C = E × aging factor × payer factor
B = C × advance rate
```

N is modeled allowed; E modeled collectible; C policy-adjusted collateral (legacy API field eligible_collateral); B illustrative borrowing base. None establishes verified recoveries or enforceable collateral. If collection factors already capture denial losses, the formula double counts that loss. All current factors are fictional research hypotheses, not lender standards.

Each stage uses the full original Decimal input chain, rounds each cohort HALF_UP to cents, then sums cents. It does not chain rounded intermediate values. This deliberately changes some v0.1 aggregate values. Original and unrounded values and adjustments remain in the trace. summary_exact / amounts_exact preserve decimal strings for downstream reconciliation. Analysis and policy IDs are reproducible checksums, not signatures, immutable records or approval evidence. See docs/UNDERWRITING.md and DATA_DICTIONARY.md.

## Live AI and usage

Core mode needs no key. For the verified course route, put `PORTKEY_API_KEY` in a private `.env` in the repository or one folder above it. Do not copy `.env.example` into the repository if your teaching-staff `.env` already sits above the clone. Root is checked first, stopping at the first existing file; process environment takes precedence. No secret is committed.

- Course key uses **gpt-6-luna only**, default gateway https://api.portkey.ai/v1. Live responses reported gpt-6-luna-global / azure-openai. Responses function calling and final structured JSON worked in six fresh final paired runs.
- A personal OPENAI_API_KEY route is supported but was not exercised live. Use one route; Portkey takes precedence if both keys exist.
- In Brief, choose a focus and scope, then Investigate with AI. Broader pass reads up to two borrowers; quick pass one. A source-linked receipt shows actual tools, requests, usage and coverage. The model has no shell, browsing, file, approval or write tool.
- Every amount remains from the Decimal engine. Unsupported or uninspected IDs, duplicate calls, invalid schemas and false human-review flags reject. The existing single-call selection API remains available as mode=ai; the tool workflow is mode=investigate.
- Up to 3 / 2 upstream requests per broader / quick review, 1,200 / 600 output tokens per request, 32,000-character transcript, 16,000-character tool result, 30-second request timeout within a 60-second review deadline, zero SDK retries. MAX_AI_CALLS counts upstream attempts per process (default 25; valid 0–500). Process restart resets it; production needs external quotas.
- Missing provider usage stays unknown. Published Azure Global Standard model-rate estimates are labeled estimates and exclude Portkey contract fees, discounts, hosting and support. Gateway HITs may replay historical token counts. Operator-supplied AI_RATE_CARD_JSON remains optional and separate.

Reproduce live evidence with `python -m scripts.evaluate_ai --pairs 3` using an authorized key. This makes real requests, writes actual successes/failures and uses unique evaluation IDs to distinguish fresh generations. Do not run it repeatedly without considering the course budget.

## Human observation

`http://127.0.0.1:8000/study` runs two synthetic worksheet/application tasks with consent, browser timing, answer checks and feedback. Observations stay in process memory until exported. The recorded baseline founder exercise, completed before Change Desk existed, had correct answers in both conditions, but the app task took longer: 132.53s versus 76.89s. This is not independent lender validation or evidence of time savings. See docs/evidence/user-study.json.

## Verify and reproduce

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
ruff check cautum scripts tests
ruff format --check cautum scripts tests
python -m scripts.check_release
python -m scripts.benchmark --url http://127.0.0.1:8000
```

Regenerate included data: `python -m scripts.generate_data`, then `python -m scripts.generate_snapshots`. Rebuild embedded HTML evidence: `python -m scripts.build_evidence_package`. Rebuild the portable case kit with `python -m scripts.build_reviewer_kit`. Existing screenshots document actual previous runs and must be recaptured after material UI changes. Benchmark measures local software only, never analyst impact.

## Security and deployment boundary

Server buffers a bounded 2MB file plus 64KiB request envelope before multipart parsing. The pinned/tested parser memory threshold exceeds that entire envelope, preventing framework temporary-file roll for permitted requests. Cross-origin unsafe requests and unapproved Host headers are rejected. App assets have a restrictive script policy. These are local guardrails, **not authentication, tenant isolation, complete PHI defense or production security**. Exports/browser/workstation artifacts remain operator-controlled. Raw upload bytes are not sent to AI or intentionally persisted. See docs/SECURITY.md and RFC_001_PREPILOT_ARCHITECTURE.md.

No external messages, payments, financing, account changes or legal filings occur. No public deployment was performed. Independent security, privacy, healthcare/lending counsel and actual lender methodology review remain mandatory gates before real use.

## Evidence and venture documents

Start with AGENTS.md and docs/CODEX_BASELINE.md. docs/CODEX_PROMPTS.md defines the sequence; docs/QA_RESULTS.md records observations. docs/PRODUCT.md, BRAND.md, ROADMAP.md and COMMERCIAL_VALIDATION.md preserve positioning and proposed commercial experiments. docs/PILOT_WORKSHEET.md is blank until a real consented observation.

The self-contained report and ten-slide reveal.js deck in deliverables/ include author/repository identity, actual screenshots, a tool/data-flow diagram, fresh model usage, sourced pricing scenarios, working safety evidence and the consented founder observation. See docs/COURSE_EVIDENCE.md for final file, print, navigation and setup verification. Independent lender utility and production readiness remain open.

Course source: https://zlisto.github.io/mgt_409_fa26/project_requirements.html . Long-range portfolio standards, credit passports and structured-finance infrastructure remain conditional business hypotheses, not present capabilities or traction.
