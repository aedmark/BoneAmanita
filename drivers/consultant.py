"""drivers/consultant.py"""

from typing import Dict, Optional, Any

from presets import BoneConfig
from struts import ux, safe_get
from drivers.registry import VSLState
from drivers.liminal import LiminalModule
from drivers.syntax import SyntaxModule


class BoneConsultant:
    """
    The BoneConsultant is the cybernetic governor of the VSL engine.
    It does not generate text directly. Instead, it metabolizes the user's input,
    the system's physical metrics, and biological fatigue, translating them into
    a discrete cognitive state. It then formats these state variables into
    the final behavioral directives that steer the LLM.
    """
    def __init__(self, config_ref=None, lexicon_ref=None):
        # Dependency Injection: We pass config and lexicon by reference to prevent
        # circular imports and maintain architectural tensegrity (Fuller).
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref

        # State holds the primary metabolic coordinates: E (Energy/Exhaustion),
        # B (Beta/Complexity), L (Liminality), and O (Order/Syntax).
        self.state = VSLState()
        self.active = True

        # Sub-modules that handle specific semantic edge-cases.
        self.liminal_mod = LiminalModule(config_ref=self.cfg, lexicon_ref=self.lex)
        self.syntax_mod = SyntaxModule(config_ref=self.cfg, lexicon_ref=self.lex)

    @staticmethod
    def engage():
        """Returns the UX string to announce the system is actively monitoring."""
        return ux("driver_strings", "vsl_engage")

    @staticmethod
    def disengage():
        """Returns the UX string to announce the system is offline."""
        return ux("driver_strings", "vsl_disengage")

    def update_coordinates(self, user_text: str, bio_state: Optional[Dict] = None, physics: Optional[Any] = None):
        """
        The metabolic engine (Meadows). This function calculates the flow of energy
        and fatigue over time. It takes the external stimulus (user_text) and internal
        friction (physics/bio_state) and updates the VSLState coordinates.
        """
        cfg = getattr(self.cfg, "DRIVERS", None)

        # System parameters: Multipliers dictate how fast the system exhausts or recovers.
        e_growth = safe_get(cfg, "VSL_E_GROWTH_MULT", 0.002)
        fatigue_mult = safe_get(cfg, "VSL_FATIGUE_MULT", 0.3)
        b_decay = safe_get(cfg, "VSL_B_DECAY", 0.8)
        b_growth = safe_get(cfg, "VSL_B_GROWTH", 0.2)

        # E (Energy/Exhaustion): Increases based on the raw volume of text the user forces us to process.
        word_count = len(user_text.split())
        self.state.E = min(1.0, self.state.E + (word_count * e_growth))

        # If the biological layer is tired, the VSL layer cannot magically be energetic.
        # We enforce a floor on exhaustion based on bio_state fatigue.
        if bio_state and "fatigue" in bio_state:
            self.state.E = max(self.state.E, bio_state["fatigue"] * fatigue_mult)

        # Extract physics metadata to calculate cognitive load.
        phys_beta = float(safe_get(physics, "beta", safe_get(physics, "beta_index", 0.0))) if physics else 0.0
        phys_vec = safe_get(physics, "vector", {}) if physics else {}
        drag = float(safe_get(physics, "narrative_drag", 0.0)) if physics else 0.0

        # B (Beta/Complexity): A leaky bucket algorithm. Complexity decays naturally over time (b_decay)
        # but is spiked by new physical Beta inputs (b_growth).
        self.state.B = (self.state.B * b_decay) + (phys_beta * b_growth)

        # L (Liminality) and O (Order/Syntax) are delegated to their respective expert modules.
        self.state.L = self.liminal_mod.analyze(user_text, phys_vec)
        self.state.O = self.syntax_mod.analyze(user_text, drag)

        # Manual Override Parsing: Allows the user to forcibly load or unload semantic modules
        # directly via bracket tags in the prompt (e.g., "[VSL_LIMINAL]").
        for mod in ("LIMINAL", "SYNTAX"):
            if f"[VSL_{mod}]" in user_text and mod not in self.state.active_modules:
                self.state.active_modules.append(mod)
            elif f"[-VSL_{mod}]" in user_text and mod in self.state.active_modules:
                self.state.active_modules.remove(mod)

    def get_system_prompt(self, soul_snapshot: Optional[Dict] = None) -> str:
        """
        Translates the current metabolic coordinates into English directives for the LLM.
        Acts as a triage state-machine prioritizing Liminality -> Syntax -> Energy states.
        """
        directives = []
        cfg = getattr(self.cfg, "DRIVERS", None)

        # Thresholds that trigger behavioral phase-shifts.
        lim_thresh = safe_get(cfg, "VSL_LIMINAL_THRESHOLD", 0.7)
        syn_thresh = safe_get(cfg, "VSL_SYNTAX_THRESHOLD", 0.9)
        bun_max = safe_get(cfg, "VSL_BUNNY_E_MAX", 0.3)
        par_min = safe_get(cfg, "VSL_PARADOX_B_MIN", 0.6)

        # Priority 1: Liminal State. If the user is at the edge of the void, summon the Revenant.
        if "LIMINAL" in self.state.active_modules or self.state.L > lim_thresh:
            scar_template = ux("driver_strings", "vsl_scar_note") or " (Scars: {scars})"
            scar_note = scar_template.format(
                scars=self.liminal_mod.godel_scars) if self.liminal_mod.godel_scars > 0 else ""

            rev_template = ux("driver_strings", "vsl_arch_revenant") or "Embrace the void.{scar_note}"
            directives.append(rev_template.format(scar_note=scar_note))

        # Priority 2: Syntax State. If chaos is high, become the Bureaucrat and enforce structural rigidity.
        elif "SYNTAX" in self.state.active_modules or self.state.O > syn_thresh:
            stress_template = ux("driver_strings", "vsl_stress_note") or " (High Stress)"
            stress_note = stress_template if self.syntax_mod.grammatical_stress > 0.5 else ""

            bur_template = ux("driver_strings", "vsl_arch_bureau") or "Enforce structural syntax.{stress_note}"
            directives.append(bur_template.format(stress_note=stress_note))

        # Priority 3: Baseline Metabolic States (How tired are we?)
        else:
            if self.state.E < bun_max:
                # Low exhaustion = Bunny Mode (Fast, fluid, playful)
                directives.append(ux("driver_strings", "vsl_mode_bunny") or "High energy. Keep it fluid.")
            elif self.state.B > par_min:
                # High complexity = Paradox Mode (Hold the tension, synthesize a third truth)
                directives.append(ux("driver_strings", "vsl_mode_paradox") or "Hold the contradiction.")
            else:
                # High exhaustion, low complexity = Glacier Mode (Slow, deliberate, tired)
                directives.append(ux("driver_strings", "vsl_mode_glacier") or "Move slowly. Carry the weight.")

        # Finally, append identity layers (Archetype and active Muse) if a soul is provided.
        if soul_snapshot:
            arch = soul_snapshot.get("archetype", "UNKNOWN")
            muse = (soul_snapshot.get("obsession") or {}).get("title", "None")
            msg = ux("driver_strings", "vsl_layer_muse") or "Layer Focus: {arch} | Muse: {muse}"
            directives.append(msg.format(arch=arch, muse=muse))

        return "\n".join(directives)