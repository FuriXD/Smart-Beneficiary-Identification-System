"""
modules/analytics.py — Aggregated statistics for the dashboard charts
"""

from sqlalchemy import func
from models import db, Application, AdminAction, User


def get_analytics():
    """Return aggregated stats used by the analytics dashboard."""

    total = Application.query.count()
    eligible = Application.query.filter_by(status="Eligible").count()
    not_eligible = Application.query.filter_by(status="Not Eligible").count()
    under_review = Application.query.filter_by(status="Under Review").count()
    approved = Application.query.filter_by(status="Approved").count()
    rejected = Application.query.filter_by(status="Rejected").count()
    fraud_flagged = Application.query.filter_by(fraud_flag=True).count()
    total_users = User.query.filter_by(role="user").count()

    # Location distribution
    rural_count = Application.query.filter_by(location="rural").count()
    urban_count = Application.query.filter_by(location="urban").count()

    # Average score
    avg_score_row = db.session.query(func.avg(Application.score)).scalar()
    avg_score = round(avg_score_row or 0, 1)

    # Score distribution buckets
    score_buckets = {
        "0-20":  Application.query.filter(Application.score.between(0, 20)).count(),
        "21-40": Application.query.filter(Application.score.between(21, 40)).count(),
        "41-60": Application.query.filter(Application.score.between(41, 60)).count(),
        "61-80": Application.query.filter(Application.score.between(61, 80)).count(),
        "81-100":Application.query.filter(Application.score.between(81, 100)).count(),
    }

    # Daily applications (last 7 trend) — date + count
    from datetime import datetime, timedelta
    trend = []
    today = datetime.utcnow().date()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        cnt = Application.query.filter(
            func.date(Application.created_at) == day.isoformat()
        ).count()
        trend.append({"date": day.isoformat(), "count": cnt})

    fraud_percent = round((fraud_flagged / total * 100) if total > 0 else 0, 1)

    return {
        "total": total,
        "eligible": eligible,
        "not_eligible": not_eligible,
        "under_review": under_review,
        "approved": approved,
        "rejected": rejected,
        "fraud_flagged": fraud_flagged,
        "fraud_percent": fraud_percent,
        "total_users": total_users,
        "rural_count": rural_count,
        "urban_count": urban_count,
        "avg_score": avg_score,
        "score_buckets": score_buckets,
        "trend": trend,
        "insights": _build_insights(total, fraud_flagged, eligible, fraud_percent)
    }


def _build_insights(total, fraud, eligible, fraud_pct):
    """Generate human-readable insight strings."""
    insights = []
    if total == 0:
        return ["No applications yet — seed data or wait for submissions."]
    if fraud_pct > 20:
        insights.append(f"⚠️ High fraud rate: {fraud_pct}% of applications flagged for review.")
    elif fraud > 0:
        insights.append(f"🔍 {fraud_pct}% duplicate/suspicious attempts detected.")
    approval_rate = round(eligible / total * 100, 1) if total else 0
    insights.append(f"✅ {approval_rate}% of applicants qualify as eligible.")
    if total > 10:
        insights.append(f"📊 {total} total applications processed through the pipeline.")
    return insights
