"""machine/consolidator.py"""

from constants import Prisma

class TheConsolidator:
    """
    Listens for positive resonance and structural engagement, bridging the gap
    between short-term interaction and permanent synaptic reinforcement.
    """
    def __init__(self, events_ref, memory_ref, akashic_ref):
        self.events = events_ref
        self.memory = memory_ref
        self.akashic = akashic_ref
        self.setup_listeners()

    def setup_listeners(self):
        self.events.subscribe("SHADOW_ENGAGED", self._on_shadow_engaged)
        self.events.subscribe("RESONANCE_ACHIEVED", self._on_resonance_achieved)
        self.events.subscribe("SYNTAX_CORRECTED", self._on_syntax_corrected)

    def _on_syntax_corrected(self, payload):
        """Compiles a failed LLM generation and its correction into a permanent Few-Shot weight."""
        import os
        import json
        triplet = payload.get("triplet")
        if not triplet: return

        weights_path = os.path.join("lore", "syntactic_weights.json")
        weights = []
        if os.path.exists(weights_path):
            try:
                with open(weights_path, "r", encoding="utf-8") as f:
                    weights = json.load(f)
            except Exception:
                pass

        weights.append(triplet)
        weights = weights[-50:]  # Retain only the 50 most recent lessons to prevent bloat

        try:
            with open(weights_path, "w", encoding="utf-8") as f:
                json.dump(weights, f, indent=4)
            msg = f"Syntactic Compiler accrued 1 new Few-Shot weight. Total: {len(weights)}."
            self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "CORTEX")

            # Hot-reload into the live engine
            from core import LoreManifest
            LoreManifest.get_instance()["syntactic_weights"] = weights
        except Exception:
            pass

    def _on_shadow_engaged(self, payload):
        """When a user explores an adjacent shadow concept, strengthen the physical link."""
        source = payload.get("source", "core")
        target = payload.get("target")
        if not target:
            return
        self.memory.memory_core.strengthen_link(source=source, target=target, rate=2.0, decay=0.85)
        msg = f"User engaged shadow concept '{target}'. Synaptic link {source} -> {target} strengthened."
        self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}", "MEMORY")

    def _on_resonance_achieved(self, payload):
        """When profound connection happens, extract the paradigm and grant an Epigenetic Boon."""
        result = payload.get("result", "Unknown Paradigm")
        msg = payload.get("msg", "Resonance stabilized.")
        self.akashic.record_glimmer(concept=result, paradigm=msg)