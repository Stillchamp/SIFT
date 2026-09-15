# SIFT: Secure Immutable Forensic Tracking

**Submission for ICSC Universities Hackathon 2026**  
**Track H:** Media, Information Integrity & Civic Trust: Proving Digital Evidence Has Not Been Changed  

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D)
![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)

##  Problem Statement & Approach
In modern digital investigations, traditional forensic storage relies on vulnerable physical drives and manual chain-of-custody tracking. SIFT replaces this "Flash Drive Chaos" with a cryptographic, automated ecosystem. 

By coupling a **Neo4j graph ledger** with SHA-256 baselines, AES-256 encrypted checkouts, and algorithmic topology analysis, SIFT guarantees absolute mathematical integrity from intake to court submission or lawful warrant expiration.

##  Core Features
1. **Cryptographic Sealing & Offline Sync:** Calculates a SHA-256 baseline upon intake. Includes an offline-sync field hash verification to trap evidence tampered with in transit from the physical crime scene.
2. **AES-256 Confidentiality ($d_{DE}$):** In accordance with ISO/IEC 27037, original master files are never analyzed directly. SIFT generates encrypted working copies for examiners.
3. **The Handoff Handshake:** Returning working copies are decrypted and hashed against the Neo4j baseline. Any bit-level discrepancy instantly triggers a Spoliation Alert attributed to the submitting officer.
4. **Algorithmic Forensic Engines:**
   * **Temporal Sequence Engine:** Mathematically proves log chronometry, instantly detecting clock manipulation (Timestomping) in CSV, JSON, and native `.evtx` files.
   * **NetworkX PageRank:** Maps directed attack interactions to identify the network's "Center of Gravity."
5. **Lawful Purge (NDPR / GDPR):** Securely scrubs physical binaries upon warrant expiration while preserving an immutable `Tombstone Record` in the graph ledger.
6. **Court-Admissible Export:** Generates an ISO 27037-compliant PDF dossier of the digital chain of custody (DCoC) on the fly.

##  Synthetic Dataset Methodology
Per hackathon constraints prohibiting real personal data, this system was built and tested entirely on synthetic datasets:
* `test_logs.json`: Synthetic enterprise domain controller logs demonstrating timestomping.
* `test_logs.csv`: Synthetic multi-hop privilege escalation data.
* `Security.evtx`: A native Windows Event Log generated from a sandboxed evaluation VM to test pure-Python binary XML parsing.

##  Honest Limitations & Failure Modes
In adherence to the evaluation rubric, we acknowledge the following systemic limitations under real-world conditions:
1. **Garbage-In, Garbage-Out (Intake Trust):** SIFT guarantees evidence is not altered *after* reaching the platform. However, if a corrupt investigator modifies a file *before* the initial offline field hash is generated, SIFT will cryptographically seal the tampered file as the baseline.
2. **In-Memory Scale Limits:** The current pure-Python `.evtx` parser loads XML structures into memory. Processing single binary event logs larger than 2GB causes memory spikes on standard hardware. Production deployment would require streaming `iterparse` logic.
3. **Single-Node Graph Availability:** SIFT currently relies on a single Neo4j database instance. Full Byzantine Fault Tolerance (BFT) against database-level attacks would require a distributed consensus protocol (e.g., Hyperledger Fabric).

##  Running the Prototype (Local Setup)

*(Note to Judges: A `docker-compose` setup is provided for 1-click evaluation.)*

### Backend (FastAPI)
```bash
cd sift-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000