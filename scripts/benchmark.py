"""Measured synthetic parse+engine and optional real loopback HTTP timings. Never analyst impact."""

import argparse
import json
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from statistics import median
from time import perf_counter
from urllib.parse import urlparse

from cautum.engine import analyze
from cautum.parser import parse_csv

ROOT = Path(__file__).resolve().parents[1]


def stats(values):
    return {
        "repetitions": len(values),
        "median_ms": round(median(values), 3),
        "p95_ms": round(sorted(values)[ceil(0.95 * len(values)) - 1], 3),
        "min_ms": round(min(values), 3),
        "max_ms": round(max(values), 3),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url")
    parser.add_argument("--output")
    args = parser.parse_args()
    raw = (ROOT / "cautum/data/synthetic_receivables.csv").read_bytes()
    values = []
    for _ in range(30):
        start = perf_counter()
        result = analyze(parse_csv(raw))
        values.append((perf_counter() - start) * 1000)
    output = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "bundled synthetic, 192 cohorts / 8 borrowers",
        "engine_parse": stats(values),
        "analysis_id": result["analysis_id"],
        "summary_exact": result["summary_exact"],
        "no_user_impact_implied": True,
        "ai_calls": 0,
    }
    if args.url:
        parsed = urlparse(args.url)
        if parsed.scheme != "http" or parsed.hostname not in (
            "127.0.0.1",
            "localhost",
            "::1",
        ):
            raise SystemExit("Benchmark URL must be loopback HTTP.")
        import httpx

        values = []
        with httpx.Client(base_url=args.url, timeout=30, trust_env=False) as client:
            for _ in range(20):
                start = perf_counter()
                r = client.post("/api/analyze", files={"file": ("synthetic.csv", raw, "text/csv")})
                r.raise_for_status()
                body = r.json()
                values.append((perf_counter() - start) * 1000)
                assert body["analysis_id"] == result["analysis_id"]
        output["real_loopback_http_multipart_analyze"] = stats(values)
    encoded = json.dumps(output, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(encoded)
    print(encoded)


if __name__ == "__main__":
    main()
