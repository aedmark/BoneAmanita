"""brian/cortex.py"""
import re
import math
from typing import List, Dict
from collections import Counter


class LinearCortexRouter:
    """
    S.L.A.S.H. SubQ Emulator for BoneAmanita.
    Executes an O(n) linear pass over the entire raw artifact (memory/lore)
    to generate a content-dependent sparsity mask before hitting the LLM.
    """

    def __init__(self, token_budget: int = 8000):
        self.token_budget = token_budget
        # The organism's active, unified state. No chunks.
        self.unified_manifold = []

    def ingest_artifact(self, artifact_name: str, raw_text: str):
        """
        Meadows: "Stock the system."
        We ingest whole files. No arbitrary chunking.
        """
        # Split by natural structural boundaries (lines/paragraphs), not fixed token counts.
        structural_nodes = raw_text.split('\n')
        for idx, node in enumerate(structural_nodes):
            if node.strip():
                self.unified_manifold.append({
                    "id": f"{artifact_name}_L{idx}",
                    "content": node,
                    "length": len(node.split()) + 1
                })

    def _calculate_resonance(self, query: str, node: str) -> float:
        """
        Pinker: "Content-dependent selection."
        A blazing fast O(n) heuristic replacing the quadratic attention indexer.
        Uses raw lexical overlap and structural density.
        """
        q_terms = set(re.findall(r'\w+', query.lower()))
        n_terms = re.findall(r'\w+', node.lower())

        if not n_terms: return 0.0

        n_counts = Counter(n_terms)
        resonance = sum(n_counts[q] for q in q_terms)

        # Boost structural/physics keys native to BoneAmanita
        if any(keyword in node for keyword in ['@', 'class ', 'def ', 'ATP', 'ROS']):
            # Ensure structural nodes survive the zero-overlap purge
            resonance = max(resonance, 1.0) * 1.5

            # Penalize bloat (emulating sparsity pressure)
        density = resonance / len(n_terms)
        return density * resonance

    def route_attention(self, query: str) -> str:
        """
        The Chef: "Plate the dish."
        Returns a linearly-selected, highly sparse context window.
        """
        # 1. Linear O(n) sweep to score all nodes against the query
        scored_nodes = []
        for node in self.unified_manifold:
            score = self._calculate_resonance(query, node["content"])
            if score > 0:
                scored_nodes.append((score, node))

        # 2. Sort by highest resonance (O(k log k))
        scored_nodes.sort(key=lambda x: x[0], reverse=True)

        # 3. Pack context until metabolic budget is hit
        current_tokens = 0
        selected_nodes = []

        for score, node in scored_nodes:
            if current_tokens + node["length"] > self.token_budget:
                break
            selected_nodes.append(node)
            current_tokens += node["length"]

        # Re-sort selected nodes by original structural ID to maintain topological order
        selected_nodes.sort(key=lambda x: x["id"])

        # Return the sparse, structural representation
        return "\n".join([f"[{n['id']}] {n['content']}" for n in selected_nodes])

# --- Usage in genesis.py or core.py ---
# cortex = LinearCortexRouter(token_budget=16000)
# cortex.ingest_artifact("akashic.py", open("brain/akashic.py").read())
# cortex.ingest_artifact("metabolism.py", open("body/metabolism.py").read())
# sparse_context = cortex.route_attention("How does ATP interact with the Akashic record?")
