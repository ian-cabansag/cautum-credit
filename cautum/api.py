"""One-process local app, zero database, no raw-file persistence."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool
from starlette.formparsers import MultiPartParser
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .agent import AgentUnavailable, generate_memo, usage_snapshot
from .boundary import MAX_REQUEST_BYTES, RequestBoundary
from .config import MAX_UPLOAD_BYTES, provider
from .engine import analyze, deterministic_brief
from .ingestion import ALIASES, normalize_csv
from .parser import DataError, parse_csv
from .review_agent import investigate
from .review_study import Observation, latest, record
from .schema import Policy

ROOT = Path(__file__).resolve().parent
app = FastAPI(
    title="Cautum Credit",
    description="Illustrative lender-side receivables monitoring",
    version="0.4.0",
    docs_url="/api/docs",
    redoc_url=None,
)
# RequestBoundary caps the entire body before multipart parsing. The tested
# Starlette parser then cannot roll a permitted file to disk. Pin/test this API.
MultiPartParser.spool_max_size = MAX_REQUEST_BYTES
app.add_middleware(RequestBoundary)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
app.mount("/data", StaticFiles(directory=ROOT / "data"), name="data")


@app.middleware("http")
async def secure_defaults(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path in ("/", "/study") or request.url.path.startswith("/static/"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
    # Local demonstration, not a substitute for internet-facing production hardening.
    return response


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/study")
def review_exercise():
    return FileResponse(ROOT / "static" / "exercise.html")


@app.post("/api/review-study")
def review_observation(observation: Observation):
    try:
        return record(observation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


@app.get("/api/review-study")
def review_result():
    result = latest()
    if result is None:
        raise HTTPException(status_code=404, detail="No participant observation recorded.")
    return result


@app.get("/api/status")
def status():
    credentials = provider()
    return {
        "ok": True,
        "version": "0.4.0",
        "demo_only": True,
        "ai_usage": usage_snapshot(),
        "ai_method": "bounded read-only borrower investigation; deterministic financial wording",
        "ai_configured": bool(credentials),
        "ai_provider": credentials[0] if credentials else None,
        "limits": {"file_bytes": MAX_UPLOAD_BYTES, "rows": 2500},
        "policy": Policy().public(),
        "import_aliases": ALIASES,
    }


async def run_engine(file: UploadFile, policy: str, mapping: str = ""):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv file using the sample template.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="CSV exceeds the 2 MB upload limit.")
    try:
        p = Policy.model_validate(json.loads(policy))
        source_digest = sha256(content).hexdigest()
        source_bytes = len(content)
        if mapping:
            content = normalize_csv(content, json.loads(mapping))
        rows = parse_csv(content)
        result = analyze(rows, p)
        result["import_evidence"] = {
            "source_sha256": source_digest,
            "source_bytes": source_bytes,
            "mapping": json.loads(mapping) if mapping else {k: k for k in ALIASES},
            "raw_file_persisted": False,
        }
        return result
    except (json.JSONDecodeError, ValidationError):
        raise HTTPException(
            status_code=400,
            detail="Invalid policy or mapping. Check aggregate fields and allowed 0–1 rate ranges.",
        ) from None
    except DataError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@app.post("/api/analyze")
async def analyze_upload(
    file: UploadFile = File(...), policy: str = Form("{}"), mapping: str = Form("")
):
    return await run_engine(file, policy, mapping)


@app.post("/api/memo")
async def memo_upload(
    file: UploadFile = File(...),
    policy: str = Form("{}"),
    mode: str = Form("offline"),
    mapping: str = Form(""),
    profile: str = Form("standard"),
    focus: str = Form("review"),
):
    result = await run_engine(file, policy, mapping)
    if mode == "offline":
        memo = deterministic_brief(result)
    elif mode == "ai":
        try:
            memo = await run_in_threadpool(generate_memo, result)
        except AgentUnavailable as e:
            raise HTTPException(status_code=503, detail=str(e)) from None
    elif mode == "investigate":
        try:
            memo = await run_in_threadpool(investigate, result, profile, focus)
        except AgentUnavailable as e:
            raise HTTPException(status_code=503, detail=str(e)) from None
    else:
        raise HTTPException(status_code=400, detail="mode must be offline, ai or investigate")
    return {"analysis_id": result["analysis_id"], "memo": memo}


@app.post("/api/certificate")
async def certificate_upload(
    file: UploadFile = File(...),
    policy: str = Form("{}"),
    mapping: str = Form(""),
    borrower: str = Form(""),
):
    from fastapi.responses import HTMLResponse

    from .certificate import render_certificate

    result = await run_engine(file, policy, mapping)
    try:
        html = render_certificate(result, borrower)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    return HTMLResponse(
        html,
        headers={
            "Content-Disposition": f'attachment; filename="cautum-certificate-{result["analysis_id"]}.html"'
        },
    )


@app.post("/api/surveillance")
async def synthetic_surveillance(
    policy: str = Form("{}"),
    opening: UploadFile | None = File(None),
    closing: UploadFile | None = File(None),
    opening_manifest: str = Form(""),
    closing_manifest: str = Form(""),
    synthetic: bool = Form(False),
    output_format: str = Form("json"),
    borrower: str = Form(""),
    example: str = Form("portfolio"),
):
    from fastapi.responses import HTMLResponse

    from .change_review import render_packet
    from .snapshot_io import read_pair

    if output_format not in ("json", "html"):
        raise HTTPException(status_code=400, detail="output_format must be json or html")
    try:
        p = Policy.model_validate(json.loads(policy))
        result = await read_pair(
            p, opening, closing, opening_manifest, closing_manifest, synthetic, example
        )
        if output_format == "html":
            html = render_packet(result, borrower)
            return HTMLResponse(
                html,
                headers={
                    "Content-Disposition": 'attachment; filename="cautum-change-'
                    + result["change_review"]["review_id"]
                    + '.html"'
                },
            )
        return result
    except (json.JSONDecodeError, ValidationError, DataError, TypeError) as exc:
        detail = (
            str(exc)
            if isinstance(exc, DataError)
            else "Invalid comparison policy or snapshot contract."
        )
        raise HTTPException(status_code=400, detail=detail) from None


@app.get("/api/examples/{name}/{source}")
def example_source(name: str, source: str):
    from fastapi.responses import JSONResponse, PlainTextResponse

    from .examples import EXAMPLES, example_sources

    if name not in EXAMPLES or source not in (
        "opening.csv",
        "closing.csv",
        "opening.json",
        "closing.json",
    ):
        raise HTTPException(status_code=404, detail="Unknown constructed example source.")
    pair = example_sources(name)
    raw, manifest = pair[0 if source.startswith("opening") else 1]
    headers = {"Content-Disposition": f'attachment; filename="{name}-{source}"'}
    if source.endswith(".csv"):
        return PlainTextResponse(raw.decode(), media_type="text/csv", headers=headers)
    return JSONResponse(manifest, headers=headers)
