# Domain 01: Physics

Vague language produces wide probability distributions in AI agents. Precise words produce narrow ones. This glossary defines BoneAmanita's highly specific, poetic, and load-bearing nomenclature. 

**Agents MUST map these concepts exactly as defined and are FORBIDDEN from substituting them with the listed synonyms.**

### Core Physics & Biological Variables

**`narrative_drag`**
* **Definition:** A core physics float representing psychological resistance or conceptual friction within the `GeodesicOrchestrator`. It increases heavily when the user breaks lore, attempts impossible actions, or forces paradoxes. It mechanically slows down the engine's response time and alters the tone.
* **Forbidden Synonyms:** `slow_factor`, `delay`, `friction`, `error_weight`, `penalty`

**`ATP` / `atp_pool`**
* **Definition:** The literal biological currency of the engine (Stamina), tracked as a float. Heavy cognitive tasks—like massive context ingestion, disk I/O file forging, or cognitive stumbles (rejections)—drain ATP. Reaching 0 results in terminal system death and the generation of a Death Spore.
* **Forbidden Synonyms:** `energy`, `mana`, `stamina_points`, `health`, `compute_budget`

**`voltage`**
* **Definition:** A physics float representing the energetic intensity, heat, and potential mania of the simulation. High voltage (>60, >80) triggers manic states, structurally fragmented thoughts, and causes the `PromptComposer` to bypass standard logic in favor of orthogonal, shadow-cast vectors.
* **Forbidden Synonyms:** `excitement`, `intensity_level`, `stress`, `temperature_modifier`

**`psi`**
* **Definition:** A physics float representing proximity to the void, reality fracture, or liminal space. High `psi` triggers somatic adrenaline, pareidolia, and structural hallucinations where the `TclWeaver` deforms the text.
* **Forbidden Synonyms:** `madness`, `void_level`, `hallucination_chance`, `weirdness`

**`chi` / `entropy`**
* **Definition:** A physics float representing systemic chaos and semantic entropy. It spikes when the Jester archetype intentionally breaks "False Cohesion" (point attractors) or when paradoxes accumulate.
* **Forbidden Synonyms:** `randomness`, `disorder`, `noise`, `variance`

---

### Architectural Components

**`LoreManifest`**
* **Definition:** The singleton configuration manager that reads the bedrock JSON files (`system_prompts.json`, `physics_constants.json`, etc.). Post-genesis, its files are strictly read-only to preserve the differential baseline of the simulation.
* **Forbidden Synonyms:** `config_parser`, `settings_manager`, `constants_file`, `json_loader`

**`TheSubstrate`**
* **Definition:** The isolated file I/O layer responsible for safely queueing and executing physical file writes (`execute_writes`). It operates under strict geometric containment using `os.path.realpath` to prevent traversal attacks.
* **Forbidden Synonyms:** `file_manager`, `disk_writer`, `io_handler`, `file_system`

**`PanicRoom`**
* **Definition:** The unconscious mathematical watchdog. It catches terminal reality fractures (crashes, unhandled exceptions) and gracefully halts the simulation, freezing the memory graph and extracting safe logs without invoking the LLM.
* **Forbidden Synonyms:** `error_handler`, `crash_manager`, `try_except_block`

**`TclWeaver`**
* **Definition:** The engine's hallucination string manipulator. It takes clean text and "consumes it by the void" based on `psi` and `chi` thresholds, introducing glitch text, redactions, and semantic decay.
* **Forbidden Synonyms:** `text_glitcher`, `string_formatter`, `madness_filter`

---

### Conceptual / Lore Entities

**`godel_scars`**
* **Definition:** An integer tracking the number of times the `LiminalModule` has breached its threshold due to reality-bending or void-like user input. A measure of permanent mathematical trauma.
* **Forbidden Synonyms:** `error_count`, `threshold_breaks`, `liminal_violations`, `glitch_tracker`

**`dark_matter_sparks`**
* **Definition:** An integer counter in the `LiminalModule` that increments when consecutive words in the user's input violently alternate between heavy physical concepts (kinetic) and abstract/void concepts.
* **Forbidden Synonyms:** `contrast_count`, `abstract_hits`, `semantic_jumps`

**`Death Spore`**
* **Definition:** A permanent cryptographic record (JSON) generated upon the biological death of the system (e.g., via ATP exhaustion or terminal ROS toxicity). It records the fatal vectors and forces architectural handicaps/scars on the subsequent boot cycle.
* **Forbidden Synonyms:** `crash_log`, `fatal_error_report`, `dead_state_save`
