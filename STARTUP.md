# Startup Guide

This project has two services that should be started separately:

- Backend: Python FastAPI API
- Frontend: React + Vite dashboard

## 1) Backend

From the project root:

```powershell
cd "d:\Agent Projects\stock-research-agent"
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

- http://localhost:8000
- Swagger docs: http://localhost:8000/docs

## 2) Frontend

Open a second terminal and run:

```powershell
cd "d:\Agent Projects\stock-research-agent\frontend"
npm install
npm run dev
```

The dashboard will be available at:

- http://localhost:5173

## 3) Run both together

Use two terminals:

- Terminal 1: run the backend command block above
- Terminal 2: run the frontend command block above

## 4) Common notes

- If the virtual environment does not exist yet, create it first:

```powershell
cd "d:\Agent Projects\stock-research-agent"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- If Node dependencies are not installed, run `npm install` in the frontend folder before starting the app.
- If the frontend needs live data from the backend, ensure `VITE_USE_MOCKS=false` is set in the frontend environment file before launching the dashboard.
