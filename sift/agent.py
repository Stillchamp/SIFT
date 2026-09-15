from typing import Dict, List, Any

class SelfCorrectingInvestigator:
    def __init__(self):
        self.claims: Dict[str, Dict[str, Any]] = {}
        
    def add_claim(self, claim_id: str, statement: str, sources: List[str]):
        # The agent optimistically assumes it's right, but the verification gate will test it
        self.claims[claim_id] = {
            "statement": statement,
            "sources": sources,
            "status": "CONFIRMED" 
        }

    def _verify_claims(self) -> int:
        """
        The core neuro-symbolic rule: No claim can remain CONFIRMED 
        unless backed by at least 2 independent artifact types.
        """
        corrections = 0
        for claim_id, data in self.claims.items():
            if data["status"] == "CONFIRMED" and len(data["sources"]) < 2:
                # Auto-downgrade hallucination or weak claim
                self.claims[claim_id]["status"] = "INFERRED"
                self.claims[claim_id]["correction_reason"] = "Downgraded: Requires >= 2 independent sources."
                corrections += 1
        return corrections
        
    def _negative_controls(self, claim_id: str, target: str):
        """Ensures benign system processes are never falsely escalated."""
        whitelist = ["svchost.exe", "lsass.exe", "explorer.exe"]
        if target in whitelist and claim_id in self.claims:
            self.claims[claim_id]["status"] = "INFO (BENIGN)"
            self.claims[claim_id]["correction_reason"] = f"Negative Control: {target} is a protected system process."

    def run_triage_loop(self):
        print("[*] Iteration 1: Volatile Triage (Memory & Network)...")
        # Agent flags an IP based on just ONE network log
        self.add_claim("clm-001", "unknown.exe communicating with 198.51.100.24", ["network_log"])
        
        print("[*] Iteration 2: Disk Corroboration...")
        # Agent finds persistence backed by TWO logs
        self.add_claim("clm-002", "evil.exe established registry persistence", ["registry_autoruns", "mft"])
        
        print("[*] Iteration 3: Negative Controls & Verification...")
        # Agent hallucinates/flags a safe Windows process
        self.add_claim("clm-003", "svchost.exe exhibits suspicious memory mapping", ["memory_malfind"])
        self._negative_controls("clm-003", "svchost.exe")
        
        # The final deterministic gate
        corrections = self._verify_claims()
        print(f"[*] Verification Gate Closed: Agent self-corrected {corrections} weak claim(s) based on deterministic rules.")
        
        return self.claims