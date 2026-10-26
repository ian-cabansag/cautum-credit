"""Build a portable, synthetic-only worked-example and future reviewer kit."""

import asyncio
import base64
import json
import zipfile
from html import escape
from pathlib import Path

from cautum.change_review import render_packet
from cautum.examples import EXAMPLES, description, example_sources
from cautum.schema import Policy
from cautum.snapshot_io import read_pair

ROOT = Path(__file__).resolve().parents[1]


def data_link(name, content, mime):
    data = base64.b64encode(content).decode()
    return f'<a download="{name}" href="data:{mime};base64,{data}">{escape(name)} ↧</a>'


def build():
    dest = ROOT / "deliverables/reviewer-kit"
    dest.mkdir(exist_ok=True)
    cards = []
    answers = {}
    for name in EXAMPLES:
        d = description(name)
        r = asyncio.run(read_pair(Policy(), None, None, "", "", False, name))
        links = []
        for side, (raw, manifest) in zip(("opening", "closing"), example_sources(name)):
            for extension, content, mime in [
                ("csv", raw, "text/csv"),
                ("json", (json.dumps(manifest, indent=2) + "\n").encode(), "application/json"),
            ]:
                filename = name + "-" + side + "." + extension
                (dest / filename).write_bytes(content)
                links.append(data_link(filename, content, mime))
        packet = render_packet(r).encode()
        filename = name + "-review.html"
        (dest / filename).write_bytes(packet)
        links.append(data_link(filename, packet, "text/html"))
        answers[name] = {
            "gross_delta": r["bridge"]["gross_ar"]["delta"],
            "base_opening": r["bridge"]["borrowing_base"]["opening"],
            "base_closing": r["bridge"]["borrowing_base"]["closing"],
            "base_delta": r["bridge"]["borrowing_base"]["delta"],
            "effects": r["change_review"]["effects"],
            "review_id": r["change_review"]["review_id"],
        }
        cards.append(
            f'<article><span class="eyebrow">CONSTRUCTED EXAMPLE</span><h2>{escape(d["title"])}</h2><p>{escape(d["story"])}</p><p><strong>Review question:</strong> {escape(d["question"])}</p><p class="note">{escape(d["meaning"])}</p><details><summary>Original sources and a worked evidence packet</summary><div class="downloads">'
            + "".join(links)
            + "</div></details></article>"
        )
    template = {
        "protocol": "change-desk-review-v1",
        "participant_role": None,
        "consent_to_share": False,
        "consent_to_quote": False,
        "observed_at": None,
        "workflow_order": None,
        "worksheet_seconds": None,
        "cautum_seconds": None,
        "assistance_used": None,
        "answers": None,
        "correctness_checked_against_reference": None,
        "missing_evidence": None,
        "confusing_steps": None,
        "would_use_again": None,
        "verbatim_feedback": None,
        "limitations": "No participant has completed this template. Record all attempts, help and errors. Self-directed timing and founder participation must be labeled.",
    }
    response = (json.dumps(template, indent=2) + "\n").encode()
    (dest / "feedback-template.json").write_bytes(response)
    key = (json.dumps(answers, indent=2) + "\n").encode()
    (dest / "reference-answers.json").write_bytes(key)
    html = (
        """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cautum | Three lender questions</title><style>@page{size:letter;margin:.6in}*{box-sizing:border-box}body{max-width:1020px;margin:50px auto;padding:0 28px;font:15px/1.65 Arial;color:#173d33;background:#f6f7f4}h1,h2{font-family:Georgia,serif;font-weight:400;line-height:1.15}h1{font-size:62px;letter-spacing:-2px;margin:22px 0}h2{font-size:30px;margin:14px 0}.eyebrow{font-size:11px;letter-spacing:1.8px;font-weight:700}article{background:white;border:1px solid #d4dfd4;padding:26px;margin:22px 0;border-radius:10px;break-inside:avoid}.note{border-left:3px solid #84a796;padding:12px 18px;background:#edf3eb;font-size:13px}a{color:inherit;text-underline-offset:3px}.downloads{display:grid;gap:10px;font-size:13px;margin:18px 0;overflow-wrap:anywhere}summary{cursor:pointer;font-weight:600}li{margin:12px 0}footer{border-top:1px solid #c5d6c8;padding:24px 0;font-size:12px}@media(max-width:600px){body{margin:24px auto;padding:0 16px}h1{font-size:42px}article{padding:20px}}</style></head><body><span class="eyebrow">CAUTUM CREDIT / REVIEWER KIT</span><h1>Can you explain<br>the change?</h1><p>Three relatable lender-review questions, with constructed aggregate source files and reproducible worked answers. These are fictional scenarios, not customer case studies. No patient information or client data is permitted.</p><p class="note">The calculation policy is illustrative and unvalidated. Model attribution does not establish cash collections, losses, legal eligibility or a lending decision. There is no claim of independent user validation.</p><article><h2>Try the workflow.</h2><ol><li>Run Cautum using the <a href="https://github.com/ian-cabansag/cautum-credit">repository README</a>. These deterministic tasks need no model key.</li><li>Open <a href="http://127.0.0.1:8000/">the local app</a>, choose <strong>Changes</strong>, then select each example from <strong>Explore a lender question</strong>.</li><li>Explain the sign of the base change, select the borrower and inspect the paired inputs. State which facts the model cannot establish.</li><li>Export the borrower evidence packet and ask another reader to reproduce the contribution from the original inputs.</li></ol></article>"""
        + "".join(cards)
        + """<article><h2>A future independent review</h2><p>No participant results are embedded in this kit. Ask a willing reviewer to record their actual role and permission before sharing any observation. A student, founder or analyst must be identified accurately.</p><p>For a paired comparison, use identical constructed inputs and policy in the reference process and Cautum. Record all preparation, timing, errors, assistance and failures. Counterbalance order across reviewers when possible. A repeated task has learning effects; one faster result does not establish causal savings.</p><p>Questions: Which answer could you not verify? Which source-owner question is missing? Which step was confusing? Would this replace a real step in your current process? What would block adoption?</p><div class="downloads">"""
        + data_link("feedback-template.json", response, "application/json")
        + """</div><details><summary>Reference answers — open after completing the tasks</summary><p>The golden values are independently asserted in tests/test_change_review.py. The observed worksheet/application timing fields remain empty until a real person completes them.</p><div class="downloads">"""
        + data_link("reference-answers.json", key, "application/json")
        + """</div></details></article><footer>Built by Ian Cabansag. Synthetic only. No data is transmitted or collected by this standalone file. No independent lender interview, operational impact or award endorsement is claimed. A useful next gate is an uncoached review by someone who performs this work.</footer></body></html>"""
    )
    (dest / "START_HERE.html").write_text(html)
    (ROOT / "cautum/static/reviewer-kit.html").write_text(html)
    archive = ROOT / "deliverables/cautum-reviewer-kit.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(dest.iterdir()):
            info = zipfile.ZipInfo(
                "cautum-reviewer-kit/" + p.name, date_time=(2026, 10, 25, 0, 0, 0)
            )
            info.external_attr = 0o100644 << 16
            z.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
    print(
        json.dumps(
            {
                "examples": len(EXAMPLES),
                "kit_files": len(list(dest.iterdir())),
                "participant_results": 0,
                "archive_bytes": archive.stat().st_size,
            }
        )
    )


if __name__ == "__main__":
    build()
