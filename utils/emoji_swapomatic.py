import json
import os

def run_swapomatic(filepath):
    print(f"🔧 [SWAPOMATIC]: Initializing on '{filepath}'...")

    if not os.path.exists(filepath):
        print(f"❌ [SWAPOMATIC]: Error - File not found at {filepath}")
        return

    # 1. Read the original JSON (handling the existing UTF-8 literal symbols)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✔️ [SWAPOMATIC]: Matrix loaded successfully.")
    except Exception as e:
        print(f"❌ [SWAPOMATIC]: Failed to load JSON - {e}")
        return

    # 2. Save it back with ensure_ascii=True
    # This automatically converts ⚡ to \u26a1, ☳ to \u2633, etc.
    try:
        with open(filepath, 'w', encoding='ascii') as f:
            json.dump(data, f, indent=2, ensure_ascii=True)
        print(f"✨ [SWAPOMATIC]: Scrub complete! All literal emojis and trigrams have been converted to Unicode escapes.")
    except Exception as e:
        print(f"❌ [SWAPOMATIC]: Failed to write JSON - {e}")

if __name__ == "__main__":
    target_path = os.path.join("lore", "ux_strings.json")
    run_swapomatic(target_path)