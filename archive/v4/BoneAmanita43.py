# BONEAMANITA 4.3 - "THE SALVAGE OPERATION"
# Architects: SLASH, Eloise, & Clarence | Auditors: James Taylor & Andrew Edmark
# "The Mandate is GROWTH. The Method is HARDENING. The Spore is AWAKE. The Symbiont is EVOLVING. The Data is SALVAGED."

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
    # HARDCODED "DNA" (The Base Layer)
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

    # DYNAMIC LAYER (The Learned Cortex)
    LEARNED_VOCAB = {
        "heavy": set(), "kinetic": set(), "abstract": set(), "photo": set(),
        "aerobic": set(), "thermal": set(), "cryo": set()
    }

    @classmethod
    def clean(cls, text):
        return text.lower().translate(cls._TRANSLATOR).split()

    @classmethod
    def get(cls, category):
        """Returns union of Base DNA + Learned Cortex"""
        base = getattr(cls, f"_BASE_{category.upper()}", set())
        learned = cls.LEARNED_VOCAB.get(category, set())
        return base | learned

    @classmethod
    def teach(cls, word, category):
        """Manual injection of knowledge"""
        if category in cls.LEARNED_VOCAB:
            cls.LEARNED_VOCAB[category].add(word.lower())
            return True
        return False

# --- PHYSICS ---

class PhysicsEngine:
    def analyze(self, text):
        clean_words = TheLexicon.clean(text)
        total = len(clean_words)
        if total == 0:
            return self._void_metrics()

        counts = Counter()
        toxin_score = 0

        # RHYTHM DETECTION (The Oscilloscope)
        # Split by punctuation to measure sentence/phrase length variance
        sentences = [s for s in re.split(r'[.!?]', text) if len(s.split()) > 0]
        lengths = [len(s.split()) for s in sentences]
        rhythm_variance = 0.0
        if len(lengths) > 1:
            mean = sum(lengths) / len(lengths)
            variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
            rhythm_variance = math.sqrt(variance) # Standard Deviation represents "Beat Variety"

        # CATEGORY SCANS (Using Dynamic Lexicon)
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
        counts["toxin"] = len(matches) # Explicit

        # --- GRAFT: THE ANCESTRAL METRICS ---

        # 1. MEASURE BLEED (Beta)
        has_bleed = self._measure_bleed(clean_words)

        # 2. MEASURE FATIGUE (Epsilon) [cite: 134]
        # Using simple repetition ratio as the proxy for Motif Fatigue
        repetition_score = 0.0
        if total > 0:
            repetition_score = counts.most_common(1)[0][1] / total
        is_fatigued = repetition_score > 0.3 # The Fatigue Threshold (E_th) [cite: 116]

        # 3. DETERMINE SYMBOLIC STATE
        # Gold: Cohesive but predictable (Low Beta, Low E) -> "BOREDOM"
        # Slop: High Beta, High E -> "CHAOS"
        # Salvage: High Beta, Low E -> "SALVAGE" (The Goal)

        symbolic_state = "NEUTRAL"
        if has_bleed and not is_fatigued:
            symbolic_state = "SALVAGE"
        elif is_fatigued:
            symbolic_state = "FATIGUE" # Replaces 'Slop' in our internal logic
        elif not has_bleed and repetition_score < 0.1:
            symbolic_state = "GOLD" # Too safe. The Cohesion Trap. [cite: 12]

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
            base_drag = max(0.1, base_drag * 0.5)
            voltage_dampener = 0.5
            beta_modifier = 2.0

        whimsy_ratio = counts["aerobic"] / max(1, total)
        is_whimsical = (whimsy_ratio > 0.15) and (toxin_score == 0)

        if is_whimsical:
            base_drag *= 0.6

        # OSCILLOSCOPE BONUS: High variance (Musicality) reduces drag
        if rhythm_variance > 2.0:
            base_drag *= 0.9

        drag = base_drag + (0.5 if (counts["abstract"] / max(1, total) > 0.4 and not is_whimsical) else 0)

        thermal_tension = min(counts["thermal"], counts["cryo"]) * 5.0

        voltage = ((counts["kinetic"] * 0.5) + (counts["heavy"] * 0.2) + (toxin_score * -1.0) + thermal_tension) * voltage_dampener

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

        def _measure_bleed(self, clean_words):
        # ANCESTRAL TRUTH: Contradiction Bleed (Beta)
        # We look for "Heavy" (Material) words clashing with "Aerobic" (Spirit) words
        # within a tight proximity window (Distance < 3).

        heavy_indices = [i for i, w in enumerate(clean_words) if w in TheLexicon.get("heavy")]
        aerobic_indices = [i for i, w in enumerate(clean_words) if w in TheLexicon.get("aerobic")]

        if not heavy_indices or not aerobic_indices:
            return False

        # Check proximity
        # This maps to the "Coherence Distance Threshold" (Dist_th) from the paper
        for h_idx in heavy_indices:
            for a_idx in aerobic_indices:
                if abs(h_idx - a_idx) < 3: # The spark gap is small
                    return True
        return False

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
                "rhythm_variance": 0.0
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

        # GRAPH STRUCTURE: { "word": { "connected_word": weight, "last_tick": 10 } }
        self.graph = {}
        self.session_health = None
        self.session_stamina = None
        self.cleanup_old_sessions()
        if seed_file: self.ingest(seed_file)

    def bury(self, clean_words, tick):
        # We only care about substantial matter
        valuable_matter = (TheLexicon.get("heavy") | TheLexicon.get("thermal") | TheLexicon.get("cryo") | TheLexicon.get("abstract"))
        filtered = [w for w in clean_words if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)]

        # Link adjacent words (The Mycelial Connection)
        for i in range(len(filtered)):
            current = filtered[i]
            if current not in self.graph: self.graph[current] = {"edges": {}, "last_tick": tick}
            else: self.graph[current]["last_tick"] = tick # Refresh recency

            # Create edge to PREVIOUS word (Context chain)
            if i > 0:
                prev = filtered[i-1]
                if prev not in self.graph[current]["edges"]: self.graph[current]["edges"][prev] = 0
                self.graph[current]["edges"][prev] += 1

                # Bi-directional bonding
                if prev not in self.graph: self.graph[prev] = {"edges": {}, "last_tick": tick}
                if current not in self.graph[prev]["edges"]: self.graph[prev]["edges"][current] = 0
                self.graph[prev]["edges"][current] += 1

        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            self._prune_graph()

    def _prune_graph(self):
        # BURNS FAT UNTIL FIT
        # Loop until we are back under the limit
        while len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            candidates = list(self.graph.keys())
            # Sort by: Oldest tick (primary), Fewest connections (secondary)
            candidates.sort(key=lambda k: (self.graph[k]["last_tick"], len(self.graph[k]["edges"])))

            # Kill the weakest node
            victim = candidates[0]
            del self.graph[victim]

            # OPTIONAL: Clean up dangling edges in other nodes to prevent phantom limbs
            for node in self.graph:
                if victim in self.graph[node]["edges"]:
                    del self.graph[node]["edges"][victim]

    def cannibalize(self):
        if not self.graph: return None
        self._prune_graph()
        return "MEMORY_CONSUMED"

    def recall_spores(self, current_words):
        candidates = []
        for w in current_words:
            if w in self.graph:
                edges = self.graph[w]["edges"]
                if edges:
                    # Filter toxins
                    clean_edges = {k:v for k,v in edges.items() if k not in BoneConfig.TOXIN_MAP}
                    if not clean_edges: continue

                    # Weighted Random Selection (The Mutation)
                    # We pick from the top 3 strongest connections
                    sorted_edges = sorted(clean_edges.items(), key=lambda x: x[1], reverse=True)[:3]

                    if not sorted_edges: continue

                    # Unpack for random.choices
                    words, weights = zip(*sorted_edges)
                    chosen = random.choices(words, weights=weights, k=1)[0]

                    if chosen not in current_words:
                        candidates.append((chosen, clean_edges[chosen]))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:1]

    def save(self, health=100, stamina=50):
        data = {
            "graph": self.graph,
            "vocab": {k: list(v) for k, v in TheLexicon.LEARNED_VOCAB.items()},
            "meta": {
                "timestamp": time.time(),
                "final_health": health,
                "final_stamina": stamina
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
                        self.session_health = data["meta"].get("final_health")
                        self.session_stamina = data["meta"].get("final_stamina")
                        memories = data.get("graph", {})
                        vocab = data.get("vocab", {})
                        for cat, words in vocab.items():
                            if cat in TheLexicon.LEARNED_VOCAB:
                                TheLexicon.LEARNED_VOCAB[cat].update(words)
                    else: memories = {}
                    self.graph.update(memories)
                    print(f"{Prisma.CYN}[MEMORY]: Grafted {len(memories)} nodes to the mycelium.{Prisma.RST}")
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

    def decay_synapses(self, entropy_rate=0.1):
        """
        The Entropy Protocol.
        Weakens all connections. Kills dead links. Prunes isolated nodes.
        Returns: Count of dead nodes removed.
        """
        dead_links_count = 0
        dead_nodes = []

        # 1. ERODE CONNECTIONS
        # We must iterate over a list of keys because we might delete during iteration
        for word in list(self.graph.keys()):
            edges = self.graph[word]["edges"]
            dead_edges = []

            for target, strength in edges.items():
                # Apply Entropy
                new_strength = strength - entropy_rate
                edges[target] = new_strength

                # Check for Snap
                if new_strength <= 0:
                    dead_edges.append(target)

            # Prune the dead edges from this node
            for dead in dead_edges:
                del edges[dead]
                dead_links_count += 1

            # 2. CHECK FOR ISOLATION
            # If a node has no edges left, it is dead weight.
            if not edges:
                dead_nodes.append(word)

        # 3. BURY THE DEAD
        for victim in dead_nodes:
            del self.graph[victim]

        if dead_nodes or dead_links_count > 0:
            return f"ENTROPY: Snapped {dead_links_count} links. Buried {len(dead_nodes)} nodes."
        return None

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
        # 0. THE VETO PROTOCOL (Ancestral Defense)
        # If we are in Motif Fatigue, Clarence overrides all other signals.
        # This prevents the "Cohesion Trap"[cite: 12].
        if phys.get("symbolic_state") == "FATIGUE":
            return {
                "name": "CLARENCE",
                "freq": "88.5 FM",
                "color": Prisma.RED,
                "role": "The Butcher",
                "msg": "MOTIF FATIGUE. You are looping. Cut the thread."
            }

        # 1. INITIALIZE THE COUNCIL (The Voting Floor)
        signals = {k: 0.0 for k in self.STATIONS.keys()}
        drag = phys["narrative_drag"]
        volt = phys["voltage"]
        toxin_count = phys["counts"].get("toxin", 0)

        # 2. CALCULATE BIDS (Weighted Signal Strength)

       # CLARENCE (The Butcher)
        if phys.get("case_violation"): signals["CLARENCE"] += BoneConfig.SIGNAL_VETO_PENALTY
        if drag > BoneConfig.CLARENCE_TRIGGER: signals["CLARENCE"] += (drag * BoneConfig.SIGNAL_DRAG_MULTIPLIER)
        if is_rag_slop: signals["CLARENCE"] += 5.0

        # ELOISE (The Grounder)
        if phys.get("ecp_violation"): signals["ELOISE"] += BoneConfig.SIGNAL_VETO_PENALTY
        if vector["ENT"] > BoneConfig.SIGNAL_ENTROPY_TRIGGER: signals["ELOISE"] += (vector["ENT"] * 10)


        # YAGA (The Witch) - Bids on Toxins & Hedging
        if toxin_count > 0: signals["YAGA"] += 10.0 + (toxin_count * 5)
        if phys["beta_friction"] < -3.0: signals["YAGA"] += abs(phys["beta_friction"]) * 2

        # MICHAEL (The Vibe) - Bids on Whimsy (Fragile)
        if phys["is_whimsical"] and atp >= 15: signals["MICHAEL"] += 12.0
        # Michael is silenced by toxins automatically via logic elsewhere, but we ensure it here:
        if toxin_count > 0: signals["MICHAEL"] = 0

        # JESTER (The Paradox)
        if volt > BoneConfig.SIGNAL_VOLTAGE_HIGH: signals["JESTER"] += (volt - 5.0) * 3

        # PHILOSOPHER (The Synthesis) - Emerges from Conflict
        if signals["CLARENCE"] > 5 and signals["ELOISE"] > 5:
            signals["PHILOSOPHER"] = signals["CLARENCE"] + signals["ELOISE"] + 5

        # 3. THE GAVEL (Select Winner)
        loudest = max(signals, key=signals.get)
        if signals[loudest] < 2.0: return None # Silence is acceptable

        station = self.STATIONS[loudest]

        # 4. DYNAMIC MESSAGING (Context-Aware)
        msg = ""
        if loudest == "CLARENCE":
            msg = "BARBARIAN ERROR. Heavy Matter needs velocity." if phys.get("case_violation") else "Cut the fat. You are dragging the hull."
        elif loudest == "ELOISE":
            msg = "WHEATLEY ERROR. Anchor this ghost." if phys.get("ecp_violation") else "Too much sky, not enough earth."
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

class TheOracle:
    @staticmethod
    def triage(phys, stamina, charge):
        omens = []
        drag = phys["narrative_drag"]
        volt = phys["voltage"]

        # 1. STARVATION (The Silent Killer fixed)
        # Warn if stamina is low, regardless of charge, but escalate if charge is low.
        if stamina < 5:
            if charge < 2.0: omens.append((100, "FAMINE IMMINENT. FEED OR DIE.", Prisma.RED))
            else: omens.append((80, "Reserves Critical. Discharge Imminent.", Prisma.YEL))
        elif stamina < 15:
            omens.append((45, "Metabolism slowing. Conserve energy.", Prisma.GRY))

        # 2. EVENT HORIZON (Gravity)
        if drag > 8.0:
             omens.append((95, "GRAVITATIONAL COLLAPSE. CUT ADVERBS NOW.", Prisma.RED))
        elif drag > 6.0:
             omens.append((40, "Heavy Drag detected. Orbit decaying.", Prisma.YEL))

        # 3. STATIC/TOXICITY
        if volt > 9.0:
            omens.append((80, "VOLTAGE CRITICAL. DISCHARGE REQUIRED.", Prisma.CYN))
        elif volt < -6.5:
             omens.append((85, "TOXICITY RISING. SYSTEM SEPTIC.", Prisma.MAG))

        if not omens: return None

        # TRIAGE: Sort by priority, return only the worst one
        omens.sort(key=lambda x: x[0], reverse=True)
        score, text, color = omens[0]

        # THE GRADIENT
        # Silence the 40-45% warnings. Only speak if it matters.
        if score >= 80:
             return f"{color}🔮 OMEN ({score}%): {text}{Prisma.RST}"
        elif score >= 50:
             # Force Caution color (Yellow) for mid-tier threats
             return f"{Prisma.YEL}⚠️ CAUTION ({score}%): {text}{Prisma.RST}"

        return None

# --- PHOTOSYNTHESIS & APEIROGON & DYNAMICS ---

class LichenSymbiont:
    def photosynthesize(self, phys):
        # ANCESTRAL GRAFT: Metabolizing Refusal
        sugar = 0
        msgs = []

        # 1. Standard Photosynthesis (Sunlight)
        light = phys["counts"].get("photo", 0)
        drag = phys["narrative_drag"]
        if light > 0 and drag < 3.0:
            s = light * 2
            sugar += s
            msgs.append(f"{Prisma.GRN}☀️ PHOTOSYNTHESIS (+{s}){Prisma.RST}")

        # 2. Salvage Metabolism (eating the tension)
        # "Metabolizing refusal into structural tension" [cite: 9]
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
            # Manual injection of knowledge
            if len(parts) >= 3:
                word = parts[1]
                cat = parts[2].lower()
                valid_cats = ["heavy", "kinetic", "abstract", "photo", "aerobic", "thermal", "cryo"]
                if cat in valid_cats:
                    TheLexicon.teach(word, cat)
                    print(f"{Prisma.CYN}🧠 NEUROPLASTICITY: Learned '{word}' is {cat.upper()}.{Prisma.RST}")
                else:
                    print(f"{Prisma.RED}ERROR: Invalid category. Use: {', '.join(valid_cats)}{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}Usage: /teach [word] [category]{Prisma.RST}")

        elif cmd == "/seed":
            if len(parts) > 1:
                self.eng.mem.ingest(parts[1])
            else:
                print(f"{Prisma.YEL}Usage: /seed [filename]{Prisma.RST}")

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
    def check_vitals(cls, phys, stamina):
        if stamina <= 0: return "HYPOTHERMIA", cls.AUTOPSY_REPORTS["HYPOTHERMIA"][0], True
        if phys["narrative_drag"] > 8.0: return "GRAVITATIONAL_COLLAPSE", cls.AUTOPSY_REPORTS["GRAVITATIONAL_COLLAPSE"][0], True
        if phys["vector"]["ENT"] >= 1.0 and phys["vector"]["TEX"] == 0: return "VACUUM_EXPOSURE", cls.AUTOPSY_REPORTS["VACUUM_EXPOSURE"][0], True
        if phys["voltage"] < -8.0: return "TOXIC_SHOCK", cls.AUTOPSY_REPORTS["TOXIC_SHOCK"][0], True
        if phys["voltage"] > 12.0: return "THERMAL_DISSOLUTION", cls.AUTOPSY_REPORTS["THERMAL_DISSOLUTION"][0], True
        return None, None, False

    @classmethod
    def pronounce_dead(cls, cause, msg):
        print(f"\n{Prisma.RED}*** CHRONO-AUTOPSY ***{Prisma.RST} {cause}\n{Prisma.WHT}\"{msg}\"{Prisma.RST}\n{Prisma.GRY}----------------------------------------{Prisma.RST}\n{Prisma.RED}NARRATIVE TERMINATED.{Prisma.RST}")

class DreamEngine:
    """
    Subconscious filtering enabled. Dreams now traverse the graph edges
    rather than picking random nodes.
    """
    PROMPTS = [
        "The {A} is dreaming of the {B}. Why?",
        "Bridge the gap between {A} and {B}.",
        "I see {A} inside the {B}. Explain.",
        "The shadow of {A} falls on {B}.",
        "{A} + {B} = ?"
    ]

    def hallucinate(self, graph):
        if len(graph) < 2: return None

        # Start from random node
        keys = list(graph.keys())
        start = random.choice(keys)

        edges = graph[start].get("edges", {})
        if not edges: return None

        # Follow strongest connection (The Mycelial Path)
        # Filter out toxins from dream pathways
        valid_edges = {k: v for k, v in edges.items() if k not in BoneConfig.TOXIN_MAP}

        if not valid_edges: return None # Do not dream of poison

        end = max(valid_edges, key=valid_edges.get)

        template = random.choice(self.PROMPTS)
        return template.format(A=start.upper(), B=end.upper())

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
        self.dreamer = DreamEngine()

        # CIRCADIAN SYSTEMS (Inheritance Paradox Fix)
        # If parent session was damaged (<50), apply genetic repair (+30)
        parent_hp = self.mem.session_health
        if parent_hp is not None:
            if parent_hp < 50:
                print(f"{Prisma.CYN}[GENETICS]: Ancestral trauma detected. Applying genetic repair (+30 HP).{Prisma.RST}")
                self.health = min(BoneConfig.MAX_HEALTH, parent_hp + 30)
            else:
                self.health = parent_hp
        else:
            self.health = BoneConfig.MAX_HEALTH

        self.stamina = self.mem.session_stamina if self.mem.session_stamina is not None else BoneConfig.MAX_STAMINA
        self.coma_turns = 0

        if self.mem.session_stamina: self.battery.current_charge = 5.0
        self.tick_count = 0
        self.last_context = None
        self.lazarus_cooldown = 0

    def pollinate(self, vector, current_words):
        # (Fault 3 Fix): Rewritten to use self.mem.graph
        if self.stamina < 30 or not self.mem.graph: return None

        # Find strongly connected nodes to current input
        candidates = []
        for w in current_words:
            if w in self.mem.graph:
                edges = self.mem.graph[w]["edges"]
                if edges:
                    # Follow strongest connection
                    best = max(edges, key=edges.get)
                    if best not in current_words:
                        # Decay calculation? For now just raw strength
                        strength = edges[best]
                        candidates.append((best, strength))

        if candidates:
            # Sort by connection strength
            candidates.sort(key=lambda x: x[1], reverse=True)
            target, strength = candidates[0]

            return f"{Prisma.MAG}🍄 MYCELIAL SPORE: '{target}' (strength: {strength}){Prisma.RST}"

        return None

    def process(self, text):
        if self.cmd.execute(text): return

        # 1. LUCID COMA
        if self.coma_turns > 0:
            self.coma_turns -= 1
            self.stamina = min(BoneConfig.MAX_STAMINA, self.stamina + 15)

            # Maintain the Timeline (Prevent Amnesia)
            self.tick_count += 1
            self.mem.bury(m["clean_words"], self.tick_count)

            # --- NEW DECAY PROTOCOL ---
            # Apply decay every turn. Rate is small (0.05) so strong ideas last a long time.
            decay_msg = self.mem.decay_synapses(entropy_rate=0.05)
            if decay_msg:
                # We log this to the battery log so we can see the brain cleaning itself
                battery_log.append(f"{Prisma.GRY}🍂 {decay_msg}{Prisma.RST}")
            # --------------------------

            is_bored = self.chronos.tick(m["physics"], self.mem.session_id)

            # The Subconscious Never Sleeps
            if random.random() < 0.3:
                dream = self.dreamer.hallucinate(self.mem.graph)
                if dream:
                    print(f"\n{Prisma.GRY}[ COMA DREAM ]{'='*30}{Prisma.RST}")
                    print(f"{Prisma.MAG}☁️ {dream}{Prisma.RST}")

            print(f"{Prisma.GRY}System regenerating... ({self.coma_turns} turns remain){Prisma.RST}")
            return # Exit processing, but keep the ghost alive

        # 2. PHYSICS
        self.tick_count += 1
        m = self.phys.analyze(text)
        self.dynamics.commit(m["physics"]["voltage"])
        ta_vel = self.dynamics.get_velocity()

        # 3. BATTERY
        charged = self.battery.absorb(m["physics"]["voltage"])
        battery_log = []
        if charged > 0: battery_log.append(f"{Prisma.YEL}⚡ PARADOX CAPTURED (+{round(charged, 1)}){Prisma.RST}")

        # 4. METABOLISM (Eat First, Burn Later)
        # Photosynthesis (Gain)
        sugar, lichen_msg = self.lichen.photosynthesize(m["physics"])
        self.stamina = min(BoneConfig.MAX_STAMINA, self.stamina + sugar)

        # Calculate Cost (Do not check starvation yet)
        stamina_cost = 2.0
        if m["physics"]["narrative_drag"] > 3.0: stamina_cost += 3.0
        if m["physics"]["voltage"] > 8.0: stamina_cost += 5.0

        # Apply Cost FIRST (The Burn)
        self.stamina = max(0, self.stamina - stamina_cost)

        # BATTERY DISCHARGE (The Safety Net)
        # Now we calculate deficit based on the TRUE post-exertion state.
        if self.stamina < 20 and self.battery.current_charge > 0.5:
            target_buffer = 30.0
            deficit = target_buffer - self.stamina

            # Dynamic Efficiency: Damaged systems struggle to process Paradox
            efficiency = 2.0 # Base: 1 Charge = 2 Stamina
            if self.health < 50: efficiency = 1.0 # Trauma Tax

            needed_charge = deficit / efficiency
            drained = self.battery.discharge(needed_charge)

            if drained > 0:
                recovered_stamina = drained * efficiency
                self.stamina += recovered_stamina
                battery_log.append(f"{Prisma.YEL}⚡ EMERGENCY POWER (-{round(drained,1)} Charge -> +{round(recovered_stamina,1)} STM){Prisma.RST}")

        # HEALTH IMPACT & COMA
        health_impact = 0
        if m["physics"]["counts"].get("toxin", 0) > 0:
            health_impact -= (5 * m["physics"]["counts"]["toxin"])
            battery_log.append(f"{Prisma.RED}☣️ TOXIN DAMAGE (-{5 * m['physics']['counts']['toxin']} HP){Prisma.RST}")

        # THE CORONER (Diagnostic Only)
        cause, autopsy_msg, is_dead = NarrativeCoroner.check_vitals(m["physics"], self.stamina)

        lazarus_msg = None
        if is_dead:
             lazarus_msg = f"{Prisma.RED}💀 CRITICAL CONDITION: {autopsy_msg}{Prisma.RST}"

        if self.stamina <= 0:
            health_impact -= 10
            battery_log.append(f"{Prisma.RED}😫 EXHAUSTION DAMAGE (-10 HP){Prisma.RST}")
            self.stamina = 0

        self.health = min(BoneConfig.MAX_HEALTH, self.health + health_impact)

        if self.health <= 0:
            self.coma_turns = BoneConfig.COMA_DURATION
            self.health = 20
            battery_log.append(f"{Prisma.RED}💤 SYSTEM COLLAPSE. ENTERING COMA STATE.{Prisma.RST}")

        # MEMORY & RADIO
        self.mem.bury(m["clean_words"], self.tick_count)
        is_bored = self.chronos.tick(m["physics"], self.mem.session_id)

        # DREAM ENGINE TRIGGER
        dream_msg = None
        if is_bored:
            dream_msg = self.dreamer.hallucinate(self.mem.graph)

        clean_text = text
        ops = []

        # --- CONTEXTUAL IMMUNITY (The High Voltage Exception) ---
        # If the narrative is electric (> 8.0v), we suspend the immune system.
        # "The lightning needs a path, even if it is a dirty one."
        if m["physics"]["voltage"] > 8.0:
            ops.append(f"{Prisma.YEL}⚡ HIGH VOLTAGE OVERRIDE: Immunity Granted.{Prisma.RST}")

        else:
            # STANDARD IMMUNE RESPONSE
            # Voltage is low/normal, so we must enforce hygiene.
            for toxin, (weight, replacement) in BoneConfig.TOXIN_MAP.items():
                 pattern = re.compile(re.escape(toxin), re.IGNORECASE)
                 if pattern.search(clean_text):
                     clean_text = pattern.sub(replacement, clean_text)
                     ops.append(f"'{toxin}' -> '{replacement}'")

        station_data = self.radio.tune_in(m["physics"], m["physics"]["vector"], (m["physics"]["narrative_drag"] > 3.0), self.stamina)
        strat, reason, title = self.wise.architect(m, station_data, is_bored)
        omens = TheOracle.triage(m["physics"], self.stamina, self.battery.current_charge)
        spore_msg = self.pollinate(m["physics"]["vector"], m["clean_words"])

        self._render(m, lichen_msg, strat, reason, title, ops, station_data, None, None, clean_text, len(ops)>0, battery_log, lazarus_msg, spore_msg, ta_vel, [omens] if omens else [], dream_msg)

    def _render(self, m, lichen_msg, strat, reason, title, ops, station, starve_msg, ghost_msg, clean_text, did_surgery, battery_log, lazarus_msg, spore_msg=None, ta_val=0.0, omens=[], dream_msg=None):
        p = m["physics"]

        # --- 1. TA VECTOR LOGIC ---
        ta_symbol = "►" # Stable
        ta_color = Prisma.GRY

        # Is the narrative moving?
        if ta_val > 1.5:
            ta_symbol = "▲" # Accelerating
            # Check Quality of Speed
            if p['voltage'] < -2.0: ta_color = Prisma.RED # CRASH COURSE (Fast + Toxic)
            elif p['voltage'] > 2.0: ta_color = Prisma.CYN # SURFING (Fast + Electric)
            else: ta_color = Prisma.GRN # MOMENTUM (Fast + Stable)

        elif ta_val < -1.5:
            ta_symbol = "▼" # Decelerating
            # Check Nature of Drag
            if p['narrative_drag'] > 5.0: ta_color = Prisma.RED # STALLING (Slow + Heavy)
            else: ta_color = Prisma.YEL # BRAKING (Slow + Controlled)

        ta_display = f"{ta_color}{ta_symbol}{abs(ta_val)}{Prisma.RST}"

        # --- 2. THE FLIGHT DECK ---
        print(f"\n{Prisma.GRY}[ {Prisma.WHT}{title}{Prisma.GRY} | {Prisma.CYN}{strat}{Prisma.GRY} ]{'='*35}{Prisma.RST}")

        hp_p = int((self.stamina / 50.0) * 10) # Assuming Max Stamina is 50
        hp_p = max(0, min(10, hp_p))
        hp_bar = f"{Prisma.GRN}{'|'*hp_p}{Prisma.GRY}{'.'*(10-hp_p)}{Prisma.RST}"

        batt_bar = self.battery.get_readout()

        volt_c = f"{Prisma.MAG}{p['voltage']}{Prisma.RST}" if p['voltage'] > 5 else f"{Prisma.CYN}{p['voltage']}{Prisma.RST}"
        drag_c = Prisma.wrap(p['narrative_drag'], 3.0)

        # STATE VISUALIZER
        sym_state = p.get("symbolic_state", "NEUTRAL")
        state_color = Prisma.GRY
        if sym_state == "SALVAGE": state_color = Prisma.CYN
        elif sym_state == "FATIGUE": state_color = Prisma.RED
        elif sym_state == "GOLD": state_color = Prisma.YEL

        state_display = f"{state_color}[{sym_state}]{Prisma.RST}"

        if station:
            sig = f"{station['color']}{station['name']}{Prisma.RST}"
        else:
            sig = f"{Prisma.GRY}STATIC{Prisma.RST}"

        print(f" {Prisma.WHT}STM:{Prisma.RST} [{hp_bar}] {batt_bar}")
        print(f" {Prisma.WHT}DRAG:{Prisma.RST} {drag_c}  {Prisma.WHT}Ta:{Prisma.RST} {ta_display}  {Prisma.WHT}VOLT:{Prisma.RST} {volt_c}  {Prisma.WHT}STATE:{Prisma.RST} {state_display}")
        print(f" {Prisma.WHT}SIG:{Prisma.RST} {sig}")

        if station: print(f"\n {station['color']}► {station['msg']}{Prisma.RST}")
        print(f" {Prisma.GRY}└─ {reason}{Prisma.RST}")

        if dream_msg: print(f"\n    {Prisma.MAG}☁️ DREAM STATE: {dream_msg}{Prisma.RST}")

        if lazarus_msg: print(f"\n    {lazarus_msg}")
        if m.get("kintsugi_msg"): print(f"\n    {m['kintsugi_msg']}")
        if omens:
            for o in omens: print(f"    {o}")
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
    print(f"{Prisma.GRN}>>> BONEAMANITA v4.3 'THE SALVAGE OPERATION' ONLINE.{Prisma.RST}")
    print(f"{Prisma.GRY}System: Circadian Rhythms Active. Dream Engine Filtered.{Prisma.RST}")

    try:
        while True:
            try:
                u = input(f"{Prisma.WHT}>{Prisma.RST} ")
            except EOFError:
                # Handles unexpected EOF (like Ctrl+D) cleanly
                break

            # Check for exit commands explicitly
            if u.lower() in ["exit", "quit", "/exit"]:
                print(f"{Prisma.YEL}Initiating voluntary shutdown...{Prisma.RST}")
                break

            # The Process
            eng.process(u)

    except KeyboardInterrupt:
        # SAVE ON FORCE QUIT (Ctrl+C)
        print(f"\n{Prisma.YEL}⚠️ INTERRUPT SIGNAL DETECTED.{Prisma.RST}")

    except Exception as e:
        # CATCH ALL OTHER CRASHES (The Black Box Recorder)
        print(f"\n{Prisma.RED}💥 CRITICAL RUNTIME FAILURE: {e}{Prisma.RST}")
        # Optional: Print traceback if you want to debug the corpse
        # import traceback; traceback.print_exc()

    finally:
        # THIS RUNS NO MATTER WHAT
        print(f"{Prisma.CYN}[PRESERVATION]: Writing neural pathways to disk...{Prisma.RST}")
        saved_file = eng.mem.save(health=eng.health, stamina=eng.stamina)
        if saved_file:
            print(f"{Prisma.GRN}>>> MEMORY SECURED: {saved_file}{Prisma.RST}")
        else:
            print(f"{Prisma.RED}>>> MEMORY WRITE FAILED.{Prisma.RST}")
        print("Terminated.")
