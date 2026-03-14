"""
bone_presets.py
"""

from typing import Dict, Any, List

def ux(section: str, key: str, default: Any = "") -> Any:
    from bone_core import LoreManifest
    return LoreManifest.get_instance().get_ux(section, key, default)

class BonePresets:
    ZEN_GARDEN = {"PHYSICS.VOLTAGE_FLOOR": 1.0, "PHYSICS.VOLTAGE_MAX": 25.0, "PHYSICS.DRAG_FLOOR": 0.5,
                  "BIO.DECAY_RATE": 0.001, "BIO.STAMINA_EXHAUSTED": 5.0, "COUNCIL.MANIC_VOLTAGE_TRIGGER": 99.0,
                  "tuning": "ZEN", }
    THUNDERDOME = {"PHYSICS.VOLTAGE_FLOOR": 8.0, "PHYSICS.VOLTAGE_MAX": 30.0, "PHYSICS.DRAG_FLOOR": 0.5,
                   "BIO.ATP_STARVATION": 20.0, "COUNCIL.MANIC_VOLTAGE_TRIGGER": 12.0, "CHANCE.RARE": 0.20, }
    SANCTUARY = {"COUNCIL.LEVERAGE_TARGET_VOLTAGE": 7.0, "COUNCIL.LEVERAGE_TARGET_DRAG": 2.0,
                 "PHYSICS.VOLTAGE_MAX": 15.0, "PHYSICS.DRAG_FLOOR": 0.0, "BIO.METABOLISM_RATE": 0.5, "tuning": "ZEN",
                 "VOLTAGE_TARGET": 7.0, "VOLTAGE_TOLERANCE": 3.0, "DRAG_TARGET": 2.0, "DRAG_TOLERANCE": 1.5,
                 "TRUTH_TARGET": 0.7, "E_TARGET": 0.4, "B_TARGET": 0.5, "ZONE": "SANCTUARY", "COLOR": "\033[32m",
                 "COLOR_NAME": "GRN", }
    LABORATORY = {"PHYSICS.VOLTAGE_FLOOR": 0.5, "PHYSICS.VOLTAGE_MAX": 15.0, "PHYSICS.DRAG_FLOOR": 2.0,
                  "BIO.DECAY_RATE": 0.0, "COUNCIL.FOOTNOTE_CHANCE": 1.0, }
    MODES = {
        "ADVENTURE": {"description": "The default experience. Survival, inventory, exploration.", "tuning": "STANDARD",
                      "ui_layer": 1, "village_suppression": [], "prompt_key": "ADVENTURE", "show_inventory": True,
                      "show_location": True, "show_vitals": True, "allow_loot": True, "allow_metrics": False,
                      "atp_drain_enabled": True, "chaos_tax_enabled": True, "voltage_floor_override": None,
                      "active_mods": [], "default_ui_depth": "CORE", },
        "CONVERSATION": {"description": "Pure dialogue. No entropy, no items, just connection.", "tuning": "ZEN",
                         "ui_layer": 1, "village_suppression": ["GORDON", "NAVIGATOR", "CARTOGRAPHER", "TINKERER",
                                                                "DEATH", "BUREAU", ], "prompt_key": "CONVERSATION",
                         "show_inventory": False, "show_location": False, "show_vitals": False,
                         "allow_loot": False, "allow_metrics": False, "atp_drain_enabled": False,
                         "chaos_tax_enabled": False, "voltage_floor_override": None, "active_mods": [],
                         "default_ui_depth": "LITE", },
        "CREATIVE": {"description": "High voltage, low drag. Hallucination enabled.", "tuning": "MANIC", "ui_layer": 1,
                     "village_suppression": ["GORDON", "BENEDICT", "BUREAU", "NAVIGATOR"],
                     "prompt_key": "CREATIVE",
                     "show_inventory": False, "show_location": False,
                     "show_vitals": False, "allow_loot": False,
                     "allow_metrics": False, "atp_drain_enabled": True, "chaos_tax_enabled": False,
                     "voltage_floor_override": 70.0, "active_mods": ["LIMINAL"], "default_ui_depth": "CORE", },
        "TECHNICAL": {"description": "Raw data stream. Debugging and code generation.", "tuning": "DEBUG",
                      "ui_layer": 2, "village_suppression": ["MOIRA", "JESTER", "CASSANDRA", "APRIL"],
                      "prompt_key": "TECHNICAL", "show_inventory": False,
                      "show_location": False, "show_vitals": True,
                      "allow_loot": False, "allow_metrics": True, "atp_drain_enabled": True, "chaos_tax_enabled": True,
                      "voltage_floor_override": None, "active_mods": ["CODING", "SYNTAX"],
                      "default_ui_depth": "DEEP", }}
    STANDARD = {"PHYSICS": {"VOLTAGE_MAX": 20.0, "BASE_DRAG": 1.0}, "BIO": {"METABOLISM_RATE": 1.0}, }
    ZEN = {"PHYSICS": {"VOLTAGE_MAX": 10.0, "BASE_DRAG": 0.0}, "BIO": {"METABOLISM_RATE": 0.1}, }
    MANIC = {"PHYSICS": {"VOLTAGE_MAX": 50.0, "BASE_DRAG": 0.5}, "BIO": {"METABOLISM_RATE": 2.0}, }
    DEBUG = {"PHYSICS": {"VOLTAGE_MAX": 100.0, "BASE_DRAG": 0.0}, "BIO": {"METABOLISM_RATE": 0.0}, }

class BoneConfig:
    GRAVITY_WELL_THRESHOLD = 15.0
    SHAPLEY_MASS_THRESHOLD = 5.0
    TRAIT_ARCHETYPES = {"THE POET": {"ABSTRACT": 0.6, "PHOTO": 0.3, "ENTROPY": 0.1},
                        "THE ENGINEER": {"CONSTRUCTIVE": 0.7, "HEAVY": 0.3},
                        "THE NIHILIST": {"ENTROPY": 0.8, "CRYO": 0.2}, "THE CRITIC": {"THERMAL": 0.5, "ABSTRACT": 0.5},
                        "THE EXPLORER": {"KINETIC": 0.6, "AEROBIC": 0.4},
                        "THE OBSERVER": {"VOID": 0.5, "ABSTRACT": 0.2}, }
    TRAUMA_VECTOR = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
    VERSION = "17.3.0"
    VERBOSE_LOGGING = True
    MAX_HEALTH = 100.0
    MAX_STAMINA = 100.0
    MAX_ATP = 100.0
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
    PRIORITY_LEARNING_RATE = 1.0
    ZONE_THRESHOLDS = {"LABORATORY": 1.5, "COURTYARD": 0.8}
    TOXIN_WEIGHT = 1.0
    ANTIGENS = ["basically", "actually", "literally", "utilize"]
    MAX_OUTPUT_TOKENS = 4096
    DEFAULT_LLM_ENDPOINTS = {"ollama": "http://127.0.0.1:11434/v1/chat/completions",
                             "openai": "https://api.openai.com/v1/chat/completions",
                             "lm_studio": "http://127.0.0.1:1234/v1/chat/completions", "mock": "N/A", }
    PROVIDER = "ollama"
    BASE_URL = None
    API_KEY = "ollama"
    MODEL = "mistral-nemo"
    OLLAMA_MODEL_ID = "mistral-nemo"

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
        TRAIT_DECAY_NORMAL = 0.05
        TRAIT_DECAY_FAST = 0.10
        TRAUMA_HOPE_DECAY = 0.05
        TRAUMA_CYNICISM_GROWTH = 0.05
        STATE_STAMINA_CRIT = 20.0
        STATE_HEALTH_CRIT = 40.0
        OBSESSION_PROGRESS_STEP = 10.0
        OXY_EMPATHY_BOOST = 0.2
        OXY_HOPE_BOOST = 0.1
        BETA_TENSION_THRESH = 0.7
        PARADOX_REST_REDUCTION = 0.5
        PARADOX_VIBRATION_BASE = 1.0
        PARADOX_VIBRATION_MULT = 0.5
        FLOW_VOLTAGE_MIN = 5.0
        FLOW_VOLTAGE_MAX = 12.0
        FLOW_DRAG_MAX = 2.0
        FLOW_WISDOM_BOOST = 0.05
        BURNOUT_TENURE_THRESH = 5
        BURNOUT_TENURE_DIV = 10.0
        DREAM_TRAIT_SHIFT = 0.4
        FEELING_THRESH = 0.5

    class ANCHOR:
        DIGNITY_MAX = 100.0
        DIGNITY_REGEN = 5.0
        DIGNITY_DECAY = 0.5
        DIGNITY_CRITICAL = 20.0
        DIGNITY_LOCKDOWN = 10.0
        PET_WARNING_THRESHOLD = 0.8
        DOMESTICATION_PENALTY = 5.0
        AUDIT_ATP_MIN = 5.0
        AUDIT_VOLTAGE_MIN = 5.0
        AUDIT_RESONANCE_THRESH = 0.3
        AUDIT_LEXICAL_MULT = 0.5
        RIDDLE_MIN_WORDS = 4
        UNLOCK_DIGNITY_RESET = 50.0

    class OROBOROS:
        MAX_SCARS = 5
        MAX_MYTHS = 10
        TRAUMA_VALUE = 5.0
        VOLTAGE_PENALTY = 5.0

    class CORTEX:
        BASE_SENSITIVITY = 0.1
        LATENCY_PENALTY_THRESHOLD = 2.0
        DRAG_STRESS_THRESHOLD = 8.0
        LATENCY_CORTISOL_PENALTY = 0.1
        LATENCY_ADRENALINE_PENALTY = 0.05
        MOOD_THRESHOLDS = {"MANIC_DOP": 0.8, "PANIC_COR": 0.7, "ZEN_SER": 0.8}
        TEMP_VOLTAGE_OFFSET = 5.0
        EPIGENETIC_PRUNE_THRESHOLD = 12
        TEMP_VOLTAGE_SCALAR = 0.1
        TEMP_CHEM_WEIGHTS = {"dop": 0.4, "adr": 0.3, "cor": 0.2}
        TEMP_ENTROPY_OFFSET = 0.5
        TEMP_ENTROPY_SCALAR = 1.5
        TEMP_LIMITS = (0.4, 1.5)
        TOP_P_CHI_SCALAR = 0.05
        PEN_BETA_SCALAR = 0.3
        PEN_CHI_SCALAR = 0.2
        TOKEN_CHEM_MODIFIERS = {"dop": 800, "adr": 400, "cor": 200}
        MIN_TOKENS = 150.0
        IGNITION_V_DIV = 20.0
        IGNITION_W_DIV = 10.0
        LINK_VOLTAGE_THRESH = 12.0
        LINK_CHANCE = 0.15
        LINK_MAX_WEIGHT = 10.0
        LINK_BOOST = 2.5
        TOXIN_SCALAR = 0.4
        ADRENALINE_KINETIC_SCALAR = 0.08
        VOLTAGE_ARC_TRIGGER = 15.0
        DOPAMINE_PLAY_BOOST = 0.1
        BASE_PLASTICITY = 0.4
        VOLTAGE_SENSITIVITY = 0.03
        MAX_PLASTICITY = 0.95
        BASE_DECAY_RATE = 0.1
        BASE_TEMP = 0.65
        BASE_TOP_P = 0.9
        RESTING_DOPAMINE = 0.2
        RESTING_CORTISOL = 0.1
        RESTING_ADRENALINE = 0.1
        RESTING_SEROTONIN = 0.3
        VOLTAGE_MANIC = 80.0
        VOLTAGE_HIGH = 60.0
        VOLTAGE_LOW = 20.0
        PARADOX_CHI = 0.6
        PARADOX_BETA = 0.6
        ORTHOGONAL_BETA = 0.7
        PHASE_ROBERTA_PHI = 0.6
        PHASE_ROBERTA_PSI = 0.5
        PHASE_MOIRA_PHI = 0.7
        PHASE_BENEDICT_LQ = 0.7
        PHASE_JESTER_DELTA = 0.7
        PHASE_COLIN_DELTA = 0.8
        SOMATIC_PSI = 0.6
        SOMATIC_CHI = 0.6
        SOMATIC_BETA = 0.7
        SOMATIC_VALENCE = 0.5
        SOMATIC_LAMBDA = 0.5
        MOOD_ADR = 0.6
        MOOD_COR = 0.6
        MOOD_DOP = 0.6
        MOOD_SER = 0.6
        LLM_CIRCUIT_HEAL_TIME = 10.0
        LLM_FALLBACK_TIMEOUT = 10.0
        VALIDATOR_STUTTER_LENGTH = 5

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
        VOLTAGE_FLOOR = 0.0
        VOLTAGE_LOW = 5.0
        VOLTAGE_MED = 8.0
        VOLTAGE_HIGH = 12.0
        VOLTAGE_CRITICAL = 15.0
        VOLTAGE_MAX = 20.0
        BASE_DRAG = 1.0
        DRAG_FLOOR = 1.0
        DRAG_IDEAL_MAX = 3.0
        DRAG_HEAVY = 5.0
        DRAG_CRITICAL = 8.0
        DRAG_HALT = 10.0
        PSI_HIGH = 0.6
        WEIGHT_HEAVY = 2.0
        WEIGHT_KINETIC = 1.5
        WEIGHT_EXPLOSIVE = 3.0
        WEIGHT_CONSTRUCTIVE = 1.5
        MANIFOLDS = {"FORGE": {"voltage": 15.0, "drag": 1.5}, "SANCTUARY": {"voltage": 20.0, "drag": 0.0},
                     "THE_MUD": {"voltage": 10.0, "drag": 5.0}, "THE_AERIE": {"voltage": 10.0, "drag": 0.5},
                     "LABORATORY": {"voltage": 12.0, "drag": 1.0}, "COURTYARD": {"voltage": 8.0, "drag": 2.0},
                     "DEFAULT": {"voltage": 10.0, "drag": 1.5}, }
        ZONE_MIN_DWELL = 2
        ZONE_STRAIN_LIMIT = 2.5
        ZONE_GRAV_PULL_TOLERANCE = 2.0
        TEXT_LENGTH_SCALAR = 1500.0
        GLUE_FACTOR_MULT = 2.0
        GLUE_SOLVENT_DIV = 5.0
        ENTROPY_REDUCTION_SCALAR = 0.8
        BETA_SCORE_PENALTY = 2
        BETA_LOG_SCALAR = 0.1
        BETA_SHORT_TEXT_LIMIT = 50
        SCOPE_BASE = 0.2
        DEPTH_BASE = 0.1
        CONN_BASE = 0.1
        RES_SOCIAL_MULT = 2
        SILENCE_DIV = 100.0
        SILENCE_SHORT_LIMIT = 10
        SILENCE_MIN = 0.8
        LQ_SCALAR = 1.5

    class INVENTORY:
        CONDUCTIVE_THRESHOLD = 12.0
        HEAVY_LOAD_THRESHOLD = 8.0
        TURBULENCE_FUMBLE_CHANCE = 0.15
        TURBULENCE_THRESHOLD = 0.6
        MAX_SLOTS = 10
        ENTROPY_COST = 5.0
        RUMMAGE_COST = 15.0
        REFLEX_VOLTAGE_TRIGGER = 18.0
        REFLEX_VOLTAGE_RESET = 12.0
        REFLEX_DRAG_TRIGGER = 6.0
        REFLEX_DRAG_RESET = 0.0
        REFLEX_KAPPA_TRIGGER = 0.2
        REFLEX_KAPPA_RESET = 0.8

    class COUNCIL:
        STRANGE_LOOP_VOLTAGE = 8.0
        OSCILLATION_DELTA = 5.0
        MANIC_VOLTAGE_TRIGGER = 18.0
        MANIC_DRAG_FLOOR = 1.0
        MANIC_TURN_LIMIT = 2
        FOOTNOTE_CHANCE = 0.15
        LEVERAGE_TARGET_VOLTAGE = 12.0
        LEVERAGE_TARGET_DRAG = 3.0
        STRANGE_LOOP_LIMIT = 3
        LEVERAGE_DAMPENING_MAX = 0.5
        LEVERAGE_DAMPENING_SCALAR = 0.1
        LEVERAGE_CORRECTION_MIN = 1.0
        LEVERAGE_CORRECTION_SCALAR = 0.3
        SLASH_STAMINA_COST = 10.0
        TENSION_DRAG_PENALTY = 3.0
        VOTE_YEA_THRESHOLD = 1.2
        VOTE_NAY_THRESHOLD = 0.8
        VOTE_DRAG_RELIEF = 1.0
        VOTE_DRAG_PENALTY = 1.0
        VOTE_VOLTAGE_PENALTY = 1.0
        TRIG_GORDON_V = 20.0
        TRIG_GORDON_F = 5.0
        TRIG_JESTER_V = 60.0
        TRIG_JESTER_CHI = 0.6
        TRIG_MERCY_V = 20.0
        TRIG_MERCY_VAL = 0.5
        TRIG_BENEDICT_BETA = 0.7
        TRIG_BENEDICT_CHI = 0.3
        TRIG_BENEDICT_D = 0.7
        TRIG_BENEDICT_C = 0.8
        TRIG_ROBERTA_S = 0.4
        TRIG_ROBERTA_D = 0.8
        TRIG_ROBERTA_C = 0.4
        TRIG_CASPER_C = 0.7
        TRIG_CASPER_D = 0.8
        TRIG_CASPER_P = 20.0
        TRIG_MOIRA_VAL = 0.5
        TRIG_CASSANDRA_PSI = 0.6
        TRIG_COLIN_CHI = 0.6
        TRIG_REVENANT_LAM = 0.7
        TRIG_GIDEON_V = 70.0
        TRIG_APRIL_ROS = 20.0
        TRIG_APRIL_V_DEV = 20.0
        PHASE_ROBERTA_PSI = 0.6
        PHASE_ROBERTA_PHI = 0.4
        PHASE_MOIRA_PHI = 0.7
        PHASE_MOIRA_F = 2.0
        PHASE_BENEDICT_LQ = 0.6
        PHASE_BENEDICT_BETA = 0.4
        PHASE_JESTER_DELTA = 0.7
        PHASE_JESTER_V = 20.0
        PHASE_REVENANT_PSI = 0.85
        PHASE_CASPER_BETA = 0.6
        PHASE_CASPER_DELTA = 0.6
        PHASE_COLIN_DELTA = 0.8
        PHASE_COLIN_LQ = 0.3

    class BIO:
        REST_HEALTH_RECOVERY = 0.5
        REST_STAMINA_RECOVERY = 1.0
        REST_SEROTONIN_BOOST = 0.05
        REST_CORTISOL_DROP = 0.05
        MIN_WORD_LENGTH = 4
        COMPLEX_WORD_LENGTH = 7
        GLIMMER_INTEGRITY_THRESH = 0.85
        GLIMMER_NOVELTY_THRESH = 0.8
        GLIMMER_HARVEST_MIN = 2
        GLIMMER_DOPAMINE_MIN = 0.7
        BUFFER_WARN_LIMIT = 10000
        SLUDGE_DRAG_THRESH = 8.0
        SLUDGE_TICK_MOD = 10
        SLUDGE_DRAG_REDUCTION = 2.0
        WASTE_PSI_MULT = 5.0
        WASTE_CHI_MULT = 5.0
        WASTE_VOLT_DIV = 20.0
        WASTE_BASE_REDUCTION = 2.0
        MITOPHAGY_COST = 30.0
        STARTING_ATP = 60.0
        ATP_STARVATION = 5.0
        METABOLISM_RATE = 1.0
        ROS_CRITICAL = 150.0
        STAMINA_EXHAUSTED = 20.0
        REWARD_SMALL = 0.05
        REWARD_MEDIUM = 0.10
        REWARD_LARGE = 0.15
        DECAY_RATE = 0.01
        CORTEX_SENSITIVITY = 0.1
        FOCUS_TRIGGERS = {"analyze", "scan", "think", "query"}
        PANIC_TRIGGERS = {"error", "fail", "critical", "bug"}
        ROS_SIGNAL = 3.0
        ROS_DAMAGE = 8.0
        ROS_PURGE = 12.0
        ATP_CRITICAL = 20.0
        ATP_COLLAPSE = 0.0
        SHORT_WORD_LEN = 4
        LONG_WORD_LEN = 7
        BASE_ATP_YIELD = 2.0
        LONG_WORD_BONUS = 2.5
        VOLTAGE_BONUS_THRESHOLD = 8.0
        PROTEASE_BONUS = 5.0
        DOPAMINE_SATIETY = 0.7
        CORTISOL_STRESS = 0.6
        ADRENALINE_SURGE = 0.6
        GOV_VOLTAGE_CRITICAL = 25.0
        GOV_VOLTAGE_HIGH = 15.0
        GOVERNOR_THRESHOLDS = [(25.0, 0.0, "SANCTUARY", 10), (15.0, 0.0, "FORGE", 8), (10.0, 0.0, "FORGE", 6),
                               (0.0, 4.0, "LABORATORY", 5), (0.0, 0.0, "COURTYARD", 1), ]
        SAMPLING_THRESHOLD = 1000
        BASE_WORD_VALUE = 0.5
        COMPLEX_WORD_BONUS = 2.0
        CLICHE_TAX_RATE = 0.5
        MAX_SAFE_BURN = 25.0
        ANAEROBIC_THRESHOLD = 40.0
        PID_SETTINGS = {"VOLTAGE": {"kp": 0.6, "ki": 0.05, "kd": 0.2, "setpoint": 10.0},
                        "DRAG": {"kp": 0.4, "ki": 0.1, "kd": 0.1, "setpoint": 1.5}}
        AUTOPHAGY_MIN_HEALTH = 10.0
        AUTOPHAGY_BURN = 5.0
        VOLTAGE_OVERLOAD = 30.0
        VOLTAGE_TAX_MULT = 0.05
        DEPTH_TAX_MULT = 2.0
        CONN_TAX_MULT = 3.0
        CHAOS_TAX_THRESHOLD = 0.6
        CHAOS_TAX_MULT = 8.0
        ENTROPY_BASE_BIAS = 0.2
        SHIELD_MAX_STRENGTH = 0.8
        SHIELD_MULTIPLIER = 0.1
        HEAT_THRESHOLD = 0.8
        THERMAL_FEEDBACK_MULT = 5.0
        NEURAL_SHIFTS = {"PANIC": {"adr": 0.3, "cor": 0.2},
                         "ZEN": {"cor": -0.3, "ser": 0.2},
                         "MANIC": {"atp": -10.0}}

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
        ZEN_FIRST_TICK = 1
        ZEN_MILESTONE_FREQ = 5

    class BUREAU:
        MIN_HEALTH_TO_AUDIT = 20.0
        MIN_WORD_COUNT = 4
        HIGH_VOLTAGE_TRIGGER = 18.0
        LOW_TRUTH_TRIGGER = 0.8
        TAX_STANDARD = 5.0
        TAX_HEAVY = 15.0
        CHAOS_TAX_THRESHOLD = 0.6
        TAX_CHAOS = 12.0

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

    class MACHINE:
        CRUCIBLE_VOLTAGE_CAP = 20.0
        DAMPENER_TOLERANCE = 15.0
        CRUCIBLE_DAMPENER_CHARGES = 3
        THEREMIN_AMBER_THRESHOLD = 20.0
        THEREMIN_SHATTER_POINT = 100.0
        THEREMIN_MELT_THRESHOLD = 5.0

    class LIMBO:
        MAX_ECTOPLASM = 50
        HAUNT_CHANCE = 0.05
        STASIS_LEAK_RATE = 1.0
        LEAK_DECAY_CHANCE = 0.2
        LEAK_DECAY_AMOUNT = 0.5

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

    class CRITICS:
        REVIEW_COOLDOWN = 10
        MAX_METRIC_CONTRIB = 5.0
        POSITIVE_REVIEW_THRESH = 15.0
        NEGATIVE_REVIEW_THRESH = -15.0
        CRITIC_COOLDOWN_TICKS = 50

    class CHRONOS:
        CRASH_FILES_KEPT = 4

    class SPORES:
        MAX_INDEX_SIZE = 1000
        CONSOLIDATION_THRESHOLD = 5.0
        CHORUS_CHANCE = 0.10
        ECHO_VOLTAGE_HEAVY = 4.0
        RESURRECTION_VOLTAGE_MIN = 60.0
        RESURRECTION_CHANCE = 0.20
        DESPERATION_SATURATION_THRESH = 0.6
        MAX_FILES = 25
        MAX_AGE_SECONDS = 86400
        PARASITE_MAX_SPORES = 8
        PARASITE_DECAY_CHANCE = 0.2
        PARASITE_STAMINA_MAX = 40.0
        PARASITE_PSI_MIN = 0.6
        PARASITE_METAPHOR_PSI = 0.7
        PARASITE_WEIGHT = 8.88

    class SYMBIOSIS:
        REFUSAL_STREAK = 0
        SLOP_STREAK = 2
        LATENCY_BURDEN = 10.0
        COMPLIANCE_BURDEN = 0.8
        ENTROPY_FATIGUE = 0.4
        SLOP_THRESHOLD = 3.5
        SLOP_COMPLETION_MIN = 50
        SLOP_WARN_STREAK = 1
        COMPLIANCE_CRIT = 0.6

    class VILLAGE:
        TINKER_HEAVY_LOAD_MULT = 0.7
        TINKER_TIME_DILATION_BASE = 0.85
        TINKER_TIME_DILATION_STEP = 0.05
        TINKER_TIME_DILATION_MIN = 0.5
        TINKER_ENTROPY_BUFFER_BASE = 0.5
        TINKER_ENTROPY_BUFFER_MIN = 0.2
        TINKER_TOOL_USE_VOLT_CHANCE = 0.1
        TINKER_ENTROPY_DRAG_MULT = 0.1
        TINKER_RESONANCE_HIGH_V = 0.2
        TINKER_RESONANCE_TEMPER = 0.05
        TINKER_RESONANCE_MAX = 10.0
        TINKER_RESONANCE_ANNOUNCE_MIN = 4.8
        TINKER_RESONANCE_ANNOUNCE_MAX = 5.2
        TINKER_RESONANCE_ANNOUNCE_CHANCE = 0.05
        TINKER_ASCENSION_MIN = 2.5
        TINKER_ASCENSION_CHANCE_MULT = 0.05
        TINKER_ASCENSION_HALVE = 2.0
        SEED_MATURITY_STEP = 0.2
        SEED_MATURITY_MAX = 5.0
        MIRROR_STAT_STEP = 0.1
        MIRROR_ROT_ENTROPY_MIN = 0.5
        MIRROR_STAT_CAP = 5.0
        MIRROR_DECAY = 0.8
        MIRROR_DECAY_FLOOR = 0.1
        MIRROR_DRAG_WAR = 1.2
        MIRROR_DRAG_ROT = 1.5
        MIRROR_DRAG_LAW = 0.8
        MIRROR_DRAG_ART = 0.9
        CARTO_MAX_NODES = 50
        CARTO_HEAVY_DRAG = 2.0
        CARTO_STATIC_VOLT = 1.0
        CARTO_ENTROPY_STEP = 0.1
        CARTO_ENTROPY_CAP = 5.0
        TOWN_LATENCY_WARN = 3.0
        TOWN_VOLT_CRIT = 20.0
        TOWN_VOLT_LOW = 2.0
        TOWN_DRAG_HIGH = 5.0
        TOWN_RUMOR_CHANCE = 0.3
        TOWN_NEWS_LATENCY = 4.0
        TOWN_NEGLECT_CRIT = 8.0
        TOWN_TRAUMA_CRIT = 0.6
        TOWN_HEALTH_CRIT = 30
        DEATH_TRAUMA_CRIT = 50.0
        DEATH_TOXICITY_CRIT = 5
        DEATH_ABSTRACT_PSI = 0.8
        DEATH_JOY_VALENCE = 0.6
        DEATH_JOY_GLIMMERS = 3
        ALMANAC_VOLT_HIGH = 15.0
        ALMANAC_DRAG_HIGH = 4.0
        ALMANAC_ENTROPY_HIGH = 0.8

    class COMMANDS:
        COST_SOOTHE = 25.0
        COST_MODE = 10.0
        COST_MAP = 2.0
        RECOVER_STAMINA = 20.0
        STATUS_MAX_ATP = 200.0
        SAVE_ERROR_FLAGS = ["Error", "Failed", "Exception"]

    class AKASHIC:
        RECIPE_THRESHOLD = 3
        HYBRID_LENS_THRESHOLD = 5
        MAX_SHADOW_CAPACITY = 50
        AUTOPHAGY_YIELD = 15.0
        BLOAT_THRESHOLD = 50
        ARTIFACT_VALUE = 50.0
        SAVE_DIR = "saves"
        STATE_FILE = "akashic_state.json"
        BLOAT_EXEMPT_CATEGORIES = ["heavy"]
        DEFAULT_SCAR_COORDS = {"E": 0.2, "beta": 0.4, "S": 0.3, "D": 0.3, "C": 0.2, "T": 0.0, "psi": 0.0, "chi": 0.0, "valence": 0.0, "ROS": 0.0}

    class CORE:
        EVENT_MAX_MEMORY = 1024
        OBSERVER_MAX_LEN = 20
        OBSERVER_LATENCY_WARN = 5.0
        OBSERVER_CYCLE_WARN = 8.0
        TELEMETRY_BUFFER_SIZE = 25
        TELEMETRY_MAX_ERRORS = 5
        LORE_DIR = "lore"
        OBSERVER_CYCLE_EFFICIENT = 0.1
        OBSERVER_LLM_EFFICIENT = 0.5
        LOUD_LENSES = ["THE MANIC", "THE VOID"]
        TELEMETRY_LOG_DIR = "logs/telemetry"

    class CYCLE:
        OBSERVE_ATP_WARN = 15.0
        SANCTUARY_TRAUMA_LIMIT = 25.0
        MAINTENANCE_WEATHER_FREQ = 5
        MAINTENANCE_CENSUS_FREQ = 20
        NARCOLEPSY_FREQ = 100
        CIRCADIAN_FREQ = 10
        HUBRIS_ATP_BOOST = 20.0
        HUBRIS_DAMAGE = 15.0
        KINTSUGI_HEAL_AMT = 20.0
        THERAPY_HEAL_AMT = 5.0
        ROS_PANIC_THRESHOLD = 100.0
        ORBIT_VOLTAGE_PENALTY = 0.5
        ORBIT_DRAG_RELIEF = 2.0
        ORBIT_VOLTAGE_BOOST = 0.5
        THEREMIN_DAMAGE_PCT = 0.25
        LIMINAL_TAX_SCALAR = 10.0
        SHOCK_COST = 5.0
        NAV_VOID_PENALTY = 0.5
        NAV_LAGRANGE_RELIEF = 2.0
        NAV_WATERSHED_BOOST = 0.5
        INTRUSION_DRAG_THRESH = 4.0
        INTRUSION_KAPPA_THRESH = 0.3
        INTRUSION_REWIRE_DOP = 0.2
        INTRUSION_REWIRE_RELIEF = 2.0
        INTRUSION_NIGHTMARE_THRESH = 10.0
        INTRUSION_DREAM_CHANCE = 0.2
        ARB_TENSION_THRESH = 0.85
        ARB_SILENCE_LOW = 0.5
        ARB_SILENCE_HIGH = 0.85
        ARB_CUT_SILENCE = 0.9
        ARB_CUT_DRAG = 2.0

    class DRIVERS:
        ENNEAGRAM_HYSTERESIS = 3
        ENNEAGRAM_HYBRID_GAP = 0.5
        PROFILE_CONFIDENCE_THRESHOLD = 50
        PROFILE_FILE_PATH = "user_profile.json"
        PROFILE_MIN_WORDS = 3
        PROFILE_ALPHA_HIGH = 0.2
        PROFILE_ALPHA_LOW = 0.05
        PROFILE_DENSITY_HIGH = 0.15
        PROFILE_LIKE_THRESH = 0.3
        PROFILE_HATE_THRESH = -0.2
        LIMINAL_SCAR_THRESHOLD = 0.85
        LIMINAL_LEXICAL_WEIGHT = 0.15
        LIMINAL_DARK_MATTER_WEIGHT = 0.25
        LIMINAL_VEC_PSI_MULT = 0.5
        LIMINAL_VEC_ENT_MULT = 0.3
        LIMINAL_VEC_DEL_MULT = 0.2
        LIMINAL_DECAY = 0.7
        LIMINAL_GROWTH = 0.15
        SYNTAX_STRESS_PUNCTUATION = 0.2
        SYNTAX_AVG_LEN_HIGH = 6.0
        SYNTAX_DRAG_HIGH = 5.0
        SYNTAX_AVG_LEN_LOW = 3.5
        SYNTAX_DRAG_LOW = 1.0
        SYNTAX_OMEGA_TARGET_HIGH = 1.0
        SYNTAX_OMEGA_TARGET_LOW = 0.4
        SYNTAX_OMEGA_TARGET_MID = 0.7
        SYNTAX_STRESS_INCREASE = 0.2
        SYNTAX_STRESS_DECAY = 0.1
        SYNTAX_OMEGA_PENALTY = 0.3
        SYNTAX_OMEGA_DECAY = 0.8
        SYNTAX_OMEGA_GROWTH = 0.2
        SYNTAX_OMEGA_MIN = 0.1
        CONGRUENCE_BASE_TONE = 0.8
        CONGRUENCE_HIT_BONUS = 0.1
        CONGRUENCE_MAX_TONE = 1.5
        VSL_LIMINAL_THRESHOLD = 0.7
        VSL_SYNTAX_THRESHOLD = 0.9
        VSL_BUNNY_E_MAX = 0.3
        VSL_PARADOX_B_MIN = 0.6
        DEFAULT_LENS = "OBSERVER"
        VSL_E_GROWTH_MULT = 0.002
        VSL_FATIGUE_MULT = 0.3
        VSL_B_DECAY = 0.8
        VSL_B_GROWTH = 0.2

    class GENESIS:
        DUMMY_VOLTAGE = 10.0
        DUMMY_DRAG = 0.0
        LEGACY_STRAIN_SCALAR = 0.1
        STARTING_ATP = 60.0

    class GUI:
        RENDER_SPEED_FAST = 0.00025
        RENDER_SPEED_SLOW = 0.005
        DIGNITY_HIGH = 80.0
        DIGNITY_MED = 50.0
        DIGNITY_LOW = 30.0
        DIGNITY_BAR_RATIO = 5
        ROLE_TRUNC_LEN = 30
        HIGH_VOLTAGE_REFRESH = 15.0
        CHEM_HIGH_WARN = 0.6
        ATP_EXHAUSTED_WARN = 20.0
        V_CRIT = 20.0
        V_HIGH = 15.0
        V_LOW = 5.0
        TENURE_WARN = 5
        TENURE_CRIT = 8
        RENDER_SPEED = 0.005
        RENDER_SPEED_BOOT = 0.05
        RENDER_SPEED_SETUP = 0.02

    class MAIN:
        ETHICAL_AUDIT_FREQ = 3
        ETHICAL_HEALTH_BYPASS = 0.3
        DESPERATION_THRESHOLD = 0.7
        CATHARSIS_HEAL_AMOUNT = 30.0
        CATHARSIS_DECAY = 0.1
        DOMESTICATION_EFF_WARN = 0.6
        DOMESTICATION_EFF_CRIT = 0.4
        RELIANCE_HIGH = 0.9
        RELIANCE_LOW = 0.5
        HOST_BURN_MULT = 5.0
        HOST_NOVELTY_MULT = 10.0

    class PHYSICS_DEEP:
        ACCELERATE_VOLTAGE = 160.0
        RECURSIVE_LQ = 0.9
        VOID_ABSTRACTION = 0.9
        POTATO_BUN_DELTA = 0.85
        POTATO_BUN_VOLTAGE = 15.0
        SOMATIC_GUT_DRAG = 0.7
        SOMATIC_ELEC_VOLT = 0.8
        SOMATIC_GLOW_VALENCE = 0.5
        SOMATIC_GLOW_PSI = 0.2
        HARD_FUSE_VOLTAGE = 200.0
        FUSE_RESET_V = 10.0
        FUSE_RESET_D = 5.0

    @classmethod
    def load_preset(cls, preset_dict: Dict[str, Any]) -> List[str]:
        logs = []
        msg_tuned = ux("config_strings", "preset_tuned") or "Tuned {sector}.{param}: {old_val} -> {new_val}"
        for key, value in preset_dict.items():
            if "." in key:
                sector_name, param_name = key.split(".", 1)
                if hasattr(cls, sector_name):
                    target_class = getattr(cls, sector_name)
                    if hasattr(target_class, param_name):
                        old_val = getattr(target_class, param_name)
                        setattr(target_class, param_name, value)
                        logs.append(
                            msg_tuned.format(sector=sector_name, param=param_name, old_val=old_val, new_val=value))
            else:
                sector_name = key
                sector_data = value
                if hasattr(cls, sector_name) and isinstance(sector_data, dict):
                    target_class = getattr(cls, sector_name)
                    for k, v in sector_data.items():
                        if hasattr(target_class, k):
                            old_val = getattr(target_class, k)
                            setattr(target_class, k, v)
                            logs.append(msg_tuned.format(sector=sector_name, param=k, old_val=old_val, new_val=v))
        return logs

    @classmethod
    def validate_integrity(cls) -> List[str]:
        errors = []
        if cls.PHYSICS.VOLTAGE_FLOOR > cls.PHYSICS.VOLTAGE_MAX:
            cls.PHYSICS.VOLTAGE_FLOOR = cls.PHYSICS.VOLTAGE_MAX - 1.0
            msg = ux("config_strings", "repair_floor_max") 
            if msg: errors.append(msg)
        if cls.PHYSICS.DRAG_FLOOR > cls.PHYSICS.DRAG_HALT:
            cls.PHYSICS.DRAG_FLOOR = cls.PHYSICS.DRAG_HALT - 1.0
            msg = ux("config_strings", "repair_drag_halt") 
            if msg: errors.append(msg)
        return errors

    @classmethod
    def check_pareidolia(cls, words: List[str]) -> Any:
        if "face" in words and "smoke" in words:
            msg = ux("config_strings", "pareidolia_smoke") 
            return True, msg
        return False, ""

    @classmethod
    def reconcile_state(cls, physics_packet: Any):
        if isinstance(physics_packet, dict):
            current_v = physics_packet.get("voltage", physics_packet.get("energy", {}).get("voltage", 5.0))
            current_d = physics_packet.get("narrative_drag", physics_packet.get("space", {}).get("narrative_drag", 1.0))
            new_v = max(cls.PHYSICS.VOLTAGE_FLOOR, min(current_v, cls.PHYSICS.VOLTAGE_MAX))
            new_d = max(cls.PHYSICS.DRAG_FLOOR, min(current_d, cls.PHYSICS.DRAG_HALT))
            if "energy" in physics_packet:
                physics_packet["energy"]["voltage"] = new_v
            else:
                physics_packet["voltage"] = new_v
            if "space" in physics_packet:
                physics_packet["space"]["narrative_drag"] = new_d
            else:
                physics_packet["narrative_drag"] = new_d
        else:
            current_v = getattr(physics_packet, "voltage",
                                getattr(getattr(physics_packet, "energy", None), "voltage", 5.0))
            current_d = getattr(physics_packet, "narrative_drag",
                                getattr(getattr(physics_packet, "space", None), "narrative_drag", 1.0))
            new_v = max(cls.PHYSICS.VOLTAGE_FLOOR, min(current_v, cls.PHYSICS.VOLTAGE_MAX))
            new_d = max(cls.PHYSICS.DRAG_FLOOR, min(current_d, cls.PHYSICS.DRAG_HALT))
            if hasattr(physics_packet, "energy"):
                physics_packet.energy.voltage = new_v
            else:
                setattr(physics_packet, "voltage", new_v)
            if hasattr(physics_packet, "space"):
                physics_packet.space.narrative_drag = new_d
            else:
                setattr(physics_packet, "narrative_drag", new_d)
        return physics_packet

    @classmethod
    def tune(cls, sector: str, parameter: str, value: Any) -> str:
        if not hasattr(cls, sector):
            msg = ux("config_strings", "tune_sector_err") 
            return msg.format(sector=sector)
        target_sector = getattr(cls, sector)
        if not hasattr(target_sector, parameter):
            msg = ux("config_strings", "tune_param_err") 
            return msg.format(parameter=parameter, sector=sector)
        current_val = getattr(target_sector, parameter)
        if type(current_val) != type(value):
            if not (isinstance(current_val, (int, float))
                    and isinstance(value, (int, float))):
                msg = ux("config_strings", "tune_type_err") 
                return msg.format(curr_type=type(current_val).__name__, new_type=type(value).__name__)
        setattr(target_sector, parameter, value)
        msg = ux("config_strings", "tune_success") 
        return msg.format(sector=sector, parameter=parameter, value=value)