from flask import Blueprint, jsonify, request, session
from backend.extensions import db
from backend.models.activity import ActivityLog
from backend.models.auth_event import AuthEvent
from backend.models.user import User

# 1. Define the blueprint FIRST so it's available for decorators
admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def require_admin():
    user_id = session.get("user_id")
    if not user_id:
        return None, (jsonify({"error": "Login required."}), 401)

    user = db.session.get(User, user_id)
    if not user or user.role != "admin":
        return None, (jsonify({"error": "Admin access required."}), 403)
    return user, None


@admin_bp.get("/activity")
def activity():
    _, error = require_admin()
    if error:
        return error

    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)
    if limit < 1 or limit > 100 or offset < 0:
        return jsonify(
            {
                "error": (
                    "Limit must be between 1 and 100 and offset must be"
                    " non-negative."
                )
            }
        ), 400

    query = ActivityLog.query.order_by(
        ActivityLog.created_at.desc(), ActivityLog.id.desc()
    )
    total = query.count()
    events = query.offset(offset).limit(limit).all()

    return jsonify(
        {
            "total": total,
            "activities": [
                {
                    "id": event.id,
                    "username": event.username,
                    "action": event.action,
                    "details": event.details,
                    "created_at": (
                        event.created_at.isoformat()
                        if event.created_at
                        else None
                    ),
                }
                for event in events
            ],
        }
    )


@admin_bp.get("/auth-events")
def auth_events():
    _, error = require_admin()
    if error:
        return error

    limit = request.args.get("limit", 200, type=int)
    limit = max(1, min(limit, 500))

    events = (
        AuthEvent.query.order_by(
            AuthEvent.event_time.desc(), AuthEvent.id.desc()
        )
        .limit(limit)
        .all()
    )

    return jsonify([event.to_dict() for event in events])