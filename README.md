# Smart Beneficiary Identification System (SBIS)

A production-grade, full-stack government welfare eligibility portal built for a hackathon demo.

## 🚀 Quick Start

```bash
cd smart-beneficiary
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python seed_data.py   # Populate with 15 test applications
./venv/bin/python app.py          # Start server on port 8080
```

Open **http://127.0.0.1:8080**

---

## 🔑 Demo Credentials

| Role  | Phone        | Password  | Redirect |
|-------|--------------|-----------|----------|
| Admin | 9999999999   | admin123  | /admin   |
| User  | 9000000001   | test123   | /status  |

---

## 🏗 Architecture

```
Flask (API + HTML server)
├── modules/
│   ├── auth.py       — JWT generation & decorators
│   ├── scoring.py    — 0-100 eligibility rule engine
│   ├── fraud.py      — Duplicate Aadhaar/phone + anomaly detection
│   ├── decision.py   — Final status decision
│   └── analytics.py  — Aggregated chart data
├── routes/
│   ├── auth_routes.py        — /api/register, /api/login
│   ├── application_routes.py — /api/apply, /api/status
│   └── admin_routes.py       — /api/admin/*, /api/analytics
├── models.py    — User, Application, AdminAction tables
├── config.py    — Configurable thresholds
└── static/
    ├── css/style.css          — Full design system CSS
    └── pages/
        ├── index.html         — Landing + Login
        ├── register.html      — Registration
        ├── apply.html         — Beneficiary application form
        ├── status.html        — User status + score ring
        ├── admin.html         — Admin dashboard
        └── analytics.html     — Charts (Chart.js)
```

---

## 🧮 Eligibility Scoring Rules

| Rule                            | Points |
|---------------------------------|--------|
| Annual income < ₹2,50,000      | +40    |
| Family size > 4                 | +20    |
| Rural location                  | +20    |
| Age ≥ 60 (senior citizen)      | +10    |
| Age < 18 (minor)               | +10    |
| **Score ≥ 60 → Eligible**      |        |

---

## 🕵️ Fraud Detection

1. **Duplicate Aadhaar** — same 12-digit ID previously submitted
2. **Duplicate Phone** — same number used in another application
3. **Anomaly Pattern** — income < ₹50,000 AND urban location

---

## ⚖️ Decision Engine

```
if fraud_flag → "Under Review"
elif score ≥ 60 → "Eligible"
else → "Not Eligible"
```

---

## 📡 API Endpoints

| Method | Endpoint                  | Auth     | Description              |
|--------|---------------------------|----------|--------------------------|
| POST   | /api/register             | None     | Register new user        |
| POST   | /api/login                | None     | Login, returns JWT       |
| POST   | /api/apply                | User JWT | Submit application       |
| GET    | /api/status               | User JWT | Get own application      |
| GET    | /api/admin/applications   | Admin    | All apps + filters       |
| POST   | /api/admin/override       | Admin    | Override decision        |
| GET    | /api/analytics            | Any JWT  | Aggregated stats         |

---

## 📊 Seeded Test Data

15 applications covering:
- ✅ 6 Eligible (score ≥ 60, no fraud)
- ❌ 4 Not Eligible (score < 60)
- 🔍 3 Under Review (fraud flagged)
- 🎉 1 Approved (admin override)
- 🚫 1 Rejected (admin override)

---

## 🔧 Configuration

All thresholds are in `config.py` — change them without touching business logic:

```python
SCORE_THRESHOLD    = 60      # Minimum score to qualify
INCOME_THRESHOLD   = 250000  # Annual income threshold (₹)
FAMILY_SIZE_THRESHOLD = 4    # Large family threshold
INCOME_SCORE       = 40      # Points for low income
FAMILY_SCORE       = 20      # Points for large family
RURAL_SCORE        = 20      # Points for rural location
AGE_SCORE          = 10      # Points for senior/minor
```
