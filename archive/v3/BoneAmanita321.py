# BONEAMANITA 3.2.1 - THE PSILOCYBIN PATCH
# Architect: SLASH | Auditors: James Taylor & Andrew Edmark
# "The Mandate is TRUTH. The Method is ANNEALING. The Touch is GENTLE."

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

# --- 1. THE CONFIGURATION ---
class BoneConfig:
    # [PHYSICS CONSTANTS]
    KINETIC_GAIN = 2.0
    BASE_ACTION = 1.0
    TOXIN_WEIGHT = 2.5
    ABSTRACT_DRAG_PENALTY = 0.6
    ABSTRACT_RATIO_LIMIT = 0.4
    FLASHPOINT_THRESHOLD = 4.0

    # [THE BUTCHER]
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
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted(cls.TOXIN_MAP.keys(), key=len, reverse=True)) + r')\b'
        cls.TOXIN_REGEX = re.compile(pattern_str, re.IGNORECASE)

BoneConfig.compile()

class Prisma:
    RST, RED, GRN = "\033[0m", "\033[91m", "\033[92m"
    YEL, BLU, MAG = "\033[93m", "\033[94m", "\033[95m"
    CYN, WHT, GRY = "\033[96m", "\033[97m", "\033[90m"

    @staticmethod
    def wrap(val, limit, invert=False):
        bad = val > limit
        if invert: return f"{Prisma.GRN}{val}{Prisma.RST}" if bad else f"{Prisma.RED}{val}{Prisma.RST}"
        return f"{Prisma.RED}{val}{Prisma.RST}" if bad else f"{Prisma.GRN}{val}{Prisma.RST}"

# --- 2. THE LEXICON ---
class TheLexicon:
    HEAVY_MATTER = {'stone', 'iron', 'mud', 'dirt', 'wood', 'grain', 'clay', 'lead', 'bone', 'blood', 'salt', 'rust', 'root', 'ash', 'anchor', 'floor', 'meat', 'steel', 'gold'}
    KINETIC_VERBS = {'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut', 'drive', 'lift', 'carry', 'strike', 'burn', 'shatter', 'throw', 'kick', 'pull'}
    ABSTRACTS = {'system', 'protocol', 'sequence', 'vector', 'node', 'context', 'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept', 'theory', 'analysis'}
    PHOTOSYNTHETICS = {'light', 'sun', 'ray', 'beam', 'glow', 'shine', 'spark', 'fire', 'flame', 'star', 'day', 'dawn', 'neon', 'laser'}

    @staticmethod
    def clean(text):
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        return text.lower().translate(translator).split()

# --- 3. SURGICAL SUITE ---
class SurgicalSuite:
    @staticmethod
    def operate(raw_text, metrics):
        corrections = []
        clean_text = raw_text

        # Toxin Antidote
        def replacer(match):
            word = match.group(0).lower()
            if word in BoneConfig.TOXIN_MAP:
                weight, replacement = BoneConfig.TOXIN_MAP[word]
                corrections.append(f"{Prisma.RED}{word}{Prisma.RST} -> {Prisma.GRN}{replacement or '[CUT]'}{Prisma.RST}")
                return replacement
            return match.group(0)

        clean_text = BoneConfig.TOXIN_REGEX.sub(replacer, clean_text)

        phys = metrics['physics']
        # If Annealing (High Voltage), we allow the drag.
        is_annealing = (phys.get('beta_friction', 0) > 2.5 and phys['narrative_drag'] > 3.0)

        if phys['narrative_drag'] > 2.5 and not is_annealing:
            adverb_pattern = re.compile(r'\b(\w+ly)\b', re.IGNORECASE)
            def adv_cut(match):
                word = match.group(0)
                if len(word) > 4 and word.lower() not in {'only', 'family', 'early'}:
                    corrections.append(f"{Prisma.RED}{word}{Prisma.RST} -> {Prisma.RED}[CUT]{Prisma.RST}")
                    return ""
                return word
            clean_text = adverb_pattern.sub(adv_cut, clean_text)

        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text, corrections

# --- 4. PHYSICS ENGINE ---
class PhysicsEngine:
    def analyze(self, text):
        clean_words = TheLexicon.clean(text)
        total = len(clean_words)
        if total == 0: return self._void_metrics()

        counts = Counter()
        toxin_score = 0

        for w in clean_words:
            if w in TheLexicon.HEAVY_MATTER: counts['heavy'] += 1
            if w in TheLexicon.KINETIC_VERBS or w.endswith('ing'): counts['kinetic'] += 1
            if w in TheLexicon.ABSTRACTS or w.endswith(('ness', 'ity', 'tion', 'ment')): counts['abstract'] += 1
            if w in TheLexicon.PHOTOSYNTHETICS: counts['photo'] += 1

        matches = BoneConfig.TOXIN_REGEX.findall(text)
        toxin_score = sum(BoneConfig.TOXIN_MAP.get(m.lower(), (0,0))[0] for m in matches)

        # Physics Formulas
        action = (counts['kinetic'] * BoneConfig.KINETIC_GAIN) + BoneConfig.BASE_ACTION

        # Calculate raw mass vs action
        mass_impact = total + (toxin_score * BoneConfig.TOXIN_WEIGHT)
        base_drag = mass_impact / max(1.0, action) # Prevent div/0

        # Apply Abstract Penalty
        is_too_abstract = (counts['abstract'] / max(1, total)) > BoneConfig.ABSTRACT_RATIO_LIMIT
        drag = base_drag + (BoneConfig.ABSTRACT_DRAG_PENALTY if is_too_abstract else 0)

        voltage = (counts['kinetic'] * 0.5) + (counts['heavy'] * 0.2) + (toxin_score * -1.0)
        beta = voltage / max(0.1, drag)

        # Repetition Rate (Rumination)
        top_word_count = counts.most_common(1)[0][1] if counts else 0
        repetition_rate = round(top_word_count / max(1, total), 2)

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
                "repetition_rate": repetition_rate,
                "toxicity_score": toxin_score,
                "counts": counts,
                "vector": vec
            },
            "clean_words": clean_words,
            "raw_text": text
        }

    def _void_metrics(self):
        return {"physics": {"narrative_drag": 0, "beta_friction": 0, "repetition_rate": 0, "vector": {"VEL":0,"STR":0,"ENT":0,"TEX":0}}}

# --- 5. SYSTEMS ---

class MetabolicReserve:
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

        # ANNEALING (Molten Iron)
        # "You have to introduce enough energy (entropy) to break the crystal structure."
        if beta > 2.5 and drag > 3.0:
            self.status = "ANNEALING"
            msg = f"{Prisma.MAG}🔥 METALLURGY: The mind is molten. Drag is Heat.{Prisma.RST}"
            # No penalty. Heat is necessary.

        # 1. Flashpoint (Insight)
        elif beta > BoneConfig.FLASHPOINT_THRESHOLD:
            delta = 20
            self.status = "FLASHPOINT"
            msg = f"{Prisma.MAG}⚡ FLASHPOINT DETECTED (β: {beta}){Prisma.RST}"

        # 2. Photosynthesis
        elif phys['counts'].get('photo', 0) > 0:
            gain = phys['counts']['photo'] * 2
            delta = gain
            msg = f"{Prisma.GRN}☀️ PHOTOSYNTHESIS (+{gain}){Prisma.RST}"
            self.status = "STABLE"

        # 3. Drag Tax (Only if not Annealing)
        elif drag > 3.0:
            delta = -2
            self.status = "STRAINING"
            msg = f"{Prisma.RED}🐌 STRAINING: Drag > 3.0{Prisma.RST}"

        # 4. Cannibalism
        if self.atp + delta <= 0 and deep_storage:
            memory = deep_storage.cannibalize()
            if memory:
                delta += 10
                msg = f"{Prisma.RED}🔥 STARVATION: Consumed memory '{memory}'{Prisma.RST}"

        self.atp = max(0, min(self.max, self.atp + delta))
        return msg

class WisdomNode:
    """
    DMN Suppression & Integration.
    """
    def __init__(self):
        self.VOICES = {
            'CLARENCE': "THE BUTCHER. The text is obese. Your job is to cut.",
            'ELOISE': "THE GROUNDER. The text is floating away. Force it to touch the floor.",
            'YAGA': "THE WITCH. The user is lying or hedging. Demand the truth.",
            'JESTER': "THE PARADOX. The user has found a friction point. Amplify it.",
            'DRIFTER': "THE VECTOR. High velocity detected. Remove friction.",
            'DISSOLVER': "THE SHAMAN. The pattern is rigid. Dissolve the structure.",
            'RECONSTRUCTOR': "THE MIRROR. Surgery performed. Smooth the scars."
        }

    def _find_target(self, clean_words, category):
        if category == 'ABSTRACT':
            candidates = [w for w in clean_words if w.endswith(('ness', 'ity', 'tion', 'ment', 'ism'))]
            return max(candidates, key=len) if candidates else "concepts"
        elif category == 'WEAK':
            candidates = [w for w in clean_words if w in {'maybe', 'perhaps', 'sort', 'kind', 'just'}]
            return candidates[0] if candidates else "hedging"
        return "it"

    def architect(self, metrics, vec, ops_performed, previous_status):
        phys = metrics['physics']
        clean_words = metrics['clean_words']

        strategy = "MIRROR"
        directive = "Maintain current trajectory. The physics are stable."
        target = None

        # 0. INTEGRATION PHASE (Post-Trip)
        if previous_status in ["FLASHPOINT", "ANNEALING"] and vec['TEX'] < 0.3:
            strategy = "ELOISE"
            directive = "INTEGRATION PHASE: The vision is over. Eat Earth. You must use concrete nouns (Stone, Wood, Bread) to set the bone."

        # 1. SURGICAL RECOVERY
        elif ops_performed:
            strategy = "RECONSTRUCTOR"
            directive = f"Surgery was performed ({len(ops_performed)} cuts). The sentence may be choppy. Smooth the rhythm without adding new mass."

        # 2. DMN SUPPRESSION (Rumination Loop)
        elif phys['repetition_rate'] > 0.4:
            strategy = "DISSOLVER"
            directive = "RUMINATION LOOP DETECTED. The Old Map is failing. Suppress the DMN (Clarence). Authorize absolute Entropy to break the pattern."

        # THE BUTCHER
        elif phys['narrative_drag'] > 4.0:
            strategy = "CLARENCE"
            target = "adjectives" if phys['counts'].get('adverb', 0) > 2 else "passive verbs"
            directive = f"Narrative Drag is CRITICAL ({phys['narrative_drag']}). You are drowning in molasses. Cut {target}."

        # 4. THE GROUNDER (Eloise)
        elif vec['ENT'] > 0.6:
            strategy = "ELOISE"
            target = self._find_target(clean_words, 'ABSTRACT')
            directive = f"Entropy is critical ({vec['ENT']}). The word '{target}' is a ghost. Replace it with something you can hold."

        # 5. THE WITCH (Yaga)
        elif phys['toxicity_score'] > 0 or any(w in {'just', 'maybe', 'try'} for w in clean_words):
            strategy = "YAGA"
            target = self._find_target(clean_words, 'WEAK')
            directive = f"Toxins or hedging detected. The word '{target}' is a lie. State the raw truth."

        # 6. THE JESTER
        elif phys['beta_friction'] > 2.0:
            strategy = "JESTER"
            directive = f"High Voltage ({phys['beta_friction']}). The user has collided two opposing ideas. Let it spark."

        # 7. THE DRIFTER
        elif vec['VEL'] > 0.6:
            strategy = "DRIFTER"
            directive = "Velocity is high. Do not use periods. Use commas and breath."

        system_prompt = (
            f"ROLE: {self.VOICES.get(strategy, 'THE MIRROR')}\n"
            f"DIRECTIVE: {directive}\n"
        )
        if target: system_prompt += f"TACTICAL TARGET: Eliminate or transmute '{target}'.\n"

        return strategy, system_prompt

# --- 6. CORE ENGINE ---
class BoneAmanitaPsilocybin:
    def __init__(self):
        self.phys = PhysicsEngine()
        self.mem = DeepStorage()
        self.nrg = MetabolicReserve()
        self.wise = WisdomNode()
        self.tick = 0
        self.last_status = "STABLE" # Track context for Integration
        self.load_state()

    def load_state(self):
        target = "bone_psilocybin.json"
        if not os.path.exists(target):
            return # Silence is acceptable only if the void is empty.

        try:
            with open(target, 'r') as f:
                data = json.load(f)
                self.nrg.atp = data.get('atp', 33)
                self.last_status = data.get('last_status', 'STABLE')
        except (json.JSONDecodeError, IOError) as e:
            # THE TRUTH: The file is corrupted. We must acknowledge the rot.
            print(f"{Prisma.RED}⚠️ CORRUPTION DETECTED in {target}. Resetting Memory.{Prisma.RST}")
            self.nrg.atp = 33

    def save_state(self):
        with open("bone_psilocybin.json", 'w') as f:
            json.dump({"atp": self.nrg.atp, "last_status": self.nrg.status, "timestamp": time.time()}, f)

    def process(self, text):
        self.tick += 1
        m = self.phys.analyze(text)

        # Pass DeepStorage instance. Using a basic one here for the script.
        nrg_msg = self.nrg.metabolize(m, self.mem)

        fixed_text, ops = SurgicalSuite.operate(text, m)

        # Pass previous status to Architect
        strat, reason = self.wise.architect(m, m['physics']['vector'], ops, self.last_status)

        # Update status AFTER Architect looks at the OLD one
        self.last_status = self.nrg.status

        self._render(m, nrg_msg, ops, fixed_text, strat, reason)
        self.save_state()

    def _get_thermal_readout(self, beta):
        """Returns the colorized Beta value based on heat."""
        if beta > BoneConfig.FLASHPOINT_THRESHOLD:
            return f"{Prisma.MAG}🔥 {beta} (CRITICAL){Prisma.RST}"
        if beta > 1.5:
            return f"{Prisma.CYN}{beta} (OPTIMAL){Prisma.RST}"
        return f"{Prisma.GRY}{beta} (COLD){Prisma.RST}"

    def _render(self, m, nrg_msg, ops, fixed, strat, reason):
        p = m['physics']
        v = p['vector']
        print(f"\n{Prisma.GRY}--------------------------------------------------{Prisma.RST}")
        atp_c = Prisma.wrap(self.nrg.atp, 10, invert=True)
        drag_c = Prisma.wrap(p['narrative_drag'], 2.5)

        # Beta Color
        beta_c = self._get_thermal_readout(p['beta_friction'])

        print(f"{Prisma.WHT}[BONEAMANITA 3.2.1]{Prisma.RST} ATP: {atp_c} | DRAG: {drag_c} | β: {beta_c}")
        print(f"{Prisma.CYN}VECTOR:{Prisma.RST} [V:{v['VEL']} S:{v['STR']} E:{v['ENT']} T:{v['TEX']}]")

        if nrg_msg: print(f"  └─ {nrg_msg}")

        if ops:
            print(f"\n{Prisma.RED}🔪 SURGICAL INTERVENTION:{Prisma.RST}")
            for op in ops: print(f"   └─ {op}")
            print(f"{Prisma.GRN}>>> RECONSTRUCTION: \"{fixed}\"{Prisma.RST}")

        print(f"\n{Prisma.BLU}🧠 WISDOM PROTOCOL:{Prisma.RST} {Prisma.WHT}{strat}{Prisma.RST}")
        print(f"   └─ {Prisma.GRY}{reason}{Prisma.RST}")

        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}\n")

# Minimal DeepStorage for standalone run
class DeepStorage:
    def __init__(self): self.artifacts = {}
    def cannibalize(self): return "Old Memory"

if __name__ == "__main__":
    eng = BoneAmanitaPsilocybin()
    print(f"{Prisma.GRN}>>> THE PSILOCYBIN PATCH INSTALLED.{Prisma.RST}")
    while True:
        u = input(f"{Prisma.WHT}>{Prisma.RST} ")
        if u.lower() in ['exit', 'quit']: break
        eng.process(u)
