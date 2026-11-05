"""Established authorization helpers. Reuse these; do not add a framework."""
from fastapi import HTTPException


def current_tenant(request) -> str:
    """Tenant ID placed in request.state by the authentication middleware."""
    tenant = getattr(request.state, "tenant_id", None)
    if not tenant:
        raise HTTPException(status_code=401, detail="unauthenticated")
    return tenant


def require_tenant(document_tenant: str, request) -> None:
    if document_tenant != current_tenant(request):
        raise HTTPException(status_code=404, detail="not found")
