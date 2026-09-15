from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel

# Import SIFT modules
from sift.security import SafePathPolicy, spoliation_probe
from sift.integrity import MerkleDAG, hash_file
from sift.anti_forensics import AntiForensicsEngine
from sift.knowledge_graph import BlastRadiusGraph
from sift.clock_drift import ClockDriftNormalizer
from sift.agent import SelfCorrectingInvestigator

app = FastAPI(title="SIFT Live Simulation API")

# Allow the Vue frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths and state storage
base_dir = Path(__file__).parent
evidence_dir = base_dir / "evidence"
output_dir = base_dir / "outputs"
mft_path = evidence_dir / "mft.csv"

# In-memory ledger tracking state
secure_ledger = {
    "is_sealed": False,
    "baseline_root_hash": None
}

class EvidenceData(BaseModel):
    content: str

@app.get("/api/evidence")
def get_evidence():
    """Reads raw CSV text for the frontend editor."""
    if not mft_path.exists():
        return {"content": ""}
    return {"content": mft_path.read_text()}

@app.post("/api/evidence")
def update_evidence(data: EvidenceData):
    """Saves edited CSV text from the frontend directly back to disk."""
    mft_path.write_text(data.content)
    return {"status": "Evidence updated on disk"}

@app.post("/api/seal")
def seal_evidence():
    """Hashes the current file state and locks in the baseline Merkle root."""
    if not mft_path.exists():
        raise HTTPException(status_code=404, detail="Evidence file missing.")
    
    # ADD THESE TWO LINES:
    if secure_ledger["is_sealed"]:
        raise HTTPException(status_code=403, detail="ERROR: Evidence is already sealed. The ledger is immutable.")
    
    dag = MerkleDAG()
    current_hash = hash_file(str(mft_path))
    dag.append_node("EVIDENCE_INGEST", {"file": "mft.csv", "sha256": current_hash})
    
    secure_ledger["baseline_root_hash"] = dag.get_root_hash()
    secure_ledger["is_sealed"] = True
    
    return {
        "status": "Sealed", 
        "baseline_hash": secure_ledger["baseline_root_hash"]
    }

@app.get("/api/triage")
def run_triage():
    if not secure_ledger["is_sealed"]:
        raise HTTPException(status_code=400, detail="Evidence must be sealed first.")

    dag = MerkleDAG()
    live_hash = hash_file(str(mft_path))
    dag.append_node("EVIDENCE_INGEST", {"file": "mft.csv", "sha256": live_hash})
    live_root_hash = dag.get_root_hash()

    is_tampered = live_root_hash != secure_ledger["baseline_root_hash"]

    agent = SelfCorrectingInvestigator()
    
    # Initialize Graph Output Data
    graph_data = {"center": None, "nodes": [], "links": []}

    if is_tampered:
        agent.add_claim("clm-999", "EVIDENCE TAMPERING DETECTED", ["ledger"])
        agent.claims["clm-999"]["status"] = "COMPROMISED"
        agent.claims["clm-999"]["correction_reason"] = f"Expected hash {secure_ledger['baseline_root_hash'][:12]}... but found {live_root_hash[:12]}..."
    else:
        agent.add_claim("clm-001", "unknown.exe communicating with 198.51.100.24", ["network_log"])
        agent.add_claim("clm-002", "evil.exe established registry persistence", ["registry", "mft"])
        agent.add_claim("clm-003", "svchost.exe exhibits suspicious memory", ["memory_malfind"])
        agent._negative_controls("clm-003", "svchost.exe")
        agent._verify_claims()

        # Execute Phase 3: Blast Radius Graph
        kg = BlastRadiusGraph()
        kg.add_evidence_node("198.51.100.24", "ip_address")
        kg.add_evidence_node("evil.exe", "process")
        kg.add_evidence_node("HKCU\\Run\\Updater", "registry")
        
        kg.link_evidence("198.51.100.24", "evil.exe", "C2_BEACON")
        kg.link_evidence("evil.exe", "HKCU\\Run\\Updater", "PERSISTENCE")
        
        targets = kg.calculate_center_of_gravity()
        
        # Format graph for the Vue frontend
        graph_data["center"] = targets[0]["node_id"] if targets else None
        graph_data["nodes"] = [
            {"id": "198.51.100.24", "type": "Network"},
            {"id": "evil.exe", "type": "Process"},
            {"id": "HKCU\\Run\\Updater", "type": "Registry"}
        ]

    return {
        "is_tampered": is_tampered,
        "chain_of_custody": {
            "live_root_hash": live_root_hash,
            "baseline_hash": secure_ledger["baseline_root_hash"]
        },
        "graph": graph_data,
        "findings": [
            {
                "id": cid,
                "status": data["status"],
                "statement": data["statement"],
                "correction": data.get("correction_reason", None)
            }
            for cid, data in agent.claims.items()
        ]
    }

@app.post("/api/reset")
def reset_demo():
    """Clears the ledger memory and restores the original CSV file."""
    secure_ledger["is_sealed"] = False
    secure_ledger["baseline_root_hash"] = None
    
    # The pristine synthetic data we use for the demo
    original_csv = (
        "timestamp,source,event_id,entity,details\n"
        "1788097880,windows_evtx,4624,203.0.113.50,Network logon\n"
        "1788098000,network_log,conn,203.0.113.50,C2_BEACON\n"
        "1788098533,prefetch,exec,evil.exe,Executed from temp\n"
        "1788099005,mft,create,evil.exe,File creation on disk\n"
        "1788099100,registry,add,evil.exe,Persistence established\n"
        "1788099200,network_log,conn,198.51.100.24,unknown.exe communicating\n"
        "1788099300,memory_malfind,inject,svchost.exe,Suspicious memory mapping\n"
    )
    
    # Make sure the directory exists just in case
    mft_path.parent.mkdir(parents=True, exist_ok=True)
    mft_path.write_text(original_csv)
    
    return {"status": "Demo reset successfully"}