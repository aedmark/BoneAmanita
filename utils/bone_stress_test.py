""" bone_stress_test.py - "Pressure makes diamonds, or dust."
    Verifies the Reactive Layer: Kintsugi, Bureau, Folly, and Somatic Enzymes.
"""
import sys, os, time
from dataclasses import dataclass

from bone_main import BoneAmanita
from bone_core import Prisma, BoneConfig
from bone_protocols import KintsugiProtocol, TheBureau, TheFolly
from bone_lexicon import TheLexicon
from bone_body import SomaticLoop, BioSystem, Biometrics, MitochondrialForge, MitochondrialState, EndocrineSystem, MetabolicGovernor

class StressTest:
    def __init__(self):
        self.results = {"PASS": 0, "FAIL": 0}
        self.engine = None
        self.print_header()

    def print_header(self):
        print(f"\n{Prisma.CYN}=== REACTIVE SYSTEMS STRESS TEST (SLASH.MOD) ==={Prisma.RST}")
        print(f"{Prisma.GRY}Targeting: Kintsugi, Bureau, Folly, Enzymes{Prisma.RST}\n")

    def log(self, msg, status="INFO"):
        color = Prisma.WHT
        if status == "PASS": color = Prisma.GRN
        elif status == "FAIL": color = Prisma.RED
        print(f"{color}[{status}] {msg}{Prisma.RST}")
        if status in self.results:
            self.results[status] += 1

    def setup_engine(self):
        config = {"provider": "mock", "model": "stress-unit", "user_name": "TESTER"}
        self.engine = BoneAmanita(config)
        self.kintsugi = KintsugiProtocol()
        self.bureau = TheBureau()
        self.folly = TheFolly()
        if not hasattr(self.engine, 'body') or not self.engine.body:
            mito_state = MitochondrialState()
            mito = MitochondrialForge(mito_state, self.engine.events)
            endo = EndocrineSystem()
            gov = MetabolicGovernor()
            bio = BioSystem(
                mito=mito, endo=endo,
                immune=None, lichen=None,
                plasticity=None, governor=gov,
                shimmer=None, parasite=None)
            self.engine.body = SomaticLoop(bio, self.engine.mind.mem, self.engine.lex, self.folly, self.engine.events)
            if not hasattr(self.engine.body.bio, 'biometrics'):
                self.engine.body.bio.biometrics = Biometrics(health=100.0, stamina=100.0)

    def test_kintsugi_gold(self):
        print(f"{Prisma.WHT}--- TEST 1: KINTSUGI (The Golden Repair) ---{Prisma.RST}")
        trauma_accum = {"SEPTIC": 5.0, "CRYO": 0.0}
        self.kintsugi.active_koan = "The crack is where the light enters."
        mock_phys = type('obj', (object,), {
            "voltage": 12.0,
            "clean_words": ["dream", "play", "cloud", "dance", "system"]})
        soul = self.engine.soul
        soul.traits.wisdom = 0.5
        initial_wisdom = soul.traits.wisdom
        result = self.kintsugi.attempt_repair(mock_phys, trauma_accum, soul_ref=soul)
        if result and result["success"] and "Integrated SEPTIC" in str(result.get("healed")):
            self.log("Trauma correctly integrated (Golden Repair).", "PASS")
        else:
            self.log(f"Repair failed or wrong path taken: {result.get('msg') if result else 'None'}", "FAIL")
        if soul.traits.wisdom > initial_wisdom:
            self.log(f"Wisdom boosted ({initial_wisdom} -> {soul.traits.wisdom:.2f}).", "PASS")
        else:
            self.log("Wisdom failed to increase.", "FAIL")

    def test_kintsugi_scar(self):
        print(f"\n{Prisma.WHT}--- TEST 2: KINTSUGI (The Scar) ---{Prisma.RST}")
        trauma_accum = {"THERMAL": 4.0}
        self.kintsugi.active_koan = "Endure."
        mock_phys = type('obj', (object,), {
            "voltage": 5.0,
            "clean_words": ["data", "chart", "file"]})
        result = self.kintsugi.attempt_repair(mock_phys, trauma_accum, soul_ref=None)
        if result and result["success"] and "Scarred THERMAL" in str(result.get("healed")):
            self.log("Trauma correctly scarred (Fallback Path).", "PASS")
        else:
            self.log(f"Scarring failed: {result.get('msg') if result else 'None'}", "FAIL")

    def test_bureaucracy(self):
        print(f"\n{Prisma.WHT}--- TEST 3: THE BUREAU (Red Tape) ---{Prisma.RST}")
        mock_phys_bad = {
            "voltage": 25.0,
            "truth_ratio": 0.2,
            "clean_words": ["chaos", "fire"],
            "counts": {}}
        mock_bio = {"health": 100.0}
        audit_bad = self.bureau.audit(mock_phys_bad, mock_bio)
        if audit_bad and "ZONING_VIOLATION" in audit_bad["ui"]:
            self.log("Bureau correctly flagged Zoning Violation.", "PASS")
        else:
            self.log(f"Failed to flag violation. Got: {audit_bad.get('ui') if audit_bad else 'None'}", "FAIL")
        mock_phys_good = {
            "voltage": 22.0,
            "truth_ratio": 0.95,
            "clean_words": ["beauty", "truth"],
            "counts": {}}
        audit_good = self.bureau.audit(mock_phys_good, mock_bio)
        if audit_good and "Form 202-A" in audit_good["ui"]:
            self.log("Bureau honored Artistic License (Form 202-A).", "PASS")
        else:
            self.log(f"Failed to recognize Art. Got: {audit_good.get('ui') if audit_good else 'None'}", "FAIL")

    def test_folly_mechanics(self):
        print(f"\n{Prisma.WHT}--- TEST 4: THE FOLLY (Metabolism 1.0) ---{Prisma.RST}")
        current_atp = 10.0
        self.folly.gut_memory.clear()
        test_word = "stone"
        status, log, yield_val, loot = self.folly.grind_the_machine(
            current_atp,
            [test_word],
            TheLexicon)
        if status == "MEAT_GRINDER" and yield_val > 0:
            self.log(f"The Folly ate '{test_word}' (+{yield_val} ATP).", "PASS")
        else:
            self.log(f"The Folly refused to eat. Status: {status}", "FAIL")
        status, _, _, _ = self.folly.grind_the_machine(current_atp, [test_word], TheLexicon)
        if status == "REGURGITATION":
            self.log("The Folly correctly regurgitated duplicate input.", "PASS")
        else:
            self.log(f"Folly failed to regurgitate. Status: {status}", "FAIL")

    def test_enzymatic_digestion(self):
        print(f"\n{Prisma.WHT}--- TEST 5: SOMATIC ENZYMES (Metabolism 2.0) ---{Prisma.RST}")
        original_classifier = TheLexicon.get_current_category
        def mock_classifier(w):
            if w == "concept": return "abstract"
            if w == "cliche": return "antigen"
            return "void"
        TheLexicon.get_current_category = mock_classifier
        try:
            body = self.engine.body
            phys_abstract = type('obj', (object,), {"voltage": 5.0, "clean_words": ["concept"], "beta_index": 0.0, "truth_ratio": 1.0, "repetition": 0.0})

            result_a = body.digest_cycle("concept", phys_abstract, {}, 100, 100, 1.0, 0)
            if result_a["enzyme"] == "DECRYPTASE":
                self.log("Enzyme 'DECRYPTASE' correctly identified for abstract word.", "PASS")
            else:
                self.log(f"Failed to trigger DECRYPTASE. Got: {result_a.get('enzyme')}", "FAIL")
            body.bio.mito.state.atp_pool = 50.0
            result_b = body.digest_cycle("concept", phys_abstract, {}, 100, 100, 1.0, 0)
            phys_toxic = type('obj', (object,), {"voltage": 5.0, "clean_words": ["cliche"], "beta_index": 0.0, "truth_ratio": 1.0, "repetition": 0.0})
            pre_atp = body.bio.mito.state.atp_pool
            body.digest_cycle("cliche", phys_toxic, {}, 100, 100, 1.0, 0)
            post_atp = body.bio.mito.state.atp_pool
            if post_atp < pre_atp:
                self.log(f"Antigen correctly taxed system (ATP {pre_atp} -> {post_atp}).", "PASS")
            else:
                self.log(f"Antigen failed to drain ATP (ATP {pre_atp} -> {post_atp}).", "FAIL")
        finally:
            TheLexicon.get_current_category = original_classifier

    def run(self):
        self.setup_engine()
        self.test_kintsugi_gold()
        self.test_kintsugi_scar()
        self.test_bureaucracy()
        self.test_folly_mechanics()
        self.test_enzymatic_digestion()

        print(f"\n{Prisma.CYN}=== STRESS TEST COMPLETE ==={Prisma.RST}")
        print(f"PASSED: {self.results['PASS']}")
        print(f"FAILED: {self.results['FAIL']}")
        if self.results['FAIL'] == 0:
            print(f"{Prisma.GRN}System integrity nominal. Ready for deployment.{Prisma.RST}")
        else:
            print(f"{Prisma.RED}System fractures detected.{Prisma.RST}")

if __name__ == "__main__":
    test = StressTest()
    test.run()