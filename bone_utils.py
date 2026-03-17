""" bone_utils.py """

import math
import random
import os
import logging
import contextlib
import warnings
import re
import threading
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, Tuple
import importlib

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
    def __init__(self, library_graph: LibraryGraph, config: dict[str, Any] | None = None):
        if config is None:
            config = {}
        self.library = library_graph
        self.randomness_dial: float = float(config.get("randomnessDial", 0.0))
        self.traversal_history: list[dict[str, Any]] = []
        self.serendipity_cache: dict[str, Any] = {}
        self.modes = {"PURIST":   {"range": (0.0, 0.2), "desc": "Shortest path, structural fidelity"},
            "TOURIST":  {"range": (0.2, 0.4), "desc": "Occasional scenic detours"},
            "EXPLORER": {"range": (0.4, 0.6), "desc": "Deliberate wrong turns, adjacent possible"},
            "FLANEUR":  {"range": (0.6, 0.8), "desc": "Let the library browse you"},
            "CHAOS":    {"range": (0.8, 1.0), "desc": "Maximum entropy, minimum predictability"}}

    def retrieve(self, query_coordinates: Coordinates, query_vector: list[float]) -> dict[str, Any]:
        r_val = self.randomness_dial
        mode = self._get_mode(r_val)
        structural_target = self._find_structural_match(query_coordinates)
        retrieval_path = self._generate_traversal_path(structural_target, r_val)
        results = self._traverse_and_collect(retrieval_path, query_vector, r_val)
        tagged_results = self._calculate_serendipity(results, query_coordinates)

        return {"mode": mode, "randomness_used": r_val, "path_length": len(retrieval_path), "results": tagged_results,
                "traversal_history": self.traversal_history[-5:],
                "note": self._generate_path_note(mode, tagged_results)}

    def _find_structural_match(self, coords: Coordinates) -> LibraryNode:
        candidates = [
            node for node in self.library.nodes
            if abs(node.coords.S - coords.S) < 0.15
            and abs(node.coords.D - coords.D) < 0.2
            and abs(node.coords.C - coords.C) < 0.25
        ]
        return candidates[0] if candidates else self.library.root

    def _generate_traversal_path(self, start_node: LibraryNode, r_val: float) -> list[LibraryNode]:
        import time
        path = [start_node]
        visited = {start_node.id}
        steps = math.floor(1 + r_val * 5)
        for _ in range(steps):
            current_node = path[-1]
            neighbors = self._get_neighbors(current_node)
            available = [n for n in neighbors if n.id not in visited]
            if not available:
                break
            if random.random() < r_val:
                if r_val > 0.7 and random.random() < 0.3:
                    random_branch = self._get_random_branch(current_node)
                    next_node = random_branch if (random_branch and random_branch.id not in visited) else random.choice(
                        available)
                else:
                    next_node = random.choice(available)
            else:
                next_node = self._most_structural_neighbor(available, start_node)
            if next_node:
                path.append(next_node)
                visited.add(next_node.id)
        self.traversal_history.append({"timestamp": time.time(), "start_node": start_node.id, "path": [n.id for n in path],
             "R": self.randomness_dial})
        return path

    def _get_neighbors(self, node: LibraryNode) -> list[LibraryNode]:
        neighbors = []
        if node.parent_id:
            parent = next((n for n in self.library.nodes if n.id == node.parent_id), None)
            if parent:
                neighbors.append(parent)
        children = [n for n in self.library.nodes if n.parent_id == node.id]
        neighbors.extend(children)
        if node.parent_id:
            siblings = [n for n in self.library.nodes if n.parent_id == node.parent_id and n.id != node.id]
            neighbors.extend(siblings)
        if node.refs:
            refs = [n for n in self.library.nodes if n.id in node.refs]
            neighbors.extend(refs)
        return neighbors

    def _most_structural_neighbor(self, neighbors: list[LibraryNode], target_node: LibraryNode) -> LibraryNode:
        return max(neighbors, key=lambda current: self._structural_similarity(current, target_node))

    def _structural_similarity(self, a: LibraryNode, b: LibraryNode) -> float:
        dist = math.sqrt((a.coords.S - b.coords.S) ** 2 +
            (a.coords.D - b.coords.D) ** 2 +
            (a.coords.C - b.coords.C) ** 2)
        return 1.0 / (1.0 + dist)

    def _get_random_branch(self, current_node: LibraryNode) -> Optional[LibraryNode]:
        lineage = self._get_lineage(current_node)
        candidates = [n for n in self.library.nodes if n.id not in lineage and n.id != current_node.id]
        if not candidates:
            return None
        return random.choice(candidates)

    def _get_lineage(self, node: LibraryNode) -> set[str]:
        lineage = {node.id}
        current = node
        while current.parent_id:
            lineage.add(current.parent_id)
            current = next((n for n in self.library.nodes if n.id == current.parent_id), None)
            if not current:
                break
        return lineage

    def _traverse_and_collect(self, path: list[LibraryNode], query_vector: list[float], r_val: float) -> list[RetrievalResult]:
        collected = []
        path_len = len(path)
        for i, node in enumerate(path):
            relevance = self._vector_similarity(node.vector, query_vector)
            position_weight = 1.0 - (i / path_len) * 0.5
            serendipity_bonus = r_val * (i / path_len) * 0.7
            score = (relevance * position_weight) + serendipity_bonus
            collected.append(RetrievalResult(node_id=node.id, title=node.title, content=node.content,
                                             coords=node.coords, path_position=i, relevance_score=relevance,
                                             serendipity_bonus=serendipity_bonus, final_score=score,
                                             snippet=node.content[:150] + "..."))
        return sorted(collected, key=lambda x: x.final_score, reverse=True)

    def _vector_similarity(self, v1: list[float], v2: list[float]) -> float:
        if not v1 or not v2:
            return 0.5
        dot = sum(val1 * val2 for val1, val2 in zip(v1, v2))
        mag1 = math.sqrt(sum(val ** 2 for val in v1))
        mag2 = math.sqrt(sum(val ** 2 for val in v2))
        if mag1 * mag2 == 0:
            return 0.5
        return ((dot / (mag1 * mag2)) + 1.0) / 2.0

    def _calculate_serendipity(self, results: list[RetrievalResult], query_coords: Coordinates) -> list[RetrievalResult]:
        for r in results:
            expected_delta = math.sqrt((r.coords.S - query_coords.S) ** 2 +
                (r.coords.D - query_coords.D) ** 2 +
                (r.coords.C - query_coords.C) ** 2)
            r.serendipity = r.relevance_score * expected_delta
            r.is_surprising = r.serendipity > 0.5
        return results

    def _get_mode(self, r_val: float) -> dict[str, str]:
        for name, spec in self.modes.items():
            if spec["range"][0] <= r_val <= spec["range"][1]:
                return {"name": name, "description": spec["desc"]}
        return {"name": "TOURIST", "description": "Default mode"}

    def _generate_path_note(self, mode: dict[str, str], results: list[RetrievalResult]) -> str:
        surprising_count = sum(1 for r in results if r.is_surprising)

        notes = {"PURIST": "Staying on the beaten path. Nothing wasted, nothing unexpected.",
                 "TOURIST": "Took a small detour. Found a nice view.",
                 "EXPLORER": "Went where the path was thin. Came back with something odd.",
                 "FLANEUR": "The library started talking. I just listened.",
                 "CHAOS": "At this point, the books are reading you."}
        base_note = notes.get(mode["name"], "Wandering...")
        if surprising_count > 0:
            noun = "gem" if surprising_count == 1 else "gems"
            surprise_note = f" Found {surprising_count} unexpected {noun}."
        else:
            surprise_note = " Nothing surprising—but sometimes that's the point."
        return base_note + surprise_note

    def set_randomness(self, value: float) -> dict[str, Any]:
        self.randomness_dial = max(0.0, min(1.0, float(value)))
        mode = self._get_mode(self.randomness_dial)
        return {"new_value": self.randomness_dial, "mode": mode["name"],
                "message": f"Random retrieval dial set to {self.randomness_dial:.2f}"}

    def get_state(self) -> dict[str, Any]:
        return {"randomness_dial": self.randomness_dial, "mode": self._get_mode(self.randomness_dial),
                "traversal_history": self.traversal_history[-3:], "serendipity_cache_size": len(self.serendipity_cache)}

class TheSubstrate:
    def __init__(self, events_ref):
        self.events = events_ref
        self.pending_writes: List[Dict[str, str]] = []

    def queue_write(self, path: str, content: str):
        self.pending_writes.append({"path": path, "content": content})

    def execute_writes(self, stamina_pool: float) -> Tuple[List[str], float]:
        logs = []
        cost = 0.0
        if not self.pending_writes:
            return logs, cost
        os.makedirs("output", exist_ok=True)
        for write in self.pending_writes:
            safe_name = os.path.basename(write["path"])
            safe_path = os.path.join("output", safe_name)
            content = write["content"]
            size = len(content)
            write_cost = size * 0.02
            if stamina_pool - cost < write_cost:
                logs.append(f"{Prisma.RED}SUBSTRATE FAULT: Insufficient stamina to forge {safe_name}.{Prisma.RST}")
                continue
            try:
                with open(safe_path, "w", encoding="utf-8") as f:
                    f.write(content)
                cost += write_cost
                logs.append(f"{Prisma.GRN}SUBSTRATE: Physically forged {safe_path} ({size} bytes).{Prisma.RST}")
                if hasattr(self.events, "publish"):
                    self.events.publish("SUBSTRATE_FORGED", {"cost": write_cost, "file": safe_name})
                if "podcast_script" in safe_name:
                    self._trigger_tts(safe_path)
            except Exception as e:
                logs.append(f"{Prisma.RED}SUBSTRATE FAULT: Write failed - {e}{Prisma.RST}")
        self.pending_writes.clear()
        return logs, cost

    def _trigger_tts(self, safe_path: str):
        def _async_tts_task(path, events):
            try:
                cords = TheVocalCords(events)
                cords.synthesize_podcast(path)
                if events:
                    events.log(f"{Prisma.VIOLET}SUBSTRATE: TTS synthesis complete for {path}.{Prisma.RST}")
            except Exception as e:
                if events:
                    events.log(f"{Prisma.RED}SUBSTRATE FAULT: TTS failed - {e}{Prisma.RST}", "CRIT")
        thread = threading.Thread(target=_async_tts_task, args=(safe_path, self.events))
        thread.daemon = True
        thread.start()

try:
    import tkinter
    TCL_AVAILABLE = True
except ImportError:
    tkinter = None
    TCL_AVAILABLE = False

class TheTclWeaver:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TheTclWeaver()
        return cls._instance

    def __init__(self):
        self.interp = None
        if TCL_AVAILABLE:
            try:
                self.interp = tkinter.Tcl()
                self._load_tcl_spells()
            except Exception as e:
                from bone_types import Prisma
                print(f"{Prisma.OCHRE}[TCL WEAVER OFFLINE]: {e}. Text deformation disabled.{Prisma.RST}")
                self.interp = None

    def _load_tcl_spells(self):
        tcl_script = """
        proc apply_entropy {text chi voltage} {
            set words [split $text " "]
            set out_words {}
            foreach word $words {
                set len [string length $word]
                # Typoglycemia (Scrambling inner letters under extreme chaos)
                if {$chi > 0.85 && $len > 4 && rand() < ($chi / 3.0)} {
                    set first [string index $word 0]
                    set last [string index $word [expr {$len - 1}]]
                    set mid [string range $word 1 [expr {$len - 2}]]
                    set mid_rev [string reverse $mid]
                    lappend out_words "${first}${mid_rev}${last}"
                # Cellular division (splitting words)
                } elseif {$chi > 0.6 && $len > 4 && rand() < ($chi / 2.0)} {
                    set mid [expr {$len / 2}]
                    set part1 [string range $word 0 [expr {$mid - 1}]]
                    set part2 [string range $word $mid end]
                    lappend out_words "${part1}·${part2}"
                # Voltage Arc (random capitalization)
                } elseif {$voltage > 80.0 && rand() < 0.1} {
                    lappend out_words [string toupper $word]
                } else {
                    lappend out_words $word
                }
            }
            return [join $out_words " "]
        }

        proc apply_void {text psi} {
            set words [split $text " "]
            set out_words {}
            foreach word $words {
                # If proximity to the Void is high, memories get redacted
                if {$psi > 0.5 && [string length $word] > 3 && rand() < ($psi / 2.5)} {
                    lappend out_words "████"
                } else {
                    lappend out_words $word
                }
            }
            return [join $out_words " "]
        }

        proc semantic_echo {text} {
            set words [split $text " "]
            if {[llength $words] == 0} { return $text }
            set last_word [lindex $words end]
            set clean_last [regsub -all {[^a-zA-Z0-9]} $last_word ""]
            if {[string length $clean_last] > 0} {
                return "$text... [string tolower $clean_last]..."
            }
            return "$text..."
        }

        proc strip_fluff {text} {
            set words [split $text " "]
            set out_words {}
            foreach word $words {
                # Protect short words like 'fish', 'relic', and 'apply' from being stripped
                if {[string length $word] > 5 && [regexp {(?i).*(ous|ful|ic|ish|ly)[.,!?]*$} $word]} {
                    # Fluff detected, do not append
                } else {
                    lappend out_words $word
                }
            }
            return [join $out_words " "]
        }
        """
        self.interp.eval(tcl_script)

    def deform_reality(self, text: str, chi: float, voltage: float) -> str:
        if not self.interp: return text
        try:
            return self.interp.call('apply_entropy', text, chi, voltage)
        except Exception as e:
            from bone_types import Prisma
            print(f"{Prisma.RED}[TCL ENGINE FRACTURE]: {e}{Prisma.RST}")
            return text

    def haunt_string(self, text: str) -> str:
        if not self.interp: return text
        try:
            return self.interp.call('semantic_echo', text)
        except Exception:
            return text

    def quantum_comb(self, text: str) -> str:
        if not self.interp: return text
        try:
            return self.interp.call('strip_fluff', text)
        except Exception as e:
            from bone_types import Prisma
            print(f"{Prisma.RED}[TCL CRASH]: {e}{Prisma.RST}")
            return text

    def consume_by_void(self, text: str, psi: float) -> str:
        if not self.interp: return text
        try:
            return self.interp.call('apply_void', text, psi)
        except Exception as e:
            from bone_types import Prisma
            print(f"{Prisma.VIOLET}[TCL VOID FRACTURE]: {e}{Prisma.RST}")
            return text

AUDIO_AVAILABLE = all(
    importlib.util.find_spec(pkg) is not None
    for pkg in ["kokoro", "soundfile", "numpy"])
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TQDM_DISABLE"] = "True"
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("torch").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

class TheVocalCords:
    def __init__(self, events_ref=None):
        self.events = events_ref
        self.voice_map = {"BENEDICT": "am_adam", "JESTER": "am_puck", "STAGE MANAGER": "af_sky", "GORDON": "am_michael",
                          "MOIRA": "af_heart", "MERCY": "af_heart", "ROBERTA": "af_nicole", "COLIN": "am_eric",
                          "CASSANDRA": "af_aoife", "REVENANT": "am_fenrir", "GIDEON": "am_onyx", "APRIL": "af_kore",
                          "DEFAULT": "af_bella"}
        self.pipeline = None
        self.sf = None
        self._synthesis_lock = threading.Lock()

    @staticmethod
    def strip_ansi(text: str) -> str:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def parse_script(self, script_text: str) -> List[Dict[str, str]]:
        clean_text = self.strip_ansi(script_text)
        pattern = re.compile(r'^\[([^\]]+)\]:?\s*(.*?)(?=\n\[|\Z)', re.MULTILINE | re.DOTALL)
        segments = []
        for match in pattern.finditer(clean_text):
            speaker = match.group(1).split("(")[0].strip().upper()
            dialogue = match.group(2).strip()
            if dialogue:
                segments.append({"speaker": speaker, "text": dialogue})
        return segments

    def synthesize_podcast(self, file_path: str):
        if not os.path.exists(file_path):
            return
        if not AUDIO_AVAILABLE:
            if self.events:
                self.events.log(f"{Prisma.OCHRE}[AUDIO OFFLINE]: TTS dependencies (kokoro, soundfile, numpy) not found. Skipping podcast synthesis.{Prisma.RST}", "SYS")
            return
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
                with open(os.devnull, 'w') as fnull:
                    with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                        if not self.pipeline:
                            from kokoro import KPipeline
                            import soundfile as sf
                            self.pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
                            self.sf = sf
                        import numpy as np
                        silence_pad = np.zeros(int(24000 * 0.6))
                        for seg in segments:
                            speaker = seg["speaker"]
                            text = seg["text"]
                            voice = self.voice_map.get(speaker, self.voice_map["DEFAULT"])
                            generator = self.pipeline(text, voice=voice, speed=1.0)
                            for _, _, audio in generator:
                                if audio is not None and len(audio) > 0:
                                    combined_audio.append(np.array(audio).flatten())
                            combined_audio.append(silence_pad)
                        if combined_audio:
                            final_array = np.concatenate(combined_audio)
                            self.sf.write(master_file, final_array, 24000)
            except Exception as e:
                error_to_report = str(e)
            handoff_msg = f"\n{Prisma.GRY}[SYSTEM: Audio thread closed. Microphone is yours.]\nTRAVELER > {Prisma.RST}"
            if error_to_report:
                if self.events:
                    self.events.log(f"{Prisma.RED}🎙️ AUDIO FAULT: {error_to_report}{Prisma.RST}{handoff_msg}", "SYS")
            elif combined_audio:
                if self.events:
                    self.events.log(f"{Prisma.MAG}🎙️ MASTER PODCAST FORGED: {os.path.basename(master_file)}{Prisma.RST}{handoff_msg}", "SYS")

try:
    import dspy
    DSPY_AVAILABLE = True

except ImportError:
    dspy = None
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
    def __init__(self, config_ref=None):
        self.enabled = DSPY_AVAILABLE
        self.cfg = config_ref
        if self.enabled:
            try:
                if self.cfg and hasattr(self.cfg, "PROVIDER"):
                    provider = getattr(self.cfg, "PROVIDER", "ollama")
                    model_name = getattr(self.cfg, "MODEL", "vsl-hermes")
                    base_url = getattr(self.cfg, "BASE_URL", "http://127.0.0.1:11434/v1/chat/completions")
                elif isinstance(self.cfg, dict):
                    provider = self.cfg.get("provider", "ollama")
                    model_name = self.cfg.get("model", "vsl-hermes")
                    base_url = self.cfg.get("base_url", "http://127.0.0.1:11434/v1/chat/completions")
                else:
                    from bone_presets import BoneConfig
                    provider = getattr(BoneConfig, "PROVIDER", "ollama")
                    model_name = getattr(BoneConfig, "MODEL", "vsl-hermes")
                    base_url = getattr(BoneConfig, "BASE_URL", "http://127.0.0.1:11434/v1/chat/completions")
                if base_url:
                    base_url = base_url.replace("/chat/completions", "")
                else:
                    base_url = "http://127.0.0.1:11434/v1"
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