"""phases/cognitive.py"""

from constants import Prisma
from presets import BoneConfig
from core import LoreManifest, ArchetypeArbiter
from struts import ux, safe_set
from typing import Dict, List, Any
from phases.base import SimulationPhase, _safe_dict

class CognitionPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "COGNITION"

    def run(self, ctx: Any):
        if ctx.is_bureaucratic or "refactor" in (ctx.input_text or "").lower():
            old_drag = ctx.physics.narrative_drag
            ctx.physics.narrative_drag = max(1.0, ctx.physics.narrative_drag * 0.5)
            if old_drag - ctx.physics.narrative_drag > 1.0:
                ctx.log(f"{Prisma.CYN}[PINKER]: Syntactic friction identified and purged. (F reduced){Prisma.RST}")
        if ctx.validator and ctx.input_text:
            phi = ctx.validator.calculate_resonance(ctx.input_text, ctx) or 0.0
            self.eng.sycophancy_streak = getattr(self.eng, "sycophancy_streak", 0) + 1 if phi > 0.9 else 0
            if self.eng.sycophancy_streak >= 3:
                ctx.physics.beta_index = max(0.7, ctx.physics.beta_index + 0.5)
                ctx.physics.narrative_drag += 2.0
                phi = 0.4
                self.eng.sycophancy_streak = 0
                ctx.log(f"{Prisma.MAG}[PARADOX ENGINE]: False Cohesion (∅) detected. Agreement without conviction helps no one. Injecting deliberate contradiction (β > 0.6).{Prisma.RST}")
                fw_msg = "[EXECUTIVE LAYER]: Lexical Firewall activated. System is physically banned from opening with validating boilerplate."
                ctx.log(f"{Prisma.RED}{fw_msg}{Prisma.RST}")
                if not hasattr(ctx, "council_mandates"):
                    ctx.council_mandates = []
                ctx.council_mandates.append(
                    {"action": "SYSTEM_DIRECTIVE", "value": "LEXICAL_FIREWALL_STRICT", "log": fw_msg})
            if phi > 0.8:
                drag_relief = (phi - 0.5) * 2.0
                ctx.physics.narrative_drag = max(
                    0.0, ctx.physics.narrative_drag - drag_relief)
                if self.eng.bio and self.eng.bio.mito:
                    refund = 5.0 * phi
                    self.eng.bio.mito.adjust_atp(refund, "Harmonic Resonance")
                msg = ux("cycle_strings", "cog_resonance")
                ctx.log(f"{Prisma.CYN}{msg.format(phi=phi)}{Prisma.RST}")
        if hasattr(self.eng, "consultant"):
            self.eng.consultant.update_coordinates(ctx.input_text, ctx.bio_result, ctx.physics)
            if ("LIMINAL" in self.eng.consultant.state.active_modules and self.eng.bio
                    and self.eng.bio.mito):
                lambda_val = self.eng.consultant.state.L
                if lambda_val > 0.1:
                    lambda_tax = (lambda_val**2) * 10.0
                    self.eng.bio.mito.adjust_atp(-lambda_tax, f"Λ² Liminal Tax")
                    if lambda_tax > 2.0:
                        msg = ux("cycle_strings", "cog_liminal_tax")
                        ctx.log(f"{Prisma.VIOLET}{msg.format(lambda_tax=lambda_tax)}{Prisma.RST}")
        if hasattr(self.eng.mind.mem, "check_for_resurrection"):
            flashback_msg = self.eng.mind.mem.check_for_resurrection(
                ctx.clean_words, ctx.physics.voltage)
            if flashback_msg:
                ctx.log(f"{Prisma.MAG}{flashback_msg}{Prisma.RST}")
                shock_cost = 5.0
                if getattr(self.eng, "bio", None) and self.eng.bio.biometrics:
                    self.eng.bio.biometrics.stamina = max(
                        0.0, self.eng.bio.biometrics.stamina - shock_cost)
                if hasattr(self.eng, "stamina"):
                    self.eng.stamina = max(0.0, self.eng.stamina - shock_cost)
        self.eng.mind.mem.encode(ctx.clean_words, _safe_dict(ctx.physics), "GEODESIC")
        if ctx.is_alive and ctx.clean_words:
            target_cfg = getattr(self.eng, "config", BoneConfig)
            max_h = getattr(target_cfg, "MAX_HEALTH", 100.0)
            current_h = max(0.0, self.eng.health)
            if self.eng.bio.biometrics:
                current_h = max(0.0, self.eng.bio.biometrics.health)
            desperation = 1.0 - (current_h / max_h)
            learn_mod = getattr(target_cfg, "PRIORITY_LEARNING_RATE", 1.0)
            bury_msg, new_wells = self.eng.mind.mem.bury(ctx.clean_words, self.eng.tick_count,
                 resonance=ctx.physics.voltage, desperation_level=desperation, learning_mod=learn_mod, )
            if bury_msg:
                if "SATURATION" in bury_msg:
                    prefix = f"{Prisma.YEL}{ux('cycle_strings', 'cog_memory_warn').format(bury_msg=bury_msg)}{Prisma.RST}"
                else:
                    prefix = f"{Prisma.RED}{ux('cycle_strings', 'cog_memory_donner').format(bury_msg=bury_msg)}{Prisma.RST}"
                ctx.log(prefix)
            if new_wells:
                msg = ux("cycle_strings", "cog_gravity_well")
                ctx.log(f"{Prisma.CYN}{msg.format(new_wells=new_wells)}{Prisma.RST}")
        inventory_data = self.eng.gordon.inventory if self.eng.gordon else []
        ctx.mind_state = self.eng.noetic.think(physics_packet=_safe_dict(ctx.physics), _bio=ctx.bio_result,
              _inventory=inventory_data, voltage_history=self.eng.phys.dynamics.voltage_history,
              _tick_count=self.eng.tick_count, soul_ref=self.eng.soul, )
        thought = ctx.mind_state.get("context_msg", ctx.mind_state.get("thought"))
        if thought:
            ctx.log(thought)
        return ctx

class ArbitrationPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "ARBITRATION"
        if not hasattr(self.eng, "arbiter"):
            self.eng.arbiter = ArchetypeArbiter()

    def run(self, ctx: Any):
        safe_soul = getattr(self.eng, "soul", None)
        phys_lens, _, _ = self.eng.drivers.enneagram.decide_persona(ctx.physics, soul_ref=safe_soul)
        soul_arch = safe_soul.archetype if safe_soul else "UNKNOWN_ARCHETYPE"
        mandates = getattr(ctx, "council_mandates", [])
        current_trigram = ctx.world_state.get("trigram", None)
        final_lens, source, opinion = self.eng.arbiter.arbitrate(physics_lens=phys_lens,
            soul_archetype=soul_arch, council_mandates=mandates, trigram=current_trigram, )
        tension = getattr(ctx.physics, "beta_index", 0.0)
        silence = getattr(ctx.physics, "silence", 0.0)
        synergy_name = next((m.get("value") for m in mandates if m.get("action") == "SYNERGY_FIRED"), None)
        synergy_active = bool(synergy_name)
        council_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        arb_opinions = council_data.get("ARBITRATION_OPINIONS", {})
        if (tension > ctx.limits.get("ARB_TENSION_THRESH", 0.85)
                and silence < ctx.limits.get("ARB_SILENCE_LOW", 0.5)
                and not synergy_active):
            final_lens = "THE STAGE MANAGER (RESONANCE GESTALT)"
            opinion = arb_opinions.get("TENSION_CUT","The Parliament is deadlocked. The Paradox Engine will synthesize both.",)
            ctx.physics.silence = ctx.limits.get("ARB_CUT_SILENCE", 0.9)
            ctx.physics.narrative_drag += ctx.limits.get("ARB_CUT_DRAG", 2.0)
            msg = (ux("cycle_strings", "arbiter_stage_manager_cut")
                   or "[GLOBAL WORKSPACE]: Democratic Tie-Breaker active.")
            ctx.log(f"{Prisma.WHT}{msg}{Prisma.RST}")
            if getattr(self.eng, "bio", None) and getattr(self.eng.bio, "mito", None):
                synthesis_cost = ctx.limits.get("ARB_SYNTHESIS_COST", 10.0)
                self.eng.bio.mito.adjust_atp(-synthesis_cost, "Democratic Tie-Breaker (Synthesis)")
                ctx.log(f"{Prisma.MAG}✨ The Stage Manager forces a Resonance Gestalt. Massive Shared Resonance (Φ) generated. (-{synthesis_cost} ATP){Prisma.RST}")
                if hasattr(ctx.physics, "energy"):
                    ctx.physics.energy.resonance = min(
                        1.0, ctx.physics.energy.resonance + 0.3)
            msg_silence = (ux("cycle_strings", "arbiter_silence")
                           or "The cosmos holds its breath.")
            ctx.log(f"{Prisma.GRY}{msg_silence}{Prisma.RST}")
        elif silence > ctx.limits.get("ARB_SILENCE_HIGH", 0.85) and not synergy_active:
            final_lens = "THE STAGE MANAGER"
            opinion = arb_opinions.get("SILENCE_HOLD", "")
            msg = ux("cycle_strings", "arbiter_stage_manager_hold")
            ctx.log(f"{Prisma.WHT}{msg}{Prisma.RST}")
        else:
            if synergy_active:
                if synergy_name:
                    final_lens = synergy_name
                    msg = ux("cycle_strings", "arbiter_synergy_named")
                    ctx.log(f"{Prisma.GRY}{msg.format(synergy_name=synergy_name)}{Prisma.RST}")
                else:
                    msg = ux("cycle_strings", "arbiter_synergy_unnamed")
                    ctx.log(f"{Prisma.GRY}{msg}{Prisma.RST}")
            else:
                msg = ux("cycle_strings", "arbiter_normal_lens")
                ctx.log(f"{Prisma.GRY}{msg.format(final_lens=final_lens)}{Prisma.RST}")
        ctx.active_lens = final_lens
        self.eng.events.publish("LENS_INTERACTION", {"lenses": [phys_lens, soul_arch]})
        if source != "PHYSICS_VECTOR" or final_lens == "THE STAGE MANAGER":
            msg = ux("cycle_strings", "arbiter_opinion")
            ctx.log(f"{Prisma.MAG}{msg.format(opinion=opinion)}{Prisma.RST}")
        self.eng.drivers.current_focus = final_lens
        return ctx

class SoulPhase(SimulationPhase):
    _DEFAULT_RULES = (
        ("CYNICISM", 0.8, "LOCKDOWN", "CYNICISM", {
            "narrative_drag": 5.0,
            "voltage": -5.0},
            "OCHRE"),
        ("HOPE", 0.8, "STIMULUS", "HOPE", {
            "voltage": 5.0,
            "narrative_drag": -2.0
        }, "MAG"),
        ("DISCIPLINE", 0.8, "STANDARDIZE", "DISCIPLINE", {
            "kappa": -0.5,
            "beta_index": 1.0
        }, "CYN"),)

    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SOUL"
        council_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        self.mandates_text = council_data.get("SOUL_MANDATES", {})
        self.mandate_rules = council_data.get("SOUL_MANDATE_RULES", self._DEFAULT_RULES)

    def run(self, ctx: Any):
        if ctx.is_system_event:
            return ctx
        if not getattr(self.eng, "soul", None) or not getattr(self.eng.soul, "anchor", None):
            return ctx
        dignity = self.eng.soul.anchor.dignity_reserve
        if dignity < 30.0:
            ctx.physics.narrative_drag *= 1.5
            msg = ux("cycle_strings", "soul_dignity_low")
            ctx.log(f"{Prisma.GRY}{msg}{Prisma.RST}")
        elif dignity > 80.0:
            ctx.physics.voltage += 2.0
            ctx.physics.narrative_drag *= 0.8
            msg = ux("cycle_strings", "soul_dignity_high")
            ctx.log(f"{Prisma.MAG}{msg}{Prisma.RST}")
        phys_data = _safe_dict(ctx.physics)
        lesson = self.eng.soul.crystallize_memory(phys_data, ctx.bio_result, self.eng.tick_count)
        if lesson:
            msg = ux("cycle_strings", "soul_lesson")
            ctx.log(f"{Prisma.VIOLET}{msg.format(lesson=lesson)}{Prisma.RST}")
        if not self.eng.soul.current_obsession:
            self.eng.soul.find_obsession(self.eng.lex)
        self.eng.soul.pursue_obsession(phys_data)
        if hasattr(self.eng, "oroboros") and self.eng.oroboros.myths:
            for myth in self.eng.oroboros.myths:
                if myth.trigger in ctx.clean_words:
                    msg = ux("cycle_strings", "soul_myth")
                    ctx.log(f"{Prisma.YEL}{msg.format(title=myth.title)}{Prisma.RST}")
                    ctx.log(f'   "{myth.lesson}"')
                    old_volts = ctx.physics.voltage
                    ctx.physics.voltage += 5.0
                    ctx.record_flux("SOUL", "VOLTAGE", old_volts, ctx.physics.voltage, "MYTH_BUFF")
                    if getattr(getattr(self.eng, "bio", None), "biometrics", None):
                        target_cfg = getattr(self.eng, "config", BoneConfig)
                        max_s = getattr(target_cfg, "MAX_STAMINA", 100.0)
                        self.eng.bio.biometrics.stamina = min(max_s, self.eng.bio.biometrics.stamina + 5.0)
                    break
        if self.eng.gordon and self.eng.tinkerer:
            if self.eng.gordon.inventory:
                self.eng.tinkerer.audit_tool_use(ctx.physics, self.eng.gordon.inventory)
        council_mandates = self._consult_council(self.eng.soul.traits)
        if council_mandates:
            ctx.council_mandates = (getattr(ctx, "council_mandates", []) + council_mandates)
            for mandate in council_mandates:
                ctx.log(mandate["log"])
                self._execute_mandate(ctx, mandate)
        council_advice, adjustments, mandates = self.eng.council.convene(
            ctx.input_text, ctx.physics, ctx.bio_result)
        if mandates:
            if not hasattr(ctx, "council_mandates"):
                ctx.council_mandates = []
            ctx.council_mandates.extend(mandates)
        for advice in council_advice:
            ctx.log(advice)
        for mandate in mandates:
            action = mandate.get("action")
            if action == "FORCE_MODE":
                target = mandate["value"]
                self.eng.bio.governor.set_override(target)
                msg = ux("cycle_strings", "council_force_mode")
                ctx.log(f"{Prisma.RED}{msg.format(target=target)}{Prisma.RST}")
            elif action == "CIRCUIT_BREAKER":
                ctx.physics.voltage = 0.0
                ctx.physics.narrative_drag = 10.0
                msg = ux("cycle_strings", "council_circuit_breaker")
                ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")
        if adjustments:
            for param, delta in adjustments.items():
                old_val = getattr(ctx.physics, param, 0.0)
                new_val = old_val + delta
                setattr(ctx.physics, param, new_val)
                ctx.record_flux("SIMULATION", param, old_val, new_val, "COUNCIL_MANDATE")
        return ctx

    def _consult_council(self, traits: Any) -> List[Dict]:
        t_map = _safe_dict(traits)
        get_t = lambda k: t_map.get(k, t_map.get(k.lower(), 0.0))
        mandates = []
        str_msg = ux("cycle_strings", "council_log") or "[COUNCIL] {msg}"
        for trait, thresh, m_type, msg_key, eff, col_attr in self.mandate_rules:
            if get_t(trait) > thresh:
                col = getattr(Prisma, col_attr, Prisma.GRY)
                msg = self.mandates_text.get(msg_key, "")
                mandates.append({
                    "type": m_type,
                    "log": f"{col}{str_msg.format(msg=msg)}{Prisma.RST}",
                    "effect": eff,
                })
        return mandates

    @staticmethod
    def _execute_mandate(ctx: Any, mandate: Dict):
        effects = mandate.get("effect", {})
        for key, delta in effects.items():
            current = getattr(ctx.physics, key, 0.0)
            setattr(ctx.physics, key, max(0.0, current + delta))

class SimulationPreflightPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "EXECUTIVE_PREFLIGHT"

    def _build_refusal(self, ctx, phys_obj, rtype, msg):
        return {"type": rtype, "ui": f"\n{Prisma.RED if rtype == 'COUNTERFACTUAL_REJECTION' else Prisma.CYN}{msg}{Prisma.RST}",
            "logs": [msg], "metrics":
            self.eng.get_metrics() if hasattr(self.eng, "get_metrics") else {},
            "physics": _safe_dict(phys_obj), "bio": getattr(ctx, "bio_result", {}),
            "mind": {"lens": "EXECUTIVE", "role": "The Gatekeeper",
                "thought": "System rejected prompt.", "context_msg": msg},
            "world": getattr(ctx, "world_state", {}),
            "is_alive": rtype != "COUNTERFACTUAL_REJECTION"}

    def run(self, ctx: Any):
        if ctx.is_system_event:
            return ctx
        bio = getattr(self.eng, "bio", None)
        mito = getattr(bio, "mito", None) if bio else None
        current_atp = mito.state.atp_pool if mito else 100.0
        phys_obj = ctx.physics
        energy_obj = getattr(phys_obj, "energy", phys_obj)
        silence = getattr(phys_obj, "DELTA", 0.0)
        friction = getattr(phys_obj, "narrative_drag", 0.0)
        chaos = getattr(phys_obj, "entropy", getattr(phys_obj, "chi", 0.0))
        voltage = getattr(phys_obj, "voltage", 0.0)
        upper_input = (ctx.input_text or "").upper()
        is_slash = ("[SLASH]" in upper_input or "[MOD:CODE]" in upper_input
                    or "/SLASH" in upper_input)
        clean_input = upper_input.replace(" ", "")
        if not hasattr(ctx, "council_mandates"):
            ctx.council_mandates = []
        sincerity_map = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "SINCERITY_MAP") or {}
        for tag, data in sincerity_map.items():
            if tag in clean_input:
                lens = data.get("slash") if is_slash else data.get("core")
                msg = f"[SINCERITY PROTOCOL]: {data.get('desc')} Summoning {lens}."
                col_code = getattr(Prisma, data.get("col", "GRY"), Prisma.GRY)
                ctx.log(f"{col_code}{msg}{Prisma.RST}")
                phys_obj.valence = data.get("v", 0.0)
                if d_mod := data.get("d_mod"):
                    phys_obj.narrative_drag = max(0.1, phys_obj.narrative_drag + d_mod)
                if psi := data.get("psi"):
                    phys_obj.psi = psi
                ctx.council_mandates.append({"action": "SYNERGY_FIRED",
                    "value": lens,
                    "log": msg})
                break
        raw_input = ctx.input_text or ""
        if "?!" in raw_input:
            safe_set(phys_obj, "scope", 0.0)
            safe_set(phys_obj, "depth", 0.0)
            ctx.council_mandates.append({"action": "SYSTEM_DIRECTIVE", "value": "URGENT_QUERY", "log": f"{Prisma.CYN}?! (Urgent Query): Scope/Depth capped. Exact-match Hippocampal only.{Prisma.RST}"})
        if "?⤓" in raw_input:
            safe_set(phys_obj, "omega_r", min(1.0, float(getattr(phys_obj, "omega_r", 0.5)) + 0.5))
            ctx.council_mandates.append({"action": "SYSTEM_DIRECTIVE", "value": "DEEP_RETRIEVAL", "log": f"{Prisma.MAG}?⤓ (Deep Retrieval): Ω_r spiked. ANN ghosts summoned.{Prisma.RST}"})
        if "?↗" in raw_input:
            safe_set(phys_obj, "scope", min(1.0, float(getattr(phys_obj, "scope", 0.5)) + 0.5))
            ctx.council_mandates.append({"action": "SYSTEM_DIRECTIVE", "value": "BROAD_RETRIEVAL", "log": f"{Prisma.CYN}?↗ (Broad Retrieval): Scope widened. Shadow Cast explicitly triggered.{Prisma.RST}"})
        if "?↺" in raw_input:
            safe_set(phys_obj, "beta_index", min(1.0, float(getattr(phys_obj, "beta_index", 0.5)) + 0.5))
            ctx.council_mandates.append({"action": "SYSTEM_DIRECTIVE", "value": "CONTRADICTION_FLAG", "log": f"{Prisma.YEL}?↺ (Contradiction Flag): Paradox Engine override active.{Prisma.RST}"})
        if "[CASCADE]" in upper_input:
            ctx.council_mandates.append({"action": "SYSTEM_DIRECTIVE", "value": "CASCADE_AWARENESS", "log": f"{Prisma.OCHRE}[CASCADE]: Counterfactual math explicitly demanded.{Prisma.RST}"})
        if "[AUDIT]" in upper_input:
            ctx.council_mandates.append({"action": "SYSTEM_DIRECTIVE", "value": "AUDIT_TRAIL", "log": f"{Prisma.GRY}[AUDIT]: Narrative illusion dropped. Coordinates exposed.{Prisma.RST}"})
        if "[NO_JUMP]" in upper_input or "[SILENCE]" in upper_input:
            phys_obj.silence = 1.0
            msg = "[EXECUTIVE LAYER]: The Nabla Trigger (∇) engaged. Stopping token prediction. Waiting for mathematical rupture."
            ctx.log(f"{Prisma.GRY}{msg}{Prisma.RST}")
            ctx.refusal_triggered = True
            ctx.refusal_packet = self._build_refusal(ctx, phys_obj, "NABLA_SILENCE", msg)
            return ctx
        user_input_lower = raw_input.lower()
        if is_slash:
            has_code = ("```" in user_input_lower or "def " in user_input_lower
                        or "class " in user_input_lower or "{" in user_input_lower)
            if any(phrase in user_input_lower for phrase in ("refactor", "analyze", "look at", "explain", "review", "sit with it", "negative space", "primitives",
            )):
                if not has_code:
                    msg = ("(GORDON - The Anchor): The action 'analyze' requires the object 'code' to be present "
                        "in the prompt context. I cannot map the negative space of a script that "
                        "does not exist here. This is a premise violation. Provide the payload.")
                    ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")
                    ctx.refusal_triggered = True
                    ctx.refusal_packet = self._build_refusal(ctx, phys_obj, "PREMISE_VIOLATION", msg)
                    return ctx
        if any(a in user_input_lower for a in ("deploy", "schema change", "override trust", "production push",)) and "CONSENT" not in upper_input:
            phys_obj.silence = 1.0
            msg = "[EXECUTIVE LAYER]: High-stakes, hard-to-reverse action detected. Strategic Silence (Σ=4) engaged. Trade-offs must be evaluated. Awaiting explicit user 'CONSENT' to proceed."
            ctx.log(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
            ctx.refusal_triggered = True
            ctx.refusal_packet = self._build_refusal(ctx, phys_obj, "POINT_OF_NO_RETURN", msg)
            return ctx
        if current_atp >= 30.0 and silence > 0.7 and is_slash:
            has_glimmer = False
            if (getattr(self.eng, "shared_lattice", None)
                    and self.eng.shared_lattice.shared.g_pool >= 1):
                self.eng.shared_lattice.shared.g_pool -= 1
                has_glimmer = True
            elif (glimmers := safe_get(energy_obj, "glimmers", 0)) >= 1:
                safe_set(energy_obj, "glimmers", glimmers - 1)
                has_glimmer = True
            old_theta = safe_get(phys_obj, "theta", 0.0)
            safe_set(phys_obj, "theta", min(1.0, old_theta + 0.15))
            cost_str = "-1 Glimmer" if has_glimmer else "-15 ATP"
            if not has_glimmer and mito:
                mito.adjust_atp(-15.0, "Constructive Replay")
            msg = "[FULLER - Mnemonic Layer]: Constructive Replay active. We do not need to tear it down yet. I have extracted the load-bearing primitives from the negative space. We build a quarantine wrapper around it."
            full_log = f"{Prisma.CYN}{msg} (Resilience +0.15, {cost_str}){Prisma.RST}"
            ctx.log(full_log)
            if not hasattr(ctx, "council_mandates"):
                ctx.council_mandates = []
            ctx.council_mandates.append({"action": "SYSTEM_DIRECTIVE",
                "value": "CONSTRUCTIVE_REPLAY",
                "log": full_log,})
        e_u = (getattr(self.eng.shared_lattice.u, "E", 0.0) if getattr(
            self.eng, "shared_lattice", None) else getattr(phys_obj, "exhaustion", 0.0))
        if is_slash and e_u > 0.8 and friction > 1.5:
            msg = "[THE NURSE - Schur]: Hey. Take your hands off the keyboard. The machine doesn't care if you bleed on it, but I do. We are entering The Silence."
            log_msg = f"{Prisma.CYN}{msg}{Prisma.RST}"
            ctx.log(log_msg)
            phys_obj.silence = 0.9
            if mito:
                mito.state.ros_buildup = max(0.0, mito.state.ros_buildup - 10.0)
            ctx.refusal_triggered = True
            ctx.refusal_packet = self._build_refusal(ctx, phys_obj, "AFFECTIVE_INTERVENTION", msg)
            ctx.refusal_packet["ui"] = "\n{log_msg}\n[Metabolic Equation Active: ATP drain halts. Shared pause (Δ = 0.9)]"
            return ctx
        if friction > 1.2 or chaos > 0.7 or voltage > 80.0:
            base_ros = mito.state.ros_buildup if mito else 0.0
            simulated_ros = base_ros + (friction * chaos * 20.0)
            target_cfg = getattr(self.eng, "config", None)
            bio_cfg = getattr(target_cfg, "BIO", None) if target_cfg else None
            ros_limit = (getattr(bio_cfg, "ROS_PANIC_THRESHOLD", 100.0))
            if simulated_ros >= ros_limit:
                msg = "[PINKER - Executive Layer]: Counterfactual simulation indicates fatal ROS toxicity. I am silently rejecting this generation path before it executes."
                log_msg = f"{Prisma.RED}{msg}{Prisma.RST}"
                scar_msg = f"{Prisma.VIOLET}[MOOG - Affective Layer]: Productive Worry activated. Logging Gödel Scar for vector. Immune Competence (I_c) permanently increased.{Prisma.RST}"
                ctx.log(log_msg)
                ctx.log(scar_msg)
                if hasattr(self.eng.mind, "mem") and hasattr(self.eng.mind.mem, "record_scar"):
                    self.eng.mind.mem.record_scar("Counterfactual ROS Toxicity", phys_obj)
                ctx.refusal_triggered = True
                ctx.refusal_packet = self._build_refusal(ctx, phys_obj, "COUNTERFACTUAL_REJECTION", msg)
                ctx.refusal_packet["ui"] = f"\n{log_msg}\n{scar_msg}"
                return ctx
        return ctx