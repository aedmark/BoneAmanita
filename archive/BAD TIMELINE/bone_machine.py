""" bone_machine.py
 'The gears turn, the pistons fire.' - The Industrial District """

import random
from typing import Tuple, Optional
from bone_bus import Prisma
from bone_lexicon import TheLexicon
from dataclasses import dataclass

class TheCrucible:
    def __init__(self):
        self.max_voltage_cap = 20.0
        self.active_state = "COLD"
        self.dampener_charges = 3
        self.dampener_tolerance = 15.0
        self.instability_index = 0.0

    def dampener_status(self):
        return f"{self.dampener_charges} Charges Remaining"

    def dampen(self, voltage_spike, stability_index):
        if self.dampener_charges <= 0:
            return False, "The Damper is empty.", 0.0
        if voltage_spike > self.dampener_tolerance:
            self.dampener_charges -= 1
            reduction = voltage_spike * 0.7
            return True, f"CRUCIBLE DAMPENER: Circuit Breaker. Reduced {voltage_spike:.1f}v by {reduction:.1f}v.", reduction
        elif voltage_spike > 8.0 and stability_index < 0.3:
            self.dampener_charges -= 1
            reduction = voltage_spike * 0.4
            return True, f"CRUCIBLE DAMPENER: Instability detected. Dampening charge on unstable ground.", reduction
        return False, "Structure is holding the charge.", 0.0

    def audit_fire(self, physics):
        voltage = physics.get("voltage", 0.0)
        structure = physics.get("kappa", 0.0)
        quantum_stress = self._calculate_quantum_instability(voltage, structure)
        current_drag = physics.get("narrative_drag", 0.0)
        adjustment = quantum_stress * 0.5
        if current_drag < 1.0 and adjustment > 0:
            adjustment *= 0.1
        new_drag = max(0.0, min(10.0, current_drag + adjustment))
        physics["narrative_drag"] = round(new_drag, 2)
        msg = None
        if abs(adjustment) > 0.5:
            if adjustment > 0:
                action = "CRYSTALLIZING"
                desc = "Structure hardening to contain Voltage."
            else:
                action = "SUBLIMATING"
                desc = "Structure relaxing. Allowing expansion."
            msg = f"{Prisma.CYN}HOMEOSTASIS: {action} - {desc} (Drag {current_drag:.1f} -> {new_drag:.1f}).{Prisma.RST}"
        if physics.get("system_surge_event", False):
            self.active_state = "SURGE"
            return "SURGE", 0.0, f"{Prisma.CYN}CRUCIBLE: Absorbing System Surge ({voltage}v). No structural damage.{Prisma.RST}"
        if voltage > 18.0:
            if structure > 0.5:
                return self._sublimate(voltage)
            else:
                return self._meltdown(voltage)
        self.active_state = "REGULATED"
        return "REGULATED", 0.0, msg

    def _calculate_quantum_instability(self, voltage, kappa):
        ideal_voltage = kappa * 20.0
        delta = voltage - ideal_voltage
        self.instability_index = (self.instability_index * 0.7) + (delta * 0.3)
        return self.instability_index

    def _sublimate(self, voltage):
        self.active_state = "RITUAL"
        gain = voltage * 0.1
        self.max_voltage_cap += gain
        return "RITUAL", gain, f"CRUCIBLE RITUAL: Voltage ({voltage}v) contained. Capacity expanded to {self.max_voltage_cap:.1f}v."

    def _meltdown(self, voltage):
        self.active_state = "MELTDOWN"
        damage = voltage * 0.5
        return "MELTDOWN", damage, f"CRUCIBLE CRACKED: Fire lacks Structure (Kappa Low). Hull Breach. -{damage:.1f} Health."

class TheForge:
    def __init__(self):
        from bone_data import GORDON
        self.recipes = GORDON.get("RECIPES", [])
        self.PLANCK_CONSTANT = 0.1

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
                return True, f"{Prisma.OCHRE}THE ANVIL THUDS: You forged gravity itself.{Prisma.RST}", "LEAD_BOOTS"
            if counts.get("kinetic", 0) > 3:
                return True, f"{Prisma.CYN}THE ANVIL CLICKS: Cold steel, safe for children.{Prisma.RST}", "SAFETY_SCISSORS"
            return True, f"{Prisma.GRY}THE ANVIL RINGS: Mass condensed into form.{Prisma.RST}", "ANCHOR_STONE"
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
                            f"{Prisma.VIOLET}⚗️ ALCHEMY: '{catalyst_hits[0].upper()}' entangled with {ingredient}. {recipe['msg']}{Prisma.RST}",
                            ingredient,
                            recipe["result"])
                    else:
                        msg = (f"{Prisma.GRY}The {ingredient} vibrates near '{catalyst_hits[0]}', "
                               f"but decoherence occurs. (Entanglement: {int(entanglement*100)}%){Prisma.RST}")
                        return False, msg, None, None
        return False, None, None, None

    @staticmethod
    def _calculate_entanglement(hit_count, voltage):
        base_chance = 0.2
        count_bonus = min(0.5, hit_count * 0.1)
        energy_bonus = min(0.3, voltage / 40.0)
        return min(1.0, base_chance + count_bonus + energy_bonus)

    @staticmethod
    def transmute(physics):
        counts = physics.get("counts", {})
        voltage = physics.get("voltage", 0)
        gamma = physics.get("gamma", 0.0)
        if gamma < 0.15 and counts.get("abstract", 0) > 1:
            oil = TheLexicon.get_random("abstract")
            binder = TheLexicon.get_random("heavy")
            return (
                f"{Prisma.OCHRE}THE EMULSIFIER: The emulsion is breaking (Tension: {gamma:.2f}).{Prisma.RST}\n"
                f"   You are pouring Oil ('{oil}') into Water without a Binder.\n"
                f"   {Prisma.WHT}Try this: Use '{binder.upper()}' to suspend the concept.{Prisma.RST}")
        if voltage > 15.0:
            coolant = TheLexicon.get_random("aerobic")
            return (
                f"{Prisma.CYN}THERMAL SPIKE ({voltage:.1f}v). Structure is brittle.{Prisma.RST}\n"
                f"   Injecting Coolant: '{coolant}'. Breathe. Add space.")
        return None

class TheTheremin:
    def __init__(self):
        self.resonance_log = []
        self.decoherence_buildup = 0.0
        self.classical_turns = 0
        self.AMBER_THRESHOLD = 20.0
        self.SHATTER_POINT = 80.0
        self.is_stuck = False

    def listen(self, physics, governor_mode="COURTYARD"):
        clean = physics["clean_words"]
        voltage = physics.get("voltage", 0.0)
        ancient_mass = sum(1 for w in clean if w in TheLexicon.get("heavy") or w in TheLexicon.get("thermal") or w in TheLexicon.get("cryo"))
        modern_mass = sum(1 for w in clean if w in TheLexicon.get("abstract"))
        thermal_hits = sum(1 for w in clean if w in TheLexicon.get("thermal"))
        solvent_active = False
        solvent_msg = ""
        if thermal_hits > 0 and self.decoherence_buildup > 5.0:
            dissolved = thermal_hits * 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - dissolved)
            self.classical_turns = 0
            solvent_active = True
            solvent_msg = f"{Prisma.OCHRE}RE-COHERENCE: Thermal energy restored superposition (-{dissolved:.1f} Resin).{Prisma.RST}"
            if self.is_stuck and self.decoherence_buildup < self.AMBER_THRESHOLD:
                self.is_stuck = False
                solvent_msg += f" {Prisma.GRN}RELEASE: You burned your way out.{Prisma.RST}"
        raw_mix = min(ancient_mass, modern_mass)
        resin_flow = raw_mix * 2.0
        if governor_mode == "LABORATORY":
            resin_flow *= 0.5
        if voltage > 5.0:
            resin_flow = max(0.0, resin_flow - (voltage * 0.6))
        rep = physics.get("repetition", 0.0)
        complexity = physics.get("truth_ratio", 0.0)
        theremin_msg = None
        critical_event = None
        if rep > 0.5:
            self.classical_turns += 1
            slag = self.classical_turns * 4.0
            self.decoherence_buildup += slag
            theremin_msg = f"{Prisma.OCHRE}DECOHERENCE: Repetition detected (Turn {self.classical_turns}). Reality hardening (+{slag}).{Prisma.RST}"
        elif complexity > 0.4 and self.classical_turns > 0:
            self.classical_turns = 0
            relief = 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - relief)
            theremin_msg = f"{Prisma.GRN}PERCUSSIVE MAINTENANCE: Calcification Shattered. Flow restored. (-{relief} Resin){Prisma.RST}"
        if solvent_active:
            theremin_msg = f"{theremin_msg} | {solvent_msg}" if theremin_msg else solvent_msg
        elif resin_flow > 0.5:
            self.decoherence_buildup += resin_flow
            if not theremin_msg:
                theremin_msg = f"{Prisma.OCHRE}RESIN FLOW: Hybrid complexity (+{resin_flow:.1f}). Keep it hot to prevent sticking.{Prisma.RST}"
        if resin_flow == 0 and self.classical_turns == 0:
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - 2.0)
        if self.decoherence_buildup > self.SHATTER_POINT:
            self.decoherence_buildup = 0.0
            self.classical_turns = 0
            return False, resin_flow, f"{Prisma.RED}WAVEFUNCTION COLLAPSE: System is solid amber. INITIATING AIRSTRIKE.{Prisma.RST}", "AIRSTRIKE"
        if self.classical_turns > 3:
            critical_event = "CORROSION"
            theremin_msg = f"{theremin_msg} | {Prisma.YEL}FOSSILIZATION IMMINENT{Prisma.RST}"
        if self.decoherence_buildup > self.AMBER_THRESHOLD:
            self.is_stuck = True
            if not theremin_msg:
                theremin_msg = f"{Prisma.RED}AMBER TRAP: You are stuck in the resin. Increase Voltage to melt it.{Prisma.RST}"
        if self.is_stuck and self.decoherence_buildup < 5.0:
            self.is_stuck = False
            if not solvent_active:
                theremin_msg = f"{Prisma.GRN}LIQUEFACTION: The Amber melts. You are free.{Prisma.RST}"
        turb = physics.get("turbulence", 0.0)
        if turb > 0.6 and self.decoherence_buildup > 0:
            shatter_amt = turb * 10.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - shatter_amt)
            theremin_msg = f"{Prisma.CYN}TURBULENCE: Jagged rhythm broke the resin (-{shatter_amt:.1f}).{Prisma.RST}"
            self.classical_turns = 0
        if turb < 0.2:
            physics["narrative_drag"] = max(0.0, physics["narrative_drag"] - 1.0)
        return self.is_stuck, resin_flow, theremin_msg, critical_event

    def get_readout(self):
        return f"{Prisma.GRY}[THEREMIN]: Resin={self.decoherence_buildup:.1f} | Calcification={self.classical_turns}{Prisma.RST}"