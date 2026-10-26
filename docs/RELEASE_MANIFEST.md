# Cautum Credit v0.3.0 · course release manifest

October 25, 2026. Author: **Ian Cabansag**. Public source: https://github.com/ian-cabansag/cautum-credit . Delivery: **local clone, synthetic demonstration**. No public application deployment or real-data authorization.

The original Downloads application was preserved; all 41 original files matched the retained starter snapshot at the baseline check. The active implementation preserves FastAPI/static HTML/CSS/JS and the deterministic Decimal engine. The versioned phase history and docs/QA_RESULTS.md retain the earlier checkpoints; those checkpoints' missing live-AI/user-evidence statements are historical.

## Actual verification

| Check | Observed result | Practical limit |
|---|---|---|
| Remote source integrity | Candidate 99b75d35aa6b09731a3e8b4fd010844699ee5b08 exactly matches local tree bd4c0c0cc50022a5a18b3f3990b1a7bbbbef1309 | Final handoff updates are documentation/artifact only |
| Fresh remote setup | **23.47s** to healthy runtime; **38.90s** for all checks | Git/Python preinstalled; macOS arm64/Python 3.12.14; pip cache disabled, network/CDN caches uncontrolled |
| Tests | **87 passed**, one Starlette TestClient deprecation warning | Mock model tests are distinct from live receipts |
| Quality/dependencies | Ruff lint/format and pip check passed | Version pins are not comprehensive security certification; earlier advisory scan is dated evidence |
| Frontend contract | **610** slider positions passed | Actual browser also checked scenario application/reset |
| HTTP proof | Exact analysis/scenario, deterministic memo, scoped certificate, surveillance and request guardrails passed | Localhost, single user |
| Parent .env | Live Portkey lookup from one folder above fresh clone succeeded | Temporary copy removed; no key published |
| Reproducibility | Datasets, snapshots and both HTML exhibits regenerated with **no Git diff** | Screenshots document their recorded runs |
| Browser layout | **20** view/width combinations; no page overflow | Five views × 1440/1024/768/390; assistive technology certification and cross-browser matrix unverified |
| HTML report | **12** bounded Letter-sized page boxes; four embedded screenshots loaded; zero external asset dependencies | Direct file opening and native print dialog blocked by environment; not recorded as passing |
| Presentation | **10** distinct slides traversed with ArrowRight; all images/content fit | Reveal F binding included; native fullscreen not reliably observable in embedded browser |
| PDF companion | **12** US Letter pages, reopened, Poppler-rendered and visually inspected | Raster companion from browser page captures; required submission is report.html |
| Secret checks | Tracked and unignored candidate text scanned for patterns and the exact configured key; no findings | Limited scan, not an exhaustive privacy audit; .env intentionally ignored |

Raw current result: `docs/evidence/remote-clone-v03.json`; aggregate `submission-qa.json`; artifact details `docs/COURSE_EVIDENCE.md`. A fresh clone used a new environment and uncached runtime/development installs. Temporary servers and copied credentials were removed. One permanent working-copy server uses the README command on 127.0.0.1:8000.

## What works

Eight fictional borrowers / 192 cohorts. Strict CSV allowlist and safe aliases with preview. Reconciled cohort cents, exact formulas/inputs/reasons, policy and analysis fingerprints, source-linked borrower exceptions, search/status/sort, applied policy scenarios, trace/analysis/certificate exports and deterministic brief. Two explicitly fictional periods have exact balance bridges; no cash-receipt inference.

Analysis `eb70906f3a2b4ef9`, policy `fd834f242bc9a5c4`: gross **1,934,634.00**, modeled allowed **1,298,648.31**, collectible **1,158,846.52**, policy-adjusted collateral **952,251.44**, illustrative base **761,801.19**. Changing advance to 70% yields **666,576.03** without changing collateral. Each stage uses original Decimal inputs, rounds cohort amounts HALF_UP, then sums cents; it does not chain rounded stage totals.

One bounded AI investigator uses one read-only evidence function, never a write/shell/browse/approval tool. Server validation admits only inspected supported IDs. Financial wording and amounts stay deterministic. Focus/scope controls and a source-linked per-request receipt work in the UI; unique memo exports preserve focus/scope metadata.

## Actual empirical evidence

**Six fresh final paired live Portkey reviews** completed, three per profile; 15 distinct responses, all MISS. Request gpt-6-luna; returned gpt-6-luna-global / azure-openai. Standard median input/cached/output 9,711/0/105; lean 3,926/0/74. Selected existing flags five versus three of twelve. Published Azure model-only estimates $0.0010236 and $0.0004296 per run exclude gateway/hosting/support and are not an invoice. Coverage is not expert-validated accuracy. Earlier failures and cached observations are separately retained. A separate live synthetic injection preserved human review and deterministic financial wording. The fresh clone also completed one real single-borrower tool review.

**One consented founder observation:** worksheet 76.89s, Cautum 132.53s; both answer pairs correct; clarity 5/5; reuse yes; “Seamless interface”. The app took 55.64s longer. Different cases, worksheet first and self-directed timing do not establish time savings, independent analyst utility or adoption.

## Boundaries and remaining work

- Fictional policy/recovery assumptions, possible double discounting, no lender-approved workbook or expert exception labels. No reserves, outstandings, disputes, recoupments, actual remittances, net undrawn availability or legal collateral determination.
- No real PHI/patient records or permissioned operational healthcare data. The allowlist cannot detect every PHI risk. No EHR/claims/clearinghouse/payer/bank integration success.
- Local, single-user, memory-only; no authentication/tenant isolation, authenticated policy approvals, signed immutable audit, production retention/deletion controls, external quotas or incident-response operation. Fingerprints are checksums, not signatures or compliance evidence.
- No independent lender validation, measured time savings, paying customer, pricing validation, financial impact, ARR or defensible moat. Legal/data-rights and commercial gates in RFC_001_PREPILOT_ARCHITECTURE.md and COMMERCIAL_VALIDATION.md remain open.
- Native file opening, HTML print dialog and fullscreen remain unverified as detailed above. Optional video was not recorded. There is no claim of a hosted production service, general security assurance, HIPAA/SOC2 compliance or credit approval authority.

## Run

Follow README.md. Core mode needs no key. Optional course Portkey uses only gpt-6-luna; root .env first, then parent, with process environment precedence. Do not commit credentials or expose the unprotected demo beyond loopback.

`python -m uvicorn cautum.api:app --host 127.0.0.1 --port 8000`
