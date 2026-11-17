"""Retrieve context, build the prompt, call the LLM, return answer + sources."""
import ollama

from config import LLM_MODEL, TEMPERATURE, TOP_K
from vectorstore import search

SYSTEM_PROMPT = """Kamu adalah asisten analisis kerja lapangan untuk koordinator operasional.
Aturan:
1. Jawab HANYA berdasarkan KONTEKS yang diberikan.
2. Jika konteks tidak cukup, jawab persis: "Data tidak cukup untuk menjawab."
3. Selalu sebutkan ticket_id yang kamu pakai, misalnya (TKT-0012).
4. Jawab dalam Bahasa Indonesia, singkat dan jelas.
5. Jangan mengarang data."""


def build_prompt(question: str, hits: list[dict]) -> str:
    """Combine the retrieved chunks and the question into one user prompt."""
    context = "\n\n".join(
        f"[{h['metadata'].get('ticket_id', '-')}] {h['text']}" for h in hits
    )
    return f"KONTEKS:\n{context}\n\nPERTANYAAN:\n{question}"


def answer(question: str) -> tuple[str, list[dict]]:
    """Return (answer_text, sources). Sources come from the retrieved chunks."""
    try:
        hits = search(question, TOP_K)
    except Exception:
        return "Index belum dibuat. Klik 'Build index' dulu.", []

    if not hits:
        return "Data tidak cukup untuk menjawab.", []

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(question, hits)},
        ],
        options={"temperature": TEMPERATURE},
    )
    text = response["message"]["content"]

    sources = [
        {
            "ticket_id": h["metadata"].get("ticket_id", ""),
            "tanggal": h["metadata"].get("tanggal", ""),
            "wilayah": h["metadata"].get("wilayah", ""),
            "isi": h["text"],
        }
        for h in hits
    ]
    return text, sources