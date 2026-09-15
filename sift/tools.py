import csv
from pathlib import Path
from typing import List, Dict, Any
from sift.security import SafePathPolicy

class ToolRunner:
    def __init__(self, policy: SafePathPolicy):
        self.policy = policy

    def parse_csv_artifact(self, file_path: Path) -> List[Dict[str, Any]]:
        validated_path = self.policy.validate_read(file_path)
        records = []
        if not validated_path.exists():
            return records
            
        with open(validated_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
        return records

    def disk_prefetch(self, evidence_dir: Path) -> List[Dict[str, Any]]:
        return self.parse_csv_artifact(evidence_dir / "prefetch.csv")

    def timeline_mft(self, evidence_dir: Path) -> List[Dict[str, Any]]:
        return self.parse_csv_artifact(evidence_dir / "mft.csv")