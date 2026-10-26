"""Independent analytical cases and seeded invariants, not lender validation."""

from dataclasses import replace
from decimal import ROUND_HALF_UP, Decimal, localcontext
from pathlib import Path
from random import Random

import pytest
from pydantic import ValidationError

from cautum.engine import MONEY_FIELDS, analyze
from cautum.parser import Receivable, parse_csv
from cautum.schema import Policy

D = Decimal
ROW = Receivable(
    "Example Clinic",
    "Example Payer",
    "Commercial",
    "31-60",
    D("1000"),
    D(".2"),
    D(".9"),
    D(".1"),
)


def decsum(items, field):
    return sum((D(str(x[field])) for x in items), D(0))


def test_independent_golden_bridge():
    a = analyze([ROW])
    assert [x["amount"] for x in a["bridge"]] == [1000, 800, 648, 615.60, 492.48]
    assert [x["reduction_from_prior"] for x in a["bridge"]] == [
        0,
        200,
        152,
        32.4,
        123.12,
    ]
    assert a["audit"][0]["inputs_exact"]["contractual_adjustment_rate"] == "0.2"
    assert a["assessment_gates"]["net_availability"] is None
    assert a["assessment_gates"]["legal_eligibility"] == "unreviewed"


def test_half_cent_rounding_is_explicit_and_reconciles():
    rows = [
        replace(
            ROW,
            provider=f"Clinic {i}",
            gross_ar=D(".01"),
            contractual_adjustment_rate=D(".5"),
            historical_collection_factor=D(1),
            denial_rate=D(0),
        )
        for i in range(3)
    ]
    a = analyze(rows, Policy(advance_rate=1, aging_31_60=1))
    # 0.005 per cohort rounds half-up to 0.01, not rounded portfolio 0.015 = 0.02.
    assert a["summary"]["net_allowed"] == 0.03
    assert all(x["unrounded"]["net_allowed"] == "0.005" for x in a["audit"])
    assert all(D(x["rounding_adjustments"]["net_allowed"]) == D(".005") for x in a["audit"])
    for key in MONEY_FIELDS:
        assert decsum(a["audit"], key) == D(a["summary_exact"][key])
        assert decsum(a["borrowers"], key) == D(a["summary_exact"][key])


def test_hash_captures_original_inputs_and_is_permutation_invariant():
    rows = [ROW, replace(ROW, provider="Example Clinic Two")]
    a = analyze(rows)
    assert a["analysis_id"] == analyze(list(reversed(rows)))["analysis_id"]
    assert a["analysis_id"] == analyze(rows, Policy(advance_rate=D(".800")))["analysis_id"]
    changed = analyze([replace(ROW, denial_rate=D(".100001")), rows[1]])
    assert a["analysis_id"] != changed["analysis_id"]
    assert a["policy_id"] == changed["policy_id"]
    assert a["policy_id"] != analyze(rows, Policy(advance_rate=".7"))["policy_id"]


@pytest.mark.parametrize(
    "changes",
    [
        {"contractual_adjustment_rate": D(1)},
        {"denial_rate": D(1)},
        {"historical_collection_factor": D(0)},
    ],
)
def test_complete_losses(changes):
    a = analyze([replace(ROW, **changes)])
    assert a["summary"]["borrowing_base"] == 0
    assert a["summary"]["expected_collectible"] == 0


def test_zero_and_upper_bound_cases():
    a = analyze([replace(ROW, gross_ar=D(0))])
    assert all(a["summary"][k] == 0 for k in MONEY_FIELDS)
    full = replace(
        ROW,
        gross_ar=D("1000000000000"),
        contractual_adjustment_rate=D(0),
        historical_collection_factor=D(1),
        denial_rate=D(0),
        aging_bucket="0-30",
    )
    a = analyze([full], Policy(advance_rate=1))
    assert a["summary_exact"]["borrowing_base"] == "1000000000000.00"
    with pytest.raises(ValidationError):
        Policy(advance_rate=D("0.1234567"))
    with pytest.raises(ValidationError):
        Policy(advance_rate="NaN")


def test_seeded_portfolio_properties_and_independent_reference():
    random = Random(71)
    with localcontext() as ctx:
        ctx.prec = 80
        for _ in range(60):
            rows = [
                replace(
                    ROW,
                    provider=f"Clinic {i}",
                    gross_ar=D(random.randrange(1, 10**9)) / D(10**6),
                    contractual_adjustment_rate=D(random.randrange(10**6 + 1)) / D(10**6),
                    historical_collection_factor=D(random.randrange(10**6 + 1)) / D(10**6),
                    denial_rate=D(random.randrange(10**6 + 1)) / D(10**6),
                )
                for i in range(12)
            ]
            a = analyze(rows)
            for r, t in zip(rows, sorted(a["audit"], key=lambda x: int(x["provider"].split()[-1]))):
                reference = (
                    r.gross_ar
                    * (1 - r.contractual_adjustment_rate)
                    * r.historical_collection_factor
                    * (1 - r.denial_rate)
                    * D(".95")
                    * D(".8")
                ).quantize(D(".01"), rounding=ROUND_HALF_UP)
                assert D(str(t["borrowing_base"])) == reference
            for k in MONEY_FIELDS:
                assert (
                    decsum(a["audit"], k) == D(a["summary_exact"][k]) == decsum(a["borrowers"], k)
                )
            s = a["summary"]
            assert (
                s["gross_ar"]
                >= s["net_allowed"]
                >= s["expected_collectible"]
                >= s["eligible_collateral"]
                >= s["borrowing_base"]
                >= 0
            )
            low = analyze(rows, Policy(advance_rate=".7"))
            assert low["summary"]["eligible_collateral"] == s["eligible_collateral"]
            assert low["summary"]["borrowing_base"] <= s["borrowing_base"]


def test_real_synthetic_sample_reconciles_all_exposures():
    a = analyze(parse_csv(Path("cautum/data/synthetic_receivables.csv").read_bytes()))
    for k in MONEY_FIELDS:
        assert decsum(a["audit"], k) == D(a["summary_exact"][k]) == decsum(a["borrowers"], k)
    assert decsum(a["aging"], "gross_ar") == D(a["summary_exact"]["gross_ar"])
    assert decsum(a["payers"], "gross_ar") == D(a["summary_exact"]["gross_ar"])
    assert a["summary"]["expected_collectible"] == 1158846.52
    assert a["summary"]["eligible_collateral"] == 952251.44
    assert a["summary"]["borrowing_base"] == 761801.19
