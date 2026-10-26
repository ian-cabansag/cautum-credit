"""Synthetic snapshot comparison, matched only by explicit organizational IDs."""

import re
from datetime import date
from decimal import Decimal
from hashlib import sha256

from .engine import analyze, money, stable_hash
from .parser import DataError, parse_csv
from .schema import Policy


def snapshot(raw: bytes, manifest: dict, policy: Policy | None = None) -> dict:
    allowed = {
        "snapshot_id",
        "reporting_date",
        "revision",
        "kind",
        "borrower_ids",
        "payer_ids",
        "source_note",
        "imported_at",
    }
    if set(manifest) != allowed or manifest["kind"] != "synthetic":
        raise DataError("Only complete synthetic snapshot manifests are supported.")
    try:
        date.fromisoformat(manifest["reporting_date"])
        if type(manifest["revision"]) is not int or manifest["revision"] < 1:
            raise ValueError()
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,48}", manifest["snapshot_id"]):
            raise ValueError()
    except (ValueError, TypeError):
        raise DataError("Snapshot date, ID or revision is invalid.") from None
    rows = parse_csv(raw)
    for key, labels in [
        ("borrower_ids", {r.provider for r in rows}),
        ("payer_ids", {r.payer for r in rows}),
    ]:
        ids = manifest[key]
        if (
            not isinstance(ids, dict)
            or not labels.issubset(ids)
            or any(
                not isinstance(v, str) or not re.fullmatch(r"[a-z][a-z0-9-]{1,48}", v)
                for v in ids.values()
            )
            or len(ids.values()) != len(set(ids.values()))
        ):
            raise DataError(
                "Every label needs an explicit unique stable organizational ID. Renames must be mapped, not inferred."
            )
    a = analyze(rows, policy)
    return {
        "manifest": manifest,
        "source_sha256": sha256(raw).hexdigest(),
        "snapshot_hash": stable_hash(
            {"manifest": manifest, "source_sha256": sha256(raw).hexdigest()}
        ),
        "analysis": a,
    }


def compare(before: dict, after: dict) -> dict:
    b, a = before["manifest"], after["manifest"]
    if date.fromisoformat(b["reporting_date"]) >= date.fromisoformat(a["reporting_date"]):
        raise DataError(
            "Reporting dates must be distinct and ordered; same-period restatements are not period movements."
        )
    if b["snapshot_id"] == a["snapshot_id"]:
        raise DataError("Distinct periods require distinct snapshot IDs.")
    if before["analysis"]["policy_id"] != after["analysis"]["policy_id"]:
        raise DataError(
            "Policy changed. Recalculate both snapshots under one policy before comparing."
        )

    def index(s):
        m = s["manifest"]
        items = {}
        for r in s["analysis"]["audit"]:
            key = (
                m["borrower_ids"][r["provider"]],
                m["payer_ids"][r["payer"]],
                r["age"],
            )
            if key in items:
                raise DataError("Duplicate stable cohort identity.")
            items[key] = r
        return items

    left, right = index(before), index(after)
    movements = []
    for key in sorted(left.keys() | right.keys()):
        old, new = left.get(key), right.get(key)
        if old and new and old["type"] != new["type"]:
            raise DataError(
                "Payer taxonomy changed for a stable identity. Review before comparing."
            )
        status = "continuing" if old and new else "added" if new else "removed"
        amounts = {
            k: (Decimal(new["amounts_exact"][k]) if new else Decimal(0))
            - (Decimal(old["amounts_exact"][k]) if old else Decimal(0))
            for k in ("gross_ar", "borrowing_base")
        }
        renamed = bool(
            old and new and (old["payer"] != new["payer"] or old["provider"] != new["provider"])
        )
        movements.append(
            {
                "borrower_id": key[0],
                "payer_id": key[1],
                "age": key[2],
                "provider": (new or old)["provider"],
                "payer": (new or old)["payer"],
                "status": status,
                "explicit_rename": renamed,
                "before_cohort_id": old["cohort_id"] if old else None,
                "after_cohort_id": new["cohort_id"] if new else None,
                "gross_delta": money(amounts["gross_ar"]),
                "base_delta": money(amounts["borrowing_base"]),
                "delta_exact": {k: format(v, ".2f") for k, v in amounts.items()},
            }
        )
    bridge = {}
    for k in ("gross_ar", "borrowing_base"):
        start = Decimal(before["analysis"]["summary_exact"][k])
        end = Decimal(after["analysis"]["summary_exact"][k])
        parts = {
            status: sum(
                (Decimal(x["delta_exact"][k]) for x in movements if x["status"] == status),
                Decimal(0),
            )
            for status in ("continuing", "added", "removed")
        }
        assert start + sum(parts.values()) == end
        bridge[k] = {
            "opening": format(start, ".2f"),
            **{s: format(v, ".2f") for s, v in parts.items()},
            "closing": format(end, ".2f"),
            "delta": format(end - start, ".2f"),
            "reconciled": True,
        }
    deltas = {
        k: round(after["analysis"]["summary"][k] - before["analysis"]["summary"][k], 6)
        for k in ("aged_share", "denial_rate", "top_payer_share")
    }
    alerts = []
    for k, label in [
        ("aged_share", "Aged gross share"),
        ("denial_rate", "Gross-weighted denial rate"),
        ("top_payer_share", "Top-payer gross concentration"),
    ]:
        if deltas[k] > 0:
            alerts.append(
                {
                    "metric": k,
                    "text": f"{label} increased by {deltas[k] * 100:.4f} percentage points in the fictional study.",
                    "delta": deltas[k],
                }
            )
    result = {
        "before": {
            "manifest": b,
            "source_sha256": before["source_sha256"],
            "snapshot_hash": before["snapshot_hash"],
            "analysis_id": before["analysis"]["analysis_id"],
            "summary": before["analysis"]["summary"],
        },
        "after": {
            "manifest": a,
            "source_sha256": after["source_sha256"],
            "snapshot_hash": after["snapshot_hash"],
            "analysis_id": after["analysis"]["analysis_id"],
            "summary": after["analysis"]["summary"],
        },
        "policy_id": before["analysis"]["policy_id"],
        "policy": before["analysis"]["policy_exact"],
        "bridge": bridge,
        "movements": movements,
        "ratio_deltas": deltas,
        "alerts": alerts,
        "restatement_included": b["revision"] > 1 or a["revision"] > 1,
        "headroom_delta": None,
        "limitations": "Balance changes only; no cash collections, remittance reconciliation, migration attribution, reserves or outstandings supplied. Headroom cannot be calculated. Ratio deltas use six-decimal displayed ratios. Explicit identity maps required for renames.",
    }
    from .change_review import build_review

    result["change_review"] = build_review(before, after, result)
    return result
