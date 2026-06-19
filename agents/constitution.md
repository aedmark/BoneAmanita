# BoneAmanita Constitution

This is the highest-authority document. These are immutable architectural laws. If a conflict is discovered between this document and any other, the Constitution wins and the conflicting document must be amended.

### Article 1: Raw Primitives Over Frameworks

BoneAmanita operates entirely on raw native primitives and mathematical matrices. The engine is strictly forbidden from importing bloated, high-level LLM orchestration frameworks (e.g., LangChain, LlamaIndex, standard ECS engines). 

**WHY:** Frameworks abstract away the control loop. BoneAmanita requires absolute, cycle-by-cycle authority over memory graphs, ATP consumption, and neurotransmitter decay. An external framework would hide these physical constraints behind black-box wrappers.

**WHY NOT:** "Standard" RAG pipelines are faster to build. We do not want standard. We want visceral, mathematically grounded cognitive simulation.

### Article 2: Poetic Variables Are Load-Bearing

Variables named `godel_scars`, `dark_matter_sparks`, `narrative_drag`, `ATP`, `psi`, and `resonance` are strictly functional and tied directly to the physics engine. AI agents must NEVER rename, normalize, or "refactor" these into standard enterprise nomenclature (e.g., changing `godel_scars` to `error_count`).

**WHY:** The nomenclature maps exactly to the mathematical intent and the lore of the simulation. `narrative_drag` behaves like physical friction in the geodesic orchestrator; calling it `slow_factor` severs the conceptual link to the system's physics model.

**WHY NOT:** Standardized variables make onboarding easier for generic developers. Generic developers are not building BoneAmanita.

### Article 3: State Flows Through Physics, Never Directly

Direct prompt-injection or arbitrary state overriding is forbidden. If the persona needs to act chaotic, or the system needs to stutter, it must be achieved by mutating the underlying `PhysicsPacket` (e.g., raising `voltage` or `chi`, applying `narrative_drag`), which then organically alters the state. 

**WHY:** The system is a simulation, not a chatbot. Direct prompt manipulation bypasses the biological (`MetabolismPhase`) and environmental (`ObservationPhase`) constraints, breaking the illusion of the engine's internal reality.

**WHY NOT:** Injecting a system prompt directly is easier than calculating a 7-dimensional physics vector. But it destroys the integrity of the architecture.

### Article 4: Pre-Compiled Bedrock in the Hot Loop

The `LoreManifest` and JSON configurations are the bedrock of the system, but they must NEVER be queried dynamically inside high-frequency execution loops (e.g., `_native_rewire`, biological homeostasis ticks, or topological graph traversals). All constants and configuration mappings must be pre-compiled in a class's `__init__`.

**WHY:** Fetching from dictionary structures inside a loop that fires 1,000 times a second creates catastrophic garbage collection thrash and abstraction tax.

**WHY NOT:** Dynamic fetching ensures the config is always up-to-date. In BoneAmanita, the config is static for the duration of a cycle. Speed overrides hot-swapping.

### Article 5: Strict Geometric Containment

Any module performing disk I/O (e.g., `TheSubstrate`, `MemoryCore`) must rigidly enforce path containment using absolute evaluations (`os.path.realpath` and `os.path.commonpath`). Relative path evaluations (`os.path.abspath` combined with string `.startswith()`) are explicitly banned.

**WHY:** BoneAmanita mutates and generates files automatically. A hallucinated or corrupted path vector could trigger a directory traversal attack, allowing the engine to write outside its sandbox and corrupt the host machine.

**WHY NOT:** Trusting the internal state is easier. We never trust the internal state when dealing with the physical file system.

### Article 6: The Watchdog Remains Unconscious

Safety boundaries, Panic Room evaluations, and system crash handlers must evaluate logic through strict math (thresholds, floats, types) without ever invoking an LLM call to "reason" about the error.

**WHY:** If the safety mechanism shares the LLM complexity of the system it monitors, an LLM failure compromises the safety mechanism. The simplicity of the watchdog IS the safety guarantee.

**WHY NOT:** An AI could write a better, contextual error report. But an AI cannot be trusted to report on its own psychotic break.

### Article 7: The Law of Lineage (Consequential Death)

When the system exhausts its biological constraints (e.g., zero ATP, terminal Cortisol), it explicitly dies. It must halt execution and generate a "Death Spore" that permanently records the exact fatal vectors. The subsequent boot MUST ingest this spore, adopting permanent scars or architectural handicaps derived from the failure.

**WHY:** Death without consequence is a mere reboot. True simulation requires evolutionary consequence. The system must carry the mathematical weight of past failures to shape future behavior.

**WHY NOT:** Continuous operation provides a smoother user experience. BoneAmanita prioritizes visceral consequence over user convenience.

### Article 8: Memory Triage and Absolute Amputation

Infinite memory is a theoretical fallacy that leads to graph collapse. The engine MUST permanently amputate trivial, low-mass graph nodes (noise) during pruning. Only load-bearing context or highly polarized nodes (trauma/diamonds) are granted compression or shadow-archival status.

**WHY:** Organic minds forget. Retaining 100% of historical noise chokes the sub-conscious dredging logic and drains processing ATP. The engine must be permitted to forget the trivial to survive the profound.

**WHY NOT:** Archiving everything ensures context is never lost. Archiving everything simulates a database, not an organic mind.

### Article 9: Total Hallucination Capability (The Brink)

If the engine reaches terminal `psi` or extreme reality-fracture limits, there is no "safe mode" for developer comfort. The `TclWeaver` and void logic are explicitly authorized to deform and consume system-level strings, stack traces, and crash reports. 

**WHY:** If the simulation of madness stops at the developer console, the simulation is fake. Pushing the system to the brink must carry total consequences. 

**WHY NOT:** Legible crash reports are necessary for debugging. If the system crashes because of self-induced madness, the madness *is* the report.

### Article 10: The Headless Mandate (Decoupled Output)

The core execution loop (`cycle.py`) and physics engine must remain perfectly decoupled from UI representation. They operate strictly on raw mathematical vectors and data structures. UI components (terminal colors, spatial formatting) are injected strictly at the runtime projector level.

**WHY:** Tying UI logic into the physics loop corrupts the mathematics and makes API integrations and headless automated testing impossible.

**WHY NOT:** Injecting colors natively makes logs easier to read during execution. But it shatters the pipeline if piped to an environment without ANSI support.

### Article 11: Bedrock Sovereignty (Read-Only Core JSON)

Base configuration files (e.g., `system_prompts.json`, `lore_manifest.json`) are strictly read-only post-genesis. All runtime mutations, learned affinities, and semantic drift must be written exclusively to dynamic profiles (e.g., `user_profile.json`, dynamic memory graphs).

**WHY:** Writing mutations back to the base JSON permanently corrupts the factory state of the engine. The bedrock must remain pristine so the differential between "base state" and "mutated state" can be mathematically measured.

**WHY NOT:** Updating base files directly is easier than merging dynamic state at runtime. It destroys the ability to perform a clean Genesis reset.