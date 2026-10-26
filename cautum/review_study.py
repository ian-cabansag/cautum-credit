"""Consented local founder/usability exercise. No claim of an independent lender pilot."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from threading import Lock
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .engine import analyze
from .parser import parse_csv

DATA = Path(__file__).resolve().parent / "data"
_lock = Lock()
_latest = None


class Trial(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    condition: Literal["worksheet", "cautum"]
    case: Literal["A", "B"]
    elapsed_seconds: float = Field(ge=1, le=7200)
    base_answer: str = Field(pattern=r"^\d{1,12}(\.\d{1,2})?$")
    excluded_age: Literal["0-30", "31-60", "61-90", "91+"]
    assistance: Literal["none", "documentation", "human help"]


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    protocol: Literal["paired-synthetic-v1"]
    role: Literal["founder", "student", "credit analyst", "other reviewer"]
    consent: Literal[True]
    trials: list[Trial] = Field(min_length=2, max_length=2)
    clarity: int = Field(ge=1, le=5)
    reuse: Literal["yes", "maybe", "no"]
    feedback: str = Field(max_length=800)


def record(observation: Observation):
    """Grade actual participant answers against the deterministic case, without coaching."""
    if {t.condition for t in observation.trials} != {"worksheet", "cautum"} or {
        t.case for t in observation.trials
    } != {"A", "B"}:
        raise ValueError("Use one different case per condition.")
    results = []
    for trial in observation.trials:
        data = (DATA / f"study_{trial.case}.csv").read_bytes()
        a = analyze(parse_csv(data))
        expected = a["summary_exact"]["borrowing_base"]
        results.append(
            {
                **trial.model_dump(),
                "expected_base": expected,
                "base_correct": Decimal(trial.base_answer) == Decimal(expected),
                "age_correct": trial.excluded_age == "91+",
                "analysis_id": a["analysis_id"],
            }
        )
    value = {
        **observation.model_dump(exclude={"trials"}),
        "trials": results,
        "source": "participant-submitted browser observation; times self-recorded by browser",
        "limitations": [
            "One participant, two different synthetic cases; no statistical inference.",
            "Order and learning effects are possible; browser timing is not independently observed.",
            "Founder participation, if selected, is not independent buyer validation.",
            "Compares worksheet calculation with Cautum, not AI quality or real lending outcomes.",
        ],
    }
    global _latest
    with _lock:
        _latest = value
    return value


def latest():
    with _lock:
        return _latest
