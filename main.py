import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parent
JOB_STORE: dict[str, dict] = {}

app = FastAPI(title="Stock Research Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _start_job(job_name: str, command: list[str]) -> dict:
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "name": job_name,
        "status": "running",
        "startedAt": _now_iso(),
        "duration": None,
        "output": [],
        "exitCode": None,
        "command": command,
    }
    JOB_STORE[job_id] = job

    def runner() -> None:
        try:
            process = subprocess.Popen(
                command,
                cwd=str(ROOT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert process.stdout is not None
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    job["output"].append(line)
                    if len(job["output"]) > 300:
                        job["output"] = job["output"][-300:]
            exit_code = process.wait()
            job["exitCode"] = exit_code
            job["status"] = "completed" if exit_code == 0 else "failed"
        except Exception as exc:  # pragma: no cover - defensive
            job["status"] = "failed"
            job["output"].append(f"ERROR: {exc}")
            job["exitCode"] = 1

    threading.Thread(target=runner, daemon=True).start()
    return job


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/stocks")
def list_stocks():
    return [
        {"stockId": 1, "symbol": "BEL", "companyName": "Bharat Electronics", "sector": "Defence", "closePrice": 412.8, "momentumScore": 92.4, "rsi14": 68.2},
        {"stockId": 2, "symbol": "TRENT", "companyName": "Trent Limited", "sector": "Retail", "closePrice": 5480, "momentumScore": 88.1, "rsi14": 63.9},
        {"stockId": 3, "symbol": "MAZDOCK", "companyName": "Mazagon Dock Shipbuilders", "sector": "Defence", "closePrice": 2810.4, "momentumScore": 87.3, "rsi14": 71.4},
        {"stockId": 4, "symbol": "HAL", "companyName": "Hindustan Aeronautics", "sector": "Defence", "closePrice": 4687.2, "momentumScore": 85.6, "rsi14": 69.8},
        {"stockId": 5, "symbol": "CDSL", "companyName": "Central Depository Services", "sector": "Financials", "closePrice": 1432.9, "momentumScore": 83.8, "rsi14": 67.1},
        {"stockId": 6, "symbol": "INDUSINDBK", "companyName": "IndusInd Bank", "sector": "Banking", "closePrice": 1428.6, "momentumScore": 81.2, "rsi14": 64.7},
        {"stockId": 7, "symbol": "TCS", "companyName": "Tata Consultancy Services", "sector": "IT", "closePrice": 3937.4, "momentumScore": 79.9, "rsi14": 66.5},
        {"stockId": 8, "symbol": "INFY", "companyName": "Infosys", "sector": "IT", "closePrice": 1790.2, "momentumScore": 78.6, "rsi14": 63.8},
        {"stockId": 9, "symbol": "HDFC", "companyName": "HDFC Bank", "sector": "Banking", "closePrice": 1710.5, "momentumScore": 77.4, "rsi14": 62.9},
        {"stockId": 10, "symbol": "ICICIBANK", "companyName": "ICICI Bank", "sector": "Banking", "closePrice": 1268.3, "momentumScore": 76.8, "rsi14": 61.5},
    ]


@app.get("/api/v1/dashboard")
def get_dashboard():
    return {
        "metrics": {
            "stocksTracked": 2364,
            "latestUpdate": "2026-07-26T09:32:00+05:30",
            "indicatorsStatus": "healthy",
            "screenersStatus": "healthy",
            "portfolioCount": 3,
        },
        "topMomentumStocks": [
            {"stockId": 1, "symbol": "BEL", "companyName": "Bharat Electronics", "score": 92.4, "price": 412.8, "changePercent": 3.2},
            {"stockId": 2, "symbol": "TRENT", "companyName": "Trent Limited", "score": 88.1, "price": 5480, "changePercent": 1.8},
            {"stockId": 3, "symbol": "MAZDOCK", "companyName": "Mazagon Dock Shipbuilders", "score": 84.6, "price": 2810.4, "changePercent": 2.5},
        ],
        "latestBuySignals": [
            {"stockId": 4, "symbol": "HAL", "companyName": "Hindustan Aeronautics", "score": 86.2, "price": 4687.2, "changePercent": 0.9},
            {"stockId": 5, "symbol": "CDSL", "companyName": "Central Depository Services", "score": 80.4, "price": 1432.9, "changePercent": 1.2},
        ],
        "recentJobs": [
            {"id": "job-1", "name": "Daily market update", "status": "healthy", "startedAt": "2026-07-26T09:00:00+05:30", "duration": "2m 18s"},
            {"id": "job-2", "name": "Portfolio rebalance", "status": "healthy", "startedAt": "2026-07-25T18:00:00+05:30", "duration": "14s"},
        ],
        "portfolios": [
            {"name": "TOP20", "value": 1_024_500, "returnPercent": 2.45, "holdings": 20},
            {"name": "TOP10", "value": 1_011_200, "returnPercent": 1.12, "holdings": 10},
        ],
    }


@app.get("/api/v1/screeners")
def get_screeners():
    return [
        {"name": "Momentum", "description": "3- and 6-month price strength", "candidateCount": 118, "status": "healthy"},
        {"name": "Strong Uptrend", "description": "Aligned moving averages and RSI", "candidateCount": 191, "status": "healthy"},
        {"name": "52 Week High", "description": "Trading within 5% of annual high", "candidateCount": 165, "status": "healthy"},
        {"name": "Golden Cross", "description": "Fresh SMA50 and SMA200 crossovers", "candidateCount": 9, "status": "healthy"},
    ]


@app.get("/api/v1/portfolios")
def get_portfolios():
    return [
        {"name": "TOP20", "value": 1_024_500, "returnPercent": 2.45, "holdings": 20},
        {"name": "TOP10", "value": 1_011_200, "returnPercent": 1.12, "holdings": 10},
        {"name": "TOP5", "value": 987_500, "returnPercent": 0.74, "holdings": 5},
    ]


@app.get("/api/v1/rules")
def get_rules():
    return [
        {"id": 1, "ruleName": "Momentum", "ruleType": "momentum", "weight": 0.25, "enabled": True},
        {"id": 2, "ruleName": "Strong Uptrend", "ruleType": "strong_uptrend", "weight": 0.20, "enabled": True},
        {"id": 3, "ruleName": "Golden Cross", "ruleType": "golden_cross", "weight": 0.10, "enabled": True},
        {"id": 4, "ruleName": "Risk Cap", "ruleType": "risk_cap", "weight": 0.15, "enabled": True},
    ]


@app.get("/api/v1/backtesting")
def get_backtesting():
    return {
        "summary": [
            {"strategy": "Momentum", "period": "12M", "totalReturnPercent": 26.8, "sharpeRatio": 1.41, "maxDrawdownPercent": -8.1, "winRatePercent": 63.4},
            {"strategy": "Golden Cross", "period": "24M", "totalReturnPercent": 18.5, "sharpeRatio": 1.18, "maxDrawdownPercent": -10.2, "winRatePercent": 58.7},
        ],
        "equityCurve": [
            {"month": "Jan", "equity": 100000},
            {"month": "Feb", "equity": 104500},
            {"month": "Mar", "equity": 109100},
            {"month": "Apr", "equity": 112800},
            {"month": "May", "equity": 118600},
            {"month": "Jun", "equity": 126800},
        ],
        "benchmark": [
            {"month": "Jan", "equity": 100000},
            {"month": "Feb", "equity": 102300},
            {"month": "Mar", "equity": 103100},
            {"month": "Apr", "equity": 104700},
            {"month": "May", "equity": 106400},
            {"month": "Jun", "equity": 108900},
        ],
    }


@app.get("/api/v1/jobs")
def get_jobs():
    return [
        {"id": "job-1", "name": "Daily market update", "status": "healthy", "startedAt": "2026-07-26T09:00:00+05:30", "duration": "2m 18s", "details": "Downloaded 64 symbols and refreshed indicators."},
        {"id": "job-2", "name": "Portfolio rebalance", "status": "healthy", "startedAt": "2026-07-25T18:00:00+05:30", "duration": "14s", "details": "Rebalanced TOP20 allocation and validated risk cap."},
        {"id": "job-3", "name": "Screener refresh", "status": "warning", "startedAt": "2026-07-25T16:30:00+05:30", "duration": "1m 05s", "details": "One screener flagged a stale rank snapshot."},
    ]


@app.post("/api/v1/jobs/run/full-portfolio-run")
def run_full_portfolio_job():
    return _start_job(
        "Full portfolio run",
        [sys.executable, "-m", "daily_jobs.full_portfolio_run"],
    )


@app.post("/api/v1/jobs/run/validate-pipeline")
def run_validate_pipeline_job():
    return _start_job(
        "Validate pipeline",
        [sys.executable, "-m", "daily_jobs.validate_pipeline"],
    )


@app.get("/api/v1/jobs/{job_id}")
def get_job(job_id: str):
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
