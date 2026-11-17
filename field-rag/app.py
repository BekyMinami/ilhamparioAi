"""Streamlit UI only. All logic lives in the other modules."""
import tempfile
from pathlib import Path

import streamlit as st

import rag
from chunker import make_chunks
from loader import load_tickets
from preprocess import preprocess
from vectorstore import build_index

st.set_page_config(page_title="Analisis Kerja Lapangan", layout="wide")
st.title("Analisis Kerja Lapangan (RAG)")
st.caption("Sistem penunjang keputusan. Keputusan akhir tetap di tangan manusia.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Upload + build index ---
uploaded = st.file_uploader("Unggah data tiket", type=["xlsx", "csv"])

if st.button("Build index"):
    if uploaded is None:
        st.error("Unggah file terlebih dahulu.")
    else:
        with st.spinner("Membangun index..."):
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(uploaded.name).suffix
            ) as tmp:
                tmp.write(uploaded.getvalue())
            df = preprocess(load_tickets(tmp.name))
            Path(tmp.name).unlink()
            chunks = make_chunks(df)
            build_index(chunks)
        st.success(f"Index selesai dibuat: {len(chunks)} chunk.")

st.divider()

# --- Chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("Sumber data"):
                st.write(msg["sources"])

# --- Chat input ---
question = st.chat_input("Tanyakan sesuatu tentang data kerja lapangan...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Menganalisis..."):
            answer, sources = rag.answer(question)
        st.write(answer)
        with st.expander("Sumber data"):
            st.write(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )