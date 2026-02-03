# bone_cortex.py - The Reality Interface
# "The adult in the room."

import time
import re
from bone_shared import Prisma

class TheCortex:
    def __init__(self, engine_ref):
        self.sub = engine_ref  # The BoneAmanita Instance (The Subconscious)
        self.complexity_threshold = 0.15
        self.sanity_check_active = True
        self.awaiting_ballast = False # NEW: Track if we need user help

    def _measure_complexity(self, text: str) -> float:
        words = text.split()
        if not words: return 0.0

        # 1. Length Factor
        length_score = min(1.0, len(words) / 10.0)

        # 2. Rare Word Factor (Cheap Heuristic)
        # Words longer than 6 chars are usually 'meatier'
        complex_words = sum(1 for w in words if len(w) > 6)
        density_score = min(1.0, complex_words / max(1, len(words)))

        return (length_score * 0.6) + (density_score * 0.4)

    def _trigger_dreamless_sleep(self):
        """
        Periodic reset to prevent 'combinatorial trauma explosion'.
        """
        if self.sub.trauma_accum:
            # Dampen trauma by 50%
            self.sub.trauma_accum = {k: v * 0.5 for k, v in self.sub.trauma_accum.items()}

        if hasattr(self.sub, 'limbo'):
            # Clear ghosts
            self.sub.limbo.ghosts.clear()

        self.sub.events.log(f"{Prisma.CYN}[CORTEX]: Dreamless Sleep initiated. Trauma dampened. Ghosts dispersed.{Prisma.RST}", "SYS")

    def _process_ballast(self, text: str):
        """
        We check for 'Ballast' (Concrete nouns or Colors) to ground the system.
        """
        # 1. Define Ballast
        common_colors = {"blue", "red", "green", "yellow", "white", "black", "orange", "purple", "brown", "grey", "gray", "silver", "gold"}

        # Access lexicon to find heavy words
        lex = getattr(self.sub, 'lex', None)
        heavy_words = lex.get("heavy") if lex else set()

        # Clean input
        words = set(text.lower().replace(".", "").replace(",", "").split())

        # 2. Check for Matches
        has_color = not words.isdisjoint(common_colors)
        has_weight = not words.isdisjoint(heavy_words)

        self.awaiting_ballast = False # Release the lock regardless

        # 3. Judgment
        if has_color or has_weight:
            # REWARD: Heal the system
            self.sub.health = min(100.0, self.sub.health + 10.0)
            self.sub.stamina = min(100.0, self.sub.stamina + 20.0)
            return {
                "type": "CORTEX_INTERVENTION",
                "ui": f"{Prisma.GRN}⚓ BALLAST ACCEPTED. The room stops spinning.{Prisma.RST}\n   {Prisma.GRY}(Stability Restored. +10 HP, +20 Stamina){Prisma.RST}",
                "logs": ["CORTEX: Grounding successful. Hallucination ended."],
                "metrics": self.sub._get_metrics()
            }
        else:
            # FAIL: No penalty, but no bonus.
            return {
                "type": "CORTEX_INTERVENTION",
                "ui": f"{Prisma.OCHRE}⚓ BALLAST FAILED. That felt abstract.{Prisma.RST}\n   {Prisma.GRY}I will attempt to steady myself without help.{Prisma.RST}",
                "logs": ["CORTEX: Grounding failed. Drift continues."],
                "metrics": self.sub._get_metrics()
            }
    def _process_direct_mode(self, text: str):
        """
        Bypasses the narrative engine for raw data access.
        Triggered by '??'.
        """
        query = text.replace("??", "").strip().lower()
        response = "No data."

        # 1. STATUS CHECK
        if any(x in query for x in ["health", "status", "vitals", "hp", "stamina"]):
            h = self.sub.health
            s = self.sub.stamina
            atp = self.sub.bio.mito.state.atp_pool
            response = f"HEALTH: {h:.1f}/100 | STAMINA: {s:.1f}/100 | ATP: {atp:.1f}"
            if h < 20: response += " [CRITICAL]"

        # 2. LOCATION CHECK
        elif any(x in query for x in ["where", "loc", "zone", "map"]):
            manifold = self.sub.navigator.current_location
            zone = self.sub.phys.tension.last_physics_packet.get("zone", "UNKNOWN")
            response = f"MANIFOLD: {manifold} | INERTIA ZONE: {zone}"

        # 3. INVENTORY CHECK
        elif any(x in query for x in ["inv", "bag", "item", "holding"]):
            items = self.sub.gordon.inventory
            if items:
                response = f"INVENTORY ({len(items)}): {', '.join(items)}"
            else:
                response = "INVENTORY: Empty."

        # 4. CHEMICAL CHECK (Debug Hormones)
        elif any(x in query for x in ["chem", "hormone", "dopamine", "endo"]):
            c = self.sub.bio.endo.get_state()
            response = f"DOP:{c['DOP']} OXY:{c['OXY']} SER:{c['SER']} COR:{c['COR']}"

        # 5. GENERAL INFO
        else:
            response = "DIRECT MODE ACTIVE. Queries: ??status, ??loc, ??inv, ??chem"

        return {
            "type": "DIRECT_MODE",
            "ui": f"{Prisma.SLATE}[RAW]: {response}{Prisma.RST}",
            "logs": ["CORTEX: Direct query executed."],
            "metrics": self.sub._get_metrics()
        }

    def process(self, user_input: str):
        """
        The Executive Loop.
        """
        # 1. DIRECT OVERRIDE (New)
        if user_input.startswith("??"):
            return self._process_direct_mode(user_input)

        # 2. BALLAST INTERCEPT
        if self.awaiting_ballast:
            return self._process_ballast(user_input)

        # 3. COMPLEXITY CHECK
        complexity = self._measure_complexity(user_input)
        if complexity < self.complexity_threshold and "?" not in user_input and not user_input.startswith("/"):
            self.sub.events.log(f"{Prisma.GRY}[CORTEX]: Low complexity ({complexity:.2f}).{Prisma.RST}", "SYS")

        # 4. SUBCONSCIOUS CYCLE
        result = self.sub.cycle_controller.run_turn(user_input)

        # 5. SOLIPSISM CHECK
        last_physics = self.sub.phys.tension.last_physics_packet
        if last_physics:
            coherence = last_physics.get("truth_ratio", 0.0)
            if coherence > 0.95 and complexity < 0.2:
                self.awaiting_ballast = True
                intervention_ui = (
                    f"{Prisma.YEL}😵‍💫 VERTIGO WARNING: Hallucination Risk.{Prisma.RST}\n"
                    f"   {Prisma.WHT}Name something {Prisma.CYN}BLUE{Prisma.WHT} or heavy to ground the system.{Prisma.RST}"
                )
                result["ui"] = intervention_ui
                result["logs"].append(f"{Prisma.YEL}CORTEX: Solipsism Triggered.{Prisma.RST}")

        # 6. HYGIENE
        if self.sub.tick_count % 50 == 0:
            self._trigger_dreamless_sleep()

        return result
