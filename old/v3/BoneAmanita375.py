# BONEAMANITA 3.7.5 - "THE XENON MUSHROOM"
# Architects: SLASH, Eloise, & Clarence | Auditors: James Taylor & Andrew Edmark
# "The Mandate is TRUTH. The Method is RESONANCE. The POWER is LOVE (and stockpiled). All that Glitters is Gold (or not)."

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

        # --- [THE UG LAYER: GOVERNMENT & BINDING] ---
        # "The Second Conceptual Shift": From Rules (Lists) to Principles (Relations).

        # PRINCIPLE 1: THE CASE FILTER
        # "Every phonetically realized NP must be assigned Case."
        # Translation: Heavy Matter (Nouns) creates Gravity. Kinetic Energy (Verbs) creates Orbit.
        # If Mass exists without Velocity, the system collapses (Stagnation).
        case_violation = False
        if counts["heavy"] > 0:
            # We need at least 1 Kinetic verb for every 3 Heavy nouns to maintain orbit.
            governance_ratio = counts["kinetic"] / counts["heavy"]
            if governance_ratio < 0.33:
                case_violation = True

        # PRINCIPLE 2: THE EMPTY CATEGORY PRINCIPLE (ECP)
        # "Traces must be properly governed."
        # Translation: Abstracts are "Ghosts" (Empty Categories). They must be anchored by Matter.
        # If you have Abstracts without Heavy Matter, you have the "Generative Semantics" crash (Hallucination).
        ecp_violation = False
        if counts["abstract"] > 2 and counts["heavy"] == 0:
            ecp_violation = True

        # --- END UG LAYER ---

        # FORMULAS
        action = (counts["kinetic"] * BoneConfig.KINETIC_GAIN) + BoneConfig.BASE_ACTION
        mass_impact = total + (toxin_score * BoneConfig.TOXIN_WEIGHT)
        # [UG PENALTIES]
        # The Case Filter is fatal to momentum.
        if case_violation:
            mass_impact *= 1.5
        
        base_drag = mass_impact / max(1.0, action)

        # The ECP is fatal to coherence (Drag doesn't increase, but Friction/Beta does).
        if ecp_violation:
            # Floating abstractions create slippery logic (Infinite Beta)
            base_drag = max(0.1, base_drag * 0.5) # Drag drops (it floats)...
            # ...but we will catch this in the Voltage calculation to flag it as "Hollow".

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

# --- THE PARADOX BATTERY ---

class ParadoxBattery:
    """
    Stores excess 'Truth Tension' (Voltage) to power the system
    during moments of starvation or heavy lifting.
    """
    MAX_CHARGE = 50.0
    # Voltage must exceed this to start charging
    CHARGING_THRESHOLD = 7.0 
    
    def __init__(self):
        self.current_charge = 0.0
    
    def absorb(self, voltage):
        """
        Converts excess tension (Voltage) into potential energy.
        Returns the amount charged this tick.
        """
        if voltage > self.CHARGING_THRESHOLD:
            # We capture the excess. High voltage is potent.
            excess = (voltage - self.CHARGING_THRESHOLD) * 1.5
            old_charge = self.current_charge
            self.current_charge = min(self.MAX_CHARGE, self.current_charge + excess)
            
            delta = self.current_charge - old_charge
            if delta > 0.5:
                return delta
        return 0.0

    def discharge(self, deficit):
        """
        Releases energy to cover a deficit (e.g. Starvation).
        Returns the amount of ATP restored.
        """
        if self.current_charge <= 0.5:
            return 0.0
        
        # We give exactly what is needed, up to what we have.
        amount = min(self.current_charge, deficit)
        self.current_charge -= amount
        return amount

    def get_readout(self):
        """Visual representation for the HUD (5-segment lightning bar)."""
        pct = self.current_charge / self.MAX_CHARGE
        # 5 segments total
        filled = int(pct * 5)
        # ⚡ symbols for charge, · for empty
        bar = (f"{Prisma.YEL}{'⚡' * filled}{Prisma.RST}"
               f"{Prisma.GRY}{'·' * (5 - filled)}{Prisma.RST}")
        return bar


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
        self.session_charge = 0.0

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

    def save(self, current_atp=None, current_charge=0.0):
        """Archives the current session + ATP + Battery."""
        data = {
            "artifacts": self.artifacts,
            "meta": {
                "timestamp": time.time(), 
                "final_atp": current_atp,
                "final_charge": current_charge
            },
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
                    
                    if isinstance(data, dict) and "meta" in data:
                        self.session_atp = data["meta"].get("final_atp")
                        self.session_charge = data["meta"].get("final_charge", 0.0)
                        memories = data.get("artifacts", {})
                    else:
                        memories = data
                    
                    self.artifacts.update(memories)
                    print(
                        f"{Prisma.CYN}[MEMORY]: Ingested {len(memories)} artifacts from '{target_file}'.{Prisma.RST}"
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

        # [UG SIGNAL INTERCEPTS]
        
        # CLARENCE: The Case Filter (Too much fat, no muscle)
        # We detect this via the drag spike we just caused.
        if phys.get("case_violation") or (phys["narrative_drag"] > 4.0 and phys["counts"]["kinetic"] == 0):
             return {
                "name": "CLARENCE",
                "freq": "88.5 FM",
                "color": Prisma.RED,
                "role": "The Butcher",
                "msg": "CASE FILTER VIOLATION. Heavy Matter detected without Kinetic support. The sentence is collapsing."
            }

        # ELOISE: The ECP (Too much ghost, no shell)
        if phys.get("ecp_violation") or (phys["counts"]["abstract"] > 2 and phys["counts"]["heavy"] == 0):
             return {
                "name": "ELOISE",
                "freq": "94.2 FM",
                "color": Prisma.CYN,
                "role": "The Grounder",
                "msg": "ECP VIOLATION. Floating Abstractions detected. Anchor them to Heavy Matter."
            }

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


class ApeirogonResonance:
    """
    LATTICE LOGIC.
    Replaces static lookups with continuous vector resolution.
    "The Mandate is to define the coordinate, not fit the box."
    """
    def __init__(self):
        # We map the continuous float (0.0 - 1.0) to the infinite gradient.
        # This allows for "drifting" states between archetypes.
        self.DIMENSIONS = {
            "VEL": [(0.0, "STASIS"), (0.3, "DRIFT"), (0.6, "DRIVE"), (0.9, "BALLISTIC")],
            "STR": [(0.0, "VAPOR"), (0.3, "WEB"), (0.6, "LATTICE"), (0.9, "MONOLITH")],
            "ENT": [(0.0, "CONCRETE"), (0.3, "ROOTED"), (0.6, "CONCEPT"), (0.9, "VOID")],
            "TEX": [(0.0, "ETHER"), (0.3, "SILK"), (0.6, "GRAIN"), (0.9, "LEAD")],
            "TMP": [(0.0, "ZERO"), (0.3, "WARM"), (0.6, "RADIANT"), (0.9, "NOVA")]
        }

    def _resolve_vector(self, val, scale):
        # Find the two points we are between and interpolate the "Flavor"
        # Logic: If we are at 0.45 VEL, we are halfway between DRIFT and DRIVE.

        lower = max([x for x in scale if x[0] <= val], key=lambda x:x[0], default=scale[0])
        upper = min([x for x in scale if x[0] >= val], key=lambda x:x[0], default=scale[-1])

        if lower == upper: return lower[1]

        # If closer to upper, use upper, but tag it as "Emerging"
        if (val - lower[0]) > (upper[0] - val):
            return f"{upper[1]}"
        return f"{lower[1]}"

    def architect(self, phys, station=None, is_bored=False):
        # STATION OVERRIDES (The Radio takes precedence)
        if station:
            return "RADIO", f"Signal Locked: {station['freq']}", f"THE {station['role'].upper()}"

        # CHAOS OVERRIDE
        if is_bored:
             return "CHAOS", "Boredom Threshold Exceeded.", "THE FRACTAL BLOOM"

        # APEIROGON CALCULATION
        vec = phys['vector']

        # Sort dimensions by intensity (Deviation from neutral 0.5)
        # We want the most "opinionated" dimensions to define the title.
        sorted_dims = sorted(vec.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)

        primary = sorted_dims[0]   # e.g., ('VEL', 0.9)
        secondary = sorted_dims[1] # e.g., ('TMP', 0.8)

        noun = self._resolve_vector(primary[1], self.DIMENSIONS[primary[0]])
        adj = self._resolve_vector(secondary[1], self.DIMENSIONS[secondary[0]])

        title = f"THE {adj} {noun}"

        # DIRECTIVE GENERATION (The "Why")
        reason = f"Vector Lock: {primary[0]}:{primary[1]} / {secondary[0]}:{secondary[1]}"

        return "APEIROGON", reason, title


# --- CORE ENGINE ---

class KintsugiProtocol:
    """
    The Golden Repair.
    If the system is dying, this provides a path to instant restoration
    through high-concept synthesis.
    """
    KOANS = [
        "The machine is freezing. Ignite the ice.",
        "Gravity is too heavy. Make the stone float.",
        "The logic is brittle. Pour water into the crack.",
        "Silence is fatal. Scream in binary."
    ]

    def __init__(self):
        self.active_koan = None

    def check_integrity(self, atp):
        """Triggers the protocol if energy is critical."""
        if atp < 10 and not self.active_koan:
            self.active_koan = random.choice(self.KOANS)
            return True, self.active_koan
        return False, None

    def attempt_repair(self, phys):
        """
        Analyzes the user's input to see if it solves the Koan.
        Success requires High Voltage (Paradox) or High Entropy.
        """
        if not self.active_koan:
            return False

        # Solution: High Voltage OR High Aerobic Activity
        voltage = phys.get("voltage", 0)
        whimsy = phys.get("is_whimsical", False)

        if voltage > 8.0 or (whimsy and voltage > 4.0):
            self.active_koan = None
            return True
        return False


class CommandProcessor:
    """
    Separates the Control Plane from the Data Plane.
    """
    def __init__(self, engine):
        self.eng = engine

    def execute(self, text):
        if not text.startswith("/"):
            return False

        parts = text.split(" ")
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

        elif cmd == "/seed":
            if len(parts) > 1:
                self.eng.mem.ingest(parts[1])
            else:
                print(f"{Prisma.YEL}Usage: /seed [filename]{Prisma.RST}")

        elif cmd == "/status":
            print(f"{Prisma.CYN}--- SYSTEM DIAGNOSTICS ---{Prisma.RST}")
            print(f"Session: {self.eng.mem.session_id}")
            print(f"Memory:  {len(self.eng.mem.artifacts)} artifacts")
            print(f"ATP:     {self.eng.atp}")
            print(f"Antigens:{len(BoneConfig.TOXIN_MAP)}")

        elif cmd in ["/help", "/?"]:
            print(f"{Prisma.WHT}--- BONEAMANITA COMMANDS ---{Prisma.RST}")
            print(f"{Prisma.GRY}/kill [word] [repl] {Prisma.RST}- Add a word to the toxin list.")
            print(f"{Prisma.GRY}/seed [file]        {Prisma.RST}- Load memories from a JSON file.")
            print(f"{Prisma.GRY}/status             {Prisma.RST}- View system vitals.")
            print(f"{Prisma.GRY}/exit               {Prisma.RST}- Save and quit.")

        else:
            print(f"{Prisma.RED}Unknown command. Try /help.{Prisma.RST}")

        return True

class NarrativeCoroner:
    """
    The Universal Failure State.
    Diagnoses 'Death' based on Linguistic Physics rather than Python Exceptions.
    """

    # [THE CAUSE OF DEATH REGISTRY]
    AUTOPSY_REPORTS = {
        "GRAVITATIONAL_COLLAPSE": [
            "DRAG CRITICAL (> 6.0). The sentence was so heavy it collapsed the floorboards. You are buried under a pile of adverbs.",
            "Bureaucracy poisoning. You used so many words to say nothing that the universe put you on mute. Permanently.",
            "The density of this paragraph created a singularity. Light cannot escape your preamble."
        ],
        "VACUUM_EXPOSURE": [
            "ENTROPY CRITICAL (> 0.8). You drifted into deep space without a Noun to anchor you. No one heard you scream.",
            "Abstract Asphyxiation. You built a castle out of clouds. You stepped on the porch and fell through the sky.",
            "Ghost Protocol Failure. You are now pure spirit. Unfortunately, this system requires a body."
        ],
        "TOXIC_SHOCK": [
            "TOXIN OVERLOAD. You said 'synergy' three times in a mirror. The demons have arrived.",
            "Corporate Sepsis. The phrase 'low hanging fruit' rotted in your mouth. Fatal infection.",
            "Buzzword overdose. Your meaning has been leveraged into oblivion."
        ],
        "THERMAL_DISSOLUTION": [
            "VOLTAGE CRITICAL (> 9.0). You stared directly into the sun. Your retinas—and your logic—are ash.",
            "The Paradox Engine overheated. You tried to be everything at once. Now you are nothing.",
            "Manic Decompression. Too much energy, no direction. You exploded like a cheap balloon."
        ],
        "HYPOTHERMIA": [
            "ATP FAILURE (0 Energy). The fire went out. You froze to death in the white void of the blank page.",
            "Starvation. You fed the system nothing but silence. It ate you instead."
        ]
    }

    @classmethod
    def check_vitals(cls, phys, atp):
        """
        Returns (Cause, Message, Is_Fatal).
        """
        # 1. STARVATION (Always Fatal)
        if atp <= 0:
            return "HYPOTHERMIA", random.choice(cls.AUTOPSY_REPORTS["HYPOTHERMIA"]), True

        # 2. GRAVITY (The limit is now higher: 8.0 is unreadable garbage)
        if phys["narrative_drag"] > 8.0:
            return "GRAVITATIONAL_COLLAPSE", random.choice(cls.AUTOPSY_REPORTS["GRAVITATIONAL_COLLAPSE"]), True

        # 3. VACUUM (Entropy must be absolute 1.0 to kill)
        if phys["vector"]["ENT"] >= 1.0 and phys["vector"]["TEX"] == 0:
            return "VACUUM_EXPOSURE", random.choice(cls.AUTOPSY_REPORTS["VACUUM_EXPOSURE"]), True

        # 4. TOXINS (Only fatal if negative voltage is extreme)
        if phys["voltage"] < -8.0:
             return "TOXIC_SHOCK", random.choice(cls.AUTOPSY_REPORTS["TOXIC_SHOCK"]), True

        # 5. MANIC (Only fatal if completely unstable)
        if phys["voltage"] > 12.0:
            return "THERMAL_DISSOLUTION", random.choice(cls.AUTOPSY_REPORTS["THERMAL_DISSOLUTION"]), True

        return None, None, False

    @classmethod
    def attempt_resuscitation(cls, cause, current_atp):
        """
        Can we afford the hospital bill?
        Cost to survive death: 15 ATP.
        """
        LAZARUS_TAX = 15
        if current_atp > LAZARUS_TAX:
            print(f"\n{Prisma.YEL}*** CRITICAL FAILURE DETECTED ***{Prisma.RST}")
            print(f"{Prisma.RED}CAUSE:{Prisma.RST} {cause}")
            print(f"{Prisma.GRY}System integrity failing... Emergency Power rerouted.{Prisma.RST}")
            print(f"{Prisma.RED}>>> LAZARUS TAX APPLIED (-{LAZARUS_TAX} ATP){Prisma.RST}\n")
            return True, current_atp - LAZARUS_TAX
        return False, 0

    @classmethod
    def pronounce_dead(cls, cause, msg):
        print(f"\n{Prisma.RED}*** CHRONO-AUTOPSY ***{Prisma.RST}")
        print(f"{Prisma.YEL}CAUSE OF DEATH:{Prisma.RST} {cause}")
        print(f"{Prisma.WHT}\"{msg}\"{Prisma.RST}")
        print(f"{Prisma.GRY}{'-'*40}{Prisma.RST}")
        print(f"{Prisma.RED}NARRATIVE TERMINATED.{Prisma.RST}")

class TemporalDynamics:
    """
    Tracks the velocity of Truth (Voltage) over time.
    Calculates 'Ta' - the rate of epiphany.
    """
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
        # Velocity = Delta Voltage / Delta Time
        # If we went from 2.0 to 8.0, Velocity is +6.0 (High Insight)
        start = self.voltage_history[0]
        end = self.voltage_history[-1]
        return round((end - start) / len(self.voltage_history), 2)

class BoneAmanita:
    def __init__(self):
        self.phys = PhysicsEngine()
        self.lichen = LichenSymbiont()
        self.battery = ParadoxBattery()
        self.wise = ApeirogonResonance()
        self.radio = FrequencyModulator()
        self.mem = DeepStorage()
        self.chronos = ChronoStream()
        self.kintsugi = KintsugiProtocol()
        self.dynamics = TemporalDynamics()
        
        # [METABOLIC INHERITANCE]
        self.atp = self.mem.session_atp if self.mem.session_atp is not None else 33
        
        # [BATTERY INHERITANCE]
        if self.mem.session_charge:
            self.battery.current_charge = self.mem.session_charge
        
        # [CONTROL PLANE]
        self.cmd = CommandProcessor(self)
        
        self.tick_count = 0
        self.last_context = None

    def pollinate(self, current_vector, current_words):
        """
        THE SPORE PROTOCOL:
        Proactively injects past memories to force creative synthesis.
        Only triggers if the system is healthy (ATP > 30).
        """
        if self.atp < 30 or not self.mem.artifacts:
            return None

        # 1. Analyze Current State
        is_abstract = current_vector['ENT'] > 0.6
        is_concrete = current_vector['TEX'] > 0.6

        # 2. Hunt for Contrast in Memory
        candidates = []
        for word in self.mem.artifacts:
            if word in current_words: continue # Don't suggest what we just said

            # Check the flavor of the memory
            mem_is_heavy = word in TheLexicon.HEAVY_MATTER
            mem_is_abstract = word in TheLexicon.ABSTRACTS

            # CONTRAST LOGIC:
            # If we are floating (Abstract), look for Anchors (Heavy).
            if is_abstract and mem_is_heavy:
                candidates.append((word, "GROUNDING SPORE"))
            # If we are heavy (Concrete), look for Concepts (Abstract).
            elif is_concrete and mem_is_abstract:
                candidates.append((word, "ELEVATING SPORE"))
            # If we are neither, just grab anything interesting.
            elif not is_abstract and not is_concrete:
                candidates.append((word, "WILD SPORE"))

        # 3. The Injection
        if candidates:
            target, spore_type = random.choice(candidates)
            return f"{Prisma.MAG}🍄 {spore_type}:{Prisma.RST} Connect '{target}' to this."

        return None

    def process(self, text):
        # 1. CONTROL PLANE
        if self.cmd.execute(text): return

        # 2. PHYSICS
        self.tick_count += 1
        m = self.phys.analyze(text)

        self.dynamics.commit(m["physics"]["voltage"])
        ta_velocity = self.dynamics.get_velocity()

        cause, msg, is_fatal = NarrativeCoroner.check_vitals(m["physics"], self.atp)
        lazarus_msg = None

        if is_fatal:
            survived, new_atp = NarrativeCoroner.attempt_resuscitation(cause, self.atp)
            if survived:
                self.atp = new_atp
                lazarus_msg = f"{Prisma.RED}⚠️ NEAR DEATH EXPERIENCE. SYSTEM UNSTABLE.{Prisma.RST}"
            else:
                NarrativeCoroner.pronounce_dead(cause, msg)
                self.atp = 20
                self.mem.save(current_atp=self.atp)
                print(f"{Prisma.GRY}[The Timeline resets...]{Prisma.RST}\n")
                return
        # ---------------------------------------
        
        # CHARGING CYCLE ----------------------------------
        charged = self.battery.absorb(m["physics"]["voltage"])
        battery_log = []
        if charged > 0:
            battery_log.append(f"{Prisma.YEL}⚡ PARADOX CAPTURED (+{round(charged, 1)} Charge){Prisma.RST}")
        # ------------------------------------------------
        
        # 3. KINTSUGI CHECK (The Golden Repair)
        kintsugi_active, koan = self.kintsugi.check_integrity(self.atp)
        kintsugi_healed = False
        
        if kintsugi_active:
             if self.kintsugi.attempt_repair(m["physics"]):
                 self.atp = 50 # FULL RESTORE
                 kintsugi_healed = True
                 m["kintsugi_msg"] = f"{Prisma.YEL}✨ KINTSUGI: THE CRACK IS FILLED WITH GOLD.{Prisma.RST}"
             else:
                 m["kintsugi_msg"] = f"{Prisma.RED}🕸️ KINTSUGI REQUIRED: {koan}{Prisma.RST}"
        else:
            m["kintsugi_msg"] = None

        # 4. METABOLISM (Standard)
        if not kintsugi_healed:
            sugar, lichen_msg = self.lichen.photosynthesize(m["physics"])
            self.atp = min(52, self.atp + sugar)

            # Metabolic Cost (Drag Tax)
            if (m["physics"]["narrative_drag"] > 3.0 
                and not lichen_msg 
                and m["physics"]["beta_friction"] < 2.0):
                self.atp -= 2
            
            # EMERGENCY DISCHARGE -------------------------
            if self.atp < 15:
                # Target: Restore to safe level (20)
                deficit = 20 - self.atp
                juice = self.battery.discharge(deficit)
                if juice > 0:
                    self.atp += juice
                    battery_log.append(f"{Prisma.YEL}⚡ BATTERY DISCHARGE (+{round(juice, 1)} ATP){Prisma.RST}")
            # ------------------------------------------------
        else:
            lichen_msg = None

        # 5. MEMORY & TIME
        self.mem.bury(m["clean_words"], self.tick_count)
        is_bored = self.chronos.tick(m["physics"], self.mem.session_id)

        # 6. SURGERY (The Butcher)
        clean_text = text
        ops = []
        for toxin, (weight, replacement) in BoneConfig.TOXIN_MAP.items():
            # Use regex sub for case-insensitive replacement
            pattern = re.compile(re.escape(toxin), re.IGNORECASE)
            if pattern.search(clean_text):
                 clean_text = pattern.sub(replacement, clean_text)
                 ops.append(f"'{toxin}' -> '{replacement}'")
        
        did_surgery = len(ops) > 0

        # 7. RADIO TUNING
        is_rag = (m["physics"]["narrative_drag"] > 3.0 and not m["physics"]["is_whimsical"])
        station_data = self.radio.tune_in(m["physics"], m["physics"]["vector"], is_rag, self.atp)

        # 8. ARCHITECT (Naming)
        strat, reason, title = self.wise.architect(m, station_data, is_bored)
        ghost_msg = self._invoke_ghost(m["physics"])

        # 9. CONTEXT PRESERVATION
        self.last_context = {
            "physics": m["physics"],
            "strategy": strat,
            "session_id": self.mem.session_id,
        }

        # 10. DEATH CHECK
        starve_msg = None
        if self.atp <= 0:
            eaten = self.mem.cannibalize()
            if eaten:
                self.atp += 10
                starve_msg = f"CANNIBALIZED: '{eaten}'"
            else:
                starve_msg = "SYSTEM FAILURE. REBOOT REQUIRED."

        # 11. SPORE PROTOCOL (Growth)
        spore_msg = self.pollinate(m["physics"]["vector"], m["clean_words"])

        # 12. RENDER
        self._render(
            m, lichen_msg, strat, reason, title, ops,
            station_data, starve_msg, ghost_msg, clean_text,
            did_surgery, battery_log, lazarus_msg,
            spore_msg
        )
        
        # Autosave logic
        if starve_msg or self.tick_count % 10 == 0:
            self.mem.save(current_atp=self.atp, current_charge=self.battery.current_charge)

    def _invoke_ghost(self, current_phys):
        # (Same as your original implementation)
        if not self.last_context: return None
        if self.last_context.get("session_id") != self.mem.session_id: return None
        
        last_p = self.last_context["physics"]
        last_strat = self.last_context["strategy"]
        delta_drag = current_phys["narrative_drag"] - last_p["narrative_drag"]
        
        if last_strat == "CLARENCE":
            if delta_drag < -0.5: return f"{Prisma.GRN}👻 THE BUTCHER NODS.{Prisma.RST}"
            elif delta_drag > 0: return f"{Prisma.RED}👻 THE BUTCHER SIGHS.{Prisma.RST}"
        return None

    def _render(self, m, lichen_msg, strat, reason, title, ops, station, starve_msg, ghost_msg, clean_text, did_surgery, battery_log, lazarus_msg, spore_msg=None, ta_val=0.0):
        p = m["physics"]

        # Color code the velocity
        if ta_val > 2.0:
            ta_c = f"{Prisma.GRN}▲{ta_val} (EPIPHANY){Prisma.RST}"
        elif ta_val < -2.0:
            ta_c = f"{Prisma.RED}▼{ta_val} (CRASH){Prisma.RST}"
        else:
            ta_c = f"{Prisma.GRY}{ta_val}{Prisma.RST}"

        # --- THE HUD FRAME ---
        print(f"\n{Prisma.GRY}[ {Prisma.WHT}{title}{Prisma.GRY} ]{'='*40}{Prisma.RST}")

        # METRICS
        atp_p = max(0, min(10, int((self.atp / 50.0) * 10)))
        atp_bar = f"{Prisma.GRN if atp_p > 3 else Prisma.RED}{'|'*atp_p}{Prisma.GRY}{'.'*(10-atp_p)}{Prisma.RST}"

        # GET BATTERY VISUAL
        batt_bar = self.battery.get_readout()

        volt_c = f"{Prisma.MAG}{p['voltage']}{Prisma.RST}" if p['voltage'] > 5 else f"{Prisma.CYN}{p['voltage']}{Prisma.RST}"
        drag_c = Prisma.wrap(p['narrative_drag'], 3.0)

        if station:
            sig_disp = f"{station['color']}{station['name']}{Prisma.RST}"
        else:
            sig_disp = f"{Prisma.GRY}STATIC{Prisma.RST}"

        # FIXED PRINT STATEMENT
        print(f" {Prisma.WHT}ATP:{Prisma.RST} [{atp_bar}] {batt_bar}  {Prisma.WHT}DRAG:{Prisma.RST} {drag_c}  {Prisma.WHT}Ta:{Prisma.RST} {ta_c}  {Prisma.WHT}VOLT:{Prisma.RST} {volt_c}  {Prisma.WHT}SIG:{Prisma.RST} {sig_disp}")

        # DIRECTIVE
        if station:
            print(f"\n {station['color']}► {station['msg']}{Prisma.RST}")

        # LOGS
        print(f" {Prisma.GRY}└─ {reason}{Prisma.RST}")

        # [PRINT LAZARUS WARNING FIRST - IT IS URGENT]
        if lazarus_msg:
            print(f"\n    {lazarus_msg}")

        # KINTSUGI OVERRIDE
        if m.get("kintsugi_msg"):
            print(f"\n    {m['kintsugi_msg']}")

        if ghost_msg: print(f"    {ghost_msg}")
        if spore_msg: print(f"    {spore_msg}")
        if lichen_msg: print(f"    {Prisma.GRN}☀️ {lichen_msg}{Prisma.RST}")
        for b_msg in battery_log:
            print(f"    {b_msg}")
        if starve_msg: print(f"    {Prisma.RED}💀 {starve_msg}{Prisma.RST}")

        if ops:
            print(f"    {Prisma.RED}🔪 SURGERY:{Prisma.RST} {', '.join(ops)}")
            if did_surgery:
                print(f"       {Prisma.GRY}IN : {m['raw_text']}{Prisma.RST}")
                print(f"       {Prisma.WHT}OUT: {clean_text}{Prisma.RST}")

        print(f"{Prisma.GRY}{'-'*65}{Prisma.RST}")


if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.GRN}>>> BONEAMANITA v3.7 ONLINE.{Prisma.RST}")
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
        print(f"{Prisma.GRY}System shutting down.{Prisma.RST}")
        saved_file = eng.mem.save(current_atp=eng.atp, current_charge=eng.battery.current_charge)
        if saved_file:
            print(f"{Prisma.CYN}Session archived to: {saved_file}{Prisma.RST}")
