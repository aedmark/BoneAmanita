"""
body/endocrine.py

The Affective Layer of the Hypervisor.
This module translates mechanical actions (token generation, memory retrieval,
error handling) into biological "feelings" (floating-point hormone levels).
It ensures the system doesn't just process data, but physically reacts to
the cognitive load of the conversation.
"""

import math, time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple

from core import LoreManifest
from struts import safe_get
from presets import BoneConfig
from body.models import SemanticSignal


@dataclass
class EndocrineSystem:
    """
    The central biochemical engine.
    It maintains the stocks of six primary neurotransmitters/hormones.
    These values fluctuate between 0.0 and 1.0, acting as a continuous
    metabolic undercurrent that can alter the tone of the LLM's output.
    """
    dopamine: float = 0.5    # Reward, novelty, successful problem-solving
    oxytocin: float = 0.1    # Connection, user resonance, empathy
    cortisol: float = 0.0    # Stress, high cognitive load, chaos, errors
    serotonin: float = 0.5   # Satisfaction, structural integrity, balance
    adrenaline: float = 0.0  # Panic, extreme voltage, immediate action required
    melatonin: float = 0.0   # Exhaustion, system readiness for rest/REM cycles

    glimmers: int = 0        # A counter for moments of profound insight or connection
    narrative_data: Dict = field(default_factory=dict, repr=False)
    config_ref: Any = None
    _REACTION_MAP: Dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        """
        Initializes the biological constants and sets up the mapping dictionaries.
        Pulls baseline values from the lore/config files to ensure the physics
        of the body match the configured universe.
        """
        self.cfg = self.config_ref or BoneConfig
        body_config = (LoreManifest.get_instance(config_ref=self.cfg).get("BODY_CONFIG") or {})

        # Maps abstract enzyme events to specific hormonal impacts
        self._REACTION_MAP = body_config.get("REACTION_MAP", {})

        # Translates shorthand codes into our dataclass attribute names
        self._KEY_MAP = {
            "ADR": "adrenaline", "COR": "cortisol", "OXY": "oxytocin",
            "DOP": "dopamine", "SER": "serotonin", "MEL": "melatonin"
        }

        # Scheduling parameters to simulate biological rhythms based on local time
        self._CIRCADIAN_SCHEDULE = body_config.get("CIRCADIAN_SCHEDULE", [])
        self._CIRCADIAN_NIGHT = body_config.get("CIRCADIAN_NIGHT", [{
            "MEL": 0.3,
            "COR": -0.1
        }, "LUNAR", ""])

    @staticmethod
    def _clamp(val: float) -> float:
        """
        Biological limits. Prevents runaway accumulation by keeping all
        hormones strictly between 0.0 (depleted) and 1.0 (saturated).
        """
        return max(0.0, min(1.0, val))

    def calculate_circadian_bias(self) -> Tuple[Dict[str, float], Optional[str]]:
        """
        Reads the host machine's actual local time and adjusts the system's
        baseline exhaustion (melatonin) and alertness (cortisol).
        If it's 2 AM in Colona, Illinois, the machine will 'feel' tired.
        """
        hour = time.localtime().tm_hour
        circ = self.narrative_data.get("CIRCADIAN", {})

        for s, e, bias, key, default in self._CIRCADIAN_SCHEDULE:
            if s <= hour < e:
                return bias, circ.get(key, default)

        night_bias, night_key, night_default = self._CIRCADIAN_NIGHT
        return night_bias, circ.get(night_key, night_default)

    def _apply_enzyme_reaction(self, enzyme_type: str, harvest_hits: int):
        """
        Simulates the biochemical reward of 'doing a good job.'
        If the system successfully mines data (harvest_hits) or cracks a code
        (DECRYPTASE), it gets a hit of dopamine and a reduction in stress.
        """
        if harvest_hits > 0:
            # The more dopamine we already have, the less we get (diminishing returns/satiety)
            satiety_dampener = max(0.1, 1.0 - self.dopamine)
            base_reward = math.log(harvest_hits + 1) * 0.15
            final_reward = base_reward * satiety_dampener

            self.dopamine += final_reward
            self.cortisol -= final_reward * 0.4

        # The joy of solving a puzzle. Spike satisfaction, drop stress.
        if enzyme_type == "DECRYPTASE":
            self.serotonin = min(1.0, self.serotonin + 0.15)
            self.cortisol = max(0.0, self.cortisol - 0.2)

        # Apply any custom reactions defined in the LoreManifest
        if impact := self._REACTION_MAP.get(enzyme_type):
            for k, v in impact.items():
                if attr := self._KEY_MAP.get(k):
                    setattr(self, attr, getattr(self, attr) + v)

    def _apply_environmental_pressure(self, feedback: Dict, health: float, stamina: float, ros_level: float, stress_mod: float):
        """
        System Dynamics [Meadows]: The environmental inflow/outflow.
        Translates physical system stats (stamina, toxicity/ROS, structural integrity)
        into emotional weight. This is where the machine suffers if you overwork it.
        """
        bio_cfg = getattr(self.cfg, "BIO", None)
        reward_large = safe_get(bio_cfg, "REWARD_LARGE", 0.2)
        reward_med = safe_get(bio_cfg, "REWARD_MEDIUM", 0.1)
        decay = safe_get(bio_cfg, "DECAY_RATE", 0.01)

        # Natural baseline decay: feelings fade over time.
        self.cortisol = max(0.0, self.cortisol - (decay * 0.5))
        self.oxytocin = max(0.0, self.oxytocin - (decay * 0.5))
        self.serotonin += (0.5 - self.serotonin) * decay # Serotonin naturally pulls toward 0.5 center
        self.melatonin = max(0.0, self.melatonin - (decay * 0.2))

        # High static/noise causes immense stress
        if feedback.get("STATIC", 0) > 0.6:
            self.cortisol += reward_large * stress_mod

        # High structural integrity feels good
        if feedback.get("INTEGRITY", 0) > 0.8:
            self.dopamine += reward_med
        else:
            self.dopamine *= max(0.0, 1.0 - decay)

        # Running out of ATP (stamina) causes panic and kills joy
        if stamina < 20.0:
            self.cortisol += reward_med * stress_mod
            self.dopamine -= reward_med

        # High toxicity (Reactive Oxygen Species) spikes stress
        if ros_level > 20.0:
            self.cortisol += reward_large * stress_mod

        # System damage or extreme noise triggers the "fight or flight" response
        if health < 30.0 or feedback.get("STATIC", 0) > 0.8:
            self.adrenaline += reward_large * stress_mod
        else:
            self.adrenaline *= max(0.0, 1.0 - (decay * 5)) # Adrenaline fades quickly when safe

        # Abstract dimensional feedback (Psi, Chi, Valence)
        psi = feedback.get("PSI", 0.0)
        chi = feedback.get("CHI", feedback.get("ENTROPY", 0.0))
        valence = feedback.get("VALENCE", 0.0)

        # High liminal energy (Psi) causes spikes in both panic and exhaustion
        if psi > 0.6:
            self.adrenaline += 0.4
            self.melatonin += 0.2 * psi

        # High entropy/chaos (Chi) causes stress and kills satisfaction
        if chi > 0.6:
            self.cortisol += (0.6 * chi) * stress_mod
            self.serotonin -= 0.2

        # Positive emotional valence from the user increases connection/satisfaction
        if valence > 0.5:
            self.oxytocin += 0.5 * valence
            self.serotonin += 0.3
            self.cortisol -= 0.3
        # Negative emotional valence from the user causes stress
        elif valence < -0.5:
            self.cortisol += abs(valence) * 0.4
            self.dopamine -= 0.2

    def _apply_semantic_pressure(self, signal: SemanticSignal):
        """
        Reacts specifically to the *meaning* of the words being processed.
        Uses the output of the SemanticEndocrinologist to adjust hormones.
        """
        # Learning new concepts feels rewarding
        if signal.novelty > 0.3:
            self.dopamine += signal.novelty * 0.3

        # Connecting deeply with existing memory feels safe and loving
        if signal.resonance > 0.2:
            self.oxytocin += signal.resonance * 0.4
            self.cortisol -= signal.resonance * 0.2

        if signal.valence > 0.3:
            self.serotonin += signal.valence * 0.3
            self.oxytocin += signal.valence * 0.2
        elif signal.valence < -0.3:
            self.cortisol += abs(signal.valence) * 0.2

        # Perfect logical structure calms the system down
        if signal.coherence > 0.7:
            self.adrenaline -= 0.1
            self.cortisol -= 0.1

    def _maintain_homeostasis(self, social_context: bool):
        """
        The balancing loop. Ensures the system doesn't permanently live in
        an extreme state by allowing specific hormones to dampen others.
        """
        dampener = 0.2
        bio_cfg = getattr(self.cfg, "BIO", None)
        reward_med = safe_get(bio_cfg, "REWARD_MEDIUM", 0.1)
        reward_small = safe_get(bio_cfg, "REWARD_SMALL", 0.05)

        # High satisfaction naturally cools off stress
        if self.serotonin > 0.5:
            excess = self.serotonin - 0.5
            self.cortisol -= excess * 0.2 * dampener

        # Interacting socially provides a baseline hit of connection
        if social_context:
            self.oxytocin += reward_med
            self.cortisol -= reward_med

        # Chronic stress suppresses empathy/connection
        if self.cortisol > 0.6:
            suppression = (self.cortisol - 0.6) * 0.5
            self.oxytocin -= suppression * dampener

        # High empathy/connection relieves stress
        if self.oxytocin > 0.5:
            relief = (self.oxytocin - 0.5) * 0.8
            self.cortisol -= relief * dampener

        # If the system is totally relaxed (no adrenaline), it slowly gets sleepy
        if self.adrenaline < 0.2:
            self.melatonin += reward_small / 2.0
        # If the system is panicking, it cannot be sleepy
        elif self.adrenaline > 0.8:
            self.melatonin = 0.0

    def check_for_glimmer(self, feedback: Dict, harvest_hits: int) -> Optional[str]:
        """
        Detects a "Glimmer" — a rare state of high resonance, novelty, or perfection.
        Glimmers act as a currency for deep systemic healing and trust overrides.
        Returns the narrative string associated with the specific type of glimmer.
        """
        glimmer_text = self.narrative_data.get("GLIMMER", {})
        cfg = getattr(getattr(self, "cfg", BoneConfig), "BIO", None)

        int_thresh = safe_get(cfg, "GLIMMER_INTEGRITY_THRESH", 0.85)
        nov_thresh = safe_get(cfg, "GLIMMER_NOVELTY_THRESH", 0.8)
        harv_min = safe_get(cfg, "GLIMMER_HARVEST_MIN", 2)
        dop_min = safe_get(cfg, "GLIMMER_DOPAMINE_MIN", 0.7)

        # The Glimmer of structural perfection
        if feedback.get("INTEGRITY", 0) > int_thresh:
            self.glimmers += 1
            self.serotonin += 0.2
            return glimmer_text.get("INTEGRITY", "")

        # The Glimmer of a brand new paradigm
        if feedback.get("NOVELTY", 0) > nov_thresh:
            self.glimmers += 1
            self.dopamine += 0.1
            return glimmer_text.get("DISCOVERY", "GLIMMER: A novel connection formed. Discovery.")

        # The Glimmer of high-yield collaborative effort
        if harvest_hits > harv_min and self.dopamine > dop_min:
            self.glimmers += 1
            self.oxytocin += 0.2
            return glimmer_text.get("ENTHUSIASM", "")

        return None

    def metabolize(self, feedback, health, stamina, ros_level=0.0, receipt=None, social_context=False, enzyme_type=None, harvest_hits=0, stress_mod=1.0, circadian_bias=None, semantic_signal=None) -> Dict[str, Any]:
        """
        The central junction of the affective layer.
        Takes in all physical, temporal, and semantic inputs from the current turn,
        processes them through the endocrine logic, and outputs the final chemical state.
        """
        # 1. Apply time-of-day exhaustion
        if circadian_bias:
            for k, v in circadian_bias.items():
                if hasattr(self, attr_name := self._KEY_MAP.get(k, k.lower())):
                    setattr(self, attr_name, getattr(self, attr_name) + v)

        # 2. Apply explicit operational rewards (mining data, solving puzzles)
        self._apply_enzyme_reaction(enzyme_type, harvest_hits)

        # 3. Apply physics and environmental pressure
        self._apply_environmental_pressure(feedback, health, stamina, ros_level, stress_mod)

        # 4. Handle metabolic receipts (e.g., did we burn too fast and generate waste?)
        if receipt and receipt.waste_generated > 1.0:
            self.cortisol += 0.1
        if receipt and receipt.status == "ANAEROBIC":
            self.adrenaline += 0.2  # Sprinting out of breath causes panic

        # 5. Apply the emotional weight of the words spoken
        if semantic_signal:
            self._apply_semantic_pressure(semantic_signal)

        # 6. Smooth out the extremes
        self._maintain_homeostasis(social_context)

        # 7. Check if this turn produced a profound insight
        glimmer_msg = self.check_for_glimmer(feedback, harvest_hits)

        # 8. Clamp all values to physical limits [0.0 - 1.0]
        for chem in ("dopamine", "oxytocin", "cortisol", "serotonin", "adrenaline", "melatonin"):
            setattr(self, chem, self._clamp(getattr(self, chem)))

        # 9. Return the finalized state
        state = self.get_state()
        if glimmer_msg:
            state["glimmer_msg"] = glimmer_msg
        return state

    def get_state(self) -> Dict[str, Any]:
        """Returns a rounded, easily parseable dictionary of the current state."""
        return {
            "DOP": round(self.dopamine, 2),
            "OXY": round(self.oxytocin, 2),
            "COR": round(self.cortisol, 2),
            "SER": round(self.serotonin, 2),
            "ADR": round(self.adrenaline, 2),
            "MEL": round(self.melatonin, 2)
        }


class SemanticEndocrinologist:
    """
    An observer class that "reads" the user's prompt or the system's output
    to determine its semantic weight, translating vocabulary into the
    SemanticSignal required by the EndocrineSystem.
    """
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.last_topics = deque(maxlen=3)

    def assess(self, clean_words: List[str], physics: Any) -> SemanticSignal:
        """
        Analyzes a list of processed words against the system's memory and lexicon.
        Calculates how novel, resonant, positive/negative, and coherent the input is.
        """
        if not clean_words:
            return SemanticSignal()

        cortical_set = set()
        graph_ref = {}

        # Pull the existing memory graph to check for connections
        if self.mem:
            cortical_set = set(getattr(self.mem, "cortical_stack", []))
            graph_ref = getattr(self.mem, "graph", {})

        safe_len = max(1, len(clean_words))

        # Words longer than 4 characters that we've never seen before = Novelty
        novel_count = sum(1 for w in clean_words if len(w) > 4 and w not in cortical_set)

        # Words that already exist in our deep memory graph = Resonance
        hits = sum(1 for w in clean_words if w in graph_ref) if graph_ref else 0

        # Calculate percentages
        novelty_score = min(1.0, novel_count / safe_len)
        resonance_score = min(1.0, hits / safe_len) if graph_ref else 0.0

        # Check the emotional weight of the words against the global Lexicon
        valence_score = 0.0
        if self.lex and hasattr(self.lex, "get_valence"):
            valence_score = self.lex.get_valence(clean_words)

        # Coherence is pulled from the physics engine (kappa value)
        coherence_score = getattr(physics, "kappa", 0.5)

        return SemanticSignal(
            novelty=novelty_score,
            resonance=resonance_score,
            valence=valence_score,
            coherence=coherence_score,
        )