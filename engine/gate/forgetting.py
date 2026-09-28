"""Forgetting (memory phase 5): before the self graph's cap starts denying writes, consolidation drops
near-duplicate memories (by meaning) and the least-recalled ones. It runs in the REM tick, and in a turn
once memory reaches the high-water mark, as an engine-built `forget` nomination in its own gate cycle."""
from __future__ import annotations

import numpy as np

from .recall import memory_hash

# SIMILAR, measured with nomic-embed-text: paraphrased duplicates 0.90 to 0.97, distinct memories at most
# 0.76 ("sister visiting next week" against "Mum visiting next week").
HIGH, LOW, SIMILAR = 0.9, 0.8, 0.88


def plan(memory: dict, stats: dict, vectors: dict | None, model: str, cap: int,
         high: float = HIGH, low: float = LOW, similar: float = SIMILAR) -> dict:
    """{key: why} for the memories to forget. Weakest first: least recalled, then longest since recalled,
    then oldest written."""
    age = {k: i for i, k in enumerate(memory)}
    weakness = lambda k: (stats.get(k, (0, 0.0))[0], stats.get(k, (0, 0.0))[1], age[k])
    reasons = {}
    live = {k: v[2] for k, v in (vectors or {}).items()
            if k in memory and v[1] == model and v[0] == memory_hash(k, memory[k])}
    if len(live) > 1:
        keys = sorted(live, key=weakness, reverse=True)
        m = np.array([live[k] for k in keys], dtype=np.float32)
        m /= np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-12)
        sims = m @ m.T
        kept = []
        for i, key in enumerate(keys):
            twin = next((j for j in kept if sims[i, j] >= similar), None)
            if twin is None:
                kept.append(i)
            else:
                reasons[key] = f"near-duplicate of {keys[twin]}"
    remaining = [k for k in memory if k not in reasons]
    if len(remaining) >= high * cap:
        for key in sorted(remaining, key=weakness)[: len(remaining) - int(low * cap)]:
            reasons[key] = "least recalled"
    return reasons


def forget_text(reasons: dict, why: str) -> str:
    lines = [f"(Forgetting, {why}: {len(reasons)} memories.)"]
    lines += [f"- {key}: {reason}" for key, reason in reasons.items()]
    lines.append(f"NOMINATE what=self/memory/consolidation verb=forget args=keys:{' | '.join(reasons)}")
    return "\n".join(lines)
