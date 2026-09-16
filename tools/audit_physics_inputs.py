"""tools/audit_physics_inputs.py

Scorecard for ROADMAP A5: how much of the physics actually comes from the
hand-written lexicon, versus the phonosemantic fallback classifier.

    python tools/audit_physics_inputs.py

Reports lexicon coverage, what the fallback thinks unknown words are, how often
the DEL dimension saturates, and the resulting zone distribution. Re-run after
any change to lore/lexicon.json, lore/linguistics.json, or the classifier.
"""

import collections
import sys

sys.path.insert(0, ".")

CORPUS = [
    "hammering steel on the anvil, forging and welding the heavy frame",
    "building the structure carefully, constructing each supporting beam",
    "the abstract liminal shape of the idea itself, a concept of concepts",
    "a sacred notion, purely theoretical, framework upon framework",
    "everything is broken shattered exploding falling apart loudly",
    "the toxin spread, rot and decay through the whole system",
    "we sat and talked and laughed together in the afternoon",
    "playing games with friends in the garden on a social evening",
    "running sprinting leaping across the field at speed",
    "the engine roared and the wheels spun and we moved fast",
    "tomatoes ripening slowly in the summer greenhouse",
    "debugging a segfault in the parser at three in the morning",
    "my grandmother kept every letter she ever received in a shoebox",
    "the motel sign buzzed outside the window all night",
    "I keep circling the same thought and cannot land it",
    "we scattered the ashes where she used to walk",
]


def main():
    from mechanics.lexicon import LexiconService
    from physics.geodesics import GeodesicEngine
    from physics.observer import QuantumObserver

    lex = LexiconService()
    lex.initialize()

    # Solvents resolve through LexiconService.SOLVENTS, not the category map, so
    # counting only get_categories_for_word hides them and overstates the gap.
    solvents = getattr(lex, "SOLVENTS", None) or set()
    known = solvent = resonant = tasted = unknown = 0
    taste_dist = collections.Counter()
    resonance_dist = collections.Counter()
    # Mirrors QuantumObserver._tally_categories_static: filler, curated lexicon
    # and its inflections, semantic resonance, then the phonosemantic guess.
    for line in CORPUS:
        for word in lex.clean(line):
            if word in solvents:
                solvent += 1
                continue
            if lex.get_categories_for_word(word):
                known += 1
                continue
            if hasattr(lex, "resolve_unknown") and (found := lex.resolve_unknown(word)):
                resonant += 1
                for category in found:
                    resonance_dist[category] += 1
                continue
            category, confidence = lex.taste(word)
            if category and confidence > 0.5:
                tasted += 1
                taste_dist[category] += 1
            else:
                unknown += 1
    total = known + solvent + resonant + tasted + unknown
    resolved = known + solvent + resonant
    print(f"word resolution over {len(CORPUS)} lines, {total} words")
    print(f"  lexicon   : {known:4d}  ({known / total * 100:5.1f}%)")
    print(f"  solvents  : {solvent:4d}  ({solvent / total * 100:5.1f}%)  grammatical filler")
    print(f"  resonance : {resonant:4d}  ({resonant / total * 100:5.1f}%)  embedding centroids")
    print(f"  resolved  : {resolved:4d}  ({resolved / total * 100:5.1f}%)  <- not guessed")
    print(f"  taste     : {tasted:4d}  ({tasted / total * 100:5.1f}%)  phonosemantic guess")
    print(f"  unresolved: {unknown:4d}  ({unknown / total * 100:5.1f}%)")
    if resonance_dist:
        print(f"  resonance verdicts: {dict(resonance_dist.most_common(8))}")
    if taste_dist:
        top = taste_dist.most_common(1)[0]
        share = top[1] / max(1, sum(taste_dist.values())) * 100
        print(f"  taste verdicts: {dict(taste_dist.most_common())}")
        print(f"  most common taste verdict: {top[0]} at {share:.0f}% of all taste calls")

    zones = collections.Counter()
    del_saturated = 0
    dim_totals = collections.Counter()
    for line in CORPUS:
        words = lex.clean(line)
        counts = QuantumObserver._tally_categories_static(lex, words)
        geo = GeodesicEngine.collapse_wavefunction(words, counts)
        dims = geo.dimensions
        zones[QuantumObserver._determine_zone(dims)] += 1
        if dims.get("DEL", 0.0) >= 0.999:
            del_saturated += 1
        for key, value in dims.items():
            dim_totals[key] += value
    print(f"\nDEL saturated (>= 0.999) on {del_saturated}/{len(CORPUS)} lines")
    print("mean dimension values:")
    for key, value in sorted(dim_totals.items(), key=lambda kv: -kv[1]):
        print(f"   {key:4} {value / len(CORPUS):.3f}")
    print(f"\nzone distribution ({len(zones)} of 4 reachable):")
    for zone, n in zones.most_common():
        print(f"   {zone:12} {n:2d}  {'#' * n}")


if __name__ == "__main__":
    main()
