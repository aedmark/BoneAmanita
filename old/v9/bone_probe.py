# bone_probe.py
from bone_lexicon import TheLexicon

print("--- LEXICON PROBE INITIATED ---")

# 1. Harvest a raw anomaly
print("Attempting harvest('heavy')...")
data = TheLexicon.harvest("heavy")

# 2. Inspect the structure
print(f"Type: {type(data)}")
print(f"Raw Data: {data}")

# 3. Check for keys
if isinstance(data, dict):
    print(f"Keys found: {list(data.keys())}")
else:
    print("Data is not a dictionary.")

print("--- PROBE COMPLETE ---")