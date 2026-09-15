import sqlite3
import json
from pathlib import Path
from typing import Dict, Any

class EvidenceGraph:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tool Runs
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_runs (
                command_id TEXT PRIMARY KEY,
                tool_name TEXT NOT NULL,
                ok INTEGER NOT NULL,
                summary TEXT,
                duration_ms INTEGER
            );
            """)

            # Parsed Artifacts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                source TEXT NOT NULL,
                command_id TEXT,
                fields_json TEXT NOT NULL,
                FOREIGN KEY(command_id) REFERENCES tool_runs(command_id)
            );
            """)

            # Forensic Claims
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                claim_id TEXT PRIMARY KEY,
                statement TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL NOT NULL,
                severity TEXT NOT NULL,
                rationale TEXT
            );
            """)

            # Claim-to-Artifact Provenance Join Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS claim_evidence (
                claim_id TEXT NOT NULL,
                artifact_id TEXT NOT NULL,
                PRIMARY KEY (claim_id, artifact_id),
                FOREIGN KEY(claim_id) REFERENCES claims(claim_id),
                FOREIGN KEY(artifact_id) REFERENCES artifacts(artifact_id)
            );
            """)

            # Cryptographic Merkle-DAG Nodes & Root
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS merkle_nodes (
                node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_hash TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                node_type TEXT NOT NULL,
                created_utc DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS merkle_root (
                root_hash TEXT PRIMARY KEY,
                sealed_utc DATETIME DEFAULT CURRENT_TIMESTAMP,
                node_count INTEGER NOT NULL
            );
            """)
            conn.commit()

    def record_artifact(self, artifact_id: str, kind: str, source: str, fields: Dict[str, Any], command_id: str = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO artifacts (artifact_id, kind, source, command_id, fields_json) VALUES (?, ?, ?, ?, ?)",
                (artifact_id, kind, source, command_id, json.dumps(fields))
            )
            conn.commit()

    def record_merkle_node(self, parent_hash: str, content_hash: str, node_type: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO merkle_nodes (parent_hash, content_hash, node_type) VALUES (?, ?, ?)",
                (parent_hash, content_hash, node_type)
            )
            conn.commit()

    def seal_graph(self, final_root_hash: str, node_count: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO merkle_root (root_hash, node_count) VALUES (?, ?)",
                (final_root_hash, node_count)
            )
            conn.commit()