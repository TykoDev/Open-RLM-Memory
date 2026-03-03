import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings

from .base import Base

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


UUIDColumn = UUID(as_uuid=True).with_variant(String(36), "sqlite")
TagsColumn = ARRAY(String).with_variant(JSON, "sqlite")
MetadataColumn = JSONB().with_variant(JSON, "sqlite")


def id_default() -> str:
    return str(uuid.uuid4())


class Memory(Base):
    __tablename__ = "memory"

    id: Mapped[uuid.UUID | str] = mapped_column(UUIDColumn, primary_key=True, default=id_default)
    user_id: Mapped[uuid.UUID | str] = mapped_column(UUIDColumn, ForeignKey("users.id", ondelete="CASCADE"))
    tags: Mapped[List[str]] = mapped_column(TagsColumn, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", MetadataColumn, default=dict)

    content: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class MemoryEmbedding(Base):
    __tablename__ = "memory_embeddings"

    embedding_column = Vector(settings.EMBEDDING_DIMENSIONS).with_variant(JSON, "sqlite") if Vector else JSON

    id: Mapped[uuid.UUID | str] = mapped_column(UUIDColumn, primary_key=True, default=id_default)
    memory_id: Mapped[uuid.UUID | str] = mapped_column(UUIDColumn, ForeignKey("memory.id", ondelete="CASCADE"))
    embedding: Mapped[Any] = mapped_column(embedding_column)

    model: Mapped[str] = mapped_column(String(100), default=settings.EMBEDDING_MODEL)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
