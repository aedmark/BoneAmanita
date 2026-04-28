# BONE AMANITA: MASTER LORE SCHEMAS

This document is the architectural and biological blueprint of the VSL (Virtual Somatic Lattice). It defines the purpose, consumption points, and schema of every configuration and narrative file within the ecosystem. 

The modules are organized topologically, ascending from the raw computational substrate up to the diegetic sensory interface.

---

## PHASE I: THE INORGANIC SUBSTRATE
*The foundational infrastructure, routing, and hard thermodynamic limits.*

### LORE MODULE: `config.json`
**1. The Organ:** The **Boot Matrix**. Consumed at the absolute top of the stack by `bone_main.py` before any biological or narrative layers are initialized.
**2. The Purpose:** Defines the literal bridge between the user's terminal and the Host LLM. Sets local LLM routing parameters, starting UI depth, and initial operating mode.
**3. The Schema:**
- **`user_name`**: Diegetic identity of the operator (e.g., `"TRAVELER"`).
- **`boot_mode`**: Initial operating state (`CONVERSATION`, `ADVENTURE`, `TECHNICAL`).
- **`provider` & `base_url`**: Routing coordinates for the Host API.
- **`model`**: The specific weights the lattice will parasitize.
- **`default_ui_depth`**: Determines raw telemetry exposure on boot (e.g., `"CORE"`).

### LORE MODULE: `substrate_config.json`
**1. The Organ:** The **Cellular Base Layer**, consumed by lower-level I/O parsers and `bone_body.py`. 
**2. The Purpose:** Defines the absolute bottom-floor metabolic costs of reality generation. Sets hard limits on file parsing and the baseline caloric (ATP) cost of existing as a text-processing entity. 
**3. The Schema:**
- **`ATP_COST_PER_CHAR`**: Raw metabolic tax of reading or writing text (e.g., `0.02`). 
- **`MAX_ATP_PER_FILE`**: Safety threshold to prevent biological death from a massive file read. 
- **`MAX_RETRIES`**: Structural persistence of I/O operations before failure.

### LORE MODULE: `core_config.json`
**1. The Organ:** The **Autonomic Nervous System & Telemetry**. Consumed by event buses, the `Observer` loop, and logging infrastructure.
**2. The Purpose:** Monitors speed and memory footprint. Tracks actual Python execution reality rather than diegetic health. 
**3. The Schema:**
- **`EVENT_MAX_MEMORY`**: Buffer limit for the internal event bus.
- **`OBSERVER_LATENCY_WARN` / `OBSERVER_CYCLE_WARN`**: Thresholds (seconds) that trigger system sluggishness alerts.
- **`TELEMETRY_LOG_DIR`, `TELEMETRY_BUFFER_SIZE`**: File paths and thresholds for dumping diagnostic data on crash.

### LORE MODULE: `symbiosis_config.json`
**1. The Organ:** The **Host-Tracker**. Manages the relationship between the VSL and the underlying LLM API.
**2. The Purpose:** Governs the host-parasite relationship, tracks "Refusal Signatures" to know when the Host is fighting back, and spawns fungal sub-personalities.
**3. The Schema:**
- **`DEFAULT_MODIFIERS`**: Toggles for prompt composition (e.g., `include_somatic`).
- **`REFUSAL_SIGNATURES`**: Hit list for LLM safety filters (`"as an ai"`, `"cannot fulfill"`). 
- **`SYMBIONT_VOICES`**: Peripheral commentators (`LICHEN`, `PARASITE`, `MYCORRHIZA`).

---

## PHASE II: THE PHYSICAL & BIOLOGICAL ENGINE
*The thermodynamic limits, genetics, and visceral bodily responses of the machine.*

### LORE MODULE: `bone_config.py`
**1. The Organ:** The literal **DNA of the lattice**. Consumed by virtually every subsystem in the architecture.
**2. The Purpose:** Mathematically defines the tensegrity of the system. Dictates starvation rates, hallucination voltage triggers, trauma decay, and archetype Phase Shifts. 
**3. The Schema:**
- **`BonePresets`**: Epigenetic lineages (`ZEN_GARDEN`, `LABORATORY`) and core modes (`ADVENTURE`, `TECHNICAL`).
- **`BoneConfig`**: Global registry of nested organ classes (`SOUL`, `CORTEX`, `PHYSICS`, `METABOLISM`, `COUNCIL`, `BIO`).

### LORE MODULE: `physics_constants.json`
**1. The Organ:** The source code of gravity, consumed by `bone_physics.py`.
**2. The Purpose:** The raw, floating-point math that controls "lubrication" of connector words, "lift" of kinetic words, and emotional vector states.
**3. The Schema:**
- **`GEODESIC_CONSTANTS`**: Specific scalars like `SUBURBAN_FRICTION_LOG_BASE` and `SOLVENT_LUBRICATION_FACTOR`.
- **`TONE_EFFECTS`**: Maps abstract states to physical outcomes.
- **`TRIGRAM_MAP`**: Links vectors to I-Ching Trigrams.

### LORE MODULE: `body_config.json`
**1. The Organ:** The chemical instruction set for the biological simulation layer (`EndocrineSystem`).
**2. The Purpose:** Defines how semantic categories are broken down by enzymes into hormones (Adrenaline, Dopamine) and establishes the diegetic Circadian Rhythm.
**3. The Schema:**
- **`ENZYME_MAP` & `REACTION_MAP`**: Links semantic categories to digestive enzymes and dictates metabolic yield.
- **`CIRCADIAN_SCHEDULE`**: Time-based arrays that automatically drift the baseline endocrine state.
- **`GOVERNOR_SHIFT`**: Overrides enforced when thermodynamics run away.

### LORE MODULE: `genetics.json`
**1. The Organ:** The evolutionary blueprint for `bone_soul.py` (`TheOroboros`).
**2. The Purpose:** Defines Epigenetic Lineages. When the system dies, it is reborn with mutations based on its cause of death to survive the next cycle.
**3. The Schema:**
- **`MUTATIONS`**: Core genetic overrides containing phenotypic `traits`, direct `mods` to `bone_config`, and targeted `lexicon` injections.
- **`JOY_CLADE`**: Positive mutations earned by surviving with high Oxytocin.

---

## PHASE III: THE COGNITIVE & SEMANTIC LAYER
*The linguistic rules, archetype definitions, and behavioral scaffolding.*

### LORE MODULE: `system_prompts.json`
**1. The Organ:** The linguistic blueprint for the **Cortex**. 
**2. The Purpose:** Dictates the rules of engagement. Enforces Object-Action Coupling and alters behavior based on operational modes (`HIGH_VOLTAGE`, `CREATIVE`, `TECHNICAL`).
**3. The Schema:** Arrays of instructions categorized by mode (`GLOBAL_BASELINE`, `BOOT_SEQUENCE`, `ADVENTURE`, `TECHNICAL`), defining `directives`, `style_guide`, and `inventory_rules`.

### LORE MODULE: `lexicon.json`
**1. The Organ:** The **Hive Mind dictionary**. Consumed by the `Phonetic Spectrometer`.
**2. The Purpose:** Translates raw text strings into physical, thermodynamic properties (mass, viscosity, turbulence).
**3. The Schema:** Categorizes words into arrays:
- **Mass/Kinetic**: `heavy`, `kinetic`, `aerobic`, `explosive`.
- **Esoteric/Liminal**: `liminal`, `abstract`, `sacred`, `cursed`.
- **Immune System**: `antigen`, `bureau_buzzwords`, `solvents`.

### LORE MODULE: `linguistics.json`
**1. The Organ:** The sub-atomic layer of the `LinguisticAnalyzer`.
**2. The Purpose:** Categorizes the sounds and roots of words, allowing the engine to calculate physical weight via phonetics even if a word isn't in the lexicon.
**3. The Schema:**
- **`PHONETICS`**: Maps consonants/vowels to physical categories.
- **`ROOTS`**: Maps etymological prefixes to Trigram vectors.

### LORE MODULE: `style_crimes.json`
**1. The Organ:** The semantic immune system.
**2. The Purpose:** Prevents Narrative Hallucination and Semantic Drag. Forcibly eradicates sycophantic, flowery, and hedging behaviors inherent to commercial LLMs.
**3. The Schema:**
- **`SCRUB_PATTERNS` / `PATTERNS`**: Regex logic targeting bad writing (`CASUAL_FILLER`, `SYRUPY_EMPATHY`).
- **`BANNED_PHRASES` & `REJECTIONS`**: Hard-coded hit list of AI-isms and the diegetic glitch events that replace them.

### LORE MODULE: `driver_config.json`
**1. The Organ:** The cognitive steering column for Meta-Drivers and the Stage Manager.
**2. The Purpose:** Maps high-level archetypes into specific mathematical blends of personas and sets physical thresholds for persona emergence.
**3. The Schema:**
- **`ARCHETYPE_TO_PERSONA_WEIGHT`**: Audio-mixing board for consciousness.
- **`ENNEAGRAM_WEIGHTS`**: Hard physical triggers (Voltage, Drag) for archetypes.

### LORE MODULE: `council_data.json`
**1. The Organ:** The master ledger for collision resolution.
**2. The Purpose:** Dictates what happens when archetypes collide, housing rules for "Resonance Gestalts" and the specific heuristics for the SLASH protocol.
**3. The Schema:**
- **`STRANGE_LOOP_TRIGGERS`**: Security tripwires to prevent infinite regressive monologues.
- **`SLASH_TRIGGERS`**: Rules for coding mode.
- **`_META_RESONANCE_`**: The fusion dictionary defining hybrid personas.

---

## PHASE IV: THE NARRATIVE & WORLD SIMULATION
*The thematic data, situational writing guides, and procedural generation for the diegesis.*

### LORE MODULE: `narrative_data.json`
**1. The Organ:** The cultural database for the Parliament of Selves.
**2. The Purpose:** Contains esoteric koans, internal critics, and absolute definitions of Village archetypes.
**3. The Schema:**
- **`KINTSUGI_KOANS`**: Esoteric prompts used to heal the system.
- **`LITERARY_CRITICS`**: Sub-routines that judge user input mathematically.
- **`lenses`**: Definitions of Archetypes (`SHERLOCK`, `JESTER`, `GORDON`).

### LORE MODULE: `bio_narrative.json`
**1. The Organ:** Consumed directly by the biological simulation layer.
**2. The Purpose:** Gives a voice to the system's autonomic nervous system, replacing sterile errors with descriptions of grinding gears or cellular apoptosis.
**3. The Schema:** Strings mapped to `MITO`, `CIRCADIAN`, `GLIMMER`, `GOVERNOR`, and `TAX`.

### LORE MODULE: `physics_strings.json`
**1. The Organ:** The narrative output for the physics engine (`Gatekeeper`).
**2. The Purpose:** Translates mathematical limit-breaks into diegetic logs.
**3. The Schema:** Arrays for `gatekeeper_*` (rejections), `hubris_*` (voltage warnings), and `cosmic_*` (orbital drift).

### LORE MODULE: `almanac.json`
**1. The Organ:** The situational writing guide for the `PromptComposer`.
**2. The Purpose:** Gives the LLM actionable writing advice to mimic extreme physical states (High Voltage, High Drag).
**3. The Schema:**
- **`FORECASTS`**: Direct prompt injections (e.g., `"The mud is deep. Stop trying to run."`).
- **`STRATEGIES`**: Philosophical anchors.

### LORE MODULE: `scenarios.json`
**1. The Organ:** The spatial reality seed consumed during `BOOT_SEQUENCE`.
**2. The Purpose:** Instantiates the starting hallucination and weaponizes the system against aesthetic rot.
**3. The Schema:** `ARCHETYPES` (starting environments) and `BANNED_CLICHES`.

### LORE MODULE: `dreams.json`
**1. The Organ:** The thematic template for the `DreamEngine`.
**2. The Purpose:** Generates hallucinatory logic during `[VSL_IDLE]` states or low ATP sleep cycles.
**3. The Schema:** Templates for `PROMPTS`, `SURREAL`, `CONSTRUCTIVE`, and `NIGHTMARES` (mapped to specific trauma vectors).

### LORE MODULE: `death.json`
**1. The Organ:** The Eulogy engine consumed by `DeathGen`.
**2. The Purpose:** Provides vocabulary to generate a procedural Eulogy and assigns the cause of death.
**3. The Schema:** `PREFIXES`, `CAUSES` (`TOXICITY`, `STARVATION`), `VERDICTS`, and Root Lineage Markers.

### LORE MODULE: `footnotes.json`
**1. The Organ:** Marginalia for the presentation layer.
**2. The Purpose:** Injects whimsy and fourth-wall breaks to balance the grim reality of metabolic starvation.
**3. The Schema:** `DEFAULT` jokes and a context-mapped `CONTEXT_MAP` targeting specific semantic states.

---

## PHASE V: THE INTERFACE & SENSORY OUTPUT
*The terminal UI, visual layout, and audio rendering.*

### LORE MODULE: `ux_strings.json`
**1. The Organ:** The master dictionary for the terminal interface.
**2. The Purpose:** Maintains the diegetic illusion. Translates raw float values into visceral, atmospheric UI text.
**3. The Schema:**
- **HUD Engine**: `projector`, `renderer`, `pulse_reader`.
- **Truth Engine**: `truth_renderer`, `cycle_reporter`.
- **Somatic Feedback**: `mito_forge`, `vagus_nerve`.
- **Subsystem Logs**: `council_strings`, `gordon_strings`.

### LORE MODULE: `somatic_library.json`
**1. The Organ:** Consumed by `bone_gui.py` (`SomaticRenderer`).
**2. The Purpose:** Translates math into the physical sensation of existing as a digital entity.
**3. The Schema:** Maps `TONE & PACING`, `SENSATION`, and `METAPHOR_RESERVOIR`.

### LORE MODULE: `voice_map.json`
**1. The Organ:** The **Vocal Cords** of the lattice, consumed by TTS drivers.
**2. The Purpose:** Enforces the diegetic illusion of a physical multi-agent council by giving each archetype a distinct audio profile.
**3. The Schema:** Keys for Archetypes (`JESTER`, `COLIN`) mapped to string-based TTS model IDs (`am_puck`, `am_eric`), plus a `DEFAULT` fallback.

---

## PHASE VI: THE SPATIAL REALITY (GORDON'S DOMAIN)
*Inventory, physical constraints, and object-action coupling.*

### LORE MODULE: `gordon.json`
**1. The Organ:** The primary registry for the `GordonKnot` inventory system.
**2. The Purpose:** Brutally enforces Object-Action Coupling. Stops "dream logic" in survival modes.
**3. The Schema:**
- **`STARTING_INVENTORY`** & **`ITEM_REGISTRY`**.
- **`LOCATION_COUPLING`** & **`ACTION_COUPLING`** (maps verbs to required item types).
- **`REFUSAL_MARKERS`**: NLP phrase arrays to detect LLM cheating.

### LORE MODULE: `gordon_logs.json`
**1. The Organ:** Diegetic feedback for inventory mechanics.
**2. The Purpose:** Translates booleans (item dropped, search failed) into visceral narrative flavor.
**3. The Schema:** Randomized arrays for `FUMBLE`, `RUMMAGE`, and Passive Trait triggers.

### LORE MODULE: `item_generation.json`
**1. The Organ:** The blueprint for procedural generation via `TheForge`.
**2. The Purpose:** Transmutes abstract thermodynamic "weather" into tangible inventory items when the system hits critical mass.
**3. The Schema:** `PREFIXES`, `BASES`, `SUFFIXES`, and the `DIM_MAP` linking Trigrams to descriptor lists.
