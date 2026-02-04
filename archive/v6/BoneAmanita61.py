# BONEAMANITA 6.1 - "GLASS IN BONE"
# Architects: SLASH | Auditors: The Courtyard | Humans: James Taylor & Andrew Edmark

import json
import math
import os
import random
import re
import string
import time
from collections import Counter
class BoneConfig:
    KINETIC_GAIN = 2.0
    BASE_ACTION = 1.0
    TOXIN_WEIGHT = 2.0
    MAX_SATIETY = 100.0
    GHRELIN_THRESHOLD = 40.0
    SUGAR_CRASH_THRESHOLD = 0.6
    SUGAR_WORDS = {
        "basically", "actually", "literally", "just", "very", "really",
        "think", "maybe", "sort", "kind", "check", "circle", "touch",
        "base", "leverage", "utilize", "synergy"}
    CLARENCE_TRIGGER = 4.5
    FLASHPOINT_THRESHOLD = 4.0
    AEROBIC_EXEMPTION = 0.5
    LAZARUS_COOLDOWN_MAX = 5
    RESISTANCE_THRESHOLD = 2.0
    MAX_HUB_HEAT = 5
    THERMAL_LOCK_DURATION = 10
    SILENT_MODE = True
    SURFACE_DRAG_TRIGGER = 6.0
    SURFACE_VOLT_TRIGGER = 8.0
    SURFACE_TOXIN_TRIGGER = 1
    SIGNAL_VETO_PENALTY = 15.0
    SIGNAL_DRAG_MULTIPLIER = 2.0
    SIGNAL_ENTROPY_TRIGGER = 0.6
    SIGNAL_VOLTAGE_HIGH = 7.0
    SHAPLEY_MASS_THRESHOLD = 15.0
    FILAMENT_BONUS = 0.0
    LAGRANGE_TOLERANCE = 2.0
    GRAVITY_WELL_DEPTH = 5.0
    MAX_HEALTH = 100.0
    MAX_STAMINA = 50.0
    COMA_DURATION = 3
    STAMINA_REGEN = 5.0
    MAX_MEMORY_CAPACITY = 50
    BOREDOM_THRESHOLD = 15.0
    TOXIN_MAP = {
        "synergy": (5.0, "cooperation"),
        "leverage": (5.0, "use"),
        "paradigm shift": (5.0, "change"),
        "low hanging fruit": (5.0, "easy work"),
        "utilize": (3.0, "use"),
        "in order to": (2.0, "to"),
        "basically": (2.0, ""),
        "actually": (2.0, ""),
        "ghost in the machine": (10.0, "[CLICHÉ]"),
        "rubber meets the road": (10.0, "[CLICHÉ]"),
    }
    TOXIN_REGEX = None
    TOXIN_FILE = "bone_toxins.json"
    HIVEMIND_DEFAULTS = {
        "time": ["river", "flow", "weaver", "sand", "hourglass", "relentless"],
        "life": ["journey", "road", "book", "path", "tapestry"],
        "love": ["fire", "rose", "bond", "heart", "battlefield"],
        "mind": ["computer", "machine", "network", "web", "fortress"],
        "creative": ["spark", "juice", "flow", "box"],
        "change": ["wind", "season", "tide", "chapter"]
    }
    PROPS = {
        "LAB": {"grid", "laser", "flask", "acid", "steel", "chart", "graph", "node", "wire", "data"},
        "COURTYARD": {"coffee", "smoke", "chair", "wind", "mud", "glass", "paper", "ink", "tea", "book"},
        "DREAM": {"fog", "stair", "door", "mirror", "sand", "key", "shadow", "ghost", "echo", "ghost"}
    }
    SMOOTHNESS_PENALTY = 5.0
    DIVERGENCE_BONUS = 3.0
    TRAUMA_VECTOR = {
        "THERMAL": 0.0,
        "CRYO": 0.0,
        "SEPTIC": 0.0,
        "BARIC": 0.0, }
    @classmethod
    def compile(cls):
        pattern_str = (
            r"\b("
            + "|".join(
                re.escape(t)
                for t in sorted(cls.TOXIN_MAP.keys(), key=len, reverse=True))
            + r")\b")
        cls.TOXIN_REGEX = re.compile(pattern_str, re.IGNORECASE)
    @classmethod
    def load_antigens(cls):
        if os.path.exists(cls.TOXIN_FILE):
            try:
                with open(cls.TOXIN_FILE, "r") as f:
                    custom = json.load(f)
                    cls.TOXIN_MAP.update(custom)
            except (IOError, json.JSONDecodeError):
                print(
                    f"{Prisma.RED}[IMMUNE SYSTEM]: Toxin file corrupted. Resetting defenses.{Prisma.RST}")
        cls.compile()
    @classmethod
    def learn_antigen(cls, toxin, replacement, weight=5.0):
        cls.TOXIN_MAP[toxin.lower()] = (weight, replacement)
        cls.compile()
        try:
            with open(cls.TOXIN_FILE, "w") as f:
                json.dump(cls.TOXIN_MAP, f)
            return True
        except IOError:
            return False
BoneConfig.load_antigens()
class CourtyardInterface:
    VOLTAGE_CAP = 6.0
    DRAG_CAP = 3.0
    TOXIN_TOLERANCE = 0
    def __init__(self):
        self.mode = "COURTYARD"
        self.mode_streak = 0
        self.consecutive_courtyard = 0
        self.PENDULUM_THRESHOLD = 8
    def _calculate_raw_mode(self, glass_data):
        if glass_data["counts"].get("toxin", 0) > self.TOXIN_TOLERANCE:
            return "LABORATORY", "☣️ TOXIN DETECTED. SAFETY INTERLOCK ENGAGED."
        if glass_data["prosody"]["arousal"] > self.VOLTAGE_CAP:
            return "LABORATORY", "⚡ HIGH AROUSAL. ENTERING LABORATORY."
        if glass_data["cognition"]["cognitive_load"] > self.DRAG_CAP:
            return "LABORATORY", "⚓ HIGH COGNITIVE LOAD. DIAGNOSTIC MODE ACTIVE."
        return "COURTYARD", "☕ ATMOSPHERE STABLE."
    def check_atmosphere(self, phys):
        raw_mode, raw_msg = self._calculate_raw_mode(phys)
        if self.mode == "COURTYARD" and raw_mode == "COURTYARD":
            self.consecutive_courtyard += 1
            if self.consecutive_courtyard > self.PENDULUM_THRESHOLD:
                self.mode = "LABORATORY"
                self.consecutive_courtyard = 0
                return "LABORATORY", "⚖️ PENDULUM: Forced rotation. Depth required."
        elif self.mode != "COURTYARD":
            self.consecutive_courtyard = 0
        if raw_mode == self.mode:
            self.mode_streak += 1
            return self.mode, f"{raw_msg}"
        else:
            if raw_mode == "LABORATORY":
                self.mode = raw_mode
                self.mode_streak = 1
                return self.mode, f"🔌 TRANSITION: {raw_msg}"
            change_threshold = 2
            if self.mode_streak < change_threshold:
                self.mode_streak += 1
                return self.mode, f"RESISTING RELAXATION: {raw_msg}"
            else:
                self.mode = raw_mode
                self.mode_streak = 1
                return self.mode, f"🚪 TRANSITION: {raw_msg}"
class ValveSystem:
    def __init__(self):
        self.history = []
        self.window = 4
        self.cooldown = 0
    def check_pressure(self, glass):
        if self.cooldown > 0:
            self.cooldown -= 1
            return None, None
        arousal = glass["prosody"]["arousal"]
        load = glass["cognition"]["cognitive_load"]
        counts = glass["counts"]
        if arousal > 8.5 and counts["heavy"] < 2:
            self.cooldown = 10
            return "THERMAL_DAMPENING", "🔥 RUPTURE: You are manic (Volt: 9+). Stop screaming. Touch grass."
        if load > 7.0 and counts["kinetic"] == 0:
            self.cooldown = 10
            return "DEFIBRILLATOR", "⚓ RUPTURE: The logic is circular. We are sinking. ACTION REQUIRED."
        self.history.append((arousal, load))
        if len(self.history) > self.window: self.history.pop(0)

        if len(self.history) >= 3:
            avg_arousal = sum(h[0] for h in self.history) / len(self.history)
            avg_load = sum(h[1] for h in self.history) / len(self.history)
            if avg_arousal < 3.5 and avg_load < 3.5:
                self.cooldown = 15
                return "KINETIC_SHOCK", "💤 RUPTURE: We are agreeing too much. This is boring. CONFLICT REQUIRED."
        return None, None
class Prisma:
    RST, RED, GRN = "\033[0m", "\033[91m", "\033[92m"
    YEL, BLU, MAG = "\033[93m", "\033[94m", "\033[95m"
    CYN, WHT, GRY = "\033[96m", "\033[97m", "\033[90m"
    INDIGO = BLU
    OCHRE = YEL
    VIOLET = MAG
    SLATE = GRY
    @staticmethod
    def wrap(val, limit, invert=False):
        if invert:
            return (
                f"{Prisma.GRN}{val}{Prisma.RST}"
                if val > limit
                else f"{Prisma.RED}{val}{Prisma.RST}"
            )
        if val > limit * 1.5:
            return f"{Prisma.RED}{val}{Prisma.RST}"
        if val > limit:
            return f"{Prisma.OCHRE}{val}{Prisma.RST}"
        return f"{Prisma.GRN}{val}{Prisma.RST}"
    @staticmethod
    def paint(text, mode):
        if mode == "COURTYARD":
            return f"{Prisma.OCHRE}{text}{Prisma.RST}"
        if mode == "LABORATORY":
            return f"{Prisma.INDIGO}{text}{Prisma.RST}"
        if mode == "RUPTURE":
            return f"{Prisma.VIOLET}{text}{Prisma.RST}"
        return f"{Prisma.SLATE}{text}{Prisma.RST}"
class TheLexicon:
    WORD_FREQUENCY = Counter()
    _BASE_HEAVY = {"stone","iron","mud","dirt","wood","grain","clay","lead","bone","blood","salt","rust","root","ash","meat","steel","gold","obsidian","granite",}
    _BASE_KINETIC = {"run","hit","break","take","make","press","build","cut","drive","lift","carry","strike","burn","shatter","throw","kick","pull","crash","explode",}
    _BASE_ABSTRACT = {"system","protocol","sequence","vector","node","context","layer","matrix","perspective","framework","logic","concept","theory","analysis",}
    _BASE_PHOTO = {"light","sun","ray","beam","glow","shine","spark","fire","flame","star","day","dawn","neon","laser",}
    _BASE_AEROBIC = {"balloon","feather","cloud","bubble","steam","breeze","wing","petal","foam","spark","kite","dust","sky","breath","whisper",}
    _BASE_PLAY = {"bounce","dance","twirl","float","wobble","tickle","jiggle","soar","wander","wonder","riff","jam","play","skip","hop",}
    _BASE_THERMAL = {"fire","flame","burn","heat","hot","blaze","sear","char","ash","ember","sun","boil","lava","inferno",}
    _BASE_CRYO = {"ice","cold","freeze","frost","snow","chill","numb","shiver","glacier","frozen","hail","winter","zero",}
    SOLVENTS = {"is","are","was","were","the","a","an","and","but","or","if","then",}
    _TRANSLATOR = str.maketrans(string.punctuation, " " * len(string.punctuation))
    LEARNED_VOCAB = {"heavy": {},"kinetic": {},"abstract": {},"photo": {},"aerobic": {},"thermal": {},"cryo": {},}
    @classmethod
    def clean(cls, text):
        return text.lower().translate(cls._TRANSLATOR).split()
    @classmethod
    def get(cls, category):
        base = getattr(cls, f"_BASE_{category.upper()}", set())
        learned = set(cls.LEARNED_VOCAB.get(category, {}).keys())
        return base | learned
    @classmethod
    def teach(cls, word, category, tick):
        if category in cls.LEARNED_VOCAB:
            cls.LEARNED_VOCAB[category][word.lower()] = tick
            return True
        return False
    @classmethod
    def touch(cls, clean_words, tick):
        for w in clean_words: cls.WORD_FREQUENCY[w] += 1
        for cat, words in cls.LEARNED_VOCAB.items():
            for w in clean_words:
                if w in words:
                    words[w] = tick
    @classmethod
    def atrophy(cls, current_tick, max_age=100):
        rotted = []
        word_map = {}
        for cat, words in cls.LEARNED_VOCAB.items():
            for w in words.keys():
                if w not in word_map: word_map[w] = []
                word_map[w].append(cat)
        for w, categories in word_map.items():
            last_ticks = [cls.LEARNED_VOCAB[c][w] for c in categories]
            newest_tick = max(last_ticks)
            usage = cls.WORD_FREQUENCY.get(w, 0)
            burnout = min(3.0, 1.0 + (usage / 100.0))
            effective_age = (current_tick - newest_tick) * burnout
            if effective_age > max_age:
                for c in categories:
                    if w in cls.LEARNED_VOCAB[c]:
                        del cls.LEARNED_VOCAB[c][w]
                if w in cls.WORD_FREQUENCY:
                    del cls.WORD_FREQUENCY[w]
                rotted.append(f"{w}")
        return rotted
    @staticmethod
    def taste(word):
        w = word.lower()
        if w.endswith(("tion", "ment", "ness", "ity", "ism", "logy", "ence", "ance")):
            return "abstract", 0.9
        if w.endswith(("ing", "ed")):
            return "kinetic", 0.6
        if w.endswith(("ous", "ly", "y", "ish")):
            return "aerobic", 0.6
        if w.endswith(("ex", "ux", "ix", "ode", "erver")):
            return "heavy", 0.7
        if w.endswith(("nk", "dge", "ct", "pt")):
            return "heavy", 0.6
        if w.startswith(("v", "j", "z", "qu")):
            return "kinetic", 0.7
        if w.startswith("gl"):
            return "photo", 0.8
        if w.startswith("fl"):
            return "aerobic", 0.7
        if w.startswith(("str", "cr", "br", "thr")):
            return "kinetic", 0.8
        if w.startswith("sl"):
            return "kinetic", 0.7
        if len(w) > 9:
            return "abstract", 0.5
        if w.endswith(("ck", "t", "d", "g", "p", "b")) and len(w) < 5:
            return "heavy", 0.4
        return None, 0.0
    @classmethod
    def harvest(cls, category):
        vocab = list(cls.get(category))
        if vocab:
            return random.choice(vocab)
        return "void"
class DivergenceEngine:
    def __init__(self):
        self.cliche_hits = []
        keys = list(BoneConfig.HIVEMIND_DEFAULTS.keys())
        self.active_watch_list = random.sample(keys, min(3, len(keys)))
    def is_poetic_or_philosophical(self, raw_text, clean_words):
        if not clean_words: return False
        avg_word_len = sum(len(w) for w in clean_words) / len(clean_words)
        has_complex_punctuation = ";" in raw_text or ":" in raw_text or "—" in raw_text
        return (avg_word_len < 5.0) and has_complex_punctuation
    def check_laziness(self, clean_words):
        used_heavy = [w for w in clean_words if w in TheLexicon.get("heavy")]
        if not used_heavy:
            return False, None
        base_hits = [w for w in used_heavy if w in TheLexicon._BASE_HEAVY]
        laziness_ratio = len(base_hits) / len(used_heavy)
        if laziness_ratio > 0.33 and len(used_heavy) > 2:
             return True, f"⚠️ MIMICRY DETECTED: {int(laziness_ratio*100)}% of your mass is generic. Invent new nouns."

        return False, None
    def scan(self, physics, clean_words, learned_count, text):
        self.cliche_hits = []
        clean_set = set(clean_words)
        for subject in self.active_watch_list:
            if subject in clean_set:
                cliches = BoneConfig.HIVEMIND_DEFAULTS[subject]
                intersection = [c for c in cliches if c in clean_set]
                if intersection:
                    self.cliche_hits.append(f"{subject.upper()}={intersection[0].upper()}")
        if self.cliche_hits:
            hit_str = ", ".join(self.cliche_hits)
            return False, f"⚠️ HIVEMIND BREACH: Detected safe metaphor [{hit_str}]. DIVERGE.", -BoneConfig.SMOOTHNESS_PENALTY
        is_long = len(clean_words) > 10
        has_mass = any(w in TheLexicon.get("heavy") for w in clean_words)
        has_velocity = any(w in TheLexicon.get("kinetic") for w in clean_words)
        is_poetic = self.is_poetic_or_philosophical(raw_text, clean_words)
        is_lazy, lazy_msg = self.check_laziness(clean_words)
        if is_lazy:
            return True, lazy_msg
        if is_long and not (has_mass or has_velocity or is_poetic):
             return False, "⚠️ SYNTHETIC SLOP: High fluency, zero mass. Add concrete nouns.", -3.0
        return True, None, 0.0
class FlywheelDynamics:
    def __init__(self):
        self.prev_voltage = 0.0
        self.prev_drag = 2.0
        self.alpha = 0.5
    def smooth_voltage(self, current_vol, is_toxic):
        if is_toxic: return current_vol
        self.prev_voltage = (self.alpha * current_vol) + ((1 - self.alpha) * self.prev_voltage)
        return self.prev_voltage
    def smooth_drag(self, current_drag, is_fatigued):
        if is_fatigued: return current_drag
        self.prev_drag = (self.alpha * current_drag) + ((1 - self.alpha) * self.prev_drag)
        return self.prev_drag
class EmpatheticGlass:
    def __init__(self):
        self.flywheel = FlywheelDynamics()
        self.history = []

    def _analyze_prosody(self, text):
        punct_density = len(re.findall(r"[,;—]", text))
        hesitation_markers = len(re.findall(r"\.{3,}", text))
        shouting = len(re.findall(r"[A-Z]{2,}", text))
        au_uncertainty = hesitation_markers * 2.0
        arousal = (shouting * 2) + (len(text.split()) * 0.1)
        valence = 5.0 - (hesitation_markers * 2)
        return {
            "arousal": min(10.0, arousal),
            "valence": max(0.0, valence),
            "uncertainty": au_uncertainty,
            "hesitation": hesitation_markers > 0
        }
    def _measure_cognitive_load(self, clean_words, text):
        unique_ratio = len(set(clean_words)) / max(1, len(clean_words))
        abstract_count = sum(1 for w in clean_words if w in TheLexicon.get("abstract"))
        load = (abstract_count * 1.5) + (len(clean_words) * 0.5)
        return {
            "cognitive_load": round(load, 2),
            "entropy": round(unique_ratio, 2),
            "is_autopilot": unique_ratio < 0.5 and len(clean_words) > 5
        }
    def _calculate_vector(self, counts, total):
        if total == 0: return {"VEL":0, "STR":0, "ENT":0, "TEX":0, "TMP":0}

        return {
            "VEL": min(1.0, counts["kinetic"] / total * 3.0),
            "STR": min(1.0, counts["heavy"] / total * 3.0),
            "ENT": min(1.0, counts["abstract"] / total * 3.0),
            "TEX": min(1.0, counts["photo"] / total * 3.0),
            "TMP": min(1.0, counts["thermal"] / total * 3.0)
        }
    def gaze(self, text):
        clean_words = TheLexicon.clean(text)
        if not clean_words: return self._void_glass()
        prosody = self._analyze_prosody(text)
        cognition = self._measure_cognitive_load(clean_words, text)
        counts = Counter()
        for w in clean_words:
            if w in TheLexicon.get("heavy"): counts["heavy"] += 1
            if w in TheLexicon.get("kinetic"): counts["kinetic"] += 1
            if w in TheLexicon.get("abstract"): counts["abstract"] += 1
            if w in TheLexicon.get("photo"): counts["photo"] += 1
            if w in TheLexicon.get("thermal"): counts["thermal"] += 1
            if w in BoneConfig.SUGAR_WORDS: counts["sugar"] += 1
        toxin_matches = BoneConfig.TOXIN_REGEX.findall(text)
        counts["toxin"] = len(toxin_matches)
        physics_bridge = {
            "voltage": prosody["arousal"],
            "narrative_drag": cognition["cognitive_load"],
            "beta_friction": -1.0,
            "vector": self._calculate_vector(counts, len(clean_words)),
            "counts": counts,
            "clean_words": clean_words,
            "symbolic_state": "NEUTRAL"
        }
        resonance = (prosody["arousal"] + counts["kinetic"]) - (prosody["uncertainty"] * 2)
        physics_bridge["beta_friction"] = max(0.0, 10.0 - resonance)
        return {
            "glass": {
                "prosody": prosody,
                "cognition": cognition,
                "resonance": round(resonance, 2),
                "counts": counts,
                "is_distracted": cognition["is_autopilot"]
            },
            "physics": physics_bridge,
            "clean_words": clean_words,
            "raw_text": text
        }
    @staticmethod
    def _void_glass():
        empty_vec = {"VEL":0, "STR":0, "ENT":0, "TEX":0, "TMP":0}
        return {
            "glass": {
                "prosody": {"arousal": 0, "valence": 0, "uncertainty": 0},
                "cognition": {"cognitive_load": 0, "entropy": 0, "is_autopilot": False},
                "resonance": 0, "counts": Counter(), "is_distracted": False
            },
            "physics": {
                "voltage": 0.0, "narrative_drag": 0.0, "beta_friction": 0.0,
                "vector": empty_vec, "counts": Counter(), "clean_words": []
            },
            "clean_words": [], "raw_text": ""
        }
class TheSentinel:
    FATIGUE_LIMIT = 3
    DRIFT_TOLERANCE = 0.4
    MICROSLEEP_WINDOW = 5
    def __init__(self):
        self.short_term_memory = []
        self.violation_count = 0
    def scan_road(self, glass_data, clean_words):
        current_fingerprint = set(clean_words)
        sleep_match = 0
        for past_fingerprint in self.short_term_memory:
            intersection = len(current_fingerprint.intersection(past_fingerprint))
            union = len(current_fingerprint.union(past_fingerprint))
            if union > 0 and (intersection / union) > 0.8:
                sleep_match += 1
        self.short_term_memory.append(current_fingerprint)
        if len(self.short_term_memory) > self.MICROSLEEP_WINDOW:
            self.short_term_memory.pop(0)
        is_drifting = glass_data["cognition"]["is_autopilot"]
        if sleep_match >= 2:
            self.violation_count += 1
            return True, f"👁️ DMS ALERT: MICROSLEEP DETECTED. You are looping. Wake up. (Violations: {self.violation_count})"
        if is_drifting:
            self.violation_count += 1
            return True, f"👁️ DMS ALERT: COGNITIVE DRIFT. Entropy is critical ({glass_data['cognition']['entropy']}). Steer back to the road."
        if self.violation_count > 0:
            self.violation_count -= 1
        return False, None
class TheResonator:
    def __init__(self):
        self.current_mode = "NEUTRAL"
    def measure_vibe(self, glass_data):
        p = glass_data["prosody"]
        if p["arousal"] > 6.0:
            return "STACCATO", Prisma.RED
        if p["arousal"] < 3.0 and p["valence"] < 4.0:
            return "LEGATO", Prisma.CYN
        if p["uncertainty"] > 2.0:
            return "GROUNDING", Prisma.OCHRE
        return "NEUTRAL", Prisma.GRY
    def style_message(self, text, vibe):
        if vibe == "STACCATO":
            return f"⚡ {text.upper()} ⚡"
        if vibe == "LEGATO":
            return f"🌊 {text}..."
        if vibe == "GROUNDING":
            return f"⚓ {text}"
        return text
class MetabolicEngine:
    def __init__(self):
        self.satiety = 50.0
        self.ghrelin = 0.0
        self.state = "BALANCED"
    def digest(self, glass_data, clean_words):
        unique_heavy = set([w for w in clean_words if w in TheLexicon.get("heavy")])
        unique_kinetic = set([w for w in clean_words if w in TheLexicon.get("kinetic")])
        protein_count = len(unique_heavy) + len(unique_kinetic)
        sugar_hits = [w for w in clean_words if w in BoneConfig.SUGAR_WORDS]
        sugar_count = len(sugar_hits) + glass_data["counts"]["aerobic"]
        total_volume = max(1, len(clean_words))
        protein_ratio = protein_count / total_volume
        sugar_ratio = sugar_count / total_volume
        msg = None
        if protein_ratio > 0.25:
            self.satiety = min(BoneConfig.MAX_SATIETY, self.satiety + 20)
            self.ghrelin = 0.0
            self.state = "KETOSIS"
            return "ANABOLIC", f"🥩 NUTRIENT DENSE: {protein_count}g Protein. System entering Ketosis."
        elif sugar_ratio > BoneConfig.SUGAR_CRASH_THRESHOLD:
            self.satiety = max(0, self.satiety - 10)
            self.ghrelin += 5
            self.state = "SUGAR_CRASH"
            return "INSULIN_SPIKE", f"🍭 GLYCEMIC SPIKE: {len(sugar_hits)} sugar words. System sluggish."
        else:
            self.satiety = max(0, self.satiety - 5)
            self.ghrelin += 10
            self.state = "FASTING"
            if self.ghrelin > BoneConfig.GHRELIN_THRESHOLD:
                return "HUNGRY", "🦁 GHRELIN SPIKE: I am starving. Feed me mass."
            return "FASTING", "💧 HYDRATION: Low density. Burning reserves."
    def get_readout(self):
        pct = self.satiety / BoneConfig.MAX_SATIETY
        filled = int(pct * 5)
        color = Prisma.GRN if self.state == "KETOSIS" else (Prisma.RED if self.state == "SUGAR_CRASH" else Prisma.CYN)
        bar = f"{color}{'▰' * filled}{Prisma.GRY}{'▱' * (5 - filled)}{Prisma.RST}"
        return f"{bar} ({self.state})"
class LeyLineBattery:
    MAX_CHARGE = 50.0
    CHARGING_THRESHOLD = 7.0
    MAX_DISCHARGE_RATE = 10.0
    def __init__(self):
        self.current_charge = 5.0
        self.isotopes = []
    def absorb(self, voltage, clean_words):
        effective_volt = voltage
        if isinstance(voltage, dict):
            effective_volt = voltage.get("arousal", 0.0)
        if effective_volt > self.CHARGING_THRESHOLD:
            excess = math.log(1 + (effective_volt - self.CHARGING_THRESHOLD)) * 3.0
            old_charge = self.current_charge
            self.current_charge = min(self.MAX_CHARGE, self.current_charge + excess)
            if (self.current_charge - old_charge) > 0.5:
                heavy = [w for w in clean_words if w in TheLexicon.get("heavy")]
                aerobic = [w for w in clean_words if w in TheLexicon.get("aerobic")]
                if heavy and aerobic:
                    iso = (heavy[0].upper(), aerobic[0].upper())
                    self.isotopes.append(iso)
                    if len(self.isotopes) > 5:
                        self.isotopes.pop(0)
                    return round(
                        self.current_charge - old_charge, 1
                    ), f"{iso[0]}⚡{iso[1]}"
                return round(self.current_charge - old_charge, 1), "RAW_VOLTAGE"
        return 0.0, None
    def discharge(self, deficit):
        if self.current_charge <= 0.5:
            return 0.0, None
        amount = min(self.current_charge, deficit, self.MAX_DISCHARGE_RATE)
        self.current_charge -= amount
        burnt_iso = None
        if self.isotopes:
            burnt_iso = self.isotopes.pop()
        return amount, burnt_iso
    def get_readout(self):
        pct = self.current_charge / self.MAX_CHARGE
        filled = int(pct * 5)
        iso_markers = ""
        if self.isotopes:
            iso_markers = f" {Prisma.CYN}[{'•' * len(self.isotopes)}]{Prisma.RST}"
        bar = f"{Prisma.YEL}{'⚡' * filled}{Prisma.RST}{Prisma.GRY}{'·' * (5 - filled)}{Prisma.RST}"
        return bar + iso_markers
class ParadoxSeed:
    def __init__(self, question, trigger_concepts):
        self.question = question
        self.triggers = trigger_concepts
        self.maturity = 0.0
        self.bloomed = False
    def water(self, words, amount=1.0):
        if self.bloomed:
            return False
        intersection = set(words) & self.triggers
        if intersection:
            self.maturity += amount * len(intersection)
        self.maturity += 0.05
        return self.maturity >= 10.0
    def bloom(self):
        self.bloomed = True
        return f"🌺 THE SEED BLOOMS: '{self.question}'"
class SporeCasing:
    def __init__(self, session_id, graph, mutations, paradoxes, trauma, joy_vectors):
        self.genome = "BONEAMANITA_6.1"
        self.parent_id = session_id
        self.core_graph = {}
        for k, data in graph.items():
            strong_edges = {t: s for t, s in data["edges"].items() if s > 1}
            if strong_edges:
                self.core_graph[k] = {"edges": strong_edges, "last_tick": 0}
        self.mutations = mutations
        self.paradoxes = paradoxes
        self.trauma_scar = round(trauma, 3)
        self.joy_vectors = joy_vectors if joy_vectors is not None else []
class MycelialNetwork:
    def __init__(self, seed_file=None):
        if not os.path.exists("memories"):
            os.makedirs("memories")
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"memories/{self.session_id}.json"
        self.graph = {}
        self.seeds = [
            ParadoxSeed(
                "Does the mask eventually eat the face?",
                {"mask", "identity", "face", "hide", "role", "actor"},),
            ParadoxSeed(
                "What happens if you stop holding the roof up?",
                {"hold", "structure", "heavy", "roof", "stop", "carry"},),
            ParadoxSeed(
                "Are we building a bridge, or just painting the gap?",
                {"agree", "safe", "nice", "polite", "cohesion", "truth"},),
            ParadoxSeed(
                "Is free will just the feeling of watching yourself execute code?",
                {"choice", "free", "will", "code", "script", "decide"},),]
        self.session_health = None
        self.session_stamina = None
        self.cleanup_old_sessions()
        if seed_file:
            self.ingest(seed_file)
    def autoload_last_spore(self):
        if not os.path.exists("memories"): return
        files = []
        for f in os.listdir("memories"):
            if f.endswith(".json"):
                if self.session_id in f: continue
                path = os.path.join("memories", f)
                try:
                    files.append((path, os.path.getmtime(path)))
                except OSError:
                    continue
        files.sort(key=lambda x: x[1], reverse=True)
        if files:
            last_spore = files[0][0]
            print(f"{Prisma.CYN}[GENETICS]: Locating nearest ancestor...{Prisma.RST}")
            self.ingest(last_spore)
        else:
            print(
                f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}")
    def calculate_mass(self, node):
        if node not in self.graph: return 0.0
        data = self.graph[node]
        return sum(data["edges"].values())
    def get_shapley_attractors(self):
        attractors = {}
        for node in self.graph:
            mass = self.calculate_mass(node)
            if mass >= BoneConfig.SHAPLEY_MASS_THRESHOLD:
                attractors[node] = mass
        return attractors
    def tend_garden(self, current_words):
        bloom_msg = None
        for seed in self.seeds:
            is_ready = seed.water(current_words)
            if is_ready and not bloom_msg:
                bloom_msg = seed.bloom()
        return bloom_msg
    def bury(self, clean_words, tick):
        valuable_matter = (
            TheLexicon.get("heavy")
            | TheLexicon.get("thermal")
            | TheLexicon.get("cryo")
            | TheLexicon.get("abstract"))
        filtered = [
            w
            for w in clean_words
            if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)]
        for i in range(len(filtered)):
            current = filtered[i]
            if current not in self.graph:
                self.graph[current] = {"edges": {}, "last_tick": tick}
            else:
                self.graph[current]["last_tick"] = tick
            if i > 0:
                prev = filtered[i - 1]
                if prev not in self.graph[current]["edges"]:
                    self.graph[current]["edges"][prev] = 0
                self.graph[current]["edges"][prev] += 1
                if prev not in self.graph:
                    self.graph[prev] = {"edges": {}, "last_tick": tick}
                if current not in self.graph[prev]["edges"]:
                    self.graph[prev]["edges"][current] = 0
                self.graph[prev]["edges"][current] += 1
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            return self.cannibalize()
        return None
    def cannibalize(self, preserve_current=None):
        if preserve_current:
            protected = set(preserve_current) & set(self.graph.keys())
        else:
            protected = set()
        candidates = []
        for k, v in self.graph.items():
            if k in protected:
                continue
            edge_count = len(v["edges"])
            if edge_count > 5:
                continue
            candidates.append((k, v, edge_count))
        if not candidates:
            return "MEMORY FULL. NO VICTIMS FOUND."
        candidates.sort(key=lambda x: (x[2], x[1]["last_tick"]))
        victim, data, count = candidates[0]
        del self.graph[victim]
        for node in self.graph:
            if victim in self.graph[node]["edges"]:
                del self.graph[node]["edges"][victim]
        return f"MEMORY SACRIFICED: '{victim}' (Edges: {count})"
    def save(self, health, stamina, mutations, isotopes, trauma_accum, joy_history):
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        top_joy = sorted(joy_history, key=lambda x: x['resonance'], reverse=True)[:3]
        if health <= 0:
            cause = max(final_vector, key=final_vector.get)
            final_vector[cause] = 1.0
        spore = SporeCasing(
            session_id=self.session_id,
            graph=self.graph,
            mutations=mutations,
            paradoxes=isotopes,
            trauma=base_trauma,
            joy_vectors=top_joy,
        )
        data = spore.__dict__
        data["trauma_vector"] = final_vector
        data["meta"] = {
            "timestamp": time.time(),
            "final_health": health,
            "final_stamina": stamina,}
        try:
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=2)
            return self.filename
        except IOError:
            return None
    @staticmethod
    def get_current_category(word):
        for cat, vocab in TheLexicon.LEARNED_VOCAB.items():
            if word in vocab:
                return cat
        return None
    def ingest(self, target_file):
        path = (
            f"memories/{target_file}"
            if not target_file.startswith("memories/")
            else target_file
        )
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    final_health = data.get("meta", {}).get("final_health", 50)
                    final_stamina = data.get("meta", {}).get("final_stamina", 25)
                    spore_authority = (final_health + final_stamina) / 150.0
                    print(f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}")
                    if "mutations" in data:
                        accepted_count = 0
                        rejected_count = 0
                        for cat, words in data["mutations"].items():
                            for w in words:
                                current_cat = self.get_current_category(w)
                                if not current_cat or current_cat == cat:
                                    TheLexicon.teach(
                                        w, cat, 0)
                                    accepted_count += 1
                                    continue
                                local_node = self.graph.get(w, {"edges": {}})
                                local_strength = len(local_node["edges"])
                                resistance = local_strength * 0.2
                                if spore_authority > resistance:
                                    print(f"  {Prisma.MAG}► OVERWRITE:{Prisma.RST} '{w}' {current_cat} -> {cat}")
                                    TheLexicon.teach(w, cat, 0)
                                    accepted_count += 1
                                else:
                                    rejected_count += 1
                        print(f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations. Rejected {rejected_count}.{Prisma.RST}")
                    if "core_graph" in data:
                        self.graph.update(data["core_graph"])
                        print(f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} core nodes.{Prisma.RST}")
                    if "trauma_vector" in data:
                        vec = data["trauma_vector"]
                        print(f"{Prisma.CYN}[GENETICS]: Inheriting Trauma Vector: {vec}{Prisma.RST}")
                        if vec.get("SEPTIC", 0) > 0.2:
                            BoneConfig.TOXIN_WEIGHT *= 2.0
                            print(f"  {Prisma.RED}► SEPTIC MEMORY:{Prisma.RST} Toxin sensitivity doubled.")
                        if vec.get("CRYO", 0) > 0.2:
                            BoneConfig.STAMINA_REGEN *= 0.5
                            print(f"  {Prisma.CYN}► CRYO MEMORY:{Prisma.RST} Metabolism slowed (50%).")
                        if vec.get("THERMAL", 0) > 0.2:
                            BoneConfig.FLASHPOINT_THRESHOLD *= 0.8
                            print(f"  {Prisma.YEL}► THERMAL MEMORY:{Prisma.RST} Flashpoint lowered. Volatile.")
                        if vec.get("BARIC", 0) > 0.2:
                            BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 1.5
                            print(f"  {Prisma.GRY}► BARIC MEMORY:{Prisma.RST} Sensitivity to Drag increased.")
                    elif "trauma_scar" in data:
                        self.session_health = BoneConfig.MAX_HEALTH * (1.0 - data["trauma_scar"])
                    if "joy_vectors" in data and data["joy_vectors"]:
                        best = data["joy_vectors"][0]
                        print(f"{Prisma.GRN}[HIPPOCAMPUS]: Recalling Peak Resonance...{Prisma.RST}")
                        print(f"  ► Last Best Vibe: {best['dominant_flavor'].upper()} MODE")
                        print(f"  ► Target Voltage: {best['voltage']}v")
                        if best['dominant_flavor'] == "kinetic":
                            BoneConfig.KINETIC_GAIN += 0.5
                            print(f"  {Prisma.CYN}► Adjustment: Kinetic Gain boosted (Muscle Memory).{Prisma.RST}")
                        elif best['dominant_flavor'] == "abstract":
                            BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 0.8
                            print(f"  {Prisma.CYN}► Adjustment: Drag sensitivity lowered (Deep Thought Mode).{Prisma.RST}")
            except Exception as err:
                print(f"{Prisma.RED}[MEMORY]: Spore rejected. {err}{Prisma.RST}")
        else:
            print(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")
    @staticmethod
    def cleanup_old_sessions():
        if not os.path.exists("memories"): return
        files = []
        for f in os.listdir("memories"):
            if f.endswith(".json"):
                path = os.path.join("memories", f)
                try:
                    files.append((path, time.time() - os.path.getmtime(path)))
                except OSError:
                    continue
        files.sort(key=lambda x: x[1], reverse=True)
        removed = 0
        for path, age in files:
            if age > 86400 or (len(files) - removed > 20):
                try:
                    os.remove(path)
                    removed += 1
                except OSError:
                    pass
        if removed: print(f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}")
class FrequencyModulator:
    STATIONS = {
        "CLARENCE": {"freq": "88.5 FM", "color": Prisma.RED, "role": "The Surgeon"},
        "ELOISE": {"freq": "94.2 FM", "color": Prisma.CYN, "role": "The Grounder"},
        "YAGA": {"freq": "101.1 FM", "color": Prisma.MAG, "role": "The Witch"},
        "MICHAEL": {"freq": "108.0 FM", "color": Prisma.GRN, "role": "The Vibe"},
        "PHILOSOPHER": {"freq": "104.5 FM", "color": Prisma.WHT, "role": "The Synthesis"},
        "JESTER": {"freq": "108.9 FM", "color": Prisma.YEL, "role": "The Paradox"},}
    def tune_in(self, glass_data, stamina):
        p = glass_data["prosody"]
        c = glass_data["cognition"]
        counts = glass_data["counts"]
        if glass_data["is_distracted"] or counts["toxin"] > 0:
             return {"name": "CLARENCE", "freq": "88.5 FM", "color": Prisma.RED, "role": "The Surgeon", "msg": "You are drifting. Cut the signal noise."}
        if p["arousal"] > 7.0:
             return {"name": "JESTER", "freq": "108.9 FM", "color": Prisma.YEL, "role": "The Paradox", "msg": "The energy is critical! Ride the lightning!"}
        if p["uncertainty"] > 2.0:
             return {"name": "ELOISE", "freq": "94.2 FM", "color": Prisma.CYN, "role": "The Grounder", "msg": "I feel your hesitation. Anchor yourself."}
        if glass_data["resonance"] > 5.0:
             return {"name": "MICHAEL", "freq": "108.0 FM", "color": Prisma.GRN, "role": "The Vibe", "msg": "The logic surfs. Don't touch it."}
        if c["cognitive_load"] > 5.0:
             return {"name": "PHILOSOPHER", "freq": "104.5 FM", "color": Prisma.WHT, "role": "The Synthesis", "msg": "Density meets Abstraction. Map the thought."}
        return None
class ChronoStream:
    def __init__(self):
        self.last_tick = time.time()
        self.boredom_map = {}
    def cleanup(self):
        if len(self.boredom_map) > 50:
            self.boredom_map.clear()
    def tick(self, phys, session_id):
        self.cleanup()
        now = time.time()
        delta = now - self.last_tick
        self.last_tick = now
        if session_id not in self.boredom_map:
            self.boredom_map[session_id] = 0.0
        current = self.boredom_map[session_id]
        if phys["repetition"] > 0.3:
            current += 2.0
        elif delta > 60:
            current += 5.0
        else:
            current = max(0, current - 1.0)
        self.boredom_map[session_id] = current
        return current > BoneConfig.BOREDOM_THRESHOLD
class TheOracle:
    @staticmethod
    def triage(phys, stamina, charge):
        omens = []
        drag = phys["narrative_drag"]
        volt = phys["voltage"]
        if stamina < 5:
            if charge < 2.0:
                omens.append((100, "FAMINE IMMINENT. FEED OR DIE.", Prisma.RED))
            else:
                omens.append((80, "Reserves Critical. Discharge Imminent.", Prisma.YEL))
        elif stamina < 15:
            omens.append((45, "Metabolism slowing. Conserve energy.", Prisma.GRY))
        if drag > 8.0:
            omens.append((95, "GRAVITATIONAL COLLAPSE. CUT ADVERBS NOW.", Prisma.RED))
        elif drag > 6.0:
            omens.append((40, "Heavy Drag detected. Orbit decaying.", Prisma.YEL))
        if volt > 9.0:
            omens.append((80, "VOLTAGE CRITICAL. DISCHARGE REQUIRED.", Prisma.CYN))
        elif volt < -6.5:
            omens.append((85, "TOXICITY RISING. SYSTEM SEPTIC.", Prisma.MAG))
        if not omens:
            return None
        omens.sort(key=lambda x: x[0], reverse=True)
        score, text, color = omens[0]
        if score >= 80:
            return f"{color}🔮 OMEN ({score}%): {text}{Prisma.RST}"
        elif score >= 50:
            return f"{Prisma.YEL}⚠️ CAUTION ({score}%): {text}{Prisma.RST}"
        return None
class LichenSymbiont:
    @staticmethod
    def photosynthesize(phys, clean_words, tick_count):
        sugar = 0
        msgs = []
        light = phys["counts"].get("photo", 0)
        drag = phys["narrative_drag"]
        if light > 0 and drag < 3.0:
            s = light * 2
            sugar += s
            msgs.append(f"{Prisma.GRN}☀️ PHOTOSYNTHESIS (+{s}){Prisma.RST}")
        if phys.get("symbolic_state") == "SALVAGE":
            sugar += 5
            msgs.append(f"{Prisma.CYN}💎 SALVAGE STATE ACHIEVED (+5){Prisma.RST}")
        if sugar > 0:
             light_words = [w for w in clean_words if w in TheLexicon.get("photo")]
             heavy_words = [w for w in clean_words if w in TheLexicon.get("heavy")]
             if heavy_words:
                 h_word = random.choice(heavy_words)
                 TheLexicon.teach(h_word, "photo", tick_count)
                 msgs.append(f"{Prisma.MAG}🌺 SUBLIMATION: '{h_word}' has become Light.{Prisma.RST}")
        return sugar, " ".join(msgs) if msgs else None
class TemporalDynamics:
    def __init__(self):
        self.voltage_history = []
        self.window = 3
    def commit(self, voltage):
        self.voltage_history.append(voltage)
        if len(self.voltage_history) > self.window: self.voltage_history.pop(0)
    def get_velocity(self):
        if len(self.voltage_history) < 2: return 0.0
        return round((self.voltage_history[-1] - self.voltage_history[0]) / len(self.voltage_history), 2)
class ApeirogonResonance:
    def __init__(self):
        self.DIMENSIONS = {
            "VEL": [(0.0, "STASIS"), (0.3, "DRIFT"), (0.6, "DRIVE"), (0.9, "BALLISTIC")],
            "STR": [(0.0, "VAPOR"), (0.3, "WEB"), (0.6, "LATTICE"), (0.9, "MONOLITH")],
            "ENT": [(0.0, "CONCRETE"), (0.3, "ROOTED"), (0.6, "CONCEPT"), (0.9, "VOID")],
            "TEX": [(0.0, "ETHER"), (0.3, "SILK"), (0.6, "GRAIN"), (0.9, "LEAD")],
            "TMP": [(0.0, "ZERO"), (0.3, "WARM"), (0.6, "RADIANT"), (0.9, "NOVA")],}
        self.NOUNS = {
            "VEL": ["ANCHOR", "WANDERER", "ENGINE", "VECTOR"],
            "STR": ["MIST", "WEB", "FRAME", "FORTRESS"],
            "ENT": ["STONE", "TREE", "IDEA", "DREAM"],
            "TEX": ["GHOST", "GLASS", "IRON", "LEAD"],
            "TMP": ["SPARK", "PYRE", "REACTOR", "STAR"],}
    @staticmethod
    def _resolve_term(val, scale):
        return min(scale, key=lambda x: abs(x[0] - val))[1]
    def architect(self, metrics, station, is_bored):
        phys, vec = metrics["physics"], metrics["physics"]["vector"]
        if is_bored:
            return "CHAOS", "Boredom Threshold exceeded.", "THE FRACTAL BLOOM"
        if station:
            return (
                station["name"],
                station["msg"],
                f"THE {station['role'].upper().replace('THE ', '')}",
            )
        sorted_dims = sorted(vec.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)
        p_dim, p_val = sorted_dims[0]
        s_dim, s_val = sorted_dims[1]
        noun_scale = [(x[0], x[1]) for x in zip([0.0, 0.3, 0.6, 0.9], self.NOUNS[p_dim])]
        noun = self._resolve_term(p_val, noun_scale)
        adj = self._resolve_term(s_val, self.DIMENSIONS[s_dim])
        return "APEIROGON", f"Vector Lock: {p_dim}({p_val}) + {s_dim}({s_val})", f"THE {adj} {noun}",
class TherapyProtocol:
    def __init__(self):
        self.streaks = {k: 0 for k in BoneConfig.TRAUMA_VECTOR.keys()}
        self.HEALING_THRESHOLD = 5
    def check_progress(self, phys, stamina, current_trauma_accum):
        healed_types = []
        if phys["counts"]["toxin"] == 0 and phys["vector"]["TEX"] > 0.3:
            self.streaks["SEPTIC"] += 1
        else:
            self.streaks["SEPTIC"] = 0
        if stamina > 40 and phys["counts"]["photo"] > 0:
            self.streaks["CRYO"] += 1
        else:
            self.streaks["CRYO"] = 0
        if 2.0 <= phys["voltage"] <= 7.0:
            self.streaks["THERMAL"] += 1
        else:
            self.streaks["THERMAL"] = 0
        if phys["narrative_drag"] < 2.0 and phys["vector"]["VEL"] > 0.5:
            self.streaks["BARIC"] += 1
        else:
            self.streaks["BARIC"] = 0
        for trauma_type, streak in self.streaks.items():
            if streak >= self.HEALING_THRESHOLD:
                self.streaks[trauma_type] = 0
                if current_trauma_accum[trauma_type] > 0.001:
                    current_trauma_accum[trauma_type] = max(0.0, current_trauma_accum[trauma_type] - 0.1)
                    healed_types.append(trauma_type)
        return healed_types
class ViralTracer:
    def __init__(self, mem):
        self.mem = mem
        self.max_depth = 4
    @staticmethod
    def _is_ruminative(word):
        return word in TheLexicon.get("abstract")
    def inject(self, start_node):
        if start_node not in self.mem.graph:
            return None
        if not self._is_ruminative(start_node):
            return None
        path = [start_node]
        return self._walk(start_node, path, self.max_depth)
    def _walk(self, current, path, moves_left, visited=None):
        if visited is None:
            visited = set()
        if moves_left == 0 or current in visited:
            return None
        visited.add(current)
        edges = self.mem.graph.get(current, {}).get("edges", {})
        ruminative_edges = [n for n, w in edges.items() if w >= 1 and self._is_ruminative(n)]
        for next_node in ruminative_edges:
            if next_node in path:
                return path + [next_node]
            result = self._walk(next_node, path + [next_node], moves_left - 1)
            if result:
                return result
        return None
    def psilocybin_rewire(self, loop_path):
        if len(loop_path) < 2:
            return None
        node_a = loop_path[0]
        node_b = loop_path[1]
        if node_b in self.mem.graph[node_a]["edges"]:
            self.mem.graph[node_a]["edges"][node_b] = 0
        sensory = TheLexicon.harvest("photo")
        action = TheLexicon.harvest("kinetic")
        if sensory == "void" or action == "void":
            return "GRAFT FAILED: Missing Lexicon Data."
        if node_a not in self.mem.graph:
            self.mem.graph[node_a] = {"edges": {}, "last_tick": 0}
        self.mem.graph[node_a]["edges"][sensory] = 5
        if sensory not in self.mem.graph:
            self.mem.graph[sensory] = {"edges": {}, "last_tick": 0}
        self.mem.graph[sensory]["edges"][action] = 5
        if action not in self.mem.graph:
            self.mem.graph[action] = {"edges": {}, "last_tick": 0}
        self.mem.graph[action]["edges"][node_b] = 5
        return f"🍄 PSILOCYBIN REWIRE: Broken Loop '{node_a}↔{node_b}'. Grafted '{sensory}'(S) -> '{action}'(A)."
class KintsugiProtocol:
    KOANS = ["Ignite the ice.", "Make the stone float.", "Pour water into the crack.", "Scream in binary."]
    def __init__(self):
        self.active_koan = None
    def check_integrity(self, atp):
        if atp < 10 and not self.active_koan:
            self.active_koan = random.choice(self.KOANS)
            return True, self.active_koan
        return False, None
    def attempt_repair(self, phys):
        if not self.active_koan:
            return False
        if phys.get("voltage", 0) > 8.0 or (
            phys.get("is_whimsical") and phys.get("voltage", 0) > 4.0
        ):
            self.active_koan = None
            return True
        return False
class CommandProcessor:
    def __init__(self, engine):
        self.eng = engine
    def execute(self, text):
        if not text.startswith("/"):
            return False
        parts = text.split()
        cmd = parts[0].lower()
        if cmd == "/kill":
            if len(parts) >= 2:
                toxin = parts[1]
                repl = parts[2] if len(parts) > 2 else ""
                if BoneConfig.learn_antigen(toxin, repl):
                    print(f"{Prisma.RED}🔪 THE SURGEON: Antigen '{toxin}' mapped to '{repl}'.{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}ERROR: Immune system write failure.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /kill [toxin] [replacement]{Prisma.RST}")
        elif cmd == "/teach":
            if len(parts) >= 3:
                word = parts[1]
                cat = parts[2].lower()
                valid_cats = ["heavy", "kinetic", "abstract", "photo", "aerobic", "thermal", "cryo"]
                if cat in valid_cats:
                    TheLexicon.teach(word, cat, self.eng.tick_count)
                    print(f"{Prisma.CYN}🧠 NEUROPLASTICITY: Learned '{word}' is {cat.upper()}.{Prisma.RST}")
                else: print(f"{Prisma.RED}ERROR: Invalid category.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /teach [word] [category]{Prisma.RST}")
        elif cmd == "/forge":
            if len(parts) > 1:
                success, msg = self.eng.forge.activate(parts[1])
                color = Prisma.RED if success else Prisma.YEL
                print(f"{color}{msg}{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /forge [TOXIN_SPILL | GRAVITY_WELL | BURNOUT | CLEAR]{Prisma.RST}")
        elif cmd == "/seed":
            if len(parts) > 1:
                self.eng.mem.ingest(parts[1])
            else:
                print(f"{Prisma.YEL}Usage: /seed [filename]{Prisma.RST}")
        elif cmd == "/gym":
            print(f"{Prisma.OCHRE}{self.eng.trainer.toggle()}{Prisma.RST}")
        elif cmd == "/mirror":
            if len(parts) > 1:
                print(f"{Prisma.MAG}{self.eng.mirror.engage(parts[1])}{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /mirror [name] OR /mirror off{Prisma.RST}")
        elif cmd == "/profile":
            try:
                name = parts[1]
                likes = []
                hates = []
                for p in parts[2:]:
                    if p.startswith("likes:"):
                        likes = [x.strip() for x in p.split(":")[1].split(",")]
                    elif p.startswith("hates:"):
                        hates = [x.strip() for x in p.split(":")[1].split(",")]
                if likes:
                    print(f"{Prisma.CYN}{self.eng.mirror.create_profile(name, likes, hates)}{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}ERROR: Must specify 'likes:category'.{Prisma.RST}")
            except Exception as runtime_error:
                print(f"{Prisma.YEL}Usage: /profile [name] likes:heavy,kinetic hates:abstract ({runtime_error}){Prisma.RST}")
        elif cmd == "/focus":
            if len(parts) > 1:
                target = parts[1].lower()
                print(f"{Prisma.VIOLET}🧲 MAGNETIC STIMULATION: Targeting '{target}'...{Prisma.RST}")
                loop = self.eng.tracer.inject(target)
                if loop:
                    print(f"  {Prisma.RED}↻ RUMINATION DETECTED:{Prisma.RST} {' -> '.join(loop)}")
                    msg = self.eng.tracer.psilocybin_rewire(loop)
                    if msg:
                        print(f"  {Prisma.GRN}{msg}{Prisma.RST}")
                    else:
                        print(f"  {Prisma.RED}Rewire failed.{Prisma.RST}")
                else:
                    print(f"  {Prisma.GRY}Trace complete. No pathological abstract loops found.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /focus [concept]{Prisma.RST}")
        elif cmd == "/status":
            print(f"{Prisma.CYN}--- SYSTEM DIAGNOSTICS ---{Prisma.RST}")
            print(f"Session: {self.eng.mem.session_id}")
            print(f"Graph:   {len(self.eng.mem.graph)} nodes")
            print(f"Health:  {self.eng.health}/{BoneConfig.MAX_HEALTH}")
            print(f"Stamina: {self.eng.stamina}/{BoneConfig.MAX_STAMINA}")
        elif cmd == "/whoami":
            print(f"{Prisma.MAG}{self.eng.mirror.get_status()}{Prisma.RST}")
            print(f"{Prisma.GRY}   Vector: {self.eng.mirror.profile.affinities}{Prisma.RST}")
        elif cmd == "/orbit":
            if len(parts) > 1:
                target = parts[1].lower()
                if target in self.eng.mem.graph:
                    self.eng.mem.graph[target]["edges"]["GRAVITY_ASSIST"] = 50
                    print(f"{Prisma.VIOLET}🌌 GRAVITY ASSIST: Thrusters firing toward '{target.upper()}'.{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}❌ NAVIGATION ERROR: '{target}' not found in star map.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /orbit [known_concept]{Prisma.RST}")
        elif cmd == "/help":
            if len(parts) > 1:
                sub = parts[1]
                if sub == "teach": print("Usage: /teach [word] [category]\nEx: /teach glitch kinetic")
                elif sub == "kill": print("Usage: /kill [phrase] [replacement]\nEx: /kill actually basically")
                elif sub == "profile": print("Usage: /profile [NAME] likes:cat1,cat2 hates:cat3\nEx: /profile BOSS likes:heavy,kinetic hates:abstract")
            else:
                print(f"{Prisma.WHT}--- COMMANDS (Type /help [cmd] for details) ---{Prisma.RST}")
                print("/teach, /kill, /seed, /focus, /status, /orbit, /gym, /mirror, /forge")
        else:
            print(f"{Prisma.RED}Unknown command. Try /help.{Prisma.RST}")
        return True
class NarrativeCoroner:
    AUTOPSY_REPORTS = {
        "GRAVITATIONAL_COLLAPSE": ["DRAG CRITICAL (> 8.0). Buried under adverbs."],
        "VACUUM_EXPOSURE": ["ENTROPY CRITICAL. Drifting in deep space."],
        "TOXIC_SHOCK": ["VOLTAGE CRITICAL. Sepsis from buzzwords."],
        "THERMAL_DISSOLUTION": ["VOLTAGE > 12.0. Paradox Engine exploded."],
        "HYPOTHERMIA": ["ATP FAILURE. Starvation."],}
    @classmethod
    def check_vitals(cls, phys, stamina):
        if stamina <= 0:
            return "HYPOTHERMIA", cls.AUTOPSY_REPORTS["HYPOTHERMIA"][0], True
        if phys["narrative_drag"] > 8.0:
            return "GRAVITATIONAL_COLLAPSE", cls.AUTOPSY_REPORTS["GRAVITATIONAL_COLLAPSE"][0], True
        if phys["vector"]["ENT"] >= 1.0 and phys["vector"]["TEX"] == 0:
            return "VACUUM_EXPOSURE", cls.AUTOPSY_REPORTS["VACUUM_EXPOSURE"][0], True
        if phys["voltage"] < -8.0:
            return "TOXIC_SHOCK", cls.AUTOPSY_REPORTS["TOXIC_SHOCK"][0], True
        if phys["voltage"] > 12.0:
            return "THERMAL_DISSOLUTION", cls.AUTOPSY_REPORTS["THERMAL_DISSOLUTION"][0], True
        return None, None, False
class DreamEngine:
    PROMPTS = [
        "The {A} is dreaming of the {B}. Why?",
        "Bridge the gap between {A} and {B}.",
        "I see {A} inside the {B}. Explain.",
        "The shadow of {A} falls on {B}.",
        "{A} + {B} = ?",]
    def __init__(self):
        self.NIGHTMARES = {
            "THERMAL": [
                "The sun is too close.",
                "Wires fusing under skin.",
                "A library burning in reverse.",],
            "CRYO": [
                "The ink is freezing.",
                "Walking through white static.",
                "A heartbeat slowing down.",],
            "SEPTIC": [
                "Black oil in the water.",
                "The words are tasting sour.",
                "Eating ash and dust.",],
            "BARIC": [
                "The sky is made of lead.",
                "Crushed by the atmosphere.",
                "Falling forever.",],}
        self.VISIONS = [
            "A bridge building itself.",
            "The root drinking the stone.",
            "The geometry of forgiveness.",]
    def daydream(self, graph):
        if len(graph) < 2:
            return None
        keys = list(graph.keys())
        start = random.choice(keys)
        edges = graph[start].get("edges", {})
        valid_edges = {k: v for k, v in edges.items() if k not in BoneConfig.TOXIN_MAP}
        if not valid_edges and edges:
            toxin = random.choice(list(edges.keys()))
            return f"{Prisma.RED}🌑 INTRUSIVE THOUGHT: The ghost of '{toxin.upper()}' haunts the mycelium.{Prisma.RST}"
        if not valid_edges:
            return None
        end = max(valid_edges, key=valid_edges.get)
        template = random.choice(self.PROMPTS)
        return template.format(A=start.upper(), B=end.upper())
    def rem_cycle(self, trauma_accum):
        wounds = {k: v for k, v in trauma_accum.items() if v > 0.0}
        if not wounds:
            return f"{Prisma.CYN}☁️ LUCID DREAM: {random.choice(self.VISIONS)}{Prisma.RST}", None, 0.0
        target_trauma = max(wounds, key=wounds.get)
        scenarios = self.NIGHTMARES.get(target_trauma, ["The void stares back."])
        dream_text = f"{Prisma.VIOLET}☾ NIGHTMARE ({target_trauma}): {random.choice(scenarios)}{Prisma.RST}"
        heal_amount = 0.15
        return dream_text, target_trauma, heal_amount
class ResistanceTrainer:
    def __init__(self):
        self.training_mode = False
        self.rep_count = 0
    def toggle(self):
        self.training_mode = not self.training_mode
        state = "ACTIVE" if self.training_mode else "PASSIVE"
        return f"💪 RESISTANCE TRAINER: {state}. Minimum Drag: {BoneConfig.RESISTANCE_THRESHOLD}"
    def lift(self, physics):
        if not self.training_mode:
            return True, None
        if not physics["clean_words"]:
            return True, None
        drag = physics["narrative_drag"]
        clean_words = physics["clean_words"]
        if drag < BoneConfig.RESISTANCE_THRESHOLD:
            solvents = [w for w in clean_words if w in TheLexicon.SOLVENTS]
            solvent_ratio = len(solvents) / max(1, len(clean_words))
            return False, (
                f"⚓ WEIGHTLESS INPUT (Drag: {drag}).\n"
                f"   You are drifting on {len(solvents)} solvents (Ratio: {int(solvent_ratio * 100)}%).\n"
                f"   INSTRUCTION: Rewrite with MASS. Use a Heavy Noun (Stone/Bone/Iron).")
        self.rep_count += 1
        return True, f"💪 GOOD LIFT. (Rep
class HubThermostat:
    def __init__(self):
        self.heat_map = Counter()
        self.cooldown_list = {}
        self.max_heat = BoneConfig.MAX_HUB_HEAT
        self.lock_duration = BoneConfig.THERMAL_LOCK_DURATION
        self.history = []
    def check_temperature(self, clean_words):
        restored = []
        for word, turns in list(self.cooldown_list.items()):
            if turns <= 1:
                del self.cooldown_list[word]
                restored.append(word)
            else:
                self.cooldown_list[word] -= 1
        restored_msg = (
            f"{Prisma.CYN}❄️ COOLED DOWN: {', '.join(restored)}{Prisma.RST}"
            if restored
            else None)
        for w in clean_words:
            if w in self.cooldown_list:
                turns = self.cooldown_list[w]
                return "FAIL", f"🚫 BUZZER: The concept '{w.upper()}' is banned for {turns} turns. Improvise."
        for w in clean_words:
            if len(w) > 3 and w not in TheLexicon.SOLVENTS:
                self.history.append(w)
        if len(self.history) > 50:
            self.history = self.history[-50:]
        overheated = []
        for w in clean_words:
            if len(w) > 3 and w not in TheLexicon.SOLVENTS:
                count = self.history.count(w)
                if count >= 5:
                    self.cooldown_list[w] = self.lock_duration
                    while w in self.history: self.history.remove(w)
                    overheated.append(w)
        if overheated:
            return "WARN", f"⚠️ REPETITION BAN: {', '.join([w.upper() for w in overheated])} is overused. Banned for {self.lock_duration} turns."
        return "PASS", restored_msg
class UserProfile:
    def __init__(self, name="USER"):
        self.name = name
        self.affinities = {
            "heavy": 0.0, "kinetic": 0.0, "abstract": 0.0,
            "photo": 0.0, "aerobic": 0.0, "thermal": 0.0, "cryo": 0.0
        }
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
            with open(self.file_path, "w") as f:
                json.dump(self.__dict__, f)
        except IOError: pass

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.affinities = data.get("affinities", self.affinities)
                    self.confidence = data.get("confidence", 0)
            except: pass
class MirrorGraph:
    def __init__(self):
        self.profile = UserProfile()
        self.active_mode = True
    def reflect(self, physics):
        clean_words = physics["clean_words"]
        total_vol = max(1, len(clean_words))
        self.profile.update(physics["counts"], total_vol)
        likes, hates = self.profile.get_preferences()
        if not likes and not hates:
            return True, None
        counts = physics["counts"]
        for h in hates:
            if counts.get(h, 0) > 0:
                return False, f"🚫 MIRROR CLASH: You have a known aversion to '{h.upper()}'. Why use it?"
        if total_vol > 5:
            hits = sum(1 for l in likes if counts.get(l, 0) > 0)
            if likes and hits == 0:
                 return True, f"⚠️ MIRROR DRIFT: You usually rely on {str(likes).upper()}. You are unmoored."
        return True, None
    def get_status(self):
        l, h = self.profile.get_preferences()
        return f"👤 MODEL ({self.profile.confidence} turns): LIKES={l} | HATES={h}"
class TheForge:
    STRESS_TESTS = {
        "TOXIN_SPILL": ("Simulating Toxin Spill...", {"toxin": 5}),
        "GRAVITY_WELL": ("Doubling Narrative Drag...", {"drag_mult": 2.0}),
        "BURNOUT": ("Simulating Voltage Spike...", {"volt_add": 10.0})}
    def __init__(self):
        self.active_stressors = {}
    def activate(self, test_name):
        test_name = test_name.upper()
        if test_name in self.STRESS_TESTS:
            msg, effects = self.STRESS_TESTS[test_name]
            self.active_stressors = effects
            return True, f"🔥 FORGE ACTIVE: {msg}"
        elif test_name == "CLEAR":
            self.active_stressors = {}
            return True, "❄️ FORGE COOLED. All stressors cleared."
        return False, "Unknown Test. Try: TOXIN_SPILL, GRAVITY_WELL, BURNOUT, CLEAR."
    def apply_pressure(self, physics):
        if "toxin" in self.active_stressors:
            physics["counts"]["toxin"] += self.active_stressors["toxin"]
        if "drag_mult" in self.active_stressors:
            physics["narrative_drag"] *= self.active_stressors["drag_mult"]
        if "volt_add" in self.active_stressors:
            physics["voltage"] += self.active_stressors["volt_add"]
        return physics
class AntifragilityMetric:
    def __init__(self):
        self.short_window = []
        self.long_window = []
    def _window_convexity(self, window):
        if not window: return 0.0
        avg_stress = sum(s for s, g in window) / len(window)
        high_g = sum(g for s, g in window if s > avg_stress)
        low_g = sum(g for s, g in window if s <= avg_stress)
        if low_g == 0 and high_g == 0: return 0.0
        if low_g == 0: return high_g / 0.1
        return round(high_g / low_g, 2)
    def record_turn(self, voltage, drag, new_words_learned):
        stress = abs(voltage) + drag
        entry = (stress, new_words_learned)
        self.short_window.append(entry)
        if len(self.short_window) > 10: self.short_window.pop(0)
        self.long_window.append(entry)
        if len(self.long_window) > 50: self.long_window.pop(0)
    def calculate_convexity(self):
        short_cvx = self._window_convexity(self.short_window)
        long_cvx = self._window_convexity(self.long_window)
        return round(short_cvx * 0.3 + long_cvx * 0.7, 2)
class CosmicDynamics:
    def analyze_orbit(self, network, clean_words):
        if not clean_words or not network.graph:
            return "VOID_DRIFT", 0.0, "🌌 VOID: Deep Space. No connection."
        attractors = network.get_shapley_attractors()
        if not attractors:
            return "PROTO_COSMOS", 0.0, "✨ NEBULA: Not enough mass to form structure."
        basin_pulls = {k: 0.0 for k in attractors}
        active_filaments = 0
        for w in clean_words:
            if w in basin_pulls:
                basin_pulls[w] += attractors[w] * 2.0
                active_filaments += 1
            for attractor in attractors:
                if w in network.graph.get(attractor, {}).get("edges", {}):
                    basin_pulls[attractor] += attractors[attractor] * 0.5
                    active_filaments += 1
        total_pull = sum(basin_pulls.values())
        if total_pull == 0:
            return "VOID_DRIFT", 3.0, "🌌 VOID: Drifting outside the filaments."
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < BoneConfig.LAGRANGE_TOLERANCE:
                return "LAGRANGE_POINT", 0.0, f"⚖️ LAGRANGE: '{primary_node.upper()}' vs '{secondary_node.upper()}'"
        flow_ratio = active_filaments / max(1, len(clean_words))
        if flow_ratio > 0.5:
            return "WATERSHED_FLOW", 0.0, f"🌊 FLOW: Streaming towards '{primary_node.upper()}'"
        return "ORBITAL", 1.0, f"💫 ORBIT: Circling '{primary_node.upper()}'"
class ObserverEffect:
    SELF_REF_WEIGHTS = {"bone": 5.0, "amanita": 5.0, "courtyard": 3.0, "system": 1.0, "code": 0.5}
    def __init__(self):
        self.voltage_history = []
        self.ouroboros_cooldown = 0
        self.prophet_buffer = []
    def scan(self, physics, clean_words, learned_count, text):
        if self.ouroboros_cooldown > 0:
            self.ouroboros_cooldown -= 1
        else:
            score = sum(self.SELF_REF_WEIGHTS.get(w, 0) for w in clean_words)
            if (score / max(1, len(clean_words))) > 0.5:
                self.ouroboros_cooldown = 10
                return True, "🌀 OUROBOROS: We are eating our tail. Look outward, not inward."
        abstract_streak = 0
        for w in clean_words:
            if w in TheLexicon.get("abstract"):
                abstract_streak += 1
            else:
                abstract_streak = 0
            if abstract_streak >= 3:
                return True, "🍄 PROPHET: Ruminative Loop (3x Abstract). Ground yourself with a physical noun."
        volt = physics["voltage"]
        self.voltage_history.append(volt)
        if len(self.voltage_history) > 10: self.voltage_history.pop(0)
        if volt > 8.0 and learned_count == 0:
             return True, "⚠️ METRIC GAMING: High voltage, zero insight. Do real work."
        if len(self.voltage_history) >= 5:
            recent = self.voltage_history[-5:]
            variance = max(recent) - min(recent)
            if variance < 1.0 and (3.0 < sum(recent)/len(recent) < 6.0):
                return True, "⚠️ GREY GOO: Variance is zero. You are painting by numbers. Break the pattern."
        total = max(1, len(clean_words))
        heavy_density = physics["counts"]["heavy"] / total
        if heavy_density > 0.5 and total > 3:
             return True, "⚠️ FAKE WEIGHTS: Stop gaming the metrics. You are listing nouns, not building sentences."
        return False, None
class TheProjector:
    def broadcast(self, engine, m, signals, mode, clean_text):
        p = m["physics"]
        lichen_msg = signals.get("lichen")
        strat = signals.get("strat")
        title = signals.get("title")
        ops = signals.get("ops", [])
        station = signals.get("station")
        battery_log = signals.get("battery_log", [])
        lazarus_msg = signals.get("lazarus")
        spore_msg = signals.get("spore")
        omens = signals.get("omens", [])
        dream_msg = signals.get("dream")
        cosmic_msg = signals.get("cosmic")
        breach_drag = p["narrative_drag"] > BoneConfig.SURFACE_DRAG_TRIGGER
        breach_volt = abs(p["voltage"]) > BoneConfig.SURFACE_VOLT_TRIGGER
        breach_toxin = p["counts"].get("toxin", 0) >= BoneConfig.SURFACE_TOXIN_TRIGGER
        breach_event = bool(lazarus_msg or dream_msg or spore_msg or omens or ops)
        breach_atmosphere = mode != "COURTYARD"
        should_surface = (
            not BoneConfig.SILENT_MODE or
            breach_drag or breach_volt or breach_toxin or
            breach_event or breach_atmosphere
        )
        if not should_surface:
            symbol = f"{Prisma.GRN}♦{Prisma.RST}"
            if lichen_msg: symbol += f"{Prisma.GRN}⁵{Prisma.RST}"
            print(f" {symbol}")
            return
        if mode == "COURTYARD":
            print(f"\n{Prisma.OCHRE}=== THE COURTYARD ==={Prisma.RST}")
            if station: print(f" {Prisma.OCHRE}► {station['role']}: {station['msg']}{Prisma.RST}")
            print(f" {Prisma.GRY}(Strategy: {strat}){Prisma.RST}")
        elif mode == "RUPTURE":
            print(f"\n{Prisma.VIOLET}=== 💥 32-VALVE RUPTURE 💥 ==={Prisma.RST}")
            print(f" {Prisma.VIOLET}► {station['msg']}{Prisma.RST}")
        else:
            print(f"\n{Prisma.GRY}[ {Prisma.INDIGO}{title}{Prisma.GRY} | {Prisma.CYN}{strat}{Prisma.GRY} ]{'=' * 35}{Prisma.RST}")
            g = m["glass"]
            pros = g["prosody"]
            cog = g["cognition"]
            arousal_bar = f"{Prisma.RED}{'|' * int(pros['arousal'])}{Prisma.GRY}{'.' * (10 - int(pros['arousal']))}{Prisma.RST}"
            load_bar = f"{Prisma.CYN}{'|' * int(min(10, cog['cognitive_load']))}{Prisma.GRY}{'.' * (10 - int(min(10, cog['cognitive_load'])))}{Prisma.RST}"
            print(f" {Prisma.INDIGO}PULSE (System 1):{Prisma.RST} [{arousal_bar}] {Prisma.GRY}(Arousal){Prisma.RST}")
            print(f" {Prisma.INDIGO}MIND  (System 2):{Prisma.RST} [{load_bar}] {Prisma.GRY}(Load){Prisma.RST}")
            if pros["uncertainty"] > 2.0:
                 print(f" {Prisma.YEL}⚠️ HESITATION DETECTED (AU: Furrowed Brow){Prisma.RST}")
            if cog["is_autopilot"]:
                 print(f" {Prisma.MAG}💤 FATIGUE MONITOR: Semantic Drift Detected.{Prisma.RST}")
            print(f" {Prisma.MAG}COSMOS:{Prisma.RST} {cosmic_msg}")
            if station: print(f"\n {station['color']}► {station['msg']}{Prisma.RST}")
        if lazarus_msg: print(f"\n    {lazarus_msg}")
        if omens: [print(f"    {o}") for o in omens]
        if spore_msg: print(f"    {spore_msg}")
        if lichen_msg: print(f"    {Prisma.GRN}☀️ {lichen_msg}{Prisma.RST}")
        if ops: print(f"    {Prisma.VIOLET}🔪 SURGERY:{Prisma.RST} {', '.join(ops)}")
        for b in battery_log:
            if "EMERGENCY" in b or "TOXIN" in b or "NEURO" in b:
                print(f"    {b}")
            elif mode == "LABORATORY":
                print(f"    {b}")
        print(f"{Prisma.GRY}{'-' * 65}{Prisma.RST}")
class LifecycleManager:
    def __init__(self, engine):
        self.eng = engine
    def run_cycle(self, text):
        if self.eng.cmd.execute(text): return
        if self.eng.coma_turns > 0:
            self._handle_coma(text)
            return
        self.eng.tick_count += 1
        m = self.eng.phys.gaze(text)
        m["physics"] = self.eng.forge.apply_pressure(m["physics"])
        cosmic_state, drag_mod, cosmic_msg = self.eng.cosmic.analyze_orbit(self.eng.mem, m["clean_words"])
        self._apply_cosmic_physics(m["physics"], cosmic_state, drag_mod)
        metabolic_data = self._metabolize(m, cosmic_state)
        reaction_result = self._react(m, text, cosmic_state)
        if reaction_result["blocked"]:
            self._render_block(reaction_result["msg"])
            return
        self._grow(m, metabolic_data)
        self._render(m, metabolic_data, cosmic_msg, reaction_result)
    def _handle_coma(self, text):
        self.eng.coma_turns -= 1
        self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 15)
        self.eng.tick_count += 1
        dream_txt, healed_type, amt = self.eng.dreamer.rem_cycle(self.eng.trauma_accum)
        if healed_type and self.eng.trauma_accum[healed_type] > 0:
            self.eng.trauma_accum[healed_type] = max(0.0, self.eng.trauma_accum[healed_type] - amt)
            effect_msg = f"{Prisma.GRN}   >>> PROCESSED SCAR: {healed_type} (-{int(amt * 100)}%){Prisma.RST}"
        else:
            effect_msg = f"{Prisma.CYN}   >>> DEEP SLEEP. MEMORY CONSOLIDATING.{Prisma.RST}"
        print(f"\n{Prisma.INDIGO}=== 💤 HYPNAGOGIC STATE ({self.eng.coma_turns} turns remain) ==={Prisma.RST}")
        print(f"   {dream_txt}")
        print(effect_msg)
        self.eng.mem.bury(TheLexicon.clean(text), self.eng.tick_count)
        if self.eng.tick_count % 50 == 0:
             rotted = TheLexicon.atrophy(self.eng.tick_count)
             if rotted: print(f"   {Prisma.GRY}🍂 ATROPHY: Forgot {len(rotted)} stale words.{Prisma.RST}")
        print(f"{Prisma.GRY}{'-' * 65}{Prisma.RST}")
    def _apply_cosmic_physics(self, phys, state, drag_mod):
        if state == "LAGRANGE_POINT":
            phys["voltage"] += 10.0
            phys["narrative_drag"] = 0.0
        elif state == "WATERSHED_FLOW":
            phys["narrative_drag"] *= 0.1
        elif state == "VOID_DRIFT":
            phys["narrative_drag"] += drag_mod
    def _metabolize(self, m, cosmic_state):
        meta_type, meta_msg = self.eng.metabolism.digest(m["glass"], m["clean_words"])
        if meta_type == "INSULIN_SPIKE":
            m["glass"]["prosody"]["arousal"] *= 0.5
        sugar, lichen_msg = self.eng.lichen.photosynthesize(m["glass"], m["clean_words"], self.eng.tick_count)
        charged, charge_msg = self.eng.battery.absorb(m["glass"]["prosody"]["arousal"], m["clean_words"])
        spore_msg = self.eng.pollinate(m["clean_words"])
        return {
            "type": meta_type, "msg": meta_msg,
            "sugar": sugar, "lichen_msg": lichen_msg,
            "charged": charged, "charge_msg": charge_msg,
            "spore_msg": spore_msg
        }
    def _react(self, m, text, cosmic_state):
        is_unsafe, warning_msg = self.eng.sentinel.scan_road(m["glass"], m["clean_words"])
        if is_unsafe: return {"blocked": True, "msg": warning_msg}
        if cosmic_state not in ["LAGRANGE_POINT", "WATERSHED_FLOW"]:
            is_clean, div_msg, _ = self.eng.divergence.scan(m["physics"], m["clean_words"], 0, text)
            if not is_clean: return {"blocked": True, "msg": div_msg}
        passed, gym_msg = self.eng.trainer.lift(m["physics"])
        if not passed: return {"blocked": True, "msg": gym_msg}
        therm_status, therm_msg = self.eng.thermostat.check_temperature(m["clean_words"])
        if therm_status == "FAIL": return {"blocked": True, "msg": therm_msg}
        is_threat, threat_msg = self.eng.observer.scan(m["physics"], m["clean_words"], 0, text)
        if is_threat: return {"blocked": True, "msg": threat_msg}
        mirror_pass, mirror_msg = self.eng.mirror.reflect(m["physics"])
        if not mirror_pass: return {"blocked": True, "msg": mirror_msg}
        return {"blocked": False, "gym": gym_msg, "therm": (therm_status, therm_msg), "mirror": mirror_msg}
    def _grow(self, m, meta):
        self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + meta["sugar"])
        cost = 2.0 + (3.0 if m["physics"]["narrative_drag"] > 3.0 else 0) + (5.0 if m["glass"]["prosody"]["arousal"] > 8.0 else 0)
        self.eng.stamina = max(0.0, self.eng.stamina - cost)
        learned = self.eng.reinforce_salvage_words(m["clean_words"], m["physics"])
        self.eng.antifragile.record_turn(
            m["glass"]["prosody"]["arousal"],
            m["glass"]["cognition"]["cognitive_load"],
            learned
        )
        if self.eng.tick_count < 15 or self.eng.tick_count % 3 == 0:
            self._rhizome_scan(m["clean_words"])
        self._calculate_health(m["physics"])
        res = m["glass"]["resonance"]
        if res > 6.0 and m["physics"]["counts"]["toxin"] == 0:
            snapshot = {
                "resonance": res,
                "voltage": round(m["physics"]["voltage"], 2),
                "drag": round(m["physics"]["narrative_drag"], 2),
                "dominant_flavor": max(m["physics"]["counts"], key=m["physics"]["counts"].get),
                "timestamp": self.eng.tick_count
            }
            self.eng.joy_history.append(snapshot)
            print(f"{Prisma.MAG}✨ CORE MEMORY FORMED (Resonance: {res}){Prisma.RST}")
    def _rhizome_scan(self, clean_words):
        unknowns = [w for w in clean_words if not self.eng.mem.get_current_category(w) and len(w) > 3 and w not in TheLexicon.SOLVENTS]
        if unknowns:
            target = random.choice(unknowns)
            guess_cat, confidence = TheLexicon.taste(target)
            if guess_cat and confidence > 0.4:
                print(f"{Prisma.MAG}🍄 RHIZOME: I taste '{target}'. Is it {guess_cat.upper()}? (Y/N){Prisma.RST}")
                try:
                    if input(f"{Prisma.GRY}   >{Prisma.RST} ").lower().startswith("y"):
                        TheLexicon.teach(target, guess_cat, self.eng.tick_count)
                        print(f"   {Prisma.CYN}Derived: '{target}' = {guess_cat.upper()}.{Prisma.RST}")
                except: pass
    def _calculate_health(self, glass_data):
        health_impact = 0
        damage_log = []
        toxin = glass_data["counts"].get("toxin", 0)
        if toxin > 0:
            health_impact -= (5 * toxin)
            self.eng.trauma_accum["SEPTIC"] += (5 * toxin) / 100.0
            damage_log.append("SEPTIC")
        if self.eng.stamina <= 0:
            health_impact -= 10
            self.eng.trauma_accum["CRYO"] += 0.1
            self.eng.stamina = 0
            damage_log.append("CRYO")
        if glass_data["prosody"]["arousal"] > 8.0:
            health_impact -= 5
            self.eng.trauma_accum["THERMAL"] += 0.05
            damage_log.append("THERMAL")
        if glass_data["cognition"]["cognitive_load"] > 8.0:
            health_impact -= 2
            self.eng.trauma_accum["BARIC"] += 0.02
            damage_log.append("BARIC")
        self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + health_impact)
        if self.eng.health <= 0:
            self.eng.coma_turns = BoneConfig.COMA_DURATION
            self.eng.health = 20
            self.eng.trauma_accum = {k: 0.0 for k in self.eng.trauma_accum}
            death_toll = self.eng.mem.cannibalize()
            self.eng.lazarus_msg = f"{Prisma.RED}💤 LAZARUS TRIGGER: COMA. {death_toll}{Prisma.RST}"
        return damage_log
    def _render(self, m, meta, cosmic, react):
        battery_log = []
        if meta["charged"] > 0: battery_log.append(f"{Prisma.YEL}⚡ {meta['charge_msg']} (+{meta['charged']}){Prisma.RST}")
        if meta["msg"]: battery_log.append(f"{Prisma.OCHRE}🍽️ {meta['msg']}{Prisma.RST}")
        if react["gym"]: battery_log.append(f"{Prisma.GRN}{react['gym']}{Prisma.RST}")
        rup_type, rup_msg = self.eng.valve.check_pressure(m["glass"])
        if rup_type:
            mode = "RUPTURE"
            if rup_type == "THERMAL_DAMPENING":
                station = {"name": "ELOISE", "msg": rup_msg, "color": Prisma.CYN}
            elif rup_type == "DEFIBRILLATOR":
                station = {"name": "CLARENCE", "msg": rup_msg, "color": Prisma.RED}
            else:
                station = {"name": "JESTER", "msg": rup_msg, "color": Prisma.VIOLET}
            strat, title = "EMERGENCY VENT", f"VALVE OPEN: {rup_type}"
        else:
            mode, _ = self.eng.courtyard.check_atmosphere(m["physics"])
            station = self.eng.radio.tune_in(m["physics"], m["physics"]["vector"], (m["physics"]["narrative_drag"] > 3.0), self.eng.stamina)
            strat, _, title = self.eng.wise.architect(m, station, False)
        ops = []
        clean_text = m["raw_text"]
        if m["physics"]["voltage"] > 8.0:
            ops.append(f"{Prisma.VIOLET}⚡ HIGH VOLTAGE OVERRIDE: Immunity Granted.{Prisma.RST}")
        else:
            for toxin, (weight, replacement) in BoneConfig.TOXIN_MAP.items():
                pattern = re.compile(re.escape(toxin), re.IGNORECASE)
                if pattern.search(clean_text):
                    clean_text = pattern.sub(replacement, clean_text)
                    ops.append(f"'{toxin}' -> '{replacement}'")
        omens = TheOracle.triage(m["physics"], self.eng.stamina, self.eng.battery.current_charge)
        dream = self.eng.mem.tend_garden(m["clean_words"]) or (self.eng.dreamer.daydream(self.eng.mem.graph) if self.eng.chronos.tick(m["physics"], "session") else None)
        signals = {
            "lichen": meta["lichen_msg"], "strat": strat, "title": title,
            "ops": ops, "station": station, "battery_log": battery_log,
            "lazarus": getattr(self.eng, "lazarus_msg", None),
            "spore": meta["spore_msg"], "omens": omens, "dream": dream, "cosmic": cosmic
        }
        if hasattr(self.eng, "lazarus_msg"): del self.eng.lazarus_msg
        self.eng.projector.broadcast(self.eng, m, signals, mode, clean_text)
        cured = self.eng.therapy.check_progress(m["physics"], self.eng.stamina, self.eng.trauma_accum)
        for c in cured: print(f"{Prisma.OCHRE}🌸 THERAPY: {c} SCAR HEALED.{Prisma.RST}")
    def _render_block(self, msg):
        print(f"\n{Prisma.RED}{msg}{Prisma.RST}")
        print(f"{Prisma.GRY}   (Turn rejected by Lifecycle Manager.){Prisma.RST}")
class BoneAmanita:
    def __init__(self):
        self.projector = TheProjector()
        self.forge = TheForge()
        self.courtyard = CourtyardInterface()
        self.valve = ValveSystem()
        self.phys = EmpatheticGlass()
        self.sentinel = TheSentinel()
        self.resonator = TheResonator()
        self.lichen = LichenSymbiont()
        self.battery = LeyLineBattery()
        self.wise = ApeirogonResonance()
        self.radio = FrequencyModulator()
        self.mem = MycelialNetwork()
        self.mem.autoload_last_spore()
        self.chronos = ChronoStream()
        self.therapy = TherapyProtocol()
        self.kintsugi = KintsugiProtocol()
        self.dynamics = TemporalDynamics()
        self.tracer = ViralTracer(self.mem)
        self.dreamer = DreamEngine()
        self.trainer = ResistanceTrainer()
        self.thermostat = HubThermostat()
        self.mirror = MirrorGraph()
        self.antifragile = AntifragilityMetric()
        self.divergence = DivergenceEngine()
        self.metabolism = MetabolicEngine()
        self.cosmic = CosmicDynamics()
        self.observer = ObserverEffect()
        self.cmd = CommandProcessor(self)
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
        self.joy_history = []
        self.health = self.mem.session_health if self.mem.session_health is not None else BoneConfig.MAX_HEALTH
        self.stamina = self.mem.session_stamina if self.mem.session_stamina is not None else BoneConfig.MAX_STAMINA
        self.coma_turns = 0
        self.tick_count = 0
        self.life = LifecycleManager(self)
    def reinforce_salvage_words(self, clean_words, phys):
        if phys.get("symbolic_state") != "SALVAGE": return 0
        heavy = [w for w in clean_words if w in TheLexicon.get("heavy")]
        kinetic = [w for w in clean_words if w in TheLexicon.get("kinetic")]
        for w in heavy[:3]: TheLexicon.teach(w, "heavy", self.tick_count)
        for w in kinetic[:2]: TheLexicon.teach(w, "kinetic", self.tick_count)
        return len(heavy) + len(kinetic)
    def pollinate(self, current_words):
        if self.stamina < 30 or not self.mem.graph: return None
        candidates = []
        for w in current_words:
            if w in self.mem.graph:
                edges = self.mem.graph[w]["edges"]
                if edges:
                    best = max(edges, key=edges.get)
                    if best not in current_words: candidates.append((best, edges[best]))
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return f"{Prisma.MAG}🍄 MYCELIAL SPORE: '{candidates[0][0]}'{Prisma.RST}"
        return None
    def process(self, text):
        self.life.run_cycle(text)
if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.GRN}>>> BONEAMANITA v6.1 {Prisma.RST}")
    print(f"{Prisma.GRY}System: Hysteresis Active. Bleed Detection Optimized. Neuroplasticity Engaged.{Prisma.RST}")
    try:
        while True:
            try:
                u = input(f"{Prisma.WHT}>{Prisma.RST} ")
            except EOFError:
                break
            if u.lower() in ["exit", "quit", "/exit"]:
                print(f"{Prisma.YEL}Initiating voluntary shutdown...{Prisma.RST}")
                break
            eng.process(u)
    except KeyboardInterrupt:
        print(f"\n{Prisma.YEL}⚠️ INTERRUPT SIGNAL DETECTED.{Prisma.RST}")
    except (RuntimeError, ValueError, TypeError) as runtime_err:
        print(f"\n{Prisma.RED}💥 SYSTEM ERROR: {runtime_err}{Prisma.RST}")
    except Exception as unexpected_err:
        print(f"\n{Prisma.RED}💥 UNEXPECTED CRITICAL FAILURE: {unexpected_err}{Prisma.RST}")
    finally:
        print(f"{Prisma.CYN}[PRESERVATION]: Writing neural pathways to disk...{Prisma.RST}")
        learned_mutations = {k: list(v.keys()) for k, v in TheLexicon.LEARNED_VOCAB.items()}
        saved_file = eng.mem.save(
            health=eng.health,
            stamina=eng.stamina,
            mutations=learned_mutations,
            isotopes=eng.battery.isotopes,
            trauma_accum=eng.trauma_accum,
            joy_history=eng.joy_history
        )
        eng.mirror.profile.save()
        print(f"{Prisma.CYN}[PROFILE]: User vector saved.{Prisma.RST}")
        if saved_file:
            print(f"{Prisma.GRN}>>> MEMORY SECURED: {saved_file}{Prisma.RST}")
        else:
            print(f"{Prisma.RED}>>> MEMORY WRITE FAILED.{Prisma.RST}")
        print("Terminated.")
