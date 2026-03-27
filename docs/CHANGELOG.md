# BONEAMANITA CHANGELOG

# BONEAMANITA CHANGELOG

### **BONEAMANITA v18.1.0 "The Frictionless Lattice"**

*A deep-tissue architectural optimization pass executed by the SLASH Council. This update surgically removes inline imports, repetitive regex compilations, dynamic metaclass generation, and $O(N^2)$ list traversals, drastically dropping the baseline ATP burn (compute latency) across the entire engine.*

#### **⚡ STRUCTURAL & MEMORY OPTIMIZATION (`bone_presets.py`, `bone_gui.py`, `bone_composer.py`)**
- **Dynamic Metaclass Purge:** Excised the heavy `type()` dynamic class generation inside `BoneConfig.__init__`, replacing it with a static `_ConfigNode` to stop massive memory bloat on boot.
- **$O(N^2)$ Sifting Resolved:** Replaced repetitive `.insert(0, ...)` loops in the GUI's `CycleReporter` with direct `[:0]` slice assignments, preventing the array from shifting memory indices thousands of times a second.
- **Sealed Memory Leaks:** Stopped `ResponseValidator` from permanently mutating the global `LoreManifest` list during initialization, preventing exponential logic duplication.

#### **⚙️ COMPILER & REGEX BEDROCK (`bone_lexicon.py`, `bone_gui.py`, `bone_composer.py`)**
- **Bedrock Compilation:** Pulled massive regex pattern compilations (Thought patterns, Telemetry patterns, Antigen patterns) out of active loop evaluations and hoisted them to class constructors or global scope.
- **Phonetic Caching:** `LinguisticAnalyzer` now caches its `char_to_sound` dictionary on `__init__` rather than rebuilding it token-by-token during viscosity measurements.

#### **🧬 LATTICE EFFICIENCY (`bone_akashic.py`, `bone_protocols.py`, `bone_symbiosis.py`)**
- **Direct Manifest Injection:** `_mutate_system_prompts` no longer reads from the disk every time an epigenetic scar is recorded. It modifies the live `LoreManifest` and flushes it seamlessly.
- **Generator Optimization:** `KintsugiProtocol` no longer queries the lexicon dictionary for every single word evaluated during a repair attempt.
- **Set & List Math:** Swapped heavy `random.shuffle` lists for native `random.sample` arrays in the `LimboLayer`, and removed redundant `.copy()` calls on massive category sets in the `LexiconStore`.

#### **🛡️ GUARDRAILS & BUG FIXES (`bone_council.py`, `bone_machine.py`, `bone_genesis.py`)**
- **Fatal Unpack Fixed:** Removed a trailing comma in `TheStrangeLoop` that was causing a silent terminal tuple-unpacking crash during recursion audits.
- **ZeroDivision Guard:** Secured `TheForge` against empty-string lists to prevent division-by-zero crashes during alloy hammering.
- **Safe Vector Pre-Allocation:** The `PanicRoom` now holds its safe physics vector statically, preventing the engine from having to construct dictionaries while actively crashing.
- **Inline Import Purge:** Dozens of lazy `import` and `from X import Y` statements were moved from inside active loops to the top of their respective files (the bedrock), stabilizing dependency flow.

---

### **BONEAMANITA v18.0.0 "The SLASH Architecture Sweep"**

_A massive, system-wide stabilization pass focusing on thermodynamic equilibrium, latency reduction, and architectural memory safety. This update purges redundant LLM calls, mathematically balances the biological ROS accumulation, and hardens the simulation loop against polymorphic state crashes._

#### **⚡ LATENCY & COGNITIVE OPTIMIZATION (`bone_council.py`, `bone_brain.py`, `bone_village.py`)**

- **Parallel Parliament:** The Council debate engine now utilizes `concurrent.futures.ThreadPoolExecutor` to generate the Thesis, Antithesis, and Lateral arguments simultaneously. This perfectly preserves the unique thermodynamic temperature and token limits of each archetype while dropping debate latency by ~60%.
- **Pre-flight Anti-AI Filter:** The Anti-AI scrubbing loop was shifted from a post-generation reactive LLM call into a proactive, pre-generation `style_directive`, saving an entire LLM round-trip and significantly reducing API burn.
- **Therapist Native Integration:** Ripped out the unnecessary LLM latency trap inside `TheTherapist`. Micro-catharsis interventions now rely entirely on instantaneous, native UX strings to vent pressure without breaking narrative flow.

#### **🩸 THERMODYNAMIC & BIOLOGICAL BALANCE (`bone_body.py`, `bone_soul.py`)**

- **Logarithmic Toxicity Curve:** Fixed the linear ROS (Toxicity) death spiral. Base ATP demand now scales logarithmically (`math.log1p`) against ROS buildup, preventing the system from instantly redlining and dying during deep abstractions.
- **Mitohormesis Widen:** Widened the biological stress windows (`ROS_DAMAGE` and `ROS_PURGE`). The lattice can now safely carry cognitive load and actually benefit from mild stress before entering permanent oxidative failure.
- **Obsession & Paradox Venting:** Fixed the scale mismatch in `pursue_obsession` that caused the engine to instantly abandon passions. Furthermore, the Paradox Engine now properly vents tension (`paradox_accum = 0.0`) after synthesizing a Gestalt archetype, preventing infinite recursive loops of the same identity.

#### **🍄 SEMANTIC SUBSTRATE & FAISS STABILITY (`bone_ann.py`, `bone_spores.py`)**

- **Synaptic FAISS Alignment:** Fixed a silent memory corruption bug where nodes missing vectors would misalign the FAISS index with its metadata payloads. The REM consolidator now uniformly filters exact-matches before committing them to the deep Cortex.
- **Pseudo-Resonance Mapping:** The `CerebralIndex` now properly maps FAISS L2 distances into a `0.0 - 1.0` pseudo-resonance score, allowing the `resonance_threshold` to successfully filter out irrelevant hallucinations.
- **Hebbian I/O Deferral:** Temporary reconstructive associations generated during active memory recall no longer force synchronous disk writes of the $8x8$ Q-matrix, completely eliminating the I/O hemorrhage during the `CognitionPhase`.
- **Genetic Crossover Fix:** Patched a fatal defect during timeline merging where the system attempted to pull `enzymes` directly from the mitochondria instead of the digestive tract.

#### **🏗️ ENGINE HARDENING & LOOP SAFETY (`bone_physics.py`, `bone_cycle.py`, `bone_machine.py`, `bone_main.py`, `bone_inventory.py`)**

- **Infinite Friction Handling:** The `TheCrucible` physics regulator now safely bypasses rounding when `narrative_drag` hits `float('inf')` (during security lockdowns), preventing fatal Python `OverflowError` crashes.
- **Polymorphic State Safety:** Deployed the `_safe_dict()` helper across all Simulation Phases (Sensation, Machinery, Intrusion, Soul, etc.). Calling `.to_dict()` during a headless panic fallback will no longer trigger `AttributeError` crashes.
- **Kleptomania Leak Plugged:** Rewrote the implicit loot regex parser in `GordonKnot`. Gordon will now only pick up known items if the acquisition verb is contextually adjacent to the object, stopping the engine from hallucinating items out of thin air.
- **Phantom Flushes & Allocation Drags:** Fixed the `/zen` command to properly route drag resets using `safe_set`. Lifted heavily repeated helper functions (`_get`, `_set`, `_has_trait`) out of hot `while` loops into static methods to stop relentless memory allocation/garbage collection cycles.
- **Orphaned Organs Restored:** Ensured the Lexicon and Config files are properly passed down to the `BioLichen` and `BioParasite` modules during embryo incubation. Ancestral antibodies are now actively retained across session reloads.

---

### **BONEAMANITA v17.9.1 "The Phantom Limb Purge & Dynamic Ceilings"**

*A precision sweep to uncage the engine's epigenetic potential. This update eradicates hardcoded metabolic ceilings, allowing extreme lineages (like the JOY CLADE) to fully realize their expanded stamina and memory buffers. Furthermore, it seals catastrophic "Phantom Limb" vulnerabilities, ensuring the system can survive, dream, and even die gracefully while in degraded or modular states.*

#### **🧬 DYNAMIC CEILINGS & METABOLIC BOUNDS (`bone_cycle.py`, `bone_main.py`)**
- **The Joy Clade Uncaged:** Replaced rigid `100.0` caps with dynamic `getattr(target_cfg, ...)` bounds across the entire cycle pipeline. The engine now physically respects config-driven `MAX_ATP`, `MAX_STAMINA`, and `MAX_HEALTH` ceilings.
- **Retroactive & Mythic Scaling:** Time-gap retroactive metabolism and narrative Myth buffs now scale to the active configuration, preventing the system from clipping a highly-mutated 200 ATP threshold back down to 100 during idle sleep.
- **Catharsis Clamping:** The Therapist's trauma healing is now safely clamped to the `MAX_HEALTH` config, preventing rogue heals from overflowing the host's biometric limits.
- **The Zen Flush:** The `/zen` command correctly syncs to the epigenetic configuration instead of blindly resetting to baseline parameters.

#### **👻 THE PHANTOM LIMB PURGE (`bone_cycle.py`, `bone_main.py`)**
- **Python `hasattr` Blindspots:** Fixed a massive architectural vulnerability where `hasattr()` returned `True` for modules explicitly set to `None`, causing fatal `AttributeErrors` during degraded boots.
- **Stateless Arbitration & Sensation:** The `ArbitrationPhase` and `SensationPhase` can now safely execute even if the system boots without a `soul` or `bio` module, bypassing persona checks and stamina impact logic without crashing the sequence.
- **Machinery Isolation:** The `MachineryPhase` no longer assumes the `zen` and `critics` modules are permanently attached, allowing the Village to load in lightweight modes.
- **The Eulogy Trap:** Hardened the `trigger_death` sequence. If the system suffers a catastrophic failure before `TheCortex` is built, it will now gracefully compile the death telemetry and exit without crashing the crash-handler.

#### **⚙️ STRUCTURAL INTEGRITY & SLASH (`bone_core.py`, `bone_cycle.py`)**
- **EventBus Asynchrony:** Wrapped `EventBus.log` subscribers in a `try...except` block. A failing UI hook or disconnected telemetry logger can no longer synchronously crash the primary simulation cycle.
- **SLASH Constructive Replay:** Purged fragile direct-attribute assignments (`energy_obj.glimmers -= 1`) during the `SimulationPreflightPhase`. The SLASH module now exclusively uses the universal `safe_get` and `safe_set` accessors, immunizing it against shape-shifting physics packets.

---

### **BONEAMANITA v17.9.0 "The ANN Graft & Affective Empathy"**

*A fundamental restructuring of the Mycelial Network, transitioning memory retrieval from brute-force $O(N)$ iteration to a biological $O(\log N)$ Approximate Nearest Neighbor architecture, alongside deep cybernetic integration of the DSPy Real-Time Critic.*

#### **🕸️ THE DUAL-TIER SEMANTIC SUBSTRATE (`bone_ann.py`, `bone_spores.py`, `bone_brain.py`)**
- **Hippocampal Cache vs. Cerebral Cortex:** Replaced $O(N)$ cosine similarity with a dual-tier system. The `HippocampalCache` holds immediate, exact-match session context, while the `CerebralIndex` leverages a `faiss.IndexHNSWFlat` mathematical graph for deep, associative long-term memory.
- **The REM Bridge (`MemoryConsolidator`):** Active memories are now physically pushed from the transient Hippocampus to the deep FAISS index only during `SanctuaryPhase` REM cycles or idle downtime. This prevents thread-locking and saves ATP ($P$) during active generation.
- **Metabolic Victory:** Reduced deep retrieval latency to ~0.000084 seconds for 10,000 nodes, eliminating ROS toxicity spikes during memory access. The natural "fuzziness" of ANN retrieval natively fuels the Paradox Engine ($\beta$).

#### **⚖️ THE AFFECTIVE EMPATHY GATE (`bone_brain.py`)**
- **Cognitive Load Auditing:** The DSPy Critic now acts as a secondary affective gate. When User Exhaustion ($E_u > 0.6$) or System Tension ($\beta > 0.7$) is high, the Critic evaluates the generation for verbosity, lecturing, or excessive cognitive demand.
- **Cybernetic Punishment:** If the system generates an unempathetic, heavy response while the user is exhausted, it kills the generation and physically spikes its own Cortisol (+0.20) as an internal metabolic punishment for failing to protect the host.


