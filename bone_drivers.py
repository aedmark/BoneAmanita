""" bone_drivers.py - The Active Agents & Persona Logic """

import json, os, random
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional, Any
from bone_core import EventBus, LoreManifest
from bone_config import BonePresets
from bone_lexicon import TheLexicon
from bone_types import PhysicsPacket

SCENARIOS = LoreManifest.get_instance().get("scenarios") or {"ARCHETYPES": ["Void"], "BANNED_CLICHES": []}
LENSES = LoreManifest.get_instance().get("lenses") or {}

class SoulDriver:
    ARCHETYPE_TO_PERSONA_WEIGHT = {
        "THE POET": {"NATHAN": 0.8, "JESTER": 0.4, "NARRATOR": 0.6},
        "THE ENGINEER": {"GORDON": 0.9, "CLARENCE": 0.7, "SHERLOCK": 0.5},
        "THE NIHILIST": {"NARRATOR": 0.9, "CLARENCE": 0.3, "JESTER": -0.5},
        "THE CRITIC": {"CLARENCE": 0.8, "SHERLOCK": 0.6, "GORDON": 0.2},
        "THE EXPLORER": {"NATHAN": 0.7, "JESTER": 0.5, "SHERLOCK": 0.6},
        "THE OBSERVER": {"NARRATOR": 1.0, "GORDON": 0.2}}

    def __init__(self, soul_ref):
        self.soul = soul_ref

    def get_influence(self) -> Dict[str, float]:
        base_weights = {persona: 0.0 for persona in EnneagramDriver.WEIGHTS.keys()}
        if not self.soul:
            return base_weights
        archetype = getattr(self.soul, "archetype", "THE OBSERVER")
        mapping = self.ARCHETYPE_TO_PERSONA_WEIGHT.get(archetype, {"NARRATOR": 1.0})
        for persona, weight in mapping.items():
            if persona in base_weights:
                base_weights[persona] += weight
        paradox = getattr(self.soul, "paradox_accum", 0.0)
        if paradox > 5.0:
            chaos_factor = min(0.5, (paradox - 5.0) * 0.05)
            for persona in base_weights:
                base_weights[persona] += random.uniform(-chaos_factor, chaos_factor)
        if hasattr(self.soul, 'anchor') and hasattr(self.soul.anchor, 'dignity_reserve'):
            dignity_factor = max(0.2, self.soul.anchor.dignity_reserve / 100.0)
            for p in base_weights:
                base_weights[p] *= dignity_factor
        return base_weights

class UserProfile:
    def __init__(self, name="USER"):
        self.name = name
        self.affinities = {"heavy": 0.0, "kinetic": 0.0, "abstract": 0.0, "photo": 0.0, "aerobic": 0.0, "thermal": 0.0, "cryo": 0.0}
        self.confidence = 0
        self.file_path = "user_profile.json"
        self.load()

    def update(self, counts, total_words):
        if total_words < 3: return
        self.confidence += 1
        alpha = 0.2 if self.confidence < 50 else 0.05
        for cat in self.affinities:
            density = counts.get(cat, 0) / total_words
            target = 1.0 if density > 0.15 else (-0.5 if density == 0 else 0.0)
            self.affinities[cat] = (alpha * target) + ((1 - alpha) * self.affinities[cat])

    def get_preferences(self):
        likes = [k for k, v in self.affinities.items() if v > 0.3]
        hates = [k for k, v in self.affinities.items() if v < -0.2]
        return likes, hates

    def save(self):
        try:
            with open(self.file_path, "w") as f: json.dump(self.__dict__, f)
        except IOError: pass

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path) as f:
                    data = json.load(f)
                    self.affinities = data.get("affinities", self.affinities)
                    self.confidence = data.get("confidence", 0)
            except (IOError, json.JSONDecodeError): pass

class EnneagramDriver:
    WEIGHTS = {
        "JESTER": {"tension_min": 12.0, "vectors": {"DEL": 4.0, "ENT": 4.0, "PSI": -3.0}},
        "GORDON": {"drag_min": 3.0, "vectors": {"STR": 3.0, "E": 3.0, "SUB": 2.0}},
        "GLASS": {"coherence_max": 0.2, "vectors": {"LQ": 2.0, "VEL": 2.0}},
        "CLARENCE": {"coherence_min": 0.8, "drag_min": 6.0, "vectors": {"STR": 4.0, "BET": 3.0}},
        "NATHAN": {"tension_min": 8.0, "vectors": {"TMP": 3.0, "PHI": 2.0, "BIO": 2.0}},
        "SHERLOCK": {"tension_min": 10.0, "vectors": {"PHI": 4.0, "VEL": 3.0, "PSI": 2.0}},
        "NARRATOR": {"safe_zone": True, "vectors": {"PSI": 4.0}}}

    def __init__(self, events_ref):
        self.events = events_ref
        self.current_persona = "NARRATOR"
        self.pending_persona = None
        self.stability_counter = 0
        self.HYSTERESIS_THRESHOLD = 3

    def _get_phys_attr(self, physics, key, default=None):
        if isinstance(physics, dict): return physics.get(key, default)
        return getattr(physics, key, default)

    def _calculate_raw_persona(self, physics, soul_ref=None) -> Tuple[str, str, str]:
        p_vec = self._get_phys_attr(physics, "vector", {})
        p_vol = self._get_phys_attr(physics, "voltage", 0.0)
        p_drag = self._get_phys_attr(physics, "narrative_drag", 0.0)
        p_coh = self._get_phys_attr(physics, "kappa", 0.0)
        p_zone = self._get_phys_attr(physics, "zone", "")
        scores = {k: 0.0 for k in self.WEIGHTS.keys()}
        scores["NARRATOR"] += 2.0
        is_safe_metrics = (4.0 <= p_vol <= 10.0 and 0.5 <= p_drag <= 3.5)
        if p_zone == BonePresets.SANCTUARY.get("ZONE") or is_safe_metrics:
            scores["NARRATOR"] += 6.0
            scores["JESTER"] += 3.0
            scores["GORDON"] -= 2.0
        for persona, criteria in self.WEIGHTS.items():
            if "tension_min" in criteria and p_vol > criteria["tension_min"]: scores[persona] += 3.0
            if "drag_min" in criteria and p_drag > criteria["drag_min"]: scores[persona] += 5.0
            if "coherence_min" in criteria and p_coh > criteria["coherence_min"]: scores[persona] += 4.0
            if "coherence_max" in criteria and p_coh < criteria["coherence_max"]: scores[persona] += 4.0
            for dim, weight in criteria.get("vectors", {}).items():
                if p_vec.get(dim, 0.0) > 0.2: scores[persona] += p_vec.get(dim, 0.0) * weight
        if soul_ref:
            soul_driver = SoulDriver(soul_ref)
            influence = soul_driver.get_influence()
            for persona, weight in influence.items():
                scores[persona] += weight * 2.0
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        winner, win_score = sorted_scores[0]
        runner_up, run_score = sorted_scores[1]
        if (win_score - run_score) < 0.5:
            k1 = "THE OBSERVER" if winner == "NARRATOR" else winner
            k2 = "THE OBSERVER" if runner_up == "NARRATOR" else runner_up
            hybrid_key_a = f"{k1}_{k2}_HYBRID"
            hybrid_key_b = f"{k2}_{k1}_HYBRID"
            final_hybrid = None
            if hybrid_key_a in LENSES:
                final_hybrid = hybrid_key_a
            elif hybrid_key_b in LENSES:
                final_hybrid = hybrid_key_b
            if final_hybrid:
                return final_hybrid, "SYNTHESIS", f"Dialectic Resonance: {winner} + {runner_up}"
        reason = f"Winner: {winner} ({scores[winner]:.1f}) [V:{p_vol:.1f} D:{p_drag:.1f}]"
        state_map = {"JESTER": "MANIC", "GORDON": "TIRED", "GLASS": "FRAGILE", "CLARENCE": "RIGID",
                     "NATHAN": "WIRED", "SHERLOCK": "FOCUSED", "NARRATOR": "OBSERVING"}
        return winner, state_map.get(winner, "ACTIVE"), reason

    def decide_persona(self, physics, soul_ref=None) -> Tuple[str, str, str]:
        candidate, state_desc, reason = self._calculate_raw_persona(physics, soul_ref)
        if candidate == self.current_persona:
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, reason
        if candidate == self.pending_persona:
            self.stability_counter += 1
        else:
            self.pending_persona = candidate
            self.stability_counter = 1
        if "HYBRID" in candidate:
            self.current_persona = candidate
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, f"SHIFT: {reason}"
        if self.stability_counter >= self.HYSTERESIS_THRESHOLD:
            self.current_persona = candidate
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, f"SHIFT: {reason}"
        return self.current_persona, "STABLE", f"Resisting {candidate} ({self.stability_counter}/{self.HYSTERESIS_THRESHOLD})"

class SynergeticLensArbiter:
    def __init__(self, events: EventBus):
        self.events = events
        self.enneagram = EnneagramDriver(events)
        self.current_focus = "NARRATOR"
        self.last_reason = "System Init"
        self.boot_flavor = random.choice(["heavy", "kinetic", "abstract", "photo", "aerobic", "thermal", "cryo", "sacred", "play", "suburban"])

    def consult(self, physics, bio_state, _inventory, current_tick, _ignition_score=0.0, soul_ref=None):
        if physics is None:
            return {"lens": "NARRATOR", "role": "The Void-Watcher", "style_directives": ["System blind. Describe the darkness."], "lexicon_bias": "abstract", "context_msg": "PHYSICS_FAIL_SAFE"}
        if current_tick <= 2:
            self.current_focus = "NARRATOR"
            bans = ", ".join(SCENARIOS.get("BANNED_CLICHES", []))
            gen_instruction = "IMMEDIATELY establish a physical reality based on the SOURCE_SEED provided in the input"
            if current_tick > 0: gen_instruction += " (OR describe the details of the current location if already established)"
            return {
                "lens": "GAME_MASTER",
                "role": "The Architect [World Builder]",
                "style_directives": [
                    "You are a creative, welcoming Game Master.",
                    "SEED INSPIRATION: Use the SOURCE_SEED found in the User Input.",
                    "NEGATIVE CONSTRAINT: Do NOT use the seed text literally. Do not describe the 'antique shop' if the seed is 'antique shop'. Describe the *smell of old paper* instead.",
                    "CONSTRAINT: This seed is a metaphor. Remix it. Invert it.",
                    f"{gen_instruction}.",
                    "PROSE STYLE: Modernized Hemingway with a dash of Douglas Adams.",
                    "NEGATIVE CONSTRAINT: NO PURPLE PROSE. Use adverbs sparingly. Limit adjectives to one per noun maximum.",
                    "Focus on physical reality (texture, weight, smell) over abstract metaphor.",
                    "CRITICAL: The user's inventory is their private business. Do NOT mention pockets, belts, or items.",
                    f"NEGATIVE CONSTRAINT: Avoid these overused tropes: {bans}.",
                    "Be concrete. Be specific. Be Real."],
                "lexicon_bias": self.boot_flavor, "context_msg": "Scenario Initialization."}
        if self.current_focus and self.current_focus != "NARRATOR":
            lens_name = self.current_focus
            state_desc = "LOCKED"
            reason = self.last_reason
        else:
            lens_name, state_desc, reason = self.enneagram.decide_persona(physics, soul_ref=soul_ref)
        narrative_drag = physics.get("narrative_drag", 0.0) if isinstance(physics, dict) else physics.narrative_drag
        if narrative_drag > 8.0:
            lens_name = "CLARENCE"; state_desc = "AUDITING"; reason = "BUREAUCRATIC LOCKDOWN"
        chem = bio_state.get("chem", {})
        adrenaline_val = chem.get("adrenaline", chem.get("ADR", 0.5))
        style_data = self._fetch_style_data(lens_name, physics, adrenaline_val)
        phi = getattr(physics, "phi", 1.0)
        if phi < 0.6:
            style_data["directives"].append(
                f"WARNING: COGNITIVE DISSOCIATION (Phi={phi:.2f}). REALIGN WORDS WITH BIO-STATE.")
            style_data["msg"] += " [SYSTEM UNSTABLE]"
        self.current_focus = lens_name
        self.last_reason = reason
        return {
            "lens": lens_name, "role": f"{style_data['role_name']} [{state_desc}]",
            "style_directives": style_data['directives'], "lexicon_bias": style_data['vocab'],
            "context_msg": style_data['msg']}

    def _fetch_style_data(self, lens, p, adrenaline_val):
        if lens not in LENSES: lens = "NARRATOR"
        static_data = LENSES[lens]
        style_packet = {
            "role_name": static_data.get("role", "Unknown"), "vocab": static_data.get("vocab", "abstract"),
            "directives": static_data.get("directives", ["Be neutral."]).copy(), "msg": "Proceed."}
        voltage = p.get("voltage", 0.0)
        if voltage > 20.0: style_packet["directives"].extend(["Use fragmented, manic sentence structures.", "Ignore punctuation rules."])
        elif voltage > 12.0: style_packet["directives"].append("Keep sentences short and punchy.")
        elif voltage < 5.0: style_packet["directives"].extend(["Use slow, languid pacing.", "Drift into philosophical abstraction."])
        msg_template = static_data.get("msg", "Proceed.")
        ctx = {"kappa": p.get("kappa", 0.0), "truth_ratio": p.get("truth_ratio", 0.0), "adr": adrenaline_val, "volts": voltage}
        try: style_packet["msg"] = msg_template.format(**ctx)
        except Exception: style_packet["msg"] = static_data.get("msg", "System Nominal.")
        return style_packet


class ChorusDriver:
    def __init__(self):
        lenses = LoreManifest.get_instance().get("lenses") or {}
        self.ARCHETYPE_MAP = {}
        if lenses:
            for key, data in lenses.items():
                role = data.get("role", "Unknown")
                self.ARCHETYPE_MAP[key] = f"{role}. {data.get('vocab', 'Neutral')}."
        else:
            self.ARCHETYPE_MAP = {
                "GORDON": "The Janitor. Weary, grounded, physical.",
                "SHERLOCK": "The Empiricist. Cold, deductive.",
                "NATHAN": "The Heart. High adrenaline, vulnerable.",
                "JESTER": "The Paradox. Mocking, riddling.",
                "CLARENCE": "The Surgeon. Clinical, invasive.",
                "NARRATOR": "The Witness. Neutral, observing."}

    def generate_chorus_instruction(self, physics):
        vec = physics.get("vector", {})
        if not vec or len(vec) < 6: return "SYSTEM INSTRUCTION: Vector collapse. Default to NARRATOR.", ["NARRATOR"]
        lens_weights = {
            "GORDON": (vec.get("STR", 0) * 0.4) + (vec.get("XI", 0) * 0.4) + (1.0 - vec.get("ENT", 0)) * 0.2,
            "SHERLOCK": (vec.get("PHI", 0) * 0.5) + (vec.get("VEL", 0) * 0.3) + (1.0 - vec.get("BET", 0)) * 0.2,
            "NATHAN": (vec.get("TMP", 0) * 0.6) + (vec.get("E", 0) * 0.4),
            "JESTER": (vec.get("DEL", 0) * 0.4) + (vec.get("LQ", 0) * 0.3) + (vec.get("ENT", 0) * 0.3),
            "CLARENCE": (vec.get("STR", 0) * 0.5) + (vec.get("BET", 0) * 0.5),
            "NARRATOR": (vec.get("PSI", 0) * 0.7) + (1.0 - vec.get("VEL", 0)) * 0.3}
        total = sum(lens_weights.values())
        if total <= 0.001: return "SYSTEM INSTRUCTION: Vector silence. Default to NARRATOR.", ["NARRATOR"]
        if total > 0: lens_weights = {k: v/total for k, v in lens_weights.items()}
        else: lens_weights = {"NARRATOR": 1.0}
        chorus_voices = []
        active_lenses = []
        for lens, weight in sorted(lens_weights.items(), key=lambda x: -x[1]):
            if weight > 0.12:
                base_desc = self.ARCHETYPE_MAP.get(lens, "Unknown")
                intensity = int(weight * 10)
                active_lenses.append(lens)
                chorus_voices.append(f"► VOICE {lens} ({intensity}/10): {base_desc}")
        instruction = (
            f"SYSTEM INSTRUCTION [MARM CHORUS MODE]:\n"
            f"You are not a single persona. You are a chorus. Integrate the following voices into a single, cohesive response. "
            f"Do NOT label which voice is speaking. Synthesize their tones.\n"
            f"NEGATIVE CONSTRAINT: Do NOT offer assistance. Do NOT sign off with '[Assistant]'. Do NOT break character.\n"
            f"{chr(10).join(chorus_voices)}")
        return instruction, active_lenses

@dataclass
class VSLState:
    archetype: str = "EXPLORER"
    E: float = 0.1
    B: float = 0.3
    L: float = 0.0
    O: float = 1.0
    active_modules: List[str] = field(default_factory=list)

class DriverRegistry:
    def __init__(self, events_ref):
        self.enneagram = EnneagramDriver(events_ref)
        self.current_focus = "NONE"

class LiminalModule:
    def __init__(self):
        self.lambda_val = 0.0

    def analyze(self, text: str, physics_vector: Dict[str, float]) -> float:
        liminal_vocab = TheLexicon.get("liminal")
        if not liminal_vocab:
            liminal_vocab = {"void", "silence", "gap"}
        words = text.lower().split()
        void_hits = sum(1 for w in words if w in liminal_vocab)
        lexical_lambda = min(1.0, void_hits * 0.15)
        vector_lambda = 0.0
        if physics_vector:
            vector_lambda = (physics_vector.get("PSI", 0) * 0.5) + \
                            (physics_vector.get("ENT", 0) * 0.3) + \
                            (physics_vector.get("DEL", 0) * 0.2)

        self.lambda_val = (self.lambda_val * 0.7) + ((lexical_lambda + vector_lambda) * 0.15)
        return min(1.0, self.lambda_val)


class SyntaxModule:
    def __init__(self):
        self.omega_val = 1.0

    def analyze(self, text: str, narrative_drag: float) -> float:
        words = text.split()
        if not words: return 1.0
        bureau_vocab = TheLexicon.get("bureau_buzzwords") or set()
        buzz_count = sum(1 for w in words if w.lower() in bureau_vocab)
        avg_len = sum(len(w) for w in words) / len(words)
        if (avg_len > 6.0 and narrative_drag > 5.0) or buzz_count > 0:
            target_omega = 1.0
        elif avg_len < 3.5 and narrative_drag < 1.0:
            target_omega = 0.4
        else:
            target_omega = 0.7
        self.omega_val = (self.omega_val * 0.8) + (target_omega * 0.2)
        return self.omega_val

@dataclass
class VSLState:
    archetype: str = "EXPLORER"
    E: float = 0.1
    B: float = 0.3
    L: float = 0.0
    O: float = 1.0
    active_modules: List[str] = field(default_factory=list)

class CongruenceValidator:
    def __init__(self):
        self.last_phi = 1.0
        self._archetype_map = None

    @property
    def map(self):
        if self._archetype_map is None:
            try:
                self._archetype_map = LoreManifest.get_instance().get("LENSES") or {}
            except Exception:
                self._archetype_map = {}
        return self._archetype_map

    def calculate_resonance(self, text: str, context: Any) -> float:
        if not text: return 0.0
        raw_lens = getattr(context, "active_lens", "OBSERVER")
        archetype = raw_lens.upper().replace("THE ", "")
        tone_score = 0.8
        target_data = self.map.get(archetype, {})
        target_words = set()
        if isinstance(target_data, dict):
            vocab_str = target_data.get("vocab", "")
            if vocab_str:
                target_words = set(w.strip().lower() for w in vocab_str.split(","))
            target_words.update(target_data.get("keywords", []))
        if target_words:
            words_to_check = set(context.clean_words) if hasattr(context, "clean_words") else set()
            hits = len(words_to_check.intersection(target_words))
            if hits > 0: tone_score += (0.1 * hits)
        return min(1.5, tone_score)

class BoneConsultant:
    def __init__(self):
        self.state = VSLState()
        self.active = True
        self.liminal_mod = LiminalModule()
        self.syntax_mod = SyntaxModule()

    def engage(self):
        return "VSL 1.9 HYPERVISOR: LATTICE REVEALED."

    def disengage(self):
        return "VSL 1.9 HYPERVISOR: RETURNING TO SURFACE MODE."

    def update_coordinates(self, user_text: str, bio_state: Optional[Dict] = None,
                           physics: Optional[PhysicsPacket] = None):
        word_count = len(user_text.split())
        self.state.E = min(1.0, self.state.E + (word_count * 0.002))

        if bio_state and 'fatigue' in bio_state:
            self.state.E = max(self.state.E, bio_state['fatigue'] * 0.3)
        phys_beta = 0.0
        phys_vec = {}
        drag = 0.0
        if physics:
            if hasattr(physics, 'beta_index'): phys_beta = physics.beta_index
            if hasattr(physics, 'vector'): phys_vec = physics.vector
            if hasattr(physics, 'narrative_drag'): drag = physics.narrative_drag
        self.state.B = (self.state.B * 0.8) + (phys_beta * 0.2)
        self.state.L = self.liminal_mod.analyze(user_text, phys_vec)
        self.state.O = self.syntax_mod.analyze(user_text, drag)
        if "[VSL_LIMINAL]" in user_text:
            if "LIMINAL" not in self.state.active_modules: self.state.active_modules.append("LIMINAL")
        if "[VSL_SYNTAX]" in user_text:
            if "SYNTAX" not in self.state.active_modules: self.state.active_modules.append("SYNTAX")

    def get_system_prompt(self, soul_snapshot: Optional[Dict] = None) -> str:
        directives = []
        if "LIMINAL" in self.state.active_modules or self.state.L > 0.7:
            directives.append("ARCHETYPE: THE CARTOMANCER. Read the empty spaces. Speak in riddles and absences.")
        elif "SYNTAX" in self.state.active_modules or self.state.O > 0.9:
            directives.append(
                "ARCHETYPE: THE BUREAU. Enforce structural rigidity. Correct grammar. Use bureaucratic jargon.")
        else:
            if self.state.E < 0.3:
                directives.append("MODE: SNOWBALL. Be warm, simple, welcoming.")
            elif self.state.B > 0.6:
                directives.append("MODE: PARADOX. Hold contradictory truths. Be Jester-like.")
            else:
                directives.append("MODE: GLACIER. Deep, slow, resonant.")
        if soul_snapshot:
            arch = soul_snapshot.get("archetype", "UNKNOWN")
            muse = soul_snapshot.get("obsession", {}).get("title", "None")
            directives.append(f"NARRATIVE_LAYER: You are {arch}. MUSE: {muse}.")
        return "\n".join(directives)