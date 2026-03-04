"""RAG service: embed question → vector search → call Claude."""
from functools import lru_cache

import anthropic
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.config import settings
from app.models.climate_data import ClimateData
from app.models.document_chunk import DocumentChunk
from app.models.source_document import SourceDocument


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


def answer_question(db: Session, country_id: int, question: str) -> dict:
    model = _get_model()
    q_vec = model.encode([question])[0].tolist()

    # --- Vector search: climate data rows for this country ---
    climate_rows = (
        db.query(ClimateData)
        .filter(ClimateData.country_id == country_id)
        .filter(ClimateData.embedding.is_not(None))
        .order_by(ClimateData.embedding.cosine_distance(q_vec))
        .limit(5)
        .all()
    )

    # --- Vector search: document chunks (country-specific or global) ---
    chunk_rows = (
        db.query(DocumentChunk, SourceDocument)
        .join(SourceDocument, DocumentChunk.source_doc_id == SourceDocument.id)
        .filter(
            (SourceDocument.country_id == country_id) | (SourceDocument.country_id.is_(None))
        )
        .filter(DocumentChunk.embedding.is_not(None))
        .order_by(DocumentChunk.embedding.cosine_distance(q_vec))
        .limit(5)
        .all()
    )

    # --- Build context ---
    context_parts: list[str] = []

    if climate_rows:
        context_parts.append("## Climate Data Records")
        for row in climate_rows:
            context_parts.append(
                f"- {row.metric_type}: {row.value} {row.unit} on {row.date} "
                f"(source: {row.source or 'unknown'})"
            )

    if chunk_rows:
        context_parts.append("\n## Reference Documents")
        for chunk, src_doc in chunk_rows:
            context_parts.append(f"**{src_doc.title}**\n{chunk.content}")

    context = "\n".join(context_parts) if context_parts else "No relevant data found."

    # --- Sources list ---
    sources: list[dict] = []
    seen_titles: set[str] = set()
    for chunk, src_doc in chunk_rows:
        if src_doc.title not in seen_titles:
            seen_titles.add(src_doc.title)
            sources.append({"title": src_doc.title, "excerpt": chunk.content[:200]})

    # --- Call Claude ---
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    system_prompt = (
        "You are a climate science assistant. Answer the user's question about a specific "
        "country using only the climate data and reference documents provided in the context. "
        "Be concise (2–4 sentences). When referencing a document, cite it by title. "
        "If the context does not contain enough information, say so briefly."
    )
    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    answer = response.content[0].text

    return {"answer": answer, "sources": sources}
