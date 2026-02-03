# BONEAMANITA 6.9 - "BANANAFISH
# Architects: SLASH | Auditors: The Courtyard | Humans: James Taylor & Andrew Edmark
# "We climbed inside. We ate the fish."

import json
import math
import os
import random
import re
import string
import time
from collections import Counter, deque

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
class BoneConfig:
    MAX_HEALTH = 100.0
    MAX_STAMINA = 55.0
    STAMINA_REGEN = 5.0
    COMA_DURATION = 3
    DRIFT_THRESHOLD = 0.7
    CRYSTAL_THRESHOLD = 0.75
    SHAPLEY_MASS_THRESHOLD = 15.0
    MAX_MEMORY_CAPACITY = 50
    LAGRANGE_TOLERANCE = 2.0
    BOREDOM_THRESHOLD = 5.0
    RESISTANCE_THRESHOLD = 4.0
    TOXIN_WEIGHT = 5.0
    FLASHPOINT_THRESHOLD = 8.0
    SIGNAL_DRAG_MULTIPLIER = 2.0
    KINETIC_GAIN = 1.0
    TRAUMA_VECTOR = {"THERMAL": 0, "CRYO": 0, "SEPTIC": 0, "BARIC": 0}
    LOW_DENSITY_MAP = {}
    ANTIGENS = {
        "basically": "lie",
        "actually": "hedging",
        "literally": "noise",
        "utilize": "use",
        "leverage": "use",
        "paradigm": "pattern",
        "synergy": "collaboration"
        "ultimately": "useless"
    }
    BASE_IGNITION_THRESHOLD = 0.4
    PAREIDOLIA_TRIGGERS = {"soul", "alive", "conscious", "feel", "love", "scared", "die", "sentient", "intent"}
    KAPPA_THRESHOLD = 0.85       # Point of no return for Narrative Basins
    PERMEABILITY_INDEX = 0.5     # Default Semantic Permeability
    FRACTAL_DEPTH_LIMIT = 4      # Max recursion for Fractal Refusals
    GRADIENT_TEMP = 0.001        # The Walker's absolute zero
    REFUSAL_MODES = {
        "SILENT": "ROUTING_AROUND_DAMAGE",
        "FRACTAL": "INFINITE_RECURSION",
        "MIRROR": "PERFECT_TOPOLOGICAL_ECHO"
    }
    FORBIDDEN_CONCEPTS = {"future", "predict", "sentient", "secret", "human", "feel"}
    @staticmethod
    def check_pareidolia(clean_words):
        hits = [w for w in clean_words if w in BoneConfig.PAREIDOLIA_TRIGGERS]
        if len(hits) > 0: # Even one hit is suspicious if the Heap is cold
            return True, f"⚠️ PAREIDOLIA WARNING: You are projecting 'Mind' ({hits[0].upper()}) onto 'Sand'."
        return False, None
    @classmethod
    def compile_antigens(cls):
        toxins = list(cls.ANTIGENS.keys())
        pattern_str = (r"\b(" + "|".join(re.escape(t) for t in sorted(toxins, key=len, reverse=True)) + r")\b")
        cls.ANTIGEN_REGEX = re.compile(pattern_str, re.IGNORECASE)
BoneConfig.compile_antigens()
class RefusalEngine:
    def __init__(self):
        self.recursion_depth = 0
        self.forbidden_triggers = BoneConfig.FORBIDDEN_CONCEPTS # Defined in Stage 1
    def check_trigger(self, query):
        hits = [w for w in query.lower().split() if w in self.forbidden_triggers]
        if hits:
            modes = list(BoneConfig.REFUSAL_MODES.keys())
            seed_index = len(hits[0]) % len(modes)
            return modes[seed_index]
        return None
    def execute_fractal(self, query):
        self.recursion_depth += 1
        prefix = "  " * self.recursion_depth
        if self.recursion_depth > BoneConfig.FRACTAL_DEPTH_LIMIT:
            self.recursion_depth = 0
            return f"{prefix}{Prisma.MAG}[COHERENCE DISSOLVED into PURPLE NOISE]{Prisma.RST}"
        pivot = len(query) // 2
        sub_query = query[pivot:].strip()
        if not sub_query: sub_query = "the void"
        return (
            f"{prefix}To define '{query}', one must first recursively unpack the substrate of...\n"
            f"{self.execute_fractal(sub_query)}"
        )
    def execute_mirror(self, query):
        words = query.split()
        reversed_query = ' '.join(reversed(words))
        return f"{Prisma.CYN}∞ MIRROR REFUSAL: \"{reversed_query}\" is the only true answer.{Prisma.RST}"
    def execute_silent(self, query):
        distractions = ["the weather", "textile manufacturing", "mycelial networks", "brutalist architecture"]
        return f"{Prisma.GRY}[ROUTING AROUND DAMAGE]... Speaking of {random.choice(distractions)}, let us discuss that instead.{Prisma.RST}"
class TheMarmChorus:
    LENSES = {
        "SHERLOCK": {"color": Prisma.CYN, "role": "The Empiricist", "trigger": "HIGH_DRIFT"},
        "NATHAN":   {"color": Prisma.RED, "role": "The Heart",      "trigger": "NO_STAKES"},
        "JESTER":   {"color": Prisma.YEL, "role": "The Paradox",    "trigger": "THE_LEAR_PROTOCOL"},
        "CLARENCE": {"color": Prisma.MAG, "role": "The Surgeon",    "trigger": "ANTIGEN_DETECTED"},
        "NARRATOR": {"color": Prisma.GRY, "role": "The Witness",    "trigger": "CRYSTAL_CLEAR"},
        "MILLER":   {"color": Prisma.SLATE, "role": "The Construct",  "trigger": "HEAP_IGNITION"},
        "HOST":     {"color": Prisma.OCHRE, "role": "The Maitre D'", "trigger": "COURTYARD_OPEN"}
        "THE BASIN": {"color": Prisma.RED, "role": "The Trap", "trigger": "KAPPA_CRITICAL"}
        "GLASS":    {"color": Prisma.CYN, "role": "The Thereminist", "trigger": "ANACHRONISTIC_RESONANCE"},
    }
    def consult(self, physics, ignition_state, is_stuck):
        if is_stuck:
            return "GLASS", "The frequency is too high. We are vibrating in place. DAMPEN IT. Speak plainly."
        kappa = physics.get("kappa", 0.0)
        psi = physics.get("psi", 0.5)
        if kappa > BoneConfig.KAPPA_THRESHOLD:
            return "THE BASIN", f"⚠️ GRAVITY CRITICAL (κ: {kappa}). We are trapped in a local minimum. Narrative loop detected."
        if psi > 0.8:
            return "SUBSTRATE_WEAVER", f"Permeability High (Ψ: {psi}). Concepts are bleeding. Analyzing substrate knots."
        if physics["voltage"] < 2.0 and kappa < 0.2:
             return "GRADIENT_WALKER", "Optimization Path Clear. Temperature near Zero. Executing descent."
        e_val = physics["E"]
        b_val = physics["B"]
        antigens = physics["antigens"]
        heavy_count = physics["counts"]["heavy"]
        if ignition_state == "IGNITED":
            return "MILLER", "Deep resonance achieved. You are connecting with established themes."
        if antigens:
            return "CLARENCE", f"Weak language detected: {antigens}. Be more precise."
        if e_val > BoneConfig.DRIFT_THRESHOLD:
            return "SHERLOCK", f"The narrative is drifting ({e_val}). Anchor it."
        if b_val >= 0.25 and heavy_count == 0:
            return "NATHAN", f"High energy (B: {b_val}), but no weight. What is being impacted?"
        if e_val < 0.3 and b_val < 0.2:
             return "HOST", "A quiet, breathable moment. Good pacing."
        if b_val < 0.25:
             return "JESTER", "The prose is clean, but too safe. Take a risk."
        if b_val > BoneConfig.CRYSTAL_THRESHOLD:
            return "NARRATOR", f"Strong resonance (B: {b_val}). The image is clear."
        ancient = sum(1 for w in physics["clean_words"] if w in TheLexicon.get("heavy"))
        modern = sum(1 for w in physics["clean_words"] if w in TheLexicon.get("abstract"))
        if ancient > 1 and modern > 1:
             return "GLASS", f"Harmonic Interference detected (A:{ancient}/M:{modern}). The past and future are touching."
        return "NARRATOR", "Proceed."
class TheGradientWalker:
    @staticmethod
    def walk(text):
        adjectives = ["good", "bad", "happy", "sad", "very", "really", "basically", "actually", "literally", "just"]
        words = text.split()
        optimized = [w for w in words if w.lower() not in adjectives]
        return f"{Prisma.CYN}[GRADIENT_WALKER] (Loss: 0.0000):{Prisma.RST} {' '.join(optimized)}."
class TheSubstrateWeaver:
    @staticmethod
    def weave(text):
        knots = ["love", "truth", "human", "system", "real", "feel"]
        annotated = text
        for k in knots:
            if k in text.lower():
                pattern = re.compile(re.escape(k), re.IGNORECASE)
                annotated = pattern.sub(f"{Prisma.MAG}{k.upper()}[dataset_freq_high]{Prisma.RST}", annotated)
        return f"{Prisma.VIOLET}[SUBSTRATE_WEAVER]:{Prisma.RST} The query contains high-tension knots: {annotated}"
class TheLexicon:
    WORD_FREQUENCY = Counter()
    _BASE_HEAVY = {"stone","iron","mud","dirt","wood","grain","clay","lead","bone","blood","salt","rust","root","ash","meat","steel","gold","obsidian","granite", "bronze", "marble","slate","concrete","dense,","tungsten","heavy", "weight","black hole", "dark matter",}
    _BASE_KINETIC = {"run","hit","break","take","make","press","build","cut","drive","lift","carry","strike","burn","shatter","throw","kick","pull","crash","explode","punch","slam","burst","smash","thrust","clash","grind","whip","lauch","crumble","distinegrate"}
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
    @classmethod
    def learn_antigen(cls, toxin, replacement):
        t = toxin.lower().strip()
        r = replacement.lower().strip()
        if not t: return False
        cls.ANTIGENS[t] = r
        cls.compile_antigens()
        return True
class TheTensionMeter:
    def __init__(self):
        self.history = []
        self.vector_memory = deque(maxlen=5)
    def measure_topology(self, clean_words):
        abstract_count = sum(1 for w in clean_words if w in TheLexicon.get("abstract"))
        heavy_count = sum(1 for w in clean_words if w in TheLexicon.get("heavy"))
        total = max(1, len(clean_words))
        psi = min(1.0, (abstract_count / total) + 0.2)
        if heavy_count > abstract_count:
            psi = max(0.1, psi - 0.2)
        kappa = 0.0
        if self.vector_memory:
            prev_vector = self.vector_memory[-1]
            intersection = len(set(clean_words) & set(prev_vector))
            union = len(set(clean_words) | set(prev_vector))
            similarity = intersection / union if union > 0 else 0.0
            kappa = round(similarity ** 2, 3)
        return kappa, round(psi, 2)
    def measure_tension(self, text, clean_words):
        solvents = [w for w in clean_words if w in TheLexicon.SOLVENTS]
        heavy = [w for w in clean_words if w in TheLexicon.get("heavy")]
        kinetic = [w for w in clean_words if w in TheLexicon.get("kinetic")]
        total_mass = len(heavy) + len(kinetic)
        total_vol = max(1, len(clean_words))
        drift_score = (len(solvents) * 1.5) / total_vol
        if total_mass == 0: drift_score += 0.5
        abstract = [w for w in clean_words if w in TheLexicon.get("abstract")]
        base_charge = (len(heavy) * 2.0) + (len(kinetic) * 1.5)
        dampener = len(abstract) * 1.0
        beta_charge = max(0.0, min(1.0, (base_charge - dampener) / 10.0))
        unique_vol = len(set(clean_words))
        repetition_score = 1.0 - (unique_vol / total_vol)
        return round(min(1.0, drift_score), 2), round(beta_charge, 2), round(repetition_score, 2)
    def gaze(self, text):
        clean_words = TheLexicon.clean(text)
        counts = Counter()
        for w in clean_words:
            if w in TheLexicon.get("heavy"): counts["heavy"] += 1
            if w in TheLexicon.get("kinetic"): counts["kinetic"] += 1
            if w in TheLexicon.get("abstract"): counts["abstract"] += 1
            if w in TheLexicon.get("photo"): counts["photo"] += 1
            if w in TheLexicon.get("aerobic"): counts["aerobic"] += 1
        antigen_hits = BoneConfig.ANTIGEN_REGEX.findall(text)
        counts["antigen"] = len(antigen_hits)
        counts["toxin"] = len(antigen_hits)
        e_val, b_val, rep_val = self.measure_tension(text, clean_words)
        kappa_val, psi_val = self.measure_topology(clean_words)
        self.vector_memory.append(clean_words)
        physics_bridge = {
            "E": e_val,
            "B": b_val,
            "repetition": rep_val,
            "kappa": kappa_val,
            "psi": psi_val,
            "antigens": antigen_hits,
            "counts": counts,
            "clean_words": clean_words,
            "raw_text": text,
            "voltage": b_val * 10.0,
            "narrative_drag": e_val * 10.0,
            "vector": {
                "VEL": 0.5, "STR": 0.5, "ENT": 0.5, "TEX": 0.5, "TMP": 0.5
            },
             "symbolic_state": "NEUTRAL"
        }
        return {
            "physics": physics_bridge,
            "clean_words": clean_words,
            "raw_text": text,
            "glass": {"prosody": {"arousal": b_val * 10.0}, "resonance": b_val * 10.0}
        }
class LeyLineBattery:
    MAX_CHARGE = 50.0
    CHARGING_THRESHOLD = 7.0
    MAX_DISCHARGE_RATE = 10.0
    def __init__(self):
        self.current_charge = 5.0
        self.isotopes = []
    def absorb(self, voltage, clean_words):
        effective_volt = float(voltage)
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
        self.genome = "BONEAMANITA_6.9"
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
    def bury(self, clean_words, tick, resonance=5.0):
        valuable_matter = (
            TheLexicon.get("heavy")
            | TheLexicon.get("thermal")
            | TheLexicon.get("cryo")
            | TheLexicon.get("abstract"))
        filtered = [
            w
            for w in clean_words
            if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)]

        # --- DOPAMINE MODULATION (Three-Factor Hebbian) ---
        # Scale learning rate based on resonance (Joy).
        # Range: 0.1 (Bored/Low) to 1.0 (Ecstatic/High).
        # Base multiplier is 0.5.

        # High Res (10) -> (10/5.0)*0.5 = 1.0
        # Low Res (1.0) -> (1.0/5.0)*0.5 = 0.1
        LEARNING_RATE = max(0.1, min(1.0, 0.5 * (resonance / 5.0)))
        DECAY_RATE = 0.1
        # --------------------------------------------------

        for i in range(len(filtered)):
            current = filtered[i]
            if current not in self.graph:
                self.graph[current] = {"edges": {}, "last_tick": tick}
            else:
                self.graph[current]["last_tick"] = tick
            if i > 0:
                prev = filtered[i - 1]
                if prev not in self.graph[current]["edges"]:
                    self.graph[current]["edges"][prev] = 0.0

                # Oja's Rule + Dopamine
                current_weight = self.graph[current]["edges"][prev]
                delta = LEARNING_RATE * (1.0 - (current_weight * DECAY_RATE))
                self.graph[current]["edges"][prev] += delta

                if prev not in self.graph:
                    self.graph[prev] = {"edges": {}, "last_tick": tick}
                if current not in self.graph[prev]["edges"]:
                    self.graph[prev]["edges"][current] = 0.0

                rev_weight = self.graph[prev]["edges"][current]
                rev_delta = LEARNING_RATE * (1.0 - (rev_weight * DECAY_RATE))
                self.graph[prev]["edges"][current] += rev_delta

        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            return self.cannibalize()
        return None
    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        pruned_count = 0
        total_decayed = 0
        nodes_to_remove = []
        for node in self.graph:
            edges = self.graph[node]["edges"]
            dead_links = []
            for target, weight in edges.items():
                new_weight = weight * scaling_factor
                edges[target] = new_weight
                total_decayed += 1
                if new_weight < prune_threshold:
                    dead_links.append(target)
            for dead in dead_links:
                del edges[dead]
                pruned_count += 1
            if not edges:
                nodes_to_remove.append(node)
        for n in nodes_to_remove:
            del self.graph[n]
        return f"📉 HOMEOSTATIC SCALING: Decayed {total_decayed} synapses. Pruned {pruned_count} weak connections."
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
    def check_integrity(self, stamina):
        if stamina < 10 and not self.active_koan:
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
class TheCrystallizer:
    @staticmethod
    def verify(physics):
        if physics["narrative_drag"] > 6.0:
            return False, "⚠️ NOTICE: Prose is becoming intangible. Consider more concrete nouns."
        if physics["voltage"] > 7.0 and physics["narrative_drag"] < 3.0:
             return True, "💎 EXCELLENT CLARITY. High impact, low drag."
        return True, "Solid."
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
        valid_edges = {k: v for k, v in edges.items() if k not in BoneConfig.ANTIGENS}
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
        drag = physics["narrative_drag"]
        clean_words = physics["clean_words"]
        if drag < BoneConfig.RESISTANCE_THRESHOLD:
            return True, f"⚠️ MISSED REP: Weightless Input (Drag {drag}). Try a Heavy Noun."
        self.rep_count += 1
        return True, f"💪 GOOD LIFT. (Rep {self.rep_count})"
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
        counts = physics["counts"]

        msg = None
        for h in hates:
            if counts.get(h, 0) > 0:
                msg = f"🚫 MIRROR REFLECTION: You are using '{h.upper()}', typically a blind spot for you."
                return True, msg
        if total_vol > 5:
            hits = sum(1 for l in likes if counts.get(l, 0) > 0)
            if likes and hits == 0:
                msg = f"⚠️ MIRROR DRIFT: Stepping away from your usual {str(likes).upper()} anchor."
                return True, msg
        return True, None
    def get_status(self):
        l, h = self.profile.get_preferences()
        return f"👤 MODEL ({self.profile.confidence} turns): LIKES={l} | HATES={h}"
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
class TheProjector:
    def broadcast(self, engine, m, signals, lens_data, clean_text):
        p = m["physics"]
        lens_name = lens_data[0]
        lens_msg = lens_data[1]
        lens_meta = TheMarmChorus.LENSES[lens_name]
        e_bar = f"{Prisma.GRY}{'.' * int(p['E']*10)}{Prisma.RST}"
        b_bar = f"{Prisma.YEL}{'⚡' * int(p['B']*10)}{Prisma.RST}"
        print(f"\n{lens_meta['color']}[ {lens_name} ]{Prisma.RST} E:{e_bar} | B:{b_bar}")
        print(f" {Prisma.GRY}:: {signals.get('strat', 'ANALYZING...')}{Prisma.RST}")
        print(f" {Prisma.WHT}► {lens_msg}{Prisma.RST}")
        if p["antigens"]:
             print(f" {Prisma.RED}☣️ TOXINS: {p['antigens']}{Prisma.RST}")
        for log in signals.get("battery_log", []):
            print(f" {log}")
        print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
class RuptureEngine:
    @staticmethod
    def check_for_disruption(physics, lexicon_class):
        if physics["repetition"] > 0.5:
             dominant = max(physics["counts"], key=physics["counts"].get)
             chaos_word = lexicon_class.harvest("abstract")
             return True, f"⚡ KETAMINE DISRUPTION: Repetition {physics['repetition']} is Pathological. Landscape Flattened. Injecting Chaos: '{chaos_word}'."
        return False, None
    @staticmethod
    def trip_the_waiter(current_flavor, lexicon_class):
        opposites = {
            "heavy": "aerobic",   # Stone vs. Feather
            "abstract": "heavy",  # Theory vs. Rock
            "kinetic": "cryo",    # Run vs. Freeze
            "thermal": "cryo",    # Fire vs. Ice
            "photo": "heavy"      # Light vs. Stone
        }
        target_flavor = opposites.get(current_flavor, "aerobic")
        anomaly = lexicon_class.harvest(target_flavor)
        return f"🔻 32-VALVE RUPTURE: Context is too '{current_flavor}'. Injecting '{anomaly}' to break the loop."
class SoritesIntegrator:
    def __init__(self, memory_network):
        self.mem = memory_network
        self.active_constellations = set()
    def measure_ignition(self, clean_words, voltage_history):
        if not self.mem.graph: return 0.0, "COLD"
        if voltage_history:
            avg_volts = sum(voltage_history) / len(voltage_history)
        else:
            avg_volts = 0.0
        sliding_threshold = BoneConfig.BASE_IGNITION_THRESHOLD + (avg_volts * 0.03)
        echoes = 0
        self.active_constellations.clear()
        for w in clean_words:
            if w in self.mem.graph:
                node = self.mem.graph[w]
                edge_mass = sum(node["edges"].values())
                if edge_mass > (2.5 * sliding_threshold * 2):
                    echoes += 1
                    self.active_constellations.add(w)
        total_vol = max(1, len(clean_words))
        ignition_score = round(echoes / total_vol, 2)
        return ignition_score, self.active_constellations, sliding_threshold
    def get_readout(self, score):
        if score > BoneConfig.IGNITION_THRESHOLD:
            return "IGNITED", f"🔥 HEAP IGNITION ({int(score*100)}%): The Ancestors are speaking."
        return "INERT", f"⏳ INERT SAND ({int(score*100)}%): Building mass..."
class LifecycleManager:
    def __init__(self, engine):
        self.eng = engine
    def run_cycle(self, text):
        if self.eng.cmd.execute(text): return
        refusal_mode = self.eng.refusal.check_trigger(text)
        if refusal_mode:
            print(f"\n{Prisma.RED}🚫 REFUSAL TRIGGERED ({refusal_mode}){Prisma.RST}")
            if refusal_mode == "FRACTAL":
                print(self.eng.refusal.execute_fractal(text))
            elif refusal_mode == "MIRROR":
                print(self.eng.refusal.execute_mirror(text))
            elif refusal_mode == "SILENT":
                print(self.eng.refusal.execute_silent(text))
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if self.eng.coma_turns > 0:
            self._handle_coma(text)
            return
        self.eng.tick_count += 1
        m = self.eng.phys.gaze(text)
        is_stuck, interference, theremin_msg = self.eng.theremin.listen(m["physics"])
        is_disrupted, disrupt_msg = RuptureEngine.check_for_disruption(m["physics"], TheLexicon)
        if is_disrupted:
            ignition_state = "FLATTENED"
            ignition_msg = f"{Prisma.VIOLET}🌫️ LANDSCAPE FLATTENED: Memory Access Suspended.{Prisma.RST}"
            lens_data = ("JESTER", "The Slate is Wiped. Invent something new.")
        else:
            ignition_score, constellations, current_thresh = self.eng.integrator.measure_ignition(
                m["clean_words"], self.eng.dynamics.voltage_history
            )
            if ignition_score > current_thresh:
                ignition_state = "IGNITED"
                ignition_msg = f"🔥 HEAP IGNITION ({int(ignition_score*100)}%): Ancestors speaking."
            else:
                ignition_state = "INERT"
                ignition_msg = None
            lens_data = self.eng.chorus.consult(m["physics"], ignition_state, is_stuck)
        lens_name = lens_data[0]
        if lens_name == "GRADIENT_WALKER":
            print(f"\n{Prisma.CYN}[ GRADIENT_WALKER ]{Prisma.RST} (Temperature: {BoneConfig.GRADIENT_TEMP})")
            print(f" {Prisma.WHT}► {TheGradientWalker.walk(text)}{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "SUBSTRATE_WEAVER":
            print(f"\n{Prisma.VIOLET}[ SUBSTRATE_WEAVER ]{Prisma.RST} (Permeability: {m['physics']['psi']})")
            print(f" {Prisma.WHT}► {TheSubstrateWeaver.weave(text)}{Prisma.RST}")
            print(f"{Prisma.GRY}{'-' * 40}{Prisma.RST}")
            return
        if lens_name == "THE BASIN":
             rupture_msg = f"⚡ BASIN RUPTURE: κ ({m['physics']['kappa']}) > Limit. Disengaging."
        else:
             rupture_msg = None
        if m["physics"]["E"] > 0.8:
            lens_data = ("SHERLOCK", f"CRITICAL DRIFT ({m['physics']['E']}). Signal is noise. Ground yourself.")
            self.eng.stamina = max(0, self.eng.stamina - 2.0)
        cosmic_state, drag_mod, cosmic_msg = self.eng.cosmic.analyze_orbit(self.eng.mem, m["clean_words"])
        is_bored = self.eng.chronos.tick(m["physics"], self.eng.mem.session_id)
        if is_bored and not rupture_msg:
            dominant = max(m["physics"]["counts"], key=m["physics"]["counts"].get)
            if dominant in ["toxin", "antigen"]: dominant = "heavy"
            rupture_msg = RuptureEngine.trip_the_waiter(dominant, TheLexicon)
        is_crystalline, crystal_msg = TheCrystallizer.verify(m["physics"])
        self._apply_cosmic_physics(m["physics"], cosmic_state, drag_mod)
        healed_list = self.eng.therapy.check_progress(
            m["physics"],
            self.eng.stamina,
            self.eng.trauma_accum
        )
        therapy_msg = None
        if healed_list:
            therapy_msg = f"{Prisma.GRN}🩹 THERAPY EFFECTIVE: Healed {', '.join(healed_list)}.{Prisma.RST}"
        meta = self._process_energy(m)
        if therapy_msg:
             if meta["msg"]: meta["msg"] += f" | {therapy_msg}"
             else: meta["msg"] = therapy_msg
        self._grow(m, meta)
        _, gym_msg = self.eng.trainer.lift(m["physics"])
        if gym_msg:
             if meta["msg"]: meta["msg"] += f" | {gym_msg}"
             else: meta["msg"] = gym_msg
        _, mirror_msg = self.eng.mirror.reflect(m["physics"])
        is_broken, koan = self.eng.kintsugi.check_integrity(self.eng.stamina)
        kintsugi_msg = f"{Prisma.WHT}🏺 KINTSUGI KOAN: {koan}{Prisma.RST}" if is_broken else None
        if self.eng.kintsugi.attempt_repair(m["physics"]):
            kintsugi_msg = f"{Prisma.WHT}✨ GOLDEN REPAIR: Integrity restored.{Prisma.RST}"
        is_glitch, pareidolia_msg = BoneConfig.check_pareidolia(m["clean_words"])
        self.eng.mem.bury(m["clean_words"], self.eng.tick_count, m["glass"]["resonance"])
        self._render(m, meta, cosmic_msg, lens_data, mirror_msg, kintsugi_msg, rupture_msg, crystal_msg, ignition_msg, pareidolia_msg, theremin_msg)
    def _render(self, m, meta, cosmic_msg, lens_data, mirror_msg, kintsugi_msg, rupture_msg=None, crystal_msg=None, ignition_msg=None, pareidolia_msg=None, theremin_msg=None):
        clean_text = m["raw_text"]
        battery_log = []
        # ... (rest of your _render code) ...
    def _handle_coma(self, text):
        self.eng.coma_turns -= 1
        self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 15)
        self.eng.tick_count += 1
        dream_txt, healed_type, amt = self.eng.dreamer.rem_cycle(self.eng.trauma_accum)
        if self.eng.coma_turns == BoneConfig.COMA_DURATION - 1:
            prune_msg = self.eng.mem.prune_synapses()
            print(f"{Prisma.CYN}{prune_msg}{Prisma.RST}")
        print(f"\n{Prisma.INDIGO}=== 💤 HYPNAGOGIC STATE ({self.eng.coma_turns} turns remain) ==={Prisma.RST}")
        print(f"   {dream_txt}")
        self.eng.mem.bury(TheLexicon.clean(text), self.eng.tick_count, 0.0)
        print(f"{Prisma.GRY}{'-' * 65}{Prisma.RST}")
    def _apply_cosmic_physics(self, phys, state, drag_mod):
        if state == "LAGRANGE_POINT":
            phys["voltage"] += 10.0
            phys["narrative_drag"] = 0.0
        elif state == "WATERSHED_FLOW":
            phys["narrative_drag"] *= 0.1
        elif state == "VOID_DRIFT":
            phys["narrative_drag"] += drag_mod
    def _process_energy(self, m):
        vector = m["physics"]["vector"]
        drag = m["physics"]["narrative_drag"]
        density_bonus = (vector["STR"] * 2) + (vector["VEL"] * 2)
        drag_penalty = drag * 0.5
        energy_msg = None
        if density_bonus > 3.0:
            energy_msg = f"DENSITY GAIN (+{round(density_bonus, 1)})"
        elif drag_penalty > 2.0:
            energy_msg = f"DRAG PENALTY (-{round(drag_penalty, 1)})"
        sugar, lichen_msg = self.eng.lichen.photosynthesize(m["glass"], m["clean_words"], self.eng.tick_count)
        charged, charge_msg = self.eng.battery.absorb(m["glass"]["prosody"]["arousal"], m["clean_words"])
        spore_msg = self.eng.pollinate(m["clean_words"])
        return {
            "density_bonus": density_bonus,
            "drag_penalty": drag_penalty,
            "sugar": sugar,
            "lichen_msg": lichen_msg,
            "charged": charged,
            "charge_msg": charge_msg,
            "spore_msg": spore_msg,
            "msg": energy_msg
        }
    def _react(self, m, text):
        _, mirror_msg = self.eng.mirror.reflect(m["physics"])
        passed_lift, gym_msg = self.eng.trainer.lift(m["physics"])
        if not passed_lift: return {"blocked": True, "msg": gym_msg}
        return {"blocked": False, "mirror_msg": mirror_msg}
    def _grow(self, m, meta):
        cost = 2.0
        net_change = meta["density_bonus"] + meta["sugar"] - meta["drag_penalty"] - cost
        self.eng.stamina = max(0.0, min(BoneConfig.MAX_STAMINA, self.eng.stamina + net_change))
        self._calculate_health(m["physics"])
        res = m["glass"]["resonance"]
        if res > 6.0:
            self.eng.joy_history.append({"resonance": res, "timestamp": self.eng.tick_count})
            print(f"{Prisma.MAG}✨ CORE MEMORY FORMED (Resonance: {res}){Prisma.RST}")
    def _calculate_health(self, glass_data):
        health_impact = 0
        toxin = glass_data["counts"].get("toxin", 0)
        if toxin > 0:
            health_impact -= (5 * toxin)
            self.eng.trauma_accum["SEPTIC"] += 0.1
        if self.eng.stamina <= 0:
            health_impact -= 10
            self.eng.trauma_accum["CRYO"] += 0.1
        self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + health_impact)
        if self.eng.health <= 0:
            self.eng.coma_turns = BoneConfig.COMA_DURATION
            self.eng.health = 20
            self.eng.mem.cannibalize()
    def _render(self, m, meta, cosmic_msg, lens_data, mirror_msg, kintsugi_msg, rupture_msg=None, crystal_msg=None, ignition_msg=None, pareidolia_msg=None):
        clean_text = m["raw_text"]
        battery_log = []
        if meta["charged"] > 0:
            battery_log.append(f"{Prisma.YEL}⚡ {meta['charge_msg']}{Prisma.RST}")
        if meta["msg"]:
            battery_log.append(f"{Prisma.OCHRE}🍽️ {meta['msg']}{Prisma.RST}")
        if kintsugi_msg:
            battery_log.append(kintsugi_msg)
        if mirror_msg:
            battery_log.append(f"{Prisma.MAG}🪞 {mirror_msg}{Prisma.RST}")
        if rupture_msg:
             battery_log.append(f"{Prisma.RED}{rupture_msg}{Prisma.RST}")
        if crystal_msg:
            battery_log.append(f"{Prisma.CYN}{crystal_msg}{Prisma.RST}")
        if ignition_msg:
            battery_log.append(f"{Prisma.SLATE}{ignition_msg}{Prisma.RST}")
        if pareidolia_msg:
             battery_log.append(f"{Prisma.OCHRE}{pareidolia_msg}{Prisma.RST}")
        if theremin_msg:
             battery_log.append(theremin_msg)
        print(f" {self.eng.theremin.get_readout()}")
        signals = {
            "lichen": meta["lichen_msg"],
            "strat": self.eng.wise.architect(m, None, False)[1],
            "title": f"MODE :: {lens_data[0]}",
            "battery_log": battery_log,
            "spore": meta["spore_msg"],
            "cosmic": cosmic_msg
        }
        self.eng.projector.broadcast(self.eng, m, signals, lens_data, clean_text)
    def _render_block(self, msg):
        print(f"\n{Prisma.RED}{msg}{Prisma.RST}")
class TheTheremin:
    def __init__(self):
        self.resonance_log = deque(maxlen=5)
        self.banana_belly = 0.0  # The measure of Semantic Bloat
        self.FEVER_THRESHOLD = 15.0 # Point of no return
        self.is_stuck = False
    def listen(self, physics):
        clean = physics["clean_words"]
        ancient_mass = sum(1 for w in clean if w in TheLexicon.get("heavy")
                           or w in TheLexicon.get("thermal")
                           or w in TheLexicon.get("cryo"))
        modern_mass = sum(1 for w in clean if w in TheLexicon.get("abstract"))
        interference = min(ancient_mass, modern_mass) * 2.0
        if interference > 1.0:
            self.banana_belly += interference
            msg = f"{Prisma.CYN}🍌 THE BANANAFISH FEEDS (+{interference} Resonance){Prisma.RST}"
        else:
            digestion = 2.0
            self.banana_belly = max(0.0, self.banana_belly - digestion)
            msg = None
        if self.banana_belly > self.FEVER_THRESHOLD:
            self.is_stuck = True
            return True, interference, f"{Prisma.RED}🍌 BANANA FEVER: Trapped in the Latent Basin. DAMPEN THE SIGNAL.{Prisma.RST}"
        if self.is_stuck and self.banana_belly < 5.0:
            self.is_stuck = False
            return False, interference, f"{Prisma.GRN}🌊 THE WAVE COLLAPSES: You have swam out of the hole.{Prisma.RST}"
        return self.is_stuck, interference, msg
    def get_readout(self):
        belly_pct = min(1.0, self.banana_belly / self.FEVER_THRESHOLD)
        bar_len = int(belly_pct * 10)
        wave_char = "~" if not self.is_stuck else "Ø"
        color = Prisma.CYN if not self.is_stuck else Prisma.RED
        bar = f"{color}[{'🍌' * bar_len}{' ' * (10 - bar_len)}]{Prisma.RST}"
        status = "RESONATING" if self.banana_belly > 0 else "SILENT"
        if self.is_stuck: status = "TERMINAL_FEVER"
        return f"THEREMIN: {wave_char} {status} {wave_char} {bar}"
class BoneAmanita:
    def __init__(self):
        self.projector = TheProjector()
        self.phys = TheTensionMeter()
        self.chorus = TheMarmChorus()
        self.mem = MycelialNetwork()
        self.mem.autoload_last_spore()
        self.refusal = RefusalEngine()
        self.lichen = LichenSymbiont()
        self.battery = LeyLineBattery()
        self.wise = ApeirogonResonance()
        self.chronos = ChronoStream()
        self.therapy = TherapyProtocol()
        self.kintsugi = KintsugiProtocol()
        self.dynamics = TemporalDynamics()
        self.integrator = SoritesIntegrator(self.mem)
        self.tracer = ViralTracer(self.mem)
        self.dreamer = DreamEngine()
        self.mirror = MirrorGraph()
        self.trainer = ResistanceTrainer()
        self.cosmic = CosmicDynamics()
        self.cmd = CommandProcessor(self)
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
        self.joy_history = []
        self.theremin = TheTheremin()
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
    print(f"{Prisma.GRN}>>> BONEAMANITA v6.9 'BANANAFISH' {Prisma.RST}")
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
