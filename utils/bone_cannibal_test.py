""" simulation_cannibal.py """
import time
from bone_spores import MycelialNetwork, EventBus, BoneConfig, Prisma

# 1. CRUELTY CONFIGURATION
# We shrink the brain to a goldfish level.
BoneConfig.MAX_MEMORY_CAPACITY = 3
BoneConfig.SHAPLEY_MASS_THRESHOLD = 50.0

# 2. INITIALIZATION
events = EventBus()
network = MycelialNetwork(events)

# We patch in the Subconscious (simulated for this run)
# (Assuming the class from the previous step is active)
print(f"{Prisma.CYN}--- BEGINNING CORTICAL STRESS TEST ---{Prisma.RST}")

# 3. THE FEEDING (The Folly's Banquet)
inputs = [
    "APPLE",      # Tick 1: Safe
    "BANANA",     # Tick 2: Safe
    "CHERRY",     # Tick 3: AT CAPACITY
    "DURIAN",     # Tick 4: OVERFLOW -> TRIGGER CANNIBALISM
    "ELDERBERRY"  # Tick 5: OVERFLOW -> TRIGGER CANNIBALISM
]

for i, word in enumerate(inputs):
    tick = i + 1
    print(f"\n[{tick}] INGESTING: '{word}'")

    # Force encode
    network.encode([word], {"voltage": 50.0}, "STRESS_TEST")
    victim_msg, buried = network.bury([word], tick, desperation_level=0.8)

    # Report Status
    print(f"    Graph Size: {len(network.graph)}/{BoneConfig.MAX_MEMORY_CAPACITY}")
    if victim_msg:
        print(f"    {Prisma.RED}⚔️  CANNIBAL EVENT: {victim_msg}{Prisma.RST}")
    else:
        print(f"    {Prisma.GRN}✓  Absorbed.{Prisma.RST}")

print(f"\n{Prisma.CYN}--- TEST COMPLETE ---{Prisma.RST}")