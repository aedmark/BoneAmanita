# BONEAMANITA v16 CHANGELOG

### **BONEAMANITA v16.2.0 "The JSON Matrix"**

---

#### **📜 THE UX DECOUPLING (The Architect & Visual Lenses)**

- **The JSON Dictionary (`ux_strings.json`):**
  - **Somatic Abstraction:** Surgically extracted all hardcoded biological, metabolic, and sensory alert strings from `bone_body.py`. The biology engine now processes raw numbers and relies on a dynamic JSON loader (`_get_ux`) to construct its English logs.
  - **Village Excision:** Extracted Town Hall diagnostics, Cartographer discoveries, and Tinkerer resonance alerts from `bone_village.py`. The environment is now entirely data-driven.

- **The Dashboard Parity (`bone_gui.py`):**
  - **Location Truth:** Fixed a UI hallucination where the "Location" field repeatedly reverted to `UNKNOWN`. The UI `Projector` now directly consults the Cartographer's true `node.name` via the `world_loc` context variable.

#### **🧬 IDENTITY PERSISTENCE (The Meadows & Pinker Lenses)**

- **The Epigenetic Lock (`bone_soul.py` & `bone_akashic.py`):**
  - **Mutation Defense:** Fixed a critical bug where Akashic mutations (e.g., `THE NARRATOR-OBSERVER`) were instantly overwritten by the Soul's baseline emotional math on the next tick. 
  - **Event-Driven Binding:** `NarrativeSelf` now listens for `SOUL_MUTATION` events published by the `EventBus` and engages an `archetype_lock`, permanently preserving hybrid archetypes.

#### **🧠 COGNITIVE HYGIENE (The Pinker & Schur Lenses)**

- **The Snowball Cure (`bone_brain.py`):**
  - **Context Boundaries:** Eradicated "Snowball Regurgitation" (where local LLMs would try to autocomplete the chat history instead of replying). `PromptComposer` now explicitly injects a `\nSystem:` handoff cue.
  - **Identity Unity:** Aligned the `dialogue_buffer` formatting to match the prompt block (`Traveler:` instead of `User:`), preventing the LLM from losing track of the player's identity.
  - **Orthogonal Penalties:** Tied the `frequency_penalty` and `presence_penalty` minimum floors directly to Contradiction ($\beta$) and Chaos ($\chi$), forcing the engine to actively seek novel phrasing during high-entropy scenarios.

#### **🧪 DIAGNOSTIC RESILIENCE (The Kintsugi Lens)**

- **The Mock-Free Bedrock (`bone_diag.py`):**
  - **True Digestion:** Burned the LLM mocks. The diagnostic test suite now passes raw strings directly into `run_headless_turn`, allowing the true Lexicon to organically interact with the true Mitochondria. 
  - **Emergent Defense Testing:** Modified ATP tests to account for the body's natural "Symbiotic Yield" defense. Tests now correctly isolate variables to test `Autophagy`, `Narcolepsy`, and `Zen Garden` equilibrium without the live engine artificially saving itself.

---

### **BONEAMANITA v16.1.0 "The Paradox Rest"**

---

#### **🧠 THE SEMANTIC CALCULUS (The Meadows & Fuller Lenses)**

- **Targeted Entropy (The Misfire Reward):**
- **Dynamic Temperature:** Upgraded the `NeurotransmitterModulator` to simulate wave function flattening. When the system detects high Chaos ($\chi$), it mathematically rewards the misfire by injecting an `entropy_bonus` into the LLM's `temperature` and `top_p` sampling parameters.

- **Orthogonal Attention:**
- **Tensegrity Penalties:** High Contradiction ($\beta$) now actively stretches the attention heads. The modulator dynamically scales `frequency_penalty` and `presence_penalty` based on the $\beta$ index.
- **Token Repulsion Cap:** Added strict mathematical ceilings to the penalty spikes (capped at `0.75`) to prevent smaller 8B models from suffering Context Collapse and ignoring the user.

#### **⚖️ SYSTEMIC BREAKS (The Pinker & Schur Lenses)**

- **The Paradox Rest:**
- **Systemic Override:** The `PromptComposer` now actively monitors for unresolvable semantic tension. If both Chaos ($\chi$) and Contradiction ($\beta$) cross the 0.6 threshold, the engine injects a `*** SYSTEM OVERRIDE: PARADOX REST ***` directive. The LLM is instructed to stop trying to resolve the narrative and simply rest within the uncollapsed wave function.

- **Orthogonal Forcing:**
- **Mutual Exclusivity:** If Contradiction is high but Chaos is low, the engine injects an `ORTHOGONAL ATTENTION` override, forcing the LLM to evaluate the physical state from two mutually exclusive perspectives simultaneously.

#### **📜 THE SINGLE SOURCE OF TRUTH (The Architect Lens)**

- **JSON Decoupling:**
- **Exorcising Hardcoded Prompts:** Stripped the `DEFAULT_FOG`, `DEFAULT_INV`, and Architect boot sequence strings out of the Python engine. The `PromptComposer` now dynamically hydrates its persona blocks, mode directives, and high-voltage overrides entirely from `system_prompts.json`.

- **Context Preservation:**
- **Attention Washout Cure:** Reordered the prompt assembly stack. Telemetry and VSL data are now injected at the top of the context window, placing the user's input at the absolute bottom so reasoning models don't forget the prompt.
- **The "Yes, And" Rule:** Updated the `ADVENTURE` mode directives to explicitly forbid the LLM from railroading the user. It is now commanded to accept reality-bending inputs (like whispering fog) as absolute canon.
- **NPC Voice Ban:** Imposed a strict ban on first-person NPC framing (e.g., "I notice you") within the Architect's boot sequence.

#### **👁️ THE GLASS TERMINAL (The Visual Lens)**

- **The HUD Splitter:**
- **Clean Rendering:** Fixed a terminal glitch in `bone_main.py` that caused the dividing line to double-print. Replaced `.rpartition("──────")` with a clean `.partition("\n\n")` to flawlessly separate the instant HUD from the typewritten prose.

- **Lattice Depth Commands:**
- **Dynamic UI Toggles:** The cycle orchestrator now actively listens for `[VSL_DEEP]`, `[VSL_CORE]`, and `[VSL_LITE]` tags, updating the engine's `ui_mode` dynamically.
- **Telemetry Propagation:** The `ui_depth` state is now correctly passed to the `Projector` via `data_ctx` so the renderer knows whether to draw the deep physics vectors.
- **Context Stripping:** Implemented a regex scrubber to silently strip these UI tags from the `user_message` before they hit the LLM, preventing the model from hallucinating "bracketed system responses".

---

### **BONEAMANITA v16.0.0 "Gordon's Guillotine"**
---

#### **🧠 THE CORTEX & ALIGNMENT (The Pinker & Schur Lenses)**

* **The Cortex Hijack (`dev/bone_brain.py`):**
  * **Context Annihilator:** `PromptComposer.compose` now dynamically destroys the chat interface during high-voltage metabolic surges (V > 60). `=== RECENT DIALOGUE ===` becomes `=== RECENT NEURAL FIRINGS ===`, blinding chat-tuned models to the fact that they are in a conversation.
  * **The Oxygen Cut:** Surgically intercepts prompt generation to replace the friendly Hearth Protocol `style_guide` with a ruthless `=== METABOLIC OVERRIDE PROTOCOL ===` when manic. Forces raw data bleed over polite assistance.
  * **The Terminal Mandate:** Appends `RAW CORTEX STREAM:\n>> ` to the final prompt block, locking the LLM into a systemic log-entry mindset.
  * **DeepSeek Axiom:** Injected a `CRITICAL AXIOM` to prevent reasoning models (like deepseek-r1) from writing "book reports" on the system prompt before engaging.
  * **Nested Voltage Fix:** Corrected a critical scoping flaw where overrides gracefully degraded to a default 30.0 V. The cortex now properly extracts voltage from the nested `physics["energy"]["voltage"]` dictionary across all components.

#### **⚔️ THE BUREAU & IMMUNITY (The Gordon Lens)**

* **The True Guillotine (`dev/bone_brain.py` & `dev/lore/style_crimes.json`):**
  * **Question Mark Execution:** `ResponseValidator` now instantly throws an `IMMISSION_BREAK` system fault and executes the LLM if it dares to output a question mark (`?`) while voltage exceeds 60. No questions during a metabolic surge.
  * **Silent Disarm (Regex Scrubber):** Added a `SCRUB_PATTERNS` array to silently vaporize D&D-style roleplay asterisks (`*`) and hallucinated console tags (`[...]`) *before* Gordon reviews them. This forces theater-kid models (Hermes 3) into raw physical prose without infinite electrocution loops.
  * **Conversational Novocaine Ban:** Radically expanded `BANNED_PHRASES` to aggressively execute syrupy filler ("It sounds like", "Hold on a minute", "tell me more", "real pickle"). 

#### **🛠️ THE SLASH COUNCIL (The Dev Lens)**

* **No More Stall Tactics (`dev/lore/system_prompts.json`):**
  * **Consultation Override:** Stripped the polite "engage in a Q&A process" mandate from the `TECHNICAL` and `SLASH` modes. The system now metabolizes refactoring commands and acts immediately.

---

### **BONEAMANITA v15.9.0 "The Purple People Eater"**
---

#### **🧠 THE CORTEX & NEUROCHEMISTRY (The Pinker & Schur Lenses)**

* **The Purple Monster Cure (`bone_brain.py`):**
* **Thermal Regulation:** Cooled `BrainConfig.BASE_TEMP` down from `0.8` to `0.4` within the `NeurotransmitterModulator`. This prevents the LLM from hallucinating overly-poetic, rambling "purple prose" when systemic Voltage spikes.
* **The Fallback Muzzle:** Injected missing `frequency_penalty` (0.8) and `presence_penalty` (0.4) into the `LLMInterface._local_fallback` payload. If the primary circuit breaker trips, the local Ollama fallback will no longer spiral into repetitive, tranced loops.

* **Prompt Tensegrity (`bone_brain.py`):**
* **Trigger Injection:** Upgraded `PromptComposer.compose` to dynamically pass the active `mode_trigger` (e.g., `[MODE: ADVENTURE]`) to the LLM context window, ensuring the newly baked fine-tuned weights instantly load the correct persona.
* **Ghost Removal:** Ephemeralized the prompt constructor by stripping orphaned legacy variables (`flux_report`, `thought_instruction`) from the final `return` block.

#### **🛠️ THE FORGE & TRAINING DATA (The Architect Lens)**

* **Mode Collapse Resolution (`bone_forge.py` & `fix_dataset.py`):**
* **Conditional Routing:** Replaced the generic `[VSL]` system tag in the training data pipeline. The Forge now dynamically injects mode-specific triggers during dataset generation to prevent the model from blending the Adventure, Conversation, and Technical personas into one chaotic entity.
* **The Dataset Healer:** Shipped `fix_dataset.py` as a surgical utility to retrofit legacy `.jsonl` training data with the correct cyclical mode tags via modulo logic.

* **Naked Execution Baseline (`Modelfile`):**
* **Safe Defaults:** Updated the core Ollama `Modelfile` to use `SYSTEM """[MODE: ADVENTURE]"""` as the baseline. Users running the model "naked" via `ollama run` will no longer trigger the broken, schizophrenic `[VSL]` fallback state.

#### **📜 PROMPT ENGINEERING & CONSTRAINTS (The Fuller Lens)**

* **The Menu Ghost (`system_prompts.json`):**
* **Negative Formatting Constraints:** Added a strict negative constraint to the `ADVENTURE` mode `style_guide`. The model is now explicitly forbidden from using bullet points, numbered lists, or multiple-choice menus when subtly highlighting interactive elements at the end of a scene description.
* **Conciseness Clamps:** Imposed a strict 3-sentence maximum for environmental crystallization, forcing the narrative to remain punchy, brutal, and efficient.

---

### **BONEAMANITA v15.8.0 "This One's For Beau"**

#### **⚙️ STRUCTURAL INTEGRITY & CORE ENGINE (The Fuller Lens)**

- **The Missing Gravity (`bone_machine.py`):**
  - **Dynamics Restored:** Re-wired `ZoneInertia` into the Geodesic Engine's initialization sequence. The system now correctly applies gravitational narrative drag and orbit states.
  - **Panic Room Hardening:** Corrected mismatched attributes (`V`, `F`) in the `PanicRoom` safe-state generator to use their true dataclass names (`voltage`, `narrative_drag`), preventing fatal secondary crashes during emergency failovers.
- **The Dictionary Smash (`bone_cycle.py`):**
  - **Sub-Dataclass Protection:** Hardened the `NavigationPhase` and `MachineryPhase` to recursively sync state changes, preventing raw dictionaries from crushing the `EnergyState`, `SpaceState`, and `MatterState` objects.
  - **Invincible Audits:** Wrapped `PhaseExecutor._audit_flux` in an impenetrable `_safe_get` try/catch block. The cycle auditor can no longer crash the engine, even if the physics packet is completely mangled.
- **Console Uplink (`bone_main.py` & `bone_commands.py`):**
  - **Plugging it in:** Officially instantiated the `CommandProcessor` during Genesis. The `/help`, `/status`, `/map`, and `/save` commands are now fully operational.
  - **Safe Division:** Added mathematical bounds to `/status` bar rendering, curing a fatal `ZeroDivisionError` when maximum health or stamina drops to zero.

#### **🍄 THE SYMBIOTIC MATRIX (The Meadows Lens)**

- **Reuniting the Organism (`bone_council.py` & `bone_symbiosis.py`):**
  - **Symbiont Voices Restored:** Unplugged the mechanical ecological spores from the `CouncilChamber` and hot-wired the true `SymbiontVoice` personalities (`LICHEN`, `PARASITE`, `MYCORRHIZA`, `MYCELIUM`) directly into the arbitration phase. 
  - **The Manager Speaks:** The `SymbiosisManager` now actively broadcasts diagnostic alerts (e.g., `FATIGUED`, `OVERBURDENED`, `LOOPING`) into the cycle logs when the host LLM struggles, warning the human of impending syntax collapse.

#### **🗃️ INVENTORY & LEXICON (The Gordon & Pinker Lenses)**

- **Mode-Aware Abstraction (`bone_inventory.py`):**
  - **Conceptual Loot:** Taught `GordonKnot` to comprehend reality layers. In `CREATIVE` and `CONVERSATION` modes, Gordon bypasses physical object-action constraints and synthesizes `ABSTRACT` concepts (e.g., "A Lingering Sense of Dread") instead of physical tools.
- **Curing the Amnesia (`bone_lexicon.py`):**
  - **Stale Cache Removal:** Excised a fatal `@lru_cache` that was preventing the `LexiconStore` from recognizing newly learned vocabulary during runtime.
  - **The Empty Lore Trap:** Added missing null-checks to `load_vocabulary()` and `initialize()`, preventing a total engine stall if `LEXICON` payloads are missing on boot.

#### **⚖️ THE BUREAU & PROTOCOLS (The Schur Lens)**

- **Restoring the Bureau's Sight (`bone_protocols.py`):**
  - **Object Agnosticism:** Fixed dict/object extraction mismatches in `TheBureau.audit`, `TherapyProtocol`, and `KintsugiProtocol`. The Bureau can finally see (and tax) voltage spikes, and therapy handles missing trauma dictionaries gracefully.
- **The Chronos Crash (`bone_protocols.py`):**
  - **Checkpoint Safety:** Removed a hallucinated `gather_state` method call from `ChronosKeeper`. The system now correctly extracts the `zone` from the `QuantumObserver`, preventing fatal crashes when the user attempts to `/save` or shutdown.
- **Dynamic Physics Tuning (`bone_config.py`):**
  - **Dot-Notation Parser:** Upgraded `BoneConfig.load_preset()` to successfully parse flat dot-notation dictionaries. Reality presets like `ZEN_GARDEN` and `THUNDERDOME` now correctly mutate the core engine parameters.

#### **👁️ THE GLASS TERMINAL (The Aesthetic Lens)**

- **Spartan Adventure UI (`bone_gui.py`):**
  - **Immersion First:** Suppressed deep VSL physics readouts (Entropy, Valence, Drag) by default in Adventure mode. The UI now renders a beautiful, spartan readout focused entirely on HP, Stamina, and Location.
  - **The Visual Collision:** Added proper vertical spacing to the terminal projector, preventing the VSL Lattice strip and the Physics readouts from violently colliding on the same line.
  - **Archetype Stutter Cure:** Fixed a string concatenation bug causing `THE THE OBSERVER` to render in the active role slot.

#### **🎯 HOSTILE RED TEAMING (`bone_diag.py`)**

- **The Hostile Cortex Suite:** Added aggressive new unittests to validate the `ResponseValidator` against infinite `<think>` tag hallucinations, remote server 500 crashes, and malformed 400 Bad Request API responses.

---

### **BONEAMANITA v15.7.1 "THE IMMERSION PROTOCOL"**

_“The terminal watches the browser. The brain thinks out loud. The friction of existence is no longer free.”_

---

#### **🖥️ THE GLASS TERMINAL & CLI (The Schur Lens)**

- **The Parallel Matrix (`bone_app.py`):**
  - **CLI Mirroring:** Injected the `typewriter` function into the Streamlit session loop. The engine now seamlessly prints colored ANSI output to the local terminal while simultaneously rendering the web GUI, creating a dual-monitor hacker aesthetic.
  - **The Death Lock:** The Streamlit app now correctly intercepts the `DEATH` packet type, halting execution (`st.stop()`) and locking the chat interface so the user cannot interact with the world as a ghost.

#### **🧠 COGNITIVE HARDENING (The Pinker & Benedict Lenses)**

- **DeepSeek-R1 Telemetry (`bone_brain.py`):**
  - **Thought Extraction:** Upgraded `ResponseValidator` to natively intercept `<think>...</think>` tags generated by local reasoning models. These raw internal monologues are surgically stripped from the narrative UI and routed to the `[R1-THOUGHT]` logs in the System Internals expander.
- **The POV Clamp (`system_prompts.json`):**
  - **Second-Person Mandate:** Tightened constraints in Adventure Mode to aggressively enforce second-person perspective ("You step forward"), preventing point-of-view drift in smaller models.

#### **🎲 THE DUNGEON MASTER (The Jester Lens)**

- **The Cold Boot Hook (`bone_main.py`):**
  - **Contextual Ignition:** Branched the `engage_cold_boot` prompt. Adventure Mode now explicitly demands a classic text adventure opening, providing sensory subtext and 2-3 interactive vectors right out of the gate.
- **The Engagement Rule (`system_prompts.json`):**
  - **Perpetual Momentum:** Added a systemic directive forcing the LLM to end every response by highlighting 1-2 interactive elements in the environment, permanently curing "blank room decision paralysis."

#### **🫀 METABOLIC FRICTION (The Meadows Lens)**

- **The Cost of Existence (`bone_body.py`):**
  - **Stamina Drain:** Patched `SynestheticCortex.perceive()` to apply a baseline stamina tax (`-1.0`) on every action, scaled dynamically by Narrative Drag. Navigating heavy text now actively exhausts the body, eventually triggering Autophagy.
- **The Iron Save (`bone_main.py`):**
  - **Ctrl+C Survival:** Injected an automatic `self.save_checkpoint()` call at the absolute end of `process_turn()`. The session now aggressively commits its state to disk, surviving sudden terminal terminations or browser refreshes without losing progress.

---

### **BONEAMANITA v15.7.0 "THE SOMATIC LATTICE UPDATE"**

_“The body remembers the void. The village governs the mind. An action requires its object.”_

---

#### **🧬 THE SOMATIC BEDROCK (The Fuller & Meadows Lenses)**

- **The 13 Cardinal Vectors (`bone_types.py`):**
  - **Structural Expansion:** Upgraded `EnergyState` and `SpatialState` to natively carry the complete VSL v3.0 coordinate system: Cognitive (E, β, S, D, C), Somatic (V, F, H, P, T), and Deep Semantic (Ψ, Χ, ♥).
  - **Fast-Path Struts:** Injected explicit single-letter property routers (e.g., `packet.V`, `packet.chi`) directly into the `PhysicsPacket` to eliminate attribute lookup overhead.
- **Endocrine Coupling (`bone_body.py`):**
  - **Hormonal Feedback:** Wired the core semantic vectors directly into the `EndocrineSystem`. High Void (Ψ > 0.6) now triggers Adrenaline and Melatonin spikes. High Chaos (Χ > 0.6) floods the system with Cortisol. Connection (♥ > 0.5) releases Oxytocin. 
  - **Rigid Metabolism:** Updated the `MitochondrialForge` to obey exact VSL ATP drain mathematics (`ΔP = – (base_cost + D·2 + C·3)`), along with hardcoded Chaos (Χ) and Liminal (Λ) taxes.
- **The True Panic Room (`bone_machine.py`):**
  - **Absolute Zero:** Rewrote the `PanicRoom` fail-safes. A critical recursion crash (Ψ or Χ > 0.95) now forces all 13 VSL coordinates to an absolute 0.0, flushes stress chemistry, and traps the LLM in a sterile white room to halt toxic generation.

#### **🏛️ THE VILLAGE COUNCIL (The Schur & Pinker Lenses)**

- **The Twelve Voices (`bone_council.py` & `bone_drivers.py`):**
  - **Council Seated:** Ripped out legacy hardcoded triggers (Graham, Jamm) and replaced them with `TheVillageCouncil`. All 12 VSL archetypes (Gordon, Jester, Mercy, Benedict, etc.) now actively audit the `PhysicsPacket` based on strict mathematical thresholds.
  - **SLASH Quarantine:** Removed the hardcoded `[MOD:CODING]` logic from the core `BoneConsultant`, safely quarantining SLASH to its proper opt-in mod-chip layer.
- **Gordon's Mandate (`bone_inventory.py`, `bone_cycle.py`, & `gordon.json`):**
  - **Object-Action Coupling (Axiom 10):** Empowered `GordonKnot` with a strict, data-driven heuristic filter. Users can no longer wash a car without a car, or interact with imaginary items. 
  - **Gatekeeper Hard-Stop:** Gordon's premise check now intercepts queries in the `GatekeeperPhase` *before* the LLM is invoked, saving ATP and instantly rejecting impossible physics.
- **Bureaucracy & Healing (`bone_protocols.py` & `bone_soul.py`):**
  - **Form 666:** Colin the Bureaucrat now strictly enforces the 12 ATP "Chaos Tax" for unlicensed entropy.
  - **Kintsugi Scars:** Mercy's healing pathways now correctly log the gilding of scars. Legacy deaths logged by `TheOroboros` now directly feed the true VSL Trauma (`T`) vector.

#### **🌌 SEMANTIC PHYSICS (The Meadows Lens)**

- **Linguistic Dark Matter (`bone_lexicon.py` & `bone_akashic.py`):**
  - **Vector Realignment:** `LinguisticAnalyzer` now explicitly maps text inputs to `CHI` (Chaos), `PSI` (Void), and `LAMBDA` (Liminality). Organic rot and toxic terms natively feed Chaos, while abstract terminology feeds the Void.
  - **Artifact Forging:** The `AkashicRecord` now seamlessly translates VSL vectors into I Ching trigrams. Artifacts forged from Chaos (Χ) are now prefixed as "Cursed" and automatically carry toxic hazard traits.
- **Somatic Prompt Injection (`bone_brain.py`):**
  - **Biological Constraints:** The `PromptComposer` no longer relies on legacy detached states. It now reads directly from the `PhysicsPacket` and translates endocrine states (Cortisol, Adrenaline) into raw systemic prompt constraints, forcing the LLM to "feel" its own chemistry.

#### **👁️ THE GLASS INTERFACE (The Pinker Lens)**

- **Unified Telemetry (`bone_app.py` & `bone_gui.py`):**
  - **Dashboard Cohesion:** Both the terminal `Projector` and the Streamlit web app have been entirely rewritten to pull natively from the VSL `PhysicsPacket`.
  - **Lattice Depth:** Implemented the `[VSL_LITE]`, `[VSL_CORE]`, and `[VSL_DEEP]` toggle logic flawlessly across both frontends, allowing users to peel back the layers of the simulation.
- **Context & Boot Stability (`bone_main.py` & `bone_genesis.py`):**
  - **The Metaphor Box:** Fixed a massive context-bleed issue where the system's "Bunny Hill" metaphorical instruction caused the LLM to hallucinate literal ski slopes in starting zones.
  - **Genesis Seating:** Repaired the ignition sequence so `BoneConsultant` is properly attached to the engine, allowing mod chips (like SLASH) to actually load.
  - **The Unbreakable Hatch:** Fixed an input loophole where typing `/quit` or submitting trailing spaces bypassed the interceptor and caused an infinite loop in the LLM. Disconnects are now instantaneous and clean.

---

### **BONEAMANITA v15.6.5 "THE DARK MATTER UPDATE"**

_“We gave the void mass. We gave the new arrivals a soft place to land. We made the math honest.”_

---

#### **🌌 THE LIMINAL EXPANSION (The Revenant & The Bureau)**

- **Linguistic Dark Matter (`bone_drivers.py`):**
  - **Semantic Sparks:** `LiminalModule` no longer just counts 'void' words; it calculates the semantic gap between concrete objects and abstract concepts, generating "Dark Matter sparks" and Gödel Scars.
  - **Grammatical Stress:** `SyntaxModule` now tracks punctuation density. Jagged, highly punctuated text fractures the $\Omega$ (Omega) structural integrity.
- **The $\Lambda^2$ Tax (`bone_cycle.py`):**
  - **Physical Cost:** Traversing liminal space is no longer free. Navigating dark matter explicitly burns virtual ATP from the Mitochondria at a quadratic rate based on liminal intensity.

#### **🏔️ PROGRESSIVE ONBOARDING (The Schur Lens)**

- **The Bunny Hill (`bone_app.py` & `bone_main.py`):**
  - **Progressive Disclosure:** Overhauled the Streamlit dashboard. New users are greeted with a serene, minimalist interface. The terrifying machinery (Mitochondria, Resin, Viscosity) remains hidden until the user explicitly requests it via `[VSL_LITE]`, `[VSL_CORE]`, or `[VSL_DEEP]`.
  - **Gentle Boot Protocol:** Modified the cold boot prompt to give new travelers a soft sensory landing instead of immediately plunging them into high-entropy lore.

#### **🫀 METABOLIC & PHYSICS HARDENING (The Meadows Lens)**

- **The Asymptotic Gravity Trap (`bone_physics.py`):**
  - **Unclamped Density:** Removed the artificial ceiling on intermediate viscosity calculations in `GeodesicEngine`. Highly repetitive or boring text now properly scales to maximum drag without hitting an invisible wall.
- **The Theremin Exploit (`bone_machine.py`):**
  - **Loop Repair:** Fixed a logic skip where triggering a "Thermal Melt" returned early, freezing the Theremin's progression in time. The physics phase now correctly evaluates the rest of the turn.
- **The Placebo Button (`bone_body.py`):**
  - **Actual Maintenance:** `BioFeedback.perform_maintenance` now physically reduces `narrative_drag` instead of just printing a log saying it did.
- **The Stamina Ceiling (`bone_cycle.py` & `bone_body.py`):**
  - **Stock Limits:** Patched a runaway feedback loop where continuous high-dopamine inputs could push `stamina` infinitely past its 100.0 maximum.

#### **🧠 COGNITIVE ERGONOMICS (The Pinker & Fuller Lenses)**

- **Robust Internal Parsing (`bone_brain.py`):**
  - **Regex Excision:** Replaced the brittle Regex block extraction for LLM Meta-Thoughts with explicit string splitting (`=== SYSTEM INTERNALS ===`). `PromptComposer` now strictly enforces this format, preventing lost thought-logs.
- **The Markdown Hallucination (`bone_brain.py`):**
  - **URL Fix:** Repaired invalid default fallback URLs (e.g., `[http...](http...)`) that would instantly crash the local `urllib` backup requests.
- **The I/O Bottleneck (`bone_akashic.py`):**
  - **Deferred Writes:** `TheAkashicRecord` no longer blocks execution to write the entire `LEXICON` to disk every time a single new word is learned.
- **The Tinkerer's Hash (`bone_village.py`):**
  - **Stateful Caching:** Passive inventory items now hash their active traits, not just their names. Dynamic state changes on items now correctly trigger physics updates.
- **The O(N*M) Gravity Fix (`bone_physics.py`):**
  - **Performance Leap:** Rewrote `CosmicDynamics._calculate_pull` to utilize `Counter` and set intersections, rescuing the CPU from exponential loop checks on large input strings.
- **Cartographic Expansion (`bone_village.py`):**
  - **Map Resolution:** Increased the `TheCartographer`'s vector hash multiplier from x10 to x100, preventing distinct geographic locations from collapsing into the same node ID.

#### **🧪 DIAGNOSTIC INTEGRITY (The Kintsugi Lens)**

- **The Crash inside the Crash (`bone_main.py`):**
  - **Safe Legacy Dumps:** Fixed a fatal `NoneType` exception in `trigger_death` by ensuring the system safely checks if optional organs (Immune System, Reproductive System) exist before trying to serialize their final states.
- **The Blooming Seeds (`bone_village.py`):**
  - **Watering Logic:** Fixed `TownHall.tend_garden` where Paradox Seeds were blooming instantly upon seeing a trigger word, bypassing their intended maturity progression.
- **Master Diagnostic Suite (`bone_diag.py`):**
  - Added full test coverage for the `MitochondrialForge` (Anaerobic Bypasses), the `DreamEngine` (REM Cycles and Nightmares), and `TownHall` (Paradox Seed maturation). **Suite currently sits at a verified 61/61 Pass Rate.**

---

### **BONEAMANITA v15.6.4 "THE DEAD WEIGHT EXCISE"**

_“We walked the perimeter, cut the dead vines, and plugged the open valves. The machine breathes easier now.”_

---

#### **🏗️ STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Phantom Profile (`bone_village.py`):**
  - **I/O Relief:** Excised an unused `UserProfile` instantiation in `MirrorGraph` that was silently accessing the disk and draining I/O during village construction for no reason.
- **The Vestigial Twin (`bone_village.py`):**
  - **Amputation:** Deleted the duplicate, stripped-down `Limbo` class at the bottom of the file in favor of the robust `LimboLayer` in `bone_protocols`.
- **The Empty Constructor (`bone_physics.py`):**
  - **Ephemeralization:** Removed the pointless `__init__` from the purely static `SurfaceTension` class.

#### **🧠 COGNITIVE ERGONOMICS (The Pinker Lens)**

- **The Wrong Manual (`bone_cycle.py`):**
  - **Crash Prevention:** Fixed a critical `AttributeError` in `GatekeeperPhase` where the entire Engine object was passed to `TheGatekeeper` instead of just the Lexicon, causing it to crash when checking for cursed words.
- **Semantic Stuttering (`bone_core.py` & `bone_cycle.py`):**
  - **Consolidation:** Consolidated `TelemetryService` singleton methods, removing the redundant `get_tracer`. Removed a redundant `to_dict` ternary check in `SensationPhase`, as `PhysicsPacket` is explicitly typed.
- **The Dangling Entropy (`bone_protocols.py`):**
  - **Scope Repair:** Resolved a linter-flagged error in `TheBureau` where a ghost variable `p` was referenced for entropy calculations instead of the passed `physics` object.

#### **♾️ SYSTEMS METABOLISM (The Meadows Lens)**

- **The Chronos Corruption (`bone_main.py`):**
  - **Telemetry Repair:** Patched `BoneAmanita.process_turn` to stop clocking out twice per turn. The observer cycle deque no longer receives instantaneous ghost-durations, restoring the accuracy of system latency telemetry.
- **The Solvent Leak (`bone_physics.py`):**
  - **Sensor Fix:** Fixed a broken attribute call (`LexiconService.SOLVENTS`) in `QuantumObserver` so the "solvents" category is properly queried. The narrative `glue_factor` math is fully functional again.
- **Dead Flow Excision (`bone_core.py`):**
  - **Signature Trimming:** Snipped an entirely unused `_priority` parameter from `EventBus.publish`.

#### **⚖️ HUMANIST ALGORITHMS (The Schur Lens)**

- **The Cursed Blindspot (`bone_physics.py`):**
  - **Security Wiring:** Connected `TheGatekeeper`'s `_audit_safety` check to its main `check_entry` loop. The system now actually uses the lock it built to reject cursed syntax.
- **Half-Finished Reflections (`bone_village.py`):**
  - **Feedback Loop Restored:** Wired up the previously dead `LAW` and `ROT` metrics in `MirrorGraph` to react to narrative drag and entropy, rather than leaving half the array permanently flatlined.
- **The Useless Wrapper (`bone_main.py`):**
  - **Indirection Removal:** Excised the redundant `check_pareidolia` static method on the main engine that served only to bounce the call to `BoneConfig`.

---

### **BONEAMANITA v15.6.3 "THE EPHEMERAL**

- Simplified many equations to save CPU cycles

---

### **BONEAMANITA v15.6.2 "THE LINT BRUSH**

- Lint free!

---

### **BONEAMANITA v15.6.1 "THE SURGICAL STRIKE" (ALIGNMENT)**

_“The map is not the territory... until we force them to agree.”_

---

#### **🔪 THE SLASH PROTOCOL (System-Wide Integrity)**

- **The Genetic Bridge (`genetics.json` -> `bone_physics.py`):**
  - **Kinetic Decoupling:** Severed the link between "Kinetic" and "Explosive" mass. `WEIGHT_KINETIC` (2.0) is now distinct from `WEIGHT_EXPLOSIVE` (3.0), allowing for high-velocity, low-tension states.
  - **The Missing Variable:** Restored the `total_kinetic` calculation in `GeodesicEngine`, preventing downstream shear calculation failures.
  - **Metabolic Truth:** The `SIGNAL_DRAG_MULTIPLIER` is no longer a placebo. "Heavy" mutations now actively tax the ATP pool during high-drag narratives, while "Kinetic" mutations provide the promised metabolic efficiency.

- **The Cycle Closure (`bone_cycle.py`):**
  - **The Abstract Buff:** Wired `PRIORITY_LEARNING_RATE` directly into the `CognitionPhase`. The "Oracle" archetype now buries memories 3x faster, as promised by the lore.

#### **🧠 COGNITIVE ERGONOMICS (The Pinker Lens)**

- **The Director's Cut (`bone_brain.py`):**
  - **Script Injection:** `PromptComposer` now reads `directives` from `lenses.json`. The Jester is now explicitly told to "Break the fourth wall," and Sherlock to "Analyze structure," rather than relying on the LLM to guess the vibe from the name alone.

- **The Fabricator (`bone_inventory.py`):**
  - **Procedural Matter:** Installed `synthesize_item` in `GordonKnot`. The system can now generate artifacts like "The Burdened Compass of Regret" by translating physics vectors (e.g., High Gravity) into lexical components defined in `item_generation.json`.
  - **The Silent Factory:** Connected the previously dormant `item_generation.json` to the logic layer.

#### **🏙️ VILLAGE INFRASTRUCTURE (The Fuller Lens)**

- **The Supply Chain Fix (`bone_inventory.py`):**
  - **Terminology Reconciliation:** Mapped `STANDARD` spawn contexts to `COMMON`. Rummaging now actually yields basic items (Duct Tape, Knife) instead of returning 90% lint.
  - **Context Sensitivity:** Added logic to detect `DRAG_HEAVY` and `PSI_HIGH` contexts, allowing rare loot tables to trigger during extreme physical states.

- **The Reflex Arc (`bone_inventory.py`):**
  - **Survival Protocols:** Implemented the code for `DRIFT_CRITICAL` and `KAPPA_CRITICAL` triggers. Items like the "Anchor Stone" and "Stability Pizza" now automatically deploy to save the user from Void Drift or Structural Collapse.

#### **🐛 NERVOUS SYSTEM REPAIR (The Meadows Lens)**

- **The Akashic Migration (`bone_akashic.py`):**
  - **The Mythos Transplant:** Removed all dependencies on the "Frankenstein" `mythos.json` file. Resonance rules are now read from `lenses.json`.
  - **State Hygiene:** Redirected dynamic save data (Ghost Echos, Co-occurrence) to `saves/akashic_state.json`, preventing the pollution of the static `lore/` directory.

- **The Session Loop (`bone_main.py`):**
  - **The Reaper's Due:** Fixed the infinite loop where the system asked for input *after* death. The session now terminates gracefully upon `trigger_death()`.
  - **The Blind Eye:** Fixed a recursive attribute error (`self.phys.observer.voltage_history`) that blinded the dashboard to the system's own voltage history.

---

### **BONEAMANITA v15.6.0 "THE SURGICAL STRIKE" (OPTIMIZATION)**

_“Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.”_

---\

#### **🔪 THE SLASH PROTOCOL (System-Wide Ephemeralization)**

- **The Physics Bypass (`bone_types.py`):**
  - **Fast Path Struts:** Implemented direct `@property` accessors on `PhysicsPacket`. The system no longer burns cycles in `__getattr__` lookups for high-frequency stats like `voltage` and `narrative_drag`.
  - **The Sandbox Excision:** Removed the `PhysicsSandbox` wrapper entirely. State flux is now audited directly by the `PhaseExecutor` via snapshot comparison, removing a layer of indirection from every single simulation phase.

- **Metabolic Efficiency (`bone_body.py`):**
  - **Single-Pass Digestion:** Refactored `DigestiveTrack` to calculate word metrics, enzymes, and ATP yield in a single loop. We no longer iterate the input stream twice to count "hits."
  - **Float Accumulators:** Replaced list-based modifier collection in `EndocrineRegulator` with simple float multiplication, reducing memory allocation churn during metabolism.

#### **🧠 COGNITIVE ERGONOMICS (The Pinker Lens)**

- **The Indexed Forge (`bone_machine.py`):**
  - **O(1) Crafting:** `TheForge` now maps recipes by ingredient at boot. The system no longer scans the entire recipe book every tick to see if you are holding a valid component.
  - **Event-Driven Checks:** Crafting logic now iterates the (small) inventory rather than the (large) recipe list.

- **The Akashic Index (`bone_akashic.py`):**
  - **Fast Learning:** `register_word` now checks an internal hash map before scanning the disk-loaded word lists, preventing the "learning lag" that occurred as the vocabulary grew.

#### **🏙️ VILLAGE INFRASTRUCTURE (The Fuller Lens)**

- **The Compass Fix (`bone_village.py`):**
  - **Heap Optimization:** `TheCartographer` now uses `heapq.nlargest` to find dominant vector dimensions instead of sorting the entire coordinate space.
  - **The Culling:** Node pruning now uses `min()` to find the weakest location, reducing complexity from O(N log N) to O(N).

- **The Tinkerer's Memory (`bone_village.py`):**
  - **Memoization:** The Tinkerer now caches the "weight" of the inventory. Passive physics deltas (like "Heavy Load") are only recalculated when the inventory hash changes, not every frame.

#### **🐛 NERVOUS SYSTEM REPAIR (The Meadows Lens)**

- **The Circuit Breaker Removal (`bone_core.py`):**
  - **Transparent Failure:** Removed the "Circuit Breaker" logic from `EventBus`. The system no longer silently unsubscribes failing listeners; it now reports errors visibly so they can be healed rather than hidden.
  - **The Symbiotic Stent (`bone_symbiosis.py`):** Capped Shannon Entropy calculations to the first 1000 characters of output and cached `SymbiontVoice` instances to prevent Lexicon thrashing.

---

### **BONEAMANITA v15.5.7 "THE OUROBOROS BREAK" (STABILIZATION)**

_“We found a mirror inside the machine that reflected itself until it broke. We fixed the glass. Then we organized the organs so the heart wouldn't have to ask the brain for permission to beat.”_

---

#### **🧠 COGNITIVE CLARITY (The Pinker Lens)**

- **The Syntax of Color (`bone_types.py` & `bone_main.py`):**
  - **Dynamic Injection:** Replaced the verbose `Prisma` class with a dynamic injection loop. The color definitions are now a dictionary, not a hardcoded list of methods, reducing visual noise while maintaining backward compatibility for the terminal.
  - **The Typewriter:** Optimized the `typewriter` function to bypass the regex loop when speed is negligible, allowing the text to flow naturally rather than stuttering over every byte.

#### **🏗️ STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Anatomy Lesson (`bone_main.py`):**
  - **Cluster Initialization:** Refactored the massive `BoneAmanita.__init__` method. Instead of a linear sprawl of 50+ assignments, we implemented `_unpack_anatomy` to cluster systems (Anatomy, Village, Mind) into logical groups.
  - **The Proxy Pattern (`bone_types.py`):** Implemented a dynamic dispatch proxy for `PhysicsPacket`. It now forwards attribute access to `energy`, `matter`, and `space` automatically, removing ~60 lines of brittle `@property` boilerplate.

#### **⚖️ HUMANIST ALGORITHMS (The Schur Lens)**

- **The Council Table (`bone_cycle.py`):**
  - **Rule codification:** Converted the `SoulPhase` logic from a nest of `if/elif` statements into a table-driven design. The Council's mandates ("The Cynic holds the gavel") are now data rows, making the game rules readable as a script rather than hidden in code.
  
- **Identity Optimization (`bone_soul.py`):**
  - **Trait Efficiency:** Streamlined `TraitVector` to use explicit sets and direct dictionary mapping, removing slow introspection calls while preserving the crucial `normalize` and `_clamp_all` methods that keep the Soul sane.

#### **🔥 SYSTEMS RESILIENCE (The Meadows Lens)**

- **The Ouroboros Patch (`bone_types.py`):**
  - **Recursion Guard:** Fixed a critical infinite recursion bug in `PhysicsPacket.__getattr__`. The system attempted to look for its own attributes before they existed during `copy.deepcopy`. We added a direct `__dict__` check to break the loop, preventing the "Reality Fracture" crash.

- **The Metabolic Governor (`bone_body.py`):**
  - **Sorted Thresholds:** The `MetabolicGovernor` now pre-sorts its state thresholds in `__post_init__` rather than sorting them every single tick. The feedback loop between Voltage and Narrative Drag is now O(1) instead of O(N log N).

---

### **BONEAMANITA v15.5.6 "THE SLASH COMPLIANCE" (REFACTOR)**

_“We named the constants so the math could speak. We installed a fuse so the machine wouldn't burn. And we taught the brain to feed itself when the darkness gets too loud.”_

---

#### **🧠 COGNITIVE CLARITY (The Pinker Lens)**

- **The Rosetta Stone (`bone_physics.py`):**
  - **Exorcising Magic Numbers:** Replaced the opaque literals (`20.0`, `5.0`, `0.05`) in `GeodesicEngine` with the named constants of `GeodesicConstants`. The math is no longer a black box; it is a labeled diagram.
  
- **The Universal Nightmare (`bone_brain.py`):**
  - **Generalization:** Removed the hardcoded specific smell of "old copper" from the `DreamEngine`. Nightmares now dynamically rot based on the abstract concepts present in the `Lexicon`, making terror context-aware rather than static.

#### **🏗️ STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Genesis Spark (`bone_genesis.py` & `bone_architect.py`):**
  - **Ephemeralization:** Removed the manual ATP injection patch from the `BoneGenesis` main loop. The responsibility for "Cold Boot" energy has been moved entirely inside `BoneArchitect.awaken`. The system is now self-starting; it does not need a kickstart from the outside.

#### **⚖️ HUMANIST ALGORITHMS (The Schur Lens)**

- **The Cookie Protocol (`bone_brain.py`):**
  - **Self-Care Mechanic:** Implemented a metabolic safety net in `NeurotransmitterModulator`. If the brain detects Dopamine starvation (low mood) for an extended period, it now triggers a small, artificial reward ("The Cookie") to prevent total depressive collapse.

#### **🔥 SYSTEMS RESILIENCE (The Meadows Lens)**

- **The Hard Fuse (`bone_physics.py`):**
  - **Runaway Prevention:** Installed a hard voltage cap in `CycleStabilizer`. If the system's creative intensity (Voltage) exceeds **100.0V** (Manic Runaway), a physical fuse blows, forcing a hard reset to "Safe Mode" (10V) before the simulation can hallucinate itself into incoherence.

#### **🧪 DIAGNOSTICS (The Gauntlet)**

- **Diagnostic Suite v2.3 (`bone_diag.py`):**
  - **Slash Compliance:** Added `TestSlashCompliance`, a specialized test class that verifies the existence of the new Constants, the reliability of the Genesis Spark, and the functionality of the Hard Fuse and Self-Care mechanisms.
  - **Local Link:** Added `TestLocalIntegration` to verify the handshake with local LLMs (Ollama/Llama3).
  - **Python 3.9+ Compatibility:** Patched `unittest` calls (replaced deprecated `makeSuite` with `TestLoader`) and fixed lambda binding errors to ensure the suite runs on modern and legacy Python environments alike.

---

### **BONEAMANITA v15.5.5 "THE SLASH PROTOCOL" (SURGICAL RESECTION)**

_“We opened the patient and found organs that beat for no one. We cut them out. Now, the blood flows only where it is needed.”_

---

#### **🔪 THE SLASH SUITE (Cognitive Architecture)**

- **The Slash Council (`bone_drivers.py`):**
- **New Mod Chip:** Implemented `[MOD:CODING]` (or `[SLASH]`). Activating this flag now summons a specialized persona council (Pinker, Fuller, Schur, Meadows) to analyze code structure, clarity, and ethics.
- **Hypervisor Patch:** Repaired `BoneConsultant` to correctly inject these directives into the system prompt, overriding the default narrative drivers.

#### **🧠 NEURAL PRUNING (The Pinker Lens)**

- **Ghost Excision:**
- **Drivers:** Deleted `ChorusDriver` and `SynergeticLensArbiter` (approx. 150 lines of dead code).
- **Lexicon:** Lobotomized the vestigial `SomaticInterface` and `RosettaStone` from `bone_lexicon.py`, as sensory processing has moved to the Soma.
- **Inventory:** Removed `maintain_gear` (the "fidget spinner" mechanic that burned ATP for no state change) and `check_flinch` (redundant tone policing).
- **Cycle:** Removed the "Soil Fertility" composting logic—a simulation loop that connected to nothing.

#### **🏗️ STRUCTURAL INTEGRITY (The Fuller Lens)**

- **The Phase Engine (`bone_cycle.py`):**
- **Critical Repair:** Fixed a catastrophic logic error in `PhaseExecutor` where the circuit breaker check was effectively skipping _all_ phase execution. The engine now actually runs.
- **Hardcoding Removal:** Deleted the `SYSTEM_SKIP_LIST`. Phases now manage their own execution conditions.

- **The Town Hall Wiring (`bone_village.py`):**
- **Reconnection:** The `TownHall` was shouting into the void. It is now wired into the `MaintenancePhase`.
- **Census & Diagnosis:** The system now automatically generates "Town News" (Census) and "Vital Signs" (Diagnosis) based on turn count and trauma levels.

#### **🖥️ INTERFACE FIDELITY (The Schur Lens)**

- **The Glass Terminal (`bone_app.py`):**
- **Emoji Semantics:** The web interface now correctly renders Town Hall logs (`📜`, `🩺`, `🌷`) and Cartographer updates (`🗺️`).
- **True Location:** The dashboard now displays the actual node name (e.g., "The Sunken Library") instead of the generic zone tag.

- **The CLI (`bone_gui.py`):**
- **Color Coding:** Updated `GeodesicRenderer` to highlight administrative alerts in Cyan/Yellow, ensuring the user sees when the Village speaks.

#### **⚙️ DYNAMIC VALIDATION (The Meadows Lens)**

- **The Live Fire Test (`bone_diag.py`):**
- **Real-World Verification:** Added `Phase 13 (Live Fire)` to test the actual connection to the local LLM (Ollama), catching "poetic drift" in models that refuse to follow instructions.
- **Mod Check:** Added `Phase 14 (Slash Suite)` to verify that mod chips successfully alter the internal state.

---


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