"""
models.py — SQLAlchemy database models
Tables: User, Application, AdminAction
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """Stores registered users (citizens and admins)."""
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(150), nullable=False)
    phone      = db.Column(db.String(15),  unique=True, nullable=False)
    aadhaar    = db.Column(db.String(12),  unique=True, nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=True)
    password   = db.Column(db.String(255), nullable=False)
    role       = db.Column(db.String(20),  default="user")      # "user" or "admin"
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    applications = db.relationship("Application", backref="user", lazy=True)

    def set_password(self, raw_pw):
        self.password = generate_password_hash(raw_pw)

    def check_password(self, raw_pw):
        return check_password_hash(self.password, raw_pw)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }


class Application(db.Model):
    """Stores beneficiary applications with computed score and status."""
    __tablename__ = "applications"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name        = db.Column(db.String(150), nullable=False)
    age         = db.Column(db.Integer,  nullable=False)
    income      = db.Column(db.Float,    nullable=False)
    family_size = db.Column(db.Integer,  nullable=False)
    location    = db.Column(db.String(20), nullable=False)   # "urban" | "rural"
    aadhaar     = db.Column(db.String(12), nullable=False)
    phone       = db.Column(db.String(15), nullable=False)

    # Computed fields
    score       = db.Column(db.Integer,  default=0)
    fraud_flag  = db.Column(db.Boolean,  default=False)
    fraud_reason= db.Column(db.String(300), nullable=True)
    status      = db.Column(db.String(30), default="Pending") # Eligible | Not Eligible | Under Review | Approved | Rejected

    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    admin_actions = db.relationship("AdminAction", backref="application", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "income": self.income,
            "family_size": self.family_size,
            "location": self.location,
            "aadhaar": self.aadhaar[:4] + "XXXXXXXX",  # mask for display
            "phone": self.phone,
            "score": self.score,
            "fraud_flag": self.fraud_flag,
            "fraud_reason": self.fraud_reason,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def to_admin_dict(self):
        """Full details for admin, including unmasked aadhaar."""
        d = self.to_dict()
        d["aadhaar"] = self.aadhaar  # unmasked for admin
        return d


class AdminAction(db.Model):
    """Audit log of every admin override."""
    __tablename__ = "admin_actions"

    id             = db.Column(db.Integer, primary_key=True)
    admin_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    action         = db.Column(db.String(30), nullable=False)   # "Approved" | "Rejected" | "Under Review"
    note           = db.Column(db.Text, nullable=True)
    timestamp      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "admin_id": self.admin_id,
            "application_id": self.application_id,
            "action": self.action,
            "note": self.note,
            "timestamp": self.timestamp.isoformat()
        }
