""" dev/bone_machine.py - 'The gears turn, the pistons fire.' """

import random
from typing import Tuple, Optional
from bone_core import Prisma, TheLore
from bone_lexicon import TheLexicon

class TheCrucible:
    def __init__(self):
        self.max_voltage_cap = 20.0
        self.active_state = "COLD"
        self.dampener_charges = 3
        self.dampener_tolerance = 15.0
        self.instability_index = 0.0

    def dampener_status(self):
        return f"🛡️ Charges: {self.dampener_charges}"

    def dampen(self, voltage_spike, stability_index):
        if self.dampener_charges <= 0:
            return False, "⚠️ DAMPER EMPTY", 0.0
        should_dampen = False
        reduction_factor = 0.0
        reason = ""
        if voltage_spike > self.dampener_tolerance:
            should_dampen = True
            reduction_factor = 0.7
            reason = "Circuit Breaker"
        elif voltage_spike > 8.0 and stability_index < 0.3:
            should_dampen = True
            reduction_factor = 0.4
            reason = "Instability"
        if should_dampen:
            self.dampener_charges -= 1
            reduction = voltage_spike * reduction_factor
            msg = f"🛡️ DAMPENER: -{reduction:.1f}v ({reason})"
            return True, msg, reduction
        return False, "Holding Charge", 0.0

    def audit_fire(self, physics):
        voltage = physics.get("voltage", 0.0)
        structure = physics.get("kappa", 0.0)
        ideal_voltage = structure * 20.0
        delta = voltage - ideal_voltage
        self.instability_index = (self.instability_index * 0.7) + (delta * 0.3)
        current_drag = physics.get("narrative_drag", 0.0)
        adjustment = self.instability_index * 0.5
        if current_drag < 1.0 and adjustment > 0:
            adjustment *= 0.1
        new_drag = max(0.0, min(10.0, current_drag + adjustment))
        physics["narrative_drag"] = round(new_drag, 2)
        msg = None
        if abs(adjustment) > 0.5:
            direction = "TIGHTENING" if adjustment > 0 else "RELAXING"
            msg = f"⚖️ REGULATOR: {direction} (Drag {current_drag:.1f} -> {new_drag:.1f})"
        if physics.get("system_surge_event", False):
            self.active_state = "SURGE"
            return "SURGE", 0.0, f"⚡ SURGE: Absorbed {voltage}v."
        if voltage > 18.0:
            if structure > 0.5:
                gain = voltage * 0.1
                self.max_voltage_cap += gain
                self.active_state = "RITUAL"
                return "RITUAL", gain, f"🔥 RITUAL: Capacity +{gain:.1f}v"
            else:
                damage = voltage * 0.5
                self.active_state = "MELTDOWN"
                return "MELTDOWN", damage, f"💥 MELTDOWN: Hull Breach (-{damage:.1f} HP)"
        self.active_state = "REGULATED"
        return "REGULATED", 0.0, msg

class TheForge:
    def __init__(self):
        gordon_data = TheLore.get("gordon") or {}
        self.recipes = gordon_data.get("RECIPES", [])

    @staticmethod
    def hammer_alloy(physics):
        voltage = physics.get("voltage", 0)
        clean_words = physics.get("clean_words", [])
        counts = physics.get("counts", {})
        total_mass = (counts.get("heavy", 0) * 2.0) + (counts.get("kinetic", 0) * 0.5)
        avg_density = total_mass / max(1, len(clean_words))
        forge_probability = (voltage / 20.0) * avg_density
        if random.random() < forge_probability:
            if counts.get("heavy", 0) > 3:
                return True, f"🔨 FORGED: Lead Boots (Mass {avg_density:.1f})", "LEAD_BOOTS"
            if counts.get("kinetic", 0) > 3:
                return True, f"🔨 FORGED: Safety Scissors (Kinetic)", "SAFETY_SCISSORS"
            return True, f"🔨 FORGED: Anchor Stone", "ANCHOR_STONE"
        return False, None, None

    def attempt_crafting(self, physics, inventory_list) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        clean = physics.get("clean_words", [])
        voltage = physics.get("voltage", 0)
        for recipe in self.recipes:
            ingredient = recipe["ingredient"]
            if ingredient in inventory_list:
                catalyst_cat = recipe["catalyst_category"]
                catalyst_hits = [w for w in clean if w in TheLexicon.get(catalyst_cat)]
                if catalyst_hits:
                    entanglement = self._calculate_entanglement(len(catalyst_hits), voltage)
                    if random.random() < entanglement:
                        return (
                            True,
                            f"⚗️ ALCHEMY: {recipe['result']} (via {ingredient})",
                            ingredient,
                            recipe["result"])
                    else:
                        return False, f"⚠️ ALCHEMY FAIL: Decoherence ({int(entanglement*100)}%)", None, None
        return False, None, None, None

    @staticmethod
    def _calculate_entanglement(hit_count, voltage):
        return min(1.0, 0.2 + (hit_count * 0.1) + (voltage / 133.0))

    @staticmethod
    def transmute(physics):
        counts = physics.get("counts", {})
        voltage = physics.get("voltage", 0)
        gamma = physics.get("gamma", 0.0)
        if gamma < 0.15 and counts.get("abstract", 0) > 1:
            return f"⚠️ EMULSION FAIL: Add Binder (Heavy)."
        if voltage > 15.0:
            return f"🌡️ OVERHEAT: {voltage:.1f}v. Add Coolant (Aerobic)."
        return None

class TheTheremin:
    def __init__(self):
        self.decoherence_buildup = 0.0
        self.classical_turns = 0
        self.AMBER_THRESHOLD = 20.0
        self.SHATTER_POINT = 100.0
        self.is_stuck = False

    def listen(self, physics, governor_mode="COURTYARD"):
        counts = physics.get("counts", {})
        voltage = physics.get("voltage", 0.0)
        turb = physics.get("turbulence", 0.0)
        rep = physics.get("repetition", 0.0)
        complexity = physics.get("truth_ratio", 0.0)
        ancient_mass = counts.get("heavy", 0) + counts.get("thermal", 0) + counts.get("cryo", 0)
        modern_mass = counts.get("abstract", 0)
        raw_mix = min(ancient_mass, modern_mass)
        resin_flow = raw_mix * 2.0
        if governor_mode == "LABORATORY": resin_flow *= 0.5
        if voltage > 5.0: resin_flow = max(0.0, resin_flow - (voltage * 0.6))
        thermal_hits = counts.get("thermal", 0)
        if thermal_hits > 0 and self.decoherence_buildup > 5.0:
            dissolved = thermal_hits * 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - dissolved)
            self.classical_turns = 0
            return False, 0.0, f"🔥 MELT: -{dissolved:.1f} Resin", None
        theremin_msg = None
        critical_event = None
        if rep > 0.5:
            self.classical_turns += 1
            slag = self.classical_turns * 2.0
            self.decoherence_buildup += slag
            theremin_msg = f"🗿 CALCIFICATION: Turn {self.classical_turns} (+{slag} Resin)"
        elif complexity > 0.4 and self.classical_turns > 0:
            self.classical_turns = 0
            relief = 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - relief)
            theremin_msg = f"🔨 SHATTER: -{relief} Resin"
        elif resin_flow > 0.5:
            self.decoherence_buildup += resin_flow
            theremin_msg = f"🎻 RESIN: +{resin_flow:.1f}"
        if turb > 0.6 and self.decoherence_buildup > 0:
            shatter_amt = turb * 10.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - shatter_amt)
            theremin_msg = f"🌊 TURBULENCE: -{shatter_amt:.1f} Resin"
            self.classical_turns = 0
        if turb < 0.2:
            physics["narrative_drag"] = max(0.0, physics["narrative_drag"] - 1.0)
        if self.decoherence_buildup > self.SHATTER_POINT:
            self.decoherence_buildup = 0.0
            self.classical_turns = 0
            return False, resin_flow, f"💣 COLLAPSE: AIRSTRIKE INITIATED", "AIRSTRIKE"
        if self.classical_turns > 3:
            critical_event = "CORROSION"
            theremin_msg = f"{theremin_msg} | ⚠️ CORROSION"
        if self.decoherence_buildup > self.AMBER_THRESHOLD:
            self.is_stuck = True
            theremin_msg = f"{theremin_msg} | 🍯 STUCK"
        if self.is_stuck and self.decoherence_buildup < 5.0:
            self.is_stuck = False
            theremin_msg = f"{theremin_msg} | 🦋 FREE"
        return self.is_stuck, resin_flow, theremin_msg, critical_event

    def get_readout(self):
        status = "STUCK" if self.is_stuck else "FLOW"
        return f"🎻 THEREMIN   Resin {self.decoherence_buildup:.1f}  Status {status}"