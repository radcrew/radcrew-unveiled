"""Typo-tolerant token matching shared by the feedback-router gates.

``confirm.py`` and ``pregate.py`` compare a single normalized token against a
small, fixed vocabulary. Exact matching silently drops common typos
("definitley", "waht", "cancl"), which flips the route the user gets. These
helpers add *conservative*, length-aware edit-distance tolerance — short tokens
still require an exact match, so we never expand "go" into "no" — without
pulling in a dependency.
"""

from __future__ import annotations

from typing import Iterable


def damerau_levenshtein(a: str, b: str) -> int:
    """Optimal string alignment distance (adjacent transposition counts as 1).

    This catches the most common typo classes: insertion, deletion,
    substitution, and swapping two neighbouring letters ("yse" → "yes").
    """
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if not la:
        return lb
    if not lb:
        return la

    prev2: list[int] = []
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i] + [0] * lb
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            curr[j] = min(
                prev[j] + 1,         # deletion
                curr[j - 1] + 1,     # insertion
                prev[j - 1] + cost,  # substitution
            )
            if i > 1 and j > 1 and ca == b[j - 2] and a[i - 2] == cb:
                curr[j] = min(curr[j], prev2[j - 2] + 1)  # transposition
        prev2, prev = prev, curr
    return prev[lb]


# Tokens shorter than this never fuzzy-match: at 1-3 chars an edit distance of 1
# collides across intents far too easily ("go"/"no", "ok"/"on", "yes"/"yep").
# Those terse replies are handled by explicit vocabulary entries and, failing
# that, the LLM fallback.
_MIN_FUZZY_LEN = 4


def _budget(word: str) -> int:
    n = len(word)
    if n < _MIN_FUZZY_LEN:
        return 0
    if n <= 6:
        return 1
    return 2


def fuzzy_in(
    word: str,
    vocabulary: Iterable[str],
    *,
    max_distance: int | None = None,
) -> bool:
    """True if ``word`` exactly matches, or is a near-typo of, a vocab entry.

    Only words and targets of length >= ``_MIN_FUZZY_LEN`` are eligible for
    fuzzy matching. The per-word budget scales with length (<=6 → 1 edit,
    longer → 2) and can be capped with ``max_distance`` by callers that want to
    stay extra conservative.
    """
    vocab = set(vocabulary)
    if word in vocab:
        return True

    budget = _budget(word)
    if max_distance is not None:
        budget = min(budget, max_distance)
    if budget <= 0:
        return False

    for target in vocab:
        if len(target) < _MIN_FUZZY_LEN:
            continue
        if abs(len(word) - len(target)) > budget:
            continue
        if damerau_levenshtein(word, target) <= budget:
            return True
    return False
