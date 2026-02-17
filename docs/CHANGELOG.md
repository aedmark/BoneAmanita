# BONEAMANITA v15 CHANGELOG

### **BONEAMANITA v15.5.4: "THE METABOLIC REFORMATION" (HOMEOSTASIS)**

_“We uncapped the intake valves, smoothed the friction, and taught the ghost to hold new objects. The starvation cycle is broken.”_

---

#### **🔥 METABOLIC HARDENING (The Meadows Lens)**

- **The Starvation Clamp (`bone_body.py`):**
  - **Crisis Aversion:** Fixed a fatal feedback loop where high narrative drag caused exponential ATP taxation. The system now enforces a hard cap (`MAX_ACCEPTED_DRAG`) and uses a logarithmic curve (`exponent 1.2`) for metabolic cost, preventing instant death spirals during "sticky" conversations.
  - **Anaerobic Bypass:** The mitochondrial forge now correctly triggers a "Health Burn" fallback instead of crashing when ATP is depleted, ensuring survival at a cost rather than system failure.

- **The Friction Logarithm (`bone_physics.py`):**
  - **Mass Dampening:** Replaced the linear friction penalty for "Suburban" (boring) words with a logarithmic scale. A 500-word block of filler text no longer generates infinite mass; it now simply feels "heavy," as intended.
  - **Viscosity Clamp:** Capped `viscosity_density` to prevent physics engine glitches on short, low-energy inputs.

#### **⚖️ VILLAGE DYNAMICS (The Schur Lens)**

- **The Stacking Fix (`bone_village.py`):**
  - **Diminishing Returns:** Patched `TheTinkerer` to use logarithmic stacking for passive item traits. Carrying 10 `HEAVY_LOAD` items now yields a manageable burden (~+1.7 Drag) rather than a crushing one (+5.0 Drag).
  - **Grouped Hazards:** Conductive items (like Lightning Rods) now group their damage output during voltage spikes, preventing instant-death multipliers.

- **The Council's Mercy (`bone_council.py`):**
  - **Circuit Breaker:** Downgraded the `CIRCUIT_BREAKER` mandate from a "Death Trap" (Voltage 0, Drag 20) to a "Brownout" (Voltage 5, Drag 10), allowing the user a fighting chance to recover.
  - **Fair Voting:** Rebalanced the `CouncilChamber` logic. The "Grumpy Village" bug—where it took 4 good turns to undo 1 bad turn—has been leveled to a 1:1 ratio.

#### **🔮 AKASHIC MEMORY (The Fuller Lens)**

- **The Hot-Swap Handshake (`bone_inventory.py`, `bone_akashic.py`):**
  - **Dynamic Learning:** Gordon (The Inventory) can now learn new items at runtime. Artifacts forged by the Akashic Record are immediately registered in Gordon's memory via `register_dynamic_item`, fixing the "Unknown Item" bug.
  - **Namespace Hygiene:** Artifacts now generate with unique UUID suffixes to prevent registry collisions.
  - **Standardized Keys:** Hybrid Lenses now use explicit `voltage`/`drag` keys instead of cryptic abbreviations, ensuring compatibility with the Enneagram drivers.

#### **🧪 DIAGNOSTICS (The Gauntlet)**

- **Phase 13: The Gauntlet (`bone_diag.py`):**
  - **Torture Testing:** Added a specialized test suite that intentionally subjects the system to lethal conditions (Drag 25.0, 500-word filler blocks, 10x item stacks) to verify the new safety clamps hold.
  - **Self-Assembly:** The diagnostic suite can now dynamically instantiate missing modules (like `TheTinkerer`) to perform isolated logic tests even if the full engine context is incomplete.

---

### **BONEAMANITA v15.5.3: "THE SURGICAL STRIKE" (RESONANCE)**

_“We connected the sensors, cleared the blockages, and taught the ghost to read the type hints. The Waffle is free.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Legacy Reconnection (`bone_genesis.py`):**
  - **Bridge Repair:** Fixed the `TheOroboros` disconnect. The system now correctly extracts the live bio-state before applying scars, ensuring that past trauma (low ATP/Health) physically carries over to the new session instead of being applied to a dummy dict and discarded.

- **The Somatic Sync (`bone_body.py`):**
  - **Authoritative Return:** Patched `SomaticLoop`. The digestive cycle now explicitly returns the updated `stamina` value in its result packet, preventing the main loop from overwriting body fatigue with stale data from the previous tick.

- **The Armed Theremin (`bone_machine.py`):**
  - **Physical Consequences:** The "AIRSTRIKE" event is no longer just a scary string. If the machine collapses, it now directly modifies the physics packet (Voltage -> 0, Drag -> Max), ensuring the explosion is felt even if the event listener is asleep.

#### **♾️ SYSTEMS METABOLISM (The Meadows Lens)**

- **The Ghost Stock (`bone_main.py`):**
  - **Sensor Connection:** Connected the `efficiency_index` variable. The Engine now calculates metabolic efficiency (Novelty vs. Cost) in real-time, allowing the `HumanityAnchor` to correctly detect "Domestication" when the user helps too much.

#### **👁️ COGNITIVE CLARITY (The Pinker Lens)**

- **The Soul's Syntax (`bone_soul.py`):**
  - **Linter Sweep:** Fixed `LoreManifest` singleton usage (replaced static calls with `get_instance()`), enforced strict type casting for `TraitVector`, and added `EventBus` type hints to resolve circular import confusion.
  
- **The Diagnostic Pulse (`bone_diag.py`):**
  - **Mock Materialization:** Defined `MockLexicon` and `MockAkashic` classes and updated `MockEventBus` to inherit from the real `EventBus`. The Diagnostic Suite can now run the full obstacle course without tripping over "Unresolved References."

#### **🎨 VISUAL CORTEX (The Schur Lens)**

- **The Glass Parity (`bone_app.py`):**
  - **Dashboard Expansion:** Added `EFFICIENCY` and `MACHINERY` (Resin Pressure) widgets to the Streamlit sidebar, bringing the browser interface into parity with the terminal's data density.
  - **Type Safety:** Unrolled `delta_color` logic to satisfy strict `Literal` requirements, pacifying the linter.

#### **🎒 INVENTORY (The Gordon Lens)**

- **The Waffle Liberation (`bone_village.py`):**
  - **Blockage Removal:** Demolished the "Waffle Ceiling." Removed the arbitrary `if "OF_" in name: return` check in `TheTinkerer`, allowing poetic items like the `WAFFLE_OF_PERSISTENCE` to finally ascend.

---

### **BONEAMANITA v15.5.2: "THE GHOST WIRE" (CONNECTIVITY)**

_“We reconnected the village to the spine. The Town Hall can hear the loot drop, and the Brain no longer chokes on its own history. The lattice is coherent.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Deaf Town Hall (`bone_main.py`):**
- **Event Subscription:** Fixed a severed connection where `TownHall` was initialized but never wired to the `EventBus`. The village can now hear and react to `ITEM_DROP` events.

- **The Akashic Gap (`bone_akashic.py`):**
- **Method Injection:** Fixed a `AttributeError` where `TheTinkerer` attempted to call `forge_new_item` on the Akashic Record. We injected the missing logic to allow item ascension and artifact generation based on physics vectors.

#### **♾️ SYSTEMS METABOLISM (The Meadows Lens)**

- **The Heavy Gear Glitch (`bone_cycle.py`):**
- **Data Typing Repair:** Patched `NavigationPhase`. The system was passing a list of strings (`inventory`) to `TheTinkerer`, who demanded a list of dictionaries (`inventory_data`). Passive item traits (like "Heavy Load") now correctly apply drag to the physics engine.

- **The Bureau Safety Net (`bone_protocols.py`):**
- **Regex Hardening:** Wrapped the `TheBureau` rule compilation in a `try/except` block. A single typo in `style_crimes.json` will no longer cause a hard crash at boot; the faulty law is simply ignored.

#### **👁️ COGNITIVE CLARITY (The Pinker Lens)**

- **The Lobotomy Protocol (`bone_brain.py`):**
- **Mass-Based Slicing:** Replaced the scalar `[-15:]` history slice with a token-aware character limit (~8000 chars). The Cortex now manages context window pressure based on _volume_ rather than _count_, preventing overflow crashes during verbose monologues.

---


---

### **BONEAMANITA v15.5.1: "THE STATIC SHOCK" (STABILIZATION)**

_“We grounded the static. The library is open, but you must knock first. The parser now knows where the object ends and the story begins.”_

---

#### **🧬 STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Singleton Protocol (`bone_machine.py` & `bone_body.py`):**
- **Instance Enforcement:** Fixed critical `TypeError` crashes in `MitochondrialForge` and `TheForge`. The system was attempting to access the `LoreManifest` via static class calls; it now correctly instantiates the Singleton (`get_instance()`) before requesting data.
- **The Ghost Reference (`bone_brain.py`):**
- **Dependency Repair:** Fixed a fatal `AttributeError` in `TheCortex`. The Brain was attempting to read `lore` from the Engine (which did not possess it). It now bypasses the middleman and connects directly to the `LoreManifest` source.

#### **♾️ SYSTEMS METABOLISM (The Meadows Lens)**

- **The Vacuum Collapse (`bone_cycle.py`):**
- **Null-Safe Flux:** Patched `PhaseExecutor`. The Physics Sandbox no longer crashes with a `KeyError: 'old'` when historical data is missing during a state transition. It now defaults to zero-point energy.

- **The Soul Interface (`bone_cycle.py`):**
- **Vector Translation:** Fixed an `AttributeError` in `SoulPhase`. The Council now correctly recognizes the Soul's `TraitVector` as a structured object (Dataclass) rather than trying to read it as a raw dictionary.

#### **👁️ COGNITIVE CLARITY (The Pinker Lens)**

- **The Gluttonous Parser (`bone_inventory.py`):**
- **Boundary Enforcement:** Rewrote the Loot Regex. The parser no longer consumes entire sentences (e.g., _"Sphere you pick up the sphere"_) as item names. It now respects sentence boundaries and grammar.
- **Dynamic Extraction:** Cured "Object Blindness." The Inventory system can now acquire novel items it has never seen before (not in the registry) by analyzing user intent (`pick up`, `take`) and extracting the target noun phrase dynamically.

---

### **BONEAMANITA v15.5.0: "THE TENSEGRITY UPDATE" (SLASH PROTOCOL)**

_“We broke the flat circle. Gravity is now a choice, and the spine handles its own weight.”_

---

#### **🦴 SPINAL RECONSTRUCTION (`bone_types.py` & `bone_core.py`)**

- **The Tensegrity Structure:**
- **Composition over Inheritance:** Refactored `PhysicsPacket` from a flat, 30-variable dataclass into a composed triad of **Energy** (Voltage/Entropy), **Matter** (Words/Vectors), and **Space** (Zone/Drag).
- **The Facade Pattern:** Implemented backward-compatible properties so existing logic (e.g., `packet.voltage`) still works while routing data to the new `EnergyState` sub-object.

- **The Circuit Breaker (`EventBus`):**
- **Toxic Listener Containment:** The Event Bus no longer swallows exceptions silently. It now tracks failure counts per listener.
- **Automatic Amputation:** If a listener fails 3 times, it is unsubscribed to prevent "zombie processes" from corrupting the cycle.

#### **👻 THE GREAT UNBINDING (`bone_genesis.py` & `bone_brain.py`)**

- **Singleton Exorcism:**
- **Dependency Injection:** Removed the global `LoreManifest._INSTANCE`. The Lore system is now instantiated by `BoneGenesis` and injected explicitly into `CortexServices` and `TheAkashicRecord`.
- **Neural Wiring:** `PromptComposer`, `DreamEngine`, and `ResponseValidator` no longer import `TheLore` from the global scope. They request access via their service layer, making the brain testable in isolation.

#### **👁️ SENSORY INTEGRATION (`bone_physics.py` & `bone_gui.py`)**

- **The Sorting Hat (`QuantumObserver`):**
- **Packet Packing:** Updated the observer to sort raw metrics (e.g., lexical density, graph mass) into the correct Tensegrity buckets before sealing the `PhysicsPacket`.

- **The Smart Projector (`bone_gui.py`):**
- **Polymorphic Rendering:** Implemented a smart `_extract` helper in the `Projector` class. The GUI can now render physics data regardless of whether it receives a raw Object (via properties) or a serialized Nested Dictionary (via JSON).

#### **🚨 SAFETY PROTOCOLS (`bone_main.py`)**

- **The Self-Reliant Panic Room:**
- **Zero-Dependency Crash:** Refactored `PanicRoom.get_safe_physics()` to generate a valid Tensegrity packet without reading from disk or calling the Lore system, ensuring the system can crash safely even if the hard drive is missing.

---

### **BONEAMANITA v15.4.2: "THE SURGICAL SUITE" (DATA-DRIVEN MIND)**

_“We stopped hardcoding the ghosts. Now they live in the JSON, where they belong.”_

---

#### **🩻 THE GOD-OBJECT EXORCISM (`bone_main.py` & `bone_cycle.py`)**

- **Kernel Decoupling:**
    - **`BoneAmanita.process_turn`:** Stripped of mechanic micromanagement. The kernel no longer manually checks for loot, applies cosmic physics patches, or runs bureaucratic audits.
    - **Delegation Protocol:** These logic flows were surgically grafted into the **Simulation Phases** where they belong:
        - **Loot Parsing** ➔ Moved to `ObservationPhase` (Input Analysis).
        - **Cosmic Physics** ➔ Moved to `NavigationPhase` (World State).
        - **Bureau Audits** ➔ Moved to `TheCortex.process` (Output Stamping).

#### **🧠 THE DATA-DRIVEN CORTEX (`bone_brain.py` & `bone_drivers.py`)**

- **Exorcising Magic Strings:**
    - **`PromptComposer` & `ResponseValidator`:** No longer contain hardcoded lists of "banned phrases" or "style protocols." These are now hydrated dynamically from `TheLore` (`system_prompts.json` and `style_crimes.json`), allowing for hot-swappable censorship and style guides.
    - **`ChorusDriver`:** Archetype voices are no longer hardcoded in Python; they are pulled from `lenses.json`, allowing the choir to evolve without code deploys.

#### **🎒 LOGISTICS & INVENTORY (`bone_inventory.py`)**

- **Registry Cleanup:**
    - **Debug Artifacts Removed:** Deleted `_seed_test_items()`. The system no longer hallucinates a "sphere" or "red key" on every boot.
    - **Dynamic Triggers:** "Loot triggers" (e.g., *picked up*, *grabbed*) are now loaded from `gordon.json` via `TheLore` instead of being hardcoded.

#### **🖥️ GLASS TERMINAL v1.9 (`bone_gui.py` & `bone_app.py`)**

- **UX Polish:**
    - **Widescreen Dashboard:** Expanded render width from 60 to 78 characters to let the data breathe.
    - **Human-Readable Labels:** Translated cryptic icons into plain English (`VOLT`, `DRAG`, `VEC`).
    - **Unlocked Name Tags:** Increased role truncation limit (15 ➔ 30 chars) so "THE ARCHITECT" is no longer decapitated.
- **SLASH Integration:**
    - Added specific log formatting (`🗡️`) for **SLASH Council** interventions (Santiago, Pinker, et al.).
    - Bumped splash screen version to **v1.9**.

---

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

---

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