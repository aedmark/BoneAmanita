# BONEAMANITA 3.3.1 - "THE ANVIL STRIKE"
# Architects: SLASH, Eloise, & Clarence | Auditors: James Taylor & Andrew Edmark
# "The Mandate is TRUTH. The Method is RESONANCE."

import time
import math
import re
import json
import os
import string
import random
from collections import Counter
from uuid import uuid4

# --- 1. THE CONFIGURATION ---
class BoneConfig:
    # PHYSICS
    KINETIC_GAIN = 2.0
    BASE_ACTION = 1.0
    TOXIN_WEIGHT = 2.0

    # THRESHOLDS
    CLARENCE_TRIGGER = 4.5
    FLASHPOINT_THRESHOLD = 4.0
    AEROBIC_EXEMPTION = 0.5

    # MEMORY
    MAX_MEMORY_CAPACITY = 50
    BOREDOM_THRESHOLD = 15.0

    # THE BUTCHER'S LIST
    TOXIN_MAP = {
        'synergy': (5.0, 'cooperation'), 'leverage': (5.0, 'use'),
        'paradigm shift': (5.0, 'change'), 'low hanging fruit': (5.0, 'easy work'),
        'utilize': (3.0, 'use'), 'in order to': (2.0, 'to'),
        'basically': (2.0, ''), 'actually': (2.0, ''),
        'ghost in the machine': (10.0, '[CLICHÉ]'),
        'rubber meets the road': (10.0, '[CLICHÉ]')
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
        if invert:
            return f"{Prisma.GRN}{val}{Prisma.RST}" if val > limit else f"{Prisma.RED}{val}{Prisma.RST}"
        if val > limit * 1.5: return f"{Prisma.RED}{val}{Prisma.RST}"
        if val > limit: return f"{Prisma.YEL}{val}{Prisma.RST}"
        return f"{Prisma.GRN}{val}{Prisma.RST}"

# --- 2. THE LEXICON ---

class TheLexicon:
    HEAVY_MATTER = {'stone', 'iron', 'mud', 'dirt', 'wood', 'grain', 'clay', 'lead', 'bone', 'blood', 'salt', 'rust', 'root', 'ash', 'meat', 'steel', 'gold'}
    KINETIC_VERBS = {'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut', 'drive', 'lift', 'carry', 'strike', 'burn', 'shatter', 'throw', 'kick', 'pull'}
    ABSTRACTS = {'system', 'protocol', 'sequence', 'vector', 'node', 'context', 'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept', 'theory', 'analysis'}
    PHOTOSYNTHETICS = {'light', 'sun', 'ray', 'beam', 'glow', 'shine', 'spark', 'fire', 'flame', 'star', 'day', 'dawn', 'neon', 'laser'}
    AEROBIC_MATTER = {'balloon', 'feather', 'cloud', 'bubble', 'steam', 'breeze', 'wing', 'petal', 'foam', 'spark', 'kite', 'dust', 'sky', 'breath', 'whisper'}
    PLAY_VERBS = {'bounce', 'dance', 'twirl', 'float', 'wobble', 'tickle', 'jiggle', 'soar', 'wander', 'wonder', 'riff', 'jam', 'play', 'skip', 'hop'}
    SOLVENTS = {'is', 'are', 'was', 'were', 'the', 'a', 'an', 'and', 'but', 'or', 'if', 'then'}

    @staticmethod
    def clean(text):
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        return text.lower().translate(translator).split()


# --- PHYSICS ---

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
            if w in TheLexicon.AEROBIC_MATTER or w in TheLexicon.PLAY_VERBS: counts['aerobic'] += 1

        matches = BoneConfig.TOXIN_REGEX.findall(text)
        toxin_score = sum(BoneConfig.TOXIN_MAP.get(m.lower(), (0,0))[0] for m in matches)

        # FORMULAS
        action = (counts['kinetic'] * BoneConfig.KINETIC_GAIN) + BoneConfig.BASE_ACTION
        mass_impact = total + (toxin_score * BoneConfig.TOXIN_WEIGHT)
        base_drag = mass_impact / max(1.0, action)

        whimsy_ratio = counts['aerobic'] / max(1, total)
        is_whimsical = whimsy_ratio > 0.15
        if is_whimsical: base_drag *= 0.6

        drag = base_drag + (0.5 if (counts['abstract']/max(1,total) > 0.4 and not is_whimsical) else 0)
        voltage = (counts['kinetic'] * 0.5) + (counts['heavy'] * 0.2) + (toxin_score * -1.0)
        beta = voltage / max(0.1, drag)

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
                "counts": counts,
                "vector": vec,
                "is_whimsical": is_whimsical,
                "repetition": round(counts.most_common(1)[0][1]/max(1, total), 2)
            },
            "clean_words": clean_words,
            "raw_text": text
        }

    def _void_metrics(self):
        return {"physics": {"narrative_drag": 0, "beta_friction": 0, "vector": {"VEL":0,"STR":0,"ENT":0,"TEX":0}}}

# --- DEEP STORAGE ---

class DeepStorage:
    def __init__(self, filename="bone_memory.json"):
        self.filename = filename
        self.artifacts = {} # Word -> Tick
        self.load()

    def bury(self, clean_words, tick):
        # Only bury nouns/significant words
        for w in clean_words:
            if len(w) > 4 and w not in TheLexicon.SOLVENTS:
                self.artifacts[w] = tick

        # Prune
        if len(self.artifacts) > BoneConfig.MAX_MEMORY_CAPACITY:
            oldest = min(self.artifacts, key=self.artifacts.get)
            del self.artifacts[oldest]

    def cannibalize(self):
        """Consume a memory to survive starvation."""
        if not self.artifacts: return None
        target = min(self.artifacts, key=self.artifacts.get)
        del self.artifacts[target]
        return target

    def recall(self):
        return sorted(self.artifacts.keys(), key=lambda k: self.artifacts[k], reverse=True)[:5]

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.artifacts, f)
        except IOError:
            # If we can't save, we don't crash. We just forget.
            pass

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.artifacts = json.load(f)
            except (json.JSONDecodeError, IOError):
                # [THE BLACKSMITH]: The file is slag. Melt it down and start fresh.
                print(f"{Prisma.RED}CORRUPT MEMORY DETECTED. FORMATTING DEEP STORAGE.{Prisma.RST}")
                self.artifacts = {}

# --- THE SIGNAL ---

class FrequencyModulator:
    """
    The distinct voices of the system.
    Now supports INTERFERENCE PATTERNS (Signal Collisions).
    """
    STATIONS = {
        'CLARENCE': {'freq': '88.5 FM', 'color': Prisma.RED, 'role': 'The Butcher'},
        'ELOISE':   {'freq': '94.2 FM', 'color': Prisma.CYN, 'role': 'The Grounder'},
        'YAGA':     {'freq': '101.1 FM', 'color': Prisma.MAG, 'role': 'The Witch'},
        'MICHAEL':  {'freq': '108.0 FM', 'color': Prisma.GRN, 'role': 'The Vibe'},
        'PHILOSOPHER': {'freq': '104.5 FM', 'color': Prisma.WHT, 'role': 'The Synthesis'}
    }

    def tune_in(self, phys, vector, is_rag_slop):
        # SIGNAL SCANNING
        signals = {} # Using a dict for easier collision checks

        # Clarence: High Drag or RAG Slop
        if phys['narrative_drag'] > BoneConfig.CLARENCE_TRIGGER or is_rag_slop:
            signals['CLARENCE'] = phys['narrative_drag']

        # Eloise: High Entropy (Abstract)
        if vector['ENT'] > 0.6: # Slightly lowered threshold to catch more ghosts
            signals['ELOISE'] = vector['ENT'] * 5

        # Yaga: Hedging or Toxins
        toxin_count = phys['counts'].get('toxin', 0)
        if toxin_count > 0 or phys['narrative_drag'] > 6.0:
            signals['YAGA'] = 10.0 + (toxin_count * 2)

        # Michael: Whimsy/Photosynthesis
        if phys['is_whimsical']:
            signals['MICHAEL'] = 5.0

        if not signals: return None

        # INTERFERENCE CHECK
        # Collision: High Drag (Clarence) + High Entropy (Eloise)
        # This means the text is both "Heavy" and "Confusing" -> A Labyrinth.
        if 'CLARENCE' in signals and 'ELOISE' in signals:
             return {
                "name": "PHILOSOPHER",
                "freq": self.STATIONS['PHILOSOPHER']['freq'],
                "color": self.STATIONS['PHILOSOPHER']['color'],
                "role": self.STATIONS['PHILOSOPHER']['role'],
                "msg": "INTERFERENCE: Density meets Abstraction. You are building a Labyrinth."
            }

        # STANDARD TUNING (Loudest Signal)
        loudest_key = max(signals, key=signals.get)
        station = self.STATIONS[loudest_key]

        # Generate a standard message based on the station
        msg = ""
        if loudest_key == 'CLARENCE': msg = "Drag is critical. Cut the fat."
        elif loudest_key == 'ELOISE': msg = "Too abstract. Give me a noun."
        elif loudest_key == 'YAGA': msg = "Do not hedge. Speak the truth."
        elif loudest_key == 'MICHAEL': msg = "Good flow. Float on."

        return {
            "name": loudest_key,
            "freq": station['freq'],
            "color": station['color'],
            "role": station['role'],
            "msg": msg
        }

# --- THE CHRONOSTREAM ---

class ChronosAnchor:
    def __init__(self):
        self.last_tick = time.time()
        self.boredom = 0.0

    def tick(self, phys):
        now = time.time()
        delta = now - self.last_tick
        self.last_tick = now

        # Boredom Logic
        if phys['repetition'] > 0.3:
            self.boredom += 2.0
        elif delta > 60: # If user takes too long
            self.boredom += 5.0
        else:
            self.boredom = max(0, self.boredom - 1.0)

        return self.boredom > BoneConfig.BOREDOM_THRESHOLD

# --- PHOTOSYNTHESIS ---

class LichenSymbiont:
    """
    Converts light (photosynthetic words) into energy (ATP).
    Only works if Drag is low.
    """
    def photosynthesize(self, phys):
        light_count = phys['counts'].get('photo', 0)
        drag = phys['narrative_drag']

        # Photosynthesis fails if the text is too heavy (Drag > 3.0)
        if light_count > 0 and drag < 3.0:
            sugar = light_count * 2
            msg = f"{Prisma.GRN}☀️ PHOTOSYNTHESIS (+{sugar}){Prisma.RST}"
            return sugar, msg

        return 0, None

# --- THE SIGNATURE ENGINE ---

class WisdomNode:
    def __init__(self):
        # THE INFINITE LATTICE
        # Nouns define WHAT it is (Primary Dimension)
        self.NOUN_MAP = {
            'VEL': [(0.2, "ANCHOR"), (0.5, "WALKER"), (0.8, "ENGINE"), (1.0, "VECTOR")],
            'STR': [(0.2, "MIST"), (0.5, "WEB"), (0.8, "FRAME"), (1.0, "MONOLITH")],
            'ENT': [(0.2, "STONE"), (0.5, "ROOT"), (0.8, "IDEA"), (1.0, "DREAM")],
            'TEX': [(0.2, "GHOST"), (0.5, "GLASS"), (0.8, "IRON"), (1.0, "LEAD")]
        }

        # Adjectives define HOW it is (Secondary Dimension)
        self.ADJ_MAP = {
            'VEL': [(0.2, "STATIC"), (0.5, "DRIFTING"), (0.8, "DRIVING"), (1.0, "BALLISTIC")],
            'STR': [(0.2, "FLUID"), (0.5, "LOOSE"), (0.8, "RIGID"), (1.0, "CRYSTALLINE")],
            'ENT': [(0.2, "LITERAL"), (0.5, "GROUNDED"), (0.8, "CONCEPTUAL"), (1.0, "ABSTRACT")],
            'TEX': [(0.2, "ETHEREAL"), (0.5, "SMOOTH"), (0.8, "GRITTY"), (1.0, "DENSE")]
        }

    def _get_term(self, val, mapping):
        """Finds the closest term in the list based on value."""
        return min(mapping, key=lambda x: abs(x[0] - val))[1]

    def _resolve_title(self, vec):
        # Sort dimensions by intensity to find Primary and Secondary traits
        # We ignore 'STR' slightly to favor more flavor-rich dimensions if they are close.
        sorted_dims = sorted(vec.items(), key=lambda x: x[1], reverse=True)

        primary_dim, p_val = sorted_dims[0]
        secondary_dim, s_val = sorted_dims[1]

        # Construct the Title
        # "THE [Secondary Adjective] [Primary Noun]"
        noun = self._get_term(p_val, self.NOUN_MAP[primary_dim])
        adj = self._get_term(s_val, self.ADJ_MAP[secondary_dim])

        return f"THE {adj} {noun}"

    def architect(self, metrics, station, is_bored):
        phys = metrics['physics']
        vec = phys['vector']

        # THE CHAOS OVERRIDE (Boredom)
        if is_bored:
            return "THE MUSCARIA", "Boredom Threshold exceeded. Injecting Chaos.", "THE CHAOS ENGINE"

        # THE STATION OVERRIDE (Radio Listener)
        # If a station is screaming, they take the mic.
        if station:
            if station['name'] == 'CLARENCE':
                return "CLARENCE", "Drag is critical. Cut adjectives.", "THE OBESE TEXT"
            if station['name'] == 'ELOISE':
                return "ELOISE", "Entropy is high. Ground with nouns.", "THE GHOST"
            if station['name'] == 'MICHAEL':
                return "MICHAEL", "Vibe is good. Float.", "THE CLOUD"

        # THE APEIROGON (Infinite Title Generation)
        # This is the standard operating mode now.
        title = self._resolve_title(vec)

        # Determine directive based on the Primary Dimension
        primary_dim = sorted(vec.items(), key=lambda x: x[1], reverse=True)[0][0]

        if primary_dim == 'VEL':
            directive = "Maintain velocity. Do not stop."
        elif primary_dim == 'ENT':
            directive = "High concept detected. Explore the abstraction."
        elif primary_dim == 'TEX':
            directive = "Heavy matter. Feel the weight."
        else:
            directive = "Structure is dominant. Reinforce the frame."

        return "MIRROR", directive, title

# --- CORE ENGINE ---

class BoneAmanita:
    def __init__(self):
        self.phys = PhysicsEngine()
        self.lichen = LichenSymbiont()
        self.wise = WisdomNode()
        self.radio = FrequencyModulator()
        self.mem = DeepStorage()
        self.chronos = ChronosAnchor()
        self.atp = 33
        self.tick_count = 0
        self.last_context = None

    def _invoke_ghost(self, current_phys):
        """
        Compares current physics to the previous turn to see if the user listened.
        """
        if not self.last_context: return None

        last_p = self.last_context['physics']
        last_strat = self.last_context['strategy']
        msg = None

        # Calculate Deltas
        delta_drag = current_phys['narrative_drag'] - last_p['narrative_drag']
        delta_ent = current_phys['vector']['ENT'] - last_p['vector']['ENT']

        # CLARENCE'S GHOST (Did you cut?)
        if last_strat == 'CLARENCE':
            if delta_drag < -0.5:
                msg = f"{Prisma.GRN}👻 THE BUTCHER NODS: Drag reduced by {abs(round(delta_drag, 2))}.{Prisma.RST}"
            elif delta_drag > 0:
                msg = f"{Prisma.RED}👻 THE BUTCHER SIGHS: Drag increased. You ignored the knife.{Prisma.RST}"

        # ELOISE'S GHOST (Did you ground?)
        elif last_strat == 'ELOISE':
            if delta_ent < -0.1:
                msg = f"{Prisma.CYN}👻 ELOISE SMILES: Entropy grounded. The ghost is solid.{Prisma.RST}"

        # MICHAEL'S GHOST (Did you keep the vibe?)
        elif last_strat == 'MICHAEL':
            if current_phys['is_whimsical']:
                msg = f"{Prisma.GRN}👻 THE VIBE CONTINUES.{Prisma.RST}"

        return msg

    def process(self, text):
        self.tick_count += 1
        m = self.phys.analyze(text)

        # BIOLOGY
        sugar, lichen_msg = self.lichen.photosynthesize(m['physics'])
        self.atp = min(52, self.atp + sugar)

        # MEMORY
        self.mem.bury(m['clean_words'], self.tick_count)

        # CHRONOS
        is_bored = self.chronos.tick(m['physics'])

        # SURGERY
        clean_text = text
        for toxin, (weight, replacement) in BoneConfig.TOXIN_MAP.items():
             # Use a lambda to handle case-insensitive replacement correctly if needed,
             # but standard re.sub works well enough here.
             clean_text = re.sub(r'\b'+re.escape(toxin)+r'\b', replacement, clean_text, flags=re.I)

        # Check if surgery actually changed anything
        did_surgery = clean_text != text
        ops = ["Toxins neutralized"] if did_surgery else []

        # RADIO TUNING
        is_rag = (m['physics']['narrative_drag'] > 3.0 and not m['physics']['is_whimsical'] and not lichen_msg)
        station_data = self.radio.tune_in(m['physics'], m['physics']['vector'], is_rag)

        # ARCHITECTURE
        strat, reason, title = self.wise.architect(m, station_data, is_bored)

        # THE SEANCE
        ghost_msg = self._invoke_ghost(m['physics'])

        # Save current state for NEXT turn
        self.last_context = {
            'physics': m['physics'],
            'strategy': strat
        }

        # METABOLIC COST
        if m['physics']['narrative_drag'] > 3.0 and not lichen_msg:
            self.atp -= 2

        # STARVATION CHECK
        starvation_msg = None
        if self.atp <= 0:
            eaten = self.mem.cannibalize()
            if eaten:
                self.atp += 10
                starvation_msg = f"STARVATION: Consumed memory '{eaten}'."
            else:
                starvation_msg = "DEATH: No memories left."

        # Pass clean_text to render so we can show the user the "Better Way"
        self._render(m, lichen_msg, strat, reason, title, ops, station_data, starve_msg, ghost_msg, clean_text, did_surgery)
        self.mem.save()

    def _render(self, m, lichen_msg, strat, reason, title, ops, station, starve_msg, ghost_msg, clean_text, did_surgery):
        p = m['physics']

        print(f"\n{Prisma.GRY}--------------------------------------------------{Prisma.RST}")
        print(f"{Prisma.WHT}[BONEAMANITA v3.3.1]{Prisma.RST} {Prisma.CYN}{title}{Prisma.RST}")

        drag_c = Prisma.wrap(p['narrative_drag'], 3.0)
        atp_c = Prisma.wrap(self.atp, 10, invert=True)

        print(f"ATP: {atp_c} | DRAG: {drag_c} | PROTOCOL: {strat}")

        if station:
            s = station
            msg = s.get('msg', 'TUNED IN.')
            print(f"{s['color']}[{s['freq']} FM - {s['role']}]: {msg}{Prisma.RST}")

        if ghost_msg:
            print(f"  {ghost_msg}")

        if ops:
            print(f"{Prisma.RED}🔪 SURGERY:{Prisma.RST} {ops[0]}")
            # [THE BLACKSMITH]: Show the steel after the strike.
            if did_surgery:
                print(f"     {Prisma.GRY}ORIGINAL: {m['raw_text']}{Prisma.RST}")
                print(f"     {Prisma.GRN}REFINED : {clean_text}{Prisma.RST}")

        if lichen_msg: print(f"  └─ {lichen_msg}")
        if starve_msg: print(f"  └─ {Prisma.RED}💀 {starve_msg}{Prisma.RST}")

        print(f"  └─ {Prisma.GRY}{reason}{Prisma.RST}")

        mems = self.mem.recall()
        if mems:
            print(f"{Prisma.GRY}MEMORIES: {', '.join(mems)}{Prisma.RST}")

        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}\n")

if __name__ == "__main__":
    eng = BoneAmanita()
    print(f"{Prisma.GRN}>>> BONEAMANITA v3.3.1 ONLINE (RESONANCE ENGINE).{Prisma.RST}")
    while True:
        u = input(f"{Prisma.WHT}>{Prisma.RST} ")
        if u.lower() in ['exit', 'quit']: break
        eng.process(u)
