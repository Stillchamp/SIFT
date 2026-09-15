from neo4j import GraphDatabase
import os

# Default credentials for a local Neo4j instance
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
except Exception as e:
    print(f"[!] Failed to initialize Neo4j driver: {e}")
    driver = None

def create_evidence_root_node(filename: str, sha256_hash: str):
    """Creates the initial, immutable root provenance node in Neo4j."""
    if not driver:
        return

    query = """
    MERGE (e:Evidence {sha256: $sha256_hash})
    ON CREATE SET 
        e.filename = $filename, 
        e.ingested_at = timestamp(),
        e.status = "Sealed"
    RETURN e
    """
    try:
        with driver.session() as session:
            session.run(query, filename=filename, sha256_hash=sha256_hash)
            print(f"[+] Neo4j: Created root chain-of-custody node for {filename}")
    except Exception as e:
        print(f"[!] Neo4j Insertion Error: {e}")

def add_finding_to_evidence(sha256_hash: str, finding_type: str, statement: str, status: str):
    """Links standard forensic findings to the root evidence node."""
    if not driver:
        return

    query = """
    MATCH (e:Evidence {sha256: $sha256_hash})
    CREATE (f:Finding {
        type: $finding_type, 
        statement: $statement, 
        status: $status, 
        timestamp: timestamp()
    })
    MERGE (e)-[:HAS_FINDING]->(f)
    RETURN f
    """
    try:
        with driver.session() as session:
            session.run(query, sha256_hash=sha256_hash, finding_type=finding_type, statement=statement, status=status)
            print(f"[+] Neo4j: Linked {status} finding to {sha256_hash[:8]}...")
    except Exception as e:
        print(f"[!] Neo4j Finding Insertion Error: {e}")

def get_all_evidence():
    """Fetches the list of all evidence for the main dashboard table."""
    if not driver:
        return []
    
    query = """
    MATCH (e:Evidence)
    RETURN e.filename AS filename, 
           e.sha256 AS sha256_hash, 
           e.status AS status, 
           e.ingested_at AS ingested_at
    ORDER BY e.ingested_at DESC
    """
    try:
        with driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    except Exception as e:
        print(f"[!] Neo4j Fetch Error: {e}")
        return []

def get_evidence_findings(sha256_hash: str):
    """Fetches findings for a specific file, prioritizing spoliation alerts."""
    if not driver:
        return []
    
    query = """
    MATCH (e:Evidence {sha256: $sha256_hash})-[:HAS_FINDING]->(f:Finding)
    RETURN f.type AS type, 
           f.statement AS statement, 
           f.status AS status, 
           f.timestamp AS timestamp
    ORDER BY f.type = "SPOLIATION_ALERT" DESC, f.timestamp DESC
    """
    try:
        with driver.session() as session:
            result = session.run(query, sha256_hash=sha256_hash)
            return [record.data() for record in result]
    except Exception as e:
        print(f"[!] Neo4j Findings Fetch Error: {e}")
        return []

def mark_evidence_spoliation(sha256_hash: str):
    """Marks evidence tampered and ensures only ONE idempotent alert node exists."""
    if not driver:
        return

    # BUG FIX: Change 'CREATE (f:Finding...)' to an idempotent 'MERGE'
    # based on the unique combination of the relationship and type.
    query = """
    MATCH (e:Evidence {sha256: $sha256_hash})
    SET e.status = "TAMPERED / SPOLIATION DETECTED"
    MERGE (e)-[:HAS_FINDING]->(f:Finding {type: "SPOLIATION_ALERT"})
    SET f.statement = "CRITICAL: Current file on disk does not match immutable root seal!",
        f.status = "TAMPERED",
        f.timestamp = timestamp()
    RETURN e
    """
    try:
        with driver.session() as session:
            session.run(query, sha256_hash=sha256_hash)
            print(f"[!] Neo4j: Marked {sha256_hash[:8]} as SPOLIATION DETECTED!")
    except Exception as e:
        print(f"[!] Neo4j Spoliation Mark Error: {e}")


def record_custody_event(sha256_hash: str, officer_id: str, action: str, reason: str, location: str):
    """
    Creates a DCoC event node answering the 5 Ws for court admissibility.
    action examples: 'INGESTED', 'VERIFIED_SEAL', 'SPOLIATION_DETECTED'
    """
    if not driver:
        return

    query = """
    MATCH (e:Evidence {sha256: $sha256_hash})
    CREATE (c:CustodyEvent {
        officer_id: $officer_id,
        action: $action,
        reason: $reason,
        location: $location,
        timestamp: timestamp()
    })
    MERGE (e)-[:HANDLED_BY]->(c)
    RETURN c
    """
    try:
        with driver.session() as session:
            session.run(query, 
                        sha256_hash=sha256_hash, 
                        officer_id=officer_id, 
                        action=action, 
                        reason=reason, 
                        location=location)
            print(f"[+] Neo4j: Logged DCoC {action} event for Officer {officer_id}")
    except Exception as e:
        print(f"[!] Neo4j DCoC Insertion Error: {e}")

def get_custody_events(sha256_hash: str):
    """Fetches the complete digital chain of custody timeline."""
    if not driver:
        return []
    
    query = """
    MATCH (e:Evidence {sha256: $sha256_hash})-[:HANDLED_BY]->(c:CustodyEvent)
    RETURN c.officer_id AS officer_id,
           c.action AS action,
           c.reason AS reason,
           c.location AS location,
           c.timestamp AS timestamp
    ORDER BY c.timestamp ASC
    """
    try:
        with driver.session() as session:
            result = session.run(query, sha256_hash=sha256_hash)
            return [record.data() for record in result]
    except Exception as e:
        print(f"[!] Neo4j Custody Fetch Error: {e}")
        return []    


def add_evidence_finding(sha256_hash: str, finding_type: str, statement: str, status: str):
    """Writes an automated Z3/Forensic finding to the evidence node."""
    if not driver:
        return

    # Fixed: Changed sha256_hash to sha256 to match your DB schema
    query = """
    MATCH (e:Evidence {sha256: $sha256_hash})
    CREATE (e)-[:HAS_FINDING]->(f:Finding {
        type: $type, 
        statement: $statement, 
        status: $status,
        timestamp: timestamp()
    })
    """
    try:
        # Fixed: Using your existing driver.session() method
        with driver.session() as session:
            session.run(query, sha256_hash=sha256_hash, type=finding_type, statement=statement, status=status)
            print(f"[+] Neo4j: Added automated finding to {sha256_hash[:8]}")
    except Exception as e:
        print(f"[!] Neo4j Finding Insertion Error: {e}")


def record_evidence_purge(sha256_hash: str, officer_id: str, reason: str, location: str):
    """
    Scrubs evidence status and creates a permanent Tombstone DCoC event 
    proving authorized destruction of the raw vault data.
    """
    if not driver:
        return

    query = """
    MATCH (e:Evidence {sha256: $sha256_hash})
    SET e.status = "PURGED / TOMBSTONE"
    CREATE (c:CustodyEvent {
        officer_id: $officer_id,
        action: "EVIDENCE_PURGED_TOMBSTONE",
        reason: $reason,
        location: $location,
        timestamp: timestamp()
    })
    MERGE (e)-[:HANDLED_BY]->(c)
    RETURN e
    """
    try:
        with driver.session() as session:
            session.run(query, 
                        sha256_hash=sha256_hash, 
                        officer_id=officer_id, 
                        reason=reason, 
                        location=location)
            print(f"[!] Neo4j: Executed PURGE TOMBSTONE for {sha256_hash[:8]}")
    except Exception as e:
        print(f"[!] Neo4j Purge Recording Error: {e}")