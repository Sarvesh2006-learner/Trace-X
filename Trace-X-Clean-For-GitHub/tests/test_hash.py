from backend.forensic.hash_engine import normalize_text, generate_content_hash

def test_normalization():
    assert normalize_text("Hello,   WORLD!") == "hello world"

def test_content_hash_same_for_spacing():
    assert generate_content_hash("Hello World") == generate_content_hash("hello   world!")
