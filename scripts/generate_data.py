"""Reproducible, fictional organization-level aggregated cohort dataset; NO PHI."""

import csv
import random
from pathlib import Path

CSV_COLUMNS = [
    "provider",
    "payer",
    "payer_type",
    "aging_bucket",
    "gross_ar",
    "contractual_adjustment_rate",
    "historical_collection_factor",
    "denial_rate",
]

OUT = Path(__file__).resolve().parent.parent / "cautum" / "data" / "synthetic_receivables.csv"
PROVIDERS = [
    ("Harborview Regional Hospital", 1.2, 0.0, 0.0),
    ("Northstar Ambulatory Surgery", 0.75, -0.02, -0.02),
    ("Lakeside Imaging Partners", 0.75, 0.0, 0.06),
    ("Meridian Behavioral Health", 0.68, 0.06, 0.04),
    ("Summit Orthopedic Group", 0.9, -0.01, -0.02),
    ("Riverbend Community Hospital", 1.12, 0.04, 0.02),
    ("Atlantic Oncology Network", 1.05, -0.02, -0.01),
    ("Prairie Women's Health", 0.7, 0.01, -0.01),
]
PAYERS = [
    ("UnitedHealthcare", "Commercial", 0.20),
    ("Anthem / BCBS", "Commercial", 0.21),
    ("Aetna / CVS", "Commercial", 0.14),
    ("Cigna", "Commercial", 0.13),
    ("Medicare", "Medicare", 0.20),
    ("Medicaid", "Medicaid", 0.12),
]
AGING = [
    ("0-30", 0.48, 0.035),
    ("31-60", 0.26, 0.050),
    ("61-90", 0.15, 0.068),
    ("91+", 0.11, 0.092),
]


def main():
    rng = random.Random(1419)
    OUT.parent.mkdir(exist_ok=True, parents=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(CSV_COLUMNS)
        for provider, scale, denial_bump, concentration_bump in PROVIDERS:
            for payer, ptype, share in PAYERS:
                # purposeful risk scenarios, not real lender / payer observations
                adjusted_share = share + (
                    concentration_bump if payer == "Anthem / BCBS" else -concentration_bump / 5
                )
                for bucket, age_weight, base_denial in AGING:
                    gross = round(
                        (210000 + rng.randrange(30000, 90000)) * scale * adjusted_share * age_weight
                    )
                    if gross <= 0:
                        gross = 1000
                    adj = {"Commercial": 0.30, "Medicare": 0.37, "Medicaid": 0.42}[
                        ptype
                    ] + rng.uniform(-0.018, 0.018)
                    realization = (
                        {"Commercial": 0.96, "Medicare": 0.97, "Medicaid": 0.93}[ptype]
                        - (0.025 if bucket == "91+" else 0)
                        - rng.uniform(0, 0.018)
                    )
                    denial = min(
                        0.40,
                        max(0, base_denial + denial_bump + rng.uniform(-0.008, 0.009)),
                    )
                    wr.writerow(
                        [
                            provider,
                            payer,
                            ptype,
                            bucket,
                            gross,
                            f"{adj:.4f}",
                            f"{realization:.4f}",
                            f"{denial:.4f}",
                        ]
                    )
    print(f"Generated {OUT}")


if __name__ == "__main__":
    main()
