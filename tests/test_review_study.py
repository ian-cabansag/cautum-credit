from copy import deepcopy

from test_api import client

from cautum import review_study


def observation():
    return {
        "protocol": "paired-synthetic-v1",
        "role": "founder",
        "consent": True,
        "clarity": 4,
        "reuse": "maybe",
        "feedback": "Synthetic automated test; not participant evidence.",
        "trials": [
            {
                "condition": "worksheet",
                "case": "A",
                "elapsed_seconds": 60.0,
                "base_answer": "12257.28",
                "excluded_age": "91+",
                "assistance": "none",
            },
            {
                "condition": "cautum",
                "case": "B",
                "elapsed_seconds": 45.0,
                "base_answer": "1.00",
                "excluded_age": "0-30",
                "assistance": "none",
            },
        ],
    }


def test_grades_actual_answers_and_discloses_founder(monkeypatch):
    monkeypatch.setattr(review_study, "_latest", None)
    r = client.post("/api/review-study", json=observation())
    assert r.status_code == 200
    value = r.json()
    assert value["trials"][0]["base_correct"] and not value["trials"][1]["base_correct"]
    assert not value["trials"][1]["age_correct"]
    assert "not independent" in " ".join(value["limitations"])
    assert client.get("/api/review-study").json() == value


def test_consent_protocol_and_invalid_trials_reject(monkeypatch):
    monkeypatch.setattr(review_study, "_latest", None)
    original = observation()
    for key, value in [
        ("consent", False),
        ("role", "validated customer"),
        ("clarity", 6),
        ("feedback", "x" * 801),
    ]:
        x = deepcopy(original)
        x[key] = value
        assert client.post("/api/review-study", json=x).status_code == 422
    x = deepcopy(original)
    x["trials"][1]["case"] = "A"
    assert client.post("/api/review-study", json=x).status_code == 400
    assert client.get("/api/review-study").status_code == 404


def test_no_study_key_can_select_arbitrary_file():
    assert client.get("/data/study_A.csv").status_code == 200
    assert client.get("/study").headers.get("content-security-policy")


def test_reference_pricing_is_explicitly_not_invoice():
    from cautum.pricing import reference_estimate

    u = {"input_tokens": 9711, "cached_input_tokens": 0, "output_tokens": 105}
    calls = [
        {
            "gateway_provider": "azure-openai",
            "returned_model": "gpt-6-luna-global",
            "gateway_cache_status": "MISS",
            "service_tier": "default",
        }
    ]
    p = reference_estimate(u, calls, "portkey", "gpt-6-luna")
    assert p["usd"] == "0.0010236" and "not an invoice" in p["basis"]
    assert reference_estimate(u, calls, "portkey", "other") is None
    calls[0]["gateway_provider"] = "unknown"
    assert reference_estimate(u, calls, "portkey", "gpt-6-luna") is None
