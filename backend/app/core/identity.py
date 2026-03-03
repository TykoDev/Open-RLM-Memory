from fastapi import Depends, Header, HTTPException

from app.services.user_service import normalize_namespace


async def get_memory_namespace(
    x_memory_namespace: str | None = Header(default=None, alias="X-Memory-Namespace"),
) -> str:
    try:
        return normalize_namespace(x_memory_namespace)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


MemoryNamespaceDep = Depends(get_memory_namespace)
