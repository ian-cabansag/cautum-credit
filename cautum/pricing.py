"""Published model-rate reference, separate from gateway/account billing."""

from decimal import Decimal

AZURE_SOURCE = "https://azure.microsoft.com/en-us/blog/gpt-6-astra-sol-and-luna-for-production-agents-in-microsoft-foundry/"
OPENAI_SOURCE = "https://developers.openai.com/api/docs/models/gpt-6-luna"
VERIFIED_ON = "2026-10-25"
RATES = {"input": "0.10", "cached_input": "0.01", "output": "0.50"}


def reference_estimate(usage, calls, provider, model):
    if model != "gpt-6-luna" or not calls or any(v is None for v in usage.values()):
        return None
    if any(c.get("service_tier") not in (None, "default", "standard") for c in calls):
        return None
    if provider == "portkey":
        if any(
            c.get("gateway_provider") != "azure-openai"
            or c.get("returned_model") != "gpt-6-luna-global"
            for c in calls
        ):
            return None
        source = AZURE_SOURCE
    elif provider == "openai":
        if any(not str(c.get("returned_model", "")).startswith("gpt-6-luna") for c in calls):
            return None
        source = OPENAI_SOURCE
    else:
        return None
    cost = (
        (usage["input_tokens"] - usage["cached_input_tokens"]) * Decimal(RATES["input"])
        + usage["cached_input_tokens"] * Decimal(RATES["cached_input"])
        + usage["output_tokens"] * Decimal(RATES["output"])
    ) / Decimal(1_000_000)
    return {
        "usd": format(cost, "f"),
        "rates_usd_per_million": RATES.copy(),
        "source_url": source,
        "verified_on": VERIFIED_ON,
        "basis": "Observed usage × published short-context Global Standard model rates. Excludes gateway fees, account discounts, hosting and support; not an invoice.",
        "gateway_cache_hit": any(c.get("gateway_cache_status") == "HIT" for c in calls),
        "cache_note": "Gateway HIT responses may replay prior token counts. Reference estimate is uncached-equivalent model cost, not verified new billable usage.",
    }
