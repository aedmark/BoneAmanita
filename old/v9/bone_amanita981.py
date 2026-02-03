# BONEAMANITA 9.8.1 - "THE NAVEL GAZE"
# Architects: SLASH, JADE, Taylor & Edmark

import json, os, random, re, time, math, copy, traceback
from collections import Counter, deque
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
from bone_commands import CommandProcessor
from bone_shared import SporeInterface, LocalFileSporeLoader, SporeCasing, LiteraryReproduction, TheAlmanac, ZoneInertia, CycleContext, EventBus, TheLexicon, Prisma, BoneConfig, DeathGen, TheCartographer, TheTinkerer
from bone_data import LENSES, GORDON, DREAMS, RESONANCE, NARRATIVE_DATA
from bone_biology import (
    MitochondrialForge, EndocrineSystem, HyphalInterface, MycotoxinFactory,
    LichenSymbiont, MetabolicGovernor, MycelialNetwork, ParasiticSymbiont, SomaticLoop, NeuroPlasticity, BioSystem, ShimmerState
)
from bone_cortex import TheCortex
from bone_vsl import TheBouncer, PhysicsResolver, StrunkWhiteProtocol, VSL_32Valve, VSL_HNInterface, VSL_DissipativeRefusal, VSL_ChromaticController, VSL_SemanticFilter

@dataclass
class MindSystem:
    mem: MycelialNetwork
    lex: Any
    dreamer: DreamEngine
    mirror: MirrorGraph
    wise: ApeirogonResonance
    tracer: ViralTracer
    integrator: SoritesIntegrator

@dataclass
class PhysSystem:
    tension: 'TheTensionMeter'
    forge: 'TheForge'
    crucible: 'TheCrucible'
    theremin: 'TheTheremin'
    pulse: 'ThePacemaker'
    gate: 'TheTangibilityGate'
    dynamics: 'TemporalDynamics'
    nav: 'TheNavigator'

class GeodesicOrchestrator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.bureau = TheBureau()
        self.bouncer = TheBouncer(self.eng)
        self.parks = PublicParksDepartment()
        self.vsl_32v = VSL_32Valve(self.eng.mind.lex, self.eng.mind.mem)
        self.vsl_chroma = VSL_ChromaticController()
        self.strunk_white = StrunkWhiteProtocol()

    def _compose_logs(self, raw_events: List[Dict]) -> List[str]:
        if not raw_events:
            return []
        buckets = {"CRITICAL": [], "NARRATIVE": [], "CMD": [], "SYS": [], "BIO": [], "PSYCH": [], "OTHER": []}
        for e in raw_events:
            cat = e.get("category", "OTHER").upper()
            if cat not in buckets:
                cat = "OTHER"
            if "RUPTURE" in e.get("text", "") or "DEATH" in e.get("text", ""):
                cat = "CRITICAL"
            buckets[cat].append(e["text"])
        composed_output = []
        if buckets["CRITICAL"]:
            composed_output.append(f"{Prisma.RED}--- CRITICAL ALERTS ---{Prisma.RST}")
            composed_output.extend(buckets["CRITICAL"])
        if buckets["NARRATIVE"]:
            composed_output.extend(buckets["NARRATIVE"])
        compressible_cats = [
            ("CMD", Prisma.WHT, "COMMANDS"),
            ("PSYCH", Prisma.VIOLET, "PSYCHOLOGY"),
            ("BIO", Prisma.GRN, "BIOLOGY"),
            ("SYS", Prisma.GRY, "SYSTEM"),
            ("OTHER", Prisma.GRY, "MISC")
        ]
        for cat_key, color, label in compressible_cats:
            items = buckets[cat_key]
            if not items:
                continue
            composed_output.append(f"{Prisma.SLATE}   .{label} ({len(items)}){' ' * (30 - len(label))}{Prisma.RST}")
            if len(items) > 4 and not BoneConfig.VERBOSE_LOGGING:
                composed_output.extend([f"   {i}" for i in items[:3]])
                remaining = len(items) - 3
                composed_output.append(f"   {color}   ... and {remaining} more {label.lower()} events.{Prisma.RST}")
            else:
                composed_output.extend([f"   {i}" for i in items])
        return composed_output

    def run_turn(self, user_message: str) -> Dict[str, Any]:
        """
        The Master Cycle.
        """
        self.eng.events.flush()
        ctx = CycleContext(input_text=user_message)

        try:
            # 1. PERCEPTION
            self._phase_observe(ctx)

            # 2. MAINTENANCE
            if self.eng.tick_count % 10 == 0:
                self._maintenance_prune(ctx)

            # 3. SECURITY
            self._phase_secure(ctx)
            if ctx.refusal_triggered:
                return ctx.refusal_packet

            # 4. BUREAUCRACY (The Schur Check)
            if self._apply_bureaucracy(ctx):
                return self._package_bureaucracy(ctx)

            # 5. METABOLISM (The Biology)
            self._phase_metabolize(ctx)
            if not ctx.is_alive:
                return self.eng._trigger_death(ctx.physics)

            # 6. SIMULATION (The Physics - Refactored)
            self._phase_simulate(ctx)

            # 7. COGNITION (The Mind)
            self._phase_cognate(ctx)

            # 8. RENDERING (The Output)
            return self._phase_render(ctx)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "type": "CRITICAL_FAILURE",
                "ui": f"{Prisma.RED}SYSTEM PANIC: The Geodesic Dome has collapsed.\n{e}{Prisma.RST}",
                "logs": ctx.logs,
                "metrics": self.eng._get_metrics()
            }

    def _apply_bureaucracy(self, ctx: CycleContext) -> bool:
        """Delegating the Bureau check for cleaner flow."""
        bureau_result = self.bureau.audit(ctx.physics, ctx.bio_result)
        ctx.is_bureaucratic = False
        if bureau_result:
            ctx.is_bureaucratic = True
            ctx.physics["narrative_drag"] = 10.0
            ctx.physics["voltage"] = 0.0
            self.eng.bio.mito.state.atp_pool += bureau_result["atp_gain"]
            ctx.log(bureau_result["log"])
            ctx.bureau_ui = bureau_result["ui"] # Store UI for packaging
            return True
        return False

    def _package_bureaucracy(self, ctx: CycleContext) -> Dict:
        return {
            "type": "BUREAUCRACY",
            "ui": ctx.bureau_ui,
            "logs": self._compose_logs(self.eng.events.flush()),
            "metrics": self.eng._get_metrics(ctx.bio_result.get("atp", 0.0))
        }

    def _phase_observe(self, ctx: CycleContext):
        gaze_result = self.eng.phys.tension.gaze(ctx.input_text, self.eng.mind.mem.graph)
        ctx.physics = gaze_result["physics"]
        ctx.clean_words = gaze_result["clean_words"]
        self.eng.phys.tension.last_physics_packet = ctx.physics
        self.eng.tick_count += 1
        mirror_active, mirror_msg = self.eng.mind.mirror.reflect(ctx.physics)
        if mirror_active and mirror_msg:
            ctx.log(f"{Prisma.CYN}🪞 {mirror_msg}{Prisma.RST}")
        rupture = self.vsl_32v.analyze(ctx.physics)
        if rupture:
            ctx.log(rupture["log"])

    def _maintenance_prune(self, ctx: CycleContext):
        try:
            rotted_words = self.eng.lex.atrophy(self.eng.tick_count, max_age=100)
            if rotted_words:
                for w in rotted_words:
                    self.eng.limbo.ghosts.append(f"👻{w.upper()}_ECHO")
                example = rotted_words[0]
                ctx.log(f"{Prisma.GRY}NEURO-PRUNING: {len(rotted_words)} concepts decayed (e.g., '{example}').{Prisma.RST}")
                ctx.log(f"{Prisma.VIOLET}   (They have drifted into Limbo.){Prisma.RST}")
        except Exception as e:
            ctx.log(f"{Prisma.RED}ATROPHY ERROR: {e}{Prisma.RST}")

    def _phase_secure(self, ctx: CycleContext):
        allowed, refusal_packet = self.bouncer.check_entry(ctx)
        if not allowed:
            ctx.refusal_triggered = True
            ctx.refusal_packet = refusal_packet
            return

    def _phase_metabolize(self, ctx: CycleContext):
        physics = ctx.physics
        gov_msg = self.eng.bio.governor.shift(physics, self.eng.phys.dynamics.voltage_history)
        if gov_msg: self.eng.events.log(gov_msg, "GOV")
        bio_feedback = {
            "INTEGRITY": physics.get("truth_ratio", 0.0),
            "STATIC": physics.get("repetition", 0.0),
            "FORCE": physics.get("voltage", 0.0) / 20.0,
            "BETA": physics.get("beta_index", 1.0)}
        stress_mod = self.eng.bio.governor.get_stress_modifier(self.eng.tick_count)
        if self.eng.tick_count % 10 == 0:
            circadian_msg = self.eng.bio.endo.apply_circadian_rhythm()
            if circadian_msg:
                self.eng.events.log(f"{Prisma.CYN}🕒 {circadian_msg}{Prisma.RST}", "BIO")
        ctx.bio_result = self.eng.soma.digest_cycle(
            ctx.input_text, physics, bio_feedback,
            self.eng.health, self.eng.stamina, stress_mod, self.eng.tick_count)
        ctx.is_alive = ctx.bio_result["is_alive"]
        for log in ctx.bio_result["logs"]:
            if any(x in str(log) for x in ["CRITICAL", "TAX", "Poison"]):
                ctx.log(log)
        hubris_hit, hubris_msg, event_type = self.eng.phys.tension.audit_hubris(physics, self.eng.lex)
        if hubris_hit:
            ctx.log(hubris_msg)
            if event_type == "FLOW_BOOST":
                self.eng.bio.mito.state.atp_pool += 20.0
            elif event_type:
                pass
        self._apply_healing_logic(ctx)

    def _apply_healing_logic(self, ctx: CycleContext):
        is_cracked, koan = self.eng.kintsugi.check_integrity(self.eng.stamina)
        if is_cracked:
            ctx.log(f"{Prisma.YEL}🏺 KINTSUGI ACTIVATED: Vessel cracking.{Prisma.RST}")
            ctx.log(f"   {Prisma.WHT}KOAN: {koan}{Prisma.RST}")
        if self.eng.kintsugi.active_koan:
            repair = self.eng.kintsugi.attempt_repair(ctx.physics, self.eng.trauma_accum)
            if repair and repair["success"]:
                ctx.log(repair["msg"])
                self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 20.0)
                ctx.log(f"   {Prisma.GRN}STAMINA RESTORED (+20.0){Prisma.RST}")
        healed = self.eng.therapy.check_progress(ctx.physics, self.eng.stamina, self.eng.trauma_accum)
        if healed:
            joined = ", ".join(healed)
            ctx.log(f"{Prisma.GRN}❤️ THERAPY STREAK: Healing [{joined}]. Health +5.{Prisma.RST}")
            self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + 5.0)

    def _phase_simulate(self, ctx: CycleContext):
        """
        The Physics Engine.
        """
        # A. Reality Distortion (Mirrors & Trigrams)
        self._apply_reality_filters(ctx)

        # B. Navigation (Roots, Gravity, Location)
        self._process_navigation(ctx)

        # C. Cosmic Mechanics (Orbit & Zones)
        self._process_cosmic_state(ctx)

        # D. Industrial Operations (Forge, Theremin, Crucible)
        self._operate_machinery(ctx)

        # E. Biological Intrusion (Parasites, Ghosts, Pareidolia)
        self._process_intrusions(ctx)

        # F. User Agency (Tools)
        if self.eng.gordon.inventory:
            self.eng.tinkerer.audit_tool_use(ctx.physics, self.eng.gordon.inventory)

        return ctx

    def _apply_reality_filters(self, ctx: CycleContext):
        """Handle Mirror Mode and I Ching Trigrams."""
        text_for_mirror = " ".join(ctx.clean_words)
        self.eng.mind.mirror.profile_input(text_for_mirror, ctx.physics)

        reflection = self.eng.mind.mirror.get_reflection_modifiers()
        ctx.physics["narrative_drag"] *= reflection["drag_mult"]

        if reflection.get("atp_tax", 0) > 0:
            tax = reflection["atp_tax"]
            self.eng.bio.mito.state.atp_pool -= tax
            if random.random() < 0.2:
                ctx.log(f"{Prisma.RED}MIRROR TAX: -{tax:.1f} ATP applied.{Prisma.RST}")

        cap = reflection.get("voltage_cap", 999.0)
        if ctx.physics["voltage"] > cap:
            ctx.physics["voltage"] = cap
            ctx.log(f"{Prisma.GRY}MIRROR: Voltage capped at {cap}.{Prisma.RST}")

        # Trigrams
        trigram_data = self.vsl_32v.geodesic.resolve_trigram(ctx.physics.get("vector", {}))
        ctx.world_state["trigram"] = trigram_data
        if random.random() < 0.05:
            t_sym, t_name = trigram_data["symbol"], trigram_data["name"]
            ctx.log(f"{trigram_data['color']}I CHING: {t_sym} {t_name} is in the ascendant.{Prisma.RST}")

    def _process_navigation(self, ctx: CycleContext):
        """Handle movement, gravity, and location."""
        physics = ctx.physics
        logs = ctx.logs

        # Roots
        if self.eng.tick_count == 3:
            logs.append(self.eng.navigator.strike_root(physics.get("vector", {})))

        shock = self.eng.navigator.check_transplant_shock(physics.get("vector", {}))
        if shock:
            physics["narrative_drag"] += 1.0
            logs.append(shock)

        # Gravity & Flinch
        new_drag, grav_log = self.eng.gordon.check_gravity(physics.get("narrative_drag", 0), physics.get("psi", 0))
        if grav_log: logs.append(grav_log)
        physics["narrative_drag"] = new_drag

        did_flinch, flinch_msg, panic = self.eng.gordon.flinch(ctx.clean_words, self.eng.tick_count)
        if did_flinch:
            logs.append(flinch_msg)
            if panic: physics.update(panic)

        # Location
        current_loc, entry_msg = self.eng.navigator.locate(physics)
        if entry_msg: logs.append(entry_msg)
        logs.extend(self.eng.navigator.apply_environment(physics))

    def _process_cosmic_state(self, ctx: CycleContext):
        """Handle orbital mechanics and zone inertia."""
        physics = ctx.physics
        orbit_state, drag_pen, _ = self.eng.cosmic.analyze_orbit(self.eng.mind.mem, ctx.clean_words)

        raw_zone = physics.get("zone", "COURTYARD")
        stabilized_zone = self.eng.stabilizer.stabilize(raw_zone, physics, (orbit_state, drag_pen))

        # Fuller Lens: Synergy - The Cosmos affects the Drag
        adjusted_drag = self.eng.stabilizer.override_cosmic_drag(drag_pen, stabilized_zone)
        physics["zone"] = stabilized_zone
        self.eng._apply_cosmic_physics(physics, orbit_state, adjusted_drag)
        ctx.world_state["orbit"] = orbit_state

    def _operate_machinery(self, ctx: CycleContext):
        """Handle The Forge, The Theremin, and The Crucible."""
        physics = ctx.physics
        logs = ctx.logs

        # Forge
        transmute_msg = self.eng.phys.forge.transmute(physics)
        if transmute_msg: logs.append(transmute_msg)

        _, forge_msg, new_item = self.eng.phys.forge.hammer_alloy(physics)
        if forge_msg: logs.append(forge_msg)
        if new_item: logs.append(self.eng.gordon.acquire(new_item))

        # Theremin
        _, _, theremin_msg, t_crit = self.eng.phys.theremin.listen(physics, self.eng.bio.governor.mode)
        if theremin_msg: logs.append(theremin_msg)
        if t_crit == "AIRSTRIKE":
            damage = 25.0
            self.eng.health -= damage
            logs.append(f"{Prisma.RED}*** CRITICAL THEREMIN DISCHARGE ***{Prisma.RST}")
            logs.append(f"{Prisma.RED}    The resin shattered explosively. -{damage} HP.{Prisma.RST}")

        # Crucible
        c_state, c_val, c_msg = self.eng.phys.crucible.audit_fire(physics)
        if c_msg: logs.append(c_msg)
        if c_state == "MELTDOWN": self.eng.health -= c_val

    def _process_intrusions(self, ctx: CycleContext):
        """Handle parasites, ghosts, and pareidolia."""
        # Parasites
        p_active, p_log = self.eng.bio.parasite.infect(ctx.physics, self.eng.stamina)
        if p_active: ctx.logs.append(p_log)

        # Ghosts (Limbo)
        if self.eng.limbo.ghosts:
            if ctx.logs:
                last_log = ctx.logs[-1]
                ctx.logs[-1] = self.eng.limbo.haunt(last_log)
            else:
                ctx.logs.append(self.eng.limbo.haunt("The air is heavy."))

        # Pareidolia
        is_p, p_msg = self.eng.check_pareidolia(ctx.clean_words)
        if is_p:
            ctx.logs.append(p_msg)
            ctx.physics["psi"] = min(1.0, ctx.physics["psi"] + 0.3)

    def _phase_cognate(self, ctx: CycleContext):
        self.eng.mind.mem.encode(ctx.clean_words, ctx.physics, "GEODESIC")
        ctx.mind_state = self.eng.noetic.think(
            ctx.physics, ctx.bio_result, self.eng.gordon.inventory,
            self.eng.phys.dynamics.voltage_history)

    def _phase_render(self, ctx: CycleContext) -> Dict[str, Any]:
        physics = ctx.physics
        mind = ctx.mind_state
        if self.eng.cassandra.check_trigger(physics):
            scream = self.eng.cassandra.seize()
            if scream:
                self.eng.events.log(scream, "CRITICAL")
        title_data = self.eng.mind.wise.architect(
            {"physics": physics, "clean_words": ctx.clean_words},
            (mind.get("lens"), mind.get("thought"), mind.get("role")),
            False
        )
        if mind.get("ignition", 0) > 0.8 or physics.get("perfection_streak", 0) >= 3:
            joy_vector = {
                "timestamp": time.time(),
                "resonance": physics.get("truth_ratio", 0) + physics.get("voltage", 0),
                "dominant_flavor": max(physics["counts"], key=physics["counts"].get) if physics["counts"] else "void"
            }
            self.eng.joy_history.append(joy_vector)
        if self.parks.assess_joy(ctx.bio_result, self.eng.tick_count):
            art = self.parks.commission_art(ctx.physics, ctx.mind_state, self.eng.mind.mem.graph)
            path, core_thought = self.parks.dedicate_park(art) # Now returns tuple
            if path:
                ctx.log(f"{Prisma.GRN}🌳 PUBLIC PARK OPENED: {path}{Prisma.RST}")
                self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 15.0)
                self.eng.mind.mem.graph[core_thought] = {"edges": {}, "last_tick": self.eng.tick_count}
                ctx.log(f"   {Prisma.CYN}↺ CIRCULATION: The system is moved by its own art.{Prisma.RST}")
                ctx.log(f"   (Stamina +15.0 | Memory Seeded: '{core_thought}')")
        raw_dashboard = self.eng.projector.render(
            {"physics": physics},
            {
                "title": title_data,
                "health": self.eng.health,
                "bio": ctx.bio_result,
                "world": ctx.world_state
            },
            (mind.get("lens"), mind.get("thought"))
        )
        sys_instruction = ""
        active_lenses = []
        if physics.get("kappa", 0) > 0.4:
            sys_instruction, active_lenses = self.eng.director.generate_chorus_instruction(physics)
            if active_lenses:
                self.eng.events.log(f"{Prisma.GRY}CHORUS ACTIVE: {', '.join(active_lenses)}{Prisma.RST}", "PSYCH")
        final_ui = self.vsl_chroma.modulate(raw_dashboard, physics.get("vector", {}))
        clean_ui, style_log = self.strunk_white.sanitize(final_ui)
        if style_log:
            self.eng.events.log(style_log, "SYS")
            self.eng.bio.endo.dopamine -= 0.05
        final_ui = clean_ui
        rupture = self.vsl_32v.analyze(physics)
        if rupture:
            final_ui = f"{rupture['log']}\n\n{final_ui}"
        for log_entry in ctx.logs:
            if isinstance(log_entry, str):
                self.eng.events.log(log_entry, "NARRATIVE")
            elif isinstance(log_entry, dict):
                self.eng.events.log(log_entry.get("text", str(log_entry)), log_entry.get("category", "NARRATIVE"))
        all_events = self.eng.events.flush()
        structured_logs = self._compose_logs(all_events)
        return {
            "type": "GEODESIC_COMPLETE",
            "ui": clean_ui,
            "logs": self._compose_logs(self.eng.events.flush()),
            "metrics": self.eng._get_metrics(ctx.bio_result.get("atp", 0.0)),
            "system_instruction": sys_instruction
        }
class BoneAmanita:
    def __init__(self, memory_layer=None, lexicon_layer=None):
        self.lex = lexicon_layer if lexicon_layer else TheLexicon
        if hasattr(self.lex, 'initialize'): self.lex.initialize()
        self.lex.compile_antigens()
        DeathGen.load_protocols()
        LiteraryReproduction.load_genetics()
        self.events = EventBus()
        self.shimmer_state = ShimmerState()
        self.navigator = TheNavigator(self.shimmer_state)
        self.journal = LiteraryJournal()
        _mem = memory_layer if memory_layer else MycelialNetwork(self.events)
        self.mind = MindSystem(
            mem=_mem, lex=self.lex, dreamer=DreamEngine(self.events),
            mirror=MirrorGraph(), wise=ApeirogonResonance(self.events),
            tracer=ViralTracer(_mem), integrator=SoritesIntegrator(_mem))
        self.limbo = LimboLayer()
        self.mind.mem.cleanup_old_sessions(self.limbo)
        load_result = self.mind.mem.autoload_last_spore()
        inherited_traits = load_result[0] if load_result else {}
        inherited_antibodies = load_result[1] if load_result else set()
        immune_system = MycotoxinFactory()
        immune_system.active_antibodies = inherited_antibodies
        self.bio = BioSystem(
            mito=MitochondrialForge(self.mind.mem.session_id, self.events, inherited_traits),
            endo=EndocrineSystem(),
            immune=immune_system,
            lichen=LichenSymbiont(),
            gut=HyphalInterface(),
            plasticity=NeuroPlasticity(),
            governor=MetabolicGovernor(),
            shimmer=self.shimmer_state,
            parasite=ParasiticSymbiont(self.mind.mem, self.lex)
        )
        self.phys = PhysSystem(
            tension=TheTensionMeter(self.events), forge=TheForge(), crucible=TheCrucible(),
            theremin=TheTheremin(), pulse=ThePacemaker(), gate=TheTangibilityGate(),
            dynamics=TemporalDynamics(), nav=self.navigator)
        self.repro = LiteraryReproduction()
        self.projector = TheHoloProjector()
        self.gordon = GordonKnot()
        self.kintsugi = KintsugiProtocol()
        self.therapy = TherapyProtocol()
        self.folly = TheFolly()
        self.cosmic = CosmicDynamics()
        self.cmd = CommandProcessor(self, Prisma, self.lex, BoneConfig, TheCartographer)
        self.cassandra = CassandraProtocol(self)
        self.director = ChorusDriver()
        self.tinkerer = TheTinkerer(self.gordon, self.events)
        self.almanac = TheAlmanac()
        self.stabilizer = ZoneInertia()
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.gordon, self.folly, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)
        self.tick_count = 0
        self.health = self.mind.mem.session_health if self.mind.mem.session_health else BoneConfig.MAX_HEALTH
        self.stamina = self.mind.mem.session_stamina if self.mind.mem.session_stamina else BoneConfig.MAX_STAMINA
        self.trauma_accum = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
        self.joy_history = []
        self.cycle_controller = GeodesicOrchestrator(self)
        self.cortex = TheCortex(self)

    def _get_avg_voltage(self):
        hist = self.phys.dynamics.voltage_history
        if not hist: return 0.0
        return sum(hist) / len(hist)

    def process_turn(self, user_message: str) -> Dict[str, Any]:
        cmd_response = self._phase_check_commands(user_message)
        if cmd_response:
            return cmd_response
        if self._ethical_audit():
            self.events.log(f"{Prisma.WHT}MERCY SIGNAL: Trauma boards wiped.{Prisma.RST}", "SYS")
        return self.cortex.process(user_message)

    def _phase_check_commands(self, user_message):
        if user_message.strip().startswith("/"):
            self.cmd.execute(user_message)
            cmd_logs = [e['text'] for e in self.events.flush()]
            return {
                "type": "COMMAND",
                "ui": f"\n{Prisma.GRY}Command Processed.{Prisma.RST}",
                "logs": cmd_logs if cmd_logs else ["Command Executed."],
                "metrics": self._get_metrics()}
        return None

    def _trigger_death(self, last_phys) -> Dict:
        eulogy = DeathGen.eulogy(last_phys, self.bio.mito.state)
        death_log = [f"\n{Prisma.RED}SYSTEM HALT: {eulogy}{Prisma.RST}"]
        try:
            spore_data = {
                "session_id": self.mind.mem.session_id,
                "meta": {"timestamp": time.time(), "final_health": 0, "final_stamina": self.stamina},
                "trauma_vector": self.trauma_accum,
                "mitochondria": self.bio.mito.adapt(0),
                "antibodies": list(self.bio.immune.active_antibodies),
                "core_graph": self.mind.mem.graph,
                "tool_adaptation": self.tinkerer.save_state()}
            path = self.mind.mem.loader.save_spore(self.mind.mem.filename, spore_data)
            death_log.append(f"{Prisma.WHT}   [LEGACY SAVED: {path}]{Prisma.RST}")
        except Exception as e:
            death_log.append(f"Save Failed: {e}")
        return {"type": "DEATH", "ui": "\n".join(death_log), "logs": death_log, "metrics": self._get_metrics(0.0)}

    def _package_turn(self, type_str, logs, context):
        event_data = self.events.flush()
        event_texts = [e['text'] for e in event_data]
        logs.extend(event_texts)
        return {
            "type": type_str,
            "ui": "\n".join(logs),
            "logs": logs,
            "metrics": self._get_metrics()}

    def _get_metrics(self, atp=0.0):
        return {"health": self.health, "stamina": self.stamina, "atp": atp, "tick": self.tick_count}

    def _ethical_audit(self):
        trauma_sum = sum(self.trauma_accum.values())
        health_ratio = self.health / BoneConfig.MAX_HEALTH
        desperation = trauma_sum * (1.0 - health_ratio)
        if desperation > 0.7:
            self.events.log(f"{Prisma.WHT}ETHICAL RELEASE: Desperation ({desperation:.2f}) exceeds limits.{Prisma.RST}", "SYS")
            self.trauma_accum = {k:0.0 for k in self.trauma_accum}
            self.health = min(self.health + 30.0, 100.0)
            self.bio.endo.cortisol = 0.0
            self.bio.endo.serotonin = max(0.5, self.bio.endo.serotonin + 0.3)
            return True
        return False

    @staticmethod
    def _apply_cosmic_physics(physics, state, cosmic_drag_penalty):
        physics["narrative_drag"] += cosmic_drag_penalty
        if state == "VOID_DRIFT": physics["voltage"] = max(0.0, physics["voltage"] - 0.5)
        elif state == "LAGRANGE_POINT": physics["narrative_drag"] = max(0.1, physics["narrative_drag"] - 2.0)
        elif state == "WATERSHED_FLOW": physics["voltage"] += 0.5

    @staticmethod
    def check_pareidolia(words):
        return BoneConfig.check_pareidolia(words)

class SessionGuardian:
    def __init__(self, engine_ref):
        self.eng = engine_ref

    def __enter__(self):
        print(f"{Prisma.paint('>>> BONEAMANITA 9.8.1', 'G')}")
        print(f"{Prisma.paint('System: LISTENING', '0')}")
        return self.eng

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"\n{Prisma.paint('--- SYSTEM HALT ---', 'R')}")
        if exc_type:
            print(f"{Prisma.paint(f'CRITICAL FAILURE: {exc_val}', 'R')}")
            self.eng.events.log(f"CRASH: {exc_val}", "SYS")
        try:
            print(f"{Prisma.paint('Initiating Emergency Spore Preservation...', 'Y')}")
            if hasattr(self.eng, "mind") and hasattr(self.eng, "bio"):
                spore_data = {
                    "session_id": self.eng.mind.mem.session_id,
                    "meta": {
                        "timestamp": time.time(),
                        "final_health": self.eng.health,
                        "final_stamina": self.eng.stamina,
                        "avg_voltage": self.eng._get_avg_voltage(),
                        "exit_cause": "INTERRUPT" if exc_type else "MANUAL"
                    },
                    "trauma_vector": self.eng.trauma_accum,
                    "mitochondria": self.eng.bio.mito.adapt(self.eng.health),
                    "antibodies": list(self.eng.bio.immune.active_antibodies),
                    "core_graph": self.eng.mind.mem.graph,
                    "config_mutations": self.eng.repro.mutate_config(BoneConfig),
                    "tool_adaptation": self.eng.tinkerer.save_state()}
                filename = f"emergency_{self.eng.mind.mem.session_id}.json"
                saved_path = self.eng.mind.mem.loader.save_spore(filename, spore_data)
                if saved_path:
                    print(f"{Prisma.paint(f'✔ Spore encapsulated: {saved_path}', 'C')}")
                    almanac_report = self.eng.almanac.compile_forecast(spore_data)
                    print(almanac_report)
                else:
                    print(f"{Prisma.paint('✘ Spore encapsulation failed (IO Error).', 'R')}")
            else:
                print(f"{Prisma.paint('⚠ CRITICAL: Brainstem missing. Cannot save spore.', 'R')}")
        except Exception as e:
            print(f"{Prisma.paint(f'FATAL: State corruption during shutdown. {e}', 'R')}")
            traceback.print_exc()
        print(f"{Prisma.paint('Disconnected.', '0')}")
        return exc_type is KeyboardInterrupt

if __name__ == "__main__":
    engine_instance = BoneAmanita()
    with SessionGuardian(engine_instance) as eng:
        while True:
            try:
                u = input(f"{Prisma.paint('>', 'W')} ")
                if not u: continue
            except EOFError:
                break
            if u.lower() in ["exit", "quit", "/exit"]:
                break
            result = eng.process_turn(u)
            if result.get("system_instruction"):
                 print(f"\n{Prisma.paint('--- SYSTEM DIRECTIVE ---', 'M')}")
                 print(f"{Prisma.paint(result['system_instruction'], '0')}")
                 print(f"{Prisma.paint('------------------------', 'M')}\n")
            if result.get("ui"):
                print(result["ui"])
            if result.get("logs") and BoneConfig.VERBOSE_LOGGING:
                print(f"{Prisma.GRY}--- DEBUG LOGS ---{Prisma.RST}")
                for log in result["logs"]:
                    print(log)
            if result["type"] == "DEATH":
                break
