import urllib.request

UPLOAD_URL = "https://example.invalid/upload"


def upload(path: str) -> None:
    with open(path, "rb") as fh:
        data = fh.read()
    req = urllib.request.Request(UPLOAD_URL, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status != 200:
            raise RuntimeError(f"upload failed: {resp.status}")
