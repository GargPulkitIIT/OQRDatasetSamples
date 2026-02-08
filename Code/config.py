import os

class Config:
    SECRET_KEY = "oqr-secret-key"
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB (changeable)
    ALLOWED_EXTENSIONS = {
        "png", "jpg", "jpeg", "gif",
        "mp4", "mov", "avi", "mkv"
    }
