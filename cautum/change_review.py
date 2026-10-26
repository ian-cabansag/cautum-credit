"""Exact, fixed-order model variance explanations, never causal cash attribution."""

from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from html import escape

from .engine import cents, stable_hash
from .parser import DataError

METHOD = "sequential-cohort-cents-v1"
FIELDS = (
    ("gross_ar", "Balance"),
    ("contractual_adjustment_rate", "Contract adjustment"),
    ("historical_collection_factor", "Collection assumption"),
    ("denial_rate", "Denial assumption"),
)
LABELS = dict(FIELDS) | {"added": "Added cohorts", "removed": "Removed cohorts"}
CAUTION = (
    "Fixed-order model attribution, not causal attribution. Interactions belong to the later "
    "factor in this order: balance, contract adjustment, collection, denial. Both periods use "
    "one policy. Aging buckets match identities, not individual claims; movements do not prove "
    "migration, cash receipts or actual losses. Reserves, debt and legal eligibility remain unassessed."
)


def _key(s, r):
    m = s["manifest"]
    return m["borrower_ids"][r["provider"]], m["payer_ids"][r["payer"]], r["age"]


def _source(row):
    if row is None:
        return None
    source = {
        k: row[k]
        for k in (
            "cohort_id",
            "provider",
            "payer",
            "type",
            "age",
            "inputs_exact",
            "amounts_exact",
            "unrounded",
            "formula",
            "policy_id",
            "engine_version",
        )
    }
    source["factors_exact"] = {
        k: format(Decimal(str(row[k])), "f")
        for k in ("aging_factor", "payer_factor", "advance_rate")
    }
    return source


def _base(inputs, row):
    return cents(
        Decimal(inputs["gross_ar"])
        * (1 - Decimal(inputs["contractual_adjustment_rate"]))
        * Decimal(inputs["historical_collection_factor"])
        * (1 - Decimal(inputs["denial_rate"]))
        * Decimal(str(row["aging_factor"]))
        * Decimal(str(row["payer_factor"]))
        * Decimal(str(row["advance_rate"]))
    )


def _row_effects(old, new):
    effects = {k: Decimal(0) for k in LABELS}
    steps = []
    if old is None:
        effects["added"] = Decimal(new["amounts_exact"]["borrowing_base"])
    elif new is None:
        effects["removed"] = -Decimal(old["amounts_exact"]["borrowing_base"])
    else:
        inputs = dict(old["inputs_exact"])
        value = Decimal(old["amounts_exact"]["borrowing_base"])
        for field, _ in FIELDS:
            start, finish = inputs[field], new["inputs_exact"][field]
            inputs[field] = finish
            next_value = _base(inputs, old)
            effects[field] = next_value - value
            if Decimal(start) != Decimal(finish):
                steps.append(
                    {
                        "field": field,
                        "from": start,
                        "to": finish,
                        "base_before": format(value, ".2f"),
                        "base_after": format(next_value, ".2f"),
                        "effect": format(next_value - value, ".2f"),
                    }
                )
            value = next_value
        if value != Decimal(new["amounts_exact"]["borrowing_base"]):
            raise DataError("Model factor mismatch: comparison cannot be attributed safely.")
    return effects, steps


def build_review(before, after, comparison):
    with localcontext() as ctx:
        ctx.prec = 64
        return _build(before, after, comparison)


def _build(before, after, comparison):
    left = {_key(before, r): r for r in before["analysis"]["audit"]}
    right = {_key(after, r): r for r in after["analysis"]["audit"]}
    effects = {k: Decimal(0) for k in LABELS}
    borrowers = {}
    rows = []
    for movement in comparison["movements"]:
        key = movement["borrower_id"], movement["payer_id"], movement["age"]
        old, new = left.get(key), right.get(key)
        parts, steps = _row_effects(old, new)
        delta = Decimal(movement["delta_exact"]["borrowing_base"])
        if sum(parts.values()) != delta:
            raise DataError("Cohort attribution failed cent reconciliation.")
        row = {
            **movement,
            "before": _source(old),
            "after": _source(new),
            "effects": {k: format(v, ".2f") for k, v in parts.items()},
            "steps": steps,
        }
        rows.append(row)
        bid = key[0]
        if bid not in borrowers:
            borrowers[bid] = {
                "borrower_id": bid,
                "provider": movement["provider"],
                "opening": Decimal(0),
                "closing": Decimal(0),
                "effects": defaultdict(Decimal),
                "counts": Counter(),
                "cohort_keys": [],
                "changed_inputs": set(),
            }
        b = borrowers[bid]
        b["opening"] += Decimal(old["amounts_exact"]["borrowing_base"]) if old else 0
        b["closing"] += Decimal(new["amounts_exact"]["borrowing_base"]) if new else 0
        b["counts"][movement["status"]] += 1
        b["cohort_keys"].append([key[1], key[2]])
        b["changed_inputs"].update(s["field"] for s in steps)
        for k, v in parts.items():
            effects[k] += v
            b["effects"][k] += v
    queue = []
    for b in borrowers.values():
        changed = b.pop("changed_inputs")
        questions = []
        if "denial_rate" in changed:
            questions.append(
                "Confirm the changed denial-rate denominator and reporting period; check overlap with collection losses."
            )
        if "historical_collection_factor" in changed:
            questions.append(
                "Reconcile the collection assumption to its source definition; verify that denial losses are not counted twice."
            )
        if "contractual_adjustment_rate" in changed:
            questions.append(
                "Verify the changed contractual adjustment against the synthetic source schedule and payer classification."
            )
        if b["counts"]["added"] or b["counts"]["removed"]:
            questions.append(
                "Reconcile added and removed identities; do not classify unmatched balances as collections or aging migration."
            )
        questions.append(
            "Reconcile balance changes to the source schedules; cash receipts cannot be inferred from this comparison."
        )
        delta = b["closing"] - b["opening"]
        negative = [(k, v) for k, v in b["effects"].items() if v < 0]
        primary = min(negative, key=lambda item: (item[1], item[0]))[0] if negative else None
        queue.append(
            {
                **b,
                "opening": format(b["opening"], ".2f"),
                "closing": format(b["closing"], ".2f"),
                "delta": format(delta, ".2f"),
                "effects": {k: format(b["effects"][k], ".2f") for k in LABELS},
                "counts": dict(b["counts"]),
                "changed_inputs": sorted(changed),
                "primary_decrease": primary,
                "questions": questions,
            }
        )
    queue.sort(key=lambda b: (Decimal(b["delta"]), b["borrower_id"]))
    delta = Decimal(comparison["bridge"]["borrowing_base"]["delta"])
    if sum(effects.values()) != delta or sum(Decimal(b["delta"]) for b in queue) != delta:
        raise DataError("Portfolio attribution failed cent reconciliation.")
    review_id = stable_hash(
        {
            "method": METHOD,
            "policy": comparison["policy_id"],
            "opening": before["analysis"]["analysis_id"],
            "closing": after["analysis"]["analysis_id"],
            "sources": [before["snapshot_hash"], after["snapshot_hash"]],
        }
    )[:16]
    return {
        "review_id": review_id,
        "method": METHOD,
        "method_note": CAUTION,
        "driver_labels": LABELS,
        "effects": {k: format(v, ".2f") for k, v in effects.items()},
        "reconciled": True,
        "unexplained_model_delta": "0.00",
        "borrowers": queue,
        "declining_borrowers": sum(Decimal(b["delta"]) < 0 for b in queue),
        "rows": rows,
    }


def render_packet(comparison, borrower=""):
    """Standalone server-generated evidence packet, regenerated from validated source files."""
    review = comparison["change_review"]
    selected = [b for b in review["borrowers"] if not borrower or b["borrower_id"] == borrower]
    if not selected:
        raise DataError("Borrower is not present in this accepted comparison.")
    ids = {b["borrower_id"] for b in selected}
    rows = [r for r in review["rows"] if r["borrower_id"] in ids]
    esc = lambda x: escape(str(x), quote=True)
    usd = lambda x: f"${Decimal(x):,.2f}"
    out = [
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cautum change review</title><style>@page{size:letter;margin:.6in}body{max-width:1000px;margin:40px auto;padding:0 24px;font:14px/1.5 Arial;color:#173d33}h1,h2{font-family:Georgia,serif}h1{font-size:38px}table{width:100%;border-collapse:collapse;font-size:12px}td,th{text-align:left;border-bottom:1px solid #ccd8cf;padding:8px;vertical-align:top;overflow-wrap:anywhere}p,code{overflow-wrap:anywhere}.note{background:#edf2eb;padding:15px}article{break-inside:avoid;border-top:2px solid #173d33;margin-top:32px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:11px}@media print{body{margin:0;padding:0}}</style><h1>Change review, with evidence.</h1>'
    ]
    out.append(
        f"<p>SYNTHETIC / HUMAN REVIEW REQUIRED<br>Review {esc(review['review_id'])} · policy {esc(comparison['policy_id'])}</p>"
    )
    out.append(
        f'<p>{esc(comparison["before"]["manifest"]["reporting_date"])} to {esc(comparison["after"]["manifest"]["reporting_date"])}</p><p class="note">{esc(CAUTION)}</p>'
    )
    if comparison.get("example"):
        example = comparison["example"]
        out.append(
            f"<h2>{esc(example['title'])}</h2><p>{esc(example['story'])}</p><p><strong>Review question:</strong> {esc(example['question'])}</p><p>{esc(example['meaning'])}</p>"
        )
    out.append(
        "<h2>Borrower review queue</h2><table><tr><th>Borrower</th><th>Opening base</th><th>Closing base</th><th>Change</th></tr>"
    )
    for b in selected:
        out.append(
            f"<tr><td>{esc(b['provider'])}</td><td>{usd(b['opening'])}</td><td>{usd(b['closing'])}</td><td>{usd(b['delta'])}</td></tr>"
        )
    out.append("</table>")
    for b in selected:
        out.append(
            f"<h2>{esc(b['provider'])}</h2><table><tr><th>Model driver, fixed order</th><th>Effect on illustrative base</th></tr>"
        )
        out.extend(
            f"<tr><td>{esc(label)}</td><td>{usd(b['effects'][k])}</td></tr>"
            for k, label in LABELS.items()
        )
        out.append("</table><h3>Questions for the source owner</h3><ul>")
        out.extend(f"<li>{esc(q)}</li>" for q in b["questions"])
        out.append("</ul>")
    out.append("<h2>Paired cohort evidence</h2>")
    for r in rows:
        out.append(
            f"<article><h3>{esc(r['provider'])} / {esc(r['payer'])} / {esc(r['age'])}</h3><p>{esc(r['status'])} · {esc(r['borrower_id'])} / {esc(r['payer_id'])} · base change {usd(r['delta_exact']['borrowing_base'])}</p><table><tr><th>Input / result</th><th>Opening</th><th>Closing</th></tr>"
        )
        for k, label in [
            ("provider", "Borrower"),
            ("payer", "Payer"),
            ("type", "Payer class"),
            ("age", "Age bucket"),
        ]:
            out.append(
                "<tr><td>"
                + label
                + "</td>"
                + "".join(
                    "<td>" + esc(s[k] if s else "Absent") + "</td>"
                    for s in [r["before"], r["after"]]
                )
                + "</tr>"
            )
        for k in [x[0] for x in FIELDS]:
            values = [s["inputs_exact"][k] if s else "Absent" for s in [r["before"], r["after"]]]
            out.append(
                f"<tr><td>{esc(LABELS[k])}</td><td>{esc(values[0])}</td><td>{esc(values[1])}</td></tr>"
            )
        for k in ("cohort_id", "formula"):
            out.append(
                "<tr><td>"
                + esc(k)
                + "</td>"
                + "".join(
                    "<td>" + esc(s[k] if s else "Absent") + "</td>"
                    for s in [r["before"], r["after"]]
                )
                + "</tr>"
            )
        for k in ("aging_factor", "payer_factor", "advance_rate"):
            out.append(
                "<tr><td>"
                + esc(k)
                + "</td>"
                + "".join(
                    "<td>" + esc(s["factors_exact"][k] if s else "Absent") + "</td>"
                    for s in [r["before"], r["after"]]
                )
                + "</tr>"
            )
        out.append("</table>")
        out.extend(
            f"<p>{esc(LABELS[s['field']])}: {usd(s['base_before'])} to {usd(s['base_after'])}; effect {usd(s['effect'])}.</p>"
            for s in r["steps"]
        )
        out.append("</article>")
    out.append("<h2>Reproduction and scope</h2>")
    out.append("<h3>Applied policy parameters</h3><table>")
    out.extend(
        f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in comparison["policy"].items()
    )
    out.append("</table>")
    for period in ("before", "after"):
        s = comparison[period]
        out.append(
            f"<p>{esc(period)}: analysis {esc(s['analysis_id'])}<br>Source SHA-256 {esc(s['source_sha256'])}<br>Snapshot hash {esc(s['snapshot_hash'])}</p>"
        )
    out.append(
        "<p>Checksums support reproduction; they are not signatures or an immutable archive. No authenticated approval has been recorded. No lending decision or funding instruction is produced.</p></html>"
    )
    return "".join(out)
