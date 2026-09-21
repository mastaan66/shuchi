"""
SHUCHI Intake — True-type checking and file validation
"""

import magic
import os

SUPPORTED_MIME = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/jpeg",
    "image/png",
}

EXT_MAP = {
    "application/pdf": ["pdf"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ["docx"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ["xlsx"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [
        "pptx"
    ],
    "image/jpeg": ["jpg", "jpeg"],
    "image/png": ["png"],
}


def check_true_type(filepath):
    try:
        ms = magic.Magic(mime=True)
        mime = ms.from_file(filepath)
        return mime
    except Exception:
        return "unknown"


def is_supported(mime_type):
    return mime_type in SUPPORTED_MIME


def verify_extension(filepath, mime_type):
    ext = os.path.splitext(filepath)[1].lower().lstrip(".")
    allowed = EXT_MAP.get(mime_type, [])
    return ext in allowed if allowed else False


def polyglot_check(filepath):
    mime = check_true_type(filepath)
    ext = os.path.splitext(filepath)[1].lower().lstrip(".")
    allowed = EXT_MAP.get(mime, [])
    if allowed and ext not in allowed:
        return True
    return False
