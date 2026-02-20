import sys
from bone_core import LoreManifest

def probe_wiring():
    print(">>> 🧠 SLASH SUBSTRATE PROBE ONLINE")

    # 1. Force Load
    manifest = LoreManifest.get_instance()
    narrative = manifest.get("narrative_data")

    if not narrative:
        print("❌ CRITICAL: narrative_data.json failed to load.")
        return

    # 2. Check Seeds (Village Wiring)
    seeds = narrative.get("SEEDS", [])
    print(f"\n[VILLAGE] Paradox Seeds found: {len(seeds)}")
    if seeds:
        print(f"   - First Seed: \"{seeds[0].get('question', 'UNKNOWN')}\"")
        print(f"   - Triggers: {seeds[0].get('triggers', [])}")
    else:
        print("   ⚠️ WARNING: No seeds found in narrative_data['SEEDS'].")

    # 3. Check Lenses (Drivers Wiring)
    lenses = narrative.get("lenses", {})
    print(f"\n[DRIVERS] Lenses found: {len(lenses)}")
    if lenses:
        print(f"   - Roles: {list(lenses.keys())}")
        if "SHERLOCK" in lenses:
             print(f"   - Sherlock's Directives: {len(lenses['SHERLOCK'].get('directives', []))}")
    else:
        print("   ⚠️ WARNING: No lenses found in narrative_data['lenses'].")

    # 4. Check Scenarios (Cold Boot Wiring)
    scenarios = manifest.get("scenarios") or {}
    archetypes = scenarios.get("ARCHETYPES", [])
    print(f"\n[BOOT] Scenarios found: {len(archetypes)}")
    print(f"   - Sample: \"{archetypes[0] if archetypes else 'None'}\"")

if __name__ == "__main__":
    probe_wiring()