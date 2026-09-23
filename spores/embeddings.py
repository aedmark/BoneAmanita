import hashlib
import math
import os
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Sequence

from engine.constants import Prisma
from engine.receipts import issue as issue_receipt

LEGACY_HASH_DIM = 8

_CACHE_CAPACITY = 4096
_MAX_CONSECUTIVE_FAILURES = 3
_PROBE_TEXT = "the cartographer maps the room"

_DEFAULTS: Dict[str, Any] = {
    "BACKEND": "auto",
    "MODEL": "nomic-embed-text",
    "URL": "http://127.0.0.1:11434/v1/embeddings",
    "API_KEY": "ollama",
    "TIMEOUT": 20.0,
    "MAX_CHARS": 2048,
    "NORMALIZE": True,
}

_ENV_KEYS = {
    "BACKEND": "BONE_EMBED_BACKEND",
    "MODEL": "BONE_EMBED_MODEL",
    "URL": "BONE_EMBED_URL",
    "API_KEY": "BONE_EMBED_API_KEY",
    "TIMEOUT": "BONE_EMBED_TIMEOUT",
    "MAX_CHARS": "BONE_EMBED_MAX_CHARS",
}


def _hash_to_vector(text: str, dim: int = LEGACY_HASH_DIM) -> List[float]:
    h = hashlib.shake_256(text.encode("utf-8")).digest(dim)
    return [(b / 127.5) - 1.0 for b in h]

def _l2_normalize(vec: Sequence[float]) -> List[float]:
    norm = math.sqrt(sum(float(v) * float(v) for v in vec))
    if norm <= 1e-12:
        return [float(v) for v in vec]
    return [float(v) / norm for v in vec]

class SemanticEmbedder:
    _instance: Optional["SemanticEmbedder"] = None
    _instance_lock = threading.Lock()

    def __init__(self, events_ref=None, **overrides):
        self.events = events_ref
        self._lock = threading.RLock()
        self._cache: "OrderedDict[str, List[float]]" = OrderedDict()
        self._settings_faults: List[str] = []
        self._settings = self._resolve_settings(overrides, self._settings_faults)
        self.backend = "hash"
        self.model = ""
        self.dimension = LEGACY_HASH_DIM
        self.degraded = True
        self.detail = "not yet resolved"
        self._consecutive_failures = 0
        self._st_model = None
        self._warned = set()
        for fault in self._settings_faults:
            self._log(
                f"{Prisma.YEL}Embedding config ignored: {fault}.{Prisma.RST}", "WARN"
            )
        self._resolve_backend()

    @staticmethod
    def _resolve_settings(overrides: Dict[str, Any], faults: Optional[List[str]] = None) -> Dict[str, Any]:
        settings = dict(_DEFAULTS)
        for key, val in (overrides or {}).items():
            if val not in (None, ""):
                settings[str(key).upper()] = val
        for key, env_name in _ENV_KEYS.items():
            raw = os.environ.get(env_name)
            if raw not in (None, ""):
                settings[key] = raw
        faults = [] if faults is None else faults
        for numeric in ("TIMEOUT", "MAX_CHARS"):
            raw_value = settings[numeric]
            try:
                settings[numeric] = float(raw_value)
            except (TypeError, ValueError):
                settings[numeric] = _DEFAULTS[numeric]
                faults.append(
                    f"{numeric}={raw_value!r} is not a number; using {_DEFAULTS[numeric]}"
                )
        settings["MAX_CHARS"] = max(64, int(settings["MAX_CHARS"]))
        settings["BACKEND"] = str(settings["BACKEND"]).strip().lower()
        return settings

    def _log(self, message: str, level: str = "INFO"):
        if self.events is not None and hasattr(self.events, "log"):
            try:
                self.events.log(message, "EMBED", level)
                return
            except Exception:
                pass
        print(message)

    def _resolve_backend(self):
        requested = self._settings["BACKEND"]
        failures: List[str] = []
        order = (
            ["http", "sentence_transformers"]
            if requested in ("auto", "")
            else [requested]
        )
        for candidate in order:
            if candidate == "hash":
                break
            probe = getattr(self, f"_probe_{candidate}", None)
            if probe is None:
                self._log(
                    f"{Prisma.YEL}Unknown backend '{candidate}'. Falling through.{Prisma.RST}",
                    "WARN",
                )
                continue
            try:
                if probe():
                    self.degraded = False
                    self.detail = f"resolved via {candidate}"
                    self._log(
                        f"{Prisma.GRN}Semantic cortex online: "
                        f"{self.backend}:{self.model} @ {self.dimension}d.{Prisma.RST}",
                        "INFO",
                    )
                    return
            except Exception as e:
                failures.append(f"{candidate}: {type(e).__name__}: {e}")
                continue
            failures.append(f"{candidate}: {self.detail}")
        self.backend = "hash"
        self.model = "shake_256"
        self.dimension = LEGACY_HASH_DIM
        self.degraded = True
        if requested == "hash":
            self.detail = "hash backend requested explicitly"
            return
        self.detail = "; ".join(failures) or "no backends probed"
        self._log(
            f"{Prisma.YEL}No embedding backend reachable ({self.detail}). "
            f"Falling back to the SHAKE-256 hash: associative recall is DISABLED, "
            f"retrieval will be effectively arbitrary. Set BONE_EMBED_URL/BONE_EMBED_MODEL "
            f"or install sentence-transformers to restore it.{Prisma.RST}",
            "WARN",
        )

    def _probe_http(self) -> bool:
        try:
            import requests
        except ImportError:
            self.detail = "requests is not installed"
            return False
        vectors = self._http_embed([_PROBE_TEXT])
        if not vectors or not vectors[0]:
            return False
        self.backend = "http"
        self.model = str(self._settings["MODEL"])
        self.dimension = len(vectors[0])
        with self._lock:
            self._cache[self._cache_key(_PROBE_TEXT)] = self._finalize(vectors[0])
        return True

    def _probe_sentence_transformers(self) -> bool:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            self.detail = "sentence-transformers is not installed"
            return False
        name = str(self._settings["MODEL"])
        if name == _DEFAULTS["MODEL"]:
            name = "sentence-transformers/all-MiniLM-L6-v2"
        self._st_model = SentenceTransformer(name)
        probe = self._st_model.encode([_PROBE_TEXT])
        self.backend = "sentence_transformers"
        self.model = name
        self.dimension = int(len(probe[0]))
        return True

    def _http_embed(self, texts: List[str]) -> List[List[float]]:
        import requests

        headers = {"Content-Type": "application/json"}
        api_key = self._settings.get("API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        payload = {"model": self._settings["MODEL"], "input": texts}
        resp = requests.post(
            str(self._settings["URL"]),
            json=payload,
            headers=headers,
            timeout=float(self._settings["TIMEOUT"]),
        )
        resp.raise_for_status()
        body = resp.json()
        rows = body.get("data")
        if not isinstance(rows, list) or len(rows) != len(texts):
            raise ValueError(
                f"embeddings endpoint returned {len(rows) if isinstance(rows, list) else 'no'} "
                f"rows for {len(texts)} inputs"
            )
        ordered = sorted(rows, key=lambda r: int(r.get("index", 0)))
        return [list(r.get("embedding") or []) for r in ordered]

    def _raw_embed(self, texts: List[str]) -> List[List[float]]:
        if self.backend == "http":
            return self._http_embed(texts)
        if self.backend == "sentence_transformers":
            encoded = self._st_model.encode(texts)
            return [list(map(float, row)) for row in encoded]
        return [_hash_to_vector(t, self.dimension) for t in texts]

    def _degrade(self, error: Exception):
        self.degraded = True
        self._consecutive_failures += 1
        if self._consecutive_failures < _MAX_CONSECUTIVE_FAILURES:
            return
        if self.backend != "hash":
            self._log(
                f"{Prisma.RED}Backend '{self.backend}' failed "
                f"{self._consecutive_failures}x ({error}). Severing to hash fallback; "
                f"associative recall is now arbitrary.{Prisma.RST}",
                "CRIT",
            )
        self.backend = "hash"
        self.model = "shake_256"
        self._cache.clear()

    def _cache_key(self, text: str) -> str:
        return f"{self.backend}:{self.model}:{text}"

    def _finalize(self, vec: Sequence[float]) -> List[float]:
        if self._settings.get("NORMALIZE", True):
            return _l2_normalize(vec)
        return [float(v) for v in vec]

    def _clean(self, text: Any) -> str:
        return str(text or "").strip()[: int(self._settings["MAX_CHARS"])]

    def _cache_get(self, key: str) -> Optional[List[float]]:
        with self._lock:
            hit = self._cache.get(key)
            if hit is not None:
                self._cache.move_to_end(key)
                return list(hit)
        return None

    def _cache_put(self, key: str, vec: List[float]):
        with self._lock:
            self._cache[key] = list(vec)
            self._cache.move_to_end(key)
            while len(self._cache) > _CACHE_CAPACITY:
                self._cache.popitem(last=False)

    def embed(self, text: Any) -> List[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: Sequence[Any]) -> List[List[float]]:
        with self._lock:
            return self._embed_batch_locked(texts)

    def _embed_batch_locked(self, texts: Sequence[Any]) -> List[List[float]]:
        cleaned = [self._clean(t) for t in texts]
        results = [[0.0] * self.dimension for _ in cleaned]
        pending: List[str] = []
        pending_slots: Dict[str, List[int]] = {}
        cache_hits = 0

        for i, text in enumerate(cleaned):
            if not text:
                continue
            if (hit := self._cache_get(self._cache_key(text))) is not None:
                results[i] = hit
                cache_hits += 1
                continue
            if text not in pending_slots:
                pending_slots[text] = []
                pending.append(text)
            pending_slots[text].append(i)

        if not pending:
            return results

        vector_backend = self.backend
        failure = ""
        try:
            raw = self._raw_embed(pending)
            if len(raw) != len(pending):
                raise ValueError("embedding batch row count mismatch")
            finalized = []
            for row in raw:
                if len(row) != self.dimension:
                    raise ValueError("embedding vector dimension mismatch")
                vec = [float(v) for v in row]
                if not all(math.isfinite(v) for v in vec):
                    raise ValueError("embedding vector contains non-finite values")
                finalized.append(self._finalize(vec))
            self._consecutive_failures = 0
            self.degraded = self.backend == "hash"
            if not self.degraded:
                self.detail = f"vectorized via {self.backend}"
        except Exception as e:
            failure = self.detail = f"{type(e).__name__}: {e}"
            if "embed_failure" not in self._warned:
                self._warned.add("embed_failure")
                self._log(
                    f"{Prisma.YEL}Vectorization failed ({self.detail}). "
                    f"Serving hash coordinates for this sweep.{Prisma.RST}",
                    "WARN",
                )
            self._degrade(e)
            vector_backend = "hash"
            pending = list(dict.fromkeys(t for t in cleaned if t))
            finalized = [
                self._finalize(_hash_to_vector(t, self.dimension)) for t in pending
            ]
            fallback = dict(zip(pending, finalized))
            results = [fallback[t] if t else [0.0] * self.dimension for t in cleaned]
            cache_hits = 0

        for text, vec in zip(pending, finalized):
            if not failure or self.backend == "hash":
                self._cache_put(self._cache_key(text), vec)
            if not failure:
                for slot in pending_slots[text]:
                    results[slot] = vec

        issue_receipt(
            "embeddings.embed_batch",
            f"vectorized via {vector_backend}",
            result_count=len(pending),
            degraded=vector_backend == "hash",
            inputs={
                "requested": len(cleaned),
                "cache_hits": cache_hits,
                "dimension": self.dimension,
                "active_backend": self.backend,
                "vector_backend": vector_backend,
                "vector_model": "shake_256" if vector_backend == "hash" else self.model,
            },
            detail=self.detail if vector_backend == "hash" else "",
        )
        return results

    def describe(self) -> str:
        state = "DEGRADED" if self.degraded else "NOMINAL"
        return f"{self.backend}:{self.model} {self.dimension}d [{state}]"

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            cached = len(self._cache)
        return {
            "backend": self.backend,
            "model": self.model,
            "dimension": self.dimension,
            "degraded": self.degraded,
            "cached": cached,
            "detail": self.detail,
        }

    @classmethod
    def get_instance(cls, events_ref=None, **overrides) -> "SemanticEmbedder":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls(events_ref=events_ref, **overrides)
        elif events_ref is not None and cls._instance.events is None:
            cls._instance.events = events_ref
        return cls._instance

    @classmethod
    def configure(cls, events_ref=None, **overrides) -> "SemanticEmbedder":
        with cls._instance_lock:
            cls._instance = cls(events_ref=events_ref, **overrides)
        return cls._instance

    @classmethod
    def reset(cls):
        with cls._instance_lock:
            cls._instance = None


def embed(text: Any) -> List[float]:
    return SemanticEmbedder.get_instance().embed(text)


def embed_batch(texts: Sequence[Any]) -> List[List[float]]:
    return SemanticEmbedder.get_instance().embed_batch(texts)


def embedding_dimension() -> int:
    return SemanticEmbedder.get_instance().dimension
