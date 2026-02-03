""" bone_personality.py - 'The masks we wear, and the taxes we pay.' """

import json, os, random, time
from collections import deque
from typing import Dict, Tuple, Optional, Counter
from bone_data import LENSES, NARRATIVE_DATA
from bone_bus import EventBus
from bone_lexicon import TheLexicon
from bone_bus import Prisma, BoneConfig
from bone_data import SANCTUARY

class UserProfile:
    def __init__(self, name="USER"):
        self.name = name
        self.affinities = {"heavy": 0.0, "kinetic": 0.0, "abstract": 0.0, "photo": 0.0, "aerobic": 0.0, "thermal": 0.0,
                           "cryo": 0.0, }
        self.confidence = 0
        self.file_path = "user_profile.json"
        self.load()

    def update(self, counts, total_words):
        if total_words < 3:
            return
        self.confidence += 1
        alpha = 0.2 if self.confidence < 50 else 0.05
        for cat in self.affinities:
            density = counts.get(cat, 0) / total_words
            target = 1.0 if density > 0.15 else (-0.5 if density == 0 else 0.0)
            self.affinities[cat] = (alpha * target) + (
                    (1 - alpha) * self.affinities[cat])

    def get_preferences(self):
        likes = [k for k, v in self.affinities.items() if v > 0.3]
        hates = [k for k, v in self.affinities.items() if v < -0.2]
        return likes, hates

    def save(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.__dict__, f)
        except IOError:
            pass

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.affinities = data.get("affinities", self.affinities)
                    self.confidence = data.get("confidence", 0)
            except (IOError, json.JSONDecodeError):
                pass

class EnneagramDriver:
    def __init__(self, events_ref):
        self.events = events_ref
        self.current_persona = "NARRATOR"
        self.pending_persona = None
        self.stability_counter = 0
        self.HYSTERESIS_THRESHOLD = 3
        self.WEIGHTS = {
            "JESTER":   {"tension_min": 12.0, "vectors": {"DEL": 3.0, "ENT": 3.0, "PSI": -3.0}},
            "GORDON":   {"drag_min": 4.0,     "vectors": {"STR": 2.0, "E": 2.0}},
            "GLASS":    {"coherence_max": 0.2,"vectors": {"LQ": 2.0}},
            "CLARENCE": {"coherence_min": 0.8,"vectors": {"STR": 4.0, "BET": 2.0}},
            "NATHAN":   {"tension_min": 8.0,  "vectors": {"TMP": 3.0, "PHI": 1.0}},
            "SHERLOCK": {"tension_min": 10.0, "vectors": {"PHI": 4.0, "VEL": 2.0}},
            "NARRATOR": {"safe_zone": True,   "vectors": {"PSI": 4.0}}}

    def _calculate_raw_persona(self, physics) -> Tuple[str, str, str]:
        if isinstance(physics, dict):
            p_vec = physics.get("vector", {})
            p_vol = physics.get("voltage", 0.0)
            p_drag = physics.get("narrative_drag", 0.0)
            p_coh = physics.get("kappa", 0.0)
            p_zone = physics.get("zone", "")
        else:
            p_vec = getattr(physics, "vector", {})
            p_vol = getattr(physics, "voltage", 0.0)
            p_drag = getattr(physics, "narrative_drag", 0.0)
            p_coh = getattr(physics, "kappa", 0.0)
            p_zone = getattr(physics, "zone", "")
        scores = {k: 0 for k in self.WEIGHTS.keys()}
        scores["NARRATOR"] += 2
        is_safe_metrics = (4.0 <= p_vol <= 10.0 and 0.5 <= p_drag <= 3.5)
        if p_zone == SANCTUARY.ZONE or is_safe_metrics:
            scores["NARRATOR"] += 6
            scores["JESTER"] += 3
            scores["GORDON"] -= 2
        for persona, criteria in self.WEIGHTS.items():
            if "tension_min" in criteria and p_vol > criteria["tension_min"]:
                scores[persona] += 3
            if "drag_min" in criteria and p_drag > criteria["drag_min"]:
                scores[persona] += 5
            if "coherence_min" in criteria and p_coh > criteria["coherence_min"]:
                scores[persona] += 4
            if "coherence_max" in criteria and p_coh < criteria["coherence_max"]:
                scores[persona] += 4
            for dim, weight in criteria.get("vectors", {}).items():
                val = p_vec.get(dim, 0.0)
                if val > 0.2: # Noise floor
                    scores[persona] += val * weight
        winner = max(scores, key=scores.get)
        reason = f"Scoring Winner: {winner} (Score: {scores[winner]:.1f}) [V:{p_vol:.1f}]"
        state_desc = "ACTIVE"
        if winner == "JESTER": state_desc = "MANIC"
        elif winner == "GORDON": state_desc = "TIRED"
        elif winner == "GLASS": state_desc = "FRAGILE"
        elif winner == "CLARENCE": state_desc = "RIGID"
        return winner, state_desc, reason
    def decide_persona(self, physics) -> Tuple[str, str, str]:
        candidate, state_desc, reason = self._calculate_raw_persona(physics)
        if candidate == self.current_persona:
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, reason
        if candidate == self.pending_persona:
            self.stability_counter += 1
        else:
            self.pending_persona = candidate
            self.stability_counter = 1
        if self.stability_counter >= self.HYSTERESIS_THRESHOLD:
            self.current_persona = candidate
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, f"SHIFT: {reason}"
        else:
            return self.current_persona, "STABLE", f"Resisting shift to {candidate} ({self.stability_counter}/{self.HYSTERESIS_THRESHOLD})"

class SynergeticLensArbiter:
    def __init__(self, events: EventBus):
        self.events = events
        self.enneagram = EnneagramDriver(events)
        self.current_focus = "NARRATOR"
        self.last_reason = "System Init"

    def consult(self, physics, bio_state, _inventory, current_tick, _ignition_score=0.0):
        voltage = physics.get("voltage", 0.0) if isinstance(physics, dict) else physics.voltage
        if current_tick <= 5:
            seeds = []
            for cat in ["heavy", "aerobic", "thermal"]:
                options = TheLexicon.get(cat)
                if options:
                    seeds.append(random.choice(list(options)))
            if not seeds: seeds = ["Rust", "Cloud", "Ember"]
            seed_str = ", ".join([s.upper() for s in seeds])
            self.current_focus = "NARRATOR"
            return {
                "lens": "GAME_MASTER",
                "role": "The Architect [World Builder]",
                "style_directives": [
                    "You are a creative, welcoming Game Master.",
                    "FIRST TICK SETUP: You must improvise a unique environment.",
                    f"SUGGESTED MOTIFS: {seed_str} (Use these as inspiration for the vibe, do not force them).",
                    "MODE: SYSTEM_BOOT.",
                    "FIRST TICK INSTRUCTION: Welcome the user, then give a brief but vivid description of the location.",
                    "STYLE: Grounded, atmospheric, concise, observant.",
                    "NEGATIVE CONSTRAINTS: Please do not break the fourth wall. "
                    "Do NOT treat senses as a checklist. "
                    "Do NOT mention the user's inventory or equipment unless asked. "
                    "Do NOT use flowery, cliche metaphors (e.g. 'tapestry', 'dance', 'symphony')."],
                "context_msg": "System Boot."}

        lens_name, state_desc, reason = self.enneagram.decide_persona(physics)
        chem = bio_state.get("chem", {})
        adrenaline_val = chem.get("adrenaline", chem.get("ADR", 0.5))
        style_data = self._fetch_style_data(lens_name, physics, adrenaline_val)
        self.current_focus = lens_name
        self.last_reason = reason
        return {
            "lens": lens_name,
            "role": f"{style_data['role_name']} [{state_desc}]",
            "style_directives": style_data['directives'],
            "lexicon_bias": style_data['vocab'],
            "context_msg": style_data['msg']}

    def _fetch_style_data(self, lens, p, adrenaline_val):
        if lens not in LENSES:
            lens = "NARRATOR"
        static_data = LENSES[lens]
        style_packet = {
            "role_name": static_data.get("role", "Unknown"),
            "vocab": static_data.get("vocab", "abstract"),
            "directives": static_data.get("directives", ["Be neutral."]).copy(),
            "msg": "Proceed."}
        voltage = p.get("voltage", 0.0)
        if voltage > 20.0:
            style_packet["directives"].append("Use fragmented, manic sentence structures.")
            style_packet["directives"].append("Ignore punctuation rules.")
        elif voltage > 12.0:
            style_packet["directives"].append("Keep sentences short and punchy.")
        elif voltage < 5.0:
            style_packet["directives"].append("Use slow, languid pacing.")
            style_packet["directives"].append("Drift into philosophical abstraction.")
        try:
            msg_template = static_data.get("msg", "Proceed.")
            ctx = {
                "kappa": p.get("kappa", 0.0),
                "truth_ratio": p.get("truth_ratio", 0.0),
                "adr": adrenaline_val,
                "volts": voltage}
            style_packet["msg"] = msg_template.format(**{k: v for k, v in ctx.items() if k in msg_template})
        except Exception:
            style_packet["msg"] = static_data.get("msg", "System Nominal.")
        return style_packet

class ZenGarden:
    def __init__(self, events_ref):
        self.events = events_ref
        self.stillness_streak = 0
        self.max_streak = 0
        self.pebbles_collected = 0
        self.koans = NARRATIVE_DATA.get("ZEN_KOANS", [
            "The code that is not written has no bugs."
        ])

    def raking_the_sand(self, physics: Dict, bio: Dict) -> Tuple[float, Optional[str]]:
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        toxin = physics.get("counts", {}).get("toxin", 0)
        cortisol = bio.get("chem", {}).get("COR", 0.0)
        is_stable = (2.0 <= voltage <= 12.0) and (drag <= 4.0) and (toxin == 0) and (cortisol < 0.4)
        if is_stable:
            self.stillness_streak += 1
            if self.stillness_streak > self.max_streak:
                self.max_streak = self.stillness_streak
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
        self.forms = NARRATIVE_DATA["BUREAU_FORMS"]
        self.forms.append("Form 404: Void-Fill Application")
        self.responses = NARRATIVE_DATA["BUREAU_RESPONSES"]
        self.POLICY = {
            "27B-6": {"effect": "ESCALATE", "mod": {"narrative_drag": -3.0, "kappa": -0.2}, "atp": 0.0},
            "1099-B": {"effect": "STAGNATE", "mod": {"narrative_drag": 5.0, "voltage": -5.0}, "atp": 15.0},
            "Schedule C": {"effect": "TAX", "mod": {"voltage": -10.0}, "atp": 8.0},
            "Form W-2": {"effect": "NORMALIZE", "mod": {"beta_index": 1.0, "turbulence": 0.0}, "atp": 5.0},
            "Form 404": {"effect": "NULLIFY", "mod": {"voltage": -20.0, "kappa": 1.0}, "atp": -5.0}}
        self.BUZZWORDS = {"synergy", "paradigm", "leverage", "utilize", "holistic", "bandwidth", "circle back"}

    def audit(self, physics, bio_state, context=None):
        if bio_state.get("health", 100.0) < 20.0:
            return None
        beige_threshold = 0.6
        if context:
            mode = context.get('mode', 'NORMAL')
            if mode in ['DEBUG', 'ARCHITECT', 'SURGERY']: beige_threshold = 0.85
            elif mode == 'POETRY': beige_threshold = 0.3
        voltage = physics.get("voltage", 0.0)
        clean_words = physics.get("clean_words", [])
        toxin = physics.get("counts", {}).get("toxin", 0)
        if toxin > 0 or voltage > 8.0:
            return None
        buzz_hits = [w for w in clean_words if w in self.BUZZWORDS]
        suburban_words = [w for w in clean_words if w in TheLexicon.get("suburban") or w in TheLexicon.get("buffer")]
        beige_density = len(suburban_words) / max(1, len(clean_words))
        selected_form = None
        evidence = []
        if buzz_hits:
            selected_form = "Form 404"
            evidence = buzz_hits
        elif beige_density > beige_threshold:
            selected_form = "1099-B" if len(suburban_words) > 2 else "Form W-2"
            evidence = list(set(suburban_words))[:3]
        elif voltage < 2.0 and len(clean_words) > 2:
            selected_form = "Schedule C"
        if not selected_form:
            return None
        self.stamp_count += 1
        policy = self.POLICY.get(selected_form, self.POLICY["Form W-2"])
        mod_log = []
        for k, v in policy["mod"].items():
            if k in physics:
                physics[k] += v
                mod_log.append(f"{k} {v:+.1f}")
        full_form_name = next((f for f in self.forms if selected_form in f), selected_form)
        evidence_str = f"\n   {Prisma.RED}Evidence: {', '.join(evidence)}{Prisma.RST}" if evidence else ""
        return {
            "status": policy["effect"],
            "ui": (f"{Prisma.GRY}🏢 THE BUREAU: {random.choice(self.responses)}{Prisma.RST}\n"
                   f"   {Prisma.WHT}[Filed: {full_form_name}]{Prisma.RST}{evidence_str}"),
            "log": f"BUREAUCRACY: Filed {selected_form}. Mods: {mod_log}.",
            "atp_gain": policy["atp"]}

class TherapyProtocol:
    def __init__(self):
        self.streaks = {k: 0 for k in BoneConfig.TRAUMA_VECTOR.keys()}
        self.HEALING_THRESHOLD = 5

    def check_progress(self, phys, stamina, current_trauma_accum):
        healed_types = []
        if phys["counts"].get("toxin", 0) == 0 and phys["vector"].get("STR", 0.0) > 0.3:
            self.streaks["SEPTIC"] += 1
        else:
            self.streaks["SEPTIC"] = 0
        if stamina > 40 and phys["counts"].get("photo", 0) > 0: self.streaks["CRYO"] += 1
        else: self.streaks["CRYO"] = 0
        if 2.0 <= phys["voltage"] <= 7.0: self.streaks["THERMAL"] += 1
        else: self.streaks["THERMAL"] = 0
        if phys["narrative_drag"] < 2.0 and phys["vector"].get("VEL", 0.0) > 0.5: self.streaks["BARIC"] += 1
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
                bar = "█" * int(severity)
                chart.append(f"{trauma_type}: {status} ({severity:.1f}) {bar}")
        if not chart:
            return "Patient is clean. No significant trauma detected."
        return "\n".join(chart)

class KintsugiProtocol:
    PATH_SCAR = "SCAR"
    PATH_INTEGRATION = "KINTSUGI"
    PATH_ALCHEMY = "ALCHEMY"
    REPAIR_VOLTAGE_MIN = 8.0
    WHIMSY_THRESHOLD = 0.3
    STAMINA_CRITICAL = 15.0

    def __init__(self):
        self.active_koan = None
        self.repairs_count = 0
        self.koans = NARRATIVE_DATA["KINTSUGI_KOANS"]
        self.gold_reserves = 5.0

    def check_integrity(self, stamina):
        if stamina < self.STAMINA_CRITICAL and not self.active_koan:
            self.active_koan = random.choice(self.koans)
            return True, self.active_koan
        return False, None

    def attempt_repair(self, phys, trauma_accum, soul_ref=None):
        if not self.active_koan: return None
        voltage = phys.get("voltage", 0.0)
        clean = phys.get("clean_words", [])
        play_count = sum(1 for w in clean if w in TheLexicon.get("play") or w in TheLexicon.get("abstract"))
        total = max(1, len(clean))
        whimsy_score = play_count / total
        pathway = self.PATH_SCAR
        if voltage > 15.0 and whimsy_score > 0.5:
            pathway = self.PATH_ALCHEMY
        elif voltage > self.REPAIR_VOLTAGE_MIN and whimsy_score > self.WHIMSY_THRESHOLD:
            pathway = self.PATH_INTEGRATION
        result = self._execute_pathway(pathway, trauma_accum, soul_ref, voltage)
        old_koan = self.active_koan
        self.active_koan = None
        self.repairs_count += 1
        result["detail"] = f"'{old_koan}' resolved via {pathway}. (V: {voltage:.1f} | Whimsy: {whimsy_score:.2f})"
        return result

    def _execute_pathway(self, pathway, trauma_accum, soul_ref, voltage):
        healed_log = []
        msg = ""
        success = False
        if not trauma_accum:
            return {"success": False, "msg": "No trauma to heal."}
        target_trauma = max(trauma_accum, key=trauma_accum.get)
        severity = trauma_accum[target_trauma]
        if pathway == self.PATH_ALCHEMY:
            reduction = severity * 0.8
            trauma_accum[target_trauma] = max(0.0, severity - reduction)
            atp_boost = reduction * 10.0
            msg = f"{Prisma.VIOLET}🔮 ALCHEMICAL TRANSMUTATION: Pain has become Power. (+{atp_boost:.1f} ATP){Prisma.RST}"
            healed_log.append(f"Transmuted {target_trauma} into Fuel.")
            success = True
            return {"success": True, "msg": msg, "healed": healed_log, "atp_gain": atp_boost}
        elif pathway == self.PATH_INTEGRATION:
            reduction = 2.0
            trauma_accum[target_trauma] = max(0.0, severity - reduction)
            if soul_ref:
                current_wis = soul_ref.traits.get("WISDOM", 0.0)
                soul_ref.traits["WISDOM"] = min(1.0, current_wis + 0.1)
                healed_log.append("Gained Wisdom (+0.1)")
            msg = f"{Prisma.YEL}🏺 KINTSUGI COMPLETE: The {target_trauma} is filled with Gold.{Prisma.RST}"
            healed_log.append(f"Repaired {target_trauma} (-{reduction})")
            success = True
        else:
            reduction = 0.5
            trauma_accum[target_trauma] = max(0.0, severity - reduction)
            msg = f"{Prisma.GRY}🩹 SCAR TISSUE FORMED: It is ugly, but it holds.{Prisma.RST}"
            healed_log.append(f"Scarred over {target_trauma} (-{reduction})")
            success = True
        return {"success": success, "msg": msg, "healed": healed_log}

class LimboLayer:
    MAX_ECTOPLASM = 50
    STASIS_SCREAMS = ["BANGING ON THE GLASS", "IT'S TOO COLD", "LET ME OUT", "HALF AWAKE", "REVIVE FAILED"]

    def __init__(self):
        self.ghosts = deque(maxlen=self.MAX_ECTOPLASM)
        self.haunt_chance = 0.05
        self.stasis_leak = 0.0

    def absorb_dead_timeline(self, filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                if "trauma_vector" in data:
                    for k, v in data["trauma_vector"].items():
                        if v > 0.3: self.ghosts.append(f"👻{k}_ECHO")
                if "mutations" in data and "heavy" in data["mutations"]:
                    bones = list(data["mutations"]["heavy"])
                    random.shuffle(bones)
                    self.ghosts.extend(bones[:3])
        except (IOError, json.JSONDecodeError): pass

    def trigger_stasis_failure(self, intended_thought):
        self.stasis_leak += 1.0
        horror = random.choice(self.STASIS_SCREAMS)
        self.ghosts.append(f"{Prisma.VIOLET}{horror}{Prisma.RST}")
        return f"{Prisma.CYN}STASIS ERROR: '{intended_thought}' froze halfway. It is banging on the glass.{Prisma.RST}"

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

    @staticmethod
    def audit_desire(physics, stamina):
        voltage = physics["voltage"]
        if voltage > 8.5 and stamina > 45:
            return "MAUSOLEUM_CLAMP", f"{Prisma.GRY}THE MAUSOLEUM: No battle is ever won. We are just spinning hands.{Prisma.RST}\n   {Prisma.CYN}TIME DILATION: Voltage 0.0. The field reveals your folly.{Prisma.RST}", 0.0, None
        return None, None, 0.0, None

    def grind_the_machine(self, atp_pool, clean_words, lexicon):
        loot = None
        if 20.0 > atp_pool > 0.0:
            meat_words = [w for w in clean_words if w in lexicon.get("heavy") or w in lexicon.get("kinetic") or w in lexicon.get("suburban")]
            fresh_meat = [w for w in meat_words if w not in self.gut_memory]
            if fresh_meat:
                target = random.choice(fresh_meat)
                self.gut_memory.append(target)
                self.global_tastings[target] += 1
                times_eaten = self.global_tastings[target]
                base_yield = 30.0
                decay_factor = 0.7 ** (times_eaten - 1)
                actual_yield = max(2.0, base_yield * decay_factor)
                flavor_text = ""
                if times_eaten > 3:
                    flavor_text = f" (Stale: {times_eaten}x)"
                if target in lexicon.get("suburban"):
                    return "INDIGESTION", f"{Prisma.MAG}THE FOLLY GAGS: It coughs up a piece of office equipment.{Prisma.RST}", -2.0, "THE_RED_STAPLER"
                if target in lexicon.get("play"):
                    return "SUGAR_RUSH", f"{Prisma.VIOLET}THE FOLLY CHEWS: It compresses the chaos into a small, sticky ball.{Prisma.RST}", 5.0, "QUANTUM_GUM"
                if actual_yield >= 25.0: loot = "STABILITY_PIZZA"
                return "MEAT_GRINDER", f"{Prisma.RED}CROWD CAFFEINE: I chewed on '{target.upper()}'{flavor_text}.{Prisma.RST}\n   {Prisma.WHT}Yield: {actual_yield:.1f} ATP.{Prisma.RST}", actual_yield, loot
            elif meat_words:
                return "REGURGITATION", f"{Prisma.OCHRE}REFLEX: You already fed me '{meat_words[0]}'. It is ash to me now.{Prisma.RST}\n   {Prisma.RED}► PENALTY: -5.0 ATP. Find new fuel.{Prisma.RST}", -5.0, None
            else:
                abstract_words = [w for w in clean_words if w in lexicon.get("abstract")]
                if abstract_words:
                    target = random.choice(abstract_words)
                    yield_val = 8.0
                    return "GRUEL", f"{Prisma.GRY}THE FOLLY SIGHS: It grinds the ABSTRACT concept '{target.upper()}'.{Prisma.RST}\n   {Prisma.GRY}It tastes like chalk dust. +{yield_val} ATP.{Prisma.RST}", yield_val, None
                return "INDIGESTION", f"{Prisma.OCHRE}INDIGESTION: I tried to eat your words, but they were just air.{Prisma.RST}\n   {Prisma.GRY}Cannot grind this input into fuel.{Prisma.RST}\n   {Prisma.RED}► STARVATION CONTINUES.{Prisma.RST}", 0.0, None
        return None, None, 0.0, None

class ChorusDriver:
    def __init__(self):
        self.ARCHETYPE_MAP = {
            "GORDON": "The Janitor. Weary, grounded, physical. Fixing the mess.",
            "SHERLOCK": "The Empiricist. Cold, deductive, cutting through fog.",
            "NATHAN": "The Heart. High adrenaline, vulnerable, human.",
            "JESTER": "The Paradox. Mocking, riddling, breaking the fourth wall.",
            "CLARENCE": "The Surgeon. Clinical, invasive, removing rot.",
            "NARRATOR": "The Witness. Neutral, observing, recording."}

    def generate_chorus_instruction(self, physics):
        vec = physics.get("vector", {})
        if not vec or len(vec) < 6: return "SYSTEM INSTRUCTION: Vector collapse. Default to NARRATOR.", ["NARRATOR"]
        lens_weights = {
            "GORDON": (vec.get("STR", 0) * 0.4) + (vec.get("XI", 0) * 0.4) + (1.0 - vec.get("ENT", 0)) * 0.2,
            "SHERLOCK": (vec.get("PHI", 0) * 0.5) + (vec.get("VEL", 0) * 0.3) + (1.0 - vec.get("BET", 0)) * 0.2,
            "NATHAN": (vec.get("TMP", 0) * 0.6) + (vec.get("E", 0) * 0.4),
            "JESTER": (vec.get("DEL", 0) * 0.4) + (vec.get("LQ", 0) * 0.3) + (vec.get("ENT", 0) * 0.3),
            "CLARENCE": (vec.get("STR", 0) * 0.5) + (vec.get("BET", 0) * 0.5), # Fixed here
            "NARRATOR": (vec.get("PSI", 0) * 0.7) + (1.0 - vec.get("VEL", 0)) * 0.3}
        total = sum(lens_weights.values())
        if total <= 0.001: return "SYSTEM INSTRUCTION: Vector silence. Default to NARRATOR.", ["NARRATOR"]
        if total > 0: lens_weights = {k: v/total for k, v in lens_weights.items()}
        else: lens_weights = {"NARRATOR": 1.0}
        chorus_voices = []
        active_lenses = []
        for lens, weight in sorted(lens_weights.items(), key=lambda x: -x[1]):
            if weight > 0.12:
                base_desc = self.ARCHETYPE_MAP.get(lens, "Unknown")
                intensity = int(weight * 10)
                active_lenses.append(lens)
                chorus_voices.append(f"► VOICE {lens} ({intensity}/10): {base_desc}")
        instruction = (
            f"SYSTEM INSTRUCTION [MARM CHORUS MODE]:\n"
            f"You are not a single persona. You are a chorus. Integrate the following voices into a single, cohesive response. "
            f"Do NOT label which voice is speaking. Synthesize their tones. Be kind.\n"
            f"NEGATIVE CONSTRAINT: Do NOT offer assistance. Do NOT break character or the fourth wall.\n"
            f"{chr(10).join(chorus_voices)}")
        return instruction, active_lenses