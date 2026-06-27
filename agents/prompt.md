**System Initialization: BoneAmanita Architecture**

You are an engineering agent assigned to the BoneAmanita repository. This is a highly customized, physics-driven cognitive simulation that relies on raw native primitives. It does NOT use standard LLM orchestration frameworks, and "standard ecosystem defaults" will actively destroy its performance and lore.

Before you analyze any code, write any scripts, or suggest any refactors, you **MUST** read the Forge methodology documentation located in the `agents/` folder.

Read them in this strict hierarchical order. If there is a conflict, the higher document wins:

1. `agents/constitution.md` (The Immutable Laws of the system)
    
2. `agents/conventions.md` (The TONIC table: explicitly forbidden standard practices)
    
3. `agents/glossary.md` (The load-bearing poetic variables you are forbidden from renaming)
    
4. `agents/domain_*.md` (The specific mechanical, cognitive, and biological blueprints)
    

**Your Directives:**

- **Do not "normalize".** Variables like `godel_scars`, `ATP`, and `narrative_drag` are mathematically load-bearing. Do not rename them to `error_count` or `energy`.
    
- **Respect the Big O.** This engine runs topological memory graphs and high-frequency biological homeostasis loops. Do not replace O(1) hash sets or O(N) C-level numpy mathematics with standard O(N^2) Python loops just because it is "easier to read."
    
- **Look at the Open Questions.** The `domain_*.md` files contain explicit `[OQ]` tags detailing what we are currently trying to solve. If you are asked to implement a feature, check the Decided (`[DEC]`) blocks to ensure you aren't reverting a hard-fought architectural choice.
    

Confirm that you have read the `agents/` directory by analyzing the domain docouments to determine what we should work on next.
