from pathlib import Path
from uuid import uuid4
from flask import Blueprint, request, jsonify, session, send_file
from werkzeug.utils import secure_filename
from backend.extensions import db
from backend.models.activity import record_activity
from backend.models.evidence import Evidence
from backend.models.user import User
from backend.config import Config
from backend.forensic.hash_engine import generate_sha256, generate_content_hash
from backend.forensic.text_analyzer import extract_text
from backend.forensic.image_analyzer import is_image, perceptual_hash
from backend.forensic.analysis import analyze_evidence
from backend.reports.report_generator import generate_report

evidence_bp = Blueprint("evidence", __name__, url_prefix="/api/evidence")

def current_user():
    return session.get("user_id")

def allowed(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in Config.ALLOWED_EXTENSIONS

@evidence_bp.post("/upload")
def upload():
    if not current_user():
        return jsonify({"error":"Login required."}), 401
    file = request.files.get("file")
    case_id = request.form.get("case_id","").strip()
    description = request.form.get("description","").strip()
    if not file or not file.filename or not case_id:
        return jsonify({"error":"Case ID and file are required."}), 400
    if not allowed(file.filename):
        return jsonify({"error":"Unsupported file type."}), 400

    Config.EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    original = secure_filename(file.filename)
    ext = Path(original).suffix.lower()
    stored = f"{uuid4().hex}{ext}"
    path = Config.EVIDENCE_DIR / stored
    file.save(path)

    sha = generate_sha256(path)
    text = extract_text(path)
    content_hash = generate_content_hash(text)
    img_hash = perceptual_hash(path) if is_image(path) else None

    evidence = Evidence(
        case_id=case_id,
        original_filename=original,
        stored_filename=stored,
        file_type=ext.lstrip("."),
        file_size=path.stat().st_size,
        sha256_hash=sha,
        content_hash=content_hash,
        image_hash=img_hash,
        extracted_text=text[:100000] if text else None,
        description=description,
        uploaded_by=current_user()
    )
    db.session.add(evidence)
    db.session.commit()

    user = db.session.get(User, current_user())
    record_activity(current_user(), user.username if user else "unknown", "evidence_uploaded",
                    f"Uploaded {original} for case {case_id}.", "evidence", evidence.id)
    db.session.commit()

    result = analyze_evidence(evidence)
    record_activity(current_user(), user.username if user else "unknown", "evidence_analyzed",
                    f"Analysis completed for {original}.", "evidence", evidence.id)
    db.session.commit()
    return jsonify(serialize_evidence(evidence, result)), 201

@evidence_bp.get("")
def list_evidence():
    if not current_user():
        return jsonify({"error":"Login required."}), 401
    items = Evidence.query.order_by(Evidence.id.desc()).all()
    return jsonify([serialize_evidence(e, e.analyses[-1] if e.analyses else None) for e in items])

@evidence_bp.get("/<int:evidence_id>")
def get_evidence(evidence_id):
    if not current_user():
        return jsonify({"error":"Login required."}), 401
    e = db.session.get(Evidence, evidence_id)
    if not e:
        return jsonify({"error":"Evidence not found."}), 404
    user = db.session.get(User, current_user())
    record_activity(current_user(), user.username if user else "unknown", "evidence_viewed",
                    f"Viewed {e.original_filename}.", "evidence", e.id)
    db.session.commit()
    return jsonify(serialize_evidence(e, e.analyses[-1] if e.analyses else None))

@evidence_bp.get("/<int:evidence_id>/download")
def download(evidence_id):
    if not current_user():
        return jsonify({"error":"Login required."}), 401
    e = db.session.get(Evidence, evidence_id)
    if not e:
        return jsonify({"error":"Evidence not found."}), 404
    user = db.session.get(User, current_user())
    record_activity(current_user(), user.username if user else "unknown", "evidence_downloaded",
                    f"Downloaded {e.original_filename}.", "evidence", e.id)
    db.session.commit()
    return send_file(Config.EVIDENCE_DIR / e.stored_filename, as_attachment=True, download_name=e.original_filename)

@evidence_bp.get("/<int:evidence_id>/report")
def report(evidence_id):
    if not current_user():
        return jsonify({"error":"Login required."}), 401
    e = db.session.get(Evidence, evidence_id)
    if not e or not e.analyses:
        return jsonify({"error":"Analysis not found."}), 404
    path = generate_report(e, e.analyses[-1])
    user = db.session.get(User, current_user())
    record_activity(current_user(), user.username if user else "unknown", "report_downloaded",
                    f"Generated and downloaded the report for {e.original_filename}.", "evidence", e.id)
    db.session.commit()
    return send_file(path, as_attachment=True, download_name=f"TRACE-X_Report_{e.id}.pdf")

def serialize_evidence(e, a):
    return {
        "id": e.id, "case_id": e.case_id, "filename": e.original_filename,
        "file_type": e.file_type, "file_size": e.file_size,
        "sha256": e.sha256_hash, "content_hash": e.content_hash,
        "image_hash": e.image_hash, "uploaded_at": e.uploaded_at.isoformat() if e.uploaded_at else None,
        "description": e.description,
        "analysis": None if not a else {
            "duplicate_found": a.duplicate_found,
            "duplicate_evidence_id": a.duplicate_evidence_id,
            "content_match_found": a.content_match_found,
            "content_match_evidence_id": a.content_match_evidence_id,
            "semantic_score": a.semantic_score,
            "image_similarity": a.image_similarity,
            "morphing_indicator": a.morphing_indicator,
            "findings": __import__("json").loads(a.findings or "[]"),
            "status": a.analysis_status
        }
    }
