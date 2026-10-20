from pathlib import Path
from flask import Flask, send_from_directory
from backend.config import Config
from backend.extensions import db, cors
from backend.models.user import User
from backend.routes.auth import auth_bp
from backend.routes.evidence import evidence_bp
from backend.routes.admin import admin_bp

def create_app():
    app = Flask(__name__, static_folder="../frontend/static", static_url_path="/static")
    app.config.from_object(Config)
    db.init_app(app)
    cors.init_app(app, supports_credentials=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(admin_bp)

    @app.get("/")
    def index():
        return send_from_directory("../frontend", "index.html")

    @app.get("/<path:path>")
    def frontend(path):
        p = Path(app.root_path).parent / "frontend" / path
        if p.exists() and p.is_file():
            return send_from_directory(str(p.parent), p.name)
        return send_from_directory(str(Path(app.root_path).parent / "frontend"), "index.html")

    with app.app_context():
        Path(Config.EVIDENCE_DIR).mkdir(parents=True, exist_ok=True)
        Path(Config.REPORT_DIR).mkdir(parents=True, exist_ok=True)
        Path(Path(Config.SQLALCHEMY_DATABASE_URI.replace("sqlite:///",""))).parent.mkdir(parents=True, exist_ok=True)
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@tracex.local", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
