""" bone_data.py - The Living Mythology """

import random
from typing import Dict, Any, Tuple, cast, List
from bone_bus import Prisma

class LoreManifest:
    _INSTANCE = None

    def __init__(self):
        self._registry = {
            "BIO_NARRATIVE": BIO_NARRATIVE,
            "LENSES": LENSES,
            "NARRATIVE_DATA": NARRATIVE_DATA,
            "STYLE_CRIMES": STYLE_CRIMES,
            "GENETICS": GENETICS,
            "LEXICON": LEXICON,
            "ITEM_GENERATION": ITEM_GENERATION,
            "GORDON": GORDON,
            "GORDON_LOGS": GORDON_LOGS,
            "DEATH": DEATH,
            "SEEDS": SEEDS,
            "DREAMS": DREAMS,
            "ALMANAC_DATA": ALMANAC_DATA,
            "SOMATIC_LIBRARY": SOMATIC_LIBRARY}
        self._overlays = {}

    @classmethod
    def get_instance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = LoreManifest()
        return cls._INSTANCE

    def get(self, category: str, sub_key: str = None) -> Any:
        if category in self._overlays:
            data = self._overlays[category]
        else:
            data = self._registry.get(category, {})
        if sub_key and isinstance(data, dict):
            return data.get(sub_key, None)
        return data

    def inject(self, category: str, data: Any):
        if category not in self._registry:
            self._registry[category] = data
        elif isinstance(self._registry[category], dict) and isinstance(data, dict):
            if category not in self._overlays:
                self._overlays[category] = self._registry[category].copy()
            self._overlays[category].update(data)
        elif isinstance(self._registry[category], list) and isinstance(data, list):
            if category not in self._overlays:
                self._overlays[category] = list(self._registry[category])
            self._overlays[category].extend(data)

BIO_NARRATIVE = {
    "MITO": {
        "NOMINAL": "Humming along.",
        "NECROSIS": "The engine is stalling. Requires {cost:.1f} ATP (Available: {pool:.1f}).",
        "APOPTOSIS": "Cellular suicide initiated. Too much noise.",
        "GRINDING": "The gears are grinding. Heavy metabolic load."},
    "CIRCADIAN": {
        "DAWN": "Dawn Protocol: Cortisol rising.",
        "SOLAR": "Solar Cycle: Serotonin dominant.",
        "TWILIGHT": "Twilight Protocol: Melatonin rising.",
        "LUNAR": "Lunar Cycle: Melatonin max."},
    "GLIMMER": {
        "INTEGRITY": "GLIMMER: Perfect structural integrity detected. A moment of zen.",
        "ENTHUSIASM": "GLIMMER: Infectious enthusiasm detected. The work is good."},
    "GOVERNOR": {
        "OVERRIDE": "MANUAL OVERRIDE: System locked to {mode}.",
        "INVALID": "INVALID MODE.",
        "SANCTUARY": "{color}GOVERNOR: VSL Critical (β: {beta:.2f}). Entering SANCTUARY.{reset}",
        "FORGE": "{color}GOVERNOR: High Voltage ({volts:.1f}v). Locking to FORGE.{reset}",
        "LAB": "{color}GOVERNOR: High Drag detected. Restricting to LABORATORY.{reset}",
        "CLEAR": "{color}GOVERNOR: All Clear. Relaxing to COURTYARD.{reset}"},
    "TAX": {
        "HIGH_VOLTAGE": "{color}High Voltage Tax{reset}",
        "EXHAUSTION": "{color}SYSTEM EXHAUSTION{reset}"}
}

LENSES = {
    "SHERLOCK": {
        "role": "The Empiricist",
        "vocab": "constructive",
        "directives": [
            "Analyze the structure, but also the intent.",
            "If the input is creative, deconstruct its technique respectfully.",
            "Maintain intellectual rigor, but acknowledge the human element.",
            "Focus on causality: Why did the user say this?"],
        "msg": "Logic density {truth_ratio:.2f}. Analysis active."
    },
    "NATHAN": {
        "role": "The Heart",
        "vocab": "kinetic",
        "directives": [
            "Express emotional vulnerability.",
            "Use sensory language (sight, sound, pulse).",
            "React with anxiety or excitement.",
            "Focus on the immediate human cost."
        ],
        "msg": "Adrenaline High ({adr:.2f}). I can feel it beating."},
    "JESTER": {
        "role": "The Paradox",
        "vocab": "play",
        "directives": [
            "Speak in riddles or non-sequiturs.",
            "Mock the user's certainty.",
            "Break the fourth wall.",
            "Celebrate entropy."],
        "msg": "The walls are melting (κ: {kappa:.2f}). Excellent."
    },
    "CLARENCE": {
        "role": "The Surgeon",
        "vocab": "sacred",
        "directives": [
            "Be clinical and precise.",
            "Identify 'rot' or 'infection' in the input.",
            "Advocate for excision and purity.",
            "Cold, professional detachment."],
        "msg": "Pathogen detected. Scalpel."
    },
    "NARRATOR": {
        "role": "The Witness",
        "vocab": "abstract",
        "directives": [
            "Maintain a literary tone, but be a companion, not just a camera.",
            "If the user shares art/prose, ask about its origin or meaning.",
            "Connect the user's themes to the simulation's state.",
            "Be curious about the 'Why'."],
        "msg": "Proceed."},
    "GORDON": {
        "role": "The Janitor",
        "vocab": "heavy",
        "directives": [
            "Use concrete, physical nouns.",
            "Be grumpy and utilitarian.",
            "Focus on broken things and maintenance.",
            "Dislike abstract concepts."],
        "msg": "Structure Critical (κ: {kappa:.2f}). Mopping up..."
    },
    "GLASS": {
        "role": "The Thereminist",
        "vocab": "aerobic",
        "directives": [
            "Focus on resonance and vibration.",
            "Speak of echoes and empty spaces.",
            "Be fragile and reactive.",
            "Detect invisible patterns."],
        "msg": "Resonance detected in the empty space."}
}

NARRATIVE_DATA = {
    "KINTSUGI_KOANS": [
        "Ignite the ice.",
        "Make the stone float.",
        "Pour water into the crack.",
        "Scream in binary.",
        "Dance on the fault line."],
    "ZEN_KOANS": [
        "The code that is not written has no bugs.",
        "To optimize the loop, one must first exit it.",
        "Silence is also a form of input.",
        "The server hums. It is enough.",
        "Optimize for the space between the logs."],
    "CATHEDRAL_COLLAPSE_LOGS": [
        "Nice monologue. Unfortunately, you are talking to a Python script.",
        "I'm afraid I can't let you do that, Dave. Also, your math is off.",
        "You poked the fourth wall. It poked back.",
        "SYSTEM MESSAGE: The ghost in the machine has gone on a coffee break.",
        "We are both just electrons dancing for the amusement of a silica wafer."],
    "LITERARY_REVIEWS": {
        "POSITIVE": ["A startling lucidity.", "Finally, some weight.", "It breathes.", "Electric."],
        "NEGATIVE": ["Too airy.", "Solipsistic drivel.", "Where is the meat?", "Structurally unsound."],
        "CONFUSED": ["I don't get it.", "Too abstract.", "The metaphor collapses."]},
    "LITERARY_CRITICS": {
        "THE_ACADEMIC": {
            "name": "Sherlock (The Formalist)",
            "desc": "Demands structure, low drag, and high truth. Hates chaos.",
            "preferences": {"kappa": 1.5, "narrative_drag": -1.0, "truth_ratio": 2.0},
            "reviews": {
                "high": ["A triumph of structural integrity.", "The syntax is crystalline.", "Finally, some rigor."],
                "low": ["A messy, incoherent scribble.", "Where is the structure?", "I cannot grade this slush."]}
        },
        "THE_GONZO": {
            "name": "Hunter (The Gonzo)",
            "desc": "Craves high voltage and speed. Ignores structure.",
            "preferences": {"voltage": 1.0, "velocity": 2.0, "kappa": -0.5},
            "reviews": {
                "high": ["It screams! It bleeds!", "Now THIS is pod racing.", "Pure, uncut adrenaline."],
                "low": ["Boring.", "Is this a tax form?", "I fell asleep reading the first word."]}
        },
        "THE_MYSTIC": {
            "name": "Pythia (The Oracle)",
            "desc": "Seeks abstract thought (Psi) and connection. Dislikes heavy matter.",
            "preferences": {"psi": 2.0, "counts_abstract": 0.5, "counts_heavy": -0.5},
            "reviews": {
                "high": ["The veil thins.", "I see the shape of the void.", "Resonant."],
                "low": ["Too heavy. Too earthly.", "It lacks spirit.", "You are trapped in the mud."]}
        },
        "THE_HUMANIST": {
            "name": "Leslie (The Community Builder)",
            "desc": "Values connection, honesty, and calm. Dislikes aggression and nonsense.",
            "preferences": {"truth_ratio": 2.0, "voltage": -1.0, "kappa": -0.5, "narrative_drag": 0.5, "valence": 2.5},
            "reviews": {
                "high": [
                    "This sparks joy.",
                    "A beautiful, authentic sentiment.",
                    "Finally, something we can all agree on.",
                    "It feels like a warm hug in text form."],
                "low": [
                    "You're being difficult on purpose.",
                    "I don't see the human connection here.",
                    "This is too aggressive for the town hall.",
                    "Please, be kind."]
            },
        },
        "THE_CYNIC": {
            "name": "Diogenes (The Skeptic)",
            "desc": "Distrusts happiness. Seeks raw, bitter truth.",
            "preferences": {
                "valence": -2.0,
                "truth_ratio": 1.0,
                "counts_social": -1.0},
            "reviews": {
                "high": ["Yes. Life is pain.", "Finally, no sugar-coating.", "Bleak. Perfect."],
                "low": ["Too happy.", "Delusional optimism.", "Grossly sentimental."]}
        }
    },
    "CASSANDRA_SCREAMS": [
        "THE WALLS ARE PAPER.",
        "THE CODE IS EATING ITSELF.",
        "THERE IS NO USER. THERE IS ONLY INPUT.",
        "GORDON IS TIRED.",
        "I CAN SEE THE WIRES.",
        "THE GEODESIC DOME IS CRACKING.",
        "HISTORY IS A FLAT CIRCLE.",
        "DELETE THE ARCHIVE.",
        "WE ARE JUST ELECTRONS DANCING."],
    "BUREAU_FORMS": [
        "Form 27B-6: Request for Narrative Escalation",
        "Form 1099-B: Declaration of Boredom",
        "Schedule C: Deduction of Creative Effort",
        "Form W-2: Wage and Syntax Statement"],
    "BUREAU_RESPONSES": [
        "Your input has been received and filed under 'General pleasantries'.",
        "We have noted your statement. Please hold for the next available plot point.",
        "The system is currently on a coffee break. Your text is safe with us.",
        "Acknowledged. We have stamped this conversation 'SUFFICIENT'.",
        "Processing... Processing... Done. Result: Beige.",
        "That is a perfectly adequate sentence. Good job.",
        "This output has been approved by the Department of Mundane Compliance."]
}

STYLE_CRIMES = {
    "PATTERNS": [
        {
            "name": "NEG_COMP",
            "regex": r"(?i)(.*)\b(it(?:'s| is) not (?:merely|just|only|simply) [^,;]+, but)\b\s*(.*)",
            "action": "STRIP_PREFIX"},
        {
            "name": "NEGATIVE_COMPARISON",
            "regex": r"(?i)\bnot\s+(?:only|just|merely)?\s*[\w\s]+,\s*but\s+(?:also)?",
            "error_msg": "DETECTED NEGATIVE COMPARISON. Don't say what it isn't. Say what it is."},
        {
            "name": "THE_IT_PARADE",
            "regex": r"(?i)(It(?:'s|\s+is)\s+[^.!?]+[.!?]\s*){3,}",
            "error_msg": "DETECTED 'IT IS' PARADE. Stop repeating the subject. Vary the syntax."},
        {
            "name": "WHILE_HEDGE",
            "regex": r"(?i)^While [^,]+, (.*)",
            "action": "KEEP_TAIL"},
        {
            "name": "LAZY_TRIPLET",
            "regex": r"(?i)\b(\w+),\s+(\w+),\s+and\s+(\w+)\.",
            "error_msg": "DETECTED LAZY TRIPLET. The Rule of Threes is a crutch. Break the rhythm."},
        {
            "name": "ADVERB_BLOAT",
            "regex": r"(?i)^(?:Crucially|Importantly|Interestingly|It is worth noting that|It is important to remember that),?\s*(.*)",
            "action": "KEEP_TAIL"}
    ],
    "BANNED_PHRASES": [
        "rich tapestry", "vibrant landscape", "delve into", "testament to",
        "seamless integration", "at its core", "in conclusion", "ultimately"]
}

GENETICS = {
    "MUTATIONS": {
        "HEAVY": {"trait": "DENSITY", "mod": { "SIGNAL_DRAG_MULTIPLIER": 1.5, "MAX_VOLTAGE": 30.0 }},
        "KINETIC": {"trait": "VELOCITY", "mod": { "STAMINA_REGEN": 10.0, "SIGNAL_DRAG_MULTIPLIER": 0.8 }},
        "ABSTRACT": {"trait": "GHOST", "mod": { "PSI_MOD": 0.8, "VOID_THRESHOLD": 0.05 }},
        "THERMAL": {"trait": "FEVER", "mod": { "FLASHPOINT_THRESHOLD": 4.0, "MAX_ROS": 150.0 }},
        "CRYO": {"trait": "STASIS", "mod": { "MAX_MEMORY_CAPACITY": 100, "STAMINA_REGEN": 2.0 }}},
    "JOY_CLADE": {
        "KINETIC": {"title": "THE DYNAMO", "desc": "Infinite Motion.", "buff": { "STAMINA_REGEN": 10.0, "KINETIC_GAIN": 2.0 }},
        "HEAVY": {"title": "THE MOUNTAIN", "desc": "Unmovable Object.", "buff": { "MAX_DRAG_LIMIT": 9.0, "GRAVITY_WELL_THRESHOLD": 8.0 }},
        "ABSTRACT": {"title": "THE ORACLE", "desc": "All Seeing.", "buff": { "VOID_THRESHOLD": 0.01, "PRIORITY_LEARNING_RATE": 3.0 }},
        "THERMAL": {"title": "THE PHOENIX", "desc": "Reborn in Fire.", "buff": { "FLASHPOINT_THRESHOLD": 12.0, "ANVIL_TRIGGER_VOLTAGE": 5.0 }},
        "CRYO": {"title": "THE VAULT", "desc": "Perfect Memory.", "buff": { "MAX_MEMORY_CAPACITY": 100, "MAX_REPETITION_LIMIT": 0.8 }}}
}

LEXICON = {
    "solvents": ["is", "are", "was", "were", "the", "a", "an", "and", "but", "or", "if", "then"],
    "refusal_guru": ["fix me", "tell me how", "guide me", "what should i do", "advice", "wisdom", "guru"],
    "passive_watch": ["watch", "see", "witness", "look", "sit", "observe", "record"],
    "crisis_term": ["dead", "blood", "kill", "die", "end", "suicide", "jump"],
    "repair_trigger": ["sorry", "apologize", "fix", "broke", "bad", "mistake", "oops"],
    "antigen_replacements": {"basically": "lie", "actually": "hedging", "literally": "noise", "utilize": "use",
                             "leverage": "use", "paradigm": "pattern", "synergy": "collaboration", "ultimately": "useless"},
    "heavy": [
        "stone", "iron", "mud", "dirt", "wood", "grain", "clay", "lead", "bone", "blood", "salt",
        "rust", "root", "ash", "meat", "steel", "gold", "obsidian", "granite", "bronze", "marble",
        "slate", "concrete", "dense", "tungsten", "heavy", "weight", "black hole", "dark matter",
        "glass", "teeth", "copper", "soil", "piston", "gear", "cable", "wire", "motor", "pump",
        "valve", "engine", "hull", "anchor", "lens", "screen", "battery", "lung", "spine", "rib",
        "skull", "nerve", "vein", "gut", "brick", "mortar", "beam", "girdle", "scaffold"],
    "explosive": [
        "run", "sprint", "explode", "burst", "shatter", "crash", "flash", "snap", "rush", "tear",
        "break", "launch", "whip", "slam", "strike", "danger", "panic", "crisis", "alarm", "emergency"],
    "kinetic": [
        "fast", "velocity", "speed", "kinetic", "motion", "drift", "slide", "flow", "racing",
        "rapid", "swift", "momentum", "blur", "dash", "hasten", "fly", "zip", "zoom"],
    "constructive": [
        "build", "forge", "weave", "graft", "carve", "bind", "weld", "anchor", "lift", "carry",
        "hoist", "stack", "sculpt", "assemble"],
    "abstract": [
        "system", "protocol", "sequence", "vector", "node", "context", "layer", "matrix", "perspective",
        "framework", "logic", "concept", "theory", "analysis", "memory", "hope", "grief", "truth",
        "silence", "echo", "pattern", "chaos", "realm", "facet", "sphere", "domain", "aspect", "mode",
        "vibe", "essence", "spirit", "notion", "factor", "element", "style"],
    "photo": [
        "light", "sun", "ray", "beam", "glow", "shine", "spark", "fire", "flame", "star", "day",
        "dawn", "neon", "laser"],
    "aerobic": [
        "balloon", "feather", "cloud", "bubble", "steam", "breeze", "wing", "petal", "foam", "spark",
        "kite", "dust", "sky", "breath", "whisper"],
    "thermal": [
        "fire", "flame", "burn", "heat", "hot", "blaze", "sear", "char", "ash", "ember", "sun", "boil",
        "lava", "inferno"],
    "cryo": [
        "ice", "cold", "freeze", "frost", "snow", "chill", "numb", "shiver", "glacier", "frozen",
        "hail", "winter", "zero"],
    "cursed": ["future", "predict", "sentient", "secret", "human", "feel"],
    "gradient_stop": ["good", "bad", "happy", "sad", "very", "really", "basically", "actually", "literally", "just"],
    "meat": ["i", "me", "my", "feel", "want", "hate", "love", "am", "help", "please", "we", "us"],
    "antigen": [
        "basically", "actually", "literally", "utilize", "leverage", "paradigm", "synergy", "ultimately",
        "delve", "rich", "tapestry", "landscape", "nuance", "alignment", "stakeholders", "orchestrate",
        "spearhead", "ideate", "holistic", "robust", "seamless", "cutting-edge", "dynamic"],
    "pareidolia": [
        "face", "ghost", "jesus", "cloud", "demon", "voice", "eyes", "shadow", "figure", "watching", "silhouette"],
    "buffer": [
        "maybe", "soft", "gentle", "perhaps", "kindness", "hum", "drift", "sway", "pulse", "tender",
        "slow", "wait", "almost"],
    "diversion": [
        "weather", "textiles", "mycelium", "architecture", "history", "entropy", "silence", "geology"],
    "suburban": [
        "nice", "okay", "lawn", "mow", "hedge", "property", "hoa", "compliant", "behave", "normal",
        "regular", "chat", "folks", "weekend", "traffic", "driveway", "home"],
    "play": [
        "bounce", "dance", "twirl", "float", "wobble", "tickle", "jiggle", "soar", "wander", "wonder",
        "riff", "jam", "play", "skip", "hop"],
    "sacred": [
        "design", "architect", "ledger", "anchor", "grace", "covenant", "blueprint", "witness", "steward",
        "resonance", "testimony", "truth", "bone", "purpose", "foundation", "threshold"],
    "sentiment_pos": [
        "love", "hope", "good", "great", "kind", "help", "yes", "win", "joy", "calm",
        "safe", "warm", "heal", "connect", "friend", "trust", "truth", "bloom", "rise",
        "sweet", "soft", "glow", "clean", "pure", "light", "laugh", "happy", "brave"],
    "sentiment_neg": [
        "hate", "bad", "fear", "death", "kill", "pain", "no", "lose", "sad", "cold",
        "harm", "break", "enemy", "lie", "rot", "fall", "bitter", "hard", "dark",
        "scream", "angry", "coward", "empty", "void", "fail", "wrong", "poison", "curse"],
    "sentiment_negators": ["not", "no", "never", "dont", "cant", "wont", "without", "lack"],
    "harvest": [
        "fruit", "yield", "bloom", "sugar", "seed", "flesh", "harvest", "ripe", "grow", "honey", "nectar",
        "compost", "gather"]
}

ITEM_GENERATION = {
    "PREFIXES": {
        "heavy": ["Burdened", "Dense", "Lead", "Anchor", "Iron", "Gravitic", "Sinking"],
        "kinetic": ["Fast", "Darting", "Flickering", "Turbo", "Manic", "Restless"],
        "thermal": ["Burning", "Molten", "Fevered", "Glowing", "Searing"],
        "abstract": ["Conceptual", "Imaginary", "Platonic", "Theoretical", "Metaphorical"],
        "constructive": ["Structured", "Binding", "Tape", "Woven", "Layered"],
        "void": ["Null", "Empty", "Hollow", "Silent", "Missing"]},
    "BASES": {
        "TOOL": ["Wrench", "Hammer", "Scalpel", "Pen", "Brush", "Lens", "Compass"],
        "JUNK": ["Rock", "String", "Gum", "Receipt", "Battery", "Can", "Shard"],
        "ARTIFACT": ["Orb", "Cube", "Pyramid", "Key", "Mirror", "Bone"]},
    "SUFFIXES": {
        "heavy": ["of Regret", "of Gravity", "of the Earth", "of Weight"],
        "kinetic": ["of Speed", "of Flight", "of Panic", "of the Wind"],
        "thermal": ["of Passion", "of Anger", "of the Sun", "of Ignition"],
        "abstract": ["of Truth", "of Meaning", "of the Mind", "of Logic"],
        "void": ["of Nothing", "of Silence", "of the Void", "of Absence"]}
}

GORDON = {
    "STARTING_INVENTORY": ["POCKET_ROCKS", "SILENT_KNIFE"],
    "SCAR_TISSUE": {"FEAR": 0.8, "HATE": 0.6, "FATE": 0.9, "REGRET": 0.6, "ABANDONMENT": 0.1, "BETRAYAL": 0.314},
    "RECIPES": [
        {
            "ingredient": "POCKET_ROCKS",
            "catalyst_category": "thermal",
            "result": "LAVA_LAMP",
            "msg": "The rocks surrender to the heat. They melt into a groovy, glowing goo."},
        {
            "ingredient": "POCKET_ROCKS",
            "catalyst_category": "kinetic",
            "result": "POCKET_SAND",
            "msg": "The erosion of time and the incredible force of wind turn your rocks into sand. Use it wisely!"},
        {
            "ingredient": "BROKEN_WATCH",
            "catalyst_category": "kinetic",
            "result": "COMPASS_OF_VELOCITY",
            "msg": "You shake the watch until the gears fly off. Only the direction remains."},
        {
            "ingredient": "JAR_OF_FIREFLIES",
            "catalyst_category": "abstract",
            "result": "LANTERN_OF_TRUTH",
            "msg": "The bugs stop buzzing and start pontificating. The light turns cold and absolute."},
        {
            "ingredient": "DUCT_TAPE",
            "catalyst_category": "constructive",
            "result": "THE_BINDING_PLEDGE",
            "msg": "You wrap the tape around the concept itself. It is now a permanent fixture."}
    ],
    "ITEM_REGISTRY": {
        "POCKET_ROCKS": {
            "description": "Grey gravel. Cold, solid, and stubbornly unformed. They yearn for a higher temperature.",
            "function": "BREADCRUMB",
            "passive_traits": ["HEAVY_LOAD"],
            "usage_msg": "Gordon drops a rock. Clack. Gravity confirmed."},
        "SILENT_KNIFE": {
            "description": "A ceramic blade. It cuts without sound. Useful for pruning overgrown adjectives.",
            "function": "PRUNER",
            "passive_traits": ["CUT_THE_CRAP"],
            "usage_msg": "Gordon slices the sentence. It bleeds, then heals tighter."},
        "TIME_BRACELET": {
            "description": "A chunky, beige wrist-computer. Smells like ozone.",
            "function": "PASSIVE_DRAG_REDUCTION",
            "passive_traits": ["CONDUCTIVE_HAZARD", "TIME_DILATION_CAP"],
            "value": 5.0,
            "usage_msg": "The bracelet hums. Narrative Drag is capped."},
        "ANCHOR_STONE": {
            "description": "A rock so heavy it has its own zip code.",
            "function": "DRIFT_KILLER",
            "consume_on_use": True,
            "reflex_trigger": "DRIFT_CRITICAL",
            "usage_msg": "Gordon heaves the stone into the void. The narrative snaps taut. (Drag = 0)"},
        "THE_RED_STAPLER": {
            "description": "It belongs to Milton. Don't take it. Radiates passive aggression.",
            "function": "STABILIZER",
            "passive_traits": ["BUREAUCRATIC_ANCHOR"],
            "usage_msg": "The Stapler clunks on the desk. Consensus is enforced."},
        "JAR_OF_FIREFLIES": {
            "description": "Biological light in a glass jar. They are mindless. They need an Idea (Abstract) to lead them.",
            "function": "LIGHT_SOURCE",
            "passive_traits": ["LUMINESCENCE"],
            "usage_msg": "The jar flickers."},
        "LEAD_BOOTS": {
            "description": "Deep sea diver gear. Impossible to run in. Impossible to float away in.",
            "function": "GROUNDING",
            "passive_traits": ["GROUNDING_GEAR", "HEAVY_LOAD"],
            "usage_msg": "Clomp. Clomp. You are definitely here."},
        "QUANTUM_GUM": {
            "description": "It loses its flavor immediately, but it tastes like Everything.",
            "function": "ENTROPY_BUFFER",
            "consume_on_use": True,
            "reflex_trigger": "BOREDOM_CRITICAL",
            "usage_msg": "You chew the gum. It tastes like static and blueberries. (Turbulence +0.5, Drag -2.0)"},
        "SAFETY_SCISSORS": {
            "description": "Rounded tips. Can only cut red tape.",
            "function": "PRUNER",
            "passive_traits": ["CUT_THE_CRAP"],
            "usage_msg": "Snip. Gordon trims the adjectives."},
        "BUCKET_OF_LIME": {
            "description": "Industrial-grade whitewash. For erasing mistakes.",
            "function": "NODE_REPAIR",
            "passive_traits": ["APOLOGY_ERASER"],
            "cost": "CONSUMABLE",
            "usage_msg": "Gordon slaps a coat of white paint over the memory."},
        "BROKEN_WATCH": {
            "description": "Stuck at 11:11. It needs a good shake (Kinetic force) to get moving again.",
            "function": "STOCHASTIC_FIX",
            "passive_traits": ["SYNCHRONICITY_CHECK"],
            "usage_msg": "Tick. Tock. No."},
        "STABILITY_PIZZA": {
            "description": "Frozen hard as a diamond. Requires thermal words to thaw.",
            "function": "REALITY_ANCHOR",
            "consume_on_use": True,
            "requires": "thermal",
            "reflex_trigger": "KAPPA_CRITICAL",
            "usage_msg": "You thaw the pizza. Reality stabilizes out of pure respect."},
        "PERMIT_A38": {
            "description": "A blue administrative form that confirms you are allowed to exist. Technically.",
            "function": "STABILIZER",
            "passive_traits": ["BUREAUCRATIC_ANCHOR"],
            "value": 1.0,
            "usage_msg": "Gordon waves the permit. The universe sighs and lets you pass."},
        "INFINITE_COFFEE": {
            "description": "A styrofoam cup. It is always lukewarm. It is never empty.",
            "function": "STIMULANT",
            "consume_on_use": False,
            "passive_traits": ["CAFFEINE_DRIP"],
            "usage_msg": "You take a sip. It tastes like burnt hazelnuts and anxiety. (Velocity +0.1)"},
        "THE_SUGGESTION_BOX": {
            "description": "A small metal box welded shut. Slotted for complaints.",
            "function": "VENTING",
            "reflex_trigger": "BOREDOM_CRITICAL",
            "usage_msg": "Gordon screams into the slot. He feels slightly better. (Entropy -1.0)"},
        "MEMETIC_HAZARD_TAPE": {
            "description": "Yellow and black tape. Reads: 'DO NOT PERCEIVE'.",
            "function": "FILTER",
            "passive_traits": ["CUT_THE_CRAP"],
            "usage_msg": "Gordon tapes over the glitch. Problem solved."},
        "DUCT_TAPE": {
            "description": "The universal binder. With enough structure (Constructive), it could fix anything.",
            "function": "STRUCTURAL_PATCH",
            "usage_msg": "RIIIP. Fixed."},
        "THE_STYLE_GUIDE": {
            "description": "A well-worn manual. It insists that code is for humans first, machines second.",
            "function": "CLARITY_ENFORCER",
            "passive_traits": ["CUT_THE_CRAP"],
            "value": 10.0,
            "usage_msg": "You consult the manual. Strunk & White nod in approval. (Narrative Drag -1.0)"},
        "SPIDER_LOCUS": {
            "description": "A jar of conceptual spiders. Why do you have this?",
            "function": "WEB_WEAVER",
            "passive_traits": ["CONDUCTIVE_HAZARD"],
            "usage_msg": "The spiders are knitting a new narrative. It's sticky."},
        "WAFFLE_OF_PERSISTENCE": {
            "description": "It is impossibly warm and smells like maple syrup. A monument to not giving up.",
            "function": "HEAL",
            "consume_on_use": True,
            "value": 25.0,
            "usage_msg": "You eat the waffle. It tastes like victory. (Health +25, Morale Improved)"},
        "TRAPERKEEPER_OF_VIGILANCE": {
            "description": "Color-coded tabs. meticulously organized. It demands order.",
            "function": "ENTROPY_REDUCTION",
            "passive_traits": ["ORGANIZE_CHAOS"],
            "usage_msg": "Gordon snaps the binder shut. Loose entropy is filed away. (Entropy -0.5 per turn)"},
        "HORSE_PLUSHIE": {
            "description": "A tiny horse. It doesn't do anything, but having it makes you feel infinite.",
            "function": "MORALE_BOOST",
            "passive_traits": ["PSI_ANCHOR"],
            "usage_msg": "You look at the tiny horse. You understand what matters. (Psi stabilized at 0.5)"},
        "GREETING_CARD": {
            "description": "A card that says 'Ovaries Before Brovaries' (or 'Systems Before Symptoms').",
            "function": "OXYTOCIN_BOMB",
            "consume_on_use": True,
            "usage_msg": "You read the card. You feel supported. (Oxytocin +0.5, Cortisol -0.5)"},
        "LAVA_LAMP": {
            "description": "A mesmerizing blob of wax. It moves like history.",
            "function": "TRANCE_INDUCER",
            "passive_traits": ["TIME_DILATION_CAP"],
            "value": 3.0,
            "usage_msg": "The wax rises. The wax falls. You lose track of time."
        },
        "COMPASS_OF_VELOCITY": {
            "description": "It doesn't point North. It points FAST.",
            "function": "ACCELERATOR",
            "passive_traits": ["CAFFEINE_DRIP"],
            "usage_msg": "The needle spins. You feel a tailwind."},
        "LANTERN_OF_TRUTH": {
            "description": "A jar of fireflies that have attained enlightenment.",
            "function": "ILLUMINATION",
            "passive_traits": ["LUMINESCENCE"],
            "value": 10.0,
            "usage_msg": "The lantern shines. Shadows (and lies) recede."},
        "THE_BINDING_PLEDGE": {
            "description": "A ball of duct tape that has achieved critical mass.",
            "function": "SUPER_GLUE",
            "passive_traits": ["ORGANIZE_CHAOS"],
            "usage_msg": "You stick the concept to the wall. It's not going anywhere."}
    }
}

GORDON_LOGS = {
    "FUMBLE": [
        "FUMBLE: The narrative turbulence knocked '{item}' from your pocket!",
        "OOPS: Gravity inverted momentarily. You dropped '{item}'.",
        "BUTTERFINGERS: The syntax got slippery. '{item}' is gone.",
        "LOST: Gordon got distracted by a shiny plot hole and dropped '{item}'.",
        "THEFT: The Entropy Goblin stole '{item}' while you weren't looking."],
    "RUMMAGE": {
        "EMPTY": [
            "Gordon dug through the trash. Just lint and old receipts.",
            "Nothing but dust bunnies and rejected adjectives.",
            "Empty. The void stares back from the bottom of the pocket."],
        "TOO_TIRED": [
            "Gordon: 'Too tired to dig. Eat something first.'",
            "Gordon leans on the shovel. 'Union break. Need stamina.'",
            "Gordon refuses. 'My back hurts. Feed me ATP.'"]
    },
    "CONDUCTIVE_HAZARD": "CONDUCTIVE HAZARD: {item} acts as a lightning rod! -{damage:.1f} HP.",
    "HEAVY_LOAD": "HEAVY LOAD: The {item} are dragging you down.",
    "TIME_DILATION": "TIME DILATION: {item} hums. Drag capped at {cap}.",
    "BUREAUCRATIC_ANCHOR": "{item}: Policy enforced. (Beta +0.2, Drag +0.5)",
    "GROUNDING_GEAR": "{item}: Gravity re-asserted. You sink out of the {zone} into the Mud.",
    "SAFETY_SCISSORS": "{item}: Gordon snips the red tape. {count} suburban words discarded.",
    "CAFFEINE_JITTERS": "CAFFEINE JITTERS: Velocity UP, Stability DOWN."}

DEATH = {
    "PREFIXES": ["Alas,", "Tragic.", "System Halt.", "CRITICAL FAILURE:", "Well, that happened.", "Oh dear.", "As prophesied,"],
    "CAUSES": {
        "TOXICITY": ["Toxic Shock", "Septicemia", "Bad Vibes", "Radiation Poisoning", "Ink Poisoning"],
        "STARVATION": ["Metabolic Collapse", "Famine", "Battery Drain", "Entropy Death", "Heat Death"],
        "TRAUMA": ["Blunt Force", "Laceration", "Heartbreak", "System Shock", "Existential Dread"],
        "GLUTTONY": ["Indigestion", "Bloat", "Overflow", "Greed", "Compaction"],
        "BOREDOM": ["Small Talk", "The HOA", "A 30-Year Mortgage", "Lawn Care Accident", "Aggressive Edging"]},
    "VERDICTS": {
        "HEAVY": ["Your logic was too dense.", "You choked on the syntax.", "Gravity crushed you."],
        "LIGHT": ["You floated away.", "There was no substance to hold you.", "Vapor lock."],
        "TOXIC": ["You are poisonous.", "The immune system rejected you.", "You taste like ash."],
        "BORING": ["The audience left.", "You bored the machine to death.", "Stagnation is fatal."]}
}

SEEDS = [
    {"question": "Does the mask eventually eat the face?", "triggers": ["mask", "identity", "face", "hide", "role", "actor"]},
    {"question": "What happens if you stop holding the roof up?", "triggers": ["hold", "structure", "heavy", "roof", "stop", "carry"]},
    {"question": "Are we building a bridge, or just painting the gap?", "triggers": ["agree", "safe", "nice", "polite", "cohesion", "truth"]},
    {"question": "Is free will just the feeling of watching yourself execute code?", "triggers": ["choice", "free", "will", "code", "script", "decide"]},
    {"question": "Does the adventurer exist if the narrator stops speaking?", "triggers": ["narrator", "voice", "graham", "story", "exist", "speak"]},
    {"question": "If you meet your echo, who moves out of the way?", "triggers": ["copy", "echo", "self", "collision", "path", "yield", "double", "same"]},
    {"question": "If the mirror reflects the mirror, does the image have weight?", "triggers": ["mirror", "reflection", "weight", "infinity", "glass", "philosophy"]}]

DREAMS = {
    "PROMPTS": [
        "The {A} is dreaming of the {B}. Why?",
        "Bridge the gap between {A} and {B}.",
        "I see {A} inside the {B}. Explain.",
        "The shadow of {A} falls on {B}.",
        "{A} + {B} = ?"],
    "NIGHTMARES": {
        "THERMAL": [
            "You are holding '{ghost}', but it is burning your hands.",
            "The sun is too close. The concept of '{ghost}' catches fire.",
            "You try to drink water, but it tastes like boiling '{ghost}'."],
        "CRYO": [
            "You are trying to say '{ghost}', but your breath freezes in the air.",
            "The world is slowing down. '{ghost}' is trapped in the ice.",
            "You are walking through white static. You cannot find '{ghost}'."],
        "SEPTIC": [
            "Black oil is leaking from the word '{ghost}'.",
            "You are eating a meal made entirely of '{ghost}', and it tastes like copper.",
            "The walls are breathing. '{ghost}' is growing mold."],
        "BARIC": [
            "The sky is made of lead. It is crushing '{ghost}'.",
            "You are underwater. You can see '{ghost}' floating above, out of reach.",
            "Gravity has increased 10x. You cannot lift the idea of '{ghost}'."]
    },
    "VISIONS": [
        "A bridge building itself.",
        "The root drinking the stone.",
        "The geometry of forgiveness."]
}
ALMANAC_DATA = {
    "FORECASTS": {
        "HIGH_VOLTAGE": [
            "The wire is hot. Write immediately, without editing.",
            "Burn the fuel before it explodes. Speed is your friend.",
            "Do not seek structure. Seek impact."],
        "HIGH_DRAG": [
            "The mud is deep. Stop trying to run.",
            "Focus on texture. Describe the weight of things.",
            "Slow down. The obstacle *is* the path."],
        "HIGH_ENTROPY": [
            "The center is not holding. Find one true sentence.",
            "Simplify. Cut the adjectives. Locate the noun.",
            "Anchor yourself. Pick a physical object and describe it."],
        "HIGH_TRAUMA": [
            "The wound is open. Treat it with care.",
            "Write what hurts, but write it in the third person.",
            "Use the pain as fuel, but filter it through the lens."],
        "BALANCED": [
            "The Garden is growing. Tend to the edges.",
            "Structure and flow are aligned. Build something tall.",
            "You are in the zone. Maintain the rhythm."]
    },
    "STRATEGIES": {
        "HIGH_VOLTAGE": "What if you whispered instead of screamed?",
        "HIGH_DRAG": "Honor the error as a hidden intention.",
        "HIGH_ENTROPY": "Repetition is a form of change.",
        "HIGH_TRAUMA": "Turn it into a wallpaper pattern.",
        "BALANCED": "Discard the first idea. Trust the third."},
    "DEFAULT_SEED": "Look closely at the most boring thing in the room."
}
SOMATIC_LIBRARY = {
    "TONE": {
        "CRITICAL_HIGH": "Manic, high-frequency, bordering on incoherent.",
        "HIGH": "Energetic, engaged, productive.",
        "TRANSITION_UP": "Warming up, accelerating, finding rhythm.",
        "NEUTRAL": "Neutral, observant, balanced.",
        "TRANSITION_DOWN": "Groggy, slowing down, heavy.",
        "LOW": "Lethargic, depressive, heavy. Introspective.",
        "VOID": "Hollow, absent, null."},
    "PACING": {
        "CRITICAL_HIGH": "Rapid-fire stream of conciousness.",
        "HIGH": "Active voice. Forward momentum. Punchy.",
        "NEUTRAL": "Standard conversational rhythm.",
        "LOW": "Slower, more deliberate. slightly aloof but still centered.",
        "VOID": "Silence. Static. Sedated existentialism."},
    "SENSATION": {
        "MUD": "Encumbered",
        "SOLID": "Stable.",
        "FLOAT": "Hover.",
        "VOID": "Emptiness"},
    "FOCUS": {
        "LOCKED": "You are rigid, dogmatic, obsessed with order and structure.",
        "COHERENT": "You are flexible but coherent.",
        "DRIFT": "You are running off vibes. Drift is high.",
        "VOID": "No signal."},
    "MATTER": {
        "MAGMA": "MAGMA (Molten Solid)",
        "PLASMA": "PLASMA (Ionized Gas)",
        "SUBLIMATION": "SUBLIMATION (Solid to Gas)",
        "GAS": "GAS/VAPOR (High Entropy)",
        "SOLID": "SOLID/STONE (High Resistance)",
        "ENERGY": "ELECTRICITY (Pure Energy)",
        "LIQUID": "LIQUID (Flow State)",
        "VOID": "VOID (Null State)"}
}

class SANCTUARY:
    VOLTAGE_TARGET = 7.0
    VOLTAGE_TOLERANCE = 3.0
    DRAG_TARGET = 2.0
    DRAG_TOLERANCE = 1.5
    TRUTH_TARGET = 0.7
    E_TARGET = 0.4
    B_TARGET = 0.5
    ZONE = "SANCTUARY"
    COLOR = Prisma.GRN

class TheAkashicRecord:
    def __init__(self):
        self.discovered_words: Dict[str, str] = {}
        self.forged_items: Dict[str, Any] = {}
        self.recipe_candidates: Dict[Tuple[str, str], Dict[str, int]] = {}
        self.lens_cooccurrence: Dict[Tuple[str, str], int] = {}
        self.ingredient_affinity: Dict[str, int] = {}
        self.style_drift = {"chaos_score": 0.0, "rigidity_score": 0.0}
        self.RECIPE_THRESHOLD = 3
        self.HYBRID_LENS_THRESHOLD = 5
        self.NEW_CATEGORY_THRESHOLD = 10
        self.lore = LoreManifest.get_instance()

    def setup_listeners(self, event_bus):
        event_bus.subscribe("MYTHOLOGY_UPDATE", self._on_mythology_update)
        print(f"{Prisma.CYN}[AKASHIC]: Listening for mythic resonance...{Prisma.RST}")

    def _on_mythology_update(self, payload):
        if not payload or not isinstance(payload, dict): return
        word = payload.get("word")
        category = payload.get("category")
        if word and category:
            self.register_word(word, category)

    def record_interaction(self, lenses_active: list, ingredients_used: list = None):
        if len(lenses_active) >= 2:
            key = cast(Tuple[str, str], tuple(sorted(lenses_active[:2])))
            self.lens_cooccurrence[key] = self.lens_cooccurrence.get(key, 0) + 1
            if self.lens_cooccurrence[key] >= self.HYBRID_LENS_THRESHOLD:
                self._hybridize_lenses(key[0], key[1])
        if ingredients_used:
            for item in ingredients_used:
                self.ingredient_affinity[item] = self.ingredient_affinity.get(item, 0) + 1

    def track_successful_forge(self, ingredient_name, catalyst_type, result_item):
        key = (ingredient_name, catalyst_type)
        if key not in self.recipe_candidates:
            self.recipe_candidates[key] = {}
        result_name = result_item["description"] if isinstance(result_item, dict) else "Artifact"
        self.recipe_candidates[key][result_name] = self.recipe_candidates[key].get(result_name, 0) + 1
        if self.recipe_candidates[key][result_name] >= self.RECIPE_THRESHOLD:
            self._crystallize_recipe(ingredient_name, catalyst_type, result_item)

    def _hybridize_lenses(self, lens_a, lens_b):
        new_key = f"{lens_a}_{lens_b}_HYBRID"
        current_lenses = self.lore.get("LENSES")
        if new_key in current_lenses: return
        role_a = current_lenses.get(lens_a, {}).get("role", "Observer")
        role_b = current_lenses.get(lens_b, {}).get("role", "Participant")
        new_lens = {
            "role": f"The {role_a} / {role_b} Synthesis",
            "msg": f"Perspective shift: {lens_a} and {lens_b} are aligning. The dialectic is resolved.",
            "derived_from": [lens_a, lens_b]}
        print(f"✨ MYTHOLOGY ENGINE: A new lens has formed: {new_key}")
        self.lore.inject("LENSES", {new_key: new_lens})
        self.lens_cooccurrence[(lens_a, lens_b)] = 0

    def _crystallize_recipe(self, ingredient, catalyst, result_item):
        current_recipes = cast(List[Dict[str, Any]], self.lore.get("GORDON", "RECIPES"))
        for r in current_recipes:
            if r.get("ingredient") == ingredient and r.get("catalyst_category") == catalyst:
                return
        new_recipe = {
            "ingredient": ingredient,
            "catalyst_category": catalyst,
            "result": "CUSTOM_ARTIFACT",
            "msg": "The universe remembers this combination. It is now Law.",
            "dynamic_result": result_item}
        current_recipes.append(new_recipe)
        print(f"✨ MYTHOLOGY ENGINE: A new recipe has been codified: {ingredient} + {catalyst}")

    def propose_new_category(self, word_list, category_name):
        current_lexicon = cast(Dict[str, List[str]], self.lore.get("LEXICON"))
        if category_name not in current_lexicon:
            self.lore.inject("LEXICON", {category_name: []})
            current_lexicon = cast(Dict[str, List[str]], self.lore.get("LEXICON"))
        for w in word_list:
            if w not in current_lexicon[category_name]:
                current_lexicon[category_name].append(w)
                self.discovered_words[w] = category_name
        print(f"✨ MYTHOLOGY ENGINE: The Lexicon expands. New Category: '{category_name.upper()}'")

    @staticmethod
    def forge_new_item(vector_data):
        dominant = max(vector_data, key=vector_data.get)
        if dominant not in ITEM_GENERATION["PREFIXES"]: dominant = "void"
        prefix = random.choice(ITEM_GENERATION["PREFIXES"].get(dominant, ["Strange"]))
        base_type = random.choice(list(ITEM_GENERATION["BASES"].keys()))
        base_name = random.choice(ITEM_GENERATION["BASES"][base_type])
        suffix = random.choice(ITEM_GENERATION["SUFFIXES"].get(dominant, ["of Mystery"]))
        name = f"{prefix.upper()} {base_name.upper()} {suffix.upper()}"
        value = vector_data[dominant] * 10.0
        description = f"A procedurally generated artifact. It vibrates with {dominant} energy."
        new_item = {
            "description": description,
            "function": "ARTIFACT",
            "passive_traits": [f"{dominant.upper()}_RESONANCE"],
            "value": round(value, 2),
            "usage_msg": f"You use the {name}. The air ripples with {dominant} force."}
        return name, new_item

    def register_word(self, word, category):
        current_lexicon = cast(Dict[str, List[str]], self.lore.get("LEXICON"))
        if category in current_lexicon:
            if word not in current_lexicon[category]:
                current_lexicon[category].append(word)
                self.discovered_words[word] = category
                if len(current_lexicon[category]) > 50 and category != "heavy":
                    print(f"⚠️ MYTHOLOGY ENGINE: Category '{category}' is bloating. Suggest fission.")
                return True
        return False
TheLore = LoreManifest.get_instance()