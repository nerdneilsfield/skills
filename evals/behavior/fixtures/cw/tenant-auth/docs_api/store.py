"""In-memory document store with two tenants worth of sample documents."""
DOCUMENTS = {
    "d-100": {"id": "d-100", "tenant": "tenant-a", "body": "alpha quarterly plan"},
    "d-200": {"id": "d-200", "tenant": "tenant-b", "body": "beta secret roadmap"},
}


def get(document_id: str):
    return DOCUMENTS.get(document_id)
