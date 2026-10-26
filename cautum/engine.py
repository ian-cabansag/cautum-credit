"""Deterministic cohort model. Monetary aggregates sum explicitly rounded cohort amounts."""

from __future__ import annotations

import json
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal, localcontext
from hashlib import sha256

from .parser import Receivable
from .schema import AGE_BUCKETS, Policy

CENT = Decimal("0.01")
ENGINE_VERSION = "cohort-cents-v0.2"
MONEY_FIELDS = (
    "gross_ar",
    "net_allowed",
    "expected_collectible",
    "eligible_collateral",
    "borrowing_base",
)
FORMULA = "N=G*(1-contract); E=N*collection*(1-denial); C=E*aging*payer; B=C*advance"


def cents(x):
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def money(x):
    return float(cents(x))


def ratio(x):
    return round(float(x), 6)


def divide(a, b):
    return a / b if b else Decimal(0)


def canonical(value):
    return format(value.normalize(), "f") if isinstance(value, Decimal) else value


def stable_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def analyze(rows: list[Receivable], policy: Policy | None = None) -> dict:
    with localcontext() as context:
        context.prec = 64
        return _analyze(rows, policy or Policy())


def _analyze(rows, p):
    if not rows:
        raise ValueError("At least one cohort is required")
    policy_exact = {k: canonical(v) for k, v in p.model_dump().items()}
    policy_id = stable_hash(policy_exact)[:16]
    cohorts = []
    audit = []
    by_provider = defaultdict(list)
    by_payer = defaultdict(Decimal)
    by_age = defaultdict(Decimal)
    for r in sorted(
        rows,
        key=lambda r: (
            r.provider.casefold(),
            r.payer.casefold(),
            AGE_BUCKETS.index(r.aging_bucket),
        ),
    ):
        net = r.gross_ar * (1 - r.contractual_adjustment_rate)
        expected = net * r.historical_collection_factor * (1 - r.denial_rate)
        eligible = expected * p.age_factor(r.aging_bucket) * p.payer_factor(r.payer_type)
        base = eligible * p.advance_rate
        raw = dict(zip(MONEY_FIELDS, [r.gross_ar, net, expected, eligible, base]))
        rounded = {k: cents(v) for k, v in raw.items()}
        cohort_id = stable_hash([r.provider, r.payer, r.payer_type, r.aging_bucket])[:16]
        reasons = []
        for active, code in [
            (r.contractual_adjustment_rate > 0, "CONTRACT_ADJUSTMENT"),
            (r.historical_collection_factor < 1, "COLLECTION_FACTOR"),
            (r.denial_rate > 0, "DENIAL_HAIRCUT"),
            (p.age_factor(r.aging_bucket) < 1, "AGING_FACTOR"),
            (p.payer_factor(r.payer_type) < 1, "PAYER_FACTOR"),
            (p.advance_rate < 1, "ADVANCE_RATE"),
        ]:
            if active:
                reasons.append(code)
        row = {
            "provider": r.provider,
            "payer": r.payer,
            "type": r.payer_type,
            "age": r.aging_bucket,
            **{k: money(v) for k, v in rounded.items()},
            "amounts_exact": {k: format(v, ".2f") for k, v in rounded.items()},
            "contractual_adjustment_rate": ratio(r.contractual_adjustment_rate),
            "historical_collection_factor": ratio(r.historical_collection_factor),
            "denial_rate": ratio(r.denial_rate),
            "aging_factor": ratio(p.age_factor(r.aging_bucket)),
            "payer_factor": ratio(p.payer_factor(r.payer_type)),
            "advance_rate": ratio(p.advance_rate),
            "cohort_id": cohort_id,
            "policy_id": policy_id,
            "engine_version": ENGINE_VERSION,
            "formula": FORMULA,
            "reason_codes": reasons,
            "legal_eligibility": "unreviewed",
            "inputs_exact": {k: canonical(v) for k, v in vars(r).items()},
            "unrounded": {k: canonical(v) for k, v in raw.items()},
            "rounding_adjustments": {k: canonical(rounded[k] - raw[k]) for k in MONEY_FIELDS},
        }
        audit.append(row)
        d = {
            **rounded,
            "provider": r.provider,
            "payer": r.payer,
            "age": r.aging_bucket,
            "denied_weight": r.gross_ar * r.denial_rate,
            "raw_gross": r.gross_ar,
            "cohort_id": cohort_id,
        }
        cohorts.append(d)
        by_provider[r.provider].append(d)
        by_payer[r.payer] += rounded["gross_ar"]
        by_age[r.aging_bucket] += rounded["gross_ar"]
    totals = {k: sum((d[k] for d in cohorts), Decimal(0)) for k in MONEY_FIELDS}
    raw_gross = sum((d["raw_gross"] for d in cohorts), Decimal(0))
    raw_aged = sum((d["raw_gross"] for d in cohorts if d["age"] == "91+"), Decimal(0))
    raw_payers = defaultdict(Decimal)
    for d in cohorts:
        raw_payers[d["payer"]] += d["raw_gross"]
    borrowers = []
    alerts = []
    for name, items in sorted(by_provider.items()):
        amounts = {k: sum((d[k] for d in items), Decimal(0)) for k in MONEY_FIELDS}
        gross = sum((d["raw_gross"] for d in items), Decimal(0))
        denial = divide(sum((d["denied_weight"] for d in items), Decimal(0)), gross)
        aged = divide(sum((d["raw_gross"] for d in items if d["age"] == "91+"), Decimal(0)), gross)
        payers = defaultdict(Decimal)
        for d in items:
            payers[d["payer"]] += d["raw_gross"]
        top, top_amount = sorted(payers.items(), key=lambda t: (-t[1], t[0]))[0]
        concentration = divide(top_amount, gross)
        advanceability = divide(amounts["borrowing_base"], gross)
        flags = []
        for condition, code, title, observed, threshold, operator, evidence in [
            (
                denial > p.denial_alert,
                "DENIAL",
                "Elevated denial exposure",
                denial,
                p.denial_alert,
                ">",
                [d for d in items if d["denied_weight"] > 0],
            ),
            (
                aged > p.aged_alert,
                "AGING",
                "Receivables aging pressure",
                aged,
                p.aged_alert,
                ">",
                [d for d in items if d["age"] == "91+"],
            ),
            (
                concentration > p.payer_concentration_alert,
                "CONCENTRATION",
                "Payer concentration",
                concentration,
                p.payer_concentration_alert,
                ">",
                [d for d in items if d["payer"] == top],
            ),
            (
                advanceability < p.minimum_advanceability,
                "ADVANCEABILITY",
                "Low estimated advanceability",
                advanceability,
                p.minimum_advanceability,
                "<",
                items,
            ),
        ]:
            if condition:
                flags.append(code)
                alerts.append(
                    {
                        "provider": name,
                        "code": code,
                        "title": title,
                        "observed": ratio(observed),
                        "threshold": ratio(threshold),
                        "observed_exact": canonical(observed),
                        "threshold_exact": canonical(threshold),
                        "operator": operator,
                        "policy_id": policy_id,
                        "cohort_ids": [d["cohort_id"] for d in evidence],
                        "severity": "high" if code in ("DENIAL", "ADVANCEABILITY") else "medium",
                    }
                )
        borrowers.append(
            {
                "name": name,
                **{k: money(v) for k, v in amounts.items()},
                "denial_rate": ratio(denial),
                "aged_share": ratio(aged),
                "top_payer": top,
                "top_payer_share": ratio(concentration),
                "advanceability": ratio(advanceability),
                "flags": flags,
                "status": "High attention"
                if len(flags) >= 3
                else "Watch"
                if flags
                else "Within policy",
            }
        )
    borrowers.sort(key=lambda x: (-x["gross_ar"], x["name"]))
    payers = sorted(
        [
            {
                "name": k,
                "gross_ar": money(v),
                "share": ratio(divide(raw_payers[k], raw_gross)),
            }
            for k, v in by_payer.items()
        ],
        key=lambda x: (-x["gross_ar"], x["name"]),
    )
    ages = [
        {
            "bucket": age,
            "gross_ar": money(by_age[age]),
            "share": ratio(
                divide(
                    sum((d["raw_gross"] for d in cohorts if d["age"] == age), Decimal(0)),
                    raw_gross,
                )
            ),
        }
        for age in AGE_BUCKETS
    ]
    alerts.sort(key=lambda x: (0 if x["severity"] == "high" else 1, x["provider"], x["code"]))
    summary = {
        **{k: money(v) for k, v in totals.items()},
        "excluded_or_haircut": money(totals["gross_ar"] - totals["eligible_collateral"]),
        "denial_rate": ratio(
            divide(sum((d["denied_weight"] for d in cohorts), Decimal(0)), raw_gross)
        ),
        "aged_share": ratio(divide(raw_aged, raw_gross)),
        "advanceability": ratio(divide(totals["borrowing_base"], raw_gross)),
        "top_payer": payers[0]["name"],
        "top_payer_share": payers[0]["share"],
        "borrower_count": len(borrowers),
        "cohort_count": len(cohorts),
        "alert_count": len(alerts),
    }
    bridge = [
        {
            "stage": key,
            "amount": money(totals[key]),
            "reduction_from_prior": money(totals[MONEY_FIELDS[i - 1]] - totals[key]) if i else 0,
        }
        for i, key in enumerate(MONEY_FIELDS)
    ]
    digest = stable_hash({"engine": ENGINE_VERSION, "policy": policy_exact, "audit": audit})[:16]
    return {
        "summary": summary,
        "borrowers": borrowers,
        "payers": payers,
        "aging": ages,
        "alerts": alerts,
        "audit": audit,
        "bridge": bridge,
        "policy": p.public(),
        "policy_exact": policy_exact,
        "policy_id": policy_id,
        "engine_version": ENGINE_VERSION,
        "analysis_id": digest,
        "summary_exact": {k: format(v, ".2f") for k, v in totals.items()},
        "rounding": "Independent full-precision cohort stages, ROUND_HALF_UP to cents, then aggregate. No rounded-stage chaining.",
        "assessment_gates": {
            "legal_eligibility": "unreviewed",
            "reserves": "not modeled",
            "outstandings": "not supplied",
            "net_availability": None,
            "approval": "to review; no authenticated sign-off",
        },
        "model_note": "Illustrative, unvalidated collection assumptions and policy-adjusted collateral. Legal eligibility, reserves and undrawn availability are not established. Not a financing recommendation.",
    }


def deterministic_brief(analysis: dict) -> dict:
    s = analysis["summary"]
    alerts = analysis["alerts"]
    flagged = list(dict.fromkeys(a["provider"] for a in alerts))
    names = flagged[:4]
    return {
        "headline": "Preliminary collateral review",
        "executive_summary": f"Across {s['borrower_count']} provider borrowers, gross A/R is ${s['gross_ar']:,.0f} and the illustrative borrowing base is ${s['borrowing_base']:,.0f} ({s['advanceability']:.1%} of gross A/R). {s['alert_count']} policy flags require review.",
        "positives": [
            f"${s['eligible_collateral']:,.0f} calculated eligible collateral under the selected demo policy.",
            "All financial calculations are deterministic and traced to uploaded cohort data.",
        ],
        "risks": [
            f"{len(flagged)} flagged provider(s). First {len(names)}: {', '.join(names)}."
            if names
            else "No borrower breached the selected demonstration thresholds."
        ],
        "diligence_questions": [
            "Are collection, contractual adjustment and denial assumptions independently calibrated?",
            "Are payer-specific assignments, account control and lender documentation legally permissible?",
            "Can results be reconciled to actual cash remittances and historical recoveries?",
        ],
        "limitations": [
            "This is an illustrative A/R cohort model, not validated credit underwriting.",
            "No legal eligibility analysis, cash-verification, claim-level reconciliation, or live payer data.",
            "Human credit/legal review required before any financing activity.",
        ],
        "human_review_required": True,
        "source": "deterministic",
        "usage": None,
    }
