
from datetime import datetime, timezone
from backend.extensions import db


class AuthEvent(db.Model):
    __tablename__ = "auth_events"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    username = db.Column(
        db.String(80),
        nullable=False
    )

    event_type = db.Column(
        db.String(30),
        nullable=False,
        index=True
    )

    event_time = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(300))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "event_type": self.event_type,
            "event_time": (
                self.event_time.isoformat()
                if self.event_time else None
            ),
            "ip_address": self.ip_address
        }
