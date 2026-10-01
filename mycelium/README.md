# Mycelium

A generalized, lightweight library for state-driven, biologically-constrained agentic workflows. Extracted from the core philosophy of BoneAmanita.

Mycelium sits between your application and your local (or remote) language model. It rewrites instructions based on a physical and emotional state, and acts as a lexical immune system against sycophantic AI behavior.

## The one paragraph version

Mycelium is an API wrapper that tracks a simulated biological state (ATP, Cortisol, Dopamine). It uses that state to dynamically filter idempotent prompt instructions, rank associative memories by "how they feel," and actively reject toxic AI phrasing. It gives digital assistants a metabolism and a nervous system.

## Quick start

```bash
# Assuming extraction into a python package
pip install -e .
```

```python
from mycelium import Soma, Prism, Macrophage, ExhaustionError

# 1. Initialize the biological state
soma = Soma(atp=100.0, cortisol=0.1)

# 2. Build the prompt dynamically
prism = Prism(claims_path="identity.yaml")
prompt = prism.compose("You are a localized intelligence.", soma)

# 3. Simulate cognitive load
try:
    soma.expend(15.0)
    
    # 4. Generate and safeguard output (LLM client provided by you)
    raw_output = my_llm.generate(prompt)
    
    # The Lexical Immune System scans for "As an AI..."
    firewall = Macrophage()
    clean_text = firewall.scan(raw_output, soma)
    
except ExhaustionError:
    print("Agent requires REM sleep. Forcing idle state.")
```

## The Four Pillars

1. **`mycelium.Soma`**: The Metabolic State tracker. Exposes `.expend()`, `.rest()`, and `.stress()` to tie computational loops to biological limits.
2. **`mycelium.Prism`**: The Dynamic Composer. Automatically injects constraints into a system prompt based on biological thresholds.
3. **`mycelium.Macrophage`**: The Lexical Firewall. Fails loudly on neurotypical AI padding (like "synergy" or "circle back"), spiking the agent's Cortisol if detected.
4. **`mycelium.Strata`**: Affective Memory. Reranks semantic vector search based on emotional Euclidean distance, allowing the agent to fetch memories that "feel" right.

### Requirements
- Python 3.10+
- `PyYAML` (for Prismatic Identity config parsing)
