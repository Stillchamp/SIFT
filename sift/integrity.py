import hashlib
from typing import List, Dict, Any

def hash_file(file_path: str) -> str:
    """Computes SHA-256 hash of a target file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            sha256.update(block)
    return sha256.hexdigest()

def compute_node_hash(node_type: str, payload: Dict[str, Any], parent_hash: str = "") -> str:
    """Generates a cryptographic hash combining node content and parent node hash."""
    hasher = hashlib.sha256()
    raw_content = f"{node_type}:{sorted(payload.items())}:{parent_hash}"
    hasher.update(raw_content.encode("utf-8"))
    return hasher.hexdigest()

class MerkleDAG:
    def __init__(self):
        self.nodes: List[Dict[str, Any]] = []
        self.current_root: str = "0" * 64  # Initial Genesis Hash

    def append_node(self, node_type: str, payload: Dict[str, Any]) -> str:
        node_hash = compute_node_hash(node_type, payload, self.current_root)
        node_record = {
            "node_id": len(self.nodes) + 1,
            "parent_hash": self.current_root,
            "content_hash": node_hash,
            "node_type": node_type,
            "payload": payload
        }
        self.nodes.append(node_record)
        self.current_root = node_hash
        return node_hash

    def get_root_hash(self) -> str:
        return self.current_root