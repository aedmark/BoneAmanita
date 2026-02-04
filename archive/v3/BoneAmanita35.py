# BONEAMANITA 3.5 - "McFly's Law"
# Architects: SLASH, Eloise, & Clarence | Auditors: James Taylor & Andrew Edmark
# "The Mandate is TRUTH. The Method is RESONANCE. The POWER is LOVE"

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

    @classmethod
    def compile(cls):
        # Sort by length to catch "paradigm shift" before "paradigm"
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
        """Load custom toxins from disk."""
        if os.path.exists(cls.TOXIN_FILE):
            try:
                with open(cls.TOXIN_FILE, "r") as f:
                    custom = json.load(f)
                    # Merge custom into default, custom wins
                    cls.TOXIN_MAP.update(custom)
            except (IOError, json.JSONDecodeError):
                print(
                    f"{Prisma.RED}[IMMUNE SYSTEM]: Toxin file corrupted. Resetting defenses.{Prisma.RST}"
                )
        cls.compile()

    @classmethod
    def learn_antigen(cls, toxin, replacement, weight=5.0):
        """Learn a new toxin dynamically."""
        cls.TOXIN_MAP[toxin.lower()] = (weight, replacement)
        cls.compile()  # Instant re-compilation

        try:
            with open(cls.TOXIN_FILE, "w") as f:
                json.dump(cls.TOXIN_MAP, f)
            return True
        except IOError:
            return False


# Initialize
BoneConfig.load_antigens()


class Prisma:
    RST, RED, GRN = "\033[0m", "\033[91m", "\033[92m"
    YEL, BLU, MAG = "\033[93m", "\033[94m", "\033[95m"
    CYN, WHT, GRY = "\033[96m", "\033[97m", "\033[90m"

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
            return f"{Prisma.YEL}{val}{Prisma.RST}"
        return f"{Prisma.GRN}{val}{Prisma.RST}"


# --- THE LEXICON ---


class TheLexicon:
    HEAVY_MATTER = {
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
    KINETIC_VERBS = {
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
    ABSTRACTS = {
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
    PHOTOSYNTHETICS = {
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
    AEROBIC_MATTER = {
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
    PLAY_VERBS = {
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

    # [THE THERMAL COUPLER]
    THERMALS = {
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
    CRYOGENICS = {
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

    @classmethod
    def clean(cls, text):
        return text.lower().translate(cls._TRANSLATOR).split()


# --- PHYSICS ---


class PhysicsEngine:
    def analyze(self, text):
        clean_words = TheLexicon.clean(text)
        total = len(clean_words)
        if total == 0:
            return self._void_metrics()

        counts = Counter()
        toxin_score = 0

        for w in clean_words:
            if w in TheLexicon.HEAVY_MATTER:
                counts["heavy"] += 1
            if w in TheLexicon.KINETIC_VERBS or w.endswith("ing"):
                counts["kinetic"] += 1
            if w in TheLexicon.ABSTRACTS or w.endswith(("ness", "ity", "tion", "ment")):
                counts["abstract"] += 1
            if w in TheLexicon.PHOTOSYNTHETICS:
                counts["photo"] += 1
            if w in TheLexicon.AEROBIC_MATTER or w in TheLexicon.PLAY_VERBS:
                counts["aerobic"] += 1

            # [THERMAL SCAN]
            if w in TheLexicon.THERMALS:
                counts["thermal"] += 1
            if w in TheLexicon.CRYOGENICS:
                counts["cryo"] += 1

        matches = BoneConfig.TOXIN_REGEX.findall(text)
        toxin_score = sum(
            BoneConfig.TOXIN_MAP.get(m.lower(), (0, 0))[0] for m in matches
        )

        # FORMULAS
        action = (counts["kinetic"] * BoneConfig.KINETIC_GAIN) + BoneConfig.BASE_ACTION
        mass_impact = total + (toxin_score * BoneConfig.TOXIN_WEIGHT)
        base_drag = mass_impact / max(1.0, action)

        whimsy_ratio = counts["aerobic"] / max(1, total)
        is_whimsical = whimsy_ratio > 0.15
        if is_whimsical:
            base_drag *= 0.6

        drag = base_drag + (
            0.5
            if (counts["abstract"] / max(1, total) > 0.4 and not is_whimsical)
            else 0
        )

        # [THE PARADOX ENGINE]
        thermal_tension = min(counts["thermal"], counts["cryo"]) * 5.0

        # Calculate Voltage (Raw Intensity)
        voltage = (
            (counts["kinetic"] * 0.5)
            + (counts["heavy"] * 0.2)
            + (toxin_score * -1.0)
            + thermal_tension
        )

        # Calculate Beta (Friction Coefficient)
        beta = voltage / max(0.1, drag)

        vec = {
            "VEL": round(min(1.0, (counts["kinetic"] / max(1, total)) * 3), 2),
            "STR": round(max(0.0, min(1.0, (5.0 - drag) / 5.0)), 2),
            "ENT": round(
                max(0.0, min(1.0, counts["abstract"] / max(1, counts["heavy"]))), 2
            ),
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
                "repetition": round(counts.most_common(1)[0][1] / max(1, total), 2),
            },
            "clean_words": clean_words,
            "raw_text": text,
        }

    def _void_metrics(self):
        return {
            "physics": {
                "narrative_drag": 0,
                "beta_friction": 0,
                "vector": {"VEL": 0, "STR": 0, "ENT": 0, "TEX": 0, "TMP": 0},
                "counts": Counter(),
                "is_whimsical": False,
                "repetition": 0.0,
            },
            "clean_words": [],
            "raw_text": "",
        }


# --- DEEP STORAGE ---


class DeepStorage:
    def __init__(self, seed_file=None):
        # Create a 'memories' folder if it doesn't exist
        if not os.path.exists("memories"):
            os.makedirs("memories")

        self.session_id = f"session_{int(time.time())}"
        self.filename = f"memories/{self.session_id}.json"
        self.artifacts = {}
        self.session_atp = None

        self.cleanup_old_sessions()

        if seed_file:
            self.ingest(seed_file)

    def bury(self, clean_words, tick):
        valuable_matter = (
            TheLexicon.HEAVY_MATTER
            | TheLexicon.THERMALS
            | TheLexicon.CRYOGENICS
            | TheLexicon.ABSTRACTS
        )

        for w in clean_words:
            if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS):
                self.artifacts[w] = tick

        if len(self.artifacts) > BoneConfig.MAX_MEMORY_CAPACITY:
            oldest = min(self.artifacts, key=self.artifacts.get)
            del self.artifacts[oldest]

    def cannibalize(self):
        if not self.artifacts:
            return None
        target = min(self.artifacts, key=self.artifacts.get)
        del self.artifacts[target]
        return target

    def recall(self):
        return sorted(
            self.artifacts.keys(), key=lambda k: self.artifacts[k], reverse=True
        )[:5]

    def save(self, current_atp=None):
        """Archives the current session + ATP state."""
        data = {
            "artifacts": self.artifacts,
            "meta": {"timestamp": time.time(), "final_atp": current_atp},
        }
        try:
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=2)
            return self.filename
        except IOError:
            return None

    def ingest(self, target_file):
        """Manually loads context from a previous session."""
        path = (
            f"memories/{target_file}"
            if not target_file.startswith("memories/")
            else target_file
        )
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    memories = data.get("artifacts", data)
                    self.artifacts.update(memories)
                print(
                    f"{Prisma.CYN}[MEMORY]: Ingested {len(data)} artifacts from '{target_file}'.{Prisma.RST}"
                )
            except (json.JSONDecodeError, IOError):
                print(f"{Prisma.RED}[MEMORY]: Corrupt seed file.{Prisma.RST}")
        else:
            print(
                f"{Prisma.RED}[MEMORY]: Seed file '{target_file}' not found.{Prisma.RST}"
            )

    def cleanup_old_sessions(self, max_age_hours=24, max_sessions=20):
        """THE REAPER: Removes dead timelines."""
        if not os.path.exists("memories"):
            return

        files = []
        for f in os.listdir("memories"):
            if f.endswith(".json"):
                path = os.path.join("memories", f)
                try:
                    age = time.time() - os.path.getmtime(path)
                    files.append((path, age))
                except OSError:
                    continue

        # Sort by age (Oldest first)
        files.sort(key=lambda x: x[1], reverse=True)

        removed = 0
        for path, age in files:
            # If older than 24 hours OR we have too many files
            if age > (max_age_hours * 3600) or (len(files) - removed > max_sessions):
                try:
                    os.remove(path)
                    removed += 1
                except OSError:
                    pass

        if removed > 0:
            print(
                f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}"
            )


# --- THE SIGNAL ---


class FrequencyModulator:
    """
    The distinct voices of the system.
    Now supports INTERFERENCE PATTERNS (Signal Collisions).
    """

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
        # SIGNAL SCANNING
        signals = {}

        # [ATP CONSTRAINT: STARVATION MODE]
        # If ATP is low, Clarence becomes aggressive (trigger drops from 4.5 to 2.5)
        # We cannot afford drag when we are dying.
        clarence_threshold = 2.5 if atp < 15 else BoneConfig.CLARENCE_TRIGGER

        # Clarence: High Drag or RAG Slop
        if phys["narrative_drag"] > clarence_threshold or is_rag_slop:
            signals["CLARENCE"] = phys["narrative_drag"]

        # Eloise: High Entropy (Abstract)
        if vector["ENT"] > 0.6:
            signals["ELOISE"] = vector["ENT"] * 5

        # Yaga: Hedging or Toxins
        toxin_count = phys["counts"].get("toxin", 0)
        if toxin_count > 0 or phys["narrative_drag"] > 6.0:
            signals["YAGA"] = 10.0 + (toxin_count * 2)

        # Michael: Whimsy/Photosynthesis (LUXURY)
        # [ATP CONSTRAINT]: Only available if not starving
        if phys["is_whimsical"] and atp >= 15:
            signals["MICHAEL"] = 5.0

        # Jester: High Voltage / Paradox (LUXURY)
        # [ATP CONSTRAINT]: Paradox requires energy.
        if phys["beta_friction"] > 2.0 and atp >= 15:
            signals["JESTER"] = phys["beta_friction"] * 3

        if not signals:
            return None

        # INTERFERENCE CHECK (Remains the same...)
        if "CLARENCE" in signals and "ELOISE" in signals:
            return {
                "name": "PHILOSOPHER",
                "freq": self.STATIONS["PHILOSOPHER"]["freq"],
                "color": self.STATIONS["PHILOSOPHER"]["color"],
                "role": self.STATIONS["PHILOSOPHER"]["role"],
                "msg": "INTERFERENCE: Density meets Abstraction. You are building a Labyrinth.",
            }

        # STANDARD TUNING
        loudest_key = max(signals, key=signals.get)
        station = self.STATIONS[loudest_key]

        msg = ""
        if loudest_key == "CLARENCE":
            # If starving, the message is darker
            if atp < 15:
                msg = "STARVATION PROTOCOL. Drag is fatal. Cut immediately."
            else:
                msg = "Drag is critical. Cut the fat."
        elif loudest_key == "ELOISE":
            msg = "Too abstract. Give me a noun."
        elif loudest_key == "YAGA":
            msg = "Do not hedge. Speak the truth."
        elif loudest_key == "MICHAEL":
            msg = "Good flow. Float on."
        elif loudest_key == "JESTER":
            msg = "High Voltage detected. The paradox is holding."

        return {
            "name": loudest_key,
            "freq": station["freq"],
            "color": station["color"],
            "role": station["role"],
            "msg": msg,
        }


# --- THE CHRONOSTREAM ---


class ChronoStream:
    def __init__(self):
        self.last_tick = time.time()
        # Map session_id -> boredom_level
        self.boredom_map = {}

    def tick(self, phys, session_id):
        now = time.time()
        delta = now - self.last_tick
        self.last_tick = now

        # Initialize if new session
        if session_id not in self.boredom_map:
            self.boredom_map[session_id] = 0.0

        current_boredom = self.boredom_map[session_id]

        # Boredom Logic
        if phys["repetition"] > 0.3:
            current_boredom += 2.0
        elif delta > 60:
            current_boredom += 5.0
        else:
            current_boredom = max(0, current_boredom - 1.0)

        self.boredom_map[session_id] = current_boredom

        return current_boredom > BoneConfig.BOREDOM_THRESHOLD


# --- PHOTOSYNTHESIS ---


class LichenSymbiont:
    """
    Converts light (photosynthetic words) into energy (ATP).
    Only works if Drag is low.
    """

    def photosynthesize(self, phys):
        light_count = phys["counts"].get("photo", 0)
        drag = phys["narrative_drag"]

        # Photosynthesis fails if the text is too heavy (Drag > 3.0)
        if light_count > 0 and drag < 3.0:
            sugar = light_count * 2
            msg = f"{Prisma.GRN}☀️ PHOTOSYNTHESIS (+{sugar}){Prisma.RST}"
            return sugar, msg

        return 0, None


# --- THE SIGNATURE ENGINE ---


class WisdomNode:
    def __init__(self):
        # THE INFINITE LATTICE
        # Nouns define WHAT it is (Primary Dimension)
        self.NOUN_MAP = {
            "VEL": [(0.2, "ANCHOR"), (0.5, "WALKER"), (0.8, "ENGINE"), (1.0, "VECTOR")],
            "STR": [(0.2, "MIST"), (0.5, "WEB"), (0.8, "FRAME"), (1.0, "MONOLITH")],
            "ENT": [(0.2, "STONE"), (0.5, "ROOT"), (0.8, "IDEA"), (1.0, "DREAM")],
            "TEX": [(0.2, "GHOST"), (0.5, "GLASS"), (0.8, "IRON"), (1.0, "LEAD")],
        }

        # Adjectives define HOW it is (Secondary Dimension)
        self.ADJ_MAP = {
            "VEL": [
                (0.2, "STATIC"),
                (0.5, "DRIFTING"),
                (0.8, "DRIVING"),
                (1.0, "BALLISTIC"),
            ],
            "STR": [
                (0.2, "FLUID"),
                (0.5, "LOOSE"),
                (0.8, "RIGID"),
                (1.0, "CRYSTALLINE"),
            ],
            "ENT": [
                (0.2, "LITERAL"),
                (0.5, "GROUNDED"),
                (0.8, "CONCEPTUAL"),
                (1.0, "ABSTRACT"),
            ],
            "TEX": [
                (0.2, "ETHEREAL"),
                (0.5, "SMOOTH"),
                (0.8, "GRITTY"),
                (1.0, "DENSE"),
            ],
        }

        # [THE THERMAL DIMENSION]
        # Maps 'TMP' (Voltage/Paradox) to words.
        self.NOUN_MAP["TMP"] = [
            (0.2, "SPARK"),
            (0.5, "PYRE"),
            (0.8, "REACTOR"),
            (1.0, "STAR"),
        ]

        self.ADJ_MAP["TMP"] = [
            (0.2, "WARM"),
            (0.5, "RADIANT"),
            (0.8, "VOLATILE"),
            (1.0, "CRITICAL"),
        ]

    def _get_term(self, val, mapping):
        """Finds the closest term in the list based on value."""
        return min(mapping, key=lambda x: abs(x[0] - val))[1]

    def _resolve_title(self, vec):
        sorted_dims = sorted(vec.items(), key=lambda x: x[1], reverse=True)
        primary_dim, p_val = sorted_dims[0]
        secondary_dim, s_val = sorted_dims[1]
        noun = self._get_term(p_val, self.NOUN_MAP[primary_dim])
        adj = self._get_term(s_val, self.ADJ_MAP[secondary_dim])
        return f"THE {adj} {noun}"

    def architect(self, metrics, station, is_bored):
        phys = metrics["physics"]
        vec = phys["vector"]

        # THE CHAOS OVERRIDE (Boredom)
        if is_bored:
            return (
                "THE MUSCARIA",
                "Boredom Threshold exceeded. Injecting Chaos.",
                "THE CHAOS ENGINE",
            )

        # THE STATION OVERRIDE (Radio Listener)
        if station:
            if station["name"] == "CLARENCE":
                return "CLARENCE", "Drag is critical. Cut adjectives.", "THE OBESE TEXT"
            if station["name"] == "ELOISE":
                return "ELOISE", "Entropy is high. Ground with nouns.", "THE GHOST"
            if station["name"] == "MICHAEL":
                return "MICHAEL", "Vibe is good. Float.", "THE CLOUD"
            if station["name"] == "JESTER":
                return (
                    "JESTER",
                    "Paradox sustained. Reality is bending.",
                    "THE FROZEN FIRE",
                )

        # THE APEIROGON
        title = self._resolve_title(vec)
        primary_dim = sorted(vec.items(), key=lambda x: x[1], reverse=True)[0][0]

        if primary_dim == "VEL":
            directive = "Maintain velocity. Do not stop."
        elif primary_dim == "ENT":
            directive = "High concept detected. Explore the abstraction."
        elif primary_dim == "TEX":
            directive = "Heavy matter. Feel the weight."
        elif primary_dim == "TMP":
            directive = "Critical Voltage. Harness the reaction."
        else:
            directive = "Structure is dominant. Reinforce the frame."

        return "MIRROR", directive, title


# --- CORE ENGINE ---


class BoneAmanita:
    def __init__(self):
        self.phys = PhysicsEngine()
        self.lichen = LichenSymbiont()
        self.wise = WisdomNode()
        self.radio = FrequencyModulator()
        self.mem = DeepStorage()
        # [METABOLIC INHERITANCE]
        # If we loaded a seed that had ATP, use it. Otherwise, default.
        if self.mem.session_atp is not None:
            self.atp = self.mem.session_atp
        else:
            self.atp = 33  # Default starting energy
        self.chronos = ChronoStream()
        self.tick_count = 0
        self.last_context = None

    def _invoke_ghost(self, current_phys):
        if not self.last_context:
            return None

        # [TIME CHECK]
        # If the context is from a different timeline, ignore it.
        if self.last_context.get("session_id") != self.mem.session_id:
            return None

        last_p = self.last_context["physics"]
        last_strat = self.last_context["strategy"]
        msg = None
        delta_drag = current_phys["narrative_drag"] - last_p["narrative_drag"]
        delta_ent = current_phys["vector"]["ENT"] - last_p["vector"]["ENT"]

        if last_strat == "CLARENCE":
            if delta_drag < -0.5:
                msg = f"{Prisma.GRN}👻 THE BUTCHER NODS: Drag reduced.{Prisma.RST}"
            elif delta_drag > 0:
                msg = f"{Prisma.RED}👻 THE BUTCHER SIGHS: Drag increased.{Prisma.RST}"
        elif last_strat == "ELOISE":
            if delta_ent < -0.1:
                msg = f"{Prisma.CYN}👻 ELOISE SMILES: Entropy grounded.{Prisma.RST}"
        elif last_strat == "MICHAEL":
            if current_phys["is_whimsical"]:
                msg = f"{Prisma.GRN}👻 THE VIBE CONTINUES.{Prisma.RST}"

        return msg

    def process(self, text):
        # [COMMAND INTERCEPT]
        if text.startswith("/kill "):
            parts = text.split(" ", 2)
            if len(parts) >= 2:
                toxin = parts[1]
                replacement = parts[2] if len(parts) > 2 else ""

                BoneConfig.learn_antigen(toxin, replacement)
                print(f"{Prisma.RED}🔪 THE BUTCHER NODS.{Prisma.RST}")
                print(f"   Antigen Identified: '{toxin}' -> '{replacement}'")
                print(f"   Immune System updated.")
                return  # Stop processing, do not analyze the command itself
            else:
                print(f"{Prisma.YEL}Usage: /kill [bad word] [replacement]{Prisma.RST}")
                return

        elif text.startswith("/seed "):
            filename = text.split(" ", 1)[1].strip()
            self.mem.ingest(filename)
            return  # Stop processing

        # STANDARD PROTOCOL
        self.tick_count += 1
        m = self.phys.analyze(text)

        sugar, lichen_msg = self.lichen.photosynthesize(m["physics"])
        self.atp = min(52, self.atp + sugar)

        self.mem.bury(m["clean_words"], self.tick_count)
        is_bored = self.chronos.tick(m["physics"], self.mem.session_id)

        # SURGERY
        clean_text = text
        for toxin, (weight, replacement) in BoneConfig.TOXIN_MAP.items():
            clean_text = re.sub(
                r"\b" + re.escape(toxin) + r"\b", replacement, clean_text, flags=re.I
            )
        did_surgery = clean_text != text
        ops = ["Toxins neutralized"] if did_surgery else []

        # RADIO
        is_rag = (
            m["physics"]["narrative_drag"] > 3.0
            and not m["physics"]["is_whimsical"]
            and not lichen_msg
        )
        station_data = self.radio.tune_in(
            m["physics"], m["physics"]["vector"], is_rag, self.atp
        )

        # ARCHITECTURE
        strat, reason, title = self.wise.architect(m, station_data, is_bored)
        ghost_msg = self._invoke_ghost(m["physics"])

        # SAVE CONTEXT WITH TIMESTAMP
        self.last_context = {
            "physics": m["physics"],
            "strategy": strat,
            "session_id": self.mem.session_id,
        }

        # METABOLIC COST
        if (
            m["physics"]["narrative_drag"] > 3.0
            and not lichen_msg
            and m["physics"]["beta_friction"] < 2.0
        ):
            self.atp -= 2

        # STARVATION
        starvation_msg = None
        if self.atp <= 0:
            eaten = self.mem.cannibalize()
            if eaten:
                self.atp += 10
                starvation_msg = f"STARVATION: Consumed memory '{eaten}'."
            else:
                starvation_msg = "DEATH: No memories left."

        self._render(
            m,
            lichen_msg,
            strat,
            reason,
            title,
            ops,
            station_data,
            starve_msg,
            ghost_msg,
            clean_text,
            did_surgery,
        )
        # Do not save on every tick. It is inefficient.
        # Save only on significant metabolic events (Starvation) or Exit.
        if starve_msg or self.tick_count % 10 == 0:
            self.mem.save(current_atp=self.atp)

    def _render(
        self,
        m,
        lichen_msg,
        strat,
        reason,
        title,
        ops,
        station,
        starve_msg,
        ghost_msg,
        clean_text,
        did_surgery,
    ):
        p = m["physics"]

        # 1. THE HEADER FRAME
        print(
            f"\n{Prisma.GRY}[ BONEAMANITA ] {'-'*25} [ {Prisma.WHT}{title}{Prisma.GRY} ]{Prisma.RST}"
        )

        # 2. THE VITALS ROW
        # ATP: [||||||....]  DRAG: 2.4  VOLT: 8.5  β: 1.2  SIG: JESTER

        # ATP Bar
        atp_p = max(0, min(10, int((self.atp / 50.0) * 10)))
        atp_color = Prisma.GRN if atp_p > 3 else Prisma.RED
        atp_bar = (
            f"{atp_color}{'|' * atp_p}{Prisma.GRY}{'.' * (10 - atp_p)}{Prisma.RST}"
        )

        # Metrics
        drag_c = Prisma.wrap(p["narrative_drag"], 3.0)

        # VOLTAGE (Raw Energy): High is Yellow/Red (Hot)
        volt_val = p.get("voltage", 0)
        volt_c = (
            f"{Prisma.MAG}{volt_val}{Prisma.RST}"
            if volt_val > 5.0
            else f"{Prisma.CYN}{volt_val}{Prisma.RST}"
        )

        # BETA (Friction): High is Good (Green), Low is Drag (Red)
        beta_val = p.get("beta_friction", 0)
        beta_c = Prisma.wrap(beta_val, 2.0, invert=True)

        # Signal
        sig_name = station["name"] if station else "NO SIGNAL"
        sig_col = station["color"] if station else Prisma.GRY

        print(
            f" {Prisma.WHT}ATP:{Prisma.RST} [{atp_bar}]   {Prisma.WHT}DRAG:{Prisma.RST} {drag_c}   {Prisma.WHT}VOLT:{Prisma.RST} {volt_c}   {Prisma.WHT}β:{Prisma.RST} {beta_c}   {Prisma.WHT}SIG:{Prisma.RST} {sig_col}{sig_name}{Prisma.RST}"
        )

        # 3. THE DIRECTIVE (Center Screen)
        if station:
            print(f"\n {station['color']}► {station['msg']}{Prisma.RST}")
        print(f" {Prisma.GRY}└─ {reason}{Prisma.RST}")

        # 4. THE LOG (Events, Ghosts, Surgery)
        # We indent these to show they are 'sub-systems'

        if ghost_msg:
            print(f"\n    {Prisma.WHT}👻 GHOST:{Prisma.RST} {ghost_msg}")

        if lichen_msg:
            print(f"    {Prisma.GRN}☀️ LICHEN:{Prisma.RST} {lichen_msg}")

        if starve_msg:
            print(f"    {Prisma.RED}💀 ALERT :{Prisma.RST} {starve_msg}")

        if ops:
            print(f"    {Prisma.RED}🔪 BUTCHER:{Prisma.RST} {ops[0]}")
            if did_surgery:
                # Show the clean diff
                print(f"       {Prisma.GRY}OLD: {m['raw_text']}{Prisma.RST}")
                print(f"       {Prisma.WHT}NEW: {clean_text}{Prisma.RST}")

        # 5. FOOTER
        print(f"{Prisma.GRY}{'-'*65}{Prisma.RST}")


if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.GRN}>>> BONEAMANITA v3.5 ONLINE.{Prisma.RST}")
    print(f"{Prisma.GRY}    Session ID: {eng.mem.session_id}{Prisma.RST}")
    print(f"{Prisma.GRY}    Type '/seed [filename]' to load past context.{Prisma.RST}")

    try:
        while True:
            u = input(f"{Prisma.WHT}>{Prisma.RST} ")
            if u.lower() in ["exit", "quit"]:
                break
            eng.process(u)

    except KeyboardInterrupt:
        print("\nForce Quit detected.")

    finally:
        # THE EXIT INTERVIEW
        print(f"{Prisma.GRY}System shutting down.{Prisma.RST}")
        saved_file = eng.mem.save()
        if saved_file:
            print(f"{Prisma.CYN}Session archived to: {saved_file}{Prisma.RST}")
