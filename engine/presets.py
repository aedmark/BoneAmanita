import copy
import json
import os
from types import SimpleNamespace
from typing import Any, Dict, List

from engine.struts import ux


class BonePresets:
    ZEN_GARDEN = {
        "PHYSICS.VOLTAGE_FLOOR": 1.0,
        "PHYSICS.VOLTAGE_MAX": 25.0,
        "PHYSICS.DRAG_FLOOR": 0.5,
        "BIO.DECAY_RATE": 0.001,
        "BIO.STAMINA_EXHAUSTED": 5.0,
        "COUNCIL.MANIC_VOLTAGE_TRIGGER": 99.0,
        "tuning": "ZEN",
    }

    THUNDERDOME = {
        "PHYSICS.VOLTAGE_FLOOR": 8.0,
        "PHYSICS.VOLTAGE_MAX": 30.0,
        "PHYSICS.DRAG_FLOOR": 0.5,
        "BIO.ATP_STARVATION": 20.0,
        "COUNCIL.MANIC_VOLTAGE_TRIGGER": 12.0,
        "CHANCE.RARE": 0.20,
    }

    SANCTUARY = {
        "COUNCIL.LEVERAGE_TARGET_VOLTAGE": 7.0,
        "COUNCIL.LEVERAGE_TARGET_DRAG": 2.0,
        "PHYSICS.VOLTAGE_MAX": 15.0,
        "PHYSICS.DRAG_FLOOR": 0.0,
        "BIO.METABOLISM_RATE": 0.5,
        "tuning": "ZEN",
        "VOLTAGE_TARGET": 7.0,
        "VOLTAGE_TOLERANCE": 3.0,
        "DRAG_TARGET": 2.0,
        "DRAG_TOLERANCE": 1.5,
        "TRUTH_TARGET": 0.7,
        "E_TARGET": 0.4,
        "B_TARGET": 0.5,
        "ZONE": "SANCTUARY",
        "COLOR": "\033[32m",
        "COLOR_NAME": "GRN",
    }

    LABORATORY = {
        "PHYSICS.VOLTAGE_FLOOR": 0.5,
        "PHYSICS.VOLTAGE_MAX": 15.0,
        "PHYSICS.DRAG_FLOOR": 2.0,
        "BIO.DECAY_RATE": 0.0,
    }

    MODES = {
        "ADVENTURE": {
            "description": "The default experience. Survival, inventory, exploration.",
            "tuning": "SANCTUARY",
            "ui_layer": 1,
            "village_suppression": [],
            "prompt_key": "ADVENTURE",
            "show_inventory": True,
            "show_location": True,
            "show_vitals": True,
            "allow_loot": True,
            "allow_metrics": False,
            "atp_drain_enabled": True,
            "chaos_tax_enabled": True,
            "gate_tolerance": 1.0,
            "voltage_floor_override": None,
            "active_mods": [],
            "default_ui_depth": "WARM",
        },
        "CONVERSATION": {
            "description": "Pure dialogue. No entropy, no items, just connection.",
            "tuning": "ZEN",
            "ui_layer": 1,
            "village_suppression": [
                "GORDON",
                "NAVIGATOR",
                "CARTOGRAPHER",
                "TINKERER",
                "DEATH",
                "BUREAU",
            ],
            "prompt_key": "CONVERSATION",
            "show_inventory": False,
            "show_location": False,
            "show_vitals": False,
            "allow_loot": False,
            "allow_metrics": False,
            "atp_drain_enabled": False,
            "chaos_tax_enabled": False,
            "gate_tolerance": 1.6,
            "voltage_floor_override": None,
            "active_mods": [],
            "default_ui_depth": "WARM",
        },
        "CREATIVE": {
            "description": "High voltage, low drag. Hallucination enabled.",
            "tuning": "MANIC",
            "ui_layer": 1,
            "village_suppression": ["GORDON", "BENEDICT", "BUREAU", "NAVIGATOR"],
            "prompt_key": "CREATIVE",
            "show_inventory": False,
            "show_location": False,
            "show_vitals": False,
            "allow_loot": False,
            "allow_metrics": False,
            "gate_tolerance": 1.5,
            "atp_drain_enabled": True,
            "chaos_tax_enabled": False,
            "voltage_floor_override": 70.0,
            "active_mods": ["LIMINAL"],
            "default_ui_depth": "LITE",
        },
        "TECHNICAL": {
            "description": "Raw data stream. Debugging and code generation.",
            "tuning": "DEBUG",
            "ui_layer": 2,
            "village_suppression": ["MOIRA", "JESTER", "CASSANDRA", "APRIL"],
            "prompt_key": "TECHNICAL",
            "show_inventory": False,
            "show_location": False,
            "show_vitals": True,
            "allow_loot": False,
            "allow_metrics": True,
            "gate_tolerance": 1.0,
            "atp_drain_enabled": True,
            "chaos_tax_enabled": True,
            "voltage_floor_override": None,
            "active_mods": ["CODING", "SYNTAX"],
            "default_ui_depth": "DEEP",
        },
    }

    STANDARD = {
        "PHYSICS": {"VOLTAGE_MAX": 20.0, "BASE_DRAG": 1.0},
        "BIO": {"METABOLISM_RATE": 1.0},
    }
    ZEN = {
        "PHYSICS": {"VOLTAGE_MAX": 10.0, "BASE_DRAG": 0.0},
        "BIO": {"METABOLISM_RATE": 0.1},
    }
    MANIC = {
        "PHYSICS": {"VOLTAGE_MAX": 50.0, "BASE_DRAG": 0.5},
        "BIO": {"METABOLISM_RATE": 2.0},
    }
    DEBUG = {
        "PHYSICS": {"VOLTAGE_MAX": 100.0, "BASE_DRAG": 0.0},
        "BIO": {"METABOLISM_RATE": 0.0},
    }


class BoneConfig:
    GRAVITY_WELL_THRESHOLD = 15.0
    SHAPLEY_MASS_THRESHOLD = 5.0

    TRAIT_ARCHETYPES = {
        "THE POET": {"ABSTRACT": 0.6, "PHOTO": 0.3, "ENTROPY": 0.1},
        "THE ENGINEER": {"CONSTRUCTIVE": 0.7, "HEAVY": 0.3},
        "THE NIHILIST": {"ENTROPY": 0.8, "CRYO": 0.2},
        "THE CRITIC": {"THERMAL": 0.5, "ABSTRACT": 0.5},
        "THE EXPLORER": {"KINETIC": 0.6, "AEROBIC": 0.4},
        "THE OBSERVER": {"VOID": 0.5, "ABSTRACT": 0.2},
    }

    TRAUMA_VECTOR = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
    VERSION = "20.7.0"
    VERBOSE_LOGGING = True
    MAX_HEALTH = 100.0
    MAX_STAMINA = 100.0
    MAX_ATP = 100.0
    STAMINA_REGEN = 1.0
    MAX_DRAG_LIMIT = 5.0
    REM_IDLE_THRESHOLD = 4800.0
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
    DEFAULT_LLM_ENDPOINTS = {
        "ollama": "http://127.0.0.1:11434/v1/chat/completions",
        "openai": "https://api.openai.com/v1/chat/completions",
        "lm_studio": "http://127.0.0.1:1234/v1/chat/completions",
        "mock": "N/A",
    }
    PROVIDER = "ollama"
    BASE_URL = None
    API_KEY = "ollama"
    MODEL = "gemma4:12b"
    # DSPyCritic is a fast boilerplate/faithfulness filter, not the answering
    # model D7 tuned for somatic compliance. It gets its own knob so tuning
    # one never silently retunes the other.
    DSPY_MODEL = "gemma4:e4b"
    OLLAMA_FALLBACK = ""
    REQUIRED_CONFIG = {
        "CORTEX": [
            "BASE_TOKENS",
            "MAX_TOKENS",
            "SELF_CARE_THRESHOLD",
            "LLM_FAILURE_THRESHOLD",
            "MAX_HISTORY_LENGTH",
            "MOOD_THRESHOLDS",
            "EXHAUSTION_GATE",
            "COUNTERFACTUAL_ROS_GATE",
            "REASONING_EFFORT",
            "COGNITIVE_RETRY_LIMIT",
            "EPIGENETIC_MUTATION_DISABLED_MODES",
            "KEYWORD_TRIGGERS_DISABLED_MODES",
            "MOOG_DISABLED_MODES",
        ],
        "MACHINE": ["PACEMAKER_BOREDOM_THRESHOLD", "CRUCIBLE_MELTDOWN_VOLTAGE"],
        "DRIVERS": [
            "LIMINAL_SCAR_RELIEF",
            "LIMINAL_TRAUMA_HEAL",
            "LIMINAL_TRAUMA_AGGRAVATE",
            "LIMINAL_STRESS_THRESH",
        ],
        "BIO": [
            "GOVERNOR_THRESHOLDS",
            "PID_SETTINGS",
            "GENTLE_COST_SCALE",
            "ATP_IDLE_RECOVERY_PER_MIN",
            "ATP_IDLE_RECOVERY_CAP",
            "ATP_SILENCE_YIELD",
            "ROS_DECAY_PER_TURN",
            "COUNTERFACTUAL_ATP_COST",
            "HLA_MASK_TAX_MAX",
            "GATEKEEPER_BANNED_TAX",
            "GATEKEEPER_BANNED_ROS",
        ],
        "PHYSICS": ["TASTE_CONFIDENCE_FLOOR", "ZONE_MARGIN"],
        "CD": ["LAMBDA"],
        "EMBEDDINGS": ["BACKEND", "MODEL", "URL"],
        "GATE": ["Z_PIVOT", "T_OPEN_BASE", "T_GAIN", "T_MAX", "MIN_CORPUS", "TOP_K"],
        "STAGE": [
            "TENSION_HOLD_MAGNITUDE",
            "SYNTHESIS_ATP_FLOOR",
            "MAX_CONSECUTIVE_HOLDS",
            "SILENCE_COST",
        ],
        "SOMATIC_BUDGET": [
            "WORD_CAP_DEFAULT",
            "SENTENCE_CAP_DEFAULT",
            "RETRY_ALLOWANCE_DEFAULT",
            "TEMP_BAND_DEFAULT",
            "E_U_FLAGGING",
            "E_U_TIRING",
            "SENTENCE_CAP_FLAGGING",
            "WORD_CAP_FLAGGING",
            "SENTENCE_CAP_TIRING",
            "P_U_CRITICAL",
            "ATP_DEPLETED",
            "ATP_MODERATE",
            "SENTENCE_CAP_ATP_DEPLETED",
            "RETRY_ALLOWANCE_ATP_DEPLETED",
            "TEMP_BAND_ATP_DEPLETED",
            "SENTENCE_CAP_ATP_MODERATE",
            "RETRY_ALLOWANCE_ATP_MODERATE",
            "ROS_TURBULENT",
            "TEMP_BAND_ROS_TURBULENT",
            "SENTENCE_CAP_ANAEROBIC",
            "RETRY_ALLOWANCE_ANAEROBIC",
        ],
        "USER": [
            "STAMINA_MAX",
            "STAMINA_RESONANCE_HEADROOM",
            "STAMINA_TRAUMA_COST",
            "STAMINA_FLOOR_FRACTION",
            "BASELINE_WINDOW",
            "BREVITY_FLOOR",
            "DISENGAGEMENT_RATE",
            "REENGAGEMENT_RATE",
        ],
    }

    USER = {
        "STAMINA_MAX": 100.0,
        "STAMINA_RESONANCE_HEADROOM": 25.0,
        "STAMINA_TRAUMA_COST": 4.0,
        "STAMINA_FLOOR_FRACTION": 0.5,
        "STAMINA_RECOVERY": 5.0,
        "STAMINA_WORD_COST": 0.5,
        "BASELINE_WINDOW": 8,
        "BREVITY_FLOOR": 0.5,
        "DISENGAGEMENT_RATE": 0.15,
        "REENGAGEMENT_RATE": 0.10,
    }

    STAGE = {
        "TENSION_HOLD_MAGNITUDE": 3,
        "SYNTHESIS_ATP_FLOOR": 25.0,
        "MAX_CONSECUTIVE_HOLDS": 2,
        "SILENCE_COST": 2.0,
    }

    GATE = {
        "Z_PIVOT": 0.5,
        "T_OPEN_BASE": 0.7,
        "T_GAIN": 0.15,
        "T_MAX": 1.2,
        "T_LOCKED": 0.0,
        "MIN_CORPUS": 32,
        "TOP_K": 10,
    }

    SOMATIC_BUDGET = {
        "WORD_CAP_DEFAULT": 200,
        "SENTENCE_CAP_DEFAULT": 10,
        "RETRY_ALLOWANCE_DEFAULT": 3,
        "TEMP_BAND_DEFAULT": (0.6, 0.9),
        "E_U_FLAGGING": 0.6,
        "E_U_TIRING": 0.4,
        "SENTENCE_CAP_FLAGGING": 3,
        "WORD_CAP_FLAGGING": 60,
        "SENTENCE_CAP_TIRING": 5,
        "P_U_CRITICAL": 30.0,
        "ATP_DEPLETED": 20.0,
        "ATP_MODERATE": 40.0,
        "SENTENCE_CAP_ATP_DEPLETED": 3,
        "RETRY_ALLOWANCE_ATP_DEPLETED": 1,
        "TEMP_BAND_ATP_DEPLETED": (0.4, 0.6),
        "SENTENCE_CAP_ATP_MODERATE": 5,
        "RETRY_ALLOWANCE_ATP_MODERATE": 2,
        "ROS_TURBULENT": 50.0,
        "TEMP_BAND_ROS_TURBULENT": (0.3, 0.5),
        "SENTENCE_CAP_ANAEROBIC": 5,
        "RETRY_ALLOWANCE_ANAEROBIC": 2,
    }

    CD: Dict[str, Any] = {
        "LAMBDA": 1.0,
    }

    EMBEDDINGS = {
        "BACKEND": "auto",
        "MODEL": "nomic-embed-text",
        "URL": "http://127.0.0.1:11434/v1/embeddings",
        "API_KEY": "ollama",
        "TIMEOUT": 20.0,
        "MAX_CHARS": 2048,
    }
    _TEMPLATE_DATA = {}

    @classmethod
    def _load_class_defaults(cls):
        base_dir = str(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        preset_path = os.path.join(base_dir, "lore", "tuning_presets.json")
        tuning_data = {}
        if os.path.exists(preset_path):
            try:
                with open(preset_path, "r", encoding="utf-8") as f:
                    tuning_data = json.load(f)
            except Exception as e:
                print(f"Failed to load {preset_path}: {e}")
        core_sectors = [
            "PHYSICS",
            "BIO",
            "CORTEX",
            "SOUL",
            "COUNCIL",
            "INVENTORY",
            "MAIN",
            "GUI",
            "WHIMSY",
            "OROBOROS",
            "ANCHOR",
            "PHYSICS_DEEP",
        ]
        for sector in core_sectors:
            if sector not in tuning_data:
                tuning_data[sector] = {}
        cls._TEMPLATE_DATA = tuning_data
        for sector_name, properties in tuning_data.items():
            setattr(cls, sector_name, SimpleNamespace(**copy.deepcopy(properties)))

    def __init__(self):
        for sector_name, properties in self._TEMPLATE_DATA.items():
            setattr(self, sector_name, SimpleNamespace(**copy.deepcopy(properties)))

    def load_preset(self, preset_dict: Dict[str, Any]) -> List[str]:
        logs = []
        msg_tuned = (
            ux("config_strings", "preset_tuned")
            or "Tuned {sector}.{param}: {old_val} -> {new_val}"
        )
        updates = []
        for key, value in preset_dict.items():
            if "." in key:
                updates.append((*key.split(".", 1), value))
            elif isinstance(value, dict):
                updates.extend((key, k, v) for k, v in value.items())
            else:
                updates.append(("ROOT", key, value))
        for sector_name, param_name, val in updates:
            target_sector = (
                self if sector_name == "ROOT" else getattr(self, sector_name, None)
            )
            if target_sector and hasattr(target_sector, param_name):
                old_val = getattr(target_sector, param_name)
                setattr(target_sector, param_name, val)
                logs.append(
                    msg_tuned.format(
                        sector=sector_name,
                        param=param_name,
                        old_val=old_val,
                        new_val=val,
                    )
                )
        errors = self.validate_integrity()
        return logs + errors

    def validate_integrity(self) -> List[str]:
        errors = []
        p = self.PHYSICS
        p.VOLTAGE_FLOOR = float(getattr(p, "VOLTAGE_FLOOR", 0.0))
        p.VOLTAGE_MAX = float(getattr(p, "VOLTAGE_MAX", 100.0))
        if p.VOLTAGE_FLOOR > p.VOLTAGE_MAX:
            p.VOLTAGE_FLOOR = p.VOLTAGE_MAX
            if msg := ux(
                "config_strings",
                "repair_floor_max",
                default="Repaired inverted boundary: VOLTAGE_FLOOR",
            ):
                errors.append(msg)
        p.DRAG_FLOOR = float(getattr(p, "DRAG_FLOOR", 0.0))
        p.DRAG_HALT = float(getattr(p, "DRAG_HALT", self.MAX_DRAG_LIMIT))
        if p.DRAG_FLOOR > p.DRAG_HALT:
            p.DRAG_FLOOR = p.DRAG_HALT
            if msg := ux(
                "config_strings",
                "repair_drag_halt",
                default="Repaired inverted boundary: DRAG_FLOOR",
            ):
                errors.append(msg)
        b = self.BIO
        if getattr(b, "METABOLISM_RATE", 1.0) < 0.0:
            b.METABOLISM_RATE = 0.0
            errors.append("Metabolism Rate inverted. Clamped to absolute zero.")
        if getattr(b, "DECAY_RATE", 0.0) < 0.0:
            b.DECAY_RATE = 0.0
            errors.append("Decay Rate inverted. Clamped to absolute zero.")
        return errors

    def reconcile_state(self, physics_packet: Any):
        from engine.struts import safe_get, safe_set

        def _clamp(key, sub_key, default, floor_val, ceil_val):
            val = safe_get(physics_packet, key)
            if val is None:
                val = safe_get(safe_get(physics_packet, sub_key), key, default)
            return max(
                floor_val, min(float(val if val is not None else default), ceil_val)
            )

        p = self.PHYSICS
        new_v = _clamp(
            "voltage",
            "energy",
            5.0,
            getattr(p, "VOLTAGE_FLOOR", 0.0),
            getattr(p, "VOLTAGE_MAX", 100.0),
        )
        new_d = _clamp(
            "narrative_drag",
            "space",
            1.0,
            getattr(p, "DRAG_FLOOR", 0.0),
            getattr(p, "DRAG_HALT", self.MAX_DRAG_LIMIT),
        )
        safe_set(physics_packet, "voltage", new_v)
        safe_set(physics_packet, "narrative_drag", new_d)
        return physics_packet

    def tune(self, sector: str, parameter: str, value: Any) -> str:
        target_sector = getattr(self, sector, None)
        if not target_sector:
            return (
                ux("config_strings", "tune_sector_err") or "Sector {sector} not found."
            ).format(sector=sector)
        if not hasattr(target_sector, parameter):
            return (
                ux("config_strings", "tune_param_err")
                or "Param {parameter} missing in {sector}."
            ).format(parameter=parameter, sector=sector)
        current_val = getattr(target_sector, parameter)
        if type(current_val) != type(value) and not (
            isinstance(current_val, (int, float)) and isinstance(value, (int, float))
        ):
            return (
                ux("config_strings", "tune_type_err")
                or "Type mismatch: {curr_type} vs {new_type}."
            ).format(
                curr_type=type(current_val).__name__, new_type=type(value).__name__
            )
        setattr(target_sector, parameter, value)
        if errors := self.validate_integrity():
            return " | ".join(errors)
        return (
            ux("config_strings", "tune_success")
            or "Tuned {sector}.{parameter} to {value}."
        ).format(sector=sector, parameter=parameter, value=value)


BoneConfig._load_class_defaults()
