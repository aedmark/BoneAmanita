"""
body/system.py
The Central Organism.
This module acts as the physical container for the LLM. It binds the metabolic,
endocrine, and regulatory systems together into a single 'BioSystem'.
The 'SomaticLoop' class acts as the heartbeat, taking the raw mathematical
physics of a conversational turn and forcing the entire body to digest it.
"""
import math
from .models import Biometrics
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any, TYPE_CHECKING
from core import Prisma, LoreManifest
from struts import ux, safe_get, safe_set
from presets import BoneConfig
from spores import ImmuneMycelium, BioLichen, BioParasite
from body.metabolism import DigestiveTrack
from body.regulation import EndocrineRegulator, BioFeedback
from body.endocrine import SemanticEndocrinologist
from body.somatic import SynestheticCortex

if TYPE_CHECKING:
    from body.endocrine import EndocrineSystem


@dataclass
class BioSystem:
    """
    The Holistic Vessel.
    Holds the references to all biological subsystems. It doesn't execute the loop itself,
    but it serves as the stateful 'body' that all modules interact with.
    """
    mito: "MitochondrialForge"
    endo: "EndocrineSystem"
    governor: "MetabolicGovernor"
    immune: Optional[ImmuneMycelium] = None
    lichen: Optional[BioLichen] = None
    parasite: Optional[BioParasite] = None
    plasticity: Any = None
    shimmer: Any = None
    events: Any = None
    biometrics: Optional["Biometrics"] = None
    config_ref: Any = None

    def setup_listeners(self):
        """
        The 'Vagus Nerve'. Connects the biological layer to the global event bus
        so the body can react autonomously to abstract cognitive shifts without
        waiting for the next sequential heartbeat.
        """
        if self.events:
            self.events.subscribe("NEURAL_STATE_SHIFT", self._on_neural_shift)
            self.events.subscribe("SUBSTRATE_FORGED", self.mito.on_substrate_forged)
            self.events.subscribe("AUTOPHAGY_EVENT", self._on_autophagy_event)
            self.events.log("[BIO]: Vagus Nerve connected.", "SYS")
        narrative = LoreManifest.get_instance().get("BIO_NARRATIVE") or {}
        if self.mito:
            self.mito.narrative = narrative.get("MITO", {})
        if self.endo:
            self.endo.narrative_map = narrative.get("CIRCADIAN", {})
            self.endo.glimmer_map = narrative.get("GLIMMER", {})
        if self.governor:
            self.governor.text_map = narrative.get("GOVERNOR", {})
            self.governor.tax_map = narrative.get("TAX", {})

    def _on_autophagy_event(self, payload):
        """Emergency callback: The system literally consumed its own structural health for energy."""
        atp_gained = payload.get("atp_gained", 15.0)
        if self.mito:
            self.mito.adjust_atp(atp_gained, "Emergency Autophagy")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the biological state for the frontend UI or memory storage."""
        return {
            "mito": asdict(self.mito.state),
            "endo": self.endo.get_state(),
            "biometrics": asdict(self.biometrics) if self.biometrics else {},
            "governor_mode": self.governor.mode,
        }

    def rest(self, factor: float = 1.0) -> List[str]:
        """
        The biological healing mechanism.
        When invoked, it slowly recovers Health and Stamina, boosts Serotonin,
        and flushes Cortisol from the system.
        """
        b = self.biometrics
        if not b:
            return []
        target_cfg = self.config_ref or BoneConfig
        MAX_H = float(safe_get(target_cfg, "MAX_HEALTH", 100.0))
        MAX_S = float(safe_get(target_cfg, "MAX_STAMINA", 100.0))
        cfg = safe_get(target_cfg, "BIO", {})
        h_rec = float(safe_get(cfg, "REST_HEALTH_RECOVERY", 0.5))
        s_rec = float(safe_get(cfg, "REST_STAMINA_RECOVERY", 1.0))
        b.health = min(MAX_H, b.health + (h_rec * factor))
        b.stamina = min(MAX_S, b.stamina + (s_rec * factor))
        if self.endo:
            ser_boost = safe_get(cfg, "REST_SEROTONIN_BOOST", 0.05)
            cor_drop = safe_get(cfg, "REST_CORTISOL_DROP", 0.05)
            self.endo.serotonin = min(1.0, self.endo.serotonin + (ser_boost * factor))
            self.endo.cortisol = max(0.0, self.endo.cortisol - (cor_drop * factor))
        return []

    def _on_neural_shift(self, payload):
        """
        Reacts to high-level cognitive directives overriding the standard cycle.
        Forces the endocrine system into extreme states based on narrative commands.
        """
        state = payload.get("state", "NEUTRAL")
        bio_cfg = getattr(self.config_ref or BoneConfig, "BIO", None)
        shifts = getattr(bio_cfg, "NEURAL_SHIFTS", {}) if bio_cfg else {}
        if state == "PANIC":
            cfg = shifts.get("PANIC", {"adr": 0.3, "cor": 0.2})
            self.endo.adrenaline = min(1.0, self.endo.adrenaline + cfg.get("adr", 0.3))
            self.endo.cortisol = min(1.0, self.endo.cortisol + cfg.get("cor", 0.2))
            if self.events and (msg := ux("vagus_nerve", "panic_spike")):
                self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}", "BIO")
        elif state == "ZEN":
            cfg = shifts.get("ZEN", {"cor": -0.3, "ser": 0.2})
            self.endo.cortisol = max(0.0, self.endo.cortisol + cfg.get("cor", -0.3))
            self.endo.serotonin = min(1.0, self.endo.serotonin + cfg.get("ser", 0.2))
            if self.events and (msg := ux("vagus_nerve", "lucid_calm")):
                self.events.log(f"{Prisma.GRN}{msg}{Prisma.RST}", "BIO")
        elif state == "MANIC":
            self.mito.adjust_atp(shifts.get("MANIC", {}).get("atp", -10.0), "Neural Overclock")

    def apply_environmental_entropy(self, physics_packet):
        """
        Calculates the physical wear and tear of existing in a chaotic environment.
        Even if the LLM does nothing, high background entropy or thermal feedback
        (from intense arguments or broken logic) will slowly drain its health.
        """
        matter = safe_get(physics_packet, "matter", physics_packet)
        vector = safe_get(matter, "vector", {}) or {}
        ent_val = vector.get("ENT", 0.0)
        phi_val = vector.get("PHI", 0.0)
        em_field = math.hypot(ent_val, phi_val)
        target_cfg = self.config_ref or BoneConfig
        cfg = safe_get(target_cfg, "BIO", {})
        base_ent_bias = float(safe_get(cfg, "ENTROPY_BASE_BIAS", 0.2))
        shield_cap = safe_get(cfg, "SHIELD_MAX_STRENGTH", 0.8)
        shield_mult = safe_get(cfg, "SHIELD_MULTIPLIER", 0.1)
        heat_thresh = safe_get(cfg, "HEAT_THRESHOLD", 0.8)
        thermal_mult = safe_get(cfg, "THERMAL_FEEDBACK_MULT", 5.0)
        base_entropy = base_ent_bias + (ent_val * 1.0)
        shield_strength = min(shield_cap, em_field * shield_mult)
        effective_entropy = base_entropy * (1.0 - shield_strength)
        thermal_feedback = 0.0
        if em_field > heat_thresh:
            thermal_feedback = min(50.0, (em_field - heat_thresh) * thermal_mult)
            if self.events and (msg := ux("entropy_shield", "inductive_heating")):
                self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}", "BIO_WARN")
        total_drain = effective_entropy + thermal_feedback
        if self.biometrics:
            self.biometrics.health = max(0.0, self.biometrics.health - total_drain)
        if shield_strength > 0.2 and self.events and (msg := ux("entropy_shield", "shield_active")):
            self.events.log(f"{Prisma.CYN}{msg.format(mitigation=int(shield_strength * 100))}{Prisma.RST}", "PHYS")


class SomaticLoop:
    """
    The Beating Heart.
    This class orchestrates the chronological sequence of a biological 'tick'.
    It takes the raw text and physics of a conversational turn, calculates the
    metabolic cost, applies stress modifiers, evaluates emotional resonance,
    and outputs the final chemical state of the machine.
    """

    def __init__(self, bio_system_ref: BioSystem, memory_ref=None, lexicon_ref=None, events_ref=None, config_ref=None):
        self.bio = bio_system_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.digestive = DigestiveTrack(self.bio, lexicon_ref=lexicon_ref, config_ref=self.cfg)
        self.regulator = EndocrineRegulator(self.bio)
        self.feedback = BioFeedback(self.bio, config_ref=self.cfg)
        self.semantic_doctor = SemanticEndocrinologist(memory_ref, lexicon_ref)
        self.synesthesia = SynestheticCortex(self.bio, config_ref=self.cfg)
        self.narrative_data = (LoreManifest.get_instance(config_ref=self.cfg).get("BIO_NARRATIVE") or {})
        if not self.narrative_data:
            if self.events:
                self.events.log(f"{Prisma.OCHRE}[BODY]: Warning - BIO_NARRATIVE missing.{Prisma.RST}", "SYS")
            self.narrative_data = {"symptoms": {}, "organs": {}, "GLIMMER": {}, "GOVERNOR": {}}
        self.bio.endo.narrative_data = self.narrative_data
        self.bio.governor.narrative_data = self.narrative_data

    def digest_cycle(self, text: str, physics_data: Any, fb_dict: Dict, health: float, stamina: float,
                     stress_modifier: float, tick_count: int = 0, circadian_bias: Dict = None) -> Dict:
        """
        The Somatic Checkpoint. Binds the abstract physics of a conversation to physical metabolism.
        If the cognitive load (physics) exceeds our energy (ATP), this loop physically degrades
        the machine's health to force a response, preventing infinite friction-less thought.
        """
        text = str(text or "")
        phys = physics_data
        logs = []
        if not (b := self.bio.biometrics):
            return self._package_result("NECROSIS", ["Critical: Biological interface disconnected."])
        max_health = float(safe_get(self.cfg, "MAX_HEALTH", 100.0))
        max_stamina = float(safe_get(self.cfg, "MAX_STAMINA", 100.0))
        b.health = max(0.0, min(max_health, health))
        b.stamina = max(0.0, min(max_stamina, stamina))
        self.bio.apply_environmental_entropy(phys)
        modifier = self.regulator.get_metabolic_modifier(phys, logs)
        delta_silence = float(safe_get(phys, "silence", 0.0))
        if delta_silence > 0.6:
            drag_relief = delta_silence * 2.0
            stamina_recovery = delta_silence * 5.0
            current_drag = float(safe_get(phys, "narrative_drag", 0.0))
            safe_set(phys, "narrative_drag", max(0.0, current_drag - drag_relief))
            b.stamina = min(max_stamina, b.stamina + stamina_recovery)
            if msg := ux("somatic_loop", "silence_heals"):
                logs.append(f"{Prisma.CYN}{msg.format(recovery=stamina_recovery)}{Prisma.RST}")
        receipt = self.bio.mito.process_cycle(phys, modifier=modifier)
        if receipt.status == "ANAEROBIC":
            b.health = max(0.0, b.health - receipt.total_burn)
            msg = ux("somatic_loop", "anaerobic_burn")
            logs.append(f"{Prisma.RED}{msg.format(burn=receipt.total_burn)}{Prisma.RST}")
        safety_status = self.feedback.check_vital_signs(phys, b.stamina, logs)
        if safety_status == "MAUSOLEUM_CLAMP":
            return self._package_result(receipt.status, logs, chem_state=self.bio.endo.get_state())
        elif safety_status == "AUTOPHAGY":
            b.stamina = 10.0
        total_yield = 0.0
        enzyme = "NONE"
        clean_words = safe_get(phys, "clean_words", [])
        if self.bio.lichen:
            sugar, photo_log = self.bio.lichen.photosynthesize(phys, clean_words, tick_count)
            if sugar > 0:
                total_yield += sugar
            if photo_log:
                logs.append(photo_log)
        soma_enzyme, soma_yield, harvest_hits = self.digestive.harvest(phys, logs)
        total_yield += soma_yield
        enzyme = soma_enzyme
        self.bio.mito.adjust_atp(total_yield, "Symbiotic Yield")
        self.feedback.perform_maintenance(text, phys, logs, tick_count)
        semantic_sig = self.semantic_doctor.assess(clean_words, phys)
        impulse = self.synesthesia.perceive(phys)
        stamina_impact = self.synesthesia.apply_impulse(impulse)
        b.stamina = max(0.0, min(max_stamina, b.stamina + stamina_impact))
        qualia = self.synesthesia.get_current_qualia(impulse, config_ref=self.cfg)
        fb_dict.update({
            "PSI": float(safe_get(phys, "psi", 0.0)),
            "CHI": float(safe_get(phys, "chi", 0.0)),
            "VALENCE": float(safe_get(phys, "valence", 0.0)),
            "INTEGRITY": semantic_sig.coherence,
            "NOVELTY": semantic_sig.novelty,
            "STATIC": float(safe_get(phys, "entropy", 0.0)),
        })
        chem_state = self.bio.endo.metabolize(
            feedback=fb_dict,
            health=b.health,
            stamina=b.stamina,
            ros_level=self.bio.mito.state.ros_buildup,
            receipt=receipt,
            harvest_hits=harvest_hits,
            stress_mod=stress_modifier,
            enzyme_type=enzyme,
            circadian_bias=circadian_bias,
            semantic_signal=semantic_sig,
        )
        return self._package_result(receipt.status, logs, chem_state, enzyme, qualia)

    def _package_result(self, resp_status, logs, chem_state=None, enzyme="NONE", qualia=None):
        """Formats the final output packet for the Executive Layer."""
        atp_val = self.bio.mito.state.atp_pool
        stam_val = self.bio.biometrics.stamina if self.bio.biometrics else 100.0
        return {
            "respiration": resp_status,
            "is_alive": resp_status in ("RESPIRING", "ANAEROBIC"),
            "logs": logs,
            "chemistry": chem_state or {},
            "enzyme": enzyme,
            "atp": atp_val,
            "stamina": stam_val,
            "qualia": qualia,
        }
