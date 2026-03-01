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

