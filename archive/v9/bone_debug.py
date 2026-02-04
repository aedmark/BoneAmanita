# bone_debug.py

import traceback
from bone_bus import EventBus
from bone_physics import TheTensionMeter

print("--- DIAGNOSTIC START ---")
try:
    # 1. Test EventBus
    print("[1] Initializing Bus...")
    bus = EventBus()
    if not hasattr(bus, "subscribers"):
        print("FAIL: Bus missing 'subscribers' attribute.")
    else:
        print(f"PASS: Bus initialized. Subscribers type: {type(bus.subscribers)}")

    # 2. Test Physics
    print("[2] Initializing Physics...")
    tension = TheTensionMeter(bus)
    print("PASS: TensionMeter initialized.")

    # 3. Test Gaze (The Crash Site)
    print("[3] Testing Gaze...")
    # We pass a dummy text to see if it explodes
    packet = tension.gaze("TESTING GRAVITY IRON STONE")
    print("PASS: Gaze completed.")
    print(f"PASS: Output Voltage: {packet.get('physics').voltage}")

except Exception:
    print("\n!!! CRITICAL FAILURE DETECTED !!!")
    traceback.print_exc()

print("--- DIAGNOSTIC END ---")