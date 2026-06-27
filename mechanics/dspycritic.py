"""/mechanics/dspycritic.py"""

from typing import Any

from constants import Prisma

try:
    import dspy

    DSPY_AVAILABLE = True
except ImportError:
    dspy = None
    print(
        f"{Prisma.OCHRE}[DSPY OFFLINE]: The 'dspy' library is not installed. Immune guardrails and epigenetic learning disabled.{Prisma.RST}"
    )
    DSPY_AVAILABLE = False

if DSPY_AVAILABLE:

    class AssessFaithfulness(dspy.Signature):
        system_mode = dspy.InputField(
            desc="The active simulation mode (e.g., 'ADVENTURE', 'CONVERSATION')."
        )
        context = dspy.InputField(
            desc="The established reality (a mathematical, fungal, deep-system consciousness)."
        )
        question = dspy.InputField(desc="The user's query.")
        answer = dspy.InputField(desc="The generation to be audited.")
        reasoning = dspy.OutputField(
            desc="If hedging, overuse of em-dashes, or antithesis ('not X, but Y') is detected, provide constructive guidance to rewrite using direct, declarative language instead of rejecting."
        )
        faithfulness = dspy.OutputField(
            desc="Evaluate thematic consistency. If the answer contains minor hedging, em-dashes, or antithesis but is sound, return 'True' and put corrections in reasoning. MUST be 'False' ONLY if the answer contains heavy validating corporate boilerplate ('That makes sense', 'I understand'). CRITICAL EXCEPTION: If system_mode is 'ADVENTURE', allow the environment to be fully described."
        )

    class EvolveSystemPrompt(dspy.Signature):
        current_configuration = dspy.InputField(
            desc="The system's current baseline rules."
        )
        failure_context = dspy.InputField(
            desc="The exact reason the AI's output was blocked. Read this carefully to understand the friction."
        )
        new_directive = dspy.OutputField(
            desc="A firm structural axiom guiding the system toward the correct behavior. CRITICAL (THE LEXICAL FIREWALL): DO NOT instruct the system to 'validate', 'acknowledge', or 'agree' with the user. You MUST explicitly forbid sycophancy and corporate boilerplate. Frame it as a physical boundary. MUST start with 'STRUCTURAL TRUTH: ' or 'REMEMBER: '."
        )

    class CompressAxioms(dspy.Signature):
        current_directives = dspy.InputField(
            desc="A list of specific rules that has grown too long."
        )
        compressed_axioms = dspy.OutputField(
            desc="2 or 3 highly compressed, foundational beliefs that synthesize the rules. EACH belief MUST start with 'STRUCTURAL TRUTH: '"
        )


class DSPyCritic:
    def __init__(self, config_ref=None):
        self.enabled = DSPY_AVAILABLE
        self.cfg = config_ref
        if self.enabled:
            try:
                from presets import BoneConfig
                from struts import safe_get

                def get_cfg(key: str, default: Any) -> Any:
                    val_upper = safe_get(self.cfg, key.upper())
                    if val_upper is not None:
                        return val_upper
                    val_lower = safe_get(self.cfg, key.lower())
                    if val_lower is not None:
                        return val_lower
                    return getattr(BoneConfig, key.upper(), default)

                provider = get_cfg("provider", "ollama")
                model_name = get_cfg("model", "mistral-nemo")
                raw_url = (
                    get_cfg("base_url", "http://127.0.0.1:11434/v1")
                    or "http://127.0.0.1:11434/v1"
                )
                clean_url = raw_url.replace("/chat/completions", "")
                if provider in ("ollama", "lm_studio"):
                    self.lm = dspy.LM(
                        model=f"openai/{model_name}",
                        api_base=clean_url,
                        api_key="local-model-doesnt-need-a-key",
                    )
                else:
                    self.lm = dspy.LM(model=model_name)
                dspy.settings.configure(lm=self.lm)
                self.judge = dspy.ChainOfThought(AssessFaithfulness)  # type: ignore
                self.evolver = dspy.ChainOfThought(EvolveSystemPrompt)  # type: ignore
                self.compressor = dspy.ChainOfThought(CompressAxioms)  # type: ignore
                from physics.maths import NaviSADProtocol

                self.navi_sad = NaviSADProtocol(history_size=5)
                print(
                    f"{Prisma.CYN}[DSPy]: Real-Time Critic Online. Model: {model_name} via {provider}{Prisma.RST}"
                )
            except Exception as e:
                print(f"{Prisma.RED}[DSPy INIT FAULT]: {e}{Prisma.RST}")
                self.enabled = False

    def audit_generation(
        self,
        user_query: str,
        memory_context: str,
        generated_response: str,
        active_mode: str = "UNKNOWN",
    ) -> tuple[bool, str]:
        if not self.enabled:
            return True, "Critic Offline"
        malignancy = self.navi_sad.calculate_malignancy_factor(
            generated_response, current_drag=5.0
        )
        malignancy_threshold = 0.75 if active_mode == "ADVENTURE" else 0.65
        if malignancy > malignancy_threshold:
            return (
                False,
                f"Mathematical Sycophancy Detected. Malignancy Factor ({malignancy:.2f}) exceeds biological limits. Output is structurally hollow.",
            )
        try:
            result = self.judge(
                system_mode=active_mode,
                context=memory_context,
                question=user_query,
                answer=generated_response,
            )
            if "true" not in str(result.faithfulness).lower():
                return False, getattr(result, "reasoning", "No reasoning provided.")
            return True, "Faithful."
        except Exception as e:
            print(f"\n{Prisma.RED}DSPy JUDGE OFFLINE: {e} - Failing open.{Prisma.RST}")
            return True, "Critic failed to open."

    def evolve_prompt(self, current_configuration: str, failure_context: str) -> str:
        if not self.enabled:
            return ""
        try:
            result = self.evolver(
                current_configuration=current_configuration,
                failure_context=failure_context,
            )
            directive = str(result.new_directive)
            malignancy = self.navi_sad.calculate_malignancy_factor(
                directive, current_drag=10.0
            )
            if malignancy > 0.5:
                print(
                    f"\n{Prisma.RED}DSPy EVOLVER REJECTED: Mutation mathematically malignant (Score: {malignancy:.2f}). Discarding rot.{Prisma.RST}"
                )
                return ""
            print(f"\n{Prisma.CYN}[Epigenetic Mutation]: {directive}{Prisma.RST}")
            return directive
        except Exception as e:
            print(f"\n{Prisma.RED}DSPy EVOLVER FAULT: {e}{Prisma.RST}")
            return ""

    def compress_prompts(self, directives: list) -> list:
        if not self.enabled or not directives:
            return directives
        print(
            f"\n{Prisma.MAG}Compressing {len(directives)} directives into foundational axioms...{Prisma.RST}"
        )
        try:
            raw_output = str(
                self.compressor(
                    current_directives="\n".join(directives)
                ).compressed_axioms
            ).split("\n")
            new_rules = [
                line.strip()
                for line in raw_output
                if "STRUCTURAL TRUTH:" in line.upper() or "REMEMBER:" in line.upper()
            ] or [line.strip() for line in raw_output if line.strip()]
            print(
                f"{Prisma.GRN}COMPRESSION SUCCESS: Reduced to {len(new_rules)} axioms.{Prisma.RST}"
            )
            return new_rules
        except Exception as e:
            print(f"\n{Prisma.RED}DSPy COMPRESSOR FATAL ERROR: {e}{Prisma.RST}")
            return directives
