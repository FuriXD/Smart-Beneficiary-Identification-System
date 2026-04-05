"""
modules/decision.py — Final decision engine
Combines eligibility score + fraud flag to produce a status.
"""

from config import Config


def make_decision(score: int, is_fraud: bool) -> str:
    """
    Determine final eligibility status.

    Priority:
        1. Fraud detected → Under Review (human review needed)
        2. Score qualifies → Eligible
        3. Otherwise      → Not Eligible

    Returns:
        Status string: "Eligible" | "Not Eligible" | "Under Review"
    """
    if is_fraud:
        return "Under Review"
    elif score >= Config.SCORE_THRESHOLD:
        return "Eligible"
    else:
        return "Not Eligible"
