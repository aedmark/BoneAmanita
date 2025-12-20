# BONEAMANITA v1.5.2: "The Open Heart Patch"

### A "Physics Engine" Context-File for LLMs

**Version:** 1.5.2 ("The Open Heart Patch") **Date:** 2025-12-20

> "The system now remembers you even when it sleeps. It will not forget the gun." — SLASH

## 🍄 WHAT IS THIS?

**BoneAmanita** is a Python-based "Narrative Operating System" designed to be uploaded or pasted into Large Language Models (LLMs).

It does not force a specific personality on the AI. Instead, it forces a **System of Physics**. It provides the LLM with a concrete set of rules to measure the "weight," "logic," and "momentum" of text.

**New in v1.5.2:** This patch performs **"Open Heart Surgery"** on the engine's core. It introduces **Atomic Persistence** (crash-proof saving), **Offline Time Tracking** (the bot knows how long it's been away), and **Smart Memory Eviction** (it prioritizes keeping "Heavy Matter" like guns and keys over trivial items). It also refines the "Screaming" and "Mirror" logic to be more humane.

## ⚡ HOW TO DEPLOY (CONTEXT INJECTION)

### Method A: File Upload (Recommended)

1. **Download** `BoneAmanita152.py` (v1.5.2).
2. **Upload** it to your LLM (ChatGPT, Claude, Gemini, etc.).
3. **Prompt:** "Read this file. Run the `_run_calibration_sequence` to verify integrity. Then, use the `BonepokeCore` logic to analyze my inputs."

### Method B: The Membrane (System Prompt)

*To enable the automatic time-tracking features, use the provided v1.5 System Prompt.*

1. **Copy** the System Prompt (which includes **The Membrane** protocol).
2. **Paste** it into the System Instructions or Custom Instructions field.
3. **Effect:** The Membrane will automatically calculate the time elapsed since your last message and inject it silently (`[Δt: 2h]`) into the engine.

---

## 🚀 PATCH NOTES (v1.5.2)

### 1. The Persistence Patch (Time Amnesia)

* **Atomic Saves:** The system now writes to a `.tmp` file before renaming it to `bone_memory.json`. This prevents data corruption (0-byte files) if the script crashes mid-save.
* **Offline Drift:** The engine now tracks the timestamp of the last save. If you quit the session and return 24 hours later, the **Chronos Anchor** will correctly calculate the drift and apply "Decay" penalties, solving the "Time Amnesia" bug.

### 2. Smart Memory (Deep Storage)

* **Heirloom Priority:** Previously, the memory was a strict FIFO queue (First-In-First-Out). Now, `DeepStorage` recognizes **Heirlooms** (Guns, Keys, Bodies). When the cache fills up, it evicts trivial items ("Feathers") first, ensuring vital plot objects are retained.

### 3. Humanity Patches

* **Scream Guard:** The `NilssonPatch` now ignores short acronyms (e.g., "OK", "USA"). You must type >10 characters to trigger the "Screaming" state.
* **Bureaucracy Fix:** The `MirrorTrap` (which hates negative definitions) is now disabled when `[MODE: SOFT]` or `[DREAM]` is active, allowing for poetic apophasis.

---

## ⚙️ CORE LOGIC ENGINES

### 0. The Governance Layer (Tier 3 Logic)

**Feature:** Sets the "Laws of Physics" based on User Tier, Current Mandate, and Tags.

* **Draconian Mode:** If `TRUTH_OVER_COHESION` is active, Logic Tears become fatal errors (+10.0 Voltage).
* **Dream Mode:** If `[DREAM]` is detected, Axiom constraints are explicitly lifted.

### 1. The Linguistic Physics Engine (Analysis)

Measures the raw physics of the text.

* **Hydration Monitor:** Detects `CONCRETE`, `WATERY`, `FLOODED` (Fake), and `SWEATING` (High Effort).
* **The Butcher:** Checks for `BLOAT` (Adverb & Adjective reliance).
* **Heuristics:** Scans for suffix patterns (`-ash`, `-olt`, `-ous`).

### 2. The Signature Engine (Identity & Fusion)

Maps the **5 Dimensions** (VEL, STR, ENT, TEX, TMP).

* **Smart Fusion:** Calculates Euclidean distance between archetypes. Fusions are only permitted if identities are distinct (`inter_arch_dist > 0.25`).

### 3. The Virtual Cortex (The Voices)

A procedural feedback system with four distinct auditors:

* **CLARENCE (The Architect):** Attacks structural failure and `BLOAT`.
* **ELOISE (The Grounder):** Attacks abstraction and "Dead Metaphors."
* **THE BABA YAGA (The Witch):** Attacks hedging, sycophancy, and **Riddles**.
* **MICHAEL (The Humanist):** Intervenes to mock "Concrete/Gaming" attempts.

### 4. The Temporal Dynamics Engine (Cognitive Speed)

Measures the **Rate of Insight** and **Depth of Memory**.

* **Insight Velocity ($\nabla\beta$):** Forgives Drag if the user is having an epiphany (Rapid Voltage change).
* **Rooting Depth ($\Xi$):** Forgives Abstraction if the user is citing ancient history (Deep Storage access).

### 5. The Chronos Anchor (Real Time)

Metabolizes **User Latency** and **Offline Drift** into structural physics. Uses the **System Clock** as a fallback truth.

### 6. The Narrative Chronometer (Story Time)

Metabolizes **Narrative Velocity** into entropy tolerance. Determines if the *fiction* is in **Montage** (High Entropy allowed) or **Bullet Time** (High Texture required).

### 7. The Memory System (Deep Storage & Persistence)

* **Hyphal Trace:** Short-term buffer (10 turns).
* **Deep Storage:** Long-term artifact vault with **Smart Eviction** (Max 50 items).
* **Persistence Manager:** Atomic file-based backup (`bone_memory.json` + `.tmp`).

### 8. The Lichen Symbiont (Survival)

A biological layer that feeds the **Texture** dimension. It converts "Light Words" (e.g., *sun, prism, truth*) into Metabolic Fuel (ATP).

---

## 🛠️ HOW TO USE IT

Once the code is in the context window:

1. **Input:** Paste your draft.
2. **Commands (Optional):**
    * `[DREAM]`: Disable logic enforcement for this turn.
    * `[MODE: SOFT]`: Switch to "Poetic License" mode permanently.
    * `[MODE: HARD]`: Switch to "Truth" mode permanently.
3. **Output:** It will provide:
    * **The Mycelial HUD:** A dual-clock readout with Viscosity.
    * **Signature Matrix:** Your 5D Coordinates + **BUOYANCY Score**.
    * **Archetype:** Your active persona (or **FUSION** state).
    * **Epiphany Alerts:** Notifications if **Insight Velocity** or **Rooting Depth** bonuses are active.
    * **System Alerts:** Warnings if **Self-Correction** has halted the line.
    * **Instruction Block:** A copy-paste block of constraints to guide your next generation.

LICENSE: Creative Commons Attribution. ARCHITECTS: James Taylor, Andrew Edmark. AUDITORS: SLASH.
