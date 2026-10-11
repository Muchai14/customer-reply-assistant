"""Deterministic FAQ lookup using only the Python standard library.

Score an FAQ by the number of words in its longest matching keyword phrase.
Repeated keywords do not increase the score. Break ties by ascending FAQ ID.
This is literal phrase matching, not semantic understanding or confidence scoring.
"""

import json
import re
import unicodedata
from pathlib import Path
from typing import Iterable, Optional, TypedDict


class FAQ(TypedDict):
    id: str
    title: str
    category: str
    keywords: list[str]
    answer: str


DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "faqs.json"


def load_faqs(path: Optional[Path] = None) -> list[FAQ]:
    """Load the project's trusted FAQ file independently of the working directory."""
    with (path or DEFAULT_DATA_PATH).open(encoding="utf-8") as source:
        return json.load(source)["faqs"]


def _tokens(text: str) -> list[str]:
    # Normalize capitalization, punctuation, spacing, and compatibility characters.
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return re.findall(r"[^\W_]+", normalized)


def match_faq(question: str, faqs: Iterable[FAQ]) -> Optional[FAQ]:
    """Return one matching FAQ, or None when no complete keyword phrase matches.

    Surrounding whitespace is removed before validating the 1–1,000 character
    limit. No files are written and no network calls are made.
    """
    if not isinstance(question, str):
        raise ValueError("Question must be a string.")
    question = question.strip()
    if not 1 <= len(question) <= 1000:
        raise ValueError("Question must contain 1–1,000 characters after trimming.")

    question_tokens = _tokens(question)
    best = None
    best_score = 0
    for faq in sorted(faqs, key=lambda item: item["id"]):
        score = 0
        for keyword in faq["keywords"]:
            phrase = _tokens(keyword)
            size = len(phrase)
            if size and any(
                question_tokens[index:index + size] == phrase
                for index in range(len(question_tokens) - size + 1)
            ):
                score = max(score, size)
        if score > best_score:
            best = faq
            best_score = score
    return best
