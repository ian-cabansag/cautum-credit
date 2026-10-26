# Current v0.3 architecture

The FastAPI + static frontend and Decimal engine are preserved. See the report's embedded diagram and `cautum/review_agent.py`: one real Responses investigator calls read_review_evidence over the accepted synthetic analysis, then an ID/provenance validator admits only inspected evidence. Up to two borrowers, no write/approval/raw-file/shell/browsing tools. Output wording and money are deterministic. Real Portkey runs are recorded in AI_EVALUATION.md. /study adds a consented local-memory usability exercise; no production audit storage is implied.

The details below preserve the earlier architecture discussion; statements describing v0.1 and future v0.2 model work are historical. Current limits and verified behavior are in AI_EVALUATION.md and RELEASE_MANIFEST.md.

# Architecture and future design

```text
Local operator (browser)
      │  CSV + demo policy JSON
      ▼
FastAPI upload boundary (size limit, strict schema, no PHI fields)
      │
      ├────► Parser + validation ──► immutable Receivable rows (in request memory)
      │                               │
      │                               ▼
      │                        Policy-as-code v0.1
      │                               │
      │                               ▼
      │                        Decimal math engine
      │                               │
      │                       summary / exposures / audit
      │                               │
      ├─────────────◄─────────────────┘
      │
      ├────► Offline brief (zero tokens)
      │
      └────► Optional AI analyst (only aggregate numeric output & labels)
                      │ structured response & usage tokens
                      ▼
                  HUMAN REVIEW
```

## Runtime
One FastAPI process serves HTML/CSS/JS with no frontend build, no database and no secret requirement for core mode. All uploads are handled in memory; no raw file storage. Every upload is treated as untrusted. Analyze/memo endpoints calculate from the file; frontend never submits pre-computed monetary values to overwrite authoritative results. Audit objects contain monetary row results and input source labels, not patient content.

## Contracts
`POST /api/analyze` form: file (CSV) + policy (JSON string). Responds with summary, borrowers, aging, payers, alerts, policy, trace audit rows, SHA-256-derived analysis_id. `POST /api/memo` same plus mode=offline|ai. `GET /api/status` flags AI configured; never returns secrets. `GET /api/docs` Swagger. `GET /data/synthetic_receivables.csv` public **fictional** sample only.

## Calculation integrity
Money uses a 64-digit Decimal context. Each cohort stage rounds independently HALF_UP to cents before aggregation. Original/unrounded inputs and stage adjustments are exported. Portfolio and borrower sums therefore reconcile to audit cents under the documented convention. Analysis/policy IDs hash canonical inputs, engine version and exact policy; order/equivalent Decimal formatting is stable. These are reproducible checksums, not authenticity proofs or durable immutable records.

The whole request envelope is capped before multipart parsing; its tested memory spool threshold exceeds that cap. Trusted localhost Host and Origin checks restrict browser cross-site actions. This remains a single-user synthetic prototype without auth or persistence. `POST /api/certificate` recomputes accepted input and returns a scoped illustrative HTML exhibit. `POST /api/surveillance` compares only the two bundled synthetic fixtures under one policy. The UI locally previews permitted aliases; server mapping independently enforces all eight semantic fields. Import evidence records original byte hash and mapping without raw file storage.

Optional AI now returns evidence ID selection only. Python supplies the financial wording. Read-only helper functions exist but are not registered model tools. Live gateway support remains unverified. See AI_EVALUATION.md.

## Future architecture (not implemented)
- PostgreSQL with per-tenant entities + row-level security and encrypted field storage.
- Blob store and signed uploads with malware/CSV scanning, retention schedules, deletion workflows and lineage.
- Authentication via enterprise SSO, least-privilege RBAC, auditable approvals, tenancy-scoped query tests.
- Immutable policy versions; draft, review, sign-off, effective-at dates, borrower exception overrides.
- Time-series snapshots, cohort roll-forwards, borrowing-base certificates, exception and covenant history.
- Import adapters for agreed aggregated 835 remittance and 837 claims metadata **only after** privacy/legal/data contracts.
- Segregated compute sandbox for sensitive workloads with applicable BAAs and auditing.
- Risk calibration: out-of-time validation, documented missingness, monitoring of realized recovery versus estimated collectibility.
- Event-driven background pipelines after product demand supports operational complexity.

## Model architecture choices
v0.1 is one bounded structured output call, not a fake multi-agent swarm. Deterministic data-validation and underwriting modules are 'tools' of an orchestrated workflow, but they are **not** separately generative agents. For MGT 409, describe this accurately. If building a true tool-calling model agent in v0.2, expose read-only functions `get_summary`, `get_borrower_flags` and `get_policy`, preserve bounded tool depth and disallow raw uploads/secret access. Test refusal, prompt injection and hallucination cases before deploying.
