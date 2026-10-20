from datetime import datetime, timezone
from backend.extensions import db


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(80), nullable=False, index=True)
    details = db.Column(db.Text, nullable=True)
    target_type = db.Column(db.String(40), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)


def record_activity(user_id, username, action, details=None, target_type=None, target_id=None):
    db.session.add(ActivityLog(
        user_id=user_id,
        username=username,
        action=action,
        details=details,
        target_type=target_type,
        target_id=target_id
    ))
