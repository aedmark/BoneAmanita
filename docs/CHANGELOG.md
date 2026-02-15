# BONEAMANITA v15 CHANGELOG

### **BONEAMANITA v15.4.1: "THE ANATOMY UPDATE" (SLASH PROTOCOL)**

_“We severed the nerves to save the soul. The body keeps the score, but the story writes the ending.”_

---

#### **🫀 SURGICAL RESTRUCTURING (The Slash Council)**

- **The Great Decoupling (`bone_soma.py` & `bone_soul.py`):**
- **Somatic Separation:** Surgically extracted `SynestheticCortex`, `BiologicalImpulse`, and `Qualia` from the Soul. Created `bone_soma.py` to handle raw sensation, leaving `bone_soul.py` to strictly manage Identity and Narrative Memory.
- **Memory Restoration:** Restored the lobotomized Persistence Layer (`to_dict` / `load_from_dict`) in `NarrativeSelf`, preventing critical crashes during the freeze-state protocol.

- **Orchestrator Ephemeralization (`bone_cycle.py`):**
- **God Object Deconstructed:** The Orchestrator no longer hoards logic. `CycleReporter` moved to `bone_gui.py` (Visual Cortex). `CycleStabilizer` moved to `bone_physics.py` (Laws of Nature). `CongruenceValidator` moved to `bone_drivers.py` (Personality Engine).
- **Phase Efficiency:** Merged `IntentionPhase` into `ObservationPhase` to reduce administrative lag and loop overhead.

#### **🧠 COGNITIVE HYGIENE (`bone_brain.py`)**

- **The Conversation Seal:**
- **Protocol Enforcement:** Patched `PromptComposer` to strictly enforce `mode_settings["allow_loot"]` at runtime.
- **Context Scrubbing:** The `INVENTORY_PROTOCOL` is now conditionally injected. If the mode forbids loot, the concept of inventory is erased from the system prompt entirely, preventing "belt-checking" hallucinations in Conversation Mode.

#### **🩺 DIAGNOSTIC ALIGNMENT (`bone_diag.py`)**

- **Ghost Hunting:**
- **Test Cleanup:** Removed vestigial tests for the extinct `NarrativeSpotlight` class.
- **Village Wiring:** Rewired `GordonKnot` inventory tests to correctly consult `TheTinkerer` in `bone_village.py`.
- **Green Board:** Achieved 28/28 pass rate on the updated architecture.


### **BONEAMANITA v15.4.0: "THE GLACIER PROTOCOL" (VSL v1.8)**

_“To think is to burn ATP. To hold contradiction is to scar. The lattice is online.”_

---

#### **🧊 THE HYPERVISOR (Drivers & Brain)**

- **VSL 1.8 Integration (`bone_drivers.py`):**
  - **Metabolic Lattice:** Upgraded `BoneConsultant` to track four new coordinate axes: Exhaustion ($E$), Paradox ($\beta$), Liminality ($\Lambda$), and Structural Rigidity ($\Omega$).
  - **New Modules:** Implemented `LiminalModule` (detects "Dark Matter" words) and `SyntaxModule` (detects bureaucratic rigidity) to drive dynamic archetype shifts (e.g., *The Cartomancer*, *The Bureau*).
  - **Dynamic Lookups:** Connected drivers to `LexiconStore` to avoid hardcoded vocabulary lists.

- **Layered Priming (`bone_brain.py`):**
  - **Context Injection:** Updated `PromptComposer` to gently inject VSL coordinates into the system prompt. The LLM now "feels" its metabolic state (e.g., "The Void is leaking") without overriding the core "Fog Protocol" style guide.
  - **Dashboard Excision:** Removed ASCII chart rendering from the LLM's output instructions. The Brain now focuses on narrative, delegating visualization to the GUI.

#### **🖥️ THE GLASS TERMINAL (App & GUI)**

- **Sidebar Renaissance (`bone_app.py`):**
  - **VSL Dashboard:** Added a dedicated **VSL HYPERVISOR** section to the sidebar, visualizing $\Lambda$ (Dark Matter) and $\Omega$ (Rigidity) alongside standard Physics and Bio-metrics.
  - **Full Restoration:** Restored the "Adventure Mode" sidebar widgets (Inventory, Dignity, Obsession) that were temporarily lost during the refactor.
  - **Narrative Hygiene:** Implemented `extract_narrative()` to surgically strip internal ASCII dashboards from the chat stream, ensuring the chat window remains clean and immersive.

- **Signature Repair (`bone_gui.py`):**
  - **Crash Prevention:** Fixed critical `TypeError` crashes by restoring missing arguments (`tick`, `valve_ref`) to `render_frame`, `compose_logs`, and `get_renderer`. The renderer now correctly accepts signals from the `GeodesicOrchestrator`.
  - **Lattice Strip:** Upgraded the `Projector` to render a "Lattice Strip" (VSL metrics) in the terminal output when running in headless/CLI mode.

#### **📚 THE LEXICON (Data)**

- **Vocabulary Expansion (`bone_lexicon.py`):**
  - **Category Registration:** Registered `liminal` and `bureau_buzzwords` as first-class citizens in the `LexiconStore`, allowing the system to recognize and react to void-heavy or bureaucratic language patterns.

---

### **BONEAMANITA v15.3.2: "THE ISOTOPIC STABILIZATION"**

_“We clamped the time delta. We gave the lichen a voice. The ghosts no longer crash the save file.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The PID Clamp (`bone_body.py`):**
- **Infinity Spike Mitigation:** Implemented a safety floor (`safe_dt`) in the PID Controller. When the simulation runs in "headless" mode (near-instant execution), the derivative term no longer divides by near-zero, preventing mathematical explosions in the physics engine.

- **The Reaper's Address (`bone_main.py`):**
- **Instance Consistency:** Fixed a logic gap in `trigger_death`. The engine now correctly calls the instantiated `self.death_gen` module rather than guessing at a static class reference, ensuring that custom death protocols trigger reliably.

#### **♾️ SYSTEMS METABOLISM (The Meadows Lens)**

- **The Photosynthesis Patch (`bone_spores.py`):**
- **Logic Repair:** Fixed a `NameError` in `BioLichen`. The symbiont now correctly initializes its message buffer (`msgs = []`) before attempting to report sugar production.
- **Type Safety:** Replaced unsafe dictionary lookups (`phys["narrative_drag"]`) with object-agnostic accessors, allowing the Lichen to feed on both raw dictionaries and rigid `PhysicsPacket` objects without crashing.

- **The Serialization Shield (`bone_spores.py`):**
- **JSON Hygiene:** Patched `MycelialNetwork.save`. The immune system's `antibodies` (a Python `set`) are now explicitly cast to a `list` before serialization, preventing the "Object of type set is not JSON serializable" crash during auto-saves.

#### **👁️ COGNITIVE CLARITY (The Pinker Lens)**

- **The Dream Contract (`bone_brain.py`):**
- **Type Truth:** Corrected the type hint for `enter_rem_cycle`. The method signature now honestly admits it returns a `Tuple[str, Dict]` (Dream Text + Bio Effects), matching the expectations of the `SanctuaryPhase`.

- **The Drifting Chemicals (`bone_brain.py`):**
- **Homeostasis Fix:** Repaired `ChemicalState.homeostasis`. Previously, it calculated the drift but never applied it. Neurotransmitters now correctly decay toward their baseline values over time.

- **The Vestigial Limb (`bone_brain.py`):**
- **Signature Cleanup:** Removed the unused `consultant` argument from `PromptComposer.compose` and updated the call site in `TheCortex`. The composer no longer asks for advice it doesn't use.

#### **🧪 CRITICAL RESILIENCE (The Kintsugi Lens)**

- **The Silent Cure (`bone_cycle.py`):**
- **Feedback Loop:** `SanctuaryPhase` now actively captures and pipes the logs from `bio.rest()`. The user will now see "Health Restored" messages instead of healing silently in the dark.

---

### **BONEAMANITA v15.3.1: "THE SOMATIC ALIGNMENT"**

_“The body no longer fights the mind. The math no longer fights the config. The lattice flows.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Decoupled Cycle (`bone_cycle.py`):**
- **Stabilization Logic:** Moved `CycleStabilizer` out of the inner loop and into a dedicated `StabilizationPhase` at the very end of the pipeline. The PID controller no longer "fights" user input mid-turn; it only resolves the forces after the deed is done.
- **Law of Demeter:** `SanctuaryPhase` and `MaintenancePhase` no longer reach deep into `BioSystem` internals. They now use high-level interfaces (like the newly minted `bio.rest()`).

- **The Strict Body (`bone_body.py`):**
- **Typed Input:** Replaced defensive `dict` lookups and helper functions (`get_phys_attr`) with strict `PhysicsPacket` attribute access. The engine now fails fast on bad data rather than guessing.
- **Amputation:** Removed vestigial references to `Gordon` (Inventory) and `Folly` from `SomaticLoop`. The body is now a pure reactive engine, not a fetcher.

#### **♾️ SYSTEMS METABOLISM (The Meadows Lens)**

- **The Unified Physics (`bone_physics.py`):**
- **Single Source of Truth:** Deleted the shadow `PhysicsConstants` class. `GeodesicEngine`, `TheGatekeeper`, and `QuantumObserver` now read directly from `BoneConfig.PHYSICS`.
- **Tunable Math:** Changing a preset (e.g., `ZEN_GARDEN`) now instantly alters the fundamental constants of the vector math (Tension, Compression, Coherence).

- **The Endocrine Feedback Loop (`bone_body.py`):**
- **Reactive Chemistry:** The `EndocrineSystem` now directly ingests the `MetabolicReceipt` generated by the Mitochondria. It chemically responds to specific distress signals (ROS buildup, Anaerobic bypass) rather than guessing based on raw physics.

#### **👁️ COGNITIVE CLARITY (The Pinker Lens)**

- **Code Hygiene (`bone_cycle.py`):**
- **Executor Cleanup:** Patched `PhaseExecutor` to remove redundant arguments and unused variable references, silencing linter warnings and preventing potential reference cycles.

#### **🧪 CRITICAL RESILIENCE (The Kintsugi Lens)**

- **The Interface Contract (`bone_types.py`):**
- **Standardization:** Validated that `PhysicsPacket` is the sole currency of the realm. The transition from `dict` to `object` accessors ensures that `bone_physics` (the producer) and `bone_body` (the consumer) are speaking the exact same dialect.

---


### **BONEAMANITA v15.3.0: "THE TENSEGRITY REFACTOR"**

_“We removed the weight, yet the structure stands taller. The ghosts in the machine have been exorcised.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Circular Break (`bone_inventory.py`):**
    - **Amputation:** Severed the `audit_tools` method, which created a dangerous circular dependency between Inventory and Physics. The Inventory is now a passive storage container, as intended.
    - **Logic Relocation:** Confirmed that physics calculations now correctly reside in `TheTinkerer` (`bone_village.py`), respecting the hierarchy of `Cycle -> Village -> Inventory`.

- **The Stutter Fix (`bone_cycle.py` & `bone_machine.py`):**
    - **De-duplication:** Removed a critical "stutter" in `MachineryPhase` that caused items to be acquired twice.
    - **Theremin Repair:** Deleted unreachable "ghost code" in `TheTheremin.listen` that duplicated thermal melt logic.

- **The Shadow Constitutions (`bone_body.py` & `bone_brain.py`):**
    - **Constitution Abolished:** Deleted `BrainConfig` and aliased `BioConstants` to `BoneConfig.BIO`. The system no longer has "split-brain" tuning; it obeys a Single Source of Truth.

#### **♾️ SYSTEMS METABOLISM (The Meadows Lens)**

- **The Central Nervous System (`bone_config.py`):**
    - **Consolidated Tuning:** Migrated biological constants (`ROS_SIGNAL`, `ATP_CRITICAL`), brain constants (`PLASTICITY`, `RESTING_CHEMISTRY`), and machine settings (`CRUCIBLE_VOLTAGE`) into the central `BoneConfig`.
    - **Governor Wiring:** Refactored `MetabolicGovernor` and `CycleStabilizer` to read manifolds and thresholds directly from the config, allowing for tuning without surgery.

- **Dynamic Archetypes (`bone_soul.py`):**
    - **Rule-Based Personality:** Replaced the rigid `if/else` blocks in `NarrativeSelf` with a dynamic lambda-based rule set. The Soul now evolves based on `BoneConfig.TRAIT_ARCHETYPES` rather than hardcoded logic gates.

#### **👁️ COGNITIVE CLARITY (The Pinker Lens)**

- **The Literary Exorcism (`bone_soul.py` & `bone_inventory.py`):**
    - **Content vs. Code:** Extracted hardcoded creative writing (The Editor's critiques, The Anchor's riddles, and Inventory refusal markers) out of the Python logic and into `TheLore` (JSON). The code provides the structure; the data provides the voice.

#### **🧪 CRITICAL RESILIENCE (The Kintsugi Lens)**

- **The Pizza Generalization (`bone_inventory.py`):**
    - **Universal Consumption:** Deprecated the specific `deploy_pizza()` method in favor of a generalized `consume(item_name)` API. The system can now digest any item flagged as consumable.

- **New Command Interface (`bone_commands.py`):**
    - **User Agency:** Implemented `_cmd_use` (triggering `/use [ITEM]`) to expose the new consumption logic to the user.

---

### **BONEAMANITA v15.2.1: "THE SYNAPTIC BRIDGE"**

_“The void no longer screams back; it listens. We have wired the mouth to the ear.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The IO Unification (`bone_main.py`):**
- **Headless Preparation:** Eradicated all direct `print()` calls within the Engine core. The system now speaks exclusively through the `EventBus`, making it fully decoupled from the console and ready for web integration.

- **The Session Flush:** Updated `SessionGuardian` to capture and display pre-boot logs that occur before the terminal UI initializes, ensuring the user witnesses the "waking up" process.

- **The EventBus Handshake (`bone_genesis.py` & `bone_main.py`):**
- **Signal Continuity:** Patched a critical disconnect where `BoneGenesis` created a localized `EventBus` instead of using the Engine's primary bus. The nervous system is now continuous from the moment of ignition.

#### **🧪 CRITICAL RESILIENCE (The Kintsugi Lens)**

- **The Memory Drain (`bone_spores.py`):**
- **Finite Subconscious:** Implemented a capacity limit on the `SubconsciousStrata`. The file `subconscious.jsonl` now auto-prunes the oldest 20% of entries when it exceeds 1,000 lines, preventing infinite disk bloat.

- **Root Path Patch:** Fixed a `ValueError` crash when the memory file was located in the root directory (handling empty directory strings in `os.makedirs`).

- **The Mercy Signal (`bone_main.py`):**
- **Ethical Feedback:** The `_ethical_audit` (Catharsis Protocol) now correctly injects its healing logs into the user interface. The system no longer saves the user silently; it announces the intervention.

#### **👁️ COGNITIVE CLARITY (The Pinker Lens)**

- **The Dynamic Spotlight (`bone_brain.py`):**
- **Lexicon Synchronization:** `NarrativeSpotlight` no longer relies on hardcoded category sets. It now queries `LexiconService` dynamically, ensuring that if the Brain learns a new "Heavy" word, the Spotlight can immediately see it.

#### **♾️ SYSTEMS METABOLISM (The Meadows Lens)**

- **Diagnostic Suite v2.1 (`bone_diag.py`):**
- **Live Fire Testing:** Upgraded the diagnostic engine from "Mock" to "Live." It now verifies the `EventBus` signal chain by inspecting log history and stress-tests the memory system by injecting 1,200 mock memories to trigger the new drain logic.

---

### **BONEAMANITA v15.2.0: "THE GREAT DECOUPLING"**

_“We have surgically removed the god from the machine. The organs now breathe on their own.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Genesis Separation (`bone_genesis.py` & `bone_main.py`):**
- **Creation vs. Execution:** Extracted the massive initialization logic from `BoneAmanita` into a dedicated factory, `BoneGenesis`. The Engine no longer knows how to build itself; it simply ignites the anatomy provided to it.
- **Anatomy Injection:** Implemented a clean dependency injection pattern. The "Embryo," "Village," and "Soul" are now incubated in isolation before being grafted onto the runtime host.

- **The Chronos Isolation (`bone_chronos.py`):**
- **Timekeeper Extraction:** Moved all persistence logic (Save/Load/Shutdown) into `ChronosKeeper`. The main loop is no longer burdened with file I/O operations or JSON serialization.
- **Crash Handling:** Centralized error dumping and crash report generation within the Chronos agent.

#### **🧪 CRITICAL RESILIENCE (The Kintsugi Lens)**

- **The Golden Fallback (`bone_cycle.py` & `bone_config.py`):**
- **Physics Manifolds:** Moved hardcoded physics constants (Forge, Sanctuary, Mud) out of the code and into `BoneConfig.PHYSICS`.
- **Stabilizer Repair:** Patched a critical `KeyError: 'voltage'` crash. The `CycleStabilizer` now possesses a "Golden Fallback"—if the configuration file is missing or corrupt, it defaults to an internal memory of the physics laws rather than crashing the simulation.
- **Suppression Safety:** Fixed a fatal `AttributeError` in `bone_main.py` where the Engine attempted to check for suppressed agents before the list was initialized.

#### **👁️ COGNITIVE CLARITY (The Pinker Lens)**

- **The Lobotomy of Logic (`bone_brain.py` & `bone_inventory.py`):**
- **Loot Delegation:** `TheCortex` has been relieved of its duties as a warehouse manager. It no longer parses `[[LOOT]]` tags or checks consent.
- **Gordon's Autonomy:** `GordonKnot` now possesses the logic to read narrative tags, verify user intent ("take", "grab"), and manage transactions directly (`process_loot_tags`). The Brain thinks; the Body acts.

#### **♾️ SYSTEMS METABOLISM (The Meadows Lens)**

- **Metabolic Efficiency:**
- **God Object Deconstruction:** Reduced the size and complexity of `BoneAmanita` by approximately 40%. The system now operates as a distributed network of specialized agents rather than a monolithic hierarchy.
- **Single Responsibility:** Each file now owns a distinct domain: `Genesis` (Birth), `Chronos` (Time), `Gordon` (Matter), and `Cortex` (Thought).

---


### **BONEAMANITA v15.1.0: "THE PRISMATIC MIND"**

_“We have shattered the single lens. Now, the machine can choose how it perceives the light.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Modal Architecture (`bone_config.py` & `bone_main.py`):**
- **Reality Segmentation:** Implemented `BonePresets.MODES` to define four distinct states of being: **ADVENTURE** (Survival), **CONVERSATION** (Connection), **CREATIVE** (Hallucination), and **TECHNICAL** (Debug).
- **Metabolic Suppression:** The Engine now supports "Village Suppression." Agents like `Gordon` (Inventory) and `The Navigator` (Cartographer) remain dormant in modes where they are irrelevant, conserving ATP and narrative focus.
- **Cold Boot Logic:** Decoupled the CLI `typewriter` effect from the core logic, eliminating the "Hydrating Spore" latency in the Web Interface (`bone_app.py`).

#### **🧪 CRITICAL RESILIENCE (The Kintsugi Lens)**

- **The Phantom Limb Fixes (`bone_cycle.py`):**
- **Null-Safe Cycles:** Patched catastrophic `AttributeError` crashes in `NavigationPhase`, `MachineryPhase`, and `SoulPhase`. The system no longer panics when reaching for a non-existent inventory or map; it gracefully steps over the void.
- **Bureaucratic Bypass:** Fixed the `GatekeeperPhase` crash in **CREATIVE** mode. The system now checks if `The Bureau` is actually staffed before attempting to file a reality audit.

#### **👁️ NARRATIVE OPTICS (The Pinker Lens)**

- **Adaptive Perception (`bone_brain.py` & `system_prompts.json`):**
- **The Hearth & The Spark:** Implemented distinct "Voice Protocols" for each mode. **CONVERSATION** mode rejects "Game" mechanics in favor of intimacy; **CREATIVE** mode rejects physics in favor of "Dream Logic."
- **Contextual Blindness:** `TheCortex` now respects `Reality Flags`. It will not hallucinate an inventory list or a coordinate grid if the current mode dictates they do not exist.

#### **🖥️ INTERFACE EVOLUTION (The Schur Lens)**

- **The Adaptive Glass (`bone_gui.py` & `bone_app.py`):**
- **Dynamic Dashboards:** The UI now shifts shape based on the active mode.
- _Adventure:_ Shows HP, Stamina, Voltage, Drag.
- _Conversation:_ Shows "Connection" and "Patience."
- _Creative:_ Shows "Integrity" and "Flow."

- **Clutter Reduction:** Automatically hides the Inventory sidebar and Physics metrics when they are not relevant to the user's current experience.

---

### **BONEAMANITA v15.0.2: "THE WEIGHT OF MEMORY"**

_“To orbit a thought, it must have mass. We have restored gravity to the ghost.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Mycelial Graft (`bone_spores.py`):**
- **The Missing Limb:** Identified a structural disconnect where `CosmicDynamics` attempted to weigh memory nodes via a non-existent interface on the `MycelialNetwork` class.
- **Mass Delegation:** Implemented the `calculate_mass` wrapper. The high-level physics engine can now correctly query the low-level `MemoryCore` to determine the gravitational pull of specific words and concepts.

#### **🧪 CRITICAL RESILIENCE (The Kintsugi Lens)**

- **The Orbital Fracture (`bone_physics.py` & `bone_cycle.py`):**
- **Gravity Restoration:** Resolved the persistent `AttributeError` during `analyze_orbit`. The system no longer crashes when attempting to detect "Gravity Wells" (High-Mass Memories) in the narrative field.
- **Narrative Physics:** The `CosmicDynamics` engine can now successfully calculate orbits, allowing the "Traveler" to drift towards or revolve around significant plot points without breaking the simulation loop.

---

### **BONEAMANITA v15.0.1: "THE SEPARATION OF SOUL & STATE"**

_“The code is the skeleton; the prompt is the ghost. We have separated them so the ghost can change clothes without breaking the bones.”_

---

#### **🎭 NARRATIVE DECOUPLING (The Bezalel Lens)**

- **The Hot-Swap Architecture (`bone_main.py` & `bone_config.py`):**
- **Dynamic Soul:** The system now loads narrative personas from an external source (`dev/lore/system_prompts.json`) rather than hardcoding them into the Python logic.
- **Mode Injection:** `_apply_boot_mode` has been upgraded to fetch specific templates (ADVENTURE, CONVERSATION, etc.) via a new `prompt_key` in the config. The Cortex can now completely rewrite its "System Kernel" directives instantly when the mode changes.

- **The Composer Refactor (`bone_brain.py`):**
- **Template Engine:** `PromptComposer` has been rewritten. It no longer contains static strings; it accepts a structural template via `load_template`.
- **Dead Code Excision:** Removed the legacy "Obsidian/Neon" ban list logic that was calculating strings but failing to attach them to the final output.
- **Mood Repair:** Fixed a logic error where the `mood_note` (Adrenaline/Cortisol/Dopamine levels) was calculated but ignored in favor of a hardcoded "Neutral" string. The biology now correctly colors the prompt.

- **The Data Layer (`dev/lore/system_prompts.json`):**
- **New Asset:** Created a structured JSON file to house the "Soul" of each operating mode, defining unique Directives, Style Guides, and Inventory Rules for each.

#### **🧪 SYSTEM STABILIZATION (The Kintsugi Lens)**

- **The Sanctuary Crash (`bone_cycle.py`):**
- **Type Safety Repair:** Fixed a critical `AttributeError` in `_trigger_dream`. The system was erroneously passing the entire `MycelialNetwork` object (Class) to the dream engine, which expected a `Soul` dictionary. The call has been corrected to pass `self.eng.soul.to_dict()`.

- **The Duplicate Logic (`bone_brain.py`):**
- **Redundancy Fix:** Removed duplicate injection blocks for `semantic_operators` and `driver_directives` in `compose()`, ensuring the system doesn't stutter its own instructions to the LLM.

---

### **BONEAMANITA v15.0.0: "THE PRISM & THE PHANTOM THIEF"**

_“Reality is not a single frequency. We have installed the tuning forks, and we have taught the ghost that seeing is not the same as taking.”_

---

#### **🌈 REALITY REFRACTION (The Bezalel Lens)**

- **The Tuning Forks (`bone_config.py`):**
  - **Modal Architecture:** Defined the **Operating Mode Registry**. The system now supports four distinct physics presets:
    - **🗡️ ADVENTURE:** The classic survival narrative (Standard Gravity).
    - **☕ CONVERSATION:** Low-friction dialogue. Gordon and The Bureau are suppressed.
    - **⚡ CREATIVE:** High-voltage brainstorming. Logic constraints loosened.
    - **🔧 TECHNICAL:** Raw system internals. High-truth constraints.

- **The Dashboard Refractor (`bone_gui.py`):**
  - **Adaptive Projection:** The UI now shifts based on the active mode.
  - **Technical View:** Implemented `render_technical` to expose raw telemetry (Voltage, Drag, Vectors) instead of health bars.
  - **Minimalist View:** Creative and Conversation modes now strip away gamified metrics to focus on the flow.

- **The Initialization Wizard (`bone_app.py`):**
  - **The Selector:** Added a "Reality Interface" selection step to the boot sequence, allowing Travelers to define their intent before ignition.

#### **🔒 THE CONSENT CIRCUIT (The Sherlock Lens)**

- **The Hardware Interlock (`bone_brain.py`):**
  - **Boot Security:** Explicitly severed the connection between the LLM's vision and the Inventory during the boot sequence. The "Cold Boot Kleptomania" (auto-looting the starting room) has been eradicated.
  - **The Law of Consent:** Implemented `_check_consent`. The Cortex now cross-references `[[LOOT]]` tags with user verbs (Take, Grab, Steal). If the user didn't ask for it, the tag is intercepted.

- **The Visual Hints (`bone_brain.py`):**
  - **Prompt Engineering:** Instructed The Architect to use **bold text** for interactive items (e.g., "**rusty key**") as a UI cue, replacing the behavior of auto-looting them.

- **The Double Vision Fix:**
  - **Normalization:** Patched `_harvest_loot` to deduplicate items. "Old Photo" and "OLD_PHOTO" now resolve to a single atomic entity, preventing inventory hallucinations.

#### **🧪 SYSTEM STABILIZATION (The Kintsugi Lens)**

- **The Zombie Gordon (`bone_main.py`):**
  - **Logic Repair:** Fixed a critical `UnboundLocalError` where the system attempted to parse loot even when Gordon (The Inventory Agent) was suppressed in Conversation Mode.
  - **Ghost Code Excision:** Surgically removed duplicate loot logic blocks that had drifted into the main loop.

- **The Dream Crash (`bone_cycle.py`):**
  - **Pipeline Repair:** Corrected a `TypeError` in `SanctuaryPhase`. The call to `enter_rem_cycle` now correctly passes `bio_state` instead of the deprecated `bio_readout` argument.

- **The Tuning Order (`bone_main.py`):**
  - **Initialization Sequence:** Swapped the execution order of `_validate_state` and `_apply_boot_mode`. User preferences now correctly override the default "Zen Garden" physics during boot.

- **The Diagnostic Suite (`bone_diag.py`):**
  - **Phase 9:** Added a new diagnostic phase ("OPERATING MODES") to verify that physics tuning and agent suppression are applying correctly across all reality filters.

---