from datetime import datetime, timezone
from backend.extensions import db

class Evidence(db.Model):
    __tablename__ = "evidence"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(100), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(80))
    file_size = db.Column(db.Integer)
    sha256_hash = db.Column(db.String(64), index=True)
    content_hash = db.Column(db.String(64), index=True)
    image_hash = db.Column(db.String(64), nullable=True)
    extracted_text = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    analyses = db.relationship("AnalysisResult", backref="evidence", cascade="all, delete-orphan")

class AnalysisResult(db.Model):
    __tablename__ = "analysis_results"
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey("evidence.id"), nullable=False)
    duplicate_found = db.Column(db.Boolean, default=False)
    duplicate_evidence_id = db.Column(db.Integer, nullable=True)
    content_match_found = db.Column(db.Boolean, default=False)
    content_match_evidence_id = db.Column(db.Integer, nullable=True)
    semantic_score = db.Column(db.Float, nullable=True)
    image_similarity = db.Column(db.Float, nullable=True)
    morphing_indicator = db.Column(db.String(80), default="NOT_ANALYZED")
    findings = db.Column(db.Text, nullable=True)
    analysis_status = db.Column(db.String(80), default="COMPLETED")
    analyzed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
