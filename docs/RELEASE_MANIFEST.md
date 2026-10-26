# Cautum Credit v0.3.0 · course release candidate

October 25, 2026. Author: Ian Cabansag. Repository: https://github.com/ian-cabansag/cautum-credit . The user created the repository public; code publication and final delivery checks are being verified separately. No public application deployment occurs.

Current functionality preserves FastAPI/static UI and deterministic financial math, and adds a real bounded Responses function-calling investigator, source-linked tool receipts, published-rate model-cost estimates, unique memo filenames, and a consented local-memory review exercise.

Actual working-copy results: 87 tests passed; Ruff checks passed; 610 slider positions passed; 20 responsive view/width combinations without page overflow. Six fresh final paired live Portkey reviews completed (all 15 upstream responses MISS), with course model gpt-6-luna, returned gpt-6-luna-global / azure-openai. Earlier failures and cached observations remain in the evidence. A live synthetic injection retained human review and unchanged deterministic financial wording.

Actual founder observation: worksheet 76.89s, Cautum 132.53s, both answer pairs correct, clarity 5/5, reuse yes, “Seamless interface”. One founder observation is not independent lender validation or evidence of time savings.

The final HTML report has 12 page containers; the reveal.js deck has 10 slides. Both embed their assets. Exact native print, offline opening, final clean setup and remote publication results will be recorded in COURSE_EVIDENCE.md and evidence/submission-qa.json before final handoff. Remaining production/lender/legal/privacy gates below still apply. The historical v0.2 statements about missing live AI and user observations describe that earlier checkpoint, superseded by this header and AI_EVALUATION.md.

---

## Historical v0.2 release record

# Cautum Credit v0.2.0 · pre-pilot release manifest

Date: **2026-10-25** (America/New_York). Decision: **ready for local synthetic demonstration and independent synthetic methodology review; not authorized for real data or production lending**.

Original `/Users/iancabansag/Downloads/cautum-credit` remains unchanged: all **41 original files** matched the preserved `ea724f5` starter snapshot byte-for-byte. Active versioned implementation is this repository in the chat's outputs. The application architecture remains FastAPI + static HTML/CSS/JS, with the documented single-process command. No public deployment, external outreach, financing action or ownership change occurred.

## Version and build proof
Code release candidate verified from local clean clone: `51a749678ec430f6057f6511a402ce60f04512a9`. Subsequent handoff changes contain documentation/evidence only. Synthetic analysis: `eb70906f3a2b4ef9`; default policy content ID `fd834f242bc9a5c4`; engine `cohort-cents-v0.2`. Exact runtime/development dependencies are pinned separately. Python **3.12.14 / macOS arm64** actually tested. Other OS/Python combinations remain unverified.

## Actual final checks
| Check | Observed result | Evidence / limits |
|---|---|---|
| Original starter suite | 21 passed before product edits | CODEX_BASELINE.md; baseline defects recorded |
| Final Python suite | **66 passed**, one deprecation warning | Clean clone: 1.22s; working copy: 0.88s in recorded run. Mock AI tests are not live model proof. |
| Frontend rate regression | **610 slider positions** serialize within six-decimal ratio contract; invalid controls reject | `node scripts/check_frontend.cjs`; Node is optional QA tooling, not app runtime |
| Python lint/format | Ruff checks passed; 26 files formatted | `ruff check cautum scripts tests`, `ruff format --check cautum scripts tests` |
| Dependency consistency | `pip check`: no broken requirements | Exact tested pins, not independently security-approved versions |
| Dependency advisories | pip-audit 2.10.1: **no known vulnerabilities found** in pinned development lock | evidence/dependency-audit.json; current registry advisory result, not comprehensive security assurance. Packages are version pinned, not fully hash locked. |
| Secret patterns | No findings in tracked text; no local .env in repo | evidence/secret-scan.json; documented limited regex scan, not exhaustive secret/PHI audit |
| Fresh setup | Local Git clone, new venv, exact dev-lock install succeeded | No reuse of original app .venv. Package cache was available. Cold install/10-minute timing was not measured. |
| Reproducible generation | Sample + both snapshots + both HTML exhibits regenerated with **no Git diff** | Clean clone at candidate commit; local screenshot assets + vendored reveal.js |
| Real clean-clone runtime | Uvicorn started on 127.0.0.1:8002; HTTP routes, calculations, memo, certificate, study and guardrails succeeded | evidence/clean-clone-run.json. Temporary server stopped after verification. |
| Browser responsive pass | **20 view/width combinations**, no horizontal page overflow | Five views × 1440/1024/768/390; evidence/browser-layouts.json. Tables scroll within containers. |
| Download fidelity | Meridian trace **24 rows / $66,889.51**, matches scoped certificate | Actual downloaded CSV/JSON/HTML read and checked; evidence/export-verification.json |
| Artifact QA | 9 distinct slides traversed with ArrowRight; contents fit, screenshots loaded | COURSE_EVIDENCE.md. Report has 12 letter-sized browser sections; exact native browser print pagination remains manual. |

Known warning: installed Starlette emits a TestClient httpx deprecation notice. It is recorded and tests pass; a future transport/dependency upgrade requires renewed compatibility tests. No production readiness is inferred from its current compatibility.

## Browser interaction coverage
Actual browser against real localhost endpoints, without network stubs:
- All navigation views, Overview links into ledger/brief, borrower search and empty state, review queue filtering and sorting.
- Native borrower buttons with Enter selection, selected scope, exception-linked cohort formulas and full precision details.
- All four sliders changed/applied/reset. Final combined scenario applied 70% advance / 9.5% denial alert / 12.3% aged alert / 22% concentration threshold successfully.
- Alias/canonical local preview, cancel import, accepted template upload, prohibited header, hostile label rejected by server, prior source/result retention, and stale selected-borrower reset after a different upload.
- Trace CSV, analysis JSON, scoped illustrative certificate, study JSON, template download, offline brief copy and JSON save. Swagger API reference loaded and displayed the real 0.2.0 routes.
- Offline brief explicitly states zero model tokens. AI disabled when no key configured; missing-key API returns 503 without an upstream request. Console error/warning queries were empty in release interaction passes.
- Focus/skip/current-page semantics, contrast/reduced-motion/forced-color styles implemented. Actual screen-reader software, forced-colors mode, cross-browser matrix and accessibility certification remain unverified.

## Defects resolved, with behavior changes disclosed
1. Rounded cohort cents now reconcile across monetary views. Expected/collateral totals deliberately change from starter aggregates to **1,158,846.52 / 952,251.44** under the documented convention; base remains **761,801.19** for the sample. Full precision and adjustments remain visible. Multiplying displayed aggregate collateral by advance can differ by cents from the sum of full-precision cohort bases, intentionally.
2. Failed/busy imports and scenarios no longer silently replace accepted file/policy provenance; old memo attribution clears on new analysis. All flagged borrowers count correctly, with named subset explicitly labeled.
3. Equivalent Decimal policy formatting and row permutations produce stable hashes. Genuine input changes remain distinguishable even if rounded dollars happen to match.
4. Browser slider binary-floating residue no longer violates the six-decimal backend contract. The final browser pass caught this defect, and all 610 allowed positions now have a standalone serialization regression check.
5. Original framework spooling and missing localhost Origin/Host defenses were corrected after RFC review. Whole-request bytes are capped before parsing and multipart memory threshold exceeds the full envelope; >1MiB rejected synthetic payload remained unrolled. Cross-origin unsafe requests and unapproved hosts reject.
6. Optional model output now selects supported evidence IDs only; wording/numbers stay deterministic. No unsupported narrative, invented amounts, false review status, duplicate IDs, malformed/refused/incomplete result or timeout becomes an accepted AI brief. This narrows free-prose AI capability deliberately; no true tool-calling agent was added without justification.

## Phase disposition
0 baseline documented before product edits; 1 runtime/interaction repairs; 2 mathematical evidence; 3 responsive design; 4 bounded safe-alias review; 5 lender review and illustrative certificates; 6 conditional AI boundary and mocked evaluation; 7 synthetic surveillance; 8 measured demo/evidence; 9 self-contained evidence drafts; 10 architecture/counsel issue RFC; 11 hypothetical commercial experiments; 12 clean-clone pre-pilot review. Each phase has a separate commit group. External empirical and production gates were not marked achieved merely to finish the sequence.

## Still unverified / release blockers for broader use
- Any real successful OpenAI/Portkey call, exact gateway Responses/structured-output support, gpt-6-luna access, real token cost or model-selection quality. No credentials configured and **zero live model calls made**.
- Independent lender workbook agreement, denominator/rounding acceptance, recovery calibration, expert-labeled exception quality, actual analyst time savings, customer demand, willingness to pay, ARR, paid design partner or provider/health impact.
- General export mapping beyond explicit safe aliases, production historical imports, actual remittance/cash reconciliation, reserves, disputes, recoupments, outstandings and legally assessed availability.
- Real-data rights/privacy classification, HIPAA/BAA roles, data retention, tenant isolation, enterprise authentication, authenticated approvals, immutable signed audit, external quotas, incident response, penetration test, legal collateral feasibility and contractual/cash-control structures. No compliance attestation.
- Report author name, published repository URL, live-model/user evidence and exact native browser print pagination. These remain explicit gaps in the draft course package. No video recording was produced; DEMO.md is a reproducible script with real screenshots.
- No public hosting or GitHub publication. Bare localhost prototype must not be presented as a production service.

## Run the reviewed working copy

```sh
cd cautum-credit
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn cautum.api:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 . Core mode needs no key. For checks, install requirements-dev.txt and run pytest/Ruff/secret checker as in README. Optional Node QA checks slider serialization. Parent/root .env precedence is tested with synthetic settings; no live secrets are committed. The final running app uses the permanent working-copy path and standard command without reload. Temporary QA servers were stopped.
