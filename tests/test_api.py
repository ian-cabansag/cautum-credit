from pathlib import Path

from fastapi.testclient import TestClient

from cautum.api import app

ROOT = Path(__file__).resolve().parents[1]
CSV = (ROOT / "cautum" / "data" / "synthetic_receivables.csv").read_bytes()
client = TestClient(app, base_url="http://127.0.0.1")


def upload(url="/api/analyze", csv=CSV, policy="{}", mode=None):
    return client.post(
        url,
        files={"file": ("synthetic.csv", csv, "text/csv")},
        data={"policy": policy, **({"mode": mode} if mode else {})},
    )


def test_ui_and_server_status():
    assert client.get("/").status_code == 200
    assert "A clearer picture" in client.get("/").text
    s = client.get("/api/status").json()
    assert s["ok"] and s["demo_only"]
    assert client.get("/data/synthetic_receivables.csv").status_code == 200


def test_analysis_end_to_end():
    r = upload()
    assert r.status_code == 200, r.text
    assert r.json()["summary"]["cohort_count"] == 192
    assert len(r.json()["audit"]) == 192
    assert r.headers["cache-control"] == "no-store"


def test_offline_memo():
    r = upload("/api/memo", mode="offline")
    assert r.status_code == 200
    assert r.json()["memo"]["source"] == "deterministic"
    assert r.json()["memo"]["usage"] is None
    assert r.json()["memo"]["human_review_required"] is True


def test_malformed_upload_and_policy():
    assert upload(csv=b"provider,payer\nfoo,bar").status_code == 400
    assert upload(policy='{"advance_rate":1.5}').status_code == 400
    assert upload(policy='{"unexpected":"ignore me"}').status_code == 400
    assert upload(csv=b"x" * 2_000_001).status_code == 413


def test_no_key_is_explicit(monkeypatch):
    import cautum.agent as agent

    monkeypatch.setattr(agent, "provider", lambda: None)
    r = upload("/api/memo", mode="ai")
    assert r.status_code == 503
    assert "No AI API key" in r.json()["detail"]


def test_every_public_route_and_error_contract():
    for path in [
        "/static/app.js",
        "/static/styles.css",
        "/static/sample-template.csv",
        "/api/docs",
        "/openapi.json",
    ]:
        r = client.get(path)
        assert r.status_code == 200
        assert r.headers["x-content-type-options"] == "nosniff"
    assert upload("/api/memo", mode="bogus").status_code == 400
    assert upload(policy="not json").status_code == 400
    assert upload(policy="[]").status_code == 400
    assert client.post("/api/analyze").status_code == 422
    assert client.post("/api/analyze", files={"file": ("bad.txt", CSV)}).status_code == 400


def test_brief_reports_all_flagged_borrowers():
    a = upload().json()
    expected = len({x["provider"] for x in a["alerts"]})
    memo = upload("/api/memo", mode="offline").json()["memo"]
    assert memo["risks"][0].startswith(f"{expected} flagged provider(s).")
