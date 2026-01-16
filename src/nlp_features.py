from __future__ import annotations

import re
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer


def _clean_text_for_nlp(text: str) -> str:
    # Remove weird hyphenation from PDF line breaks: "educa- tional" -> "educational"
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_keywords_tfidf(text: str, top_k: int = 10) -> List[str]:
    """
    Cleaner, more 'concept-like' keywords.
    - TF-IDF on bigrams only (concept phrases)
    - Drop meta/noise tokens (abstract, paper, results...)
    - Drop verb-like bigrams (-ing / -ed) to reduce "allows identify"
    - Drop common weak phrases + near-duplicates
    """
    text = _clean_text_for_nlp(text)
    if len(text) < 200:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(2, 2),  # ONLY bigrams
        max_features=6000,
        min_df=1,
    )

    X = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = X.toarray()[0]

    ranked = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)

    bad_tokens = {
        "abstract", "analysis", "results", "result", "paper", "study",
        "method", "methods", "approach", "dataset",
        "introduction", "conclusion", "keywords", "index", "terms"
    }

    blacklist_phrases = {
        "in order", "on the", "such as", "based on",
        "this study", "this paper", "paper presents", "results show",
        "growing demand", "different faculties", "educational systems",
        "data collection", "data processing",
    }

    def is_verb_like_bigram(kw: str) -> bool:
        # Filter out action/noise phrases (simple heuristic)
        return any(t.endswith(("ing", "ed")) for t in kw.split())

    keywords: List[str] = []

    for kw, score in ranked:
        if len(keywords) >= top_k:
            break

        kw = kw.lower().strip()

        if len(kw) < 10:
            continue
        if re.search(r"\d", kw):
            continue
        if kw in blacklist_phrases:
            continue

        tokens = kw.split()

        # remove meta-like tokens
        if any(t in bad_tokens for t in tokens):
            continue

        # remove verb-like phrases
        if is_verb_like_bigram(kw):
            continue

        # avoid near-duplicates
        if any(kw in k or k in kw for k in keywords):
            continue

        keywords.append(kw)

    return keywords


def summarize_textrank(text: str, sentences_count: int = 4) -> str:
    """
    Extractive summary using TextRank (Sumy).
    Strategy:
      1) If an ABSTRACT section exists, summarize that.
      2) Otherwise, summarize the first ~4000 characters.
    """
    text = _clean_text_for_nlp(text)
    if len(text) < 200:
        return text

    lower = text.lower()

    abstract = ""
    if "abstract" in lower:
        start = lower.find("abstract")
        chunk = text[start:start + 5000]
        stop_markers = ["introduction", "1 introduction", "keywords", "index terms", "contents"]
        stop_pos = len(chunk)
        chunk_lower = chunk.lower()
        for m in stop_markers:
            pos = chunk_lower.find(m)
            if pos != -1 and pos > 50:
                stop_pos = min(stop_pos, pos)
        abstract = chunk[:stop_pos].strip()

    target = abstract if len(abstract) >= 200 else text[:4000]

    # Remove leading "Abstract" if present
    target = re.sub(r"^abstract\s+", "", target, flags=re.IGNORECASE)

    parser = PlaintextParser.from_string(target, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    summary_sentences = summarizer(parser.document, sentences_count)

    summary = " ".join(str(s) for s in summary_sentences).strip()
    return summary
