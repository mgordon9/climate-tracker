from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_doc_id: Mapped[int] = mapped_column(ForeignKey("source_documents.id"))
    chunk_index: Mapped[int] = mapped_column()
    content: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(384), nullable=True)

    source_doc: Mapped["SourceDocument"] = relationship(back_populates="chunks")
