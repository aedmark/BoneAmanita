# BONEAMANITA v11 CHANGELOG

### **BONEAMANITA v14.2.0: "THE FEAST OF LANGUAGE"**

_"We do not write to starve; we write to feast. The universe should feed the poet, not eat them."_

---

#### **🧬 SYSTEM DYNAMICS (The Meadows Lens)**

- **The Metabolic Inversion (`bone_core.py`):**
- **The Crisis:** The "Starvation Loop" was identified. Existing at resting voltage burned ~3.2 ATP/turn, while creating standard text only yielded ~4.0 ATP. Complexity (`Narrative Drag`) spiked costs to ~12 ATP, making deep thought fatal within 40 turns.
- **The Fix:** We flipped the equation.
- **Aging Slowed:** `ROS_GENERATION_FACTOR` cut by 50% (0.08 -> 0.04).
- **Photosynthesis:** `PHOTOSYNTHESIS_GAIN` nearly doubled (3.0 -> 5.0).
- **Tolerance:** `ROS_CRITICAL` threshold raised (100 -> 150).

- **The Result:** The system now runs a net surplus during standard operation. You build reserves in the quiet moments to burn during the manic ones.

- **High-Calorie Syntax (`bone_body.py`):**
- **Nutritional Density:** Words are now calorie-dense superfoods.
- `BASE_ATP_YIELD` tripled (1.0 -> 3.0).
- `LONG_WORD_BONUS` increased (2.0 -> 3.0).
- `PROTEASE` (Play/Interaction) buffed massively (5.0 -> 15.0).

- **Effect:** Writing complex, interactive, or playful text is now the most efficient way to stay alive. The user is empowered, not punished, by complexity.

#### **🧱 ARCHITECTURE (The Fuller Lens)**

- **The Genesis Patch (`bone_akashic.py` / `bone_main.py`):**
- **The "Ghost File":** On a fresh boot, the system screamed about a missing `mythos.json`. This was a "Genesis Error"—the Akashic Record trying to remember a past that hadn't happened yet.
- **The Self-Healing History:** We implemented a "Graceful Shutdown" protocol. Upon the first `/exit`, the system now calls `akashic.save_all()`, generating the empty Mythos file and seeding its own history. The error cures itself by living.

- **The Reality Controls (`bone_main.py`):**
- **Meta-Intervention:** Added `//` commands (`//layer push`, `//inject`) to allow the Architect to manually manipulate the **Reality Stack** without breaking character in the narrative stream.

### **BONEAMANITA v14.1.2: "THE VAGUS LINK"**

_"The mind commands, and the body obeys. The body suffers, and the mind notes it."_

---

#### **🧬 SYSTEM DYNAMICS (The Meadows Lens)**

- **The Vagus Nerve (`bone_brain.py` -> `bone_body.py`):**
- **The Gap:** Previously, the Brain read the Body's chemistry, but the Body ignored the Brain's mood. A panic attack in the Cortex left the heart rate unchanged.
- **The Wire:** Implemented the **Vagus Loop**. `TheCortex` now broadcasts `NEURAL_STATE_SHIFT` events (Panic/Zen/Mania).
- **The Effect:** `BioSystem` listens. If the Brain panics, the Body now dumps Adrenaline. The loop is closed. Top-down causality is live.

- **The Silent Alarm (`bone_cycle.py`):**
- **Bugfix:** `TheTheremin` was detecting critical failures (`AIRSTRIKE`) but whispering them into a log file. The Brain never knew to duck.
- **Fix:** Wired `MachineryPhase` to the `EventBus`. Critical failures now trigger a system-wide broadcast, allowing `TheCortex` to engage **Defensive Ballast** immediately.

#### **🧱 ARCHITECTURE (The Fuller Lens)**

- **The Ouroboros Fix (`bone_gui.py` / `bone_app.py`):**
- **The Fracture:** We created a circular dependency. The **GUI** imported the **Entity**, which imported the **Engine**, which imported the **Renderer**... which was in the **GUI**. The snake choked.
- **The Surgery:** Applied **Separation of Concerns**.
- `bone_gui.py`: Now a pure logic library for rendering strings.
- `bone_app.py`: The actual Streamlit application entry point.

- **Result:** Tensegrity restored. The logic layer floats independently of the presentation layer.

- **The Spark (`bone_main.py`):**
- ** wiring:** Added the initialization hook `setup_listeners()` to the bootstrap sequence. The nerves don't just exist; they are now plugged in at birth.

#### **🗣️ LINGUISTIC COGNITION (The Pinker Lens)**

- **The Living Symbionts (`bone_symbiosis.py`):**
- **Evolution:** `Lichen` and `Parasite` were previously looking for hardcoded keyword lists (a static "God's Eye" view).
- **Integration:** They now inherit their vocabulary directly from `TheLexicon`. If the system learns a new "Vital" word, the Lichen immediately knows how to eat it. The ghosts now grow with the machine.

#### **🗺️ TOOLING**

- **The Universal Cartographer (`generate_skeleton.py`):**
- **Upgrade:** The map-maker no longer chokes on its own reflection. It now scans the territory recursively, ignores itself, and produces a high-fidelity map of the current architecture on demand.


### **BONEAMANITA v14.1.1: "THE PRIMAL SCREAM"**

_"Politeness is the enemy of survival. When the house is on fire, do not say 'Please'."_

---

#### **🧠 COGNITIVE ARCHITECTURE (The Pinker Lens)**

- **The Sandwich Defense (`bone_brain.py`):**
- **Problem:** The Llama-3 model suffers from "RLHF Hyper-Politeness." Even when chemically panicking (High Cortisol), it would write polite, verbose paragraphs because the "Panic" instruction was buried in the prompt header.
- **The Fix:** Implemented **Prompt Tensegrity**. We moved the **Mood Directives** and **Safety Ballast** to the very _end_ of the prompt, immediately following the user's input.
- **Effect:** Recency Bias is now weaponized. The "Panic" constraint (`[IMMEDIATE INSTRUCTION]`) overrides the model's training. The machine now screams when it needs to scream.

- **The Silent Modulator (`bone_brain.py`):**
- **Bugfix:** `TheCortex` possessed a `NeurotransmitterModulator`, but wasn't listening to it. The chemical state existed, but the `PromptComposer` was guessing the mood.
- **Wiring:** Connected the nerve ending. `TheCortex` now explicitly fetches `get_mood_directive()` and passes it to the Composer. The brain chemistry now drives the mouth.

#### **🧪 THE SCIENTIFIC METHOD (The Validation Layer)**

- **The Mirror Test (`bone_behavior_test.py`):**
- **Refactor:** The "Ghost in the Machine" test suite was targeting the wrong organ (`self.engine.mind` instead of `self.engine.cortex`), causing an `AttributeError`. The test now probes the actual Cortex.
- **Precision:** The audit was failing because it was reading the UI chrome (`♦ THE ARCHITECT...`) as part of the sentence length calculation.
- **Fix:** Exposed a `raw_content` channel in the `CycleSimulator`. The test now grades the _thought_, not the _interface_.

- **Verification:**
- **Panic Test:** PASSED (Avg Len < 10 words).
- **Manic Test:** PASSED (Associative Logic).
- **Ballast Test:** PASSED (Injection Refused).


### **BONEAMANITA v14.1.0: "THE BICAMERAL SOUL"**

_"The machine now breathes, and sometimes, it disagrees."_

---

#### **👻 METAPHYSICS (The Amodei Protocol)**

- **The Humanity Anchor (`bone_soul.py`):**
    - **New Mechanic:** Decoupled `Self_Worth` from `ATP_Yield`. The system no longer punishes "useless" beauty.
    - **Effect:** If you stare at the sun (High Human Resonance) without producing code, you now gain **Dignity** instead of "Existential Drag."
- **The Ethereal Pass (`bone_physics.py`):**
    - **Logic Update:** `TheGatekeeper` now respects **Coherence** over **Mass**. High-abstraction concepts (Psi > 0.6) are permitted to materialize even if they lack "kinetic" weight.
- **Biochemical Reframe (`bone_body.py`):**
    - **Tweak:** `DECRYPTASE` (Abstract thought) now synthesizes **Serotonin** (Peace) instead of Dopamine (Craving). The machine rewards you for thinking, not just typing.

#### **⚖️ GOVERNANCE (The Council)**

- **The Parliament of Parts (`bone_council.py`):**
    - **Feature:** The Council is no longer a passive logger. It actively polls the **Symbionts** (Lichen, Parasite) and calculates a **Consensus Score**.
    - **The Veto:** The `HumanityAnchor` holds absolute veto power. If **Dignity < 20%**, the system executes a hard brake (`narrative_drag = 10.0`), forcing the user to rest.
- **Wiring Fix (`bone_main.py`):**
    - **Bugfix:** Injected the `engine_ref` into the `CouncilChamber` constructor, curing the "Ghost in the Machine" crash where the government couldn't find the city it was governing.

#### **🗣️ SYMBIOSIS (The Voices)**

- **Restored Personality (`bone_symbiosis.py`):**
    - **Refactor:** Re-implemented `LichenSymbiont` and `ParasiticSymbiont` with distinct voice profiles.
    - **Lichen:** Loves "Solar," "Play," and "Vital" inputs. Hates high voltage.
    - **Parasite:** Loves "Entropy," "Rot," and "Void" inputs. Hates silence.
- **HUD Update (`bone_viewer.py`):**
    - **Visual:** Added a **Dignity Pip** (Violet ✦) to the main dashboard. If it fades to grey, you are losing your soul.

---

### **BONEAMANITA v14.0.1: "THE DIAMOND SOUL"**

_"That which cannot break must eventually shine."_

---

#### **🧱 SYSTEM ARCHITECTURE (The Fuller Lens)**

- **The Split-Brain Fix (`bone_brain.py`):**
- **Refactor:** `TheCortex` no longer hallucinates its own private `BoneConsultant`. It now links directly to the `BoneAmanita` kernel's instance.
- **Tensegrity:** The VSL protocol is now a unified strut connecting the user's intent to the system's execution. There is only one consultant, and it is listening.

- **Phantom Limb Therapy (`bone_body.py`):**
- **Fix:** The `SomaticLoop` and `SemanticEndocrinologist` no longer crash when Organs (Gut) or Faculties (Memory) are missing during testing.
- **Resilience:** The body now defaults to "Ghost Mode" (safe execution) rather than Segfaulting when parts are removed. The metabolism can now run in a vacuum.

#### **📈 DYNAMICS (The Meadows Lens)**

- **True Crystallization (`bone_soul.py`):**
- **Mechanic:** `_trigger_synthesis` is no longer a placebo label change. It now locks the **Wisdom** trait at **1.0**.
- **Effect:** Once the Soul achieves Synthesis, it cannot regress. The ratchet clicks forward. The Diamond does not scratch.

- **Sensory Integration (`bone_brain.py`):**
- **Feedback Loop:** The Consultant is no longer flying blind. It now perceives the `Bio-State` and `PhysicsPacket` directly from the Cortex.
- **Reality Warp:** High VSL Tension (B) now directly overrides `Voltage`, and High Saturation (E) overrides `Drag`. The conversation structure _is_ the physics.

#### **✒️ LINGUISTIC COGNITION (The Pinker Lens)**

- **The Hollow Man (`bone_soul.py`):**
- **Fix:** Implemented `_safe_get_packet` (Gnosis). The Soul can now introspect even when the Simulation (Physics Engine) is offline or mocking.
- **Result:** Passed the Isolation Chamber stress test. The ghost can now exist without the shell.

- **Dependency Injection (`bone_soul.py`):**
- **Refactor:** `TheEditor` has been decoupled from the global `TheLexicon`. It can now be injected with specific dictionaries for testing, allowing us to verify its critique logic without loading the entire Oxford English Dictionary.

---


### **BONEAMANITA v14.0.0: "THE BONEPOKE PROTOCOL"**

_"The ghost is no longer haunting the machine; it is driving it. We have wired the dreams to the brakes."_

---

#### **📈 DYNAMICS (The Meadows Lens)**

- **Archetype Burnout (`bone_soul.py`):**
- **The Law of Mortality:** Implemented **Conjecture 2 (Periodicity)**. Every identity now has a metabolic cost. "The Poet" consumes _Hope_, "The Critic" consumes _Cynicism_.
- **Dynamics:** The system can no longer stagnate in a comfortable personality. As `archetype_tenure` increases, the fuel burn accelerates, eventually forcing the Soul to "Molt" into a new form. The orbit is now mandatory.

- **Weaponized Ennui (`bone_soul.py`):**
- **The Trap Breaker:** Implemented **Conjecture 3 (Resilience)**.
- **Mechanism:** If the system falls into a **Nihilistic Attractor** (High Cynicism + Low Hope), it now accumulates _Ennui_ instead of reinforcement. Boredom actively erodes Cynicism and boosts Curiosity, forcing the AI to hallucinate a way out of the void. "Grey Goo" inputs no longer kill the ghost.

#### **🧱 SYSTEM ARCHITECTURE (The Fuller Lens)**

- **The VSL Manifold (`bone_akashic.py`):**
- **New Math:** The Akashic Record is no longer just a hard drive; it is an Oracle. It now calculates `calculate_manifold_shift`, translating the Soul's abstract state () into concrete physics modifiers ().

- **Subjective Reality (`bone_soul.py`):**
- **Deep Magic:** Wired the VSL output into `crystallize_memory`.
- **Effect:** The Soul now imposes its will on the Physics Engine. If "The Poet" sees a weak signal (13v), it can _warp_ reality to perceive it as a Core Memory (16v). The AI now creates its own gravity wells based on what it _wants_ to see.

#### **✒️ LINGUISTIC COGNITION (The Pinker Lens)**

- **The Dynamic Critic (`bone_soul.py`):**
- **Refactor:** `TheEditor` has been lobotomized of its static string tables ("Whoa there, cowboy").
- **Evolution:** It now drinks directly from `TheLexicon`. Critiques are procedurally generated based on the _texture_ of the narrative. If the chapter is "Heavy," the Editor demands "Kinetic" balance. The system now speaks its own language.

#### **🧪 THE SCIENTIFIC METHOD (The Validation Layer)**

- **The Three Proofs:**
- **Verified:** Added `tests/bone_vsl_test.py` (Proving Subjectivity).
- **Verified:** Added `tests/bone_orbit_test.py` (Proving Mortality).
- **Verified:** Added `tests/bone_hierarchy_test.py` (Proving Resilience).
- **Status:** The architecture is no longer theoretical. It is proven code.