from fastapi import FastAPI

app = FastAPI(title="AI-killer backend")


@app.get("/")
async def read_root():
    return {"message": "Hello from backend venv"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/detect")
async def detect_abstract(payload: dict):
    """Placeholder endpoint for abstract detection.

    Expects JSON with at least a `abstract` field. Returns a placeholder
    response until the real detection pipeline is implemented.
    """
    abstract = payload.get("abstract")
    if not abstract:
        return {"error": "missing abstract"}
    return {"result": "unknown", "confidence": 0.0}
