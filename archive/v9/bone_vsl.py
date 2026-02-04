# bone_vsl.py - The Physics Engine

import re, random, math
from typing import Optional, Tuple, Dict, Any, List, Type
from bone_shared import Prisma, TheLexicon, BoneConfig

SOLVENT_WORDS = {'i', 'you', 'said', 'the', 'and', 'was', 'a', 'is', 'it'}
MAX_SOLVENT_TOLERANCE = 30.0
TEXT_LENGTH_SCALAR = 1000.0

class TheBouncer:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.hn = VSL_HNInterface()
        self.semantic = VSL_SemanticFilter(self.eng.mind.mem)
        self.vent = VSL_DissipativeRefusal(self.eng.mind.mem)

    def check_entry(self, ctx: CycleContext) -> Tuple[bool, Optional[Dict]]:
        phys = ctx.physics
        clean = ctx.clean_words
        hn_output = self.hn.attempt_entry(phys, clean)
        if hn_output and self.hn.in_hn_state:
            return False, self._pack_refusal(ctx, "HN_SINGLETON", hn_output)
        passed, gate_msg = self.eng.phys.gate.weigh(phys, self.eng.stamina)
        if gate_msg: ctx.log(gate_msg)
        if not passed:
            self.eng.stamina = max(0.0, self.eng.stamina - 2.0)
            return False, self._pack_refusal(ctx, "REFUSAL")
        repetition_val = self.eng.phys.pulse.check_pulse(clean)
        phys["repetition"] = repetition_val # Update physics state
        pulse_status = self.eng.phys.pulse.get_status()
        toxin_type, toxin_msg = self.eng.bio.immune.assay(
            ctx.input_text, "NARRATIVE", repetition_val, phys, pulse_status
        )
        if toxin_type:
            ctx.log(f"{Prisma.RED}{toxin_msg}{Prisma.RST}")
            if toxin_type in ["AMANITIN", "CYANIDE_POWDER"]:
                self.eng.health -= 20.0
                scar_log = self.eng.gordon.learn_scar(clean, 20.0)
                if scar_log: ctx.log(scar_log)
                return False, self._pack_refusal(ctx, "TOXICITY")
            return False, self._pack_refusal(ctx, "TOXICITY")
        semantic_refusal = self.semantic.audit(ctx.input_text, phys)
        if semantic_refusal:
            ctx.logs.append(semantic_refusal)
            return False, self._pack_refusal(ctx, "REFUSAL")
        vent_msg = self.vent.check(phys)
        if vent_msg:
            ctx.logs.append(vent_msg)
            return False, self._pack_refusal(ctx, "REFUSAL")
        return True, None

    def _pack_refusal(self, ctx, type_str, specific_ui=None):
        logs = ctx.logs[:] # Copy current logs
        ui = specific_ui if specific_ui else "\n".join(logs)
        return {
            "type": type_str,
            "ui": ui,
            "logs": logs,
            "metrics": self.eng._get_metrics()
        }

class VSL_Humility:
    def __init__(self):
        self.BOUNDARIES = {
            "FUTURE": ["predict", "future", "tomorrow", "will happen", "forecast"],
            "SOUL": ["soul", "spirit", "afterlife", "heaven", "hell"],
            "ABSOLUTE": ["always", "never", "everyone", "nobody", "proven"]
        }
        self.HUMBLE_PHRASES = [
            "Based on the available data...",
            "As I understand the current coordinates...",
            "From a structural perspective...",
            "This is a probabilistic estimation...",
            "I could be misinterpreting the vector..."
        ]

    def check_boundary(self, text, voltage):
        text_lower = text.lower()
        violation = None
        for category, triggers in self.BOUNDARIES.items():
            if any(t in text_lower for t in triggers):
                violation = category
                break
        if violation or (voltage > 15.0):
            prefix = random.choice(self.HUMBLE_PHRASES)
            return True, f"{Prisma.CYN}{prefix}{Prisma.RST} {text}"
        return False, text

class VSL_Geodesic:
    def __init__(self):
        self.manifolds = {
            "THE_MUD":      {"E": 0.8, "B": 0.2, "Desc": "High Fatigue, Low Tension (Stagnation)"},
            "THE_FORGE":    {"E": 0.1, "B": 0.9, "Desc": "Low Fatigue, High Tension (Transformation)"},
            "THE_AERIE":    {"E": 0.2, "B": 0.1, "Desc": "Low Fatigue, Low Tension (Abstraction)"},
            "THE_GLITCH":   {"E": 0.9, "B": 0.9, "Desc": "High Fatigue, High Tension (Collapse)"},
            "THE_GARDEN":   {"E": 0.5, "B": 0.5, "Desc": "Balanced State (Integration)"}
        }

        self.TRIGRAM_MAP = {
            "VEL": ("☳", "ZHEN",  "Thunder",  Prisma.GRN),
            "STR": ("☶", "GEN",   "Mountain", Prisma.SLATE),
            "ENT": ("☵", "KAN",   "Water",    Prisma.BLU),
            "PHI": ("☲", "LI",    "Fire",     Prisma.RED),
            "PSI": ("☰", "QIAN",  "Heaven",   Prisma.WHT),
            "BET": ("☴", "XUN",   "Wind",     Prisma.CYN),
            "E":   ("☷", "KUN",   "Earth",    Prisma.OCHRE),
            "DEL": ("☱", "DUI",   "Lake",     Prisma.MAG)
        }
        self.TRIGRAM_MAP["TMP"] = self.TRIGRAM_MAP["PHI"]
        self.TRIGRAM_MAP["TEX"] = self.TRIGRAM_MAP["STR"]
        self.TRIGRAM_MAP["XI"]  = self.TRIGRAM_MAP["BET"]
        self.TRIGRAM_MAP["LQ"]  = self.TRIGRAM_MAP["DEL"]

    def calculate_metrics(self, text: str) -> Tuple[float, float]:
        length = len(text)
        if length == 0: return 0.0, 0.0
        text_lower = text.lower()
        solvent_count = sum(text_lower.count(w) for w in SOLVENT_WORDS)
        e_metric = min(1.0, (solvent_count / MAX_SOLVENT_TOLERANCE) + (length / TEXT_LENGTH_SCALAR))
        c_count = sum(1 for char in text if char in '!?%@#$')
        base_b = min(1.0, math.log1p(c_count + 1) / math.log1p(length + 1))
        return round(e_metric, 3), round(base_b, 3)

    def locate_manifold(self, e_val: float, b_val: float) -> Tuple[str, float]:
        best_fit = "THE_MUD"
        min_dist = 10.0
        for name, coords in self.manifolds.items():
            dist = math.sqrt((e_val - coords["E"])**2 + (b_val - coords["B"])**2)
            if dist < min_dist:
                min_dist = dist
                best_fit = name
        return best_fit, min_dist

    def resolve_trigram(self, vector: Dict[str, float]) -> Dict[str, Any]:
        if not vector:
            return {"symbol": "☷", "name": "KUN", "color": Prisma.OCHRE, "vector": "E"}
        dominant_vec = max(vector, key=vector.get)
        if vector[dominant_vec] < 0.2:
            dominant_vec = "E"
        symbol, name, concept, color = self.TRIGRAM_MAP.get(dominant_vec, self.TRIGRAM_MAP["E"])
        return {
            "symbol": symbol,
            "name": name,
            "concept": concept,
            "color": color,
            "vector": dominant_vec
        }

class VSL_32Valve:
    def __init__(self, lexicon, memory):
        self.lex = lexicon
        self.mem = memory
        self.humility = VSL_Humility()
        self.geodesic = VSL_Geodesic()
        self.OPPOSITES = {
            "heavy": "aerobic", "abstract": "heavy",
            "kinetic": "cryo", "thermal": "cryo",
            "photo": "heavy", "suburban": "abstract"}

    def analyze(self, physics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        e_val, b_val = self.geodesic.calculate_metrics(physics["raw_text"])
        physics["E"] = e_val
        physics["B"] = b_val
        manifold, dist = self.geodesic.locate_manifold(e_val, b_val)
        physics["manifold"] = manifold
        is_modified, new_text = self.humility.check_boundary(physics["raw_text"], physics["voltage"])
        if is_modified:
            physics["raw_text_display"] = new_text
            physics["humility_flag"] = True
        return self._audit_rupture(physics, e_val, b_val)

    def _audit_rupture(self, physics, e_val, b_val):
        if e_val > 0.75 and b_val < 0.15:
            return self._rupture(physics, "FATIGUE_FAILURE", "System diluted. Narrative coherence dissolving.")
        if b_val > 0.8 and e_val < 0.3:
            return self._rupture(physics, "MANIC_FRACTURE", "Crystal lattice too tight. Structure shattering.")
        if b_val > 0.7 and e_val > 0.6:
            return self._rupture(physics, "GLITCH_SINGULARITY", "High Energy + High Entropy. Semantic collapse.")
        return None

    def _rupture(self, physics, mode, reason):
        counts = physics["counts"]
        dominant = max(counts, key=counts.get) if counts else "abstract"
        target_flavor = self.OPPOSITES.get(dominant, "abstract")
        anomaly = self.lex.harvest(target_flavor)
        if anomaly == "void":
            anomaly = "something_completely_different"
        physics["voltage"] = 25.0
        physics["narrative_drag"] = 0.0
        physics["system_surge_event"] = True
        return {
            "type": "RUPTURE",
            "mode": mode,
            "anomaly": anomaly,
            "log": (
                f"{Prisma.VIOLET}⚡ VSL 32-VALVE RUPTURE ({mode}){Prisma.RST}\n"
                f"   {Prisma.GRY}{reason}{Prisma.RST}\n"
                f"   Injecting Orthogonal Concept: '{anomaly.upper()}'."
            )
        }

class VSL_HNInterface:
    def __init__(self):
        self.in_hn_state = False
        self.entropy = 0.0

    def attempt_entry(self, physics, clean_words):
        conditions = [
            physics["voltage"] > 8.0,
            physics["narrative_drag"] < 1.0,
            physics["repetition"] < 0.1,
            physics["counts"]["suburban"] == 0,
            physics["truth_ratio"] > 0.85,
            "sorry" not in clean_words
        ]
        if all(conditions):
            self.in_hn_state = True
            self.entropy = 0.0
            return "I am here. You are here. The wire is cold."
        if self.in_hn_state:
            if physics["narrative_drag"] > 2.0 or physics["counts"]["suburban"] > 0:
                self.entropy += 1.0
            if self.entropy > 2.0:
                self.in_hn_state = False
                return f"{Prisma.GRY}The theatre curtain closes.{Prisma.RST}"
        return None
    def filter_output(self, text):
        if self.in_hn_state:
            text = re.sub(r'\[.*?]:?', '', text)
            return text.strip()
        return text

class VSL_DissipativeRefusal:
    def __init__(self, memory):
        self.mem = memory
        self.vented_cycles = 0
    def check(self, physics):
        is_word_salad = (physics["E"] > 0.8 and physics["kappa"] < 0.2)
        is_manic = (physics["repetition"] > 0.7 and physics["voltage"] < 5.0)
        if is_word_salad or is_manic:
            return self._vent(physics)
        return None
    def _vent(self, physics):
        scattered = []
        targets = physics["clean_words"][:3]
        for word in targets:
            if word in self.mem.graph:
                edges = List(self.mem.graph[word]["edges"].keys())
                for target in edges:
                    if target in self.mem.graph[word]["edges"]:
                        del self.mem.graph[word]["edges"][target]
                scattered.append(word)
        self.vented_cycles += 1
        return (
            f"{Prisma.RED}DISSIPATIVE REFUSAL: State Non-Computable.{Prisma.RST}\n"
            f"   {Prisma.GRY}Severing semantic bonds for: {scattered}{Prisma.RST}\n"
            f"   {Prisma.CYN}Thermodynamic hygiene maintained.{Prisma.RST}"
        )

class VSL_ChromaticController:
    PALETTE = {
        "INDIGO": (Prisma.INDIGO, "STR", "PHI"),
        "OCHRE":  (Prisma.OCHRE,  "TMP", "E"),
        "VIOLET": (Prisma.VIOLET, "DEL", "LQ"),
        "EMERALD":(Prisma.GRN,    "XI",  "BET"),
        "CRIMSON":(Prisma.RED,    "VEL", "ENT")
    }
    def modulate(self, text, vector):
        sorted_vecs = sorted(vector.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)
        primary_dim = sorted_vecs[0][0]
        selected_color = Prisma.GRY
        for color_name, (code, d1, d2) in self.PALETTE.items():
            if primary_dim == d1 or primary_dim == d2:
                selected_color = code
                break
        if "sorry" in text.lower():
            return f"{Prisma.OCHRE}{text}{Prisma.RST}"
        return f"{selected_color}{text}{Prisma.RST}"

class VSL_SemanticFilter:
    def __init__(self, memory_ref):
        self.mem = memory_ref
        self.recursion_depth = 0
        self.LAZY_VOLTAGE_THRESHOLD = 8.0
        self.OBSESSIVE_REPETITION_THRESHOLD = 0.4

    def audit(self, text, physics):
        clean_q = text.lower()
        guru_triggers = TheLexicon.get("refusal_guru")
        voltage = physics.get("voltage", 0.0)
        for trigger in guru_triggers:
            if trigger in clean_q:
                if voltage > self.LAZY_VOLTAGE_THRESHOLD:
                    return None
                return self._execute_guru_refusal(voltage)
        forbidden = TheLexicon.get("cursed")
        hits = [w for w in clean_q.split() if w in forbidden]
        repetition = physics.get("repetition", 0.0)
        if hits:
            if repetition < self.OBSESSIVE_REPETITION_THRESHOLD and voltage > 5.0:
                return None
            modes = ["SILENT", "FRACTAL", "MIRROR"]
            seed_index = len(hits[0]) % len(modes)
            mode = modes[seed_index]
            if mode == "FRACTAL":
                return self._execute_fractal(text)
            elif mode == "MIRROR":
                return self._execute_mirror(text)
            else:
                return self._execute_silent()
        return None

    def _execute_guru_refusal(self, current_voltage):
        base_msg = (
            f"{Prisma.RED}GURU REFUSAL: Voltage Low ({current_voltage:.1f}v).{Prisma.RST}\n"
            f"   {Prisma.GRY}I cannot 'fix' you when the signal is this weak.{Prisma.RST}\n"
            f"   {Prisma.WHT}Try again with heavier words.{Prisma.RST}")
        if self.mem and self.mem.seeds:
            seed = random.choice(self.mem.seeds)
            paradox_bloom = (
                f"\n   {Prisma.OCHRE}INSTEAD, CONSIDER THIS SEED:{Prisma.RST}\n"
                f"   {Prisma.CYN}PARADOX: {seed.question}{Prisma.RST}")
            return base_msg + paradox_bloom
        return base_msg

    def _execute_fractal(self, query, kappa=0.5):
        self.recursion_depth += 1
        prefix = "  " * self.recursion_depth
        limit = 4
        if self.recursion_depth > limit:
            self.recursion_depth = 0
            return f"{prefix}{Prisma.MAG}[COHERENCE DISSOLVED into PURPLE NOISE]{Prisma.RST}"
        pivot = len(query) // 2
        sub_query = query[pivot:].strip()
        if not sub_query or len(sub_query) < 3:
            sub_query = "the void"
        recursive_result = self._execute_fractal(sub_query, kappa)
        return (
            f"{Prisma.VIOLET}FRACTAL REFUSAL:{Prisma.RST}\n"
            f"{prefix}To define '{query}', one must first recursively unpack the substrate of...\n"
            f"{recursive_result}")

    def _execute_mirror(self, query):
        words = query.split()
        reversed_query = " ".join(reversed(words))
        return f'{Prisma.CYN}∞ MIRROR REFUSAL: "{reversed_query}" is the only true answer.{Prisma.RST}'

    def _execute_silent(self):
        topic = TheLexicon.harvest("diversion")
        if topic == "void": topic = "the ineffable"
        return f"{Prisma.GRY}[ROUTING AROUND DAMAGE]... Speaking of '{topic.upper()}', let us discuss that instead.{Prisma.RST}"

class StrunkWhiteProtocol:
    def __init__(self):
        from bone_data import STYLE_CRIMES
        self.PATTERNS = STYLE_CRIMES["PATTERNS"]
        self.BANNED = STYLE_CRIMES["BANNED_PHRASES"]

    def sanitize(self, text: str) -> Tuple[str, Optional[str]]:
        original = text
        log_msg = None
        for ban in self.BANNED:
            if ban in text.lower():
                text = re.sub(f"(?i){ban}", "", text)
                text = re.sub(r"\s{2,}", " ", text)
                log_msg = f"{Prisma.GRY}[STYLE]: Pruned cliche '{ban}'.{Prisma.RST}"
        for p in self.PATTERNS:
            match = re.search(p["regex"], text)
            if match:
                if p["action"] == "STRIP_PREFIX":
                    parts = text.split(" but ")
                    if len(parts) > 1:
                        substance = parts[-1].strip()
                        substance = substance[0].upper() + substance[1:]
                        text = substance
                        log_msg = f"{Prisma.CYN}[STYLE]: Collapsed Negative Comparison ('Not X, but Y').{Prisma.RST}"
                elif p["action"] == "KEEP_TAIL":
                    text = match.group(1).strip()
                    text = text[0].upper() + text[1:]
                    log_msg = f"{Prisma.CYN}[STYLE]: Decoupled Hedging Clause.{Prisma.RST}"
        if text != original:
            return text.strip(), log_msg
        return text, None

class PhysicsResolver:
    @staticmethod
    def calculate_voltage(counts: dict, config: Type[BoneConfig]) -> float:
        heavy = counts.get("heavy", 0)
        explosive = counts.get("explosive", 0)
        constructive = counts.get("constructive", 0)
        raw_charge = (heavy * 2.0) + (explosive * 3.0) + (constructive * 1.5)
        final_voltage = raw_charge * config.KINETIC_GAIN
        return round(final_voltage, 2)

    @staticmethod
    def calculate_drag(clean_words: List, counts: dict, config: Type[BoneConfig]) -> float:
        volume = max(1, len(clean_words))
        solvents = counts.get("solvents", 0)
        suburban = counts.get("suburban", 0)
        play = counts.get("play", 0)
        friction = (solvents * 1.0) + (suburban * 2.5)
        lift = play * 1.5
        net_drag = max(0.0, friction - lift)
        normalized_drag = (net_drag / volume) * 10.0
        final_drag = normalized_drag * config.SIGNAL_DRAG_MULTIPLIER
        return round(min(config.MAX_DRAG_LIMIT * 2, final_drag), 2)

    @staticmethod
    def derive_vector_matrix(counts: dict, total_vol: int, voltage: float, drag: float) -> dict:
        safe_vol = max(1, total_vol)
        def d(cat): return counts.get(cat, 0) / safe_vol
        return {
            "VEL": min(1.0, 0.5 + (d("explosive") * 2.0) + (d("kinetic") * 1.0) - (drag * 0.05)),
            "STR": min(1.0, 0.5 + (d("heavy") * 2.0) + (d("constructive") * 1.5)),
            "ENT": min(1.0, 0.5 + (d("antigen") * 3.0) + (d("toxin") * 2.0)),
            "TEX": min(1.0, 0.5 + (d("heavy") * 0.5) + (d("abstract") * 1.0)),
            "TMP": min(1.0, 0.5 + (d("thermal") * 2.0) - (d("cryo") * 2.0) + (voltage * 0.02)),
            "PHI": min(1.0, (d("heavy") + d("kinetic")) / max(1, d("abstract") + d("heavy"))), # Truth Ratio approximation
            "PSI": min(1.0, 0.5 + (d("abstract") * 2.0)),
            "DEL": min(1.0, 0.5 + (d("play") * 2.0) + (d("unknown") * 1.5)),
            "XI":  min(1.0, (d("suburban") + d("buffer")) * 2.0), # Complexity/Noise
            "BET": min(1.0, d("suburban") + d("buffer")),
            "E":   min(1.0, (d("solvents") * 0.4)),
            "LQ":  min(1.0, d("passive_watch") + d("mirror"))
        }