def semantic_similarity(text1, text2):
    if not text1 or not text2:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        from sentence_transformers.util import cos_sim
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        embeddings = model.encode([text1[:12000], text2[:12000]], convert_to_tensor=True)
        return round(float(cos_sim(embeddings[0], embeddings[1]).item() * 100), 2)
    except Exception:
        return None
