import hashlib
from pathlib import Path
from fastapi import APIRouter, UploadFile, HTTPException, File, Form, BackgroundTasks, Body
from fastapi.responses import FileResponse,StreamingResponse
from app.services.aes_cipher import encrypt_data, decrypt_data
from app.services.pdf_generator import generate_court_report
from app.database.neo4j_client import record_evidence_purge
import aiofiles

from app.database.neo4j_client import (
    get_all_evidence, 
    create_evidence_root_node, 
    get_evidence_findings,
    mark_evidence_spoliation,
    record_custody_event,
    get_custody_events
)
from app.services.z3_engine import run_analysis_pipeline

router = APIRouter()
UPLOAD_DIR = Path("evidence_locker")
UPLOAD_DIR.mkdir(exist_ok=True)
CHUNK_SIZE = 1024 * 1024 * 5  # 5 MB chunks

@router.post("/ingest")
async def ingest_evidence(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    field_hash: str = Form(None),
    officer_id: str = Form(...), 
    location: str = Form(...)
):
    file_path = UPLOAD_DIR / file.filename
    sha256_hash = hashlib.sha256()
    
    async with aiofiles.open(file_path, "wb") as out_file:
        while chunk := await file.read(CHUNK_SIZE):
            await out_file.write(chunk)
            sha256_hash.update(chunk)
            
    intake_hash = sha256_hash.hexdigest()
    
    # Check for Spoliation on field intake
    if field_hash and field_hash.strip().lower() != intake_hash.lower():
        file_path.unlink()
        raise HTTPException(
            status_code=400, 
            detail="Spoliation Error: Field hash does not match intake hash."
        )
    
    # DUPLICATE PROTECTION: Check if hash already exists in Neo4j
    existing_evidence = get_all_evidence()
    if any(item["sha256_hash"].lower() == intake_hash.lower() for item in existing_evidence):
        file_path.unlink() # Delete duplicate from locker
        raise HTTPException(
            status_code=409, 
            detail=f"DUPLICATE DETECTED: This file ({file.filename}) is already cryptographically sealed in the ledger."
        )

    # Commit root node immediately to Neo4j
    create_evidence_root_node(file.filename, intake_hash)

    # LOG THE CHAIN OF CUSTODY EVENT
    record_custody_event(
        sha256_hash=intake_hash,
        officer_id=officer_id,
        action="INGESTED & SEALED",
        reason="Initial intake into SIFT vault",
        location=location
    )
    
    # Trigger background Z3 analysis
    background_tasks.add_task(run_analysis_pipeline, str(file_path), intake_hash)
    
    return {
        "filename": file.filename,
        "status": "Cryptographically Sealed",
        "sha256_hash": intake_hash,
        "field_match": bool(field_hash)
    }

@router.get("/evidence")
def list_evidence():
    data = get_all_evidence()
    
    # AUTOMATIC CONTINUOUS RE-VERIFICATION ON FETCH
    for item in data:
        # 1. SKIP PURGED EVIDENCE: Do NOT flag spoliation if lawfully purged
        if item.get("status") == "PURGED / TOMBSTONE":
            continue

        file_path = UPLOAD_DIR / item["filename"]
        if not file_path.exists():
            mark_evidence_spoliation(item["sha256_hash"])
            item["status"] = "TAMPERED / SPOLIATION DETECTED"
            continue
            
        current_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                current_hash.update(chunk)
                
        if current_hash.hexdigest().lower() != item["sha256_hash"].lower():
            mark_evidence_spoliation(item["sha256_hash"])
            item["status"] = "TAMPERED / SPOLIATION DETECTED"
            
    return {"count": len(data), "evidence": data}

@router.get("/evidence/{sha256_hash}/findings")
def list_findings(sha256_hash: str):
    findings = get_evidence_findings(sha256_hash)
    return {"hash": sha256_hash, "count": len(findings), "findings": findings}

@router.post("/evidence/{sha256_hash}/verify")
async def verify_evidence_integrity(sha256_hash: str, payload: dict = Body(...)):
    officer_id = payload.get("officer_id", "UNKNOWN")
    location = payload.get("location", "UNKNOWN")
    all_evidence = get_all_evidence()
    target = next((item for item in all_evidence if item["sha256_hash"] == sha256_hash), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Evidence record not found in ledger.")
    
    # 2. GUARD: Return HTTP 410 if already lawfully purged
    if target.get("status") == "PURGED / TOMBSTONE":
        raise HTTPException(
            status_code=410, 
            detail="This evidence record was lawfully PURGED under court order. Raw files no longer exist."
        )

    file_path = UPLOAD_DIR / target["filename"]
    if not file_path.exists():
        mark_evidence_spoliation(sha256_hash)
        record_custody_event(sha256_hash, officer_id, "SPOLIATION_DETECTED", "File is missing from disk without purge authorization.", location)
        return {
            "status": "SPOLIATION_DETECTED",
            "is_intact": False,
            "message": "File is missing from disk."
        }
        
    current_hash = hashlib.sha256()
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(CHUNK_SIZE):
            current_hash.update(chunk)
            
    disk_hash = current_hash.hexdigest()
    
    if disk_hash.lower() != sha256_hash.lower():
        mark_evidence_spoliation(sha256_hash)
        # Log the exact officer who discovered the spoliation
        record_custody_event(sha256_hash, officer_id, "SPOLIATION_DETECTED", "Automated hash verification failed", location)
        return {
            "status": "SPOLIATION_DETECTED",
            "is_intact": False,
            "expected_hash": sha256_hash,
            "current_disk_hash": disk_hash,
            "message": "File contents have been altered since sealing!"
        }
        
    # Log successful verification
    record_custody_event(sha256_hash, officer_id, "VERIFIED_SEAL", "Manual baseline verification", location)
    
    return {
        "status": "SEAL_INTACT",
        "is_intact": True,
        "hash": sha256_hash,
        "message": "Cryptographic seal intact. Disk hash matches baseline."
    }

@router.get("/evidence/{sha256_hash}/custody")
def list_custody_events(sha256_hash: str):
    """Exposes the handling timeline to the Vue dashboard."""
    events = get_custody_events(sha256_hash)
    return {"hash": sha256_hash, "events": events}

@router.post("/evidence/{sha256_hash}/checkout")
async def checkout_working_copy(sha256_hash: str, payload: dict = Body(...)):
    """
    Securely generates a duplicated working copy (d_DE), encrypts it with AES-256,
    logs the checkout event, and protects the original file.
    """
    officer_id = payload.get("officer_id")
    location = payload.get("location")
    reason = payload.get("reason", "External analysis checkout")
    encryption_key = payload.get("encryption_key", "SIFT_Default_Secure_Key_2026")
    
    if not officer_id or not location:
        raise HTTPException(status_code=400, detail="Officer ID and Location are strictly required for checkout.")

    # Find the target evidence in the ledger
    all_evidence = get_all_evidence()
    target = next((item for item in all_evidence if item["sha256_hash"] == sha256_hash), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Evidence record not found in ledger.")

    # =========================================================================
    # ADDED GUARD: Block checkout if evidence was lawfully purged under court order
    # =========================================================================
    if target.get("status") == "PURGED / TOMBSTONE":
        raise HTTPException(
            status_code=410, 
            detail="Cannot check out evidence. Raw file was lawfully PURGED under court order."
        )
    # =========================================================================

    file_path = UPLOAD_DIR / target["filename"]
    if not file_path.exists():
        mark_evidence_spoliation(sha256_hash)
        record_custody_event(sha256_hash, officer_id, "SPOLIATION_DETECTED", "Original missing during checkout attempt.", location)
        raise HTTPException(status_code=404, detail="Original file is missing from the secure vault!")

    # 1. LOG THE CUSTODY EVENT
    record_custody_event(
        sha256_hash=sha256_hash,
        officer_id=officer_id,
        action="AES_ENCRYPTED_CHECKOUT",
        reason=reason,
        location=location
    )
    
    # 2. ENCRYPT AND SERVE THE DUPLICATED WORKING COPY (d_DE)
    with open(file_path, "rb") as f:
        raw_bytes = f.read()
        
    encrypted_bytes = encrypt_data(raw_bytes, encryption_key)
    
    encrypted_filename = f"AES_ENC_d_DE_{target['filename']}.enc"
    encrypted_filepath = UPLOAD_DIR / encrypted_filename
    
    with open(encrypted_filepath, "wb") as f:
        f.write(encrypted_bytes)

    return FileResponse(
        path=encrypted_filepath, 
        media_type='application/octet-stream', 
        filename=encrypted_filename
    )



@router.post("/evidence/{sha256_hash}/checkin")
async def checkin_working_copy(
    sha256_hash: str,
    file: UploadFile = File(...),
    officer_id: str = Form(...),
    location: str = Form(...),
    reason: str = Form("Returning working copy after analysis"),
    encryption_key: str = Form("SIFT_Default_Secure_Key_2026")
):
    """
    Accepts an encrypted working copy, decrypts it, verifies the hash 
    against the baseline, and logs the outcome in the DCoC.
    """
    # 1. Verify the evidence exists in the ledger
    all_evidence = get_all_evidence()
    target = next((item for item in all_evidence if item["sha256_hash"] == sha256_hash), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Evidence record not found in ledger.")

    # 2. Read the uploaded encrypted file
    encrypted_bytes = await file.read()

    # 3. Decrypt the file using the provided passphrase
    try:
        decrypted_bytes = decrypt_data(encrypted_bytes, encryption_key)
    except Exception as e:
        # If decryption fails, the key is wrong or the file is heavily corrupted
        record_custody_event(sha256_hash, officer_id, "FAILED_DECRYPTION", "Invalid key or corrupted cipher file submitted.", location)
        raise HTTPException(status_code=401, detail="Decryption failed. Invalid AES passphrase or corrupted file.")

    # 4. Hash the decrypted working copy
    checkin_hash = hashlib.sha256(decrypted_bytes).hexdigest()

    # 5. The Handoff Handshake: Compare against the immutable baseline
    if checkin_hash.lower() != sha256_hash.lower():
        # TAMPERING DETECTED: Log the specific officer who submitted the tampered file
        mark_evidence_spoliation(sha256_hash)
        record_custody_event(
            sha256_hash=sha256_hash,
            officer_id=officer_id,
            action="SPOLIATION_DETECTED",
            reason=f"Check-in failed! Returned hash {checkin_hash[:8]}... does not match baseline.",
            location=location
        )
        return {
            "status": "REJECTED",
            "is_intact": False,
            "message": "CRITICAL: The working copy you returned has been altered. Spoliation alert logged."
        }

    # 6. SUCCESS: The file is intact. Log the successful return.
    record_custody_event(
        sha256_hash=sha256_hash,
        officer_id=officer_id,
        action="HANDOFF_VERIFIED",
        reason=reason,
        location=location
    )

    return {
        "status": "ACCEPTED",
        "is_intact": True,
        "message": "Working copy integrity verified. Handoff successfully logged in the DCoC."
    }


@router.delete("/evidence/{sha256_hash}/purge")
async def purge_evidence(sha256_hash: str, payload: dict = Body(...)):
    """
    Securely scrubs raw binary files from disk and sets a permanent 
    DCoC Tombstone record for warrant expiration or compliance.
    """
    officer_id = payload.get("officer_id")
    location = payload.get("location")
    reason = payload.get("reason", "Warrant Expired / Court Order Case Closure")

    if not officer_id or not location:
        raise HTTPException(status_code=400, detail="Officer ID and Location are strictly required for purging evidence.")

    all_evidence = get_all_evidence()
    target = next((item for item in all_evidence if item["sha256_hash"] == sha256_hash), None)

    if not target:
        raise HTTPException(status_code=404, detail="Evidence record not found in ledger.")

    # 1. Scrub physical files from disk (Original + Working Copies)
    deleted_files_count = 0
    original_path = UPLOAD_DIR / target["filename"]
    
    if original_path.exists():
        original_path.unlink()
        deleted_files_count += 1

    # Clean up any lingering .enc working copies in vault directory
    for file_item in UPLOAD_DIR.glob(f"*{sha256_hash[:8]}*"):
        try:
            file_item.unlink()
            deleted_files_count += 1
        except Exception:
            pass

    # 2. Log the immutable Tombstone Event in Neo4j
    record_evidence_purge(
        sha256_hash=sha256_hash,
        officer_id=officer_id,
        reason=reason,
        location=location
    )

    return {
        "status": "PURGED",
        "sha256_hash": sha256_hash,
        "message": f"Raw evidence binaries scrubbed from disk ({deleted_files_count} files deleted). DCoC Tombstone permanently logged.",
        "purged_by": officer_id
    }



@router.get("/evidence/{sha256_hash}/report")
async def download_forensic_report(sha256_hash: str):
    """Generates a court-admissible PDF dossier combining the DCoC and analysis findings."""
    all_evidence = get_all_evidence()
    target = next((item for item in all_evidence if item["sha256_hash"] == sha256_hash), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Evidence record not found in ledger.")
        
    # Gather the timeline and findings from Neo4j
    custody_events = get_custody_events(sha256_hash)
    findings = get_evidence_findings(sha256_hash)
    
    # Generate the PDF in memory
    pdf_buffer = generate_court_report(target, custody_events, findings)
    
    # Stream the PDF directly to the browser as a downloadable file
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=SIFT_Dossier_{sha256_hash[:8]}.pdf"}
    )