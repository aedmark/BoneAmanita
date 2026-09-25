# Project Update: Structural Invariant Governance (The Warden & The Mechanism)

BoneAmanita is an experimental framework designed to embed Large Language Models within a strictly deterministic, simulated physical environment. Rather than treating LLMs as omnipotent conversationalists, the framework treats them as biological components operating under literal metabolic constraints—tracking exhaustion, ATP expenditure, and narrative momentum as rigid numerical values. 

Today, we significantly hardened the boundary between the model's stochastic generation and the framework's deterministic state space by implementing a strict governance pipeline. 

## What We Built Today

We introduced two new paradigms to the framework: **The Warden** and **The Mechanism (Gatekeeper)**.

### 1. The Warden (Syntactic Sandboxing)
Historically, BoneAmanita allowed the model to output free-form narrative prose and extracted context using regex sweeps. This left the system vulnerable to jailbreaks, prompt bleeding, and unconstrained formatting errors. 

We replaced this with a strict JSON-enforced boundary. The system prompt is now forcefully prepended with a `STRUCTURAL INVARIANT GOVERNANCE` block. The model is treated as a sandboxed system actor that may only output exactly one JSON object per turn, executing specific "tools" (e.g., `nominate_response`, `commit_memory`). If the model attempts to generate conversational prose or markdown outside of the designated JSON schema, the turn is structurally intercepted and rejected before it reaches the simulation pipeline.

### 2. The Mechanism & The Gatekeeper (Semantic Verification)
LLMs are highly prone to hallucinating facts, memories, and citations. To solve this, we introduced an Invariant Gatekeeper that evaluates the model's requested state transitions against physical reality. 

A primary feature of this Gatekeeper is **Evidence-Gated Memory**. If the model attempts to execute a `commit_memory` action, it must provide exact, verbatim citations from the historical dialogue buffer. If the Gatekeeper detects that the cited evidence was hallucinated or altered, the memory commit is completely blocked.

### 3. Trial-and-Commit Atomic State
Because LLM outputs are inherently unpredictable, trusting their state transitions is dangerous. We refactored the central simulation loop to run on a "Trial-then-Commit" architecture. 

Before the model is invoked, the engine freezes a deep snapshot of all metabolic and structural parameters. The model's response is generated, parsed, and evaluated against both local invariants (like the Evidence Gate) and global invariants (such as ensuring the turn's token generation didn't force the system's ATP pool below 0). 

If any invariant is breached, the model is fed a `SYSTEM REJECTION` payload and forced to retry silently. If it exhausts its retry allowance, the system discards the corrupted trial state, thaws the pristine pre-turn snapshot, and cleanly degrades the turn—preventing any hallucinated or malformed output from permanently corrupting the simulation state.

## What BoneAmanita Can Do Now

With these systems fully integrated, BoneAmanita is now capable of:

- **Self-Healing Execution**: The system can safely absorb and silently correct degenerate model outputs without human intervention or state corruption.
- **Strictly Grounded Memory**: The model's internal long-term memory graph is now cryptographically bound to the actual dialogue that occurred, entirely eliminating hallucinated historical context.
- **Atomic Simulation Integrity**: The continuous state-space (tracking health, stamina, and biological variables) is mathematically guaranteed to never fall into an illegal or paradoxical state, regardless of the model's generated text. 

By treating the LLM as an untrusted biological organ rather than a trusted software layer, BoneAmanita has achieved a profound level of deterministic stability while maintaining dynamic, generative capabilities.
