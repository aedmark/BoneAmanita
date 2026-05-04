"""machine/pacemaker.py

The Pacemaker is the system's internal metronome and attention span.
It regulates the passage of simulated time and monitors the conversational
flow for stagnation, forcing the system to react (typically via the Jester
or a systemic Phase Shift) if the interaction becomes a sycophantic or repetitive loop.
"""

from presets import BoneConfig

class ThePacemaker:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig

        # The running tally (Stock) of how long the system has been stuck in a
        # low-voltage or highly repetitive interaction loop.
        self.boredom_level = 0.0

        # Simulated biological heart rate, acting as a baseline multiplier for
        # metabolic burn rates across the broader bio-system.
        self.heart_rate = 60

        cfg = getattr(self.cfg, "MACHINE", object())
        # The tipping point. Once boredom exceeds this, the system will actively
        # seek to shatter the current conversational state and inject chaos.
        self.BOREDOM_THRESHOLD = getattr(cfg, "PACEMAKER_BOREDOM_THRESHOLD", 10.0)

    def beat(self, stress: float):
        """
        Calculates the current somatic pace of the system.
        A resting system sits at 60 BPM. High environmental or conversational stress
        scales this linearly (e.g., a stress factor of 1.0 pushes it to 80 BPM).
        """
        self.heart_rate = 60 + (stress * 20)

    def update(self, repetition_score: float, voltage: float):
        """
        The core dynamic feedback loop for attention. Evaluates the most recent
        interaction and adjusts the boredom stock accordingly.
        """
        # If the user is repeating themselves (score > 0.5) OR the conversation
        # lacks structural tension (voltage < 5.0), boredom accumulates.
        if repetition_score > 0.5 or voltage < 5.0:
            # Cap the boredom at 2x the threshold to prevent infinite accumulation.
            # This ensures the system can eventually recover if the user becomes interesting again.
            self.boredom_level = min(self.BOREDOM_THRESHOLD * 2.0, self.boredom_level + 1.0)
        else:
            # High-voltage, novel interactions relieve boredom twice as fast as it builds.
            # The max() function ensures boredom never drops below absolute zero.
            self.boredom_level = max(0.0, self.boredom_level - 2.0)

    def is_bored(self) -> bool:
        """
        A simple boolean flag read by the Global Workspace to determine if an
        intervention is required to break a conversational Point Attractor.
        """
        if self.boredom_level > self.BOREDOM_THRESHOLD:
            # Debounce: Once triggered, reset boredom to 0 to prevent a cascade loop.
            self.boredom_level = 0.0
            return True
        return False