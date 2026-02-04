# BONEAMANITA 2.7.2 - "LAZARUS" (FINAL MERGE)
# Architect: SLASH | Curators: James Taylor & Andrew Edmark
# "The Mandate is TRUTH. The Method is ADAPTATION. The Metric is BETA."

import re
import math
import time
import json
import os
import string
import random
import hashlib
from collections import Counter

# --- THE PANTRY (HARDCODED LEXICON) ---
class BoneConfig:
    # The Matter
    HEAVY = {'stone', 'iron', 'mud', 'dirt', 'wood', 'clay', 'lead', 'bone', 'blood', 'root', 'ash', 'anchor', 'floor', 'meat', 'steel', 'gold', 'brass', 'rock', 'gravel', 'sand', 'cement', 'flesh', 'tooth', 'spine', 'rib', 'skull', 'basalt', 'granite', 'oak', 'pine', 'metal', 'rust', 'salt', 'glass', 'obsidian'}
    AEROBIC = {'balloon', 'feather', 'cloud', 'mist', 'steam', 'breeze', 'wing', 'petal', 'light', 'ray', 'sky', 'ghost', 'echo', 'breath', 'gas', 'helium', 'air', 'smoke', 'vapor', 'dust', 'spark', 'shadow', 'void', 'dream', 'thought', 'mind', 'soul', 'spirit', 'shade', 'whisper', 'ozone', 'ether'}
    HOT = {'fire', 'burn', 'flame', 'sun', 'heat', 'magma', 'scorch', 'boil', 'ember', 'ash', 'summer', 'noon', 'bright', 'sweat', 'fever', 'lava', 'explode', 'blast'}
    COLD = {'ice', 'snow', 'frost', 'freeze', 'chill', 'winter', 'glacier', 'void', 'numb', 'shiver', 'night', 'dark', 'cool', 'crypt', 'grave', 'absolute', 'zero'}

    # The Physics
    KINETIC = {'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut', 'drive', 'lift', 'strike', 'burn', 'shatter', 'throw', 'kick', 'punch', 'grab', 'climb', 'jump', 'sprint', 'crawl', 'drag', 'push', 'pull', 'tear', 'rip', 'slice', 'crush', 'grind', 'slam', 'biff', 'pow', 'scream', 'howl'}
    PLAY = {'bounce', 'dance', 'twirl', 'float', 'wobble', 'tickle', 'jiggle', 'skip', 'hop', 'drift', 'slide', 'roll', 'spin', 'whirl', 'zig', 'zag', 'zoom', 'pop', 'snap', 'crackle', 'fizz', 'buzz', 'hum', 'wiggle', 'jazz'}
    ABSTRACT = {'system', 'protocol', 'sequence', 'context', 'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept', 'theory', 'analysis', 'nuance', 'paradigm', 'dimension', 'variable', 'function', 'aspect', 'mode', 'type', 'version', 'environment', 'situation', 'reality', 'nature', 'essence', 'basis', 'strategy', 'optimization'}

    # The Solvents (Function words)
    SOLVENTS = {'basically', 'simply', 'actually', 'kind of', 'sort of', 'usually', 'often', 'perhaps', 'maybe', 'literally', 'essentially', 'generally', 'technically', 'virtually', 'practically', 'apparently', 'seemingly', 'presumably'}
    SYCOPHANCY = {'just', 'actually', 'maybe', 'perhaps', 'hopefully', 'possibly', 'sorry', 'try', 'believe', 'feel', 'think', 'little', 'bit', 'humbly', 'respectfully'}
    CONNECTORS = {'and', 'but', 'or', 'so', 'yet', 'because', 'although', 'since', 'while', 'whereas', 'therefore', 'however'}

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

# --- MEMORY & TIME ---
class BoneMemory:
    FILE = "bone_memory_lazarus.json"
    HEIRLOOM_CAP = 25
    # Weight Hierarchy: Higher number = Harder to burn
    WEIGHTS = {'HEAVY': 4, 'KINETIC': 3, 'HOT': 2, 'COLD': 2, 'ABSTRACT': 1, 'AEROBIC': 0}

    @staticmethod
    def load():
        default = {"atp": 33, "last_seen": time.time(), "heirlooms": [], "last_run_stats": None}
        if os.path.exists(BoneMemory.FILE):
            try:
                with open(BoneMemory.FILE, 'r') as f:
                    return {**default, **json.load(f)}
            except Exception as e:
                print(f"{Prisma.RED}⚠️ MEMORY CORRUPTION. RESETTING.{Prisma.RST}")
                return default
        return default

    @staticmethod
    def prioritize_heirlooms(heirlooms):
        """Sorts heirlooms by weight (ascending) so light things are at index 0 (to be popped)."""
        # Heirlooms are dicts: {'w': 'word', 't': 'TYPE'}
        return sorted(heirlooms, key=lambda x: BoneMemory.WEIGHTS.get(x.get('t'), 1))

    @staticmethod
    def save(state):
        # Sort by weight so we drop the light stuff if we exceed CAP
        sorted_loot = BoneMemory.prioritize_heirlooms(state['heirlooms'])
        # Keep the heaviest/best ones up to the CAP (slice from end)
        if len(sorted_loot) > BoneMemory.HEIRLOOM_CAP:
            state['heirlooms'] = sorted_loot[-BoneMemory.HEIRLOOM_CAP:]

        with open(BoneMemory.FILE, 'w') as f:
            json.dump(state, f)

    @staticmethod
    def calc_delta(last_seen):
        delta = time.time() - last_seen
        if delta > 86400: return "FOSSIL", 2.0
        if delta > 3600: return "DECAY", 0.5
        return "WARM", 0.0

# --- THE PHYSICS ENGINE ---
class LinguisticPhysicsEngine:
    def __init__(self):
        self.suffixes = {'abstract': ('ness', 'ity', 'tion', 'ment', 'ism', 'ence', 'logy'),
                         'kinetic': ('ing',),
                         'adj': ('ful', 'ous', 'ive', 'ic', 'al', 'ish', 'ary')}
        self.stative = {'is', 'are', 'was', 'were', 'be', 'being', 'been', 'have', 'has', 'seem', 'feel'}
        # LAZARUS UPDATE: Regex tokenizer to preserve soul
        self.tokenizer = re.compile(r"[\w']+|[?!,;]")

    def analyze(self, raw_text):
        tokens = self.tokenizer.findall(raw_text.lower())
        total_tokens = len(tokens)
        if total_tokens == 0: return None

        c = Counter()
        c['abstract_set'] = set()
        new_heirlooms = []

        for w in tokens:
            # Categorization
            if w in BoneConfig.HEAVY:
                c['heavy'] += 1
                new_heirlooms.append({'w': w, 't': 'HEAVY'})

            # Pinker Hierarchy
            if w in BoneConfig.KINETIC or w.endswith(self.suffixes['kinetic']):
                c['kinetic'] += 1
                new_heirlooms.append({'w': w, 't': 'KINETIC'})
            elif w in BoneConfig.PLAY:
                c['play'] += 1
                c['kinetic'] += 0.5 # Play contributes to motion
                new_heirlooms.append({'w': w, 't': 'AEROBIC'})

            if w in BoneConfig.AEROBIC: c['aerobic'] += 1
            if w in BoneConfig.SOLVENTS: c['solvent'] += 1
            if w in BoneConfig.CONNECTORS: c['connector'] += 1
            if w in self.stative: c['stative'] += 1
            if w in BoneConfig.SYCOPHANCY: c['hedging'] += 1
            if w in BoneConfig.HOT: c['hot'] += 1
            if w in BoneConfig.COLD: c['cold'] += 1

            is_abstract = w in BoneConfig.ABSTRACT or w.endswith(self.suffixes['abstract'])
            if is_abstract:
                c['abstract'] += 1
                c['abstract_set'].add(w)

            if w.endswith('ly') and w not in BoneConfig.SOLVENTS: c['adverb'] += 1
            if w.endswith(self.suffixes['adj']): c['adjective'] += 1

        toxin_score = 0.0; toxin_hits = []
        for match in BoneConfig.TOXIN_REGEX.findall(raw_text):
            phrase = match.lower()
            weight = BoneConfig.TOXINS.get(phrase, 3.0)
            toxin_score += weight
            toxin_hits.append(phrase)

        # Physics Calculations
        # Avoid ZeroDivision
        safe_total = max(1, total_tokens)

        density = c['heavy'] / safe_total
        hydration = c['solvent'] / safe_total
        hydro_penalty = 4.0 if hydration > 0.35 else (5.0 if density > 0.25 and hydration < 0.05 else 0.0)
        visc_status = "FLOODED" if hydration > 0.35 else ("CONCRETE" if density > 0.25 and hydration < 0.05 else "OPTIMAL")

        garnish_load = c['adverb'] + (c['adjective'] * 0.8)
        butcher_penalty = 3.0 if (garnish_load / safe_total) > 0.18 else 0.0

        action_score = (c['kinetic'] * 2.0) + (c['stative'] * 0.5) + 1.0
        base_drag = (safe_total + (toxin_score * 5.0)) / action_score
        narrative_drag = base_drag + hydro_penalty + butcher_penalty

        abstract_repetition = c['abstract'] - len(c['abstract_set'])
        entropy = c['abstract'] + (abstract_repetition * 2) - c['heavy']

        # BETA FRICTION (Voltage)
        voltage = (c['hot'] + c['cold']) + (c['kinetic'] * 0.5)
        beta = voltage / max(0.1, narrative_drag)

        # Vectors
        vel = min(1.0, (c['kinetic'] / max(1, c['kinetic'] + c['stative'])) * 1.5)
        tex = min(1.0, density * 3.0)
        ent = max(0.0, min(1.0, (entropy + 2) / 8.0))
        buoyancy = (c['aerobic'] + c['play']) / safe_total

        return {
            "counts": c,
            "metrics": {
                "drag": round(narrative_drag, 2), "entropy": round(entropy, 2),
                "beta": round(beta, 2), "voltage": round(voltage, 2),
                "buoyancy": round(buoyancy, 2), "hedging_count": c['hedging'],
                "viscosity": visc_status, "VEL": vel, "TEX": tex, "ENT": ent
            },
            "toxins": toxin_hits,
            "new_heirlooms": new_heirlooms
        }

# --- THE CHROMA LATTICE ---
class ApeirogonLattice:
    @staticmethod
    def resolve_title(vel, ent, beta):
        if beta > 2.0: return f"THE {Prisma.MAG}VOLATILE{Prisma.WHT} PARADOX"
        if vel > 0.7: p = "ENGINE" if ent < 0.5 else "VECTOR"
        elif vel > 0.4: p = "CONSTRUCT" if ent < 0.5 else "IDEA"
        else: p = "ANCHOR" if ent < 0.5 else "GHOST"
        s = "ABSTRACT" if ent > 0.7 else ("CONCEPTUAL" if ent > 0.4 else "LITERAL")
        return f"THE {s} {p}"

# --- THE GUIDANCE SYSTEMS (JADE LINK) ---
class JadeLink:
    @staticmethod
    def generate(m, delta_status, toxin_list):
        # 1. Initialize Scoreboard
        scores = {
            "JESTER": 0,    # Paradox / High Voltage
            "YAGA": 0,      # Sycophancy / Slickness
            "CLARENCE": 0,  # Butcher / High Drag
            "ELOISE": 0,    # Grounding / Confusion
            "DRIFTER": 0,   # Poetry / High Buoyancy
            "MICHAEL": 1    # Baseline Stability
        }

        # 2. Calculate Weights (The Barbarian's Logic)
        if m['beta'] > 1.5: scores['JESTER'] += 2
        if m['beta'] > 2.5: scores['JESTER'] += 3

        if m['drag'] > 3.0: scores['CLARENCE'] += 3
        if toxin_list: scores['CLARENCE'] += len(toxin_list) * 2
        if m['viscosity'] == "CONCRETE": scores['CLARENCE'] += 2

        if m['beta'] < 0.2: scores['YAGA'] += 3
        if m['hedging_count'] > 1: scores['YAGA'] += 2

        if m['entropy'] > 2.5:
            if m['buoyancy'] > 0.15: scores['DRIFTER'] += 4
            else: scores['ELOISE'] += 4

        if delta_status == "FOSSIL":
            return "REBOOT", f"{Prisma.RED}>>> [SYSTEM COLD]:{Prisma.RST} I am freezing. Reboot me with high-energy input."

        # 3. Determine Winner
        winner = max(scores, key=scores.get)
        return JadeLink.render_voice(winner, m, toxin_list)

    @staticmethod
    def render_voice(archetype, m, toxins):
        if archetype == "CLARENCE":
            target = f"'{toxins[0]}'" if toxins else "the adjective pile"
            return "CLARENCE", f"{Prisma.RED}>>> [CLARENCE]:{Prisma.RST} Drag is {m['drag']}. I am cutting {target}."
        elif archetype == "JESTER":
            return "JESTER", f"{Prisma.MAG}>>> [JESTER]:{Prisma.RST} β:{m['beta']}. Chaos is good. Twist it further."
        elif archetype == "DRIFTER":
            return "DRIFTER", f"{Prisma.CYN}>>> [DRIFTER]:{Prisma.RST} We are floating (Buoy: {m['buoyancy']}). Don't look down."
        elif archetype == "ELOISE":
            return "ELOISE", f"{Prisma.CYN}>>> [ELOISE]:{Prisma.RST} Too abstract (Ent: {m['entropy']}). Give me a stone."
        elif archetype == "YAGA":
            return "YAGA", f"{Prisma.RED}>>> [THE YAGA]:{Prisma.RST} You are sliding on grease. Stop hedging."

        return "MICHAEL", f"{Prisma.BLU}>>> [MICHAEL]:{Prisma.RST} Systems nominal."

# --- MAIN SYSTEM ---
class BonepokeChronos:
    def __init__(self):
        self.mem = BoneMemory.load()
        self.physics = LinguisticPhysicsEngine()
        self.status, self.decay_penalty = BoneMemory.calc_delta(self.mem['last_seen'])
        self.mem['last_seen'] = time.time()
        self.last_heirlooms = set()

        print(f"{Prisma.GRN}>>> BONEAMANITA 2.7.2 [LAZARUS] ONLINE{Prisma.RST}")
        if self.status in ["DECAY", "FOSSIL"] and self.mem['heirlooms']:
            # Burn the lightest memory
            burnt = self.mem['heirlooms'][0]['w'] # Prioritize_heirlooms puts light first
            self.mem['heirlooms'].pop(0)
            print(f"{Prisma.RED}🔥 MEMORY BURN:{Prisma.RST} I burned '{burnt}' to stay warm.")

        if self.mem.get('last_run_stats'):
            print(f"{Prisma.GRY}>>> GHOST LOOP STANDBY.{Prisma.RST}")

    def get_user_id(self, text):
        return hashlib.md5(text[:20].encode()).hexdigest()[:6]

    def check_continuity(self, current_heirlooms_set):
        if not self.last_heirlooms: return 0.0
        intersection = len(current_heirlooms_set.intersection(self.last_heirlooms))
        union = len(current_heirlooms_set.union(self.last_heirlooms))
        return intersection / max(1, union)

    def process(self, text):
        user_id = self.get_user_id(text)
        data = self.physics.analyze(text)

        if not data: return
        m = data['metrics']

        # Continuity Check
        current_heirlooms_set = set(item['w'] for item in data['new_heirlooms'])
        continuity_score = self.check_continuity(current_heirlooms_set)

        # Energy Dynamics
        energy_cost = int(m['drag'] * 3) if m['drag'] > 3.0 else 2
        flow_bonus = 5 if continuity_score > 0.3 else 0
        buoy_bonus = int(m['buoyancy'] * 10)

        self.mem['atp'] = max(0, min(100, self.mem['atp'] - energy_cost + flow_bonus + buoy_bonus))

        # Update State
        self.last_heirlooms = current_heirlooms_set
        self.mem['heirlooms'].extend(data['new_heirlooms'])
        self.mem['last_run_stats'] = {'drag': m['drag']}

        # Strategy Generation
        strat_name, strat_msg = JadeLink.generate(m, self.status, data['toxins'])

        # Save
        BoneMemory.save(self.mem)

        # Render
        title = ApeirogonLattice.resolve_title(m['VEL'], m['ENT'], m['beta'])
        self._render(m, title, strat_msg, data['toxins'])
        print(f"Ω (Continuity): {continuity_score:.2f} | User: {user_id}")

    def _render(self, m, title, strat_msg, toxins):
        atp_c = Prisma.GRN if self.mem['atp'] > 20 else Prisma.RED

        if m['beta'] > 2.0: beta_c = f"{Prisma.MAG}⚡{m['beta']}{Prisma.RST}"
        elif m['beta'] < 0.1: beta_c = f"{Prisma.RED}⚠️{m['beta']}{Prisma.RST}"
        else: beta_c = f"{Prisma.CYN}{m['beta']}{Prisma.RST}"

        print(f"\n{Prisma.GRY}--------------------------------------------------{Prisma.RST}")
        print(f"{Prisma.WHT}BONEAMANITA 2.7.2 (LAZARUS){Prisma.RST} | ATP: {atp_c}{self.mem['atp']}{Prisma.RST} | DRAG: {m['drag']} | BUOY: {m['buoyancy']}")
        print(f"{Prisma.CYN}ARCHETYPE:{Prisma.RST} {Prisma.WHT}{title}{Prisma.RST}")
        print(f"VEL: {Prisma.bar(m['VEL'], color=Prisma.CYN)} | TEX: {Prisma.bar(m['TEX'], color=Prisma.YEL)} | ENT: {Prisma.bar(m['ENT'], color=Prisma.MAG)}")
        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}")
        print(f"📡 {strat_msg}")
        if toxins: print(f"{Prisma.RED}💀 TOXINS:{Prisma.RST} {', '.join(toxins)}")
        print(f"{Prisma.CYN}DYNAMICS:{Prisma.RST} β: {beta_c} | Visc: {m['viscosity']}")
        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}\n")

if __name__ == "__main__":
    engine = BonepokeChronos()
    while True:
        try:
            u = input(f"{Prisma.GRY}>{Prisma.RST} ")
            if u.lower() in ['exit', 'quit']: break
            engine.process(u)
        except KeyboardInterrupt: break
