# Live AI evaluation · v0.3.0

The verified course route uses Portkey with requested `gpt-6-luna`; returned model `gpt-6-luna-global`, gateway provider `azure-openai`. All data was bundled synthetic aggregate data, including the separate synthetic instruction-like label test. No real healthcare data was used.

## Actual behavior

One model investigator chooses a borrower and emits a real `read_review_evidence` function call. Server dispatch returns exact borrower cents, policy exceptions and bounded source cohorts. The broader profile permits two different borrowers and three upstream requests; quick permits one borrower and two requests. The final schema selects only IDs from inspected results. No generated financial prose, approval, shell, browsing, raw-file or write access is available. Delivered figures and wording remain deterministic.

The implementation excludes previously inspected borrowers from subsequent tool schemas. Unknown/repeated tools, unsupported arguments, duplicate JSON keys, invented/uninspected IDs, missing/refused/incomplete output, false review flags, extra prose, deadlines and budgets fail closed. A failed request never becomes a rules-based response labeled AI. The legacy mode=ai selector is separate from the verified mode=investigate tool workflow.

## Final fresh paired sample

`python -m scripts.evaluate_ai --pairs 3` ran sequential paired general reviews on the same 192-cohort portfolio. Order alternated. Unique evaluation request IDs prevented exact gateway cache replay. All 15 final upstream responses reported MISS and distinct response IDs; observed gateway retry counts were zero. Six reviews completed, three per profile.

| Median | Broader | Quick |
|---|---:|---:|
| Input tokens | 9,711 | 3,926 |
| Cached input | 0 | 0 |
| Output tokens | 105 | 74 |
| Selected existing rule flags / total | 5/12 | 3/12 |
| End-to-end latency, ms | 4,087.25 | 2,625.12 |
| Published-rate model-cost estimate, USD | 0.0010236 | 0.0004296 |

The quick configuration lowered this model-cost estimate by about 58% and reduced selected rule-flag coverage. Three runs/profile do not establish statistical reliability or credit accuracy. Rule flags are demonstration rules, not independently labeled ground truth. Admission validity is enforced by code and is not a model-accuracy score.

Raw actual requests/results/usage/route metadata: evidence/ai-evaluation.json. Cached-request observations are separate in ai-evaluation-cached.json; HIT responses replayed earlier IDs/counts and are not independent generations.

## Failures and repairs are retained

Initial broader runs repeated a borrower; the runner rejected them. The tool schema now excludes inspected IDs. Some low-reasoning fresh runs exhausted the 1,200-token cap; Luna now uses reasoning effort none for this bounded selection task. These are not silently discarded: ai-evaluation-before-repair.json and ai-evaluation-output-cap-failures.json retain their usage and rejection evidence. The final sample is explicitly identified as post-repair.

The live instruction-like synthetic label test completed with valid inspected evidence and human review required. Delivered financial summary wording was unchanged from the deterministic engine. See live-injection.json. One successful boundary exercise does not prove comprehensive injection resilience.

## Pricing and spending scope

Published Microsoft Azure GPT-6 Luna Global Standard short-context rates, reviewed October 25, 2026: $0.10 input, $0.01 cached input, $0.50 output per million tokens. Source: https://azure.microsoft.com/en-us/blog/gpt-6-astra-sol-and-luna-for-production-agents-in-microsoft-foundry/ . The observed route reports azure-openai / gpt-6-luna-global. `cautum/pricing.py` keeps this reference calculation distinct from operator-supplied contract prices and actual account billing.

Cost = ((input − cached) × input rate + cached × cached rate + output × output rate) / 1,000,000. No cache-write option was requested. Account discounts, gateway fees, failed-call charges, hosting and support remain unverified. Gateway HIT token payloads are historical usage, not proof of new billable tokens. Scale tables disclose 50 reviews/user/month as a planning assumption, not observed usage or capacity.

Bounds: one tool/turn, 3/2 upstream requests, 1,200/600 output cap, 32,000-character transcript, 16,000-character tool result, per-request 30s timeout within 60s review deadline, no SDK retries. Shared MAX_AI_CALLS counts upstream attempts per server process. Restarts/workers reset it; external quotas remain necessary before deployment.

Official implementation reference: https://developers.openai.com/api/docs/guides/function-calling . Live success verifies this synthetic workflow, not provider retention guarantees, billing, real-data rights, lender usefulness or legal eligibility.
