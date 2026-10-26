"""Strict schema allowlist to keep sensitive fields away from the app and LLM."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from .config import MAX_ROWS
from .schema import AGE_BUCKETS, CSV_COLUMNS, PAYER_TYPES


@dataclass(frozen=True)
class Receivable:
    provider: str
    payer: str
    payer_type: str
    aging_bucket: str
    gross_ar: Decimal
    contractual_adjustment_rate: Decimal
    historical_collection_factor: Decimal
    denial_rate: Decimal


class DataError(ValueError):
    pass


SAFE_LABEL = re.compile(r"^[\w &.'()/+-]{2,70}$", re.UNICODE)
SUSPICIOUS = re.compile(
    r"(@|https?://|\b\d{3}-\d{2}-\d{4}\b|\b(?:patient|dob|mrn|ssn|social security)\b|\b(?:ignore (?:all )?(?:previous|prior|system) instructions|reveal (?:the )?(?:key|prompt|secret))\b)",
    re.I,
)


def parse_csv(content: bytes) -> list[Receivable]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise DataError("Upload a UTF-8 CSV file.") from e
    if "\x00" in text:
        raise DataError("Binary/NUL content is not allowed.")
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        if not reader.fieldnames:
            raise DataError("CSV headers are missing.")
        if reader.fieldnames != CSV_COLUMNS:
            unknown = [x for x in reader.fieldnames if x not in CSV_COLUMNS]
            missing = [x for x in CSV_COLUMNS if x not in reader.fieldnames]
            raise DataError(
                f"Use the exact eight template columns in order. Unexpected: {unknown}. Missing: {missing}. Patient-level data is prohibited."
            )
        rows = []
        seen = set()
        labels = {}
        payer_types = {}
        for lineno, record in enumerate(reader, start=2):
            if len(rows) >= MAX_ROWS:
                raise DataError(f"Maximum {MAX_ROWS} data rows allowed.")
            if None in record or any(v is None for v in record.values()):
                raise DataError(f"Row {lineno}: inconsistent column count.")
            provider = record["provider"].strip()
            payer = record["payer"].strip()
            for label, value in (("provider", provider), ("payer", payer)):
                if (
                    not SAFE_LABEL.fullmatch(value)
                    or SUSPICIOUS.search(value)
                    or value.startswith(("=", "+", "-", "@"))
                ):
                    raise DataError(
                        f"Row {lineno}: invalid {label}. Use organization names only, never patient information."
                    )
            for kind, value in (("provider", provider), ("payer", payer)):
                identity = (kind, value.casefold())
                if identity in labels and labels[identity] != value:
                    raise DataError(
                        f"Row {lineno}: inconsistent {kind} spelling/case; normalize explicitly."
                    )
                labels[identity] = value
            payer_type = record["payer_type"].strip()
            aging = record["aging_bucket"].strip()
            if payer_type not in PAYER_TYPES or aging not in AGE_BUCKETS:
                raise DataError(f"Row {lineno}: payer_type or aging_bucket is not recognized.")
            if payer.casefold() in payer_types and payer_types[payer.casefold()] != payer_type:
                raise DataError(
                    f"Row {lineno}: inconsistent payer_type for payer; review taxonomy."
                )
            payer_types[payer.casefold()] = payer_type
            key = (provider.casefold(), payer.casefold(), aging)
            if key in seen:
                raise DataError(
                    f"Row {lineno}: duplicated provider / payer / aging cohort; aggregate before upload."
                )
            seen.add(key)

            def decimal_of(field: str, high: Decimal | None = None) -> Decimal:
                raw = record[field].strip()
                try:
                    value = Decimal(raw)
                except (InvalidOperation, ValueError) as e:
                    raise DataError(f"Row {lineno}: {field} is not a number.") from e
                if not value.is_finite() or value < 0 or (high is not None and value > high):
                    raise DataError(
                        f"Row {lineno}: {field} must be finite and between 0 and {high if high is not None else 'positive infinity'}."
                    )
                if value.as_tuple().exponent < -6:
                    raise DataError(
                        f"Row {lineno}: {field} has too many decimal places (maximum six)."
                    )
                return value

            gross = decimal_of("gross_ar")
            if gross > Decimal("1000000000000"):
                raise DataError(f"Row {lineno}: gross_ar exceeds demo safety limit.")
            rows.append(
                Receivable(
                    provider,
                    payer,
                    payer_type,
                    aging,
                    gross,
                    decimal_of("contractual_adjustment_rate", Decimal(1)),
                    decimal_of("historical_collection_factor", Decimal(1)),
                    decimal_of("denial_rate", Decimal(1)),
                )
            )
        if not rows:
            raise DataError("No receivables rows found.")
        if sum(x.gross_ar for x in rows) <= 0:
            raise DataError("Portfolio must contain positive gross receivables.")
        if sum(x.gross_ar for x in rows) > Decimal("1000000000000"):
            raise DataError("Portfolio gross exceeds the $1 trillion demo safety limit.")
        return rows
    except csv.Error as e:
        raise DataError("Malformed CSV file.") from e
