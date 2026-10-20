from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance
import imagehash

IMAGE_EXTENSIONS = {"jpg","jpeg","png","bmp","tif","tiff"}

def is_image(path):
    return Path(path).suffix.lower().lstrip(".") in IMAGE_EXTENSIONS

def perceptual_hash(path):
    return str(imagehash.phash(Image.open(path).convert("RGB")))

def hamming_similarity(hash_a, hash_b):
    if not hash_a or not hash_b:
        return None
    a, b = imagehash.hex_to_hash(hash_a), imagehash.hex_to_hash(hash_b)
    distance = a - b
    max_distance = len(a.hash.flatten())
    return round(max(0.0, 100.0 * (1 - distance / max_distance)), 2)

def ela_indicator(path):
    image = Image.open(path).convert("RGB")
    temp = image.copy()
    # Recompression in memory avoids creating a user-visible temp file.
    import io
    buf = io.BytesIO()
    temp.save(buf, "JPEG", quality=90)
    buf.seek(0)
    recompressed = Image.open(buf).convert("RGB")
    diff = ImageChops.difference(image, recompressed)
    extrema = diff.getextrema()
    mean = sum((lo + hi) / 2 for lo, hi in extrema) / 3
    score = mean
    if score >= 18:
        return "ELEVATED_RECOMPRESSION_DIFFERENCE", round(score, 2)
    if score >= 8:
        return "MODERATE_RECOMPRESSION_DIFFERENCE", round(score, 2)
    return "LOW_RECOMPRESSION_DIFFERENCE", round(score, 2)

def image_dimensions(path):
    with Image.open(path) as im:
        return {"width": im.width, "height": im.height, "mode": im.mode}
