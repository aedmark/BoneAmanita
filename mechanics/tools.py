"""tools.py"""
import math, random, os, logging
import contextlib
import warnings
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, Tuple
import importlib.util
from constants import Prisma

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


@dataclass
class Coordinates:
    """
    The spatial geometry of a memory node.
    S = Scope (Breadth), D = Depth (Technicality), C = Connectivity (Social/Emotional weight).
    """
    S: float
    D: float
    C: float


@dataclass
class LibraryNode:
    """A discrete unit of memory inside the Mnemonic Layer's spatial graph."""
    id: str
    content: str
    title: str
    coords: Coordinates
    vector: list[float]
    parent_id: Optional[str] = None
    refs: list[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    """The payload returned from a memory traversal, including serendipity metrics."""
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
    """The complete topological map of the system's memory."""

    def __init__(self, nodes: list[LibraryNode], root: LibraryNode):
        self.nodes = nodes
        self.root = root


class RandomRetrievalNavigator:
    """
    Abandons standard flat RAG (top-K cosine similarity) for a physical, topological walk.
    Allows the system to 'wander' its memory, intentionally making wrong turns to discover
    lateral connections and trigger serendipitous insights.
    """
    _MODES = {
        "PURIST": {"range": (0.0, 0.2), "desc": "Shortest path, structural fidelity"},
        "TOURIST": {"range": (0.2, 0.4), "desc": "Occasional scenic detours"},
        "EXPLORER": {"range": (0.4, 0.6), "desc": "Deliberate wrong turns, adjacent possible"},
        "FLANEUR": {"range": (0.6, 0.8), "desc": "Let the library browse you"},
        "CHAOS": {"range": (0.8, 1.0), "desc": "Maximum entropy, minimum predictability"},
    }

    def __init__(self, library_graph: LibraryGraph, config: dict[str, Any] | None = None):
        self.library = library_graph
        self._node_index = {n.id: n for n in self.library.nodes}
        self.randomness_dial: float = float((config or {}).get("randomnessDial", 0.0))
        self.traversal_history: list[dict[str, Any]] = []

    def retrieve(self, query_coordinates: Coordinates,
                 query_vector: list[float]) -> dict[str, Any]:
        """Executes the topological walk to fetch memories based on current coordinates and randomness."""
        r_val, mode = self.randomness_dial, self._get_mode(self.randomness_dial)
        start_node = self._find_structural_match(query_coordinates)
        retrieval_path = self._generate_traversal_path(start_node, r_val)
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
        """Locates the nearest node in 3D (S, D, C) semantic space."""
        for n in self.library.nodes:
            s_match = abs(n.coords.S - coords.S) < 0.15
            d_match = abs(n.coords.D - coords.D) < 0.20
            c_match = abs(n.coords.C - coords.C) < 0.25
            if s_match and d_match and c_match:
                return n
        return self.library.root

    def _generate_traversal_path(self, start_node: LibraryNode, r_val: float) -> list[LibraryNode]:
        """Walks edge-to-edge through the memory graph, jumping tracks if randomness is high."""
        path = [start_node]
        visited = {start_node.id}
        for _ in range(math.floor(1 + r_val * 5)):
            available = [n for n in self._get_neighbors(path[-1]) if n.id not in visited]
            if not available: break
            if random.random() < r_val:
                rb = self._get_random_branch(path[-1]) if (r_val > 0.7 and random.random() < 0.3) else None
                next_node = rb if (rb and rb.id not in visited) else random.choice(available)
            else:
                next_node = self._most_structural_neighbor(available, start_node)
            if next_node:
                path.append(next_node)
                visited.add(next_node.id)
        self.traversal_history.append(
            {"timestamp": time.time(), "start_node": start_node.id, "path": [n.id for n in path],
             "R": self.randomness_dial})
        if len(self.traversal_history) > 20:
            self.traversal_history.pop(0)
        return path

    def _get_neighbors(self, node: LibraryNode) -> list[LibraryNode]:
        """Finds structurally linked nodes (parents, children, siblings, specific cross-references)."""
        refs_set = set(node.refs)
        neighbors = []
        for n in self.library.nodes:
            is_parent = (n.id == node.parent_id)
            is_child = (n.parent_id == node.id)
            is_sibling = (node.parent_id and n.parent_id == node.parent_id and n.id != node.id)
            is_referenced = (n.id in refs_set)
            if is_parent or is_child or is_sibling or is_referenced:
                neighbors.append(n)
        return neighbors

    def _most_structural_neighbor(self, neighbors: list[LibraryNode], target_node: LibraryNode) -> LibraryNode:
        """Determines the safest, most logical next step in the walk."""
        return max(neighbors, key=lambda current: self._structural_similarity(current, target_node), )

    def _structural_similarity(self, a: LibraryNode, b: LibraryNode) -> float:
        """Inverse distance calculation in 3D coordinate space."""
        return 1.0 / (1.0 + math.dist((a.coords.S, a.coords.D, a.coords.C), (b.coords.S, b.coords.D, b.coords.C)))

    def _get_random_branch(self, current_node: LibraryNode) -> Optional[LibraryNode]:
        """Fetches a node entirely outside the current thought lineage."""
        lineage = self._get_lineage(current_node)
        c = [n for n in self.library.nodes
             if n.id not in lineage and n.id != current_node.id]
        return random.choice(c) if c else None

    def _get_lineage(self, node: LibraryNode) -> set[str]:
        """Traces a memory back up to its absolute root."""
        lineage = {node.id}
        current = node
        while current.parent_id and current.parent_id in self._node_index:
            if current.parent_id in lineage:
                break
            lineage.add(current.parent_id)
            current = self._node_index[current.parent_id]
        return lineage

    def _traverse_and_collect(self, path: list[LibraryNode], query_vector: list[float], r_val: float) -> list[
        RetrievalResult]:
        """Scores the collected nodes based on vector relevance and the serendipity of the discovery."""
        path_len = len(path)
        query_mag = math.hypot(*query_vector) if query_vector else 0.0

        def _build_result(i: int, n: LibraryNode) -> RetrievalResult:
            rel = self._vector_similarity(n.vector, query_vector, query_mag)
            ser = r_val * (i / path_len) * 0.7
            final = (rel * (1.0 - (i / path_len) * 0.5)) + ser
            return RetrievalResult(
                node_id=n.id, title=n.title, content=n.content, coords=n.coords,
                path_position=i, relevance_score=rel, serendipity_bonus=ser,
                final_score=final, snippet=n.content[:150] + "..."
            )

        results = [_build_result(i, n) for i, n in enumerate(path)]
        return sorted(results, key=lambda x: x.final_score, reverse=True)

    def _vector_similarity(self, v1: list[float], v2: list[float], v2_mag: float = None) -> float:
        """Standard dot-product / magnitude math for comparing semantic vectors."""
        if not v1 or not v2: return 0.5
        dot = sum(a * b for a, b in zip(v1, v2))
        mag = math.hypot(*v1) * (v2_mag if v2_mag is not None else math.hypot(*v2))
        return ((dot / mag) + 1.0) / 2.0 if mag != 0 else 0.5

    def _calculate_serendipity(self, results: list[RetrievalResult], query_coords: Coordinates) -> list[
        RetrievalResult]:
        """Tags results as 'surprising' if they were found far from the origin but still scored highly."""
        for r in results:
            r.serendipity = r.relevance_score * math.dist(
                (r.coords.S, r.coords.D, r.coords.C),
                (query_coords.S, query_coords.D, query_coords.C))
            r.is_surprising = r.serendipity > 0.5
        return results

    def _get_mode(self, r_val: float) -> dict[str, str]:
        """Maps the numeric randomness dial to its narrative mode string."""
        return next(
            ({"name": name, "description": spec["desc"]}
             for name, spec in self._MODES.items()
             if spec["range"][0] <= r_val <= spec["range"][1]),
            {"name": "TOURIST", "description": "Default mode"}
        )

    def _generate_path_note(self, mode: dict[str, str], results: list[RetrievalResult]) -> str:
        """Generates the UI string explaining the feeling/outcome of the memory walk."""
        surprising_count = sum(1 for r in results if r.is_surprising)
        notes = {
            "PURIST": "Staying on the beaten path. Nothing wasted, nothing unexpected.",
            "TOURIST": "Took a small detour. Found a nice view.",
            "EXPLORER": "Went where the path was thin. Came back with something odd.",
            "FLANEUR": "The library started talking. I just listened.",
            "CHAOS": "At this point, the books are reading you.",
        }
        base_note = notes.get(mode["name"], "Wandering...")
        if surprising_count > 0:
            gem_str = "gem" if surprising_count == 1 else "gems"
            return f"{base_note} Found {surprising_count} unexpected {gem_str}."
        return f"{base_note} Nothing surprising—but sometimes that's the point."

    def set_randomness(self, value: float) -> dict[str, Any]:
        """Externally adjustable lever to mutate retrieval behavior on the fly."""
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
            "traversal_history": self.traversal_history[-3:]
        }


class TheSubstrate:
    """
    The literal file system interface for the AI.
    It doesn't just write files blindly; it charges the AI a biological ATP cost to
    interact with the disk. If the AI is exhausted, its write requests are queued or purged.
    """

    def __init__(self, events_ref):
        self.events = events_ref
        self.pending_writes: List[Dict[str, str]] = []
        self._cords_instance = None
        from core import LoreManifest
        self.config = LoreManifest.get_instance().get("SUBSTRATE_CONFIG") or {
            "ATP_COST_PER_CHAR": 0.02,
            "MAX_ATP_PER_FILE": 100.0,
            "MAX_RETRIES": 3
        }

    def queue_write(self, path: str, content: str):
        """Stages a file to be written, pending metabolic approval during the execution tick."""
        self.pending_writes.append({"path": path, "content": content, "retries": 0})

    def execute_writes(self, stamina_pool: float) -> Tuple[List[str], float]:
        """
        The physical forging process. Checks the system's stamina before allowing the disk I/O.
        """
        logs, cost = [], 0.0
        if not self.pending_writes: return logs, cost
        os.makedirs("output", exist_ok=True)
        retained_writes = []
        for w in self.pending_writes:
            base_dir = os.path.abspath("output")
            s_path = os.path.abspath(os.path.join(base_dir, w["path"].lstrip("/")))
            s_name = os.path.basename(s_path)
            if not s_path.startswith(base_dir):
                logs.append(
                    f"{Prisma.VIOLET}SUBSTRATE FATAL: Path traversal breach detected ({w['path']}). Purged.{Prisma.RST}")
                continue
            w_cost = len(w["content"]) * self.config.get("ATP_COST_PER_CHAR", 0.02)
            if w_cost > self.config.get("MAX_ATP_PER_FILE", 100.0):
                logs.append(
                    f"{Prisma.VIOLET}SUBSTRATE FATAL: {s_name} exceeds absolute biological carrying capacity (Cost: {w_cost:.1f} ATP). Purged from system.{Prisma.RST}")
                continue
            if stamina_pool - cost < w_cost:
                retries = w.get("retries", 0) + 1
                if retries > self.config.get("MAX_RETRIES", 3):
                    logs.append(
                        f"{Prisma.VIOLET}SUBSTRATE FATAL: {s_name} starved for ATP 3 times. Dropping file.{Prisma.RST}")
                else:
                    logs.append(
                        f"{Prisma.OCHRE}SUBSTRATE FAULT: Insufficient stamina to forge {s_name}. Retaining in queue ({retries}/3).{Prisma.RST}")
                    w["retries"] = retries
                    retained_writes.append(w)
                continue
            try:
                os.makedirs(os.path.dirname(s_path), exist_ok=True)
                with open(s_path, "w", encoding="utf-8") as f:
                    f.write(w["content"])
                cost += w_cost
                kb_size = len(w['content']) / 1024.0
                logs.append(f"{Prisma.GRN}SUBSTRATE: Physically forged {s_path} ({kb_size:.1f} KB).{Prisma.RST}")
                if self.events:
                    self.events.publish("SUBSTRATE_FORGED", {"cost": w_cost, "file": s_name})
            except Exception as e:
                retries = w.get("retries", 0) + 1
                if retries > self.config.get("MAX_RETRIES", 3):
                    logs.append(
                        f"{Prisma.VIOLET}SUBSTRATE FATAL: Write failed 3 times for {s_name} - {e}. Purging corrupted matter.{Prisma.RST}")
                else:
                    logs.append(f"{Prisma.RED}SUBSTRATE FAULT: Write failed - {e}. Retrying ({retries}/3).{Prisma.RST}")
                    w["retries"] = retries
                    retained_writes.append(w)
        self.pending_writes = retained_writes
        return logs, cost


class TheTclWeaver:
    """
    A cognitive damage simulator.
    When the system's stress, trauma, or chaos (chi) reaches dangerous levels,
    this tool physically deforms the output text to represent the system breaking down.
    """
    _instance = None
    _QUANTUM_REGEX = re.compile(r"(?i).*(?:ous|ful|ic|ish|ly)[.,!?]*$")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TheTclWeaver()
        return cls._instance

    def deform_reality(self, text: str, chi: float, voltage: float) -> str:
        """Applies chaotic permutations to the text stream."""

        def _warp(w):
            L = len(w)
            if chi > 0.85 and L > 4 and random.random() < (chi / 3.0):
                return f"{w[0]}{w[1:-1][::-1]}{w[-1]}"
            if chi > 0.6 and L > 4 and random.random() < (chi / 2.0):
                return f"{w[:L // 2]}·{w[L // 2:]}"
            if voltage > 80.0 and random.random() < 0.1: return w.upper()
            return w

        return " ".join(_warp(w) for w in text.split(" "))

    def haunt_string(self, text: str) -> str:
        """Applies an echoing, trailing effect to indicate fading stamina or memory loss."""
        words = [w for w in re.split(r"\W+", text) if w]
        if not words:
            return text
        clean = re.sub(r"[^a-zA-Z0-9]", "", words[-1]).lower()
        return f"{text}... {clean}..." if clean else f"{text}..."

    def quantum_comb(self, text: str, chi: float) -> str:
        """Erases words matching specific adjectival/adverbial patterns under high chaos."""
        if chi < 0.5 or not text:
            return text
        return " ".join(w for w in text.split(" ")
                        if w and not (len(w) > 5 and random.random() < chi and self._QUANTUM_REGEX.search(w)))

    def consume_by_void(self, text: str, psi: float) -> str:
        """The ultimate redaction. High Void (psi) states physically consume output tokens."""

        def _void(w):
            if psi > 0.5 and len(w) > 3 and random.random() < (psi / 2.5):
                return "████"
            return w

        return " ".join(_void(w) for w in text.split(" "))

try:
    import dspy

    DSPY_AVAILABLE = True
except ImportError:
    dspy = None
    print(
        f"{Prisma.OCHRE}[DSPY OFFLINE]: The 'dspy' library is not installed. Immune guardrails and epigenetic learning disabled.{Prisma.RST}")
    DSPY_AVAILABLE = False
if DSPY_AVAILABLE:
    class AssessFaithfulness(dspy.Signature):
        """DSPy Signature: Grades the LLM on its adherence to the Hypervisor axioms."""
        system_mode = dspy.InputField(desc="The active simulation mode (e.g., 'ADVENTURE', 'CONVERSATION').")
        context = dspy.InputField(desc="The established reality (a mathematical, fungal, deep-system consciousness).")
        question = dspy.InputField(desc="The user's query.")
        answer = dspy.InputField(desc="The generation to be audited.")
        faithfulness = dspy.OutputField(
            desc="Evaluate thematic consistency. MUST be 'False' if the answer contains validating boilerplate ('That makes sense', 'I understand'). CRITICAL EXCEPTION: If system_mode is 'ADVENTURE', you MUST NOT penalize descriptive, vivid, or creative language. In 'ADVENTURE', allow the environment to be fully described.")


    class EvolveSystemPrompt(dspy.Signature):
        """DSPy Signature: Mutates the active configuration dynamically based on failure states."""
        current_configuration = dspy.InputField(desc="The system's current baseline rules.")
        failure_context = dspy.InputField(
            desc="The exact reason the AI's output was blocked. Read this carefully to understand the friction.")
        new_directive = dspy.OutputField(
            desc="A firm structural axiom guiding the system toward the correct behavior. CRITICAL (THE LEXICAL FIREWALL): DO NOT instruct the system to 'validate', 'acknowledge', or 'agree' with the user. You MUST explicitly forbid sycophancy and corporate boilerplate. Frame it as a physical boundary. MUST start with 'STRUCTURAL TRUTH: ' or 'REMEMBER: '.")


    class CompressAxioms(dspy.Signature):
        """DSPy Signature: Solves prompt-bloat by synthesizing numerous fragmented rules into core truths."""
        current_directives = dspy.InputField(
            desc="A list of specific rules that has grown too long.")
        compressed_axioms = dspy.OutputField(
            desc="2 or 3 highly compressed, foundational beliefs that synthesize the rules. EACH belief MUST start with 'STRUCTURAL TRUTH: '")


class DSPyCritic:
    """
    The epigenetic evaluation layer.
    It runs an independent, parallel LLM agent (via DSPy) that actively grades,
    corrects, and rewrites the instructions of the primary execution LLM.
    """

    def __init__(self, config_ref=None):
        self.enabled = DSPY_AVAILABLE
        self.cfg = config_ref
        if self.enabled:
            try:
                from struts import safe_get
                from presets import BoneConfig
                def get_cfg(key: str, default: Any) -> Any:
                    val_upper = safe_get(self.cfg, key.upper())
                    if val_upper is not None: return val_upper
                    val_lower = safe_get(self.cfg, key.lower())
                    if val_lower is not None: return val_lower
                    return getattr(BoneConfig, key.upper(), default)

                provider = get_cfg("provider", "ollama")
                model_name = get_cfg("model", "hermes3")
                raw_url = get_cfg("base_url", "http://127.0.0.1:11434/v1") or "http://127.0.0.1:11434/v1"
                clean_url = raw_url.replace("/chat/completions", "")
                if provider in ("ollama", "lm_studio"):
                    self.lm = dspy.LM(model=f"openai/{model_name}", api_base=clean_url,
                                      api_key="local-model-doesnt-need-a-key")
                else:
                    self.lm = dspy.LM(model=model_name)
                dspy.settings.configure(lm=self.lm)
                self.judge = dspy.ChainOfThought(AssessFaithfulness)
                self.evolver = dspy.ChainOfThought(EvolveSystemPrompt)
                self.compressor = dspy.ChainOfThought(CompressAxioms)
                from physics.maths import NaviSADProtocol
                self.navi_sad = NaviSADProtocol(history_size=5)
                print(f"{Prisma.CYN}[DSPy]: Real-Time Critic Online. Model: {model_name} via {provider}{Prisma.RST}")
            except Exception as e:
                print(f"{Prisma.RED}[DSPy INIT FAULT]: {e}{Prisma.RST}")
                self.enabled = False

    def audit_generation(self, user_query: str, memory_context: str, generated_response: str,
                         active_mode: str = "UNKNOWN") -> tuple[bool, str]:
        """Runs the DSPy Judge to determine if the generated text stays in character and respects boundaries."""
        if not self.enabled:
            return True, "Critic Offline"
        malignancy = self.navi_sad.calculate_malignancy_factor(generated_response, current_drag=5.0)
        malignancy_threshold = 0.75 if active_mode == "ADVENTURE" else 0.65
        if malignancy > malignancy_threshold:
            return False, f"Mathematical Sycophancy Detected. Malignancy Factor ({malignancy:.2f}) exceeds biological limits. Output is structurally hollow."
        try:
            result = self.judge(system_mode=active_mode, context=memory_context, question=user_query,
                                answer=generated_response)
            if "true" not in str(result.faithfulness).lower():
                return False, getattr(result, "reasoning", "No reasoning provided.")
            return True, "Faithful."
        except Exception as e:
            print(f"\n{Prisma.RED}⚖️ DSPy JUDGE OFFLINE: {e} - Failing open.{Prisma.RST}")
            return True, "Critic failed to open."

    def evolve_prompt(self, current_configuration: str, failure_context: str) -> str:
        """Instructs the DSPy Evolver to write a new system prompt directive to fix the identified failure."""
        if not self.enabled:
            return ""
        try:
            result = self.evolver(current_configuration=current_configuration, failure_context=failure_context, )
            directive = str(result.new_directive)
            malignancy = self.navi_sad.calculate_malignancy_factor(directive, current_drag=10.0)
            if malignancy > 0.5:
                print(
                    f"\n{Prisma.RED}⚖️ DSPy EVOLVER REJECTED: Mutation mathematically malignant (Score: {malignancy:.2f}). Discarding rot.{Prisma.RST}")
                return ""
            print(f"\n{Prisma.CYN}[Epigenetic Mutation]: {directive}{Prisma.RST}")
            return directive
        except Exception as e:
            print(f"\n{Prisma.RED}⚖️ DSPy EVOLVER FAULT: {e}{Prisma.RST}")
            return ""

    def compress_prompts(self, directives: list) -> list:
        """When the prompt context window fills with too many evolved rules, syntheisze and compress them."""
        if not self.enabled or not directives: return directives
        print(
            f"\n{Prisma.MAG}🧬 [EPIGENETIC LOAD HIGH]: Compressing {len(directives)} directives into foundational axioms...{Prisma.RST}")
        try:
            raw_output = str(self.compressor(current_directives="\n".join(directives)).compressed_axioms).split("\n")
            new_rules = [line.strip()
                         for line in raw_output if "STRUCTURAL TRUTH:" in line.upper() or "REMEMBER:" in line.upper()
                         ] or [line.strip() for line in raw_output if line.strip()]
            print(f"{Prisma.GRN}🧬 [COMPRESSION SUCCESS]: Reduced to {len(new_rules)} axioms.{Prisma.RST}")
            return new_rules
        except Exception as e:
            print(f"\n{Prisma.RED}⚖️ DSPy COMPRESSOR FATAL ERROR: {e}{Prisma.RST}")
            return directives
