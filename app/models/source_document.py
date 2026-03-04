from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str] = mapped_column(String(100))  # "ipcc_ar6", "ndc", "news"
    title: Mapped[str] = mapped_column(String(500))
    full_content: Mapped[str] = mapped_column(Text)
    country_id: Mapped[int | None] = mapped_column(ForeignKey("countries.id"), nullable=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="source_doc")

    __table_args__ = (Index("ix_source_docs_source_type", "source_type"),)
