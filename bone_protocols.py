""" bone_protocols.py - The Reactive Systems & Game Mechanics """

import random, json
from collections import deque, Counter
from typing import Dict, Tuple, Optional, Any
from bone_core import Prisma, BoneConfig, TheLore
from bone_lexicon import TheLexicon

NARRATIVE_DATA = TheLore.get("narrative_data") or {}

class ZenGarden:
    def __init__(self, events_ref):
        self.events = events_ref
        self.stillness_streak = 0
        self.max_streak = 0
        self.pebbles_collected = 0
        self.koans = NARRATIVE_DATA.get("ZEN_KOANS", ["The code that is not written has no bugs."])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stillness_streak": self.stillness_streak,
            "max_streak": self.max_streak,
            "pebbles_collected": self.pebbles_collected}

    def load_state(self, data: Dict[str, Any]):
        self.stillness_streak = data.get("stillness_streak", 0)
        self.max_streak = data.get("max_streak", 0)
        self.pebbles_collected = data.get("pebbles_collected", 0)

    def raking_the_sand(self, physics: Any, bio: Dict) -> Tuple[float, Optional[str]]:
        vol = getattr(physics, "voltage", 0.0) if not isinstance(physics, dict) else physics.get("voltage", 0.0)
        drag = getattr(physics, "narrative_drag", 0.0) if not isinstance(physics, dict) else physics.get("narrative_drag", 0.0)
        is_stable = (2.0 <= vol <= 12.0) and (drag <= 4.0)
        if is_stable:
            self.stillness_streak += 1
            if self.stillness_streak > self.max_streak:
                self.max_streak = self.stillness_streak
            efficiency_boost = min(0.5, self.stillness_streak * 0.05)
            msg = None
            if self.stillness_streak == 1:
                msg = f"{Prisma.GRY}⛩️ ZEN GARDEN: Entering the quiet zone.{Prisma.RST}"
            elif self.stillness_streak % 5 == 0:
                self.pebbles_collected += 1
                koan = random.choice(self.koans)
                msg = (f"{Prisma.CYN}⛩️ ZEN GARDEN: {self.stillness_streak} ticks of poise.\n"
                       f"   \"{koan}\" (Efficiency +{int(efficiency_boost * 100)}%){Prisma.RST}")
            return efficiency_boost, msg
        if self.stillness_streak > 5:
            self.events.log(f"{Prisma.GRY}🍂 ZEN GARDEN: Leaf falls. Turbulence broke the streak.{Prisma.RST}", "SYS")
        self.stillness_streak = 0
        return 0.0, None

class TheBureau:
    def __init__(self):
        self.stamp_count = 0
        self.forms = NARRATIVE_DATA.get("BUREAU_FORMS", ["Form 27B-6", "Form 404"])
        self.responses = NARRATIVE_DATA.get("BUREAU_RESPONSES", ["Processing..."])
        self.BUZZWORDS = {"synergy", "paradigm", "leverage", "utilize", "holistic", "bandwidth", "circle back"}

    def to_dict(self) -> Dict[str, Any]:
        return {"stamp_count": self.stamp_count}

    def load_state(self, data: Dict[str, Any]):
        self.stamp_count = data.get("stamp_count", 0)

    def audit(self, physics, bio_state, context=None):
        if bio_state.get("health", 100.0) < 20.0: return None
        vol = getattr(physics, "voltage", 0.0) if not isinstance(physics, dict) else physics.get("voltage", 0.0)
        clean_words = getattr(physics, "clean_words", []) if not isinstance(physics, dict) else physics.get(
            "clean_words", [])
        truth = getattr(physics, "truth_ratio", 0.0) if not isinstance(physics, dict) else physics.get("truth_ratio", 0.0)
        selected_form = None
        evidence = []
        if vol > 18.0:
            if truth < 0.8:
                selected_form = "ZONING_VIOLATION"
                evidence = ["Excessive Voltage", "Unlicensed Fiction"]
            else:
                selected_form = "Form 202-A"
        elif any(w in self.BUZZWORDS for w in clean_words):
            hits = [w for w in clean_words if w in self.BUZZWORDS]
            selected_form = random.choice(self.forms)
            evidence = hits
        elif vol < 2.0 and len(clean_words) > 5:
            selected_form = "Schedule C"
            evidence = ["Lack of Ambition"]
        if not selected_form:
            return None
        self.stamp_count += 1
        chaos_tax = 5.0
        if selected_form == "ZONING_VIOLATION": chaos_tax = 15.0
        bureau_resp = random.choice(self.responses)
        ui_msg = f"{Prisma.GRY}🏢 THE BUREAU: {bureau_resp}{Prisma.RST}\n   {Prisma.WHT}[Filed: {selected_form}]{Prisma.RST}"
        if evidence:
            ui_msg += f"\n   {Prisma.RED}Evidence: {', '.join(evidence)}{Prisma.RST}"
        return {
            "status": "AUDITED",
            "ui": ui_msg,
            "log": f"BUREAUCRACY: Filed {selected_form}. Chaos Tax: -{chaos_tax:.1f} ATP.",
            "atp_gain": -chaos_tax}

class TherapyProtocol:
    def __init__(self):
        self.streaks = {k: 0 for k in BoneConfig.TRAUMA_VECTOR.keys()}
        self.HEALING_THRESHOLD = 5

    def to_dict(self) -> Dict[str, Any]:
        return {"streaks": self.streaks}

    def load_state(self, data: Dict[str, Any]):
        self.streaks = data.get("streaks", {k: 0 for k in BoneConfig.TRAUMA_VECTOR.keys()})

    def check_progress(self, phys, stamina, current_trauma_accum, qualia=None):
        counts = getattr(phys, "counts", {}) if not isinstance(phys, dict) else phys.get("counts", {})
        vector = getattr(phys, "vector", {}) if not isinstance(phys, dict) else phys.get("vector", {})
        healed_types = []
        is_clean = counts.get("toxin", 0) == 0
        has_strength = vector.get("STR", 0.0) > 0.3
        if is_clean and has_strength:
            self.streaks["SEPTIC"] += 1
        else:
            self.streaks["SEPTIC"] = 0
        for trauma_type, streak in self.streaks.items():
            if streak >= self.HEALING_THRESHOLD:
                self.streaks[trauma_type] = 0
                if current_trauma_accum[trauma_type] > 0.0:
                    current_trauma_accum[trauma_type] = max(0.0, current_trauma_accum[trauma_type] - 0.5)
                    healed_types.append(trauma_type)
        return healed_types

class KintsugiProtocol:
    PATH_SCAR = "SCAR"
    PATH_INTEGRATION = "KINTSUGI"
    PATH_ALCHEMY = "ALCHEMY"

    def __init__(self):
        self.active_koan = None
        self.koans = NARRATIVE_DATA.get("KINTSUGI_KOANS", ["The crack is where the light enters."])

    def to_dict(self) -> Dict[str, Any]:
        return {"active_koan": self.active_koan}

    def load_state(self, data: Dict[str, Any]):
        self.active_koan = data.get("active_koan", None)

    def check_integrity(self, stamina):
        if stamina < 15.0 and not self.active_koan:
            self.active_koan = random.choice(self.koans)
            return True, self.active_koan
        return False, None

    def attempt_repair(self, phys, trauma_accum, soul_ref=None, qualia=None):
        if not self.active_koan: return None
        vol = getattr(phys, "voltage", 0.0) if not isinstance(phys, dict) else phys.get("voltage", 0.0)
        clean = getattr(phys, "clean_words", []) if not isinstance(phys, dict) else phys.get("clean_words", [])
        play_count = sum(1 for w in clean if w in TheLexicon.get("play") or w in TheLexicon.get("abstract"))
        whimsy_score = play_count / max(1, len(clean))
        pathway = self.PATH_SCAR
        if vol > 15.0 and whimsy_score > 0.4:
            pathway = self.PATH_ALCHEMY
        elif vol > 8.0 and whimsy_score > 0.2:
            pathway = self.PATH_INTEGRATION
        return self._execute_pathway(pathway, trauma_accum, soul_ref)

    def _execute_pathway(self, pathway, trauma_accum, soul_ref):
        if not trauma_accum: return {"success": False, "msg": "No fissures found."}
        target = max(trauma_accum, key=trauma_accum.get)
        severity = trauma_accum[target]
        healed_log = []
        msg = ""
        success = False
        if pathway == self.PATH_ALCHEMY:
            reduction = severity * 0.8
            trauma_accum[target] = max(0.0, severity - reduction)
            atp_boost = reduction * 15.0
            msg = f"{Prisma.VIOLET}🔮 ALCHEMY: The wound '{target}' burns into pure fuel. (+{atp_boost:.1f} ATP){Prisma.RST}"
            healed_log.append(f"Transmuted {target}")
            success = True
            return {"success": True, "msg": msg, "healed": healed_log, "atp_gain": atp_boost}
        elif pathway == self.PATH_INTEGRATION:
            reduction = 2.0
            trauma_accum[target] = max(0.0, severity - reduction)
            if soul_ref:
                soul_ref.traits.adjust("WISDOM", 0.1)
                healed_log.append("Wisdom +0.1")
            msg = f"{Prisma.YEL}🏺 KINTSUGI: The '{target}' crack is filled with gold. The vessel is stronger.{Prisma.RST}"
            healed_log.append(f"Integrated {target}")
            success = True
        else:
            reduction = 0.5
            trauma_accum[target] = max(0.0, severity - reduction)
            msg = f"{Prisma.GRY}🩹 SCAR: It's ugly, but it holds.{Prisma.RST}"
            healed_log.append(f"Scarred {target}")
            success = True
        return {"success": success, "msg": msg, "healed": healed_log}


class TheCriticsCircle:
    def __init__(self, events_ref):
        self.events = events_ref
        self.critics = NARRATIVE_DATA.get("LITERARY_CRITICS", {})
        self.active_cooldowns = {}
        self.last_review_turn = 0

    def to_dict(self):
        return {"active_cooldowns": self.active_cooldowns, "last_review_turn": self.last_review_turn}

    def load_state(self, data):
        self.active_cooldowns = data.get("active_cooldowns", {})
        self.last_review_turn = data.get("last_review_turn", 0)

    def audit_performance(self, physics: Any, turn_count: int) -> Optional[str]:
        if turn_count - self.last_review_turn < 10: return None
        p = physics if isinstance(physics, dict) else getattr(physics, "__dict__", {})
        voltage = p.get("voltage", 0.0)
        drag = p.get("narrative_drag", 0.0)
        if "velocity" not in p: p["velocity"] = voltage * (1.0 / max(0.1, drag))
        best_match = None
        highest_intensity = 0.0
        review_type = "neutral"

        for key, critic in self.critics.items():
            if self.active_cooldowns.get(key, 0) > turn_count: continue
            prefs = critic.get("preferences", {})
            score = 0.0
            for metric, target in prefs.items():
                current = p.get(metric, 0.0)
                if target > 0:
                    score += current * target
                else:
                    score -= current * abs(target)

            if score > 15.0:
                best_match = (key, critic)
                highest_intensity = score
                review_type = "high"
            elif score < -15.0:
                best_match = (key, critic)
                highest_intensity = abs(score)
                review_type = "low"

        if best_match:
            key, critic = best_match
            self.last_review_turn = turn_count
            self.active_cooldowns[key] = turn_count + 50
            reviews = critic["reviews"].get(review_type, ["Hrm."])
            comment = random.choice(reviews)
            color = Prisma.GRN if review_type == "high" else Prisma.RED
            icon = "🌟" if review_type == "high" else "💢"
            return f"{color}{icon} CRITIC REVIEW ({critic['name']}): \"{comment}\"{Prisma.RST}"
        return None

class LimboLayer:
    MAX_ECTOPLASM = 50
    STASIS_SCREAMS = NARRATIVE_DATA.get("CASSANDRA_SCREAMS", [
        "BANGING ON THE GLASS", "IT'S TOO COLD", "LET ME OUT"])

    def __init__(self):
        self.ghosts = deque(maxlen=self.MAX_ECTOPLASM); self.haunt_chance = 0.05; self.stasis_leak = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ghosts": list(self.ghosts),
            "stasis_leak": self.stasis_leak}

    def load_state(self, data: Dict[str, Any]):
        self.ghosts = deque(data.get("ghosts", []), maxlen=self.MAX_ECTOPLASM)
        self.stasis_leak = data.get("stasis_leak", 0.0)

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
        self.stasis_leak += 1.0
        horror = random.choice(self.STASIS_SCREAMS)
        self.ghosts.append(f"{Prisma.VIOLET}{horror}{Prisma.RST}")
        return f"{Prisma.CYN}STASIS ERROR: '{intended_thought}' froze halfway. {horror}.{Prisma.RST}"

    def haunt(self, text):
        if self.stasis_leak > 0:
            if random.random() < 0.2:
                self.stasis_leak = max(0.0, self.stasis_leak - 0.5)
                scream = random.choice(self.STASIS_SCREAMS)
                return f"{text} ...{Prisma.RED}{scream}{Prisma.RST}..."
        if self.ghosts and random.random() < self.haunt_chance:
            spirit = random.choice(self.ghosts)
            return f"{text} ...{Prisma.GRY}{spirit}{Prisma.RST}..."
        return text

class TheFolly:
    def __init__(self):
        self.gut_memory = deque(maxlen=50); self.global_tastings = Counter()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gut_memory": list(self.gut_memory),
            "global_tastings": dict(self.global_tastings)}

    def load_state(self, data: Dict[str, Any]):
        self.gut_memory = deque(data.get("gut_memory", []), maxlen=50)
        self.global_tastings = Counter(data.get("global_tastings", {}))

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