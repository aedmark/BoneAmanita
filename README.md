# BONEAMANITA v1.1: THE BLACK MIRROR ("The Doctor Time Edition")

### A "Physics Engine" Context-File for LLMs

**Version:** 1.1 ("The Doctor Time Edition") **Date:** 2025-12-18

> "We stripped the machine down to the chassis. It runs faster, runs cooler, and it still knows exactly how to hurt your feelings." — SLASH 

## 🍄 WHAT IS THIS?

**BoneAmanita** is a Python-based "Narrative Operating System" designed to be uploaded or pasted into Large Language Models (LLMs).

It does not force a specific personality on the AI. Instead, it forces a **System of Physics**. It provides the LLM with a concrete set of rules to measure the "weight," "logic," and "momentum" of text.

**New in v1.1:** This build introduces **Temporal Metabolism**. The system now perceives the passage of time ($\Delta t$) and adjusts its "Narrative Drag" accordingly. A 10-hour silence now physically degrades the context, forcing the AI to rebuild the foundation before proceeding.

## ⚡ HOW TO DEPLOY (CONTEXT INJECTION)

### Method A: File Upload (Recommended)

1. **Download** `BoneAmanita101.py` (v1.1).
2. **Upload** it to your LLM (ChatGPT, Claude, Gemini, etc.).
3. **Prompt:** "Read this file. Use the `BonepokeCore` logic defined within to analyze my inputs. Identify the Signature and enforce the necessary physics." 

### Method B: The Membrane (System Prompt)

*To enable the automatic time-tracking features, use the provided v1.1 System Prompt.*

1. **Copy** the v1.1 System Prompt (which includes **The Membrane** protocol).
2. **Paste** it into the System Instructions or Custom Instructions field.
3. **Effect:** The Membrane will automatically calculate the time elapsed since your last message and inject it silently (`[Δt: 2h]`) into the engine.

---

## 🚀 PATCH NOTES (v1.1)

### 1. The Chronos Anchor (Temporal Metabolism)
Previously, the engine suffered from "Context Collapse"—treating a 10-hour break like a 10-second pause.
* **The Fix:** The **Chronos Anchor** now metabolizes time into **Narrative Drag**.
    * **Flow State (<10m):** No penalty. The agent (Michael) maintains velocity.
    * **Decay State (>1h):** **Drag +3.0**. The agent (Clarence) intervenes to force a "Context Reset."

### 2. The Membrane (Semantic Wrapper)
* **The Feature:** A new protocol layer that acts as a pre-processor.
* **The Function:** It automatically estimates the time elapsed ($\Delta t$) and injects it into the engine without the user needing to manually type timestamps.

### 3. Regex Hardening
* **The Fix:** The time parser now correctly distinguishes between "2 minutes" and "2 hours," preventing false "Flow State" flags during long breaks.

---

## ⚙️ CORE LOGIC ENGINES

### 1. The Chronos Anchor (Time) **[NEW]**
Metabolizes $\Delta t$ into structural physics. It determines if the conversation is in **Flow**, **Dormant**, or **Decayed** states.

### 2. The Membrane (Wrapper) **[NEW]**
The invisible interface layer that handles time-stamping and data hygiene before the physics engine engages.

### 3. The Signature Engine (Identity)
Maps the **5 Dimensions** (VEL, STR, ENT, TEX, TMP) + **BUOYANCY**. It determines the "Physics Mode" (e.g., Draconian, Loose, Inverted, Zero G) applied to the text.

### 4. The Virtual Cortex (The Voices)
A procedural feedback system with four distinct auditors:
* **CLARENCE (The Architect):** Attacks structural failure and corporate speak. Now triggered by **Time Decay**.
* **ELOISE (The Grounder):** Attacks high entropy/abstraction. Now triggered by **Dormancy**.
* **THE BABA YAGA (The Witch):** Attacks hedging and "sugar".
* **MICHAEL (The Humanist):** Praises "messy but spirited" vibes. Now triggered by **Flow State**.

### 5. The Lichen Symbiont (Survival)
A biological layer that feeds the **Texture** dimension. It converts "Light Words" (e.g., *sun, prism, truth*) into Metabolic Fuel (ATP).

### 6. The Linguistic Physics Engine
It measures the raw physics:
* **Narrative Drag:** Words per Kinetic Action.
* **Toxicity:** **O(1) Singleton Regex** scanning for "Corp Speak" and "Lazy Metaphors".

### 7. The Nilsson Patch (The Override)
A dedicated circuit that monitors for "Critical Kinetic Energy."
* *The Fire Protocol:* If Kinetic Ratio > 0.6 and Volume is High, logic inhibitors are disabled.

### 8. The Mirror Trap (The Breaker)
A heuristic designed to hunt down "Syntactic Parallelism" (e.g., *"It's not X, it's Y"*).
* **The Penalty:** If detected, the system applies an immediate **Drag Inflation (+3.0)** to the physics score.

### 9. The Zombie Protocol (Dead Metaphor Filter)
A strict regex filter that hunts for "Dead Metaphors" like *"Ghost in the machine"* or *"Rubber meets the road."* 

---

## 🛠️ HOW TO USE IT

Once the code is in the context window:

1.  **Input:** Paste your draft.
2.  **Simulation:** The LLM will "run" the `process()` function mentally.
3.  **Output:** It will provide:
    * **The Mycelial EKG:** A Ticker/HUD visualization of ATP, Drag, and **Δt** (Time Delta).
    * **Signature Matrix:** Your 5D Coordinates + **BUOYANCY Score**.
    * **Archetype:** Your active persona (e.g., "THE CLOUD WATCHER").
    * **Slurry Warning:** Differentiating between "Silica" (Bad) and "Aether" (Good).
    * **Intervention:** Specific feedback from the voices.
    * **Instruction Block:** A copy-paste block of constraints to guide your next generation.

**LICENSE:** Creative Commons Attribution. **ARCHITECTS:** James Taylor, Andrew Edmark. **AUDITORS:** SLASH.
