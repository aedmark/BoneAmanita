"""brian/cortex.py"""

import math
import re
from collections import Counter
from typing import Dict, List


class LinearCortexRouter:
    def __init__(self, token_budget: int = 8000):
        self.token_budget = token_budget
        self.unified_manifold = []

    def ingest_artifact(self, artifact_name: str, raw_text: str):
        structural_nodes = raw_text.split("\n")
        for idx, node in enumerate(structural_nodes):
            if node.strip():
                self.unified_manifold.append(
                    {
                        "id": f"{artifact_name}_L{idx}",
                        "content": node,
                        "length": len(node.split()) + 1,
                    }
                )

    def _calculate_resonance(self, query: str, node: str) -> float:
        q_terms = set(re.findall(r"\w+", query.lower()))
        n_terms = re.findall(r"\w+", node.lower())
        if not n_terms:
            return 0.0
        n_counts = Counter(n_terms)
        resonance = sum(n_counts[q] for q in q_terms)
        if any(keyword in node for keyword in ["@", "class ", "def ", "ATP", "ROS"]):
            resonance = max(resonance, 1.0) * 1.5
        density = resonance / len(n_terms)
        return density * resonance

    def route_attention(self, query: str) -> str:
        scored_nodes = []
        for node in self.unified_manifold:
            score = self._calculate_resonance(query, node["content"])
            if score > 0:
                scored_nodes.append((score, node))
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        current_tokens = 0
        selected_nodes = []
        for score, node in scored_nodes:
            if current_tokens + node["length"] > self.token_budget:
                break
            selected_nodes.append(node)
            current_tokens += node["length"]
        selected_nodes.sort(key=lambda x: x["id"])
        return "\n".join([f"[{n['id']}] {n['content']}" for n in selected_nodes])
