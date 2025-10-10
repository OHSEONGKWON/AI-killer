# Backend setup

This folder contains a minimal FastAPI app and a virtual environment.

Activate the venv (PowerShell):

    .\\venv\\Scripts\\Activate.ps1

Install additional packages (if needed):

    python -m pip install <package>

Run the app with uvicorn (from inside activated venv):

    uvicorn app:app --reload --port 8000

Open http://127.0.0.1:8000/ and http://127.0.0.1:8000/health

API endpoints
-------------

- GET / -> returns a welcome message used by tests
- GET /health -> basic health check
- POST /detect -> placeholder detection endpoint; expects JSON {"abstract": "..."}


Development setup for the detection service
-----------------------------------------

1. Activate venv (PowerShell):

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
    .\\venv\\Scripts\\Activate.ps1

2. Install dev dependencies:

    python -m pip install -r requirements-dev.txt

3. Run tests:

    pytest -q

4. Pre-commit hooks:

    python -m pip install pre-commit
    pre-commit install

Pipeline notes
--------------
This project aims to implement a pipeline that:

1. Extracts the title from a user-provided Korean abstract.
2. Uses GPT to generate 20 candidate abstracts for the title.
3. Encodes the original + generated abstracts with a sentence-transformer (KR-SBERT).
4. Computes cosine similarities and averages them against a threshold to decide AI vs human.

Next dev steps (I can scaffold these):
- Add GPT client wrapper and generation endpoint
- Add embedding encoder wrapper (sentence-transformers) and caching
- Add similarity computation service and threshold config
- Add database or Redis cache for generated samples (optional)
