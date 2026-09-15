from pathlib import Path
import os
from sift.security import SafePathPolicy, spoliation_probe
from sift.integrity import MerkleDAG, hash_file
from sift.graph import EvidenceGraph

# Setup directories
base_dir = Path(__file__).parent
evidence_dir = base_dir / "evidence"
output_dir = base_dir / "outputs"

evidence_dir.mkdir(exist_ok=True)
output_dir.mkdir(exist_ok=True)

# 1. Initialize Security Policy
policy = SafePathPolicy(evidence_root=evidence_dir, output_root=output_dir)
is_secure = spoliation_probe(evidence_dir, policy)
print(f"[+] OS Read-Only Spoliation Probe: {'PASSED' if is_secure else 'FAILED'}")

# 2. Initialize Ledger & Graph DB
db_path = output_dir / "evidence_graph.sqlite"
graph = EvidenceGraph(db_path)
dag = MerkleDAG()

# 3. Simulate Ingesting Evidence
sample_log = evidence_dir / "sample_evtx.csv"
sample_log.write_text("timestamp,event_id,user\n2026-08-30T10:00:00Z,4688,SYSTEM")

log_hash = hash_file(str(sample_log))
node_hash = dag.append_node("EVIDENCE_INGEST", {"file": "sample_evtx.csv", "sha256": log_hash})
graph.record_merkle_node("0" * 64, node_hash, "EVIDENCE_INGEST")

# 4. Seal Ledger
root_hash = dag.get_root_hash()
graph.seal_graph(root_hash, len(dag.nodes))

print(f"[+] Evidence Ingest Hash: {log_hash}")
print(f"[+] Cryptographic Merkle Root Seal: {root_hash}")
print("[+] Phase 1 Ledger & Security Engine Initialized Successfully.")