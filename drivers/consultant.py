"""drivers/consultant.py"""

from typing import Any, Dict, Optional

from drivers.liminal import LiminalModule
from drivers.registry import VSLState
from drivers.syntax import SyntaxModule
from presets import BoneConfig
from struts import safe_get, ux, ux_format


class BoneConsultant:
    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.state = VSLState()
        self.active = True
        self.liminal_mod = LiminalModule(config_ref=self.cfg, lexicon_ref=self.lex)
        self.syntax_mod = SyntaxModule(config_ref=self.cfg, lexicon_ref=self.lex)

    @staticmethod
    def engage():
        return ux("driver_strings", "vsl_engage")

    @staticmethod
    def disengage():
        return ux("driver_strings", "vsl_disengage")

    def update_coordinates(
        self,
        user_text: str,
        bio_state: Optional[Dict] = None,
        physics: Optional[Any] = None,
    ):
        user_text = user_text or ""
        cfg = safe_get(self.cfg, "DRIVERS", {})
        e_growth = float(safe_get(cfg, "VSL_E_GROWTH_MULT", 0.002))
        fatigue_mult = float(safe_get(cfg, "VSL_FATIGUE_MULT", 0.3))
        b_decay = float(safe_get(cfg, "VSL_B_DECAY", 0.8))
        b_growth = float(safe_get(cfg, "VSL_B_GROWTH", 0.2))
        word_count = len(user_text.split())
        self.state.E = min(1.0, self.state.E + (word_count * e_growth))
        if bio_state and "fatigue" in bio_state:
            self.state.E = max(self.state.E, bio_state["fatigue"] * fatigue_mult)
        phys_beta = float(safe_get(physics, "beta_index", 0.0))
        phys_vec = safe_get(physics, "vector", {})
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        self.state.B = (self.state.B * b_decay) + (phys_beta * b_growth)
        self.state.O = self.syntax_mod.analyze(user_text, drag)
        self.state.L = self.liminal_mod.analyze(
            user_text, phys_vec, grammatical_stress=self.syntax_mod.grammatical_stress
        )
        for mod in ("LIMINAL", "SYNTAX"):
            if f"[VSL_{mod}]" in user_text and mod not in self.state.active_modules:
                self.state.active_modules.append(mod)
            elif f"[-VSL_{mod}]" in user_text and mod in self.state.active_modules:
                self.state.active_modules.remove(mod)

    def get_system_prompt(self, soul_snapshot: Optional[Dict] = None) -> str:
        directives = []
        cfg = safe_get(self.cfg, "DRIVERS", {})
        lim_thresh = float(safe_get(cfg, "VSL_LIMINAL_THRESHOLD", 0.7))
        syn_thresh = float(safe_get(cfg, "VSL_SYNTAX_THRESHOLD", 0.9))
        bun_max = float(safe_get(cfg, "VSL_BUNNY_E_MAX", 0.3))
        par_min = float(safe_get(cfg, "VSL_PARADOX_B_MIN", 0.6))
        if "LIMINAL" in self.state.active_modules or self.state.L > lim_thresh:
            scar_note = (
                ux_format(
                    "driver_strings",
                    "vsl_scar_note",
                    default=" (Scars: {scars})",
                    scars=self.liminal_mod.godel_scars,
                )
                if self.liminal_mod.godel_scars > 0
                else ""
            )
            directives.append(
                ux_format(
                    "driver_strings",
                    "vsl_arch_revenant",
                    default="Embrace the void.{scar_note}",
                    scar_note=scar_note,
                )
            )
        elif "SYNTAX" in self.state.active_modules or self.state.O > syn_thresh:
            stress_note = (
                (ux("driver_strings", "vsl_stress_note") or " (High Stress)")
                if self.syntax_mod.grammatical_stress > 0.5
                else ""
            )
            directives.append(
                ux_format(
                    "driver_strings",
                    "vsl_arch_bureau",
                    default="Enforce structural syntax.{stress_note}",
                    stress_note=stress_note,
                )
            )
        else:
            if self.state.E < bun_max:
                directives.append(
                    ux("driver_strings", "vsl_mode_bunny")
                    or "High energy. Keep it fluid."
                )
            elif self.state.B > par_min:
                directives.append(
                    ux("driver_strings", "vsl_mode_paradox")
                    or "Hold the contradiction."
                )
            else:
                directives.append(
                    ux("driver_strings", "vsl_mode_glacier")
                    or "Move slowly. Carry the weight."
                )
        if soul_snapshot:
            arch = soul_snapshot.get("archetype", "UNKNOWN")
            muse = (soul_snapshot.get("obsession") or {}).get("title", "None")
            directives.append(
                ux_format(
                    "driver_strings",
                    "vsl_layer_muse",
                    default="Layer Focus: {arch} | Muse: {muse}",
                    arch=arch,
                    muse=muse,
                )
            )
        return "\n".join(directives)
