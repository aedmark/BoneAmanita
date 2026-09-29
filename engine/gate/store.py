"""The Halcyon store, ported from bone-iris: canonical state, its audit trail, and what the engine learns
or needs to resume, in one SQLite file (saves/iris.db). What BoneAmanita had no use for was pruned
(20.7.4.67); the affect vector, Self claims and profile seeds stay dormant until Gordon's discussion."""
from __future__ import annotations

import copy
import json
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .graph import empty_world, normalize_world


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.in_story = lambda: False  # the engine says when it is in ADVENTURE (secrets.py)
        self.mode = lambda: None       # and which mode a memory is kept in (memory_meta)
        self._init()

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("PRAGMA journal_mode = WAL")
        db.execute("PRAGMA synchronous = FULL")
        return db

    @contextmanager
    def transaction(self, immediate: bool = False) -> Iterator[sqlite3.Connection]:
        with self._lock:
            db = self.connect()
            try:
                db.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
                yield db
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()

    def _init(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS conversations (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, created_at REAL NOT NULL,
          updated_at REAL NOT NULL, archived_at REAL
        );
        CREATE TABLE IF NOT EXISTS turns (
          id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL REFERENCES conversations(id),
          ordinal INTEGER NOT NULL, status TEXT NOT NULL, outcome TEXT,
          context_state_sequence INTEGER NOT NULL, created_at REAL NOT NULL,
          completed_at REAL, error_code TEXT, input_tokens INTEGER,
          reasoning_tokens INTEGER, output_tokens INTEGER, total_tokens INTEGER,
          token_count_source TEXT, context_limit INTEGER,
          UNIQUE(conversation_id, ordinal)
        );
        CREATE TABLE IF NOT EXISTS messages (
          id TEXT PRIMARY KEY, turn_id TEXT NOT NULL REFERENCES turns(id),
          conversation_id TEXT NOT NULL REFERENCES conversations(id), role TEXT NOT NULL,
          raw_content TEXT NOT NULL, display_content TEXT NOT NULL,
          reasoning_content TEXT, reasoning_kind TEXT, status TEXT NOT NULL,
          created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS turn_contexts (
          turn_id TEXT PRIMARY KEY REFERENCES turns(id), mode TEXT, zone TEXT,
          recalled_json TEXT NOT NULL, facts_json TEXT NOT NULL, refusal_json TEXT,
          model_id TEXT, created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS receipts (
          id TEXT PRIMARY KEY, turn_id TEXT UNIQUE NOT NULL REFERENCES turns(id),
          decision TEXT NOT NULL, outcome TEXT NOT NULL, claim_json TEXT,
          rationale TEXT NOT NULL, decision_basis_json TEXT NOT NULL,
          result_json TEXT, boundary_hash TEXT NOT NULL, created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proposals (
          id TEXT PRIMARY KEY, turn_id TEXT UNIQUE NOT NULL REFERENCES turns(id),
          raw_line TEXT NOT NULL, what_path TEXT, verb TEXT, raw_args TEXT,
          normalized_args_json TEXT, parse_status TEXT NOT NULL, created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS gate_decisions (
          id TEXT PRIMARY KEY, turn_id TEXT UNIQUE NOT NULL REFERENCES turns(id),
          proposal_id TEXT REFERENCES proposals(id), admission TEXT NOT NULL,
          execution TEXT NOT NULL, persistence TEXT NOT NULL,
          terminal_stage TEXT NOT NULL, checks_json TEXT NOT NULL, created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS mutations (
          id TEXT PRIMARY KEY, turn_id TEXT UNIQUE NOT NULL REFERENCES turns(id),
          state_sequence_before INTEGER NOT NULL, state_sequence_after INTEGER NOT NULL,
          verb TEXT NOT NULL, what_path TEXT NOT NULL, args_json TEXT NOT NULL,
          result_json TEXT, patch_json TEXT NOT NULL, created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS canonical_state (
          singleton INTEGER PRIMARY KEY CHECK(singleton = 1), sequence INTEGER NOT NULL,
          world_json TEXT NOT NULL, self_json TEXT NOT NULL, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS engine_records (
          key TEXT PRIMARY KEY, value_json TEXT NOT NULL, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS learned_words (
          category TEXT NOT NULL, word TEXT NOT NULL, learned_tick INTEGER NOT NULL,
          updated_at REAL NOT NULL, PRIMARY KEY(category, word)
        );
        CREATE TABLE IF NOT EXISTS memory_stats (
          key TEXT PRIMARY KEY, recalled INTEGER NOT NULL, last_recalled REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS memory_meta (
          key TEXT PRIMARY KEY, mode TEXT, turn_id TEXT NOT NULL, kept_at REAL NOT NULL,
          receipt_id TEXT, kept_by TEXT, feeling_json TEXT
        );
        CREATE TABLE IF NOT EXISTS memory_vectors (
          key TEXT PRIMARY KEY, text_hash TEXT NOT NULL, model TEXT NOT NULL,
          vector_json TEXT NOT NULL, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS engine_checkpoint (
          singleton INTEGER PRIMARY KEY CHECK(singleton = 1), snapshot_json TEXT NOT NULL,
          state_sequence INTEGER NOT NULL, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS seed_imports (
          seed_id TEXT NOT NULL, seed_version INTEGER NOT NULL, seed_hash TEXT NOT NULL,
          source_path TEXT NOT NULL, state_sequence INTEGER NOT NULL, imported_at REAL NOT NULL,
          PRIMARY KEY(seed_id, seed_hash)
        );
        CREATE TABLE IF NOT EXISTS affect_state (
          dimension TEXT PRIMARY KEY, current_value REAL NOT NULL, baseline REAL NOT NULL,
          homeostasis_rate REAL NOT NULL, max_delta REAL NOT NULL, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS affect_history (
          id TEXT PRIMARY KEY, source_event_id TEXT NOT NULL UNIQUE, transition_kind TEXT NOT NULL,
          before_json TEXT NOT NULL, delta_json TEXT NOT NULL, after_json TEXT NOT NULL,
          created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS domain_versions (
          domain TEXT PRIMARY KEY, version INTEGER NOT NULL, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS self_claims (
          id TEXT PRIMARY KEY, kind TEXT NOT NULL, subject TEXT NOT NULL,
          predicate TEXT NOT NULL, value TEXT NOT NULL, status TEXT NOT NULL,
          source TEXT NOT NULL, created_at REAL NOT NULL, self_version INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_turns_conversation ON turns(conversation_id, ordinal);
        CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at);
        """
        with self.connect() as db:
            # Pruned in 20.7.4.67; turn_contexts was Iris's whole-prompt shape, never written here.
            for table in ("turn_braid_contexts", "turn_system_contexts", "memory_entries", "active_context",
                          "capabilities", "tool_receipts", "imagination_turns", "imagination_runs"):
                db.execute(f"DROP TABLE IF EXISTS {table}")
            if "instructions_text" in {r[1] for r in db.execute("PRAGMA table_info(turn_contexts)")}:
                db.execute("DROP TABLE turn_contexts")
            db.executescript(schema)
            # memory_meta gained who kept each memory and its receipt (20.7.4.66), and how it felt (20.7.4.68).
            have = {r[1] for r in db.execute("PRAGMA table_info(memory_meta)")}
            for column in ("receipt_id", "kept_by", "feeling_json"):
                if column not in have:
                    db.execute(f"ALTER TABLE memory_meta ADD COLUMN {column} TEXT")
            now = time.time()
            world = empty_world()
            self_state = {"name": "halcyon", "memory": {}}
            db.execute(
                "INSERT OR IGNORE INTO canonical_state VALUES (1, 0, ?, ?, ?)",
                (json.dumps(world), json.dumps(self_state), now),
            )
            for dimension in ('joy','sadness','fear','anger','trust','disgust','surprise','anticipation'):
                db.execute("INSERT OR IGNORE INTO affect_state VALUES (?,50.0,50.0,0.015,10.0,?)", (dimension, now))
            for domain in ("self", "affect"):
                db.execute("INSERT OR IGNORE INTO domain_versions VALUES (?,0,?)", (domain, now))
            db.execute("DELETE FROM domain_versions WHERE domain NOT IN ('self','affect')")
            db.commit()

    def state(self, db: sqlite3.Connection | None = None) -> tuple[int, dict]:
        owns = db is None
        db = db or self.connect()
        try:
            row = db.execute("SELECT * FROM canonical_state WHERE singleton=1").fetchone()
            return row["sequence"], {
                "world": normalize_world(json.loads(row["world_json"])),
                "self": json.loads(row["self_json"]),
            }
        finally:
            if owns:
                db.close()

    def commit_cycle(self, trace_id: str, new_state: dict, expected_sequence: int, receipt: dict, raw: str,
                     *, user_text: str = "", display: str = "", boundary_hash: str = "", by: str = "model",
                     context: dict | None = None, feeling: dict | None = None, mode: str | None = None) -> dict:
        """One engine turn, atomically: canonical state plus its audit trail (turn, messages, proposal,
        receipt, gate decision, mutation), in the shape Brad's `finalize` writes. Secrets are withheld from it.
        What the effect wrote carries the receipt as its source; `by` says who nominated it. `context` is what
        the model was handed for this turn's reply (turn_contexts) and its token usage (the turn's columns);
        `feeling` is the endocrine state, kept with a remembered memory; `mode` overrides the engine's (a REM
        reflection is kept in its zone's mode, not whichever mode the engine slept in)."""
        from .secrets import scrub, scrub_all

        story = self.in_story()
        mode = self.mode() if mode is None else mode
        user_text, raw, display = (scrub(t, story) for t in (user_text, raw, display))
        receipt = scrub_all(receipt, story)
        now = time.time()
        with self.transaction(immediate=True) as db:
            current_sequence, old_state = self.state(db)
            if current_sequence != expected_sequence:
                raise StateConflict(current_sequence)
            outcome = receipt_outcome(receipt)
            state_changed = new_state != old_state and receipt["decision"] == "ACCEPT"
            next_sequence = current_sequence + 1 if state_changed else current_sequence
            turn_id, receipt_id = _id("turn"), _id("rcpt")
            if state_changed:
                new_state = {**new_state, "world": stamp_sources(
                    old_state["world"], new_state["world"], receipt_id,
                    {"kind": "gate", "turn": turn_id, "verb": (receipt.get("claim") or {}).get("verb"),
                     "mode": mode, "by": by, "at": now})}
                db.execute(
                    "UPDATE canonical_state SET sequence=?, world_json=?, self_json=?, updated_at=? WHERE singleton=1",
                    (next_sequence, json.dumps(new_state["world"]), json.dumps(new_state["self"]), now),
                )
            conversation_id = self._session_conversation(db, user_text, now)
            ordinal = db.execute(
                "SELECT COALESCE(MAX(ordinal),0)+1 n FROM turns WHERE conversation_id=?", (conversation_id,)
            ).fetchone()["n"]
            db.execute(
                "INSERT INTO turns (id,conversation_id,ordinal,status,outcome,context_state_sequence,created_at,completed_at) "
                "VALUES (?,?,?,'complete',?,?,?,?)",
                (turn_id, conversation_id, ordinal, outcome, current_sequence, now, now),
            )
            if context:
                usage = context.get("usage") or {}
                db.execute("INSERT INTO turn_contexts VALUES (?,?,?,?,?,?,?,?)",
                           (turn_id, context.get("mode"), context.get("zone"), json.dumps(context.get("recalled") or []),
                            json.dumps(context.get("facts") or []),
                            json.dumps(context["refusal"]) if context.get("refusal") else None, context.get("model"), now))
                if usage.get("prompt_tokens") is not None:
                    total = (usage.get("prompt_tokens") or 0) + (usage.get("output_tokens") or 0)
                    db.execute("UPDATE turns SET input_tokens=?, output_tokens=?, total_tokens=?, token_count_source='provider', "
                               "context_limit=? WHERE id=?",
                               (usage.get("prompt_tokens"), usage.get("output_tokens"), total, usage.get("num_ctx"), turn_id))
            db.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,NULL,NULL,'final',?)",
                       (_id("msg"), turn_id, conversation_id, "user", user_text, user_text, now))
            db.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,NULL,NULL,'final',?)",
                       (_id("msg"), turn_id, conversation_id, "assistant", raw, display, now))
            proposal = proposal_from(raw, receipt)
            proposal_id = None
            if proposal:
                proposal_id = _id("prop")
                db.execute(
                    "INSERT INTO proposals VALUES (?,?,?,?,?,?,?,?,?)",
                    (proposal_id, turn_id, proposal["raw_line"], proposal.get("what_path"),
                     proposal.get("verb"), proposal.get("raw_args"),
                     json.dumps(proposal.get("normalized_args")) if proposal.get("normalized_args") else None,
                     proposal["parse_status"], now),
                )
            db.execute(
                "INSERT INTO receipts VALUES (?,?,?,?,?,?,?,?,?,?)",
                (receipt_id, turn_id, receipt["decision"], outcome,
                 json.dumps(receipt["claim"]) if receipt.get("claim") else None,
                 receipt["rationale"], json.dumps(receipt["decision_basis"]),
                 json.dumps(receipt["result"]) if receipt.get("result") is not None else None,
                 boundary_hash, now),
            )
            admission, execution, persistence, terminal = decision_dimensions(receipt, state_changed)
            db.execute(
                "INSERT INTO gate_decisions VALUES (?,?,?,?,?,?,?,?,?)",
                (_id("gate"), turn_id, proposal_id, admission, execution, persistence,
                 terminal, json.dumps(receipt["decision_basis"]), now),
            )
            if state_changed:
                claim = receipt["claim"]
                if claim["verb"] in ("remember", "reflect"):
                    db.execute("INSERT OR REPLACE INTO memory_meta (key, mode, turn_id, kept_at, receipt_id, kept_by, "
                               "feeling_json) VALUES (?,?,?,?,?,?,?)",
                               (claim["args"]["key"], mode, turn_id, now, receipt_id, by,
                                json.dumps(feeling) if feeling else None))
                elif claim["verb"] == "forget":
                    db.executemany("DELETE FROM memory_meta WHERE key=?",
                                   [(k,) for k in (receipt.get("result") or {}).get("forgot", [])])
                db.execute(
                    "INSERT INTO mutations VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (_id("mut"), turn_id, current_sequence, next_sequence, claim["verb"],
                     claim["what"], json.dumps(claim["args"]), json.dumps(receipt.get("result")),
                     json.dumps(scrub_all({"before": old_state, "after": new_state}, story)), now),
                )
        return {"turn_id": turn_id, "outcome": outcome, "state_sequence": next_sequence,
                "receipt_id": receipt_id, "proposal_id": proposal_id}

    def save_checkpoint(self, snapshot: dict) -> int:
        """BoneAmanita's resume point (was saves/quicksave.json): one row, replaced atomically,
        tagged with the canonical sequence it was taken against. Returns that sequence."""
        payload = json.dumps(snapshot)
        now = time.time()
        with self.transaction(immediate=True) as db:
            sequence, _ = self.state(db)
            db.execute(
                "INSERT INTO engine_checkpoint VALUES (1, ?, ?, ?) ON CONFLICT(singleton) DO UPDATE SET "
                "snapshot_json=excluded.snapshot_json, state_sequence=excluded.state_sequence, updated_at=excluded.updated_at",
                (payload, sequence, now),
            )
        return sequence

    def put_record(self, key: str, value) -> None:
        """One named piece of engine state (e.g. "akashic.state"), replaced atomically."""
        payload = json.dumps(value)
        with self.transaction(immediate=True) as db:
            db.execute(
                "INSERT INTO engine_records VALUES (?,?,?) ON CONFLICT(key) DO UPDATE SET "
                "value_json=excluded.value_json, updated_at=excluded.updated_at",
                (key, payload, time.time()),
            )

    def record(self, key: str):
        """A named piece of engine state, or None if it was never saved."""
        db = self.connect()
        try:
            row = db.execute("SELECT value_json FROM engine_records WHERE key=?", (key,)).fetchone()
        finally:
            db.close()
        return None if row is None else json.loads(row["value_json"])

    def learned_vocabulary(self) -> dict[str, dict[str, int]]:
        """Every word the lexicon taught itself, by category (was saves/cortex_hive.json)."""
        db = self.connect()
        try:
            rows = db.execute("SELECT category, word, learned_tick FROM learned_words").fetchall()
        finally:
            db.close()
        vocab: dict[str, dict[str, int]] = {}
        for row in rows:
            vocab.setdefault(row["category"], {})[row["word"]] = row["learned_tick"]
        return vocab

    def learn_word(self, category: str, word: str, tick: int, evicted: str | None = None) -> None:
        """One learned word, durable at once; the word it evicted from a full category goes in the same transaction."""
        now = time.time()
        with self.transaction(immediate=True) as db:
            if evicted:
                db.execute("DELETE FROM learned_words WHERE category=? AND word=?", (category, evicted))
            db.execute(
                "INSERT INTO learned_words VALUES (?,?,?,?) ON CONFLICT(category, word) DO UPDATE SET "
                "learned_tick=excluded.learned_tick, updated_at=excluded.updated_at",
                (category, word, int(tick), now),
            )

    def save_learned_vocabulary(self, vocab: dict) -> None:
        """Replace the whole learned vocabulary (the import of an old hive, and the shutdown sync)."""
        now = time.time()
        with self.transaction(immediate=True) as db:
            db.execute("DELETE FROM learned_words")
            db.executemany(
                "INSERT INTO learned_words VALUES (?,?,?,?)",
                [(cat, word, int(tick), now) for cat, words in vocab.items() for word, tick in words.items()],
            )

    def memory_vectors(self) -> dict[str, tuple[str, str, list]]:
        """Each self/memory entry's embedding, as {key: (text_hash, model, vector)}."""
        db = self.connect()
        try:
            rows = db.execute("SELECT key, text_hash, model, vector_json FROM memory_vectors").fetchall()
        finally:
            db.close()
        return {r["key"]: (r["text_hash"], r["model"], json.loads(r["vector_json"])) for r in rows}

    def save_memory_vectors(self, rows: list, keep: set) -> None:
        """Upsert (key, text_hash, model, vector) rows and drop vectors of memories no longer held."""
        now = time.time()
        with self.transaction(immediate=True) as db:
            db.executemany(
                "INSERT INTO memory_vectors VALUES (?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET "
                "text_hash=excluded.text_hash, model=excluded.model, vector_json=excluded.vector_json, "
                "updated_at=excluded.updated_at",
                [(k, h, m, json.dumps(v), now) for k, h, m, v in rows],
            )
            for (key,) in db.execute("SELECT key FROM memory_vectors").fetchall():
                if key not in keep:
                    db.execute("DELETE FROM memory_vectors WHERE key=?", (key,))

    def note_recalled(self, keys: list) -> None:
        """Memories handed back to the model this turn; forgetting evicts the least recalled first."""
        now = time.time()
        with self.transaction(immediate=True) as db:
            db.executemany(
                "INSERT INTO memory_stats VALUES (?,1,?) ON CONFLICT(key) DO UPDATE SET "
                "recalled=recalled+1, last_recalled=excluded.last_recalled",
                [(k, now) for k in keys],
            )

    def memory_stats(self) -> dict[str, tuple[int, float]]:
        """{key: (times recalled, when last recalled)} for memories recalled at least once."""
        db = self.connect()
        try:
            rows = db.execute("SELECT key, recalled, last_recalled FROM memory_stats").fetchall()
        finally:
            db.close()
        return {r["key"]: (r["recalled"], r["last_recalled"]) for r in rows}

    def memory_modes(self) -> dict[str, str | None]:
        """{key: the mode it was kept in}; memories kept before 20.7.4.62 have no row."""
        return {k: m["mode"] for k, m in self.memory_meta().items()}

    def memory_meta(self) -> dict[str, dict]:
        """{key: mode, turn_id, kept_at, receipt_id, kept_by, feeling}: where each memory came from, and how
        the engine felt when it was kept."""
        db = self.connect()
        try:
            rows = db.execute("SELECT * FROM memory_meta").fetchall()
        finally:
            db.close()
        return {r["key"]: {**dict(r), "feeling": json.loads(r["feeling_json"]) if r["feeling_json"] else None}
                for r in rows}

    def provenance(self, receipt_id: str) -> dict | None:
        """The commit behind a source: when, the gate's checks, what the person said that turn, and what the
        model had been handed for its reply."""
        db = self.connect()
        try:
            row = db.execute(
                "SELECT r.created_at, r.decision, r.decision_basis_json, r.claim_json, t.ordinal, "
                "t.input_tokens, t.context_limit, c.mode, c.recalled_json, c.facts_json, c.refusal_json, "
                "(SELECT raw_content FROM messages m WHERE m.turn_id=r.turn_id AND m.role='user') user_text "
                "FROM receipts r JOIN turns t ON t.id=r.turn_id LEFT JOIN turn_contexts c ON c.turn_id=r.turn_id "
                "WHERE r.id=?", (receipt_id,)).fetchone()
        finally:
            db.close()
        return dict(row) if row else None

    def drop_memory_stats(self, keys: list) -> None:
        with self.transaction(immediate=True) as db:
            db.executemany("DELETE FROM memory_stats WHERE key=?", [(k,) for k in keys])
            db.executemany("DELETE FROM memory_vectors WHERE key=?", [(k,) for k in keys])

    def checkpoint(self) -> dict | None:
        """The last saved resume point, or None if the engine has never saved one."""
        db = self.connect()
        try:
            row = db.execute("SELECT * FROM engine_checkpoint WHERE singleton=1").fetchone()
        finally:
            db.close()
        if row is None:
            return None
        return {"snapshot": json.loads(row["snapshot_json"]), "state_sequence": row["state_sequence"],
                "updated_at": row["updated_at"]}

    def _session_conversation(self, db: sqlite3.Connection, first_text: str, now: float) -> str:
        """Every turn of one engine session belongs to one conversation, created on its first turn."""
        if getattr(self, "_conversation_id", None) is None:
            self._conversation_id = _id("conv")
            title = " ".join(str(first_text or "").split())[:56] or "BoneAmanita session"
            db.execute("INSERT INTO conversations VALUES (?, ?, ?, ?, NULL)", (self._conversation_id, title, now, now))
        else:
            db.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, self._conversation_id))
        return self._conversation_id

    def recent_decisions(self, limit: int = 10) -> list[dict]:
        """The gate's latest decisions on actual nominations (plain turns left out), newest first."""
        db = self.connect()
        try:
            rows = db.execute(
                "SELECT r.created_at, r.decision, r.decision_basis_json, r.result_json, p.verb, p.what_path "
                "FROM receipts r JOIN proposals p ON p.turn_id = r.turn_id ORDER BY r.created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        finally:
            db.close()
        return [dict(r) for r in rows]

    def audit(self, table: str, limit: int = 50) -> list[dict]:
        """Rows of one audit table, newest first."""
        if table not in {"turns", "messages", "proposals", "receipts", "gate_decisions", "mutations"}:
            raise ValueError(f"not an audit table: {table}")
        db = self.connect()
        try:
            rows = db.execute(f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            db.close()

    # Dormant, as ported: the affect vector, Self claims and their domain versions wait on the discussion
    # Gordon shelved (2026-09-27), with seed_imports. Nothing calls them.
    def _apply_affect_values(self, db: sqlite3.Connection, source_event_id: str,
                             values: dict[str, float], now: float) -> dict:
        if db.execute("SELECT 1 FROM affect_history WHERE source_event_id=?", (source_event_id,)).fetchone():
            raise ValueError("affect event already applied")
        rows = db.execute("SELECT * FROM affect_state ORDER BY rowid").fetchall()
        known = {row["dimension"]: row for row in rows}
        if set(values) != set(known):
            raise ValueError("affect proposal must contain all configured dimensions")
        before, after, delta = {}, {}, {}
        for dimension, row in known.items():
            hours = max(0.0, (now - row["updated_at"]) / 3600.0)
            current = row["current_value"] + (row["baseline"] - row["current_value"]) * min(1.0, row["homeostasis_rate"] * hours)
            value = float(values[dimension])
            change = value - current
            if not (1.0 <= value <= 100.0) or abs(change) > row["max_delta"]:
                raise ValueError(f"invalid affect transition for {dimension}")
            before[dimension], after[dimension], delta[dimension] = round(current, 2), round(value, 2), round(change, 2)
            db.execute("UPDATE affect_state SET current_value=?,updated_at=? WHERE dimension=?", (value, now, dimension))
        history_id = _id("aff")
        db.execute("INSERT INTO affect_history VALUES (?,?,?,?,?,?,?)",
                   (history_id, source_event_id, "model", json.dumps(before), json.dumps(delta), json.dumps(after), now))
        self._bump_domain(db, "affect")
        return {"id": history_id, "source_event_id": source_event_id, "before": before, "delta": delta, "after": after, "created_at": now}

    def effective_affect(self, at: float | None = None) -> dict:
        at = at or time.time()
        values, baselines, directions = {}, {}, {}
        with self.connect() as db:
            rows = db.execute("SELECT * FROM affect_state ORDER BY rowid").fetchall()
            history = db.execute("SELECT * FROM affect_history ORDER BY created_at DESC LIMIT 24").fetchall()
        for row in rows:
            current, baseline = row["current_value"], row["baseline"]
            hours = max(0.0, (at - row["updated_at"]) / 3600.0)
            pull = min(1.0, row["homeostasis_rate"] * hours)
            effective = current + (baseline - current) * pull
            values[row["dimension"]] = round(effective, 2)
            baselines[row["dimension"]] = baseline
            directions[row["dimension"]] = "steady" if abs(effective - baseline) < .01 else "settling"
        return {"values": values, "baselines": baselines, "directions": directions,
                "history": [{**dict(r), "before": json.loads(r["before_json"]), "delta": json.loads(r["delta_json"]),
                             "after": json.loads(r["after_json"])} for r in history]}

    def apply_affect(self, source_event_id: str, deltas: dict[str, float]) -> dict:
        now = time.time()
        with self.transaction(immediate=True) as db:
            if db.execute("SELECT 1 FROM affect_history WHERE source_event_id=?", (source_event_id,)).fetchone():
                raise ValueError("affect event already applied")
            rows = db.execute("SELECT * FROM affect_state ORDER BY rowid").fetchall()
            known = {row["dimension"]: row for row in rows}
            if not deltas or any(key not in known for key in deltas):
                raise ValueError("unknown or empty affect dimensions")
            before, after, applied = {}, {}, {}
            for dimension, row in known.items():
                hours = max(0.0, (now - row["updated_at"]) / 3600.0)
                base_value = row["current_value"] + (row["baseline"] - row["current_value"]) * min(1.0, row["homeostasis_rate"] * hours)
                delta = float(deltas.get(dimension, 0.0))
                if not (-row["max_delta"] <= delta <= row["max_delta"]):
                    raise ValueError(f"{dimension} delta exceeds configured limit")
                value = max(1.0, min(100.0, base_value + delta))
                before[dimension], after[dimension], applied[dimension] = round(base_value, 2), round(value, 2), round(value - base_value, 2)
                db.execute("UPDATE affect_state SET current_value=?,updated_at=? WHERE dimension=?", (value, now, dimension))
            history_id = _id("aff")
            db.execute("INSERT INTO affect_history VALUES (?,?,?,?,?,?,?)",
                       (history_id, source_event_id, "event", json.dumps(before), json.dumps(applied), json.dumps(after), now))
            self._bump_domain(db, "affect")
        return {"id": history_id, "source_event_id": source_event_id, "before": before, "delta": applied, "after": after, "created_at": now}

    @staticmethod
    def _bump_domain(db: sqlite3.Connection, domain: str) -> int:
        now = time.time()
        db.execute("UPDATE domain_versions SET version=version+1,updated_at=? WHERE domain=?", (now, domain))
        return db.execute("SELECT version FROM domain_versions WHERE domain=?", (domain,)).fetchone()["version"]

    def versions(self) -> dict[str, int]:
        with self.connect() as db:
            rows = db.execute("SELECT domain,version FROM domain_versions").fetchall()
        versions = {row["domain"]: row["version"] for row in rows}
        sequence, _ = self.state()
        versions["memory"] = max(versions.get("memory", 0), sequence)
        return versions

    def self_claims(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM self_claims WHERE status='active' ORDER BY kind,created_at").fetchall()
        return [dict(row) for row in rows]

    def add_self_claim(self, kind: str, subject: str, predicate: str, value: str,
                       source: str = "operator") -> dict:
        if kind not in {"identity","value","preference","commitment","relationship","goal","self_understanding"}:
            raise ValueError("invalid Self claim kind")
        if not all(part.strip() for part in (subject, predicate, value)):
            raise ValueError("Self claim fields cannot be empty")
        claim_id, now = _id("self"), time.time()
        with self.transaction(immediate=True) as db:
            version = self._bump_domain(db, "self")
            db.execute("INSERT INTO self_claims VALUES (?,?,?,?,?,'active',?,?,?)",
                       (claim_id, kind, subject.strip(), predicate.strip(), value.strip(), source, now, version))
            row = db.execute("SELECT * FROM self_claims WHERE id=?", (claim_id,)).fetchone()
        return dict(row)


def stamp_sources(old: dict, new: dict, receipt_id: str, source: dict, keep: int = 8) -> dict:
    """`new` world with `receipt_id` on each node, edge and constraint the commit created or changed (the
    last `keep`), and in the sources registry; sources nothing cites any more are dropped."""
    world = copy.deepcopy(new)
    bare = lambda item: {k: v for k, v in (item or {}).items() if k != "sources"}
    before = {**old.get("nodes", {}), **{e["id"]: e for e in old.get("edges", []) + old.get("constraints", [])}}
    items = list(world.get("nodes", {}).items()) + [(e["id"], e) for e in world.get("edges", []) + world.get("constraints", [])]
    for item_id, item in items:
        if bare(item) != bare(before.get(item_id)):
            item["sources"] = (list(item.get("sources") or []) + [receipt_id])[-keep:]
    cited = {s for _, item in items for s in item.get("sources") or []}
    registry = {**old.get("sources", {}), **world.get("sources", {}), receipt_id: source}
    world["sources"] = {k: v for k, v in registry.items() if k in cited}
    return world


class StateConflict(Exception):
    def __init__(self, sequence: int):
        self.sequence = sequence


def proposal_from(raw: str, receipt: dict) -> dict | None:
    """The nomination as the model wrote it, parsed or not (Brad's server.proposal_from)."""
    from .kernel import NOMINATION

    lines = [line.strip() for line in str(raw or "").splitlines() if line.strip()]
    matches = [(line, NOMINATION.match(line)) for line in lines if NOMINATION.match(line)]
    if not matches:
        nomination_like = next((line for line in lines if line.startswith("NOMINATE")), None)
        return {"raw_line": nomination_like, "parse_status": "malformed"} if nomination_like else None
    if len(matches) > 1:
        return {"raw_line": "\n".join(line for line, _ in matches), "parse_status": "multiple"}
    line, match = matches[0]
    claim = receipt.get("claim")
    return {"raw_line": line, "what_path": match.group("what"), "verb": match.group("verb"),
            "raw_args": match.group("args"), "normalized_args": claim.get("args") if claim else None,
            "parse_status": "valid"}


def receipt_outcome(receipt: dict) -> str:
    if receipt["decision"] == "NOOP":
        return "none"
    if receipt["decision"] == "DENY":
        return "denied"
    checks = receipt["decision_basis"]
    if any(c[1] == "ERROR" for c in checks):
        return "execution_failed"
    result = receipt.get("result") or {}
    if "noop" in result:
        return "noop"
    return "committed"


def decision_dimensions(receipt: dict, changed: bool) -> tuple[str, str, str, str]:
    checks = receipt["decision_basis"]
    terminal = checks[-1][0] if checks else "schema"
    if receipt["decision"] == "NOOP":
        return "none", "not_run", "not_required", terminal
    if receipt["decision"] == "DENY":
        return "denied", "not_run", "not_required", terminal
    if any(c[1] == "ERROR" for c in checks):
        return "admitted", "failed", "not_required", terminal
    execution = "applied" if changed else "noop"
    return "admitted", execution, "committed" if changed else "not_required", terminal
