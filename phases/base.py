"""phases/base.py"""

from abc import ABC, abstractmethod
from typing import Tuple

from core import CycleContext


def _safe_dict(obj):
    return (
        obj.to_dict()
        if hasattr(obj, "to_dict")
        else (obj if isinstance(obj, dict) else {})
    )


def _deep_update(target_object, source_dict):
    for key, value in source_dict.items():
        is_dict = isinstance(target_object, dict)
        nested_target = (
            target_object.get(key) if is_dict else getattr(target_object, key, None)
        )
        if isinstance(value, dict) and nested_target is not None:
            _deep_update(nested_target, value)
        else:
            if is_dict:
                target_object[key] = value
            else:
                setattr(target_object, key, value)


class SimulationPhase(ABC):
    """Contract for all cycle phases."""

    required_context: Tuple[str, ...] = ()

    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.name = "GENERIC_PHASE"

    @abstractmethod
    def run(self, ctx: CycleContext) -> CycleContext:
        """Execute the phase logic. Must be implemented by subclasses."""
        pass

    def validate_context(self, ctx: CycleContext) -> bool:
        """
        Fail-fast intercept.
        Call this at the beginning of a subclass run() method to catch missing requirements
        before they cost ATP or mutate the active physics state.
        """
        for attr in self.required_context:
            if getattr(ctx, attr, None) is None:
                raise ValueError(
                    f"[{self.name}] Pre-flight abort: Required CycleContext attribute '{attr}' is missing or None."
                )
        return True
