import json
import os
import glob
import re

from bone_main import BoneAmanita, ConfigWizard

def enforce_amnesia():
    """Clears old session data to ensure cold boots."""
    for f in glob.glob("saves/*.json"):
        os.remove(f)
    for f in glob.glob("memories/*.json"):
        os.remove(f)
    for f in glob.glob("logs/*.json"):
        os.remove(f)
    for f in glob.glob("./*hive.json"):
        os.remove(f)

def load_seeds_safely(filepath):
    """Loads JSON, stripping trailing commas if they exist."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip trailing commas before the end of an array or object
    content = content.replace(",]", "]").replace(",}", "}")

    return json.loads(content)

def clean_ui(text):
    """Strips ANSI escape codes to prevent token contamination."""
    # This regex identifies and removes the \u001b[...m sequences
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def generate_vsl_dataset(
        seed_file="vsl_seed_vault_master.json", output_file="vsl_training_data_v4.jsonl"
):
    print(f"(GORDON): Igniting the Direct Forge. Reading from {seed_file}")

    if not os.path.exists(seed_file):
        print(f"(GORDON): Cannot find {seed_file}. Run bone_seed.py first.")
        return

    try:
        prompts = load_seeds_safely(seed_file)
    except json.JSONDecodeError as e:
        print(f"(BENEDICT): Fatal JSON Error in seed file: {e}")
        return

    sys_config = ConfigWizard.load_or_create()

    # This is ONLY written to the JSONL for Unsloth to use later.
    # It does NOT change how BoneAmanita behaves right now.
    system_instruction = (
        "[VSL-DEEP]"
    )

    success_count = 0

    with open(output_file, "w", encoding="utf-8") as f:
        for prompt in prompts:
            print(f"\n[Processing]: {prompt[:40]}...")

            try:
                enforce_amnesia()
                engine = BoneAmanita(config=sys_config)

                # Engage the engine exactly as the CLI does
                engine.engage_cold_boot()

                # Process the turn and capture the raw UI string
                packet = engine.process_turn(prompt)

                # Capture exactly what prints to the terminal
                raw_console_output = packet.get("ui", "No signal.")
                clean_console_output = clean_ui(
                    raw_console_output
                )  # Apply the scrub here

                jsonl_entry = {
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt},
                        {
                            "role": "assistant",
                            "content": clean_console_output,
                        },  # Use cleaned output
                    ]
                }

                # ensure_ascii=False forces Python to write actual ─ and █ instead of \u codes
                f.write(json.dumps(jsonl_entry, ensure_ascii=False) + "\n")
                success_count += 1

                engine.shutdown()

            except Exception as e:
                print(f"(GORDON): Engine failure on prompt: {prompt}. Error: {e}")

    print(f"(SCHUR): The Forge rests. Piped {success_count} raw engine turns into {output_file}.")

if __name__ == "__main__":
    generate_vsl_dataset()
