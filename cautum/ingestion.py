"""Explicit safe aliases, no inferred denominators or discarded columns."""

import csv
import io

from .parser import DataError, parse_csv
from .schema import CSV_COLUMNS

ALIASES = {
    "provider": ["provider", "borrower"],
    "payer": ["payer", "payer_name"],
    "payer_type": ["payer_type", "payer_class"],
    "aging_bucket": ["aging_bucket", "age_band"],
    "gross_ar": ["gross_ar", "billed_ar_usd"],
    "contractual_adjustment_rate": [
        "contractual_adjustment_rate",
        "contract_adjustment",
    ],
    "historical_collection_factor": [
        "historical_collection_factor",
        "collection_factor_pre_denial",
    ],
    "denial_rate": ["denial_rate", "modeled_denial_rate"],
}


def normalize_csv(content: bytes, mapping: dict) -> bytes:
    if not isinstance(mapping, dict) or set(mapping) != set(CSV_COLUMNS):
        raise DataError("Mapping must explicitly cover all eight aggregate fields.")
    if any(not isinstance(v, str) or v not in ALIASES[k] for k, v in mapping.items()):
        raise DataError(
            "Mapping uses an unknown or incompatible field meaning. Check the data dictionary."
        )
    if len(set(mapping.values())) != 8:
        raise DataError("Each source field must map exactly once.")
    try:
        text = content.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        headers = next(reader, [])
        if len(headers) != 8 or len(set(headers)) != 8 or set(headers) != set(mapping.values()):
            raise DataError(
                "Extra, missing or duplicate source columns are prohibited. No columns may be silently discarded."
            )
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(CSV_COLUMNS)
        indexes = [headers.index(mapping[k]) for k in CSV_COLUMNS]
        for line, row in enumerate(reader, 2):
            if len(row) != 8:
                raise DataError(f"Row {line}: inconsistent column count.")
            writer.writerow([row[i] for i in indexes])
        normalized = output.getvalue().encode()
        parse_csv(normalized)  # Canonical boundary remains authoritative.
        return normalized
    except UnicodeDecodeError as exc:
        raise DataError("Upload a UTF-8 CSV file.") from exc
    except csv.Error as exc:
        raise DataError("Malformed CSV file.") from exc
