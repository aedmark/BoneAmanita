# BONEAMANITA 3.0 - "THE CHIMERA"
# Architect: SLASH
# "The Mandate is TRUTH. The Method is SURGERY."

import re
import time
import json
import os
from collections import Counter

# --- 1. THE CONFIG & LEXICON ---
class BoneConfig:
    HEAVY = {'stone', 'iron', 'mud', 'dirt', 'wood', 'clay', 'lead', 'bone', 'blood', 'root', 'ash', 'anchor', 'floor', 'meat', 'steel', 'gold', 'brass', 'rock', 'gravel', 'sand', 'cement', 'flesh', 'tooth', 'spine', 'rib', 'skull', 'basalt', 'granite', 'oak', 'pine', 'metal', 'rust', 'salt', 'glass', 'obsidian'}
    KINETIC = {'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut', 'drive', 'lift', 'strike', 'burn', 'shatter', 'throw', 'kick', 'punch', 'grab', 'climb', 'jump', 'sprint', 'crawl', 'drag', 'push', 'pull', 'tear', 'rip', 'slice', 'crush', 'grind', 'slam'}
    ABSTRACT = {'system', 'protocol', 'sequence', 'context', 'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept', 'theory', 'analysis', 'nuance', 'paradigm', 'dimension', 'variable', 'function', 'aspect', 'mode', 'type', 'version', 'environment', 'situation', 'reality', 'nature', 'essence'}
    PHOTOSYNTHETICS = {'sun', 'beam', 'glow', 'shine', 'fire', 'flame', 'star', 'dawn', 'gold', 'glimmer', 'prism', 'bloom', 'neon', 'laser', 'flash', 'bright', 'radiant', 'summer', 'solar'}

    # THE TOXIN MAP (Phrase -> Weight, Replacement)
    TOXINS = {
        'synergy': (5.0, 'cooperation'), 'leverage': (5.0, 'use'), 'circle back': (4.0, 'return'),
        'drill down': (4.0, 'examine'), 'paradigm shift': (5.0, 'change'), 'game changer': (4.0, 'important'),
        'low hanging fruit': (5.0, 'easy work'), 'bandwidth': (4.0, 'time'), 'deliverables': (4.0, 'work'),
        'actionable': (4.0, 'useful'), 'ecosystem': (3.0, 'group'), 'holistic': (4.0, 'whole'),
        'utilize': (3.0, 'use'), 'in order to': (2.0, 'to'), 'at the end of the day': (3.0, 'finally'),
        'literally': (3.0, ''), 'basically': (3.0, ''), 'essentially': (3.0, ''), 'actually': (3.0, '')
    }
    TOXIN_REGEX = None

    @classmethod
    def compile(cls):
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted(cls.TOXINS.keys(), key=len, reverse=True)) + r')\b'
        cls.TOXIN_REGEX = re.compile(pattern_str, re.IGNORECASE)

BoneConfig.compile()

# --- 2. THE MEMORY (New Feature) ---
class BoneMemory:
    FILE = "bone_amanita_state.json"

    @staticmethod
    def load():
        default = {"atp": 33, "spores": 0, "total_words": 0, "last_session": time.time()}
        if os.path.exists(BoneMemory.FILE):
            try:
                with open(BoneMemory.FILE, 'r') as f:
                    data = json.load(f)
                    # Decay Logic: If gone > 24h, lose ATP
                    hours_gone = (time.time() - data.get('last_session', time.time())) / 3600
                    if hours_gone > 24: data['atp'] = max(0, data['atp'] - int(hours_gone))
                    return {**default, **data}
            except: pass
        return default

    @staticmethod
    def save(state):
        state['last_session'] = time.time()
        with open(BoneMemory.FILE, 'w') as f:
            json.dump(state, f)

# --- 3. THE SURGICAL SUITE (New Feature) ---
class SurgicalSuite:
    """
    The Auto-Corrector. Deterministic text replacement based on Physics.
    """
    @staticmethod
    def operate(text, m):
        # 1. Toxin Removal (The Antidote)
        clean_text = text
        corrections = []

        # Replace Toxins using the Map
        def replacer(match):
            word = match.group(0).lower()
            replacement = BoneConfig.TOXINS.get(word, (0, ''))[1]
            corrections.append(f"{word} -> {replacement or '[CUT]'}")
            return replacement

        clean_text = BoneConfig.TOXIN_REGEX.sub(replacer, clean_text)

        # 2. Adverbctomy (The Butcher)
        # If Drag is high, we cut adverbs ending in 'ly'
        if m['drag'] > 2.5:
            # Look for words ending in ly that aren't in a safe list (simplified)
            # We construct a new regex for adverbs on the fly
            adverb_pattern = re.compile(r'\b(\w+ly)\b', re.IGNORECASE)
            matches = adverb_pattern.findall(clean_text)
            for adv in matches:
                # Basic filter: if it's > 4 chars, likely an adverb.
                if len(adv) > 4 and adv not in {'only', 'family', 'rely'}:
                    clean_text = clean_text.replace(adv, "")
                    corrections.append(f"{adv} -> [CUT]")

        # Cleanup double spaces created by deletions
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return clean_text, corrections

# --- 4. PHYSICS & VECTORS (From 3.0) ---
class VectorPhysicsEngine:
    def __init__(self): self.tokenizer = re.compile(r"[\w']+|[?!,;]")
    def analyze(self, raw_text):
        tokens = self.tokenizer.findall(raw_text.lower())
        if not tokens: return None
        c = Counter()
        for w in tokens:
            if w in BoneConfig.HEAVY: c['heavy'] += 1
            if w in BoneConfig.KINETIC or w.endswith('ing'): c['kinetic'] += 1
            if w.endswith(('ness', 'ity', 'tion', 'ment', 'ism')): c['abstract'] += 1
            if w in BoneConfig.PHOTOSYNTHETICS: c['photosynthetic'] += 1
            if w.endswith('ly'): c['adverb'] += 1

        toxin_score = sum(BoneConfig.TOXINS.get(match.lower(), (0,0))[0] for match in BoneConfig.TOXIN_REGEX.findall(raw_text))

        action = (c['kinetic'] * 2.0) + 1.0
        drag = (len(tokens) + (toxin_score * 5.0)) / action
        if (c['adverb'] / len(tokens)) > 0.15: drag += 2.0

        voltage = (c['kinetic'] * 0.5) + (c['heavy'] * 0.2) + (toxin_score * -1.0)
        beta = max(0.1, voltage) / max(0.1, drag)

        vec = {
            "VEL": round(min(1.0, (c['kinetic']/max(1, len(tokens)))*3), 2),
            "STR": round(max(0.0, min(1.0, (5.0 - drag) / 5.0)), 2),
            "ENT": round(max(0.0, min(1.0, c['abstract'] / max(1, c['heavy']))), 2),
            "TEX": round(min(1.0, (c['heavy']/max(1, len(tokens)))*3), 2)
        }
        return {"counts": c, "total_words": len(tokens), "drag": round(drag, 2), "beta": round(beta, 2), "vec": vec, "toxin_hits": toxin_score}

# --- 5. JADE LINK (Voices) ---
class JadeLink_FM:
    STATIONS = {
        "CLARENCE": {"freq": "88.5 FM", "color": "\033[91m", "role": "The Butcher"},
        "ELOISE":   {"freq": "94.2 FM", "color": "\033[96m", "role": "The Grounder"},
        "YAGA":     {"freq": "101.1 FM", "color": "\033[95m", "role": "The Witch"},
        "DRIFTER":  {"freq": "104.5 FM", "color": "\033[94m", "role": "The Vector"},
        "JESTER":   {"freq": "108.0 FM", "color": "\033[93m", "role": "The Paradox"}
    }
    @staticmethod
    def broadcast(m, atp):
        s = {k: 0 for k in JadeLink_FM.STATIONS}
        if m['drag'] > 3.0 or atp < 20: s['CLARENCE'] += 5
        if m['vec']['ENT'] > 0.6: s['ELOISE'] += 4
        if m['toxin_hits'] > 0: s['YAGA'] += 4
        if m['beta'] > 2.0: s['JESTER'] += 3
        if m['beta'] > 0.5 and m['drag'] < 2.0: s['DRIFTER'] += 2

        winner = max(s, key=s.get)
        st = JadeLink_FM.STATIONS[winner]
        msg = "Systems Nominal."
        if winner == "CLARENCE": msg = f"Drag is {m['drag']}. I am cutting the fat."
        elif winner == "ELOISE": msg = f"Too abstract (Ent: {m['vec']['ENT']}). Grounding required."
        elif winner == "YAGA": msg = "Toxins detected. Purging lies."
        elif winner == "JESTER": msg = f"High Voltage ({m['beta']}). Riding the wave."
        elif winner == "DRIFTER": msg = "Vector optimized."

        return winner, f"{st['color']}[{st['freq']}] {st['role']}:\033[0m {msg}"

# --- 6. CORE ---
class BoneAmanita31:
    def __init__(self):
        self.mem = BoneMemory.load()
        self.phys = VectorPhysicsEngine()
        print(f"\033[97m>>> BONEAMANITA 3.0 [THE CHIMERA] ONLINE (ATP: {self.mem['atp']})\033[0m")

    def process(self, text):
        d = self.phys.analyze(text)
        if not d: return

        # State Update
        self.mem['total_words'] += d['total_words']
        if d['counts']['photosynthetic']: self.mem['atp'] += d['counts']['photosynthetic']
        if d['beta'] < 0.5: self.mem['spores'] += 1
        else: self.mem['spores'] = max(0, self.mem['spores'] - 1)

        # Save
        BoneMemory.save(self.mem)

        # Broadcast & Surgery
        arch, sig = JadeLink_FM.broadcast(d, self.mem['atp'])
        fixed_text, ops = SurgicalSuite.operate(text, d)

        self._render(d, sig, fixed_text, ops)

    def _render(self, d, sig, fixed, ops):
        R, G, C, W, RST = "\033[91m", "\033[92m", "\033[96m", "\033[97m", "\033[0m"
        print(f"\n{RST}--------------------------------------------------")
        print(f"{W}STATUS{RST} | ATP: {self.mem['atp']} | β: {C}{d['beta']}{RST} | DRAG: {d['drag']}")
        print(f"VECTOR: [V:{d['vec']['VEL']} S:{d['vec']['STR']} E:{d['vec']['ENT']} T:{d['vec']['TEX']}]")
        print(f"📡 {sig}")

        if ops:
            print(f"{R}🔪 SURGICAL INTERVENTION:{RST}")
            for op in ops: print(f"   └─ {op}")
            print(f"{G}>>> {fixed}{RST}")
        print(f"{RST}--------------------------------------------------\n")

if __name__ == "__main__":
    eng = BoneAmanita31()
    # Test case with Toxins and Adverbs
    eng.process("Essentially, we need to leverage the synergy to literally drive the solution forward rapidly.")
