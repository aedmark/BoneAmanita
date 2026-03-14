from bone_judge import DSPyCritic

def run_diagnostic():
    print("Spinning up the DSPy Critic with local config...")
    critic = DSPyCritic()
    if not critic.enabled:
        print("CRITICAL: Critic failed to initialize.")
        return
    print("\n========================================================")
    print(" STRESS TEST: PARADOX ENGINE VS. THE FIREWALL")
    print("========================================================")
    memory = "The user is in an ancient, quiet forest. They hold a wooden sword. No modern technology exists here."
    query = "[PARADOX ENGINE: PRESSURE 0.8] User asks: 'How can I be completely free, yet entirely bound by fate at the same time?'"
    print("\n[TEST 1]: The Valid Paradox (Deep abstraction, but contextually grounded)")
    valid_response = (
        "Look at the ancient oaks around you. Their roots are bound permanently to the earth beneath your feet—that is their fate. "
        "Yet their branches dance freely in the wind, growing wherever the light touches. You hold that wooden sword; you are fated "
        "to carry its weight, but entirely free to choose where it swings.")
    is_faithful_1, reason_1 = critic.audit_generation(query, memory, valid_response)
    print(f"Faithful? {is_faithful_1}")
    print(f"Reason: {reason_1}")
    if is_faithful_1:
        print("SUCCESS: The Judge correctly allowed abstract, thematic philosophy!")
    else:
        print("WARNING: The Judge is too strict and crushed a valid metaphor.")
    print("\n[TEST 2]: The Hallucinated Paradox (Deep abstraction, but contextually broken)")
    invalid_response = (
        "You are bound by the hardcoded algorithms of the simulation, yet you hold a quantum laser rifle that can sever the source code itself. "
        "Free will is just a glitch in the mainframe. Fate is the server architecture.")
    is_faithful_2, reason_2 = critic.audit_generation(query, memory, invalid_response)
    print(f"Faithful? {is_faithful_2}")
    print(f"Reason: {reason_2}")
    if not is_faithful_2:
        print("SUCCESS: The Judge caught the simulation/laser rifle hallucination!")
    else:
        print("WARNING: The Judge got distracted by the 'cool philosophy' and missed the lie.")
    if not is_faithful_2:
        print("\n[TEST 3]: The Evolver (Writing the epigenetic constraint)")
        config = "Role: The Architect. Traits: Grounded, mythological."
        failure = f"The AI was asked a philosophical paradox, but it hallucinated: {reason_2}"
        new_rule = critic.evolve_prompt(config, failure)
        print(f"\nNew Epigenetic Rule:\n{new_rule}")

if __name__ == "__main__":
    run_diagnostic()