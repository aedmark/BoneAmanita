""" bone_config.py - The System Tunables """
from typing import Dict, Any, List, Tuple

class BonePresets:
    ZEN_GARDEN = {
        "PHYSICS.VOLTAGE_FLOOR": 1.0,
        "PHYSICS.VOLTAGE_MAX": 10.0,
        "PHYSICS.DRAG_FLOOR": 2.0,
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


class BoneConfig:
    GRAVITY_WELL_THRESHOLD = 15.0
    SHAPLEY_MASS_THRESHOLD = 5.0
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

    class WHIMSY:
        ABSURDITY_CONSTANT = 42
        MAX_SARCASM_LEVEL = 11
        LUDICROUS_SPEED = True
        DEPARTMENT_NAME = "The Ministry of Silly Hats & Semantic Vectors"

    class METABOLISM:
        BASE_RATE = 2.0
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
        MAX_SLOTS = 8
        RUMMAGE_COST = 15.0

    class COUNCIL:
        STRANGE_LOOP_VOLTAGE = 8.0
        OSCILLATION_DELTA = 5.0
        MANIC_VOLTAGE_TRIGGER = 18.0
        MANIC_DRAG_FLOOR = 1.0
        MANIC_TURN_LIMIT = 2
        FOOTNOTE_CHANCE = 0.15

    class BIO:
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
        if cls.VERBOSE_LOGGING:
            print(f"[CONFIG]: Paradigm Shift Complete. {len(logs)} parameters tuned.")
        return logs

    @classmethod
    def check_pareidolia(cls, words):
        triggers = {"face", "ghost", "jesus", "cloud", "voice", "eyes"}
        hits = [w for w in words if w in triggers]
        if hits:
            return True, f"PAREIDOLIA: You see a {hits[0].upper()} in the noise. It blinks."
        return False, None

    @classmethod
    def reconcile_state(cls, physics_packet: Any):
        if physics_packet.voltage > cls.PHYSICS.VOLTAGE_MAX:
            physics_packet.voltage = cls.PHYSICS.VOLTAGE_MAX
        if physics_packet.voltage < cls.PHYSICS.VOLTAGE_FLOOR:
            physics_packet.voltage = cls.PHYSICS.VOLTAGE_FLOOR
        if physics_packet.narrative_drag < cls.PHYSICS.DRAG_FLOOR:
            physics_packet.narrative_drag = cls.PHYSICS.DRAG_FLOOR
        if physics_packet.narrative_drag > cls.PHYSICS.DRAG_HALT:
            physics_packet.narrative_drag = cls.PHYSICS.DRAG_HALT
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