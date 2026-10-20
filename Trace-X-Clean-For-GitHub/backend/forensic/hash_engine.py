import hashlib

def generate_sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def normalize_text(text):
    import re
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

def generate_content_hash(text):
    if not text:
        return None
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()
