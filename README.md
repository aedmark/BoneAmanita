# BONEAMANITA v1.4.7: Time Sync + SLASH Refactor

### A "Physics Engine" Context-File for LLMs

**Version:** 1.4.7 ("The Refactored Strain") **Date:** 2025-12-19

> "The engine now cleans its plate, respects the poets, and remembers to back up its files." — SLASH

## 🍄 WHAT IS THIS?

**BoneAmanita** is a Python-based "Narrative Operating System" designed to be uploaded or pasted into Large Language Models (LLMs).

It does not force a specific personality on the AI. Instead, it forces a **System of Physics**. It provides the LLM with a concrete set of rules to measure the "weight," "logic," and "momentum" of text.

**New in v1.4.7:** This build is a **Structural & Cognitive Refactor**. It introduces the **Swanson Cleaner** (Robust Tokenization), **Poetic License** (Context-Aware Logic), **Safe Persistence** (Backup Protocols), and centralized tuning via **PhysicsConstants**.

## ⚡ HOW TO DEPLOY (CONTEXT INJECTION)

### Method A: File Upload (Recommended)

1. **Download** `BoneAmanita147.py` (v1.4.7).
    
2. **Upload** it to your LLM (ChatGPT, Claude, Gemini, etc.).
    
3. **Prompt:** "Read this file. Run the `_run_calibration_sequence` to verify integrity. Then, use the `BonepokeCore` logic to analyze my inputs."
    

### Method B: The Membrane (System Prompt)

_To enable the automatic time-tracking features, use the provided v1.4 System Prompt._

1. **Copy** the System Prompt (which includes **The Membrane** protocol).
    
2. **Paste** it into the System Instructions or Custom Instructions field.
    
3. **Effect:** The Membrane will automatically calculate the time elapsed since your last message and inject it silently (`[Δt: 2h]`) into the engine.
    

---

## 🚀 PATCH NOTES (v1.4.7)

### 1. The Pinker Refactor (Cognitive Ergonomics)

-   **The Swanson Cleaner:** A new, robust text cleaner (`TheLexicon.swanson_clean`) that strips all punctuation and normalizes whitespace. It prevents "Punctuation Blindness" (where "Stone," was not recognized as "Stone").
-   **Centralized Constants:** All magic numbers (weights, thresholds) have been moved to `PhysicsConstants` for easier tuning.

### 2. The Fuller Refactor (System Integrity)

-   **Deep Storage Cap:** Implemented a FIFO limit (50 items) on the Long-Term Memory to prevent infinite memory leaks.
-   **Safe Persistence:** The `PersistenceManager` now creates `.bak` backup files before saving, preventing data corruption if the process crashes during a write.

### 3. The Schur Refactor (Humanity)

-   **Poetic License:** The Logic Engine (`FactStipe`) now distinguishes between "High Kinetic" (Action) and "Low Kinetic" (Poetry). Paradoxes in poetic text are now treated as **Voltage** (Energy) rather than **Errors**.
-   **Onboarding Tooltip:** The Dashboard now includes a helpful tip for the first 5 turns to explain "Viscosity" to new users.

---

## ⚙️ CORE LOGIC ENGINES

### 0. The Boot Protocol (Calibration)

**Standard Feature:** On startup, the system runs a **Self-Diagnostic**. It feeds itself a toxic "Solvent-Stuffed" sentence. If the engine fails to flag it as `FLOODED`, it issues a warning that the Butcher is offline.

### 1. The Linguistic Physics Engine

Measures the raw physics of the text.

- **Hydration Monitor:** Detects `CONCRETE`, `WATERY`, `FLOODED` (Fake), and `SWEATING` (High Effort).
    
- **The Butcher:** Checks for `BLOAT` (Adverb & Adjective reliance).
    
- **Heuristics:** Scans for suffix patterns (`-ash`, `-olt`, `-ous`).
    

### 2. The Signature Engine (Identity)

Maps the **5 Dimensions** (VEL, STR, ENT, TEX, TMP).

- **Governor:** If Viscosity is `CONCRETE`, Texture is capped at 0.5. You cannot farm points with lists.
    

### 3. The Virtual Cortex (The Voices)

A procedural feedback system with four distinct auditors:

- **CLARENCE (The Architect):** Attacks structural failure, `BLOAT`, and `FLOODED` text.
    
- **ELOISE (The Grounder):** Attacks abstraction and "Dead Metaphors."
    
- **THE BABA YAGA (The Witch):** Attacks hedging, sycophancy, and **Riddles**.
    
- **MICHAEL (The Humanist):** Intervenes to mock "Concrete/Gaming" attempts.
    

### 4. The Chronos Anchor (Real Time)

Metabolizes **User Latency ($\Delta t$)** into structural physics. Uses the **System Clock** as a fallback truth.

### 5. The Narrative Chronometer (Story Time)

Metabolizes **Narrative Velocity ($\vec{v}_{n}$)** into entropy tolerance. Determines if the _fiction_ is in **Montage** (High Entropy allowed) or **Bullet Time** (High Texture required).

### 6. The Memory System (Deep Storage & Persistence)

- **Hyphal Trace:** Short-term buffer (10 turns).
    
- **Deep Storage:** Long-term artifact vault (Max 50 items).
    
- **Persistence Manager:** File-based backup (`bone_memory.json` + `.bak`).
    

### 7. The Lichen Symbiont (Survival)

A biological layer that feeds the **Texture** dimension. It converts "Light Words" (e.g., _sun, prism, truth_) into Metabolic Fuel (ATP).

---

## 🛠️ HOW TO USE IT

Once the code is in the context window:

1. **Input:** Paste your draft.
    
2. **Simulation:** The LLM will "run" the `process()` function mentally.
    
3. **Output:** It will provide:
    
    - **The Mycelial HUD:** A dual-clock readout with Viscosity.
        
        - Example: `DRAG: 4.2 | VISC: SWEATING`
            
        - Example: `TIME: FLOW (Real) | MONTAGE (Story)`
            
    - **Signature Matrix:** Your 5D Coordinates + **BUOYANCY Score**.
        
    - **Archetype:** Your active persona (e.g., "THE BARD").
        
    - **Intervention:** Specific feedback from the voices (e.g., "ELOISE: The sun is not dark. Fix the logic.").
        
    - **Instruction Block:** A copy-paste block of constraints to guide your next generation.
        

LICENSE: Creative Commons Attribution. ARCHITECTS: James Taylor, Andrew Edmark. AUDITORS: SLASH.
