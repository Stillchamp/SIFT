from pathlib import Path
from sift.security import SafePathPolicy
from sift.tools import ToolRunner
from sift.anti_forensics import AntiForensicsEngine

base_dir = Path(__file__).parent
evidence_dir = base_dir / "evidence"
output_dir = base_dir / "outputs"

policy = SafePathPolicy(evidence_root=evidence_dir, output_root=output_dir)
runner = ToolRunner(policy)

# 1. Parse typed evidence artifacts
prefetch_data = runner.disk_prefetch(evidence_dir)
mft_data = runner.timeline_mft(evidence_dir)

print(f"[+] Prefetch Artifacts Ingested: {len(prefetch_data)}")
print(f"[+] MFT Artifacts Ingested: {len(mft_data)}")

# 2. Extract timestamps for 'evil.exe'
prefetch_epoch = int(prefetch_data[0]['epoch_timestamp'])
mft_epoch = int(mft_data[0]['epoch_timestamp'])

# 3. Run Z3 Formal Mathematical Contradiction Solver
z3_result = AntiForensicsEngine.detect_timestomping(prefetch_epoch, mft_epoch)

print("\n--- Z3 SMT Anti-Forensics Analysis ---")
print(f"[*] Timestomping Detected: {z3_result['detected']}")
print(f"[*] Mathematical Proof:   {z3_result['proof']}")
print(f"[*] Time Contradiction:   {z3_result['delta_seconds']} seconds")
print(f"[*] Rationale:            {z3_result['rationale']}")