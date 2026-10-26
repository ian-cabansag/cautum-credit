# RFC 001 · Commercial feasibility and pre-pilot security

Date: 2026-10-25. Status: proposed architecture and specialist questions, **not legal findings or production authorization**. Preserve the one-process localhost synthetic demo. Founder remains sole product owner. No enterprise infrastructure was added merely to create an appearance of readiness.

## Decision
Proceed with a reproducible synthetic review workflow. Require independent lender methodology, privacy/security assessment, counsel analysis and permissioned design-partner scope before processing real data. Do not execute payments, account changes, assignments, filings, financing, external messages or autonomous credit decisions.

## Current threat model
Untrusted CSV/header/labels, malicious websites targeting localhost, workstation access, compromised dependencies, API/gateway failures, model evidence omissions, analyst misinterpretation and unjustified legal eligibility claims. Trust boundaries: browser preview, actual request byte boundary, canonical parser, Decimal model, bounded AI evidence catalog, export files and the human review process.

Two concrete defects discovered during this review:
1. Installed Starlette defaults to a 1,048,576-byte multipart spool threshold. A permitted 2MB upload can therefore hit a temporary file before the route validates it. Existing unqualified memory-only documentation overstated the framework boundary. Release fix must impose a whole-request byte cap before parsing and keep all permitted multipart files below an explicit tested memory spool threshold.
2. No server-side Origin/Host validation protects local form endpoints. Cross-origin sites can potentially submit forms to localhost even without reading responses. Release fix must restrict hosts and reject mismatched Origin / cross-site browser requests, including optional AI routes. This is local attack-surface reduction, not authentication or production CSRF architecture.

Neither finding was tested with real sensitive data. Rejected/accepted synthetic payloads only. Browser downloads, local QA screenshots, workstation caches and exported evidence are operator-controlled artifacts and are not covered by a raw-upload in-memory claim.

## Prioritized architecture and acceptance gates
| Priority | Blocker | Required decision / artifact | Acceptance evidence / accountable role |
|---|---|---|---|
| P0 local | Request size before multipart; temporary spooling; hostile browser origins | Bounded ASGI request wrapper, explicit memory threshold, trusted hosts/origins | Chunked oversize request and >1MiB synthetic multipart tests; engineer |
| P0 pilot | Data ownership, purpose, privacy classification, linkage risk, small-cell exposure | Approved aggregate dictionary, data-rights agreement, documented HIPAA/BAA role analysis | Written privacy/security/counsel sign-off and sample contract; founder + specialists |
| P0 pilot | Source formulas, denial double counting, missing amounts | Lender-authored golden workbook, explicit denominators, rounding and uncertainty conventions | Independent cent agreement and exception labels; credit officer |
| P0 pilot | Legal collateral classification versus modeled amount | Payer/program/jurisdiction/contract matrix; distinguish security attachment/perfection from collection and enforcement rights | Specialist secured-lending and healthcare counsel memorandum; no engine inference |
| P0 enterprise | Identity, access, isolation | Organization SSO, least-privilege RBAC, explicit tenant context, DB row-level controls | Cross-tenant negative tests on every route/job/export/cache, revocation tests; security lead |
| P0 enterprise | Durable evidence and policy authority | Append-only event storage, signed policy versions, review/effective dates, exception authority and retention | Reconstruct prior result after policy change, verify event-chain tampering/deletion controls; risk + engineering |
| P0 enterprise | Storage/retention and safe ingest | Approved encrypted object/DB storage, signed uploads, malware/DLP boundaries, retention/deletion/legal-hold schedules | Threat model and restore/deletion/hold tests; privacy + platform |
| P0 enterprise | Model/data vendor boundaries | Approved vendors/contracts/BAAs if applicable, exact permitted fields, egress restriction and minimization | Real synthetic refusal/injection/factuality/cost tests, independent kill switch; model-risk owner |
| P0 enterprise | Quotas and operations | Tenant/user/gateway quotas, concurrency controls, timeouts, alerts, incident response and secret rotation | Failure injection, rate-limit/cost exhaustion drills, runbooks and on-call owner |
| P1 | Supply chain and liability | Pinned reviewed dependencies, vulnerability triage, SBOM, access-controlled CI, cyber/E&O assessment | Reproducible build, secret scan, independent security assessment and insurance/legal review |
| P1 | Economic completeness | Lender-specific reserves, disputes, dilution, recoupments, concentrations, netting, obligor/borrower limits and outstandings | Reviewed cases with opening/delta/closing evidence and no hidden default zeroes |
| P2 | Actual integrations / cash realization | Authorized payer/remittance/RCM mappings, contractual permissions and data lineage | Agreed source-to-receipt reconciliation and repeatable permitted integration tests |

## Counsel issue register, not conclusions
- **HIPAA / BAA / privacy:** identify covered entity/business-associate roles, permitted use, minimum data, expert determination/Safe Harbor applicability, linkage and reidentification risk, breach notification, subcontractors, data location and retention. A field allowlist does not establish de-identification.
- **Data rights:** borrower/provider consent, lender authority, export ownership, RCM/clearinghouse contracts, secondary model use, cross-lender aggregation and revocation. A borrower label can still be confidential.
- **Government reimbursement:** separately assess Medicare providers/suppliers, Medicaid/state arrangements and managed-plan contracts. Do not treat a generic payer factor as an assignment or payment-rights opinion.
- **UCC and contracts:** counsel must determine collateral category, actual jurisdictional enactment, attachment/perfection, priority, lien searches, competing interests, proceeds, offsets, setoff/recoupment, enforcement, confidentiality, payer consent and borrower covenants. Uniform model text is not a state-specific legal opinion.
- **Cash control:** permissible lockbox/deposit ownership, control agreements, payer instructions, reversals/recoupments, servicing, payment redirection and bankruptcy exposure. The app performs none of these actions.
- **State and federal activity classification:** software-only role versus broker, lender, purchaser, servicer or securities activity, disclosures/licensing, fee structures, underwriting reliance, liability allocation, cyber/E&O and consumer/patient data rules where relevant. No geography or actual transaction facts supplied, so feasibility remains open.
- **Governance:** credit authority, signed policy approvals, model-risk ownership, overrides, dispute correction, evidence retention, adverse incident escalation and supplier/procurement diligence. No SOC 2/HIPAA or other attestation claimed.

## Primary materials reviewed 2026-10-25
These establish topics requiring specialist analysis, not that any proposed Cautum transaction is permissible.

- [HHS de-identification guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html) describes Expert Determination and Safe Harbor, organizational roles and residual identification considerations. Our allowlist is not either method.
- [42 CFR 424.80, eCFR](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-424/subpart-F/section-424.80) addresses supplier reassignment restrictions and exceptions. Provider payment arrangements need separate review under [424.73](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-424/subpart-F/section-424.73).
- [42 CFR 447.10](https://www.law.cornell.edu/cfr/text/42/447.10) addresses Medicaid provider payment/reassignment and factor restrictions with specific exceptions. No general purchase/assignment permission is inferred.
- [UCC model §9-408](https://www.law.cornell.edu/ucc/9/9-408) distinguishes effects on creating/perfecting interests from enforcement against an account debtor and access/use of underlying rights/information. State enactments and federal/contract interactions require counsel.

## Sequence and release posture
Patch and test local request/origin boundaries in Prompt 12 after this RFC, then retain synthetic-only localhost operation. Obtain methodology review and observed workflow evidence before adding operational complexity. Design enterprise controls with specialists before coding production services. No public demo deployment is authorized by this RFC, and no legal or regulatory gate is complete.
