"""body/endocrine.py"""

import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from body.models import SemanticSignal
from core import LoreManifest
from presets import BoneConfig
from struts import safe_get


@dataclass
class EndocrineSystem:
    dopamine: float = 0.5
    oxytocin: float = 0.1
    cortisol: float = 0.0
    serotonin: float = 0.5
    adrenaline: float = 0.0
    melatonin: float = 0.0
    glimmers: int = 0
    narrative_data: Dict = field(default_factory=dict, repr=False)
    config_ref: Any = None
    _REACTION_MAP: Dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.cfg = self.config_ref or BoneConfig
        body_config = (
            LoreManifest.get_instance(config_ref=self.cfg).get("BODY_CONFIG") or {}
        )
        self._REACTION_MAP = body_config.get("REACTION_MAP", {})
        self._KEY_MAP = {
            "ADR": "adrenaline",
            "COR": "cortisol",
            "OXY": "oxytocin",
            "DOP": "dopamine",
            "SER": "serotonin",
            "MEL": "melatonin",
        }
        self._CIRCADIAN_SCHEDULE = body_config.get("CIRCADIAN_SCHEDULE", [])
        self._CIRCADIAN_NIGHT = body_config.get(
            "CIRCADIAN_NIGHT", [{"MEL": 0.3, "COR": -0.1}, "LUNAR", ""]
        )
        if (
            not isinstance(self._CIRCADIAN_NIGHT, list)
            or len(self._CIRCADIAN_NIGHT) < 3
        ):
            self._CIRCADIAN_NIGHT = [{"MEL": 0.3, "COR": -0.1}, "LUNAR", ""]

    @staticmethod
    def _clamp(val: float) -> float:
        return max(0.0, min(1.0, val))

    def calculate_circadian_bias(self) -> Tuple[Dict[str, float], Optional[str]]:
        hour = time.localtime().tm_hour
        circ = self.narrative_data.get("CIRCADIAN", {})
        for s, e, bias, key, default in self._CIRCADIAN_SCHEDULE:
            if s <= hour < e:
                return bias, circ.get(key, default)
        night_bias, night_key, night_default = self._CIRCADIAN_NIGHT
        return night_bias, circ.get(night_key, night_default)

    def _apply_enzyme_reaction(self, enzyme_type: str, harvest_hits: int):
        if harvest_hits > 0:
            satiety_dampener = max(0.1, 1.0 - float(self.dopamine))
            base_reward = math.log(harvest_hits + 1) * 0.15
            final_reward = base_reward * satiety_dampener
            self.dopamine = float(self.dopamine) + final_reward
            self.cortisol = float(self.cortisol) - (final_reward * 0.4)
        if enzyme_type == "DECRYPTASE":
            self.serotonin = min(1.0, float(self.serotonin) + 0.15)
            self.cortisol = max(0.0, float(self.cortisol) - 0.2)
        if isinstance(impact := self._REACTION_MAP.get(enzyme_type), dict):
            for k, v in impact.items():
                attr = self._KEY_MAP.get(k)
                if isinstance(attr, str) and hasattr(self, attr):
                    setattr(self, attr, float(getattr(self, attr)) + float(v))

    def _apply_environmental_pressure(
        self,
        feedback: Dict,
        health: float,
        stamina: float,
        ros_level: float,
        stress_mod: float,
    ):
        bio_cfg = safe_get(self.cfg, "BIO", {})
        reward_large = safe_get(bio_cfg, "REWARD_LARGE", 0.2)
        reward_med = safe_get(bio_cfg, "REWARD_MEDIUM", 0.1)
        decay = safe_get(bio_cfg, "DECAY_RATE", 0.01)
        self.cortisol = max(0.0, float(self.cortisol) - (decay * 0.5))
        self.oxytocin = max(0.0, float(self.oxytocin) - (decay * 0.5))
        self.serotonin = float(self.serotonin) + ((0.5 - float(self.serotonin)) * decay)
        self.melatonin = max(0.0, float(self.melatonin) - (decay * 0.2))
        if feedback.get("STATIC", 0) > 0.6:
            self.cortisol = float(self.cortisol) + (reward_large * stress_mod)
        if feedback.get("INTEGRITY", 0) > 0.8:
            self.dopamine = float(self.dopamine) + reward_med
        else:
            self.dopamine = max(0.0, float(self.dopamine) - decay)
        if stamina < 20.0:
            self.cortisol = float(self.cortisol) + (reward_med * stress_mod)
            self.dopamine = max(0.0, float(self.dopamine) - reward_med)
        if ros_level > 20.0:
            self.cortisol = float(self.cortisol) + (reward_large * stress_mod)
        if health < 30.0 or feedback.get("STATIC", 0) > 0.8:
            self.adrenaline = float(self.adrenaline) + (reward_large * stress_mod)
        else:
            self.adrenaline = max(0.0, float(self.adrenaline) - (decay * 5.0))
        psi = feedback.get("PSI", 0.0)
        chi = feedback.get("CHI", feedback.get("ENTROPY", 0.0))
        valence = feedback.get("VALENCE", 0.0)
        if psi > 0.6:
            self.adrenaline = float(self.adrenaline) + 0.4
            self.melatonin = float(self.melatonin) + (0.2 * psi)
        if chi > 0.6:
            self.cortisol = float(self.cortisol) + ((0.6 * chi) * stress_mod)
            self.serotonin = float(self.serotonin) - 0.2
        if valence > 0.5:
            self.oxytocin = float(self.oxytocin) + (0.5 * valence)
            self.serotonin = float(self.serotonin) + 0.3
            self.cortisol = float(self.cortisol) - 0.3
        elif valence < -0.5:
            self.cortisol = float(self.cortisol) + (abs(valence) * 0.4)
            self.dopamine = float(self.dopamine) - 0.2

    def _apply_semantic_pressure(self, signal: SemanticSignal):
        if signal.novelty > 0.3:
            self.dopamine = float(self.dopamine) + (signal.novelty * 0.3)
        if signal.resonance > 0.2:
            self.oxytocin = float(self.oxytocin) + (signal.resonance * 0.4)
            self.cortisol = float(self.cortisol) - (signal.resonance * 0.2)
        if signal.valence > 0.3:
            self.serotonin = float(self.serotonin) + (signal.valence * 0.3)
            self.oxytocin = float(self.oxytocin) + (signal.valence * 0.2)
        elif signal.valence < -0.3:
            self.cortisol = float(self.cortisol) + (abs(signal.valence) * 0.2)
        if signal.coherence > 0.7:
            self.adrenaline = float(self.adrenaline) - 0.1
            self.cortisol = float(self.cortisol) - 0.1

    def _maintain_homeostasis(self, social_context: bool):
        dampener = 0.2
        bio_cfg = safe_get(self.cfg, "BIO", {})
        reward_med = float(safe_get(bio_cfg, "REWARD_MEDIUM", 0.1))
        reward_small = float(safe_get(bio_cfg, "REWARD_SMALL", 0.05))
        if self.serotonin > 0.5:
            excess = self.serotonin - 0.5
            self.cortisol -= excess * 0.2 * dampener
        if social_context:
            self.oxytocin += reward_med
            self.cortisol -= reward_med
        if self.cortisol > 0.6:
            suppression = (self.cortisol - 0.6) * 0.5
            self.oxytocin -= suppression * dampener
        if self.oxytocin > 0.5:
            relief = (self.oxytocin - 0.5) * 0.8
            self.cortisol -= relief * dampener
        if self.adrenaline < 0.2:
            self.melatonin += reward_small / 2.0
        elif self.adrenaline > 0.8:
            self.melatonin = 0.0

    def check_for_glimmer(self, feedback: Dict, harvest_hits: int) -> Optional[str]:
        glimmer_text = self.narrative_data.get("GLIMMER", {})
        target_cfg = getattr(self, "cfg", BoneConfig)
        bio_cfg = getattr(target_cfg, "BIO", None)
        if bio_cfg and not isinstance(bio_cfg, dict):
            int_thresh = float(getattr(bio_cfg, "GLIMMER_INTEGRITY_THRESH", 0.85))
            nov_thresh = getattr(bio_cfg, "GLIMMER_NOVELTY_THRESH", 0.8)
            harv_min = getattr(bio_cfg, "GLIMMER_HARVEST_MIN", 2)
            dop_min = getattr(bio_cfg, "GLIMMER_DOPAMINE_MIN", 0.7)
        else:
            cfg_dict = bio_cfg or {}
            int_thresh = float(cfg_dict.get("GLIMMER_INTEGRITY_THRESH", 0.85))
            nov_thresh = cfg_dict.get("GLIMMER_NOVELTY_THRESH", 0.8)
            harv_min = cfg_dict.get("GLIMMER_HARVEST_MIN", 2)
            dop_min = cfg_dict.get("GLIMMER_DOPAMINE_MIN", 0.7)
        if feedback.get("INTEGRITY", 0) > int_thresh:
            self.glimmers = int(self.glimmers) + 1
            self.serotonin = float(self.serotonin) + 0.2
            return glimmer_text.get("INTEGRITY", "")
        if feedback.get("NOVELTY", 0) > nov_thresh:
            self.glimmers = int(self.glimmers) + 1
            self.dopamine = float(self.dopamine) + 0.1
            return glimmer_text.get(
                "DISCOVERY", "GLIMMER: A novel connection formed. Discovery."
            )
        if harvest_hits > harv_min and self.dopamine > dop_min:
            self.glimmers = int(self.glimmers) + 1
            self.oxytocin = float(self.oxytocin) + 0.2
            return glimmer_text.get("ENTHUSIASM", "")
        return None

    def metabolize(
        self,
        feedback,
        health,
        stamina,
        ros_level=0.0,
        receipt=None,
        social_context=False,
        enzyme_type=None,
        harvest_hits=0,
        stress_mod=1.0,
        circadian_bias=None,
        semantic_signal=None,
    ) -> Dict[str, Any]:
        if isinstance(circadian_bias, dict):
            for k, v in circadian_bias.items():
                attr_name = self._KEY_MAP.get(k) or str(k).lower()
                if isinstance(attr_name, str) and hasattr(self, attr_name):
                    current_val = float(getattr(self, attr_name))
                    drift = float(v) * 0.1
                    setattr(self, attr_name, current_val + drift)
        self._apply_enzyme_reaction(enzyme_type, harvest_hits)
        self._apply_environmental_pressure(
            feedback, health, stamina, ros_level, stress_mod
        )
        if receipt and receipt.waste_generated > 1.0:
            self.cortisol = float(self.cortisol) + 0.1
        if receipt and receipt.status == "ANAEROBIC":
            self.adrenaline = float(self.adrenaline) + 0.2
        if semantic_signal:
            self._apply_semantic_pressure(semantic_signal)
        self._maintain_homeostasis(social_context)
        glimmer_msg = self.check_for_glimmer(feedback, harvest_hits)
        for chem in (
            "dopamine",
            "oxytocin",
            "cortisol",
            "serotonin",
            "adrenaline",
            "melatonin",
        ):
            setattr(self, chem, self._clamp(getattr(self, chem)))
        state = self.get_state()
        if glimmer_msg:
            state["glimmer_msg"] = glimmer_msg
        return state

    def get_state(self) -> Dict[str, Any]:
        return {
            "DOP": round(self.dopamine, 2),
            "OXY": round(self.oxytocin, 2),
            "COR": round(self.cortisol, 2),
            "SER": round(self.serotonin, 2),
            "ADR": round(self.adrenaline, 2),
            "MEL": round(self.melatonin, 2),
        }


class SemanticEndocrinologist:
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.last_topics = deque(maxlen=3)

    def assess(self, clean_words: List[str], physics: Any) -> SemanticSignal:
        if not clean_words:
            return SemanticSignal()
        graph_ref = getattr(self.mem, "graph", {})
        cortical_set = set(getattr(self.mem, "cortical_stack", []))
        word_count = len(clean_words)
        novel_count = 0
        hits = 0
        for w in clean_words:
            if graph_ref and w in graph_ref:
                hits += 1
            elif len(w) > 4 and w not in cortical_set:
                novel_count += 1
        novelty_score = min(1.0, novel_count / word_count)
        resonance_score = min(1.0, hits / word_count) if graph_ref else 0.0
        valence_score = 0.0
        if self.lex and hasattr(self.lex, "get_valence"):
            valence_score = self.lex.get_valence(clean_words)
        coherence_score = getattr(physics, "kappa", 0.5)
        return SemanticSignal(
            novelty=novelty_score,
            resonance=resonance_score,
            valence=valence_score,
            coherence=coherence_score,
        )
