"""Rebuild the two self-contained course submissions from recorded, attributable evidence."""

from __future__ import annotations

import argparse
import json
from base64 import b64encode
from decimal import Decimal
from html import escape
from pathlib import Path
from statistics import median

from cautum.engine import analyze
from cautum.parser import parse_csv
from cautum.pricing import AZURE_SOURCE, reference_estimate
from cautum.schema import Policy

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "docs/evidence"
COURSE = "https://zlisto.github.io/mgt_409_fa26/project_requirements.html"


def img(name, alt, cls="screen-wide"):
    path = E / name
    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    return f'<img class="{cls}" alt="{escape(alt)}" src="data:{mime};base64,{b64encode(path.read_bytes()).decode()}">'


def table(headers, rows):
    return (
        "<table><thead><tr>"
        + "".join(f"<th>{escape(str(h))}</th>" for h in headers)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in r) + "</tr>" for r in rows)
        + "</tbody></table>"
    )


def diagram():
    return """<svg class="architecture" viewBox="0 0 680 315" role="img" aria-label="CSV passes through validation and Decimal calculation. A read-only tool gives accepted evidence to one AI investigator. A validator admits only inspected IDs for human review. The model cannot change the calculation." xmlns="http://www.w3.org/2000/svg"><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7" fill="#547b65"/></marker></defs><g fill="none" stroke="#547b65" stroke-width="1.5" marker-end="url(#arrow)"><path d="M155 47 H185"/><path d="M335 47 H365"/><path d="M515 47 H545"/><path d="M610 77 V119 H435 V151"/><path d="M170 184 H287"/><path d="M287 199 H170"/><path d="M100 222 V271 H288"/><path d="M462 271 H545"/></g><g fill="#edf2eb" stroke="#a5bdac"><rect x="5" y="16" width="150" height="62" rx="5"/><rect x="185" y="16" width="150" height="62" rx="5"/><rect x="365" y="16" width="150" height="62" rx="5"/><rect x="545" y="16" width="130" height="62" rx="5"/><rect x="15" y="151" width="155" height="72" rx="5" fill="#173d33"/><rect x="287" y="151" width="250" height="72" rx="5"/><rect x="288" y="243" width="174" height="56" rx="5"/><rect x="545" y="243" width="130" height="56" rx="5"/></g><g font-family="Arial,sans-serif" font-size="13" fill="#173d33" text-anchor="middle"><text x="80" y="42">Synthetic CSV</text><text x="80" y="61" font-size="11">8 aggregate fields</text><text x="260" y="42">Strict parser</text><text x="260" y="61" font-size="11">Reject unknown data</text><text x="440" y="42">Decimal engine</text><text x="440" y="61" font-size="11">Owns every amount</text><text x="610" y="42">Accepted evidence</text><text x="610" y="61" font-size="11">Analysis + policy IDs</text><text x="92" y="179" fill="#fff">One AI investigator</text><text x="92" y="200" fill="#d9e8dd" font-size="11">gpt-6-luna / Portkey</text><text x="412" y="179">read_review_evidence</text><text x="412" y="200" font-size="11">Server dispatch / borrower facts only</text><text x="225" y="170" font-size="10">model requests</text><text x="226" y="217" font-size="10">tool returns facts</text><text x="375" y="266">ID + provenance check</text><text x="375" y="285" font-size="11">No invented or uninspected IDs</text><text x="610" y="266">Human review</text><text x="610" y="285" font-size="11">No credit approval</text></g></svg>"""


REPORT_CSS = """@page{size:letter;margin:0}*{box-sizing:border-box}body{margin:0;background:#dfe7df;color:#173d33;font:14px/1.55 Arial,sans-serif}.page{width:8.5in;height:11in;margin:24px auto;background:#f6f7f4;padding:.60in .66in;display:flex;flex-direction:column;position:relative;break-after:page;page-break-after:always}.page:last-child{break-after:auto;page-break-after:auto}.kicker{border-top:2px solid #173d33;padding-top:12px;margin-bottom:14px;font-size:10px;letter-spacing:1.3px;text-transform:uppercase}h1{font:76px/.98 Georgia,serif;letter-spacing:-3px;margin:30px 0 20px}h2{font:34px/1.12 Georgia,serif;margin:8px 0 16px;letter-spacing:-.7px}h3{font-size:15px;margin:18px 0 7px}p{margin:9px 0}.lead{font-size:17px;line-height:1.5}.coverline{font:29px/1.3 Georgia,serif}.notice{background:#e9f0e7;border-left:3px solid #84a796;padding:13px 16px;font-size:13px}.source,.caption{font-size:11px;color:#536b60;line-height:1.5}.rule{height:1px;background:#9bb6a6;margin:24px 0}table{border-collapse:collapse;width:100%;font-size:12px;margin:12px 0}th,td{text-align:left;padding:9px 8px;border-bottom:1px solid #c9d8cc;vertical-align:top}th{background:#e9f0e7;font-size:11px;color:#536b60}td{overflow-wrap:anywhere}.footer{border-top:1px solid #b8cbbd;padding-top:12px;margin-top:auto;display:flex;justify-content:space-between;font-size:9px;letter-spacing:.8px;color:#536b60}.screen-wide{width:100%;max-height:375px;object-fit:contain;display:block;margin:9px auto;border:1px solid #d3ded5}.screen-tall{display:block;width:100%;max-height:610px;object-fit:contain;margin:8px auto}.screen-compact{width:100%;max-height:180px;object-fit:contain;display:block;margin:8px auto}.screen-safety{width:100%;max-height:215px;object-fit:contain;display:block;margin:8px auto}.screen-half{width:100%;max-height:270px;object-fit:contain;display:block;margin:8px auto}.architecture{width:100%;margin:12px 0}.formula,pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#fff;border:1px solid #d3ded5;padding:13px;font:12px/1.55 monospace}a{color:inherit;text-underline-offset:2px}li{margin:10px 0}ol{padding-left:22px}.two{display:grid;grid-template-columns:1fr 1fr;gap:20px}.stat{font:45px Georgia,serif;margin:14px 0 5px;font-variant-numeric:tabular-nums}.small{font-size:12px}.print-control{position:fixed;right:14px;top:14px;z-index:100;background:#173d33;color:white;border:0;border-radius:7px;padding:12px 16px;cursor:pointer}@media(max-width:850px){.page{width:100%;height:auto;min-height:11in;padding:30px;margin:0 0 16px}.footer{margin-top:25px}.two{grid-template-columns:1fr}}@media print{body{background:white}.print-control{display:none}.page{width:8.5in;height:11in;min-height:0;margin:0;padding:.60in .66in}.footer{margin-top:auto}.two{grid-template-columns:1fr 1fr}}"""


def build(reveal_path):
    meta = json.loads((ROOT / "submission.json").read_text())
    evaluation = json.loads((E / "ai-evaluation.json").read_text())
    user = json.loads((E / "user-study.json").read_text())
    attack = json.loads((E / "live-injection.json").read_text())
    a = analyze(parse_csv((ROOT / "cautum/data/synthetic_receivables.csv").read_bytes()))
    low = analyze(
        parse_csv((ROOT / "cautum/data/synthetic_receivables.csv").read_bytes()),
        Policy(advance_rate=".7"),
    )
    qa = (
        json.loads((E / "submission-qa.json").read_text())
        if (E / "submission-qa.json").exists()
        else {}
    )
    runs = [r for r in evaluation["runs"] if r["status"] == "succeeded"]
    if not runs:
        raise ValueError("A real successful AI run is required to build the final submission.")
    standard = json.loads((E / "browser-focused-ai-receipt.json").read_text())["memo"]
    for r in runs:
        m = r["memo"]
        m["price_estimate"] = reference_estimate(
            m["usage"], m["investigation"]["calls"], m["provider"], m["model"]
        )
    costs = {
        p: median(Decimal(r["memo"]["price_estimate"]["usd"]) for r in runs if r["profile"] == p)
        for p in ("standard", "lean")
    }
    base_user = next(t for t in user["trials"] if t["condition"] == "worksheet")
    app_user = next(t for t in user["trials"] if t["condition"] == "cautum")
    author = escape(meta["author"])
    repo = escape(meta["repository_url"])
    pages = []

    def page(section, title, content, cover=False):
        pages.append((section, title, content, cover))

    def screenshot(name, alt, cls="screen-wide"):
        return img(name, alt, cls)

    live_image = "final-ai-path.png" if (E / "final-ai-path.png").exists() else "final-overview.png"
    page(
        "1. Title + links",
        "Cautum Credit",
        f'''<p class="coverline">Policy intelligence for healthcare receivables-backed credit.</p><p class="lead">A lender review workspace that connects deterministic collateral calculations to source evidence and gives one AI investigator bounded, read-only tools.</p><div class="rule"></div><p><strong>{author}</strong><br>MGT 409 · AI Foundations for Managers<br>October 25, 2026 · v0.3.0</p><p>Repository: <a href="{repo}">{repo}</a><br>Delivery: local clone. No hosted application.<br>After startup: <a href="http://127.0.0.1:8000">http://127.0.0.1:8000</a></p><p class="notice">Synthetic data only. Financial policy factors are unvalidated. This is review software, not a lender, credit approval system, validated valuation model or compliance attestation.</p><p>Evidence includes real Portkey tool-calling runs, provider token counts, live and automated safety checks, and a consented founder exercise that did not demonstrate faster review.</p><p class="source">Prepared against the <a href="{COURSE}">published final-project requirements</a>. Every screenshot, diagram, script and style is embedded in this file. The accompanying repository preserves raw evidence and reproduction scripts.</p>''',
        True,
    )
    page(
        "2. Motivation",
        "The problem is reconstructing the answer",
        """<p class="lead">A specialty healthcare lender needs to know how a reported receivables balance became an illustrative borrowing base, and which assumptions deserve follow-up.</p><p>The proposed user is a credit analyst overseeing several provider borrowers. Their review must distinguish billed charges, modeled allowed amounts, collection assumptions, policy reductions and advance rates. A portfolio manager also needs a reproducible comparison between reporting periods.</p><h3>The current-workflow hypothesis</h3><p>Spreadsheets and existing asset-based lending systems are the baseline. The pain to investigate is repeated evidence reconstruction: matching a flag to its source rows, applying the correct policy version, and preparing a review note someone else can check. No lender interview has established how frequent or costly this problem is.</p>"""
        + table(
            ["Review question", "Implemented response", "Commercial proof still needed"],
            [
                [
                    "What changed the amount?",
                    "Gross-to-base bridge and exact cohort trace",
                    "Independent policy/workbook agreement",
                ],
                [
                    "What needs attention?",
                    "Borrower queue and source-linked exceptions",
                    "Expert assessment of useful/missed risks",
                ],
                [
                    "What did AI actually inspect?",
                    "Tool receipt and accepted evidence IDs",
                    "Analyst judgment of prioritization value",
                ],
                [
                    "Can I reproduce the result?",
                    "CSV/JSON/certificate exports and fingerprints",
                    "Adoption in an approved lender workflow",
                ],
            ],
        )
        + f"""<h3>A real observation, with a narrow conclusion</h3><p>Founder {author} completed two synthetic tasks correctly. Worksheet: {base_user["elapsed_seconds"]:.2f}s. Cautum: {app_user["elapsed_seconds"]:.2f}s. The exercise does not support a speed-saving claim. It gives an initial usability observation and a concrete reason to test onboarding and evidence navigation with independent analysts.</p><p class="notice">No paying customer, lender endorsement, financing volume, measured buyer pain cost or provider benefit is claimed. The business model remains a lender subscription/implementation hypothesis.</p>""",
    )
    page(
        "3. What is new here",
        "A specific workflow in an existing market",
        """<p>Named primary product pages were reviewed on October 25, 2026. Their descriptions establish meaningful overlap; they do not establish independently verified performance.</p>"""
        + table(
            ["Existing option", "Public positioning / overlap", "Cautum distinction to test"],
            [
                [
                    "Orcho",
                    "Receivables review and monitoring supporting lender conversations",
                    "Cross-borrower, versioned policy evidence; overlap is substantial",
                ],
                [
                    "Klaim",
                    "Healthcare treasury, forecasts, receivables acceleration and recovery",
                    "Independent lender review; no purchase, financing or collection execution",
                ],
                [
                    "MedLiquidity",
                    "Claims valuation, underwriting, monitoring and securitization",
                    "A narrower auditable aggregate-cohort review demonstration",
                ],
                [
                    "Spreadsheets / ABL systems",
                    "The incumbent calculation and review workflow",
                    "Source-linked investigation and explicit review receipts",
                ],
                [
                    "Generic ChatGPT interaction",
                    "Flexible explanation of supplied information",
                    "Server-owned exact financial math and validation of inspected evidence IDs",
                ],
            ],
        )
        + """<h3>What is implemented</h3><p>The application combines visible policy factors, cohort-level cent reconciliation, exception-to-source navigation, dated synthetic monitoring and a tool-using AI investigator. The investigator can choose a borrower to inspect, but it cannot invent delivered financial wording, change amounts or approve credit.</p><h3>What is not established</h3><p>This combination is a product hypothesis, not a proven moat. Switching value depends on data compatibility, credit-officer agreement and a workflow benefit that exceeds the integration and governance burden. Aggregate data may be insufficient for the intended buyer.</p><p class="source">Primary sources: <a href="https://www.orcho.ai/product">Orcho product</a>; <a href="https://klaim.com/">Klaim</a>; <a href="https://www.medliquidity.com/">MedLiquidity</a>. Public company claims are attributed, not endorsed. No comparative accuracy or traction claim is reproduced.</p>""",
    )
    page(
        "4. The agents",
        "One investigator, bounded authority",
        """<p class="lead">The model chooses where to look. The server controls what it can read and what can appear in the final review.</p>"""
        + diagram()
        + table(
            ["Component", "Actual authority"],
            [
                [
                    "Parser + Decimal engine",
                    "Validate eight aggregate fields; calculate from original rates and policy; reconcile cohort cents",
                ],
                [
                    "AI investigator",
                    "Request borrower evidence and select supported risk/question IDs",
                ],
                [
                    "read_review_evidence",
                    "Return exact borrower amounts, policy exceptions and a bounded calculation sample from the accepted analysis",
                ],
                [
                    "Output validator",
                    "Reject new IDs, uninspected IDs, duplicates, extra prose, false review status and unsupported actions",
                ],
                [
                    "Human",
                    "Assess completeness, policy validity, legal eligibility and any actual credit decision",
                ],
            ],
        )
        + """<p>Course requests specify <strong>gpt-6-luna</strong> through Portkey. Live responses reported <strong>gpt-6-luna-global</strong> and the gateway reported <strong>azure-openai</strong>. Luna fits this small evidence-selection task; no cross-model superiority claim is made. Reasoning is disabled for this route after bounded low-reasoning runs exhausted their output cap.</p><p class="source">Official implementation reference: <a href="https://developers.openai.com/api/docs/guides/function-calling">OpenAI function calling</a>. The application uses actual function-call/output round trips, not relabeled ordinary helper functions.</p>""",
    )
    steps = []
    for t in standard["investigation"]["trace"]:
        steps.append(
            [
                str(t["step"]),
                t["result"]["provider"],
                f"{len(t['result']['flags'])} flags; {t['result']['coverage']['cohorts_returned']} of {t['result']['coverage']['borrower_cohorts']} cohorts",
                t["tool"],
            ]
        )
    page(
        "4. The agents / one real run",
        "What the investigator actually did",
        f"""<p>Recorded browser run, payer-concentration focus: analysis <code>{a["analysis_id"]}</code>; policy <code>{a["policy_id"]}</code>. The broader profile made two read-only tool calls and a final schema-constrained selection. The receipt records gateway cache status for each request. Equivalent cached responses are not counted as independent generations.</p>"""
        + table(
            ["Step", "Borrower chosen by model", "Server evidence returned", "Actual tool"], steps
        )
        + screenshot(
            live_image,
            "Actual live AI investigation with borrower evidence and source links",
            "screen-half",
        )
        + f"""<p>Accepted rule evidence: <code>{escape(", ".join(x for x in standard["evidence_ids"] if x.startswith("risk:")))}</code>. The final delivered figures and wording come from the numeric engine and evidence catalog. New financial prose is rejected.</p><p>At this run: {standard["usage"]["input_tokens"]:,} input, {standard["usage"]["cached_input_tokens"]:,} cached-input and {standard["usage"]["output_tokens"]:,} output tokens; {standard["latency_ms"]:,.2f}ms total. This is a real run, not a simulated conversation.</p><p class="source">Evidence: docs/evidence/browser-focused-ai-receipt.json; this screenshot and trace describe the same actual browser run. The separate paired benchmark uses general-review focus and unique evaluation IDs, so its token counts and selections differ. The full tool/usage receipt is exportable from the app.</p>""",
    )
    page(
        "4. The agents / financial authority",
        "The financial answer remains reproducible",
        screenshot(
            "final-overview.png",
            "Actual application overview with cent-reconciling financial stages",
            "screen-compact",
        )
        + table(["Stage", "USD, exact cohort cents"], list(a["summary_exact"].items()))
        + """<p class="formula">N = G × (1 − contract)<br>E = N × collection × (1 − denial)<br>C = E × aging factor × payer factor<br>B = C × advance rate</p><p>Each stage uses the full original Decimal chain, rounds each cohort HALF_UP to cents, then aggregates. Intermediate rounded values are not chained. Original inputs, unrounded results, adjustments and policy reasons remain inspectable.</p>"""
        + f"""<p>Changing advance from 80% to 70% changes the illustrative base from $761,801.19 to ${low["summary"]["borrowing_base"]:,.2f}; policy-adjusted collateral remains $952,251.44. These are fictional sensitivity factors, not lender standards.</p><p class="notice">Collection factors and denial rates may double-count losses. “Policy-adjusted collateral” does not establish legally enforceable collateral. Reserves, debt outstandings and net undrawn availability are unassessed.</p>""",
    )
    token_rows = []
    for p in ("standard", "lean"):
        v = evaluation["summary"][p]
        token_rows.append(
            [
                p,
                f"{v['succeeded']}/{v['attempted']}",
                f"{v['median_input_tokens']:,}",
                f"{v['median_cached_tokens']:,}",
                f"{v['median_output_tokens']:,}",
                f"${costs[p]:.7f}",
            ]
        )
    page(
        "5. Tokenomics",
        "Measured tokens, explicit pricing assumptions",
        """<p class="lead">Six fresh completed reviews, three per profile. Same bundled portfolio and general-review task; sequential paired order alternated by pair.</p>"""
        + table(
            ["Profile", "Complete", "Median input", "Cached input", "Output", "Model cost / run"],
            token_rows,
        )
        + """<p>All 15 final-evaluation upstream responses reported gateway MISS; response IDs are distinct. No retries were made by the SDK; observed gateway retry counts were zero. A separate cached-request experiment is retained and is not counted as independent model generations.</p><p class="formula">Cost = ((input − cached) × input rate + cached × cached rate + output × output rate) / 1,000,000</p><p>Published Azure GPT-6 Luna Global Standard short-context reference rates: $0.10 input, $0.01 cached input, $0.50 output per million tokens. No cache-write option was requested. These are measured-token model-cost estimates, not an invoice or verification of the course gateway contract.</p>"""
        + table(
            ["Illustrative monthly workload", "Broader profile", "Quick profile"],
            [
                [
                    "1 reviewer × 50 reviews",
                    f"${costs['standard'] * 50:.5f}",
                    f"${costs['lean'] * 50:.5f}",
                ],
                [
                    "100 reviewers × 50 reviews",
                    f"${costs['standard'] * 5000:.3f}",
                    f"${costs['lean'] * 5000:.3f}",
                ],
                [
                    "10,000 reviewers × 50 reviews",
                    f"${costs['standard'] * 500000:.2f}",
                    f"${costs['lean'] * 500000:.2f}",
                ],
            ],
        )
        + f'''<p class="notice">50 reviews/user/month is a disclosed planning assumption, not observed usage. Scale rows are arithmetic scenarios, not a demonstrated capacity. Hosting, gateway fees/discounts, failed calls, support, integration and enterprise controls are additional, unmeasured costs. The current local demo is not an enterprise deployment.</p><p class="source">Rates: <a href="{AZURE_SOURCE}">Microsoft's GPT-6 Global Standard pricing table</a>, verified October 25, 2026. Actual provider/gateway usage and route metadata are retained in ai-evaluation.json.</p>''',
    )
    reduction = (Decimal(1) - costs["lean"] / costs["standard"]) * 100
    page(
        "5. Tokenomics / quality tradeoff",
        "The cheaper review sees less",
        f"""<div class="two"><div><p class="stat">{reduction:.1f}%</p><p>Lower median model-cost estimate for the quick profile.</p></div><div><p class="stat">3 vs 5</p><p>Existing rule flags selected, out of 12. Quick versus broader profile.</p></div></div>"""
        + table(
            ["Control", "Broader profile", "Quick profile"],
            [
                ["Borrower evidence calls", "At most 2", "At most 1"],
                ["Calculation rows per borrower", "At most 4", "At most 2"],
                ["Upstream requests", "At most 3", "At most 2"],
                ["Output cap per request", "1,200 tokens", "600 tokens"],
                ["Median selected rule-flag coverage", "41.7%", "25.0%"],
            ],
        )
        + """<p>The lower-cost configuration reduced source coverage in this synthetic sample. Every admitted ID was validated against inspected tool results. That admission rule does not prove that the selected flags were the most useful, that all material risks were found, or that real credit outcomes improve.</p><h3>Failures informed the final design</h3><p>Earlier runs repeated a borrower or exhausted an output cap. The runner rejected them. The final tool schema removes inspected borrowers from its allowed IDs; focused Luna requests use reasoning effort none. Failure records remain in ai-evaluation-before-repair.json and ai-evaluation-output-cap-failures.json.</p><h3>Spending and latency bounds</h3><p>32,000-character transcript bound; 16,000-character tool-result bound; one tool call per turn; 30-second per-request timeout within a 60-second review deadline; zero SDK retries; default 25 upstream attempts per server process. Process budgets reset on restart and require external quotas for production.</p><p class="notice">Earlier gateway cache HITs replayed response IDs and token counts. Cached observations are separated from fresh generation results. Gateway billing and complete account spend remain unverified.</p>""",
    )
    page(
        "6. Safety",
        "Defenses that actually ran",
        screenshot(
            "demo-rejection.jpg", "Actual prohibited patient_name-header rejection", "screen-safety"
        )
        + table(
            ["Risk", "Implemented defense", "Observed evidence"],
            [
                [
                    "Unexpected sensitive fields",
                    "Exact fields/aliases; bounded whole request before multipart parsing",
                    "Browser rejection screenshot and backend tests",
                ],
                [
                    "Invented financial claims or actions",
                    "Only inspected risk/question IDs; deterministic delivered financial text",
                    "Mocked unsupported-ID/extra-prose/approval rejection tests",
                ],
                [
                    "Tool misuse / repeated reads",
                    "Strict tool name and argument schemas; exclude already-inspected borrowers",
                    "Actual rejected repeats informed repaired dispatch",
                ],
                [
                    "Injection through labels",
                    "Labels treated as data; no write, browsing, shell or approval tools",
                    "Live instruction-like synthetic label exercise retained",
                ],
                [
                    "Overspending / loops",
                    "Per-call, per-run and process bounds; no automatic SDK retries",
                    "Bound exhaustion and timeout tests",
                ],
            ],
        )
        + f"""<p>Live injection exercise result: <strong>{escape(attack["status"])}</strong>. The model selected supported evidence with human review required, and delivered financial summary wording stayed identical to the deterministic engine. This single exercise does not prove universal injection resistance.</p><p class="notice">The allowlist cannot certify absence of PHI. The local app has no enterprise authentication, tenant isolation or immutable operational audit. Real healthcare files and credit decisions remain outside its permitted use.</p><p class="source">Evidence: tests/test_review_agent.py, test_boundary.py, test_security.py; docs/evidence/live-injection.json. Mocked provider tests are identified as mocks, not live model results.</p>""",
    )
    page(
        "7. Impact",
        "Correct answers, no speed gain",
        screenshot(
            "founder-observation.png",
            "Actual recorded founder timing, correct answers and consented feedback",
            "screen-half",
        )
        + table(
            ["Observed measure", "Worksheet case A", "Cautum case B"],
            [
                [
                    "Browser-recorded elapsed time",
                    f"{base_user['elapsed_seconds']:.2f} seconds",
                    f"{app_user['elapsed_seconds']:.2f} seconds",
                ],
                [
                    "Borrowing-base answer",
                    f"${base_user['base_answer']} — correct",
                    f"${app_user['base_answer']} — correct",
                ],
                ["Excluded aging bucket", "91+ — correct", "91+ — correct"],
                ["Additional help", "None, self-reported", "None, self-reported"],
            ],
        )
        + f"""<p>Participant: {author}, founder/project author; consent recorded. Clarity: {user["clarity"]}/5. Would use again: {escape(user["reuse"])}. Feedback, faithfully quoted: <strong>“{escape(user["feedback"])}”</strong>.</p><p>Cautum took {app_user["elapsed_seconds"] - base_user["elapsed_seconds"]:.2f} seconds longer in this exercise. No time saving is claimed. Next test: distinguish tab-switching/onboarding time from evidence-reconstruction time and observe independent analysts on larger, comparable tasks.</p><p class="notice">One founder, two different synthetic cases, worksheet first; learning, order and case effects are unresolved. Timing is browser-recorded and not independently observed. This is not an independent buyer pilot, statistical estimate, lender validation or evidence of customer demand.</p><p class="source">Raw participant submission: docs/evidence/user-study.json. Sample data: study_A.csv and study_B.csv. The in-app exercise at /study can reproduce the protocol.</p>""",
    )
    page(
        "8. Limits + next steps",
        "The next month should earn trust",
        table(
            ["Week", "Evidence-producing work", "Acceptance gate"],
            [
                [
                    "1",
                    "Independent lender-authored synthetic workbook; agree rate denominators and cent convention",
                    "Resolve every material discrepancy and policy disagreement",
                ],
                [
                    "2",
                    "Observe 3–5 independent reviewers using counterbalanced cases",
                    "Record timing, errors, help, missed risks and source-navigation problems",
                ],
                [
                    "3",
                    "Evaluate AI prioritization against expert-labeled exceptions; inspect misses and cost controls",
                    "Report coverage/quality/cost together; no credit-accuracy claim without labels",
                ],
                [
                    "4",
                    "Resolve data rights and legal/security design; test buyer willingness to adopt",
                    "Permissioned scope and credible procurement decision before real data",
                ],
            ],
        )
        + """<h3>Financial limits</h3><p>Fictional recovery and policy factors; possible double discounting; no reserves, outstandings, disputes, recoupment, actual cash-remittance reconciliation or legal eligibility determination. The two-period study uses fictional fixtures and cannot establish cash collections or causal aging migration.</p><h3>Product and commercial limits</h3><p>No EHR, claims clearinghouse, payer or banking integration. No paying customer, pricing validation, independent lender approval or defensible switching advantage. The founder observation did not show improved speed.</p><h3>Security and operational limits</h3><p>Localhost-only, single-user, memory-only. No authenticated policy approvals, tenant controls, production retention/deletion system, signed durable audit, external quotas or incident response operation. Fingerprints are reproducible checksums, not signatures or compliance proof.</p><p class="notice">The long-term healthcare credit-infrastructure thesis remains conditional on real demand, credible methodology, permissioned evidence and specialist counsel. An attractive demonstration does not satisfy those gates.</p>""",
    )
    checks = [
        [
            "Code and sample data",
            "Repository with README, pinned runtime/development dependencies and synthetic fixtures",
        ],
        [
            "Financial provenance",
            f"Analysis {a['analysis_id']}; policy {a['policy_id']}; Decimal cohort-cent convention",
        ],
        [
            "Automated verification",
            f"{qa.get('tests_passed', 'See release evidence')} tests passed; lint/format and frontend rate contract checks",
        ],
        [
            "Live AI",
            "Six fresh final paired runs; actual model/tool/usage receipts; earlier failures retained",
        ],
        [
            "User evidence",
            "Consented founder observation; correct answers, slower app task, no independent lender claim",
        ],
        [
            "Delivery",
            "Two embedded HTML files; local-clone startup; no secret required for deterministic mode",
        ],
    ]
    page(
        "8. Limits + next steps / reproduction",
        "A reviewer can check the work",
        table(["Evidence", "Reproduction / source"], checks)
        + """<h3>Run the application</h3><pre>git clone https://github.com/ian-cabansag/cautum-credit.git
cd cautum-credit
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn cautum.api:app --host 127.0.0.1 --port 8000</pre><p>On Windows activate with .venv\\Scripts\\Activate.ps1. Python 3.12/macOS was tested; other environments must be checked separately. The course .env may sit in the repo or one folder above it; process environment takes precedence. Core mode needs no key.</p><h3>Verify and reproduce the evidence</h3><p>Install requirements-dev.txt, run pytest/Ruff and scripts.check_release using the exact README commands. scripts.evaluate_ai records actual authorized requests; scripts.build_evidence_package rebuilds these exhibits from saved evidence.</p><p class="source">See README.md, docs/RELEASE_MANIFEST.md and docs/COURSE_EVIDENCE.md for release checks and known limits. No secret belongs in the repository or either HTML file.</p>""",
    )
    html = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cautum Credit | Ian Cabansag | Report</title><style>'
        + REPORT_CSS
        + '</style></head><body><button class="print-control" onclick="window.print()">Print report</button>'
    )
    for i, (section, title, content, cover) in enumerate(pages, 1):
        html += f'<article class="page"><div class="kicker">Cautum Credit / {escape(section)}</div><h{1 if cover else 2}>{title}</h{1 if cover else 2}>{content}<footer class="footer"><span>SYNTHETIC DEMONSTRATION / HUMAN REVIEW REQUIRED</span><span>{i:02} / {len(pages):02}</span></footer></article>'
    (ROOT / "deliverables/report.html").write_text(html + "</body></html>")
    standard_tokens = evaluation["summary"]["standard"]
    lean_tokens = evaluation["summary"]["lean"]
    slides = [
        (
            "Cautum Credit",
            f'<p class="big">Policy intelligence for healthcare receivables-backed credit</p><p>Deterministic financial evidence.<br>One bounded, tool-using AI investigator.</p><p class="small">{author} · MGT 409 · October 25, 2026<br>Synthetic local demonstration</p>',
        ),
        (
            "The analyst must reconstruct the answer",
            '<p class="big">Which source rows and policy assumptions changed this borrowing base?</p><p>Proposed buyer: a specialty healthcare lender reviewing several provider borrowers.</p><p>Current baseline: spreadsheets and existing ABL systems. Repeated evidence reconstruction is the workflow hypothesis to test.</p><p class="small">No independent buyer interview or measured lender pain cost yet.</p>',
        ),
        (
            "Existing products overlap",
            '<p>Orcho: receivables review and monitoring.<br>Klaim: healthcare treasury, acceleration and recovery.<br>MedLiquidity: valuation, underwriting and monitoring.</p><p class="big">Cautum tests visible policy evidence and source-linked borrower investigation.</p><p class="small">A differentiation hypothesis, not a proven moat. Primary product pages are linked in the report.</p>',
        ),
        (
            "The model chooses where to look",
            diagram()
            + '<p class="small">One agent, one read-only tool. Financial calculations remain in Python. Course model: gpt-6-luna; observed route: Azure through Portkey.</p>',
        ),
        (
            "A real investigation, with a receipt",
            screenshot(live_image, "Actual live AI investigation", "slide-screen")
            + '<p class="small">The model requests borrower evidence; the server returns exact sources. Only inspected evidence IDs can enter the final review.</p>',
        ),
        (
            "Every financial stage reconciles",
            screenshot(
                "final-overview.png", "Actual overview with exact financial bridge", "slide-screen"
            )
            + '<p class="small">192 fictional cohorts · 8 borrowers · $761,801.19 illustrative base.<br>70% advance scenario: $666,576.03. Policy factors remain unvalidated.</p>',
        ),
        (
            "A cheaper pass selects fewer flags",
            table(
                ["Fresh-run median", "Broader", "Quick"],
                [
                    [
                        "Input / cached / output",
                        f"{standard_tokens['median_input_tokens']:,} / {standard_tokens['median_cached_tokens']:,} / {standard_tokens['median_output_tokens']:,}",
                        f"{lean_tokens['median_input_tokens']:,} / {lean_tokens['median_cached_tokens']:,} / {lean_tokens['median_output_tokens']:,}",
                    ],
                    ["Model cost estimate", f"${costs['standard']:.7f}", f"${costs['lean']:.7f}"],
                    ["Existing flags selected", "5 of 12", "3 of 12"],
                ],
            )
            + f'<p>At 50 reviews/user/month and 100 users: ${costs["standard"] * 5000:.3f} broader / ${costs["lean"] * 5000:.3f} quick.</p><p class="small">Three fresh runs/profile. Published Azure model rates × observed tokens; excludes gateway fees, hosting and support. Coverage is not expert-validated accuracy.</p>',
        ),
        (
            "A working rejection boundary",
            screenshot("demo-rejection.jpg", "Actual unknown-header defense", "slide-screen")
            + '<p class="small">Unknown fields reject. Tool misuse and unsupported outputs reject. A live synthetic injection retained human review and unchanged deterministic financial wording. No universal PHI or injection guarantee.</p>',
        ),
        (
            "Correct answers; no speed gain",
            table(
                ["Founder exercise", "Worksheet", "Cautum"],
                [
                    ["Browser time", "76.89 s", "132.53 s"],
                    ["Base and aging answers", "Both correct", "Both correct"],
                ],
            )
            + f'<p class="big">“{escape(user["feedback"])}”</p><p>Clarity {user["clarity"]}/5. Would use again: {escape(user["reuse"])}.</p><p class="small">One consenting founder, different synthetic cases, worksheet first. Timing is not independently observed. This does not demonstrate analyst time savings or buyer adoption.</p>',
        ),
        (
            "The next proof is independent use",
            f'<p class="big">Agree the math.<br>Observe analysts.<br>Measure useful evidence.</p><p>Then earn data permission, legal feasibility and enterprise operating controls.</p><p class="small">Run locally from <a href="{repo}">{repo}</a><br>Python + FastAPI; included synthetic data. No key needed for core mode.</p>',
        ),
    ]
    js = (reveal_path / "dist/reveal.js").read_text().replace("</script", "<\\/script")
    css = (reveal_path / "dist/reveal.css").read_text()
    custom = """body{background:#f6f7f4;color:#173d33}.reveal{font:28px Arial,sans-serif}.reveal .slides{text-align:left}.reveal .slides section{padding:25px 40px;box-sizing:border-box}.reveal h2{font:52px/1.12 Georgia,serif;letter-spacing:-1px;margin:0 0 28px}.reveal p{line-height:1.5;margin:22px 0}.reveal .big{font-size:36px;line-height:1.4}.reveal .small{font-size:20px;line-height:1.45;color:#536b60}.reveal .slide-screen{display:block;max-height:465px;max-width:100%;object-fit:contain;margin:auto}.reveal .architecture{max-height:405px;width:100%}.reveal table{font-size:25px;border-collapse:collapse;width:100%;margin:24px 0}.reveal th,.reveal td{padding:15px;border-bottom:1px solid #a9bfaf;text-align:left}.reveal th{font-size:20px;color:#536b60}.reveal .chapter{font-size:16px;letter-spacing:2px;color:#536b60;margin-bottom:20px}.reveal a{color:#173d33}.reveal .controls,.reveal .progress{color:#173d33}.slide-number{color:#173d33!important;background:transparent!important}"""
    deck = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cautum Credit | Ian Cabansag | Slides</title><style>'
        + css
        + custom
        + '</style></head><body><div class="reveal"><div class="slides">'
    )
    deck += "".join(
        f'<section><div class="chapter">CAUTUM CREDIT / {i:02}</div><h2>{title}</h2>{content}</section>'
        for i, (title, content) in enumerate(slides, 1)
    )
    deck += (
        "</div></div><script>"
        + js
        + '</script><script>Reveal.initialize({hash:true,transition:"none",width:1280,height:800,margin:.06,slideNumber:"c/t",center:false,controls:true,progress:true});</script></body></html>'
    )
    (ROOT / "deliverables/slides.html").write_text(deck)
    print(
        json.dumps(
            {
                "report_pages": len(pages),
                "slides": len(slides),
                "author": meta["author"],
                "real_ai_runs": len(runs),
                "images_embedded": True,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reveal-path", type=Path, default=ROOT / "deliverables/vendor/reveal-6.0.2"
    )
    build(parser.parse_args().reveal_path)
