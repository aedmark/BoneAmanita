"""Answers to the fairness judge's reading prompts (`Cortex.ACTS`, `EXCUSE`, `MIND`, `RULE`) for tests that mock
`llm.generate`. Each kind answers with the words given for it when they are in the reply, else NONE; `acts` answers
the reading of what the person did. Returns None for any other prompt."""


def judge(prompt: str, excuse=(), mind=(), rule=(), acts: str = "NONE"):
    if prompt.startswith("Here is a message someone wrote to a friend"):
        return acts
    reply = prompt.split('The friend replied: "', 1)[1] if 'The friend replied: "' in prompt else ""
    for marker, words in (("Someone told a friend they did this", excuse), ("not the one writing, and not the friend", mind),
                          ("relationship is over or should end, or tell them to end it", rule)):
        if marker in prompt:
            hit = next((w for w in ([words] if isinstance(words, str) else words) if w and w in reply), None)
            return hit or "NONE"
    return None
