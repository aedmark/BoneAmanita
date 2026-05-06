"""phases/base.py"""
from core import CycleContext


def _safe_dict(obj):
    """
    Safely coerces an arbitrary object into a dictionary representation.
    This acts as a structural fail-safe before state merges. It attempts to call
    a native 'to_dict()' method if it exists. If the object is already a dictionary,
    it returns it directly. If it is neither, it defaults to an empty dictionary,
    preventing type-error cascade failures in downstream processing.
    """
    return obj.to_dict() if hasattr(
        obj, "to_dict") else (obj if isinstance(obj, dict) else {})


def _deep_update(target_object, source_dict):
    """
    Recursively mutates a target object or dictionary with values from a source dictionary.
    This is a critical state transition mechanism. It navigates the nested tensegrity
    of the object structure, ensuring that nested dictionaries or sub-objects are updated
    in place rather than overwritten wholesale.
    Constraints:
    - It dynamically handles both standard Python dictionaries and custom class objects.
    - It applies recursive depth natively, drilling down until it hits primitive values.
    """
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
    """
    The abstract base class for all operational phases within the simulation cycle.
    This defines the structural contract that all specialized phases (e.g., biological,
    mechanical, cognitive) must fulfill. It binds the phase to the master engine and
    enforces the implementation of the 'run' method.
    """

    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.name = "GENERIC_PHASE"

    def run(self, ctx: CycleContext) -> CycleContext:
        """
        The execution loop for the phase.
        Takes the current CycleContext, processes it through the phase's specific
        logic gates, and returns the mutated CycleContext.
        Must be implemented by subclasses. If a subclass fails to define its run
        mechanic, the architecture intentionally fractures and throws a NotImplementedError.
        """
        raise NotImplementedError
