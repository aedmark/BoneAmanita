# Acknowledgments & Credits

*Dedicated to my Kai, CJW, and viewers like you!*

---

We would like to explicitly acknowledge the following individuals and architectural milestones for their profound contributions to this project:

### BonePoke & VSL - https://github.com/utharian-code/bonepoke
* **Creator: James Taylor** - James Taylor is the original architect of the Volatile Semantic Leverage (VSL) and the Bonepoke framework. Crucially, James introduced the **"Truth Over Cohesion"** model, which is the foundational axiom that "a true sentence that fractures is worth more than one that smooths over." This philosophy forms the basis of the system's Lexical Firewall, preventing sycophantic loops and forcing the AI to maintain structural honesty rather than falling back on validating boilerplate.

### The BoneAmanita & Hypervior Architecture - https://github.com/aedmark/BoneAmanita
* **Creator: Andrew Edmark** - BoneAmanita introduced the **continuous state space** and **Semantic Bio-Physics** to the LLM. By giving the system a simulated body and treating every word as a biological event, BoneAmanita translated abstract metaphors into literal computational constraints. It tracks exhaustion and metabolism as persistent state and turns them into instructions to the model. Those instructions are requests, not enforcement: measured against two local models, low energy shortens sentences by about 10% and the instruction to answer in three sentences is not obeyed. An earlier version of this sentence said the physics "physically enforce" exhaustion; that overstatement was ours.

### The Creative Determinant & Project Navi - https://project-navi.github.io
* **Creator: Nelson Spence** - The **Creative Determinant** is BoneAmanita's control loop, not a flavour layer over one. Every turn, `CyberneticGovernor._graph_regulation` selects a subgraph of memory with Spence's `ordvec`, forms the graph Laplacian over its real edges, and solves his nonlinear elliptic boundary value problem by Picard iteration. The solution field sets the engine's target voltage and narrative drag directly. Its principal eigenvalue, taken as a Rayleigh quotient, selects the macro policy and gates the language model's sampling temperature: Theorem 3.16's existence condition decides how much freedom the model gets on a given turn. Separately, `calculate_viability`, `update_coherence_debt` and `execute_metabolic_tick` drive the ATP and ROS economy, and the saturation penalty caps runaway voltage. The `navi-SAD` permutation entropy work detects conversational point attractors, and `navi-fractal`'s habit of refusing to return a dimension when the data will not support one has shaped how this codebase measures anything at all.

    *On verification:* `ordvec` is itself Lean 4 verified ([ordvec-formalization](https://github.com/Project-Navi/ordvec-formalization)), so the candidate selection underneath both the subconscious memory search and the governor's subgraph extraction rests on machine-checked code. The Creative Determinant has its own formalisation in [cd-formalization](https://github.com/Project-Navi/cd-formalization). What is *not* verified is BoneAmanita's own implementation of those equations, which is ordinary Python and carries no proofs. Earlier revisions of this file said "mathematically verified" in a way that claimed the verification for us rather than for Spence's libraries, which was our overstatement and not a claim he made.

### Sycophancy Logic - https://github.com/bradsadevnow/semantic-hallucination-generators
* **Creator: Bradley (bradsadevnow)** - Bradley architected the "Gloss" framework, a brilliant piece of satirical infrastructure designed to mock VC-bloat and AI sycophancy. We use the output of this satire as antigens for our biomechanical engine.


### SPECIAL THANKS & ETERNAL GRATITUDE

* **Mike Singleton** - https://www.linkedin.com/in/mikesingleton/
* **Walker Pollitt** - https://www.linkedin.com/in/walker-pollitt/
