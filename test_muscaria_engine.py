from muscaria.engine import MuscariaEngine

engine = MuscariaEngine(db_path=":memory:")
print("="*60)
print("USER: Tell me about the void.")
print("="*60)
print(f"[Pre-turn Physics] Dopamine: {engine.physics.energy.dopamine:.2f} | Stamina: {engine.physics.energy.stamina:.1f}")
response = engine.process_input("Tell me about the void.")
print(f"[Post-turn Physics] Dopamine: {engine.physics.energy.dopamine:.2f} | Stamina: {engine.physics.energy.stamina:.1f}")
print(f"\n[RESPONSE]:\n{response}")
print("="*60)
