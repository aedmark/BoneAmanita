import pytest
import os
import tempfile
from mycelium.store import HalcyonStore

@pytest.fixture
def store():
    # Use a temporary file for the database
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    db = HalcyonStore(path)
    yield db
    
    os.remove(path)

def test_records(store):
    store.put_record("test_key", {"foo": "bar"})
    val = store.get_record("test_key")
    assert val == {"foo": "bar"}
    
    store.put_record("string_key", "hello")
    assert store.get_record("string_key") == "hello"

def test_lexicon_hive(store):
    store.learn_word("synergy", "heavy")
    store.learn_word("run", "kinetic")
    
    vocab = store.get_learned_vocabulary()
    assert "synergy" in vocab["heavy"]
    assert "run" in vocab["kinetic"]

def test_memories(store):
    store.save_memory("mem1", "I am a tree.", [0.1, 0.2, 0.3])
    mems = store.get_memories()
    assert len(mems) == 1
    assert mems[0]["text"] == "I am a tree."
    assert mems[0]["vector"] == [0.1, 0.2, 0.3]
