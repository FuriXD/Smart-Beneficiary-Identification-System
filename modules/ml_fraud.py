"""
modules/ml_fraud.py — Simple ML fraud risk predictor.

Uses logistic regression (scikit-learn) trained on rule-derived feature
combinations. Since we don't have labelled ground truth from a real dataset,
we SIMULATE training data from the same rule logic used in fraud.py — this
makes the ML score a complementary "second opinion" rather than a duplicate.

The model is trained once at startup and cached on the module.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------- #
# Synthetic training data (rule-inspired, not identical to rule logic)        #
# --------------------------------------------------------------------------- #
#  Features: [income_norm, family_size, is_rural, age, fraud_label]            #
#  income_norm = income / 1_000_000  (normalized 0-1 for ~₹0-10L range)       #
#  fraud_label = 1 if suspicious pattern, 0 if legitimate                      #
# --------------------------------------------------------------------------- #

_TRAINING_SEED = [
    # income_norm, family_size, is_rural, age, label
    # ── Legitimate applicants (label=0) ─────────────────────────────────────
    (0.12, 5, 1, 45, 0),
    (0.08, 6, 1, 60, 0),
    (0.18, 4, 1, 35, 0),
    (0.00, 3, 1, 70, 0),
    (0.22, 5, 0, 30, 0),   # low income urban — borderline
    (0.15, 7, 1, 25, 0),
    (0.10, 4, 1, 22, 0),
    (0.05, 6, 1, 55, 0),
    (0.20, 3, 1, 68, 0),
    (0.16, 5, 1, 40, 0),
    (0.09, 4, 0, 50, 0),
    (0.14, 6, 1, 33, 0),
    # ── Suspicious / anomalous patterns (label=1) ───────────────────────────
    (0.04, 2, 0, 29, 1),   # very low income + urban = suspicious
    (0.03, 1, 0, 24, 1),
    (0.02, 2, 0, 31, 1),
    (0.01, 1, 0, 27, 1),
    (0.05, 2, 0, 22, 1),
    (0.90, 5, 1, 40, 1),   # very high income claiming welfare
    (0.80, 4, 1, 38, 1),
    (0.75, 6, 1, 42, 1),
    (0.95, 3, 1, 50, 1),
    (1.00, 2, 0, 35, 1),
    (0.85, 4, 0, 45, 1),
    # ── Mixed / edge cases ──────────────────────────────────────────────────
    (0.25, 3, 0, 35, 0),
    (0.30, 4, 0, 42, 0),
    (0.35, 5, 1, 48, 0),
    (0.60, 3, 0, 30, 1),
    (0.55, 2, 0, 34, 1),
]


def _train():
    """Train a logistic regression model on the synthetic seed data."""
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline

        data = np.array(_TRAINING_SEED, dtype=float)
        X = data[:, :-1]   # features
        y = data[:, -1]    # labels

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf",    LogisticRegression(max_iter=300, C=1.0, random_state=42))
        ])
        model.fit(X, y)
        return model
    except ImportError:
        return None   # scikit-learn not installed


# Module-level singleton — trained once on import
_MODEL = _train()


def predict_fraud_probability(income: float, family_size: int, location: str,
                               age: int, fraud_flag: bool = False) -> float | None:
    """
    Return a 0.0–1.0 fraud probability estimate.
    Returns None if scikit-learn is not available.

    Parameters
    ----------
    income      : annual income in ₹
    family_size : number of family members
    location    : "rural" or "urban"
    age         : applicant age
    fraud_flag  : existing rule-based fraud flag (used as a soft prior)
    """
    if _MODEL is None:
        return None

    income_norm = min(income / 1_000_000, 1.0)
    is_rural    = 1 if str(location).lower() == "rural" else 0
    features    = np.array([[income_norm, family_size, is_rural, age]])

    prob = _MODEL.predict_proba(features)[0][1]      # P(fraud=1)

    # Soft boost if rule engine also flagged
    if fraud_flag:
        prob = min(prob + 0.15, 0.99)

    return round(float(prob), 4)
