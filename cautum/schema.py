"""Input contract and lender-configurable ILLUSTRATIVE policy."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Policy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(default="Cautum illustrative v0.1", max_length=64)
    advance_rate: Decimal = Field(default=Decimal("0.80"), ge=0, le=1)
    aging_0_30: Decimal = Field(default=Decimal("1.00"), ge=0, le=1)
    aging_31_60: Decimal = Field(default=Decimal("0.95"), ge=0, le=1)
    aging_61_90: Decimal = Field(default=Decimal("0.80"), ge=0, le=1)
    aging_91_plus: Decimal = Field(default=Decimal("0.00"), ge=0, le=1)
    payer_commercial: Decimal = Field(default=Decimal("1.00"), ge=0, le=1)
    payer_medicare: Decimal = Field(default=Decimal("0.90"), ge=0, le=1)
    payer_medicaid: Decimal = Field(default=Decimal("0.80"), ge=0, le=1)
    denial_alert: Decimal = Field(default=Decimal("0.09"), ge=0, le=1)
    aged_alert: Decimal = Field(default=Decimal("0.122"), ge=0, le=1)
    payer_concentration_alert: Decimal = Field(default=Decimal("0.215"), ge=0, le=1)
    minimum_advanceability: Decimal = Field(default=Decimal("0.45"), ge=0, le=1)

    @field_validator("*")
    @classmethod
    def bounded_precision(cls, value):
        if isinstance(value, Decimal) and (not value.is_finite() or value.as_tuple().exponent < -6):
            raise ValueError("Policy rates require finite values with at most six decimal places")
        return value

    def age_factor(self, bucket: str) -> Decimal:
        return {
            "0-30": self.aging_0_30,
            "31-60": self.aging_31_60,
            "61-90": self.aging_61_90,
            "91+": self.aging_91_plus,
        }[bucket]

    def payer_factor(self, payer_type: str) -> Decimal:
        return {
            "Commercial": self.payer_commercial,
            "Medicare": self.payer_medicare,
            "Medicaid": self.payer_medicaid,
        }[payer_type]

    def public(self) -> dict:
        return {k: float(v) if isinstance(v, Decimal) else v for k, v in self.model_dump().items()}


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
AGE_BUCKETS = ["0-30", "31-60", "61-90", "91+"]
PAYER_TYPES = ["Commercial", "Medicare", "Medicaid"]


class MemoSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    headline: str
    executive_summary: str
    positives: list[str]
    risks: list[str]
    diligence_questions: list[str]
    limitations: list[str]
    human_review_required: Literal[True] = True
