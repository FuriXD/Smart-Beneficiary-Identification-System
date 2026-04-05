"""
routes/admin_routes.py — Admin-only endpoints
GET  /api/admin/applications  — list all applications (with optional filters)
POST /api/admin/override      — manually approve/reject an application
GET  /api/analytics           — analytics data for charts
"""

from flask import Blueprint, request, jsonify
from models import db, Application, AdminAction
from modules.auth import admin_required, token_required
from modules.analytics import get_analytics

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/api/admin/applications", methods=["GET"])
@admin_required
def get_all_applications(current_user):
    """
    Return all applications. Supports query filters:
      ?status=Eligible|Not Eligible|Under Review|Approved|Rejected
      ?fraud=true
      ?search=<name substring>
    """
    query = Application.query

    status_filter = request.args.get("status")
    if status_filter:
        query = query.filter_by(status=status_filter)

    fraud_filter = request.args.get("fraud")
    if fraud_filter and fraud_filter.lower() == "true":
        query = query.filter_by(fraud_flag=True)

    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(Application.name.ilike(f"%{search}%"))

    # Pagination
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    paginated = query.order_by(Application.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "applications": [a.to_admin_dict() for a in paginated.items],
        "total": paginated.total,
        "page": page,
        "pages": paginated.pages
    }), 200


@admin_bp.route("/api/admin/override", methods=["POST"])
@admin_required
def override_application(current_user):
    """
    Manually override an application status.
    Body: { "application_id": int, "action": "Approved"|"Rejected"|"Under Review", "note": str }
    """
    data = request.get_json()
    app_id = data.get("application_id")
    action = data.get("action")
    note = data.get("note", "")

    if not app_id or not action:
        return jsonify({"error": "application_id and action are required"}), 400

    valid_actions = ["Approved", "Rejected", "Under Review", "Eligible", "Not Eligible"]
    if action not in valid_actions:
        return jsonify({"error": f"action must be one of {valid_actions}"}), 400

    application = Application.query.get(app_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    old_status = application.status
    application.status = action
    db.session.flush()

    # Log the override in the audit table
    log = AdminAction(
        admin_id=current_user.id,
        application_id=application.id,
        action=action,
        note=f"[Override from '{old_status}'] {note}"
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "message": f"Application #{app_id} status updated to '{action}'",
        "application": application.to_admin_dict()
    }), 200


@admin_bp.route("/api/admin/audit/<int:app_id>", methods=["GET"])
@admin_required
def get_audit_log(current_user, app_id):
    """Return full admin action history for a given application."""
    application = Application.query.get(app_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    actions = AdminAction.query \
        .filter_by(application_id=app_id) \
        .order_by(AdminAction.timestamp.desc()) \
        .all()

    return jsonify({
        "application_id": app_id,
        "actions": [a.to_dict() for a in actions]
    }), 200


@admin_bp.route("/api/analytics", methods=["GET"])
@token_required           # both admin and users can see analytics
def analytics(current_user):
    """Return aggregated analytics data."""
    data = get_analytics()
    return jsonify(data), 200
