"""Generate reproducible fictional periods. Balance changes are not cash remittances."""

import csv
import io
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from cautum.engine import stable_hash
from cautum.parser import parse_csv

ROOT = Path(__file__).resolve().parents[1] / "cautum" / "data"
raw = (ROOT / "synthetic_receivables.csv").read_bytes()
rows = parse_csv(raw)
provider_ids = {r.provider: "borrower-" + stable_hash(r.provider)[:10] for r in rows}
payer_ids = {r.payer: "payer-" + stable_hash(r.payer)[:10] for r in rows}
for period, day in [("T0", "2026-08-31"), ("T1", "2026-09-30")]:
    records = list(csv.DictReader(io.StringIO(raw.decode())))
    if period == "T1":
        for r in records:
            factor = Decimal("1.08") if r["aging_bucket"] == "91+" else Decimal(".97")
            r["gross_ar"] = str(
                (Decimal(r["gross_ar"]) * factor).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
            )
            if r["provider"] == "Meridian Behavioral Health":
                r["denial_rate"] = str(min(Decimal(1), Decimal(r["denial_rate"]) + Decimal(".02")))
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
    (ROOT / f"synthetic_{period}.csv").write_text(output.getvalue())
    manifest = {
        "snapshot_id": f"synthetic-{period.lower()}",
        "reporting_date": day,
        "revision": 1,
        "kind": "synthetic",
        "borrower_ids": provider_ids,
        "payer_ids": payer_ids,
        "source_note": "Bundled fictional cohort balances; no bank cash or remittance evidence",
        "imported_at": None,
    }
    (ROOT / f"synthetic_{period}.json").write_text(json.dumps(manifest, indent=2) + "\n")
