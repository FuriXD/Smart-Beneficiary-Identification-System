"""
config.py — App configuration constants
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "sbis-super-secret-key-2024")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'sbis.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRY_HOURS = 24

    # Eligibility thresholds
    SCORE_THRESHOLD = 60
    INCOME_THRESHOLD = 250000
    FAMILY_SIZE_THRESHOLD = 4
    INCOME_SCORE = 40
    FAMILY_SCORE = 20
    RURAL_SCORE = 20
    SENIOR_AGE = 60
    MINOR_AGE = 18
    AGE_SCORE = 10
