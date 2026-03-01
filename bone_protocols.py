import os, random, json, re, time
from collections import deque, Counter
from typing import Dict, Tuple, Optional, Any
from bone_core import LoreManifest
from bone_types import Prisma
from bone_lexicon import LexiconService
from bone_config import BoneConfig

NARRATIVE_DATA = LoreManifest.get_instance().get("narrative_data") or {}

class ZenGarden:
    def __init__(self, events_ref):
        self.events = events_ref
        self.stillness_streak = 0
        self.max_streak = 0
        self.pebbles_collected = 0
        self.koans = NARRATIVE_DATA.get(
            "ZEN_KOANS", ["The code that is not written has no bugs."]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stillness_streak": self.stillness_streak,
            "max_streak": self.max_streak,
            "pebbles_collected": self.pebbles_collected,
        }

    def load_state(self, data: Dict[str, Any]):
        self.stillness_streak = data.get("stillness_streak", 0)
        self.max_streak = data.get("max_streak", 0)
        self.pebbles_collected = data.get("pebbles_collected", 0)

    def raking_the_sand(self, physics: Any, _bio: Dict) -> Tuple[float, Optional[str]]:
        vol = (
            getattr(physics, "voltage", 0.0)
            if not isinstance(physics, dict)
            else physics.get("voltage", 0.0)
        )
        drag = (
            getattr(physics, "narrative_drag", 0.0)
            if not isinstance(physics, dict)
            else physics.get("narrative_drag", 0.0)
        )
        is_stable = (
            BoneConfig.ZEN.VOLTAGE_MIN <= vol <= BoneConfig.ZEN.VOLTAGE_MAX
        ) and (drag <= BoneConfig.ZEN.DRAG_MAX)
        if is_stable:
            self.stillness_streak += 1
            if self.stillness_streak > self.max_streak:
                self.max_streak = self.stillness_streak
            efficiency_boost = min(
                BoneConfig.ZEN.EFFICIENCY_CAP,
                self.stillness_streak * BoneConfig.ZEN.EFFICIENCY_SCALAR,
            )
            msg = None
            if self.stillness_streak == 1:
                raw_enter = LoreManifest.get_instance().get_ux(
                    "protocol_strings",
                    "zen_enter",
                    "⛩️ ZEN GARDEN: Entering the quiet zone.",
                )
                msg = f"{Prisma.GRY}{raw_enter}{Prisma.RST}"
            elif self.stillness_streak % 5 == 0:
                self.pebbles_collected += 1
                koan = random.choice(self.koans)
                raw_streak = LoreManifest.get_instance().get_ux(
                    "protocol_strings",
                    "zen_streak",
                    '⛩️ ZEN GARDEN: {streak} ticks of poise.\n   "{koan}" (Efficiency +{boost}%)',
                )
                msg = f"{Prisma.CYN}{raw_streak.format(streak=self.stillness_streak, koan=koan, boost=int(efficiency_boost * 100))}{Prisma.RST}"
            return efficiency_boost, msg
        if self.stillness_streak > BoneConfig.ZEN.STREAK_BREAK_THRESHOLD:
            break_msg = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "zen_break",
                "🍂 ZEN GARDEN: Leaf falls. Turbulence broke the streak.",
            )
            self.events.log(
                f"{Prisma.GRY}{break_msg}{Prisma.RST}",
                "SYS",
            )
        self.stillness_streak = 0
        return 0.0, None


class TheBureau:
    def __init__(self):
        self.stamp_count = 0
        self.forms = NARRATIVE_DATA.get("BUREAU_FORMS", ["Form 27B-6", "Form 404"])
        self.responses = NARRATIVE_DATA.get("BUREAU_RESPONSES", ["Processing..."])
        lex_data = LoreManifest.get_instance().get("LEXICON") or {}
        raw_buzz = (
            lex_data.get("bureau_buzzwords") or lex_data.get("bureau_buzzwords") or []
        )
        self.buzzwords = (
            set(raw_buzz)
            if raw_buzz
            else {"synergy", "paradigm", "leverage", "utilize"}
        )
        self.crimes = []
        self.crime_data = LoreManifest.get_instance().get("STYLE_CRIMES") or {}
        if "PATTERNS" in self.crime_data:
            for p in self.crime_data["PATTERNS"]:
                try:
                    self.crimes.append(
                        {
                            "name": p.get("name", "Unknown Violation"),
                            "regex": re.compile(p["regex"], re.IGNORECASE),
                            "msg": p.get("error_msg", "Style Violation Detected."),
                            "tax": float(p.get("tax", 5.0)),
                            "action": p.get("action", None),
                        }
                    )
                except re.error as e:
                    err_msg = LoreManifest.get_instance().get_ux(
                        "protocol_strings",
                        "bureau_compile_fail",
                        "[BUREAU]: Failed to compile law '{name}': {e}",
                    )
                    print(
                        f"{Prisma.RED}{err_msg.format(name=p.get('name'), e=e)}{Prisma.RST}"
                    )
        scenarios = LoreManifest.get_instance().get("scenarios") or {}
        self.cliches = set(scenarios.get("BANNED_CLICHES", []))

    def to_dict(self) -> Dict[str, Any]:
        return {"stamp_count": self.stamp_count}

    def load_state(self, data: Dict[str, Any]):
        self.stamp_count = data.get("stamp_count", 0)

    def audit(self, physics, bio_state, _context=None, origin="USER") -> Optional[Dict]:
        if bio_state.get("health", 100.0) < BoneConfig.BUREAU.MIN_HEALTH_TO_AUDIT:
            return None

        def _get(p, k, d=0.0):
            return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

        vol = _get(physics, "voltage", 0.0)
        clean_words = _get(physics, "clean_words", [])
        raw_text = _get(physics, "raw_text", "")
        truth = _get(physics, "truth_ratio", 0.0)
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
                    evidence.append(crime["msg"])
                    tax += crime["tax"]
                    break
        if not selected_form and vol > BoneConfig.BUREAU.HIGH_VOLTAGE_TRIGGER:
            if truth < BoneConfig.BUREAU.LOW_TRUTH_TRIGGER:
                selected_form = "ZONING_VIOLATION"
                evidence = ["Excessive Voltage", "Unlicensed Fiction"]
                tax = BoneConfig.BUREAU.TAX_HEAVY
            else:
                selected_form = "Form 202-A"
                tax = BoneConfig.BUREAU.TAX_STANDARD
        chi = _get(physics, "chi", _get(physics, "entropy", 0.0))
        if not selected_form and chi > 0.6:
            selected_form = "Form 666: Unlicensed Chaos"
            evidence = ["Unlicensed Chaos (Χ > 0.6)", f"Level: {chi:.2f}"]
            tax = 12.0
        elif not selected_form:
            buzz_hits = [w for w in clean_words if w in self.buzzwords]
            cliche_hits = [c for c in self.cliches if c.lower() in raw_text.lower()]
            if buzz_hits:
                selected_form = random.choice(self.forms)
                evidence = buzz_hits
                tax = BoneConfig.BUREAU.TAX_STANDARD
            elif cliche_hits:
                selected_form = "Form 101: Derivative Content"
                evidence = cliche_hits
                tax = BoneConfig.BUREAU.TAX_HEAVY

        if not selected_form:
            return None
        self.stamp_count += 1
        bureau_resp = random.choice(self.responses)
        prefix = f"{Prisma.GRY}{LoreManifest.get_instance().get_ux('protocol_strings', 'bureau_prefix_normal', '🏢 THE BUREAU')}"
        if origin == "SYSTEM":
            prefix = f"{Prisma.RED}{LoreManifest.get_instance().get_ux('protocol_strings', 'bureau_prefix_internal', '🏢 INTERNAL AFFAIRS')}"
            bureau_resp = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "bureau_sys_violation",
                "System Output Violation detected.",
            )
        filed_msg = LoreManifest.get_instance().get_ux(
            "protocol_strings", "bureau_filed", "[Filed: {form} against {origin}]"
        )
        ui_msg = f"{prefix}: {bureau_resp}{Prisma.RST}\n   {Prisma.WHT}{filed_msg.format(form=selected_form, origin=origin)}{Prisma.RST}"
        if evidence:
            ev_msg = LoreManifest.get_instance().get_ux(
                "protocol_strings", "bureau_evidence", "Evidence: {evidence}"
            )
            ui_msg += f"\n   {Prisma.RED}{ev_msg.format(evidence=', '.join(evidence))}{Prisma.RST}"
        log_msg = LoreManifest.get_instance().get_ux(
            "protocol_strings",
            "bureau_log",
            "BUREAUCRACY: Filed {form} against {origin}. Chaos Tax: -{tax:.1f} ATP.",
        )
        return {
            "status": "AUDITED",
            "ui": ui_msg,
            "log": log_msg.format(form=selected_form, origin=origin, tax=tax),
            "atp_gain": -tax,
        }

    @staticmethod
    def _apply_correction(text: str, crime: Dict, match: re.Match) -> str:
        action = crime.get("action")
        if not action:
            return text
        if action == "KEEP_TAIL":
            idx = match.lastindex
            if idx is not None:
                segment = match.group(idx)
                if isinstance(segment, str):
                    return segment.strip()
        elif action == "STRIP_PREFIX":
            if len(match.groups()) >= 3:
                p_val = match.group(1)
                s_val = match.group(3)
                prefix = p_val if isinstance(p_val, str) else ""
                suffix = s_val if isinstance(s_val, str) else ""
                if not prefix.strip() and suffix:
                    suffix = suffix[0].upper() + suffix[1:]
                return f"{prefix}{suffix}".strip()
        return text

    def sanitize(self, text: str) -> Tuple[str, Optional[str]]:
        for crime in self.crimes:
            match = crime["regex"].search(text)
            if match and crime.get("action"):
                corrected_text = self._apply_correction(text, crime, match)
                corr_msg = LoreManifest.get_instance().get_ux(
                    "protocol_strings",
                    "bureau_correction",
                    "BUREAU CORRECTION: {msg} -> Text optimized.",
                )
                log_msg = corr_msg.format(msg=crime["msg"])
                return corrected_text, log_msg
        dummy_physics = type(
            "obj",
            (object,),
            {"voltage": 0.0, "raw_text": text, "clean_words": text.split()},
        )
        dummy_bio = {"health": 100.0}
        result = self.audit(dummy_physics, dummy_bio, origin="SYSTEM")
        if result:
            return text, result.get("log")
        return text, None


class TherapyProtocol:
    def __init__(self):
        default_vector = {"SEPTIC": 0, "EXHAUSTION": 0, "PARANOIA": 0}
        vector_keys = getattr(BoneConfig, "TRAUMA_VECTOR", default_vector).keys()
        self.streaks = {k: 0 for k in vector_keys}
        self.HEALING_THRESHOLD = 5

    def to_dict(self) -> Dict[str, Any]:
        return {"streaks": self.streaks}

    def load_state(self, data: Dict[str, Any]):
        self.streaks = data.get(
            "streaks", {k: 0 for k in BoneConfig.TRAUMA_VECTOR.keys()}
        )

    def check_progress(self, phys, _stamina, current_trauma_accum, _qualia=None):
        counts = (
            getattr(phys, "counts", {})
            if not isinstance(phys, dict)
            else phys.get("counts", {})
        )
        vector = (
            getattr(phys, "vector", {})
            if not isinstance(phys, dict)
            else phys.get("vector", {})
        )
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
                if current_trauma_accum.get(trauma_type, 0.0) > 0.0:
                    current_trauma_accum[trauma_type] = max(
                        0.0, current_trauma_accum[trauma_type] - 0.5
                    )
                    healed_types.append(trauma_type)
        return healed_types


class KintsugiProtocol:
    PATH_SCAR = "SCAR"
    PATH_INTEGRATION = "KINTSUGI"
    PATH_ALCHEMY = "ALCHEMY"

    def __init__(self):
        self.active_koan = None
        self.koans = NARRATIVE_DATA.get(
            "KINTSUGI_KOANS", ["The crack is where the light enters."]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"active_koan": self.active_koan}

    def load_state(self, data: Dict[str, Any]):
        self.active_koan = data.get("active_koan", None)

    def check_integrity(self, stamina):
        if stamina < 15.0 and not self.active_koan:
            self.active_koan = random.choice(self.koans)
            return True, self.active_koan
        return False, None

    def attempt_repair(self, phys, trauma_accum, soul_ref=None, _qualia=None):
        if not self.active_koan:
            return None
        vol = getattr(phys, "voltage", 0.0)
        clean = LexiconService.sanitize(getattr(phys, "raw_text", ""))
        play_count = sum(
            1
            for w in clean
            if w in LexiconService.get("play") or w in LexiconService.get("abstract")
        )
        whimsy_score = play_count / max(1, len(clean))
        pathway = self.PATH_SCAR
        if vol > 15.0 and whimsy_score > 0.4:
            pathway = self.PATH_ALCHEMY
        elif vol > 8.0 and whimsy_score > 0.2:
            pathway = self.PATH_INTEGRATION
        return self._execute_pathway(pathway, trauma_accum, soul_ref)

    def _execute_pathway(self, pathway, trauma_accum, soul_ref):
        if not trauma_accum:
            return {
                "success": False,
                "msg": LoreManifest.get_instance().get_ux(
                    "protocol_strings", "kintsugi_no_fissures", "No fissures found."
                ),
            }
        target = max(trauma_accum, key=trauma_accum.get)
        severity = trauma_accum[target]
        healed_log = []

        if pathway == self.PATH_ALCHEMY:
            reduction = severity * 0.8
            trauma_accum[target] = max(0.0, severity - reduction)
            atp_boost = reduction * 15.0
            msg_raw = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "kintsugi_alchemy",
                "🔮 ALCHEMY: The wound '{target}' burns into pure fuel. (+{boost:.1f} ATP)",
            )
            msg = f"{Prisma.VIOLET}{msg_raw.format(target=target, boost=atp_boost)}{Prisma.RST}"
            healed_log.append(f"Transmuted {target}")
            return {
                "success": True,
                "msg": msg,
                "healed": healed_log,
                "atp_gain": atp_boost,
            }
        elif pathway == self.PATH_INTEGRATION:
            reduction = 2.0
            trauma_accum[target] = max(0.0, severity - reduction)
            if soul_ref:
                soul_ref.traits.adjust("WISDOM", 0.1)
                healed_log.append("Wisdom +0.1")
            msg_raw = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "kintsugi_mercy",
                "🏺 MERCY (KINTSUGI): The gold sets. The '{target}' crack becomes a story.",
            )
            msg = f"{Prisma.OCHRE}{msg_raw.format(target=target)}{Prisma.RST}"
            healed_log.append(f"Integrated {target}")
            success = True
        else:
            reduction = 0.5
            trauma_accum[target] = max(0.0, severity - reduction)
            msg_raw = LoreManifest.get_instance().get_ux(
                "protocol_strings", "kintsugi_scar", "🩹 SCAR: It's ugly, but it holds."
            )
            msg = f"{Prisma.GRY}{msg_raw}{Prisma.RST}"
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
        return {
            "active_cooldowns": self.active_cooldowns,
            "last_review_turn": self.last_review_turn,
        }

    def load_state(self, data):
        self.active_cooldowns = data.get("active_cooldowns", {})
        self.last_review_turn = data.get("last_review_turn", 0)

    def audit_performance(self, physics: Any, turn_count: int) -> Optional[str]:
        if turn_count - self.last_review_turn < 10:
            return None
        p = physics if isinstance(physics, dict) else getattr(physics, "__dict__", {})
        voltage = p.get("voltage", 0.0)
        drag = p.get("narrative_drag", 0.0)
        if "velocity" not in p:
            p["velocity"] = voltage * (1.0 / max(0.1, drag))
        best_match = None
        review_type = "neutral"

        for key, critic in self.critics.items():
            if self.active_cooldowns.get(key, 0) > turn_count:
                continue
            prefs = critic.get("preferences", {})
            score = 0.0
            for metric, target in prefs.items():
                metric_str = str(metric)
                if metric_str.startswith("counts_"):
                    category = metric_str.replace("counts_", "")
                    counts = p.get("counts", {})
                    raw_count = counts.get(category, 0)
                    current = min(5.0, raw_count * 0.5)
                else:
                    current = p.get(metric_str, 0.0)
                if target > 0:
                    score += current * target
                else:
                    score -= current * abs(target)

            if score > 15.0:
                best_match = (key, critic)
                review_type = "high"
            elif score < -15.0:
                best_match = (key, critic)
                review_type = "low"

        if best_match:
            key, critic = best_match
            self.last_review_turn = turn_count
            self.active_cooldowns[key] = turn_count + 50
            reviews = critic["reviews"].get(review_type, ["Hrm."])
            comment = random.choice(reviews)
            color = Prisma.GRN if review_type == "high" else Prisma.RED
            icon = "🌟" if review_type == "high" else "💢"
            rev_msg = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "critic_review",
                '{icon} CRITIC REVIEW ({name}): "{comment}"',
            )
            return f"{color}{rev_msg.format(icon=icon, name=critic['name'], comment=comment)}{Prisma.RST}"
        return None


class LimboLayer:
    MAX_ECTOPLASM = 50
    STASIS_SCREAMS = NARRATIVE_DATA.get(
        "CASSANDRA_SCREAMS", ["BANGING ON THE GLASS", "IT'S TOO COLD", "LET ME OUT"]
    )

    def __init__(self):
        self.ghosts = deque(maxlen=self.MAX_ECTOPLASM)
        self.haunt_chance = 0.05
        self.stasis_leak = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {"ghosts": list(self.ghosts), "stasis_leak": self.stasis_leak}

    def load_state(self, data: Dict[str, Any]):
        self.ghosts = deque(data.get("ghosts", []), maxlen=self.MAX_ECTOPLASM)
        self.stasis_leak = data.get("stasis_leak", 0.0)

    def absorb_dead_timeline(self, filepath: str) -> None:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            self._extract_ghosts(data)
        except (IOError, json.JSONDecodeError) as e:
            err_msg = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "limbo_absorb_fail",
                "[LIMBO] Failed to absorb timeline '{filepath}': {e}",
            )
            print(f"{Prisma.RED}{err_msg.format(filepath=filepath, e=e)}{Prisma.RST}")

    def _extract_ghosts(self, data: Dict[str, Any]) -> None:
        if "trauma_vector" in data:
            for k, v in data["trauma_vector"].items():
                if v > 0.3:
                    echo_msg = LoreManifest.get_instance().get_ux("protocol_strings", "limbo_echo", "👻{k}_ECHO")
                    self.ghosts.append(echo_msg.format(k=k))
        if "mutations" in data and "heavy" in data["mutations"]:
            bones = list(data["mutations"]["heavy"])
            random.shuffle(bones)
            self.ghosts.extend(bones[:3])

    def trigger_stasis_failure(self, intended_thought):
        self.stasis_leak += 1.0
        horror = random.choice(self.STASIS_SCREAMS)
        self.ghosts.append(f"{Prisma.VIOLET}{horror}{Prisma.RST}")
        err_msg = LoreManifest.get_instance().get_ux(
            "protocol_strings",
            "limbo_stasis_err",
            "STASIS ERROR: '{thought}' froze halfway. {horror}.",
        )
        return f"{Prisma.CYN}{err_msg.format(thought=intended_thought, horror=horror)}{Prisma.RST}"

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
        self.gut_memory = deque(maxlen=50)
        self.global_tastings = Counter()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gut_memory": list(self.gut_memory),
            "global_tastings": dict(self.global_tastings),
        }

    def load_state(self, data: Dict[str, Any]):
        self.gut_memory = deque(data.get("gut_memory", []), maxlen=50)
        self.global_tastings = Counter(data.get("global_tastings", {}))

    @staticmethod
    def audit_desire(physics, stamina):
        def _get(p, k, d=0.0):
            return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

        voltage = _get(physics, "voltage", 0.0)
        if (
            voltage > BoneConfig.FOLLY.MAUSOLEUM_VOLTAGE
            and stamina > BoneConfig.FOLLY.MAUSOLEUM_STAMINA
        ):
            msg1 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "folly_mausoleum",
                "THE MAUSOLEUM: No battle is ever won. We are just spinning hands.",
            )
            msg2 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "folly_dilation",
                "TIME DILATION: Voltage 0.0. The field reveals your folly.",
            )
            return (
                "MAUSOLEUM_CLAMP",
                f"{Prisma.GRY}{msg1}{Prisma.RST}\n   {Prisma.CYN}{msg2}{Prisma.RST}",
                0.0,
                None,
            )
        return None, None, 0.0, None

    def grind_the_machine(
        self, atp_pool: float, clean_words: list, lexicon: Dict
    ) -> Tuple[Optional[str], Optional[str], float, Optional[str]]:
        if not (0.0 < atp_pool < BoneConfig.FOLLY.FEEDING_CAP):
            return None, None, 0.0, None
        meat_words = self._filter_meat_words(clean_words, lexicon)
        if not meat_words:
            return self._attempt_digest_abstract(clean_words, lexicon)
        fresh_meat = [w for w in meat_words if w not in self.gut_memory]
        if not fresh_meat:
            target = meat_words[0]
            msg1 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "folly_reflex",
                "REFLEX: You already fed me '{target}'. It is ash to me now.",
            )
            msg2 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "folly_penalty",
                "► PENALTY: -{penalty} ATP. Find new fuel.",
            )
            msg = (
                f"{Prisma.OCHRE}{msg1.format(target=target)}{Prisma.RST}\n"
                f"   {Prisma.RED}{msg2.format(penalty=BoneConfig.FOLLY.PENALTY_REGURGITATION)}{Prisma.RST}"
            )
            return "REGURGITATION", msg, -BoneConfig.FOLLY.PENALTY_REGURGITATION, None
        return self._eat_meat(fresh_meat, lexicon)

    def _eat_meat(
        self, fresh_meat: list, _lexicon_data: Dict
    ) -> Tuple[str, str, float, Optional[str]]:
        target = random.choice(fresh_meat)
        suburban_set = LexiconService.get("suburban")
        suburban_set = suburban_set if suburban_set else []
        play_set = LexiconService.get("play")
        play_set = play_set if play_set else []
        self.gut_memory.append(target)
        self.global_tastings[target] += 1
        if target in suburban_set:
            gags = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "folly_gags",
                "THE FOLLY GAGS: It coughs up a piece of office equipment.",
            )
            return (
                "INDIGESTION",
                f"{Prisma.MAG}{gags}{Prisma.RST}",
                -BoneConfig.FOLLY.PENALTY_INDIGESTION,
                "THE_RED_STAPLER",
            )
        if target in play_set:
            chews = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "folly_chews",
                "THE FOLLY CHEWS: It compresses the chaos into a small, sticky ball.",
            )
            return (
                "SUGAR_RUSH",
                f"{Prisma.VIOLET}{chews}{Prisma.RST}",
                BoneConfig.FOLLY.SUGAR_RUSH_YIELD,
                "QUANTUM_GUM",
            )
        times_eaten = self.global_tastings[target]
        base_yield = BoneConfig.FOLLY.BASE_YIELD
        decay_factor = BoneConfig.FOLLY.DECAY_EXPONENT ** (times_eaten - 1)
        actual_yield = max(2.0, base_yield * decay_factor)
        loot = (
            "STABILITY_PIZZA"
            if actual_yield >= BoneConfig.FOLLY.PIZZA_THRESHOLD
            else None
        )
        flavor_text = f" (Stale: {times_eaten}x)" if times_eaten > 3 else ""
        msg1 = LoreManifest.get_instance().get_ux(
            "protocol_strings",
            "folly_caffeine",
            "CROWD CAFFEINE: I chewed on '{target}'{flavor_text}.",
        )
        msg2 = LoreManifest.get_instance().get_ux("protocol_strings", "folly_yield", "Yield: {yield_val:.1f} ATP.")
        msg = (
            f"{Prisma.RED}{msg1.format(target=target.upper(), flavor_text=flavor_text)}{Prisma.RST}\n"
            f"   {Prisma.WHT}{msg2.format(yield_val=actual_yield)}{Prisma.RST}"
        )
        return "MEAT_GRINDER", msg, actual_yield, loot

    @staticmethod
    def _filter_meat_words(clean_words: list, _lexicon: Dict) -> list:
        meat_pool = (
            set(LexiconService.get("heavy") or [])
            | set(LexiconService.get("kinetic") or [])
            | set(LexiconService.get("suburban") or [])
        )
        return [w for w in clean_words if w in meat_pool]

    @staticmethod
    def _attempt_digest_abstract(
        clean_words: list, _lexicon: Dict
    ) -> Tuple[str, str, float, Optional[str]]:
        abstract_set = LexiconService.get("abstract")
        abstract_set = abstract_set if abstract_set else []
        abstract_words = [w for w in clean_words if w in abstract_set]
        if abstract_words:
            target = random.choice(abstract_words)
            yield_val = BoneConfig.FOLLY.YIELD_ABSTRACT
            msg1 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "folly_sighs",
                "THE FOLLY SIGHS: It grinds the ABSTRACT concept '{target}'.",
            )
            msg2 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "folly_chalk",
                "It tastes like chalk dust. +{yield_val} ATP.",
            )
            msg = (
                f"{Prisma.GRY}{msg1.format(target=target.upper())}{Prisma.RST}\n"
                f"   {Prisma.GRY}{msg2.format(yield_val=yield_val)}{Prisma.RST}"
            )
            return "GRUEL", msg, yield_val, None
        msg1 = LoreManifest.get_instance().get_ux(
            "protocol_strings",
            "folly_indigestion",
            "INDIGESTION: I tried to eat your words, but they were just air.",
        )
        msg2 = LoreManifest.get_instance().get_ux(
            "protocol_strings",
            "folly_cannot_grind",
            "Cannot grind this input into fuel.",
        )
        msg3 = LoreManifest.get_instance().get_ux(
            "protocol_strings", "folly_starvation", "► STARVATION CONTINUES."
        )
        msg = (
            f"{Prisma.OCHRE}{msg1}{Prisma.RST}\n"
            f"   {Prisma.GRY}{msg2}{Prisma.RST}\n"
            f"   {Prisma.RED}{msg3}{Prisma.RST}"
        )
        return "INDIGESTION", msg, 0.0, None


class ChronosKeeper:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.SAVE_DIR = "saves"
        self.CRASH_DIR = "crashes"

    def save_checkpoint(self, history: list = None) -> str:
        try:
            if not os.path.exists(self.SAVE_DIR):
                os.makedirs(self.SAVE_DIR)

            loc = "Void"
            if (
                hasattr(self.eng, "phys")
                and hasattr(self.eng.phys, "observer")
                and getattr(self.eng.phys.observer, "last_physics_packet", None)
            ):
                loc = getattr(
                    self.eng.phys.observer.last_physics_packet, "zone", "Void"
                )

            last_speech = "Silence."
            if self.eng.cortex.dialogue_buffer:
                last_speech = self.eng.cortex.dialogue_buffer[-1]
            continuity_packet = {
                "location": loc,
                "last_output": last_speech,
                "inventory": self.eng.gordon.inventory if self.eng.gordon else [],
            }
            start_history = (
                history if history is not None else self.eng.cortex.dialogue_buffer
            )
            state_data = {
                "health": self.eng.health,
                "stamina": self.eng.stamina,
                "trauma_accum": self.eng.trauma_accum,
                "soul_data": self.eng.soul.to_dict(),
                "village_data": self._gather_village_state(),
                "continuity": continuity_packet,
                "timestamp": time.time(),
                "chat_history": start_history,
            }
            path = os.path.join(self.SAVE_DIR, "quicksave.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2, default=str)
            msg_save = LoreManifest.get_instance().get_ux(
                "protocol_strings", "chronos_save_success", "✔ Checkpoint Saved: {path}"
            )
            return msg_save.format(path=path)
        except Exception as e:
            self.eng.events.log(
                LoreManifest.get_instance().get_ux(
                    "protocol_strings", "chronos_save_failed_log", "SAVE FAILED: {e}"
                ).format(e=e),
                "SYS_ERR",
            )
            return LoreManifest.get_instance().get_ux(
                "protocol_strings", "chronos_save_failed_msg", "❌ Save Failed: {e}"
            ).format(e=e)

    def resume_checkpoint(self) -> Tuple[bool, list]:
        path = os.path.join(self.SAVE_DIR, "quicksave.json")
        if not os.path.exists(path):
            msg = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "chronos_resume_none",
                "[RESUME]: No quicksave found. Starting fresh.",
            )
            print(f"{Prisma.GRY}{msg}{Prisma.RST}")
            return False, []
        try:
            msg1 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "chronos_resume_hydrating",
                "[RESUME]: Hydrating from {path}...",
            )
            print(f"{Prisma.CYN}{msg1.format(path=path)}{Prisma.RST}")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.eng.health = data.get("health", 100.0)
            self.eng.stamina = data.get("stamina", 100.0)
            self.eng.trauma_accum = data.get("trauma_accum", {})
            if "soul_data" in data and hasattr(self.eng, "soul"):
                self.eng.soul.load_from_dict(data["soul_data"])
            if "village_data" in data:
                self._restore_village_state(data["village_data"])
            if "continuity" in data:
                self.eng.embryo.continuity = data["continuity"]
                if "inventory" in data["continuity"] and self.eng.gordon:
                    self.eng.gordon.inventory = data["continuity"]["inventory"]
            restored_history = data.get("chat_history", [])
            msg2 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "chronos_resume_success",
                "[RESUME]: System State & Logs Restored.",
            )
            print(f"{Prisma.GRN}{msg2}{Prisma.RST}")
            return True, restored_history
        except Exception as e:
            msg3 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "chronos_resume_failed",
                "[RESUME]: Failed to hydrate: {e}",
            )
            print(f"{Prisma.RED}{msg3.format(e=e)}{Prisma.RST}")
            return False, []

    def perform_shutdown(self):
        msg = LoreManifest.get_instance().get_ux("protocol_strings", "chronos_halt", "...System Halt...")
        print(f"{Prisma.GRY}{msg}{Prisma.RST}")
        self.eng.events.publish("SYSTEM_HALT", {"tick": self.eng.tick_count})

        loc = "Void"
        if (
            hasattr(self.eng, "phys")
            and hasattr(self.eng.phys, "observer")
            and getattr(self.eng.phys.observer, "last_physics_packet", None)
        ):
            loc = getattr(self.eng.phys.observer.last_physics_packet, "zone", "Void")

        continuity_packet = {
            "location": loc,
            "last_output": (
                self.eng.cortex.dialogue_buffer[-1]
                if self.eng.cortex.dialogue_buffer
                else "Silence."
            ),
            "inventory": self.eng.gordon.inventory if self.eng.gordon else [],
        }
        try:
            msg2 = LoreManifest.get_instance().get_ux(
                "protocol_strings", "chronos_freezing", "[MEMORY]: Freezing State..."
            )
            print(f"{Prisma.GRY}{msg2}{Prisma.RST}")
            mito_traits = {}
            if hasattr(self.eng.bio.mito, "state"):
                mito_traits = self.eng.bio.mito.state.__dict__
            self.eng.mind.mem.save(
                health=self.eng.health,
                stamina=self.eng.stamina,
                mutations={},
                trauma_accum=self.eng.trauma_accum,
                joy_history=[],
                mitochondria_traits=mito_traits,
                antibodies=list(self.eng.bio.immune.active_antibodies),
                soul_data=self.eng.soul.to_dict(),
                village_data=self._gather_village_state(),
                continuity=continuity_packet,
                world_atlas=(
                    self.eng.phys.nav.export_atlas()
                    if hasattr(self.eng.phys, "nav")
                    else {}
                ),
            )
        except Exception as e:
            msg3 = LoreManifest.get_instance().get_ux(
                "protocol_strings",
                "chronos_mem_save_fail",
                "[MEMORY]: Save Failed: {e}",
            )
            print(f"{Prisma.RED}{msg3.format(e=e)}{Prisma.RST}")
        subsystems = [
            ("LEXICON", self.eng.lex, "save"),
            ("AKASHIC", self.eng.akashic, "save_all"),
        ]
        for name, sys, method in subsystems:
            if hasattr(sys, method):
                try:
                    msg4 = LoreManifest.get_instance().get_ux(
                        "protocol_strings",
                        "chronos_persisting",
                        "[{name}]: Persisting...",
                    )
                    print(f"{Prisma.GRY}{msg4.format(name=name)}{Prisma.RST}")
                    getattr(sys, method)()
                except Exception as e:
                    msg5 = LoreManifest.get_instance().get_ux(
                        "protocol_strings",
                        "chronos_persist_fail",
                        "[{name}]: Failed: {e}",
                    )
                    print(f"{Prisma.RED}{msg5.format(name=name, e=e)}{Prisma.RST}")

    def _gather_village_state(self) -> Dict[str, Any]:
        state = {}
        for name, component in self.eng.village.items():
            if component and hasattr(component, "to_dict"):
                state[name] = component.to_dict()
        return state

    def _restore_village_state(self, state_data: Dict[str, Any]):
        if not state_data:
            return
        for name, data in state_data.items():
            if (
                name in self.eng.village
                and self.eng.village[name]
                and hasattr(self.eng.village[name], "load_state")
            ):
                try:
                    self.eng.village[name].load_state(data)
                except Exception as e:
                    msg = LoreManifest.get_instance().get_ux(
                        "protocol_strings",
                        "chronos_hydrate_fail",
                        "[RESUME]: Failed to hydrate {name}: {e}",
                    )
                    print(f"{Prisma.RED}{msg.format(name=name, e=e)}{Prisma.RST}")

    def get_crash_path(self, prefix="crash"):
        if not os.path.exists(self.CRASH_DIR):
            try:
                os.makedirs(self.CRASH_DIR)
            except OSError:
                pass
        try:
            files = sorted(
                [f for f in os.listdir(self.CRASH_DIR) if f.startswith(prefix)]
            )
            for oldest in files[:-4]:
                os.remove(os.path.join(self.CRASH_DIR, oldest))
        except Exception:
            pass
        return os.path.join(self.CRASH_DIR, f"{prefix}_{int(time.time())}.json")

    @staticmethod
    def emergency_dump(exit_cause="UNKNOWN") -> str:
        msg = LoreManifest.get_instance().get_ux(
            "protocol_strings", "chronos_emerg_dump", "✔ Emergency Dump: {exit_cause}"
        )
        return msg.format(exit_cause=exit_cause)
