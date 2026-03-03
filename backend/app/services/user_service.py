import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User

_NAMESPACE_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")


def normalize_namespace(value: str | None) -> str:
    namespace = (value or "").strip()
    if not namespace:
        namespace = settings.DEFAULT_MEMORY_NAMESPACE

    if len(namespace) > settings.MAX_NAMESPACE_LENGTH:
        raise ValueError(f"namespace exceeds {settings.MAX_NAMESPACE_LENGTH} characters")

    if not _NAMESPACE_PATTERN.fullmatch(namespace):
        raise ValueError("namespace may contain only letters, numbers, dot, underscore, and hyphen")

    return namespace.lower()


async def get_or_create_user_by_namespace(db: AsyncSession, namespace: str) -> User:
    normalized = normalize_namespace(namespace)

    result = await db.execute(select(User).where(User.namespace == normalized))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(namespace=normalized, display_name=normalized)
    db.add(user)
    await db.flush()
    return user
