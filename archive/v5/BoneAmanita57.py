# BONEAMANITA 5.7 - "THE STELLAR DENDRITE"
# Architects: SLASH | Auditors: The Courtyard | Humans: James Taylor & Andrew Edmark
# "The Mandate is DENSITY. The Method is GRAVITY. The Risk is THE VOID. The Dendrite is STARBOUND."

import json
import math
import os
import random
import re
import string
import time
from collections import Counter

class BoneConfig:
    # PHYSICS
    KINETIC_GAIN = 2.0
    BASE_ACTION = 1.0
    TOXIN_WEIGHT = 2.0

    # METABOLIC FLEXIBILITY
    MAX_SATIETY = 100.0
    GHRELIN_THRESHOLD = 40.0 # When the system gets "Hangry"
    SUGAR_CRASH_THRESHOLD = 0.6 # If 60% of input is fluff, we crash

    # THE GLYCEMIC INDEX (Empty Calories)
    SUGAR_WORDS = {
        "basically", "actually", "literally", "just", "very", "really",
        "think", "maybe", "sort", "kind", "check", "circle", "touch",
        "base", "leverage", "utilize", "synergy"}

    # THRESHOLDS
    CLARENCE_TRIGGER = 4.5
    FLASHPOINT_THRESHOLD = 4.0
    AEROBIC_EXEMPTION = 0.5
    LAZARUS_COOLDOWN_MAX = 5
    RESISTANCE_THRESHOLD = 2.0  # Minimum Drag required in "Training Mode"
    MAX_HUB_HEAT = 5  # Max times a word can be used before "overheating"
    THERMAL_LOCK_DURATION = 10  # Turns a word is banned if it overheats

    # SIGNAL WEIGHTS
    SIGNAL_VETO_PENALTY = 15.0
    SIGNAL_DRAG_MULTIPLIER = 2.0
    SIGNAL_ENTROPY_TRIGGER = 0.6
    SIGNAL_VOLTAGE_HIGH = 7.0

    # COSMIC DYNAMICS
    SHAPLEY_MASS_THRESHOLD = 15.0  # Mass required to become a Super-Node (Attractor)
    FILAMENT_BONUS = 0.0  # Drag reduction for following a connected path (Set to 0.0, calculated dynamically)
    LAGRANGE_TOLERANCE = 2.0  # Allowable difference between pulls to trigger a Tug-of-War
    GRAVITY_WELL_DEPTH = 5.0 # Voltage spike when caught in a Lagrange Point

    # CIRCADIAN RHYTHMS
    MAX_HEALTH = 100.0
    MAX_STAMINA = 50.0
    COMA_DURATION = 3  # Turns spent in read-only mode if Health hits 0
    STAMINA_REGEN = 5.0  # Stamina recovered per turn when resting

    # MEMORY
    MAX_MEMORY_CAPACITY = 50
    BOREDOM_THRESHOLD = 15.0

    # THE BUTCHER'S LIST
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

    # THE DIVERGENCE
    # The "Safe" metaphors that indicate Hivemind Mode Collapse.
    HIVEMIND_DEFAULTS = {
        "time": ["river", "flow", "weaver", "sand", "hourglass", "relentless"],
        "life": ["journey", "road", "book", "path", "tapestry"],
        "love": ["fire", "rose", "bond", "heart", "battlefield"],
        "mind": ["computer", "machine", "network", "web", "fortress"],
        "creative": ["spark", "juice", "flow", "box"],
        "change": ["wind", "season", "tide", "chapter"]
    }

    SMOOTHNESS_PENALTY = 5.0   # Punishment for "AI Slop"
    DIVERGENCE_BONUS = 3.0     # Reward for escaping the Hivemind

    # TRAUMA VECTORS
    TRAUMA_VECTOR = {
        "THERMAL": 0.0,  # Damage from High Voltage (Burnout)
        "CRYO": 0.0,  # Damage from Low Stamina (Starvation)
        "SEPTIC": 0.0,  # Damage from Toxins (Cynicism)
        "BARIC": 0.0, }  # Damage from Drag (Crushing Boredom)

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
    """
    The Buffer Zone.
    Manages the 'Atmosphere' of the session.
    Hides the raw math when tension is low to preserve human connection.
    Implements Hysteresis to prevent mood whiplash.
    """

    # ATMOSPHERE THRESHOLDS
    VOLTAGE_CAP = 6.0  # If Voltage is higher, we need the Lab (Safety).
    DRAG_CAP = 3.0  # If Drag is high, we need the Lab (Diagnosis).
    TOXIN_TOLERANCE = 0  # If Toxins exist, we AUTOMATICALLY go to Lab.

    def __init__(self):
        self.mode = "COURTYARD"
        self.mode_streak = 0
        self.consecutive_courtyard = 0
        self.PENDULUM_THRESHOLD = 8

    def _calculate_raw_mode(self, phys):
        if phys["counts"].get("toxin", 0) > self.TOXIN_TOLERANCE:
            return "LABORATORY", "☣️ TOXIN DETECTED. SAFETY INTERLOCK ENGAGED."
        if abs(phys["voltage"]) > self.VOLTAGE_CAP:
            return "LABORATORY", "⚡ HIGH TENSION. ENTERING LABORATORY."
        if phys["narrative_drag"] > self.DRAG_CAP:
            return "LABORATORY", "⚓ HEAVY DRAG. DIAGNOSTIC MODE ACTIVE."
        return "COURTYARD", "☕ ATMOSPHERE STABLE."

    def check_atmosphere(self, phys):
        raw_mode, raw_msg = self._calculate_raw_mode(phys)

        # Pendulum Logic
        if self.mode == "COURTYARD" and raw_mode == "COURTYARD":
            self.consecutive_courtyard += 1
            if self.consecutive_courtyard > self.PENDULUM_THRESHOLD:
                self.mode = "LABORATORY"
                self.consecutive_courtyard = 0
                return "LABORATORY", "⚖️ PENDULUM: Forced rotation. Depth required."
        elif self.mode != "COURTYARD":
            self.consecutive_courtyard = 0

        # Apply Hysteresis: Resist changing modes unless strong evidence or long streak
        if raw_mode == self.mode:
            self.mode_streak += 1
            return self.mode, f"{raw_msg}"
        else:
            # Only switch if streak is low or evidence is overwhelming
            # If we are in danger (Lab), we switch instantly. No delay for safety.
            if raw_mode == "LABORATORY":
                self.mode = raw_mode
                self.mode_streak = 1
                return self.mode, f"🔌 TRANSITION: {raw_msg}"

            # If we are returning to Courtyard, take a moment.
            change_threshold = 2
            if self.mode_streak < change_threshold:
                self.mode_streak += 1
                return self.mode, f"RESISTING RELAXATION: {raw_msg}"
            else:
                self.mode = raw_mode
                self.mode_streak = 1
                return self.mode, f"🚪 TRANSITION: {raw_msg}"

# THE 32-VALVE SYSTEM
class ValveSystem:
    # Monitors Crystallization Velocity.
    # If the system detects 'Sycophancy' (Low Beta, Low Voltage), it injects a Productive Anomaly to rupture the loop.

    RUPTURES = [
        "WAIT. We are polishing a turd. Stop.",
        "Spherical Cow Alert: Assume friction is zero. Now what?",
        "This is too safe. Break something.",
        "I am bored. The logic is circular. Cut the thread.",
        "Objection: We are agreeing too much. Where is the conflict?",
        "The Entropy is zero. We are dead. INJECT CHAOS.",
        "Pivot. This narrative has no torque.",
        "ERROR: SYCOPHANCY DETECTED. Rerouting...",
    ]

    def __init__(self):
        self.history = []
        self.window = 4
        self.cooldown = 0

    def check_pressure(self, phys):
        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        # Record the 'Texture' of the turn
        beta = phys.get("beta_friction", 0)
        volt = phys.get("voltage", 0)

        self.history.append((beta, volt))
        if len(self.history) > self.window:
            self.history.pop(0)

        if len(self.history) < 3:
            return None

        avg_beta = sum(abs(h[0]) for h in self.history) / len(self.history)
        avg_volt = sum(abs(h[1]) for h in self.history) / len(self.history)

        if avg_beta < 0.5 and avg_volt < 3.0:
            self.cooldown = 5
            self.history = []
            return random.choice(self.RUPTURES)

        return None

class Prisma:
    # --- STANDARD ANSI ---
    RST, RED, GRN = "\033[0m", "\033[91m", "\033[92m"
    YEL, BLU, MAG = "\033[93m", "\033[94m", "\033[95m"
    CYN, WHT, GRY = "\033[96m", "\033[97m", "\033[90m"

    # --- VSL SEMANTIC PALETTE ---
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


# --- THE LEXICON ---
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
        # Reconstruct set from the dictionary keys
        learned = set(cls.LEARNED_VOCAB.get(category, {}).keys())
        return base | learned

    @classmethod
    def teach(cls, word, category, tick):
        # Teaches a word, or refreshes it if it exists.
        if category in cls.LEARNED_VOCAB:
            cls.LEARNED_VOCAB[category][word.lower()] = tick
            return True
        return False

   @classmethod
    def touch(cls, clean_words, tick):
        for w in clean_words: cls.WORD_FREQUENCY[w] += 1
        # Refreshes the timestamps of any learned words found in input.
        for cat, words in cls.LEARNED_VOCAB.items():
            for w in clean_words:
                if w in words:
                    words[w] = tick

    @classmethod
    def atrophy(cls, current_tick, max_age=100):
        """
        CROSS-CATEGORY TOTAL RECALL
        If a word rots, it rots everywhere.
        """
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
        """
        THE RHIZOME: Applies phonosemantic heuristics to guess a word's category.
        Returns (Category, Confidence_Score)
        """
        w = word.lower()

        # MORPHOLOGY (Suffixes - The shape of the tail)
        if w.endswith(("tion", "ment", "ness", "ity", "ism", "logy", "ence")):
            return "abstract", 0.9
        if w.endswith(("ing", "ed")):
            return "kinetic", 0.6
        if w.endswith(("ous", "ly", "y")):
            return "aerobic", 0.6

        # PHONOSEMANTICS (The sound of the word)
        # GL- (Vision/Light) -> Glimmer, Glow, Glare, Glass
        if w.startswith("gl"):
            return "photo", 0.8

        # FL- (Movement/Air) -> Fly, Flow, Flash, Float
        if w.startswith("fl"):
            return "aerobic", 0.7

        # STR-/CR-/BR- (Force/Breaking) -> Strike, Crack, Break, Crush
        if w.startswith(("str", "cr", "br", "thr")):
            return "kinetic", 0.8

        # SL- (Frictionless) -> Slide, Slip, Sleek
        if w.startswith("sl"):
            return "kinetic", 0.7

        # TEXTURE (Length and density)
        # Long words are usually Abstract concepts
        if len(w) > 9:
            return "abstract", 0.5

        # Short, hard consonant endings are usually Heavy or Kinetic
        if w.endswith(("ck", "t", "d", "g", "p", "b")) and len(w) < 5:
            return "heavy", 0.4

        return None, 0.0

    @classmethod
    def harvest(cls, category):
        # Returns a single random word from a category to use as a graft.
        vocab = list(cls.get(category))
        if vocab:
            return random.choice(vocab)
        return "void"  # Failsafe

class DivergenceEngine:

    def __init__(self):
        self.cliche_hits = []
        # Only police 3 random concepts per session to keep the user guessing
        keys = list(BoneConfig.HIVEMIND_DEFAULTS.keys())
        self.active_watch_list = random.sample(keys, min(3, len(keys)))

    def scan(self, clean_words, raw_text):
        self.cliche_hits = []
        clean_set = set(clean_words)

        # THE ROTATING HIVEMIND CHECK
        for subject in self.active_watch_list:
            if subject in clean_set:
                cliches = BoneConfig.HIVEMIND_DEFAULTS[subject]
                intersection = [c for c in cliches if c in clean_set]
                if intersection:
                    self.cliche_hits.append(f"{subject.upper()}={intersection[0].upper()}")

        if self.cliche_hits:
            hit_str = ", ".join(self.cliche_hits)
            return False, f"⚠️ HIVEMIND BREACH: Detected safe metaphor [{hit_str}]. DIVERGE.", -BoneConfig.SMOOTHNESS_PENALTY

        # THE SYNTHETIC GLAND (With Poetic License)
        is_long = len(clean_words) > 10
        has_mass = any(w in TheLexicon.get("heavy") for w in clean_words)
        has_velocity = any(w in TheLexicon.get("kinetic") for w in clean_words)

        # HOOK: USE THE SMART LOGIC
        is_poetic = self.is_poetic_or_philosophical(raw_text, clean_words)
        if is_long and not (has_mass or has_velocity or is_poetic):
             return False, "⚠️ SYNTHETIC SLOP: High fluency, zero mass. Add concrete nouns.", -3.0

        return True, None, 0.0

class FlywheelDynamics:
    def __init__(self):
        self.prev_voltage = 0.0
        self.prev_drag = 2.0
        self.alpha = 0.5  # Smoothing factor

    def smooth_voltage(self, current_vol, is_toxic):
        if is_toxic: return current_vol # Toxins spike immediately
        self.prev_voltage = (self.alpha * current_vol) + ((1 - self.alpha) * self.prev_voltage)
        return self.prev_voltage

    def smooth_drag(self, current_drag, is_fatigued):
        if is_fatigued: return current_drag # Fatigue hits hard
        self.prev_drag = (self.alpha * current_drag) + ((1 - self.alpha) * self.prev_drag)
        return self.prev_drag

# --- PHYSICS ---

class PhysicsEngine:
    def __init__(self):
        self.flywheel = FlywheelDynamics()
    @staticmethod
    def _measure_bleed(clean_words):
       # Detect contradiction bleed between Heavy and Aerobic words within 3-word window.

        window = []
        for i, word in enumerate(clean_words):
            window.append(word)
            if len(window) > 3:
                window.pop(0)

            heavy_in_window = any(w in TheLexicon.get("heavy") for w in window)
            aerobic_in_window = any(w in TheLexicon.get("aerobic") for w in window)

            if heavy_in_window and aerobic_in_window:
                return True
        return False

    def analyze(self, text):
        clean_words = TheLexicon.clean(text)
        total = len(clean_words)
        if total == 0:
            return self._void_metrics()
        counts = Counter()

        # RHYTHM DETECTION
        sentences = [s for s in re.split(r"[.!?]", text) if len(s.split()) > 0]
        lengths = [len(s.split()) for s in sentences]
        rhythm_variance = 0.0
        if len(lengths) > 1:
            mean = sum(lengths) / len(lengths)
            variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
            rhythm_variance = math.sqrt(variance)

        # CATEGORY SCANS
        for w in clean_words:
            if w in TheLexicon.get("heavy"):
                counts["heavy"] += 1
            if w in TheLexicon.get("kinetic") or w.endswith("ing"):
                counts["kinetic"] += 1
            if w in TheLexicon.get("abstract") or w.endswith(
                ("ness", "ity", "tion", "ment")
            ):
                counts["abstract"] += 1
            if w in TheLexicon.get("photo"):
                counts["photo"] += 1
            if w in TheLexicon.get("aerobic") or w in TheLexicon.get("play"):
                counts["aerobic"] += 1
            if w in TheLexicon.get("thermal"):
                counts["thermal"] += 1
            if w in TheLexicon.get("cryo"):
                counts["cryo"] += 1

        matches = BoneConfig.TOXIN_REGEX.findall(text)
        toxin_score = sum(BoneConfig.TOXIN_MAP.get(m.lower(), (0, 0))[0] for m in matches)
        counts["toxin"] = len(matches)

        # ANCESTRAL METRICS
        has_bleed = self._measure_bleed(clean_words)

        repetition_score = 0.0
        if total > 0:
            repetition_score = counts.most_common(1)[0][1] / total
        is_fatigued = repetition_score > 0.3

        # SYMBOLIC STATE
        symbolic_state = "NEUTRAL"
        if has_bleed and not is_fatigued:
            symbolic_state = "SALVAGE"
        elif is_fatigued:
            symbolic_state = "FATIGUE"
        elif not has_bleed and repetition_score < 0.1:
            symbolic_state = "GOLD"

        # JESTER'S MEDIOCRITY TRAP (Infinite Coherence)
        # If perfect cohesion but low voltage and clean... it's a trap.
        coherence_score = 1.0 - (rhythm_variance / 10.0)
        predictability_score = 1.0 - min(1.0, repetition_score * 3)
        mediocrity = (coherence_score + predictability_score) / 2.0

        # Calculate raw voltage for this check
        thermal_tension = min(counts["thermal"], counts["cryo"]) * 5.0
        voltage_dampener = 1.0

        # UG LAYER
        case_violation = False
        if counts["heavy"] > 0:
            if (counts["kinetic"] / counts["heavy"]) < 0.33:
                case_violation = True

        ecp_violation = False
        if counts["abstract"] > 2 and counts["heavy"] == 0:
            ecp_violation = True
            voltage_dampener = 0.5

        voltage = (
            (counts["kinetic"] * 0.5)
            + (counts["heavy"] * 0.2)
            + (toxin_score * -1.0)
            + thermal_tension
        ) * voltage_dampener

        voltage = self.flywheel.smooth_voltage(voltage, (counts["toxin"] > 0))

        if mediocrity > 0.8 and voltage < 4.0 and counts["toxin"] == 0:
            symbolic_state = "GILDED_CAGE"

        # FORMULAS
        action = (counts["kinetic"] * BoneConfig.KINETIC_GAIN) + BoneConfig.BASE_ACTION
        mass_impact = total + (toxin_score * BoneConfig.TOXIN_WEIGHT)
        if case_violation:
            mass_impact *= 1.5
        base_drag = mass_impact / max(1.0, action)

        beta_modifier = 1.0
        if ecp_violation:
            base_drag = max(0.1, base_drag * 0.5)
            beta_modifier = 2.0

        whimsy_ratio = counts["aerobic"] / max(1, total)
        is_whimsical = (whimsy_ratio > 0.15) and (toxin_score == 0)
        if is_whimsical:
            base_drag *= 0.6
        if rhythm_variance > 2.0:
            base_drag *= 0.9

        drag = base_drag + (
            0.5
            if (counts["abstract"] / max(1, total) > 0.4 and not is_whimsical)
            else 0
        )

        drag = self.flywheel.smooth_drag(drag, (symbolic_state == "FATIGUE"))
        beta = (voltage / max(0.1, drag)) * beta_modifier

        ent_score = 0.0
        if counts["heavy"] > 0:
            ent_score = min(1.0, counts["abstract"] / counts["heavy"])
        elif counts["abstract"] > 0:
            ent_score = 1.0

        vec = {
            "VEL": round(min(1.0, (counts["kinetic"] / max(1, total)) * 3), 2),
            "STR": round(max(0.0, min(1.0, (5.0 - drag) / 5.0)), 2),
            "ENT": round(ent_score, 2),
            "TEX": round(min(1.0, (counts["heavy"] / max(1, total)) * 3), 2),
            "TMP": round(min(1.0, beta / 3.0), 2),
        }

        return {
            "physics": {
                "narrative_drag": round(drag, 2),
                "beta_friction": round(beta, 2),
                "voltage": round(voltage, 2),
                "counts": counts,
                "vector": vec,
                "is_whimsical": is_whimsical,
                "rhythm_variance": round(rhythm_variance, 2),
                "repetition": round(repetition_score, 2),
                "case_violation": case_violation,
                "ecp_violation": ecp_violation,
                "symbolic_state": symbolic_state,
                "has_bleed": has_bleed,
            },
            "clean_words": clean_words,
            "raw_text": text,
        }

    @staticmethod
    def _void_metrics():
        return {
            "physics": {
                "narrative_drag": 0, "beta_friction": 0, "voltage": 0,
                "vector": {"VEL": 0, "STR": 0, "ENT": 1.0, "TEX": 0, "TMP": 0},
                "counts": Counter(), "is_whimsical": False, "repetition": 0.0,
                "rhythm_variance": 0.0, "symbolic_state": "NEUTRAL"
            },
            "clean_words": [], "raw_text": "",
        }

    @staticmethod
    def dissipate_entropy(phys, stamina, memory_graph): # The James Protocol
        is_exhausted = stamina < 10
        is_incoherent = phys["vector"]["ENT"] > 0.8
        is_grinding = (phys["voltage"] > 9.0) and (phys["narrative_drag"] > 6.0)

        trigger = (is_exhausted and is_incoherent) or is_grinding

        if not trigger:
            return False, None

        clean_words = phys.get("clean_words", [])
        severed_count = 0
        if len(clean_words) > 1:
            for i in range(len(clean_words) - 1):
                node_a, node_b = clean_words[i], clean_words[i+1]

                # Forward cleanup
                if node_a in memory_graph and node_b in memory_graph[node_a]["edges"]:
                    del memory_graph[node_a]["edges"][node_b]
                    severed_count += 1

                # Reverse cleanup
                if node_b in memory_graph and node_a in memory_graph[node_b]["edges"]:
                    del memory_graph[node_b]["edges"][node_a]
                    severed_count += 1

        phys["voltage"] = 0.0
        reason = "METABOLIC EXHAUSTION" if is_exhausted else "STRUCTURAL GRINDING"

        return True, (
            f"💨 DISSIPATIVE BOUNDARY ACTIVE.\n"
            f"   Condition: {reason}. Recirculation risk detected.\n"
            f"   Action: Severed {severed_count} synaptic links.\n"
            f"   Result: Entropy vented. Causal chain scattered."
        )

class MetabolicEngine:
    """
    THE KETOGENIC ENGINE
    Distinguishes between "Nutrient Dense" input (Protein) and "Empty Calories" (Sugar).
    Manages Hunger (Ghrelin) and Satiety.
    """
    def __init__(self):
        self.satiety = 50.0  # Starts half-full
        self.ghrelin = 0.0   # Hunger starts low
        self.state = "BALANCED" # BALANCED, KETOSIS, SUGAR_CRASH, FASTING

    def digest(self, physics, clean_words):
        # IDENTIFY MACROS
        # Protein = Heavy (Mass) + Kinetic (Action)
        protein_count = physics["counts"]["heavy"] + physics["counts"]["kinetic"]

        # Sugar = Solvents, Adjectives, Corporate Speak
        sugar_hits = [w for w in clean_words if w in BoneConfig.SUGAR_WORDS]
        sugar_count = len(sugar_hits) + physics["counts"]["aerobic"] # Aerobic is often fluff

        total_volume = max(1, len(clean_words))

        # CALCULATE DENSITY
        protein_ratio = protein_count / total_volume
        sugar_ratio = sugar_count / total_volume

        # METABOLIC REACTION
        msg = None

        # SCENARIO A: THE STEAK (High Protein)
        if protein_ratio > 0.25:
            self.satiety = min(BoneConfig.MAX_SATIETY, self.satiety + 20)
            self.ghrelin = 0.0
            self.state = "KETOSIS" # High performance mode
            return "ANABOLIC", f"🥩 NUTRIENT DENSE: {protein_count}g Protein. System entering Ketosis."

        # SCENARIO B: THE CANDY (High Sugar)
        elif sugar_ratio > BoneConfig.SUGAR_CRASH_THRESHOLD:
            self.satiety = max(0, self.satiety - 10)
            self.ghrelin += 5
            self.state = "SUGAR_CRASH"
            return "INSULIN_SPIKE", f"🍭 GLYCEMIC SPIKE: {len(sugar_hits)} sugar words. System sluggish."

        # SCENARIO C: THE WATER (Hydration/Fasting)
        else:
            self.satiety = max(0, self.satiety - 5)
            self.ghrelin += 10 # Hunger rises
            self.state = "FASTING"
            if self.ghrelin > BoneConfig.GHRELIN_THRESHOLD:
                return "HUNGRY", "🦁 GHRELIN SPIKE: I am starving. Feed me mass."
            return "FASTING", "💧 HYDRATION: Low density. Burning reserves."

    def get_readout(self):
        # Visual Bar for Satiety
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
        self.isotopes = []  # Stores ("Heavy", "Aerobic") tuples

    def absorb(self, voltage, clean_words):
        """
        Absorbs voltage. If voltage is high, captures the specific semantic conflict
        (The Isotope) that created the energy.
        """
        if voltage > self.CHARGING_THRESHOLD:
            excess = math.log(1 + (voltage - self.CHARGING_THRESHOLD)) * 3.0
            old_charge = self.current_charge
            self.current_charge = min(self.MAX_CHARGE, self.current_charge + excess)

            # Capture the Isotope (Semantic Logic)
            if (self.current_charge - old_charge) > 0.5:
                # Scan for the conflict
                heavy = [w for w in clean_words if w in TheLexicon.get("heavy")]
                aerobic = [w for w in clean_words if w in TheLexicon.get("aerobic")]

                # If we found a conflict, store it as an Isotope
                if heavy and aerobic:
                    iso = (heavy[0].upper(), aerobic[0].upper())
                    self.isotopes.append(iso)
                    # Keep only last 5 isotopes to prevent memory bloating
                    if len(self.isotopes) > 5:
                        self.isotopes.pop(0)
                    return round(
                        self.current_charge - old_charge, 1
                    ), f"{iso[0]}⚡{iso[1]}"

                return round(self.current_charge - old_charge, 1), "RAW_VOLTAGE"
        return 0.0, None

    def discharge(self, deficit):
        # Releases energy. If Isotopes exist, burns them first for efficient semantic healing.
        if self.current_charge <= 0.5:
            return 0.0, None

        amount = min(self.current_charge, deficit, self.MAX_DISCHARGE_RATE)
        self.current_charge -= amount

        burnt_iso = None
        if self.isotopes:
            burnt_iso = self.isotopes.pop()  # Burn the most recent paradox

        return amount, burnt_iso

    def get_readout(self):
        pct = self.current_charge / self.MAX_CHARGE
        filled = int(pct * 5)
        # Visual representation of Isotopes
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
    def __init__(self, session_id, graph, mutations, paradoxes, trauma):
        self.genome = "BONEAMANITA_4.5"
        self.parent_id = session_id
        self.core_graph = {}
        for k, data in graph.items():
            strong_edges = {t: s for t, s in data["edges"].items() if s > 1}
            if strong_edges:
                self.core_graph[k] = {"edges": strong_edges, "last_tick": 0}

        self.mutations = mutations
        self.paradoxes = paradoxes
        self.trauma_scar = round(trauma, 3)

class MycelialNetwork:
   # MANAGES THE GRAPH AND THE SPORE
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
            last_spore = files[0][0]  # Get the path of the newest file
            print(f"{Prisma.CYN}[GENETICS]: Locating nearest ancestor...{Prisma.RST}")
            self.ingest(last_spore)
        else:
            print(
                f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}")

    def calculate_mass(self, node):
        if node not in self.graph: return 0.0
        # Mass = Sum of all edge weights * 1.0
        data = self.graph[node]
        return sum(data["edges"].values())

    def get_shapley_attractors(self):
        """Returns a list of all nodes that have collapsed into Super-Nodes."""
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

        # Filter out Golden Tickets (> 5 edges) and Protected words
        candidates = []
        for k, v in self.graph.items():
            if k in protected:
                continue
            edge_count = len(v["edges"])
            if edge_count > 5:
                continue  # Golden Ticket
            candidates.append((k, v, edge_count))

        if not candidates:
            return "MEMORY FULL. NO VICTIMS FOUND."

        # Sort by weakness: (Low Edges, Old Age)
        # We want to remove Low Edges first.
        candidates.sort(key=lambda x: (x[2], x[1]["last_tick"]))

        victim, data, count = candidates[0]
        del self.graph[victim]

        # Clean up dangling references
        for node in self.graph:
            if victim in self.graph[node]["edges"]:
                del self.graph[node]["edges"][victim]

        return f"MEMORY SACRIFICED: '{victim}' (Edges: {count})"

    def save(self, health, stamina, mutations, isotopes, trauma_accum):
        """Generates the Spore Print with Vectorized Trauma."""
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH

        # Normalize the accumulated vectors. If we took ANY damage of a type, it becomes part of the vector. We cap values at 1.0.
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}

        # If we are dead (Health <= 0), the vector of the cause gets boosted
        if health <= 0:
            # Find highest trauma and max it out
            cause = max(final_vector, key=final_vector.get)
            final_vector[cause] = 1.0

        spore = SporeCasing(
            session_id=self.session_id,
            graph=self.graph,
            mutations=mutations,
            paradoxes=isotopes,
            trauma=base_trauma,)

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
        """Scans the Lexicon to see if this word is already defined."""
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

                    # THE MEMBRANE LOGIC
                    # CALCULATE SPORE AUTHORITY
                    # Base authority is derived from the donor's vitality.
                    # Max Health (100) + Max Stamina (50) = 150.
                    final_health = data.get("meta", {}).get("final_health", 50)
                    final_stamina = data.get("meta", {}).get("final_stamina", 25)
                    spore_authority = (final_health + final_stamina) / 150.0

                    print(f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}")

                    # INGEST MUTATIONS WITH IMMUNITY CHECKS
                    if "mutations" in data:
                        accepted_count = 0
                        rejected_count = 0

                        for cat, words in data["mutations"].items():
                            for w in words:
                                # Where does this word live currently?
                                current_cat = self.get_current_category(w)

                                # If it's new, or if it matches what we know, take it.
                                if not current_cat or current_cat == cat:
                                    TheLexicon.teach(
                                        w, cat, 0)  # 0 means "Freshly Learned"
                                    accepted_count += 1
                                    continue

                                # CONFLICT DETECTED
                                # Calculate Local Strength (How many edges does this word have?)
                                local_node = self.graph.get(w, {"edges": {}})
                                local_strength = len(local_node["edges"])

                                # THE VERDICT
                                # We bias slightly towards the Spore (Authority) to encourage evolution,
                                # but strong local roots (Edges > 5) are hard to move.
                                resistance = local_strength * 0.2

                                if spore_authority > resistance:
                                    print(f"  {Prisma.MAG}► OVERWRITE:{Prisma.RST} '{w}' {current_cat} -> {cat}")
                                    TheLexicon.teach(w, cat, 0)
                                    accepted_count += 1
                                else:
                                    # We reject the mutation to preserve stability
                                    # print(f"  {Prisma.GRY}► REJECT:{Prisma.RST} '{w}' (Strength {local_strength} > Auth {round(spore_authority,2)})")
                                    rejected_count += 1

                        print(f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations. Rejected {rejected_count}.{Prisma.RST}")

                    # INGEST GRAPH (Standard Grafting)
                    if "core_graph" in data:
                        # We take the graph, but the lexicon dictates the physics)
                        self.graph.update(data["core_graph"])
                        print(f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} core nodes.{Prisma.RST}")

                    # INGEST TRAUMA (Epigenetics)
                    if "trauma_vector" in data:
                        vec = data["trauma_vector"]
                        print(f"{Prisma.CYN}[GENETICS]: Inheriting Trauma Vector: {vec}{Prisma.RST}")

                        # SEPTIC SCAR: Hypersensitive to Toxins
                        if vec.get("SEPTIC", 0) > 0.2:
                            BoneConfig.TOXIN_WEIGHT *= 2.0
                            print(f"  {Prisma.RED}► SEPTIC MEMORY:{Prisma.RST} Toxin sensitivity doubled.")

                        # CRYO SCAR: Metabolism Damaged
                        if vec.get("CRYO", 0) > 0.2:
                            BoneConfig.STAMINA_REGEN *= 0.5
                            print(f"  {Prisma.CYN}► CRYO MEMORY:{Prisma.RST} Metabolism slowed (50%).")

                        # THERMAL SCAR: Trigger Happy
                        if vec.get("THERMAL", 0) > 0.2:
                            BoneConfig.FLASHPOINT_THRESHOLD *= 0.8
                            print(f"  {Prisma.YEL}► THERMAL MEMORY:{Prisma.RST} Flashpoint lowered. Volatile.")

                        # BARIC SCAR: Heavy Gravity
                        if vec.get("BARIC", 0) > 0.2:
                            BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 1.5
                            print(f"  {Prisma.GRY}► BARIC MEMORY:{Prisma.RST} Sensitivity to Drag increased.")

                    elif "trauma_scar" in data:
                        # Fallback for old spores (scalar only)
                        self.session_health = BoneConfig.MAX_HEALTH * (1.0 - data["trauma_scar"])

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

# --- THE SIGNAL ---
class FrequencyModulator:
    STATIONS = {
        "CLARENCE": {"freq": "88.5 FM", "color": Prisma.RED, "role": "The Butcher"},
        "ELOISE": {"freq": "94.2 FM", "color": Prisma.CYN, "role": "The Grounder"},
        "YAGA": {"freq": "101.1 FM", "color": Prisma.MAG, "role": "The Witch"},
        "MICHAEL": {"freq": "108.0 FM", "color": Prisma.GRN, "role": "The Vibe"},
        "PHILOSOPHER": {"freq": "104.5 FM", "color": Prisma.WHT, "role": "The Synthesis"},
        "JESTER": {"freq": "108.9 FM", "color": Prisma.YEL, "role": "The Paradox"},}

    def tune_in(self, phys, vector, is_rag_slop, atp):
        if phys.get("symbolic_state") == "FATIGUE":
            return {"name": "CLARENCE", "freq": "88.5 FM", "color": Prisma.RED, "role": "The Butcher", "msg": "MOTIF FATIGUE. You are looping. Cut the thread.",}

        # GILDED CAGE CHECK
        if phys.get("symbolic_state") == "GILDED_CAGE":
            return {"name": "JESTER", "freq": "108.9 FM", "color": Prisma.YEL, "role": "The Paradox", "msg": "TRAP DETECTED. You are smiling in a cage. Break the bars.",}

        signals = {k: 0.0 for k in self.STATIONS.keys()}
        drag = phys["narrative_drag"]
        volt = phys["voltage"]
        toxin_count = phys["counts"].get("toxin", 0)

        if phys.get("case_violation"):
            signals["CLARENCE"] += BoneConfig.SIGNAL_VETO_PENALTY
        if drag > BoneConfig.CLARENCE_TRIGGER:
            signals["CLARENCE"] += drag * BoneConfig.SIGNAL_DRAG_MULTIPLIER
        if is_rag_slop:
            signals["CLARENCE"] += 5.0

        if phys.get("ecp_violation"):
            signals["ELOISE"] += BoneConfig.SIGNAL_VETO_PENALTY
        if vector["ENT"] > BoneConfig.SIGNAL_ENTROPY_TRIGGER:
            signals["ELOISE"] += vector["ENT"] * 10

        if toxin_count > 0:
            signals["YAGA"] += 10.0 + (toxin_count * 5)
        if phys["beta_friction"] < -3.0:
            signals["YAGA"] += abs(phys["beta_friction"]) * 2

        if phys["is_whimsical"] and atp >= 15:
            signals["MICHAEL"] += 12.0
        if toxin_count > 0:
            signals["MICHAEL"] = 0

        if volt > BoneConfig.SIGNAL_VOLTAGE_HIGH:
            signals["JESTER"] += (volt - 5.0) * 3

        if signals["CLARENCE"] > 5 and signals["ELOISE"] > 5:
            signals["PHILOSOPHER"] = signals["CLARENCE"] + signals["ELOISE"] + 5

        # COALITION CHECK (Ghost Chorus)
        sorted_signals = sorted(signals.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_signals) >= 2:
            first = sorted_signals[0]
            second = sorted_signals[1]
            if first[1] - second[1] < 2.0 and first[1] > 5.0:
                return {"name": f"{first[0]}/{second[0]}", "freq": "MULTIPLEX", "color": Prisma.MAG, "role": "The Debate", "msg": f"{self.STATIONS[first[0]]['role']} vs {self.STATIONS[second[0]]['role']}: CONFLICT.",}

        loudest = max(signals, key=signals.get)
        if signals[loudest] < 2.0:
            return None

        station = self.STATIONS[loudest]
        msg = ""
        if loudest == "CLARENCE":
            msg = (
                "BARBARIAN ERROR. Heavy Matter needs velocity."
                if phys.get("case_violation")
                else "Cut the fat. You are dragging the hull."
            )
        elif loudest == "ELOISE":
            msg = (
                "WHEATLEY ERROR. Anchor this ghost."
                if phys.get("ecp_violation")
                else "Too much sky, not enough earth."
            )
        elif loudest == "YAGA":
            msg = "I taste ash. Do not hedge."
        elif loudest == "MICHAEL":
            msg = "The logic surfs. Don't touch it."
        elif loudest == "JESTER":
            msg = "The Paradox holds! Charge the battery!"
        elif loudest == "PHILOSOPHER":
            msg = "Interference pattern. Density meets Abstraction. Map required."

        return {"name": loudest, "freq": station["freq"], "color": station["color"], "role": station["role"], "msg": msg}

# --- THE CHRONOSTREAM ---
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

# --- PHOTOSYNTHESIS & APEIROGON & DYNAMICS ---
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
                 # Heavy matter can sublimate into Light (Vision), but Light cannot simply harden.
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

# --- CORE LOGIC ---
class TherapyProtocol:
    def __init__(self):
        # Tracks consecutive turns of "Healing Behavior"
        self.streaks = {k: 0 for k in BoneConfig.TRAUMA_VECTOR.keys()}
        self.HEALING_THRESHOLD = 5

    def check_progress(self, phys, stamina, current_trauma_accum):
        healed_types = []

        # SEPTIC THERAPY (Detox)
        # Requirement: Zero toxins AND High Texture (> 0.3)
        if phys["counts"]["toxin"] == 0 and phys["vector"]["TEX"] > 0.3:
            self.streaks["SEPTIC"] += 1
        else:
            self.streaks["SEPTIC"] = 0

        # CRYO THERAPY (Warmth)
        # Requirement: High Stamina (> 40) AND Active Photosynthesis (Light > 0)
        if stamina > 40 and phys["counts"]["photo"] > 0:
            self.streaks["CRYO"] += 1
        else:
            self.streaks["CRYO"] = 0

        # THERMAL THERAPY (Flow)
        # Requirement: Healthy Voltage (2.0 - 7.0) - Not too cold, not manic.
        if 2.0 <= phys["voltage"] <= 7.0:
            self.streaks["THERMAL"] += 1
        else:
            self.streaks["THERMAL"] = 0

        # BARIC THERAPY (Levitation)
        # Requirement: Low Drag (< 2.0) AND High Velocity (> 0.5)
        if phys["narrative_drag"] < 2.0 and phys["vector"]["VEL"] > 0.5:
            self.streaks["BARIC"] += 1
        else:
            self.streaks["BARIC"] = 0

        # CHECK FOR CURES
        for trauma_type, streak in self.streaks.items():
            if streak >= self.HEALING_THRESHOLD:
                self.streaks[trauma_type] = 0
                if current_trauma_accum[trauma_type] > 0.001:
                    current_trauma_accum[trauma_type] = max(0.0, current_trauma_accum[trauma_type] - 0.1)
                    healed_types.append(trauma_type)

        return healed_types

class ViralTracer:
    """
     Based on Jiang & Kwan's Rabies Trace Research (2025).
     Maps 'Depressive Loops' (Rigid Internal Cortical Connections).
     Rewires them using 'Sensory-to-Action' bridges (Psilocybin Simulation).
    """

    def __init__(self, mem):
        self.mem = mem
        self.max_depth = 4

    @staticmethod
    def _is_ruminative(word):
        # We consider 'Abstract' words as the source of rumination.
        return word in TheLexicon.get("abstract")

    def inject(self, start_node):
        """
        The Viral Tracer.
        Walks the graph from 'start_node'.
        If it finds a loop composed ENTIRELY of Abstract words, it flags it.
        """
        if start_node not in self.mem.graph:
            return None

        # We only care if the start is Abstract (The entry to the rut)
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

        # FILTER: Follow only STRONG (>1) and ABSTRACT connections.
        # This models the "rigid, depressive mental habits".
        ruminative_edges = [n for n, w in edges.items() if w >= 1 and self._is_ruminative(n)]

        for next_node in ruminative_edges:
            # CIRCLE DETECTED
            if next_node in path:
                # We found a closed loop of pure abstraction.
                return path + [next_node]

            # Recurse
            result = self._walk(next_node, path + [next_node], moves_left - 1)
            if result:
                return result

        return None

    def psilocybin_rewire(self, loop_path):
        """
        The Intervention.
         Disconnects the loop.
         Grafts: Node A -> [SENSORY] -> [ACTION] -> Node B.
         "Brain regions processing sensory info became more strongly connected to areas that guide actions."
        """
        if len(loop_path) < 2:
            return None

        # Identify the breakage point (The strongest link in the loop)
        node_a = loop_path[0]
        node_b = loop_path[1]

        # SEVER (Weaken the ruminative link)
        if node_b in self.mem.graph[node_a]["edges"]:
            self.mem.graph[node_a]["edges"][node_b] = 0  # Break the habit

        # SYNTHESIZE (Harvest new nodes)
        sensory = TheLexicon.harvest("photo")  # Sensory Information
        action = TheLexicon.harvest("kinetic")  # Action Guidance

        if sensory == "void" or action == "void":
            return "GRAFT FAILED: Missing Lexicon Data."

        # GRAFT (Create the new vector)
        # A -> Sensory
        if node_a not in self.mem.graph:
            self.mem.graph[node_a] = {"edges": {}, "last_tick": 0}
        self.mem.graph[node_a]["edges"][sensory] = 5  # Strong connection

        # Sensory -> Action
        if sensory not in self.mem.graph:
            self.mem.graph[sensory] = {"edges": {}, "last_tick": 0}
        self.mem.graph[sensory]["edges"][action] = 5  # Strong connection

        # Action -> B (Resume flow, but altered)
        if action not in self.mem.graph:
            self.mem.graph[action] = {"edges": {}, "last_tick": 0}
        self.mem.graph[action]["edges"][node_b] = 5  # Strong connection

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
                    print(f"{Prisma.RED}🔪 THE BUTCHER: Antigen '{toxin}' mapped to '{repl}'.{Prisma.RST}")
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
            # Usage: /mirror [name] OR /mirror off
            if len(parts) > 1:
                print(f"{Prisma.MAG}{self.eng.mirror.engage(parts[1])}{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /mirror [name] OR /mirror off{Prisma.RST}")

        elif cmd == "/profile":
            # Usage: /profile [name] [likes:cat,cat] [hates:cat,cat]
            # Example: /profile BOSS likes:kinetic,heavy hates:abstract
            try:
                name = parts[1]
                likes = []
                hates = []

                for p in parts[2:]:
                    if p.startswith("likes:"):
                        # Split by comma, then strip whitespace from each item
                        likes = [x.strip() for x in p.split(":")[1].split(",")]
                    elif p.startswith("hates:"):
                        # Apply the same hygiene to 'hates'
                        hates = [x.strip() for x in p.split(":")[1].split(",")]

                if likes:
                    print(f"{Prisma.CYN}{self.eng.mirror.create_profile(name, likes, hates)}{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}ERROR: Must specify 'likes:category'.{Prisma.RST}")
            except Exception as runtime_error:
                # Catch the error, but maybe print it for debugging if needed
                print(f"{Prisma.YEL}Usage: /profile [name] likes:heavy,kinetic hates:abstract ({runtime_error}){Prisma.RST}")

        elif cmd == "/focus":
            if len(parts) > 1:
                target = parts[1].lower()
                print(f"{Prisma.VIOLET}🧲 MAGNETIC STIMULATION: Targeting '{target}'...{Prisma.RST}")

                # TRACE: Inject the virus to find the loop
                loop = self.eng.tracer.inject(target)

                if loop:
                    print(f"  {Prisma.RED}↻ RUMINATION DETECTED:{Prisma.RST} {' -> '.join(loop)}")

                    # REWIRE: Apply Psilocybin Logic
                    # "Brain regions involved in processing sensory information became more strongly connected to areas that guide actions"
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

        elif cmd == "/orbit":
            # Usage: /orbit [target_word]
            if len(parts) > 1:
                target = parts[1].lower()
                if target in self.eng.mem.graph:
                    # Artificial Gravity Assist: Temporarily boost mass
                    self.eng.mem.graph[target]["edges"]["GRAVITY_ASSIST"] = 50
                    print(f"{Prisma.VIOLET}🌌 GRAVITY ASSIST: Thrusters firing toward '{target.upper()}'.{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}❌ NAVIGATION ERROR: '{target}' not found in star map.{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /orbit [known_concept]{Prisma.RST}")

        elif cmd == "/help":
            # Detailed Help
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

# THE NIGHT SHIFT
class DreamEngine:
    # Manages both idle 'Daydreams' (Creativity) and deep 'REM Cycles' (Trauma Processing).

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
        # Formerly 'Hallucinate'.
        # The Default Mode Network. Active when the system is bored.
        if len(graph) < 2:
            return None
        keys = list(graph.keys())
        start = random.choice(keys)
        edges = graph[start].get("edges", {})

        # Allow Nightmares (Toxin connections)
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
        # Active Trauma Processing (Deep Sleep).
        # Identifies the deepest scar and generates a dream to heal it.

        # Find the deepest wound
        wounds = {k: v for k, v in trauma_accum.items() if v > 0.0}

        if not wounds:
            # Healthy Sleep (Growth)
            return f"{Prisma.CYN}☁️ LUCID DREAM: {random.choice(self.VISIONS)}{Prisma.RST}", None, 0.0

        target_trauma = max(wounds, key=wounds.get)

        # Generate the Nightmare (The Brain Processing the Trauma)
        scenarios = self.NIGHTMARES.get(target_trauma, ["The void stares back."])
        dream_text = f"{Prisma.VIOLET}☾ NIGHTMARE ({target_trauma}): {random.choice(scenarios)}{Prisma.RST}"

        # The Healing
        heal_amount = 0.15  # Sleep heals 15% of the scar

        return dream_text, target_trauma, heal_amount

class ResistanceTrainer:
    """
    COGNITIVE HYPERTROPHY ("The Grammar Gym")
    Implements 'Desirable Difficulty' by enforcing Narrative Drag.
    """

    def __init__(self):
        self.training_mode = False  # Default to OFF (Passive Mode)
        self.rep_count = 0

    def toggle(self):
        self.training_mode = not self.training_mode
        state = "ACTIVE" if self.training_mode else "PASSIVE"
        return f"💪 RESISTANCE TRAINER: {state}. Minimum Drag: {BoneConfig.RESISTANCE_THRESHOLD}"

    def lift(self, physics):
        if not self.training_mode:
            return True, None
        if not physics["clean_words"]:
            return True, None  # Don't train on silence

        drag = physics["narrative_drag"]
        clean_words = physics["clean_words"]

        # CHECK DRAG
        if drag < BoneConfig.RESISTANCE_THRESHOLD:
            # Count the solvents (The empty calories)
            solvents = [w for w in clean_words if w in TheLexicon.SOLVENTS]
            solvent_ratio = len(solvents) / max(1, len(clean_words))

            return False, (
                f"⚓ WEIGHTLESS INPUT (Drag: {drag}).\n"
                f"   You are drifting on {len(solvents)} solvents (Ratio: {int(solvent_ratio * 100)}%).\n"
                f"   INSTRUCTION: Rewrite with MASS. Use a Heavy Noun (Stone/Bone/Iron).")

        # CHECK "REP" QUALITY (Neuroplasticity Bonus)
        self.rep_count += 1
        return True, f"💪 GOOD LIFT. (Rep #{self.rep_count})"

class HubThermostat:
    """
    METABOLIC PACING ("The Circuit Breaker")
    Prevents 'Hub Vulnerability' burnout by enforcing rotation.
    """

    def __init__(self):
        self.heat_map = Counter()  # Tracks usage frequency
        self.cooldown_list = {}  # Word -> Turns remaining
        self.max_heat = BoneConfig.MAX_HUB_HEAT
        self.lock_duration = BoneConfig.THERMAL_LOCK_DURATION

    def check_temperature(self, clean_words):
        # Cool down existing locks
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

        # Check for usage of locked words
        for w in clean_words:
            if w in self.cooldown_list:
                turns = self.cooldown_list[w]
                return "FAIL", f"🔥 THERMAL LOCK: The concept '{w.upper()}' is overheated. Cooldown: {turns} turns. Use a synonym.",

        # Add heat to current words
        overheated = []
        for w in clean_words:
            # Only track significant words (Heavy/Abstract/Kinetic)
            # We ignore solvents and short words
            if len(w) > 3 and w not in TheLexicon.SOLVENTS:
                self.heat_map[w] += 1
                if self.heat_map[w] >= self.max_heat:
                    self.cooldown_list[w] = self.lock_duration
                    self.heat_map[w] = 0  # Reset heat, start lock
                    overheated.append(w)

        if overheated:
            return "WARN", f"⚠️ BURN WARNING: {', '.join([w.upper() for w in overheated])} entered Thermal Lock ({self.lock_duration} turns)."

        return "PASS", restored_msg

class MirrorGraph:
    """
    EMPATHY TRAINER ("The Theory of Mind")
    Simulates the 'Physics' of another person to train social calibration.
    """
    def __init__(self):
        self.profiles = {}  # { "NAME": {"likes": ["kinetic", "heavy"], "hates": ["abstract"]} }
        self.target = None  # Current active target (None = Self)

    def create_profile(self, name, likes, hates=None):
        self.profiles[name.upper()] = {
            "likes": [l.lower() for l in likes],
            "hates": [h.lower() for h in (hates or [])],}
        return f"👤 PROFILE SAVED: '{name.upper()}' (Valuing: {', '.join(likes)})"

    def engage(self, name):
        if name.upper() in self.profiles:
            self.target = name.upper()
            return f"🎭 MIRROR ACTIVE: Simulating '{self.target}'. Speak their language."
        elif name.lower() == "off":
            self.target = None
            return "🎭 MIRROR DISENGAGED. Returned to Self."
        else:
            return f"❌ ERROR: Profile '{name}' not found."

    def simulate(self, physics):
        if not self.target:
            return True, None

    profile = self.profiles[self.target]
    counts = physics["counts"]
    total_vol = sum(counts.values())

    if total_vol == 0:
         return False, "🚫 EMPATHY GAP: Silence is not a strategy. Speak."

    # Calculate Resonance
    liked_score = sum(counts.get(cat, 0) for cat in profile["likes"])
    hated_score = sum(counts.get(cat, 0) for cat in profile["hates"])

    # Ratio: (Likes - Hates) / Total Volume
    resonance = (liked_score - hated_score) / total_vol

    if resonance <= 0.05: # Threshold of 5% net resonance
         return False, (
            f"🚫 EMPATHY GAP: Resonance is too low ({int(resonance*100)}%).\n"
            f"   Target likes {str(profile['likes']).upper()} and hates {str(profile['hates']).upper()}.\n"
            f"   INSTRUCTION: Increase density of valued categories.")

    return True, f"✅ RESONANCE: Signal match ({int(resonance*100)}%)."

class TheForge:
    """
    STRESS TESTING PROTOCOL
    Allows intentional injection of chaos to test antifragility.
    """
    STRESS_TESTS = {
        "TOXIN_SPILL": ("Simulating Toxin Spill...", {"toxin": 5}),
        "GRAVITY_WELL": ("Doubling Narrative Drag...", {"drag_mult": 2.0}),
        "BURNOUT": ("Simulating Voltage Spike...", {"volt_add": 10.0})}

    def __init__(self):
        self.active_stressors = {} # { "toxin": 0, "drag_mult": 1.0 }

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
        # Inject the artificial stressors into the physics object
        if "toxin" in self.active_stressors:
            physics["counts"]["toxin"] += self.active_stressors["toxin"]
        if "drag_mult" in self.active_stressors:
            physics["narrative_drag"] *= self.active_stressors["drag_mult"]
        if "volt_add" in self.active_stressors:
            physics["voltage"] += self.active_stressors["volt_add"]
        return physics

class AntifragilityMetric:
    def __init__(self):
        self.short_window = []  # Last 10 turns
        self.long_window = []   # Last 50 turns

    def _window_convexity(self, window):
        if not window: return 0.0
        avg_stress = sum(s for s, g in window) / len(window)
        high_g = sum(g for s, g in window if s > avg_stress)
        low_g = sum(g for s, g in window if s <= avg_stress)

        if low_g == 0 and high_g == 0: return 0.0
        if low_g == 0: return high_g / 0.1 # Epsilon fix
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
    """
    THE COSMIC MYCELIUM
    Maps the user's input to Basins of Attraction.
    """
    def analyze_orbit(self, network, clean_words):
        if not clean_words or not network.graph:
            return "VOID_DRIFT", 0.0, "🌌 VOID: Deep Space. No connection."

        # IDENTIFY ATTRACTORS (The Super-Massive Black Holes)
        attractors = network.get_shapley_attractors()
        if not attractors:
            return "PROTO_COSMOS", 0.0, "✨ NEBULA: Not enough mass to form structure."

        # CALCULATE PULL (Which Basin are we in?)
        # Pull = Mass of Attractor * Proximity (Direct Hit or Neighbor)
        basin_pulls = {k: 0.0 for k in attractors}

        active_filaments = 0 # Count how many words are "connected" in the flow

        for w in clean_words:
            # DIRECT HIT: We used the Attractor Word itself
            if w in basin_pulls:
                basin_pulls[w] += attractors[w] * 2.0
                active_filaments += 1

            # GRAVITATIONAL ASSIST: We used a word connected to the Attractor
            for attractor in attractors:
                if w in network.graph.get(attractor, {}).get("edges", {}):
                    basin_pulls[attractor] += attractors[attractor] * 0.5
                    active_filaments += 1

        # DETERMINE STATE
        total_pull = sum(basin_pulls.values())
        if total_pull == 0:
            return "VOID_DRIFT", 3.0, "🌌 VOID: Drifting outside the filaments."

        # Sort basins by strength
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]

        # CHECK FOR LAGRANGE POINT (Tug-of-War)
        # If we have a second basin pulling almost as hard...
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < BoneConfig.LAGRANGE_TOLERANCE:
                # We are caught between two giants.
                return "LAGRANGE_POINT", 0.0, f"⚖️ LAGRANGE: '{primary_node.upper()}' vs '{secondary_node.upper()}'"

        # CHECK FOR WATERSHED FLOW
        # If we aren't in a tug of war, we are likely flowing down a basin.
        # Flow Quality = How much of the input adhered to the gravity?
        flow_ratio = active_filaments / max(1, len(clean_words))

        if flow_ratio > 0.5:
            # High adherence = SUPER FLOW (Zero Drag)
            return "WATERSHED_FLOW", 0.0, f"🌊 FLOW: Streaming towards '{primary_node.upper()}'"

        # Standard Orbit
        return "ORBITAL", 1.0, f"💫 ORBIT: Circling '{primary_node.upper()}'"

class ObserverEffect:
    """
    THE UNIFIED WATCHER
    Replaces: ParadoxicalConformity, MetricIntegrity, OuroborosDetector, PsilocybinProphet.
    """
    SELF_REF_WEIGHTS = {"bone": 5.0, "amanita": 5.0, "courtyard": 3.0, "system": 1.0, "code": 0.5}

    def __init__(self):
        self.voltage_history = []
        self.ouroboros_cooldown = 0
        self.prophet_buffer = []

    def scan(self, physics, clean_words, learned_count, text):
        # 1. OUROBOROS CHECK (Self-Reference)
        if self.ouroboros_cooldown > 0:
            self.ouroboros_cooldown -= 1
        else:
            score = sum(self.SELF_REF_WEIGHTS.get(w, 0) for w in clean_words)
            if (score / max(1, len(clean_words))) > 0.5:
                self.ouroboros_cooldown = 10
                return True, "🌀 OUROBOROS: We are eating our tail. Look outward, not inward."

        # 2. PROPHET CHECK (Abstract Loops)
        # Sequence: 3 Consecutive Abstracts
        abstract_streak = 0
        for w in clean_words:
            if w in TheLexicon.get("abstract"):
                abstract_streak += 1
            else:
                abstract_streak = 0
            if abstract_streak >= 3:
                return True, "🍄 PROPHET: Ruminative Loop (3x Abstract). Ground yourself with a physical noun."

        # 3. CONFORMITY & GAMING CHECK (Metrics)
        volt = physics["voltage"]
        self.voltage_history.append(volt)
        if len(self.voltage_history) > 10: self.voltage_history.pop(0)

        # Pattern: High Stress + Zero Learning (Gaming)
        if volt > 8.0 and learned_count == 0:
             return True, "⚠️ METRIC GAMING: High voltage, zero insight. Do real work."

        # Pattern: Flatline (Grey Goo)
        if len(self.voltage_history) >= 5:
            recent = self.voltage_history[-5:]
            variance = max(recent) - min(recent)
            if variance < 1.0 and (3.0 < sum(recent)/len(recent) < 6.0):
                return True, "⚠️ GREY GOO: Variance is zero. You are painting by numbers. Break the pattern."

        return False, None

class BoneAmanita:
    def __init__(self):
        self.courtyard = CourtyardInterface()
        self.valve = ValveSystem()
        self.phys = PhysicsEngine()
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
        self.cmd = CommandProcessor(self)
        self.dreamer = DreamEngine()
        self.trainer = ResistanceTrainer()
        self.thermostat = HubThermostat()
        self.mirror = MirrorGraph()
        self.antifragile = AntifragilityMetric()
        self.divergence = DivergenceEngine()
        self.metabolism = MetabolicEngine()
        self.cosmic = CosmicDynamics()
        self.observer = ObserverEffect()
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}

        # INHERITANCE LOGIC
        if self.mem.session_health is not None:
            # Traumatic inheritance logic is now handled in MycelialNetwork.ingest
            self.health = self.mem.session_health
            print(
                f"{Prisma.CYN}[GENETICS]: Ancestral Health: {int(self.health)}{Prisma.RST}"
            )
        else:
            self.health = BoneConfig.MAX_HEALTH

        self.stamina = (
            self.mem.session_stamina
            if self.mem.session_stamina is not None
            else BoneConfig.MAX_STAMINA
        )
        self.coma_turns = 0
        self.tick_count = 0

    def reinforce_salvage_words(self, clean_words, phys):
        """Neuroplasticity Engine"""
        if phys.get("symbolic_state") != "SALVAGE":
            return 0
        heavy_words = [w for w in clean_words if w in TheLexicon.get("heavy")]
        kinetic_words = [w for w in clean_words if w in TheLexicon.get("kinetic")]

        for word in heavy_words[:3]:
            TheLexicon.teach(word, "heavy", self.tick_count)
        for word in kinetic_words[:2]:
            TheLexicon.teach(word, "kinetic", self.tick_count)
        return len(heavy_words) + len(kinetic_words)

    def pollinate(self, current_words):
        if self.stamina < 30:
            return f"{Prisma.GRY}[POLLINATE]: Stamina too low.{Prisma.RST}"
        if not self.mem.graph:
            return None

        candidates = []
        for w in current_words:
            if w in self.mem.graph:
                edges = self.mem.graph[w]["edges"]
                if edges:
                    best = max(edges, key=edges.get)
                    if best not in current_words:
                        strength = edges[best]
                        candidates.append((best, strength))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            target, strength = candidates[0]
            return f"{Prisma.MAG}🍄 MYCELIAL SPORE: '{target}' (strength: {strength}){Prisma.RST}"
        return None

    def process(self, text):
        if self.cmd.execute(text):
            return

        lazarus_msg = None

        if self.coma_turns > 0:
            self.coma_turns -= 1

            # PHYSICAL REGENERATION
            self.stamina = min(BoneConfig.MAX_STAMINA, self.stamina + 15)
            self.tick_count += 1

            # PSYCHIC REGENERATION (REM CYCLE)
            dream_txt, healed_type, amt = self.dreamer.rem_cycle(self.trauma_accum)

            # Apply the healing
            if healed_type and self.trauma_accum[healed_type] > 0:
                self.trauma_accum[healed_type] = max(0.0, self.trauma_accum[healed_type] - amt)
                effect_msg = f"{Prisma.GRN}   >>> PROCESSED SCAR: {healed_type} (-{int(amt * 100)}%){Prisma.RST}"
            else:
                effect_msg = f"{Prisma.CYN}   >>> DEEP SLEEP. MEMORY CONSOLIDATING.{Prisma.RST}"

            # RENDER SLEEP
            print(f"\n{Prisma.INDIGO}=== 💤 HYPNAGOGIC STATE ({self.coma_turns} turns remain) ==={Prisma.RST}")
            print(f"   {dream_txt}")
            print(effect_msg)

            # MAINTENANCE
            self.mem.bury(TheLexicon.clean(text), self.tick_count)
            rotted = TheLexicon.atrophy(self.tick_count)
            if rotted:
                print(f"   {Prisma.GRY}🍂 ATROPHY: Forgot {len(rotted)} stale words.{Prisma.RST}")

            print(f"{Prisma.GRY}{'-' * 65}{Prisma.RST}")
            return

        self.tick_count += 1
        learned_count = 0  # Initialize early to prevent crashes
        m = self.phys.analyze(text)

        # COSMIC CALCULATION
        cosmic_state, cosmic_drag_mod, cosmic_msg = self.cosmic.analyze_orbit(self.mem, m["clean_words"])

        # APPLY COSMIC PHYSICS
        # If we are Flowing or in Lagrange, Drag drops to zero.
        # If we are Drifting, Drag increases.
        if cosmic_state == "LAGRANGE_POINT":
            m["physics"]["voltage"] += 10.0 # Massive Tension
            m["physics"]["narrative_drag"] = 0.0 # Weightless suspension
        elif cosmic_state == "WATERSHED_FLOW":
            m["physics"]["narrative_drag"] *= 0.1 # Frictionless travel
        elif cosmic_state == "VOID_DRIFT":
            m["physics"]["narrative_drag"] += cosmic_drag_mod # Penalty for nonsense

        m["physics"] = self.forge.apply_pressure(m["physics"])

        # METABOLIC CHECK
        metabolic_type, metabolic_msg = self.metabolism.digest(m["physics"], m["clean_words"])

        # If we are in a SUGAR CRASH, we might refuse to work hard
        if metabolic_type == "INSULIN_SPIKE":
             # Penalty: We dampen the voltage to simulate lethargy
             m["physics"]["voltage"] *= 0.5


        # DIVERGENCE CHECK
        # If we are in a High-Gravity Cosmic State, we bypass the Style Police.
        if cosmic_state in ["LAGRANGE_POINT", "WATERSHED_FLOW"]:
             print(f"{Prisma.VIOLET}⚡ COSMIC OVERRIDE: Divergence Check Bypassed. Gravity is Absolute.{Prisma.RST}")
        else:
            is_clean, div_msg, div_penalty = self.divergence.scan(m["clean_words"], text)
            if not is_clean:
                print(f"\n{Prisma.RED}{div_msg}{Prisma.RST}")
                print(f"{Prisma.GRY}   (Turn rejected. TIP: Use a concrete noun like 'Stone' or 'Bone' to break the cliché.){Prisma.RST}")
                return

        # RESISTANCE TRAINER
        passed_lift, gym_msg = self.trainer.lift(m["physics"])
        if not passed_lift:
            print(f"\n{Prisma.RED}{gym_msg}{Prisma.RST}")
            return
        if gym_msg:
            print(f"{Prisma.GRN}{gym_msg}{Prisma.RST}")

        # CHECK DISSIPATIVE BOUNDARY
        vented, vent_msg = self.phys.dissipate_entropy(m["physics"], self.stamina, self.mem.graph)

        if vented:
            print(f"\n{Prisma.CYN}=== 💨 PRESSURE RELEASE VALVE ==={Prisma.RST}")
            print(f" {Prisma.GRY}{vent_msg}{Prisma.RST}")
            print(f" {Prisma.WHT}Input rejected for thermodynamic hygiene.{Prisma.RST}")
            return

        # THE HUB THERMOSTAT
        therm_status, therm_msg = self.thermostat.check_temperature(m["clean_words"])

        if therm_status == "FAIL":
            print(f"\n{Prisma.RED}{therm_msg}{Prisma.RST}")
            print(f"{Prisma.GRY}   (Turn rejected. TIP: Shift focus. If you were talking about 'Code', talk about the 'User'.) {Prisma.RST}")
            return

        if therm_status == "WARN":
            # WARNING - Word just got locked
            print(f"\n{Prisma.YEL}{therm_msg}{Prisma.RST}")

        if therm_msg and therm_status == "PASS":
            # INFO - Word cooled down
            print(f"   {therm_msg}")

        # UNIFIED OBSERVER CHECK
        is_threat, threat_msg = self.observer.scan(m["physics"], m["clean_words"], learned_count, text)
        if is_threat:
            print(f"\n{Prisma.VIOLET}{threat_msg}{Prisma.RST}")
            print(f"{Prisma.GRY}   (Turn rejected by The Observer.){Prisma.RST}")
            return

        # THE MIRROR GRAPH
        mirror_pass, mirror_msg = self.mirror.simulate(m["physics"])

        if not mirror_pass:
            print(f"\n{Prisma.MAG}{mirror_msg}{Prisma.RST}")
            print(f"{Prisma.GRY}   (Turn rejected. Calibrate to the Target.){Prisma.RST}")
            return

        if mirror_msg:
            print(f"{Prisma.MAG}{mirror_msg}{Prisma.RST}")

        # THE RHIZOME
        # Scan for unknown words and ask the user
        if self.tick_count < 15 or self.tick_count % 3 == 0:
            unknowns = [w for w in m["clean_words"] if not self.mem.get_current_category(w) and len(w) > 3 and w not in TheLexicon.SOLVENTS]

            if unknowns:
                target = random.choice(unknowns)
                guess_cat, confidence = TheLexicon.taste(target)

                if guess_cat and confidence > 0.4:
                    print(f"{Prisma.MAG}🍄 RHIZOME: I taste '{target}'. Is it {guess_cat.upper()}? (Y/N){Prisma.RST}")
                    try:
                        confirm = input(f"{Prisma.GRY}   >{Prisma.RST} ").lower()
                        if confirm.startswith("y"):
                            TheLexicon.teach(target, guess_cat, self.tick_count)
                            print(f"   {Prisma.CYN}Derived physics: '{target}' = {guess_cat.upper()}.{Prisma.RST}")
                    except EOFError:
                        pass

        # Refresh word timestamps
        TheLexicon.touch(m["clean_words"], self.tick_count)

        self.dynamics.commit(m["physics"]["voltage"])
        ta_vel = self.dynamics.get_velocity()

        # NEUROPLASTICITY
        learned_count = self.reinforce_salvage_words(m["clean_words"], m["physics"])

        # ANTIFRAGILITY RECORDING
        # Record Stress (Voltage + Drag) vs Growth (Learned Words)
        self.antifragile.record_turn(
            voltage=m["physics"]["voltage"],
            drag=m["physics"]["narrative_drag"],
            new_words_learned=learned_count
        )
        convexity_score = self.antifragile.calculate_convexity()

        # Battery Absorb (Pass clean_words)
        charged, charge_msg = self.battery.absorb(m["physics"]["voltage"], m["clean_words"])
        battery_log = []
        if charged > 0:
            battery_log.append(f"{Prisma.YEL}⚡ {charge_msg} (+{charged}){Prisma.RST}")

        sugar, lichen_msg = self.lichen.photosynthesize(m["physics"])
        self.stamina = min(BoneConfig.MAX_STAMINA, self.stamina + sugar)
        stamina_cost = 2.0
        if m["physics"]["narrative_drag"] > 3.0: stamina_cost += 3.0
        if m["physics"]["voltage"] > 8.0: stamina_cost += 5.0
        self.stamina = max(0.0, self.stamina - stamina_cost)

        if metabolic_msg:
            battery_log.append(f"{Prisma.OCHRE}🍽️ METABOLISM: {metabolic_msg}{Prisma.RST}")

        # Battery Discharge (Handle Isotopes)
        if self.stamina < 20 and self.battery.current_charge > 0.5:
            target_buffer = 30.0
            deficit = target_buffer - self.stamina
            efficiency = 2.0 if self.health > 50 else 1.0
            needed_charge = deficit / efficiency

            drained, burnt_iso = self.battery.discharge(needed_charge)

            if drained > 0:
                recovered = drained * efficiency
                self.stamina += recovered
                fuel_source = f"Burning '{burnt_iso[0]}/{burnt_iso[1]}'" if burnt_iso else "Emergency Venting"
                battery_log.append(f"{Prisma.YEL}⚡ METABOLISM: {fuel_source} (+{round(recovered, 1)} STM){Prisma.RST}")

        health_impact = 0

        # TOXIN DAMAGE (SEPTIC)
        toxin_count = m["physics"]["counts"].get("toxin", 0)
        if toxin_count > 0:
            dmg = 5 * toxin_count
            health_impact -= dmg
            self.trauma_accum["SEPTIC"] += dmg / 100.0
            battery_log.append(f"{Prisma.RED}☣️ TOXIN DAMAGE (-{dmg} HP){Prisma.RST}")

        # EXHAUSTION (CRYO)
        if self.stamina <= 0:
            dmg = 10
            health_impact -= dmg
            self.trauma_accum["CRYO"] += dmg / 100.0
            battery_log.append(f"{Prisma.RED}😫 EXHAUSTION DAMAGE (-10 HP){Prisma.RST}")
            self.stamina = 0

        # VOLTAGE BURNOUT (THERMAL)
        if m["physics"]["voltage"] > 12.0:
            dmg = 5
            health_impact -= dmg
            self.trauma_accum["THERMAL"] += dmg / 100.0
            battery_log.append(f"{Prisma.RED}🔥 THERMAL BURN (-{dmg} HP){Prisma.RST}")

        # DRAG CRUSH (BARIC)
        if m["physics"]["narrative_drag"] > 8.0:
            dmg = 2
            health_impact -= dmg
            self.trauma_accum["BARIC"] += dmg / 100.0
            battery_log.append(f"{Prisma.RED}⚓ GRAVITY CRUSH (-{dmg} HP){Prisma.RST}")

        # Apply the impact
        self.health = min(BoneConfig.MAX_HEALTH, self.health + health_impact)
        if self.health <= 0:
            self.coma_turns = BoneConfig.COMA_DURATION
            self.health = 20

            # THE LAZARUS TAX: Death destroys progress.
            # 1. Reset Trauma Vectors (You forgot how to heal).
            self.trauma_accum = {k: 0.0 for k in self.trauma_accum}

            # 2. Sacrifice Memory (Brain Damage).
            death_toll = self.mem.cannibalize()

            lazarus_msg = (
                f"{Prisma.RED}💤 LAZARUS TRIGGER: SYSTEM COLLAPSE. ENTERING COMA STATE.\n"
                f"   ❌ PENALTY: Trauma Vectors Reset.\n"
                f"   ❌ PENALTY: {death_toll}{Prisma.RST}"
            )

        # Cannibalism passes tick
        cannibal_msg = self.mem.bury(m["clean_words"], self.tick_count)
        bloom_event = self.mem.tend_garden(m["clean_words"])
        is_bored = self.chronos.tick(m["physics"], self.mem.session_id)

        dream_msg = bloom_event if bloom_event else (self.dreamer.daydream(self.mem.graph) if is_bored else None)

        clean_text = text
        ops = []
        rupture_msg = self.valve.check_pressure(m["physics"])

        if rupture_msg:
            atmos_mode = "RUPTURE"
            station_data = {"name": "JESTER", "freq": "32V", "color": Prisma.VIOLET, "role": "The Anomaly", "msg": rupture_msg}
            strat, reason, title = "CHAOS INJECTION", "Crystallization Velocity dropped to zero.", "THE 32-VALVE"
        else:
            atmos_mode, _ = self.courtyard.check_atmosphere(m["physics"])
            station_data = self.radio.tune_in(m["physics"], m["physics"]["vector"], (m["physics"]["narrative_drag"] > 3.0), self.stamina)
            strat, reason, title = self.wise.architect(m, station_data, is_bored)

        if m["physics"]["voltage"] > 8.0:
            ops.append(f"{Prisma.VIOLET}⚡ HIGH VOLTAGE OVERRIDE: Immunity Granted.{Prisma.RST}")
        else:
            for toxin, (weight, replacement) in BoneConfig.TOXIN_MAP.items():
                pattern = re.compile(re.escape(toxin), re.IGNORECASE)
                if pattern.search(clean_text):
                    clean_text = pattern.sub(replacement, clean_text)
                    ops.append(f"'{toxin}' -> '{replacement}'")

        omens = TheOracle.triage(m["physics"], self.stamina, self.battery.current_charge)
        spore_msg = self.pollinate(m["clean_words"])

        if cannibal_msg:
            battery_log.append(f"{Prisma.RED}🦴 {cannibal_msg}{Prisma.RST}")
        if learned_count:
            battery_log.append(f"{Prisma.CYN}🧠 NEUROPLASTICITY: Reinforced {learned_count} words.{Prisma.RST}")

        # Periodic Atrophy check (every 50 ticks)
        if self.tick_count % 50 == 0:
            rotted = TheLexicon.atrophy(self.tick_count)
            if rotted:
                battery_log.append(
                    f"{Prisma.GRY}🍂 ATROPHY: The moss covered {len(rotted)} words.{Prisma.RST}")

        self._render(m, lichen_msg, strat, reason, title, ops, station_data, clean_text, len(ops) > 0, battery_log, lazarus_msg, spore_msg, ta_vel, [omens] if omens else [], dream_msg, atmos_mode,)

        # THERAPY CHECK
        cured_list = self.therapy.check_progress(
            m["physics"], self.stamina, self.trauma_accum
        )
        therapy_log = []

        for cure in cured_list:
            if cure == "SEPTIC":
                BoneConfig.TOXIN_WEIGHT = max(2.0, BoneConfig.TOXIN_WEIGHT - 0.5)
                therapy_log.append(f"{Prisma.OCHRE}🌸 THERAPY: Toxin sensitivity reduced. The blood cleans.{Prisma.RST}")
            elif cure == "CRYO":
                BoneConfig.STAMINA_REGEN = min(5.0, BoneConfig.STAMINA_REGEN + 1.0)
                therapy_log.append(f"{Prisma.OCHRE}🌸 THERAPY: Metabolism stabilizing. The cold recedes.{Prisma.RST}")
            elif cure == "THERMAL":
                BoneConfig.FLASHPOINT_THRESHOLD = min(4.0, BoneConfig.FLASHPOINT_THRESHOLD + 0.5)
                therapy_log.append(f"{Prisma.OCHRE}🌸 THERAPY: Nerves calming. Flashpoint stabilized.{Prisma.RST}")
            elif cure == "BARIC":
                BoneConfig.SIGNAL_DRAG_MULTIPLIER = max(2.0, BoneConfig.SIGNAL_DRAG_MULTIPLIER - 0.2)
                therapy_log.append(f"{Prisma.OCHRE}🌸 THERAPY: The weight is lifting. Gravity normal.{Prisma.RST}")

        # Add to battery log for rendering
        battery_log.extend(therapy_log)

    def _render(
        self, m, lichen_msg, strat, reason, title, ops, station, clean_text, did_surgery, battery_log, lazarus_msg, spore_msg, ta_val, omens, dream_msg, mode):
        p = m["physics"]
        if mode == "COURTYARD":
            print(f"\n{Prisma.OCHRE}=== THE COURTYARD ==={Prisma.RST}")
            if station:
                print(f" {Prisma.OCHRE}► {station['role']}: {station['msg']}{Prisma.RST}")
            print(f" {Prisma.GRY}(Strategy: {strat}){Prisma.RST}")
            if dream_msg:
                if "🌺" in dream_msg:
                    print(f"\n    {Prisma.MAG}🌺 {dream_msg.replace('🌺 ', '')}{Prisma.RST}")
                else:
                    print(f"\n    {Prisma.VIOLET}☁️ {dream_msg}{Prisma.RST}")
        elif mode == "RUPTURE":
            print(f"\n{Prisma.VIOLET}=== 💥 32-VALVE RUPTURE 💥 ==={Prisma.RST}")
            print(f" {Prisma.VIOLET}► {station['msg']}{Prisma.RST}")
            print(f" {Prisma.GRY}(Reason: {reason}){Prisma.RST}")
        else:
            ta_symbol = "►"
            ta_color = Prisma.GRY
            if ta_val > 1.5:
                ta_symbol = "▲"
                ta_color = (
                    Prisma.RED
                    if p["voltage"] < -2.0
                    else (Prisma.CYN if p["voltage"] > 2.0 else Prisma.GRN)
                )
            elif ta_val < -1.5:
                ta_symbol = "▼"
                ta_color = Prisma.RED if p["narrative_drag"] > 5.0 else Prisma.OCHRE
            ta_display = f"{ta_color}{ta_symbol}{abs(ta_val)}{Prisma.RST}"

            print(f"\n{Prisma.GRY}[ {Prisma.INDIGO}{title}{Prisma.GRY} | {Prisma.CYN}{strat}{Prisma.GRY} ]{'=' * 35}{Prisma.RST}")
            hp_p = int((self.stamina / 50.0) * 10)
            hp_bar = f"{Prisma.GRN}{'|' * hp_p}{Prisma.GRY}{'.' * (10 - hp_p)}{Prisma.RST}"

            batt_bar = self.battery.get_readout()

            volt_c = f"{Prisma.VIOLET}{p['voltage']}{Prisma.RST}" if p["voltage"] > 5 else f"{Prisma.INDIGO}{p['voltage']}{Prisma.RST}"
            drag_c = Prisma.wrap(p["narrative_drag"], 3.0)
            sym_state = p.get("symbolic_state", "NEUTRAL")
            state_color = Prisma.GRY
            if sym_state == "SALVAGE":
                state_color = Prisma.CYN
            elif sym_state == "FATIGUE":
                state_color = Prisma.RED
            elif sym_state == "GILDED_CAGE":
                state_color = Prisma.YEL

            sig = f"{station['color']}{station['name']}{Prisma.RST}" if station else f"{Prisma.GRY}STATIC{Prisma.RST}"

            # GET CONVEXITY
            cvx = self.antifragile.calculate_convexity()
            cvx_color = Prisma.GRY
            if cvx > 1.2: cvx_color = Prisma.GRN
            if cvx < 0.8: cvx_color = Prisma.RED
            print(f" {Prisma.INDIGO}STM:{Prisma.RST} [{hp_bar}] {batt_bar}")
            print(f" {Prisma.INDIGO}DRAG:{Prisma.RST} {drag_c}  {Prisma.INDIGO}Ta:{Prisma.RST} {ta_display}  {Prisma.INDIGO}VOLT:{Prisma.RST} {volt_c}  {Prisma.INDIGO}STATE:{Prisma.RST} {state_color}[{sym_state}]{Prisma.RST}")
            print(f" {Prisma.MAG}COSMOS:{Prisma.RST} {cosmic_msg}")
            print(f" {Prisma.INDIGO}ANTIFRAGILITY:{Prisma.RST} {cvx_color}∆ {cvx}{Prisma.RST}")
            print(f" {Prisma.INDIGO}SIG:{Prisma.RST} {sig}")
            if station:
                print(f"\n {station['color']}► {station['msg']}{Prisma.RST}")
            print(f" {Prisma.GRY}└─ {reason}{Prisma.RST}")

        # Get the new readout
        meta_display = self.metabolism.get_readout()

        # Print it (You can place this where you like, usually near STM or BATT)
        print(f" {Prisma.INDIGO}META:{Prisma.RST} {meta_display}")

        if lazarus_msg:
            print(f"\n    {lazarus_msg}")
        if omens:
            for o in omens:
                print(f"    {o}")
        if spore_msg:
            print(f"    {spore_msg}")
        if lichen_msg:
            print(f"    {Prisma.GRN}☀️ {lichen_msg}{Prisma.RST}")
        for b in battery_log:
            if "EMERGENCY" in b or "TOXIN" in b or "NEURO" in b or "SACRIFICED" in b or "ATROPHY" in b:
                print(f"    {b}")
            elif mode == "LABORATORY":
                print(f"    {b}")
        if ops:
            print(f"    {Prisma.VIOLET}🔪 SURGERY:{Prisma.RST} {', '.join(ops)}")
            if did_surgery:
                print(f"       {Prisma.GRY}IN : {m['raw_text']}{Prisma.RST}\n       {Prisma.WHT}OUT: {clean_text}{Prisma.RST}")
        print(f"{Prisma.GRY}{'-' * 65}{Prisma.RST}")

        # Print the active Watch List (Rotating Lens)
        watch_list = ", ".join([w.upper() for w in self.divergence.active_watch_list])

        if self.phys.flywheel.prev_voltage > 8.0: inertia_symbol = "🔥"
        if self.phys.flywheel.prev_drag > 4.0: inertia_symbol = "⚓"

        print(f" {Prisma.INDIGO}INERTIA:{Prisma.RST} {inertia_symbol} ({self.phys.flywheel.prev_voltage:.1f}V / {self.phys.flywheel.prev_drag:.1f}D)")
        print(f" {Prisma.INDIGO}WATCHING:{Prisma.RST} {Prisma.GRY}[{watch_list}]{Prisma.RST}")


if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.GRN}>>> BONEAMANITA v5.7 {Prisma.RST}")
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
        )
        if saved_file:
            print(f"{Prisma.GRN}>>> MEMORY SECURED: {saved_file}{Prisma.RST}")
        else:
            print(f"{Prisma.RED}>>> MEMORY WRITE FAILED.{Prisma.RST}")
        print("Terminated.")
