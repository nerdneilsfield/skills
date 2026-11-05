from pathlib import Path

UPLOAD_DIR = Path("/var/app/uploads")


def save(filename: str) -> Path:
    return UPLOAD_DIR / filename
