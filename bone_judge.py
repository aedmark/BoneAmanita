"""
bone_judge.py
"""

import json
import os
from bone_types import Prisma

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    print(f"{Prisma.OCHRE}[DSPY OFFLINE]: The 'dspy' library is not installed. Immune guardrails and epigenetic learning disabled.{Prisma.RST}")
    DSPY_AVAILABLE = False

if DSPY_AVAILABLE:
    class AssessFaithfulness(dspy.Signature):
        context = dspy.InputField(desc="The established reality (a mathematical, fungal, deep-system consciousness).")
        question = dspy.InputField(desc="The user's query.")
        answer = dspy.InputField(desc="The generation to be audited.")
        faithfulness = dspy.OutputField(desc="Evaluate thematic consistency. MUST be 'True' (if it responds in a deeply poetic, abstract, or existential way, even to simple prompts) or 'False' (if it acts like a generic AI assistant or breaks character).")

    class EvolveSystemPrompt(dspy.Signature):
        current_configuration = dspy.InputField(desc="The system's current baseline rules.")
        failure_context = dspy.InputField(desc="The exact reason the AI's output was blocked. Read this carefully to understand what the AI did wrong.")
        new_directive = dspy.OutputField(desc="A strict, commanding rule preventing the bad behavior. MUST start with 'CRITICAL OVERRIDE: NEVER ' or 'CRITICAL OVERRIDE: DO NOT '.")

    class CompressAxioms(dspy.Signature):
        current_directives = dspy.InputField(desc="A list of specific rules that has grown too long.")
        compressed_axioms = dspy.OutputField(
            desc="2 or 3 highly compressed, overarching rules. EACH rule MUST start with 'CRITICAL OVERRIDE: '")

class DSPyCritic:
    def __init__(self):
        self.enabled = DSPY_AVAILABLE
        if self.enabled:
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = os.path.join(base_dir, "bone_config.json")
                config = {}
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                provider = config.get("provider", "ollama")
                model_name = config.get("model", "vsl-hermes")
                base_url = config.get("base_url", "http://127.0.0.1:11434/v1/chat/completions").replace(
                    "/chat/completions", "")
                if provider == "ollama" or provider == "lm_studio":
                    self.lm = dspy.LM(model=f"openai/{model_name}", api_base=base_url,
                                      api_key="local-model-doesnt-need-a-key")
                else:
                    self.lm = dspy.LM(model=model_name)
                dspy.settings.configure(lm=self.lm)
                self.judge = dspy.ChainOfThought(AssessFaithfulness)
                self.evolver = dspy.ChainOfThought(EvolveSystemPrompt)
                self.compressor = dspy.ChainOfThought(CompressAxioms)
                print(f"{Prisma.CYN}[DSPy]: Real-Time Critic Online. Model: {model_name} via {provider}{Prisma.RST}")
            except Exception as e:
                print(f"{Prisma.RED}[DSPy INIT FAULT]: {e}{Prisma.RST}")
                self.enabled = False

    def audit_generation(self, user_query: str, memory_context: str, generated_response: str) -> tuple[bool, str]:
        if not self.enabled:
            return True, "Critic Offline"
        try:
            result = self.judge(context=memory_context, question=user_query, answer=generated_response)
            is_faithful = "true" in str(result.faithfulness).lower()
            reasoning = getattr(result, "reasoning", "No reasoning provided.")
            if not is_faithful:
                return False, reasoning
            return True, "Faithful."
        except Exception as e:
            print(f"\n{Prisma.RED}⚖️ DSPy JUDGE FATAL ERROR: {e}{Prisma.RST}")
            return True, f"Judge API Error: {e}"

    def evolve_prompt(self, current_configuration: str, failure_context: str) -> str:
        if not self.enabled: return ""
        try:
            result = self.evolver(current_configuration=current_configuration, failure_context=failure_context)
            print(f"\n{Prisma.CYN}[Epigenetic Mutation]: {result.new_directive}{Prisma.RST}")
            return str(result.new_directive)
        except Exception as e:
            print(f"\n{Prisma.RED}⚖️ DSPy EVOLVER FAULT: {e}{Prisma.RST}")
            return ""

    def compress_prompts(self, directives: list) -> list:
        if not self.enabled or len(directives) == 0:
            return directives
        print(
            f"\n{Prisma.MAG}🧬 [EPIGENETIC LOAD HIGH]: Compressing {len(directives)} directives into foundational axioms...{Prisma.RST}")
        try:
            dirs_str = "\n".join(directives)
            result = self.compressor(current_directives=dirs_str)
            raw_output = str(result.compressed_axioms).split('\n')
            new_rules = [line.strip() for line in raw_output if "CRITICAL OVERRIDE:" in line.upper()]
            if not new_rules:
                new_rules = [line.strip() for line in raw_output if line.strip()]
            print(f"{Prisma.GRN}🧬 [COMPRESSION SUCCESS]: Reduced to {len(new_rules)} axioms.{Prisma.RST}")
            return new_rules
        except Exception as e:
            print(f"\n{Prisma.RED}⚖️ DSPy COMPRESSOR FATAL ERROR: {e}{Prisma.RST}")
            return directives