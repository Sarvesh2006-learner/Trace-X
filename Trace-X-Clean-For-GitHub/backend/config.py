from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.environ.get("TRACEX_SECRET_KEY", "change-this-secret-key")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(BASE_DIR / "database" / "tracex.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024
    EVIDENCE_DIR = BASE_DIR / "storage" / "evidence"
    REPORT_DIR = BASE_DIR / "storage" / "reports"
    ALLOWED_EXTENSIONS = {
        "txt","pdf","docx","jpg","jpeg","png","bmp","tif","tiff",
        "mp4","avi","mov","mkv","wav","mp3","csv","json","xml","log"
    }
