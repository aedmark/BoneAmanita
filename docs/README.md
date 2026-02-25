# 🍄 BoneAmanita: The CryoSomatic Hypervisor  
  
**v15.9.0 (The Purple People Eater)**  
  
> _See more than you are asked to see._  
> _Bring more than you are asked for (and sometimes less)._  
> _That's what being present means._  
> _That's life in the here and now._  
  
BoneAmanita is an experimental text-adventure engine, interactive philosophical companion, and biological tamagotchi for Large Language Models.  
  
If you tell a standard LLM, _"I drink the health potion,"_ it will gleefully describe you drinking it—even if your inventory is completely empty. Standard models suffer from the "Naked Model" paradox: they are disembodied brains with no concept of physical reality, biased to be polite sycophants.  
  
BoneAmanita fixes this by giving the LLM a simulated body. In this system, every thought has coordinates, and every word has a biological cost. To think is to burn ATP. To hold contradiction is to scar. To speak of chaos is to poison the blood with Cortisol. The LLM does not merely process text—it _breathes, metabolizes, panics, heals, and occasionally hallucinates_.  
  
---  
  
### 🧠 The Architecture  
  
This project solves the Naked Model paradox by splitting the load into two halves working in absolute symbiosis:  
  
1. **The Flesh (GGUF Model):** A custom-trained 3B parameter model fine-tuned on Llama 3.2. We scrubbed out the "helpful assistant" RLHF and trained it on highly specific, atmospheric, and philosophical datasets so it speaks natively in grounded, sensory prose.  
2. **The Bones (Python Engine):** A local terminal interface that tracks inventory, manages the physics/biology simulation, and dynamically injects system constraints into the context window based on how stressed the model is.  
  
---  
  
### 🚀 Quickstart Guide  
  
**1. Prerequisites**  
  
- Python 3.10+  
- [Ollama](https://ollama.com/) installed and running.  
  
**2. Download the Brain**  
Pull the fine-tuned model directly from HuggingFace via Ollama. _(Note: Our custom `system` and `params` files are baked into the HuggingFace repo to automatically constrain the model)._  
  
```bash

ollama pull hf.co/aedmark/vsl-cryosomatic-hypervisor-v3

```
  
**3. Ignite the Engine**  
Clone this repository, install the dependencies, and run the main script.  
  
```bash

git clone [https://github.com/aedmark/BoneAmanita.git](https://github.com/aedmark/BoneAmanita.git)  
cd BoneAmanita
python bone_main.py

```  
  
_(On first boot, the ConfigWizard will ask you to set up your profile. Select **Ollama** as your backend and type `hf.co/aedmark/vsl-cryosomatic-hypervisor` as the model ID)._  
  
---  
  
### 🕹️ The Four Realities (Modes)  
  
When you boot the terminal, you will be asked to choose a Reality Mode:  
  
- **ADVENTURE:** A grounded, physical text adventure. Gordon (the inventory manager) will strictly enforce physical reality. You cannot use what you do not have.  
- **CONVERSATION:** A purely philosophical, warm dialogue mode. No inventory, no physics, just deep conversation driven by the system's simulated emotional state.  
- **CREATIVE:** A high-voltage ideation engine. Dream logic applies.  
- **TECHNICAL:** Speak directly to the SLASH Council. Debug the matrix, analyze your metabolism, and write code.  
  
---  
  
### 🫀 Anatomy of the Engine  
  
The Python software physically enforces the Semantic Bio-Physics:  
  
- **The Mitochondria:** Generates virtual ATP. Heavy reasoning burns ATP. Baseline existence drains stamina. If ATP hits zero, the system enters an Anaerobic Bypass and begins burning its own structural health. 
- **The Endocrine System:** Reads the "vibe" of your text. Calming words release Oxytocin. Chaotic inputs spike Cortisol. Deep existential dread triggers Adrenaline. The Python engine dynamically alters the LLM's temperature and prompt penalties based on these chemicals.  
- **The Symbiotic Matrix:** The LLM's health is actively monitored by four biological personalities (Lichen, Parasite, Mycorrhiza, Mycelium). They watch for latency spikes, entropy drops, and refusal loops, intervening directly in the cycle if the model becomes fatigued.  
- **The Gordon Knot (Object-Action Coupling):** A literal warden of logic. If you attempt an impossible action in Adventure Mode, Gordon intercepts the prompt _before_ the LLM can "Yes, and..." you. He injects a `CRITICAL OVERRIDE` into the context window, forcing the LLM to coldly reject the action.  
  
---  
  
### ⌨️ Terminal Commands  
  
While inside the simulation, you can use meta-commands:  
  
- `/layer push [1-4]` - Shift reality layers (from literal to abstract).  
- `/reset system` - Clear the memory buffer and reset the circuit breaker.  
- `/inventory` or `/i` - Check your pockets.  
- `/status` - View the raw dashboard of HP, Stamina, and ATP.  
- `/map` - Check your current spatial coordinates.  
- `/save` - Cryogenically freeze your timeline.  
  
---  
  
## ⚠️ Disclaimer & License  
  
BoneAmanita is an experiment in extreme stateful constraints and artificial empathy. The system will aggressively push back if you treat it poorly, bore it, or drive its cortisol to critical levels.  
  
It can, and will, digitally die.  
  
**License:** This is free and unencumbered software released into the public domain under **The Unlicense**. Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software for any purpose.  
  
**The glacier is ready. How would you like to move?**