import networkx as nx
from typing import Dict, Any, List

class BlastRadiusGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_evidence_node(self, node_id: str, entity_type: str, **kwargs):
        self.graph.add_node(node_id, type=entity_type, **kwargs)

    def link_evidence(self, source: str, target: str, relation: str):
        self.graph.add_edge(source, target, relation=relation)

    def calculate_center_of_gravity(self) -> List[Dict[str, Any]]:
        """
        Uses PageRank to determine the most highly connected and influential 
        node in the attack graph (the Center of Gravity).
        """
        if len(self.graph) == 0:
            return []
        
        # Calculate PageRank algorithm
        pagerank_scores = nx.pagerank(self.graph)
        
        # Sort nodes by score descending
        ranked_nodes = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for node_id, score in ranked_nodes:
            node_data = self.graph.nodes[node_id]
            results.append({
                "node_id": node_id,
                "type": node_data.get("type", "unknown"),
                "influence_score": round(score, 4)
            })
        return results