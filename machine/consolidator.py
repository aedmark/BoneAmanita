"""machine/consolidator.py"""

from constants import Prisma

class TheConsolidator:
    def __init__(self, events_ref, memory_ref, akashic_ref):
        self.events = events_ref
        self.memory = memory_ref
        self.akashic = akashic_ref
        self.setup_listeners()

    def setup_listeners(self):
        self.events.subscribe("SHADOW_ENGAGED", self._on_shadow_engaged)
        self.events.subscribe("RESONANCE_ACHIEVED", self._on_resonance_achieved)
        self.events.subscribe("SYNTAX_CORRECTED", self._on_syntax_corrected)
        self.events.subscribe("MEMORY_BURIED", self._on_memory_buried)

    def _on_memory_buried(self, payload):
        from struts import safe_get
        fossil = safe_get(payload, "fossil")
        if fossil and self.akashic:
            self.akashic.bury_memory(safe_get(fossil, "word", "Unknown"), fossil)

    def _on_syntax_corrected(self, payload):
        from struts import safe_get
        triplet = safe_get(payload, "triplet")
        if not triplet: return
        from core import LoreManifest
        lore = LoreManifest.get_instance()
        weights = list(lore.get("SYNTACTIC_WEIGHTS") or [])
        weights = (weights + [triplet])[-50:]
        try:
            lore.inject("SYNTACTIC_WEIGHTS", weights)
            lore.save("SYNTACTIC_WEIGHTS")
            msg = f"Syntactic Compiler accrued 1 new Few-Shot weight. Total: {len(weights)}."
            self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "CORTEX")
        except Exception as e:
            self.events.log(f"{Prisma.RED}Failed to save syntactic weights: {e}{Prisma.RST}", "ERROR")

    def _on_shadow_engaged(self, payload):
        from struts import safe_get
        source = safe_get(payload, "source", "core")
        target = safe_get(payload, "target")
        if not target:
            return
        self.memory.memory_core.strengthen_link(source=source, target=target, rate=2.0, decay=0.85)
        msg = f"User engaged shadow concept '{target}'. Synaptic link {source} -> {target} strengthened."
        self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}", "MEMORY")

    def _on_resonance_achieved(self, payload):
        from struts import safe_get
        result = safe_get(payload, "result", "Unknown Paradigm")
        msg = safe_get(payload, "msg", "Resonance stabilized.")
        self.akashic.record_glimmer(concept=result, paradigm=msg)