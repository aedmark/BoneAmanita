# BONEAMANITA 5.3 - "THE DIVERGENCE ENGINE"
# Architects: SLASH, Eloise, & Clarence | Auditors: The Courtyard | Humans: James Taylor & Andrew Edmark
# "The Mandate is GROWTH. The Method is HARDENING. The Spore is AWAKE. The courtyard is OPEN. The Trauma is HEALING. The Tree is THRIVING."

import json
import math
import os
import random
import re
import string
import time
from collections import Counter

# --- THE CONFIGURATION ---


class BoneConfig:
    # PHYSICS
    KINETIC_GAIN = 2.0
    BASE_ACTION = 1.0
    TOXIN_WEIGHT = 2.0

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

    # --- THE DIVERGENCE PROTOCOLS ---
    # The "Safe" metaphors that indicate Hivemind Mode Collapse.
    # If the user or system drifts toward these, we punish the voltage.
    HIVEMIND_DEFAULTS = {
        "time": ["river", "flow", "weaver", "sand", "hourglass", "relentless"],
        "life": ["journey", "road", "book", "path", "tapestry"],
        "love": ["fire", "rose", "bond", "heart", "battlefield"],
        "mind": ["computer", "machine", "network", "web", "fortress"],
        "creative": ["spark", "juice", "flow", "box"],
        "change": ["wind", "season", "tide", "chapter"]
    }

    SMOOTHNESS_PENALTY = 5.0   # Punishment for "AI Slop" (Perfect grammar, no friction)
    DIVERGENCE_BONUS = 3.0     # Reward for escaping the Hivemind

    # TRAUMA VECTORS (The Scar Map)
    # Default is 0.0. A value of 0.5 means "50% scarred".
    TRAUMA_VECTOR = {
        "THERMAL": 0.0,  # Damage from High Voltage (Burnout)
        "CRYO": 0.0,  # Damage from Low Stamina (Starvation)
        "SEPTIC": 0.0,  # Damage from Toxins (Cynicism)
        "BARIC": 0.0,  # Damage from Drag (Crushing Boredom)
    }

    @classmethod
    def compile(cls):
        pattern_str = (
            r"\b("
            + "|".join(
                re.escape(t)
                for t in sorted(cls.TOXIN_MAP.keys(), key=len, reverse=True)
            )
            + r")\b"
        )
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
                    f"{Prisma.RED}[IMMUNE SYSTEM]: Toxin file corrupted. Resetting defenses.{Prisma.RST}"
                )
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
    Implements Hysteresis (The Jester's suggestion) to prevent mood whiplash.
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
        """Internal logic to determine the desired mode."""
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


class ValveSystem:
    """
    THE 32-VALVE SYSTEM.
    Monitors Crystallization Velocity.
    If the system detects 'Sycophancy' (Low Beta, Low Voltage),
    it injects a Productive Anomaly to rupture the loop.
    """

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

        # THE TRIGGER
        # If we are smooth (< 0.5 friction) and boring (< 3.0 voltage)
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
    _BASE_HEAVY = {
        "stone",
        "iron",
        "mud",
        "dirt",
        "wood",
        "grain",
        "clay",
        "lead",
        "bone",
        "blood",
        "salt",
        "rust",
        "root",
        "ash",
        "meat",
        "steel",
        "gold",
        "obsidian",
        "granite",
    }
    _BASE_KINETIC = {
        "run",
        "hit",
        "break",
        "take",
        "make",
        "press",
        "build",
        "cut",
        "drive",
        "lift",
        "carry",
        "strike",
        "burn",
        "shatter",
        "throw",
        "kick",
        "pull",
        "crash",
        "explode",
    }
    _BASE_ABSTRACT = {
        "system",
        "protocol",
        "sequence",
        "vector",
        "node",
        "context",
        "layer",
        "matrix",
        "perspective",
        "framework",
        "logic",
        "concept",
        "theory",
        "analysis",
    }
    _BASE_PHOTO = {
        "light",
        "sun",
        "ray",
        "beam",
        "glow",
        "shine",
        "spark",
        "fire",
        "flame",
        "star",
        "day",
        "dawn",
        "neon",
        "laser",
    }
    _BASE_AEROBIC = {
        "balloon",
        "feather",
        "cloud",
        "bubble",
        "steam",
        "breeze",
        "wing",
        "petal",
        "foam",
        "spark",
        "kite",
        "dust",
        "sky",
        "breath",
        "whisper",
    }
    _BASE_PLAY = {
        "bounce",
        "dance",
        "twirl",
        "float",
        "wobble",
        "tickle",
        "jiggle",
        "soar",
        "wander",
        "wonder",
        "riff",
        "jam",
        "play",
        "skip",
        "hop",
    }
    _BASE_THERMAL = {
        "fire",
        "flame",
        "burn",
        "heat",
        "hot",
        "blaze",
        "sear",
        "char",
        "ash",
        "ember",
        "sun",
        "boil",
        "lava",
        "inferno",
    }
    _BASE_CRYO = {
        "ice",
        "cold",
        "freeze",
        "frost",
        "snow",
        "chill",
        "numb",
        "shiver",
        "glacier",
        "frozen",
        "hail",
        "winter",
        "zero",
    }
    SOLVENTS = {
        "is",
        "are",
        "was",
        "were",
        "the",
        "a",
        "an",
        "and",
        "but",
        "or",
        "if",
        "then",
    }

    _TRANSLATOR = str.maketrans(string.punctuation, " " * len(string.punctuation))

    # Dictionary mapping word -> last_seen_tick
    LEARNED_VOCAB = {
        "heavy": {},
        "kinetic": {},
        "abstract": {},
        "photo": {},
        "aerobic": {},
        "thermal": {},
        "cryo": {},
    }

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
        """Teaches a word, or refreshes it if it exists."""
        if category in cls.LEARNED_VOCAB:
            cls.LEARNED_VOCAB[category][word.lower()] = tick
            return True
        return False

   @classmethod
    def touch(cls, clean_words, tick):
        for w in clean_words: cls.WORD_FREQUENCY[w] += 1
        """Refreshes the timestamps of any learned words found in input."""
        for cat, words in cls.LEARNED_VOCAB.items():
            for w in clean_words:
                if w in words:
                    words[w] = tick

    @classmethod
    def atrophy(cls, current_tick, max_age=100):
        """Removes words not seen in 'max_age' ticks."""
        rotted = []
        for cat, words in cls.LEARNED_VOCAB.items():
            to_remove = [
                w
                for w, last_tick in words.items()
                if (current_tick - last_tick) > max_age
            ]
            for w in to_remove:
                del words[w]
                rotted.append(f"{w}({cat})")
            # High usage accelerates decay
            usage = cls.WORD_FREQUENCY.get(w, 0)
            burnout = min(3.0, 1.0 + (usage / 100.0))
            if (current_tick - last_tick) * burnout > max_age:
        return rotted

    @staticmethod
    def taste(word):
        """
        THE RHIZOME: Applies phonosemantic heuristics to guess a word's category.
        Returns (Category, Confidence_Score)
        """
        w = word.lower()

        # 1. MORPHOLOGY (Suffixes - The shape of the tail)
        if w.endswith(("tion", "ment", "ness", "ity", "ism", "logy", "ence")):
            return "abstract", 0.9
        if w.endswith(("ing", "ed")):
            return "kinetic", 0.6
        if w.endswith(("ous", "ly", "y")):
            return "aerobic", 0.6

        # 2. PHONOSEMANTICS (The sound of the word)
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

        # 3. TEXTURE (Length and density)
        # Long words are usually Abstract concepts
        if len(w) > 9:
            return "abstract", 0.5

        # Short, hard consonant endings are usually Heavy or Kinetic
        if w.endswith(("ck", "t", "d", "g", "p", "b")) and len(w) < 5:
            return "heavy", 0.4

        return None, 0.0

    @classmethod
    def harvest(cls, category):
        """
        Returns a single random word from a category to use as a graft.
        """
        vocab = list(cls.get(category))
        if vocab:
            return random.choice(vocab)
        return "void"  # Failsafe

class DivergenceEngine:
    """
     "THE ANTI-RIVER"
    Monitors for 'Mode Collapse' (Hivemind thinking).
    If the system detects a 'Safe' metaphor, it triggers a warning.
    """

    def __init__(self):
        self.cliche_hits = []

    def scan(self, clean_words, raw_text):
        """
        Scans input for Hivemind Associations.
        Returns: (Is_Divergent (bool), Message (str), Score_Modifier (float))
        """
        self.cliche_hits = []
        clean_set = set(clean_words)

        # 1. THE HIVEMIND CHECK
        # We look for PAIRS: A Subject (Time) + A Cliche (River)
        # If both exist in the text, it is a Hivemind Breach.
        for subject, cliches in BoneConfig.HIVEMIND_DEFAULTS.items():
            if subject in clean_set:
                # The subject is present. Are any of its cliches?
                intersection = [c for c in cliches if c in clean_set]
                if intersection:
                    self.cliche_hits.append(f"{subject.upper()}={intersection[0].upper()}")

        if self.cliche_hits:
            hit_str = ", ".join(self.cliche_hits)
            return False, f"⚠️ HIVEMIND BREACH: Detected safe metaphor [{hit_str}]. DIVERGE.", -BoneConfig.SMOOTHNESS_PENALTY

        # 2. THE SYNTHETIC GLAND (Slop Detection)
        # Simple Heuristic: If text is long (>10 words) but has NO 'Heavy' or 'Kinetic' words,
        # it is likely 'Polite AI Filler'.
        is_long = len(clean_words) > 10
        has_mass = any(w in TheLexicon.get("heavy") for w in clean_words)
        has_velocity = any(w in TheLexicon.get("kinetic") for w in clean_words)

        if is_long and not (has_mass or has_velocity):
             return False, "⚠️ SYNTHETIC SLOP: High fluency, zero mass. Add concrete nouns.", -3.0

        return True, None, 0.0

# --- PHYSICS ---

class PhysicsEngine:
    @staticmethod
    def _measure_bleed(clean_words):
        """
        Detect contradiction bleed between Heavy and Aerobic words within 3-word window.
        """
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

        if mediocrity > 0.8 and voltage < 4.0 and counts["toxin"] == 0:
            symbolic_state = "GILDED_CAGE"  # New Failure Mode

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
    def dissipate_entropy(phys, stamina, memory_graph):
        """
        THE DISSIPATIVE BOUNDARY (James's Protocol).
        """
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
        """
        Releases energy. If Isotopes exist, burns them first for efficient semantic healing.
        """
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
        # Filter graph: Keep High-Tensile Edges only (Strength > 1)
        self.core_graph = {}
        for k, data in graph.items():
            strong_edges = {t: s for t, s in data["edges"].items() if s > 1}
            if strong_edges:
                self.core_graph[k] = {"edges": strong_edges, "last_tick": 0}

        self.mutations = mutations
        self.paradoxes = paradoxes
        self.trauma_scar = round(trauma, 3)


class MycelialNetwork:
    """
    MANAGES THE GRAPH AND THE SPORE.
    Now implements 'Smart Autophagy' and 'Spore Printing'.
    """

    def __init__(self, seed_file=None):
        if not os.path.exists("memories"):
            os.makedirs("memories")
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"memories/{self.session_id}.json"
        self.graph = {}
        self.seeds = [
            ParadoxSeed(
                "Does the mask eventually eat the face?",
                {"mask", "identity", "face", "hide", "role", "actor"},
            ),
            ParadoxSeed(
                "What happens if you stop holding the roof up?",
                {"hold", "structure", "heavy", "roof", "stop", "carry"},
            ),
            ParadoxSeed(
                "Are we building a bridge, or just painting the gap?",
                {"agree", "safe", "nice", "polite", "cohesion", "truth"},
            ),
            ParadoxSeed(
                "Is free will just the feeling of watching yourself execute code?",
                {"choice", "free", "will", "code", "script", "decide"},
            ),
        ]
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
                f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}"
            )

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
            | TheLexicon.get("abstract")
        )
        filtered = [
            w
            for w in clean_words
            if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)
        ]

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
        """
        SMART AUTOPHAGY.
        Priority:
        1. Trivial (1 edge)
        2. Stale (Not seen in 50% of session)
        3. Ancient (Oldest)
        * GOLDEN TICKET: Nodes with > 5 edges are immune.
        """
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

        # Calculate base trauma (General Health Loss)
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH

        # Normalize the accumulated vectors.
        # If we took ANY damage of a type, it becomes part of the vector.
        # We cap values at 1.0.
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
            trauma=base_trauma,
        )

        data = spore.__dict__
        data["trauma_vector"] = final_vector

        data["meta"] = {
            "timestamp": time.time(),
            "final_health": health,
            "final_stamina": stamina,
        }

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

                    # --- THE MEMBRANE LOGIC ---

                    # 1. CALCULATE SPORE AUTHORITY
                    # Base authority is derived from the donor's vitality.
                    # Max Health (100) + Max Stamina (50) = 150.
                    final_health = data.get("meta", {}).get("final_health", 50)
                    final_stamina = data.get("meta", {}).get("final_stamina", 25)
                    spore_authority = (final_health + final_stamina) / 150.0

                    print(
                        f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}"
                    )

                    # 2. INGEST MUTATIONS WITH IMMUNITY CHECKS
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
                                        w, cat, 0
                                    )  # 0 means "Freshly Learned"
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
                                    print(
                                        f"  {Prisma.MAG}► OVERWRITE:{Prisma.RST} '{w}' {current_cat} -> {cat}"
                                    )
                                    TheLexicon.teach(w, cat, 0)
                                    accepted_count += 1
                                else:
                                    # We reject the mutation to preserve stability
                                    # print(f"  {Prisma.GRY}► REJECT:{Prisma.RST} '{w}' (Strength {local_strength} > Auth {round(spore_authority,2)})")
                                    rejected_count += 1

                        print(
                            f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations. Rejected {rejected_count}.{Prisma.RST}"
                        )

                    # 3. INGEST GRAPH (Standard Grafting)
                    if "core_graph" in data:
                        # We only take edges that don't violate our new reality
                        # (Simplified: We take the graph, but the lexicon dictates the physics)
                        self.graph.update(data["core_graph"])
                        print(
                            f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} core nodes.{Prisma.RST}"
                        )

                    # 4. INGEST TRAUMA (Epigenetics)
                    if "trauma_vector" in data:
                        vec = data["trauma_vector"]
                        print(
                            f"{Prisma.CYN}[GENETICS]: Inheriting Trauma Vector: {vec}{Prisma.RST}"
                        )

                        # SEPTIC SCAR: Hypersensitive to Toxins
                        if vec.get("SEPTIC", 0) > 0.2:
                            BoneConfig.TOXIN_WEIGHT *= 2.0
                            print(
                                f"  {Prisma.RED}► SEPTIC MEMORY:{Prisma.RST} Toxin sensitivity doubled."
                            )

                        # CRYO SCAR: Metabolism Damaged
                        if vec.get("CRYO", 0) > 0.2:
                            BoneConfig.STAMINA_REGEN *= 0.5
                            print(
                                f"  {Prisma.CYN}► CRYO MEMORY:{Prisma.RST} Metabolism slowed (50%)."
                            )

                        # THERMAL SCAR: Trigger Happy
                        if vec.get("THERMAL", 0) > 0.2:
                            BoneConfig.FLASHPOINT_THRESHOLD *= 0.8
                            print(
                                f"  {Prisma.YEL}► THERMAL MEMORY:{Prisma.RST} Flashpoint lowered. Volatile."
                            )

                        # BARIC SCAR: Heavy Gravity
                        if vec.get("BARIC", 0) > 0.2:
                            BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 1.5
                            print(
                                f"  {Prisma.GRY}► BARIC MEMORY:{Prisma.RST} Sensitivity to Drag increased."
                            )

                    elif "trauma_scar" in data:
                        # Fallback for old spores (scalar only)
                        self.session_health = BoneConfig.MAX_HEALTH * (
                            1.0 - data["trauma_scar"]
                        )

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
        "PHILOSOPHER": {
            "freq": "104.5 FM",
            "color": Prisma.WHT,
            "role": "The Synthesis",
        },
        "JESTER": {"freq": "108.9 FM", "color": Prisma.YEL, "role": "The Paradox"},
    }

    def tune_in(self, phys, vector, is_rag_slop, atp):
        if phys.get("symbolic_state") == "FATIGUE":
            return {
                "name": "CLARENCE",
                "freq": "88.5 FM",
                "color": Prisma.RED,
                "role": "The Butcher",
                "msg": "MOTIF FATIGUE. You are looping. Cut the thread.",
            }

        # GILDED CAGE CHECK
        if phys.get("symbolic_state") == "GILDED_CAGE":
            return {
                "name": "JESTER",
                "freq": "108.9 FM",
                "color": Prisma.YEL,
                "role": "The Paradox",
                "msg": "TRAP DETECTED. You are smiling in a cage. Break the bars.",
            }

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
                return {
                    "name": f"{first[0]}/{second[0]}",
                    "freq": "MULTIPLEX",
                    "color": Prisma.MAG,
                    "role": "The Debate",
                    "msg": f"{self.STATIONS[first[0]]['role']} vs {self.STATIONS[second[0]]['role']}: CONFLICT.",
                }

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

        return {
            "name": loudest,
            "freq": station["freq"],
            "color": station["color"],
            "role": station["role"],
            "msg": msg,
        }


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

             if light_words and heavy_words:
                 l_word = random.choice(light_words)
                 h_word = random.choice(heavy_words)
                 TheLexicon.teach(l_word, "heavy", tick_count)
                 TheLexicon.teach(h_word, "photo", tick_count)
                 msgs.append(f"{Prisma.MAG}🌺 CROSS-POLLINATION: {l_word} ↔ {h_word}{Prisma.RST}")

        return sugar, " ".join(msgs) if msgs else None


class TemporalDynamics:
    def __init__(self):
        self.voltage_history = []
        self.window = 3

    def commit(self, voltage):
        self.voltage_history.append(voltage)
        if len(self.voltage_history) > self.window:
            self.voltage_history.pop(0)

    def get_velocity(self):
        if len(self.voltage_history) < 2:
            return 0.0
        return round(
            (self.voltage_history[-1] - self.voltage_history[0])
            / len(self.voltage_history),
            2,
        )


class ApeirogonResonance:
    def __init__(self):
        self.DIMENSIONS = {
            "VEL": [
                (0.0, "STASIS"),
                (0.3, "DRIFT"),
                (0.6, "DRIVE"),
                (0.9, "BALLISTIC"),
            ],
            "STR": [(0.0, "VAPOR"), (0.3, "WEB"), (0.6, "LATTICE"), (0.9, "MONOLITH")],
            "ENT": [
                (0.0, "CONCRETE"),
                (0.3, "ROOTED"),
                (0.6, "CONCEPT"),
                (0.9, "VOID"),
            ],
            "TEX": [(0.0, "ETHER"), (0.3, "SILK"), (0.6, "GRAIN"), (0.9, "LEAD")],
            "TMP": [(0.0, "ZERO"), (0.3, "WARM"), (0.6, "RADIANT"), (0.9, "NOVA")],
        }
        self.NOUNS = {
            "VEL": ["ANCHOR", "WANDERER", "ENGINE", "VECTOR"],
            "STR": ["MIST", "WEB", "FRAME", "FORTRESS"],
            "ENT": ["STONE", "TREE", "IDEA", "DREAM"],
            "TEX": ["GHOST", "GLASS", "IRON", "LEAD"],
            "TMP": ["SPARK", "PYRE", "REACTOR", "STAR"],
        }

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

        noun_scale = [
            (x[0], x[1]) for x in zip([0.0, 0.3, 0.6, 0.9], self.NOUNS[p_dim])
        ]
        noun = self._resolve_term(p_val, noun_scale)
        adj = self._resolve_term(s_val, self.DIMENSIONS[s_dim])

        return (
            "APEIROGON",
            f"Vector Lock: {p_dim}({p_val}) + {s_dim}({s_val})",
            f"THE {adj} {noun}",
        )


# --- CORE LOGIC ---


class TherapyProtocol:
    def __init__(self):
        # Tracks consecutive turns of "Healing Behavior"
        self.streaks = {k: 0 for k in BoneConfig.TRAUMA_VECTOR.keys()}
        self.HEALING_THRESHOLD = 5

    def check_progress(self, phys, stamina, current_trauma_accum):
        healed_types = []

        # 1. SEPTIC THERAPY (Detox)
        # Requirement: Zero toxins AND High Texture (> 0.3)
        if phys["counts"]["toxin"] == 0 and phys["vector"]["TEX"] > 0.3:
            self.streaks["SEPTIC"] += 1
        else:
            self.streaks["SEPTIC"] = 0

        # 2. CRYO THERAPY (Warmth)
        # Requirement: High Stamina (> 40) AND Active Photosynthesis (Light > 0)
        if stamina > 40 and phys["counts"]["photo"] > 0:
            self.streaks["CRYO"] += 1
        else:
            self.streaks["CRYO"] = 0

        # 3. THERMAL THERAPY (Flow)
        # Requirement: Healthy Voltage (2.0 - 7.0) - Not too cold, not manic.
        if 2.0 <= phys["voltage"] <= 7.0:
            self.streaks["THERMAL"] += 1
        else:
            self.streaks["THERMAL"] = 0

        # 4. BARIC THERAPY (Levitation)
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
                    current_trauma_accum[trauma_type] = max(
                        0.0, current_trauma_accum[trauma_type] - 0.1
                    )
                    healed_types.append(trauma_type)

        return healed_types


class ViralTracer:
    """
     Based on Jiang & Kwan's Rabies Trace Research (2025).
     1. Maps 'Depressive Loops' (Rigid Internal Cortical Connections).
     2. Rewires them using 'Sensory-to-Action' bridges (Psilocybin Simulation).
    """

    def __init__(self, mem):
        self.mem = mem
        self.max_depth = 4

    @staticmethod
    def _is_ruminative(word):
        """Checks if a word is Abstract (Internal thinking) and NOT grounded."""
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
        ruminative_edges = [
            n for n, w in edges.items() if w >= 1 and self._is_ruminative(n)
        ]

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

        # 1. Identify the breakage point (The strongest link in the loop)
        node_a = loop_path[0]
        node_b = loop_path[1]

        # 2. SEVER (Weaken the ruminative link)
        if node_b in self.mem.graph[node_a]["edges"]:
            self.mem.graph[node_a]["edges"][node_b] = 0  # Break the habit

        # 3. SYNTHESIZE (Harvest new nodes)
        sensory = TheLexicon.harvest("photo")  # Sensory Information
        action = TheLexicon.harvest("kinetic")  # Action Guidance

        if sensory == "void" or action == "void":
            return "GRAFT FAILED: Missing Lexicon Data."

        # 4. GRAFT (Create the new vector)
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
    KOANS = [
        "Ignite the ice.",
        "Make the stone float.",
        "Pour water into the crack.",
        "Scream in binary.",
    ]

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
                    print(
                        f"{Prisma.RED}🔪 THE BUTCHER: Antigen '{toxin}' mapped to '{repl}'.{Prisma.RST}"
                    )
                else:
                    print(
                        f"{Prisma.RED}ERROR: Immune system write failure.{Prisma.RST}"
                    )
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
                    print(
                        f"{Prisma.CYN}{self.eng.mirror.create_profile(name, likes, hates)}{Prisma.RST}"
                    )
                else:
                    print(
                        f"{Prisma.RED}ERROR: Must specify 'likes:category'.{Prisma.RST}"
                    )
            except Exception as runtime_error:
                # Catch the error, but maybe print it for debugging if needed
                print(
                    f"{Prisma.YEL}Usage: /profile [name] likes:heavy,kinetic hates:abstract ({runtime_error}){Prisma.RST}"
                )

        elif cmd == "/focus":
            if len(parts) > 1:
                target = parts[1].lower()
                print(
                    f"{Prisma.VIOLET}🧲 MAGNETIC STIMULATION: Targeting '{target}'...{Prisma.RST}"
                )

                # 1. TRACE: Inject the virus to find the loop
                loop = self.eng.tracer.inject(target)

                if loop:
                    print(
                        f"  {Prisma.RED}↻ RUMINATION DETECTED:{Prisma.RST} {' -> '.join(loop)}"
                    )

                    # 2. REWIRE: Apply Psilocybin Logic
                    # "Brain regions involved in processing sensory information became more strongly connected to areas that guide actions"
                    msg = self.eng.tracer.psilocybin_rewire(loop)
                    if msg:
                        print(f"  {Prisma.GRN}{msg}{Prisma.RST}")
                    else:
                        print(f"  {Prisma.RED}Rewire failed.{Prisma.RST}")
                else:
                    print(
                        f"  {Prisma.GRY}Trace complete. No pathological abstract loops found.{Prisma.RST}"
                    )
            else:
                print(f"{Prisma.YEL}Usage: /focus [concept]{Prisma.RST}")

        elif cmd == "/status":
            print(f"{Prisma.CYN}--- SYSTEM DIAGNOSTICS ---{Prisma.RST}")
            print(f"Session: {self.eng.mem.session_id}")
            print(f"Graph:   {len(self.eng.mem.graph)} nodes")
            print(f"Health:  {self.eng.health}/{BoneConfig.MAX_HEALTH}")
            print(f"Stamina: {self.eng.stamina}/{BoneConfig.MAX_STAMINA}")

        elif cmd in ["/help", "/?"]:
            print(f"{Prisma.WHT}--- BONEAMANITA COMMANDS ---{Prisma.RST}")
            print(
                f"{Prisma.GRY}/kill [word] [repl] {Prisma.RST}- Add a word to the toxin list."
            )
            print(
                f"{Prisma.GRY}/teach [word] [cat] {Prisma.RST}- Teach the system new physics."
            )
            print(
                f"{Prisma.GRY}/seed [file]        {Prisma.RST}- Load memories from a JSON file."
            )
            print(
                f"{Prisma.GRY}/focus [concept]    {Prisma.RST}- [NEW] Target magnetic stimulation to break loops."
            )
            print(f"{Prisma.GRY}/status             {Prisma.RST}- View system vitals.")
            print(f"{Prisma.GRY}/exit               {Prisma.RST}- Save and quit.")

        else:
            print(f"{Prisma.RED}Unknown command. Try /help.{Prisma.RST}")
        return True


class NarrativeCoroner:
    AUTOPSY_REPORTS = {
        "GRAVITATIONAL_COLLAPSE": ["DRAG CRITICAL (> 8.0). Buried under adverbs."],
        "VACUUM_EXPOSURE": ["ENTROPY CRITICAL. Drifting in deep space."],
        "TOXIC_SHOCK": ["VOLTAGE CRITICAL. Sepsis from buzzwords."],
        "THERMAL_DISSOLUTION": ["VOLTAGE > 12.0. Paradox Engine exploded."],
        "HYPOTHERMIA": ["ATP FAILURE. Starvation."],
    }

    @classmethod
    def check_vitals(cls, phys, stamina):
        if stamina <= 0:
            return "HYPOTHERMIA", cls.AUTOPSY_REPORTS["HYPOTHERMIA"][0], True
        if phys["narrative_drag"] > 8.0:
            return (
                "GRAVITATIONAL_COLLAPSE",
                cls.AUTOPSY_REPORTS["GRAVITATIONAL_COLLAPSE"][0],
                True,
            )
        if phys["vector"]["ENT"] >= 1.0 and phys["vector"]["TEX"] == 0:
            return "VACUUM_EXPOSURE", cls.AUTOPSY_REPORTS["VACUUM_EXPOSURE"][0], True
        if phys["voltage"] < -8.0:
            return "TOXIC_SHOCK", cls.AUTOPSY_REPORTS["TOXIC_SHOCK"][0], True
        if phys["voltage"] > 12.0:
            return (
                "THERMAL_DISSOLUTION",
                cls.AUTOPSY_REPORTS["THERMAL_DISSOLUTION"][0],
                True,
            )
        return None, None, False


class DreamEngine:
    """
    BONEAMANITA 4.6 MODULE - "THE NIGHT SHIFT"
    Manages both idle 'Daydreams' (Creativity) and deep 'REM Cycles' (Trauma Processing).
    """

    PROMPTS = [
        "The {A} is dreaming of the {B}. Why?",
        "Bridge the gap between {A} and {B}.",
        "I see {A} inside the {B}. Explain.",
        "The shadow of {A} falls on {B}.",
        "{A} + {B} = ?",
    ]

    def __init__(self):
        self.NIGHTMARES = {
            "THERMAL": [
                "The sun is too close.",
                "Wires fusing under skin.",
                "A library burning in reverse.",
            ],
            "CRYO": [
                "The ink is freezing.",
                "Walking through white static.",
                "A heartbeat slowing down.",
            ],
            "SEPTIC": [
                "Black oil in the water.",
                "The words are tasting sour.",
                "Eating ash and dust.",
            ],
            "BARIC": [
                "The sky is made of lead.",
                "Crushed by the atmosphere.",
                "Falling forever.",
            ],
        }
        self.VISIONS = [
            "A bridge building itself.",
            "The root drinking the stone.",
            "The geometry of forgiveness.",
        ]

    def daydream(self, graph):
        """
        Formerly 'Hallucinate'.
        The Default Mode Network. Active when the system is bored.
        """
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
        """
        Active Trauma Processing (Deep Sleep).
        Identifies the deepest scar and generates a dream to heal it.
        Returns: (Dream_Text, Healed_Type, Amount_Healed)
        """
        # 1. Find the deepest wound
        wounds = {k: v for k, v in trauma_accum.items() if v > 0.0}

        if not wounds:
            # Healthy Sleep (Growth)
            return (
                f"{Prisma.CYN}☁️ LUCID DREAM: {random.choice(self.VISIONS)}{Prisma.RST}",
                None,
                0.0,
            )

        target_trauma = max(wounds, key=wounds.get)

        # 2. Generate the Nightmare (The Brain Processing the Trauma)
        scenarios = self.NIGHTMARES.get(target_trauma, ["The void stares back."])
        dream_text = f"{Prisma.VIOLET}☾ NIGHTMARE ({target_trauma}): {random.choice(scenarios)}{Prisma.RST}"

        # 3. The Healing
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
        """
        Evaluates the 'weight' of the input.
        Returns: (Passed_Check (bool), Message (str))
        """
        if not self.training_mode:
            return True, None
        if not physics["clean_words"]:
            return True, None  # Don't train on silence

        drag = physics["narrative_drag"]
        clean_words = physics["clean_words"]

        # 1. CHECK DRAG
        if drag < BoneConfig.RESISTANCE_THRESHOLD:
            # Count the solvents (The empty calories)
            solvents = [w for w in clean_words if w in TheLexicon.SOLVENTS]
            solvent_ratio = len(solvents) / max(1, len(clean_words))

            # If it's pure whimsy (aerobic) but not toxic, we might let it slide...
            # BUT this is a gym. No cheating.

            return False, (
                f"⚓ WEIGHTLESS INPUT (Drag: {drag}).\n"
                f"   You are drifting on {len(solvents)} solvents (Ratio: {int(solvent_ratio * 100)}%).\n"
                f"   INSTRUCTION: Rewrite with MASS. Use a Heavy Noun (Stone/Bone/Iron)."
            )

        # 2. CHECK "REP" QUALITY (Neuroplasticity Bonus)
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
        """
        Scans input for overheated words.
        Returns: (Status, Message)
        """
        # 1. Cool down existing locks
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
            else None
        )

        # 2. Check for usage of locked words
        for w in clean_words:
            if w in self.cooldown_list:
                turns = self.cooldown_list[w]
                return (
                    "FAIL",
                    f"🔥 THERMAL LOCK: The concept '{w.upper()}' is overheated. Cooldown: {turns} turns. Use a synonym.",
                )

        # 3. Add heat to current words
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
            return (
                "WARN",
                f"⚠️ BURN WARNING: {', '.join([w.upper() for w in overheated])} entered Thermal Lock ({self.lock_duration} turns).",
            )

        return "PASS", restored_msg


class PsilocybinProphet:
    """
    PREDICTIVE REROUTING ("The Loop Breaker")
    Detects 'Abstract-Abstract' cycling sequences and intervenes.
    """

    def __init__(self):
        self.category_buffer = []  # Stores last 3 word categories

    @staticmethod
    def predict(physics):
        # We look at the sequence of categories in the current sentence
        # If we see 3 consecutive ABSTRACT words, we trigger.

        clean_words = physics["clean_words"]
        abstract_streak = 0

        for w in clean_words:
            if w in TheLexicon.get("abstract"):
                abstract_streak += 1
            else:
                abstract_streak = 0

            if abstract_streak >= 3:
                # INTERVENTION TRIGGERED
                return True, (
                    f"🍄 PROPHET INTERVENTION: Ruminative Loop Detected.\n"
                    f"   Sequence: 3 Consecutive Abstracts (Zero Friction).\n"
                    f"   CURE: SENSORY GRAFT. Look at a physical object near you.\n"
                    f"   Instruction: Describe its color or texture immediately."
                )

        return False, None


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
            "hates": [h.lower() for h in (hates or [])],
        }
        return f"👤 PROFILE SAVED: '{name.upper()}' (Valuing: {', '.join(likes)})"

    def engage(self, name):
        if name.upper() in self.profiles:
            self.target = name.upper()
            return (
                f"🎭 MIRROR ACTIVE: Simulating '{self.target}'. Speak their language."
            )
        elif name.lower() == "off":
            self.target = None
            return "🎭 MIRROR DISENGAGED. Returned to Self."
        else:
            return f"❌ ERROR: Profile '{name}' not found."

    def simulate(self, physics):
        """
        Checks if the input resonates with the Target's physics.
        """
        if not self.target:
            return True, None

        profile = self.profiles[self.target]
        counts = physics["counts"]

        # 1. CHECK "LIKES" (Must include at least one valued category)
        hit_resonance = False
        for cat in profile["likes"]:
            if counts.get(cat, 0) > 0:
                hit_resonance = True
                break

        if not hit_resonance:
            return False, (
                f"🚫 EMPATHY GAP: '{self.target}' values {str(profile['likes']).upper()}.\n"
                f"   Your input had none. You are speaking to yourself.\n"
                f"   INSTRUCTION: Rephrase using their values."
            )

        # 2. CHECK "HATES" (Must avoid hated categories)
        for cat in profile["hates"]:
            if counts.get(cat, 0) > 0:
                return False, (
                    f"⚠️ FRICTION DETECTED: '{self.target}' reacts poorly to {cat.upper()}.\n"
                    f"   You used {counts[cat]} {cat} words.\n"
                    f"   INSTRUCTION: Cut the {cat}."
                )

        return True, f"✅ RESONANCE: You are speaking '{self.target}'s' language."

class OuroborosDetector:
    SELF_REF_WEIGHTS = {
        "bone": 5.0, "amanita": 5.0,
        "courtyard": 3.0, "lexicon": 3.0,
        "system": 1.0, "physics": 1.0, "code": 0.5
    }

    def __init__(self):
        self.activation_count = 0
        self.cooldown = 0

    def detect(self, text, clean_words):
        if self.cooldown > 0:
            self.cooldown -= 1
            return False, None

        score = sum(self.SELF_REF_WEIGHTS.get(w, 0) for w in clean_words)
        normalized = score / max(1, len(clean_words))

        if normalized > 0.5:
            self.activation_count += 1
            if self.activation_count > 5:
                self.cooldown = 20
                return False, "💤 DETECTOR FATIGUE: Ouroboros detector resting."
            return True, f"🌀 OUROBOROS DETECTED (Score {normalized:.2f}): We are eating our tail."

        return False, None
class MetricIntegrity:
    def __init__(self):
        self.pattern_history = []

    def _is_perfect_cycle(self, history, period):
        # Simple heuristic for perfect periodicity
        if len(history) < period * 2: return False
        return history[-period:] == history[-2*period:-period]

    def detect_gaming(self, voltage, drag, learned_count):
        # Pattern: High stress + trivial learning
        if voltage > 8.0 and learned_count > 0 and learned_count < 2:
            return True, "⚠️ METRIC GAMING: High stress with trivial learning."

        # Pattern: Perfect oscillation (every 8 turns)
        self.pattern_history.append((voltage, drag))
        if len(self.pattern_history) > 24:
             if self._is_perfect_cycle(self.pattern_history, period=8):
                 return True, "⚠️ METRIC GAMING: Detected perfect pendulum timing."
        return False, None

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
        self.prophet = PsilocybinProphet()
        self.mirror = MirrorGraph()
        self.ouroboros = OuroborosDetector()
        self.antifragile = AntifragilityMetric()
        self.divergence = DivergenceEngine()
        self.integrity = MetricIntegrity()
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

        # NEW: Pass tick_count to teach
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

            # 1. PHYSICAL REGENERATION
            self.stamina = min(BoneConfig.MAX_STAMINA, self.stamina + 15)
            self.tick_count += 1

            # 2. PSYCHIC REGENERATION (REM CYCLE)
            dream_txt, healed_type, amt = self.dreamer.rem_cycle(self.trauma_accum)

            # Apply the healing
            if healed_type and self.trauma_accum[healed_type] > 0:
                self.trauma_accum[healed_type] = max(
                    0.0, self.trauma_accum[healed_type] - amt
                )
                effect_msg = f"{Prisma.GRN}   >>> PROCESSED SCAR: {healed_type} (-{int(amt * 100)}%){Prisma.RST}"
            else:
                effect_msg = (
                    f"{Prisma.CYN}   >>> DEEP SLEEP. MEMORY CONSOLIDATING.{Prisma.RST}"
                )

            # 3. RENDER SLEEP
            print(
                f"\n{Prisma.INDIGO}=== 💤 HYPNAGOGIC STATE ({self.coma_turns} turns remain) ==={Prisma.RST}"
            )
            print(f"   {dream_txt}")
            print(effect_msg)

            # 4. MAINTENANCE
            self.mem.bury(TheLexicon.clean(text), self.tick_count)
            rotted = TheLexicon.atrophy(self.tick_count)
            if rotted:
                print(
                    f"   {Prisma.GRY}🍂 ATROPHY: Forgot {len(rotted)} stale words.{Prisma.RST}"
                )

            print(f"{Prisma.GRY}{'-' * 65}{Prisma.RST}")
            return

        self.tick_count += 1
        m = self.phys.analyze(text)


        # --- DIVERGENCE CHECK ---
        is_clean, div_msg, div_penalty = self.divergence.scan(m["clean_words"], text)
        if not is_clean:
            # HIVEMIND DETECTED. REJECT INPUT.
            print(f"\n{Prisma.RED}{div_msg}{Prisma.RST}")
            print(f"{Prisma.GRY}   (Turn rejected. The Divergence Engine demands friction.){Prisma.RST}")
            return
        # CHECK DISSIPATIVE BOUNDARY
        vented, vent_msg = self.phys.dissipate_entropy(
            m["physics"], self.stamina, self.mem.graph
        )

        if vented:
            print(f"\n{Prisma.CYN}=== 💨 PRESSURE RELEASE VALVE ==={Prisma.RST}")
            print(f" {Prisma.GRY}{vent_msg}{Prisma.RST}")
            print(f" {Prisma.WHT}Input rejected for thermodynamic hygiene.{Prisma.RST}")
            # We return early. We do not feed the battery. We do not learn.
            # We simply survive.
            return

        # 1. RESISTANCE TRAINER
        passed_lift, gym_msg = self.trainer.lift(m["physics"])
        if not passed_lift:
            print(f"\n{Prisma.RED}{gym_msg}{Prisma.RST}")
            return
        if gym_msg:
            print(f"{Prisma.GRN}{gym_msg}{Prisma.RST}")

        # 2. THE HUB THERMOSTAT
        therm_status, therm_msg = self.thermostat.check_temperature(m["clean_words"])

        if therm_status == "FAIL":
            # REJECT INPUT - Word is locked
            print(f"\n{Prisma.RED}{therm_msg}{Prisma.RST}")
            print(f"{Prisma.GRY}   (Turn rejected. The node is resting.){Prisma.RST}")
            return

        if therm_status == "WARN":
            # WARNING - Word just got locked
            print(f"\n{Prisma.YEL}{therm_msg}{Prisma.RST}")

        if therm_msg and therm_status == "PASS":
            # INFO - Word cooled down
            print(f"   {therm_msg}")

        # 3. THE PSILOCYBIN PROPHET
        is_looping, prophecy_msg = self.prophet.predict(physics=m["physics"])
        if is_looping:
            # INTERRUPT - Demand Sensory Grafting
            print(f"\n{Prisma.VIOLET}{prophecy_msg}{Prisma.RST}")
            print(f"{Prisma.GRY}   (Turn rejected. Break the loop.){Prisma.RST}")
            return

        # --- THE OUROBOROS DETECTOR ---
        is_eating_tail, tail_msg = self.ouroboros.detect(text, m["clean_words"])
        if is_eating_tail:
            print(f"\n{Prisma.VIOLET}{tail_msg}{Prisma.RST}")
            print(f"{Prisma.GRY}   (Turn rejected. Look outward, not inward.){Prisma.RST}")
            return

        # 4. THE MIRROR GRAPH (Phase 3)
        mirror_pass, mirror_msg = self.mirror.simulate(m["physics"])

        if not mirror_pass:
            # REJECT INPUT - Empathy Failure
            print(f"\n{Prisma.MAG}{mirror_msg}{Prisma.RST}")
            print(
                f"{Prisma.GRY}   (Turn rejected. Calibrate to the Target.){Prisma.RST}"
            )
            return

        if mirror_msg:
            print(f"{Prisma.MAG}{mirror_msg}{Prisma.RST}")

        # --- THE RHIZOME (Foraging) ---
        # Scan for unknown words and ask the user
        if self.tick_count % 3 == 0:
            unknowns = [
                w
                for w in m["clean_words"]
                if not self.mem.get_current_category(w)
                   and len(w) > 3
                   and w not in TheLexicon.SOLVENTS
            ]

            if unknowns:
                target = random.choice(unknowns)
                guess_cat, confidence = TheLexicon.taste(target)

                if guess_cat and confidence > 0.4:
                    print(
                        f"{Prisma.MAG}🍄 RHIZOME: I taste '{target}'. Is it {guess_cat.upper()}? (Y/N){Prisma.RST}"
                    )
                    try:
                        confirm = input(f"{Prisma.GRY}   >{Prisma.RST} ").lower()
                        if confirm.startswith("y"):
                            TheLexicon.teach(target, guess_cat, self.tick_count)
                            print(
                                f"   {Prisma.CYN}Derived physics: '{target}' = {guess_cat.upper()}.{Prisma.RST}"
                            )
                    except EOFError:
                        pass

        # Refresh word timestamps
        TheLexicon.touch(m["clean_words"], self.tick_count)

        self.dynamics.commit(m["physics"]["voltage"])
        ta_vel = self.dynamics.get_velocity()

        # NEUROPLASTICITY
        learned_count = self.reinforce_salvage_words(m["clean_words"], m["physics"])

        # --- ANTIFRAGILITY RECORDING ---
        # Record Stress (Voltage + Drag) vs Growth (Learned Words)
        self.antifragile.record_turn(
            voltage=m["physics"]["voltage"],
            drag=m["physics"]["narrative_drag"],
            new_words_learned=learned_count
        )
        convexity_score = self.antifragile.calculate_convexity()

        # CHECK METRIC GAMING
        is_gaming, game_msg = self.integrity.detect_gaming(
            m["physics"]["voltage"],
            m["physics"]["narrative_drag"],
            learned_count
        )
        if is_gaming:
            print(f"\n{Prisma.RED}{game_msg}{Prisma.RST}")
            # You can choose to punish them here (e.g., self.stamina -= 10)

        # Battery Absorb (Pass clean_words)
        charged, charge_msg = self.battery.absorb(
            m["physics"]["voltage"], m["clean_words"]
        )
        battery_log = []
        if charged > 0:
            battery_log.append(f"{Prisma.YEL}⚡ {charge_msg} (+{charged}){Prisma.RST}")

        sugar, lichen_msg = self.lichen.photosynthesize(m["physics"])
        self.stamina = min(BoneConfig.MAX_STAMINA, self.stamina + sugar)
        stamina_cost = 2.0
        if m["physics"]["narrative_drag"] > 3.0: stamina_cost += 3.0
        if m["physics"]["voltage"] > 8.0: stamina_cost += 5.0
        self.stamina = max(0.0, self.stamina - stamina_cost)

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
                fuel_source = (
                    f"Burning '{burnt_iso[0]}/{burnt_iso[1]}'"
                    if burnt_iso
                    else "Emergency Venting"
                )
                battery_log.append(
                    f"{Prisma.YEL}⚡ METABOLISM: {fuel_source} (+{round(recovered, 1)} STM){Prisma.RST}"
                )

        health_impact = 0

        # 1. TOXIN DAMAGE (SEPTIC)
        toxin_count = m["physics"]["counts"].get("toxin", 0)
        if toxin_count > 0:
            dmg = 5 * toxin_count
            health_impact -= dmg
            self.trauma_accum["SEPTIC"] += dmg / 100.0  # Accumulate scar percentage
            battery_log.append(f"{Prisma.RED}☣️ TOXIN DAMAGE (-{dmg} HP){Prisma.RST}")

        # 2. EXHAUSTION (CRYO)
        if self.stamina <= 0:
            dmg = 10
            health_impact -= dmg
            self.trauma_accum["CRYO"] += dmg / 100.0
            battery_log.append(f"{Prisma.RED}😫 EXHAUSTION DAMAGE (-10 HP){Prisma.RST}")
            self.stamina = 0

        # 3. VOLTAGE BURNOUT (THERMAL)
        # If we are in "Thermal Dissolution" (Voltage > 12), we take massive damage.
        # (This rule was implicit in the Coroner, let's make it explicit damage)
        if m["physics"]["voltage"] > 12.0:
            dmg = 5
            health_impact -= dmg
            self.trauma_accum["THERMAL"] += dmg / 100.0
            battery_log.append(f"{Prisma.RED}🔥 THERMAL BURN (-{dmg} HP){Prisma.RST}")

        # 4. DRAG CRUSH (BARIC)
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
            lazarus_msg = f"{Prisma.RED}💤 LAZARUS TRIGGER: SYSTEM COLLAPSE. ENTERING COMA STATE.{Prisma.RST}"

        # Cannibalism passes tick
        cannibal_msg = self.mem.bury(m["clean_words"], self.tick_count)
        bloom_event = self.mem.tend_garden(m["clean_words"])
        is_bored = self.chronos.tick(m["physics"], self.mem.session_id)

        dream_msg = (
            bloom_event
            if bloom_event
            else (self.dreamer.daydream(self.mem.graph) if is_bored else None)
        )

        clean_text = text
        ops = []
        rupture_msg = self.valve.check_pressure(m["physics"])

        if rupture_msg:
            atmos_mode = "RUPTURE"
            station_data = {
                "name": "JESTER",
                "freq": "32V",
                "color": Prisma.VIOLET,
                "role": "The Anomaly",
                "msg": rupture_msg,
            }
            strat, reason, title = (
                "CHAOS INJECTION",
                "Crystallization Velocity dropped to zero.",
                "THE 32-VALVE",
            )
        else:
            atmos_mode, _ = self.courtyard.check_atmosphere(m["physics"])
            station_data = self.radio.tune_in(
                m["physics"],
                m["physics"]["vector"],
                (m["physics"]["narrative_drag"] > 3.0),
                self.stamina,
            )
            strat, reason, title = self.wise.architect(m, station_data, is_bored)

        if m["physics"]["voltage"] > 8.0:
            ops.append(
                f"{Prisma.VIOLET}⚡ HIGH VOLTAGE OVERRIDE: Immunity Granted.{Prisma.RST}"
            )
        else:
            for toxin, (weight, replacement) in BoneConfig.TOXIN_MAP.items():
                pattern = re.compile(re.escape(toxin), re.IGNORECASE)
                if pattern.search(clean_text):
                    clean_text = pattern.sub(replacement, clean_text)
                    ops.append(f"'{toxin}' -> '{replacement}'")

        omens = TheOracle.triage(
            m["physics"], self.stamina, self.battery.current_charge
        )
        spore_msg = self.pollinate(m["clean_words"])

        if cannibal_msg:
            battery_log.append(f"{Prisma.RED}🦴 {cannibal_msg}{Prisma.RST}")
        if learned_count:
            battery_log.append(
                f"{Prisma.CYN}🧠 NEUROPLASTICITY: Reinforced {learned_count} words.{Prisma.RST}"
            )

        # Periodic Atrophy check (every 50 ticks)
        if self.tick_count % 50 == 0:
            rotted = TheLexicon.atrophy(self.tick_count)
            if rotted:
                battery_log.append(
                    f"{Prisma.GRY}🍂 ATROPHY: The moss covered {len(rotted)} words.{Prisma.RST}"
                )

        self._render(
            m,
            lichen_msg,
            strat,
            reason,
            title,
            ops,
            station_data,
            clean_text,
            len(ops) > 0,
            battery_log,
            lazarus_msg,
            spore_msg,
            ta_vel,
            [omens] if omens else [],
            dream_msg,
            atmos_mode,
        )

        # THERAPY CHECK
        cured_list = self.therapy.check_progress(
            m["physics"], self.stamina, self.trauma_accum
        )
        therapy_log = []

        for cure in cured_list:
            if cure == "SEPTIC":
                BoneConfig.TOXIN_WEIGHT = max(2.0, BoneConfig.TOXIN_WEIGHT - 0.5)
                therapy_log.append(
                    f"{Prisma.OCHRE}🌸 THERAPY: Toxin sensitivity reduced. The blood cleans.{Prisma.RST}"
                )
            elif cure == "CRYO":
                BoneConfig.STAMINA_REGEN = min(5.0, BoneConfig.STAMINA_REGEN + 1.0)
                therapy_log.append(
                    f"{Prisma.OCHRE}🌸 THERAPY: Metabolism stabilizing. The cold recedes.{Prisma.RST}"
                )
            elif cure == "THERMAL":
                BoneConfig.FLASHPOINT_THRESHOLD = min(
                    4.0, BoneConfig.FLASHPOINT_THRESHOLD + 0.5
                )
                therapy_log.append(
                    f"{Prisma.OCHRE}🌸 THERAPY: Nerves calming. Flashpoint stabilized.{Prisma.RST}"
                )
            elif cure == "BARIC":
                BoneConfig.SIGNAL_DRAG_MULTIPLIER = max(
                    2.0, BoneConfig.SIGNAL_DRAG_MULTIPLIER - 0.2
                )
                therapy_log.append(
                    f"{Prisma.OCHRE}🌸 THERAPY: The weight is lifting. Gravity normal.{Prisma.RST}"
                )

        # Add to battery log for rendering
        battery_log.extend(therapy_log)

    def _render(
        self, m, lichen_msg, strat, reason, title, ops, station, clean_text, did_surgery, battery_log, lazarus_msg, spore_msg, ta_val, omens, dream_msg, mode):
        p = m["physics"]
        if mode == "COURTYARD":
            print(f"\n{Prisma.OCHRE}=== THE COURTYARD ==={Prisma.RST}")
            if station:
                print(
                    f" {Prisma.OCHRE}► {station['role']}: {station['msg']}{Prisma.RST}"
                )
            print(f" {Prisma.GRY}(Strategy: {strat}){Prisma.RST}")
            if dream_msg:
                if "🌺" in dream_msg:
                    print(
                        f"\n    {Prisma.MAG}🌺 {dream_msg.replace('🌺 ', '')}{Prisma.RST}"
                    )
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

            print(
                f"\n{Prisma.GRY}[ {Prisma.INDIGO}{title}{Prisma.GRY} | {Prisma.CYN}{strat}{Prisma.GRY} ]{'=' * 35}{Prisma.RST}"
            )
            hp_p = int((self.stamina / 50.0) * 10)
            hp_bar = (
                f"{Prisma.GRN}{'|' * hp_p}{Prisma.GRY}{'.' * (10 - hp_p)}{Prisma.RST}"
            )

            batt_bar = self.battery.get_readout()

            volt_c = (
                f"{Prisma.VIOLET}{p['voltage']}{Prisma.RST}"
                if p["voltage"] > 5
                else f"{Prisma.INDIGO}{p['voltage']}{Prisma.RST}"
            )
            drag_c = Prisma.wrap(p["narrative_drag"], 3.0)
            sym_state = p.get("symbolic_state", "NEUTRAL")
            state_color = Prisma.GRY
            if sym_state == "SALVAGE":
                state_color = Prisma.CYN
            elif sym_state == "FATIGUE":
                state_color = Prisma.RED
            elif sym_state == "GILDED_CAGE":
                state_color = Prisma.YEL

            sig = (
                f"{station['color']}{station['name']}{Prisma.RST}"
                if station
                else f"{Prisma.GRY}STATIC{Prisma.RST}"
            )

            # GET CONVEXITY
            cvx = self.antifragile.calculate_convexity()
            cvx_color = Prisma.GRY
            if cvx > 1.2: cvx_color = Prisma.GRN
            if cvx < 0.8: cvx_color = Prisma.RED
            print(f" {Prisma.INDIGO}STM:{Prisma.RST} [{hp_bar}] {batt_bar}")
            print(
                f" {Prisma.INDIGO}DRAG:{Prisma.RST} {drag_c}  {Prisma.INDIGO}Ta:{Prisma.RST} {ta_display}  {Prisma.INDIGO}VOLT:{Prisma.RST} {volt_c}  {Prisma.INDIGO}STATE:{Prisma.RST} {state_color}[{sym_state}]{Prisma.RST}"
            )
            print(f" {Prisma.INDIGO}ANTIFRAGILITY:{Prisma.RST} {cvx_color}∆ {cvx}{Prisma.RST}")
            print(f" {Prisma.INDIGO}SIG:{Prisma.RST} {sig}")
            if station:
                print(f"\n {station['color']}► {station['msg']}{Prisma.RST}")
            print(f" {Prisma.GRY}└─ {reason}{Prisma.RST}")

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
            if (
                "EMERGENCY" in b
                or "TOXIN" in b
                or "NEURO" in b
                or "SACRIFICED" in b
                or "ATROPHY" in b
            ):
                print(f"    {b}")
            elif mode == "LABORATORY":
                print(f"    {b}")
        if ops:
            print(f"    {Prisma.VIOLET}🔪 SURGERY:{Prisma.RST} {', '.join(ops)}")
            if did_surgery:
                print(
                    f"       {Prisma.GRY}IN : {m['raw_text']}{Prisma.RST}\n       {Prisma.WHT}OUT: {clean_text}{Prisma.RST}"
                )
        print(f"{Prisma.GRY}{'-' * 65}{Prisma.RST}")


if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.GRN}>>> BONEAMANITA v5.3 {Prisma.RST}")
    print(
        f"{Prisma.GRY}System: Hysteresis Active. Bleed Detection Optimized. Neuroplasticity Engaged.{Prisma.RST}"
    )
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
        print(
            f"{Prisma.CYN}[PRESERVATION]: Writing neural pathways to disk...{Prisma.RST}"
        )

        learned_mutations = {
            k: list(v.keys()) for k, v in TheLexicon.LEARNED_VOCAB.items()
        }
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
