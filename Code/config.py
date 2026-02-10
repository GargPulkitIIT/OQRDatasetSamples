import os

class Config:
    SECRET_KEY = "oqr-secret-key"
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB (changeable)
    
    # Image formats for encoder output
    OUTPUT_FORMATS = {
        "png": "PNG (Portable Network Graphics)",
        "jpg": "JPG (Joint Photographic Experts Group)",
        "jpeg": "JPEG (Joint Photographic Experts Group)",
        "bmp": "BMP (Bitmap)",
        "tiff": "TIFF (Tagged Image File Format)",
        "tif": "TIF (Tagged Image File Format)",
        "webp": "WEBP (WebP Image Format)"
    }
    
    # File formats allowed for decoder input
    ALLOWED_EXTENSIONS = {
        "png", "jpg", "jpeg", "gif", "bmp", "tiff", "tif", "webp",
        "mp4", "mov", "avi", "mkv"
    }
