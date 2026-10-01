import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class HalcyonStore:
    """
    The persistent memory layer. Stores lexicon hive data, 
    general state records, and semantic memory vectors.
    """
    def __init__(self, db_path: str):
        self.path = Path(db_path)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        db.row_factory = sqlite3.Row
        return db

    def _init_db(self):
        schema = """
        CREATE TABLE IF NOT EXISTS records (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS lexicon_hive (
            word TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            learned_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            vector TEXT NOT NULL,
            recalled_count INTEGER DEFAULT 0
        );
        """
        with self.connect() as db:
            db.executescript(schema)

    def put_record(self, key: str, value: Any) -> None:
        val_str = json.dumps(value) if not isinstance(value, str) else value
        with self.connect() as db:
            db.execute(
                "INSERT INTO records (key, value, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, val_str, time.time())
            )

    def get_record(self, key: str) -> Optional[Any]:
        with self.connect() as db:
            row = db.execute("SELECT value FROM records WHERE key = ?", (key,)).fetchone()
            if row:
                try:
                    return json.loads(row["value"])
                except json.JSONDecodeError:
                    return row["value"]
        return None

    def learn_word(self, word: str, category: str) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO lexicon_hive (word, category, learned_at) VALUES (?, ?, ?) "
                "ON CONFLICT(word) DO UPDATE SET category=excluded.category",
                (word, category, int(time.time()))
            )

    def get_learned_vocabulary(self) -> Dict[str, List[str]]:
        vocab = {}
        with self.connect() as db:
            rows = db.execute("SELECT word, category FROM lexicon_hive")
            for r in rows:
                cat = r["category"]
                if cat not in vocab:
                    vocab[cat] = []
                vocab[cat].append(r["word"])
        return vocab

    def save_memory(self, mem_id: str, text: str, vector: List[float]) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO memories (id, text, vector) VALUES (?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET text=excluded.text, vector=excluded.vector",
                (mem_id, text, json.dumps(vector))
            )

    def get_memories(self) -> List[Dict[str, Any]]:
        mems = []
        with self.connect() as db:
            rows = db.execute("SELECT id, text, vector, recalled_count FROM memories")
            for r in rows:
                mems.append({
                    "id": r["id"],
                    "text": r["text"],
                    "vector": json.loads(r["vector"]),
                    "recalled_count": r["recalled_count"]
                })
        return mems
