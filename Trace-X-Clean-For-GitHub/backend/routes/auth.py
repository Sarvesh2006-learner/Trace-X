
from flask import Blueprint, request, jsonify, session
from backend.extensions import db
from backend.models.activity import record_activity
from backend.models.user import User
from backend.models.auth_event import AuthEvent

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def record_auth_event(user, username, event_type):
    """Record a login or logout without storing credentials."""

    event = AuthEvent(
        user_id=user.id if user else None,
        username=username,
        event_type=event_type,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent", "")[:300]
    )

    db.session.add(event)
    record_activity(
        user.id if user else None,
        username,
        event_type.lower(),
        f"{event_type.replace('_', ' ').capitalize()} authentication event."
    )
    db.session.commit()


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or len(password) < 6:
        return jsonify({
            "error": (
                "Username, email and a password "
                "of at least 6 characters are required."
            )
        }), 400

    existing = User.query.filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if existing:
        return jsonify({
            "error": "Username or email already exists."
        }), 409

    user = User(
        username=username,
        email=email,
        role="investigator"
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful."
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        # Record failed attempts without recording passwords.
        record_auth_event(None, username or "unknown", "LOGIN_FAILED")

        return jsonify({
            "error": "Invalid username or password."
        }), 401

    session.clear()
    session["user_id"] = user.id

    record_auth_event(user, user.username, "LOGIN")

    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role
    })


@auth_bp.post("/logout")
def logout():
    user_id = session.get("user_id")

    if user_id is not None:
        user = db.session.get(User, user_id)

        if user:
            record_auth_event(
                user,
                user.username,
                "LOGOUT"
            )

    session.clear()

    return jsonify({
        "message": "Logged out."
    })


@auth_bp.get("/me")
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"authenticated": False})

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return jsonify({"authenticated": False})

    return jsonify({
        "authenticated": True,
        "id": user.id,
        "username": user.username,
        "role": user.role
    })
