"""
modules/fraud.py — Fraud detection engine
Checks for duplicate Aadhaar, duplicate phone, and pattern anomalies.
"""

from models import Application


def detect_fraud(aadhaar: str, phone: str, income: float, location: str,
                 exclude_id: int = None) -> dict:
    """
    Run fraud detection checks against existing applications.

    Args:
        aadhaar: Aadhaar number submitted
        phone: Phone number submitted
        income: Annual income submitted
        location: 'urban' or 'rural'
        exclude_id: Application ID to exclude (for re-checks)

    Returns:
        dict with 'is_fraud' (bool) and 'reasons' (list of str)
    """
    reasons = []

    # Build base query excluding the current application (if updating)
    base_q = Application.query
    if exclude_id is not None:
        base_q = base_q.filter(Application.id != exclude_id)

    # Check 1: Duplicate Aadhaar
    dup_aadhaar = base_q.filter_by(aadhaar=aadhaar).first()
    if dup_aadhaar:
        reasons.append(f"Duplicate Aadhaar — matches application #{dup_aadhaar.id}")

    # Check 2: Duplicate phone
    dup_phone = base_q.filter_by(phone=phone).first()
    if dup_phone:
        reasons.append(f"Duplicate phone number — matches application #{dup_phone.id}")

    # Check 3: Pattern anomaly — very low income but urban
    # Suspicious: claims income < 50,000 and says location is urban
    if income < 50000 and location.lower() == "urban":
        reasons.append(
            "Anomaly: Declared income < ₹50,000 yet location is Urban — flagged for review"
        )

    return {
        "is_fraud": len(reasons) > 0,
        "reasons": reasons,
        "reason_str": "; ".join(reasons) if reasons else None
    }
