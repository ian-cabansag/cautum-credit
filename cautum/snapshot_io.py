"""Bounded synthetic snapshot pair input. No raw-file persistence or model calls."""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .parser import DataError
from .surveillance import compare, snapshot


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    snapshot_id: str = Field(pattern=r"^[a-z][a-z0-9-]{1,48}$")
    reporting_date: str = Field(max_length=10)
    revision: int = Field(ge=1, le=1000000)
    kind: Literal["synthetic"]
    borrower_ids: dict[str, str] = Field(max_length=2500)
    payer_ids: dict[str, str] = Field(max_length=2500)
    source_note: str = Field(max_length=240)
    imported_at: None

    @model_validator(mode="after")
    def bounded_text(self):
        texts = [self.snapshot_id, self.reporting_date, self.source_note]
        for mapping in (self.borrower_ids, self.payer_ids):
            if any(len(k) > 70 for k in mapping):
                raise ValueError("Organizational labels are limited to 70 characters.")
            texts.extend(mapping)
            texts.extend(mapping.values())
        if any(any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF for c in t) for t in texts):
            raise ValueError("Invalid control or surrogate character in manifest.")
        return self


def _unique(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise DataError("Duplicate manifest keys are not supported.")
        out[k] = v
    return out


def parse_manifest(text):
    if len(text.encode()) > 32768:
        raise DataError("Each identity manifest must be at most 32 KiB.")
    try:
        return Manifest.model_validate(json.loads(text, object_pairs_hook=_unique)).model_dump()
    except (ValueError, ValidationError, TypeError, RecursionError):
        raise DataError(
            "Invalid synthetic identity manifest. Use the complete JSON template."
        ) from None


async def read_pair(
    policy, opening, closing, opening_manifest, closing_manifest, synthetic, example="portfolio"
):
    from .examples import EXAMPLES, description, example_sources

    if example not in {"portfolio", *EXAMPLES}:
        raise DataError("Unknown synthetic example.")
    supplied = [
        opening is not None,
        closing is not None,
        bool(opening_manifest),
        bool(closing_manifest),
    ]
    if any(supplied):
        if example != "portfolio":
            raise DataError("Do not combine uploaded sources with a bundled example.")
        if not all(supplied) or not synthetic:
            raise DataError(
                "Provide both CSVs and both identity manifests, and confirm synthetic-only data."
            )
        sources = []
        for f in (opening, closing):
            if not (f.filename or "").lower().endswith(".csv"):
                raise DataError("Snapshot uploads must be .csv files.")
            raw = await f.read(2_000_001)
            if len(raw) > 2_000_000:
                raise DataError("Snapshot CSV exceeds the file size limit.")
            sources.append(raw)
        meta = [parse_manifest(opening_manifest), parse_manifest(closing_manifest)]
        pair = [snapshot(raw, m, policy) for raw, m in zip(sources, meta)]
        origin = "uploaded synthetic pair"
    elif example == "portfolio":
        root = Path(__file__).resolve().parent / "data"
        pair = [
            snapshot(
                (root / f"synthetic_{p}.csv").read_bytes(),
                parse_manifest((root / f"synthetic_{p}.json").read_text()),
                policy,
            )
            for p in ("T0", "T1")
        ]
        origin = "bundled synthetic pair"
    else:
        pair = [snapshot(raw, manifest, policy) for raw, manifest in example_sources(example)]
        origin = "constructed synthetic example"
    if sum(len(p["analysis"]["audit"]) for p in pair) > 2500:
        raise DataError(
            "Comparison is limited to 2,500 total source cohorts across both snapshots."
        )
    result = compare(*pair)
    result["source_kind"] = origin
    result["example"] = description(example) if example != "portfolio" else None
    return result
