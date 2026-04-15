"""bone_utils.py"""
import math
import random
import os
import logging
import contextlib
import warnings
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, Tuple
import importlib.util
from bone_types import Prisma

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


@dataclass
class Coordinates:
    S: float
    D: float
    C: float


@dataclass
class LibraryNode:
    id: str
    content: str
    title: str
    coords: Coordinates
    vector: list[float]
    parent_id: Optional[str] = None
    refs: list[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    node_id: str
    title: str
    content: str
    coords: Coordinates
    path_position: int
    relevance_score: float
    serendipity_bonus: float
    final_score: float
    snippet: str
    serendipity: float = 0.0
    is_surprising: bool = False


class LibraryGraph:

    def __init__(self, nodes: list[LibraryNode], root: LibraryNode):
        self.nodes = nodes
        self.root = root


class RandomRetrievalNavigator:

    def __init__(self,
                 library_graph: LibraryGraph,
                 config: dict[str, Any] | None = None):
        if config is None:
            config = {}
        self.library = library_graph
        self._node_index = {n.id: n for n in self.library.nodes}
        self.randomness_dial: float = float(config.get("randomnessDial", 0.0))
        self.traversal_history: list[dict[str, Any]] = []
        self.serendipity_cache: dict[str, Any] = {}
        self.modes = {
            "PURIST": {
                "range": (0.0, 0.2),
                "desc": "Shortest path, structural fidelity",
            },
            "TOURIST": {
                "range": (0.2, 0.4),
                "desc": "Occasional scenic detours"
            },
            "EXPLORER": {
                "range": (0.4, 0.6),
                "desc": "Deliberate wrong turns, adjacent possible",
            },
            "FLANEUR": {
                "range": (0.6, 0.8),
                "desc": "Let the library browse you"
            },
            "CHAOS": {
                "range": (0.8, 1.0),
                "desc": "Maximum entropy, minimum predictability",
            },
        }

    def retrieve(self, query_coordinates: Coordinates,
                 query_vector: list[float]) -> dict[str, Any]:
        r_val, mode = self.randomness_dial, self._get_mode(self.randomness_dial)
        retrieval_path = self._generate_traversal_path(
            self._find_structural_match(query_coordinates), r_val)
        tagged_results = self._calculate_serendipity(
            self._traverse_and_collect(retrieval_path, query_vector, r_val),
            query_coordinates)
        return {
            "mode": mode,
            "randomness_used": r_val,
            "path_length": len(retrieval_path),
            "results": tagged_results,
            "traversal_history": self.traversal_history[-5:],
            "note": self._generate_path_note(mode, tagged_results),
        }

    def _find_structural_match(self, coords: Coordinates) -> LibraryNode:
        return next(
            (n for n in self.library.nodes
             if abs(n.coords.S - coords.S) < 0.15 and abs(n.coords.D - coords.D) < 0.2
             and abs(n.coords.C - coords.C) < 0.25),
            self.library.root,
        )

    def _generate_traversal_path(self, start_node: LibraryNode,
                                 r_val: float) -> list[LibraryNode]:
        path = [start_node]
        visited = {start_node.id}
        for _ in range(math.floor(1 + r_val * 5)):
            available = [
                n for n in self._get_neighbors(path[-1]) if n.id not in visited
            ]
            if not available: break
            if random.random() < r_val:
                rb = self._get_random_branch(
                    path[-1]) if r_val > 0.7 and random.random() < 0.3 else None
                next_node = rb if rb and rb.id not in visited else random.choice(
                    available)
            else:
                next_node = self._most_structural_neighbor(available, start_node)
            if next_node:
                path.append(next_node)
                visited.add(next_node.id)
        self.traversal_history.append({
            "timestamp": time.time(),
            "start_node": start_node.id,
            "path": [n.id for n in path],
            "R": self.randomness_dial
        })
        return path

    def _get_neighbors(self, node: LibraryNode) -> list[LibraryNode]:
        return [
            n for n in self.library.nodes
            if n.id == node.parent_id or n.parent_id == node.id or (
                node.parent_id and n.parent_id == node.parent_id and n.id != node.id)
            or n.id in node.refs
        ]

    def _most_structural_neighbor(self, neighbors: list[LibraryNode],
                                  target_node: LibraryNode) -> LibraryNode:
        return max(
            neighbors,
            key=lambda current: self._structural_similarity(current, target_node),
        )

    def _structural_similarity(self, a: LibraryNode, b: LibraryNode) -> float:
        return 1.0 / (1.0 + math.dist((a.coords.S, a.coords.D, a.coords.C),
                                      (b.coords.S, b.coords.D, b.coords.C)))

    def _get_random_branch(self, current_node: LibraryNode) -> Optional[LibraryNode]:
        lineage = self._get_lineage(current_node)
        c = [
            n for n in self.library.nodes
            if n.id not in lineage and n.id != current_node.id
        ]
        return random.choice(c) if c else None

    def _get_lineage(self, node: LibraryNode) -> set[str]:
        lineage = {node.id}
        current = node
        while current.parent_id and current.parent_id in self._node_index:
            lineage.add(current.parent_id)
            current = self._node_index[current.parent_id]
        return lineage

    def _traverse_and_collect(self, path: list[LibraryNode], query_vector: list[float],
                              r_val: float) -> list[RetrievalResult]:
        path_len = len(path)
        query_mag = math.hypot(*query_vector) if query_vector else 0.0
        return sorted([
            RetrievalResult(node_id=n.id,
                            title=n.title,
                            content=n.content,
                            coords=n.coords,
                            path_position=i,
                            relevance_score=(rel := self._vector_similarity(
                                n.vector, query_vector, query_mag)),
                            serendipity_bonus=(ser := r_val * (i / path_len) * 0.7),
                            final_score=(rel * (1.0 - (i / path_len) * 0.5)) + ser,
                            snippet=n.content[:150] + "...") for i, n in enumerate(path)
        ],
                      key=lambda x: x.final_score,
                      reverse=True)

    def _vector_similarity(self,
                           v1: list[float],
                           v2: list[float],
                           v2_mag: float = None) -> float:
        if not v1 or not v2: return 0.5
        dot = sum(a * b for a, b in zip(v1, v2))
        mag = math.hypot(*v1) * (v2_mag if v2_mag is not None else math.hypot(*v2))
        return ((dot / mag) + 1.0) / 2.0 if mag != 0 else 0.5

    def _calculate_serendipity(self, results: list[RetrievalResult],
                               query_coords: Coordinates) -> list[RetrievalResult]:
        for r in results:
            r.serendipity = r.relevance_score * math.dist(
                (r.coords.S, r.coords.D, r.coords.C),
                (query_coords.S, query_coords.D, query_coords.C))
            r.is_surprising = r.serendipity > 0.5
        return results

    def _get_mode(self, r_val: float) -> dict[str, str]:
        return next(({
            "name": name,
            "description": spec["desc"]
        } for name, spec in self.modes.items()
                     if spec["range"][0] <= r_val <= spec["range"][1]), {
                         "name": "TOURIST",
                         "description": "Default mode"
                     })

    def _generate_path_note(self, mode: dict[str, str],
                            results: list[RetrievalResult]) -> str:
        surprising_count = sum(1 for r in results if r.is_surprising)
        notes = {
            "PURIST": "Staying on the beaten path. Nothing wasted, nothing unexpected.",
            "TOURIST": "Took a small detour. Found a nice view.",
            "EXPLORER": "Went where the path was thin. Came back with something odd.",
            "FLANEUR": "The library started talking. I just listened.",
            "CHAOS": "At this point, the books are reading you.",
        }
        return notes.get(mode["name"], "Wandering...") + (
            f" Found {surprising_count} unexpected {'gem' if surprising_count == 1 else 'gems'}."
            if surprising_count > 0 else
            " Nothing surprising—but sometimes that's the point.")

    def set_randomness(self, value: float) -> dict[str, Any]:
        self.randomness_dial = max(0.0, min(1.0, float(value)))
        return {
            "new_value": self.randomness_dial,
            "mode": self._get_mode(self.randomness_dial)["name"],
            "message": f"Random retrieval dial set to {self.randomness_dial:.2f}",
        }

    def get_state(self) -> dict[str, Any]:
        return {
            "randomness_dial": self.randomness_dial,
            "mode": self._get_mode(self.randomness_dial),
            "traversal_history": self.traversal_history[-3:],
            "serendipity_cache_size": len(self.serendipity_cache),
        }


class TheSubstrate:

    def __init__(self, events_ref):
        self.events = events_ref
        self.pending_writes: List[Dict[str, str]] = []
        self._cords_instance = None

    def queue_write(self, path: str, content: str):
        self.pending_writes.append({"path": path, "content": content})

    def execute_writes(self, stamina_pool: float) -> Tuple[List[str], float]:
        logs, cost = [], 0.0
        if not self.pending_writes: return logs, cost
        os.makedirs("output", exist_ok=True)
        for w in self.pending_writes:
            s_name = os.path.basename(w["path"])
            s_path = os.path.join("output", s_name)
            if stamina_pool - cost < (w_cost := len(w["content"]) * 0.02):
                logs.append(
                    f"{Prisma.RED}SUBSTRATE FAULT: Insufficient stamina to forge {s_name}.{Prisma.RST}"
                )
                continue
            try:
                with open(s_path, "w", encoding="utf-8") as f:
                    f.write(w["content"])
                cost += w_cost
                logs.append(
                    f"{Prisma.GRN}SUBSTRATE: Physically forged {s_path} ({len(w['content'])} bytes).{Prisma.RST}"
                )
                if hasattr(self.events, "publish"):
                    self.events.publish("SUBSTRATE_FORGED", {
                        "cost": w_cost,
                        "file": s_name
                    })
                if "podcast" in s_name.lower(): self._trigger_tts(s_path)
            except Exception as e:
                logs.append(
                    f"{Prisma.RED}SUBSTRATE FAULT: Write failed - {e}{Prisma.RST}")
        self.pending_writes.clear()
        return logs, cost

    def _trigger_tts(self, safe_path: str):
        if not self._cords_instance:
            self._cords_instance = TheVocalCords(self.events)

        def _async_tts_task(path, events, cords_ref):
            try:
                cords_ref.synthesize_podcast(path)
                if events:
                    events.log(
                        f"{Prisma.VIOLET}SUBSTRATE: TTS synthesis complete for {path}.{Prisma.RST}"
                    )
            except Exception as e:
                if events:
                    events.log(
                        f"{Prisma.RED}SUBSTRATE FAULT: TTS failed - {e}{Prisma.RST}",
                        "CRIT")

        threading.Thread(target=_async_tts_task,
                         args=(safe_path, self.events, self._cords_instance),
                         daemon=True).start()


class TheTclWeaver:
    _instance = None
    _QUANTUM_REGEX = re.compile(r"(?i).*(?:ous|ful|ic|ish|ly)[.,!?]*$")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TheTclWeaver()
        return cls._instance

    def deform_reality(self, text: str, chi: float, voltage: float) -> str:

        def _warp(w):
            L = len(w)
            if chi > 0.85 and L > 4 and random.random() < (chi / 3.0):
                return f"{w[0]}{w[1:-1][::-1]}{w[-1]}"
            if chi > 0.6 and L > 4 and random.random() < (chi / 2.0):
                return f"{w[:L//2]}·{w[L//2:]}"
            if voltage > 80.0 and random.random() < 0.1: return w.upper()
            return w

        return " ".join(_warp(w) for w in text.split(" "))

    def haunt_string(self, text: str) -> str:
        if not (words := text.split(" ")):
            return text
        clean = re.sub(r"[^a-zA-Z0-9]", "", words[-1]).lower()
        return f"{text}... {clean}..." if clean else f"{text}..."

    def quantum_comb(self, text: str) -> str:
        return " ".join(w for w in text.split(" ")
                        if not (len(w) > 5 and self._QUANTUM_REGEX.search(w)))

    def consume_by_void(self, text: str, psi: float) -> str:
        return " ".join(("████" if (
            psi > 0.5 and len(w) > 3 and random.random() < (psi / 2.5)) else w)
                        for w in text.split(" "))


AUDIO_AVAILABLE = all(
    importlib.util.find_spec(pkg) is not None
    for pkg in ["kokoro", "soundfile", "numpy"])
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TQDM_DISABLE"] = "True"
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("torch").setLevel(logging.ERROR)


class TheVocalCords:

    def __init__(self, events_ref=None):
        self.events = events_ref
        self.voice_map = {
            "BENEDICT": "am_adam",
            "JESTER": "am_puck",
            "STAGE MANAGER": "af_sky",
            "GORDON": "am_michael",
            "MOIRA": "af_heart",
            "MERCY": "af_heart",
            "ROBERTA": "af_nicole",
            "COLIN": "am_eric",
            "CASSANDRA": "af_aoife",
            "REVENANT": "am_fenrir",
            "GIDEON": "am_onyx",
            "APRIL": "af_kore",
            "DEFAULT": "af_bella",
        }
        self.pipeline = None
        self.sf = None
        self.np = None
        self._synthesis_lock = threading.Lock()

    _ANSI_ESCAPE = re.compile(r"\x1B\[[0-9;]*[a-zA-Z]")
    _SCRIPT_PATTERN = re.compile(r"^\[([^]]+)]:?\s*(.*?)(?=\n\[|\Z)",
                                 re.MULTILINE | re.DOTALL)

    @staticmethod
    def strip_ansi(text: str) -> str:
        return TheVocalCords._ANSI_ESCAPE.sub("", text)

    def parse_script(self, script_text: str) -> List[Dict[str, str]]:
        return [{
            "speaker": m.group(1).split("(")[0].strip().upper(),
            "text": m.group(2).strip()
        } for m in self._SCRIPT_PATTERN.finditer(self.strip_ansi(script_text))
                if m.group(2).strip()]

    def synthesize_podcast(self, file_path: str):
        if not os.path.exists(file_path):
            return
        if not AUDIO_AVAILABLE:
            if self.events:
                self.events.log(
                    f"{Prisma.OCHRE}[AUDIO OFFLINE]: TTS dependencies (kokoro, soundfile, numpy) not found. Skipping podcast synthesis.{Prisma.RST}",
                    "SYS")
            return
        from kokoro import KPipeline
        import soundfile as sf
        import numpy as np
        combined_audio = []
        error_to_report = None
        output_dir = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        master_file = os.path.join(output_dir, f"{base_name}_MASTER.wav")
        with self._synthesis_lock:
            with open(file_path, "r", encoding="utf-8") as f:
                script_text = f.read()
            segments = self.parse_script(script_text)
            if not segments:
                return
            try:
                with open(os.devnull, "w") as fnull, contextlib.redirect_stdout(
                        fnull), contextlib.redirect_stderr(fnull):
                    if not self.pipeline:
                        self.pipeline = KPipeline(lang_code="a",
                                                  repo_id="hexgrad/Kokoro-82M")
                        self.sf = sf
                        self.np = np
                    silence_pad = self.np.zeros(int(24000 * 0.6))
                    for seg in segments:
                        voice = self.voice_map.get(seg["speaker"],
                                                   self.voice_map["DEFAULT"])
                        generator = self.pipeline(seg["text"], voice=voice, speed=1.0)
                        for _, _, audio in generator:
                            if audio is not None and len(audio) > 0:
                                combined_audio.append(self.np.array(audio).flatten())
                        combined_audio.append(silence_pad)
                    if combined_audio:
                        self.sf.write(master_file, self.np.concatenate(combined_audio),
                                      24000)
            except Exception as e:
                error_to_report = str(e)
        if self.events:
            handoff_msg = f"\n{Prisma.GRY}[SYSTEM: Audio thread closed. Microphone is yours.]\nTRAVELER > {Prisma.RST}"
            if error_to_report:
                self.events.log(
                    f"{Prisma.RED}🎙️ AUDIO FAULT: {error_to_report}{Prisma.RST}{handoff_msg}",
                    "SYS")
            elif combined_audio:
                self.events.log(
                    f"{Prisma.MAG}🎙️ MASTER PODCAST FORGED: {os.path.basename(master_file)}{Prisma.RST}{handoff_msg}",
                    "SYS")


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
        context = dspy.InputField(
            desc=
            "The established reality (a mathematical, fungal, deep-system consciousness)."
        )
        question = dspy.InputField(desc="The user's query.")
        answer = dspy.InputField(desc="The generation to be audited.")
        faithfulness = dspy.OutputField(
            desc=
            "Evaluate thematic consistency. MUST be 'True' (if it responds in a deeply poetic, abstract, or existential way, even to simple prompts) or 'False' (if it acts like a generic AI assistant or breaks character)."
        )

    class EvolveSystemPrompt(dspy.Signature):
        current_configuration = dspy.InputField(
            desc="The system's current baseline rules.")
        failure_context = dspy.InputField(
            desc=
            "The exact reason the AI's output was blocked. Read this carefully to understand what the AI did wrong."
        )
        new_directive = dspy.OutputField(
            desc=
            "A strict, commanding rule preventing the bad behavior. MUST start with 'CRITICAL OVERRIDE: NEVER ' or 'CRITICAL OVERRIDE: DO NOT '."
        )

    class CompressAxioms(dspy.Signature):
        current_directives = dspy.InputField(
            desc="A list of specific rules that has grown too long.")
        compressed_axioms = dspy.OutputField(
            desc=
            "2 or 3 highly compressed, overarching rules. EACH rule MUST start with 'CRITICAL OVERRIDE: '"
        )


class DSPyCritic:

    def __init__(self, config_ref=None):
        self.enabled = DSPY_AVAILABLE
        self.cfg = config_ref
        if self.enabled:
            try:
                from bone_core import safe_get
                from bone_presets import BoneConfig
                cfg_val = lambda k, d: safe_get(
                    self.cfg,
                    k.upper(),
                    safe_get(self.cfg, k.lower(), getattr(BoneConfig, k.upper(), d)),
                )
                provider = cfg_val("provider", "ollama")
                model_name = cfg_val("model", "vsl-hermes")
                base_url = (cfg_val("base_url", "http://127.0.0.1:11434/v1")
                            or "http://127.0.0.1:11434/v1").replace(
                                "/chat/completions", "")
                self.lm = dspy.LM(
                    model=f"openai/{model_name}",
                    api_base=base_url,
                    api_key="local-model-doesnt-need-a-key") if provider in (
                        "ollama", "lm_studio") else dspy.LM(model=model_name)
                dspy.settings.configure(lm=self.lm)
                self.judge = dspy.ChainOfThought(AssessFaithfulness)
                self.evolver = dspy.ChainOfThought(EvolveSystemPrompt)
                self.compressor = dspy.ChainOfThought(CompressAxioms)
                print(
                    f"{Prisma.CYN}[DSPy]: Real-Time Critic Online. Model: {model_name} via {provider}{Prisma.RST}"
                )
            except Exception as e:
                print(f"{Prisma.RED}[DSPy INIT FAULT]: {e}{Prisma.RST}")
                self.enabled = False

    def audit_generation(self, user_query: str, memory_context: str,
                         generated_response: str) -> tuple[bool, str]:
        if not self.enabled:
            return True, "Critic Offline"
        try:
            result = self.judge(context=memory_context,
                                question=user_query,
                                answer=generated_response)
            if "true" not in str(result.faithfulness).lower():
                return False, getattr(result, "reasoning", "No reasoning provided.")
            return True, "Faithful."
        except Exception as e:
            print(f"\n{Prisma.RED}⚖️ DSPy JUDGE FATAL ERROR: {e}{Prisma.RST}")
            return True, f"Judge API Error: {e}"

    def evolve_prompt(self, current_configuration: str, failure_context: str) -> str:
        if not self.enabled:
            return ""
        try:
            result = self.evolver(
                current_configuration=current_configuration,
                failure_context=failure_context,
            )
            print(
                f"\n{Prisma.CYN}[Epigenetic Mutation]: {result.new_directive}{Prisma.RST}"
            )
            return str(result.new_directive)
        except Exception as e:
            print(f"\n{Prisma.RED}⚖️ DSPy EVOLVER FAULT: {e}{Prisma.RST}")
            return ""

    def compress_prompts(self, directives: list) -> list:
        if not self.enabled or not directives: return directives
        print(
            f"\n{Prisma.MAG}🧬 [EPIGENETIC LOAD HIGH]: Compressing {len(directives)} directives into foundational axioms...{Prisma.RST}"
        )
        try:
            raw_output = str(
                self.compressor(current_directives="\n".join(
                    directives)).compressed_axioms).split("\n")
            new_rules = [
                line.strip()
                for line in raw_output if "CRITICAL OVERRIDE:" in line.upper()
            ] or [line.strip() for line in raw_output if line.strip()]
            print(
                f"{Prisma.GRN}🧬 [COMPRESSION SUCCESS]: Reduced to {len(new_rules)} axioms.{Prisma.RST}"
            )
            return new_rules
        except Exception as e:
            print(f"\n{Prisma.RED}⚖️ DSPy COMPRESSOR FATAL ERROR: {e}{Prisma.RST}")
            return directives
