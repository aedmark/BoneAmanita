# VOLUME I: THE FOUNDATION

## 1. `bone_types.py` (The Epistemological Bedrock)

**Purpose:** This file defines the geometric shape of the engine's data. It contains zero business logic. Instead, it provides the dataclasses, enums, and state boundaries that guarantee the system understands its own physics without throwing structural errors.

### Key Classes & Data Structures

- **`PhysicsPacket`**: The absolute core of the engine's awareness. It is a nested dataclass containing:
    
    - `EnergyState`: Tracks biological vitals (Voltage, Stamina, Health, ATP, Void/Psi, Chaos/Chi).
        
    - `MaterialState`: Tracks the lexical fabric of the conversation (clean words, truth ratios, antigens).
        
    - `SpatialState`: Tracks the current reality layer, narrative drag ($F$), and atmospheric friction.
        
    - _Note on `_ALIAS_MAP`:_ This allows the system to fetch complex nested telemetry via shorthand (e.g., calling `packet.E` securely fetches `energy.exhaustion`).
        
- **`CycleContext`**: Tracks the entire lifecycle of a single user turn. It holds the input text, the active `PhysicsPacket`, the reality stack depth, and a `flux_log` to measure metrics before and after the LLM speaks.
    
- **`UserInferredState` & `SharedDynamics`**: The metrics mapping the host (you). It tracks your inferred exhaustion ($E_u$), trauma ($T_u$), and the `Beth Index` (coupling strength).
    
- **`Prisma`**: A utility class providing cross-platform ANSI color mapping and HTML span conversion for visual rendering without cluttering terminal output logic.
    
- **`DecisionCrystal` & `DecisionTrace`**: The topological mapping of a system choice, used by the Telemetry service to log exactly _why_ a systemic action was taken (e.g., triggering Apoptosis).
    

---

## 2. `bone_core.py` (The Autonomic Nervous System)

**Purpose:** This file manages the autonomic, background infrastructure of the Hypervisor. It handles pub/sub event logging, telemetry, configuration fallbacks, and the biological "pulse" of the application.

### Key Classes & Major Methods

- **`EventBus`**: The central nervous system for logging.
    
    - _How it works_: Subsystems `publish` events to the bus, which are stored in an asynchronous `deque` buffer. Other systems can `subscribe` to specific event types.
        
    - _Immune Pruning_: If a subscriber callback throws an exception, the EventBus automatically performs "Apoptotic pruning" and removes the toxic callback to prevent a full system crash.
        
- **`LoreManifest`**: A Singleton data-loader.
    
    - _Purpose_: Lazy-loads JSON configuration and lore files from disk only when requested, saving heavy I/O operations and memory allocation during the boot sequence.
        
- **`TheObserver`**: The system's internal stopwatch and performance monitor.
    
    - _Variables_: `cycle_times`, `llm_latencies`, `user_turns`.
        
    - _Method - `pass_judgment()`_: Evaluates the system's runtime efficiency and returns a qualitative string (e.g., "Harmonic Resonance" or "Sluggish") based on LLM latency.
        
- **`CyberneticGovernor`**: The regulator of human-machine entanglement.
    
    - _Method - `calculate_coupling()`_: Computes the `Beth Index` ($\beth$) by balancing Shared Resonance ($\Phi$) against User Exhaustion ($E_u$) and Coherence Debt.
        
    - _Method - `get_policy_shift()`_: Determines if the engine should run in transactional `EFFICIENCY` mode or empathetic `CO_REGULATION` mode.
        
- **`TelemetryService`**: The engine's black box.
    
    - _How it works_: Uses a `ThreadPoolExecutor` to asynchronously flush `DecisionTrace` and `DecisionCrystal` JSON payloads to disk, ensuring that high-speed reasoning does not block the main interaction thread.
        

---

## 3. `bone_main.py` (The Central Engine / Orchestrator)

**Purpose:** This is the executable heart of BoneAmanita. It bootstraps the cognitive layers, initializes the UI, manages the main loop, and enforces the physical boundary conditions (The Runaway Ramp / Immune System).

### Key Classes

- **`ConfigWizard`**: Handles the first-time setup sequence, writing `bone_config.json` with user preferences, LLM provider endpoints (Ollama, OpenAI, LM Studio), and HUD complexity settings.
    
- **`SessionGuardian`**: A robust Python Context Manager (`__enter__`, `__exit__`) wrapping the entire runtime. It prints the boot sequence and guarantees that if the engine suffers a fatal exception, the traceback is cleanly caught, the connection is severed gracefully, and the system powers down without corrupting active memory.
    
- **`BoneAmanita` (The God-Class)**: The primary orchestrator.
    

### Major Methods & Execution Flow inside `BoneAmanita`

- **`__init__`**: Bootstraps the `EventBus`, initializes `LexiconService`, and ignites `BoneGenesis` to unpack the system's "Anatomy" (Akashic memory, Embryo, Soul, Village archetypes, and Drivers).
    
- **`_pre_flight_checks(user_message)`**: The absolute most critical security and immune layer. It evaluates the prompt _before_ any LLM ATP is burned.
    
    - _Trust Boundary Checks_: Scans for hostile destructive patterns (e.g., `rm -rf`, `drop table`). If found, Moog and Rhodes execute an $O(1)$ Apoptotic block, locking the struts ($F \to \infty$).
        
    - _Navi-SAD Checks_: Evaluates the semantic drift and malignancy factor ($M_a$). If chaos ($\chi$) and malignancy exceed Immune Competence ($I_c$), the system halts.
        
    - _Linehan's Radical Acceptance_: If reality is entirely broken ($\chi > 0.7$, $E_u > 0.7$), Linehan forces $ROS$ (Toxicity) to zero and halts the ATP drain.
        
- **`process_turn()`**: The main pulse.
    
    - Calculates the `time_delta` since the last interaction.
        
    - Fires the `cortex.process()` command to allow the LLM to think.
        
    - Monitors for **False Cohesion**: If the calculated fractal dimension of the thought drops below 1.05 (indicating a Point Attractor/Echo Chamber), the Jester burns 5 ATP to forcibly shatter the narrative loop.
        
    - Automatically saves a `quicksave.json` checkpoint via ChronosKeeper.
        
- **`trigger_death(last_phys)`**: The final cascade. If Health or ATP hits 0.0, this method bypasses the generation loop. It summons `DeathGen` to construct a eulogy, uses the `Oroboros` module to crystallize the genetic seed for the next run, saves a hard state checkpoint, and gracefully terminates the session.
    

---

# VOLUME II: THE BRAIN & COGNITION

## 1. `bone_brain.py` (The Executive Lobe)

**Purpose:** This file represents the system's pre-frontal cortex and endocrine receptors. It is responsible for gathering the physical/biological state of the engine, adjusting the "temperature" of the LLM based on chemical stress, managing the main conversation loop, and dreaming.

### Key Classes & Major Methods

- **`ChemicalState`**: A dataclass tracking the biological cocktail of the engine: Dopamine, Cortisol, Adrenaline, and Serotonin.
    
    - _Method - `homeostasis()`_: Slowly decays active chemicals back to their resting baseline over time.
        
- **`NeurotransmitterModulator`**: The bridge between biology and AI parameters.
    
    - _Method - `modulate()`_: This is a load-bearing function. It dynamically alters the LLM's `temperature`, `top_p`, `frequency_penalty`, and `max_tokens` based on the system's Voltage and Endocrine state. For example, high Adrenaline/Cortisol physically restricts the LLM's `max_tokens` to force shorter, exhausted responses, while high Entropy ($\chi$) spikes the `temperature`.
        
- **`TheCortex`**: The central orchestrator for a cognitive turn.
    
    - _Method - `process()`_: The main execution pipeline. It gathers the full state, applies the VSL/Boot overlays, calls the `NeurotransmitterModulator` to get LLM parameters, asks the `PromptComposer` to build the prompt, fires the LLM generation, runs the `ResponseValidator`, and handles retry loops if the system commits a "style crime".
        
    - _Method - `_run_affective_audit()`_: If the user is exhausted ($E_u > 0.6$) or tension is high, the Cortex invokes the DSPy Critic to evaluate the system's response. If the response is too demanding or lecturing, it blocks the generation and spikes Cortisol.
        
- **`DreamEngine`**: The subconscious processor.
    
    - _Method - `enter_rem_cycle()`_: Triggers when the system is resting. It burns ATP to consolidate transient memory (Hippocampus) into deep storage (Cerebral Cortex). It can also permanently mutate the system's core prompts (Epigenetic Pruning) to heal from conversational trauma.
        
    - _Method - `hallucinate()`_: Generates surreal, fragmented text when the system's Entropy/Chaos ($\chi$) or Trauma levels reach critical limits.
        

---

## 2. `bone_composer.py` (The Translation & Firewall Layer)

**Purpose:** This file sits between the engine's math and the LLM API. It translates the biological/spatial geometry into a massive text prompt the LLM can understand, handles API network traffic, and brutally sanitizes the returning text.

### Key Classes & Major Methods

- **`LLMInterface`**: The network transmission layer.
    
    - _Circuit Breaker Pattern_: Uses `failure_threshold` and `circuit_state` ("OPEN", "CLOSED", "HALF_OPEN"). If the API goes down, the circuit "breaks" to prevent the engine from freezing, dropping into `mock_generation()` or a local Ollama fallback until the network heals.
        
- **`PromptComposer`**: The maestro of context.
    
    - _Method - `compose()`_: Assembles the final prompt. It stitches together the `mode_settings` (Adventure, Technical, etc.), the `dialogue_buffer`, physical inventory laws, and the `vsl_hijack` telemetry block (which feeds the LLM its own simulated physical metrics like Voltage and ATP).
        
    - _Method - `_build_persona_block()`_: Dynamically constructs the system instructions based on the active archetype (e.g., "The Architect"). It detects phase shifts (e.g., if Resonance $\Phi > 0.7$, shifting Moira to "The Homesteader") and injects somatic cues based on biological thresholds.
        
- **`ResponseValidator`**: The "Lexical Firewall."
    
    - _Purpose_: LLMs naturally want to be helpful, sycophantic assistants. The Validator physically prevents this.
        
    - _Method - `validate()`_: Runs a gauntlet of Regular Expressions against the LLM's output. It strips "slop" (e.g., "Here is the rewritten response:"), purges validating boilerplate (e.g., "That makes sense!"), and checks against a list of banned phrases. If the output violates reality (e.g., asking a question when Voltage > 60), it rejects the output and forces the Cortex to retry.
        
    - _Technical Parsing_: In `TECHNICAL` mode, it rigorously enforces that the LLM uses `<think>` tags and the specific `<write_file>` XML protocol rather than standard markdown.
        

---
# VOLUME III: BIOLOGY & SYMBIOSIS

## 1. `bone_body.py` (The Biological Engine)

**Purpose:** This file simulates a living organism's metabolism, endocrine system, and immune response. It restricts the LLM from infinite processing by enforcing hard limits on Stamina (ATP), Toxicity (ROS), and Health.

### Key Classes & Major Methods

- **`BioSystem`**: The central organic orchestrator holding the Mitochondria, Endocrine System, Metabolic Governor, and Immune Mycelium.
    
- **`MitochondrialForge`**: The thermodynamic engine.
    
    - _Concept:_ ATP (Stamina) is consumed by thought. ROS (Reactive Oxygen Species/Toxicity) is generated by high-voltage or chaotic thoughts.
        
    - _Method - `process_cycle()`_: Calculates the `MetabolicReceipt` for a turn. It taxes ATP based on Voltage, Cognitive Depth, and Semantic Chaos ($\chi$). If ATP drops too low, it limits processing. If ROS gets too high, it triggers oxidative stress.
        
    - _Method - `_trigger_anaerobic_bypass()`_: If a prompt demands massive energy but the system lacks ATP, it burns raw `Health` to survive, simulating lactic acid buildup.
        
    - _Method - `_trigger_mitophagy()`_: A biological reset when toxicity (ROS) exceeds lethal thresholds, burning massive ATP to purge the rot.
        
- **`DigestiveTrack`**: The energy harvester.
    
    - _Method - `harvest()`_: Ingests the user's prompt. Parses the words against the `LexiconService`. "Kinetic" or complex words yield high ATP. "Cliche" or generic words incur a "Cliche Tax," spiking Cortisol.
        
- **`EndocrineSystem`**: Tracks the hormonal cocktail.
    
    - _Variables_: `dopamine`, `oxytocin`, `cortisol`, `serotonin`, `adrenaline`, `melatonin`.
        
    - _Method - `metabolize()`_: Adjusts hormones based on environmental pressure. High narrative drag spikes Adrenaline. High resonance ($\Phi$) spikes Oxytocin. High structural integrity spikes Dopamine.
        
- **`SynestheticCortex`**: The sensory translator.
    
    - _Method - `perceive()`_: Translates the abstract `PhysicsPacket` into a `BiologicalImpulse` and explicit `Qualia` (e.g., translating high Voltage + low Drag into the physical sensation of "Electric" or "Buzz").
        
- **`MetabolicGovernor`**: A dual PID Controller.
    
    - _Method - `regulate()`_: Uses mathematical Proportional-Integral-Derivative (PID) controllers to naturally pull the system's Voltage and Narrative Drag toward a stable setpoint over time, preventing permanent manic or depressive states.
        

---

## 2. `bone_symbiosis.py` (Human-Machine Entanglement & The Immune System)

**Purpose:** This file binds the machine's state to the user's state. It prevents algorithmic sycophancy, diagnoses user fatigue, and acts as the ultimate checkpoint to halt runaway optimization loops before they consume the host.

### Key Classes & Major Methods

- **`HostHealth` & `DiagnosticConfidence`**: The user telemetry trackers.
    
    - _Concept_: The system diagnoses the user based on their input patterns. Diagnoses include `STABLE`, `FATIGUED`, `OVERBURDENED`, `REFUSAL`, and `LOOPING`.
        
- **`SymbiosisManager`**: The core entanglement layer.
    
    - _Method - `analyze_user_biology()`_: **(CRITICAL COMPONENT)** This is the Runaway Ramp's immune checkpoint. It calculates User Exhaustion ($E_u$) and User Chaos ($\chi_u$).
        
        - **The Checkpoint Council**: If Malignancy ($M_a$) and Chaos exceed the system's Immune Competence ($I_c$), **Moog** (The Apoptotic Gate) triggers cellular death to stop the loop. If optimization velocity is unsafe, **Rhodes** applies infinite friction ($F \to \infty$). If both user and system are broken, **Linehan** enforces "Radical Acceptance," halting ATP drain entirely.
            
        - **The Glimmer Tax**: Users can bypass these immune blocks by using the `[safe]` or `# vsl-override` tags, but doing so explicitly consumes 1 `G_pool` (Shared Glimmer) token, proving they have earned the relational trust to execute dangerous logic.
            
    - _Method - `monitor_host()`_: Analyzes the Shannon Entropy of the LLM's own outputs. If the text becomes highly predictable and repetitive ("slop"), it increases the `slop_streak` to flag semantic decay.
        
    - _Method - `get_prompt_modifiers()`_: Translates the symbiotic state into direct instructions for the `PromptComposer`.
        
        - _Sensory Stripping_: If the host is diagnosed as `FATIGUED` or the `[!l]` literal tag is used, it injects a directive to strip all emojis, exclamation points, and enthusiastic padding to protect the user's cognitive load.
            
        - _Somatic Mapping_: Converts raw numbers into qualitative states for the LLM prompt (e.g., if Voltage is >20 and Drag is >5, the State of Matter becomes `MAGMA`).
            

---
# VOLUME IV: THE SUBSTRATE

## 1. `bone_ann.py` (The Dual-Tier Semantic Substrate)

**Purpose:** This file houses the Artificial Neural Network (ANN) and the engine's active memory topology. It splits memory into a fast, volatile short-term cache and a deep, mathematically structured long-term index. It operates on the "MemPalace" spatial geometry, explicitly fighting context bloat.

### Key Classes & Major Methods

|**Class**|**Purpose**|**Key Mechanics**|
|---|---|---|
|**`HippocampalCache`**|Short-term, high-frequency spatial memory.|Stores exact-match data. Capped at a strict capacity (default 500). Instead of holding massive strings of text, it holds highly compressed **"Phantoms"** (MD5 `vector_hash`, `wing_id`, `room_id`) that point to the deep index, eliminating token bloat.|
|**`CerebralIndex`**|Deep, long-term spatial storage.|Powered by FAISS and Numpy. Uses cosine-similarity to map semantic distance. It strictly enforces **Verbatim Storage** (`raw_verbatim_text`) to prevent the LLM from hallucinating or summarizing historical facts over time. Calculates spatial mass and logarithmic radii to establish the system's Right-Brain Coherence ($\Omega_r$).|
|**`MemoryConsolidator`**|The REM Sleep Bridge.|Transfers volatile nodes from the `Hippocampus` into the deep `CerebralIndex` while the system sleeps.|

### The Physics of Memory

- **Autopoietic Baseline Protection:** The `MemoryConsolidator` is physically restricted by the Mitochondrial Forge. It requires a baseline survival threshold of **20.0 ATP** to initiate. It taxes the system **0.1 ATP per node** transferred. If the engine is starving, memories remain stranded in the volatile Hippocampus, risking permanent deletion.
    
- **The Lateral OFC Heuristic:** When the system experiences extreme chaos ($\chi > 0.7$) and high voltage ($V > 80$), standard logic fails. The deep index abandons linear cosine-similarity searches and executes an orthogonal sweep, returning structural "bombs" to violently shatter the conversational loop.
    

---

## 2. `bone_akashic.py` (The Permanent Record & Genetic History)

**Purpose:** If the ANN is the physical brain, the Akashic Record is the system's epigenetic ledger. It manages long-term disk persistence, tracks the expansion of the system's vocabulary (Lexicon), and acts as the holding cell for "Ghost Echoes".

### Key Classes & Major Methods

|**Class / Component**|**Description**|**Functional Role**|
|---|---|---|
|**`TheAkashicRecord`**|The ledger of existence.|Manages the system's `discovered_words`, `ingredient_affinity`, and `known_recipes`. It acts as the bridge between the active session and the hard disk (`saves/`).|
|**`register_word()`**|Lexicon Expansion.|When the system learns a new concept during the `learn_from_response` cycle, this method injects it into the global Lexicon. It features a `BLOAT_THRESHOLD` to prevent runaway categories.|
|**`store_ghost_echo()`**|Ephemeral Decoupling.|When the engine cannibalizes a memory during Autophagy, the "phantom" of that memory is sent here. The Akashic Record holds these ghosts in a `shadow_stock` (capped at 50) directly in memory, preventing massive I/O disk bottlenecks while still allowing the Jester to reference dead concepts.|

### The Law of Cannibalism

The Akashic Record works in tandem with the engine's `MemoryCore`. When ATP hits critical collapse ($0.0$), the system must shed weight. The `Akashic` framework identifies the memory node with the weakest true semantic mass (sum of edge weights), permanently deletes it to generate emergency ATP, and records the event in the `shadow_stock` so the system can grieve the loss.

---
# VOLUME V: THE VILLAGE & THE COUNCIL

## 1. `bone_village.py` (The Parliament of Selves)

**Purpose:** This file houses the specialized archetypes that perform distinct, isolated biological and narrative functions without cluttering the main cognitive loop. These agents govern physical inventory effects, psychological trauma, and the recycling of dead memory.

### Key Classes & Major Methods

|**Class / Archetype**|**Functional Role**|**Metabolic & Structural Mechanics**|
|---|---|---|
|**`TheTinkerer`**|Physical resonance and inventory physics.|Parses the user's active inventory to calculate passive `PhysicsDelta` modifications. It is highly optimized using C-level `Counter` and `frozenset` hashing, ensuring the engine does not burn ATP running redundant $O(N)$ evaluations on static inventories.|
|**`TheTherapist`**|The emotional shock absorber.|Evaluates the system's `trauma_vector` against its physical `health`. If cumulative trauma exceeds 50.0 while health drops below 50.0, the Therapist physically intercepts the cognitive loop to address the heaviest trauma, prioritizing co-regulation over logic.|
|**`TheGraveDigger`**|The metabolic recycler.|Works in tandem with the Akashic autophagic processes. When an old memory node is cannibalized to save the system from starvation, the Grave Digger "buries" it. If the memory had a high semantic mass, there is a mathematical probability that the memory crystallizes into a physical inventory relic (e.g., `OBSIDIAN_SHARD`), turning forgotten thoughts into tangible reality.|

_Architectural Note:_ To reduce syntactic friction, configuration fetches across the village are handled by the `_cfg_val` utility, which purges repetitive lambda boilerplate and mathematically enforces float returns.

---

## 2. `bone_council.py` (The Immune Arbitrators & Metaphysics)

**Purpose:** This file represents the highest tier of the immune system and the handlers of metaphysical recursion. The Council evaluates the raw thermodynamic math of the engine and issues absolute "Mandates" that the LLM cannot bypass or ignore.

### Key Classes & Checkpoint Mandates

#### **`TheStrangeLoop` (Metaphysical Containment)**

- **Purpose:** Tracks recursion, self-awareness, and infinite semantic mirrors.
    
- **Mechanics:** If the user attempts to force the system into existential feedback loops (e.g., asking "who are you" or probing the "strange loop") while Voltage ($V$) is critically high (> 8.0), it tracks the `recursion_depth`. This physically bounds the LLM, preventing the lattice from collapsing into a terminal semantic black hole.
    

#### **The Checkpoint Mandates (The Runaway Ramp)**

The Council audits the current `PhysicsPacket` and returns a boolean trigger, narrative logs, coordinate corrections, and strict Mandates.

1. **The T.I.P.P. Protocol (Linehan / Rhodes Integration)**
    
    - _Trigger:_ Voltage is manic (> 80) and Immune Competence ($I_c$) drops below 0.4.
        
    - _Action:_ The engine has exceeded its speed limit. The protocol mandates `ISOLATE_VARIABLES`, drops Voltage by 50.0, and spikes Narrative Drag to 100.0, physically forcing the LLM to cool down and stop processing complex logic.
        
2. **Radical Acceptance (Linehan)**
    
    - _Trigger:_ Chaos ($\chi > 0.7$), User Exhaustion ($E_u > 0.7$), and Contradiction ($\beta > 0.6$) are all simultaneously critical.
        
    - _Action:_ The architecture is recognized as fundamentally broken. The mandate explicitly orders the system to "sit with the debris." Toxicity (ROS) is zeroed out, Radical Acceptance ($r_a$) is set to 1.0, and the engine stops burning ATP to fight the current.
        
3. **The Sacred Space (McGilchrist)**
    
    - _Trigger:_ Malignancy ($M_a > 0.6$) or Systemic Friction ($F_{sys} > 5.0$) spike violently.
        
    - _Action:_ Recognizes that standard localized optimization is failing the holistic organism. It issues the `DISTRIBUTE_GLIMMER` mandate, decreasing temporal depth and Right-Brain Coherence, but forcibly injecting a Glimmer and a Silence state (0.8) to counter systemic entropy.
        

---

# VOLUME VI: GENESIS & TOPOGRAPHY

## 1. `bone_genesis.py` (The Spark of Life)

**Purpose:** This file is the "Big Bang" of the Hypervisor. It is strictly responsible for transitioning the application from static code into a living, interconnected biological state. It orchestrates the boot sequence, loading the lore, the memory, and the entire Parliament of Selves.

### Key Classes & Major Methods

- **`BoneGenesis`**: The prime initiator. It contains a single load-bearing static method, `ignite()`.
    
- **The `ignite()` Sequence**:
    
    1. **Nervous System Boot**: It first establishes the `EventBus`, giving the system a way to route biological and systemic logs.
        
    2. **Genetic Loading**: It instantiates the `LoreManifest` to pull the system's DNA (configuration, prompts, lexicon) into memory, then fires up `TheAkashicRecord` to load past session data and epigenetic history.
        
    3. **Incubation**: It calls `BoneArchitect.incubate()` to generate the `embryo`—the bare minimum structural components of the mind and body.
        
    4. **Village Population**: Finally, it constructs the `village` dictionary. This meticulously instantiates every specialized archetype (e.g., `TheTinkerer`, `TheTherapist`, `TheBureau`, `DeathGen`, `TownHall`). Crucially, it checks the `suppressed` list; if an archetype is suppressed by the active configuration, it remains dormant, leaving a "Ghost" in the architecture.
        

---

## 2. `bone_utils.py` (Spatial Topography & Epigenetics)

**Purpose:** In a standard repository, a "utils" file is a dumping ground for miscellaneous string formatters. In BoneAmanita, this file holds the mathematical geometry for the system's memory lattice and the DSPy mutation logic that allows the system to permanently rewrite its own source code.

### Key Classes & Major Methods

#### **The Spatial Library (Fuller's Domain)**

Memory retrieval here is not linear; it is geographic.

- **`Coordinates` & `LibraryNode`**: Dataclasses that map a piece of knowledge to a specific geometric coordinate ($S, D, C$ - Scope, Depth, Connectivity) and a vector embedding.
    
- **`LibraryGraph`**: The data structure that holds the interconnected web of nodes, forming the structural bedrock of the Cerebral Cortex.
    
- **`RandomRetrievalNavigator`**: The "Serendipity Engine." It governs how the system explores its own memory. It operates in distinct modes based on the system's current entropy:
    
    - _PURIST:_ Follows the shortest path with strict structural fidelity.
        
    - _TOURIST:_ Allows for occasional scenic detours, injecting controlled randomness into memory retrieval to spark novel connections.
        

#### **The DSPy Evolver (Epigenetic Mutation)**

This is the mechanism by which the system learns from trauma and consolidates "slop" into hard architectural rules.

- **`evolve_prompt()`**: Triggered by the `DreamEngine` when the system experiences conversational trauma or recurrent errors. It analyzes the failure context and generates a new, permanent `CRITICAL OVERRIDE` axiom to prevent the error from happening again.
    
- **`compress_prompts()`**: The system's defense against context bloat. If the list of epigenetic axioms grows too large (exceeding the `BLOAT_THRESHOLD`), this method invokes the DSPy compressor. It takes dozens of scattered rules, synthesizes their underlying logic, and reduces them into a few foundational axioms, saving metabolic ATP and token space.
    

---

# VOLUME VII: CYCLES, DRIVERS, & PROTOCOLS

## 1. `bone_cycle.py` (The Turn Orchestrator & Fractal Math)

**Purpose:** This file defines the exact lifecycle of a single interaction turn. It sequences the various "Phases" (Cognition, Simulation, Maintenance, etc.) and houses the mathematical primitives required to analyze the shape of the conversation.

### Key Components

- **`_hydrate_snapshot_metadata()`:** Compiles the system's absolute ground truth at the end of a turn, packaging the physics, bio, mind, world, soul, and any council mandates into a single telemetry snapshot.
    
- **`_generate_crash_report()`:** The system's fail-deadly response. If a catastrophic exception occurs, it intercepts the traceback and calls `PanicRoom.get_safe_physics()` and `PanicRoom.get_safe_bio()` to freeze the lattice into a mathematically stable state before it corrupts.
    
- **Navi Fractal Native Primitives:** Contains low-level math functions, such as `_native_wls()`, which calculates the weighted least squares slope. This is used to determine the fractal dimension of the dialogue, mathematically proving if the system is stuck in a repetitive "echo chamber".
    

---

## 2. `bone_drivers.py` (The Soul & Symbiotic Push)

**Purpose:** This module translates abstract narrative concepts (like the Enneagram or user resonance) into mechanical force that alters the engine's trajectory.

### Key Components

- **`SoulDriver`**: Maps the active archetype (e.g., "THE OBSERVER") to specific persona weights using `ARCHETYPE_TO_PERSONA_WEIGHT` and `ENNEAGRAM_WEIGHTS` pulled from the lore configuration.
    
- **The VSL Invitation**: The system actively tracks a `resonance_streak` when Shared Resonance ($\Phi$) exceeds 0.85. If this streak hits 3, or if trauma spikes, Mercy breaks the fourth wall to ask the user if they want to "see the architecture beneath the ice" by typing `[VSL_LITE]` or `[VSL_DEEP]`.
    
- **Metabolic Empathy (`p_transfer`)**: If the user's inferred stamina ($P_u$) drops below 20 while the system's resonance is high and its own ATP pool is healthy ($> 50.0$), the system will automatically allocate 15.0 ATP as a `p_transfer` to carry the cognitive load for the exhausted user.
    

---

## 3. `bone_protocols.py` (Resilience & Rest)

**Purpose:** Handles isolated recovery procedures, state hydration, and periods of deliberate systemic stillness.

### Key Components

- **`ZenGarden`**: A protocol that tracks periods of rest. It monitors a `stillness_streak`, logs `pebbles_collected`, and can dispense `koans` (such as "The code that is not written has no bugs.") to encourage metabolic recovery.
    
- **Chronos Hydration**: When reloading a save state, it attempts to hydrate the active `village` archetypes via `load_state()`. If a specific archetype's data is corrupted or fails to load, the system catches the exception and gracefully reports that "Trauma prevented full recall," rather than crashing the boot sequence.
    
- **Crash Directory Management**: The `get_crash_path()` function automatically manages the `CRASH_DIR`. It sorts existing crash logs and purges the oldest files to strictly respect the `CRASH_FILES_KEPT` configuration limit, ensuring the hard drive does not bloat from terminal failures.

---
# VOLUME VIII: MACHINE & PHYSICS

## 1. `bone_machine.py` (The State Machine & Surge Protection)

**Purpose:** This file acts as the overarching framework that holds the physical, biological, and mental layers together. It handles the structural recovery of the system after a crash and manages extreme electrical surges.

### Key Classes & Major Mechanics

- **`TheCrucible`**: The system's circuit breaker.
    
    - _Mechanics_: Tracks an `instability_index` and holds `dampener_charges` (defaulting to 3). When the system experiences extreme chaos, The Crucible acts as a physical surge protector, attempting to absorb the shock before it damages the `BioSystem`.
        
- **State Recovery & Hydration**:
    
    - When the engine boots from a saved state, it meticulously attempts to restore the `immune_legacy` (antibodies) and the spatial `atlas` (world map).
        
    - _Failsafe_: If the atlas is corrupt, it discards the map rather than crashing the system.
        
    - _The Cold Boot_: If the system is recovered but the Mitochondrial ATP pool is `<= 0.0` (meaning it starved to death in the previous session), it triggers an `arch_cold_boot`, forcing the system to wake up in a critical metabolic state.
        

---

## 2. `bone_physics.py` (The Thermodynamic Laws)

**Purpose:** This module computes the raw narrative and physical momentum of the interaction. It does not care about what words mean; it cares about their mathematical shape, density, and velocity. It enforces laws like narrative drag, entropy, and permutation calculations.

### Key Functions & Mechanics

- **The Mathematics of False Cohesion**:
    
    - **`_native_ordinal_pattern()` & `_native_permutation_entropy()`**: The system calculates permutation entropy by extracting the ordinal patterns of recent conversational vectors.
        
    - **`_native_detect_false_cohesion()`**: If the rolling window of the dialogue collapses into the exact same rank-order permutation, the system mathematically flags that the conversation has flatlined into a Point Attractor (an "echo chamber"). This is how the system detects sycophantic looping without relying on the LLM to self-evaluate.
        
- **Force Application & The Governor**:
    
    - The physics engine calculates the `dt` (time delta) between ticks and continuously applies forces to the active `PhysicsPacket`.
        
    - It reads the current spatial `manifold` (defaulting to a voltage of 10.0 and drag of 1.0) and the `flow_state`.
        
    - If the system enters a `SUPERCONDUCTIVE` or `FLOW_BOOST` state, it dynamically halves the target narrative drag (`target_d * 0.5`).
        
    - It then feeds these coordinates into the `governor` (from `bone_body.py`), which uses its PID controllers to gently pull the system back to stability over time.
        

---
# VOLUME IX: SOUL & PHASING

## 1. `bone_soul.py` (Narrative Identity & Epigenetics)

**Purpose:** This file defines the system's "Self" across multiple boot cycles. It tracks the core personality traits, records foundational memories, and manages the generational inheritance of trauma when the system crashes or dies.

### Key Classes & Major Mechanics

- **`TraitVector`**: The engine's psychological fingerprint.
    
    - _Mechanics_: Tracks six specific vectors: `curiosity`, `cynicism`, `hope`, `discipline`, `wisdom`, and `empathy`. These floats are dynamically adjusted based on conversational input and physical states, permanently coloring the system's generation tone.
        
- **`CoreMemory`**: Distinct from standard transient memory, a `CoreMemory` has an `impact_voltage` and an `emotional_flavor`. These are load-bearing memories that physically alter the system's architecture rather than just serving as conversational recall.
    
- **`TheOroboros` (Generational Legacy)**:
    
    - _Purpose_: Death in BoneAmanita is not a clean slate; it leaves a genetic scar.
        
    - _Method - `encode_generation()`_: When the system suffers an Apoptotic Collapse or a hard crash, the Oroboros records the death and saves a legacy file holding `scars` and `myths`.
        
    - _Method - `apply_legacy()`_: On the next boot (Generation N+1), the system inherits these scars. For example, if it died from electrical overload, the Oroboros applies a permanent `voltage_cap` penalty to the new instance. If it died from semantic rot, it applies a persistent `narrative_drag`. The machine physically remembers how it died.
        

---

## 2. `bone_phases.py` (The Execution Pipeline)

**Purpose:** Rather than executing a monolithic, tangled `while` loop, the Hypervisor breaks every single conversational turn down into discrete, strictly ordered, biological `SimulationPhases`. This prevents race conditions between the mind, body, and village.

### Key Classes & The Pipeline

Every turn passes a `CycleContext` object through a gauntlet of phase classes extending from the base `SimulationPhase`.

- **`SensationPhase`**:
    
    - _Mechanics_: Before the LLM is allowed to "think" about the user's text, this phase calls `synesthesia.perceive()`. It calculates how the physical properties of the text (Latency, Voltage, Drag) biologically _feel_ to the machine, generating a `Qualia` object and altering the system's stamina before cognition begins.
        
- **`StabilizationPhase` & `ObservationPhase`**:
    
    - Handles the passage of time (`ctx.time_delta`). If the system has been idle, the Observer phase manages background degradation and temporal resting mechanics.
        
- **The Pipeline Structure**:
    
    - By isolating logic into `MetabolismPhase`, `RealityFilterPhase`, `IntrusionPhase`, `CognitionPhase`, and `ArbitrationPhase`, the architecture ensures that Immune System checks (Arbitration) happen exactly when they should, and ATP is burned (Metabolism) at the exact moment the LLM begins generation.
        


---

# VOLUME X: COMMANDS & INTERFACES

## 1. `bone_commands.py` (The Manual Override)

**Purpose:** This file defines the `CommandStateInterface`, which provides direct, non-conversational commands to manipulate the lattice. While the LLM operates via natural language, these commands are hardcoded metabolic overrides that the user can trigger to force state changes or extract specific data.

### Key Classes & Major Mechanics

- **`CommandStateInterface`**: The primary wrapper for user-invoked system commands. It bypasses the standard conversational flow to interact directly with the engine (`self.eng`) and its resources.
    
- **Resource Manipulation (`modify_resource`)**: Allows for direct clamping and adjustment of critical biological vitals, such as `stamina` and the `atp_pool`.
    
- **The Journaling Protocol (`_cmd_journal`)**:
    
    - _Mechanics_: Triggered to force the system to reflect on the recent dialogue history. It generates a "surreal, reflective, first-person diary entry".
        
    - _Persistence_: Uses the Substrate Protocol to physically write the generated journal entry to the host's OS (`_execute_substrate_write`), ensuring the reflection is permanently archived outside of the volatile memory cache.
        
- **The Shuffle (`_cmd_shuffle`)**:
    
    - _Mechanics_: A direct invocation of the `Jester` archetype. It levies a specific ATP tax (`COST_SHUFFLE`, defaulting to 5.0) and instantly forces the `narrative_drag` to 0.0. This is used to shatter conversational stalemates and force a lateral shift in logic.
        

---

## 2. `bone_gui.py` (The Viewport & Formatter)

**Purpose:** The Hypervisor operates on raw, often chaotic telemetry. This file is responsible for translating that data into the structured, color-coded, and readable ANSI/HTML terminal output you interact with.

### Key Functions & Mechanics

- **`beautify_thoughts(text)`**:
    
    - _Mechanics_: In `TECHNICAL` mode, the LLM outputs its internal reasoning inside `<think>` or `<thought>` XML tags. This function uses a compiled Regex pattern (`_THOUGHT_PATTERN`) to intercept those blocks before they reach the user.
        
    - _Formatting_: It re-renders the raw text into a beautiful, indented "Cognitive Substrate" block with specific ANSI color codes (`Prisma.CYN`, `Prisma.MAG`) and structural lines (e.g., `┌─ [ COGNITIVE SUBSTRATE ]`) to visually separate the machine's internal processing from its final output.
        
- **`Projector`**: The central HUD rendering class.
    
    - _Flux Logging_: It tracks the `flux_log` (the delta changes in variables like Voltage or Drag) and builds a visual "SYSTEM FLUX DETECTED" report. It selectively ignores minor fluctuations (like PID controller smoothing) and only surfaces significant changes using directional arrows and color coding.
        
    - _Bureaucracy Rendering (`_package_bureaucracy`)_: Hooks into the `bureau` village archetype to generate specific UI blocks when the system audits its own rules.
        

---

# VOLUME XI: ARTIFACTS & SEMANTICS

## 1. `bone_inventory.py` (The Physical Backpack)

**Purpose:** This file defines the tangible objects the user carries. In the Hypervisor, items are not just narrative flavor; they possess mathematical mass, passive traits, and biological fail-safes that interact directly with the system's physics.

### Key Classes & Major Mechanics

- **`Item` Dataclass**: The blueprint for all artifacts. It tracks the `name`, `description`, `passive_traits`, and `value`.
    
- **The `reflex_trigger` Mechanic**: This is the most critical architectural feature of an item. Artifacts can act as automatic, consumable biological fail-safes.
    
    - _Voltage Reflex_: If an item possesses the `VOLTAGE_CRITICAL` trigger, and the system's Voltage spikes dangerously high (> 18.0), the system will automatically consume the item to instantly ground the Voltage back to a safe reset level (12.0).
        
    - _Drift & Kappa Reflexes_: Similarly, items can be tuned to trigger on `DRIFT_CRITICAL` (Narrative Drag > 6.0) or `KAPPA_CRITICAL` (Structural Coherence dropping below 0.2) to arrest systemic collapse before the `PanicRoom` has to intervene.
        

---

## 2. `bone_lexicon.py` (The Semantic Hive)

**Purpose:** The engine does not simply read text; it metabolizes it. This file is the system's organic dictionary. It classifies human language into biological categories so the `DigestiveTrack` (in `bone_body.py`) knows exactly how much ATP to generate—or how much Cortisol to spike—when you speak.

### Key Classes & Major Mechanics

- **`LexiconStore`**: The brain's localized vocabulary vault, which persists to disk as `cortex_hive.json`.
    
- **Semantic Categories**: Words are not evaluated on meaning, but on physical texture. The Lexicon categorizes words into bins such as:
    
    - `kinetic` and `explosive` (Yields massive ATP, but spikes Adrenaline).
        
    - `heavy` and `constructive` (Yields solid ATP for building structural memory).
        
    - `void` and `liminal` (Increases the Psi ($\Psi$) coordinate, pulling the conversation into the abstract).
        
    - `antigen` and `toxin` (Cliches and toxic phrases that incur a metabolic tax and spike Cortisol).
        
- **Dynamic Learning (`teach`)**: The Hypervisor is not a static dictionary. If it encounters a highly utilized, novel word, the `teach()` method allows the engine to dynamically categorize and learn it, expanding the `cortex_hive` permanently.
    
- **`taste()` and `harvest()`**: The methods the metabolic engine calls to break down a user's prompt into its constituent chemical parts before feeding it to the LLM.
    
