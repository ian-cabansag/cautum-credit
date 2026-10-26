# Current v0.3 live demonstration

1. Start the app with the README command and included synthetic dataset.
2. Show exact gross-to-base cents, policy/analysis IDs and a selected cohort trace.
3. Open Brief, choose General review / Broader pass, and click Investigate with AI using an authorized course key.
4. Inspect the actual borrower tool path, evidence-to-cohort links, review receipt and provider usage. Export the JSON receipt.
5. Demonstrate unknown-column rejection; show the recorded founder result honestly: both correct, app slower.
6. End with independent lender review, expert exception labels, legal/data permission and enterprise controls as next gates.

Real current evidence: ai-evaluation.json, browser-ai-receipt.json, live-injection.json and user-study.json. Runtime benchmarks below are software timings, not analyst impact. The earlier phase-8 demo below is historical; its statement that AI/user evidence was missing was true at that checkpoint.

# Reproducible 2–3 minute demo · 2026-10-25

Run on localhost using synthetic data only. Start `python -m uvicorn cautum.api:app --host 127.0.0.1 --port 8000` and reload the page. No key needed. Explain that all factors are hypotheses and legal eligibility is unreviewed.

1. **0:00–0:30** Overview: 8 fictional borrowers / 192 cohorts. Trace gross $1,934,634.00 → modeled allowed $1,298,648.31 → collectible $1,158,846.52 → policy-adjusted $952,251.44 → illustrative base $761,801.19. Explain the cent convention and policy ID.
2. **0:30–1:00** Ledger: filter High attention, select Meridian by keyboard, check Selected borrower only, follow an exception to cohort inputs/formula. Export trace and illustrative certificate. Explain missing reserves, outstandings and legal review.
3. **1:00–1:25** Policy: change 80% to 70%, apply. Base decreases while collateral stays $952,251.44. Display is compact; export provides exact cents. Reset. No real advance-rate recommendation is being made.
4. **1:25–1:50** Credit brief: Generate rules-based brief. Observe deterministic label / zero AI tokens. Optional AI remains unavailable without approved key; do not imply a live successful model call.
5. **1:50–2:15** Monitor: open separate dated fictional study. Gross delta −$34,530.37; base delta −$24,306.09. No headroom or verified cash collection estimate.
6. **2:15–2:40** Import: use a synthetic invalid header to show rejection, then a permitted reordered alias sample to show local preview and explicit denominator review. Last accepted analysis remains intact. No patient information is needed to demonstrate the guardrail.

## Evidence actually captured
Real IAB browser against actual Uvicorn; no network stubs. `docs/evidence/demo-overview.jpg`, demo-trace, demo-policy-before, demo-policy-after, demo-brief, demo-surveillance and demo-rejection. Header rejection is the browser's pre-upload check; backend rejection is independently tested via HTTP. Prior root-level PNG previews are historical starter artifacts, not evidence of current app behavior.

## Measured runtime
Run `python -m scripts.benchmark --url http://127.0.0.1:8000 --output docs/evidence/benchmark.json`. Recorded 2026-10-25: 30 parse+engine runs median 4.064ms / nearest-rank p95 4.508ms; 20 real loopback multipart HTTP runs median 11.703ms / p95 12.055ms, max 226.379ms (includes first-request overhead). Hardware/session-specific, not production latency or analyst efficiency. Browser rendering/download/user review time excluded. AI calls: zero. Do not extrapolate user savings from this benchmark.

## Claims register
Actual: technical tests, computed synthetic dollars, observed browser controls and measured local runtimes. Estimated: none presented as empirical performance. Not yet tested: live AI/provider support, published exact-model cost, expert spreadsheet agreement, actual users, lender value, willingness to pay, commercial integrations, legal/security readiness. Pilot worksheet remains blank until real observation with consent.
