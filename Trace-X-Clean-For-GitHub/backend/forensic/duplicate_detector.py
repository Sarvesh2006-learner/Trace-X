from backend.extensions import db
from backend.models.evidence import Evidence

def find_exact_duplicate(sha256, exclude_id=None):
    q = Evidence.query.filter_by(sha256_hash=sha256)
    if exclude_id:
        q = q.filter(Evidence.id != exclude_id)
    return q.first()

def find_content_duplicate(content_hash, exclude_id=None):
    if not content_hash:
        return None
    q = Evidence.query.filter_by(content_hash=content_hash)
    if exclude_id:
        q = q.filter(Evidence.id != exclude_id)
    return q.first()

def find_similar_images(image_hash, exclude_id=None, threshold=80):
    if not image_hash:
        return []
    from backend.forensic.image_analyzer import hamming_similarity
    q = Evidence.query.filter(Evidence.image_hash.isnot(None))
    if exclude_id:
        q = q.filter(Evidence.id != exclude_id)
    matches = []
    for item in q.all():
        score = hamming_similarity(image_hash, item.image_hash)
        if score is not None and score >= threshold:
            matches.append((item, score))
    return sorted(matches, key=lambda x: x[1], reverse=True)
