"""presets.py"""

import copy
import json
import os
from types import SimpleNamespace
from typing import Any, Dict, List

from struts import ux


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
    MODEL = "mistral-nemo"
    OLLAMA_FALLBACK = ""
    _TEMPLATE_DATA = {}

    @classmethod
    def _load_class_defaults(cls):
        base_dir = str(os.path.dirname(os.path.abspath(__file__)))
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
        from struts import safe_get, safe_set

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
