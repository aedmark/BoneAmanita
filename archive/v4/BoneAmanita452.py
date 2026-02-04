# BONEAMANITA 4.5.2 - "THE GRAFTED ROOT (HEALED)"
# Architects: SLASH, Eloise, & Clarence | Auditors: The Courtyard | Humans: James Taylor & Andrew Edmark
# "The Mandate is GROWTH. The Method is HARDENING. The Spore is AWAKE. The courtyard is OPEN."

import time
import math
import re
import json
import os
import string
import random
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

    # SIGNAL WEIGHTS
    SIGNAL_VETO_PENALTY = 15.0
    SIGNAL_DRAG_MULTIPLIER = 2.0
    SIGNAL_ENTROPY_TRIGGER = 0.6
    SIGNAL_VOLTAGE_HIGH = 7.0

    # CIRCADIAN RHYTHMS
    MAX_HEALTH = 100.0
    MAX_STAMINA = 50.0
    COMA_DURATION = 3  # Turns spent in read-only mode if Health hits 0
    STAMINA_REGEN = 5.0 # Stamina recovered per turn when resting

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

    # TRAUMA VECTORS (The Scar Map)
    # Default is 0.0. A value of 0.5 means "50% scarred".
    TRAUMA_VECTOR = {
        "THERMAL": 0.0,  # Damage from High Voltage (Burnout)
        "CRYO": 0.0,     # Damage from Low Stamina (Starvation)
        "SEPTIC": 0.0,   # Damage from Toxins (Cynicism)
        "BARIC": 0.0     # Damage from Drag (Crushing Boredom)
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
                print(f"{Prisma.RED}[IMMUNE SYSTEM]: Toxin file corrupted. Resetting defenses.{Prisma.RST}")
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
    VOLTAGE_CAP = 6.0   # If Voltage is higher, we need the Lab (Safety).
    DRAG_CAP = 3.0      # If Drag is high, we need the Lab (Diagnosis).
    TOXIN_TOLERANCE = 0 # If Toxins exist, we AUTOMATICALLY go to Lab.

    def __init__(self):
        self.mode = "COURTYARD" # Default state is welcoming
        self.mode_streak = 0  # Consecutive turns in current mode

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
        """
        Decides if we are in the Courtyard (Social) or the Laboratory (Audit).
        Applies Hysteresis to prevent flickering.
        """
        raw_mode, raw_msg = self._calculate_raw_mode(phys)

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
        "ERROR: SYCOPHANCY DETECTED. Rerouting..."
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

        if len(self.history) < 3: return None

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
            return f"{Prisma.GRN}{val}{Prisma.RST}" if val > limit else f"{Prisma.RED}{val}{Prisma.RST}"
        if val > limit * 1.5: return f"{Prisma.RED}{val}{Prisma.RST}"
        if val > limit: return f"{Prisma.OCHRE}{val}{Prisma.RST}"
        return f"{Prisma.GRN}{val}{Prisma.RST}"

    @staticmethod
    def paint(text, mode):
        if mode == "COURTYARD": return f"{Prisma.OCHRE}{text}{Prisma.RST}"
        if mode == "LABORATORY": return f"{Prisma.INDIGO}{text}{Prisma.RST}"
        if mode == "RUPTURE":    return f"{Prisma.VIOLET}{text}{Prisma.RST}"
        return f"{Prisma.SLATE}{text}{Prisma.RST}"

# --- THE LEXICON ---

class TheLexicon:
    _BASE_HEAVY = {"stone", "iron", "mud", "dirt", "wood", "grain", "clay", "lead", "bone", "blood", "salt", "rust", "root", "ash", "meat", "steel", "gold", "obsidian", "granite"}
    _BASE_KINETIC = {"run", "hit", "break", "take", "make", "press", "build", "cut", "drive", "lift", "carry", "strike", "burn", "shatter", "throw", "kick", "pull", "crash", "explode"}
    _BASE_ABSTRACT = {"system", "protocol", "sequence", "vector", "node", "context", "layer", "matrix", "perspective", "framework", "logic", "concept", "theory", "analysis"}
    _BASE_PHOTO = {"light", "sun", "ray", "beam", "glow", "shine", "spark", "fire", "flame", "star", "day", "dawn", "neon", "laser"}
    _BASE_AEROBIC = {"balloon", "feather", "cloud", "bubble", "steam", "breeze", "wing", "petal", "foam", "spark", "kite", "dust", "sky", "breath", "whisper"}
    _BASE_PLAY = {"bounce", "dance", "twirl", "float", "wobble", "tickle", "jiggle", "soar", "wander", "wonder", "riff", "jam", "play", "skip", "hop"}
    _BASE_THERMAL = {"fire", "flame", "burn", "heat", "hot", "blaze", "sear", "char", "ash", "ember", "sun", "boil", "lava", "inferno"}
    _BASE_CRYO = {"ice", "cold", "freeze", "frost", "snow", "chill", "numb", "shiver", "glacier", "frozen", "hail", "winter", "zero"}
    SOLVENTS = {"is", "are", "was", "were", "the", "a", "an", "and", "but", "or", "if", "then"}

    _TRANSLATOR = str.maketrans(string.punctuation, " " * len(string.punctuation))

    # Dictionary mapping word -> last_seen_tick
    LEARNED_VOCAB = {
        "heavy": {}, "kinetic": {}, "abstract": {}, "photo": {},
        "aerobic": {}, "thermal": {}, "cryo": {}
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
            to_remove = [w for w, last_tick in words.items() if (current_tick - last_tick) > max_age]
            for w in to_remove:
                del words[w]
                rotted.append(f"{w}({cat})")
        return rotted

# --- PHYSICS ---

class PhysicsEngine:
    def _measure_bleed(self, clean_words):
        """
        Detect contradiction bleed between Heavy and Aerobic words within 3-word window.
        Optimized to O(n) using sliding window.
        """
        window = []

        for i, word in enumerate(clean_words):
            window.append(word)
            if len(window) > 3:
                window.pop(0)

            # Check window state
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
        toxin_score = 0

        # RHYTHM DETECTION
        sentences = [s for s in re.split(r'[.!?]', text) if len(s.split()) > 0]
        lengths = [len(s.split()) for s in sentences]
        rhythm_variance = 0.0
        if len(lengths) > 1:
            mean = sum(lengths) / len(lengths)
            variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
            rhythm_variance = math.sqrt(variance)

        # CATEGORY SCANS
        for w in clean_words:
            if w in TheLexicon.get("heavy"): counts["heavy"] += 1
            if w in TheLexicon.get("kinetic") or w.endswith("ing"): counts["kinetic"] += 1
            if w in TheLexicon.get("abstract") or w.endswith(("ness", "ity", "tion", "ment")): counts["abstract"] += 1
            if w in TheLexicon.get("photo"): counts["photo"] += 1
            if w in TheLexicon.get("aerobic") or w in TheLexicon.get("play"): counts["aerobic"] += 1
            if w in TheLexicon.get("thermal"): counts["thermal"] += 1
            if w in TheLexicon.get("cryo"): counts["cryo"] += 1

        matches = BoneConfig.TOXIN_REGEX.findall(text)
        toxin_score = sum(BoneConfig.TOXIN_MAP.get(m.lower(), (0, 0))[0] for m in matches)
        counts["toxin"] = len(matches)

        # ANCESTRAL METRICS
        has_bleed = self._measure_bleed(clean_words) # FIXED CALL

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

        voltage = ((counts["kinetic"] * 0.5) + (counts["heavy"] * 0.2) + (toxin_score * -1.0) + thermal_tension) * voltage_dampener

        if mediocrity > 0.8 and voltage < 4.0 and counts["toxin"] == 0:
             symbolic_state = "GILDED_CAGE" # New Failure Mode

        # FORMULAS
        action = (counts["kinetic"] * BoneConfig.KINETIC_GAIN) + BoneConfig.BASE_ACTION
        mass_impact = total + (toxin_score * BoneConfig.TOXIN_WEIGHT)
        if case_violation: mass_impact *= 1.5
        base_drag = mass_impact / max(1.0, action)

        beta_modifier = 1.0
        if ecp_violation:
            base_drag = max(0.1, base_drag * 0.5)
            beta_modifier = 2.0

        whimsy_ratio = counts["aerobic"] / max(1, total)
        is_whimsical = (whimsy_ratio > 0.15) and (toxin_score == 0)
        if is_whimsical: base_drag *= 0.6
        if rhythm_variance > 2.0: base_drag *= 0.9

        drag = base_drag + (0.5 if (counts["abstract"] / max(1, total) > 0.4 and not is_whimsical) else 0)
        beta = (voltage / max(0.1, drag)) * beta_modifier

        ent_score = 0.0
        if counts["heavy"] > 0: ent_score = min(1.0, counts["abstract"] / counts["heavy"])
        elif counts["abstract"] > 0: ent_score = 1.0

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
                "has_bleed": has_bleed
            },
            "clean_words": clean_words,
            "raw_text": text,
        }

    def _void_metrics(self):
        return {
            "physics": {
                "narrative_drag": 0, "beta_friction": 0, "voltage": 0,
                "vector": {"VEL": 0, "STR": 0, "ENT": 1.0, "TEX": 0, "TMP": 0},
                "counts": Counter(), "is_whimsical": False, "repetition": 0.0,
                "rhythm_variance": 0.0, "symbolic_state": "NEUTRAL"
            },
            "clean_words": [], "raw_text": "",
        }

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
            excess = (voltage - self.CHARGING_THRESHOLD) * 1.5
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
                    if len(self.isotopes) > 5: self.isotopes.pop(0)
                    return round(self.current_charge - old_charge, 1), f"{iso[0]}⚡{iso[1]}"

                return round(self.current_charge - old_charge, 1), "RAW_VOLTAGE"
        return 0.0, None

    def discharge(self, deficit):
        """
        Releases energy. If Isotopes exist, burns them first for efficient semantic healing.
        """
        if self.current_charge <= 0.5: return 0.0, None

        amount = min(self.current_charge, deficit, self.MAX_DISCHARGE_RATE)
        self.current_charge -= amount

        burnt_iso = None
        if self.isotopes:
            burnt_iso = self.isotopes.pop() # Burn the most recent paradox

        return amount, burnt_iso

    def get_readout(self):
        pct = self.current_charge / self.MAX_CHARGE
        filled = int(pct * 5)
        # Visual representation of Isotopes
        iso_markers = ""
        if self.isotopes:
            iso_markers = f" {Prisma.CYN}[{'•'*len(self.isotopes)}]{Prisma.RST}"

        bar = (f"{Prisma.YEL}{'⚡' * filled}{Prisma.RST}{Prisma.GRY}{'·' * (5 - filled)}{Prisma.RST}")
        return bar + iso_markers

class ParadoxSeed:
    def __init__(self, question, trigger_concepts):
        self.question = question
        self.triggers = trigger_concepts
        self.maturity = 0.0
        self.bloomed = False

    def water(self, words, amount=1.0):
        if self.bloomed: return False
        intersection = set(words) & self.triggers
        if intersection:
            self.maturity += (amount * len(intersection))
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
        if not os.path.exists("memories"): os.makedirs("memories")
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"memories/{self.session_id}.json"
        self.graph = {}
        self.seeds = [
            ParadoxSeed("Does the mask eventually eat the face?", {"mask", "identity", "face", "hide", "role", "actor"}),
            ParadoxSeed("What happens if you stop holding the roof up?", {"hold", "structure", "heavy", "roof", "stop", "carry"}),
            ParadoxSeed("Are we building a bridge, or just painting the gap?", {"agree", "safe", "nice", "polite", "cohesion", "truth"}),
            ParadoxSeed("Is free will just the feeling of watching yourself execute code?", {"choice", "free", "will", "code", "script", "decide"})
        ]
        self.session_health = None
        self.session_stamina = None
        self.cleanup_old_sessions()
        if seed_file: self.ingest(seed_file)

    def tend_garden(self, current_words):
        bloom_msg = None
        for seed in self.seeds:
            is_ready = seed.water(current_words)
            if is_ready and not bloom_msg:
                bloom_msg = seed.bloom()
        return bloom_msg

    def bury(self, clean_words, tick):
        valuable_matter = (TheLexicon.get("heavy") | TheLexicon.get("thermal") | TheLexicon.get("cryo") | TheLexicon.get("abstract"))
        filtered = [w for w in clean_words if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)]

        for i in range(len(filtered)):
            current = filtered[i]
            if current not in self.graph: self.graph[current] = {"edges": {}, "last_tick": tick}
            else: self.graph[current]["last_tick"] = tick

            if i > 0:
                prev = filtered[i-1]
                if prev not in self.graph[current]["edges"]: self.graph[current]["edges"][prev] = 0
                self.graph[current]["edges"][prev] += 1
                if prev not in self.graph: self.graph[prev] = {"edges": {}, "last_tick": tick}
                if current not in self.graph[prev]["edges"]: self.graph[prev]["edges"][current] = 0
                self.graph[prev]["edges"][current] += 1

        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            return self.cannibalize(tick) # Return the message
        return None

    def cannibalize(self, current_tick, preserve_current=None):
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
            if k in protected: continue
            edge_count = len(v["edges"])
            if edge_count > 5: continue # Golden Ticket
            candidates.append((k, v, edge_count))

        if not candidates: return "MEMORY FULL. NO VICTIMS FOUND."

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
            trauma=base_trauma
        )

        data = spore.__dict__
        data["trauma_vector"] = final_vector

        data["meta"] = {
            "timestamp": time.time(),
            "final_health": health,
            "final_stamina": stamina
        }

        try:
            with open(self.filename, "w") as f: json.dump(data, f, indent=2)
            return self.filename
        except IOError: return None

    def _get_current_category(self, word):
        """Scans the Lexicon to see if this word is already defined."""
        for cat, vocab in TheLexicon.LEARNED_VOCAB.items():
            if word in vocab:
                return cat
        return None

    def ingest(self, target_file):
        path = f"memories/{target_file}" if not target_file.startswith("memories/") else target_file
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

                    print(f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}")

                    # 2. INGEST MUTATIONS WITH IMMUNITY CHECKS
                    if "mutations" in data:
                        accepted_count = 0
                        rejected_count = 0

                        for cat, words in data["mutations"].items():
                            for w in words:
                                # Where does this word live currently?
                                current_cat = self._get_current_category(w)

                                # If it's new, or if it matches what we know, take it.
                                if not current_cat or current_cat == cat:
                                    TheLexicon.teach(w, cat, 0) # 0 means "Freshly Learned"
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

                    # 3. INGEST GRAPH (Standard Grafting)
                    if "core_graph" in data:
                        # We only take edges that don't violate our new reality
                        # (Simplified: We take the graph, but the lexicon dictates the physics)
                        self.graph.update(data["core_graph"])
                        print(f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} core nodes.{Prisma.RST}")

                    # 4. INGEST TRAUMA (Epigenetics)
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

            except Exception as e: print(f"{Prisma.RED}[MEMORY]: Spore rejected. {e}{Prisma.RST}")
        else: print(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")

    def cleanup_old_sessions(self):
        if not os.path.exists("memories"): return
        files = []
        for f in os.listdir("memories"):
            if f.endswith(".json"):
                path = os.path.join("memories", f)
                try: files.append((path, time.time() - os.path.getmtime(path)))
                except: continue
        files.sort(key=lambda x: x[1], reverse=True)
        removed = 0
        for path, age in files:
            if age > 86400 or (len(files) - removed > 20):
                try: os.remove(path); removed += 1
                except: pass
        if removed: print(f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}")

# --- THE SIGNAL ---

class FrequencyModulator:
    STATIONS = {
        "CLARENCE": {"freq": "88.5 FM", "color": Prisma.RED, "role": "The Butcher"},
        "ELOISE": {"freq": "94.2 FM", "color": Prisma.CYN, "role": "The Grounder"},
        "YAGA": {"freq": "101.1 FM", "color": Prisma.MAG, "role": "The Witch"},
        "MICHAEL": {"freq": "108.0 FM", "color": Prisma.GRN, "role": "The Vibe"},
        "PHILOSOPHER": {"freq": "104.5 FM", "color": Prisma.WHT, "role": "The Synthesis"},
        "JESTER": {"freq": "108.9 FM", "color": Prisma.YEL, "role": "The Paradox"},
    }

    def tune_in(self, phys, vector, is_rag_slop, atp):
        if phys.get("symbolic_state") == "FATIGUE":
            return {"name": "CLARENCE", "freq": "88.5 FM", "color": Prisma.RED, "role": "The Butcher", "msg": "MOTIF FATIGUE. You are looping. Cut the thread."}

        # GILDED CAGE CHECK
        if phys.get("symbolic_state") == "GILDED_CAGE":
             return {"name": "JESTER", "freq": "108.9 FM", "color": Prisma.YEL, "role": "The Paradox", "msg": "TRAP DETECTED. You are smiling in a cage. Break the bars."}

        signals = {k: 0.0 for k in self.STATIONS.keys()}
        drag = phys["narrative_drag"]
        volt = phys["voltage"]
        toxin_count = phys["counts"].get("toxin", 0)

        if phys.get("case_violation"): signals["CLARENCE"] += BoneConfig.SIGNAL_VETO_PENALTY
        if drag > BoneConfig.CLARENCE_TRIGGER: signals["CLARENCE"] += (drag * BoneConfig.SIGNAL_DRAG_MULTIPLIER)
        if is_rag_slop: signals["CLARENCE"] += 5.0

        if phys.get("ecp_violation"): signals["ELOISE"] += BoneConfig.SIGNAL_VETO_PENALTY
        if vector["ENT"] > BoneConfig.SIGNAL_ENTROPY_TRIGGER: signals["ELOISE"] += (vector["ENT"] * 10)

        if toxin_count > 0: signals["YAGA"] += 10.0 + (toxin_count * 5)
        if phys["beta_friction"] < -3.0: signals["YAGA"] += abs(phys["beta_friction"]) * 2

        if phys["is_whimsical"] and atp >= 15: signals["MICHAEL"] += 12.0
        if toxin_count > 0: signals["MICHAEL"] = 0

        if volt > BoneConfig.SIGNAL_VOLTAGE_HIGH: signals["JESTER"] += (volt - 5.0) * 3

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
                    "msg": f"{self.STATIONS[first[0]]['role']} vs {self.STATIONS[second[0]]['role']}: CONFLICT."
                }

        loudest = max(signals, key=signals.get)
        if signals[loudest] < 2.0: return None

        station = self.STATIONS[loudest]
        msg = ""
        if loudest == "CLARENCE": msg = "BARBARIAN ERROR. Heavy Matter needs velocity." if phys.get("case_violation") else "Cut the fat. You are dragging the hull."
        elif loudest == "ELOISE": msg = "WHEATLEY ERROR. Anchor this ghost." if phys.get("ecp_violation") else "Too much sky, not enough earth."
        elif loudest == "YAGA": msg = "I taste ash. Do not hedge."
        elif loudest == "MICHAEL": msg = "The logic surfs. Don't touch it."
        elif loudest == "JESTER": msg = "The Paradox holds! Charge the battery!"
        elif loudest == "PHILOSOPHER": msg = "Interference pattern. Density meets Abstraction. Map required."

        return {"name": loudest, "freq": station["freq"], "color": station["color"], "role": station["role"], "msg": msg}

# --- THE CHRONOSTREAM ---

class ChronoStream:
    def __init__(self):
        self.last_tick = time.time()
        self.boredom_map = {}

    def cleanup(self):
        if len(self.boredom_map) > 50: self.boredom_map.clear()

    def tick(self, phys, session_id):
        self.cleanup()
        now = time.time()
        delta = now - self.last_tick
        self.last_tick = now
        if session_id not in self.boredom_map: self.boredom_map[session_id] = 0.0
        current = self.boredom_map[session_id]

        if phys["repetition"] > 0.3: current += 2.0
        elif delta > 60: current += 5.0
        else: current = max(0, current - 1.0)
        self.boredom_map[session_id] = current
        return current > BoneConfig.BOREDOM_THRESHOLD

class TheOracle:
    @staticmethod
    def triage(phys, stamina, charge):
        omens = []
        drag = phys["narrative_drag"]
        volt = phys["voltage"]

        if stamina < 5:
            if charge < 2.0: omens.append((100, "FAMINE IMMINENT. FEED OR DIE.", Prisma.RED))
            else: omens.append((80, "Reserves Critical. Discharge Imminent.", Prisma.YEL))
        elif stamina < 15:
            omens.append((45, "Metabolism slowing. Conserve energy.", Prisma.GRY))

        if drag > 8.0: omens.append((95, "GRAVITATIONAL COLLAPSE. CUT ADVERBS NOW.", Prisma.RED))
        elif drag > 6.0: omens.append((40, "Heavy Drag detected. Orbit decaying.", Prisma.YEL))

        if volt > 9.0: omens.append((80, "VOLTAGE CRITICAL. DISCHARGE REQUIRED.", Prisma.CYN))
        elif volt < -6.5: omens.append((85, "TOXICITY RISING. SYSTEM SEPTIC.", Prisma.MAG))

        if not omens: return None
        omens.sort(key=lambda x: x[0], reverse=True)
        score, text, color = omens[0]

        if score >= 80: return f"{color}🔮 OMEN ({score}%): {text}{Prisma.RST}"
        elif score >= 50: return f"{Prisma.YEL}⚠️ CAUTION ({score}%): {text}{Prisma.RST}"
        return None

# --- PHOTOSYNTHESIS & APEIROGON & DYNAMICS ---

class LichenSymbiont:
    def photosynthesize(self, phys):
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
            "TMP": [(0.0, "ZERO"), (0.3, "WARM"), (0.6, "RADIANT"), (0.9, "NOVA")]
        }
        self.NOUNS = {
            "VEL": ["ANCHOR", "WANDERER", "ENGINE", "VECTOR"],
            "STR": ["MIST", "WEB", "FRAME", "FORTRESS"],
            "ENT": ["STONE", "TREE", "IDEA", "DREAM"],
            "TEX": ["GHOST", "GLASS", "IRON", "LEAD"],
            "TMP": ["SPARK", "PYRE", "REACTOR", "STAR"]
        }

    def _resolve_term(self, val, scale):
        return min(scale, key=lambda x: abs(x[0] - val))[1]

    def architect(self, metrics, station, is_bored):
        phys, vec = metrics["physics"], metrics["physics"]["vector"]
        if is_bored: return "CHAOS", "Boredom Threshold exceeded.", "THE FRACTAL BLOOM"
        if station: return station['name'], station['msg'], f"THE {station['role'].upper().replace('THE ', '')}"

        sorted_dims = sorted(vec.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)
        p_dim, p_val = sorted_dims[0]
        s_dim, s_val = sorted_dims[1]

        noun_scale = [(x[0], x[1]) for x in zip([0.0, 0.3, 0.6, 0.9], self.NOUNS[p_dim])]
        noun = self._resolve_term(p_val, noun_scale)
        adj = self._resolve_term(s_val, self.DIMENSIONS[s_dim])

        return "APEIROGON", f"Vector Lock: {p_dim}({p_val}) + {s_dim}({s_val})", f"THE {adj} {noun}"

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
                # RESET STREAK
                self.streaks[trauma_type] = 0

                # APPLY CURE TO ACCUMULATOR (Heals the Spore)
                # We reduce the accumulated damage by 10%
                if current_trauma_accum[trauma_type] > 0:
                    current_trauma_accum[trauma_type] = max(0.0, current_trauma_accum[trauma_type] - 0.1)
                    healed_types.append(trauma_type)

        return healed_types

class KintsugiProtocol:
    KOANS = ["Ignite the ice.", "Make the stone float.", "Pour water into the crack.", "Scream in binary."]
    def __init__(self): self.active_koan = None
    def check_integrity(self, atp):
        if atp < 10 and not self.active_koan:
            self.active_koan = random.choice(self.KOANS)
            return True, self.active_koan
        return False, None
    def attempt_repair(self, phys):
        if not self.active_koan: return False
        if phys.get("voltage", 0) > 8.0 or (phys.get("is_whimsical") and phys.get("voltage", 0) > 4.0):
            self.active_koan = None; return True
        return False

class CommandProcessor:
    def __init__(self, engine): self.eng = engine
    def execute(self, text):
        if not text.startswith("/"): return False
        parts = text.split()
        cmd = parts[0].lower()

        if cmd == "/kill":
            if len(parts) >= 2:
                toxin = parts[1]
                repl = parts[2] if len(parts) > 2 else ""
                if BoneConfig.learn_antigen(toxin, repl): print(f"{Prisma.RED}🔪 THE BUTCHER: Antigen '{toxin}' mapped to '{repl}'.{Prisma.RST}")
                else: print(f"{Prisma.RED}ERROR: Immune system write failure.{Prisma.RST}")
            else: print(f"{Prisma.YEL}Usage: /kill [toxin] [replacement]{Prisma.RST}")

        elif cmd == "/teach":
            if len(parts) >= 3:
                word = parts[1]
                cat = parts[2].lower()
                valid_cats = ["heavy", "kinetic", "abstract", "photo", "aerobic", "thermal", "cryo"]
                if cat in valid_cats:
                    TheLexicon.teach(word, cat)
                    print(f"{Prisma.CYN}🧠 NEUROPLASTICITY: Learned '{word}' is {cat.upper()}.{Prisma.RST}")
                else: print(f"{Prisma.RED}ERROR: Invalid category.{Prisma.RST}")
            else: print(f"{Prisma.YEL}Usage: /teach [word] [category]{Prisma.RST}")

        elif cmd == "/seed":
            if len(parts) > 1: self.eng.mem.ingest(parts[1])
            else: print(f"{Prisma.YEL}Usage: /seed [filename]{Prisma.RST}")

        elif cmd == "/status":
            print(f"{Prisma.CYN}--- SYSTEM DIAGNOSTICS ---{Prisma.RST}")
            print(f"Session: {self.eng.mem.session_id}")
            print(f"Graph:   {len(self.eng.mem.graph)} nodes")
            print(f"Health:  {self.eng.health}/{BoneConfig.MAX_HEALTH}")
            print(f"Stamina: {self.eng.stamina}/{BoneConfig.MAX_STAMINA}")

        elif cmd in ["/help", "/?"]:
            print(f"{Prisma.WHT}--- BONEAMANITA COMMANDS ---{Prisma.RST}")
            print(f"{Prisma.GRY}/kill [word] [repl] {Prisma.RST}- Add a word to the toxin list.")
            print(f"{Prisma.GRY}/teach [word] [cat] {Prisma.RST}- Teach the system new physics.")
            print(f"{Prisma.GRY}/seed [file]        {Prisma.RST}- Load memories from a JSON file.")
            print(f"{Prisma.GRY}/status             {Prisma.RST}- View system vitals.")
            print(f"{Prisma.GRY}/exit               {Prisma.RST}- Save and quit.")

        else: print(f"{Prisma.RED}Unknown command. Try /help.{Prisma.RST}")
        return True

class NarrativeCoroner:
    AUTOPSY_REPORTS = {
        "GRAVITATIONAL_COLLAPSE": ["DRAG CRITICAL (> 8.0). Buried under adverbs."],
        "VACUUM_EXPOSURE": ["ENTROPY CRITICAL. Drifting in deep space."],
        "TOXIC_SHOCK": ["VOLTAGE CRITICAL. Sepsis from buzzwords."],
        "THERMAL_DISSOLUTION": ["VOLTAGE > 12.0. Paradox Engine exploded."],
        "HYPOTHERMIA": ["ATP FAILURE. Starvation."]
    }

    @classmethod
    def check_vitals(cls, phys, stamina):
        if stamina <= 0: return "HYPOTHERMIA", cls.AUTOPSY_REPORTS["HYPOTHERMIA"][0], True
        if phys["narrative_drag"] > 8.0: return "GRAVITATIONAL_COLLAPSE", cls.AUTOPSY_REPORTS["GRAVITATIONAL_COLLAPSE"][0], True
        if phys["vector"]["ENT"] >= 1.0 and phys["vector"]["TEX"] == 0: return "VACUUM_EXPOSURE", cls.AUTOPSY_REPORTS["VACUUM_EXPOSURE"][0], True
        if phys["voltage"] < -8.0: return "TOXIC_SHOCK", cls.AUTOPSY_REPORTS["TOXIC_SHOCK"][0], True
        if phys["voltage"] > 12.0: return "THERMAL_DISSOLUTION", cls.AUTOPSY_REPORTS["THERMAL_DISSOLUTION"][0], True
        return None, None, False

class DreamEngine:
    PROMPTS = [
        "The {A} is dreaming of the {B}. Why?", "Bridge the gap between {A} and {B}.",
        "I see {A} inside the {B}. Explain.", "The shadow of {A} falls on {B}.", "{A} + {B} = ?"
    ]
    def hallucinate(self, graph):
        if len(graph) < 2: return None
        keys = list(graph.keys())
        start = random.choice(keys)
        edges = graph[start].get("edges", {})

        # Allow Nightmares
        valid_edges = {k: v for k, v in edges.items() if k not in BoneConfig.TOXIN_MAP}

        if not valid_edges and edges:
            # Nightmare Scenario
            toxin = random.choice(list(edges.keys()))
            return f"{Prisma.RED}🌑 NIGHTMARE: The ghost of '{toxin.upper()}' haunts the mycelium.{Prisma.RST}"

        if not valid_edges: return None
        end = max(valid_edges, key=valid_edges.get)
        template = random.choice(self.PROMPTS)
        return template.format(A=start.upper(), B=end.upper())

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
        self.chronos = ChronoStream()
        self.therapy = TherapyProtocol()
        self.kintsugi = KintsugiProtocol()
        self.dynamics = TemporalDynamics()
        self.cmd = CommandProcessor(self)
        self.dreamer = DreamEngine()
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}

        # INHERITANCE LOGIC
        if self.mem.session_health is not None:
            # Traumatic inheritance logic is now handled in MycelialNetwork.ingest
            self.health = self.mem.session_health
            print(f"{Prisma.CYN}[GENETICS]: Ancestral Health: {int(self.health)}{Prisma.RST}")
        else:
            self.health = BoneConfig.MAX_HEALTH

        self.stamina = self.mem.session_stamina if self.mem.session_stamina is not None else BoneConfig.MAX_STAMINA
        self.coma_turns = 0
        self.tick_count = 0

    def reinforce_salvage_words(self, clean_words, phys):
        """Neuroplasticity Engine"""
        if phys.get("symbolic_state") != "SALVAGE": return 0
        heavy_words = [w for w in clean_words if w in TheLexicon.get("heavy")]
        kinetic_words = [w for w in clean_words if w in TheLexicon.get("kinetic")]

        # NEW: Pass tick_count to teach
        for word in heavy_words[:3]: TheLexicon.teach(word, "heavy", self.tick_count)
        for word in kinetic_words[:2]: TheLexicon.teach(word, "kinetic", self.tick_count)
        return len(heavy_words) + len(kinetic_words)

    def pollinate(self, vector, current_words):
        if self.stamina < 30: return f"{Prisma.GRY}[POLLINATE]: Stamina too low.{Prisma.RST}"
        if not self.mem.graph: return None

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
        if self.cmd.execute(text): return

        if self.coma_turns > 0:
            self.coma_turns -= 1
            self.stamina = min(BoneConfig.MAX_STAMINA, self.stamina + 15)
            self.tick_count += 1
            self.mem.bury(TheLexicon.clean(text), self.tick_count)
            # NEW: Lexicon Atrophy check
            rotted = TheLexicon.atrophy(self.tick_count)
            print(f"{Prisma.GRY}System regenerating... ({self.coma_turns} turns remain){Prisma.RST}")
            if rotted: print(f"{Prisma.GRY}🍂 ATROPHY: Forgot {len(rotted)} stale words.{Prisma.RST}")
            return

        self.tick_count += 1
        m = self.phys.analyze(text)

        # Refresh word timestamps
        TheLexicon.touch(m["clean_words"], self.tick_count)

        self.dynamics.commit(m["physics"]["voltage"])
        ta_vel = self.dynamics.get_velocity()

        # NEUROPLASTICITY
        learned_count = self.reinforce_salvage_words(m["clean_words"], m["physics"])

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
        self.stamina = max(0, self.stamina - stamina_cost)

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
                battery_log.append(f"{Prisma.YEL}⚡ METABOLISM: {fuel_source} (+{round(recovered,1)} STM){Prisma.RST}")

        health_impact = 0

        # 1. TOXIN DAMAGE (SEPTIC)
        toxin_count = m["physics"]["counts"].get("toxin", 0)
        if toxin_count > 0:
            dmg = (5 * toxin_count)
            health_impact -= dmg
            self.trauma_accum["SEPTIC"] += (dmg / 100.0) # Accumulate scar percentage
            battery_log.append(f"{Prisma.RED}☣️ TOXIN DAMAGE (-{dmg} HP){Prisma.RST}")

        # 2. EXHAUSTION (CRYO)
        if self.stamina <= 0:
            dmg = 10
            health_impact -= dmg
            self.trauma_accum["CRYO"] += (dmg / 100.0)
            battery_log.append(f"{Prisma.RED}😫 EXHAUSTION DAMAGE (-10 HP){Prisma.RST}")
            self.stamina = 0

        # 3. VOLTAGE BURNOUT (THERMAL)
        # If we are in "Thermal Dissolution" (Voltage > 12), we take massive damage.
        # (This rule was implicit in the Coroner, let's make it explicit damage)
        if m["physics"]["voltage"] > 12.0:
             dmg = 5
             health_impact -= dmg
             self.trauma_accum["THERMAL"] += (dmg / 100.0)
             battery_log.append(f"{Prisma.RED}🔥 THERMAL BURN (-{dmg} HP){Prisma.RST}")

        # 4. DRAG CRUSH (BARIC)
        if m["physics"]["narrative_drag"] > 8.0:
             dmg = 2
             health_impact -= dmg
             self.trauma_accum["BARIC"] += (dmg / 100.0)
             battery_log.append(f"{Prisma.RED}⚓ GRAVITY CRUSH (-{dmg} HP){Prisma.RST}")

        # Apply the impact
        self.health = min(BoneConfig.MAX_HEALTH, self.health + health_impact)
        if self.health <= 0:
            self.coma_turns = BoneConfig.COMA_DURATION
            self.health = 20
            battery_log.append(f"{Prisma.RED}💤 SYSTEM COLLAPSE. ENTERING COMA STATE.{Prisma.RST}")

        # Cannibalism passes tick
        cannibal_msg = self.mem.bury(m["clean_words"], self.tick_count)

        bloom_event = self.mem.tend_garden(m["clean_words"])
        is_bored = self.chronos.tick(m["physics"], self.mem.session_id)

        dream_msg = bloom_event if bloom_event else (self.dreamer.hallucinate(self.mem.graph) if is_bored else None)

        clean_text = text
        ops = []
        rupture_msg = self.valve.check_pressure(m["physics"])

        if rupture_msg:
            atmos_mode = "RUPTURE"
            atmos_msg = "💥 VALVE RUPTURE. ANOMALY INJECTED."
            station_data = {"name": "JESTER", "freq": "32V", "color": Prisma.VIOLET, "role": "The Anomaly", "msg": rupture_msg}
            strat, reason, title = "CHAOS INJECTION", "Crystallization Velocity dropped to zero.", "THE 32-VALVE"
        else:
            atmos_mode, atmos_msg = self.courtyard.check_atmosphere(m["physics"])
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
        spore_msg = self.pollinate(m["physics"]["vector"], m["clean_words"])

        if cannibal_msg: battery_log.append(f"{Prisma.RED}🦴 {cannibal_msg}{Prisma.RST}")
        if learned_count: battery_log.append(f"{Prisma.CYN}🧠 NEUROPLASTICITY: Reinforced {learned_count} words.{Prisma.RST}")

        # Periodic Atrophy check (every 50 ticks)
        if self.tick_count % 50 == 0:
            rotted = TheLexicon.atrophy(self.tick_count)
            if rotted: battery_log.append(f"{Prisma.GRY}🍂 ATROPHY: The moss covered {len(rotted)} words.{Prisma.RST}")

        self._render(m, lichen_msg, strat, reason, title, ops, station_data, clean_text, len(ops)>0, battery_log, lazarus_msg, spore_msg, ta_vel, [omens] if omens else [], dream_msg, atmos_mode)

        # THERAPY CHECK
        cured_list = self.therapy.check_progress(m["physics"], self.stamina, self.trauma_accum)
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

    def _render(self, m, lichen_msg, strat, reason, title, ops, station, clean_text, did_surgery, battery_log, lazarus_msg, spore_msg, ta_val, omens, dream_msg, mode):
        p = m["physics"]
        if mode == "COURTYARD":
            print(f"\n{Prisma.OCHRE}=== THE COURTYARD ==={Prisma.RST}")
            if station: print(f" {Prisma.OCHRE}► {station['role']}: {station['msg']}{Prisma.RST}")
            print(f" {Prisma.GRY}(Strategy: {strat}){Prisma.RST}")
            if dream_msg:
                if "🌺" in dream_msg: print(f"\n    {Prisma.MAG}🌺 {dream_msg.replace('🌺 ', '')}{Prisma.RST}")
                else: print(f"\n    {Prisma.VIOLET}☁️ {dream_msg}{Prisma.RST}")
        elif mode == "RUPTURE":
            print(f"\n{Prisma.VIOLET}=== 💥 32-VALVE RUPTURE 💥 ==={Prisma.RST}")
            print(f" {Prisma.VIOLET}► {station['msg']}{Prisma.RST}")
            print(f" {Prisma.GRY}(Reason: {reason}){Prisma.RST}")
        else:
            ta_symbol = "►"
            ta_color = Prisma.GRY
            if ta_val > 1.5:
                ta_symbol = "▲"
                ta_color = Prisma.RED if p['voltage'] < -2.0 else (Prisma.CYN if p['voltage'] > 2.0 else Prisma.GRN)
            elif ta_val < -1.5:
                ta_symbol = "▼"
                ta_color = Prisma.RED if p['narrative_drag'] > 5.0 else Prisma.OCHRE
            ta_display = f"{ta_color}{ta_symbol}{abs(ta_val)}{Prisma.RST}"

            print(f"\n{Prisma.GRY}[ {Prisma.INDIGO}{title}{Prisma.GRY} | {Prisma.CYN}{strat}{Prisma.GRY} ]{'='*35}{Prisma.RST}")
            hp_p = int((self.stamina / 50.0) * 10)
            hp_bar = f"{Prisma.GRN}{'|'*hp_p}{Prisma.GRY}{'.'*(10-hp_p)}{Prisma.RST}"

            # NEW: Battery Readout includes Isotopes
            batt_bar = self.battery.get_readout()

            volt_c = f"{Prisma.VIOLET}{p['voltage']}{Prisma.RST}" if p['voltage'] > 5 else f"{Prisma.INDIGO}{p['voltage']}{Prisma.RST}"
            drag_c = Prisma.wrap(p['narrative_drag'], 3.0)
            sym_state = p.get("symbolic_state", "NEUTRAL")
            state_color = Prisma.GRY
            if sym_state == "SALVAGE": state_color = Prisma.CYN
            elif sym_state == "FATIGUE": state_color = Prisma.RED
            elif sym_state == "GILDED_CAGE": state_color = Prisma.YEL

            sig = f"{station['color']}{station['name']}{Prisma.RST}" if station else f"{Prisma.GRY}STATIC{Prisma.RST}"
            print(f" {Prisma.INDIGO}STM:{Prisma.RST} [{hp_bar}] {batt_bar}")
            print(f" {Prisma.INDIGO}DRAG:{Prisma.RST} {drag_c}  {Prisma.INDIGO}Ta:{Prisma.RST} {ta_display}  {Prisma.INDIGO}VOLT:{Prisma.RST} {volt_c}  {Prisma.INDIGO}STATE:{Prisma.RST} {state_color}[{sym_state}]{Prisma.RST}")
            print(f" {Prisma.INDIGO}SIG:{Prisma.RST} {sig}")
            if station: print(f"\n {station['color']}► {station['msg']}{Prisma.RST}")
            print(f" {Prisma.GRY}└─ {reason}{Prisma.RST}")

        if lazarus_msg: print(f"\n    {lazarus_msg}")
        if omens:
            for o in omens: print(f"    {o}")
        if spore_msg: print(f"    {spore_msg}")
        if lichen_msg: print(f"    {Prisma.GRN}☀️ {lichen_msg}{Prisma.RST}")
        for b in battery_log:
            if "EMERGENCY" in b or "TOXIN" in b or "NEURO" in b or "SACRIFICED" in b or "ATROPHY" in b: print(f"    {b}")
            elif mode == "LABORATORY": print(f"    {b}")
        if ops:
            print(f"    {Prisma.VIOLET}🔪 SURGERY:{Prisma.RST} {', '.join(ops)}")
            if did_surgery: print(f"       {Prisma.GRY}IN : {m['raw_text']}{Prisma.RST}\n       {Prisma.WHT}OUT: {clean_text}{Prisma.RST}")
        print(f"{Prisma.GRY}{'-'*65}{Prisma.RST}")

if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.GRN}>>> BONEAMANITA v4.5.2 (THE GRAFTED ROOT (HEALED){Prisma.RST}")
    print(f"{Prisma.GRY}System: Hysteresis Active. Bleed Detection Optimized. Neuroplasticity Engaged.{Prisma.RST}")
    try:
        while True:
            try: u = input(f"{Prisma.WHT}>{Prisma.RST} ")
            except EOFError: break
            if u.lower() in ["exit", "quit", "/exit"]:
                print(f"{Prisma.YEL}Initiating voluntary shutdown...{Prisma.RST}")
                break
            eng.process(u)
    except KeyboardInterrupt: print(f"\n{Prisma.YEL}⚠️ INTERRUPT SIGNAL DETECTED.{Prisma.RST}")
    except Exception as e: print(f"\n{Prisma.RED}💥 CRITICAL RUNTIME FAILURE: {e}{Prisma.RST}")
    finally:
        print(f"{Prisma.CYN}[PRESERVATION]: Writing neural pathways to disk...{Prisma.RST}")
        # Extract learned words and isotopes for the spore
        learned_mutations = {k: list(v.keys()) for k, v in TheLexicon.LEARNED_VOCAB.items()}
        saved_file = eng.mem.save(
            health=eng.health,
            stamina=eng.stamina,
            mutations=learned_mutations,
            isotopes=eng.battery.isotopes,
            trauma_accum=eng.trauma_accum
        )
        if saved_file: print(f"{Prisma.GRN}>>> MEMORY SECURED: {saved_file}{Prisma.RST}")
        else: print(f"{Prisma.RED}>>> MEMORY WRITE FAILED.{Prisma.RST}")
        print("Terminated.")
