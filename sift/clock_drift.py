from typing import Dict, Optional

class ClockDriftNormalizer:
    def __init__(self):
        # Stores observations as {source: {anchor_value: timestamp_epoch}}
        self.observations: Dict[str, Dict[str, int]] = {}

    def add_observation(self, source: str, anchor_value: str, timestamp_epoch: int):
        """Records an entity (like an IP) seen at a specific time in a specific log source."""
        if source not in self.observations:
            self.observations[source] = {}
        self.observations[source][anchor_value] = timestamp_epoch

    def detect_and_calculate_drift(self, reference_source: str, target_source: str) -> Optional[Dict[str, int]]:
        """
        Finds shared anchors between two sources and calculates the time drift delta.
        """
        if reference_source not in self.observations or target_source not in self.observations:
            return None

        ref_obs = self.observations[reference_source]
        target_obs = self.observations[target_source]

        # Find entities (like IPs) that exist in both log files
        shared_anchors = set(ref_obs.keys()).intersection(set(target_obs.keys()))
        
        if not shared_anchors:
            return None
        
        # Use the shared anchor to calculate the time discrepancy
        anchor = list(shared_anchors)[0]
        ref_time = ref_obs[anchor]
        target_time = target_obs[anchor]
        
        delta_seconds = ref_time - target_time
        
        return {
            "anchor_matched": anchor,
            "reference_time": ref_time,
            "target_time": target_time,
            "delta_seconds": delta_seconds
        }