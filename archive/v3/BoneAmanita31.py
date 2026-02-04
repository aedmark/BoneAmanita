# BONEAMANITA 3.1 - "THE UNICORN"
# Synthesis: SLASH | Base: v2.2 | Upgrade: v3.0
# "The Mandate is TRUTH. The Method is SYNTHESIS."

import time
import math
import random
from collections import Counter
from uuid import uuid4
import re
import json
import os
import string
import shutil

# --- 1. THE CONFIGURATION (Unified) ---
class BoneConfig:
    """
    Consolidated Constants from v2.2 and v3.0.
    """
    # [PHYSICS 2.2]
    ACTION_KINETIC_WEIGHT = 2.0
    TOXICITY_DRAG_MULTIPLIER = 10.0
    BOREDOM_THRESHOLD = 11.0
    FLASHPOINT_THRESHOLD = 2.5

    # [THE BUTCHER 3.0]
    # Maps toxic phrases to (Weight, Replacement)
    TOXIN_MAP = {
        'synergy': (5.0, 'cooperation'), 'leverage': (5.0, 'use'), 'circle back': (4.0, 'return'),
        'drill down': (4.0, 'examine'), 'paradigm shift': (5.0, 'change'), 'game changer': (4.0, 'important'),
        'low hanging fruit': (5.0, 'easy work'), 'bandwidth': (4.0, 'time'), 'deliverables': (4.0, 'work'),
        'actionable': (4.0, 'useful'), 'ecosystem': (3.0, 'group'), 'holistic': (4.0, 'whole'),
        'utilize': (3.0, 'use'), 'in order to': (2.0, 'to'), 'at the end of the day': (3.0, 'finally'),
        'literally': (3.0, ''), 'basically': (3.0, ''), 'essentially': (3.0, ''), 'actually': (3.0, ''),
        'ghost in the machine': (10.0, '[CLICHÉ]'), 'rubber meets the road': (10.0, '[CLICHÉ]')
    }

    TOXIN_REGEX = None

    @classmethod
    def compile(cls):
        # Compiles the efficient regex for 3.0 Surgical Suite
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted(cls.TOXIN_MAP.keys(), key=len, reverse=True)) + r')\b'
        cls.TOXIN_REGEX = re.compile(pattern_str, re.IGNORECASE)

BoneConfig.compile()

class Prisma:
    """The Technicolor Membrane (v2.2 Style)."""
    RST = "\033[0m"
    RED = "\033[91m" # Butcher / Drag
    GRN = "\033[92m" # Growth / Velocity
    YEL = "\033[93m" # Warning / Voltage
    BLU = "\033[94m" # Structure
    MAG = "\033[95m" # Magic / Flashpoint
    CYN = "\033[96m" # Systems / Ice
    WHT = "\033[97m" # Bone
    GRY = "\033[90m" # Metadata

    @staticmethod
    def wrap(val, limit, invert=False):
        bad = val > limit
        if invert: return f"{Prisma.GRN}{val}{Prisma.RST}" if bad else f"{Prisma.RED}{val}{Prisma.RST}"
        return f"{Prisma.RED}{val}{Prisma.RST}" if bad else f"{Prisma.GRN}{val}{Prisma.RST}"

# --- 2. THE LEXICON (v2.2 Base) ---
class TheLexicon:
    HEAVY_MATTER = {'stone', 'iron', 'mud', 'dirt', 'wood', 'grain', 'clay', 'lead', 'bone', 'blood', 'salt', 'rust', 'root', 'ash', 'anchor', 'floor', 'meat', 'steel', 'gold'}
    KINETIC_VERBS = {'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut', 'drive', 'lift', 'carry', 'strike', 'burn', 'shatter', 'throw', 'kick', 'pull'}
    ABSTRACTS = {'system', 'protocol', 'sequence', 'vector', 'node', 'context', 'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept', 'theory', 'analysis'}
    PHOTOSYNTHETICS = {'light', 'sun', 'ray', 'beam', 'glow', 'shine', 'spark', 'fire', 'flame', 'star', 'day', 'dawn', 'neon', 'laser'}
    SOLVENTS = {'basically', 'simply', 'actually', 'kind of', 'sort of', 'usually', 'often', 'perhaps', 'maybe', 'technically', 'honestly'}

    @staticmethod
    def clean(text):
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        return text.lower().translate(translator).split()

# --- 3. THE SURGICAL SUITE (v3.0 Import) ---
class SurgicalSuite:
    """
    The deterministic intervention engine from v3.0.
    It doesn't just critique; it fixes.
    """
    @staticmethod
    def operate(raw_text, metrics):
        corrections = []
        clean_text = raw_text

        # 1. TOXIN ANTIDOTE (Deterministic Replacement)
        def replacer(match):
            word = match.group(0).lower()
            if word in BoneConfig.TOXIN_MAP:
                weight, replacement = BoneConfig.TOXIN_MAP[word]
                corrections.append(f"{Prisma.RED}{word}{Prisma.RST} -> {Prisma.GRN}{replacement or '[CUT]'}{Prisma.RST}")
                return replacement
            return match.group(0)

        clean_text = BoneConfig.TOXIN_REGEX.sub(replacer, clean_text)

        # 2. ADVERBCTOMY (Conditional Logic)
        # Only activate the Butcher if Drag > 2.5
        phys = metrics['physics']
        if phys['narrative_drag'] > 2.5:
            adverb_pattern = re.compile(r'\b(\w+ly)\b', re.IGNORECASE)

            def adv_cut(match):
                word = match.group(0)
                # Protect short words or solvents explicitly handled
                if len(word) > 4 and word.lower() not in {'only', 'family', 'early'}:
                    corrections.append(f"{Prisma.RED}{word}{Prisma.RST} -> {Prisma.RED}[CUT]{Prisma.RST}")
                    return ""
                return word

            clean_text = adverb_pattern.sub(adv_cut, clean_text)

        # Cleanup whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return clean_text, corrections

# --- 4. PHYSICS ENGINE (v2.2 Base) ---
class PhysicsEngine:
    def __init__(self):
        self.surg = SurgicalSuite() # Integrated Suite

    def analyze(self, text):
        clean_words = TheLexicon.clean(text)
        total = len(clean_words)
        if total == 0: return self._void_metrics()

        counts = Counter()
        toxin_score = 0

        # 1. Metrics Calculation (v2.2 Logic)
        for w in clean_words:
            if w in TheLexicon.HEAVY_MATTER: counts['heavy'] += 1
            if w in TheLexicon.KINETIC_VERBS or w.endswith('ing'): counts['kinetic'] += 1
            if w in TheLexicon.ABSTRACTS or w.endswith(('ness', 'ity', 'tion', 'ment')): counts['abstract'] += 1
            if w in TheLexicon.PHOTOSYNTHETICS: counts['photo'] += 1

        # Toxin Scan using 3.0 Map
        matches = BoneConfig.TOXIN_REGEX.findall(text)
        toxin_score = sum(BoneConfig.TOXIN_MAP.get(m.lower(), (0,0))[0] for m in matches)

        # Physics Formulas
        action = (counts['kinetic'] * 2.0) + 1.0
        base_drag = (total + (toxin_score * 5.0)) / action

        # Narrative Drag
        drag = base_drag + (2.0 if (counts['abstract'] / total) > 0.3 else 0)

        # Beta Friction (Voltage / Drag)
        voltage = (counts['kinetic'] * 0.5) + (counts['heavy'] * 0.2) + (toxin_score * -1.0)
        beta = voltage / max(0.1, drag)

        # Apeirogon Vectors (v2.2 / v3.0 Hybrid)
        vec = {
            "VEL": round(min(1.0, (counts['kinetic']/max(1, total))*3), 2),
            "STR": round(max(0.0, min(1.0, (5.0 - drag) / 5.0)), 2),
            "ENT": round(max(0.0, min(1.0, counts['abstract'] / max(1, counts['heavy']))), 2),
            "TEX": round(min(1.0, (counts['heavy']/max(1, total))*3), 2)
        }

        return {
            "physics": {
                "narrative_drag": round(drag, 2),
                "beta_friction": round(beta, 2),
                "kinetic_ratio": round(counts['kinetic'] / total, 2),
                "toxicity_score": toxin_score,
                "counts": counts,
                "vector": vec
            },
            "clean_words": clean_words,
            "raw_text": text
        }

    def _void_metrics(self):
        return {"physics": {"narrative_drag": 0, "beta_friction": 0, "vector": {"VEL":0,"STR":0,"ENT":0,"TEX":0}}}

# --- 5. SYSTEMS (The Synthesis) ---

class DeepStorage:
    """v2.2 Memory System: Artifacts & Cannibalism."""
    def __init__(self):
        self.artifacts = {}
        self.capacity = 50

    def bury(self, words, tick):
        for w in words:
            if w in TheLexicon.HEAVY_MATTER and w not in self.artifacts:
                if len(self.artifacts) >= self.capacity: self.artifacts.pop(next(iter(self.artifacts)))
                self.artifacts[w] = tick

    def cannibalize(self):
        if not self.artifacts: return None
        target = min(self.artifacts, key=self.artifacts.get)
        del self.artifacts[target]
        return target

class MetabolicReserve:
    """v2.2 Metabolism + v3.0 Decay Logic."""
    def __init__(self):
        self.atp = 33
        self.max = 52
        self.status = "STABLE"

    def metabolize(self, metrics, deep_storage):
        phys = metrics['physics']
        drag = phys['narrative_drag']
        beta = phys.get('beta_friction', 0)

        delta = 0
        msg = None

        # 1. Flashpoint (Insight)
        if beta > BoneConfig.FLASHPOINT_THRESHOLD:
            delta = 20
            self.status = "FLASHPOINT"
            msg = f"{Prisma.MAG}⚡ FLASHPOINT DETECTED (β: {beta}){Prisma.RST}"

        # 2. Photosynthesis
        elif phys['counts'].get('photo', 0) > 0:
            gain = phys['counts']['photo'] * 2
            delta = gain
            msg = f"{Prisma.GRN}☀️ PHOTOSYNTHESIS (+{gain}){Prisma.RST}"

        # 3. Drag Tax
        elif drag > 3.0:
            delta = -2
            self.status = "STRAINING"

        # 4. Cannibalism (Survival)
        if self.atp + delta <= 0 and deep_storage:
            memory = deep_storage.cannibalize()
            if memory:
                delta += 10
                msg = f"{Prisma.RED}🔥 STARVATION PROTOCOL: Consumed memory '{memory}'{Prisma.RST}"

        self.atp = max(0, min(self.max, self.atp + delta))
        return msg

class WisdomNode:
    """
    v3.1 Refined: Target-Aware Strategy.
    Integrates the 'Frequency Modulator' logic from v2.2 into the prompt architecture.
    """
    def __init__(self):
        # The Voices of the Machine
        self.VOICES = {
            'CLARENCE': "THE BUTCHER. The text is obese. Your job is to cut.",
            'ELOISE': "THE GROUNDER. The text is floating away. Force it to touch the floor.",
            'YAGA': "THE WITCH. The user is lying or hedging. Demand the truth.",
            'JESTER': "THE PARADOX. The user has found a friction point. Amplify it.",
            'DRIFTER': "THE VECTOR. High velocity detected. Remove friction."
        }

    def _find_target(self, clean_words, category):
        """Locates the heaviest offender in the list for specific targeting."""
        if category == 'ABSTRACT':
            # Find the longest abstract word
            candidates = [w for w in clean_words if w.endswith(('ness', 'ity', 'tion', 'ment', 'ism'))]
            return max(candidates, key=len) if candidates else "concepts"
        elif category == 'WEAK':
            # Find hedging words
            candidates = [w for w in clean_words if w in {'maybe', 'perhaps', 'sort', 'kind', 'just'}]
            return candidates[0] if candidates else "hedging"
        return "it"

    def architect(self, metrics, vec, ops_performed):
        phys = metrics['physics']
        clean_words = metrics['clean_words']

        strategy = "MIRROR"
        directive = "Maintain current trajectory. The physics are stable."
        target = None

        # 1. SURGICAL RECOVERY (New 3.1 Feature)
        # If the Surgical Suite just cut text, the LLM must smooth the scars.
        if ops_performed:
            strategy = "RECONSTRUCTOR"
            directive = f"Surgery was performed ({len(ops_performed)} cuts). The sentence may be choppy. Smooth the rhythm without adding new mass."

        # 2. THE BUTCHER (Clarence) - High Drag
        elif phys['narrative_drag'] > 3.0:
            strategy = "CLARENCE"
            target = "adjectives" if phys['counts'].get('adverb', 0) > 2 else "passive verbs"
            directive = f"Narrative Drag is {phys['narrative_drag']}. You are drowning in molasses. Cut {target}. Use Subject-Verb-Object syntax."

        # 3. THE GROUNDER (Eloise) - High Entropy
        elif vec['ENT'] > 0.6:
            strategy = "ELOISE"
            target = self._find_target(clean_words, 'ABSTRACT')
            directive = f"Entropy is critical ({vec['ENT']}). The word '{target}' is a ghost. Replace it with something you can hold (stone, wood, iron)."

        # 4. THE WITCH (Yaga) - High Toxins/Hedging
        elif phys['toxicity_score'] > 0 or any(w in {'just', 'maybe', 'try'} for w in clean_words):
            strategy = "YAGA"
            target = self._find_target(clean_words, 'WEAK')
            directive = f"Toxins or hedging detected. The word '{target}' is a lie. State the raw truth. Do not apologize."

        # 5. THE JESTER - High Voltage / Paradox
        elif phys['beta_friction'] > 2.0:
            strategy = "JESTER"
            directive = f"High Voltage ({phys['beta_friction']}). The user has collided two opposing ideas. Do not solve the contradiction. Let it spark."

        # 6. THE DRIFTER - High Velocity
        elif vec['VEL'] > 0.6:
            strategy = "DRIFTER"
            directive = "Velocity is high. Do not use periods. Use commas, dashes, and breath. Keep it moving."

        # Construct the System Prompt
        system_prompt = (
            f"ROLE: {self.VOICES.get(strategy, 'THE MIRROR')}\n"
            f"DIRECTIVE: {directive}\n"
        )
        if target:
            system_prompt += f"TACTICAL TARGET: Eliminate or transmute '{target}'.\n"

        return strategy, system_prompt

# --- 6. CORE ENGINE ---

class BoneAmanitaUnicorn:
    def __init__(self):
        self.phys = PhysicsEngine()
        self.mem = DeepStorage()
        self.nrg = MetabolicReserve()
        self.wise = WisdomNode()
        self.tick = 0

        # Persistence (v3.0 Style - Simplified)
        self.load_state()

    def load_state(self):
        if os.path.exists("bone_unicorn.json"):
            try:
                with open("bone_unicorn.json", 'r') as f:
                    data = json.load(f)
                    self.nrg.atp = data.get('atp', 33)
                    self.mem.artifacts = data.get('artifacts', {})
            except: pass

    def save_state(self):
        with open("bone_unicorn.json", 'w') as f:
            json.dump({
                "atp": self.nrg.atp,
                "artifacts": self.mem.artifacts,
                "timestamp": time.time()
            }, f)

    def process(self, text):
        self.tick += 1

        # 1. Physics Analysis
        m = self.phys.analyze(text)

        # 2. Metabolic Update
        nrg_msg = self.nrg.metabolize(m, self.mem)
        self.mem.bury(m['clean_words'], self.tick)

        # 3. Surgical Intervention (The Unicorn Feature)
        fixed_text, ops = SurgicalSuite.operate(text, m)

        # 4. Wisdom Generation
        strat, system_prompt = self.wise.architect(m, m['physics']['vector'], ops))

        # 5. Render HUD
        self._render(m, nrg_msg, ops, fixed_text, strat, reason)
        self.save_state()

    def _render(self, m, nrg_msg, ops, fixed, strat, reason):
        p = m['physics']
        v = p['vector']

        print(f"\n{Prisma.GRY}--------------------------------------------------{Prisma.RST}")

        # Header
        atp_c = Prisma.wrap(self.nrg.atp, 10, invert=True)
        drag_c = Prisma.wrap(p['narrative_drag'], 2.5)
        beta_c = f"{Prisma.MAG}{p['beta_friction']}{Prisma.RST}" if p['beta_friction'] > 2.5 else f"{Prisma.CYN}{p['beta_friction']}{Prisma.RST}"

        print(f"{Prisma.WHT}[BONEAMANITA 3.1]{Prisma.RST} ATP: {atp_c} | DRAG: {drag_c} | β: {beta_c}")
        print(f"{Prisma.CYN}VECTOR:{Prisma.RST} [V:{v['VEL']} S:{v['STR']} E:{v['ENT']} T:{v['TEX']}]")

        if nrg_msg: print(f"  └─ {nrg_msg}")

        # The Surgical Block
        if ops:
            print(f"\n{Prisma.RED}🔪 SURGICAL INTERVENTION:{Prisma.RST}")
            for op in ops: print(f"   └─ {op}")
            print(f"{Prisma.GRN}>>> RECONSTRUCTION: \"{fixed}\"{Prisma.RST}")

        # The Wisdom Block
        print(f"\n{Prisma.BLU}🧠 WISDOM PROTOCOL:{Prisma.RST} {Prisma.WHT}{strat}{Prisma.RST}")
        print(f"   └─ {Prisma.GRY}{reason}{Prisma.RST}")
        print(f"   └─ PROMPT: \"{WisdomNode.STRATEGIES[strat]}\"")

        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}\n")

if __name__ == "__main__":
    eng = BoneAmanitaUnicorn()
    print(f"{Prisma.GRN}>>> THE UNICORN IS ALIVE.{Prisma.RST}")
    print(f"{Prisma.GRY}Type inputs to feed the machine.{Prisma.RST}")

    while True:
        u = input(f"{Prisma.WHT}>{Prisma.RST} ")
        if u.lower() in ['exit', 'quit']: break
        eng.process(u)
