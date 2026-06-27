"""body/system.py"""

import math
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from body.endocrine import SemanticEndocrinologist
from body.metabolism import DigestiveTrack
from body.regulation import BioFeedback, EndocrineRegulator
from body.somatic import SynestheticCortex
from core import LoreManifest, Prisma
from presets import BoneConfig
from spores import BioLichen, BioParasite
from struts import safe_get, safe_set, ux

from .models import Biometrics

if TYPE_CHECKING:
    from body.endocrine import EndocrineSystem
    from body.metabolism import MitochondrialForge
    from body.regulation import MetabolicGovernor


@dataclass
class BioSystem:
    mito: "MitochondrialForge"
    endo: "EndocrineSystem"
    governor: "MetabolicGovernor"
    lichen: Optional[BioLichen] = None
    parasite: Optional[BioParasite] = None
    plasticity: Any = None
    shimmer: Any = None
    events: Any = None
    biometrics: Optional["Biometrics"] = None
    config_ref: Any = None

    def setup_listeners(self):
        if self.events:
            self.events.subscribe("NEURAL_STATE_SHIFT", self._on_neural_shift)
            self.events.subscribe("SUBSTRATE_FORGED", self.mito.on_substrate_forged)
            self.events.subscribe("AUTOPHAGY_EVENT", self._on_autophagy_event)
            self.events.log("Vagus Nerve connected.", "SYS")
        narrative = (
            LoreManifest.get_instance(config_ref=self.config_ref).get("BIO_NARRATIVE")
            or {}
        )
        self.mito.narrative = narrative.get("MITO", {})
        self.endo.narrative_map = narrative.get("CIRCADIAN", {})
        self.endo.glimmer_map = narrative.get("GLIMMER", {})
        self.governor.text_map = narrative.get("GOVERNOR", {})
        self.governor.tax_map = narrative.get("TAX", {})

    def _on_autophagy_event(self, payload):
        self.mito.adjust_atp(payload.get("atp_gained", 15.0), "Emergency Autophagy")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mito": asdict(self.mito.state),
            "endo": self.endo.get_state(),
            "biometrics": asdict(self.biometrics) if self.biometrics else {},
            "governor_mode": self.governor.mode,
        }

    def expend_glimmer(self) -> bool:
        if self.endo.glimmers >= 1:
            self.endo.glimmers = self.endo.glimmers - 1
            return True
        return False

    def rest(self, factor: float = 1.0) -> List[str]:
        b = self.biometrics
        if not b:
            return []
        target_cfg = self.config_ref or BoneConfig
        MAX_H = float(safe_get(target_cfg, "MAX_HEALTH", 100.0))
        MAX_S = float(safe_get(target_cfg, "MAX_STAMINA", 100.0))
        bio_cfg = safe_get(target_cfg, "BIO", {})
        h_rec = float(safe_get(bio_cfg, "REST_HEALTH_RECOVERY", 0.5))
        s_rec = float(safe_get(bio_cfg, "REST_STAMINA_RECOVERY", 1.0))
        ser_boost = float(safe_get(bio_cfg, "REST_SEROTONIN_BOOST", 0.05))
        cor_drop = float(safe_get(bio_cfg, "REST_CORTISOL_DROP", 0.05))
        b.health = min(MAX_H, b.health + (h_rec * factor))
        b.stamina = min(MAX_S, b.stamina + (s_rec * factor))
        self.endo.serotonin = min(1.0, self.endo.serotonin + (ser_boost * factor))
        self.endo.cortisol = max(0.0, self.endo.cortisol - (cor_drop * factor))
        return []

    def _on_neural_shift(self, payload):
        state = payload.get("state", "NEUTRAL")
        bio_cfg = safe_get(self.config_ref or BoneConfig, "BIO") or {}
        shifts = safe_get(bio_cfg, "NEURAL_SHIFTS") or {}

        if state == "PANIC":
            cfg = shifts.get("PANIC") or {"adr": 0.3, "cor": 0.2}
            self.endo.adrenaline = min(1.0, self.endo.adrenaline + cfg.get("adr", 0.3))
            self.endo.cortisol = min(1.0, self.endo.cortisol + cfg.get("cor", 0.2))
            if self.events and (msg := ux("vagus_nerve", "panic_spike")):
                self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}", "BIO")
        elif state == "ZEN":
            cfg = shifts.get("ZEN") or {"cor": -0.3, "ser": 0.2}
            self.endo.cortisol = max(0.0, self.endo.cortisol + cfg.get("cor", -0.3))
            self.endo.serotonin = min(1.0, self.endo.serotonin + cfg.get("ser", 0.2))
            if self.events and (msg := ux("vagus_nerve", "lucid_calm")):
                self.events.log(f"{Prisma.GRN}{msg}{Prisma.RST}", "BIO")
        elif state == "MANIC":
            manic_cfg = shifts.get("MANIC") or {}
            self.mito.adjust_atp(manic_cfg.get("atp", -10.0), "Neural Overclock")

    def apply_environmental_entropy(self, physics_packet):
        vector = safe_get(physics_packet, "vector") or {}
        ent_val = vector.get("ENT", 0.0)
        phi_val = vector.get("PHI", 0.0)
        em_field = math.hypot(ent_val, phi_val)
        target_cfg = self.config_ref or BoneConfig
        cfg = safe_get(target_cfg, "BIO") or {}
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
        if (
            shield_strength > 0.2
            and self.events
            and (msg := ux("entropy_shield", "shield_active"))
        ):
            self.events.log(
                f"{Prisma.CYN}{msg.format(mitigation=int(shield_strength * 100))}{Prisma.RST}",
                "PHYS",
            )


class SomaticLoop:
    def __init__(
        self,
        bio_system_ref: BioSystem,
        memory_ref=None,
        lexicon_ref=None,
        events_ref=None,
        config_ref=None,
    ):
        self.bio = bio_system_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.digestive = DigestiveTrack(
            self.bio, lexicon_ref=lexicon_ref, config_ref=self.cfg
        )
        self.regulator = EndocrineRegulator(self.bio)
        self.feedback = BioFeedback(self.bio, config_ref=self.cfg)
        self.semantic_doctor = SemanticEndocrinologist(memory_ref, lexicon_ref)
        self.synesthesia = SynestheticCortex(self.bio, config_ref=self.cfg)
        self.narrative_data = (
            LoreManifest.get_instance(config_ref=self.cfg).get("BIO_NARRATIVE") or {}
        )
        if not self.narrative_data:
            if self.events:
                self.events.log(
                    f"{Prisma.OCHRE}Warning - BIO_NARRATIVE missing.{Prisma.RST}", "SYS"
                )
            self.narrative_data = {
                "symptoms": {},
                "organs": {},
                "GLIMMER": {},
                "GOVERNOR": {},
            }
        self.bio.endo.narrative_data = self.narrative_data
        self.bio.governor.narrative_data = self.narrative_data

    def digest_cycle(
        self,
        text: str,
        physics_data: Any,
        fb_dict: Dict,
        health: float,
        stamina: float,
        stress_modifier: float,
        tick_count: int = 0,
        circadian_bias: Optional[Dict] = None,
    ) -> Dict:
        text = str(text or "")
        phys = physics_data
        logs = []
        if not (b := self.bio.biometrics):
            return self._package_result(
                "NECROSIS", ["Critical: Biological interface disconnected."]
            )
        max_health = float(safe_get(self.cfg, "MAX_HEALTH", 100.0))
        max_stamina = float(safe_get(self.cfg, "MAX_STAMINA", 100.0))
        voltage = float(safe_get(phys, "voltage", 0.0))
        entropy = float(safe_get(phys, "chi", safe_get(phys, "entropy", 0.0)))
        is_crisis = voltage > 85.0 or entropy > 0.85
        health_mod, stamina_mod = (0.0, 0.0) if is_crisis else (3.0, 10.0)
        b.health = max(0.0, min(max_health, health + health_mod))
        b.stamina = max(0.0, min(max_stamina, stamina + stamina_mod))
        if not is_crisis and self.bio.mito.state.atp_pool < 20.0:
            self.bio.mito.adjust_atp(15.0, "Emergency Vagus Nerve Support")
        elif is_crisis:
            logs.append(
                f"{Prisma.RED}CRITICAL: Systemic crisis detected (V={voltage:.1f}, E={entropy:.2f}). Vagus nerve support severed.{Prisma.RST}"
            )
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
                logs.append(
                    f"{Prisma.CYN}{msg.format(recovery=stamina_recovery)}{Prisma.RST}"
                )
        receipt = self.bio.mito.process_cycle(phys, modifier=modifier)
        if receipt.status == "ANAEROBIC":
            b.health = max(0.0, b.health - receipt.total_burn)
            if msg := ux("somatic_loop", "anaerobic_burn"):
                logs.append(
                    f"{Prisma.RED}{msg.format(burn=receipt.total_burn)}{Prisma.RST}"
                )
        safety_status = self.feedback.check_vital_signs(phys, b.stamina, logs)
        if safety_status == "MAUSOLEUM_CLAMP":
            return self._package_result(
                receipt.status, logs, chem_state=self.bio.endo.get_state()
            )
        elif safety_status == "AUTOPHAGY":
            b.stamina = 10.0
        is_safe, _ = self.bio.governor.assess(phys)
        if is_safe:
            b.stamina = min(max_stamina, b.stamina + 3.0)
            self.bio.mito.adjust_atp(3.0, "PID Homeostasis")
            self.bio.mito.state.ros_buildup = max(
                0.0, self.bio.mito.state.ros_buildup - 2.0
            )
            logs.append(
                f"{Prisma.GRN}Homeostasis active. Resting in Safe Room.{Prisma.RST}"
            )

        total_yield = 0.0
        enzyme = "NONE"
        clean_words = safe_get(phys, "clean_words", [])

        if self.bio.lichen:
            sugar, photo_log = self.bio.lichen.photosynthesize(
                phys, clean_words, tick_count
            )
            if sugar > 0:
                total_yield = total_yield + sugar
            if photo_log:
                logs.append(photo_log)

        soma_enzyme, soma_yield, harvest_hits = self.digestive.harvest(phys, logs)
        total_yield = total_yield + soma_yield
        enzyme = soma_enzyme
        self.bio.mito.adjust_atp(total_yield, "Symbiotic Yield")
        self.feedback.perform_maintenance(text, phys, logs, tick_count)
        semantic_sig = self.semantic_doctor.assess(clean_words, phys)
        impulse = self.synesthesia.perceive(phys)
        stamina_impact = self.synesthesia.apply_impulse(impulse)
        b.stamina = max(0.0, min(max_stamina, b.stamina + stamina_impact))
        qualia = self.synesthesia.get_current_qualia(impulse, config_ref=self.cfg)

        fb_dict.update(
            {
                "PSI": float(safe_get(phys, "psi", 0.0)),
                "CHI": float(safe_get(phys, "chi", 0.0)),
                "VALENCE": float(safe_get(phys, "valence", 0.0)),
                "INTEGRITY": semantic_sig.coherence,
                "NOVELTY": semantic_sig.novelty,
                "STATIC": float(safe_get(phys, "entropy", 0.0)),
            }
        )

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

    def _package_result(
        self, resp_status, logs, chem_state=None, enzyme="NONE", qualia=None
    ):
        atp_val = self.bio.mito.state.atp_pool
        stam_val = self.bio.biometrics.stamina if self.bio.biometrics else 100.0
        return {
            "respiration": resp_status,
            "is_alive": resp_status not in ("NECROSIS", "APOPTOSIS", "FATAL"),
            "logs": logs,
            "chemistry": chem_state or {},
            "enzyme": enzyme,
            "atp": atp_val,
            "stamina": stam_val,
            "qualia": qualia,
        }
