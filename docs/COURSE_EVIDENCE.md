# Course submission evidence · v0.4.0 · October 25, 2026

Author: **Ian Cabansag**. Repository: https://github.com/ian-cabansag/cautum-credit . Requirements: https://zlisto.github.io/mgt_409_fa26/project_requirements.html . Delivery is a local clone with included synthetic data.

## Submission artifacts

- `deliverables/report.html`: **13** Letter-sized pages with the eight required topics in order: identity/links, motivation, alternatives, agents and actual run, tokenomics, safety, observed human evidence, limitations and next month. Five actual embedded screenshots and an inline architecture SVG. No external rendering assets.
- `deliverables/slides.html`: **10** reveal.js 6.0.2 slides. All assets and full MIT notice embedded; upstream provenance retained in vendor/.
- Public GitHub source, README, exact dependencies, credential template and synthetic examples. Deterministic mode requires no key. The local-clone option does not require public application hosting.
- Additional `deliverables/cautum-reviewer-kit.zip`: eighteen files, including original sources for all three examples, worked review packets, reference answers and a **blank** future-feedback template. No independent participant is implied.

Generate with `python -m scripts.build_reviewer_kit` and `python -m scripts.build_evidence_package`. The optional PDF is a thirteen-page US Letter raster companion, not a replacement for required HTML. No optional video was recorded.

## Observed checks

All thirteen browser page boxes measured **816 × 1056 CSS px**; every footer ended at 998.41px inside its page. All five images loaded, zero external asset dependencies, no page overflow (`v04-report-layout.json`). All ten slide headings were traversed with ArrowRight, Home returned to the title, and all content fit (`v04-slides-layout.json`). The PDF was reopened to assert thirteen 612 × 792pt pages, Poppler-rendered and visually inspected (`report-contact-v04.jpg`). The slide contact sheet was also inspected.

Browser security blocks `file://` and native desktop control is unavailable. Direct local-file opening and the native HTML Print dialog remain **unverified**. Reveal's F binding is included; native fullscreen was not reliably observable. The browser layout and separately authored PDF do not certify native HTML pagination. Print CSS requests Letter, explicit page breaks and zero extra margins; use 100% scale and disable browser headers/footers.

Current working-copy verification: **107 tests**, Ruff lint/format, dependency consistency and **610** frontend positions passed. Actual HTTP comparisons reconcile all four datasets; **80** measured comparison requests made **zero AI attempts**. Actual browser exercised paired uploads, source downloads, packet/JSON export, keyboard selection, materiality/search/empty states and rejection retaining accepted sources. **23** responsive combinations had no document overflow. See `v04-runtime.json`, `v04-browser-layouts.json` and QA_RESULTS.md. Fresh remote verification is recorded in the release manifest after publication.

## AI and empirical evidence

The unchanged optional investigator uses one read-only `read_review_evidence` tool and strict inspected-ID validation. The financial engine owns all amounts and financial wording. `ai-evaluation.json` retains **six fresh final paired successes**, three per profile, 15 distinct upstream MISS responses. Requested model gpt-6-luna, returned gpt-6-luna-global / azure-openai. Median input/cached/output: standard **9,711 / 0 / 105**; lean **3,926 / 0 / 74**. Existing-rule coverage five versus three of twelve is not expert accuracy. Published Azure model-only reference costs are $0.0010236 versus $0.0004296 per run, excluding gateway/hosting/support; workload scales are planning assumptions. Failed experiments and cached observations remain separate. The traced browser screenshot matches a cached receipt, not an additional independent generation. A separate successful v0.4 smoke used **3,882 input / 0 cached / 70 output**; it is not added to the paired benchmark.

The actual synthetic injection record retains human review and unchanged financial wording. Automated boundaries and one live test do not establish complete PHI detection, universal injection resistance or regulatory compliance.

The consented **founder** exercise in `user-study.json` predates Change Desk: worksheet **76.89s**, Cautum **132.53s**, both answer pairs correct, clarity 5/5, reuse yes, “Seamless interface”. Cautum took **55.64s longer**. Different cases, worksheet first, one founder and self-directed timing prevent a causal/general time-saving claim. **No independent tester is available and none has completed the upgrade.** The kit enables future evaluation without manufacturing evidence.

## Requirement mapping

| Requirement | Evidence and honest limit |
|---|---|
| Identity, repository, setup | Cover, README, submission.json, public source; local-clone route |
| Motivation and alternatives | Report motivation and named primary product sources; buyer demand unvalidated |
| Agents/tools and traced actual run | Architecture SVG, actual read-only tool path, matching screenshot/receipt |
| Measured tokenomics and tradeoff | Fresh usage, rate sources, per-run/user/100/10,000 scenarios; coverage not expert accuracy |
| Working safety defense | Actual rejection screenshot, live synthetic injection, boundary tests |
| Human-impact evidence | Consented founder baseline, correct answers and slower app disclosed; no independent lender evidence |
| Real-world applicability | Three source-backed constructed examples; exact change packets; utility not independently validated |
| 10–15 pages / at most 10 slides | 13 bounded HTML pages, 13-page PDF companion, 10 traversed slides; native checks unverified |
| Fresh setup under ten minutes | Current remote-clone receipt and tested-host limits in RELEASE_MANIFEST.md |

No grade, award, model accuracy, adoption, financial impact, compliance or live healthcare integration success is asserted. Canvas upload of the URL and both HTML files remains an external submission action.

## Final fresh public-clone verification · October 26, 2026

Public candidate **896affc9d82778a3bc80167e0e7f9b922e34cc69** exactly matched local tree **5b34a43c320d1af5ee8cef85a338cadc6b1e13f7**. New remote clone, new venv and pip `--no-cache-dir`: **18.48 seconds** to healthy runtime, **30.89 seconds** to finish all checks on macOS arm64/Python 3.12.14. Git/Python were preinstalled; their installation was not timed. Network/CDN caches were uncontrolled.

All 107 tests passed; Ruff lint/format, dependency consistency and 610 slider positions passed. Real HTTP verified exact analysis/sensitivity, deterministic brief, scoped certificate, default comparison, all three worked cases and original sources, paired-file import, scoped HTML packet with original factors/policy, reviewer-kit route and request guardrails. A real single-borrower Portkey investigation completed. Datasets, snapshots, reviewer kit and both HTML deliverables regenerated with **no Git diff**.

The key was temporarily one folder above the clone; launch credential variables were removed and no .env existed inside the clone. Parent lookup succeeded. The temporary key copy and QA server were removed. Raw receipt: `evidence/remote-clone-v04.json`. The first harness attempt incorrectly requested `/reviewer-kit.html` rather than the existing `/static/reviewer-kit.html`; it stopped before any model call. The script was corrected and repeated in a new directory/environment with uncached installs; application code did not change. That unsuccessful measurement is retained separately. Final handoff additions contain documentation and receipts only.
