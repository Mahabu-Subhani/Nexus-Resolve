import re

HOURLY_ENG_COST_USD = 120

_DOLLAR_OR_PERCENT_PATTERN = re.compile(
    r"\$\s?\d[\d,]*(?:\.\d+)?\s?(?:[kK]|[mM]illion|[mM]|[bB]illion|[bB])?"
    r"|\d[\d,]*(?:\.\d+)?\s?%"
)

def estimate_structural_cost_usd(estimated_hours: float, hourly_rate: float = HOURLY_ENG_COST_USD) -> dict:
    total_cost = round(estimated_hours * hourly_rate, 2)
    return {
        "hourly_rate_assumption_usd": hourly_rate,
        "estimated_hours": estimated_hours,
        "estimated_structural_cost_usd": total_cost,
        "assumption_note": f"${hourly_rate}/hr fully-loaded engineering cost x {estimated_hours}h = ${total_cost:,.2f}."
    }

def extract_stated_financial_claims(proposal_text: str) -> list[str]:
    return _DOLLAR_OR_PERCENT_PATTERN.findall(proposal_text or "")
