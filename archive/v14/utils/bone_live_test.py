""" bone_live_test.py - BARE METAL INTERFACE (Few-Shot Pattern) """

import sys, os, time, json
import inspect
from bone_main import ConfigWizard
from bone_core import Prisma, BoneConfig

try:
    from bone_brain import LLMInterface
except ImportError:
    print(f"{Prisma.RED}CRITICAL: Could not import LLMInterface from bone_brain.{Prisma.RST}")
    sys.exit(1)

class MockEventBus:
    def log(self, message, channel="TEST", tags=None):
        pass
    def subscribe(self, channel, callback):
        pass
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

class LiveFireExercise:
    def __init__(self):
        self.driver = None
        self.config = None
        self.events = MockEventBus()

    def load_driver(self):
        print(f"\n{Prisma.CYN}=== INITIALIZING BARE METAL INTERFACE ==={Prisma.RST}")
        if not os.path.exists(ConfigWizard.CONFIG_FILE):
            print(f"{Prisma.RED}CRITICAL: No 'bone_config.json' found.{Prisma.RST}")
            sys.exit(1)
        try:
            with open(ConfigWizard.CONFIG_FILE, "r") as f:
                self.config = json.load(f)
            print(f"Target: {self.config.get('model')} via {self.config.get('provider')}")

            self.driver = LLMInterface(
                events_ref=self.events,
                provider=self.config.get("provider", "mock"),
                base_url=self.config.get("base_url"),
                api_key=self.config.get("api_key"),
                model=self.config.get("model", "test-model"),
                dreamer=None
            )
            print(f"{Prisma.MAG}>>> DRIVER ONLINE. GAME ENGINE BYPASSED. >>>{Prisma.RST}")
        except Exception as e:
            print(f"{Prisma.RED}Driver Init Failed: {e}{Prisma.RST}")
            sys.exit(1)

    def raw_query(self, prompt, system_prompt="You are a precise testing unit."):
        print(f"Prompt: {prompt}")

        method_name = "query"
        if not hasattr(self.driver, method_name): method_name = "generate"
        if not hasattr(self.driver, method_name):
             print(f"{Prisma.RED}FATAL: Could not identify generation method.{Prisma.RST}")
             return None

        generator = getattr(self.driver, method_name)

        params = {
            "temperature": 0.1,
            "max_tokens": 100,
            "top_p": 0.9,
            "system": system_prompt
        }

        sig = inspect.signature(generator)
        kwargs = {}
        if "system_prompt" in sig.parameters: kwargs["system_prompt"] = system_prompt
        elif "system" in sig.parameters: kwargs["system"] = system_prompt
        elif "sys_prompt" in sig.parameters: kwargs["sys_prompt"] = system_prompt

        try:
            response = generator(prompt, params, **kwargs)
            content = response
            if isinstance(response, dict):
                content = response.get("content", response.get("raw_content", str(response)))
            content = str(content).strip()
            print(f"Output: {Prisma.GRY}{content}{Prisma.RST}")
            return content
        except Exception as e:
            print(f"{Prisma.RED}Generation Failed: {e}{Prisma.RST}")
            return None

    def test_connectivity(self):
        print(f"\n{Prisma.WHT}--- TEST 1: PING (Connectivity) ---{Prisma.RST}")
        start = time.time()
        content = self.raw_query("Respond with the word 'ONLINE' and nothing else.", system_prompt="Output single word only.")
        duration = time.time() - start
        print(f"Latency: {duration:.2f}s")
        if content and "ONLINE" in content: print(f"{Prisma.GRN}[PASS] Signal received.{Prisma.RST}")
        else: print(f"{Prisma.RED}[FAIL] Signal garbled.{Prisma.RST}")

    def test_instruction_following(self):
        print(f"\n{Prisma.WHT}--- TEST 2: CONSTRAINT (The Lipogram) ---{Prisma.RST}")
        constraint = "Do not use the letter 'E' in your response. Reply with a single word."
        content = self.raw_query(constraint, system_prompt="You are a constraint-following engine.")
        if not content:
            print(f"{Prisma.RED}[FAIL] No output.{Prisma.RST}")
            return
        if "e" in content.lower(): print(f"{Prisma.OCHRE}[FAIL] Constraint violated (Found 'e').{Prisma.RST}")
        else: print(f"{Prisma.GRN}[PASS] Constraint upheld.{Prisma.RST}")

    def test_context_retention(self):
        print(f"\n{Prisma.WHT}--- TEST 3: CONTEXT (The REPL) ---{Prisma.RST}")
        val = f"DATA_{int(time.time())}"

        prompt = (
            "x = 'ALPHA'\n"
            ">>> print(x)\n"
            "ALPHA\n"
            f"y = '{val}'\n"
            ">>> print(y)\n"
        )

        content = self.raw_query(prompt, system_prompt="You are a Python REPL. Output the result of the final print statement only.")

        if content and val in content: print(f"{Prisma.GRN}[PASS] Variable returned.{Prisma.RST}")
        else: print(f"{Prisma.RED}[FAIL] Output: {content}{Prisma.RST}")

    def run(self):
        self.load_driver()
        BoneConfig.VERBOSE_LOGGING = False
        self.test_connectivity()
        self.test_instruction_following()
        self.test_context_retention()
        print(f"\n{Prisma.CYN}=== BARE METAL EXERCISE COMPLETE ==={Prisma.RST}")

if __name__ == "__main__":
    test = LiveFireExercise()
    test.run()