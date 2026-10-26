from decimal import Decimal
from pathlib import Path

from cautum.engine import analyze
from cautum.parser import Receivable, parse_csv
from cautum.schema import Policy

DEMO = Path(__file__).resolve().parents[1] / "cautum" / "data" / "synthetic_receivables.csv"


def test_exact_illustrative_math():
    row = Receivable(
        "Fictional Clinic",
        "Example Commercial",
        "Commercial",
        "31-60",
        Decimal("1000"),
        Decimal(".20"),
        Decimal(".90"),
        Decimal(".10"),
    )
    a = analyze([row])
    # 1000 * .8 * .9 * .9 * .95 * 1 * .8 = 492.48
    assert a["summary"]["gross_ar"] == 1000.00
    assert a["summary"]["expected_collectible"] == 648.00
    assert a["summary"]["eligible_collateral"] == 615.60
    assert a["summary"]["borrowing_base"] == 492.48
    assert a["audit"][0]["aging_factor"] == 0.95
    assert a["summary"]["advanceability"] == 0.49248


def test_policy_sensitivity_and_id_change():
    rows = parse_csv(DEMO.read_bytes())
    base = analyze(rows)
    conservative = analyze(rows, Policy(advance_rate=Decimal(".70")))
    assert conservative["summary"]["borrowing_base"] < base["summary"]["borrowing_base"]
    assert conservative["summary"]["eligible_collateral"] == base["summary"]["eligible_collateral"]
    assert conservative["analysis_id"] != base["analysis_id"]


def test_synthetic_portfolio_invariants():
    a = analyze(parse_csv(DEMO.read_bytes()))
    s = a["summary"]
    assert s["borrower_count"] == 8
    assert s["cohort_count"] == 192
    assert (
        s["gross_ar"]
        >= s["expected_collectible"]
        >= s["eligible_collateral"]
        >= s["borrowing_base"]
        >= 0
    )
    assert abs(sum(x["share"] for x in a["aging"]) - 1) < 0.00001
    assert abs(sum(x["share"] for x in a["payers"]) - 1) < 0.00001
    assert s["alert_count"] == len(a["alerts"])
    assert all(x["provider"] in [b["name"] for b in a["borrowers"]] for x in a["alerts"])


def test_all_old_ineligible():
    r = Receivable(
        "Clinic A",
        "Example Pay",
        "Medicaid",
        "91+",
        Decimal("1000"),
        Decimal("0"),
        Decimal("1"),
        Decimal("0"),
    )
    assert analyze([r])["summary"]["borrowing_base"] == 0
