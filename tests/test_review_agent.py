"""Actual runner/dispatch safety with mocked provider. Never live model evidence."""

import json
from types import SimpleNamespace as NS

import openai
import pytest
from test_api import upload

from cautum import agent
from cautum import review_agent as review


class Item(NS):
    def model_dump(self, **kwargs):
        return vars(self)


def tool(bid="b0", name="read_review_evidence", arguments=None):
    return Item(
        type="function_call",
        name=name,
        call_id=f"call-{bid}",
        arguments=arguments if arguments is not None else json.dumps({"borrower_id": bid}),
    )


def response(items=None, selection=None, status="completed", usage=True):
    return NS(
        id="mock-response",
        status=status,
        output=items or [],
        output_text=json.dumps(
            selection
            or {
                "risk_ids": ["risk:limitations"],
                "question_ids": ["question:0"],
                "human_review_required": True,
            }
        ),
        usage=NS(input_tokens=100, input_tokens_details=NS(cached_tokens=10), output_tokens=20)
        if usage
        else None,
        service_tier="default",
    )


@pytest.fixture
def portfolio(monkeypatch):
    monkeypatch.setattr(agent, "provider", lambda: ("openai", "SYNTHETIC_TEST_KEY", "test-model"))
    monkeypatch.setattr(agent, "_call_count", 0)
    monkeypatch.setattr(agent, "MAX_AI_CALLS", 25)
    return upload().json()


def mock(monkeypatch, responses):
    queue = iter(responses)
    captured = []

    def create(**kwargs):
        captured.append(kwargs)
        value = next(queue)
        if isinstance(value, Exception):
            raise value
        return value

    class Client:
        def __init__(self, **kwargs):
            assert kwargs["max_retries"] == 0

        def __enter__(self):
            return NS(responses=NS(create=create))

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(openai, "OpenAI", Client)
    return captured


def test_real_dispatch_roundtrip_readonly_provenance(portfolio, monkeypatch):
    original = json.dumps(portfolio, sort_keys=True)
    captured = mock(monkeypatch, [response([tool()]), response()])
    result = review.investigate(portfolio)
    assert json.dumps(portfolio, sort_keys=True) == original
    assert result["source"] == "ai" and result["human_review_required"]
    assert result["investigation"]["trace"][0]["result"]["analysis_id"] == portfolio["analysis_id"]
    assert result["usage"] == {"input_tokens": 200, "cached_input_tokens": 20, "output_tokens": 40}
    assert captured[0]["tool_choice"] == "required" and captured[0]["store"] is False
    assert captured[0]["tools"][0]["strict"] is True
    assert captured[0]["parallel_tool_calls"] is False
    assert captured[1]["input"][-1]["type"] == "function_call_output"
    assert len(result["investigation"]["calls"]) == 2 and agent._call_count == 2


@pytest.mark.parametrize(
    "item",
    [
        tool("missing"),
        tool(name="shell"),
        tool(arguments='{"borrower_id":"b0","path":".env"}'),
        tool(arguments='{"borrower_id":"b0","borrower_id":"b1"}'),
        tool(arguments='["b0"]'),
        tool(arguments='{"borrower_id":5}'),
    ],
)
def test_untrusted_tool_calls_reject(portfolio, monkeypatch, item):
    mock(monkeypatch, [response([item])])
    with pytest.raises(review.ReviewUnavailable):
        review.investigate(portfolio)


def test_duplicate_tool_and_budget_reject(portfolio, monkeypatch):
    mock(monkeypatch, [response([tool()]), response([tool()])])
    with pytest.raises(review.ReviewUnavailable):
        review.investigate(portfolio)
    mock(monkeypatch, [response([tool()]), response([tool("b1")])])
    with pytest.raises(review.ReviewUnavailable):
        review.investigate(portfolio, profile="lean")


def test_must_actually_call_tool(portfolio, monkeypatch):
    mock(monkeypatch, [response()])
    with pytest.raises(review.ReviewUnavailable):
        review.investigate(portfolio)


@pytest.mark.parametrize(
    "selection",
    [
        {"risk_ids": ["risk:999"], "question_ids": ["question:0"], "human_review_required": True},
        {"risk_ids": [], "question_ids": ["question:0"], "human_review_required": False},
        {
            "risk_ids": ["risk:limitations", "risk:limitations"],
            "question_ids": ["question:0"],
            "human_review_required": True,
        },
        {
            "risk_ids": [],
            "question_ids": ["question:0"],
            "human_review_required": True,
            "amount": "$99999",
        },
    ],
)
def test_invalid_selection_rejects(portfolio, monkeypatch, selection):
    mock(monkeypatch, [response([tool()]), response(selection=selection)])
    with pytest.raises(review.ReviewUnavailable):
        review.investigate(portfolio)


def test_context_usage_and_failures_are_honest(portfolio, monkeypatch):
    mock(monkeypatch, [response([tool()], usage=False), response()])
    result = review.investigate(portfolio)
    assert all(x is None for x in result["usage"].values()) and result["cost"] is None
    mock(monkeypatch, [response([tool()]), TimeoutError("SYNTHETIC_TEST_KEY")])
    with pytest.raises(review.ReviewUnavailable) as error:
        review.investigate(portfolio)
    assert "SYNTHETIC_TEST_KEY" not in str(error.value)
    assert len(error.value.evidence["calls"]) == 1
    monkeypatch.setattr(agent, "MAX_AI_CALLS", 0)
    captured = mock(monkeypatch, [])
    with pytest.raises(review.ReviewUnavailable, match="budget"):
        review.investigate(portfolio)
    assert not captured


def test_exact_borrower_cents_reconcile(portfolio):
    borrowers = {f"b{i}": b for i, b in enumerate(portfolio["borrowers"])}
    from decimal import Decimal

    parts = [
        review.inspect_borrower(portfolio, b, borrowers, review.PROFILES["standard"])
        for b in borrowers
    ]
    for k, value in portfolio["summary_exact"].items():
        assert sum(Decimal(p["amounts_exact"][k]) for p in parts) == Decimal(value)


def test_inspected_evidence_only(portfolio, monkeypatch):
    first_name = portfolio["borrowers"][0]["name"]
    uninspected = next(
        f"risk:{i}" for i, f in enumerate(portfolio["alerts"]) if f["provider"] != first_name
    )
    mock(
        monkeypatch,
        [
            response([tool()]),
            response(
                selection={
                    "risk_ids": [uninspected],
                    "question_ids": ["question:0"],
                    "human_review_required": True,
                }
            ),
        ],
    )
    with pytest.raises(review.ReviewUnavailable):
        review.investigate(portfolio)


def test_single_borrower_uses_one_tool_and_valid_final_schema(portfolio, monkeypatch):
    from pathlib import Path

    from cautum.engine import analyze
    from cautum.parser import parse_csv

    a = analyze(parse_csv(Path("cautum/data/study_A.csv").read_bytes()))
    captured = mock(monkeypatch, [response([tool()]), response()])
    result = review.investigate(a)
    assert result["investigation"]["max_tools"] == 1
    assert captured[-1]["tool_choice"] == "none"
    assert captured[-1]["tools"][0]["parameters"]["properties"]["borrower_id"]["enum"]
