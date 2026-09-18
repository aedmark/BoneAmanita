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
            # The refusal gates were sized for ADVENTURE, where high drag means a
            # story coming apart. In conversation they read a person going terse:
            # over 30 census turns the PINKER sum averaged 44 against a gate of
            # 35, and voltage averaged 21.7 against a MELTDOWN at 18. Both sat
            # below the mean of an ordinary conversation. 1.6 puts them above it
            # and still refuses the genuine extremes (PINKER peaked at 62.5).
            # ROADMAP D0b.
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
    MODEL = "gemma4:e4b"
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

    # The engine's model of the PERSON (ROADMAP C3). Two separate signals, and
    # keeping them separate is the point.
    #
    # P_u is EFFORT SPENT. It drains with how much you write and recovers when
    # you rest. Low P_u is what triggers the engine to carry some of the load
    # for you, so writing a lot should lower it: that is the supportive path,
    # not a penalty.
    #
    # E_u is DISENGAGEMENT. It rises when your messages get short, blunt or
    # repetitive RELATIVE TO YOUR OWN BASELINE, and falls when you write at
    # length. It is what shortens the engine's replies to match you.
    #
    # These used to be one signal: E_u rose only when P_u fell below a floor,
    # which meant writing long searching prose was what made the engine read you
    # as exhausted and start cutting its answers to three sentences. That is
    # backwards. Someone working hard on something difficult is the person this
    # engine exists for, and terse "ok, sure, fine" restored them to full.
    USER = {
        # Ceiling for P_u. Modulated per turn; see STAMINA_* below.
        "STAMINA_MAX": 100.0,
        # Extra headroom at full shared resonance. A conversation that is
        # landing costs you less than one that is not.
        "STAMINA_RESONANCE_HEADROOM": 25.0,
        # Headroom lost per unit of accumulated user trauma (T_u).
        "STAMINA_TRAUMA_COST": 4.0,
        # The ceiling never falls below this fraction of STAMINA_MAX, however
        # heavy the conversation gets.
        "STAMINA_FLOOR_FRACTION": 0.5,
        # Stamina returned per turn, before the per-word cost.
        "STAMINA_RECOVERY": 5.0,
        "STAMINA_WORD_COST": 0.5,
        # How many recent messages define "your normal length".
        "BASELINE_WINDOW": 8,
        # A message shorter than this fraction of your baseline starts reading
        # as disengagement. 0.5 means "half your usual length".
        "BREVITY_FLOOR": 0.5,
        # How fast E_u moves toward the disengagement reading, per turn.
        "DISENGAGEMENT_RATE": 0.15,
        "REENGAGEMENT_RATE": 0.10,
    }

    # The Stage Manager (ROADMAP C4). More than one voice triggered at once is
    # Tension; the Stage Manager negotiates it before anyone speaks, and
    # unresolved Tension becomes Silence.
    #
    # On Silence and the metabolism, which the roadmap asked be decided rather
    # than guessed: a held turn makes NO model call, so it spends no generation
    # energy. That is the honest account, you did not speak. It is not free
    # either: negotiating costs SILENCE_COST, so declining is a choice with a
    # price rather than the cheapest path. MAX_CONSECUTIVE_HOLDS is the guard
    # that matters most, because an engine that can always decline eventually
    # always will.
    STAGE = {
        # Voices at once beyond the first before an unfused tension is held.
        # 3 means four voices talking with no pairing between them.
        "TENSION_HOLD_MAGNITUDE": 3,
        # Below this ATP the engine holds rather than blending conflicting
        # voices into something smooth and false.
        "SYNTHESIS_ATP_FLOOR": 25.0,
        # After this many held turns the first voice takes the floor regardless.
        "MAX_CONSECUTIVE_HOLDS": 2,
        # What negotiating a silence costs. Small, but not nothing.
        "SILENCE_COST": 2.0,
    }

    # The governor's regime gate, read off the ordvec sign bitmap.
    #
    # This replaced a graph Laplacian and a Picard solve, on Nelson Spence's
    # recommendation and our own measurement. Instrumented on a 23-node subgraph
    # seeded at 17% edge density (denser than a real session), the Laplacian
    # contributed 1.53% of the reported eigenvalue and the voltage input
    # contributed nothing at all: lambda_1 came back byte-identical at every
    # voltage from 15 to 90. What was left after the graph and the voltage
    # cancelled was the mean ordvec similarity, computed the expensive way.
    #
    # `z_top10` is how far the utterance's neighbourhood stands above the
    # corpus null, in standard deviations of the sign-agreement distribution.
    # For a 768-dim sign bitmap chance sits near 384 agreements with a spread
    # near 14, so the scale is stable and reads the same across corpora.
    GATE = {
        # How far above the NULL a neighbourhood has to stand before it counts
        # as coherent: opens heat and selects CO_REGULATION. This is an excess,
        # not a raw z. The top-10 mean of n samples drifts upward with n for no
        # reason but order statistics (1.13 sigma at n=32, 3.55 at n=20000), so
        # a threshold on raw z would fall open as the memory grew. Calibrate
        # this the way LAMBDA was calibrated, by sweeping it against how often
        # the engine lands in the generative regime.
        "Z_PIVOT": 0.5,
        # Temperature when the gate opens, and how fast it climbs per z above
        # the pivot.
        "T_OPEN_BASE": 0.7,
        "T_GAIN": 0.15,
        "T_MAX": 1.2,
        # Below the pivot generation collapses to deterministic logic, which is
        # what the eigenvalue sign used to decide.
        "T_LOCKED": 0.0,
        # Fewer memories than this and we decline to emit a number at all: the
        # mean and deviation are not meaningful yet. This is navi-fractal's own
        # rule (refuse to return a dimension the data will not support) applied
        # to the governor. A declined turn runs the default temperature and
        # files a receipt saying it was not measured.
        "MIN_CORPUS": 32,
        "TOP_K": 10,
    }

    # Creative Determinant coupling (Project Navi, Apache 2.0).
    # LAMBDA is the contradiction-cost weight in b = kappa*gamma - lambda*mu.
    # The resting state sits on the phase boundary b=0, so lambda = E[k*g]/E[m].
    # Under independent uniform inputs, E[k*g]/E[m] = 0.5.
    CD: Dict[str, Any] = {
        "LAMBDA": 1.0,
    }

    # The Mnemonic Arcade's coordinate system. BACKEND "auto" probes the HTTP
    # endpoint first, then a local sentence-transformers model, then falls back
    # to the legacy SHAKE-256 hash (which has no semantic signal and disables
    # associative recall). Env vars BONE_EMBED_* override these at boot.
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
