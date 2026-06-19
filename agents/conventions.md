# BoneAmanita Conventions

This document locks down implementation choices for BoneAmanita to prevent inconsistency across AI coding sessions. 

## The TONIC Table (Technically Obvious, Not Intended Choice)

Agents generating code for BoneAmanita must strictly adhere to this table. The "obvious" ecosystem default is often highly destructive to BoneAmanita's physics-driven native primitive architecture.

| Use                                                                     | Do NOT Use                                                           | Why                                                                                                                                                                                                       |
|-------------------------------------------------------------------------|----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `os.path.realpath` / `os.path.commonpath`                               | `os.path.abspath` / `startswith()`                                   | `abspath` is vulnerable to directory traversal attacks when paired with string-based root checks. BoneAmanita generates files dynamically; geometric containment must be absolute.                        |
| Raw Native Primitives (Lists, Tuples, Dicts, Floats)                    | LangChain, LlamaIndex, SemanticKernel                                | BoneAmanita requires cycle-by-cycle authority over the ATP pool, memory topology, and physics vectors. External orchestration wrappers hide these physical constraints.                                   |
| `numpy` (`np.argpartition`, matrices)                                   | Eager Python loops (`sorted()`, nested `min()`)                      | BoneAmanita traverses dense memory graphs and N-Dimensional topologies. $O(N)$ running minimums and C-level math are required. $O(N \log N)$ sorts will bottleneck the `GeodesicOrchestrator`.            |
| `.get()` with defaults / explicit dictionary bracket notation `adj[a1]` | Heavy abstraction wrappers (`safe_get`, `safe_set`) inside hot loops | "Paranoia drift" causes garbage collection thrash. Inside high-frequency loops (like biological homeostasis or topological rewiring), trust the established datatypes and run closer to the metal.        |
| The native `LLMInterface` (`composer.py`)                               | OpenAI SDK / Anthropic SDK directly                                  | The engine modulates `temperature` and `top_p` organically based on internal physics (e.g., `voltage`, `chi`). Bypassing the native composer severs the generative output from the biological simulation. |
| Pre-compiled class-level `__init__` configurations                      | `LoreManifest.get_instance()` dynamically fetched in a loop          | Fetching from the JSON singleton on every cycle tick introduces an immense function-call abstraction tax.                                                                                                 |
| `itertools.combinations` / `set.intersection`                           | Nested $O(N^2)$ list iterations                                      | Subconscious dredging and memory pruning requires pure C-level evaluation speed.                                                                                                                          |

## Language-Specific Conventions

* **Typing:** Explicit type casting (e.g., `float()`, `int()`) is required when extracting variables from the `physics_vector` or `LoreManifest` to prevent downstream mathematical errors.
* **Inline Math:** Avoid negative array padding calculations (e.g., `[None] * (5 - len(x))`). Explicitly bind lower limits `max(0, ...)` to prevent Python's negative multiplier list quirks.
* **Exceptions:** Fail loudly. Do not silently catch `TypeError` on critical system structures (like the `PhysicsPacket`). Toxic string injections into energy floats must crash the loop to trigger the `PanicRoom`, not mask the corrupted state.
