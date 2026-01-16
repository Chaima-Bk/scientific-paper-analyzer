from __future__ import annotations

import re
from typing import Dict, List


def _clean_line(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def guess_title(text: str, max_lines: int = 25) -> str:
    """
    Heuristic: title is often in the first lines, relatively long,
    not an email, not 'abstract', not 'keywords'.
    """
    lines = [l for l in text.splitlines() if _clean_line(l)]
    lines = lines[:max_lines]

    candidates = []
    for l in lines:
        ll = l.lower().strip()
        if "@" in l:
            continue
        if ll in {"abstract", "keywords", "index terms", "contents"}:
            continue
        if len(l) < 12 or len(l) > 140:
            continue
        # avoid lines that look like affiliations
        if any(x in ll for x in ["university", "department", "institute", "email", "http", "www"]):
            continue
        candidates.append(_clean_line(l))

    # Best candidate: longest reasonable line
    if not candidates:
        return ""
    return max(candidates, key=len)


def guess_year(text: str) -> str:
    """
    Finds a likely publication year (1900-2099), returns the most frequent / first plausible.
    """
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
    if not years:
        return ""
    # Prefer a year that appears near the beginning
    head = text[:3000]
    head_years = re.findall(r"\b(19\d{2}|20\d{2})\b", head)
    if head_years:
        return head_years[0]
    return years[0]


def guess_emails(text: str, max_items: int = 5) -> List[str]:
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    # unique keep order
    seen = set()
    out = []
    for e in emails:
        if e.lower() in seen:
            continue
        seen.add(e.lower())
        out.append(e)
        if len(out) >= max_items:
            break
    return out


def extract_metadata(text: str) -> Dict[str, object]:
    """
    Returns a small metadata dict.
    """
    return {
        "title": guess_title(text),
        "year": guess_year(text),
        "emails": guess_emails(text),
    }
