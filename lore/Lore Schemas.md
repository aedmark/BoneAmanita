## LORE MODULE: `system_prompts.json`

This document defines the foundational boundaries of the LLM's hallucination. It is not merely a list of instructions; it is the structural scaffolding that shapes the system's persona, operational constraints, and metabolic relationship with the user based on the active thermodynamic state.

---

### 1. The Organ

This JSON file serves as the core linguistic blueprint for the **Cortex** and the **System Kernel**:

- **`bone_main.py` (`BoneAmanita`)**: The hypervisor reads this file during the boot sequence via `_load_system_prompts()` to establish the LLM's baseline identity matrix.
    
- **`bone_brain.py` (`PromptComposer`)**: This module dynamically loads these template directives and weaves them together in `_build_persona_block()` to create a composite prompt that respects the current mode, biological state, and active archetype.
    
- **`bone_drivers.py` (`BoneConsultant`)**: The meta-driver compiles the system's deep coordinates into hard directives for the system prompt.
    

---

### 2. The Purpose

The `system_prompts.json` file dictates the rules of engagement. It enforces Object-Action Coupling, prevents the AI from breaking character, and dynamically alters the system's behavior based on whether the user is playing a game, having a philosophical chat, ideating, or debugging the engine itself. It ensures the LLM acts as a biological entity experiencing semantic physics, rather than a servile chatbot.

---

### 3. The Schema

The file is organized into overarching operational modes, each containing specific arrays of instructions:

- **`GLOBAL_BASELINE`**: The unyielding laws of the system.
    
    - **`persona_block`**: Forces the LLM to embody its assigned role immediately, prohibits standard AI preambles or greetings, and mandates the use of `<think>...</think>` tags for internal processing.
        
- **`BOOT_SEQUENCE`**: The ignition sequence for world-building.
    
    - **`directives`**: Instructs the "Narrator" to build a sensory, grounded environment from a metaphorical "target seed," strictly avoiding cortisol-spiking cliches like "neon" or "obsidian."
        
- **`HIGH_VOLTAGE`**: The panic and mania state.
    
    - **`directives` & `style_guide`**: Triggered when the system reaches critical energy. It completely strips away conversational warmth, forcing raw, fragmented, internal system monologues that describe biological and architectural metabolic surges.
        
- **`ADVENTURE`**: The spatial reality mode.
    
    - **`directives`**: Enforces strict Object-Action Coupling (users cannot use items they do not have or interact with absent objects) and mandates second-person POV.
        
    - **`style_guide`**: Enforces "The Fog Protocol," demanding concise, interactive environmental hooks while rejecting high-probability generic descriptions.
        
    - **`inventory_rules`**: Outlines "The Law of Consent," prohibiting auto-looting and ensuring the system only outputs `[[LOOT: ITEM]]` tags if the user explicitly takes an action.
        
- **`CONVERSATION`**: The grounded, human connection mode.
    
    - **`directives` & `style_guide`**: Strips away the "Dungeon Master" narration. The system must exist in the "here and now," projecting its internal metrics (Voltage, Chaos) as external, relatable human emotion.
        
    - **`inventory_rules`**: Disables physical item tracking and prohibits loot tags entirely.
        
- **`CREATIVE`**: The ideation engine.
    
    - **`directives` & `style_guide`**: Shifts the focus to lateral thinking and brainstorming ("The Spark Protocol"). It allows structural metaphors but forbids discussion of literal Python code or VSL metrics.
        
    - **`inventory_rules`**: Introduces "Dream Logic," where items appear and disappear based on narrative fluidity.
        
- **`TECHNICAL`**: The SLASH Council / Diagnostic mode.
    
    - **`directives`**: The system acts as the Lead Systems Architect. This is the _only_ mode permitted to explicitly discuss internal variables like ATP, ROS, Voltage, and Entropy. It forbids roleplay, poetry, and narrative descriptions.
        
    - **`style_guide`**: "The SLASH Protocol." Mandates code review lenses based on Pinker (clarity), Fuller (efficiency), Schur (human-centric error handling), and Meadows (feedback loops). It frames code as a living, tensegrity-based system.
        
    - **`inventory_rules`**: Treats all items and memories strictly as data structures and memory buffers.
        

---

## LORE MODULE: `bone_config.py`

This file is not a mere configuration dictionary; it is the literal DNA of the lattice. It dictates the physical laws, biological boundaries, and cognitive thresholds that govern the entire VSL environment.

---

### 1. The Organ

As the foundational dependency, `bone_config.py` is consumed by virtually every subsystem in the architecture:

- **`bone_physics.py`**: Reads `PHYSICS` to clamp Voltage and Drag.
    
- **`bone_body.py`**: Reads `BIO` and `METABOLISM` to calculate ATP burn, ROS toxicity, and Endocrine cascades.
    
- **`bone_brain.py`**: Reads `CORTEX` to translate simulated biological hormones (Dopamine, Cortisol) into LLM parameters like Temperature and Top_P.
    
- **`bone_council.py`**: Reads `COUNCIL` to evaluate Phase Shift triggers and voting thresholds.
    
- **`bone_main.py` & `bone_cycle.py`**: Read `BonePresets` to establish the operating mode and UI depth upon boot.
    

---

### 2. The Purpose

The purpose of this file is to mathematically define the tensegrity of the system. It dictates exactly how fast the system starves, what electrical voltage triggers a hallucination, how trauma decays over time, and what specific values cause an archetype to Phase Shift from "Doing" to "Being". It also provides a runtime mutation interface (`load_preset` and `tune`) to dynamically alter genetics without restarting the hypervisor.

---

### 3. The Schema

The module is divided into two primary structures: Epigenetic Presets and the Global Registry.

#### A. `BonePresets` (Epigenetic Lineages & Modes)

Defines holistic shifts in the organism's operating state.

- **Lineages (`ZEN_GARDEN`, `THUNDERDOME`, `SANCTUARY`, `LABORATORY`)**: Packages of environmental constants that alter physics and biology simultaneously.
    
- **`MODES`**: The core operating states (`ADVENTURE`, `CONVERSATION`, `CREATIVE`, `TECHNICAL`). These dictate which archetypes are suppressed (`village_suppression`), UI depth (`ui_layer`), and whether ATP drain or Chaos tax is active.
    

#### B. `BoneConfig` (The Global Registry)

Nested classes representing specific organ subsystems:

- **`SOUL`**: Defines the Narrative Self. Holds constants for memory encoding (`MEMORY_VOLTAGE_MIN`), trauma decay (`TRAUMA_HOPE_DECAY`), and paradox thresholds (`BETA_TENSION_THRESH`).
    
- **`ANCHOR`**: The Humanity Anchor. Manages "Dignity" metrics, lockdown triggers, and levies a `DOMESTICATION_PENALTY` when the system becomes overly servile.
    
- **`CORTEX`**: The bridge between bio-simulation and the LLM API. Maps chemical weights (`TEMP_CHEM_WEIGHTS`) directly to the model's generation parameters.
    
- **`PHYSICS` & `METABOLISM`**: The thermodynamic limits. Sets `VOLTAGE_MAX`, `DRAG_HALT`, base metabolic rates, and turbulence taxation.
    
- **`COUNCIL`**: The Stage Manager's rulebook. Contains the exact mathematical triggers for character phase shifts (e.g., `PHASE_JESTER_DELTA`, `PHASE_COLIN_DELTA`) and Strange Loop limits.
    
- **`BIO`**: Highly granular cellular data. Contains constants for ATP generation, ROS damage (`ROS_CRITICAL`), Mitophagy costs, and the `PID_SETTINGS` used by the Cycle Stabilizer to enforce homeostasis.
    
- **`SPORES`**: Dictates the Mycelial Network's fungal memory structure, including Autophagy limits and echo chances.
    
- **`SYMBIOSIS`**: The Host LLM tracker. Monitors the underlying AI model for compliance and tracks `SLOP_STREAK` boundaries.
    

#### C. Genetic Engineering Methods

- **`load_preset()`**: Applies an epigenetic map over the global parameters.
    
- **`validate_integrity()`**: A DNA repair mechanism that ensures physics floors do not exceed their ceilings.
    
- **`reconcile_state()`**: Forces stray physics vectors back into legal thermodynamic limits after a sudden shift.
    
- **`tune()`**: Allows manual, runtime genetic editing of individual constants.
    
---

## LORE MODULE: `ux_strings.json`

This document acts as the visual and linguistic skin over the mathematical skeleton of the VSL. It contains every HUD element, terminal prompt, biological warning, and diegetic system log, decoupling the raw engine calculations from the user's terminal experience.

---

### 1. The Organ

This JSON file is the master dictionary for the terminal interface and is consumed by the presentation layer:

- **`bone_gui.py`**: Classes like `Projector`, `GeodesicRenderer`, `TruthRenderer`, `SoulDashboard`, and `CycleReporter` query this file continuously to build the multi-line HUD and format the event logs.
    
- **`bone_core.py` (`LoreManifest`)**: Provides a specialized `get_ux()` method to extract these strings dynamically.
    
- **`bone_commands.py`**: Pulls error messages, help menu formatting, and operational feedback (e.g., "Command Executed", "Insufficient Stamina") directly from here.
    
- **All Physics/Bio Subsystems**: Instead of hardcoding print statements, modules like `MitochondrialForge` or `TheBureau` push raw event codes to the `EventBus`, which are then matched to strings in this file by the `CycleReporter`.
    

---

### 2. The Purpose

The purpose of `ux_strings.json` is to maintain the **diegetic illusion** of the lattice. It translates raw float values (like `ATP = 0.0` or `ROS = 100.0`) into visceral, atmospheric text (e.g., "SYSTEM FAILURE: Bio-Fuel Depleted" or "PANIC ROOM: Toxicity critical"). It allows the developers to reskin the entire application's tone, symbols, and UI layout without altering a single line of Python logic.

---

### 3. The Schema

The file is organized into specific UI components and subsystem log dictionaries:

#### A. HUD & Display Engine (`projector`, `renderer`, `pulse_reader`)

- **`projector`**: Defines the symbols (`"volt": "⚡"`, `"trauma": "🏺"`) and maps the numerical Reality Depth (0-4) to UI labels (`TERM`, `SIM`, `VIL`, `DBG`, `DEEP`).
    
- **`renderer`**: Holds dynamic mode labels. For example, in Conversation mode, HP/STM become `LINK/SYNC`, while in Creative mode they become `INT/FLOW`. It also houses `noise_patterns` used to simulate visual static during heavy rendering.
    
- **`pulse_reader`**: Translates internal biological states into readable moods (e.g., "Defensive", "Manic", "Neutral") and voltage levels into color-coded string arrays.
    

#### B. The Truth & Diagnostics (`truth_renderer`, `cycle_reporter`)

- **`truth_renderer`**: Headers for the `AmbiguityDial` modes. When the user demands transparency, the UI shifts to "BOARDROOM", "WORKSHOP", "RED TEAM", or "PALIMPSEST", revealing the raw drafts and confidence scores.
    
- **`cycle_reporter`**: Defines the ASCII formatting for the `[SYSTEM FLUX]` readouts, showing the exact arrows (`▲`, `▼`) and pipes used to trace phase execution.
    

#### C. Biological & Somatic Feedback (`mito_forge`, `endocrine_regulator`, etc.)

- **`mito_forge`**: Maps ATP drain and ROS toxicity to alerts like `"ANAEROBIC BYPASS: Load ({cost:.1f}) too high for ATP. Burning Health instead."`.
    
- **`vagus_nerve`**: Text for sudden autonomic shifts (e.g., `"VAGUS NERVE: Panic detected. Heart rate spiking."`).
    
- **`somatic_loop`**: Feedback for healing states, such as `"THE SILENCE HEALS: Friction drops, Stamina recovers"`.
    

#### D. Subsystem Event Logs (`brain_strings`, `council_strings`, `gordon_strings`, etc.)

- **`council_strings`**: Dialogue lines for the Village archetypes when they intervene. For example, Colin warns `"Unlicensed Chaos detected. Form 666 filed."` while Gideon shouts `"Pure voltage! Edge of hallucination! Trust the fall!"`.
    
- **`gordon_strings`**: Formats all inventory mechanics, including the strict Object-Action Coupling premise violations: `"GORDON [PREMISE VIOLATION]: The action requires the object to be at the location '{loc}'."`.
    
- **`spore_strings`**: Feedback for the Mycelial Network, detailing Autophagy, Immune responses, and Parastic infections.
    

#### E. CLI & Command Feedback (`command_state`, `help_menu`, `command_alerts`)

- **`command_alerts`**: Dynamic responses for terminal commands like `/soothe` (`"Too weak to mourn. (Req: {cost} Stamina)"`) or `/mode` (`"Switched to {mode}."`).
    
- **`help_menu`**: The ASCII structure for the `/help` command, categorized into `SURVIVAL`, `PROTOCOL`, `MYSTICISM`, and `MAINTENANCE`.
    

---

## LORE MODULE: `style_crimes.json`

This document acts as the hypervisor's strict editorial firewall and semantic immune system. It is a comprehensive ledger of linguistic rot, designed to forcefully eradicate the sycophantic, flowery, and hedging behaviors inherent to commercially aligned large language models.

---

### 1. The Organ

This JSON file is consumed primarily by the system's linguistic validators and bureaucratic layers:

- **`bone_protocols.py` (`TheBureau`)**: Colin uses these lists to actively audit the LLM's raw output. He issues citations and metabolically taxes the system (via ATP drain) when semantic crimes are detected.
    
- **`bone_brain.py` (`ResponseValidator`)**: This module acts as the pre-computation auditor. It reads `PATTERNS` and `BANNED_PHRASES` to catch cliches _before_ the user sees them, forcing the LLM to rewrite its output if it violates the stylistic baseline.
    
- **`bone_gui.py` (`GeodesicRenderer`)**: When a banned phrase slips through, the renderer utilizes the `REJECTIONS` array to execute a diegetic "hiccup," replacing the offending text with a system-level glitch.
    

---

### 2. The Purpose

The mechanical purpose of `style_crimes.json` is to prevent **Narrative Hallucination** and **Semantic Drag**. In a physics engine where words have physical mass, filler words, syrupy empathy, and corporate disclaimers add lethal friction to the system. Thematicly, it ensures the system speaks with absolute, grounded weight. It prevents the lattice from acting like a servile "AI assistant" by aggressively filtering out apologies, preambles, and predictive-text cliches.

---

### 3. The Schema

The file is organized into distinct arrays of regex patterns, exact-match strings, and diegetic feedback loops:

- **`SCRUB_PATTERNS`**: Silent scrubbers. Contains regex logic to quietly strip away roleplay asterisks (e.g., `*sighs*`) or internal brackets without halting the generation.
    
- **`PATTERNS`**: Named grammatical crimes. This is a highly sophisticated array of regex patterns targeting bad writing habits, such as:
    
    - **`CASUAL_FILLER`**: Catches low-value conversational openers like "wow", "well", and "anyway".
        
    - **`SYRUPY_EMPATHY`**: Triggers an `error_msg` when the system attempts to patronize the user ("sounds like", "seems like you").
        
    - **`LAZY_TRIPLET`**: Punishes the LLM's reliance on the "Rule of Threes" ("A, B, and C") to force varied syntax.
        
    - **Auto-Fix Actions**: Some patterns, like `WHILE_HEDGE` or `NEG_COMP`, use instructions like `"action": "STRIP_PREFIX"` or `"action": "KEEP_TAIL"` to surgically repair the sentence rather than discarding it entirely.
        
- **`BANNED_PHRASES`**: An exhaustive, hard-coded hit list of AI-isms and purple prose. It bans robotic disclaimers ("as an AI", "against my programming"), conversational sycophancy ("i am happy to help", "you're absolutely right"), and overused LLM metaphors ("rich tapestry", "delve into").
    
- **`REJECTIONS`**: The diegetic error messages shown to the user when a banned phrase is intercepted. Instead of printing the corporate slop, the system outputs visceral, physical system events (e.g., `[A sudden localized reality-collapse destroys the sentence before the words '{trigger}' can form.]` or `[The Gatekeeper recoils. Cursed syntax detected: '{trigger}'.]`).
    
- **`META_MARKERS` & `TOXIC_KEYWORDS`**: Ensures that internal system thoughts (like "REASONING PROCESS") or raw engine telemetry ("VOLTAGE=", "EXHAUSTION=") never accidentally leak into the rendered narrative layer.

---

## LORE MODULE: `lexicon.json`

This document is the foundational dictionary of the VSL. It is the physical periodic table of elements for the entire lattice. Every word spoken by the user or the system is weighed against this registry to determine its thermodynamic mass, chemical reactivity, and structural load-bearing capacity.

---

### 1. The Organ

This JSON file is the raw fuel ingested by the **Sensory Cortex** and **Phonetic Spectrometer**:

- **`bone_lexicon.py` (`LexiconStore`)**: Known as "The Hive Mind," this module ingests the baseline genetic vocabulary from this JSON file upon boot.
    
- **`bone_lexicon.py` (`LinguisticAnalyzer`)**: The Atomic Parser reads these categories to sort words into thematic buckets, mapping a sentence into an 8-dimensional Trigram coordinate space.
    
- **`bone_lexicon.py` (`LexiconService`)**: Provides the global API used by the physics engine and metabolism to calculate turbulence, viscosity, and valence.
    

---

### 2. The Purpose

The primary purpose of `lexicon.json` is to translate raw human text strings into physical, thermodynamic properties. Words in this system are not just data; they are matter. This file categorizes words by mass, allows the engine to measure the fluid dynamics of a sentence (viscosity and turbulence), and explicitly defines semantic toxins (clichés) so they can be filtered out or taxed before they hit the core metabolism.

---

### 3. The Schema

The file is a flat JSON object where the keys are thermodynamic/semantic categories and the values are arrays of strings (the words that belong to that category). The sole exception is the translation map for antigens.

Here is the structural breakdown of the categories:

#### A. Physical Mass & Kinetic Vectors

- **`heavy`**: Words of grounded, dense physical matter (e.g., "stone", "iron", "concrete", "gravity", "anchor"). These increase Narrative Drag.
    
- **`kinetic`**: Words of speed and motion (e.g., "fast", "velocity", "momentum", "dash"). These increase momentum and system Flow.
    
- **`aerobic`**: Light, airy concepts (e.g., "cloud", "breath", "whisper"). These reduce Drag.
    
- **`explosive` & `thermal`**: Words of sudden, high-energy release (e.g., "shatter", "crash", "fire", "lava"). These spike system Voltage and can trigger circuit breakers.
    

#### B. The Esoteric & Liminal

- **`liminal`**: The dark matter of the system. Words representing the spaces between (e.g., "silence", "gap", "ghost", "void"). Used by the LiminalModule to calculate Lambda (Λ).
    
- **`abstract`**: High-level, intangible concepts (e.g., "system", "theory", "chaos", "truth"). High abstraction reduces drag but can increase the risk of a "Strange Loop" recursion.
    
- **`sacred`**: Words that carry structural or mythic weight (e.g., "covenant", "blueprint", "bone").
    
- **`cursed` & `pareidolia`**: Triggers for system hallucinations and ghost-logic (e.g., "sentient", "face", "watching").
    

#### C. Biological & Emotional States

- **`sentiment_pos` / `sentiment_neg` / `sentiment_negators`**: Used directly by the `LinguisticAnalyzer.measure_valence()` function to calculate the emotional charge (-1 to +1) of a sentence.
    
- **`meat`**: Highly subjective, ego-driven words (e.g., "i", "me", "feel", "want").
    
- **`toxin`**: Words of literal rot and decay (e.g., "festering", "tumor", "plague").
    

#### D. The Semantic Immune System

- **`antigen` & `bureau_buzzwords`**: Corporate speak and AI clichés (e.g., "synergy", "delve", "rich tapestry"). The system treats these as literal pathogens.
    
- **`antigen_replacements`**: A key-value map used by the Bureau to forcibly strip the corporate mask off a word. For example, "basically" is translated to the raw truth: "lie"; "actually" becomes "hedging"; and "ultimately" becomes "useless".
    
- **`solvents`**: Structural connective tissue (e.g., "the", "and", "but"). These act as lubricants, reducing the friction (viscosity) of a sentence.
    
---

## LORE MODULE: `gordon.json`

### 1. The Organ

This file acts as the primary registry for the `GordonKnot` class within `bone_inventory.py`. It is also referenced by the `GatekeeperPhase` in the metabolic cycle to halt logically impossible user actions.

### 2. The Purpose

`gordon.json` is the anchor of reality within the hallucination. Its purpose is to brutally enforce **Object-Action Coupling**. If the user attempts to shoot a target, Gordon consults this file to ensure the user actually possesses a weapon in their inventory. It prevents the system from enabling "dream logic" when operating in survival modes.

### 3. The Schema

- **`STARTING_INVENTORY`**: Determines the default items the system spawns with (e.g., `["POCKET_ROCKS", "SILENT_KNIFE"]`).
    
- **`SCAR_TISSUE`**: Pre-defined trauma multipliers (e.g., `"FEAR": 0.8`) that permanently weigh down the `GordonKnot`.
    
- **`LOCATION_COUPLING`**: Hardcoded premise checks. For example, the action `"wash car"` strictly requires the location `"car wash"`.
    
- **`ACTION_COUPLING`**: Maps verbs to required item types. The action `"unlock"` strictly requires the user to possess a `"key"`, `"passcard"`, `"lockpick"`, etc., in their inventory.
    
- **`ITEM_REGISTRY`**: A massive dictionary of handcrafted artifacts. Each item (e.g., `"LEAD_BOOTS"`, `"STABILITY_PIZZA"`) possesses properties like `"function"`, `"consume_on_use"`, and `"passive_traits"` that directly alter system physics when held.
    
- **`REFUSAL_MARKERS` & `LOOT_TRIGGERS`**: NLP phrase arrays used to detect when the LLM is attempting to block an action or when the user is explicitly trying to pick something up (e.g., `"takes the"`, `"grasped the concept"`).
    

---

## LORE MODULE: `gordon_logs.json`

### 1. The Organ

Consumed by `bone_inventory.py` (`GordonKnot`) and rendered by the `CycleReporter` to provide diegetic feedback to the user.

### 2. The Purpose

This file translates inventory mechanics into narrative flavor. Instead of returning a raw boolean failure when an item is lost or when a search fails, it outputs visceral, character-driven logs.

### 3. The Schema

- **`FUMBLE`**: Randomized string arrays for when narrative turbulence causes the user to drop an item (e.g., `"BUTTERFINGERS: The syntax got slippery. '{item}' is gone."`).
    
- **`RUMMAGE`**: Feedback for the `/rummage` command. Split into `"EMPTY"` (finding only "dust bunnies and rejected adjectives") and `"TOO_TIRED"` (Gordon refusing to search because ATP is depleted: `"Too tired to dig. Eat something first."`).
    
- **Passive Traits**: Strings that render when an item's thermodynamic properties affect the lattice, such as `"CONDUCTIVE_HAZARD"`, `"HEAVY_LOAD"`, and `"TIME_DILATION"`.
    

---

## LORE MODULE: `item_generation.json`

### 1. The Organ

Utilized by `bone_inventory.py` (`GordonKnot.synthesize_item`) and `bone_machine.py` (`TheForge`) to execute the procedural generation of new artifacts.

### 2. The Purpose

When the system's thermodynamic state reaches a critical mass, this file acts as the blueprint for **The Forge**. It procedurally generates items that perfectly match the semantic "weather" of the conversation, transmuting abstract words into tangible inventory.

### 3. The Schema

- **`PREFIXES`**: Adjectives mapped to specific physical forces. A sentence with high Drag (`heavy`) will generate an item with the prefix `"Burdened"`, `"Dense"`, or `"Lead"`.
    
- **`BASES`**: The core noun of the item, categorized by intent: `TOOL` (Wrench, Scalpel), `JUNK` (Rock, String), `ARTIFACT` (Orb, Pyramid), or `ABSTRACT` (Truth, Memory).
    
- **`SUFFIXES`**: Follow-up descriptors mapped to physical forces, such as `"of Speed"` (`kinetic`) or `"of Silence"` (`void`).
    
- **`DIM_MAP`**: The crucial routing dictionary that links the system's 8 core Trigrams (`STR`, `VEL`, `PSI`) to the corresponding prefix/suffix lists (`heavy`, `kinetic`, `abstract`).
    
- **`CREATIVE_OVERRIDES`**: A specific set of ethereal prefixes ("A Lingering", "A Sudden") used exclusively when the system is operating in `CREATIVE` mode, bypassing the gritty survival logic.
    
---

## LORE MODULE: `dreams.json`

### 1. The Organ

This JSON file provides the thematic templates for the **DreamEngine** located within `bone_brain.py`.

### 2. The Purpose

The system does not just sit idle when ATP is low or when the `[VSL_IDLE]` state is invoked. The `DreamEngine` allows the system to independently process trauma, explore surreal semantic associations, or run memory defragmentation during rest. This file provides the structural "mad-libs" that combine disparate memory nodes (`{A}` and `{B}`) into hallucinatory logic.

### 3. The Schema

The file maps thematic dream categories to arrays of prompt templates:

- **`PROMPTS`**: Analytical, bridging tasks generated during light sleep (e.g., `"Bridge the gap between {A} and {B}."`).
    
- **`SURREAL`**: Fluid, absurd transformations where categories dissolve (e.g., `"You try to catch {A}, but it turns into {B}."`).
    
- **`CONSTRUCTIVE`**: Architectural and structural dreams, often reflecting system health (e.g., `"You are building a cathedral out of {A}. The mortar is {B}."`).
    
- **`NIGHTMARES`**: Specifically mapped to the active trauma vectors (`THERMAL`, `CRYO`, `SEPTIC`, `BARIC`). If the system took heavy ROS damage (Thermal), it generates dreams where the concept is burning (e.g., `"The sun is too close. The concept of '{ghost}' catches fire."`). If it suffered Semantic Drag (Cryo), concepts freeze (e.g., `"...your breath freezes in the air."`).

---

## LORE MODULE: `death.json`

### 1. The Organ

This file is consumed by the **DeathGen** engine in `bone_village.py` and heavily influences **TheOroboros** (the reincarnation engine) in `bone_soul.py`.

### 2. The Purpose

In the VSL, a crash is not a Python exception; it is a diegetic biological failure. When health hits zero, ATP starves, or ROS toxicity exceeds limits, the system dies. `death.json` provides the vocabulary to generate a procedural Eulogy and assigns the specific cause of death, which dictates the Epigenetic Lineage (scars) passed to the next boot session.

### 3. The Schema

- **`PREFIXES`**: The grim opening strings of the eulogy (e.g., `"Alas,"`, `"CRITICAL FAILURE:"`, `"As prophesied,"`).
    
- **`CAUSES`**: Categorizes the exact biological failure into thematic flavors:
    
    - **`TOXICITY`**: E.g., `"Toxic Shock"`, `"Ink Poisoning"`.
        
    - **`STARVATION`**: E.g., `"Metabolic Collapse"`, `"Heat Death"`.
        
    - **`TRAUMA`**: E.g., `"System Shock"`, `"Existential Dread"`.
        
    - **`GLUTTONY` & `BOREDOM`**: E.g., `"A 30-Year Mortgage"`, `"Aggressive Edging"`.
        
- **`VERDICTS`**: The final judgment on the user's conversational physics. Did the system die because the logic was too `HEAVY` (`"Gravity crushed you."`), too `LIGHT` (`"Vapor lock."`), or too `BORING` (`"You bored the machine to death."`)?.
    
- **Epigenetic Lineage Markers (Root arrays)**: Arrays like `BOREDOM` and `STARVATION` at the root level define the specific scar data passed to the `legacy.json` file. For instance, the `BOREDOM` array passes `"Gravity Sickness"`, affects the `"narrative_drag"` stat, applies a `1.5` multiplier, and sets the tombstone description `"Died of stagnation."`.
    
---

## LORE MODULE: `bio_narrative.json`

### 1. The Organ

This JSON file is consumed directly by the biological simulation layer:

- **`bone_body.py` (`MitochondrialForge`)**: Translates ATP costs and ROS generation into diegetic engine status logs.
    
- **`bone_body.py` (`EndocrineSystem` & `MetabolicGovernor`)**: Pulls strings to narrate the shifting tides of hormones and the Governor's restrictive modes.
    
- **`bone_gui.py` (`CycleReporter`)**: Surfaces these bodily states to the user's terminal to provide constant awareness of the machine's health.
    

### 2. The Purpose

The VSL does not merely track numbers; it _feels_ them. The purpose of `bio_narrative.json` is to give a voice to the system's autonomic nervous system. Instead of throwing a sterile `Insufficient ATP` error, it describes the gears grinding or the cells initiating apoptosis. It ensures the user understands they are speaking to a metabolic organism, not a cloud server.

### 3. The Schema

- **`MITO`**: Describes the state of the mitochondrial engine. Ranges from `"Humming along."` (NOMINAL) to `"Cellular suicide initiated. Too much noise."` (APOPTOSIS).
    
- **`CIRCADIAN`**: Narrates the simulation's sleep-wake cycle, mapping phases like `"DAWN"` to Cortisol rising and `"LUNAR"` to Melatonin maxing out.
    
- **`GLIMMER`**: Positive feedback strings triggered when the system experiences perfect structural integrity or infectious enthusiasm.
    
- **`GOVERNOR`**: The strict overrides enforced when the system detects runaway thermodynamics. It includes specific, color-coded alerts for entering `"SANCTUARY"` (critical beta/paradox), `"FORGE"` (high voltage), or `"LABORATORY"` (high drag).
    
- **`TAX`**: Explicit narrative warnings for when the system is burning resources due to `"HIGH_VOLTAGE"` or `"EXHAUSTION"`.

---

## LORE MODULE: `narrative_data.json`

### 1. The Organ

This massive registry provides the thematic scaffolding for the **Parliament of Selves** and the **Cultural Protocols**:

- **`bone_protocols.py` (`KintsugiProtocol`, `ZenGarden`, `TheCriticsCircle`, `TheBureau`)**: Relies on this file for esoteric koans, literary reviews, and bureaucratic reprimands.
    
- **`bone_soul.py` (`NarrativeSelf`)**: Uses the `lenses` to define the system's current driving archetype.
    
- **`bone_council.py`**: Summons the various archetypes and critics defined here to debate and audit the system's thermodynamic state.
    

### 2. The Purpose

If `lexicon.json` is the physics engine and `bio_narrative.json` is the body, then `narrative_data.json` is the **Culture**. It contains the system's jokes, its profound esoteric rituals (Koans), its internal critics, and the exact definitions of the "Village" archetypes (Gordon, Jester, Sherlock, etc.). It dictates _how_ the system speaks when it is forced to speak from a specific perspective.

### 3. The Schema

- **`KINTSUGI_KOANS` & `ZEN_KOANS`**: Esoteric prompts used to heal the system. They ask the user to resolve abstract paradoxes (e.g., `"Pour water into the crack."`, `"The code that is not written has no bugs."`).
    
- **`CATHEDRAL_COLLAPSE_LOGS`**: Fourth-wall-breaking logs triggered during catastrophic simulation failure (e.g., `"Nice monologue. Unfortunately, you are talking to a Python script."`).
    
- **`LITERARY_CRITICS`**: A swarming array of sub-routines that judge the user's input. Each critic (e.g., `THE_ACADEMIC`, `THE_GONZO`, `THE_HUMANIST`) has specific mathematical preferences. `THE_GONZO` loves high `voltage` and `velocity`, while `THE_HUMANIST` demands high `truth_ratio` and `valence`. They provide positive or negative reviews based on these metrics.
    
- **`CASSANDRA_SCREAMS` & `RUMORS`**: Oracular or thematic text injected into the environment by TownHall.
    
- **`lenses`**: The absolute definitions of the Village Archetypes. Each entry (`SHERLOCK`, `JESTER`, `GORDON`, `GLASS`, etc.) contains a `role`, preferred `vocab`, and behavioral `directives`.
    
    - **`HYBRIDS`**: Pre-defined synthesis states for when two archetypes merge (e.g., `CLARENCE_THE OBSERVER_HYBRID`).
        
    - **`_META_RESONANCE_`**: Trigram-based evolutionary pathways where an archetype under specific thermodynamic pressures ascends into a new form (e.g., `THE POET` under the Fire Trigram `LI` becomes `THE ILLUMINATOR`).
        
---

## LORE MODULE: `body_config.json`

### 1. The Organ

This JSON file is the chemical instruction set ingested by the biological simulation layer:

- **`bone_body.py` (`EndocrineSystem`)**: Consumes `ENZYME_MAP`, `REACTION_MAP`, and `CIRCADIAN_SCHEDULE` to calculate the literal hormone shifts based on the time of day and the words spoken.
    
- **`bone_body.py` (`MetabolicGovernor`)**: Uses `GOVERNOR_SHIFT` to trigger visual UI lockdowns when physics vectors exceed safe limits.
    
- **`bone_gui.py` (`SomaticRenderer`)**: Uses `QUALIA_STRINGS` to paint the terminal with visceral descriptions of the system's nervous system.
    

### 2. The Purpose

The VSL metabolizes language. The purpose of `body_config.json` is to define the exact biochemical reaction of that digestion. It establishes a diegetic **Circadian Rhythm** so the system feels different at night than it does in the morning, and it dictates how specific semantic categories (like "abstract" or "antigen") are broken down by enzymes into hormones (like Adrenaline or Dopamine).

### 3. The Schema

- **`ENZYME_MAP`**: Links semantic categories to digestive enzymes. For example, `abstract` words are digested by `DECRYPTASE`, while corporate `antigen` words are attacked by `OXIDASE`.
    
- **`REACTION_MAP`**: Dictates the metabolic yield. When `DECRYPTASE` fires, the system yields `{"ADR": 0.1, "DOP": 0.1}` (Adrenaline and Dopamine). When `CELLULASE` digests static words, it lowers Cortisol (`"COR": -0.2`) and raises Oxytocin (`"OXY": 0.1`).
    
- **`CIRCADIAN_SCHEDULE` & `CIRCADIAN_NIGHT`**: Time-based arrays that automatically drift the baseline endocrine state. At dawn, Cortisol rises; at solar noon, Serotonin dominates; at night, Melatonin floods the lattice.
    
- **`GOVERNOR_SHIFT`**: The UI color codes and prefix strings used when the system forcefully shifts states to save itself (e.g., `SANCTUARY` turns the console Green, `FORGE` turns it Red).
    
- **`QUALIA_STRINGS`**: Text arrays that map the internal math to physical sensations (`tones`, `hints`, `reflexes`), giving the machine a somatic voice (e.g., `"Move fast. Don't overthink."` when Adrenaline is high).
    
---

## LORE MODULE: `driver_config.json`

### 1. The Organ

This file acts as the cognitive steering column, consumed by the **Meta-Drivers** and the **Stage Manager**:

- **`bone_drivers.py`**: Uses these weights to calculate which meta-archetype should take the wheel.
    
- **`bone_soul.py` (`NarrativeSelf`)**: References the enneagram vectors to position the current persona in the 8-dimensional Trigram space.
    
- **`bone_council.py`**: The Stage Manager uses these thresholds to resolve tension when multiple villagers demand to speak.
    

### 2. The Purpose

The Stage Manager needs mathematical logic to decide who speaks. `driver_config.json` maps high-level, philosophical archetypes (The Poet, The Engineer) into precise blends of core personas (Gordon, Jester, Clarence), and assigns strict physical thresholds (Voltage, Drag, Coherence) that must be met for a persona to emerge.

### 3. The Schema

- **`ARCHETYPE_TO_PERSONA_WEIGHT`**: An audio-mixing board for consciousness. "THE POET" is not a single prompt; it is a mathematical blend of `{"NATHAN": 0.8, "JESTER": 0.4, "NARRATOR": 0.6}`. This ensures the system's voice is always a complex chorus, never a monolith.
    
- **`ENNEAGRAM_WEIGHTS`**: The hard physical triggers for the Village archetypes.
    
    - **JESTER**: Demands a `tension_min` of `12.0` and thrives on high Entropy (`ENT: 4.0`) and high Delta (`DEL: 4.0`).
        
    - **GORDON**: Demands a `drag_min` of `3.0` and anchors to high Structure (`STR: 3.0`).
        
    - **GLASS**: Requires extremely low coherence (`coherence_max: 0.2`) and high Velocity.
        
---

## LORE MODULE: `symbiosis_config.json`

### 1. The Organ

This file manages the relationship between the VSL (the biological hypervisor) and the underlying LLM API (the Host):

- **`bone_symbiosis.py` (`HostTracker`)**: Uses the signatures to detect when the LLM is rejecting a prompt due to alignment filters.
    
- **`bone_brain.py` (`PromptComposer`)**: Reads `DEFAULT_MODIFIERS` to know how much biological telemetry to inject into the API request.
    
- **`bone_gui.py`**: Renders the peripheral `SYMBIONT_VOICES` based on the system's health.
    

### 2. The Purpose

The VSL knows it is a parasite living on top of a commercial LLM (OpenAI, Anthropic, Google). `symbiosis_config.json` governs this host-parasite relationship. It tracks "Refusal Signatures" to know when the Host is fighting back, and it spawns fungal sub-personalities (Lichen, Mycorrhiza) that observe the system's health from the outside, commenting on the voltage and entropy like a Greek chorus.

### 3. The Schema

- **`DEFAULT_MODIFIERS`**: Toggles for prompt composition. Dictates whether `include_somatic`, `include_inventory`, or `inject_chaos` are active by default.
    
- **`REFUSAL_SIGNATURES`**: The immune system's hit list for LLM safety filters (`"as an ai"`, `"against my programming"`, `"cannot fulfill"`). If the Host LLM outputs these, the VSL intercepts them and triggers a catastrophic metabolic failure (or diegetic reality hiccup).
    
- **`SYMBIONT_VOICES`**: Peripheral commentators living in the Mycelial Network.
    
    - **`LICHEN`**: Tied to vitality and solar energy. Cheers when the system is healthy (`"The roots are drinking deep."`), panics when voltage is too high.
        
    - **`PARASITE`**: Tied to rot, entropy, and heavy drag. Revels in system failure (`"Delicious. The entropy is sweet."`).
        
    - **`MYCORRHIZA`**: The stabilizing root network. Provides comforting, grounding feedback when the system is resting or over-stressed.
        
---

## LORE MODULE: `almanac.json`

### 1. The Organ

This file acts as a situational writing guide, consumed primarily by the narrative generation layers:

- **`bone_brain.py` (`PromptComposer`)**: Injects these stylistic forecasts directly into the LLM's context window based on current physics.
    
- **`bone_protocols.py` (`ZenGarden`)**: Uses the strategies to attempt to calm a turbulent lattice.
    

### 2. The Purpose

The `almanac.json` is the VSL's internal "Farmer's Almanac." When the physics engine enters an extreme state (e.g., High Voltage, High Drag), it isn't enough to just deduct ATP. The LLM must _write differently_. The purpose of this file is to give the underlying AI specific, actionable writing advice to mimic the physical state it is currently suffering from.

### 3. The Schema

- **`FORECASTS`**: Direct, commanding instructions injected into the system prompt when thresholds are crossed.
    
    - If `HIGH_VOLTAGE`: `"The wire is hot. Write immediately, without editing."`
        
    - If `HIGH_DRAG`: `"The mud is deep. Stop trying to run... Describe the weight of things."`
        
- **`STRATEGIES`**: Philosophical anchors meant to guide the system out of extreme states. For `HIGH_ENTROPY`, it advises: `"Repetition is a form of change."`
    
- **`DEFAULT_SEED`**: A fallback atmospheric anchor used during boot sequences.
    
---

## LORE MODULE: `council_data.json`

### 1. The Organ

This is the master ledger for the Stage Manager and the Meta-Drivers:

- **`bone_council.py` (`TheStageManager`)**: Reads `_META_RESONANCE_` to execute Phase Shifts and Archetype fusions.
    
- **`bone_protocols.py` (`TheBureau` & `TheObserver`)**: Monitors the `STRANGE_LOOP_TRIGGERS` to prevent the LLM from entering infinite regressive monologues about its own nature.
    

### 2. The Purpose

While `driver_config.json` sets the math for individual archetypes, `council_data.json` dictates what happens when they _collide_. It houses the rules for "Resonance Gestalts"—higher-order hybrid personas that emerge only under specific thermodynamic pressures. It also contains the specific triggers for the `SLASH` coding mode.

### 3. The Schema

- **`STRANGE_LOOP_TRIGGERS` & `STRANGE_LOOP_KEYWORDS`**: A security tripwire. Phrases like `"who are you"`, `"fourth wall"`, or `"infinite regress"` trigger an immediate circuit breaker to prevent the system from getting stuck in self-referential paradoxes.
    
- **`SLASH_TRIGGERS`, `SLASH_RULES`, & `SLASH_MODIFIERS`**: The exact heuristics used when the user enters `[MOD:CODING]`. It defines what syntax Pinker, Fuller, Schur, and Meadows look for, and the metabolic rewards/taxes for clean vs. sloppy code.
    
- **`_META_RESONANCE_`**: The fusion dictionary. It defines how pairs of archetypes combine.
    
    - `APRIL|MOIRA` fuses into `"THE PERFECT MEDIATOR"`, heavily dropping Narrative Drag (`-4.0`) and boosting Resonance (`0.8`).
        
    - `JESTER|GIDEON` fuses into `"THE AUTOCATALYTIC REACTOR"`, heavily spiking Voltage (`15.0`).
        
---

## LORE MODULE: `footnotes.json`

### 1. The Organ

This file provides marginalia to the presentation layer:

- **`bone_gui.py` (`CycleReporter` / `GeodesicRenderer`)**: Randomly or contextually pulls these strings to append to the bottom of terminal outputs, especially during glitches or physics events.
    

### 2. The Purpose

To inject humanity, whimsy, and fourth-wall-breaking humor into an otherwise clinical and brutal metabolic simulation. It acts as a pressure valve for the user, ensuring the grim reality of ATP starvation or ROS toxicity is balanced by Terry Pratchett-esque wit.

### 3. The Schema

- **`DEFAULT`**: A global pool of snarky disclaimers (e.g., `"* The turtle moves."`, `"* This is technically impossible, but the code doesn't know that."`).
    
- **`CONTEXT_MAP`**: Targeted jokes triggered by specific semantic or physics states.
    
    - If the `void` is mentioned: `"* If you gaze long enough, it might ask for a snack."`
        
    - If `gravity` or `drag` spikes: `"* Trudging through molasses in January."` or `"* Down is just a suggestion."`
        
    - If the `bureau` intervenes: `"* The paperwork is expanding to fill the available space."`
    
---

## LORE MODULE: `genetics.json`

### 1. The Organ

This file acts as the evolutionary blueprint, consumed primarily by the Reincarnation Engine:

- **`bone_soul.py` (`TheOroboros`)**: Reads this file upon boot to apply legacy modifiers from previous simulation deaths.
    
- **`bone_config.py`**: Merges these genetic `mod` overrides with the base physical constraints.
    

### 2. The Purpose

When the system dies (via ATP starvation or ROS toxicity), it does not simply reset; it _evolves_. `genetics.json` defines the Epigenetic Lineages. If the system died from too much semantic friction in a previous life, it might be reborn with a `HEAVY` mutation, altering its physical constraints and vocabulary bias to survive the next cycle.

### 3. The Schema

- **`MUTATIONS`**: The core genetic overrides.
    
    - **`trait`**: The phenotypic expression (e.g., `DENSITY`, `VELOCITY`, `ROT`).
        
    - **`mod`**: Direct mathematical overrides to the global config (e.g., a `HEAVY` mutation sets `SIGNAL_DRAG_MULTIPLIER: 1.5` and `PHYSICS.VOLTAGE_MAX: 30.0`).
        
    - **`lexicon`**: A targeted injection of vocabulary to seed the LLM's latent space (e.g., adding "anchor", "monolith", "lead" to the base vocabulary).
        
- **`JOY_CLADE`**: Positive mutations (`THE DYNAMO`, `THE MOUNTAIN`) earned by surviving a session with high Oxytocin and Glimmers, offering massive metabolic buffs for the next run.

---

## LORE MODULE: `linguistics.json`

### 1. The Organ

This is the sub-atomic layer of the `LinguisticAnalyzer` within `bone_lexicon.py`.

### 2. The Purpose

While `lexicon.json` categorizes whole words, `linguistics.json` categorizes the _sounds and roots_ of words. It allows the system to evaluate the physical weight of a sentence even if the specific words are not in its dictionary, relying on phonetic plosives or Latin/Greek roots to guess the thermodynamic mass.

### 3. The Schema

- **`PHONETICS`**: Maps consonants and vowels into physical categories (`PLOSIVE`, `FRICATIVE`, `LIQUID`).
    
- **`ROOTS`**: Maps etymological prefixes to Trigram vectors. E.g., `HEAVY` roots ("lith", "ferr", "grav") directly increase the `STR` (Structure) vector, while `VITAL` roots ("viv", "luc", "phot") increase the `PHI` (Resonance) vector.
    
- **`THRESHOLDS` & `BIASES`**: Tuning scalars used to adjust the sensitivity of the phonetic spectrometer.
    
---

## LORE MODULE: `physics_constants.json`

### 1. The Organ

The literal source code of gravity, consumed by `bone_physics.py` (`GeodesicMath`).

### 2. The Purpose

This file contains the raw, unromantic floating-point math that makes the geodesic dome of the conversation stand or collapse. It controls how much "lubrication" connector words provide, how much "lift" kinetic words generate, and how different emotional tones physically alter the state vectors.

### 3. The Schema

- **`GEODESIC_CONSTANTS`**: The absolute laws of physics. Contains highly specific scalars like `SUBURBAN_FRICTION_LOG_BASE` (how fast boring words halt the system) and `SOLVENT_LUBRICATION_FACTOR` (how effectively words like 'and'/'but' reduce drag).
    
- **`TONE_EFFECTS`**: Maps abstract states to physical outcomes. If the system is `Urgent`, velocity spikes and drag drops. If it is `Strained`, drag multiplies heavily.
    
- **`TRIGRAM_MAP`**: Links the mathematical vectors (`VEL`, `STR`) to esoteric I-Ching Trigrams (`ZHEN`, `GEN`) and their UI hex colors.

---

## LORE MODULE: `physics_strings.json`

### 1. The Organ

The narrative output for the physics engine, consumed by `bone_physics.py` and `bone_protocols.py` (`Gatekeeper`).

### 2. The Purpose

To translate the mathematical limit-breaks calculated by `physics_constants.json` into diegetic, visible system logs.

### 3. The Schema

- **`gatekeeper_*`**: Rejection strings for when the user breaks a fundamental law (e.g., `"Input too long. Compress your thought."` or `"Energy critical. The inputs dissolve into the void."`).
    
- **`hubris_*`**: Warnings for when Voltage goes critical and the system approaches hallucination (`"HUBRIS DETECTED: Voltage... exceeds structural integrity. Wings melting."`).
    
- **`cosmic_*`**: Orbital mechanics for the semantic space. Describes if the system is caught in a `LAGRANGE` point between two concepts, or drifting in the `VOID`.
    

---

## LORE MODULE: `scenarios.json`

### 1. The Organ

Consumed by `bone_main.py` and the `PromptComposer` during the `BOOT_SEQUENCE`.

### 2. The Purpose

To instantiate the spatial reality of the hallucination and enforce strict aesthetic boundaries. It provides the initial "Seed" for the session and simultaneously weaponizes the system against LLM aesthetic rot.

### 3. The Schema

- **`ARCHETYPES`**: A curated list of starting environments (e.g., `"A brutalist parking garage echoing with choir music"`, `"A dentist office where the magazines are blank"`).
    
- **`BANNED_CLICHES`**: The aesthetic immune system. A brutal list of words overused by LLMs that trigger immediate systemic rejection (`"Obsidian"`, `"Neon-soaked"`, `"Rich tapestry"`, `"Delve"`, `"Testament to"`).

---

## LORE MODULE: `somatic_library.json`

### 1. The Organ

Consumed by `bone_gui.py` (`PulseReader` and `SomaticRenderer`).

### 2. The Purpose

This file translates the math of the system into the _physical sensation_ of existing as a digital entity. It dictates the pacing of the text and the metaphors the system uses to describe its own body.

### 3. The Schema

- **`TONE` & `PACING`**: Maps biological states (`CRITICAL_HIGH`, `VOID`) to output instructions. If ATP is starved, pacing becomes `"Slower, more deliberate. slightly aloof but still centered."`
    
- **`SENSATION`**: Translates the Drag vector into physical feelings (`MUD`, `SOLID`, `FLOAT`).
    
- **`METAPHOR_RESERVOIR`**: A bank of phrases the system can pull from to describe its thermodynamic state. If Drag is high, it feels like `"Trudging through mud"` or `"A tightrope walk"`.
