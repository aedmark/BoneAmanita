import time
import os
import json
from bone_amanita973 import BoneAmanita, SessionGuardian
from bone_shared import Prisma, BoneConfig

def mock_missing_data():
    if not os.path.exists("seeds.json"):
        print(f"{Prisma.GRY}[BOOT STRAP]: Creating dummy seeds.json...{Prisma.RST}")
        with open("seeds.json", "w") as f:
            json.dump({
                "SEEDS": [
                    {"question": "What is the velocity of silence?", "triggers": ["silence", "speed", "quiet"]}
                ]
            }, f)

def run_diagnostic():
    print(f"{Prisma.CYN}--- INITIATING SLASH DIAGNOSTIC ---{Prisma.RST}")

    # 1. Pre-flight checks
    mock_missing_data()

    # 2. Instantiate the Organism
    try:
        engine = BoneAmanita()
        print(f"{Prisma.GRN}✔ Engine Instantiated.{Prisma.RST}")
    except Exception as e:
        print(f"{Prisma.RED}✘ Engine Failure: {e}{Prisma.RST}")
        return

    # 3. Simulate a Turn (The Schur Test: Is it fun?)
    test_input = "I pick up the heavy stone and throw it at the sun."
    print(f"\n{Prisma.WHT}INPUT:{Prisma.RST} \"{test_input}\"")

    # Force a cycle
    result = engine.process_turn(test_input)

    # 4. Analyze Results (The Fuller Analysis)
    print(f"\n{Prisma.OCHRE}--- METABOLIC REPORT ---{Prisma.RST}")
    print(f"UI Output:\n{result.get('ui', 'NO OUTPUT')}")

    metrics = result.get('metrics', {})
    print(f"\n{Prisma.MAG}System Vitals:{Prisma.RST}")
    print(f"Health:  {metrics.get('health', 'ERR')}")
    print(f"Stamina: {metrics.get('stamina', 'ERR')}")
    print(f"ATP:     {metrics.get('atp', 'ERR')}")

    # 5. Check Internal Physics
    phys = engine.phys.tension.last_physics_packet
    if phys:
        print(f"\n{Prisma.CYN}Physics Packet:{Prisma.RST}")
        print(f"Voltage: {phys.get('voltage')} | Drag: {phys.get('narrative_drag')}")
        print(f"Vector:  {phys.get('vector')}")

if __name__ == "__main__":
    run_diagnostic()