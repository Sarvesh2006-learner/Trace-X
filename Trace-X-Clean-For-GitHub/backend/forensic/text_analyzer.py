from pathlib import Path
from backend.forensic.hash_engine import normalize_text

TEXT_EXTENSIONS = {"txt","csv","json","xml","log"}

def extract_text(path):
    ext = Path(path).suffix.lower().lstrip(".")
    if ext in TEXT_EXTENSIONS:
        try:
            return Path(path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""
    if ext == "pdf":
        import fitz
        doc = fitz.open(path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text
    if ext == "docx":
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

def text_statistics(text):
    words = normalize_text(text).split()
    return {
        "characters": len(text or ""),
        "words": len(words),
        "lines": len((text or "").splitlines())
    }
