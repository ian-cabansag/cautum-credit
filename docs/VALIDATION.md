# Pilot validation and evidence plan

The business is not proven by shipping an attractive demo. Validate both **underwriting accuracy and buyer workflow value**.

## Pilot design
**Participants:** ideally two credit analysts or lenders and one provider revenue-cycle specialist, without real PHI during discovery. Seek permission before recording or quoting anyone. All early validation can use synthetic or an appropriately scoped synthetic adaptation of their workflow.

**Workflow:** ask lender to share a manually constructed, no-PHI test case with expected results, policy assumptions and 3–5 known exceptions. Run the same scenario using their established process and Cautum, with the same input data and policy; measure without coaching.

### Quantitative measures
- Formula fidelity: exact agreement (to rounding) on net allowed, eligible, borrowing base and limits under independently supplied lender assumptions.
- Alert precision and recall compared to **verified** expert-labeled exceptions. Avoid accuracy claims without an expert reference.
- Analyst minutes per portfolio review, separately for data mapping, calculations, investigation, memo drafting.
- Audit reconstruction time: how long to trace one ineligible amount to source and policy.
- Exceptions missed or falsely raised, plus decision-maker trust on 1–5 scale.
- AI token input/cached/output, real cost per successfully completed review, failures and retries.
- CSV rejection rate for an unfamiliar, sanitized export and mapping pain points.

### Evaluation worksheet
| Test | Spreadsheet/current process | Cautum v0.1 | Difference | Evidence |
|---|---|---|---|---|
| Import/setup, minutes | TBD | TBD | TBD | Screen recording |
| Base calculation, dollars | Expected value (expert) | Actual result | Absolute cents diff | Side-by-side |
| Policy alerts identified | Confirmed list | Detected list | False pos/neg | Annotated test |
| Time to review, minutes | TBD | TBD | TBD | Timed observer log |
| Time to reproduce one excluded row | TBD | TBD | TBD | Observer log |
| Run AI tokens + cost | Not applicable | Actual API usage | Actual pricing | Redacted telemetry |

**Do not fill TBD with fabricated estimates.** The repo has automated technical tests and a consented founder exercise; independent buyer impact remains unverified. A quote from a real pilot participant must be authorized, attributable or intentionally anonymized, and faithfully represented.

## 20-minute customer interview
1. Walk me through the last borrowing-base certificate or annual/quarterly collateral review you prepared.
2. What input fields are painful and how often are they inconsistent?
3. Which assumptions affect eligibility and where do you get these values?
4. Which three exceptions trigger follow-up and which are no longer useful?
5. Show me where you disagree with our gross-to-base methodology.
6. Would aggregated cohort data suffice for a first pass, or do you need claim/remit data immediately?
7. What evidence would make a new system approved for workflow use?
8. Who signs off on software purchase, data sharing and security?
9. If this saved X analyst hours/month *as verified*, where would those hours actually go?
10. What would make you abandon the product after one test?

**End with:** 'Can I observe one anonymized, permissioned review using our demo data, then ask you to score accuracy, clarity, and trust?'

## No fabricated financial benefits
Better underwriting does not directly equal better patient access, lower financing rates or more capital funded. Such impact requires longitudinal lender/provider evidence and a defensible causal argument.

## Acceptance milestones
A. Developer QA: local API tests, browser interactions, hostile CSV, no secrets.
B. Credit professional: independently reproduces sample calculation and agrees definitions.
C. Workflow pilot: real person uses synthetic or properly permissioned inputs uncoached, demonstrated time/quality result.
D. Security/legal gate: permission to process real data, compliant contracts, infrastructure and audits.
E. Paid pilot: written scope, outcomes and validation criteria; no fabricated customer logos or ARR.

## 2026-10-25 engineering evidence update
Developer QA now includes real localhost browser interactions, exact cohort-cent reconciliation, safe-alias review, scoped illustrative certificates, mocked AI evidence-boundary tests and two dated synthetic snapshots. At the phase-8 checkpoint 61 tests passed; final release results are recorded separately in RELEASE_MANIFEST.md. This advances technical proof only. No credit professional independently validated the policy, no uncoached workflow pilot occurred and no paid demand is established. Use PILOT_WORKSHEET.md and COMMERCIAL_VALIDATION.md for the next observation and proposed rejection tests. No interview response or TBD field has been filled from role-play.

## v0.3 founder observation

See evidence/user-study.json for actual consent, role, timing, answers and feedback. The founder completed both tasks correctly, with Cautum taking longer. This is a real founder observation, not an independent lender pilot or evidence of time savings. The six fresh AI reviews and one live instruction-like label test are in AI_EVALUATION.md.

## v0.4 evidence scope

Change Desk has independent golden arithmetic, 64 seeded exact Fraction-reference cases, request-boundary and identity/packet tests. Three constructed workflow stories have explicit expected default-policy results. This is technical verification. The earlier founder observation predates this upgrade and does not establish its user benefit. No independent tester is currently available; the reviewer kit is prepared with blank response fields, not fabricated outcomes. See IMPACT_LEDGER.md.
