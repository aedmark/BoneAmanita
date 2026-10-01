from spore.engine import SporeEngine

engine = SporeEngine(db_path=":memory:")
print("="*60)
print("USER: Refactor this infrastructure dependency.")
print("="*60)

# Simulate the LLM outputting fluff
bad_llm_output = "I hope this helps! In conclusion, here is the architecture."
response = engine.process_input("Refactor this infrastructure dependency.", bad_llm_output)

print(f"\n[FINAL RESPONSE]:\n{response}")
print("="*60)
