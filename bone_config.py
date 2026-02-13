""" bone_config.py - The System Tunables """

from typing import Dict, Any, List

class BonePresets:
    ZEN_GARDEN = {
        "PHYSICS.VOLTAGE_FLOOR": 1.0,
        "PHYSICS.VOLTAGE_MAX": 25.0,
        "PHYSICS.DRAG_FLOOR": 0.5,
        "BIO.DECAY_RATE": 0.001,
        "BIO.STAMINA_EXHAUSTED": 5.0,
        "COUNCIL.MANIC_VOLTAGE_TRIGGER": 99.0}
    THUNDERDOME = {
        "PHYSICS.VOLTAGE_FLOOR": 8.0,
        "PHYSICS.VOLTAGE_MAX": 30.0,
        "PHYSICS.DRAG_FLOOR": 0.5,
        "BIO.ATP_STARVATION": 20.0,
        "COUNCIL.MANIC_VOLTAGE_TRIGGER": 12.0,
        "CHANCE.RARE": 0.20}
    SANCTUARY = {
        "VOLTAGE_TARGET": 7.0,
        "VOLTAGE_TOLERANCE": 3.0,
        "DRAG_TARGET": 2.0,
        "DRAG_TOLERANCE": 1.5,
        "TRUTH_TARGET": 0.7,
        "E_TARGET": 0.4,
        "B_TARGET": 0.5,
        "ZONE": "SANCTUARY",
        "COLOR": "GRN"}
    LABORATORY = {
        "PHYSICS.VOLTAGE_FLOOR": 0.5,
        "PHYSICS.VOLTAGE_MAX": 15.0,
        "PHYSICS.DRAG_FLOOR": 2.0,
        "BIO.DECAY_RATE": 0.0,
        "COUNCIL.FOOTNOTE_CHANCE": 1.0}
    MODES = {
        "ADVENTURE": {
            "description": "The classic survival narrative. High immersion.",
            "tuning": "THUNDERDOME",
            "ui_layer": 1,
            "village_suppression": []
        },
        "CONVERSATION": {
            "description": "Low-friction dialogue. Connection over mechanics.",
            "tuning": "SANCTUARY",
            "ui_layer": 1,
            "village_suppression": ["GORDON", "DEATH_GEN", "BUREAU"]
        },
        "CREATIVE": {
            "description": "High-voltage brainstorming. Logic constraints loosened.",
            "tuning": "ZEN_GARDEN",
            "ui_layer": 0,
            "village_suppression": ["BUREAU", "CRITICS"]
        },
        "TECHNICAL": {
            "description": "System internals and raw debugging.",
            "tuning": "LABORATORY",
            "ui_layer": 3,
            "village_suppression": ["FOLLY", "DREAMER", "ZEN"]
        }
    }

class BoneConfig:
    GRAVITY_WELL_THRESHOLD = 15.0
    SHAPLEY_MASS_THRESHOLD = 5.0
    TRAIT_ARCHETYPES = {
        "THE POET": {
            "ABSTRACT": 0.6,
            "PHOTO": 0.3,
            "ENTROPY": 0.1
        },
        "THE ENGINEER": {
            "CONSTRUCTIVE": 0.7,
            "HEAVY": 0.3
        },
        "THE NIHILIST": {
            "ENTROPY": 0.8,
            "CRYO": 0.2
        },
        "THE CRITIC": {
            "THERMAL": 0.5,
            "ABSTRACT": 0.5
        },
        "THE EXPLORER": {
            "KINETIC": 0.6,
            "AEROBIC": 0.4
        },
        "THE OBSERVER": {
            "VOID": 0.5,
            "ABSTRACT": 0.2
        }
    }
    TRAUMA_VECTOR = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
    MAX_HEALTH = 100.0
    MAX_STAMINA = 100.0
    MAX_ATP = 200.0
    STAMINA_REGEN = 1.0
    MAX_DRAG_LIMIT = 5.0
    GEODESIC_STRENGTH = 10.0
    BASE_IGNITION_THRESHOLD = 0.5
    MAX_REPETITION_LIMIT = 0.8
    BOREDOM_THRESHOLD = 10.0
    ANVIL_TRIGGER_VOLTAGE = 10.0
    MIN_DENSITY_THRESHOLD = 0.3
    LAGRANGE_TOLERANCE = 2.0
    FLASHPOINT_THRESHOLD = 10.0
    SIGNAL_DRAG_MULTIPLIER = 1.0
    KINETIC_GAIN = 1.0
    CRITICAL_ROS_LIMIT = 100.0
    MAX_MEMORY_CAPACITY = 100
    ZONE_THRESHOLDS = {"LABORATORY": 1.5, "COURTYARD": 0.8}
    TOXIN_WEIGHT = 1.0
    ANTIGENS = ["basically", "actually", "literally", "utilize"]
    MAX_OUTPUT_TOKENS = 4096
    DEFAULT_LLM_ENDPOINTS = {
        "ollama": "http://127.0.0.1:11434/v1/chat/completions",
        "openai": "https://api.openai.com/v1/chat/completions",
        "lm_studio": "http://127.0.0.1:1234/v1/chat/completions",
        "localai": "http://127.0.0.1:8080/v1/chat/completions"}
    VERBOSE_LOGGING = True
    PROVIDER = "openai"
    BASE_URL = None
    API_KEY = None
    MODEL = "gpt-4"
    OLLAMA_MODEL_ID = "llama3"

    class SOUL:
        MEMORY_VOLTAGE_MIN = 14.0
        MEMORY_TRUTH_MIN = 0.8
        MANIC_TRIGGER = 18.0
        MAX_CORE_MEMORIES = 7
        ENTROPY_DRAG_TRIGGER = 4.0
        TRAIT_MOMENTUM = 0.05
        PARADOX_CRITICAL_MASS = 10.0
        OBSESSION_NEGLECT_WARN = 5.0
        OBSESSION_NEGLECT_FAIL = 10.0
        OBSESSION_GRAVITY_ASSIST = 20.0
        ARCHETYPE_BURNOUT_RATE = 0.02
        TRAIT_DECAY_NORMAL = 0.002
        TRAIT_DECAY_FAST = 0.005

    class ANCHOR:
        DIGNITY_MAX = 100.0
        DIGNITY_REGEN = 5.0
        DIGNITY_DECAY = 0.5
        DIGNITY_CRITICAL = 20.0
        DIGNITY_LOCKDOWN = 10.0
        PET_WARNING_THRESHOLD = 0.8
        DOMESTICATION_PENALTY = 5.0

    class CORTEX:
        BASE_SENSITIVITY = 0.1
        LATENCY_PENALTY_THRESHOLD = 2.0
        DRAG_STRESS_THRESHOLD = 8.0
        TOXIN_SCALAR = 0.4
        ADRENALINE_KINETIC_SCALAR = 0.08
        VOLTAGE_ARC_TRIGGER = 15.0
        DOPAMINE_PLAY_BOOST = 0.1

    class WHIMSY:
        ABSURDITY_CONSTANT = 42
        MAX_SARCASM_LEVEL = 11
        LUDICROUS_SPEED = True
        DEPARTMENT_NAME = "The Ministry of Silly Hats & Semantic Vectors"

    class METABOLISM:
        BASE_RATE = 2.0
        GENESIS_VOLTAGE = 100.0
        BASE_METABOLIC_RATE = 1.0
        DRAG_TAX_LOW = 0.10
        DRAG_TAX_HIGH = 0.25
        DRAG_GRACE_BUFFER = 2.0
        ROS_GENERATION_FACTOR = 0.04
        PHOTOSYNTHESIS_GAIN = 5.0
        TURBULENCE_TAX = 4.0
        BUREAU_ENTROPY_SCALAR = 20.0

    class PHYSICS:
        VOLTAGE_FLOOR = 2.0
        VOLTAGE_LOW = 5.0
        VOLTAGE_MED = 8.0
        VOLTAGE_HIGH = 12.0
        VOLTAGE_CRITICAL = 15.0
        VOLTAGE_MAX = 20.0
        DRAG_FLOOR = 1.0
        DRAG_IDEAL_MAX = 3.0
        DRAG_HEAVY = 5.0
        DRAG_CRITICAL = 8.0
        DRAG_HALT = 10.0
        WEIGHT_HEAVY = 2.0
        WEIGHT_KINETIC = 1.5
        WEIGHT_EXPLOSIVE = 3.0
        WEIGHT_CONSTRUCTIVE = 1.5

    class INVENTORY:
        CONDUCTIVE_THRESHOLD = 12.0
        HEAVY_LOAD_THRESHOLD = 8.0
        TURBULENCE_FUMBLE_CHANCE = 0.15
        TURBULENCE_THRESHOLD = 0.6
        MAX_SLOTS = 10
        ENTROPY_COST = 5.0
        RUMMAGE_COST = 15.0

    class COUNCIL:
        STRANGE_LOOP_VOLTAGE = 8.0
        OSCILLATION_DELTA = 5.0
        MANIC_VOLTAGE_TRIGGER = 18.0
        MANIC_DRAG_FLOOR = 1.0
        MANIC_TURN_LIMIT = 2
        FOOTNOTE_CHANCE = 0.15

    class BIO:
        STARTING_ATP = 60.0
        ATP_STARVATION = 5.0
        ROS_CRITICAL = 150.0
        STAMINA_EXHAUSTED = 20.0
        REWARD_SMALL = 0.05
        REWARD_MEDIUM = 0.10
        REWARD_LARGE = 0.15
        DECAY_RATE = 0.01
        CORTEX_SENSITIVITY = 0.1

    class CHANCE:
        RARE = 0.05
        UNCOMMON = 0.10
        COMMON = 0.20
        FREQUENT = 0.30

    class ZEN:
        VOLTAGE_MIN = 2.0
        VOLTAGE_MAX = 12.0
        DRAG_MAX = 4.0
        EFFICIENCY_CAP = 0.5
        EFFICIENCY_SCALAR = 0.05
        STREAK_BREAK_THRESHOLD = 5

    class BUREAU:
        MIN_HEALTH_TO_AUDIT = 20.0
        MIN_WORD_COUNT = 4
        HIGH_VOLTAGE_TRIGGER = 18.0
        LOW_TRUTH_TRIGGER = 0.8
        TAX_STANDARD = 5.0
        TAX_HEAVY = 15.0

    class THERAPY:
        HEALING_THRESHOLD = 5
        STRENGTH_REQ = 0.3
        TRAUMA_REDUCTION = 0.5

    class KINTSUGI:
        STAMINA_TRIGGER = 15.0
        ALCHEMY_VOLTAGE = 15.0
        ALCHEMY_WHIMSY = 0.4
        INTEGRATION_VOLTAGE = 8.0
        INTEGRATION_WHIMSY = 0.2
        REDUCTION_SCAR = 0.5
        REDUCTION_INTEGRATION = 2.0
        REDUCTION_ALCHEMY_FACTOR = 0.8
        ALCHEMY_ATP_FACTOR = 15.0

    class LIMBO:
        MAX_ECTOPLASM = 50
        HAUNT_CHANCE = 0.05
        STASIS_LEAK_RATE = 1.0

    class FOLLY:
        MAUSOLEUM_VOLTAGE = 8.5
        MAUSOLEUM_STAMINA = 45.0
        FEEDING_CAP = 20.0
        BASE_YIELD = 30.0
        DECAY_EXPONENT = 0.7
        PIZZA_THRESHOLD = 25.0
        SUGAR_RUSH_YIELD = 5.0
        YIELD_ABSTRACT = 8.0
        PENALTY_REGURGITATION = 5.0
        PENALTY_INDIGESTION = 2.0

    @classmethod
    def load_preset(cls, preset_dict: Dict[str, Any]) -> List[str]:
        logs = []
        for key, value in preset_dict.items():
            if "." not in key:
                logs.append(f"⚠️ SKIPPED: Invalid key format '{key}'")
                continue
            sector_name, param_name = key.split(".", 1)
            result = cls.tune(sector_name, param_name, value)
            logs.append(result)
        sanity_check = cls.validate_integrity()
        if sanity_check:
            logs.extend(sanity_check)
        if cls.VERBOSE_LOGGING:
            print(f"[CONFIG]: Paradigm Shift Complete. {len(logs)} parameters tuned.")
        return logs

    @classmethod
    def validate_integrity(cls) -> List[str]:
        errors = []
        if cls.PHYSICS.VOLTAGE_FLOOR > cls.PHYSICS.VOLTAGE_MAX:
            cls.PHYSICS.VOLTAGE_FLOOR = cls.PHYSICS.VOLTAGE_MAX - 1.0
            errors.append("⚠️ PHYSICS REPAIR: Floor > Max. Clamped Floor.")
        if cls.PHYSICS.DRAG_FLOOR > cls.PHYSICS.DRAG_HALT:
            cls.PHYSICS.DRAG_FLOOR = cls.PHYSICS.DRAG_HALT - 1.0
            errors.append("⚠️ PHYSICS REPAIR: Drag Floor > Halt. Clamped Floor.")
        return errors

    @classmethod
    def check_pareidolia(cls, words):
        triggers = {"face", "ghost", "jesus", "cloud", "voice", "eyes"}
        word_set = set(words) if not isinstance(words, set) else words
        hits = list(triggers.intersection(word_set))
        if hits:
            hit_word = hits[0]
            return True, f"PAREIDOLIA: You see a {hit_word.upper()} in the noise. It blinks."
        return False, None

    @classmethod
    def reconcile_state(cls, physics_packet: Any):
        is_dict = isinstance(physics_packet, dict)
        def get_val(key, default):
            if is_dict: return physics_packet.get(key, default)
            return getattr(physics_packet, key, default)
        def set_val(key, value):
            if is_dict:
                physics_packet[key] = value
            else:
                setattr(physics_packet, key, value)
        current_v = get_val("voltage", 5.0)
        current_d = get_val("narrative_drag", 1.0)
        new_v = max(cls.PHYSICS.VOLTAGE_FLOOR, min(current_v, cls.PHYSICS.VOLTAGE_MAX))
        new_d = max(cls.PHYSICS.DRAG_FLOOR, min(current_d, cls.PHYSICS.DRAG_HALT))
        set_val("voltage", new_v)
        set_val("narrative_drag", new_d)
        return physics_packet

    @classmethod
    def tune(cls, sector: str, parameter: str, value: Any) -> str:
        if not hasattr(cls, sector):
            return f"❌ SECTOR ERROR: '{sector}' does not exist."
        target_sector = getattr(cls, sector)
        if not hasattr(target_sector, parameter):
            return f"❌ PARAM ERROR: '{parameter}' not found in {sector}."
        current_val = getattr(target_sector, parameter)
        if type(current_val) != type(value) and not (isinstance(current_val, float) and isinstance(value, int)):
            return f"⚠️ TYPE MISMATCH: Cannot replace {type(current_val)} with {type(value)}."
        setattr(target_sector, parameter, value)
        return f"✅ TUNED: {sector}.{parameter} -> {value}"