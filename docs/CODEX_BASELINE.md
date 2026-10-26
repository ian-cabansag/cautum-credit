# Baseline QA · 2026-10-25

## Scope and provenance
Read AGENTS.md, README.md and all ten supplied docs before product edits. Original source: `/Users/iancabansag/Downloads/cautum-credit`, extracted folder without Git history. Preserved unchanged. Active versioned copy: this repository under the chat's outputs. Starter snapshot commit `ea724f5`. All tests below use fictional included data, not patient records. Existing preview PNGs and prior RELEASE_NOTES claims are historical evidence, not newly verified measurements.

## Engineering understanding and sequence
Cautum is a sole-founder, lender-side review and surveillance venture. The wedge is import, reconciliation, explicit policy application, exceptions, evidence and committee preparation. Core dollars must remain deterministic Decimal outputs; AI may explain evidence and cannot approve credit. Collection estimates, policy-adjusted amounts and legal collateral rights must stay distinct. Preserve FastAPI/static frontend and the botanical green/bone/serif identity.

Work in separate commit groups: 0 baseline; 1 runtime and interaction repairs; 2 financial evidence and cent reconciliation; 3 interface/accessibility; 4 safe mapping; 5 lender review/certificates; 6 bounded AI evaluation; 7 synthetic two-period surveillance; 8 measured demonstration; 9 evidence-based course materials; 10 architecture/security review; 11 commercial experiments; 12 release verification. External validation gates remain open where evidence or authorization is absent.

## Actual commands and results
- System `python3 --version`: 3.9.6; `python3 -m pytest -q` failed because pytest is absent. This interpreter is below documented minimum.
- Bundled Python 3.12.14 used to create `.venv`; `.venv/bin/python -m pip install -r requirements-dev.txt` succeeded. Sandbox DNS initially blocked install; authorized network execution succeeded.
- `.venv/bin/python -m pytest -q`: **21 passed, 1 warning in 0.62s**. Warning: installed Starlette test client deprecates httpx transport.
- `.venv/bin/python -m uvicorn cautum.api:app --host 127.0.0.1 --port 8000`: sandbox bind initially denied; authorized loopback execution succeeded. Actual IAB browser connected, no network stubbing.
- Synthetic analysis: 192 cohorts, 8 fictional borrowers, 12 alerts, analysis `aedb9f4c941365d4`; gross $1,934,634.00; expected $1,158,846.64; collateral $952,251.49; base $761,801.19. Full response saved in `docs/evidence/baseline-analysis.json`.
- Browser: all four navigation screens loaded; search Meridian matched one borrower; Enter opened its profile; unmatched search yielded an empty tbody; CSV and JSON download events produced files; advance slider 80% to 70% showed $666.6K base with $952.3K collateral; reset restored default. Offline brief rendered, labeled rules-based with zero model tokens. A synthetic prohibited patient_name header produced visible rejection.
- 390 × 844 overview: document width 390, no horizontal page overflow; screenshot visually inspected. Browser console warning/error query returned empty list. Other sizes and every view still require phase 1/3 checks.

## Observed defects and limitations
1. Sum of rounded audit rows: expected $1,158,846.52 versus summary $1,158,846.64 (−$0.12); collateral $952,251.44 versus $952,251.49 (−$0.05). Base happens to reconcile in this sample. No general cent reconciliation guarantee.
2. Rejected upload changes dataset badge to REJECTED.CSV while old $761.8K base remains. Source file/policy state changes before success; busy actions are silently ignored. Failed-policy/network paths need transactional state handling.
3. Unmatched borrower search has no explanatory empty state. Trace visually rounds to whole dollars and omits several original input factors. Navigation labels disappear visually at narrow widths.
4. AI button remains available without credentials; missing-key test returns explicit 503. Live provider calls, generated factuality, costs and model endpoint compatibility remain **unverified**. No credentials requested or printed.
5. Rules brief lists only four flagged providers and calls that the flagged count; all eight borrowers are flagged. Needs accurate total with explicit truncation wording.

## Unverified assumptions and gates
Policy factors are fictional hypotheses. Denial/collection independence, loss calibration, enforceability, reserves, outstandings, buyer demand, user time savings and legal/privacy classification are not validated. No authentication, tenancy, durable audit, compliance attestation, live integrations or financing authority. No live model request, lender interview or real-data ingestion was performed. These are not established by passing technical tests.
