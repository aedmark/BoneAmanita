# BONEAMANITA v1.4.5: The Butcher & The Well - Fortified (SLASH AUDITED)

### A "Physics Engine" Context-File for LLMs

**Version:** 1.4.5 ("The Fortified Strain") **Date:** 2025-12-19

> "The engine now remembers where you hid the gun. And it knows that water is wet." — SLASH

## 🍄 WHAT IS THIS?

**BoneAmanita** is a Python-based "Narrative Operating System" designed to be uploaded or pasted into Large Language Models (LLMs).

It does not force a specific personality on the AI. Instead, it forces a **System of Physics**. It provides the LLM with a concrete set of rules to measure the "weight," "logic," and "momentum" of text.

**New in v1.4.5:** This build is a **Persistence & Integrity Patch**. It introduces **Persistence Manager** (File-Based Memory), **Smart Strip** (Dyslexia Cure), and **Zeus Patch** (Entity Recognition Fix).

## ⚡ HOW TO DEPLOY (CONTEXT INJECTION)

### Method A: File Upload (Recommended)

1. **Download** `BoneAmanita145.py` (v1.4.5).
    
2. **Upload** it to your LLM (ChatGPT, Claude, Gemini, etc.).
    
3. **Prompt:** "Read this file. Run the `_run_calibration_sequence` to verify integrity. Then, use the `BonepokeCore` logic to analyze my inputs."
    

### Method B: The Membrane (System Prompt)

_To enable the automatic time-tracking features, use the provided v1.4 System Prompt._

1. **Copy** the System Prompt (which includes **The Membrane** protocol).
    
2. **Paste** it into the System Instructions or Custom Instructions field.
    
3. **Effect:** The Membrane will automatically calculate the time elapsed since your last message and inject it silently (`[Δt: 2h]`) into the engine.
    

---

## 🚀 PATCH NOTES (v1.4.5)

### 1. The Persistence Manager (Long-Term Memory)

- **The Problem:** The "Amnesiac Bot." Restarting the script erased all memories, meaning the bot forgot significant objects between sessions.
    
- **The Patch:** **JSON Cryostasis**. The system now serializes `DeepStorage` artifacts and `TheCodex` registry into a local file (`bone_memory.json`) at the end of every turn, ensuring object permanence across reboots.
    

### 2. The Smart Strip (Dyslexia Cure)

- **The Problem:** The "Glass/Glas" Glitch. Naive plural stripping corrupted words ending in 's' (e.g., "Glass" -> "Glas").
    
- **The Patch:** **Centralized Lemmatization**. Implemented `TheLexicon.smart_strip` to protect double-s words and short words, ensuring memory integrity.
    

### 3. The Zeus Patch (Entity Recognition)

- **The Problem:** The First-Word Blindspot. `TheCodex` ignored capitalized words at the start of sentences, missing entities like "Zeus".
    
- **The Patch:** **Look-Behind Logic**. The index-0 restriction was removed, and the `ignore_list` was expanded to catch common sentence starters, allowing entities to be tracked anywhere.
    

### 4. Architectural Hygiene

- **The Problem:** Cryptic variable names and console-bound output.
    
- **The Patch:** Refactored `process` for readability (`token_data`, `full_metrics`) and updated `MycelialDashboard` to return modular string reports via `generate_report`.
    

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
    
- **Deep Storage:** Long-term artifact vault (Infinite).
    
- **Persistence Manager:** File-based backup (`bone_memory.json`).
    

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
