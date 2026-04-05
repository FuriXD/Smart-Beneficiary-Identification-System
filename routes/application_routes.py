"""
routes/application_routes.py — /api/apply and /api/status endpoints
"""

from flask import Blueprint, request, jsonify
from models import db, Application
from modules.auth import token_required
from modules.scoring import compute_score
from modules.fraud import detect_fraud
from modules.decision import make_decision

app_bp = Blueprint("applications", __name__)


@app_bp.route("/api/apply", methods=["POST"])
@token_required
def apply(current_user):
    """Submit a beneficiary application. One active application per user."""

    # Check if user already has an application
    existing = Application.query.filter_by(user_id=current_user.id).first()
    if existing:
        return jsonify({
            "error": "You have already submitted an application",
            "application_id": existing.id,
            "status": existing.status
        }), 409

    data = request.get_json()

    # Validate required fields
    required = ["name", "age", "income", "family_size", "location", "aadhaar", "phone"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Type coercion and validation
    try:
        age = int(data["age"])
        income = float(data["income"])
        family_size = int(data["family_size"])
    except (ValueError, TypeError):
        return jsonify({"error": "age, income, family_size must be valid numbers"}), 400

    if age < 0 or age > 120:
        return jsonify({"error": "Invalid age"}), 400
    if income < 0:
        return jsonify({"error": "Income cannot be negative"}), 400
    if family_size < 1:
        return jsonify({"error": "Family size must be at least 1"}), 400

    location = data["location"].lower()
    if location not in ("urban", "rural"):
        return jsonify({"error": "Location must be 'urban' or 'rural'"}), 400

    aadhaar = str(data["aadhaar"]).strip()
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        return jsonify({"error": "Aadhaar must be exactly 12 digits"}), 400

    phone = str(data["phone"]).strip()
    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"error": "Phone must be exactly 10 digits"}), 400

    # --- Scoring Engine ---
    score_result = compute_score(income, family_size, location, age)
    score = score_result["score"]

    # --- Fraud Detection ---
    fraud_result = detect_fraud(aadhaar, phone, income, location)
    is_fraud = fraud_result["is_fraud"]
    fraud_reason = fraud_result["reason_str"]

    # --- Decision Engine ---
    status = make_decision(score, is_fraud)

    # Persist application
    application = Application(
        user_id=current_user.id,
        name=data["name"].strip(),
        age=age,
        income=income,
        family_size=family_size,
        location=location,
        aadhaar=aadhaar,
        phone=phone,
        score=score,
        fraud_flag=is_fraud,
        fraud_reason=fraud_reason,
        status=status
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({
        "message": "Application submitted successfully",
        "application": application.to_dict(),
        "score_breakdown": score_result["breakdown"],
        "status": status
    }), 201


@app_bp.route("/api/status", methods=["GET"])
@token_required
def check_status(current_user):
    """Check the status of the current user's application."""
    application = Application.query.filter_by(user_id=current_user.id).first()
    if not application:
        return jsonify({"message": "No application found", "has_application": False}), 200

    return jsonify({
        "has_application": True,
        "application": application.to_dict()
    }), 200


@app_bp.route("/api/ml-predict", methods=["POST"])
@token_required
def ml_predict(current_user):
    """
    Run ML-based fraud probability estimation.
    Body: { income, family_size, location, age, fraud_flag }
    Returns: { fraud_probability: 0.0-1.0 | null }
    """
    from modules.ml_fraud import predict_fraud_probability
    data = request.get_json() or {}
    try:
        prob = predict_fraud_probability(
            income=float(data.get("income", 0)),
            family_size=int(data.get("family_size", 1)),
            location=str(data.get("location", "urban")),
            age=int(data.get("age", 30)),
            fraud_flag=bool(data.get("fraud_flag", False))
        )
        return jsonify({"fraud_probability": prob}), 200
    except Exception as e:
        return jsonify({"fraud_probability": None, "error": str(e)}), 200
