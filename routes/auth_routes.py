"""
routes/auth_routes.py — /api/register and /api/login endpoints
"""

from flask import Blueprint, request, jsonify
from models import db, User
from modules.auth import generate_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register", methods=["POST"])
def register():
    """Register a new user (citizen). Admins are seeded, not self-registered."""
    data = request.get_json()

    # Validate required fields
    required = ["name", "phone", "aadhaar", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Aadhaar must be 12 digits
    aadhaar = str(data["aadhaar"]).strip()
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        return jsonify({"error": "Aadhaar must be exactly 12 digits"}), 400

    # Phone must be 10 digits
    phone = str(data["phone"]).strip()
    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"error": "Phone must be exactly 10 digits"}), 400

    # Check uniqueness
    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Phone number already registered"}), 409

    if User.query.filter_by(aadhaar=aadhaar).first():
        return jsonify({"error": "Aadhaar already registered"}), 409

    if data.get("email") and User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    # Create user
    user = User(
        name=data["name"].strip(),
        phone=phone,
        aadhaar=aadhaar,
        email=data.get("email", "").strip() or None,
        role="user"
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = generate_token(user)
    return jsonify({
        "message": "Registration successful",
        "token": token,
        "user": user.to_dict()
    }), 201


@auth_bp.route("/api/login", methods=["POST"])
def login():
    """Login with phone + password. Returns JWT on success."""
    data = request.get_json()

    phone = str(data.get("phone", "")).strip()
    password = data.get("password", "")

    if not phone or not password:
        return jsonify({"error": "Phone and password are required"}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid phone number or password"}), 401

    token = generate_token(user)
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    }), 200
