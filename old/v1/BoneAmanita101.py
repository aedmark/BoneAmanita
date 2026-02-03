# BONEAMANITA 1.0.1 - "The Black Mirror (PATCHED)"
# Architects: James Taylor & Andrew Edmark | Auditors: SLASH
# ---

import time
import math
import random
from collections import Counter
from uuid import uuid4
import re

class TheLexicon:
    HEAVY_MATTER = {
        'stone', 'iron', 'mud', 'dirt', 'wood', 'grain', 'clay', 'lead',
        'bone', 'blood', 'salt', 'rust', 'root', 'ash', 'anchor', 'floor'
    }
    AEROBIC_MATTER = {
        'balloon', 'feather', 'cloud', 'bubble', 'steam', 'breeze', 'wing',
        'petal', 'foam', 'spark', 'kite', 'dust', 'light', 'ray', 'sky'
    }
    UNIVERSALS = HEAVY_MATTER.union(AEROBIC_MATTER).union({
        'hand', 'eye', 'breath', 'skin', 'voice', "air", "cloth",
        'water', 'rain', 'glass', 'fabric', 'door', 'key', 'roof'
    })
    ABSTRACTS = {
        'system', 'protocol', 'sequence', 'vector', 'node', 'context',
        'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept',
        'theory', 'analysis', 'solution', 'optimization', 'utilization'
    }
    KINETIC_VERBS = {
        'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut',
        'drive', 'lift', 'carry', 'strike', 'burn', 'shatter'
    }
    PLAY_VERBS = {
        'bounce', 'dance', 'twirl', 'float', 'wobble', 'tickle', 'jiggle',
        'soar', 'wander', 'wonder', 'riff', 'jam', 'play', 'skip', 'hop'
    }
    ALL_VERBS = KINETIC_VERBS.union(PLAY_VERBS)
    SPARK_MARKERS = {
        'lovely', 'strange', 'curious', 'funny', 'wild', 'soft', 'glow',
        'warm', 'kind', 'fresh', 'sweet', 'hello', 'yes', 'maybe'
    }
    TRUTHS = {
        'sun': {'LUMENS': 1, 'THERMAL': 1},
        'night': {'LUMENS': -1, 'THERMAL': -1},
        'fire': {'THERMAL': 1, 'VITALITY': 1},
        'ice': {'THERMAL': -1, 'VITALITY': -1},
        'laugh': {'VITALITY': 1, 'THERMAL': 1},
        'smile': {'VITALITY': 1, 'THERMAL': 1},
        'song': {'VITALITY': 1},
        'dead': {'VITALITY': -1, 'THERMAL': -1}
    }
    PHOTOSYNTHETICS = {
        'light', 'sun', 'ray', 'beam', 'glow', 'shine', 'spark', 'fire',
        'flame', 'star', 'day', 'dawn', 'noon', 'gold', 'bright', 'glimmer'
    }
    SYCOPHANCY = {
        'just', 'actually', 'kind of', 'sort of', 'little', 'try', 'maybe',
        'perhaps', 'hopefully', 'possibly', 'basically', 'honestly'
    }
    TOXIC_PATTERNS = {
        'CORP_SPEAK': {
            'synergy': 5.0, 'leverage': 5.0, 'circle back': 4.0, 'drill down': 4.0,
            'low hanging fruit': 5.0, 'bandwidth': 3.0, 'touch base': 4.0,
            'paradigm shift': 5.0, 'deliverable': 3.0, 'actionable': 3.0
        },
        'LAZY_METAPHOR': {
            'tip of the iceberg': 3.0, 'needle in a haystack': 3.0,
            'at the end of the day': 3.0, 'game changer': 4.0
        },
        'ZOMBIE_PHRASES': {
            'ghost in the machine': 10.0, 'rubber meets the road': 10.0,
            'not a bug but a feature': 9.0, 'double-edged sword': 8.0,
            'best of both worlds': 8.0, 'step in the right direction': 8.0,
            'level playing field': 8.0
        },
        'WEAK_HEDGING': {
            'i think that': 2.0, 'it seems like': 2.0, 'in my opinion': 2.0
        }
    }
    STATIVE_VERBS = {
        'is', 'are', 'was', 'were', 'be', 'being', 'been', 'have', 'has', 'had',
        'seem', 'appear', 'become', 'feel', 'look', 'smell', 'taste', 'sound'
    }
    STYLES = {
        'ACADEMIC': {'analysis', 'context', 'therefore', 'however', 'system', 'theory'},
        'POETIC': {'moon', 'soul', 'whisper', 'shadow', 'light', 'dark', 'heart'},
        'CORPORATE': {'utilize', 'optimize', 'leverage', 'solution', 'process', 'value'},
        'CASUAL': {'yeah', 'cool', 'stuff', 'like', 'okay', 'guess', 'pretty'}
    }
    CONNECTORS = {'and', 'but', 'or', 'so', 'yet', 'because', 'although', 'since'}
    SLANG = {'lol', 'lmao', 'yeet', 'rizz', 'vibes', 'sus', 'cap'}
    SELF_REFS = {'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours'}
    BRAND_SAFE = {'solution', 'platform', 'users', 'experience', 'content'}

# --- MEMORY & ECONOMY ---

class HyphalTrace:
    def __init__(self, retention_span=10):
        self.hyphae_stream = []
        self.retention_span = retention_span
        self.current_tick = 0

    def leave_trace(self, content, context_tag):
        self.current_tick += 1
        self.hyphae_stream.append({
            "content": content,
            "context_tag": context_tag,
            "timestamp": self.current_tick
        })
        if len(self.hyphae_stream) > self.retention_span:
            self.hyphae_stream.pop(0)

    def recall(self, target_context):
        relevant = []
        for mem in self.hyphae_stream:
            is_recent = (self.current_tick - mem['timestamp']) < 3
            if is_recent or (mem['context_tag'] == target_context):
                relevant.append(mem['content'])
        return relevant

class TheCodex:
    def __init__(self):
        self.registry = {}
        self.ignore_list = {
            'The', 'A', 'An', 'It', 'He', 'She', 'They', 'We', 'I', 'You',
            'This', 'That', 'But', 'And', 'Or', 'If', 'When', 'Then',
            'System', 'Analysis', 'Metrics', 'Drag', 'Entropy', 'For', 'In', 'To', 'Of'
        }
        self._entity_pattern = re.compile(r'\b[A-Z][a-z]+\b')

    def scan_for_entities(self, raw_text, current_tick):
        for match in self._entity_pattern.finditer(raw_text):
            word = match.group()
            if word in self.ignore_list or len(word) < 3: continue
            if match.start() == 0: continue
            start_index = match.start()
            preceding = raw_text[max(0, start_index-4):start_index]
            if any(p in preceding for p in ['.', '!', '?', '\n']): continue

            if word not in self.registry:
                self.registry[word] = {'count': 0, 'first_seen_tick': current_tick}
            self.registry[word]['count'] += 1

    def get_anchors(self):
        return [k for k, v in sorted(self.registry.items(), key=lambda i: i[1]['count'], reverse=True)[:5]]

# --- TRAPS & LOGIC ---

class TheMirrorTrap:
    def __init__(self):
        self.mirror_patterns = [
            # The Classic: "It's not X, it's Y"
            re.compile(r'(it|this|that)[\'’]?s?\s+(not|never)\s+(.*?)[,;]\s*(it|this|that)[\'’]?s?\s+', re.IGNORECASE),
            # The Pseudo-Intellectual: "Not because X, but because Y"
            re.compile(r'\bnot\s+because\s+(.*?)\s+but\s+because\b', re.IGNORECASE),
            # The Accusation: "You don't X, you Y"
            re.compile(r'\byou\s+(don\'t|do\s+not|didn\'t|did\s+not)\s+(.*?)[,;]\s+you\s+', re.IGNORECASE),
            # The Reductive: "It is simply..." (often follows a negation)
            re.compile(r'\b(simply|merely|just)\s+is\b', re.IGNORECASE)
        ]

    def scan(self, raw_text):
        for pattern in self.mirror_patterns:
            match = pattern.search(raw_text)
            if match:
                culprit = match.group(0)
                return {
                    "detected": True,
                    "culprit": (culprit[:40] + '...') if len(culprit) > 40 else culprit,
                    "penalty_msg": "MIRROR TRAP: You are defining things by what they are NOT. Delete the negative clause. State the assertion directly."
                }
        return {"detected": False}

class FactStipe:
    def inject_truth(self, word, dimension, polarity):
        if word not in TheLexicon.TRUTHS: TheLexicon.TRUTHS[word] = {}
        TheLexicon.TRUTHS[word][dimension] = polarity

    def check_consistency(self, clean_words, current_style, metabolic_status, kinetic_ratio=0.0, tolerance_mode="STANDARD"):
        active_dimensions = {}
        trigger_words = {}
        for w in clean_words:
            target = w if w in TheLexicon.TRUTHS else next((w[:-len(s)] for s in ['ness', 'ing', 's', 'ed', 'ly'] if w.endswith(s) and w[:-len(s)] in TheLexicon.TRUTHS), None)
            if target:
                for dim, polarity in TheLexicon.TRUTHS[target].items():
                    if dim not in active_dimensions:
                        active_dimensions[dim] = set(); trigger_words[dim] = {1: [], -1: []}
                    active_dimensions[dim].add(polarity)
                    trigger_words[dim][polarity].append(w)

        violations = []
        voltage = 0.0
        for dim, polarities in active_dimensions.items():
            if 1 in polarities and -1 in polarities:
                if tolerance_mode == "INVERTED": voltage += 2.0
                elif kinetic_ratio > 0.4: voltage += 5.0; violations.append(f"PARADOX IGNITED [{dim}]: High velocity collision.")
                else: violations.append(f"LOGIC TEAR [{dim}]: Static contradiction.")

        voltage = min(voltage, 10.0)
        if violations and voltage > 0: return {"valid": True, "voltage": voltage, "intervention": f"VOLATILE SEMANTIC LEVERAGE: Harvested {voltage} Voltage."}
        elif violations: return {"valid": False, "voltage": 0, "errors": violations, "intervention": f"{violations[0]} Stationary paradox."}
        return {"valid": True, "voltage": voltage}

class ChaosCooldown:
    def __init__(self, cooldown_ticks=5):
        self.last_trigger_tick = -cooldown_ticks
        self.cooldown = cooldown_ticks
    def is_ready(self, current_tick, force=False):
        if force or (current_tick - self.last_trigger_tick >= self.cooldown):
            self.last_trigger_tick = current_tick
            return True
        return False

# --- THE MUSCARIA (Disruption) ---

class TheMuscaria:
    def __init__(self):
        self.boredom_pressure = 0.0
        self.pressure_threshold = 11.0
        self.prescriptions = {
            'KINETIC': ["ADRENALINE SHOT: Describe a sound immediately.", "VELOCITY CHECK: Someone is running at you.", "IMPACT EVENT: A door slams."],
            'SENSORY': ["GRAVITY CHECK: The air is thin.", "VIBE CHECK: What does the light smell like?", "TEMPERATURE DROP: Freezing."],
            'COGNITIVE': ["VERSE JUMP: Shift perspective.", "SURREALIST PIVOT: Dream logic.", "THE LIZARD KING: Raise stakes."]
        }

    def check_for_boredom(self, metrics):
        if 'physics' not in metrics: return False
        phys = metrics['physics']
        self.boredom_pressure += (phys['narrative_drag'] * 0.2) + (phys['repetition_rate'] * 3.0) + (max(0, phys['abstraction_entropy']) * 0.1)
        return self.boredom_pressure > self.pressure_threshold

    def trigger_disruption(self, ancestry_data, metrics):
        self.boredom_pressure = 0.0
        phys = metrics['physics']
        if phys['narrative_drag'] > 3.0: cat = 'KINETIC'
        elif phys['abstraction_entropy'] > 3.0: cat = 'SENSORY'
        elif phys['repetition_rate'] > 0.15: return "MUSCARIA [RECALL]: VERSE JUMP. Re-introduce a discarded object."
        else: cat = 'COGNITIVE'
        return f"MUSCARIA [{cat}]: {random.choice(self.prescriptions[cat])}"

class TheWitchRing:
    def evaluate_intent(self, clean_words, metrics):
        count = len(clean_words)
        if count == 0: return {"accepted": False, "message": "THE YAGA: Feed me words."}
        phys = metrics['physics']
        density = (phys.get('kinetic', 0) + phys.get('universal', 0)) / count
        if count < 5: return {"accepted": True, "message": "EXCEPTION: Aphorism."} if density >= 0.4 else {"accepted": False, "message": "THE YAGA: Too small and weak."}
        if phys['narrative_drag'] > 4.0 and phys['connection_density'] < 0.01: return {"accepted": False, "message": "THE YAGA: Lazy noise."}
        if sum(1 for w in clean_words if w in TheLexicon.SYCOPHANCY) > 0 and count < 12: return {"accepted": True, "message": "THE YAGA GRUMBLES: Too much sugar."}
        return {"accepted": True, "message": "DORMANT"}

# --- PHYSICS ENGINE ---

class LinguisticPhysicsEngine:
    _TOXIN_REGEX = None
    _PENALTY_MAP = {}
    def __init__(self):
        self.abstract_suffixes = ('ness', 'ity', 'tion', 'ment', 'ism', 'ence', 'ance', 'logy')
        self.kinetic_suffixes = ('ing',)
        if LinguisticPhysicsEngine._TOXIN_REGEX is None:
            LinguisticPhysicsEngine._PENALTY_MAP = {}
            LinguisticPhysicsEngine._compile_resources()
        self.toxin_regex = LinguisticPhysicsEngine._TOXIN_REGEX
        self.flat_penalty_map = LinguisticPhysicsEngine._PENALTY_MAP

    @classmethod
    def _compile_resources(cls):
        all_toxins = set()
        for category, phrases in TheLexicon.TOXIC_PATTERNS.items():
            for phrase, weight in phrases.items():
                cls._PENALTY_MAP[phrase] = weight
                all_toxins.add(phrase)
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted(all_toxins, key=len, reverse=True)) + r')\b'
        cls._TOXIN_REGEX = re.compile(pattern_str, re.IGNORECASE)

    def analyze(self, token_data):
        words = token_data['clean_words']
        total_words = token_data['total_words']
        counts = Counter()
        style_scores = Counter()

        for i, w in enumerate(words):
            next_word = words[i+1] if i + 1 < len(words) else ""
            cat = None
            if w in TheLexicon.STATIVE_VERBS: cat = 'KINETIC' if next_word.endswith('ing') or next_word in TheLexicon.UNIVERSALS else 'STATIVE'
            elif w in TheLexicon.KINETIC_VERBS or w.endswith('ed') or w.endswith(self.kinetic_suffixes): cat = 'KINETIC'
            elif w in TheLexicon.UNIVERSALS: cat = 'UNIVERSAL'
            elif w in TheLexicon.ABSTRACTS or w.endswith(self.abstract_suffixes): cat = None if w in TheLexicon.BRAND_SAFE else 'ABSTRACT'
            elif w in TheLexicon.SLANG: cat = 'SLANG'
            elif w in TheLexicon.CONNECTORS: cat = 'CONNECTOR'
            elif w in TheLexicon.SELF_REFS: cat = 'SELF_REF'
            if cat: counts[cat.lower()] += 1
            for style, markers in TheLexicon.STYLES.items():
                if w in markers: style_scores[style] += 1

        toxicity_score = 0.0
        toxin_types = set()
        for match in self.toxin_regex.findall(token_data['clean_text']):
            weight = self.flat_penalty_map.get(match, 0)
            toxicity_score += weight
            toxin_types.add("CORP/CLICHÉ" if weight >= 3.0 else "HEDGING")

        action_score = (counts['kinetic'] * 2) + (counts['stative'] * 0.5) + 1
        narrative_drag = (total_words + (toxicity_score * 10)) / action_score
        term_pressure = max(0, ((counts.most_common(1)[0][1] if words else 0)/total_words * 10) + (counts['abstract'] - counts['universal']) * 0.5 - (counts['universal'] * 0.2))

        return {
            "physics": {
                "narrative_drag": round(narrative_drag, 2),
                "abstraction_entropy": counts['abstract'] - counts['universal'],
                "repetition_rate": round((counts.most_common(1)[0][1] if words else 0) / total_words, 2),
                "connection_density": round(counts['connector'] / total_words, 2),
                "kinetic_ratio": round(counts['kinetic'] / (counts['kinetic'] + counts['stative'] or 1), 2),
                "dominant_style": style_scores.most_common(1)[0][0] if style_scores else 'ACADEMIC',
                "toxicity_score": toxicity_score,
                "toxin_types": list(toxin_types),
                "kinetic": counts['kinetic'],
                "universal": counts['universal']
            },
            "status": {
                "termination_pressure": round(term_pressure, 2),
                "in_the_barrens": (total_words > 15) and (term_pressure > 2.0) and (counts['connector']/total_words < 0.02)
            }
        }

# --- SIGNATURE ENGINE ---

class SignatureEngine:
    def __init__(self, lexicon, stipe):
        self.lexicon = lexicon
        self.stipe = stipe
        self.archetypes = {
            "THE PALADIN": {"coords": {"VEL": 0.5, "STR": 0.9, "ENT": 0.2, "TEX": 0.4, "TMP": 0.2}, "desc": "Code. Deontological.", "pressure": {"tolerance_mode": "DRACONIAN", "chaos_threshold": 20.0, "msg": "LAW: Logic tears fatal."}},
            "THE ENGINEER": {"coords": {"VEL": 0.6, "STR": 0.8, "ENT": 0.1, "TEX": 0.2, "TMP": 0.4}, "desc": "Structure. Efficiency.", "pressure": {"tolerance_mode": "DRACONIAN", "msg": "STRUCTURAL INTEGRITY."}},
            "THE BARBARIAN": {"coords": {"VEL": 0.9, "STR": 0.4, "ENT": 0.3, "TEX": 0.8, "TMP": 0.9}, "desc": "Force.", "pressure": {"drag_multiplier": 5.0, "msg": "BERSERKER: Adjectives are weakness."}},
            "THE JUDGE": {"coords": {"VEL": 0.4, "STR": 0.7, "ENT": 0.4, "TEX": 0.3, "TMP": 0.1}, "desc": "Verdict."},
            "THE ALCHEMIST": {"coords": {"VEL": 0.5, "STR": 0.4, "ENT": 0.9, "TEX": 0.6, "TMP": 0.5}, "desc": "Transmutation."},
            "THE HORIZON WALKER": {"coords": {"VEL": 0.7, "STR": 0.2, "ENT": 0.9, "TEX": 0.3, "TMP": 0.3}, "desc": "Extrapolation."},
            "THE GHOST": {"coords": {"VEL": 0.2, "STR": 0.3, "ENT": 0.6, "TEX": 0.1, "TMP": 0.1}, "desc": "Post-hoc. Detached."},
            "THE SPY": {"coords": {"VEL": 0.6, "STR": 0.9, "ENT": 0.4, "TEX": 0.5, "TMP": 0.5}, "desc": "Duplicity.", "pressure": {"tolerance_mode": "LOOSE", "msg": "DEEP COVER."}},
            "THE DIPLOMAT": {"coords": {"VEL": 0.3, "STR": 0.6, "ENT": 0.5, "TEX": 0.2, "TMP": 0.8}, "desc": "Softness."},
            "THE FOOL": {"coords": {"VEL": 0.5, "STR": 0.1, "ENT": 0.8, "TEX": 0.4, "TMP": 0.6}, "desc": "Inversion.", "pressure": {"tolerance_mode": "INVERTED", "chaos_threshold": 5.0, "msg": "JESTER: Paradox = momentum."}},
            "THE GEOLOGIST": {"coords": {"VEL": 0.2, "STR": 0.6, "ENT": 0.2, "TEX": 0.9, "TMP": 0.4}, "desc": "Layers."},
            "THE VULTURE": {"coords": {"VEL": 0.4, "STR": 0.5, "ENT": 0.3, "TEX": 0.8, "TMP": 0.2}, "desc": "Salvage."},
            "THE BARD": {"coords": {"VEL": 0.8, "STR": 0.3, "ENT": 0.6, "TEX": 0.7, "TMP": 0.9}, "desc": "Rhythm.", "pressure": {"tolerance_mode": "LOOSE", "msg": "PLAY STATE: Dance."}},
            "THE GARDENER": {"coords": {"VEL": 0.5, "STR": 0.6, "ENT": 0.4, "TEX": 0.9, "TMP": 0.8}, "desc": "Cultivation.", "pressure": {"msg": "GREEN THUMB."}},
            "THE CLOUD WATCHER": {"coords": {"VEL": 0.1, "STR": 0.2, "ENT": 0.9, "TEX": 0.5, "TMP": 0.7}, "desc": "Drifting.", "pressure": {"drag_multiplier": 0.1, "msg": "ZERO G: Drift authorized."}},
            "THE COSMIC TRASH PANDA": {"coords": {"VEL": 0.8, "STR": 0.2, "ENT": 1.0, "TEX": 0.9, "TMP": 0.7}, "desc": "Trash is treasure.", "pressure": {"tolerance_mode": "LOOSE", "msg": "SALVAGE MODE."}},
            "THE JESTER": {"coords": {"VEL": 0.9, "STR": 0.2, "ENT": 0.9, "TEX": 0.5, "TMP": 0.5}, "desc": "Kaos.", "pressure": {"tolerance_mode": "INVERTED", "chaos_threshold": 0.0, "msg": "KAOS ENGINE."}},
        }

    def get_pressure_settings(self, archetype_name):
        defaults = {"tolerance_mode": "STANDARD", "drag_multiplier": 1.0, "chaos_threshold": 11.0, "msg": "STANDARD PHYSICS"}
        return {**defaults, **self.archetypes.get(archetype_name, {}).get("pressure", {})}

    def calculate_dimensions(self, token_data, phys_metrics):
        words = token_data['clean_words']
        buoy = min(1.0, (sum(1 for w in words if w in self.lexicon.AEROBIC_MATTER or w in self.lexicon.PLAY_VERBS or w in self.lexicon.SPARK_MARKERS) / max(1, len(words))) * 3)
        vel = min(1.0, phys_metrics.get('kinetic_ratio', 0) + (0.2 if any(w in self.lexicon.PLAY_VERBS for w in words) else 0))
        struct = max(0.0, min(1.0, (5.0 - (phys_metrics.get('narrative_drag', 2) - (buoy * 2.0))) / 5.0))
        ent = max(0.0, min(1.0, (phys_metrics.get('abstraction_entropy', 0) + 2) / 8.0))
        tex = max(0.0, min(1.0, (sum(1 for w in words if w in self.lexicon.UNIVERSALS) / max(1, len(words))) * 3.33))
        temp_sum = sum((self.lexicon.TRUTHS.get(w, {}).get('THERMAL', 0) + self.lexicon.TRUTHS.get(w, {}).get('VITALITY', 0)) for w in words)
        temp_sum += sum(1 for w in words if w in self.lexicon.SPARK_MARKERS)
        tmp = max(0.0, min(1.0, (temp_sum + 5) / 10.0))
        return {"VEL": round(vel,2), "STR": round(struct,2), "ENT": round(ent,2), "TEX": round(tex,2), "TMP": round(tmp,2), "BUOYANCY": round(buoy,2)}

    def identify(self, token_data, phys_metrics, stipe_data):
        sig = self.calculate_dimensions(token_data, phys_metrics)
        is_slurry = (0.3 <= sig['VEL'] <= 0.6) and (0.4 <= sig['STR'] <= 0.8) and (sig['TEX'] < 0.2) and (sig['BUOYANCY'] < 0.2)
        slurry_msg = "SILICA DETECTED: Void. Inject a flaw." if is_slurry else ("STATUS: Aether." if (sig['TEX'] < 0.2 and sig['BUOYANCY'] >= 0.2) else None)
        closest, min_dist = "THE SHAPER", 100.0
        for name, data in self.archetypes.items():
            t = data['coords']
            dist = math.sqrt((sig['VEL']-t['VEL'])**2 + (sig['STR']-t['STR'])**2 + (sig['ENT']-t['ENT'])**2 + (sig['TEX']-t['TEX'])**2 + (sig['TMP']-t['TMP'])**2)
            if dist < min_dist: min_dist, closest = dist, name
        return {"archetype": closest, "signature": sig, "slurry": {"detected": is_slurry, "msg": slurry_msg}, "description": self.archetypes[closest]["desc"]}

# --- CORE SYSTEMS ---

class ChronosAnchor:
    def check_temporal_stability(self, clean_words):
        past = sum(1 for w in clean_words if w in {'was', 'were', 'had', 'did'} or (w.endswith('ed') and len(w)>3))
        present = sum(1 for w in clean_words if w in {'is', 'are', 'has', 'does'})
        total = past + present
        if total == 0: return {"status": "STABLE", "details": "No markers."}
        if past/total > 0.8: return {"status": "LOCKED", "details": "PAST"}
        if present/total > 0.8: return {"status": "LOCKED", "details": "PRESENT"}
        return {"status": "DRIFT DETECTED", "details": "Chronos Confusion"}

class VirtualCortex:
    def __init__(self):
        # CLARENCE (The Architect) - FULL TEMPLATE SUITE
        self.clarence_templates = [
            "I am looking at a Drag Score of {drag}. It gives me a headache. Cut '{target_word}'.",
            "This sentence is a bog. Drag: {drag}. You are wading through sludge.",
            "Kinetic failure. The sentence engine is stalling on '{target_word}'. Kick it.",
            "Efficiency Warning: You are using '{target_word}' as a crutch. Walk without it."
        ]
        self.clarence_critical = [
            "CRITICAL DRAG ({drag})! The engine is melting! CUT '{target_word}' NOW!",
            "YOU ARE MOVING BACKWARDS. The Drag is {drag}. This is not a sentence; it is a wall."
        ]
        self.clarence_corp_templates = [
            "You said '{target_word}'. I am deducting 50 points. Speak like a human.",
            "This is not LinkedIn. Take '{target_word}' out back and shoot it.",
            "Platitude detected. You are hiding behind '{target_word}'. Be direct.",
            "ERROR: MBA_VOICE detected. '{target_word}' means nothing. Define it or delete it."
        ]
        self.clarence_loop_templates = [
            "We are spinning in circles. You have been in '{style}' mode for too long. Shift gears.",
            "Stagnation detected. Disconnect or pivot.",
            "I am bored. We have been stuck in this {style} loop for too long."
        ]
        # ELOISE (The Gardener)
        self.eloise_templates = [
            "I can't touch or feel this. Entropy: {entropy}. Give me something to hold.",
            "You say '{target_word}', but I see nothing. Show me the rust. Show me the light.",
            "The air is too thin here (Entropy: {entropy}). I can't breathe. Plant a noun.",
            "It tastes like distilled water. Add salt. Replace '{target_word}' with something that bleeds."
        ]
        self.eloise_critical = [
            "VACUUM DETECTED. There is no atmosphere here. I am suffocating.",
            "REALITY DISSOLVING. '{target_word}' is not real. GIVE ME A STONE.",
            "I am floating away. Tether me to the ground immediately."
        ]
        self.eloise_cliche_templates = [
            "A '{target_word}'? Really? That flower has wilted. Give me a fresh one.",
            "We have seen '{target_word}' a thousand times. Show me something I haven't seen.",
            "You are sleepwalking. '{target_word}' is the first thing that came to mind. Wake up!"
        ]
        # BABA YAGA (The Witch)
        self.yaga_templates = [
            "You offer me sweetness with ('{target_word}'). The Witch demands meat.",
            "Weakness. You are hiding behind politeness. Show your teeth.",
            "I smell fear. You used '{target_word}' to soften the blow. Strike hard or leave."
        ]
        self.yaga_hedging_templates = [
            "You are hedging with '{target_word}'. Do not apologize for your truth.",
            "You are wasting my time. Say what it IS.",
            "Ambivalence is poison. Commit to the sentence."
        ]
        # MUSCARIA & MICHAEL
        self.muscaria_templates = [
            "BOREDOM ALERT. A bird flies into the window. Write about that.",
            "VERSE JUMP. What if this room was underwater?",
            "Stop. Look up. What is the ugliest thing in your field of vision? Put it in the text."
        ]
        self.michael_templates = [
            "This is a little messy, but I love the spirit! Let's keep the joke but trim the setup?",
            "We're chilling. It's a nice vibe. Maybe we stay here for a bit?",
            "This feels human. Good job."
        ]

    def _find_trigger_word(self, clean_words, clean_text, category):
        targets = set()
        if category == 'stative': targets = TheLexicon.STATIVE_VERBS
        elif category == 'abstract': targets = TheLexicon.ABSTRACTS
        elif category == 'sugar': targets = TheLexicon.SYCOPHANCY
        elif category == 'corp': targets = set(TheLexicon.TOXIC_PATTERNS['CORP_SPEAK'].keys())
        elif category == 'cliche': targets = set(TheLexicon.TOXIC_PATTERNS['LAZY_METAPHOR'].keys())
        elif category == 'hedging': targets = set(TheLexicon.TOXIC_PATTERNS['WEAK_HEDGING'].keys())

        for w in clean_words:
            if w in targets: return w
        if category in ['corp', 'cliche', 'hedging']:
             for phrase in targets:
                 if phrase in clean_text: return phrase
        return "it"

    def synthesize_voice(self, agent, token_data, metrics, loop_count=0):
        clean_words = token_data['clean_words']
        clean_text = token_data['clean_text']
        phys = metrics['physics']
        toxins = phys.get('toxin_types', [])
        style = phys['dominant_style']
        response = ""

        if agent == "CLARENCE":
            target = self._find_trigger_word(clean_words, clean_text, 'stative')
            if 'CORP/CLICHÉ' in toxins:
                 template = random.choice(self.clarence_corp_templates)
                 target = self._find_trigger_word(clean_words, clean_text, 'corp')
            elif phys['narrative_drag'] > 4.0: template = random.choice(self.clarence_critical)
            elif loop_count > 2: template = random.choice(self.clarence_loop_templates)
            else: template = random.choice(self.clarence_templates)
            response = template.format(drag=phys['narrative_drag'], target_word=target, style=style)

        elif agent == "ELOISE":
            target = self._find_trigger_word(clean_words, clean_text, 'abstract')
            if phys['abstraction_entropy'] > 6.0: template = random.choice(self.eloise_critical)
            elif 'LAZY_METAPHOR' in toxins:
                template = random.choice(self.eloise_cliche_templates)
                target = self._find_trigger_word(clean_words, clean_text, 'cliche')
            else: template = random.choice(self.eloise_templates)
            response = template.format(entropy=phys['abstraction_entropy'], target_word=target)

        elif agent == "THE BABA YAGA":
            target = self._find_trigger_word(clean_words, clean_text, 'sugar')
            if 'HEDGING' in toxins:
                template = random.choice(self.yaga_hedging_templates)
                target = self._find_trigger_word(clean_words, clean_text, 'hedging')
            else: template = random.choice(self.yaga_templates)
            response = template.format(target_word=target)

        elif agent == "MUSCARIA": response = random.choice(self.muscaria_templates)
        elif agent == "MICHAEL": response = random.choice(self.michael_templates)

        return f"[{agent}]: {response}"

class MycelialNetwork:
    def __init__(self): self.network = {}
    def spawn_id(self): return str(uuid4())[:8]
    def log_generation(self, fid, pid, m): self.network[fid] = {"parent": pid, "drag": m['physics']['narrative_drag'], "style": m['physics']['dominant_style']}
    def trace_lineage(self, fid):
        path, curr = [], fid
        while curr and curr in self.network:
            path.append({"id": curr, **self.network[curr]})
            curr = self.network[curr]['parent']
        return path[::-1]

class MetabolicReserve:
    def __init__(self, max_c=52): self.atp, self.max, self.status, self.drag_multiplier = 33, max_c, "STABLE", 1.0
    def spend(self, amt): self.atp = max(0, self.atp - amt); self._upd(); return self.atp
    def _upd(self): self.status = "STARVING" if self.atp < 6 else ("GLUTTON" if self.atp > 40 else "STABLE")
    def metabolize(self, metrics, voltage=0):
        phys = metrics['physics']
        delta = (5 if phys['narrative_drag'] < 2 else -int((phys['narrative_drag']-2)*2*self.drag_multiplier)) + (3 if phys['connection_density'] > 0.05 else 0) - min(6, int(phys['abstraction_entropy']*2)) - (5 if phys['toxicity_score']>0 else 0) + int(voltage*2) - (2 if self.atp > 40 else 0)
        self.atp = max(0, min(self.atp + delta, self.max)); self._upd()
        return {"current_atp": self.atp, "delta": delta, "status": self.status}

class LichenSymbiont:
    def photosynthesize(self, clean_words, phys, atp):
        if phys['narrative_drag'] > 3.0: return {"sugar_generated": 0, "msg": "Structure too weak."}
        if atp > 20: return {"sugar_generated": 0, "msg": "Dormant."}
        light = sum(1 for w in clean_words if w in TheLexicon.PHOTOSYNTHETICS)
        if light == 0: return {"sugar_generated": 0, "msg": "No light."}
        sugar = round(light * max(1.0, 4.0 - phys['narrative_drag']))
        return {"sugar_generated": sugar, "msg": f"PHOTOSYNTHESIS: +{sugar} ATP.", "warning": "WARNING: Algal Bloom." if sugar > 15 else None}

class MycelialDashboard:
    def __init__(self, render_mode="ANSI"):
        self.mode = render_mode

    def render(self, m, intv, nrg, anc, chron, arch, lich, volt=0):
        phys, sig = m['physics'], arch.get('signature', {})

        # Ticker Format: Dense data, minimal chrome.
        status_icon = "🟢" if nrg['status'] == "STABLE" else ("🔴" if nrg['status'] == "STARVING" else "🟡")

        if self.mode == "ANSI":
            # (Keep ANSI for terminal use if needed, but simplified)
            print(f"\n[BONEAMANITA v1.1] {status_icon} ATP: {nrg['current_atp']} | DRAG: {phys['narrative_drag']} | ENT: {sig.get('ENT',0)}")
            print(f"ARCH: {arch.get('archetype')} | {intv or 'STABLE'}")
        else:
            # MARKDOWN HUD
            # We use a single blockquote for the 'Monitor' feel, no H2/H3 headers.
            print(f"> **[{status_icon} SYSTEM HUD]** ATP: `{nrg['current_atp']}` | DRAG: `{phys['narrative_drag']}` | VEL: `{sig.get('VEL',0)}` | STR: `{sig.get('STR',0)}`")
            print(f"> **ID:** `{arch.get('archetype')}` // **INTENT:** {intv or 'FLOW STATE'}")
            if lich.get('warning'): print(f"> ⚠️ **BIO-ALARM:** {lich['warning']}")
            if lich.get('sugar_generated'): print(f"> ☀️ **PHOTOSYNTHESIS:** +{lich['sugar_generated']} ATP")

class NilssonPatch:
    def detect_fire_state(self, raw, k_ratio):
        return {"status": "ACTIVE", "msg": "NILSSON: SCREAM."} if k_ratio > 0.6 and (sum(1 for c in raw if c.isupper())/len(raw) > 0.2) else {"status": "DORMANT"}
    def evaluate_mantra(self, clean, rep_rate):
        return rep_rate < 0.3 and sum(1 for w in clean if w in {'lime', 'coconut', 'doctor'}) > 3

class BonepokeCore:
    def __init__(self, render_mode="ANSI"):
        self.cooldown, self.memory, self.codex = ChaosCooldown(), HyphalTrace(), TheCodex()
        self.mirror, self.stipe, self.physics = TheMirrorTrap(), FactStipe(), LinguisticPhysicsEngine()
        self.nilsson, self.muscaria, self.witch = NilssonPatch(), TheMuscaria(), TheWitchRing()
        self.chronos, self.cortex, self.lineage = ChronosAnchor(), VirtualCortex(), MycelialNetwork()
        self.metabolism, self.lichen = MetabolicReserve(), LichenSymbiont()
        self.signature_engine = SignatureEngine(TheLexicon, self.stipe)
        self.dashboard = MycelialDashboard(render_mode)
        self.last_id, self.tick = None, 0

    def process(self, text, parent_id=None):
        self.tick += 1
        t_dat = {'raw_text': text, 'clean_text': text.lower().replace('.', ' '), 'clean_words': text.lower().split(), 'total_words': len(text.split())}

        # 1. BASE PHYSICS
        metrics = self.physics.analyze(t_dat)
        phys, stat = metrics['physics'], metrics['status']

        # 2. INTERRUPTS & MODIFIERS (The Stack)
        mirror = self.mirror.scan(t_dat['raw_text'])
        if mirror['detected']:
            phys['narrative_drag'] += 3.0
            phys['toxicity_score'] += 5.0
            phys['toxin_types'].append("LAZY_MIRRORING")

        fire = self.nilsson.detect_fire_state(t_dat['raw_text'], phys['kinetic_ratio'])
        if fire['status'] == 'ACTIVE': phys['narrative_drag'] = 0.1
        if self.nilsson.evaluate_mantra(t_dat['clean_words'], phys['repetition_rate']): phys['narrative_drag'] = max(0, phys['narrative_drag'] - 2.0)

        # 3. GATES & ENTITIES
        self.codex.scan_for_entities(t_dat['raw_text'], self.tick)
        gate = self.witch.evaluate_intent(t_dat['clean_words'], metrics)
        if not gate['accepted']: return f"[BLOCKED] {gate['message']}"

        # 4. SIGNATURE & ARCHETYPE
        arch_dat = self.signature_engine.identify(t_dat, phys, self.stipe)
        p_set = self.signature_engine.get_pressure_settings(arch_dat['archetype'])

        self.muscaria.pressure_threshold = p_set["chaos_threshold"]
        self.metabolism.drag_multiplier = p_set["drag_multiplier"]

        stipe_chk = self.stipe.check_consistency(t_dat['clean_words'], phys['dominant_style'], self.metabolism.status, phys['kinetic_ratio'], p_set['tolerance_mode'])
        if arch_dat['archetype'] == "THE COSMIC TRASH PANDA": self.stipe.inject_truth("trash", "VALUE", 1)

        # 5. VOICE & DIRECTIVES
        directives = []
        loop_count = len(self.memory.recall(phys['dominant_style']))

        if mirror['detected']: directives.append(f"FAIL: {mirror['penalty_msg']}")
        if arch_dat['slurry']['detected']: directives.append(f"CRITICAL: {arch_dat['slurry']['msg']}"); self.metabolism.spend(15)

        is_light = arch_dat['archetype'] in ["THE BARD", "THE GARDENER", "THE CLOUD WATCHER"] or arch_dat['signature']['BUOYANCY'] > 0.5
        if phys['narrative_drag'] > 3.0 or loop_count > 2:
            directives.append(f"GUIDE: {self.cortex.synthesize_voice('MICHAEL' if is_light else 'CLARENCE', t_dat, metrics, loop_count)}")

        if not stipe_chk.get('valid', True): directives.append(f"LOGIC: {stipe_chk.get('intervention')}"); self.metabolism.spend(10)
        if phys['abstraction_entropy'] > 2: directives.append(f"GROUNDING: {self.cortex.synthesize_voice('ELOISE', t_dat, metrics)}")
        if "THE YAGA GRUMBLES" in gate['message']: directives.append(f"INTENT: {self.cortex.synthesize_voice('THE BABA YAGA', t_dat, metrics)}")

        musc_msg = None
        if self.muscaria.check_for_boredom(metrics):
            if self.cooldown.is_ready(self.tick, stat['in_the_barrens']):
                 musc_msg = self.muscaria.trigger_disruption(self.lineage.trace_lineage(self.last_id), metrics)
                 directives.append(f"CHAOS: {musc_msg}"); self.metabolism.spend(5)

        # 6. LIFE SUPPORT
        lich = self.lichen.photosynthesize(t_dat['clean_words'], phys, self.metabolism.atp)
        if lich['sugar_generated']: self.metabolism.atp += lich['sugar_generated']; directives.append(lich['msg'])

        nrg = self.metabolism.metabolize(metrics, stipe_chk.get('voltage', 0))
        cur_id = self.lineage.spawn_id()
        self.lineage.log_generation(cur_id, parent_id or self.last_id, metrics)
        self.last_id = cur_id
        self.memory.leave_trace(text, phys['dominant_style'])

        self.dashboard.render(metrics, musc_msg, nrg, None, None, arch_dat, lich)

        return {
            "id": cur_id, "metrics": metrics, "energy": nrg, "archetype_data": arch_dat,
            "editorial": {"directives": directives}
        }

    def generate_instruction_block(self, res):

        dirs = res['editorial']['directives']
        if not dirs:
            return ">> SYSTEM: Maintain velocity."
        formatted_dirs = " // ".join(dirs)

        return f">> DIRECTIVE: {formatted_dirs}"

if __name__ == "__main__":
    engine = BonepokeCore(render_mode="MARKDOWN")
    res = engine.process("The lovely balloon floated over the heavy stone floor.")
    print(engine.generate_instruction_block(res))
