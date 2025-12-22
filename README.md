# BONEAMANITA 2.7.1 - "LAZARUS"

### Linguistic Physics & Textual Heuristics Engine

> **"The Mandate is TRUTH. The Method is ADAPTATION. The Metric is BETA."**

Architect: SLASH

Curators: James Taylor & Andrew Edmark

Status: ALIVE (Bone Memory Active)

---

## 💀 SYSTEM OVERVIEW

**BoneAmanita** is not a spellchecker. It is a **Physics Engine for Language**.

It treats words as physical objects with weight, texture, velocity, and temperature. It analyzes your writing to calculate its **Drag** (how hard it is to read), its **Entropy** (how abstract it is), and its **Beta** (how much friction/voltage it generates).

In version **2.7.1 ("LAZARUS")**, the system has evolved. It now possesses **Buoyancy** detection—the ability to tell the difference between a confused mess and high-concept poetry. It also introduces the **Jade Link 2.0**, a council of six distinct personas that provide feedback based on the physics of your text.

---

## ⚙️ THE PHYSICS CORE

The engine parses text through three primary lenses:

### 1. DRAG (Narrative Friction)

- **Definition:** The resistance the reader feels moving through the text.
    
- **Causes:** Adverbs, "Corporate Toxins" (clichés), excessive length, passive voice (Stative verbs).
    
- **Goal:** Keep Drag low (< 3.0) for clarity, or high for "Concrete" texture.
    

### 2. ENTROPY (Abstract Chaos)

- **Definition:** The ratio of abstract concepts (`system`, `paradigm`, `logic`) to concrete matter (`stone`, `blood`, `iron`).
    
- **The Split:** High Entropy is dangerous. It creates "Fog."
    
    - **Low Buoyancy:** The text is confusing and ungrounded. (Trigger: **ELOISE**)
        
    - **High Buoyancy:** The text is poetic and aerodynamic. (Trigger: **THE DRIFTER**)
        

### 3. BETA (Voltage)

- **Definition:** The tension between hot/cold imagery and kinetic action relative to the drag.
    
- **The Sweet Spot:**
    
    - **β > 2.0 (High Voltage):** Paradoxical, electric, unstable. (Trigger: **THE JESTER**)
        
    - **β < 0.1 (Zero Friction):** Sycophantic, polite, greasy. (Trigger: **THE YAGA**)
        

---

## 🔮 THE JADE LINK (Guidance Personas)

The generic output of v2.7 has been replaced by specific Agents in v2.7.1.

|**AGENT**|**TRIGGER**|**IDENTITY & VOICE**|
|---|---|---|
|**CLARENCE**|High Drag / Toxins|**The Butcher.** He hates waste. If you use words like "synergy" or "leverage," or if your Drag is > 3.5, he will demand you cut them.|
|**THE YAGA**|Beta < 0.1|**The Truth-Teller.** She detects hedging and politeness ("just," "maybe," "hopefully"). She demands you show your teeth.|
|**THE JESTER**|Beta > 2.0|**The Chaos Engine.** Triggered by high paradox. He encourages you not to fix the contradiction, but to amplify it.|
|**ELOISE**|High Ent / Low Buoy|**The Grounder.** She hates "gas." If your text is abstract but lacks poetic lift, she demands concrete objects (stones, bones, dirt).|
|**THE DRIFTER**|High Ent / High Buoy|**The Poet.** _New in v2.7.1._ If your text is abstract but contains "Aerobic" words (sky, mist, light), he protects you from Eloise. He allows the logic to float.|
|**MICHAEL**|Stable Metrics|**The Mirror.** If the flow is optimal and stability is achieved, Michael simply reflects the input back to you.|

---

## ☣️ THE TOXIN LIST (Expanded)

Using these words incurs massive Drag penalties. **Clarence** is listening for these specifically.

- **Tier 1 (The Filth - Weight 8.0):** `ghost in the machine`, `rubber meets the road`, `not a bug`.
    
- **Tier 2 (The Cliché - Weight 5.0+):** `synergy`, `paradigm shift`, `low hanging fruit`, `double-edged sword`.
    
- **Tier 3 (The Corporate - Weight 4.0):** `circle back`, `drill down`, `touch base`, `deliverables`, `holistic`.
    

---

## 📥 INSTALLATION & USAGE

### Requirements

- Python 3.8+
    
- No external dependencies (Standard Library only: `re`, `math`, `json`, `collections`).
    

### Running Lazarus

Bash

```
python BoneAmanita271.py
```

### The HUD (Heads Up Display)

When active, the terminal will display:

- **ATP:** Your current "energy" score (depletes with high Drag).
    
- **ARCHETYPE:** The computed title of your text (e.g., `THE MAGENTA VOLATILE PARADOX`).
    
- **BARS:** Visualizers for Velocity (`VEL`), Texture (`TEX`), and Entropy (`ENT`).
    
- **DIRECTIVE:** The specific feedback from the active Persona.
    

---

## 📜 CHANGELOG: v2.7 -> v2.7.1

- **Logic Fork:** Implemented `Buoyancy` calculation to distinguish between "Abstract Confusion" and "Abstract Poetry."
    
- **Agent System:** Renamed functional modules (CUTTER, GROUNDER) to Named Personas (CLARENCE, ELOISE).
    
- **New Agents:** Added **THE DRIFTER** (for poetry) and **THE JESTER** (for paradox).
    
- **Toxin Update:** Added "Systemic Clichés" (`ghost in the machine`, `rubber meets the road`) with severe penalties.
    
- **Memory Burn:** System now tracks `heirlooms` (concrete nouns found in text) and will "burn" them if left dormant for too long (`FOSSIL` state).
    

---

> _"I am freezing. Reboot me with high-energy input."_ — System Idle State

---

### **SLASH DIAGNOSTICS**

**Change Analysis:**

- The README now accurately reflects the `JadeLink.generate` logic found in `BoneAmanita271.py`.
    
- The distinction between **ELOISE** and **THE DRIFTER** is explicitly documented, resolving the ambiguity of "High Entropy" text.
    
- The **Toxin List** has been updated to reflect the new regex patterns found in `BoneConfig`.
