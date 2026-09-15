import os
from pathlib import Path
import time

# Import our 5 phases
from sift.security import SafePathPolicy, spoliation_probe
from sift.integrity import MerkleDAG, hash_file
from sift.anti_forensics import AntiForensicsEngine
from sift.knowledge_graph import BlastRadiusGraph
from sift.clock_drift import ClockDriftNormalizer
from sift.agent import SelfCorrectingInvestigator

print("\n" + "="*50)
print(" SIFT: TRUSTWORTHY DIGITAL FORENSICS")
print("="*50)

# Setup directories
base_dir = Path(__file__).parent
evidence_dir = base_dir / "evidence"
output_dir = base_dir / "outputs"

print("\n[PHASE 1] INITIALIZING CHAIN OF CUSTODY...")
time.sleep(1)
policy = SafePathPolicy(evidence_root=evidence_dir, output_root=output_dir)
if spoliation_probe(evidence_dir, policy):
    print("  ✅ OS-Level Spoliation Probe: PASSED (Evidence is read-only)")

dag = MerkleDAG()
log_hash = hash_file(str(evidence_dir / "mft.csv"))
node_hash = dag.append_node("EVIDENCE_INGEST", {"file": "mft.csv", "sha256": log_hash})
print(f"  🔒 Cryptographic Merkle Root Seal: {dag.get_root_hash()}")

print("\n[PHASE 2] ANTI-FORENSICS Z3 SMT ANALYSIS...")
time.sleep(1)
# Simulating Prefetch vs MFT timestomping values
prefetch_epoch, mft_epoch = 1788098533, 1788099005 
z3_result = AntiForensicsEngine.detect_timestomping(prefetch_epoch, mft_epoch)
if z3_result['detected']:
    print(f"  🚨 Z3 UNSATISFIABLE_CAUSALITY_VIOLATION")
    print(f"     Proof: {z3_result['rationale']}")

print("\n[PHASE 3] NETWORKX BLAST RADIUS & PAGE-RANK...")
time.sleep(1)
kg = BlastRadiusGraph()
kg.add_evidence_node("203.0.113.50", "ip_address")
kg.add_evidence_node("evil.exe", "process")
kg.link_evidence("203.0.113.50", "evil.exe", "C2_BEACON")
targets = kg.calculate_center_of_gravity()
print(f"  🎯 Center of Gravity: {targets[0]['node_id']} (Score: {targets[0]['influence_score']})")

print("\n[PHASE 4] CLOCK DRIFT NORMALIZATION...")
time.sleep(1)
norm = ClockDriftNormalizer()
norm.add_observation("network", "203.0.113.50", 1788098000)
norm.add_observation("evtx", "203.0.113.50", 1788097880)
drift = norm.detect_and_calculate_drift("network", "evtx")
print(f"  ⏱️ Time Skew Detected. Auto-aligning EVTX logs by +{drift['delta_seconds']}s")

print("\n[PHASE 5] NEURO-SYMBOLIC AGENT TRIAGE...")
time.sleep(1)
agent = SelfCorrectingInvestigator()
agent.add_claim("clm-001", "unknown.exe communicating with 198.51.100.24", ["network_log"])
agent.add_claim("clm-002", "evil.exe established registry persistence", ["registry", "mft"])
agent.add_claim("clm-003", "svchost.exe exhibits suspicious memory", ["memory_malfind"])
agent._negative_controls("clm-003", "svchost.exe")
agent._verify_claims()

print("\n--- FINAL COURT-READY FINDINGS ---")
for cid, data in agent.claims.items():
    status = f"✅ {data['status']}" if data['status'] == "CONFIRMED" else f"⚠️ {data['status']}"
    print(f"  {status}: {data['statement']}")
    if "correction_reason" in data:
        print(f"     -> {data['correction_reason']}")
print("="*50 + "\n")