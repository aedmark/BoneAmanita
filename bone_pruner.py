import json
import os
import glob


def prune_vaults(
    file_pattern="vsl_seed_vault*.json", output_filename="vsl_seed_vault_master.json"
):
    print(f"(GORDON): Initiating mass inventory audit on pattern: {file_pattern}...")

    files = glob.glob(file_pattern)

    if not files:
        print("(GORDON): No files found matching that pattern. The garden is empty.")
        return

    initial_count = 0
    seen_prompts = set()
    unique_vault = []

    for filename in files:
        print(f"(ROBERTA): Harvesting from {filename}...")
        try:
            with open(filename, "r", encoding="utf-8") as f:
                vault = json.load(f)

            if not isinstance(vault, list):
                print(f"(GORDON): Skipping {filename} - root is not a JSON array.")
                continue

            initial_count += len(vault)

            for prompt in vault:
                if not isinstance(prompt, str):
                    continue

                normalized = prompt.strip().lower()

                if normalized not in seen_prompts:
                    seen_prompts.add(normalized)
                    unique_vault.append(prompt.strip())

        except json.JSONDecodeError:
            print(
                f"(GORDON): Synapse failure in {filename}. Corrupted or invalid JSON. Skipping."
            )
        except Exception as e:
            print(f"(GORDON): Unexpected friction reading {filename}: {e}")

    final_count = len(unique_vault)
    duplicates_removed = initial_count - final_count

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(unique_vault, f, indent=2)

    print(
        f"(SCHUR): Mass audit complete! The harvest is consolidated into {output_filename}."
    )
    print(f"   -> Files Processed:  {len(files)}")
    print(f"   -> Total Raw Seeds:  {initial_count}")
    print(f"   -> Clones Removed:   {duplicates_removed}")
    print(f"   -> Final Vault Size: {final_count}")


if __name__ == "__main__":
    prune_vaults()
