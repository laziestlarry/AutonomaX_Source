"""Sparse Priming Representation utilities.

This module provides simple functions to create and decompress sparse
priming representations (SPRs) from longer pieces of text.  SPRs are
succinct summaries comprised of a small number of complete sentences
capturing the core ideas of the original text.  They can be used to
prime language models with limited context while preserving key
information.  The implementations here are deliberately lightweight and
do not depend on external NLP libraries.

Functions:
    generate_spr(text: str, max_sentences: int = 5) -> str:
        Extract the first ``max_sentences`` sentences from the input
        ``text`` and return them as an SPR.  Sentences are separated
        by common punctuation marks.  Empty or whitespace-only segments
        are skipped.

    decompress_spr(spr: str) -> str:
        Reconstruct a full paragraph from a sparse representation by
        joining the lines with spaces.  Since SPRs contain complete
        sentences, simple concatenation is sufficient.

These simple heuristics serve as a placeholder for more sophisticated
SPR generators and decompressors.  They can easily be replaced with
LLM‑based summarisation techniques or more advanced text rankers if
desired.
"""

from __future__ import annotations

import re
from typing import List


def generate_spr(text: str, max_sentences: int = 5) -> str:
    """Generate a sparse priming representation from a block of text.

    The implementation uses a naive sentence splitter based on
    punctuation.  It selects the first ``max_sentences`` non‑empty
    sentences and returns them separated by newlines.  Whitespace is
    trimmed from each sentence.

    Args:
        text: The source text from which to build the SPR.
        max_sentences: Maximum number of sentences to include.  Fewer
            sentences may be returned if the input contains fewer than
            ``max_sentences`` sentences.

    Returns:
        A string containing up to ``max_sentences`` complete sentences
        separated by newlines.  If the input is empty or contains no
        recognisable sentences, an empty string is returned.
    """
    if not text:
        return ""
    # Split on sentence terminators followed by whitespace
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    selected: List[str] = []
    for sent in sentences:
        s = sent.strip()
        if s:
            selected.append(s)
        if len(selected) >= max_sentences:
            break
    return "\n".join(selected)


def decompress_spr(spr: str) -> str:
    """Decompress a sparse priming representation back into a paragraph.

    Since SPRs consist of complete sentences separated by newlines,
    decompression simply involves joining those lines with spaces.

    Args:
        spr: A sparse priming representation as returned by
            :func:`generate_spr`.

    Returns:
        A single string containing the sentences concatenated with
        spaces.  If ``spr`` is empty, an empty string is returned.
    """
    if not spr:
        return ""
    # Split on newlines and join sentences with spaces
    parts = [line.strip() for line in spr.splitlines() if line.strip()]
    return " ".join(parts)