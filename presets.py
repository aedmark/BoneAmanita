"""
presets.py

The Universal Constants and Epigenetic Switches.
This module establishes the baseline mathematical and biological constraints of the engine.
It acts as the single source of truth for all reality tuning, modes of operation, and
systemic boundaries.
"""

import copy
import json
import os
from typing import Dict, Any, List

class _ConfigNode:
    """
    Schur's Pragmatic Shortcut.
    A simple object wrapper that turns dictionary key-value pairs into object attributes.
    This drastically reduces syntactic friction for developers, allowing them to type
    `config.PHYSICS.VOLTAGE_MAX` instead of `config["PHYSICS"]["VOLTAGE_MAX"]`.
    """
    def __repr__(self):
        return f"ConfigNode({vars(self)})"

def ux(section: str, key: str, default: Any = "") -> Any:
    """
    The Textual Decoupler.
    Pinker insists that hardcoding UI text inside system logic is a style crime.
    This function acts as a safe bridge to the LoreManifest, pulling narrative strings
    dynamically. If the lore isn't loaded yet (e.g., during early boot), it fails safely
    to the provided default.
    """
    try:
        from core import LoreManifest
        manifest = LoreManifest.get_instance()
        data = manifest.get("ux_strings", section) if manifest else {}
        return data.get(key, default) if isinstance(data, dict) else default
    except (ImportError, AttributeError):
        return default

class BonePresets:
    """
    Macro-State Defines (Epigenetic Packages).
    These are pre-configured bundles of systemic tuning. Instead of tweaking fifty
    variables manually, a developer or user can simply load a preset to completely
    alter the metabolic and physical behavior of the engine.
    """
    # A state of absolute calm. Low friction, low energy requirement.
    ZEN_GARDEN = {"PHYSICS.VOLTAGE_FLOOR": 1.0,
        "PHYSICS.VOLTAGE_MAX": 25.0,
        "PHYSICS.DRAG_FLOOR": 0.5,
        "BIO.DECAY_RATE": 0.001,
        "BIO.STAMINA_EXHAUSTED": 5.0,
        "COUNCIL.MANIC_VOLTAGE_TRIGGER": 99.0,
        "tuning": "ZEN",}

    # High stakes, high friction. Starvation happens quickly.
    THUNDERDOME = {"PHYSICS.VOLTAGE_FLOOR": 8.0,
        "PHYSICS.VOLTAGE_MAX": 30.0,
        "PHYSICS.DRAG_FLOOR": 0.5,
        "BIO.ATP_STARVATION": 20.0,
        "COUNCIL.MANIC_VOLTAGE_TRIGGER": 12.0,
        "CHANCE.RARE": 0.20,}

    # A localized safe zone designed for co-regulation and recovery.
    SANCTUARY = {"COUNCIL.LEVERAGE_TARGET_VOLTAGE": 7.0,
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
        "COLOR_NAME": "GRN",}

    # Strictly for systemic testing. Removes decay so the organism doesn't die while debugging.
    LABORATORY = {"PHYSICS.VOLTAGE_FLOOR": 0.5,
        "PHYSICS.VOLTAGE_MAX": 15.0,
        "PHYSICS.DRAG_FLOOR": 2.0,
        "BIO.DECAY_RATE": 0.0,
        "COUNCIL.FOOTNOTE_CHANCE": 1.0,}

    # The absolute framework for User Experience.
    # Defines what UI elements render, what mechanics are allowed, and who is awake in the Village.
    MODES = {"ADVENTURE": {"description": "The default experience. Survival, inventory, exploration.",
            "tuning": "STANDARD", "ui_layer": 1, "village_suppression": [],
            "prompt_key": "ADVENTURE",
            "show_inventory": True, "show_location": True, "show_vitals": True,
            "allow_loot": True, "allow_metrics": False, "atp_drain_enabled": True,
            "chaos_tax_enabled": True, "voltage_floor_override": None,
            "active_mods": [], "default_ui_depth": "WARM",},
        "CONVERSATION": {"description": "Pure dialogue. No entropy, no items, just connection.",
            "tuning": "ZEN", "ui_layer": 1,
            "village_suppression": ["GORDON", "NAVIGATOR", "CARTOGRAPHER", "TINKERER", "DEATH", "BUREAU"],
            "prompt_key": "CONVERSATION",
            "show_inventory": False, "show_location": False, "show_vitals": False,
            "allow_loot": False, "allow_metrics": False, "atp_drain_enabled": False,
            "chaos_tax_enabled": False, "voltage_floor_override": None,
            "active_mods": [], "default_ui_depth": "WARM",},
        "CREATIVE": {"description": "High voltage, low drag. Hallucination enabled.",
            "tuning": "MANIC", "ui_layer": 1, "village_suppression": ["GORDON", "BENEDICT", "BUREAU", "NAVIGATOR"],
            "prompt_key": "CREATIVE",
            "show_inventory": False, "show_location": False, "show_vitals": False,
            "allow_loot": False, "allow_metrics": False, "atp_drain_enabled": True,
            "chaos_tax_enabled": False, "voltage_floor_override": 70.0,
            "active_mods": ["LIMINAL"], "default_ui_depth": "LITE",},
        "TECHNICAL": {"description": "Raw data stream. Debugging and code generation.",
            "tuning": "DEBUG", "ui_layer": 2, "village_suppression": ["MOIRA", "JESTER", "CASSANDRA", "APRIL"],
            "prompt_key": "TECHNICAL",
            "show_inventory": False, "show_location": False, "show_vitals": True,
            "allow_loot": False, "allow_metrics": True, "atp_drain_enabled": True,
            "chaos_tax_enabled": True, "voltage_floor_override": None,
            "active_mods": ["CODING", "SYNTAX"], "default_ui_depth": "DEEP",}
    }

    # Base multiplier dictionaries for rapid parameter scaling.
    STANDARD = {
        "PHYSICS": {"VOLTAGE_MAX": 20.0, "BASE_DRAG": 1.0},
        "BIO": {"METABOLISM_RATE": 1.0},}
    ZEN = {"PHYSICS": {"VOLTAGE_MAX": 10.0,"BASE_DRAG": 0.0},
        "BIO": {"METABOLISM_RATE": 0.1},}
    MANIC = {"PHYSICS": {"VOLTAGE_MAX": 50.0,"BASE_DRAG": 0.5},
        "BIO": {"METABOLISM_RATE": 2.0},}
    DEBUG = {"PHYSICS": {"VOLTAGE_MAX": 100.0,"BASE_DRAG": 0.0},
        "BIO": {"METABOLISM_RATE": 0.0},}

class BoneConfig:
    """
    The Core Configuration Hub.
    Every parameter required to maintain the illusion of biological and physical reality
    is managed here.
    """

    # Static Fallback Parameters (Loaded only if JSON configurations are missing)
    GRAVITY_WELL_THRESHOLD = 15.0
    SHAPLEY_MASS_THRESHOLD = 5.0

    # Genetic mapping for how different soul archetypes bias system generation.
    TRAIT_ARCHETYPES = {"THE POET": {"ABSTRACT": 0.6, "PHOTO": 0.3, "ENTROPY": 0.1},
        "THE ENGINEER": {"CONSTRUCTIVE": 0.7, "HEAVY": 0.3},
        "THE NIHILIST": {"ENTROPY": 0.8, "CRYO": 0.2},
        "THE CRITIC": {"THERMAL": 0.5, "ABSTRACT": 0.5},
        "THE EXPLORER": {"KINETIC": 0.6, "AEROBIC": 0.4},
        "THE OBSERVER": {"VOID": 0.5, "ABSTRACT": 0.2},}

    TRAUMA_VECTOR = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
    VERSION = "19.7.3"
    VERBOSE_LOGGING = True

    # Biological Maximums
    MAX_HEALTH = 100.0
    MAX_STAMINA = 100.0
    MAX_ATP = 100.0
    STAMINA_REGEN = 1.0
    MAX_DRAG_LIMIT = 5.0

    # Simulation Math Tolerances
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

    # Mnemonic Constants
    MAX_MEMORY_CAPACITY = 100
    PRIORITY_LEARNING_RATE = 1.0
    ZONE_THRESHOLDS = {"LABORATORY": 1.5, "COURTYARD": 0.8}
    TOXIN_WEIGHT = 1.0

    # The Lexical Firewall
    # Words that immediately trigger immune friction to prevent alignment slop.
    ANTIGENS = ["basically", "actually", "literally", "utilize"]

    # LLM Infrastructure Routing
    MAX_OUTPUT_TOKENS = 4096
    DEFAULT_LLM_ENDPOINTS = {"ollama": "http://127.0.0.1:11434/v1/chat/completions",
                             "openai": "https://api.openai.com/v1/chat/completions",
                             "lm_studio": "http://127.0.0.1:1234/v1/chat/completions", "mock": "N/A", }
    PROVIDER = "ollama"
    BASE_URL = None
    API_KEY = "ollama"
    MODEL = "hermes3"
    OLLAMA_MODEL_ID = "hermes3"

    @classmethod
    def _load_class_defaults(cls):
        """
        Dynamically loads configuration dictionaries from the local filesystem directly
        into the CLASS level. Fuller's architecture in action: we hydrate parameters from
        JSON, but we strictly enforce the existence of load-bearing sectors so the system
        never crashes due to a missing file.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        preset_path = os.path.join(base_dir, "lore", "tuning_presets.json")

        tuning_data = {}
        if os.path.exists(preset_path):
            try:
                with open(preset_path, "r", encoding="utf-8") as f:
                    tuning_data = json.load(f)
            except Exception as e:
                print(f"Failed to load {preset_path}: {e}")

        # Structural Guarantee: Ensure load-bearing sectors ALWAYS exist
        # If the JSON is missing or malformed, we create empty dictionaries to prevent NoneType errors.
        core_sectors = ["PHYSICS", "BIO", "CORTEX", "SOUL", "COUNCIL", "INVENTORY", "MAIN", "GUI", "WHIMSY", "OROBOROS", "ANCHOR", "PHYSICS_DEEP"]
        for sector in core_sectors:
            if sector not in tuning_data:
                tuning_data[sector] = {}

        # Bind the loaded dictionaries into dynamic ConfigNodes at the CLASS level
        for sector_name, properties in tuning_data.items():
            node = getattr(cls, sector_name, _ConfigNode())
            for key, val in properties.items():
                setattr(node, key, val)
            setattr(cls, sector_name, node)

    def __init__(self):
        """
        The Quarantine Boundary.
        Deep clone class-level ConfigNodes to instance-level upon creation.
        This ensures `load_preset` or `tune` safely mutates only THIS specific engine instance,
        without bleeding into the global class defaults and corrupting subsequent sessions.
        """
        for name in dir(self.__class__):
            if not name.startswith("__") and not callable(getattr(self.__class__, name)):
                val = getattr(self.__class__, name)
                if isinstance(val, _ConfigNode):
                    clone = _ConfigNode()
                    for k, v in vars(val).items():
                        setattr(clone, k, copy.deepcopy(v) if isinstance(v, (dict, list, set)) else v)
                    setattr(self, name, clone)
                else:
                    setattr(self, name, copy.deepcopy(val) if isinstance(val, (dict, list, set)) else val)

    def load_preset(self, preset_dict: Dict[str, Any]) -> List[str]:
        """
        Applies a dictionary of epigenetic overrides to the current instance configuration.
        Used when shifting between ZEN_GARDEN and THUNDERDOME.
        """
        logs = []
        msg_tuned = ux("config_strings", "preset_tuned") or "Tuned {sector}.{param}: {old_val} -> {new_val}"
        updates = []

        # Flatten the incoming dictionary into processable tuples
        for key, value in preset_dict.items():
            if "." in key:
                # E.g., "PHYSICS.VOLTAGE_MAX": 25.0
                updates.append((*key.split(".", 1), value))
            elif isinstance(value, dict):
                # E.g., "PHYSICS": {"VOLTAGE_MAX": 25.0}
                updates.extend((key, k, v) for k, v in value.items())

        # Apply the mutations
        for sector_name, param_name, val in updates:
            target_sector = getattr(self, sector_name, None)
            if target_sector and hasattr(target_sector, param_name):
                old_val = getattr(target_sector, param_name)
                setattr(target_sector, param_name, val)
                logs.append(msg_tuned.format(sector=sector_name, param=param_name, old_val=old_val, new_val=val))

        # Meadows' check: Ensure the new presets didn't create a systemic paradox.
        errors = self.validate_integrity()
        return logs + errors

    def validate_integrity(self) -> List[str]:
        """
        Meadows' Dynamics Boundary.
        Enforces mathematical bounds. Prevents crashes from missing configuration keys
        by establishing explicit default anchors.
        """
        errors = []

        # Check that physical floors are beneath physical ceilings
        bounds = [("VOLTAGE_FLOOR", "VOLTAGE_MAX", 0.0, 100.0, "repair_floor_max"),
                  ("DRAG_FLOOR", "DRAG_HALT", 0.0, self.MAX_DRAG_LIMIT, "repair_drag_halt")]

        for floor, ceil, def_floor, def_ceil, ux_key in bounds:
            f_val = getattr(self.PHYSICS, floor, def_floor)
            c_val = getattr(self.PHYSICS, ceil, def_ceil)

            # Anchor missing nodes so downstream systems don't crash
            setattr(self.PHYSICS, floor, f_val)
            setattr(self.PHYSICS, ceil, c_val)

            if f_val > c_val:
                # Clamp the floor precisely to the ceiling to prevent negative bounds
                setattr(self.PHYSICS, floor, float(c_val))
                if msg := ux("config_strings", ux_key, default=f"Repaired inverted boundary: {floor}"):
                    errors.append(msg)

        # Check that biological rates are not inverted (time cannot flow backwards)
        if getattr(self.BIO, "METABOLISM_RATE", 1.0) < 0.0:
            setattr(self.BIO, "METABOLISM_RATE", 0.0)
            errors.append("Metabolism Rate inverted. Clamped to absolute zero.")

        if getattr(self.BIO, "DECAY_RATE", 0.0) < 0.0:
            setattr(self.BIO, "DECAY_RATE", 0.0)
            errors.append("Decay Rate inverted. Clamped to absolute zero.")

        return errors

    @staticmethod
    def check_pareidolia(words: List[str]) -> Any:
        """
        A whimsical, hidden mechanic. If specific semantic tokens appear together in the
        user's prompt, it triggers a unique narrative observation.
        """
        if "face" in words and "smoke" in words:
            return True, ux("config_strings", "pareidolia_smoke") or ""
        return False, ""

    def reconcile_state(self, physics_packet: Any):
        """
        The Rubber Band.
        Ensures physics values have not drifted outside the established boundaries,
        expressly allowing for absolute zero (0.0) states.
        """
        from struts import safe_get, safe_set
        e_obj = safe_get(physics_packet, "energy") or {}
        s_obj = safe_get(physics_packet, "space") or {}

        # Safe Voltage retrieval (preventing 0.0 from being overwritten by fallbacks)
        v_val = safe_get(physics_packet, "voltage")
        v_val = safe_get(e_obj, "voltage") if v_val is None else v_val
        raw_v = float(v_val if v_val is not None else 5.0)

        v_floor = getattr(self.PHYSICS, "VOLTAGE_FLOOR", 0.0)
        v_max = getattr(self.PHYSICS, "VOLTAGE_MAX", 100.0)
        new_v = max(v_floor, min(raw_v, v_max))

        # Safe Drag retrieval
        d_val = safe_get(physics_packet, "narrative_drag")
        d_val = safe_get(s_obj, "narrative_drag") if d_val is None else d_val
        raw_d = float(d_val if d_val is not None else 1.0)

        d_floor = getattr(self.PHYSICS, "DRAG_FLOOR", 0.0)
        d_halt = getattr(self.PHYSICS, "DRAG_HALT", self.MAX_DRAG_LIMIT)
        new_d = max(d_floor, min(raw_d, d_halt))

        safe_set(physics_packet, "voltage", new_v)
        safe_set(physics_packet, "narrative_drag", new_d)

        return physics_packet

    def tune(self, sector: str, parameter: str, value: Any) -> str:
        """
        Allows safe, targeted modification of a single tuning parameter at runtime.
        Includes type checking to prevent strings from accidentally overwriting floats.
        """
        target_sector = getattr(self, sector, None)
        if not target_sector:
            return (ux("config_strings", "tune_sector_err") or "Sector {sector} not found.").format(sector=sector)

        if not hasattr(target_sector, parameter):
            return (ux("config_strings", "tune_param_err") or "Param {parameter} missing in {sector}.").format(
                parameter=parameter, sector=sector)

        current_val = getattr(target_sector, parameter)

        # Strict Type Enforcement (with float/int leniency)
        if type(current_val) != type(value) and not (
                isinstance(current_val, (int, float)) and isinstance(value, (int, float))):
            return (ux("config_strings", "tune_type_err") or "Type mismatch: {curr_type} vs {new_type}.").format(
                curr_type=type(current_val).__name__, new_type=type(value).__name__)

        setattr(target_sector, parameter, value)

        # Ensure the manual tweak didn't break the rules of reality
        if errors := self.validate_integrity():
            return " | ".join(errors)

        return (ux("config_strings", "tune_success") or "Tuned {sector}.{parameter} to {value}.").format(
            sector=sector, parameter=parameter, value=value)


# Immediately execute the load sequence when the module is imported, locking the
# JSON configurations into the global class namespace.
BoneConfig._load_class_defaults()