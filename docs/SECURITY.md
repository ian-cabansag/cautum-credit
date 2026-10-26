# Security, privacy and regulated finance gate

**DO NOT PUT REAL PATIENT, IDENTIFIABLE CLAIM OR PROTECTED HEALTH INFORMATION INTO THIS APP.** It is a local synthetic educational prototype, with no authentication, database, BAA, penetration test, enterprise retention policy or production access control. Field allowlisting provides a guardrail but does not establish HIPAA de-identification. Even aggregated and ostensibly anonymous data must be evaluated for linkage/reidentification risk. See HHS guidance: https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html

## What is implemented
- Fixed CSV headers, strict parser, upper bound on rows and uploaded bytes, rate/type validation, duplicate cohort rejection.
- Unknown patient-related columns prohibited; free-text label characters limited; suspicious patient strings rejected.
- Analysis uses Decimal; model sees structured calculation summaries, not raw file bytes.
- Optional AI bounded to one call (max 30 seconds, no retries), process-level call cap, 600-token output cap, bounded evidence-selection schema, no model tools, `store=False` request flag.
- Safe DOM string escaping on labels and model output; HTML attributes escaped; export CSV mitigates spreadsheet formula prefixes.
- Before parsing, ASGI bounds the entire request to 2,000,000 + 65,536 bytes. File limit stays 2,000,000. Tested/pinned Starlette multipart memory threshold is set to the whole-envelope cap, so permitted file parts cannot roll to temporary files. Test covers a >1MiB rejected synthetic payload. OS paging, workstation caches, downloads and exports are outside this raw-upload boundary.
- Host allowlist (127.0.0.1/localhost), mismatched Origin and cross-site unsafe-request rejection; app script CSP. No authentication or production CSRF/tenant control implied.
- No database or intentional raw-file storage; response cache disabled. Loopback only. Framework-spooling gap identified in the original baseline was repaired and explicitly tested in Prompt 12.

## What is NOT guaranteed
- The input restrictions are not an accredited PHI detection or anonymization program. An organization name or payer string can still be confidential or contain personal information.
- No full prompt-injection defense can guarantee model compliance. Current tests check schema, hostile labels and absence of AI route without key; **live model red-team tests have not yet been run**.
- No authentication, CSRF protection for future logged-in actions, rate limiting per user, secrets manager, network firewall, PHI authorization controls, encryption-at-rest, operational monitoring, DLP, audit logs, backups, tenant separation or data residency.
- The `MAX_AI_CALLS` cap is in-process only; restarts/multiple workers reset it. It is not production billing protection.
- Local source code and browser/client traces may be accessible to a user with workstation access. Using a hosted model has data governance implications and requires vendor contractual review before transmitting protected or confidential information.

## Production gating (must complete before real data)
1. Privacy attorney and healthcare security specialist map data flows, roles, potential covered entity/business associate roles, BAA requirements, permitted uses, retention and breach notification.
2. Data governance design and privacy threat model, documented de-identification/expert determination where appropriate.
3. App authentication, tenant isolation, RBAC, per-user and per-tenant quotas, immutable signed audit logs and retention/deletion controls.
4. Secrets management, encryption with managed keys, signed blob upload, validation/malware scanning, logging minimization and structured DLP.
5. Approved model vendors and contractual terms; only minimum-needed data; injection/hallucination tests; manual override and kill switch.
6. Third-party penetration test and remediation, software supply-chain review, vulnerability patching and dependency pinning.
7. Legal evaluation of UCC Article 9, Medicare/Medicaid anti-assignment and payer-specific contracts; lender documents and relevant regulatory licensing before any capital workflow.
8. SOC 2 or equivalent evidence can be pursued only after operational controls exist; never claim attestation early.

## Release boundary review · 2026-10-25
See RFC_001_PREPILOT_ARCHITECTURE.md for the original spooling/origin findings and proposed production control owners. Release tests verify bounded/chunked requests, cross-origin/Host rejection, large multipart staying in memory, .env lookup precedence, and no secret values in tracked text under documented pattern rules. Pattern/advisory scans do not certify the absence of secrets, vulnerabilities or PHI. Full security assessment, concurrency/DoS testing, enterprise identity/audit, contractual privacy review and all legal gates remain open.

## v0.3 tool and study boundary

The model now has one real read-only function tool with a strict borrower-ID schema. It cannot choose files, URLs, secrets or executable code. Tool results come from the request's already-validated analysis. A final ID/provenance check rejects uninspected findings and false approval status. Bounds and live/mock evidence are documented in AI_EVALUATION.md. This is not comprehensive model-safety proof.

The consented /study observation accepts a bounded role, timings, answers and feedback into local process memory, without automatic persistence. The participant is told to enter no confidential information. Exports are operator controlled. No authentication or independent timing attestation is implied. The course artifact includes an actual consenting founder observation. Active key values are compared against candidate text during the release scan without displaying them; the ignored .env never enters the archive.
