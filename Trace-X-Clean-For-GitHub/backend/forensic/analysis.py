import json
from backend.extensions import db
from backend.models.evidence import Evidence, AnalysisResult
from backend.forensic.hash_engine import generate_sha256, generate_content_hash
from backend.forensic.text_analyzer import extract_text
from backend.forensic.image_analyzer import is_image, perceptual_hash, ela_indicator
from backend.forensic.duplicate_detector import find_exact_duplicate, find_content_duplicate, find_similar_images
from backend.forensic.similarity_engine import semantic_similarity

def analyze_evidence(evidence):
    exact = find_exact_duplicate(evidence.sha256_hash, evidence.id)
    content = find_content_duplicate(evidence.content_hash, evidence.id)

    image_matches = []
    morphing = "NOT_ANALYZED"
    if evidence.image_hash:
        image_matches = find_similar_images(evidence.image_hash, evidence.id)
        try:
            morphing, ela_score = ela_indicator(evidence_path(evidence))
        except Exception:
            ela_score = None
    else:
        ela_score = None

    semantic = None
    if evidence.extracted_text and content is None:
        candidates = Evidence.query.filter(Evidence.extracted_text.isnot(None), Evidence.id != evidence.id).limit(100).all()
        best = None
        best_item = None
        for item in candidates:
            score = semantic_similarity(evidence.extracted_text, item.extracted_text)
            if score is not None and (best is None or score > best):
                best, best_item = score, item
        if best is not None and best >= 75:
            semantic = best

    findings = []
    if exact:
        findings.append(f"EXACT DUPLICATE: evidence #{exact.id} has the same SHA-256.")
    if content:
        findings.append(f"IDENTICAL NORMALIZED CONTENT: evidence #{content.id}.")
    if semantic is not None:
        findings.append(f"SEMANTIC SIMILARITY: {semantic}% with the closest indexed text.")
    if image_matches:
        findings.append(f"IMAGE SIMILARITY: {image_matches[0][1]}% with evidence #{image_matches[0][0].id}.")
    if morphing != "NOT_ANALYZED":
        findings.append(f"IMAGE RECOMPRESSION INDICATOR: {morphing}. This is an investigative indicator, not proof of manipulation.")
    if not findings:
        findings.append("No indexed duplicate or high-similarity match was found.")

    result = AnalysisResult(
        evidence_id=evidence.id,
        duplicate_found=bool(exact),
        duplicate_evidence_id=exact.id if exact else None,
        content_match_found=bool(content),
        content_match_evidence_id=content.id if content else None,
        semantic_score=semantic,
        image_similarity=image_matches[0][1] if image_matches else None,
        morphing_indicator=morphing,
        findings=json.dumps(findings),
        analysis_status="COMPLETED"
    )
    db.session.add(result)
    db.session.commit()
    return result

def evidence_path(evidence):
    from pathlib import Path
    from backend.config import Config
    return str(Config.EVIDENCE_DIR / evidence.stored_filename)
