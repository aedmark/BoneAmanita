"""phases/base.py"""

from core import CycleContext

def _safe_dict(obj):
    return obj.to_dict() if hasattr(
        obj, "to_dict") else (obj if isinstance(obj, dict) else {})

def _deep_update(target_object, source_dict):
    for key, value in source_dict.items():
        nested_target = target_object.get(key) if isinstance(target_object, dict) else getattr(target_object, key, None)
        is_valid_nesting = isinstance(value, dict) and nested_target is not None and (
                isinstance(nested_target, dict) or hasattr(nested_target, "__dict__"))
        if is_valid_nesting:
            _deep_update(nested_target, value)
        else:
            if isinstance(target_object, dict):
                target_object[key] = value
            else:
                setattr(target_object, key, value)

class SimulationPhase:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.name = "GENERIC_PHASE"

    def run(self, ctx: CycleContext) -> CycleContext:
        raise NotImplementedError
