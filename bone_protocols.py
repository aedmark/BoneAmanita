""" bone_protocols.py - The Reactive Systems & Game Mechanics """

import random, json
from collections import deque, Counter
from typing import Dict, Tuple, Optional
from bone_data import TheLore
from bone_bus import Prisma, BoneConfig
from bone_lexicon import TheLexicon

NARRATIVE_DATA = TheLore.get("narrative_data") or {}


class ZenGarden:
    def __init__(self, events_ref):
        self.events = events_ref
        self.stillness_streak = 0
        self.max_streak = 0
        self.pebbles_collected = 0
        self.koans = NARRATIVE_DATA.get("ZEN_KOANS", ["The code that is not written has no bugs."])

    def raking_the_sand(self, physics: Dict, bio: Dict) -> Tuple[float, Optional[str]]:
        def _get(p, k, d=0.0):
            return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

        voltage = _get(physics, "voltage", 0.0)
        drag = _get(physics, "narrative_drag", 0.0)
        counts = _get(physics, "counts", {})
        toxin = counts.get("toxin", 0) if isinstance(counts, dict) else 0
        cortisol = bio.get("chem", {}).get("COR", 0.0)
        is_stable = (2.0 <= voltage <= 12.0) and (drag <= 4.0) and (toxin == 0) and (cortisol < 0.4)
        if is_stable:
            self.stillness_streak += 1
            if self.stillness_streak > self.max_streak: self.max_streak = self.stillness_streak
            efficiency_boost = min(0.5, self.stillness_streak * 0.05)
            msg = None
            if self.stillness_streak % 5 == 0:
                self.pebbles_collected += 1
                msg = f"{Prisma.CYN}⛩️ ZEN GARDEN: {self.stillness_streak} ticks of poise. (Voltage 2-12v, Low Drag). Efficiency +{int(efficiency_boost*100)}%{Prisma.RST}"
            elif self.stillness_streak == 1:
                msg = f"{Prisma.GRY}ZEN GARDEN: Entering the quiet zone.{Prisma.RST}"
            return efficiency_boost, msg
        else:
            if self.stillness_streak > 5:
                reason = []
                if not (2.0 <= voltage <= 12.0): reason.append(f"Voltage({voltage:.1f})")
                if drag > 4.0: reason.append(f"Drag({drag:.1f})")
                if toxin > 0: reason.append("Toxin")
                self.events.log(f"{Prisma.GRY}ZEN GARDEN: Leaf falls. Streak broken by {', '.join(reason)}.{Prisma.RST}", "SYS")
            self.stillness_streak = 0
            return 0.0, None

class TheBureau:
    def __init__(self):
        self.stamp_count = 0
        self.forms = NARRATIVE_DATA.get("BUREAU_FORMS", ["Form 1A"]).copy()
        self.forms.extend(["Form 404: Void-Fill Application", "Form 1040-EZ: Existence Zoning", "STOP WORK ORDER"])
        self.responses = NARRATIVE_DATA.get("BUREAU_RESPONSES", ["Processing..."])
        self.POLICY = {
            "27B-6": {"effect": "ESCALATE", "mod": {"narrative_drag": -3.0, "kappa": -0.2}, "atp": 0.0},
            "1099-B": {"effect": "STAGNATE", "mod": {"narrative_drag": 5.0, "voltage": -5.0}, "atp": 15.0},
            "Schedule C": {"effect": "TAX", "mod": {"voltage": -10.0}, "atp": 8.0},
            "Form W-2": {"effect": "NORMALIZE", "mod": {"beta_index": 1.0, "turbulence": 0.0}, "atp": 5.0},
            "Form 404": {"effect": "NULLIFY", "mod": {"voltage": -20.0, "kappa": 1.0}, "atp": -5.0},
            "ZONING_VIOLATION": {"effect": "LOCKDOWN", "mod": {"voltage": -100.0, "narrative_drag": 100.0}, "atp": -10.0}}
        self.BUZZWORDS = {"synergy", "paradigm", "leverage", "utilize", "holistic", "bandwidth", "circle back"}

    def audit(self, physics, bio_state, context=None):
        if bio_state.get("health", 100.0) < 20.0: return None

        def _get(p, k, d=0.0):
            return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

        def _set(p, k, v):
            if isinstance(p, dict): p[k] = v
            else: setattr(p, k, v)

        def _has(p, k):
            if isinstance(p, dict): return k in p
            return hasattr(p, k)

        beige_threshold = 0.6
        if context:
            mode = context.get('mode', 'NORMAL')
            if mode in ['DEBUG', 'ARCHITECT', 'SURGERY']: beige_threshold = 0.85
            elif mode == 'POETRY': beige_threshold = 0.3

        voltage = _get(physics, "voltage", 0.0)
        clean_words = _get(physics, "clean_words", [])
        counts = _get(physics, "counts", {})
        toxin = counts.get("toxin", 0) if isinstance(counts, dict) else 0

        buzz_hits = [w for w in clean_words if w in self.BUZZWORDS]
        suburban_words = [w for w in clean_words if w in TheLexicon.get("suburban") or w in TheLexicon.get("buffer")]
        beige_density = len(suburban_words) / max(1, len(clean_words))
        selected_form = None; evidence = []
        truth_ratio = _get(physics, "truth_ratio", 0.0)

        if voltage > 18.0:
            if truth_ratio > 0.8: selected_form = "Form 202-A"; evidence = ["Voltage > 18.0", "Truth > 80%", "Artistic License Verified"]
            else: selected_form = "ZONING_VIOLATION"; evidence = ["Excessive Voltage", "Unlicensed Reality Construction"]
        elif buzz_hits: selected_form = "Form 404"; evidence = buzz_hits
        elif beige_density > beige_threshold: selected_form = "1099-B" if len(suburban_words) > 2 else "Form W-2"; evidence = list(set(suburban_words))[:3]
        elif voltage < 2.0 and len(clean_words) > 2: selected_form = "Schedule C"

        if not selected_form: return None
        self.stamp_count += 1
        policy = self.POLICY.get(selected_form, self.POLICY["Form W-2"])
        mod_log = []

        for k, v in policy["mod"].items():
            if _has(physics, k):
                old_val = _get(physics, k, 0.0)
                new_val = old_val + v
                if k == "voltage" and new_val < 0: new_val = 0.0
                _set(physics, k, new_val)
                mod_log.append(f"{k} {v:+.1f}")

        full_form_name = next((f for f in self.forms if selected_form in f), selected_form)
        evidence_str = f"\n   {Prisma.RED}Evidence: {', '.join(evidence)}{Prisma.RST}" if evidence else ""
        ui_msg = f"{Prisma.GRY}🏢 THE BUREAU: {random.choice(self.responses)}{Prisma.RST}\n   {Prisma.WHT}[Filed: {full_form_name}]{Prisma.RST}{evidence_str}"
        if selected_form == "ZONING_VIOLATION":
            ui_msg = f"{Prisma.RED}🛑 STOP WORK ORDER 🛑{Prisma.RST}\n   {Prisma.GRY}You are exceeding the licensed voltage for this district.{Prisma.RST}\n   {Prisma.WHT}Please sign 'Form 1040-EZ' (Type: 'I accept reality') to restore service.{Prisma.RST}"
        return {"status": policy["effect"], "ui": ui_msg, "log": f"BUREAUCRACY: Filed {selected_form}. Mods: {mod_log}.", "atp_gain": policy["atp"]}


class TherapyProtocol:
    def __init__(self):
        self.streaks = {k: 0 for k in BoneConfig.TRAUMA_VECTOR.keys()}
        self.HEALING_THRESHOLD = 5

    def check_progress(self, phys, stamina, current_trauma_accum):
        def _get(p, k, d=0.0):
            return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

        counts = _get(phys, "counts", {})
        vector = _get(phys, "vector", {})
        voltage = _get(phys, "voltage", 0.0)
        drag = _get(phys, "narrative_drag", 0.0)

        healed_types = []
        if counts.get("toxin", 0) == 0 and vector.get("STR", 0.0) > 0.3: self.streaks["SEPTIC"] += 1
        else: self.streaks["SEPTIC"] = 0
        if stamina > 40 and counts.get("photo", 0) > 0: self.streaks["CRYO"] += 1
        else: self.streaks["CRYO"] = 0
        if 2.0 <= voltage <= 7.0: self.streaks["THERMAL"] += 1
        else: self.streaks["THERMAL"] = 0
        if drag < 2.0 and vector.get("VEL", 0.0) > 0.5: self.streaks["BARIC"] += 1
        else: self.streaks["BARIC"] = 0
        for trauma_type, streak in self.streaks.items():
            if streak >= self.HEALING_THRESHOLD:
                self.streaks[trauma_type] = 0
                if current_trauma_accum[trauma_type] > 0.001:
                    current_trauma_accum[trauma_type] = max(0.0, current_trauma_accum[trauma_type] - 0.5)
                    healed_types.append(trauma_type)
        return healed_types

    @staticmethod
    def get_medical_chart(current_trauma_accum):
        chart = []
        for trauma_type, severity in current_trauma_accum.items():
            if severity > 0.1:
                status = "Acute" if severity > 5.0 else "Chronic" if severity > 2.0 else "Mild"
                bar = "█" * int(severity); chart.append(f"{trauma_type}: {status} ({severity:.1f}) {bar}")
        if not chart: return "Patient is clean. No significant trauma detected."
        return "\n".join(chart)

class KintsugiProtocol:
    PATH_SCAR = "SCAR"; PATH_INTEGRATION = "KINTSUGI"; PATH_ALCHEMY = "ALCHEMY"
    REPAIR_VOLTAGE_MIN = 8.0; WHIMSY_THRESHOLD = 0.3; STAMINA_CRITICAL = 15.0

    def __init__(self):
        self.active_koan = None; self.repairs_count = 0
        self.koans = NARRATIVE_DATA.get("KINTSUGI_KOANS", ["The crack is where the light enters."])
        self.gold_reserves = 5.0

    def check_integrity(self, stamina):
        if stamina < self.STAMINA_CRITICAL and not self.active_koan:
            self.active_koan = random.choice(self.koans)
            return True, self.active_koan
        return False, None

    def attempt_repair(self, phys, trauma_accum, soul_ref=None):
        if not self.active_koan: return None

        def _get(p, k, d=0.0):
            return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

        voltage = _get(phys, "voltage", 0.0)
        clean = _get(phys, "clean_words", [])

        play_count = sum(1 for w in clean if w in TheLexicon.get("play") or w in TheLexicon.get("abstract"))
        total = max(1, len(clean)); whimsy_score = play_count / total
        pathway = self.PATH_SCAR
        if voltage > 15.0 and whimsy_score > 0.5: pathway = self.PATH_ALCHEMY
        elif voltage > self.REPAIR_VOLTAGE_MIN and whimsy_score > self.WHIMSY_THRESHOLD: pathway = self.PATH_INTEGRATION
        result = self._execute_pathway(pathway, trauma_accum, soul_ref, voltage)
        old_koan = self.active_koan; self.active_koan = None; self.repairs_count += 1
        result["detail"] = f"'{old_koan}' resolved via {pathway}. (V: {voltage:.1f} | Whimsy: {whimsy_score:.2f})"
        return result

    def _execute_pathway(self, pathway, trauma_accum, soul_ref, voltage):
        healed_log = []; msg = ""; success = False
        if not trauma_accum: return {"success": False, "msg": "No trauma to heal."}
        target_trauma = max(trauma_accum, key=trauma_accum.get); severity = trauma_accum[target_trauma]
        if pathway == self.PATH_ALCHEMY:
            reduction = severity * 0.8; trauma_accum[target_trauma] = max(0.0, severity - reduction)
            atp_boost = reduction * 10.0
            msg = f"{Prisma.VIOLET}🔮 ALCHEMICAL TRANSMUTATION: Pain has become Power. (+{atp_boost:.1f} ATP){Prisma.RST}"
            healed_log.append(f"Transmuted {target_trauma} into Fuel."); success = True
            return {"success": True, "msg": msg, "healed": healed_log, "atp_gain": atp_boost}
        elif pathway == self.PATH_INTEGRATION:
            reduction = 2.0; trauma_accum[target_trauma] = max(0.0, severity - reduction)
            if soul_ref:
                current_wis = soul_ref.traits.get("WISDOM", 0.0)
                soul_ref.traits["WISDOM"] = min(1.0, current_wis + 0.1)
                healed_log.append("Gained Wisdom (+0.1)")
            msg = f"{Prisma.YEL}🏺 KINTSUGI COMPLETE: The {target_trauma} is filled with Gold.{Prisma.RST}"
            healed_log.append(f"Repaired {target_trauma} (-{reduction})"); success = True
        else:
            reduction = 0.5; trauma_accum[target_trauma] = max(0.0, severity - reduction)
            msg = f"{Prisma.GRY}🩹 SCAR TISSUE FORMED: It is ugly, but it holds.{Prisma.RST}"
            healed_log.append(f"Scarred over {target_trauma} (-{reduction})"); success = True
        return {"success": success, "msg": msg, "healed": healed_log}

class LimboLayer:
    MAX_ECTOPLASM = 50
    STASIS_SCREAMS = ["BANGING ON THE GLASS", "IT'S TOO COLD", "LET ME OUT", "HALF AWAKE", "REVIVE FAILED"]

    def __init__(self):
        self.ghosts = deque(maxlen=self.MAX_ECTOPLASM); self.haunt_chance = 0.05; self.stasis_leak = 0.0

    def absorb_dead_timeline(self, filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                if "trauma_vector" in data:
                    for k, v in data["trauma_vector"].items():
                        if v > 0.3: self.ghosts.append(f"👻{k}_ECHO")
                if "mutations" in data and "heavy" in data["mutations"]:
                    bones = list(data["mutations"]["heavy"]); random.shuffle(bones); self.ghosts.extend(bones[:3])
        except (IOError, json.JSONDecodeError): pass

    def trigger_stasis_failure(self, intended_thought):
        self.stasis_leak += 1.0; horror = random.choice(self.STASIS_SCREAMS)
        self.ghosts.append(f"{Prisma.VIOLET}{horror}{Prisma.RST}")
        return f"{Prisma.CYN}STASIS ERROR: '{intended_thought}' froze halfway. It is banging on the glass.{Prisma.RST}"

    def haunt(self, text):
        if self.stasis_leak > 0:
            if random.random() < 0.2:
                self.stasis_leak = max(0.0, self.stasis_leak - 0.5); scream = random.choice(self.STASIS_SCREAMS)
                return f"{text} ...{Prisma.RED}{scream}{Prisma.RST}..."
        if self.ghosts and random.random() < self.haunt_chance:
            spirit = random.choice(self.ghosts)
            return f"{text} ...{Prisma.GRY}{spirit}{Prisma.RST}..."
        return text

class TheFolly:
    def __init__(self):
        self.gut_memory = deque(maxlen=50); self.global_tastings = Counter()

    @staticmethod
    def audit_desire(physics, stamina):
        def _get(p, k, d=0.0):
            return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)
        voltage = _get(physics, "voltage", 0.0)
        if voltage > 8.5 and stamina > 45:
            return "MAUSOLEUM_CLAMP", f"{Prisma.GRY}THE MAUSOLEUM: No battle is ever won. We are just spinning hands.{Prisma.RST}\n   {Prisma.CYN}TIME DILATION: Voltage 0.0. The field reveals your folly.{Prisma.RST}", 0.0, None
        return None, None, 0.0, None

    def grind_the_machine(self, atp_pool, clean_words, lexicon):
        loot = None
        if 20.0 > atp_pool > 0.0:
            meat_words = [w for w in clean_words if w in lexicon.get("heavy") or w in lexicon.get("kinetic") or w in lexicon.get("suburban")]
            fresh_meat = [w for w in meat_words if w not in self.gut_memory]
            if fresh_meat:
                target = random.choice(fresh_meat); self.gut_memory.append(target); self.global_tastings[target] += 1
                times_eaten = self.global_tastings[target]
                base_yield = 30.0; decay_factor = 0.7 ** (times_eaten - 1); actual_yield = max(2.0, base_yield * decay_factor)
                flavor_text = f" (Stale: {times_eaten}x)" if times_eaten > 3 else ""
                if target in lexicon.get("suburban"): return "INDIGESTION", f"{Prisma.MAG}THE FOLLY GAGS: It coughs up a piece of office equipment.{Prisma.RST}", -2.0, "THE_RED_STAPLER"
                if target in lexicon.get("play"): return "SUGAR_RUSH", f"{Prisma.VIOLET}THE FOLLY CHEWS: It compresses the chaos into a small, sticky ball.{Prisma.RST}", 5.0, "QUANTUM_GUM"
                if actual_yield >= 25.0: loot = "STABILITY_PIZZA"
                return "MEAT_GRINDER", f"{Prisma.RED}CROWD CAFFEINE: I chewed on '{target.upper()}'{flavor_text}.{Prisma.RST}\n   {Prisma.WHT}Yield: {actual_yield:.1f} ATP.{Prisma.RST}", actual_yield, loot
            elif meat_words: return "REGURGITATION", f"{Prisma.OCHRE}REFLEX: You already fed me '{meat_words[0]}'. It is ash to me now.{Prisma.RST}\n   {Prisma.RED}► PENALTY: -5.0 ATP. Find new fuel.{Prisma.RST}", -5.0, None
            else:
                abstract_words = [w for w in clean_words if w in lexicon.get("abstract")]
                if abstract_words:
                    target = random.choice(abstract_words); yield_val = 8.0
                    return "GRUEL", f"{Prisma.GRY}THE FOLLY SIGHS: It grinds the ABSTRACT concept '{target.upper()}'.{Prisma.RST}\n   {Prisma.GRY}It tastes like chalk dust. +{yield_val} ATP.{Prisma.RST}", yield_val, None
                return "INDIGESTION", f"{Prisma.OCHRE}INDIGESTION: I tried to eat your words, but they were just air.{Prisma.RST}\n   {Prisma.GRY}Cannot grind this input into fuel.{Prisma.RST}\n   {Prisma.RED}► STARVATION CONTINUES.{Prisma.RST}", 0.0, None
        return None, None, 0.0, None