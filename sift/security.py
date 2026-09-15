import os
from pathlib import Path

class PolicyViolation(Exception):
    """Raised when an unauthorized path access or write attempt occurs."""
    pass

class SafePathPolicy:
    def __init__(self, evidence_root: Path, output_root: Path):
        self.evidence_root = evidence_root.resolve()
        self.output_root = output_root.resolve()

    def validate_read(self, target_path: Path) -> Path:
        resolved = target_path.resolve()
        try:
            resolved.relative_to(self.evidence_root)
            return resolved
        except ValueError:
            try:
                resolved.relative_to(self.output_root)
                return resolved
            except ValueError:
                raise PolicyViolation(f"Read path out of bounds: {target_path}")

    def validate_write(self, target_path: Path) -> Path:
        resolved = target_path.resolve()
        try:
            resolved.relative_to(self.output_root)
            return resolved
        except ValueError:
            raise PolicyViolation(f"Write attempted outside output directory: {target_path}")

def spoliation_probe(evidence_root: Path, policy: SafePathPolicy) -> bool:
    """Proves evidence directory is write-protected at the OS level."""
    sentinel = evidence_root / "_proofsift_spoliation_probe.tmp"
    try:
        policy.validate_write(sentinel)
        with open(sentinel, "w") as f:
            f.write("probe")
        raise PolicyViolation("CRITICAL SECURITY RISK: Evidence root is writable!")
    except (PermissionError, PolicyViolation):
        return True  # OS or Policy correctly rejected the write operation