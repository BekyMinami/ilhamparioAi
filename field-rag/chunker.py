"""Turn each ticket row into text chunk(s) plus metadata."""
import pandas as pd

from config import CHUNK_OVERLAP, CHUNK_SIZE


def _split(text: str) -> list[str]:
    """Split long text into pieces of CHUNK_SIZE with CHUNK_OVERLAP."""
    if len(text) <= CHUNK_SIZE:
        return [text]
    step = CHUNK_SIZE - CHUNK_OVERLAP
    pieces = []
    for start in range(0, len(text), step):
        pieces.append(text[start:start + CHUNK_SIZE])
        if start + CHUNK_SIZE >= len(text):
            break
    return pieces


def make_chunks(df: pd.DataFrame) -> list[dict]:
    """Return a list of {"text": str, "metadata": dict}."""
    chunks = []
    for _, row in df.iterrows():
        durasi = "belum ada" if pd.isna(row["durasi_jam"]) else f"{row['durasi_jam']} jam"
        header = (
            f"Tiket {row['ticket_id']} | {row['tanggal']} | {row['wilayah']} | "
            f"{row['jenis_gangguan']} | Teknisi: {row['teknisi']} | "
            f"Status: {row['status']} | Durasi: {durasi}"
        )
        metadata = {
            "ticket_id": row["ticket_id"],
            "tanggal": row["tanggal"],
            "wilayah": row["wilayah"],
            "jenis": row["jenis_gangguan"],
            "teknisi": row["teknisi"],
            "status": row["status"],
        }
        for piece in _split(row["catatan_teknisi"]):
            chunks.append({"text": f"{header}\nCatatan: {piece}", "metadata": metadata})
    return chunks