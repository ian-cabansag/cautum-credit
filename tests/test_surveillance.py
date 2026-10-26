import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from test_security import VALID

from cautum.api import app
from cautum.parser import DataError
from cautum.schema import Policy
from cautum.surveillance import compare, snapshot

ROOT = Path("cautum/data")


def fixture(period):
    return (ROOT / f"synthetic_{period}.csv").read_bytes(), json.loads(
        (ROOT / f"synthetic_{period}.json").read_text()
    )


def test_two_period_bridge_exact_and_reproducible():
    b = snapshot(*fixture("T0"))
    a = snapshot(*fixture("T1"))
    r = compare(b, a)
    assert r["bridge"]["gross_ar"]["reconciled"]
    assert r["bridge"]["borrowing_base"]["reconciled"]
    assert len(r["movements"]) == 192
    assert r["headroom_delta"] is None
    assert r == compare(snapshot(*fixture("T0")), snapshot(*fixture("T1")))
    assert r["before"]["manifest"]["imported_at"] is None
    assert r["alerts"]


def manifest(day):
    return {
        "snapshot_id": "test-" + day[-2:],
        "reporting_date": day,
        "revision": 1,
        "kind": "synthetic",
        "borrower_ids": {
            "Fictional Clinic": "borrower-1",
            "Other Clinic": "borrower-2",
        },
        "payer_ids": {"Example Commercial": "payer-1"},
        "source_note": "synthetic test",
        "imported_at": None,
    }


def test_removed_and_added_rows_reconcile_without_cash_claim():
    b = snapshot(VALID.encode(), manifest("2026-08-01"))
    a = snapshot(
        VALID.replace("Fictional Clinic", "Other Clinic").replace("1000,", "800,").encode(),
        manifest("2026-09-02"),
    )
    r = compare(b, a)
    assert {x["status"] for x in r["movements"]} == {"added", "removed"}
    assert r["bridge"]["gross_ar"]["removed"] == "-1000.00"
    assert r["bridge"]["gross_ar"]["added"] == "800.00"
    assert r["bridge"]["gross_ar"]["delta"] == "-200.00"


def test_rename_requires_explicit_identity_mapping():
    b = snapshot(VALID.encode(), manifest("2026-08-01"))
    renamed = VALID.replace("Example Commercial", "Renamed Payer").encode()
    m = manifest("2026-09-02")
    with pytest.raises(DataError):
        snapshot(renamed, m)
    m["payer_ids"] = {"Renamed Payer": "payer-1"}
    r = compare(b, snapshot(renamed, m))
    assert r["movements"][0]["explicit_rename"]
    assert r["movements"][0]["status"] == "continuing"


def test_policy_changes_dates_and_restatements():
    b = snapshot(*fixture("T0"))
    with pytest.raises(DataError, match="Policy changed"):
        compare(b, snapshot(*fixture("T1"), Policy(advance_rate=".7")))
    raw, m = fixture("T1")
    m["reporting_date"] = "2026-08-31"
    with pytest.raises(DataError, match="restatements"):
        compare(b, snapshot(raw, m))
    m["reporting_date"] = ["2026-08-31", "2026-09-30"]
    with pytest.raises(DataError):
        snapshot(raw, m)
    raw, m = fixture("T1")
    m["revision"] = 2
    assert compare(b, snapshot(raw, m))["restatement_included"]


def test_http_synthetic_study():
    c = TestClient(app, base_url="http://127.0.0.1")
    r = c.post("/api/surveillance", data={"policy": "{}"})
    assert r.status_code == 200 and r.json()["policy_id"]
    assert c.post("/api/surveillance", data={"policy": '{"advance_rate":2}'}).status_code == 400
