"""
app.py — Flask application entry point
Registers all blueprints, initializes DB, serves static HTML pages.
"""

import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from models import db

# ─── Factory ───────────────────────────────────────────────────────────────────

def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(Config)

    CORS(app)           # Allow cross-origin requests during development
    db.init_app(app)

    # Register route blueprints
    from routes.auth_routes import auth_bp
    from routes.application_routes import app_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(app_bp)
    app.register_blueprint(admin_bp)

    # ── HTML page routes ───────────────────────────────────────────────────────
    pages_dir = os.path.join(app.static_folder, "pages")

    @app.route("/")
    def index():
        return send_from_directory(pages_dir, "index.html")

    @app.route("/register")
    def register_page():
        return send_from_directory(pages_dir, "register.html")

    @app.route("/apply")
    def apply_page():
        return send_from_directory(pages_dir, "apply.html")

    @app.route("/status")
    def status_page():
        return send_from_directory(pages_dir, "status.html")

    @app.route("/admin")
    def admin_page():
        return send_from_directory(pages_dir, "admin.html")

    @app.route("/analytics")
    def analytics_page():
        return send_from_directory(pages_dir, "analytics.html")

    # ── Error handlers ─────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    # ── Create tables ──────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


# ─── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    application = create_app()
    print("\n" + "="*60)
    print("  Smart Beneficiary Identification System")
    print("  Running at: http://127.0.0.1:8080")
    print("  Admin login:  phone=9999999999  password=admin123")
    print("  User login:   phone=9000000001  password=test123")
    print("="*60 + "\n")
    application.run(debug=True, host="0.0.0.0", port=8080)
