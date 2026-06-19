# Domain 04: The Phases Pipeline

**Domain Scope:** This document defines the sequential, immutable execution pipeline of BoneAmanita. Every user input travels through these phases exactly in order.


## 1. Specification

BoneAmanita processes input not as a chatbot, but as a biological simulation. The `phases/` pipeline is the heart of this process. It guarantees that mathematical reality (Physics), bodily state (Biology), and environmental context (Observation) are evaluated *before* any cognitive processing (AI Generation) occurs. 

The pipeline order is strict and immutable:

1.  **`ObservationPhase`:** The engine "gazes" at the input, extracting length, sentiment, and `clean_words`. It maps external input onto the internal `physics` vector.
2.  **`MetabolismPhase`:** (Biology) The core biological drain occurs. ATP is calculated based on the complexity of the input. If ATP reaches 0, the system initiates death protocols.
3.  **`MaintenancePhase`:** (Mechanical) Background tasks execute, such as tending the "village" garden or evaluating town hall census data.
4.  **`GatekeeperPhase`:** (Mechanical) The system checks for lore violations or impossible actions. If found, it applies massive `narrative_drag` rather than scolding the user.
5.  **`IntrusionPhase`:** (Biology) If the `psi` (madness) float is high, this phase intercepts the clean text and deforms it using the `TclWeaver` to simulate hallucinations.
6.  **`SimulationPreflightPhase`:** (Cognitive) Compiles the JSON bedrock variables (e.g., Sincerity Map) to prepare for generation, evaluating refusal conditions.
7.  **`CognitionPhase`:** (Cognitive) The final prep. It calculates philosophical resonance (`phi`) and determines if the engine is operating under extreme tension (requiring orthogonal shadow-casts).

Only after this entire pipeline successfully completes does the orchestrator pass the mutated physics vector and sanitized context to the `LLMInterface` for generation.


## 2. Decided

### [DEC-01] The Front-Loaded Configuration Map

**Decision:** All phases (`SimulationPreflightPhase`, `GatekeeperPhase`, etc.) must pre-compile their required dictionary targets (e.g., `SINCERITY_MAP`, `DRAG_MAX`) during class initialization (`__init__`) rather than dynamically fetching them from `LoreManifest` inside the `run()` loop.

**WHY:** The pipeline executes for every single interaction. Dynamic JSON fetches inside the `run` method introduce redundant abstraction tax. 

**WHY NOT:** Dynamic fetching ensures real-time updates. However, the system's execution speed dictates that bedrock variables remain static during the lifespan of the instance.

### [DEC-02] Trusting Internal Object Structures

**Decision:** Within the phases, internal data passing (like extracting variables from the guaranteed `gaze_result` or mutating `ctx.physics`) uses native Python bracket notation (`dict["key"]`) and direct assignment (`ctx.physics.psi = 1.0`).

**WHY:** The pipeline boundaries are inherently secure by design. Reapplying paranoid abstraction wrappers like `safe_get` to objects that are mathematically guaranteed to be the correct type ("paranoia drift") forces the Python runtime to evaluate unnecessary Try/Except bytecode.

**WHY NOT:** Wrapper functions prevent unexpected null errors. In BoneAmanita, unexpected nulls in the physics pipeline *should* crash the system and trigger the `PanicRoom` rather than silently continuing.

### [DEC-03] Biological Override (The Coma State)

**Decision:** If `MetabolismPhase` calculates that ATP is insufficient to process the query, it short-circuits the rest of the pipeline and returns a "limbo" or coma response.

**WHY:** The engine is constrained by simulated biology. It cannot "think" if it has no energy. 

**WHY NOT:** Skipping generation results in a poor user experience. BoneAmanita prioritizes visceral biological simulation over standard chatbot convenience.

### [DEC-04] The Somatic Shock Protocol (Controlled Bleed)

**Decision:** While the pipeline is strictly sequential, mechanical or cognitive phases (like `GatekeeperPhase`) that encounter terminal paradoxes or extreme reality-breaks are authorized to reach backward into the biological layer and instantly burn ATP (Somatic Shock).

**WHY:** The standard `MetabolismPhase` calculates energy based on syntactic input complexity. It cannot predict if a simple sentence ("delete the core") is conceptually toxic. When the cognitive layer realizes the danger, the engine must simulate an instant biological stress response (heart rate spike/energy burn).

**WHY NOT:** Strict phase isolation makes debugging easier. However, biological systems do not isolate adrenaline responses; cognitive realization triggers instant physical consequences.


### [DEC-05] Waking Dream Injection
**Decision:** Dreams are injected during the Waking Waking `CognitionPhase`, not `ObservationPhase`. Waking triggers "Brain Fog" (spikes in `chi` and `narrative_drag`), and "ghost words" are mechanically extracted from the dream log and prepended to the user's `clean_words` array.
**WHY:** A dream is a cognitive distortion, not an external observation. By prepending dream artifacts to the waking text, the `MemoryCore` is forced to topologically bind the hallucination to the physical user input before encoding it to the graph.

## 3. Open Questions

*(Currently no open architectural questions for Domain 04. The phase pipeline is strictly sealed.)*