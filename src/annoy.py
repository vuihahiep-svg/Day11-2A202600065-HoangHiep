"""Lightweight fallback for AnnoyIndex used by NeMo Guardrails in this lab.

This module is a minimal in-memory replacement for the third-party `annoy`
package, which can fail to compile on some local macOS setups.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Tuple


class AnnoyIndex:
    """Subset of AnnoyIndex API needed by nemoguardrails.embeddings.basic."""

    def __init__(self, f: int, metric: str = "angular"):
        self.f = f
        self.metric = metric
        self._items: Dict[int, List[float]] = {}

    def add_item(self, i: int, vector: Iterable[float]) -> None:
        vec = list(vector)
        if len(vec) != self.f:
            raise ValueError(f"Vector length {len(vec)} != expected {self.f}")
        self._items[i] = vec

    def build(self, n_trees: int = 10) -> bool:  # API compatibility
        return True

    def get_nns_by_vector(
        self, vector: Iterable[float], n: int, include_distances: bool = False
    ) -> Tuple[List[int], List[float]] | List[int]:
        q = list(vector)
        scores: List[Tuple[int, float]] = []
        for idx, item in self._items.items():
            distance = self._angular_distance(q, item)
            scores.append((idx, distance))
        scores.sort(key=lambda x: x[1])
        top = scores[:n]
        ids = [idx for idx, _ in top]
        if include_distances:
            dists = [dist for _, dist in top]
            return ids, dists
        return ids

    @staticmethod
    def _angular_distance(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 2.0
        cosine = max(-1.0, min(1.0, dot / (norm_a * norm_b)))
        # Match basic Annoy "angular-like" range used by NeMo threshold math.
        return 2.0 * (1.0 - cosine)
