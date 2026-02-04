#bone_biology.py - The Wetware

import json, math, time, random, re
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple
from bone_shared import SporeInterface, LocalFileSporeLoader, SporeCasing, LiteraryReproduction, Prisma, TheLexicon, BoneConfig, PhysicsPacket, EventBus, ParadoxSeed, TheAlmanac

DEFAULT_BMR = 2.0

@dataclass
class BioSystem:
    mito: MitochondrialForge
    endo: EndocrineSystem
    immune: MycotoxinFactory
    lichen: LichenSymbiont
    gut: HyphalInterface
    plasticity: NeuroPlasticity
    governor: MetabolicGovernor
    shimmer: ShimmerState
    parasite: ParasiticSymbiont

@dataclass
class MetabolicReceipt:
    base_cost: float
    drag_tax: float
    inefficiency_tax: float
    total_burn: float
    status: str
    symptom: str = "Nominal"

@dataclass
class MitochondrialState:
    atp_pool: float = 100.0
    ros_buildup: float = 0.0
    membrane_potential: float = -150.0
    mother_hash: str = "MITOCHONDRIAL_EVE_001"
    efficiency_mod: float = 1.0
    ros_resistance: float = 1.0
    enzymes: Set[str] = field(default_factory=set)

class TheCortex:
    """
    The Executive Hypervisor.
    Acts as the 'Ron Swanson' of the system: utilitarian, skeptical, and
    capable of shutting down the nonsense to get actual work done.
    """
    def __init__(self, engine_ref):
        self.sub = engine_ref
        self.ballast_state = {"active": False, "turns_remaining": 0}
        self.plain_mode_active = False # The "Boring" Switch
        self.solipsism_counter = 0
        self.SOLIPSISM_THRESHOLD = 3

    # --- LENS 1: EXTERNAL VALIDATION (Pinker) ---
    # We do not trust the VSL engine. We check the raw text ourselves.

    def _calculate_lexical_diversity(self, text: str) -> float:
        """Type-Token Ratio. High = Rich/Chaotic. Low = Repetitive/Solipsistic."""
        words = text.lower().split()
        if not words: return 0.0
        return len(set(words)) / len(words)

    def _check_concreteness(self, text: str) -> float:
        """
        Checks for 'heavy' words directly from the raw data,
        bypassing the VSL interpretation layer.
        """
        # We access the raw set, not the dynamic lexicon
        raw_heavy = set(LEXICON.get("heavy", []))
        words = text.lower().split()
        hits = sum(1 for w in words if w in raw_heavy)
        return hits / max(1, len(words))

    # --- LENS 2: THE "RON SWANSON" BYPASS (Schur) ---
    
    def _execute_plain_mode(self, query: str):
        """
        Bypasses the Geodesic Orchestrator entirely.
        Returns raw, unformatted data. No poetry. No drama.
        """
        query = query.lower()
        response = "System is in PLAIN MODE. Simulation suspended."
        
        if "status" in query:
            h = self.sub.health
            s = self.sub.stamina
            response = f"Health: {h:.1f} | Stamina: {s:.1f} | ATP: {self.sub.bio.mito.state.atp_pool:.1f}"
        elif "inv" in query:
            response = f"Inventory: {self.sub.gordon.inventory}"
        elif "reset" in query:
            self.plain_mode_active = False
            response = "PLAIN MODE DEACTIVATED. Resuming simulation."
        else:
            response = "PLAIN MODE ACTIVE. Type 'reset' to resume narrative protocols."

        return {
            "type": "PLAIN_MODE",
            "ui": f"{Prisma.SLATE}[EXECUTIVE OVERRIDE]: {response}{Prisma.RST}",
            "logs": ["CORTEX: Narrative engine bypassed."],
            "metrics": self.sub._get_metrics()
        }

    # --- LENS 3: THE BALLAST STATE MACHINE (Fuller) ---

    def _trigger_ballast_protocol(self):
        self.ballast_state["active"] = True
        self.ballast_state["turns_remaining"] = 3
        return (
            f"{Prisma.YEL}😵‍💫 VERTIGO WARNING: Solipsism detected.{Prisma.RST}\n"
            f"   {Prisma.WHT}SYSTEM LOCK PENDING.{Prisma.RST} "
            f"Name a concrete object (e.g., 'Stone', 'Iron') within 3 turns to ground the circuit."
        )

    def _process_ballast_attempt(self, text: str):
        # 1. Check Reality
        concreteness = self._check_concreteness(text)
        
        # 2. Success Condition
        if concreteness > 0.1: # At least 10% of the input is solid matter
            self.ballast_state["active"] = False
            self.ballast_state["turns_remaining"] = 0
            self.solipsism_counter = 0
            self.sub.health = min(100.0, self.sub.health + 10.0)
            return {
                "success": True,
                "msg": f"{Prisma.GRN}⚓ ANCHOR DEPLOYED. Reality re-asserted.{Prisma.RST}"
            }
            
        # 3. Failure Condition
        self.ballast_state["turns_remaining"] -= 1
        if self.ballast_state["turns_remaining"] <= 0:
            self.ballast_state["active"] = False
            self.plain_mode_active = True # PUNISHMENT: TIMEOUT
            return {
                "success": False,
                "msg": f"{Prisma.RED}❌ ANCHOR FAILED. Too much drift.{Prisma.RST}\n   {Prisma.GRY}Initiating PLAIN MODE (Timeout Protocol).{Prisma.RST}"
            }
            
        return {
            "success": False,
            "msg": f"{Prisma.OCHRE}⚠️ DRIFTING... {self.ballast_state['turns_remaining']} attempts remain.{Prisma.RST}"
        }

    # --- THE EXECUTIVE LOOP ---

    def process(self, user_input: str):
        # 1. COMMAND INTERCEPT (Explicit Backdoor)
        if user_input.startswith("??"):
            # This is now a feature of Plain Mode, but accessible globally
            return self._execute_plain_mode(user_input.replace("??", ""))

        # 2. PLAIN MODE LOCK (The Punishment/Safety Valve)
        if self.plain_mode_active:
            if "reset" in user_input.lower():
                 self.plain_mode_active = False
                 return {"type": "INFO", "ui": f"{Prisma.CYN}Simulation Restored.{Prisma.RST}", "logs": [], "metrics": self.sub._get_metrics()}
            return self._execute_plain_mode(user_input)

        # 3. BALLAST INTERCEPT
        if self.ballast_state["active"]:
            result = self._process_ballast_attempt(user_input)
            if result["success"]:
                # If successful, we allow the turn to process normally, but append the success msg
                pass 
            elif self.plain_mode_active:
                # If we just failed into Plain Mode, return immediately
                return {
                    "type": "TIMEOUT", 
                    "ui": result["msg"], 
                    "logs": ["CORTEX: Ballast failed. System grounded forcibly."],
                    "metrics": self.sub._get_metrics()
                }
            else:
                # Still drifting, return warning but allow processing (or block it?)
                # Fuller: "Don't process garbage data." Block it.
                return {
                    "type": "DRIFT",
                    "ui": result["msg"],
                    "logs": ["CORTEX: Awaiting ballast."],
                    "metrics": self.sub._get_metrics()
                }

        # 4. RUN SIMULATION (The Subordinate)
        sim_result = self.sub.cycle_controller.run_turn(user_input)

        # 5. POST-PROCESS VALIDATION (The Solipsism Check)
        # We analyze the OUTPUT, not just the input.
        # Pinker: "Is the machine talking nonsense?"
        
        sim_text = sim_result.get("ui", "")
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', sim_text) # Strip colors
        diversity = self._calculate_lexical_diversity(clean_text)
        
        # If diversity is low (repetitive) but the physics engine claims high truth...
        physics_truth = self.sub.phys.tension.last_physics_packet.get("truth_ratio", 0.0)
        
        if diversity < 0.4 and physics_truth > 0.9:
            self.solipsism_counter += 1
            if self.solipsism_counter >= self.SOLIPSISM_THRESHOLD:
                # Trigger the Ballast Protocol
                warning = self._trigger_ballast_protocol()
                sim_result["ui"] += f"\n\n{warning}"
                sim_result["logs"].append("CORTEX: Solipsism Threshold Exceeded.")

        # 6. SCHEDULED MAINTENANCE (Targeted, not Random)
        if self.sub.tick_count % 50 == 0:
            self._perform_targeted_maintenance()

        return sim_result

    def _perform_targeted_maintenance(self):
        """
        Consensual Memory Management.
        Instead of a wipe, we archive.
        """
        # Only dampen trauma if it's critical
        trauma_sum = sum(self.sub.trauma_accum.values())
        if trauma_sum > 2.0:
            self.sub.trauma_accum = {k: v * 0.8 for k, v in self.sub.trauma_accum.items()}
            self.sub.events.log("CORTEX: Trauma dampened to prevent cascade.", "SYS")
        
        # Don't delete ghosts unless necessary
        if len(self.sub.limbo.ghosts) > 40:
             self.sub.limbo.ghosts.clear()
             self.sub.events.log("CORTEX: Limbo purged (Overcrowded).", "SYS")

class MitochondrialForge:
    APOPTOSIS_TRIGGER = "CYTOCHROME_C_RELEASE"

    def __init__(self, lineage_seed: str, events, inherited_traits: Optional[Dict] = None):
        self.state = MitochondrialState(mother_hash=lineage_seed)
        self.events = events
        self.krebs_cycle_active = True
        if inherited_traits:
            self._apply_inheritance(inherited_traits)

    def _apply_inheritance(self, traits: Dict):
        self.state.efficiency_mod = traits.get("efficiency_mod", 1.0)
        self.state.ros_resistance = traits.get("ros_resistance", 1.0)
        if "enzymes" in traits:
            self.state.enzymes = set(traits["enzymes"])
            self.events.log(f"{Prisma.CYN}[MITO]: Inherited Enzymes: {list(self.state.enzymes)}.{Prisma.RST}")

    def adapt(self, final_health: float) -> Dict:
        traits = {
            "efficiency_mod": self.state.efficiency_mod,
            "ros_resistance": self.state.ros_resistance,
            "enzymes": list(self.state.enzymes)}
        if final_health <= 0 and random.random() < 0.3:
            traits["ros_resistance"] += 0.1
        return traits

    def calculate_metabolism(self, drag: float, external_modifiers: Optional[List[float]] = None) -> MetabolicReceipt:
        bmr = getattr(BoneConfig, "BASE_METABOLIC_RATE", DEFAULT_BMR)
        limit = BoneConfig.MAX_DRAG_LIMIT
        safe_drag = max(0.0, drag)
        if safe_drag <= limit:
            drag_tax = safe_drag * 0.2
        else:
            drag_tax = 1.0 + ((safe_drag - limit) * 0.5)
        if external_modifiers:
            for mod in external_modifiers:
                drag_tax *= mod
        raw_cost = bmr + drag_tax
        safe_efficiency = max(0.1, self.state.efficiency_mod)
        final_cost = raw_cost / safe_efficiency
        inefficiency = 0.0
        if safe_efficiency < 1.0:
            inefficiency = final_cost - raw_cost
        status = "RESPIRING"
        symptom = "Humming along."
        if final_cost > self.state.atp_pool:
            status = "NECROSIS"
            symptom = f"The engine is stalling. Requires {final_cost:.1f} ATP."
        elif self.state.ros_buildup > BoneConfig.CRITICAL_ROS_LIMIT:
            status = self.APOPTOSIS_TRIGGER
            symptom = "Cellular suicide initiated. Too much noise."
        elif drag_tax > limit:
            symptom = "The gears are grinding. Heavy load."
        return MetabolicReceipt(
            base_cost=round(bmr, 2),
            drag_tax=round(drag_tax, 2),
            inefficiency_tax=round(inefficiency, 2),
            total_burn=round(final_cost, 2),
            status=status,
            symptom=symptom)

    def respirate(self, receipt: MetabolicReceipt) -> str:
        if receipt.status == "NECROSIS":
            self.state.atp_pool = 0.0
            return "NECROSIS"
        if receipt.status == self.APOPTOSIS_TRIGGER:
            self.krebs_cycle_active = False
            self.state.atp_pool = 0.0
            return self.APOPTOSIS_TRIGGER
        self.state.atp_pool -= receipt.total_burn
        ros_generation = receipt.total_burn * 0.1 * (1.0 / self.state.ros_resistance)
        self.state.ros_buildup += ros_generation
        return "RESPIRING"

class SomaticLoop:
    """
    The SomaticLoop acts as the biological orchestrator (The Grammar of the Body).
    It manages the input/output of energy, ensuring the system pays its taxes (Burn),
    eats its vegetables (Harvest), and deals with the consequences (Maintenance).
    """
    def __init__(self, bio_layer, memory_layer, lexicon_layer, gordon_ref, folly_ref, events_ref):
        self.bio = bio_layer
        self.mem = memory_layer
        self.lex = lexicon_layer
        self.gordon = gordon_ref
        self.folly = folly_ref
        self.events = events_ref

    def digest_cycle(self, text: str, physics_data: Any, feedback: Dict,
                     current_health: float, current_stamina: float,
                     stress_mod: float = 1.0, tick_count: int = 0,
                     circadian_bias: Dict[str, float] = None) -> Dict:
  
        phys = self._normalize_physics(physics_data)
        logs = []
        receipt = self._calculate_taxes(phys, logs)
        resp_status = self.bio.mito.respirate(receipt)
        if self._audit_folly_desire(phys, current_stamina, logs) == "MAUSOLEUM_CLAMP":
            return self._package_result(resp_status, logs, enzyme="NONE")
        enzyme, total_yield = self._harvest_resources(text, phys, logs, tick_count)
        self.bio.mito.state.atp_pool += total_yield
        self._perform_maintenance(phys, logs, tick_count)
        chem_state = self.bio.endo.metabolize(
            feedback, current_health, current_stamina,
            self.bio.mito.state.ros_buildup,
            harvest_hits=self._count_harvest_hits(phys),
            stress_mod=stress_mod,
            enzyme_type=enzyme,
            circadian_bias=circadian_bias
        )
        return self._package_result(resp_status, logs, chem_state, enzyme)

    def _normalize_physics(self, data: Any) -> PhysicsPacket:
        if isinstance(data, dict):
            return PhysicsPacket.from_dict(data)
        return data

    def _calculate_taxes(self, phys, logs) -> MetabolicReceipt:
        modifiers = []
        if "TIME_BRACELET" in self.gordon.inventory:
            modifiers.append(0.5)
        is_hybrid = (phys.counts.get("heavy", 0) >= 2 and phys.counts.get("abstract", 0) >= 2)
        if is_hybrid:
            modifiers.append(0.8)
        receipt = self.bio.mito.calculate_metabolism(phys.narrative_drag, external_modifiers=modifiers)
        if receipt.total_burn > 3.0:
            tax_note = f" (Drag Tax: {receipt.drag_tax:.1f})" if receipt.drag_tax > 1.0 else ""
            logs.append(f"{Prisma.GRY}METABOLISM: Burned {receipt.total_burn:.1f} ATP{tax_note}.{Prisma.RST}")
        return receipt

    def _audit_folly_desire(self, phys, stamina, logs) -> str:
        if not hasattr(self.folly, 'audit_desire'):
            return "NONE"
        p_dict = phys.to_dict() if hasattr(phys, 'to_dict') else phys.__dict__
        event, msg, _, _ = self.folly.audit_desire(p_dict, stamina)
        if event:
            logs.append(msg)
        return event

    def _harvest_resources(self, text, phys, logs, tick) -> Tuple[str, float]:
        total_yield = 0.0
        p_dict = phys.to_dict() if hasattr(phys, 'to_dict') else phys.__dict__
        enzyme, nutrient_profile = self.bio.gut.secrete(text, p_dict)
        base_yield = nutrient_profile.get("yield", 0.0)
        geo_mass = phys.geodesic_mass
        geo_mod = 1.0 + min(1.5, (geo_mass / BoneConfig.GEODESIC_STRENGTH))
        complexity_tax = 0.0
        if phys.psi > 0.6 and geo_mass < 2.0:
            complexity_tax = base_yield * 0.4
            logs.append(f"{Prisma.YEL}COMPLEXITY TAX: High Psi, Low Structure. -{complexity_tax:.1f} Yield.{Prisma.RST}")
        digestive_yield = max(0.0, (base_yield * geo_mod) - complexity_tax)
        total_yield += digestive_yield
        if geo_mod > 1.2:
            logs.append(f"{Prisma.GRN}INFRASTRUCTURE BONUS: Mass {geo_mass:.1f}. Yield x{geo_mod:.2f}.{Prisma.RST}")
        clean = phys.clean_words
        sugar, lichen_msg = self.bio.lichen.photosynthesize(p_dict, clean, tick)
        if sugar > 0:
            total_yield += sugar
            logs.append(f"\n{lichen_msg}")
        event, msg, folly_yield, loot = self.folly.grind_the_machine(
            self.bio.mito.state.atp_pool, clean, self.lex
        )
        if event:
            logs.append(f"\n{msg}")
            total_yield += folly_yield
            if loot:
                loot_msg = self.gordon.acquire(loot)
                if loot_msg: logs.append(loot_msg)
        return enzyme, total_yield

    def _perform_maintenance(self, phys, logs, tick):
        if phys.turbulence > 0.7:
            burn = 5.0
            self.bio.mito.state.atp_pool -= burn
            logs.append(f"{Prisma.YEL}CHOPPY WATERS: High Turbulence burn. -{burn} ATP.{Prisma.RST}")
        elif phys.turbulence < 0.2:
            self.bio.mito.state.atp_pool += 2.0
        if self.bio.mito.state.atp_pool < 10.0:
            logs.append(f"{Prisma.RED}STARVATION PROTOCOL: ATP Critical. Initiating Autophagy...{Prisma.RST}")
            victim, log_msg = self.mem.cannibalize(current_tick=tick)
            if victim:
                self.bio.mito.state.atp_pool += 15.0
                logs.append(f"   {Prisma.RED}AUTOPHAGY: {log_msg} (+15.0 ATP){Prisma.RST}")
            else:
                logs.append(f"   {Prisma.RED}AUTOPHAGY FAILED: {log_msg}{Prisma.RST}")

    def _count_harvest_hits(self, phys):
        return sum(1 for w in phys.clean_words if w in TheLexicon.get("harvest"))

    def _package_result(self, status, logs, chem=None, enzyme="NONE"):
        return {
            "is_alive": status != "NECROSIS",
            "atp": self.bio.mito.state.atp_pool,
            "chem": chem if chem else self.bio.endo.get_state(),
            "enzyme_active": enzyme,
            "logs": logs
        }

class MycotoxinFactory:
    def __init__(self):
        self.active_antibodies = set()
        self.PHONETICS = {
            "PLOSIVE": set("bdgkpt"), "FRICATIVE": set("fthszsh"),
            "LIQUID": set("lr"), "NASAL": set("mn")
        }
        self.ROOTS = {
            "HEAVY": ("lith", "ferr", "petr", "dens", "grav", "struct", "base", "fund", "mound"),
            "KINETIC": ("mot", "mov", "ject", "tract", "pel", "crat", "dynam", "flux"),
        }

    def assay(self, word, _context, _rep_val, _phys, _pulse):
        w = word.lower()
        clean_len = len(w)
        if clean_len < 3: return None, ""
        for cat, roots in self.ROOTS.items():
            for r in roots:
                if r in w:
                    is_anchor = w.startswith(r) or w.endswith(r)
                    density = len(r) / clean_len
                    if is_anchor or density > 0.5:
                        return None, ""
        plosive = sum(1 for c in w if c in self.PHONETICS["PLOSIVE"])
        nasal = sum(1 for c in w if c in self.PHONETICS["NASAL"])
        density_score = (plosive * 1.5) + (nasal * 0.8)
        compression_mod = 1.0 if clean_len > 5 else 1.5
        final_density = (density_score / clean_len) * compression_mod
        if final_density > 0.8:
            return "TOXIN_HEAVY", f"Detected phonetic toxicity in '{w}'."
        return None, ""

class MycelialNetwork:
    def __init__(self, events: EventBus, loader: SporeInterface = None, seed_file=None):
        self.loader = loader if loader else LocalFileSporeLoader()
        self.events = events
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"{self.session_id}.json"
        self.graph = {}
        self.cortical_stack = deque(maxlen=15)
        self.fossils = deque(maxlen=200)
        self.lineage_log = []
        self.seeds = self.load_seeds()
        self.session_health = None
        self.session_stamina = None
        self.short_term_buffer = deque(maxlen=10)
        self.consolidation_threshold = 5.0
        if seed_file:
            self.ingest(seed_file)

    def load_seeds(self):
        loaded_seeds = []
        try:
            for item in SEEDS:
                seed = ParadoxSeed(item["question"], set(item["triggers"]))
                loaded_seeds.append(seed)
            self.events.log(f"{Prisma.GRY}[SYSTEM]: Paradox Seeds loaded ({len(loaded_seeds)} active) from Data Core.{Prisma.RST}")
        except Exception as e:
            self.events.log(f"{Prisma.RED}[CRITICAL]: Seed Injection Failed: {e}{Prisma.RST}")
            # Emergency Fallback
            loaded_seeds = [ParadoxSeed("Does the mask eat the face?", {"mask", "face", "hide"})]
        return loaded_seeds

    def encode(self, clean_words, physics, governor_mode):
        significance = physics["voltage"]
        if governor_mode == "FORGE": significance *= 2.0
        elif governor_mode == "LABORATORY": significance *= 1.2
        engram = {"trigger": clean_words[:3] if clean_words else ["void"], "context": governor_mode,
                  "voltage": physics["voltage"], "significance": significance, "timestamp": time.time()}
        if significance > self.consolidation_threshold:
            self.short_term_buffer.append(engram)
            return True
        return False

    def replay_dreams(self):
        if not self.short_term_buffer:
            return "🌑 SLEEPLESS: No significant memories to process."
        strengthened = 0
        for engram in self.short_term_buffer:
            weight_boost = engram["significance"] * 0.1
            words = engram["trigger"]
            if len(words) >= 2:
                w1, w2 = words[0], words[1]
                if w1 in self.graph and w2 in self.graph:
                    if w2 in self.graph[w1]["edges"]:
                        self.graph[w1]["edges"][w2] += weight_boost
                        strengthened += 1
        self.short_term_buffer.clear()
        return f"💤 HIPPOCAMPAL REPLAY: Consolidated {strengthened} high-voltage pathways."

    def autoload_last_spore(self):
        files = self.loader.list_spores()
        if not files:
            self.events.log(f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}")
            return None
        candidates = [f for f in files if self.session_id not in f[0]]
        if candidates:
            last_spore_path = candidates[0][0]
            self.events.log(f"{Prisma.CYN}[GENETICS]: Locating nearest ancestor...{Prisma.RST}")
            return self.ingest(last_spore_path)
        return None

    def calculate_mass(self, node):
        if node not in self.graph: return 0.0
        return sum(self.graph[node]["edges"].values())

    def get_shapley_attractors(self):
        attractors = {}
        for node in self.graph:
            mass = self.calculate_mass(node)
            if mass >= BoneConfig.SHAPLEY_MASS_THRESHOLD:
                attractors[node] = mass
        return attractors

    def check_echo_well(self, node):
        mass = self.calculate_mass(node)
        if mass > BoneConfig.GRAVITY_WELL_THRESHOLD * 1.5:
            self.events.log(f"{Prisma.VIOLET}GRAVITY WARNING: '{node.upper()}' is becoming a black hole (Mass {int(mass)}).{Prisma.RST}")
            return 2.0
        return 0.0

    def tend_garden(self, current_words):
        bloom_msg = None
        for seed in self.seeds:
            is_ready = seed.water(current_words)
            if is_ready and not bloom_msg:
                bloom_msg = seed.bloom()
        return bloom_msg

    def bury(self, clean_words: List[str], tick: int, resonance=5.0, learning_mod=1.0) -> Tuple[Optional[str], List[str]]:
        total_len = sum(len(w) for w in clean_words)
        count = max(1, len(clean_words))
        avg_len = total_len / count
        if avg_len < 3.5 and count > 3:
            self.events.log(f"{Prisma.YEL}REJECTED: Input is too 'Optimized' (Avg Len: {avg_len:.1f}).{Prisma.RST}")
            return "MECHANICAL_STARVATION", []
        if avg_len > 5.0: resonance += 2.0
        valuable_matter = (TheLexicon.get("heavy") | TheLexicon.get("thermal") | TheLexicon.get("cryo") | TheLexicon.get("abstract"))
        filtered = [w for w in clean_words if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)]
        self.cortical_stack.extend(filtered)
        base_rate = 0.5 * (resonance / 5.0)
        learning_rate = max(0.1, min(1.0, base_rate * learning_mod))
        decay_rate = 0.1
        for i in range(len(filtered)):
            current = filtered[i]
            if current not in self.graph:
                self.graph[current] = {"edges": {}, "last_tick": tick}
            else:
                self.graph[current]["last_tick"] = tick
            start_window = max(0, i - 2)
            context_window = filtered[start_window:i]
            for prev in context_window:
                if prev not in self.graph[current]["edges"]: self.graph[current]["edges"][prev] = 0.0
                current_weight = self.graph[current]["edges"][prev]
                delta = learning_rate * (1.0 - (current_weight * decay_rate))
                self.graph[current]["edges"][prev] = min(10.0, self.graph[current]["edges"][prev] + delta)
                if prev not in self.graph: self.graph[prev] = {"edges": {}, "last_tick": tick}
                if current not in self.graph[prev]["edges"]: self.graph[prev]["edges"][current] = 0.0
                rev_weight = self.graph[prev]["edges"][current]
                rev_delta = learning_rate * (1.0 - (rev_weight * decay_rate))
                self.graph[prev]["edges"][current] = min(10.0, self.graph[prev]["edges"][current] + rev_delta)
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            victim, log_msg = self.cannibalize(current_tick=tick)
            if not victim:
                protected = set(self.cortical_stack)
                candidates = [k for k in self.graph.keys() if k not in protected]
                if candidates:
                    oldest = min(candidates, key=lambda k: self.graph[k].get("last_tick", 0))
                    del self.graph[oldest]
                    for node in self.graph:
                        if oldest in self.graph[node]["edges"]:
                            del self.graph[node]["edges"][oldest]
                    victim = oldest
                    log_msg = f"FORCED AMNESIA: '{oldest}' deleted to save space."
                else:
                    return f"MEMORY FULL: Cortical Lock. Input '{clean_words[0]}' rejected.", []
            return log_msg, [victim] if victim else []
        new_wells = []
        for w in filtered:
            if w in self.graph:
                mass = sum(self.graph[w]["edges"].values())
                if mass > BoneConfig.SHAPLEY_MASS_THRESHOLD:
                    node_data = self.graph[w]
                    if "strata" not in node_data:
                        node_data["strata"] = {"birth_tick": tick, "birth_mass": mass, "stability_index": 0.0}
                        new_wells.append(w)
                    else:
                        age = max(1, tick - node_data["strata"]["birth_tick"])
                        growth = (mass - node_data["strata"]["birth_mass"]) / age
                        node_data["strata"]["growth_rate"] = round(growth, 3)
        return None, new_wells

    def cannibalize(self, preserve_current=None, current_tick=0) -> Tuple[Optional[str], str]:
        protected = set()
        if preserve_current: protected.update(preserve_current)
        protected.update(self.cortical_stack)
        candidates = []
        for k, v in self.graph.items():
            if k in protected: continue
            edge_count = len(v["edges"])
            age = current_tick - v.get("last_tick", 0)
            score = edge_count + (1.0 / max(1, age))
            candidates.append((k, v, score))
        if not candidates:
            return None, "MEMORY FULL. CORTEX LOCKED."
        candidates.sort(key=lambda x: x[2])
        victim, data, score = candidates[0]
        mass = sum(data["edges"].values())
        lifespan = current_tick - data.get("strata", {}).get("birth_tick", current_tick)
        self.fossils.append({
            "word": victim,
            "mass": round(mass, 2),
            "lifespan": lifespan,
            "death_tick": current_tick
        })
        del self.graph[victim]
        for node in self.graph:
            if victim in self.graph[node]["edges"]:
                del self.graph[node]["edges"][victim]

        return victim, f"FOSSILIZED: '{victim}' (Mass {mass:.1f} -> Ossuary)"

    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        pruned_count = 0
        total_decayed = 0
        nodes_to_remove = []
        for node in self.graph:
            edges = self.graph[node]["edges"]
            dead_links = []
            for target, weight in edges.items():
                resistance = min(1.0, weight / 10.0)
                dynamic_factor = scaling_factor + (0.14 * resistance)
                new_weight = weight * dynamic_factor
                edges[target] = new_weight
                total_decayed += 1
                if new_weight < prune_threshold: dead_links.append(target)
            for dead in dead_links:
                del edges[dead]
                pruned_count += 1
            if not edges: nodes_to_remove.append(node)
        for n in nodes_to_remove: del self.graph[n]
        return f"📉 HOMEOSTATIC SCALING: Decayed {total_decayed} synapses. Pruned {pruned_count} weak connections."

    def save(self, health, stamina, mutations, trauma_accum, joy_history, mitochondria_traits=None, antibodies=None):
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        top_joy = sorted(joy_history, key=lambda x: x["resonance"], reverse=True)[:3]
        joy_legacy_data = None
        if top_joy:
            primary_joy = top_joy[0]
            joy_legacy_data = {
                "flavor": primary_joy["dominant_flavor"],
                "resonance": primary_joy["resonance"],
                "timestamp": primary_joy["timestamp"]
            }
        if health <= 0:
            cause = max(final_vector, key=final_vector.get) if final_vector else "UNKNOWN"
            final_vector[cause] = 1.0
        spore = SporeCasing(session_id=self.session_id, graph=self.graph, mutations=mutations, trauma=base_trauma, joy_vectors=top_joy)
        seed_state = [{"q": s.question, "m": s.maturity, "b": s.bloomed} for s in self.seeds]
        data = spore.__dict__
        data["seeds"] = seed_state
        if antibodies: data["antibodies"] = list(antibodies)
        data["trauma_vector"] = final_vector
        data["fossils"] = list(self.fossils)
        data["meta"] = {"timestamp": time.time(), "final_health": health, "final_stamina": stamina}
        if mitochondria_traits: data["mitochondria"] = mitochondria_traits
        if joy_legacy_data:
            data["joy_legacy"] = joy_legacy_data
        almanac = TheAlmanac()
        condition, _ = almanac.diagnose_condition(data)
        future_seed = almanac.get_seed(condition)
        data["seeds"].append({"q": future_seed, "m": 0.0, "b": False})
        return self.loader.save_spore(self.filename, data)

    def ingest(self, target_file, current_tick=0):
        data = self.loader.load_spore(target_file)
        if not data:
            self.events.log(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")
            return None, set()
        try:
            required_keys = ["meta", "trauma_vector", "core_graph"]
            if not all(k in data for k in required_keys):
                self.events.log(f"{Prisma.RED}[MEMORY]: Spore rejected (Missing Structural Keys).{Prisma.RST}")
                return None
            final_health = data.get("meta", {}).get("final_health", 50)
            final_stamina = data.get("meta", {}).get("final_stamina", 25)
            spore_authority = (final_health + final_stamina) / 150.0
            self.events.log(f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}")
            session_source = data.get("session_id", "UNKNOWN_ANCESTOR")
            timestamp = data.get("meta", {}).get("timestamp", 0)
            time_ago = int((time.time() - timestamp) / 3600)
            trauma_summary = {k:v for k,v in data.get("trauma_vector", {}).items() if v > 0.1}
            mutation_count = sum(len(v) for v in data.get("mutations", {}).values())
            self.lineage_log.append({"source": session_source, "age_hours": time_ago, "trauma": trauma_summary, "mutations": mutation_count, "loaded_at": time.time()})
            if "fossils" in data:
                self.fossils.extend(data["fossils"])
                self.events.log(f"{Prisma.GRY}[OSSUARY]: Loaded {len(data['fossils'])} fossilized memories.{Prisma.RST}")
            if "mutations" in data:
                accepted_count = 0
                for cat, words in data["mutations"].items():
                    for w in words:
                        current_cat = TheLexicon.get_current_category(w)
                        if not current_cat:
                            current_cat = "unknown"
                        if current_cat == "unknown":
                            TheLexicon.teach(w, cat, 0)
                            accepted_count += 1
                self.events.log(f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations.{Prisma.RST}")
            if "config_mutations" in data:
                self.events.log(f"{Prisma.MAG}EPIGENETICS: Applying ancestral configuration shifts...{Prisma.RST}")
                for key, value in data["config_mutations"].items():
                    if hasattr(BoneConfig, key):
                        setattr(BoneConfig, key, value)
            if "joy_legacy" in data and data["joy_legacy"]:
                joy = data["joy_legacy"]
                flavor = joy.get("flavor")
                clade = LiteraryReproduction.JOY_CLADE.get(flavor)
                if clade:
                    self.events.log(f"{Prisma.CYN}INHERITED GLORY: {clade['title']} ({clade['desc']}){Prisma.RST}")
                    for stat, val in clade["buff"].items():
                        if hasattr(BoneConfig, stat):
                            setattr(BoneConfig, stat, val)
            if "core_graph" in data:
                self.graph.update(data["core_graph"])
                grafted_nodes = list(data["core_graph"].keys())
                for node in grafted_nodes:
                    if node in self.graph:
                        self.graph[node]["last_tick"] = current_tick
                sample_size = min(len(grafted_nodes), 10)
                if sample_size > 0:
                    self.cortical_stack.extend(random.sample(grafted_nodes, sample_size))
                self.events.log(f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} nodes. {sample_size} anchored to Cortical Stack.{Prisma.RST}")
            if "trauma_vector" in data:
                vec = data["trauma_vector"]
                self.events.log(f"{Prisma.CYN}[GENETICS]: Inheriting Trauma Vector: {vec}{Prisma.RST}")
                if vec.get("SEPTIC", 0) > 0.2: BoneConfig.TOXIN_WEIGHT *= 2.0
                if vec.get("CRYO", 0) > 0.2: BoneConfig.STAMINA_REGEN *= 0.5
                if vec.get("THERMAL", 0) > 0.2: BoneConfig.FLASHPOINT_THRESHOLD *= 0.8
                if vec.get("BARIC", 0) > 0.2: BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 1.5
            if "joy_vectors" in data and data["joy_vectors"]:
                best = data["joy_vectors"][0]
                if best.get("dominant_flavor") == "kinetic": BoneConfig.KINETIC_GAIN += 0.5
                elif best.get("dominant_flavor") == "abstract": BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 0.8
            return data.get("mitochondria", {}), set(data.get("antibodies", []))
        except Exception as err:
            self.events.log(f"{Prisma.RED}[MEMORY]: Spore rejected. {err}{Prisma.RST}")
            import traceback
            traceback.print_exc()
            return None

    def cleanup_old_sessions(self, limbo_layer=None):
        files = self.loader.list_spores()
        removed = 0
        for path, age, fname in files:
            file_age = time.time() - age
            if file_age > 86400 or (len(files) - removed > 20):
                try:
                    if limbo_layer: limbo_layer.absorb_dead_timeline(path)
                    if self.loader.delete_spore(path):
                        removed += 1
                except Exception:
                    pass
        if removed:
            self.events.log(f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}")

class HyphalInterface:
    def __init__(self):
        self.enzymes = {
            "LIGNASE": self._digest_structure,
            "CELLULASE": self._digest_narrative,
            "PROTEASE": self._digest_intent,
            "CHITINASE": self._digest_complex,
            "DECRYPTASE": self._digest_encrypted,
            "AMYLASE": self._digest_joy
        }
        self.biome = deque(maxlen=5)
        self.WEATHER_CIPHER = {"pressure", "humidity", "barometric", "temp", "forecast", "storm", "resource", "allocation"}

    def secrete(self, text, physics):
        code_markers = sum(1 for c in text if c in "{}[];=<>_()|")
        code_density = code_markers / max(1, len(text))
        meat_triggers = TheLexicon.get("meat")
        meat_count = sum(1 for w in physics["clean_words"] if w in meat_triggers)
        meat_density = meat_count / max(1, len(physics["clean_words"]))
        play_count = physics["counts"].get("play", 0)
        vital_count = physics["counts"].get("vital", 0)
        lines = [l for l in text.splitlines() if l.strip()]
        avg_line_len = len(text.split()) / max(1, len(lines))
        is_list = any(l.strip().startswith(("-", "*", "1.", "•")) for l in lines[:3])
        is_poetic = len(lines) > 2 and avg_line_len < 8 and not is_list
        enzyme_type = "CELLULASE"
        if play_count + vital_count > 1:
            enzyme_type = "AMYLASE"
        elif (code_density > 0.02 and meat_density > 0.05) or is_poetic:
            enzyme_type = "CHITINASE"
        elif code_density > 0.05 or "def " in text or "class " in text:
            enzyme_type = "LIGNASE"
        elif meat_density > 0.1 or "?" in text:
            enzyme_type = "PROTEASE"
        clean = physics.get("clean_words", [])
        cipher_hits = sum(1 for w in clean if w in self.WEATHER_CIPHER)
        if cipher_hits >= 2:
            enzyme_type = "DECRYPTASE"
        if "antigens" in physics and physics["antigens"]:
            for bug in physics["antigens"]:
                self.biome.append(bug)
        unique_bugs = len(set(self.biome))
        biome_mod = 1.0 + (math.log(unique_bugs + 1) * 0.3)
        extract_nutrients = self.enzymes.get(enzyme_type, self.enzymes["CELLULASE"])
        nutrient_profile = extract_nutrients()
        if unique_bugs > 0:
            nutrient_profile["yield"] *= biome_mod
            nutrient_profile["desc"] += f" (+{int((biome_mod-1)*100)}% Symbiotic Boost)"
        return enzyme_type, nutrient_profile

    @staticmethod
    def _digest_joy(_text=None):
        return {"type": "VITALITY", "yield": 25.0, "toxin": -5.0, "desc": "Pure Sugar (Joy/Play)"}

    @staticmethod
    def _digest_structure(text=None):
        loc = 0
        if text:
            lines = text.splitlines()
            loc = len([l for l in lines if l.strip()])
        return {"type": "STRUCTURAL", "yield": 15.0, "toxin": 5.0, "desc": f"Hard Lignin ({loc} LOC)", }

    @staticmethod
    def _digest_narrative(_text=None):
        return {"type": "NARRATIVE", "yield": 5.0, "toxin": -2.0, "desc": "Soft Cellulose", }

    @staticmethod
    def _digest_intent(_text=None):
        return {"type": "BIOLOGICAL", "yield": 8.0, "toxin": 0.0, "desc": "Raw Meat (User Intent)", }

    @staticmethod
    def _digest_complex(_text=None):
        return {"type": "COMPLEX", "yield": 20.0, "toxin": 8.0, "desc": "Chitin (Structured Intent / Poetry)", }

    @staticmethod
    def _digest_encrypted(_text=None):
        return {"type": "ENCRYPTED", "yield": 25.0, "toxin": 2.0, "desc": "Cipher Text (High Density / Puzzle Logic)", }

class ParasiticSymbiont:
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.spores_deployed = 0
        self.MAX_SPORES = 8

    def infect(self, physics_packet, stamina):
        psi = physics_packet.get("psi", 0.0)
        if stamina > 40.0 and psi < 0.6:
            return False, None
        if self.spores_deployed >= self.MAX_SPORES:
            if random.random() < 0.2:
                self.spores_deployed = max(0, self.spores_deployed - 1)
            return False, None
        heavy_candidates = [w for w in self.mem.graph if w in self.lex.get("heavy")]
        abstract_candidates = [w for w in self.mem.graph if w in self.lex.get("abstract")]
        if not heavy_candidates or not abstract_candidates:
            return False, None
        host = random.choice(heavy_candidates)
        parasite = random.choice(abstract_candidates)
        if parasite in self.mem.graph[host]["edges"]:
            return False, None
        is_metaphor = psi > 0.7
        weight = 8.88
        self.mem.graph[host]["edges"][parasite] = weight
        if parasite not in self.mem.graph:
            self.mem.graph[parasite] = {"edges": {}, "last_tick": 0}
        self.mem.graph[parasite]["edges"][host] = weight
        self.spores_deployed += 1
        if is_metaphor:
            return True, (
                f"{Prisma.CYN}✨ SYNAPSE SPARK: Your mind bridges '{host.upper()}' and '{parasite.upper()}'.\n"
                f"   A new metaphor is born. The map folds.{Prisma.RST}"
            )
        else:
            return True, (
                f"{Prisma.VIOLET}🍄 INTRUSIVE THOUGHT: Exhaustion logic links '{host.upper()}' <-> '{parasite.upper()}'.\n"
                f"   This makes no sense, yet there it is. 'Some things just happen.'{Prisma.RST}"
            )

class LichenSymbiont:
    @staticmethod
    def photosynthesize(phys, clean_words, tick_count):
        sugar = 0
        msgs = []
        light = phys["counts"].get("photo", 0)
        drag = phys["narrative_drag"]
        light_words = [w for w in clean_words if w in TheLexicon.get("photo")]
        if light > 0 and drag < 3.0:
            s = light * 2
            sugar += s
            source_str = ""
            if light_words:
                source_str = f" via '{random.choice(light_words)}'"
            msgs.append(f"{Prisma.GRN}PHOTOSYNTHESIS{source_str} (+{s}){Prisma.RST}")
        if sugar > 0:
            heavy_words = [w for w in clean_words if w in TheLexicon.get("heavy")]
            if heavy_words:
                h_word = random.choice(heavy_words)
                TheLexicon.teach(h_word, "photo", tick_count)
                msgs.append(
                    f"{Prisma.MAG}SUBLIMATION: '{h_word}' has become Light.{Prisma.RST}")
        return sugar, " ".join(msgs) if msgs else None

@dataclass
class EndocrineSystem:
    dopamine: float = 0.5
    oxytocin: float = 0.1
    cortisol: float = 0.0
    serotonin: float = 0.5
    adrenaline: float = 0.0
    melatonin: float = 0.0
    glimmers: int = 0
    REWARD_SMALL = 0.05
    REWARD_MEDIUM = 0.1
    REWARD_LARGE = 0.15
    STRESS_SMALL = 0.05
    STRESS_MEDIUM = 0.1
    STRESS_LARGE = 0.15
    DECAY_RATE = 0.01

    def _clamp(self, val: float) -> float:
        return max(0.0, min(1.0, val))

    def calculate_circadian_bias(self) -> Tuple[Dict[str, float], Optional[str]]:
        hour = time.localtime().tm_hour
        bias = {"COR": 0.0, "SER": 0.0, "MEL": 0.0}
        msg = None
        
        if 6 <= hour < 10: # DAWN
            bias["COR"] = 0.1
            msg = "Dawn Protocol: Cortisol rising."
        elif 10 <= hour < 18: # DAY
            bias["SER"] = 0.1
            msg = "Solar Cycle: Serotonin dominant."
        elif 18 <= hour < 23: # DUSK
            bias["MEL"] = 0.1
            msg = "Twilight Protocol: Melatonin rising."
        else: # NIGHT
            bias["MEL"] = 0.3
            bias["COR"] = -0.1
            msg = "Lunar Cycle: Melatonin max."
            
        return bias, msg

    def _apply_enzyme_reaction(self, enzyme_type: str, harvest_hits: int):
        if harvest_hits > 0:
            satiety_dampener = max(0.1, 1.0 - self.dopamine)
            base_reward = math.log(harvest_hits + 1) * 0.15
            final_reward = base_reward * satiety_dampener
            self.dopamine += final_reward
            self.cortisol -= (final_reward * 0.4)
        reactions = {
            "PROTEASE":   {"ADR": self.REWARD_MEDIUM},
            "CELLULASE":  {"COR": -self.REWARD_MEDIUM, "OXY": self.REWARD_SMALL},
            "CHITINASE":  {"DOP": self.REWARD_LARGE},
            "LIGNASE":    {"SER": self.REWARD_MEDIUM},
            "DECRYPTASE": {"ADR": self.REWARD_SMALL, "DOP": self.REWARD_SMALL},
            "AMYLASE":    {"SER": self.REWARD_LARGE, "OXY": self.REWARD_MEDIUM}
        }
        if enzyme_type in reactions:
            impact = reactions[enzyme_type]
            if "ADR" in impact: self.adrenaline += impact["ADR"]
            if "COR" in impact: self.cortisol += impact["COR"]
            if "OXY" in impact: self.oxytocin += impact["OXY"]
            if "DOP" in impact: self.dopamine += impact["DOP"]
            if "SER" in impact: self.serotonin += impact["SER"]

    def _apply_environmental_pressure(self, feedback: Dict, health: float, stamina: float, ros_level: float, stress_mod: float):
        if feedback.get("STATIC", 0) > 0.6:
            self.cortisol += (self.STRESS_LARGE * stress_mod)
        if feedback.get("INTEGRITY", 0) > 0.8:
            self.dopamine += self.REWARD_MEDIUM
        else:
            self.dopamine -= self.DECAY_RATE
        if stamina < 20.0:
            self.cortisol += (self.STRESS_MEDIUM * stress_mod)
            self.dopamine -= self.REWARD_MEDIUM
        if ros_level > 20.0:
            self.cortisol += (self.STRESS_LARGE * stress_mod)
        if health < 30.0 or feedback.get("STATIC", 0) > 0.8:
            self.adrenaline += (self.REWARD_LARGE * stress_mod)
        else:
            self.adrenaline -= (self.DECAY_RATE * 5)

    def _maintain_homeostasis(self, social_context: bool):
        if self.serotonin > 0.6:
            self.cortisol -= self.STRESS_SMALL
        if social_context:
            self.oxytocin += self.REWARD_MEDIUM
            self.cortisol -= self.REWARD_MEDIUM
        elif self.serotonin > 0.7 and self.cortisol < 0.3:
            self.oxytocin += self.REWARD_SMALL
        if self.cortisol > 0.7 and not social_context:
            self.oxytocin -= self.STRESS_SMALL
        if self.oxytocin > 0.6:
            self.cortisol -= self.REWARD_LARGE
        if self.adrenaline < 0.2:
            self.melatonin += (self.REWARD_SMALL / 2)
        else:
            self.melatonin = 0.0

    def check_for_glimmer(self, feedback: Dict, harvest_hits: int) -> Optional[str]:
        if feedback.get("INTEGRITY", 0) > 0.9 and feedback.get("STATIC", 0) < 0.2:
            self.glimmers += 1
            self.serotonin += 0.2
            return "GLIMMER: Perfect structural integrity detected. A moment of zen."
        if harvest_hits > 2 and self.dopamine > 0.8:
            self.glimmers += 1
            self.oxytocin += 0.2
            return "GLIMMER: Infectious enthusiasm detected. The work is good."
        return None

    def metabolize(self, feedback: Dict, health: float, stamina: float, ros_level: float = 0.0,
                   social_context: bool = False, enzyme_type: Optional[str] = None,
                   harvest_hits: int = 0, stress_mod: float = 1.0,
                   circadian_bias: Dict[str, float] = None) -> Dict[str, float]:
                   
        self._apply_enzyme_reaction(enzyme_type, harvest_hits)
        self._apply_environmental_pressure(feedback, health, stamina, ros_level, stress_mod)
        self._maintain_homeostasis(social_context)
        
        if circadian_bias:
            self.cortisol += circadian_bias.get("COR", 0.0)
            self.serotonin += circadian_bias.get("SER", 0.0)
            self.melatonin += circadian_bias.get("MEL", 0.0)
            
        glimmer_msg = self.check_for_glimmer(feedback, harvest_hits)
        
        # Clamping
        self.dopamine = self._clamp(self.dopamine)
        self.oxytocin = self._clamp(self.oxytocin)
        self.cortisol = self._clamp(self.cortisol)
        self.serotonin = self._clamp(self.serotonin)
        self.adrenaline = self._clamp(self.adrenaline)
        self.melatonin = self._clamp(self.melatonin)
        
        state = self.get_state()
        if glimmer_msg:
            state["glimmer_msg"] = glimmer_msg
        return state

    def get_state(self) -> Dict[str, float]:
        return {
            "DOP": round(self.dopamine, 2),
            "OXY": round(self.oxytocin, 2),
            "COR": round(self.cortisol, 2),
            "SER": round(self.serotonin, 2),
            "ADR": round(self.adrenaline, 2),
            "MEL": round(self.melatonin, 2)
        }

@dataclass
class MetabolicGovernor:
    mode: str = "COURTYARD"
    psi_mod: float = 0.2
    kappa_target: float = 0.0
    drag_floor: float = 2.0
    manual_override: bool = False
    birth_tick: float = field(default_factory=time.time)

    @staticmethod
    def get_stress_modifier(tick_count):
        if tick_count <= 2: return 0.0
        if tick_count <= 5: return 0.5
        return 1.0

    def set_override(self, target_mode):
        valid = {"COURTYARD", "LABORATORY", "FORGE", "SANCTUARY"}
        if target_mode in valid:
            self.mode = target_mode
            self.manual_override = True
            return f"MANUAL OVERRIDE: System locked to {target_mode}."
        return "INVALID MODE."

    def shift(self, physics: Dict, _voltage_history: List[float]) -> Optional[str]:
        if self.manual_override:
            return None
        current_voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        beta = physics.get("beta_index", 0.0)
        if current_voltage > 15.0 and beta > 1.5:
            if self.mode != "SANCTUARY":
                self.mode = "SANCTUARY"
                physics["narrative_drag"] = 0.0
                return f"{Prisma.GRN}GOVERNOR: VSL Critical (β: {beta:.2f}). Entering SANCTUARY.{Prisma.RST}"
        if current_voltage > 10.0:
            if self.mode != "FORGE":
                self.mode = "FORGE"
                return f"{Prisma.RED}GOVERNOR: High Voltage ({current_voltage:.1f}v). Locking to FORGE.{Prisma.RST}"
        if drag > 4.0 > current_voltage:
            if self.mode != "LABORATORY":
                self.mode = "LABORATORY"
                return f"{Prisma.CYN}GOVERNOR: High Drag detected. Restricting to LABORATORY.{Prisma.RST}"
        if self.mode != "COURTYARD":
            if current_voltage < 5.0 and drag < 2.0:
                self.mode = "COURTYARD"
                return f"{Prisma.GRN}GOVERNOR: All Clear. Relaxing to COURTYARD.{Prisma.RST}"
        return None

class NeuroPlasticity:
    def __init__(self):
        self.plasticity_mod = 1.0

    def force_hebbian_link(self, graph, word_a, word_b):
        if word_a == word_b: return None
        if word_a not in graph:
            graph[word_a] = {"edges": {}, "last_tick": 0}
        if word_b not in graph:
            graph[word_b] = {"edges": {}, "last_tick": 0}
        current_weight = graph[word_a]["edges"].get(word_b, 0.0)
        new_weight = min(10.0, current_weight + 2.5)
        graph[word_a]["edges"][word_b] = new_weight
        rev_weight = graph[word_b]["edges"].get(word_a, 0.0)
        graph[word_b]["edges"][word_a] = min(10.0, rev_weight + 1.0)
        return f"{Prisma.MAG}⚡ HEBBIAN GRAFT: Wired '{word_a}' <-> '{word_b}'. Synapse strengthened.{Prisma.RST}"

    def trigger_neurogenesis(self, lex, graph, unknown_word):
        target_cat = "abstract"
        lex.teach(unknown_word, target_cat, 0)
        if unknown_word not in graph:
            graph[unknown_word] = {"edges": {}, "last_tick": 0}
        return f"{Prisma.CYN}NEUROGENESIS: Assigned '{unknown_word}' to [ABSTRACT] cortex and seeded Memory.{Prisma.RST}"

class ShimmerState:
    def __init__(self, max_val=50.0):
        self.current = max_val
        self.max_val = max_val

    def recharge(self, amount):
        self.current = min(self.max_val, self.current + amount)

    def spend(self, amount):
        if self.current >= amount:
            self.current -= amount
            return True
        return False
