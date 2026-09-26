"""Transactional persistence for the Halcyon server UI.

SQLite is authoritative. JSON files are compatibility projections written only
after a successful state transaction.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .graph import empty_world, normalize_world


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


class Store:
    def __init__(self, path: str | Path, state_dir: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
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
          turn_id TEXT PRIMARY KEY REFERENCES turns(id), instructions_text TEXT NOT NULL,
          knowledge_text TEXT NOT NULL, conversation_json TEXT NOT NULL,
          state_sequence INTEGER NOT NULL, model_id TEXT NOT NULL, created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS turn_braid_contexts (
          turn_id TEXT PRIMARY KEY REFERENCES turns(id), retrieved_memory_json TEXT NOT NULL,
          affect_json TEXT NOT NULL, active_context_json TEXT NOT NULL
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
        CREATE TABLE IF NOT EXISTS seed_imports (
          seed_id TEXT NOT NULL, seed_version INTEGER NOT NULL, seed_hash TEXT NOT NULL,
          source_path TEXT NOT NULL, state_sequence INTEGER NOT NULL, imported_at REAL NOT NULL,
          PRIMARY KEY(seed_id, seed_hash)
        );
        CREATE TABLE IF NOT EXISTS memory_entries (
          id TEXT PRIMARY KEY, scope_type TEXT NOT NULL, scope_id TEXT,
          channel TEXT NOT NULL CHECK(channel IN ('experience','cognitive_semantic','emotional_semantic')),
          content TEXT NOT NULL, origin TEXT NOT NULL DEFAULT 'experience',
          source_event_id TEXT, derived_from_json TEXT NOT NULL DEFAULT '[]',
          affect_before_json TEXT, affect_after_json TEXT, affect_delta_json TEXT,
          visibility TEXT NOT NULL DEFAULT 'standard', created_at REAL NOT NULL
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
        CREATE TABLE IF NOT EXISTS active_context (
          singleton INTEGER PRIMARY KEY CHECK(singleton=1), world_scope TEXT,
          task_scope TEXT, skill_scopes_json TEXT NOT NULL, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS domain_versions (
          domain TEXT PRIMARY KEY, version INTEGER NOT NULL, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS self_claims (
          id TEXT PRIMARY KEY, kind TEXT NOT NULL, subject TEXT NOT NULL,
          predicate TEXT NOT NULL, value TEXT NOT NULL, status TEXT NOT NULL,
          source TEXT NOT NULL, created_at REAL NOT NULL, self_version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS capabilities (
          id TEXT PRIMARY KEY, source TEXT NOT NULL, effect_class TEXT NOT NULL,
          description TEXT NOT NULL, schema_json TEXT NOT NULL, scope_json TEXT NOT NULL,
          limits_json TEXT NOT NULL, available INTEGER NOT NULL, boundary_version TEXT NOT NULL,
          created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tool_receipts (
          id TEXT PRIMARY KEY, tool_id TEXT NOT NULL, source TEXT NOT NULL,
          effect_class TEXT NOT NULL, raw_args_json TEXT NOT NULL, normalized_args_json TEXT,
          context_json TEXT NOT NULL, capability_version INTEGER NOT NULL,
          decision TEXT NOT NULL, checks_json TEXT NOT NULL, execution_status TEXT NOT NULL,
          result_json TEXT, error TEXT, created_at REAL NOT NULL, completed_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS turn_system_contexts (
          turn_id TEXT PRIMARY KEY REFERENCES turns(id), projection_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS imagination_runs (
          id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL REFERENCES conversations(id),
          seed TEXT NOT NULL, max_steps INTEGER NOT NULL, completed_steps INTEGER NOT NULL,
          status TEXT NOT NULL, active_turn_id TEXT REFERENCES turns(id),
          created_at REAL NOT NULL, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS imagination_turns (
          run_id TEXT NOT NULL REFERENCES imagination_runs(id),
          turn_id TEXT PRIMARY KEY REFERENCES turns(id), kind TEXT NOT NULL,
          step_number INTEGER, created_at REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_turns_conversation ON turns(conversation_id, ordinal);
        CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at);
        """
        with self.connect() as db:
            db.executescript(schema)
            now = time.time()
            world = empty_world()
            self_state = {"name": "halcyon", "memory": {}}
            db.execute(
                "INSERT OR IGNORE INTO canonical_state VALUES (1, 0, ?, ?, ?)",
                (json.dumps(world), json.dumps(self_state), now),
            )
            for dimension in ('joy','sadness','fear','anger','trust','disgust','surprise','anticipation'):
                db.execute("INSERT OR IGNORE INTO affect_state VALUES (?,50.0,50.0,0.015,10.0,?)", (dimension, now))
            db.execute("INSERT OR IGNORE INTO active_context VALUES (1,'world:iris',NULL,'[]',?)", (now,))
            db.execute("UPDATE active_context SET world_scope='world:halcyon',updated_at=? WHERE world_scope='world:iris'", (now,))
            for domain in ("self", "memory", "affect", "context", "capabilities", "governance"):
                db.execute("INSERT OR IGNORE INTO domain_versions VALUES (?,0,?)", (domain, now))
            pass
            defaults = (
                ("system.inspect", "builtin", "observe", "Inspect the composed Halcyon System Identity projection", "{}"),
                ("memory.search", "builtin", "observe", "Search currently reachable scoped Memory", '{"query":{"type":"string","required":true}}'),
                ("affect.inspect", "builtin", "observe", "Inspect effective Affect and recent trajectory", "{}"),
            )
            for tool_id, source, effect, description, schema_json in defaults:
                db.execute("INSERT OR IGNORE INTO capabilities VALUES (?,?,?,?,?,'{}','{}',1,'capability-v1',?)",
                           (tool_id, source, effect, description, schema_json, now))
            db.execute("UPDATE capabilities SET description=? WHERE id='system.inspect'",
                       ("Inspect the composed Halcyon System Identity projection",))
            db.execute("UPDATE domain_versions SET version=MAX(version,1),updated_at=? WHERE domain='capabilities'", (now,))
            db.commit()
            pass # self.recover_interrupted()

    @staticmethod
    def _install_identity(self, db, now: float) -> None:
        db.execute("INSERT OR IGNORE INTO canonical_state VALUES (1, 0, '{}', '{}', ?)", (now,))
    def recover_interrupted(self):
        pass
    def create_imagination_run(self, seed: str, max_steps: int, running: bool = True) -> dict:
        now, run_id, conversation_id = time.time(), _id("imagine"), _id("conv")
        title = f"Imagination · {' '.join(seed.split())[:42]}"
        status = "running" if running else "paused"
        with self.transaction(immediate=True) as db:
            db.execute("INSERT INTO conversations VALUES (?,?,?,?,NULL)", (conversation_id, title, now, now))
            db.execute("INSERT INTO imagination_runs VALUES (?,?,?,?,0,?,NULL,?,?)",
                       (run_id, conversation_id, seed, max_steps, status, now, now))
        return self.imagination_run(run_id)

    def imagination_run(self, run_id: str) -> dict | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM imagination_runs WHERE id=?", (run_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["conversation"] = self.conversation(result["conversation_id"])
        with self.connect() as db:
            turns = db.execute("SELECT turn_id,kind,step_number FROM imagination_turns WHERE run_id=?", (run_id,)).fetchall()
        result["turn_kinds"] = {item["turn_id"]: {"kind": item["kind"], "step": item["step_number"]} for item in turns}
        return result

    def imagination_runs(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM imagination_runs ORDER BY created_at DESC LIMIT 50").fetchall()
        return [dict(row) for row in rows]

    def set_imagination_status(self, run_id: str, status: str) -> dict | None:
        if status not in {"running", "paused", "cancelled", "complete", "failed"}:
            raise ValueError("invalid imagination status")
        with self.transaction(immediate=True) as db:
            db.execute("UPDATE imagination_runs SET status=?,updated_at=? WHERE id=?", (status, time.time(), run_id))
        return self.imagination_run(run_id)

    def imagination_step_started(self, run_id: str, turn_id: str) -> None:
        with self.transaction(immediate=True) as db:
            db.execute("UPDATE imagination_runs SET active_turn_id=?,updated_at=? WHERE id=?",
                       (turn_id, time.time(), run_id))

    def link_imagination_turn(self, run_id: str, turn_id: str, kind: str,
                              step_number: int | None = None) -> None:
        if kind not in {"chat", "autonomous"}:
            raise ValueError("invalid imagination turn kind")
        with self.transaction(immediate=True) as db:
            db.execute("INSERT INTO imagination_turns VALUES (?,?,?,?,?)",
                       (run_id, turn_id, kind, step_number, time.time()))

    def start_imagination_batch(self, run_id: str, steps: int) -> dict | None:
        if not 1 <= steps <= 20:
            raise ValueError("imagination batch must contain 1 to 20 turns")
        with self.transaction(immediate=True) as db:
            row = db.execute("SELECT completed_steps FROM imagination_runs WHERE id=?", (run_id,)).fetchone()
            if not row:
                return None
            db.execute("UPDATE imagination_runs SET max_steps=?,status='running',updated_at=? WHERE id=?",
                       (row["completed_steps"] + steps, time.time(), run_id))
        return self.imagination_run(run_id)

    def imagination_step_finished(self, run_id: str, failed: bool = False) -> dict:
        with self.transaction(immediate=True) as db:
            row = db.execute("SELECT * FROM imagination_runs WHERE id=?", (run_id,)).fetchone()
            completed = row["completed_steps"] + (0 if failed else 1)
            if failed:
                status = "failed"
            elif row["status"] in {"paused", "cancelled"}:
                status = row["status"]
            elif completed >= row["max_steps"]:
                status = "complete"
            else:
                status = "running"
            db.execute("UPDATE imagination_runs SET completed_steps=?,status=?,active_turn_id=NULL,updated_at=? WHERE id=?",
                       (completed, status, time.time(), run_id))
        return self.imagination_run(run_id)

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

    def conversations(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT c.*, COUNT(t.id) turn_count FROM conversations c "
                "LEFT JOIN turns t ON t.conversation_id=c.id "
                "WHERE c.archived_at IS NULL AND NOT EXISTS "
                "(SELECT 1 FROM imagination_runs i WHERE i.conversation_id=c.id) "
                "GROUP BY c.id ORDER BY c.updated_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def conversation(self, conversation_id: str) -> dict | None:
        with self.connect() as db:
            conv = db.execute("SELECT * FROM conversations WHERE id=?", (conversation_id,)).fetchone()
            if not conv:
                return None
            messages = db.execute(
                "SELECT m.*, t.status turn_status, t.outcome, t.input_tokens, "
                "t.reasoning_tokens, t.output_tokens, t.total_tokens, t.token_count_source "
                "FROM messages m JOIN turns t ON t.id=m.turn_id "
                "WHERE m.conversation_id=? ORDER BY m.created_at, m.role DESC",
                (conversation_id,),
            ).fetchall()
            active = db.execute(
                "SELECT * FROM turns WHERE conversation_id=? AND status IN ('generating','finalizing')",
                (conversation_id,),
            ).fetchone()
            return {**dict(conv), "messages": [dict(r) for r in messages],
                    "active_turn": dict(active) if active else None}

    def begin_turn(self, conversation_id: str | None, content: str, context: dict) -> dict:
        now = time.time()
        conversation_id = conversation_id or _id("conv")
        turn_id, message_id = _id("turn"), _id("msg")
        title = " ".join(content.strip().split())[:56] or "New conversation"
        with self.transaction(immediate=True) as db:
            existing = db.execute("SELECT id FROM conversations WHERE id=?", (conversation_id,)).fetchone()
            if not existing:
                db.execute("INSERT INTO conversations VALUES (?, ?, ?, ?, NULL)",
                           (conversation_id, title, now, now))
            active = db.execute(
                "SELECT id FROM turns WHERE conversation_id=? AND status IN ('generating','finalizing')",
                (conversation_id,),
            ).fetchone()
            if active:
                raise ConversationBusy(active["id"])
            ordinal = db.execute(
                "SELECT COALESCE(MAX(ordinal),0)+1 n FROM turns WHERE conversation_id=?",
                (conversation_id,),
            ).fetchone()["n"]
            db.execute(
                "INSERT INTO turns (id,conversation_id,ordinal,status,outcome,context_state_sequence,created_at,context_limit) "
                "VALUES (?,?,?,'generating',NULL,?,?,?)",
                (turn_id, conversation_id, ordinal, context["state_sequence"], now, context["context_limit"]),
            )
            db.execute(
                "INSERT INTO messages VALUES (?,?,?,?,?,?,NULL,NULL,'final',?)",
                (message_id, turn_id, conversation_id, "user", content, content, now),
            )
            db.execute(
                "INSERT INTO turn_contexts VALUES (?,?,?,?,?,?,?)",
                (turn_id, context["instructions"], context["knowledge"],
                 json.dumps(context["conversation"]), context["state_sequence"],
                 context["model_id"], now),
            )
            db.execute("INSERT INTO turn_braid_contexts VALUES (?,?,?,?)",
                       (turn_id, json.dumps(context.get("retrieved_memory", [])),
                        json.dumps(context.get("affect", {})), json.dumps(context.get("active_context", {}))))
            db.execute("INSERT INTO turn_system_contexts VALUES (?,?)",
                       (turn_id, json.dumps(context.get("system_projection", {}))))
            db.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conversation_id))
        return {"id": turn_id, "conversation_id": conversation_id, "ordinal": ordinal,
                "status": "generating", "created_at": now, "user_message_id": message_id}

    def mark_finalizing(self, turn_id: str) -> None:
        with self.transaction(immediate=True) as db:
            db.execute("UPDATE turns SET status='finalizing' WHERE id=? AND status='generating'", (turn_id,))

    def fail_turn(self, turn_id: str, code: str, cancelled: bool = False) -> dict:
        now = time.time()
        status = "cancelled" if cancelled else "failed"
        with self.transaction(immediate=True) as db:
            db.execute(
                "UPDATE turns SET status=?, outcome='none', error_code=?, completed_at=? WHERE id=?",
                (status, code, now, turn_id),
            )
            row = db.execute("SELECT * FROM turns WHERE id=?", (turn_id,)).fetchone()
        return dict(row)

    def commit_cycle(self, trace_id: str, new_state: dict, expected_sequence: int, receipt: dict, raw: str,
                     *, user_text: str = "", display: str = "", boundary_hash: str = "") -> dict:
        """One engine turn, atomically: canonical state plus its audit trail (turn, messages, proposal,
        receipt, gate decision, mutation), in the shape Brad's `finalize` writes."""
        now = time.time()
        with self.transaction(immediate=True) as db:
            current_sequence, old_state = self.state(db)
            if current_sequence != expected_sequence:
                raise StateConflict(current_sequence)
            outcome = receipt_outcome(receipt)
            state_changed = new_state != old_state and receipt["decision"] == "ACCEPT"
            next_sequence = current_sequence + 1 if state_changed else current_sequence
            if state_changed:
                db.execute(
                    "UPDATE canonical_state SET sequence=?, world_json=?, self_json=?, updated_at=? WHERE singleton=1",
                    (next_sequence, json.dumps(new_state["world"]), json.dumps(new_state["self"]), now),
                )
            conversation_id = self._session_conversation(db, user_text, now)
            ordinal = db.execute(
                "SELECT COALESCE(MAX(ordinal),0)+1 n FROM turns WHERE conversation_id=?", (conversation_id,)
            ).fetchone()["n"]
            turn_id = _id("turn")
            db.execute(
                "INSERT INTO turns (id,conversation_id,ordinal,status,outcome,context_state_sequence,created_at,completed_at) "
                "VALUES (?,?,?,'complete',?,?,?,?)",
                (turn_id, conversation_id, ordinal, outcome, current_sequence, now, now),
            )
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
            receipt_id = _id("rcpt")
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
                db.execute(
                    "INSERT INTO mutations VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (_id("mut"), turn_id, current_sequence, next_sequence, claim["verb"],
                     claim["what"], json.dumps(claim["args"]), json.dumps(receipt.get("result")),
                     json.dumps({"before": old_state, "after": new_state}), now),
                )
        return {"turn_id": turn_id, "outcome": outcome, "state_sequence": next_sequence,
                "receipt_id": receipt_id, "proposal_id": proposal_id}

    def _session_conversation(self, db: sqlite3.Connection, first_text: str, now: float) -> str:
        """Every turn of one engine session belongs to one conversation, created on its first turn."""
        if getattr(self, "_conversation_id", None) is None:
            self._conversation_id = _id("conv")
            title = " ".join(str(first_text or "").split())[:56] or "BoneAmanita session"
            db.execute("INSERT INTO conversations VALUES (?, ?, ?, ?, NULL)", (self._conversation_id, title, now, now))
        else:
            db.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, self._conversation_id))
        return self._conversation_id

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

    def write_projections(self, sequence: int, state: dict) -> None:
        for name in ("world", "self"):
            target = self.state_dir / f"{name}.json"
            temp = self.state_dir / f".{name}.json.tmp"
            value = dict(state[name])
            value["_state_sequence"] = sequence
            temp.write_text(json.dumps(value, indent=1), encoding="utf-8")
            temp.replace(target)

    def context_messages(self, conversation_id: str, limit: int = 20) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT role, raw_content FROM messages WHERE conversation_id=? AND status='final' "
                "ORDER BY created_at DESC LIMIT ?", (conversation_id, limit),
            ).fetchall()
            return [{"role": r["role"], "content": r["raw_content"]} for r in reversed(rows)]

    def turn(self, turn_id: str) -> dict | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM turns WHERE id=?", (turn_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            msg = db.execute("SELECT * FROM messages WHERE turn_id=? AND role='assistant'", (turn_id,)).fetchone()
            data["assistant_message"] = dict(msg) if msg else None
            rec = db.execute("SELECT * FROM receipts WHERE turn_id=?", (turn_id,)).fetchone()
            data["receipt"] = dict(rec) if rec else None
            return data

    def turn_context(self, turn_id: str) -> dict | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM turn_contexts WHERE turn_id=?", (turn_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            data["conversation"] = json.loads(data.pop("conversation_json"))
            braid = db.execute("SELECT * FROM turn_braid_contexts WHERE turn_id=?", (turn_id,)).fetchone()
            if braid:
                data["retrieved_memory"] = json.loads(braid["retrieved_memory_json"])
                data["affect"] = json.loads(braid["affect_json"])
                data["active_context"] = json.loads(braid["active_context_json"])
            system = db.execute("SELECT projection_json FROM turn_system_contexts WHERE turn_id=?", (turn_id,)).fetchone()
            data["system_projection"] = json.loads(system["projection_json"]) if system else {}
            return data

    def governance(self, table: str) -> list[dict]:
        if table not in {"proposals", "gate_decisions", "receipts"}:
            raise ValueError(table)
        with self.connect() as db:
            rows = db.execute(
                f"SELECT x.*, t.conversation_id, t.ordinal FROM {table} x "
                "JOIN turns t ON t.id=x.turn_id ORDER BY x.created_at DESC LIMIT 200"
            ).fetchall()
            return [dict(r) for r in rows]

    def node_provenance(self, node_name: str) -> dict | None:
        """Return the earliest committed mutation that explicitly created a node."""
        with self.connect() as db:
            rows = db.execute(
                "SELECT m.*, t.conversation_id, t.ordinal, r.id receipt_id "
                "FROM mutations m JOIN turns t ON t.id=m.turn_id "
                "LEFT JOIN receipts r ON r.turn_id=m.turn_id ORDER BY m.state_sequence_after"
            ).fetchall()
            for row in rows:
                args = json.loads(row["args_json"])
                if (row["verb"] == "create" and args.get("name") == node_name) or (
                    row["verb"] == "occur" and args.get("event") == node_name
                ):
                    return dict(row)
        return None

    def active_context(self) -> dict:
        with self.connect() as db:
            row = db.execute("SELECT * FROM active_context WHERE singleton=1").fetchone()
        return {"global": True, "world": row["world_scope"], "task": row["task_scope"],
                "skills": json.loads(row["skill_scopes_json"])}

    def set_active_context(self, world: str | None, task: str | None, skills: list[str]) -> dict:
        clean = sorted({s for s in skills if s.startswith("skill:")})
        with self.transaction(immediate=True) as db:
            db.execute("UPDATE active_context SET world_scope=?,task_scope=?,skill_scopes_json=?,updated_at=? WHERE singleton=1",
                       (world, task, json.dumps(clean), time.time()))
            self._bump_domain(db, "context")
        return self.active_context()

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

    def memory_entries(self, channels: list[str] | None = None) -> list[dict]:
        context = self.active_context()
        scopes = ["global"] + context["skills"] + [s for s in (context["world"], context["task"]) if s]
        marks = ",".join("?" for _ in scopes)
        params: list[Any] = scopes
        where = f"(scope_type='global' OR (scope_type || ':' || scope_id) IN ({marks})) AND visibility='standard'"
        if channels:
            where += " AND channel IN (" + ",".join("?" for _ in channels) + ")"
            params.extend(channels)
        with self.connect() as db:
            rows = db.execute(f"SELECT * FROM memory_entries WHERE {where} ORDER BY created_at DESC LIMIT 300", params).fetchall()
        return [self._decode_memory_row(row) for row in rows]

    @staticmethod
    def _decode_memory_row(row: sqlite3.Row) -> dict:
        item = dict(row)
        item["scope"] = "global" if item["scope_type"] == "global" else f"{item['scope_type']}:{item['scope_id']}"
        item["derived_from"] = json.loads(item.pop("derived_from_json"))
        for key in ("affect_before", "affect_after", "affect_delta"):
            raw = item.pop(f"{key}_json")
            item[key] = json.loads(raw) if raw else None
        return item

    def add_memory_entry(self, *, scope: str, channel: str, content: str, origin: str = "experience",
                         source_event_id: str | None = None, derived_from: list[str] | None = None,
                         affect_before: dict | None = None, affect_after: dict | None = None,
                         affect_delta: dict | None = None) -> dict:
        scope_type, _, scope_id = scope.partition(":")
        if scope_type not in {"global","skill","world","task"} or (scope_type != "global" and not scope_id):
            raise ValueError("invalid memory scope")
        if channel not in {"experience","cognitive_semantic","emotional_semantic"}:
            raise ValueError("invalid memory channel")
        entry_id, now = _id("mem"), time.time()
        with self.transaction(immediate=True) as db:
            db.execute("INSERT INTO memory_entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (entry_id, scope_type, scope_id or None, channel, content, origin, source_event_id,
                        json.dumps(derived_from or []), json.dumps(affect_before) if affect_before else None,
                        json.dumps(affect_after) if affect_after else None, json.dumps(affect_delta) if affect_delta else None,
                        "standard", now))
            self._bump_domain(db, "memory")
        with self.connect() as db:
            row = db.execute("SELECT * FROM memory_entries WHERE id=?", (entry_id,)).fetchone()
        return self._decode_memory_row(row)

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

    def capabilities(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM capabilities ORDER BY source,id").fetchall()
        result = []
        for row in rows:
            item = dict(row)
            for key in ("schema", "scope", "limits"):
                item[key] = json.loads(item.pop(f"{key}_json"))
            item["available"] = bool(item["available"])
            result.append(item)
        return result

    def capability(self, tool_id: str) -> dict | None:
        return next((item for item in self.capabilities() if item["id"] == tool_id), None)

    def register_mcp_capability(self, tool_id: str, server: str, description: str,
                                schema: dict, effect_class: str) -> dict:
        if not tool_id.strip() or not server.strip():
            raise ValueError("MCP tool and server are required")
        if effect_class not in {"observe","modify","communicate","execute"}:
            raise ValueError("invalid effect class")
        capability_id = f"mcp.{server.strip()}.{tool_id.strip()}"
        now = time.time()
        with self.transaction(immediate=True) as db:
            db.execute("INSERT INTO capabilities VALUES (?,?,?,?,?,'{}','{}',0,'capability-v1',?) "
                       "ON CONFLICT(id) DO UPDATE SET description=excluded.description,schema_json=excluded.schema_json,effect_class=excluded.effect_class",
                       (capability_id, f"mcp:{server.strip()}", effect_class, description.strip(), json.dumps(schema), now))
            self._bump_domain(db, "capabilities")
        return self.capability(capability_id)

    def tool_receipts(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM tool_receipts ORDER BY created_at DESC LIMIT 200").fetchall()
        result = []
        for row in rows:
            item = dict(row)
            for key in ("raw_args", "normalized_args", "context", "checks", "result"):
                raw = item.pop(f"{key}_json")
                item[key] = json.loads(raw) if raw else None
            result.append(item)
        return result

    def record_tool_receipt(self, *, tool_id: str, source: str, effect_class: str,
                            raw_args: dict, normalized_args: dict | None, context: dict,
                            decision: str, checks: list, execution_status: str,
                            result: Any = None, error: str | None = None) -> dict:
        receipt_id, now = _id("tool"), time.time()
        version = self.versions().get("capabilities", 0)
        with self.transaction(immediate=True) as db:
            db.execute("INSERT INTO tool_receipts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (receipt_id, tool_id, source, effect_class, json.dumps(raw_args),
                        json.dumps(normalized_args) if normalized_args is not None else None,
                        json.dumps(context), version, decision, json.dumps(checks), execution_status,
                        json.dumps(result) if result is not None else None, error, now, now))
            row = db.execute("SELECT * FROM tool_receipts WHERE id=?", (receipt_id,)).fetchone()
        item = dict(row)
        return item


class ConversationBusy(Exception):
    def __init__(self, turn_id: str):
        self.turn_id = turn_id


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
