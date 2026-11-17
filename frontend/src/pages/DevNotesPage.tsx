import { Card } from '../components/Card'
import { PageHeader } from '../components/PageHeader'

const architectureItems = [
    'Frontend: React + Vite dashboard in the frontend folder.',
    'Backend: FastAPI app in main.py with API routes under /api/v1.',
    'Database: PostgreSQL schema and SQL assets under database/ and Alembic migrations under alembic/versions.',
    'Data ingestion: ingestion/ downloads and loads data to the database.',
    'Calculations: calculations/ updates indicators and momentum indicators.',
    'Screeners: screeners/ contains the screening and ranking pipeline.',
    'Portfolio: portfolio/ builds portfolios, orders, pricing, accounting, and performance reporting.',
    'Execution: execution/ contains paper-execution and cost logic.',
    'Backtesting: backtesting/ stores analysis and historical ranking jobs.',
    'Jobs: daily_jobs/ is the operational runner for the full data pipeline.',
]

export function DevNotesPage() {
    return (
        <div className="page-container space-y-6">
            <PageHeader
                title="DevNotes"
                description="Project context, startup steps, update flow, and developer commands for future work."
                breadcrumbs={['Research', 'DevNotes']}
            />

            <Card>
                <div className="space-y-5 p-5">
                    <div>
                        <h2 className="text-lg font-semibold text-white">Architecture</h2>
                        <ul className="mt-3 space-y-2 text-sm text-slate-300">
                            {architectureItems.map((item) => (
                                <li key={item} className="flex gap-2">
                                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-400" />
                                    <span>{item}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div>
                        <h3 className="text-base font-semibold text-white">App flow</h3>
                        <pre className="mt-3 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-emerald-300">
                            {`Database
  ↓
Ingestion / daily price update
  ↓
Calculations / indicators
  ↓
Screeners / combined ranking
  ↓
Portfolio build / order generation / execution
  ↓
Front-end dashboard`}
                        </pre>
                    </div>
                </div>
            </Card>

            <Card>
                <div className="space-y-4 p-5">
                    <h2 className="text-lg font-semibold text-white">How to run the app</h2>

                    <div>
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Backend</h3>
                        <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-emerald-300">
                            {`cd "d:\Agent Projects\stock-research-agent"
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload`}
                        </pre>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Frontend</h3>
                        <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-emerald-300">
                            {`cd "d:\Agent Projects\stock-research-agent\frontend"
npm install
npm run dev`}
                        </pre>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Local URLs</h3>
                        <ul className="mt-2 space-y-1 text-sm text-slate-300">
                            <li>Backend: http://localhost:8000</li>
                            <li>Swagger UI: http://localhost:8000/docs</li>
                            <li>Frontend: http://localhost:5173</li>
                        </ul>
                    </div>
                </div>
            </Card>

            <Card>
                <div className="space-y-4 p-5">
                    <h2 className="text-lg font-semibold text-white">How to update the data pipeline</h2>

                    <div>
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Full portfolio run</h3>
                        <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-emerald-300">
                            {`cd "d:\Agent Projects\stock-research-agent"
.\.venv\Scripts\Activate.ps1
python -m daily_jobs.full_portfolio_run`}
                        </pre>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Run all screeners manually</h3>
                        <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-emerald-300">
                            {`cd "d:\Agent Projects\stock-research-agent"
.\.venv\Scripts\Activate.ps1
python -m screeners.run_all_screeners 2026-10-28`}
                        </pre>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Validate pipeline</h3>
                        <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-emerald-300">
                            {`cd "d:\Agent Projects\stock-research-agent"
.\.venv\Scripts\Activate.ps1
python -m daily_jobs.validate_pipeline`}
                        </pre>
                    </div>
                </div>
            </Card>

            <Card>
                <div className="space-y-4 p-5">
                    <h2 className="text-lg font-semibold text-white">Testing and verification</h2>

                    <div>
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Python tests</h3>
                        <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-emerald-300">
                            {`cd "d:\Agent Projects\stock-research-agent"
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests`}
                        </pre>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Frontend build</h3>
                        <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs text-emerald-300">
                            {`cd "d:\Agent Projects\stock-research-agent\frontend"
npm run build`}
                        </pre>
                    </div>
                </div>
            </Card>

            <Card>
                <div className="space-y-4 p-5">
                    <h2 className="text-lg font-semibold text-white">Developer notes</h2>
                    <ul className="space-y-2 text-sm text-slate-300">
                        <li>1. Keep the backend and frontend running in separate terminals while developing locally.</li>
                        <li>2. Use the live API flow by default; mock data is only used when VITE_USE_MOCKS is set to true.</li>
                        <li>3. The full portfolio job refreshes prices, indicators, screeners, and portfolio logic in one pass.</li>
                        <li>4. The dashboard latest update is expected to reflect the most recent complete trade date from the database.</li>
                        <li>5. Check the database and the daily_jobs orchestration scripts before changing report output or pipeline sequencing.</li>
                    </ul>
                </div>
            </Card>
        </div>
    )
}
