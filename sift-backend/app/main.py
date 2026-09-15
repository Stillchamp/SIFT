from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ingestion

app = FastAPI(
    title="Hybrid SIFT Engine",
    description="Forensic Triage with Cryptographic Provenance"
)

# Allow the Vue.js frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change to ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount ingestion router
app.include_router(ingestion.router, prefix="/api/v1", tags=["Ingestion"])

@app.get("/")
def health_check():
    return {"status": "SIFT Core Running"}