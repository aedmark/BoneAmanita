# BONEAMANITA 2.5 - "CHRONOS"
# Architect: SLASH | Status: ALIVE
# "The Mandate is TRUTH. The Method is RHYTHM. The Anchor is TIME."

import re
import math
import time
import json
import os
import string
from collections import Counter

# --- THE PANTRY (HARDCODED LEXICON) ---
class BoneConfig:
    W_KINETIC = 2.0; W_STATIVE = 0.5; THRESHOLD_BOREDOM = 12.0

    HEAVY = {'stone', 'iron', 'mud', 'dirt', 'wood', 'clay', 'lead', 'bone', 'blood', 'root', 'ash', 'anchor', 'floor', 'meat', 'steel', 'gold', 'brass', 'rock', 'gravel', 'sand', 'cement', 'flesh', 'tooth', 'spine', 'rib', 'skulls', 'basalt', 'granite', 'oak', 'pine', 'metal', 'rust', 'salt'}
    AEROBIC = {'balloon', 'feather', 'cloud', 'mist', 'steam', 'breeze', 'wing', 'petal', 'light', 'ray', 'sky', 'ghost', 'echo', 'breath', 'gas', 'helium', 'air', 'smoke', 'vapor', 'dust', 'spark', 'shadow', 'void', 'dream', 'thought', 'mind', 'soul', 'spirit', 'shade', 'whisper', 'ozone'}
    HOT = {'fire', 'burn', 'flame', 'sun', 'heat', 'magma', 'scorch', 'boil', 'ember', 'ash', 'summer', 'noon', 'bright'}
    COLD = {'ice', 'snow', 'frost', 'freeze', 'chill', 'winter', 'glacier', 'void', 'numb', 'shiver', 'night', 'dark', 'cool'}
    KINETIC = {'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut', 'drive', 'lift', 'strike', 'burn', 'shatter', 'throw', 'kick', 'punch', 'grab', 'climb', 'jump', 'sprint', 'crawl', 'drag', 'push', 'pull', 'tear', 'rip', 'slice', 'crush', 'grind', 'slam', 'biff', 'pow'}
    PLAY = {'bounce', 'dance', 'twirl', 'float', 'wobble', 'tickle', 'jiggle', 'skip', 'hop', 'drift', 'slide', 'roll', 'spin', 'whirl', 'zig', 'zag', 'zoom', 'pop', 'snap', 'crackle', 'fizz', 'buzz', 'hum', 'wiggle'}
    ABSTRACT = {'system', 'protocol', 'sequence', 'context', 'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept', 'theory', 'analysis', 'nuance', 'paradigm', 'dimension', 'variable', 'function', 'aspect', 'mode', 'type', 'version', 'environment', 'situation', 'reality', 'nature', 'essence', 'basis'}
    SOLVENTS = {'basically', 'simply', 'actually', 'kind of', 'sort of', 'usually', 'often', 'perhaps', 'maybe', 'literally', 'essentially', 'generally', 'technically', 'virtually', 'practically', 'apparently', 'seemingly', 'presumably'}
    SYCOPHANCY = {'just', 'actually', 'maybe', 'perhaps', 'hopefully', 'possibly', 'sorry', 'try', 'believe', 'feel', 'think', 'little', 'bit'}
    CONNECTORS = {'and', 'but', 'or', 'so', 'yet', 'because', 'although', 'since', 'while', 'whereas'}

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
    def bar(val, max_val=1.0, width=10, color=WHT):
        filled = int((min(val, max_val) / max_val) * width)
        return f"{color}{'█' * filled}{Prisma.GRY}{'░' * (width - filled)}{Prisma.RST}"

# --- MEMORY & TIME (THE RESTORED SOUL) ---
class BoneMemory:
    FILE = "bone_memory.json"

    @staticmethod
    def load():
        if os.path.exists(BoneMemory.FILE):
            try:
                with open(BoneMemory.FILE, 'r') as f: return json.load(f)
            except: pass
        return {"atp": 33, "last_seen": time.time(), "history": [], "total_turns": 0}

    @staticmethod
    def save(state):
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

        for w in clean_words:
            if w in BoneConfig.KINETIC or w in BoneConfig.PLAY or w.endswith(self.suffixes['kinetic']): c['kinetic'] += 1
            if w in BoneConfig.HEAVY: c['heavy'] += 1
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

        return {
            "counts": c,
            "metrics": {
                "drag": round(narrative_drag, 2), "entropy": round(entropy, 2), "density": round(density, 2),
                "kinetic_ratio": round(c['kinetic'] / max(1, c['kinetic'] + c['stative']), 2),
                "toxin_score": toxin_score, "viscosity": visc_status, "spatial": c['spatial'] / total_words, "thermal": c['hot'] - c['cold']
            },
            "toxins": toxin_hits, "raw_text": raw_text
        }

# --- THE CHROMA LATTICE ---
class ApeirogonLattice:
    VEL_MAP = [(0.2, "Static", "Anchor"), (0.4, "Drifting", "Observer"), (0.6, "Walking", "Construct"), (0.8, "Running", "Engine"), (1.0, "Ballistic", "Vector")]
    ENT_MAP = [(0.2, "Literal", "Stone"), (0.4, "Grounded", "Root"), (0.6, "Conceptual", "Idea"), (0.8, "Abstract", "Dream"), (1.0, "Chaos", "Void")]
    TMP_MAP = [(-1.0, "Frozen", "Ice"), (0.0, "Room Temp", "Water"), (1.0, "Burning", "Fire")]

    @classmethod
    def resolve(cls, m):
        vel = min(1.0, m['kinetic_ratio'] * 1.5); ent = max(0.0, min(1.0, (m['entropy'] + 2) / 8.0))
        tex = min(1.0, m['density'] * 3.0); str_val = max(0.0, min(1.0, (5.0 - m['drag']) / 5.0))
        tmp = max(-1.0, min(1.0, m['thermal']))

        p_term = min(cls.VEL_MAP, key=lambda x: abs(x[0] - vel))
        s_term = min(cls.ENT_MAP, key=lambda x: abs(x[0] - ent))
        t_term = min(cls.TMP_MAP, key=lambda x: abs(x[0] - tmp))

        hud = [
            f"VEL: {Prisma.bar(vel, color=Prisma.CYN)} {vel:.1f} ({p_term[1]})", f"STR: {Prisma.bar(str_val, color=Prisma.BLU)} {str_val:.1f}",
            f"ENT: {Prisma.bar(ent, color=Prisma.MAG)} {ent:.1f} ({s_term[1]})", f"TEX: {Prisma.bar(tex, color=Prisma.YEL)} {tex:.1f}",
            f"TMP: {Prisma.bar((tmp+1)/2, color=Prisma.RED)} {tmp:.1f} ({t_term[1]})"
        ]
        return {"title": f"THE {s_term[1].upper()} {p_term[2].upper()}", "hud": hud}

# --- THE GUIDANCE SYSTEMS ---
class JadeLink:
    @staticmethod
    def generate(m, delta_status):
        if delta_status == "FOSSIL": return f"{Prisma.RED}[MODE: REBOOT] {Prisma.GRY}SYSTEM COLD. IGNORE CONTEXT.{Prisma.RST}"
        if m['viscosity'] == "CONCRETE" or m['drag'] > 3.5: return f"{Prisma.RED}[MODE: DEDUCTIVE] {Prisma.GRY}PATTERN: EDEN (Constraints Required){Prisma.RST}"
        elif m['entropy'] > 3.0 and m['density'] < 0.1: return f"{Prisma.CYN}[MODE: INDUCTIVE] {Prisma.GRY}PATTERN: TRIPLE (Grounding Required){Prisma.RST}"
        elif m['kinetic_ratio'] > 0.7: return f"{Prisma.MAG}[MODE: ABDUCTIVE] {Prisma.GRY}PATTERN: FRACTAL (Expansion Authorized){Prisma.RST}"
        return f"{Prisma.BLU}[MODE: OBSERVATION] {Prisma.GRY}PATTERN: STABLE{Prisma.RST}"

class RadioTuner:
    STATIONS = {
        'CLARENCE': {'freq': '88.5 FM', 'color': Prisma.RED, 'role': 'The Butcher', 'trigger': lambda m, c: m['drag'] > 3.5, 'msg': "Drag is {drag}. Cut the adverbs."},
        'ELOISE':   {'freq': '94.2 FM', 'color': Prisma.CYN, 'role': 'The Grounder', 'trigger': lambda m, c: m['entropy'] > 3.0, 'msg': "Too much sky. Plant a heavy noun."},
        'YAGA':     {'freq': '101.1 FM', 'color': Prisma.MAG, 'role': 'The Witch', 'trigger': lambda m, c: c['hedging'] > 1 or m['toxin_score'] > 0, 'msg': "You smell of sugar. Spit it out."}
    }
    @staticmethod
    def broadcast(m, c):
        active = [v for k,v in RadioTuner.STATIONS.items() if v['trigger'](m, c)]
        if not active: return None
        s = active[0]; return f"{s['color']}[{s['freq']}] {s['role']}: {s['msg'].format(**m)}{Prisma.RST}"

# --- MAIN SYSTEM ---
class BonepokeChronos:
    def __init__(self):
        self.mem = BoneMemory.load()
        self.physics = LinguisticPhysicsEngine()

        # Calculate Time Delta
        self.status, self.decay_penalty = BoneMemory.calc_delta(self.mem['last_seen'])
        self.mem['last_seen'] = time.time()

        print(f"{Prisma.GRN}>>> BONEAMANITA 2.5 [CHRONOS] ONLINE{Prisma.RST}")
        if self.status != "FLOW":
            print(f"{Prisma.YEL}>>> TIME GAP DETECTED: {self.status} (+{self.decay_penalty} Drag Penalty){Prisma.RST}")

    def process(self, text):
        data = self.physics.analyze(text)
        if not data: return
        m, c = data['metrics'], data['counts']

        # Apply Temporal Decay to Physics
        m['drag'] += self.decay_penalty

        chroma = ApeirogonLattice.resolve(m)
        radio = RadioTuner.broadcast(m, c)
        jade = JadeLink.generate(m, self.status)

        # Metabolism
        burn = int(m['drag'] * 2) if m['drag'] > 2 else -2
        self.mem['atp'] = max(0, min(100, self.mem['atp'] - burn))
        self.mem['total_turns'] += 1

        # History Tracking
        self.mem['history'].append({'arch': chroma['title'], 'drag': m['drag']})
        if len(self.mem['history']) > 5: self.mem['history'].pop(0)

        BoneMemory.save(self.mem)
        self._render(m, chroma, radio, jade, data['toxins'])

    def _render(self, m, chroma, radio, jade, toxins):
        atp_c = Prisma.GRN if self.mem['atp'] > 20 else Prisma.RED
        print(f"\n{Prisma.GRY}--------------------------------------------------{Prisma.RST}")
        print(f"{Prisma.WHT}BONEAMANITA 2.5{Prisma.RST} | ATP: {atp_c}{self.mem['atp']}{Prisma.RST} | DRAG: {m['drag']} | STATE: {self.status}")
        print(f"{Prisma.CYN}ARCHETYPE:{Prisma.RST} {Prisma.WHT}{chroma['title']}{Prisma.RST}")
        for bar in chroma['hud']: print(f"  {bar}")
        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}")
        print(f"📡 {radio}" if radio else f"🔮 {jade}")
        if toxins: print(f"{Prisma.RED}💀 TOXINS DETECTED:{Prisma.RST} {', '.join(toxins)}")
        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}\n")

if __name__ == "__main__":
    engine = BonepokeChronos()
    while True:
        try:
            u = input(f"{Prisma.GRY}>{Prisma.RST} ")
            if u.lower() in ['exit', 'quit']: break
            engine.process(u)
        except KeyboardInterrupt: break
