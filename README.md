# AI-killer

Minimal helper files added by assistant.

Setup (Python):

1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill values.

Run the FastAPI app from `Back/app/main.py` (example):

```powershell
# from project root
cd Back\app
uvicorn main:app --reload
```
