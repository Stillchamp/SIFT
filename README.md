SIFT  Secure Immutable Forensic Tracking
Track H: Proving Digital Evidence Has Not Been Changed

An enterprise-grade digital forensics vault and chain-of-custody ledger.

📌 The Problem & Our Solution
Digital evidence is only useful if you can prove it is genuine. Today, massive files like 100GB phone extractions are copied onto flash drives, emailed between precincts, and change hands for years. Cases are routinely lost because nobody can mathematically prove the files weren't altered.

SIFT replaces this chaos. We built an immutable, cryptographically sealed chain-of-custody platform that decouples massive physical files from their digital fingerprints.

✨ Core Features
📶 Offline Intake (For 100GB+ Files): Officers generate a SHA-256 fingerprint locally at the crime scene in seconds. The massive file stays secure locally, while the tiny hash is synced to the cloud when the network is restored.

🔒 Neo4j Immutable Vault: Baseline hashes and custody handoffs are permanently locked into a Neo4j graph database.

🚨 The Spoliation Trap: When examiners check out evidence, SIFT gives them an AES-256 encrypted working copy. If they decrypt it, alter even a single word, and try to check it back in, SIFT catches the hash mismatch and instantly flags a tamper alert.

🧠 Algorithmic Audits: Automatically maps network attack topologies (PageRank) and catches manipulated timestamps (Temporal Check).

📄 Judge-Friendly Court PDFs: With one click, SIFT translates complex system logs and JSON into a plain-English, ISO 27037-compliant court dossier.

⚠️ Honest Limitations
To be completely transparent about where our prototype boundaries lie:

Browser Limits: The current web frontend will crash if you drag-and-drop a 100GB file. Enterprise deployment requires a chunked, multi-part upload pipeline.

Pre-Ingestion Tampering: SIFT is a vault, not a time machine. We guarantee perfect custody after the first hash is generated, but if an officer alters a file before that initial hash, SIFT will seal the altered file as the truth.

🛠️ Tech Stack
Frontend: Vue 3, Vite, Tailwind CSS (Hosted on Vercel)

Backend: FastAPI, Python, AES-256 Cryptography (Hosted on Render)

Database: Neo4j Graph Database

Analysis & Reports: NetworkX (PageRank), ReportLab (PDF Generation)

🚀 Quick Start
vist: https://sift-dashboard-kohl.vercel.app/

