"""tests/__init__.py"""

import os

# Pin the entire suite to the offline hash embedder before any test module is
# imported. A test run must never depend on a reachable embedding server: without
# this, whichever test happens to construct a store first decides the vector width
# for everything after it, and a test that mocks the vectorizer at one width ends
# up stacking it against live vectors at another.
#
# tests/test_embeddings.py overrides this per-test to exercise the real backends
# against mocked transport, and restores it in tearDown.
os.environ.setdefault("BONE_EMBED_BACKEND", "hash")
