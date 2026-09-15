from sift.knowledge_graph import BlastRadiusGraph

print("[*] Initializing NetworkX Blast Radius Graph...")
kg = BlastRadiusGraph()

# 1. Add Entities (IPs, Processes, Registry Keys)
kg.add_evidence_node("203.0.113.50", "ip_address", is_ioc=True)
kg.add_evidence_node("evil.exe", "process")
kg.add_evidence_node("svchost.exe", "process")
kg.add_evidence_node("HKCU\\Run\\Updater", "registry_key")
kg.add_evidence_node("cmd.exe", "process")

# 2. Map the Attack Topology (Directed Edges)
# The attacker connects from the IP, to evil.exe, and spreads out.
kg.link_evidence("203.0.113.50", "evil.exe", "C2_BEACON")
kg.link_evidence("evil.exe", "HKCU\\Run\\Updater", "PERSISTENCE")
kg.link_evidence("evil.exe", "svchost.exe", "PROCESS_INJECTION")
kg.link_evidence("evil.exe", "cmd.exe", "EXECUTION")

# 3. Calculate Blast Radius / Center of Gravity
ranked_targets = kg.calculate_center_of_gravity()

print("\n--- NetworkX PageRank: Attack Center of Gravity ---")
for rank, node in enumerate(ranked_targets, 1):
    print(f"{rank}. {node['node_id']} (Type: {node['type']}) - Influence Score: {node['influence_score']}")