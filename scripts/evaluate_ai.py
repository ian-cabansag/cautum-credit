"""Authorized real-API evidence collection. No fabricated responses or silent offline fallback."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

from cautum.config import provider
from cautum.engine import analyze
from cautum.parser import parse_csv
from cautum.review_agent import ReviewUnavailable, investigate

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=3, choices=range(1, 5))
    parser.add_argument("--output", type=Path, default=ROOT / "docs/evidence/ai-evaluation.json")
    parser.add_argument("--allow-gateway-cache", action="store_true")
    args = parser.parse_args()
    if not provider():
        raise SystemExit("No approved key configured. No API request made.")
    source = (ROOT / "cautum/data/synthetic_receivables.csv").read_bytes()
    analysis = analyze(parse_csv(source))
    records = []

    def save():
        by_profile = {}
        for profile in ("standard", "lean"):
            runs = [r for r in records if r["profile"] == profile]
            good = [r for r in runs if r["status"] == "succeeded"]
            by_profile[profile] = {
                "attempted": len(runs),
                "succeeded": len(good),
                "failed": len(runs) - len(good),
                "median_input_tokens": median([r["memo"]["usage"]["input_tokens"] for r in good])
                if good and all(r["memo"]["usage"]["input_tokens"] is not None for r in good)
                else None,
                "median_cached_tokens": median(
                    [r["memo"]["usage"]["cached_input_tokens"] for r in good]
                )
                if good and all(r["memo"]["usage"]["cached_input_tokens"] is not None for r in good)
                else None,
                "median_output_tokens": median([r["memo"]["usage"]["output_tokens"] for r in good])
                if good and all(r["memo"]["usage"]["output_tokens"] is not None for r in good)
                else None,
                "median_latency_ms": median([r["memo"]["latency_ms"] for r in good])
                if good
                else None,
                "median_rule_flag_coverage": median(
                    [r["memo"]["investigation"]["rule_flag_coverage"] for r in good]
                )
                if good
                else None,
            }
        value = {
            "measured_at_utc": datetime.now(timezone.utc).isoformat(),
            "fresh_request_ids": not args.allow_gateway_cache,
            "method": "Sequential paired standard/lean, same included synthetic portfolio and general-review task. No retries. Order alternates by pair.",
            "analysis_id": analysis["analysis_id"],
            "summary": by_profile,
            "runs": records,
            "limitations": [
                "Small developer-run synthetic sample, not expert-labeled credit accuracy.",
                "Rule-flag coverage is selected existing flags / all deterministic flags; not precision/recall of real risks.",
                "Cached usage and latency may depend on request order and provider conditions.",
                "Unknown usage and unsuccessful upstream calls may have unreported billable cost.",
            ],
        }
        args.output.write_text(json.dumps(value, indent=2) + "\n")

    for pair in range(args.pairs):
        order = ("standard", "lean") if pair % 2 == 0 else ("lean", "standard")
        for profile in order:
            at = datetime.now(timezone.utc).isoformat()
            try:
                memo = investigate(analysis, profile=profile, fresh=not args.allow_gateway_cache)
                records.append(
                    {
                        "pair": pair + 1,
                        "profile": profile,
                        "started_at_utc": at,
                        "status": "succeeded",
                        "memo": memo,
                    }
                )
                print(
                    json.dumps(
                        {
                            "pair": pair + 1,
                            "profile": profile,
                            "status": "succeeded",
                            "usage": memo["usage"],
                            "tools": len(memo["investigation"]["trace"]),
                        }
                    ),
                    flush=True,
                )
            except ReviewUnavailable as exc:
                records.append(
                    {
                        "pair": pair + 1,
                        "profile": profile,
                        "started_at_utc": at,
                        "status": "failed",
                        "error": str(exc),
                        "evidence": exc.evidence,
                    }
                )
                print(
                    json.dumps(
                        {
                            "pair": pair + 1,
                            "profile": profile,
                            "status": "failed",
                            "error": str(exc),
                        }
                    ),
                    flush=True,
                )
            save()
    print("Recorded actual runs:", args.output)


if __name__ == "__main__":
    main()
