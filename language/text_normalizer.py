import unicodedata


def normalize_text(text):
    """Normalize a detection-only copy; never rewrite executable input."""
    if not isinstance(text, str):
        raise TypeError('Text must be a string.')
    return unicodedata.normalize('NFC', text).strip()
