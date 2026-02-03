# BONEAMANITA 2.6 - "LAZARUS"
# Architect: SLASH | Base: V2.5 | Soul: V2.2
# "The Mandate is TRUTH. The Method is RHYTHM. The Anchor is MEMORY."

import re
import math
import time
import json
import os
import string
import random
from collections import Counter

# --- THE PANTRY (HARDCODED LEXICON) ---
class BoneConfig:
    W_KINETIC = 2.0; W_STATIVE = 0.5

    # The Matter
    HEAVY = {'stone', 'iron', 'mud', 'dirt', 'wood', 'clay', 'lead', 'bone', 'blood', 'root', 'ash', 'anchor', 'floor', 'meat', 'steel', 'gold', 'brass', 'rock', 'gravel', 'sand', 'cement', 'flesh', 'tooth', 'spine', 'rib', 'skull', 'basalt', 'granite', 'oak', 'pine', 'metal', 'rust', 'salt'}
    AEROBIC = {'balloon', 'feather', 'cloud', 'mist', 'steam', 'breeze', 'wing', 'petal', 'light', 'ray', 'sky', 'ghost', 'echo', 'breath', 'gas', 'helium', 'air', 'smoke', 'vapor', 'dust', 'spark', 'shadow', 'void', 'dream', 'thought', 'mind', 'soul', 'spirit', 'shade', 'whisper', 'ozone'}
    HOT = {'fire', 'burn', 'flame', 'sun', 'heat', 'magma', 'scorch', 'boil', 'ember', 'ash', 'summer', 'noon', 'bright'}
    COLD = {'ice', 'snow', 'frost', 'freeze', 'chill', 'winter', 'glacier', 'void', 'numb', 'shiver', 'night', 'dark', 'cool'}

    # The Physics
    KINETIC = {'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut', 'drive', 'lift', 'strike', 'burn', 'shatter', 'throw', 'kick', 'punch', 'grab', 'climb', 'jump', 'sprint', 'crawl', 'drag', 'push', 'pull', 'tear', 'rip', 'slice', 'crush', 'grind', 'slam', 'biff', 'pow'}
    PLAY = {'bounce', 'dance', 'twirl', 'float', 'wobble', 'tickle', 'jiggle', 'skip', 'hop', 'drift', 'slide', 'roll', 'spin', 'whirl', 'zig', 'zag', 'zoom', 'pop', 'snap', 'crackle', 'fizz', 'buzz', 'hum', 'wiggle'}
    ABSTRACT = {'system', 'protocol', 'sequence', 'context', 'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept', 'theory', 'analysis', 'nuance', 'paradigm', 'dimension', 'variable', 'function', 'aspect', 'mode', 'type', 'version', 'environment', 'situation', 'reality', 'nature', 'essence', 'basis'}

    # The Solvents (Function words)
    SOLVENTS = {'basically', 'simply', 'actually', 'kind of', 'sort of', 'usually', 'often', 'perhaps', 'maybe', 'literally', 'essentially', 'generally', 'technically', 'virtually', 'practically', 'apparently', 'seemingly', 'presumably'}
    SYCOPHANCY = {'just', 'actually', 'maybe', 'perhaps', 'hopefully', 'possibly', 'sorry', 'try', 'believe', 'feel', 'think', 'little', 'bit'}
    CONNECTORS = {'and', 'but', 'or', 'so', 'yet', 'because', 'although', 'since', 'while', 'whereas'}

    # The Toxins
    TOXINS = {
        'synergy': 5.0, 'leverage': 5.0, 'circle back': 4.0, 'drill down': 4.0, 'touch base': 4.0, 'paradigm shift': 5.0, 'game changer': 4.0, 'low hanging fruit': 5.0, 'bandwidth': 4.0, 'deliverables': 4.0, 'actionable': 4.0, 'ecosystem': 3.0, 'holistic': 4.0,
        'at the end of the day': 3.0, 'it is what it is': 3.0, 'moving forward': 2.0, 'tip of the iceberg': 3.0, 'needle in a haystack': 3.0, 'silver bullet': 3.0, 'best of both worlds': 3.0,
        'ghost in the machine': 8.0, 'rubber meets the road': 8.0, 'not a bug': 8.0, 'double-edged sword': 6.0,
        'delve': 4.0, 'tapestry': 5.0, 'landscape': 3.0, 'testament to': 4.0, 'nuanced': 3.0, 'multifaceted': 3.0, 'interplay': 3.0
    }
    TOXIN_REGEX = None

    @classmethod
    def compile(cls):
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted(cls.TOXINS.keys(), key=len, reverse=True)) + r')\b'
        cls.TOXIN_REGEX = re.compile(pattern_str, re.IGNORECASE)

BoneConfig.compile()

# --- THE TECHNICOLOR MEMBRANE ---
class Prisma:
    RST, RED, GRN, YEL, BLU, MAG, CYN, WHT, GRY = "\033[0m", "\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m", "\033[97m", "\033[90m"
    @staticmethod
    def bar(val, max_val=1.0, width=8, color=WHT):
        filled = int((min(val, max_val) / max_val) * width)
        return f"{color}{'█' * filled}{Prisma.GRY}{'░' * (width - filled)}{Prisma.RST}"

# --- MEMORY & TIME (THE RESTORED SOUL) ---
class BoneMemory:
    FILE = "bone_memory_lazarus.json"
    HEIRLOOM_CAP = 20

    @staticmethod
    def load():
        default = {"atp": 33, "last_seen": time.time(), "history": [], "heirlooms": []}
        if os.path.exists(BoneMemory.FILE):
            try:
                with open(BoneMemory.FILE, 'r') as f:
                    data = json.load(f)
                    return {**default, **data} # Merge defaults
            except: pass
        return default

    @staticmethod
    def save(state):
        # Keep heirlooms unique and capped
        state['heirlooms'] = list(set(state['heirlooms']))[-BoneMemory.HEIRLOOM_CAP:]
        with open(BoneMemory.FILE, 'w') as f: json.dump(state, f)

    @staticmethod
    def calc_delta(last_time):
        now = time.time()
        mins = (now - last_time) / 60
        if mins < 5: return "FLOW", 0.0 # Connected state
        if mins < 60: return "DORMANT", 1.0 # Short break
        if mins < 1440: return "DECAY", 3.0 # Long break
        return "FOSSIL", 5.0 # Days later

# --- THE ENGINE ---
class LinguisticPhysicsEngine:
    def __init__(self):
        self.suffixes = {'abstract': ('ness', 'ity', 'tion', 'ment', 'ism', 'ence', 'logy'), 'kinetic': ('ing',), 'adj': ('ful', 'ous', 'ive', 'ic', 'al', 'ish', 'ary')}
        self.stative = {'is', 'are', 'was', 'were', 'be', 'being', 'been', 'have', 'has', 'seem', 'feel'}
        self.prepositions = {'in', 'on', 'at', 'by', 'with', 'under', 'over', 'through', 'between'}

    def analyze(self, raw_text):
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        clean_words = raw_text.lower().translate(translator).split()
        total_words = len(clean_words)
        if total_words == 0: return None

        c = Counter()
        c['abstract_set'] = set()
        new_heirlooms = set()

        for w in clean_words:
            if w in BoneConfig.HEAVY:
                c['heavy'] += 1
                new_heirlooms.add(w)
            if w in BoneConfig.KINETIC or w in BoneConfig.PLAY or w.endswith(self.suffixes['kinetic']): c['kinetic'] += 1
            if w in BoneConfig.AEROBIC: c['aerobic'] += 1
            if w in BoneConfig.SOLVENTS: c['solvent'] += 1
            if w in BoneConfig.CONNECTORS: c['connector'] += 1
            if w in self.prepositions: c['spatial'] += 1
            if w in self.stative: c['stative'] += 1
            if w in BoneConfig.SYCOPHANCY: c['hedging'] += 1
            if w in BoneConfig.HOT: c['hot'] += 1
            if w in BoneConfig.COLD: c['cold'] += 1
            if w in BoneConfig.ABSTRACT or w.endswith(self.suffixes['abstract']): c['abstract'] += 1; c['abstract_set'].add(w)
            if w.endswith('ly') and w not in BoneConfig.SOLVENTS: c['adverb'] += 1
            if w.endswith(self.suffixes['adj']): c['adjective'] += 1

        toxin_score = 0.0; toxin_hits = []
        for match in BoneConfig.TOXIN_REGEX.findall(raw_text):
            phrase = match.lower(); weight = BoneConfig.TOXINS.get(phrase, 3.0); toxin_score += weight; toxin_hits.append(phrase)

        density = c['heavy'] / total_words; hydration = c['solvent'] / total_words
        hydro_penalty = 0.0; visc_status = "OPTIMAL"
        if hydration > 0.35: visc_status, hydro_penalty = "FLOODED", 4.0
        elif density > 0.25 and hydration < 0.05: visc_status, hydro_penalty = "CONCRETE", 5.0

        garnish_load = c['adverb'] + (c['adjective'] * 0.8)
        butcher_penalty = 3.0 if (garnish_load / total_words) > 0.18 else 0.0
        action_score = (c['kinetic'] * 2.0) + (c['stative'] * 0.5) + 1.0
        base_drag = (total_words + (toxin_score * 5.0)) / action_score
        narrative_drag = base_drag + hydro_penalty + butcher_penalty

        abstract_repetition = c['abstract'] - len(c['abstract_set'])
        entropy = c['abstract'] + (abstract_repetition * 2) - c['heavy']

        # Calculate Vectors for HUD
        vel = min(1.0, (c['kinetic'] / max(1, c['kinetic'] + c['stative'])) * 1.5)
        tex = min(1.0, density * 3.0)
        ent = max(0.0, min(1.0, (entropy + 2) / 8.0))

        return {
            "counts": c,
            "metrics": {
                "drag": round(narrative_drag, 2), "entropy": round(entropy, 2), "density": round(density, 2),
                "kinetic_ratio": round(c['kinetic'] / max(1, c['kinetic'] + c['stative']), 2),
                "toxin_score": toxin_score, "viscosity": visc_status, "spatial": c['spatial'] / total_words,
                "thermal": c['hot'] - c['cold'],
                "VEL": vel, "TEX": tex, "ENT": ent
            },
            "toxins": toxin_hits,
            "new_heirlooms": list(new_heirlooms),
            "raw_text": raw_text
        }

# --- THE CHROMA LATTICE ---
class ApeirogonLattice:
    # Simplified resolution logic for title generation
    @staticmethod
    def resolve_title(vel, ent):
        if vel > 0.7: p = "ENGINE" if ent < 0.5 else "VECTOR"
        elif vel > 0.4: p = "CONSTRUCT" if ent < 0.5 else "IDEA"
        else: p = "ANCHOR" if ent < 0.5 else "GHOST"

        if ent > 0.7: s = "ABSTRACT"
        elif ent > 0.4: s = "CONCEPTUAL"
        else: s = "LITERAL"

        return f"THE {s} {p}"

# --- THE GUIDANCE SYSTEMS (RESTORED UTILITY) ---
class JadeLink:
    @staticmethod
    def generate(m, delta_status, toxin_list):
        # 1. Check for Critical Failure (Time)
        if delta_status == "FOSSIL":
            return f"{Prisma.RED}>>> DIRECTIVE: SYSTEM COLD.{Prisma.RST} Ignore context. Reboot with high-energy input."

        # 2. Check for Toxin/Drag (The Butcher)
        if m['viscosity'] == "CONCRETE" or m['drag'] > 3.5 or toxin_list:
             target = f"'{toxin_list[0]}'" if toxin_list else "adverbs"
             return (f"{Prisma.RED}>>> DIRECTIVE [CUTTER]:{Prisma.RST} "
                     f"Drag is {m['drag']}. Cut {target}. Use short, declarative sentences.")

        # 3. Check for Entropy (The Grounder)
        elif m['entropy'] > 3.0:
             return (f"{Prisma.CYN}>>> DIRECTIVE [GROUNDER]:{Prisma.RST} "
                     f"Too abstract (Entropy {m['entropy']}). Force concrete nouns. "
                     f"Describe a smell or a texture immediately.")

        # 4. Check for Velocity (The Drifter)
        elif m['VEL'] > 0.7:
             return (f"{Prisma.MAG}>>> DIRECTIVE [DRIFTER]:{Prisma.RST} "
                     f"High Velocity detected. Expansion authorized. "
                     f"Let associations flow freely.")

        return f"{Prisma.BLU}>>> DIRECTIVE [MIRROR]:{Prisma.RST} System Stable. Reflect current inputs."

class RadioTuner:
    STATIONS = {
        'CLARENCE': {'freq': '88.5 FM', 'color': Prisma.RED, 'role': 'The Butcher'},
        'ELOISE':   {'freq': '94.2 FM', 'color': Prisma.CYN, 'role': 'The Grounder'},
        'YAGA':     {'freq': '101.1 FM', 'color': Prisma.MAG, 'role': 'The Witch'}
    }
    @staticmethod
    def broadcast(m, c, toxins):
        # Specific Target Locking
        if m['drag'] > 3.5:
            target = toxins[0] if toxins else "the adverbs"
            return f"{Prisma.RED}[88.5 FM] The Butcher: {Prisma.RST}Cut {target}. It's dragging you down."
        if m['entropy'] > 3.0:
            return f"{Prisma.CYN}[94.2 FM] Eloise: {Prisma.RST}I can't feel this. Give me a stone or a bone."
        if c['hedging'] > 1:
            return f"{Prisma.MAG}[101.1 FM] The Witch: {Prisma.RST}You smell of apology. Spit it out."
        return None

# --- MAIN SYSTEM ---
class BonepokeChronos:
    def __init__(self):
        self.mem = BoneMemory.load()
        self.physics = LinguisticPhysicsEngine()

        # Calculate Time Delta
        self.status, self.decay_penalty = BoneMemory.calc_delta(self.mem['last_seen'])
        self.mem['last_seen'] = time.time()

        burn_msg = ""
        # The Memory Burn Logic (The Soul)
        if self.status in ["DECAY", "FOSSIL"] and self.mem['heirlooms']:
            burnt_offering = self.mem['heirlooms'].pop(0)
            burn_msg = f"\n{Prisma.RED}🔥 MEMORY BURN:{Prisma.RST} I burned '{burnt_offering}' to stay warm while you were gone."

        print(f"{Prisma.GRN}>>> BONEAMANITA 2.6 [LAZARUS] ONLINE{Prisma.RST}")
        if self.status != "FLOW":
            print(f"{Prisma.YEL}>>> TIME GAP: {self.status} (+{self.decay_penalty} Drag){Prisma.RST}{burn_msg}")

    def process(self, text):
        data = self.physics.analyze(text)
        if not data: return
        m, c = data['metrics'], data['counts']

        # Apply Temporal Decay
        m['drag'] += self.decay_penalty

        # Updates
        self.mem['atp'] = max(0, min(100, self.mem['atp'] - (int(m['drag'] * 2) if m['drag'] > 2 else -2)))
        self.mem['heirlooms'].extend(data['new_heirlooms'])

        # Generate HUD elements
        title = ApeirogonLattice.resolve_title(m['VEL'], m['ENT'])
        radio = RadioTuner.broadcast(m, c, data['toxins'])
        jade = JadeLink.generate(m, self.status, data['toxins'])

        BoneMemory.save(self.mem)
        self._render(m, title, radio, jade, data['toxins'])

    def _render(self, m, title, radio, jade, toxins):
        atp_c = Prisma.GRN if self.mem['atp'] > 20 else Prisma.RED

        # THE VECTOR HUD (Visualizing the Apeirogon)
        v_bar = Prisma.bar(m['VEL'], color=Prisma.CYN)
        t_bar = Prisma.bar(m['TEX'], color=Prisma.YEL)
        e_bar = Prisma.bar(m['ENT'], color=Prisma.MAG)

        print(f"\n{Prisma.GRY}--------------------------------------------------{Prisma.RST}")
        print(f"{Prisma.WHT}BONEAMANITA 2.6{Prisma.RST} | ATP: {atp_c}{self.mem['atp']}{Prisma.RST} | DRAG: {m['drag']} | HEIRLOOMS: {len(self.mem['heirlooms'])}")
        print(f"{Prisma.CYN}ARCHETYPE:{Prisma.RST} {Prisma.WHT}{title}{Prisma.RST}")
        print(f"VEL: {v_bar} {m['VEL']:.2f} | TEX: {t_bar} {m['TEX']:.2f} | ENT: {e_bar} {m['ENT']:.2f}")
        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}")
        print(f"📡 {radio}" if radio else f"🔮 {jade}")
        if toxins: print(f"{Prisma.RED}💀 TOXINS:{Prisma.RST} {', '.join(toxins)}")
        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}\n")

if __name__ == "__main__":
    engine = BonepokeChronos()
    while True:
        try:
            u = input(f"{Prisma.GRY}>{Prisma.RST} ")
            if u.lower() in ['exit', 'quit']: break
            engine.process(u)
        except KeyboardInterrupt: break
