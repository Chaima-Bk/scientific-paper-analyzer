import sys
from pathlib import Path
import tempfile
import json

import streamlit as st

# Add project root to PYTHONPATH so we can import from "src"
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.pdf_extraction import extract_text_from_pdf
from src.section_parser import split_into_sections
from src.nlp_features import extract_keywords_tfidf, summarize_textrank
from src.metadata_extractor import extract_metadata
from src.report_builder import save_report


st.set_page_config(page_title="Scientific Paper Analyzer", layout="wide")

st.title("📄 Scientific Paper Analyzer (MVP)")
st.write(
    "Upload a scientific PDF or try a sample paper, then extract its text, detect sections, and show NLP insights."
)

sample_dir = Path("data/sample_papers")

# --- Sample selection
st.subheader("1) Try a sample paper")
samples = sorted([p.name for p in sample_dir.glob("*.pdf")]) if sample_dir.exists() else []
sample_choice = st.selectbox("Select a sample PDF", ["(none)"] + samples)

st.divider()

# --- Upload
st.subheader("2) Upload your PDF")
uploaded = st.file_uploader("Upload a PDF file", type=["pdf"])

st.divider()

# --- Action
st.subheader("3) Analyze")
col1, col2 = st.columns([1, 2])

with col1:
    extract_btn = st.button("Extract & Analyze", type="primary")

with col2:
    st.caption("Tip: Start with a sample PDF to ensure everything works.")

# --- Result
if extract_btn:
    try:
        # Choose the PDF source
        if uploaded is not None:
            # Save uploaded file to a temporary path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.getbuffer())
                pdf_path = tmp.name
            source_label = f"Uploaded: {uploaded.name}"

        elif sample_choice != "(none)":
            pdf_path = sample_dir / sample_choice
            source_label = f"Sample: {sample_choice}"

        else:
            st.warning("Please select a sample PDF or upload a PDF first.")
            st.stop()

        # Extract text
        text = extract_text_from_pdf(pdf_path)

        if not text.strip():
            st.error("No text extracted. This PDF may be scanned or protected.")
            st.stop()

        st.success(f"Text extracted successfully ✅ ({len(text):,} characters) — {source_label}")

        # --- Metadata
        meta = extract_metadata(text)

        st.subheader("Metadata (heuristics)")
        colm1, colm2, colm3 = st.columns([2, 1, 2])

        with colm1:
            st.markdown("**Title (guessed)**")
            st.write(meta.get("title") or "Not detected")

        with colm2:
            st.markdown("**Year**")
            st.write(meta.get("year") or "—")

        with colm3:
            st.markdown("**Emails found**")
            emails = meta.get("emails") or []
            st.write(", ".join(emails) if emails else "—")

        st.download_button(
            label="Download metadata (.json)",
            data=json.dumps(meta, indent=2, ensure_ascii=False),
            file_name="metadata.json",
            mime="application/json",
        )

        # --- Sections
        sections = split_into_sections(text)

        st.subheader("Detected sections")
        if sections:
            st.write("Sections found:", ", ".join(sections.keys()))
            tabs = st.tabs([name.upper() for name in sections.keys()])
            for tab, (name, content) in zip(tabs, sections.items()):
                with tab:
                    st.text_area(f"{name.upper()} content", content[:20000], height=350)
        else:
            st.warning("No standard sections detected. Showing full text preview.")
            st.text_area("Extracted text (preview)", text[:15000], height=350)

        # --- NLP Insights
        st.divider()
        st.subheader("Paper insights (NLP)")

        text_for_summary = sections.get("abstract", text) if sections else text

        keywords = extract_keywords_tfidf(text_for_summary, top_k=12)
        summary = summarize_textrank(text_for_summary, sentences_count=4)

        colA, colB = st.columns([1, 2])

        with colA:
            st.markdown("**Top keywords**")
            st.write(", ".join(keywords) if keywords else "No keywords extracted.")

        with colB:
            st.markdown("**Auto summary**")
            st.text_area("Summary (preview)", summary, height=200)

        # --- Build & save report (JSON)
        report = {
            "source": source_label,
            "stats": {
                "text_length_chars": len(text),
                "num_sections_detected": len(sections) if sections else 0,
                "num_keywords": len(keywords) if keywords else 0,
            },
            "metadata": meta,
            "keywords": keywords,
            "summary": summary,
            "sections": sections,
        }

        report_path = save_report(report, output_dir="outputs/json")

        st.success(f"Report saved ✅ {report_path.as_posix()}")
        st.download_button(
            label="Download full report (.json)",
            data=json.dumps(report, indent=2, ensure_ascii=False),
            file_name="paper_report.json",
            mime="application/json",
        )

        # --- Downloads
        st.download_button(
            label="Download extracted text (.txt)",
            data=text,
            file_name="extracted_text.txt",
            mime="text/plain",
        )

    except Exception as e:
        st.error(f"Extraction failed: {e}")
