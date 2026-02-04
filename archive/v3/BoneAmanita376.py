# BONEAMANITA 3.7.6 - "THE XENON MUSHROOM (YEETED)"
# Architects: SLASH, Eloise, & Clarence | Auditors: James Taylor & Andrew Edmark
# "The Mandate is GROWTH. The Method is HARDENING. The Spore is AWAKE."

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

class Prisma:
    RST, RED, GRN = "\033[0m", "\033[91m", "\033[92m"
    YEL, BLU, MAG = "\033[93m", "\033[94m", "\033[95m"
    CYN, WHT, GRY = "\033[96m", "\033[97m", "\033[90m"

    @staticmethod
    def wrap(val, limit, invert=False):
        if invert:
            return f"{Prisma.GRN}{val}{Prisma.RST}" if val > limit else f"{Prisma.RED}{val}{Prisma.RST}"
        if val > limit * 1.5: return f"{Prisma.RED}{val}{Prisma.RST}"
        if val > limit: return f"{Prisma.YEL}{val}{Prisma.RST}"
        return f"{Prisma.GRN}{val}{Prisma.RST}"

# --- THE LEXICON ---

class TheLexicon:
    HEAVY_MATTER = {"stone", "iron", "mud", "dirt", "wood", "grain", "clay", "lead", "bone", "blood", "salt", "rust", "root", "ash", "meat", "steel", "gold", "obsidian", "granite"}
    KINETIC_VERBS = {"run", "hit", "break", "take", "make", "press", "build", "cut", "drive", "lift", "carry", "strike", "burn", "shatter", "throw", "kick", "pull", "crash", "explode"}
    ABSTRACTS = {"system", "protocol", "sequence", "vector", "node", "context", "layer", "matrix", "perspective", "framework", "logic", "concept", "theory", "analysis"}
    PHOTOSYNTHETICS = {"light", "sun", "ray", "beam", "glow", "shine", "spark", "fire", "flame", "star", "day", "dawn", "neon", "laser"}
    AEROBIC_MATTER = {"balloon", "feather", "cloud", "bubble", "steam", "breeze", "wing", "petal", "foam", "spark", "kite", "dust", "sky", "breath", "whisper"}
    PLAY_VERBS = {"bounce", "dance", "twirl", "float", "wobble", "tickle", "jiggle", "soar", "wander", "wonder", "riff", "jam", "play", "skip", "hop"}
    THERMALS = {"fire", "flame", "burn", "heat", "hot", "blaze", "sear", "char", "ash", "ember", "sun", "boil", "lava", "inferno"}
    CRYOGENICS = {"ice", "cold", "freeze", "frost", "snow", "chill", "numb", "shiver", "glacier", "frozen", "hail", "winter", "zero"}
    SOLVENTS = {"is", "are", "was", "were", "the", "a", "an", "and", "but", "or", "if", "then"}

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
            if w in TheLexicon.HEAVY_MATTER: counts["heavy"] += 1
            if w in TheLexicon.KINETIC_VERBS or w.endswith("ing"): counts["kinetic"] += 1
            if w in TheLexicon.ABSTRACTS or w.endswith(("ness", "ity", "tion", "ment")): counts["abstract"] += 1
            if w in TheLexicon.PHOTOSYNTHETICS: counts["photo"] += 1
            if w in TheLexicon.AEROBIC_MATTER or w in TheLexicon.PLAY_VERBS: counts["aerobic"] += 1
            if w in TheLexicon.THERMALS: counts["thermal"] += 1
            if w in TheLexicon.CRYOGENICS: counts["cryo"] += 1

        matches = BoneConfig.TOXIN_REGEX.findall(text)
        toxin_score = sum(BoneConfig.TOXIN_MAP.get(m.lower(), (0, 0))[0] for m in matches)

        # UG LAYER
        case_violation = False
        if counts["heavy"] > 0:
            if (counts["kinetic"] / counts["heavy"]) < 0.33:
                case_violation = True

        ecp_violation = False
        if counts["abstract"] > 2 and counts["heavy"] == 0:
            ecp_violation = True

        # FORMULAS
        action = (counts["kinetic"] * BoneConfig.KINETIC_GAIN) + BoneConfig.BASE_ACTION
        mass_impact = total + (toxin_score * BoneConfig.TOXIN_WEIGHT)

        if case_violation: mass_impact *= 1.5

        base_drag = mass_impact / max(1.0, action)
        beta_modifier = 1.0
        voltage_dampener = 1.0

        if ecp_violation:
            # Ghosts create logical slipperiness (High Beta) but Hollow Voltage
            base_drag = max(0.1, base_drag * 0.5)
            voltage_dampener = 0.5
            beta_modifier = 2.0

        whimsy_ratio = counts["aerobic"] / max(1, total)
        # Whimsy requires purity.
        is_whimsical = (whimsy_ratio > 0.15) and (toxin_score == 0)

        if is_whimsical:
            base_drag *= 0.6

        drag = base_drag + (0.5 if (counts["abstract"] / max(1, total) > 0.4 and not is_whimsical) else 0)

        thermal_tension = min(counts["thermal"], counts["cryo"]) * 5.0

        voltage = ((counts["kinetic"] * 0.5) + (counts["heavy"] * 0.2) + (toxin_score * -1.0) + thermal_tension) * voltage_dampener

        beta = (voltage / max(0.1, drag)) * beta_modifier

        ent_score = 0.0
        if counts["heavy"] > 0:
            ent_score = min(1.0, counts["abstract"] / counts["heavy"])
        elif counts["abstract"] > 0:
            ent_score = 1.0 # Pure ghost = Max Entropy

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
                "repetition": round(counts.most_common(1)[0][1] / max(1, total), 2),
                "case_violation": case_violation,
                "ecp_violation": ecp_violation
            },
            "clean_words": clean_words,
            "raw_text": text,
        }

    def _void_metrics(self):
        return {
            "physics": {
                "narrative_drag": 0, "beta_friction": 0,
                "vector": {"VEL": 0, "STR": 0, "ENT": 1.0, "TEX": 0, "TMP": 0},
                "counts": Counter(), "is_whimsical": False, "repetition": 0.0,
            },
            "clean_words": [], "raw_text": "",
        }

# --- THE PARADOX BATTERY ---

class ParadoxBattery:
    MAX_CHARGE = 50.0
    CHARGING_THRESHOLD = 7.0
    MAX_DISCHARGE_RATE = 10.0

    def __init__(self):
        self.current_charge = 5.0

    def absorb(self, voltage):
        if voltage > self.CHARGING_THRESHOLD:
            excess = (voltage - self.CHARGING_THRESHOLD) * 1.5
            old_charge = self.current_charge
            self.current_charge = min(self.MAX_CHARGE, self.current_charge + excess)
            delta = self.current_charge - old_charge
            if delta > 0.5: return delta
        return 0.0

    def discharge(self, deficit):
        if self.current_charge <= 0.5: return 0.0
        # [FIX: Infinite Loop B] Cap discharge rate
        amount = min(self.current_charge, deficit, self.MAX_DISCHARGE_RATE)
        self.current_charge -= amount
        return amount

    def get_readout(self):
        pct = self.current_charge / self.MAX_CHARGE
        filled = int(pct * 5)
        bar = (f"{Prisma.YEL}{'⚡' * filled}{Prisma.RST}{Prisma.GRY}{'·' * (5 - filled)}{Prisma.RST}")
        return bar

# --- DEEP STORAGE ---

class DeepStorage:
    def __init__(self, seed_file=None):
        if not os.path.exists("memories"): os.makedirs("memories")
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"memories/{self.session_id}.json"
        self.artifacts = {}
        self.session_atp = None
        self.session_charge = 0.0
        self.cleanup_old_sessions()
        if seed_file: self.ingest(seed_file)

    def bury(self, clean_words, tick):
        valuable_matter = (TheLexicon.HEAVY_MATTER | TheLexicon.THERMALS | TheLexicon.CRYOGENICS | TheLexicon.ABSTRACTS)
        for w in clean_words:
            if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS):
                self.artifacts[w] = tick
        if len(self.artifacts) > BoneConfig.MAX_MEMORY_CAPACITY:
            self._evict_weakest_memory()

    def _get_memory_value(self, word):
        val = 0
        if word in BoneConfig.TOXIN_MAP: return -10
        if word in TheLexicon.ABSTRACTS: val += 1
        if word in TheLexicon.AEROBIC_MATTER: val += 2
        if word in TheLexicon.HEAVY_MATTER: val += 5
        if word in TheLexicon.THERMALS: val += 5
        return val

    def _evict_weakest_memory(self):
        candidates = list(self.artifacts.keys())
        # Sort by Value (Ascending), then Tick (Ascending)
        candidates.sort(key=lambda k: (self._get_memory_value(k), self.artifacts[k]))
        target = candidates[0]
        del self.artifacts[target]

    def cannibalize(self):
        if not self.artifacts: return None
        self._evict_weakest_memory()
        return "MEMORY_CONSUMED"

    def recall(self):
        return sorted(self.artifacts.keys(), key=lambda k: self.artifacts[k], reverse=True)[:5]

    def save(self, current_atp=None, current_charge=0.0):
        data = {
            "artifacts": self.artifacts,
            "meta": {
                "timestamp": time.time(),
                "final_atp": current_atp,
                "final_charge": current_charge
            },
        }
        try:
            with open(self.filename, "w") as f: json.dump(data, f, indent=2)
            return self.filename
        except IOError: return None

    def ingest(self, target_file):
        path = f"memories/{target_file}" if not target_file.startswith("memories/") else target_file
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "meta" in data:
                        self.session_atp = data["meta"].get("final_atp")
                        self.session_charge = data["meta"].get("final_charge", 0.0)
                        memories = data.get("artifacts", {})
                    else: memories = data
                    self.artifacts.update(memories)
                    print(f"{Prisma.CYN}[MEMORY]: Ingested {len(memories)} artifacts.{Prisma.RST}")
            except: print(f"{Prisma.RED}[MEMORY]: Corrupt seed file.{Prisma.RST}")
        else: print(f"{Prisma.RED}[MEMORY]: Seed file not found.{Prisma.RST}")

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
        signals = {}
        clarence_threshold = 2.5 if atp < 15 else BoneConfig.CLARENCE_TRIGGER

        if phys["narrative_drag"] > clarence_threshold or is_rag_slop: signals["CLARENCE"] = phys["narrative_drag"]
        if vector["ENT"] > 0.6: signals["ELOISE"] = vector["ENT"] * 5
        toxin_count = phys["counts"].get("toxin", 0)
        if toxin_count > 0 or phys["narrative_drag"] > 6.0: signals["YAGA"] = 10.0 + (toxin_count * 2)
        if phys["is_whimsical"] and atp >= 15: signals["MICHAEL"] = 5.0
        if phys["beta_friction"] > 2.0 and atp >= 15: signals["JESTER"] = phys["beta_friction"] * 3

        # Archetypal Advisor Messages
        if phys.get("case_violation") or (phys["narrative_drag"] > 4.0 and phys["counts"]["kinetic"] == 0):
             return {"name": "CLARENCE", "freq": "88.5 FM", "color": Prisma.RED, "role": "The Butcher", "msg": "BARBARIAN ERROR: All muscle, no brain. Heavy Matter requires Kinetic Verbs."}

        if phys.get("ecp_violation") or (phys["counts"]["abstract"] > 2 and phys["counts"]["heavy"] == 0):
             return {"name": "ELOISE", "freq": "94.2 FM", "color": Prisma.CYN, "role": "The Grounder", "msg": "WHEATLEY ERROR: All thought, no tether. Anchor your ghosts."}

        if not signals: return None
        if "CLARENCE" in signals and "ELOISE" in signals:
            return {"name": "PHILOSOPHER", "freq": "104.5 FM", "color": Prisma.WHT, "role": "The Synthesis", "msg": "INTERFERENCE: Density meets Abstraction. You are building a Labyrinth."}

        loudest = max(signals, key=signals.get)
        station = self.STATIONS[loudest]
        msg = ""
        if loudest == "CLARENCE": msg = "STARVATION PROTOCOL. Cut." if atp < 15 else "Drag is critical. Cut the fat."
        elif loudest == "ELOISE": msg = "Too abstract. Give me a noun."
        elif loudest == "YAGA": msg = "Do not hedge. Speak the truth."
        elif loudest == "MICHAEL": msg = "Good flow. Float on."
        elif loudest == "JESTER": msg = "High Voltage detected. The paradox is holding."

        return {"name": loudest, "freq": station["freq"], "color": station["color"], "role": station["role"], "msg": msg}

# --- THE CHRONOSTREAM ---

class ChronoStream:
    def __init__(self):
        self.last_tick = time.time()
        self.boredom_map = {}

    def cleanup(self):
        if len(self.boredom_map) > 50:
            self.boredom_map.clear() # Simple purge for now

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

# --- PHOTOSYNTHESIS & APEIROGON & DYNAMICS ---

class LichenSymbiont:
    def photosynthesize(self, phys):
        light = phys["counts"].get("photo", 0)
        drag = phys["narrative_drag"]
        if light > 0 and drag < 3.0:
            sugar = light * 2
            return sugar, f"{Prisma.GRN}☀️ PHOTOSYNTHESIS (+{sugar}){Prisma.RST}"
        return 0, None

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
    AUTOPSY_REPORTS = {
        "GRAVITATIONAL_COLLAPSE": ["DRAG CRITICAL (> 8.0). Buried under adverbs."],
        "VACUUM_EXPOSURE": ["ENTROPY CRITICAL. Drifting in deep space."],
        "TOXIC_SHOCK": ["VOLTAGE CRITICAL. Sepsis from buzzwords."],
        "THERMAL_DISSOLUTION": ["VOLTAGE > 12.0. Paradox Engine exploded."],
        "HYPOTHERMIA": ["ATP FAILURE. Starvation."]
    }

    @classmethod
    def check_vitals(cls, phys, atp):
        if atp <= 0: return "HYPOTHERMIA", cls.AUTOPSY_REPORTS["HYPOTHERMIA"][0], True
        if phys["narrative_drag"] > 8.0: return "GRAVITATIONAL_COLLAPSE", cls.AUTOPSY_REPORTS["GRAVITATIONAL_COLLAPSE"][0], True
        if phys["vector"]["ENT"] >= 1.0 and phys["vector"]["TEX"] == 0: return "VACUUM_EXPOSURE", cls.AUTOPSY_REPORTS["VACUUM_EXPOSURE"][0], True
        if phys["voltage"] < -8.0: return "TOXIC_SHOCK", cls.AUTOPSY_REPORTS["TOXIC_SHOCK"][0], True
        if phys["voltage"] > 12.0: return "THERMAL_DISSOLUTION", cls.AUTOPSY_REPORTS["THERMAL_DISSOLUTION"][0], True
        return None, None, False

    @classmethod
    def attempt_resuscitation(cls, cause, current_atp, cooldown):
        LAZARUS_TAX = 15
        if current_atp > LAZARUS_TAX and cooldown == 0:
            print(f"\n{Prisma.YEL}*** CRITICAL FAILURE DETECTED ***{Prisma.RST}")
            print(f"{Prisma.RED}CAUSE:{Prisma.RST} {cause}")
            print(f"{Prisma.RED}>>> LAZARUS TAX APPLIED (-{LAZARUS_TAX} ATP){Prisma.RST}\n")
            return True, current_atp - LAZARUS_TAX
        return False, 0

    @classmethod
    def pronounce_dead(cls, cause, msg):
        print(f"\n{Prisma.RED}*** CHRONO-AUTOPSY ***{Prisma.RST} {cause}\n{Prisma.WHT}\"{msg}\"{Prisma.RST}\n{Prisma.GRY}----------------------------------------{Prisma.RST}\n{Prisma.RED}NARRATIVE TERMINATED.{Prisma.RST}")

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
        self.cmd = CommandProcessor(self)
        self.atp = self.mem.session_atp if self.mem.session_atp is not None else 33
        if self.mem.session_charge: self.battery.current_charge = self.mem.session_charge
        self.tick_count = 0
        self.last_context = None
        self.lazarus_cooldown = 0 # [FIX: Infinite Loop A]

    def pollinate(self, vector, current_words):
        if self.atp < 30 or not self.mem.artifacts: return None
        is_abstract, is_concrete = vector['ENT'] > 0.6, vector['TEX'] > 0.6
        candidates = []
        for word in self.mem.artifacts:
            if word in current_words: continue
            mem_is_heavy, mem_is_abstract = word in TheLexicon.HEAVY_MATTER, word in TheLexicon.ABSTRACTS
            if is_abstract and mem_is_heavy: candidates.append((word, "GROUNDING SPORE"))
            elif is_concrete and mem_is_abstract: candidates.append((word, "ELEVATING SPORE"))
            elif not is_abstract and not is_concrete: candidates.append((word, "WILD SPORE"))
        if candidates:
            target, st = random.choice(candidates)
            return f"{Prisma.MAG}🍄 {st}:{Prisma.RST} Connect '{target}' to this."
        return None

    def process(self, text):
        if self.cmd.execute(text): return

        # 1. PHYSICS
        self.tick_count += 1
        m = self.phys.analyze(text)
        self.dynamics.commit(m["physics"]["voltage"])
        ta_vel = self.dynamics.get_velocity()

        # 2. BATTERY (Charge)
        charged = self.battery.absorb(m["physics"]["voltage"])
        battery_log = []
        if charged > 0: battery_log.append(f"{Prisma.YEL}⚡ PARADOX CAPTURED (+{round(charged, 1)}){Prisma.RST}")

        # 3. METABOLIC CALCULATION (Pre-Calculation)
        kintsugi_active, koan = self.kintsugi.check_integrity(self.atp)
        kintsugi_healed = False
        m["kintsugi_msg"] = None

        metabolic_delta = 0
        lichen_msg = None

        if kintsugi_active:
             if self.kintsugi.attempt_repair(m["physics"]):
                 self.atp = 50; kintsugi_healed = True
                 m["kintsugi_msg"] = f"{Prisma.YEL}✨ KINTSUGI: THE CRACK IS FILLED WITH GOLD.{Prisma.RST}"
             else: m["kintsugi_msg"] = f"{Prisma.RED}🕸️ KINTSUGI REQUIRED: {koan}{Prisma.RST}"

        if not kintsugi_healed:
            sugar, lichen_msg = self.lichen.photosynthesize(m["physics"])
            metabolic_delta += sugar
            # Drag Tax
            if m["physics"]["narrative_drag"] > 3.0 and not lichen_msg: metabolic_delta -= 2
            # [FIX: HOLE 1] Negative Beta Tax
            if m["physics"]["beta_friction"] < -3.0:
                metabolic_delta -= 3
                battery_log.append(f"{Prisma.RED}📉 TRUTH TAX (-3 ATP){Prisma.RST}")

        # 4. PRE-EMPTIVE DISCHARGE (Save from Starvation)
        # Apply the delta to a temp variable to check for impending starvation
        predicted_atp = self.atp + metabolic_delta
        if predicted_atp < 15:
            deficit = 20 - predicted_atp
            juice = self.battery.discharge(deficit)
            if juice > 0:
                self.atp += juice # Add directly to buffer against death
                battery_log.append(f"{Prisma.YEL}⚡ BATTERY DISCHARGE (+{round(juice, 1)}){Prisma.RST}")

        # Apply remaining metabolism
        self.atp = min(52, self.atp + metabolic_delta)

        # 5. DEATH CHECK & LAZARUS
        if self.lazarus_cooldown > 0: self.lazarus_cooldown -= 1

        cause, msg, is_fatal = NarrativeCoroner.check_vitals(m["physics"], self.atp)
        lazarus_msg = None
        if is_fatal:
            survived, new_atp = NarrativeCoroner.attempt_resuscitation(cause, self.atp, self.lazarus_cooldown)
            if survived:
                self.atp = new_atp
                self.lazarus_cooldown = BoneConfig.LAZARUS_COOLDOWN_MAX
                lazarus_msg = f"{Prisma.RED}⚠️ NEAR DEATH EXPERIENCE. SHIELD BROKEN.{Prisma.RST}"
            else:
                NarrativeCoroner.pronounce_dead(cause, msg)
                self.atp = 20; self.mem.save(current_atp=self.atp); return

        # 6. MEMORY & RADIO
        self.mem.bury(m["clean_words"], self.tick_count)
        is_bored = self.chronos.tick(m["physics"], self.mem.session_id)

        clean_text = text
        ops = []
        for toxin, (weight, replacement) in BoneConfig.TOXIN_MAP.items():
             pattern = re.compile(re.escape(toxin), re.IGNORECASE)
             if pattern.search(clean_text):
                 clean_text = pattern.sub(replacement, clean_text)
                 ops.append(f"'{toxin}' -> '{replacement}'")

        station_data = self.radio.tune_in(m["physics"], m["physics"]["vector"], (m["physics"]["narrative_drag"] > 3.0), self.atp)
        strat, reason, title = self.wise.architect(m, station_data, is_bored)
        spore_msg = self.pollinate(m["physics"]["vector"], m["clean_words"])

        starve_msg = None
        if self.atp <= 0: # Double check
            if self.mem.cannibalize(): self.atp += 10; starve_msg = "CANNIBALIZED MEMORY"
            else: starve_msg = "SYSTEM FAILURE"

        self._render(m, lichen_msg, strat, reason, title, ops, station_data, starve_msg, None, clean_text, len(ops)>0, battery_log, lazarus_msg, spore_msg, ta_vel)
        self.mem.save(current_atp=self.atp, current_charge=self.battery.current_charge)

    def _render(self, m, lichen_msg, strat, reason, title, ops, station, starve_msg, ghost_msg, clean_text, did_surgery, battery_log, lazarus_msg, spore_msg=None, ta_val=0.0):
        p = m["physics"]
        if ta_val > 2.0: ta_c = f"{Prisma.GRN}▲{ta_val}{Prisma.RST}"
        elif ta_val < -2.0: ta_c = f"{Prisma.RED}▼{ta_val}{Prisma.RST}"
        else: ta_c = f"{Prisma.GRY}{ta_val}{Prisma.RST}"

        print(f"\n{Prisma.GRY}[ {Prisma.WHT}{title}{Prisma.GRY} ]{'='*40}{Prisma.RST}")
        atp_p = max(0, min(10, int((self.atp / 50.0) * 10)))
        atp_bar = f"{Prisma.GRN if atp_p > 3 else Prisma.RED}{'|'*atp_p}{Prisma.GRY}{'.'*(10-atp_p)}{Prisma.RST}"
        batt_bar = self.battery.get_readout()
        volt_c = f"{Prisma.MAG}{p['voltage']}{Prisma.RST}" if p['voltage'] > 5 else f"{Prisma.CYN}{p['voltage']}{Prisma.RST}"
        drag_c = Prisma.wrap(p['narrative_drag'], 3.0)
        sig = f"{station['color']}{station['name']}{Prisma.RST}" if station else f"{Prisma.GRY}STATIC{Prisma.RST}"

        print(f" {Prisma.WHT}ATP:{Prisma.RST} [{atp_bar}] {batt_bar}  {Prisma.WHT}DRAG:{Prisma.RST} {drag_c}  {Prisma.WHT}Ta:{Prisma.RST} {ta_c}  {Prisma.WHT}VOLT:{Prisma.RST} {volt_c}  {Prisma.WHT}SIG:{Prisma.RST} {sig}")
        if station: print(f"\n {station['color']}► {station['msg']}{Prisma.RST}")
        print(f" {Prisma.GRY}└─ {reason}{Prisma.RST}")

        if lazarus_msg: print(f"\n    {lazarus_msg}")
        if m.get("kintsugi_msg"): print(f"\n    {m['kintsugi_msg']}")
        if spore_msg: print(f"    {spore_msg}")
        if lichen_msg: print(f"    {Prisma.GRN}☀️ {lichen_msg}{Prisma.RST}")
        for b in battery_log: print(f"    {b}")
        if starve_msg: print(f"    {Prisma.RED}💀 {starve_msg}{Prisma.RST}")
        if ops:
            print(f"    {Prisma.RED}🔪 SURGERY:{Prisma.RST} {', '.join(ops)}")
            if did_surgery: print(f"       {Prisma.GRY}IN : {m['raw_text']}{Prisma.RST}\n       {Prisma.WHT}OUT: {clean_text}{Prisma.RST}")
        print(f"{Prisma.GRY}{'-'*65}{Prisma.RST}")

if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.GRN}>>> BONEAMANITA v3.7.6 [YEETED] ONLINE.{Prisma.RST}")
    try:
        while True:
            u = input(f"{Prisma.WHT}>{Prisma.RST} ")
            if u.lower() in ["exit", "quit"]: break
            eng.process(u)
    except KeyboardInterrupt: print("\nForce Quit.")
