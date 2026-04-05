"""
modules/scoring.py — Eligibility scoring engine
Rule-based point system producing a 0-100 score.
"""

from config import Config


def compute_score(income: float, family_size: int, location: str, age: int) -> dict:
    """
    Compute eligibility score based on applicant attributes.

    Returns:
        dict with 'score' (int) and 'breakdown' (list of rule hits)
    """
    score = 0
    breakdown = []

    # Rule 1: Low income
    if income < Config.INCOME_THRESHOLD:
        score += Config.INCOME_SCORE
        breakdown.append({
            "rule": "Income below ₹2,50,000",
            "points": Config.INCOME_SCORE
        })

    # Rule 2: Large family
    if family_size > Config.FAMILY_SIZE_THRESHOLD:
        score += Config.FAMILY_SCORE
        breakdown.append({
            "rule": f"Family size greater than {Config.FAMILY_SIZE_THRESHOLD}",
            "points": Config.FAMILY_SCORE
        })

    # Rule 3: Rural location
    if location.lower() == "rural":
        score += Config.RURAL_SCORE
        breakdown.append({
            "rule": "Rural location",
            "points": Config.RURAL_SCORE
        })

    # Rule 4: Senior citizen
    if age >= Config.SENIOR_AGE:
        score += Config.AGE_SCORE
        breakdown.append({
            "rule": f"Senior citizen (age ≥ {Config.SENIOR_AGE})",
            "points": Config.AGE_SCORE
        })

    # Rule 5: Minor applicant
    elif age < Config.MINOR_AGE:
        score += Config.AGE_SCORE
        breakdown.append({
            "rule": f"Minor applicant (age < {Config.MINOR_AGE})",
            "points": Config.AGE_SCORE
        })

    # Cap score at 100
    score = min(score, 100)

    return {
        "score": score,
        "breakdown": breakdown,
        "threshold": Config.SCORE_THRESHOLD,
        "qualifies": score >= Config.SCORE_THRESHOLD
    }
