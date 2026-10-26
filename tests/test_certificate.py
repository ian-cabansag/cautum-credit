from decimal import Decimal

from fastapi.testclient import TestClient
from test_api import CSV, upload

from cautum.api import app
from cautum.certificate import render_certificate


def test_certificate_scoped_totals_and_pending_gates():
    a = upload().json()
    name = a["borrowers"][0]["name"]
    html = render_certificate(a, name)
    expected = sum(
        (
            Decimal(r["amounts_exact"]["borrowing_base"])
            for r in a["audit"]
            if r["provider"] == name
        ),
        Decimal(0),
    )
    assert f"${expected:,.2f}" in html
    assert "TO REVIEW" in html
    assert "Net undrawn availability: not calculated" in html
    assert a["policy_id"] in html
    assert "not a lender certificate" in html


def test_certificate_http_and_escaping():
    c = TestClient(app, base_url="http://127.0.0.1")
    r = c.post("/api/certificate", files={"file": ("demo.csv", CSV)})
    assert r.status_code == 200 and "attachment" in r.headers["content-disposition"]
    assert "Illustrative borrowing base certificate" in r.text
    assert (
        c.post(
            "/api/certificate",
            files={"file": ("demo.csv", CSV)},
            data={"borrower": "Missing Borrower"},
        ).status_code
        == 400
    )
    a = upload().json()
    a["audit"][0]["payer"] = "<script>alert(1)</script>"
    html = render_certificate(a)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
