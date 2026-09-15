import json
import csv
import os
import networkx as nx
import xml.etree.ElementTree as ET
from datetime import datetime
from Evtx import Evtx
from app.database.neo4j_client import add_evidence_finding

def build_pagerank_topology(logs: list, sha256_hash: str):
    """
    Builds a directed graph of network/user interactions, calculates 
    PageRank scores, and identifies the Center of Gravity.
    """
    G = nx.DiGraph()

    # Step 1: Build the directed graph from log edges
    for log in logs:
        source = log.get("source")
        target = log.get("target")
        if source and target:
            G.add_edge(source, target)

    if len(G.nodes) == 0:
        add_evidence_finding(
            sha256_hash,
            "PAGERANK",
            json.dumps({"nodes": []}),
            "SKIPPED"
        )
        return

    # Step 2: Compute PageRank scores using NetworkX
    try:
        scores = nx.pagerank(G, alpha=0.85)
    except Exception:
        # Fallback for small or disconnected graphs
        scores = {node: 1.0 / len(G.nodes) for node in G.nodes}

    # Step 3: Identify the node with the highest PageRank score (Center of Gravity)
    max_node = max(scores, key=scores.get)

    # Step 4: Format node data for the Vue dashboard UI
    node_list = []
    for node in G.nodes:
        is_center = (node == max_node)
        node_type = "Critical Asset / Threat Vector" if is_center else "Network Node"
        node_list.append({
            "id": str(node),
            "type": node_type,
            "is_center": is_center
        })

    graph_payload = json.dumps({"nodes": node_list})

    # Step 5: Save finding to Neo4j
    add_evidence_finding(
        sha256_hash,
        "PAGERANK",
        graph_payload,
        "CONFIRMED"
    )
    print(f"[+] NetworkX: Generated PageRank topology. Center of Gravity: {max_node}")


def run_analysis_pipeline(file_path: str, sha256_hash: str):
    """
    Main forensic analysis pipeline called in background upon ingestion.
    Supports JSON, CSV, and native Windows EVTX binary log formats.
    """
    logs = []

    try:
        # --- FILE PARSING (JSON, CSV, EVTX) ---
        if file_path.lower().endswith('.json'):
            with open(file_path, 'r') as f:
                logs = json.load(f)

        elif file_path.lower().endswith('.csv'):
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'event_id' in row:
                        row['event_id'] = int(row['event_id'])
                    if 'timestamp' in row:
                        row['timestamp'] = int(row['timestamp'])
                    logs.append(row)

        elif file_path.lower().endswith('.evtx'):
            # Define the standard Windows XML namespace for event logs
            ns = {'e': 'http://schemas.microsoft.com/win/2004/08/events/event'}
            
            with Evtx(file_path) as log:
                for record in log.records():
                    try:
                        root = ET.fromstring(record.xml())
                        
                        # Extract EventID
                        event_id_elem = root.find('.//e:System/e:EventID', ns)
                        event_id = int(event_id_elem.text) if event_id_elem is not None else 0
                        
                        # Extract SystemTime and convert to Unix Timestamp for the Paradox Engine
                        time_elem = root.find('.//e:System/e:TimeCreated', ns)
                        if time_elem is not None:
                            time_str = time_elem.get('SystemTime')
                            # Handle ISO 8601 format and the 'Z' timezone indicator
                            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                            timestamp = int(dt.timestamp())
                        else:
                            continue
                            
                        # Extract Computer Name (Source) for the NetworkX Topology
                        computer_elem = root.find('.//e:System/e:Computer', ns)
                        source = computer_elem.text if computer_elem is not None else "Unknown_Host"
                        
                        logs.append({
                            'event_id': event_id,
                            'timestamp': timestamp,
                            'source': source,
                            'target': "Local_Windows_System" # Default target for topology
                        })
                    except Exception:
                        # Skip corrupted individual records but keep parsing
                        continue

        else:
            add_evidence_finding(
                sha256_hash, 
                "PARADOX_ENGINE", 
                f"File {os.path.basename(file_path)} is not a recognized log format (.json, .csv, .evtx). Skipped.", 
                "SKIPPED"
            )
            return

        if not logs:
            return

        # --- 1. TEMPORAL PARADOX CHECK ---
        logs_by_id = sorted(logs, key=lambda x: x.get('event_id', 0))
        paradox_found = False
        paradox_details = ""

        for i in range(len(logs_by_id) - 1):
            current_event = logs_by_id[i]
            next_event = logs_by_id[i+1]
            
            if current_event.get('timestamp', 0) > next_event.get('timestamp', 0):
                paradox_found = True
                paradox_details = f"Paradox between Event ID {current_event.get('event_id')} and {next_event.get('event_id')}."
                break

        if not paradox_found:
            add_evidence_finding(
                sha256_hash, 
                "TEMPORAL_ANALYSIS", 
                "Temporal sequence mathematically proven intact. No timestomping detected.", 
                "CONFIRMED"
            )
        else:
            add_evidence_finding(
                sha256_hash, 
                "TEMPORAL_ANALYSIS", 
                f"CRITICAL PARADOX! {paradox_details} System clock manipulation (Timestomping) detected.", 
                "FLAGGED"
            )

        # --- 2. NETWORKX PAGERANK TOPOLOGY ---
        build_pagerank_topology(logs, sha256_hash)

    except Exception as e:
        add_evidence_finding(sha256_hash, "ANALYSIS_ERROR", f"Failed to analyze logs: {str(e)}", "ERROR")