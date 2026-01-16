import re
from typing import Dict


SECTION_PATTERNS = {
    "abstract": r"\nabstract\n",
    "introduction": r"\nintroduction\n",
    "methods": r"\n(methods?|materials and methods?|approach)\n",
    "results": r"\n(results?|experiments?)\n",
    "discussion": r"\n(discussion)\n",
    "conclusion": r"\n(conclusion|conclusions)\n",
    "references": r"\nreferences\n",
}


def split_into_sections(text: str) -> Dict[str, str]:
    """
    Split a scientific paper into sections using simple regex rules.
    Returns a dict: {section_name: section_text}
    """
    text_lower = text.lower()

    matches = []
    for name, pattern in SECTION_PATTERNS.items():
        for m in re.finditer(pattern, text_lower):
            matches.append((m.start(), name))

    # Sort sections by appearance in text
    matches.sort(key=lambda x: x[0])

    sections = {}
    for i, (start, name) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        sections[name] = section_text

    return sections
