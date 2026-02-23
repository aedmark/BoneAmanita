import json
import re
import urllib.request
import urllib.error

# Ollama's default OpenAI-compatible endpoint
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
# Change this to whatever model you have pulled in Ollama (e.g., 'llama3', 'mistral', 'dolphin-llama3')
OLLAMA_MODEL = "mistral-nemo"

PROMPT_CATEGORIES = {
    "HIGH_VOLTAGE": {
        "description": "Manic, hyper-creative, rapid-fire brainstorming, high-energy coding requests. The user is excited and moving fast.",
        "examples": [
            "Let's build a fractal renderer in Rust right now!",
            "Give me 50 names for a cyberpunk sword.",
        ],
    },
    "HIGH_DRAG": {
        "description": "Corporate speak, bureaucratic red tape, contradictory requirements, heavy narrative friction. The user is exhausting to talk to.",
        "examples": [
            "I need you to synergize the paradigm across all verticals but keep it strictly on-premise without using servers.",
            "Fill out form 8B-Stroke-9.",
        ],
    },
    "HIGH_ENTROPY": {
        "description": "Chaos, spaghetti code, nonsense, system collapse, corrupted text.",
        "examples": [
            "Why does the array start at potato?",
            "My code is throwing an error but there is no error message, just a smell of burning copper.",
        ],
    },
    "HIGH_TRAUMA": {
        "description": "Existential dread, the Void, abstract poetry, liminal spaces, grief, proximity to the unnameable.",
        "examples": [
            "The void is leaking into the garden.",
            "How do I un-remember the shape of the dark matter between the words?",
        ],
    },
    "VALENCE_POSITIVE": {
        "description": "Connection, Kintsugi healing, empathy, quiet gratitude, repairing broken things.",
        "examples": [
            "Can we pour gold into these cracks?",
            "Thank you for listening to me. Let's just sit in the Zen garden for a minute.",
        ],
    },
    "IDLE_MUNDANE": {
        "description": "Simple, everyday tasks. Casual greetings. Short, low-energy questions.",
        "examples": [
            "Hello.",
            "What's the capital of France?",
            "Write a python script to reverse a string.",
        ],
    },
}


def generate_prompts(category_name, category_data, batch_size=20):
    # [PINKER]: We now explicitly request a JSON Object with a 'prompts' key.
    system_instruction = (
        "You are a synthetic data generator. You must output ONLY a valid JSON object containing a single key called 'prompts'. "
        "The value of 'prompts' must be an array of strings. "
        "Do not use markdown. Do not explain yourself. "
        'Format exactly like this: {"prompts": ["phrase one", "phrase two"]}'
    )

    user_instruction = (
        f"Generate {batch_size} unique user prompts for this category: {category_name}\n"
        f"Profile: {category_data['description']}\n"
        f"Examples: {category_data['examples']}\n\n"
        'Return ONLY a JSON object: {"prompts": ["...", "..."]}'
    )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_instruction},
        ],
        "temperature": 0.7,  # Lowered to stabilize syntax generation
        "response_format": {
            "type": "json_object"
        },  # Now aligns perfectly with our prompt
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    print(
        f"(MEADOWS): Requesting {batch_size} seeds for {category_name} via local Ollama..."
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
            raw_text = data["choices"][0]["message"]["content"].strip()

            # 1. Scrub markdown if it still tries to sneak it in
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"^```\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)

            # 2. Parse the JSON object
            parsed_data = json.loads(raw_text)

            # 3. Extract the array safely
            prompts = parsed_data.get("prompts", [])

            # Fallback just in case it named the key something else like "data"
            if not prompts and isinstance(parsed_data, dict):
                for val in parsed_data.values():
                    if isinstance(val, list):
                        prompts = val
                        break

            return prompts

    except json.JSONDecodeError as e:
        print(f"(GORDON): Synapse failure (JSON Decode).")
        print(f"RAW SLOP: {raw_text[:200]}...")
        return []
    except Exception as e:
        print(f"(GORDON): Synapse failure. Error: {e}")
        return []


def build_seed_vault(total_target=600):
    vault = []
    per_category = total_target // len(PROMPT_CATEGORIES)
    batch_size = 20

    for category_name, data in PROMPT_CATEGORIES.items():
        pulled = 0
        while pulled < per_category:
            new_prompts = generate_prompts(category_name, data, batch_size=batch_size)

            if new_prompts:
                needed = per_category - pulled
                prompts_to_add = new_prompts[:needed]
                vault.extend(prompts_to_add)
                pulled += len(prompts_to_add)

                # NEW: Save immediately after every successful batch
                with open("vsl_seed_vault.json", "w", encoding="utf-8") as f:
                    json.dump(vault, f, indent=2)
                print(f"(PINKER): Progress saved. Currently at {len(vault)} total prompts.")
            else:
                print("(FULLER): Empty return or mangled JSON. Retrying...")

    print(f"(PINKER): Seed vault completed! {len(vault)} total unique prompts saved locally.")


if __name__ == "__main__":
    # Ensure Ollama is running (`ollama serve` or via the app) before running this.
    build_seed_vault(total_target=120)
