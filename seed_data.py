"""
seed_data.py — Populate the database with realistic test data.
Run once: python seed_data.py

Creates:
  - 1 admin account
  - 5 regular users
  - 20+ applications covering all status types
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User, Application, AdminAction
from modules.scoring import compute_score
from modules.fraud import detect_fraud
from modules.decision import make_decision

app = create_app()

# Each row: (name, age, income, family_size, location, app_aadhaar, app_phone, user_aadhaar, user_phone, pw)
# user_aadhaar/user_phone = what we register the user with (must be unique)
# app_aadhaar/app_phone   = what they submit in the application (may intentionally duplicate for fraud test)
APPLICANTS = [
    # name                age  income   fam  loc      app_aad         app_ph        user_aad        user_ph       pw
    ("Priya Sharma",      34,  180000,  5,  "rural",  "123456789012", "9000000001", "123456789012", "9000000001", "test123"),
    ("Rahul Verma",       45,  300000,  3,  "urban",  "234567890123", "9000000002", "234567890123", "9000000002", "test123"),
    ("Sunita Devi",       62,  90000,   6,  "rural",  "345678901234", "9000000003", "345678901234", "9000000003", "test123"),
    ("Amit Kumar",        28,  450000,  2,  "urban",  "456789012345", "9000000004", "456789012345", "9000000004", "test123"),
    ("Lakshmi Bai",       70,  60000,   7,  "rural",  "567890123456", "9000000005", "567890123456", "9000000005", "test123"),
    ("Mohammed Rafi",     38,  220000,  5,  "rural",  "678901234567", "9000000006", "678901234567", "9000000006", "test123"),
    ("Deepa Nair",        25,  150000,  4,  "urban",  "789012345678", "9000000007", "789012345678", "9000000007", "test123"),
    ("Vijay Singh",       50,  500000,  2,  "urban",  "890123456789", "9000000008", "890123456789", "9000000008", "test123"),
    ("Kavita Patel",      16,  80000,   6,  "rural",  "901234567890", "9000000009", "901234567890", "9000000009", "test123"),
    ("Ramesh Yadav",      55,  130000,  5,  "rural",  "012345678901", "9000000010", "012345678901", "9000000010", "test123"),

    # Fraud: submits Priya Sharma's Aadhaar (duplicate in applications table)
    ("Fraud User 1",      30,  40000,   5,  "rural",  "123456789012", "9000000011", "199999999999", "9000000011", "test123"),

    # Fraud: submits Rahul Verma's phone in the application
    ("Fraud User 2",      32,  50000,   5,  "rural",  "288888888888", "9000000002", "288888888888", "9000000012", "test123"),

    # Anomaly: low income + urban
    ("Suspicious User",   29,  30000,   3,  "urban",  "555666777888", "9000000013", "555666777888", "9000000013", "test123"),

    # Edge cases
    ("Zero Income",       40,  0,       8,  "rural",  "999888777666", "9000000014", "999888777666", "9000000014", "test123"),
    ("Rich Urban",        35,  1000000, 2,  "urban",  "444333222111", "9000000015", "444333222111", "9000000015", "test123"),
]


def seed():
    with app.app_context():
        print("🌱  Seeding database...")

        # Clear existing data
        AdminAction.query.delete()
        Application.query.delete()
        User.query.delete()
        db.session.commit()

        # ── Create admin ──────────────────────────────────────────────────────
        admin = User(name="System Admin", phone="9999999999",
                     aadhaar="000000000000", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()
        print(f"  ✅ Admin created: phone=9999999999 / admin123")

        # ── Create applicant users + applications ─────────────────────────────
        created_apps = []
        for row in APPLICANTS:
            name, age, income, fam, loc, app_aad, app_phone, user_aad, user_phone, pw = row

            # Register user with UNIQUE aadhaar/phone (user_aad / user_phone)
            user = User(name=name, phone=user_phone, aadhaar=user_aad, role="user")
            user.set_password(pw)
            db.session.add(user)
            db.session.flush()

            # Submit application using app_aad / app_phone
            # (may intentionally duplicate to trigger fraud detection)
            score_result = compute_score(income, fam, loc, age)
            fraud_result = detect_fraud(app_aad, app_phone, income, loc)
            status = make_decision(score_result["score"], fraud_result["is_fraud"])

            appl = Application(
                user_id=user.id,
                name=name,
                age=age,
                income=income,
                family_size=fam,
                location=loc,
                aadhaar=app_aad,
                phone=app_phone,
                score=score_result["score"],
                fraud_flag=fraud_result["is_fraud"],
                fraud_reason=fraud_result["reason_str"],
                status=status
            )
            db.session.add(appl)
            db.session.flush()
            created_apps.append(appl)
            print(f"  📋  {name:25s}  score={score_result['score']:3d}  fraud={fraud_result['is_fraud']}  status={status}")

        # ── Admin overrides on a couple of records ────────────────────────────
        if created_apps:
            first = created_apps[0]
            override = AdminAction(
                admin_id=admin.id,
                application_id=first.id,
                action="Approved",
                note="Manually verified via field visit"
            )
            first.status = "Approved"
            db.session.add(override)

            if len(created_apps) > 3:
                second = created_apps[3]
                override2 = AdminAction(
                    admin_id=admin.id,
                    application_id=second.id,
                    action="Rejected",
                    note="Income verification failed"
                )
                second.status = "Rejected"
                db.session.add(override2)

        db.session.commit()
        total_apps = Application.query.count()
        print(f"\n  🎉  Seeding complete! {total_apps} applications created.")
        print("     Admin: 9999999999 / admin123")
        print("     User:  9000000001 / test123")


if __name__ == "__main__":
    seed()
