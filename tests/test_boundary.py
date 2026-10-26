import asyncio

from fastapi.testclient import TestClient
from test_api import CSV
from test_security import VALID

from cautum.api import app
from cautum.boundary import MAX_REQUEST_BYTES, RequestBoundary

client = TestClient(app, base_url="http://127.0.0.1")


def test_local_host_and_origin_enforcement():
    assert client.get("/api/status", headers={"host": "attacker.example"}).status_code == 400
    for origin in (
        "https://attacker.example",
        "null",
        "http://localhost",
        "http://127.0.0.1:1234",
    ):
        for path in (
            "/api/analyze",
            "/api/memo",
            "/api/certificate",
            "/api/surveillance",
        ):
            assert client.post(path, headers={"origin": origin}).status_code == 403
    assert (
        client.post(
            "/api/analyze",
            files={"file": ("demo.csv", CSV)},
            headers={"origin": "http://127.0.0.1"},
        ).status_code
        == 200
    )
    assert client.post("/api/analyze", headers={"sec-fetch-site": "cross-site"}).status_code == 403
    assert "script-src 'self'" in client.get("/").headers["content-security-policy"]


def test_entire_request_limit_before_multipart():
    r = client.post(
        "/api/analyze",
        content=b"x" * (MAX_REQUEST_BYTES + 1),
        headers={"content-type": "multipart/form-data; boundary=test"},
    )
    assert r.status_code == 413


def test_chunked_request_limit_without_content_length():
    async def run():
        consumed = []
        sent = []

        async def app(scope, receive, send):
            consumed.append(await receive())

        messages = iter(
            [
                {"type": "http.request", "body": b"x" * 1_100_000, "more_body": True},
                {"type": "http.request", "body": b"x" * 1_100_000, "more_body": False},
            ]
        )

        async def receive():
            return next(messages)

        async def send(m):
            sent.append(m)

        await RequestBoundary(app)(
            {
                "type": "http",
                "method": "POST",
                "scheme": "http",
                "headers": [(b"host", b"127.0.0.1")],
            },
            receive,
            send,
        )
        assert not consumed and sent[0]["status"] == 413

    asyncio.run(run())


def test_large_multipart_never_rolls_to_disk(monkeypatch):
    import cautum.api as api

    original = api.run_engine
    observed = []

    async def inspect_file(file, policy, mapping=""):
        observed.append(getattr(file.file, "_rolled", None))
        return await original(file, policy, mapping)

    monkeypatch.setattr(api, "run_engine", inspect_file)
    payload = VALID.encode() + b" " * 1_200_000
    r = client.post("/api/analyze", files={"file": ("synthetic.csv", payload)})
    assert r.status_code == 400  # Invalid synthetic row, but large accepted HTTP envelope.
    assert observed == [False]


def test_env_precedence_and_process_priority(tmp_path, monkeypatch):
    from cautum.config import load_settings_env

    root = tmp_path / "repository"
    root.mkdir()
    monkeypatch.delenv("CAUTUM_TEST_SETTING", raising=False)
    (tmp_path / ".env").write_text("CAUTUM_TEST_SETTING=synthetic-parent\n")
    assert load_settings_env(root) == tmp_path / ".env"
    assert __import__("os").getenv("CAUTUM_TEST_SETTING") == "synthetic-parent"
    monkeypatch.delenv("CAUTUM_TEST_SETTING")
    (root / ".env").write_text("CAUTUM_TEST_SETTING=synthetic-root\n")
    assert load_settings_env(root) == root / ".env"
    assert __import__("os").getenv("CAUTUM_TEST_SETTING") == "synthetic-root"
    monkeypatch.setenv("CAUTUM_TEST_SETTING", "synthetic-process")
    load_settings_env(root)
    assert __import__("os").getenv("CAUTUM_TEST_SETTING") == "synthetic-process"
