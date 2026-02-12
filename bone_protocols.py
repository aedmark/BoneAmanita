""" bone_protocols.py - The Reactive Systems & Game Mechanics """

import random, json
import re
from collections import deque, Counter
from typing import Dict, Tuple, Optional, Any
from bone_core import TheLore
from bone_types import Prisma
from bone_lexicon import LexiconService
from bone_config import BoneConfig

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
        is_stable = (BoneConfig.ZEN.VOLTAGE_MIN <= vol <= BoneConfig.ZEN.VOLTAGE_MAX) and (drag <= BoneConfig.ZEN.DRAG_MAX)
        if is_stable:
            self.stillness_streak += 1
            if self.stillness_streak > self.max_streak:
                self.max_streak = self.stillness_streak
            efficiency_boost = min(BoneConfig.ZEN.EFFICIENCY_CAP, self.stillness_streak * BoneConfig.ZEN.EFFICIENCY_SCALAR)
            msg = None
            if self.stillness_streak == 1:
                msg = f"{Prisma.GRY}⛩️ ZEN GARDEN: Entering the quiet zone.{Prisma.RST}"
            elif self.stillness_streak % 5 == 0:
                self.pebbles_collected += 1
                koan = random.choice(self.koans)
                msg = (f"{Prisma.CYN}⛩️ ZEN GARDEN: {self.stillness_streak} ticks of poise.\n"
                       f"   \"{koan}\" (Efficiency +{int(efficiency_boost * 100)}%){Prisma.RST}")
            return efficiency_boost, msg
        if self.stillness_streak > BoneConfig.ZEN.STREAK_BREAK_THRESHOLD:
            self.events.log(f"{Prisma.GRY}🍂 ZEN GARDEN: Leaf falls. Turbulence broke the streak.{Prisma.RST}", "SYS")
        self.stillness_streak = 0
        return 0.0, None


class TheBureau:
    def __init__(self):
        self.stamp_count = 0
        self.forms = NARRATIVE_DATA.get("BUREAU_FORMS", ["Form 27B-6", "Form 404"])
        self.responses = NARRATIVE_DATA.get("BUREAU_RESPONSES", ["Processing..."])
        lex_data = TheLore.get("LEXICON") or {}
        self.buzzwords = set(lex_data.get("bureau_buzzwords", [
            "synergy", "paradigm", "leverage", "utilize"
        ]))
        self.crimes = []
        self.crime_data = TheLore.get("STYLE_CRIMES") or {}
        if "PATTERNS" in self.crime_data:
            for p in self.crime_data["PATTERNS"]:
                try:
                    self.crimes.append({
                        "name": p.get("name", "Unknown Violation"),
                        "regex": re.compile(p["regex"], re.IGNORECASE),
                        "msg": p.get("error_msg", "Style Violation Detected."),
                        "tax": 5.0})
                except re.error as e:
                    print(f"{Prisma.RED}[BUREAU]: Failed to compile law '{p.get('name')}': {e}{Prisma.RST}")

    def to_dict(self) -> Dict[str, Any]:
        return {"stamp_count": self.stamp_count}

    def load_state(self, data: Dict[str, Any]):
        self.stamp_count = data.get("stamp_count", 0)

    def audit(self, physics, bio_state, context=None, origin="USER") -> Optional[Dict]:
        if bio_state.get("health", 100.0) < BoneConfig.BUREAU.MIN_HEALTH_TO_AUDIT: return None
        p = physics if isinstance(physics, dict) else getattr(physics, "__dict__", {})
        vol = p.get("voltage", 0.0)
        clean_words = p.get("clean_words", [])
        raw_text = p.get("raw_text", "")
        truth = p.get("truth_ratio", 0.0)
        word_count = len(raw_text.split())
        if raw_text.startswith("/") or word_count < BoneConfig.BUREAU.MIN_WORD_COUNT:
            return None
        selected_form = None
        evidence = []
        tax = 0.0
        if raw_text:
            for crime in self.crimes:
                if crime["regex"].search(raw_text):
                    selected_form = f"VIOLATION: {crime['name']}"
                    evidence.append(crime['msg'])
                    tax += crime['tax']
                    break
        if not selected_form and vol > BoneConfig.BUREAU.HIGH_VOLTAGE_TRIGGER:
            if truth < BoneConfig.BUREAU.LOW_TRUTH_TRIGGER:
                selected_form = "ZONING_VIOLATION"
                evidence = ["Excessive Voltage", "Unlicensed Fiction"]
                tax = BoneConfig.BUREAU.TAX_HEAVY
            else:
                selected_form = "Form 202-A"
                tax = BoneConfig.BUREAU.TAX_STANDARD
        elif not selected_form and any(w in self.buzzwords for w in clean_words):
            hits = [w for w in clean_words if w in self.buzzwords]
            selected_form = random.choice(self.forms)
            evidence = hits
            tax = BoneConfig.BUREAU.TAX_STANDARD
        if not selected_form:
            return None
        self.stamp_count += 1
        bureau_resp = random.choice(self.responses)
        prefix = f"{Prisma.GRY}🏢 THE BUREAU"
        if origin == "SYSTEM":
            prefix = f"{Prisma.RED}🏢 INTERNAL AFFAIRS"
            bureau_resp = "System Output Violation detected."
        ui_msg = f"{prefix}: {bureau_resp}{Prisma.RST}\n   {Prisma.WHT}[Filed: {selected_form} against {origin}]{Prisma.RST}"
        if evidence:
            ui_msg += f"\n   {Prisma.RED}Evidence: {', '.join(evidence)}{Prisma.RST}"
        return {
            "status": "AUDITED",
            "ui": ui_msg,
            "log": f"BUREAUCRACY: Filed {selected_form} against {origin}. Chaos Tax: -{tax:.1f} ATP.",
            "atp_gain": -tax
        }

class TherapyProtocol:
    def __init__(self):
        default_vector = {"SEPTIC": 0, "EXHAUSTION": 0, "PARANOIA": 0}
        vector_keys = getattr(BoneConfig, "TRAUMA_VECTOR", default_vector).keys()
        self.streaks = {k: 0 for k in vector_keys}
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
        clean = LexiconService.sanitize(getattr(phys, "raw_text", "")) if hasattr(phys, "raw_text") else []
        play_count = sum(1 for w in clean if w in LexiconService.get("play") or w in LexiconService.get("abstract"))
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

    def absorb_dead_timeline(self, filepath: str) -> None:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            self._extract_ghosts(data)
        except (IOError, json.JSONDecodeError) as e:
            print(f"{Prisma.RED}[LIMBO] Failed to absorb timeline '{filepath}': {e}{Prisma.RST}")

    def _extract_ghosts(self, data: Dict[str, Any]) -> None:
        if "trauma_vector" in data:
            for k, v in data["trauma_vector"].items():
                if v > 0.3:
                    self.ghosts.append(f"👻{k}_ECHO")
        if "mutations" in data and "heavy" in data["mutations"]:
            bones = list(data["mutations"]["heavy"])
            random.shuffle(bones)
            self.ghosts.extend(bones[:3])

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
        self.gut_memory = deque(maxlen=50);
        self.global_tastings = Counter()

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
        if voltage > BoneConfig.FOLLY.MAUSOLEUM_VOLTAGE and stamina > BoneConfig.FOLLY.MAUSOLEUM_STAMINA:
            return "MAUSOLEUM_CLAMP", f"{Prisma.GRY}THE MAUSOLEUM: No battle is ever won. We are just spinning hands.{Prisma.RST}\n   {Prisma.CYN}TIME DILATION: Voltage 0.0. The field reveals your folly.{Prisma.RST}", 0.0, None
        return None, None, 0.0, None

    def grind_the_machine(self, atp_pool: float, clean_words: list, lexicon: Dict) -> Tuple[
        Optional[str], Optional[str], float, Optional[str]]:
        if not (0.0 < atp_pool < BoneConfig.FOLLY.FEEDING_CAP):
            return None, None, 0.0, None
        meat_words = self._filter_meat_words(clean_words, lexicon)
        if not meat_words:
            return self._attempt_digest_abstract(clean_words, lexicon)
        fresh_meat = [w for w in meat_words if w not in self.gut_memory]
        if not fresh_meat:
            target = meat_words[0]
            msg = (f"{Prisma.OCHRE}REFLEX: You already fed me '{target}'. It is ash to me now.{Prisma.RST}\n"
                   f"   {Prisma.RED}► PENALTY: -{BoneConfig.FOLLY.PENALTY_REGURGITATION} ATP. Find new fuel.{Prisma.RST}")
            return "REGURGITATION", msg, -BoneConfig.FOLLY.PENALTY_REGURGITATION, None
        return self._eat_meat(fresh_meat, lexicon)

    def _eat_meat(self, fresh_meat: list, lexicon: Dict) -> Tuple[str, str, float, Optional[str]]:
        target = random.choice(fresh_meat)
        suburban_set = lexicon.get("suburban")
        suburban_set = suburban_set if suburban_set else []
        play_set = lexicon.get("play")
        play_set = play_set if play_set else []
        self.gut_memory.append(target)
        self.global_tastings[target] += 1
        if target in suburban_set:
            return "INDIGESTION", f"{Prisma.MAG}THE FOLLY GAGS: It coughs up a piece of office equipment.{Prisma.RST}", -BoneConfig.FOLLY.PENALTY_INDIGESTION, "THE_RED_STAPLER"
        if target in play_set:
            return "SUGAR_RUSH", f"{Prisma.VIOLET}THE FOLLY CHEWS: It compresses the chaos into a small, sticky ball.{Prisma.RST}", BoneConfig.FOLLY.SUGAR_RUSH_YIELD, "QUANTUM_GUM"
        times_eaten = self.global_tastings[target]
        base_yield = BoneConfig.FOLLY.BASE_YIELD
        decay_factor = BoneConfig.FOLLY.DECAY_EXPONENT ** (times_eaten - 1)
        actual_yield = max(2.0, base_yield * decay_factor)
        loot = "STABILITY_PIZZA" if actual_yield >= BoneConfig.FOLLY.PIZZA_THRESHOLD else None
        flavor_text = f" (Stale: {times_eaten}x)" if times_eaten > 3 else ""
        msg = (f"{Prisma.RED}CROWD CAFFEINE: I chewed on '{target.upper()}'{flavor_text}.{Prisma.RST}\n"
               f"   {Prisma.WHT}Yield: {actual_yield:.1f} ATP.{Prisma.RST}")
        return "MEAT_GRINDER", msg, actual_yield, loot

    def _filter_meat_words(self, clean_words: list, lexicon: Dict) -> list:
        heavy = lexicon.get("heavy")
        kinetic = lexicon.get("kinetic")
        suburban = lexicon.get("suburban")
        heavy = heavy if heavy else []
        kinetic = kinetic if kinetic else []
        suburban = suburban if suburban else []
        return [w for w in clean_words if w in heavy or w in kinetic or w in suburban]

    def _attempt_digest_abstract(self, clean_words: list, lexicon: Dict) -> Tuple[str, str, float, Optional[str]]:
        abstract_set = lexicon.get("abstract")
        abstract_set = abstract_set if abstract_set else []
        abstract_words = [w for w in clean_words if w in abstract_set]
        if abstract_words:
            target = random.choice(abstract_words)
            yield_val = BoneConfig.FOLLY.YIELD_ABSTRACT
            msg = (f"{Prisma.GRY}THE FOLLY SIGHS: It grinds the ABSTRACT concept '{target.upper()}'.{Prisma.RST}\n"
                   f"   {Prisma.GRY}It tastes like chalk dust. +{yield_val} ATP.{Prisma.RST}")
            return "GRUEL", msg, yield_val, None
        msg = (f"{Prisma.OCHRE}INDIGESTION: I tried to eat your words, but they were just air.{Prisma.RST}\n"
               f"   {Prisma.GRY}Cannot grind this input into fuel.{Prisma.RST}\n"
               f"   {Prisma.RED}► STARVATION CONTINUES.{Prisma.RST}")
        return "INDIGESTION", msg, 0.0, None