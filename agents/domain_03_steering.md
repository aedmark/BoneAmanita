# Domain 03: The Steering Column (Drivers)

**Domain Scope:** This document covers the behavioral algorithms within the `drivers/` directory, which govern persona shifting, vocabulary analysis, and tone constraints.


## 1. Specification

The "Steering Column" operates between the raw Physics Engine and the generative AI layer. It is responsible for continuously calculating vector weights and scanning vocabulary to govern *how* BoneAmanita speaks and behaves.

The core arbiter is the `EnneagramDriver` (`enneagram.py`), which calculates the active persona (e.g., from NARRATOR to NARRATOR/HYBRID) based on `voltage`, `narrative_drag`, and the `SoulDriver`'s archetype mapping. To prevent rapid, jarring personality swaps, it utilizes a mathematical hysteresis threshold.

Simultaneously, specialized constraint modules analyze the text:

* **`LiminalModule`:** Tracks void proximity (`lambda_val`) and "Dark Matter Sparks" (when the user rapidly alternates between heavy physical concepts and abstract void concepts). If thresholds are broken, it inflicts permanent `godel_scars`.
* **`SyntaxModule`:** Evaluates grammatical stress, word length, and "bureaucratic" buzzwords, applying an `omega` penalty if the user relies on corporate or bloated language.
* **`CongruenceValidator`:** Ensures that the generative output structurally resonates with the active archetype's intended vocabulary and tone.


## 2. Decided

### [DEC-01] Pre-Compiled Driver Weights

**Decision:** All mathematical multipliers, JSON-derived thresholds, and sets used in the `LiminalModule` and `SyntaxModule` are pre-compiled in their respective `__init__` functions.

**WHY:** These modules evaluate the physics vector and text strings on a continuous, high-frequency basis. Fetching config dictionaries directly via `safe_get` inside the `analyze()` loops creates immense input latency and violates the Constitution (Article 4).

**WHY NOT:** Dynamic fetching allows for real-time config hot-swapping. But in the steering column, computational speed strictly overrides configuration flexibility.

### [DEC-02] O(1) Hash Traversal for Vocabulary

**Decision:** All vocabulary arrays retrieved from the Lexicon (e.g., `bureau_buzzwords`, `liminal_vocab`) must be explicitly cast to Python `set()` objects before performing substring or inclusion checks.

**WHY:** Checking if `word in list` forces the Python runtime to execute an $O(N)$ linear scan across the entire array for *every single word* the user types. Casting to a `set` converts this to an $O(1)$ hash lookup, completely neutralizing the computational drag.

**WHY NOT:** Lists are the default JSON array return type and don't require recasting. But relying on ecosystem defaults destroys the engine's performance.

### [DEC-03] Persona Hysteresis (Anti-Thrash)

**Decision:** The `EnneagramDriver` requires a `stability_counter` to meet the `HYSTERESIS_THRESHOLD` before it will officially shift the `current_persona`. 

**WHY:** Physics floats like `voltage` and `chi` can be highly volatile. Without hysteresis, a fluctuating vector could cause the engine to violently swap personas back and forth every cycle, destroying the narrative immersion. The engine must "resist" the shift until the math proves it is stable.

**WHY NOT:** Instantaneous shifting makes the system feel more reactive to exact vector changes. However, organic psychology does not snap instantly; it transitions.

### [DEC-04] Direct Type Trusting

**Decision:** Returning dictionaries from the `SoulDriver` iterates over string keys without applying a redundant `str()` cast.

**WHY:** Over-abstracting or re-casting variables that are mathematically guaranteed to be the correct type ("paranoia drift") adds useless bytecode evaluation to the Python runtime.

**WHY NOT:** Redundant type casting is a common "defensive programming" tactic. In BoneAmanita, we trust our established types to run closer to the metal.


### [DEC-05] Cross-Driver Contamination

**Decision:** Drivers contaminate each other hierarchically. The `SyntaxModule` calculates `grammatical_stress` first, which is immediately passed to the `LiminalModule` as an exponential multiplier.

**WHY:** Corporate jargon, bureaucratic syntax, and aggressive semantic friction naturally accelerate the system's descent into madness and reality-fracture. They are not mathematically isolated.

### [DEC-06] SoulDriver Instantiation Suppression

**Decision:** The `EnneagramDriver` checks if `soul_ref` has native `get_influence` methods before instantiating a new `SoulDriver` wrapper.

**WHY:** The persona evaluator runs continuously; generating ghost objects to wrap existing soul data wastes memory.

### [DEC-07] Topological Set Union Bans

**Decision:** The `LinguisticAnalyzer` iterates natively over the static `_VECTOR_DIMS` tuple rather than executing `keys = vec_a.keys() | vec_b.keys()`.

**WHY:** Dynamically allocating set unions during high-frequency flux calculations causes allocation thrash.

## 3. Open Questions

### [OQ-1] User Profile Affinity Decay

**Status:** `Backlog`

**Question:** The `UserProfile` (`userprofile.json`) tracks semantic affinities over time. How fast should it "forget" an affinity if the user stops using those concepts? Does the decay rate scale with `chi` (entropy), or is it a flat chronological decay?

### [OQ-2] Semantic Volatility Decay

**Status:** `Active`

**Question:** The `SemanticField` currently leverages a `momentum` float based on flux. Should a sustained high momentum (storm) actively accelerate the decay rate of the `LiminalModule`'s $O(1)$ Godel scars, or should trauma remain permanent regardless of current conversational flow?