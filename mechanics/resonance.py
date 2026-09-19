import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

RESONANT_CATEGORIES = (
    "heavy", "kinetic", "constructive", "abstract", "liminal", "harvest",
    "explosive", "meat", "social", "void", "thermal", "cryo", "photo", "play",
    "toxin", "sacred", "suburban", "aerobic", "crisis_term", "pareidolia",
)

MIN_CATEGORY_SIZE = 8
MAX_CENTROID_WORDS = 48
DEFAULT_MARGIN = 0.05


def _unit(vector: Sequence[float]) -> List[float]:
    norm = math.sqrt(sum(float(v) * float(v) for v in vector))
    if norm <= 1e-12:
        return [float(v) for v in vector]
    return [float(v) / norm for v in vector]


class ResonanceClassifier:
    def __init__(self, margin: float = DEFAULT_MARGIN):
        self.margin = float(margin)
        self.centroids: Dict[str, List[float]] = {}
        self.mean: List[float] = []
        self.ready = False
        self.detail = "not built"
        self._warned = False

    def build(self, vocab: Dict[str, Sequence[str]], events: Any = None) -> bool:
        try:
            from spores.embeddings import SemanticEmbedder

            embedder = SemanticEmbedder.get_instance()
            if embedder.degraded:
                self.detail = "embedder degraded; hash vectors carry no meaning"
                return False

            blocks: List[Tuple[str, int]] = []
            words: List[str] = []
            for category in RESONANT_CATEGORIES:
                members = [
                    w for w in (vocab.get(category) or []) if w and " " not in str(w)
                ][:MAX_CENTROID_WORDS]
                if len(members) < MIN_CATEGORY_SIZE:
                    continue
                blocks.append((category, len(members)))
                words.extend(str(w) for w in members)
            if not blocks:
                self.detail = "no category large enough to form a centroid"
                return False

            matrix = embedder.embed_batch(words)
            dimension = len(matrix[0])
            mean = [0.0] * dimension
            for row in matrix:
                for i, value in enumerate(row):
                    mean[i] += value
            mean = [v / len(matrix) for v in mean]

            offset = 0
            centroids: Dict[str, List[float]] = {}
            for category, size in blocks:
                block = matrix[offset : offset + size]
                offset += size
                centred = [0.0] * dimension
                for row in block:
                    for i, value in enumerate(row):
                        centred[i] += value - mean[i]
                centroids[category] = _unit([v / size for v in centred])

            self.mean = mean
            self.centroids = centroids
            self.ready = True
            self.detail = f"{len(centroids)} categories, {len(words)} words"
            if events is not None and hasattr(events, "log"):
                events.log(
                    f"Resonance classifier online: {self.detail}.", "LEXICON", "INFO"
                )
            return True
        except Exception as e:
            self.detail = f"{type(e).__name__}: {e}"
            self.ready = False
            if events is not None and hasattr(events, "log"):
                events.log(
                    f"Resonance classifier unavailable ({self.detail}). Unknown "
                    f"words fall back to the phonosemantic classifier.",
                    "LEXICON",
                    "WARN",
                )
            else:
                print(f"[RESONANCE] Unavailable: {self.detail}")
            return False

    def classify(self, word: str) -> Tuple[Optional[str], float]:
        if not self.ready or not word:
            return None, 0.0
        try:
            from spores.embeddings import SemanticEmbedder

            raw = SemanticEmbedder.get_instance().embed(word)
        except Exception as e:
            if not self._warned:
                self._warned = True
                print(
                    f"[RESONANCE] Embedding failed ({type(e).__name__}: {e}). "
                    f"Unknown words fall back to the phonosemantic classifier."
                )
            return None, 0.0
        if not raw or len(raw) != len(self.mean):
            return None, 0.0
        vector = _unit([v - m for v, m in zip(raw, self.mean)])

        best_category, best_score, runner_up = None, -2.0, -2.0
        for category, centroid in self.centroids.items():
            score = sum(a * b for a, b in zip(vector, centroid))
            if score > best_score:
                best_category, best_score, runner_up = category, score, best_score
            elif score > runner_up:
                runner_up = score
        margin = best_score - runner_up
        if best_category is None or margin < self.margin:
            return None, round(max(0.0, margin), 3)
        return best_category, round(margin, 3)
