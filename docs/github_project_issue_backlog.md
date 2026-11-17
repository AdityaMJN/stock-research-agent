# Stock Research Agent - GitHub Issue Backlog (End-to-End)

This backlog is sequenced so that if all issues are completed in order, you reach a production-ready v1 with paper-trading validation and live-readiness gates.

## Labels to Use

1. track:data-platform
2. track:ai-intelligence
3. track:portfolio-execution
4. track:intraday
5. track:governance-risk
6. type:backend
7. type:frontend
8. type:data
9. type:ml
10. type:infra
11. type:qa
12. priority:critical
13. priority:high

## Ordered Issue List

1. SRA-001 - Define trading KPIs and paper-to-live gates
2. SRA-002 - Define risk policy and hard stop controls
3. SRA-003 - Replace stocks list API with DB-backed query
4. SRA-004 - Implement stock detail API GET /api/v1/stocks/{symbol}
5. SRA-005 - Implement stock history API GET /api/v1/stocks/{symbol}/history
6. SRA-006 - Build frontend stock detail page /stocks/:symbol
7. SRA-007 - Remove hardcoded payloads from dashboard and jobs surfaces
8. SRA-008 - Add job_runs persistence, retry policy, and structured logs
9. SRA-009 - Add Sprint 1 integration tests for stock and job endpoints
10. SRA-010 - Add schema: promoter_snapshots, insider_trades, news_articles, news_signals
11. SRA-011 - Build promoter holdings ingestion job
12. SRA-012 - Build insider transactions ingestion job
13. SRA-013 - Build multi-source news ingestion job
14. SRA-014 - Build NLP enrichment pipeline (entity, sentiment, event tagging)
15. SRA-015 - Implement ownership and news APIs for stock detail
16. SRA-016 - Add stock detail intelligence panels (ownership and news)
17. SRA-017 - Add data freshness SLAs and monitoring checks
18. SRA-018 - Add feature store schema and daily feature snapshot pipeline
19. SRA-019 - Implement hybrid scoring engine v1
20. SRA-020 - Implement recommendation APIs
21. SRA-021 - Add explainability and evidence payload for recommendations
22. SRA-022 - Add walk-forward validation pipeline
23. SRA-023 - Add benchmark comparison report vs baseline screeners
24. SRA-024 - Add paper trading schema (accounts, orders, fills, snapshots)
25. SRA-025 - Implement paper execution simulator (slippage, partial fills, rejection)
26. SRA-026 - Implement paper trading APIs
27. SRA-027 - Implement risk engine controls (position, sector, daily loss, kill switch)
28. SRA-028 - Implement PnL, attribution, and cost-aware performance reports
29. SRA-029 - Build paper trading dashboard page
30. SRA-030 - Add end-to-end paper replay tests
31. SRA-031 - Add intraday schema and ingestion pipeline
32. SRA-032 - Implement intraday signal engine (breakout and VWAP pullback)
33. SRA-033 - Implement intraday session APIs
34. SRA-034 - Implement intraday risk controls and session limits
35. SRA-035 - Build intraday monitoring dashboard
36. SRA-036 - Produce intraday evaluation report and stability gate
37. SRA-037 - Build promotion gate dashboard for paper-to-live decision
38. SRA-038 - Implement broker adapter framework and dry-run live mode
39. SRA-039 - Add trading mode switch with live safeguards
40. SRA-040 - Write operational runbooks and incident playbooks
41. SRA-041 - Run final UAT and go/no-go review
42. SRA-042 - Release v1 and enable post-launch monitoring

## Issue Templates

Use each issue title exactly with the SRA-ID prefix so dependency tracking stays clear.

---

### SRA-001 - Define trading KPIs and paper-to-live gates

Labels: track:governance-risk, type:infra, priority:critical
Depends on: none

Description:
Define measurable KPI gates for promoting paper mode to live mode.

Acceptance Criteria:
1. KPI document committed with thresholds for return, alpha, drawdown, Sharpe, Sortino, win rate, and execution quality.
2. Promotion decision matrix documented as pass/fail with rationale.
3. KPI definitions include formulas and data sources.

---

### SRA-002 - Define risk policy and hard stop controls

Labels: track:governance-risk, type:infra, priority:critical
Depends on: SRA-001

Description:
Create enforceable risk policy across positional and intraday systems.

Acceptance Criteria:
1. Configurable limits for max position, max sector, daily loss, and portfolio drawdown.
2. Kill switch behavior documented and tested.
3. Emergency flat-position procedure documented.

---

### SRA-003 - Replace stocks list API with DB-backed query

Labels: track:data-platform, type:backend, priority:high
Depends on: SRA-001

Description:
Replace static stocks payload with database query using latest snapshot.

Acceptance Criteria:
1. Endpoint reads from DB in production mode.
2. Response includes pagination and optional query filters.
3. Unit tests cover empty state and normal state.

---

### SRA-004 - Implement stock detail API GET /api/v1/stocks/{symbol}

Labels: track:data-platform, type:backend, priority:high
Depends on: SRA-003

Description:
Expose per-symbol profile and latest technical snapshot.

Acceptance Criteria:
1. Valid symbol returns profile, indicators, and latest pricing fields.
2. Unknown symbol returns 404 with consistent error body.
3. OpenAPI docs updated.

---

### SRA-005 - Implement stock history API GET /api/v1/stocks/{symbol}/history

Labels: track:data-platform, type:backend, priority:high
Depends on: SRA-004

Description:
Provide historical OHLCV and optional indicator overlays.

Acceptance Criteria:
1. Supports from, to, interval params with validation.
2. Returns chart-ready ordered time series.
3. Handles missing dates and market holidays cleanly.

---

### SRA-006 - Build frontend stock detail page /stocks/:symbol

Labels: track:data-platform, type:frontend, priority:high
Depends on: SRA-004, SRA-005

Description:
Create symbol detail page with profile cards and historical chart panel.

Acceptance Criteria:
1. Route loads data from detail and history APIs.
2. Error and loading states implemented.
3. Navigation from stocks list to detail page works.

---

### SRA-007 - Remove hardcoded payloads from dashboard and jobs surfaces

Labels: track:data-platform, type:backend, priority:high
Depends on: SRA-003

Description:
Replace all static metrics and list payloads with DB-backed or job-backed sources.

Acceptance Criteria:
1. Dashboard and jobs endpoints avoid static sample arrays.
2. Source of each metric documented.
3. Fallback behavior for missing data is deterministic.

---

### SRA-008 - Add job_runs persistence, retry policy, and structured logs

Labels: track:governance-risk, type:backend, priority:high
Depends on: SRA-007

Description:
Add persistent job run records and controlled retry behavior.

Acceptance Criteria:
1. job_runs schema and migration added.
2. Retry count and failure reason captured.
3. API returns last N runs for each job.

---

### SRA-009 - Add Sprint 1 integration tests for stock and job endpoints

Labels: track:governance-risk, type:qa, priority:high
Depends on: SRA-004, SRA-005, SRA-008

Description:
Add integration tests for core sprint 1 APIs.

Acceptance Criteria:
1. Test suite validates happy path and failure cases.
2. CI command and local command documented.
3. Tests are deterministic with seed data.

---

### SRA-010 - Add schema: promoter_snapshots, insider_trades, news_articles, news_signals

Labels: track:data-platform, type:data, priority:critical
Depends on: SRA-009

Description:
Create DB schema and indexes for ownership and news intelligence.

Acceptance Criteria:
1. Alembic migration added with rollback.
2. Indexes support symbol/date lookups.
3. Data retention policy defined.

---

### SRA-011 - Build promoter holdings ingestion job

Labels: track:data-platform, type:data, priority:high
Depends on: SRA-010

Description:
Ingest promoter holding snapshots into normalized schema.

Acceptance Criteria:
1. Source connector implemented.
2. Upsert strategy handles duplicates.
3. Ingestion audit metrics logged.

---

### SRA-012 - Build insider transactions ingestion job

Labels: track:data-platform, type:data, priority:high
Depends on: SRA-010

Description:
Ingest insider buy/sell transactions with entity normalization.

Acceptance Criteria:
1. Historical backfill supported.
2. Data validation rules applied.
3. Daily incremental mode supported.

---

### SRA-013 - Build multi-source news ingestion job

Labels: track:data-platform, type:data, priority:high
Depends on: SRA-010

Description:
Ingest finance and policy news from multiple sources.

Acceptance Criteria:
1. Source adapters implemented with dedupe by canonical URL/hash.
2. Publish time normalization and timezone handling present.
3. Fallback handling for source outages implemented.

---

### SRA-014 - Build NLP enrichment pipeline (entity, sentiment, event tagging)

Labels: track:ai-intelligence, type:ml, priority:critical
Depends on: SRA-013

Description:
Create enrichment pipeline that converts raw news into model-ready signals.

Acceptance Criteria:
1. Entity extraction links articles to listings and sectors.
2. Sentiment and event tags generated with confidence scores.
3. At least 90% of valid articles produce enrichment output.

---

### SRA-015 - Implement ownership and news APIs for stock detail

Labels: track:data-platform, type:backend, priority:high
Depends on: SRA-011, SRA-012, SRA-014

Description:
Expose stock intelligence APIs.

Acceptance Criteria:
1. GET /api/v1/stocks/{symbol}/ownership returns latest ownership timeline.
2. GET /api/v1/stocks/{symbol}/news returns relevance-ranked enriched articles.
3. API validation, pagination, and caching behavior documented.

---

### SRA-016 - Add stock detail intelligence panels (ownership and news)

Labels: track:data-platform, type:frontend, priority:high
Depends on: SRA-006, SRA-015

Description:
Integrate ownership and news insights in stock detail view.

Acceptance Criteria:
1. Ownership trend panel and news feed panel render from live API.
2. Empty and stale data states handled clearly.
3. Clicking article opens source link safely.

---

### SRA-017 - Add data freshness SLAs and monitoring checks

Labels: track:governance-risk, type:infra, priority:high
Depends on: SRA-011, SRA-012, SRA-013

Description:
Add freshness checks and alerts for all critical datasets.

Acceptance Criteria:
1. SLA thresholds defined per dataset.
2. Daily freshness checks run automatically.
3. Breach status visible in jobs or dashboard endpoint.

---

### SRA-018 - Add feature store schema and daily feature snapshot pipeline

Labels: track:ai-intelligence, type:data, priority:critical
Depends on: SRA-015, SRA-017

Description:
Build persistent feature snapshots for model training and inference.

Acceptance Criteria:
1. feature_snapshots schema and write pipeline added.
2. Feature versioning included.
3. Reproducible snapshot by date is possible.

---

### SRA-019 - Implement hybrid scoring engine v1

Labels: track:ai-intelligence, type:ml, priority:critical
Depends on: SRA-018

Description:
Compute combined score from technical, ownership, news, and regime features.

Acceptance Criteria:
1. Weighted scoring config is externalized.
2. Per-component score breakdown is persisted.
3. Scoring run can process target universe within SLA.

---

### SRA-020 - Implement recommendation APIs

Labels: track:ai-intelligence, type:backend, priority:high
Depends on: SRA-019

Description:
Expose recommendation list and symbol-level recommendation endpoints.

Acceptance Criteria:
1. GET /api/v1/recommendations supports filters and horizon.
2. GET /api/v1/recommendations/{symbol} returns latest action and confidence.
3. API contracts documented in Swagger.

---

### SRA-021 - Add explainability and evidence payload for recommendations

Labels: track:ai-intelligence, type:backend, priority:high
Depends on: SRA-020

Description:
Attach reason codes and evidence links to each recommendation.

Acceptance Criteria:
1. Response includes top drivers and confidence trace.
2. Evidence references source rows or articles.
3. Explainability payload stored for audits.

---

### SRA-022 - Add walk-forward validation pipeline

Labels: track:ai-intelligence, type:ml, priority:high
Depends on: SRA-019

Description:
Evaluate model robustness with rolling train/test windows.

Acceptance Criteria:
1. Walk-forward report generated by run date.
2. Includes drawdown, Sharpe, Sortino, and hit-rate by window.
3. Result is archived and comparable to prior runs.

---

### SRA-023 - Add benchmark comparison report vs baseline screeners

Labels: track:portfolio-execution, type:backend, priority:high
Depends on: SRA-022

Description:
Compare AI strategy against baseline screeners and benchmark indices.

Acceptance Criteria:
1. Report includes alpha, CAGR, drawdown, and turnover.
2. Costs and slippage included in net returns.
3. Result exported in machine-readable format.

---

### SRA-024 - Add paper trading schema (accounts, orders, fills, snapshots)

Labels: track:portfolio-execution, type:data, priority:critical
Depends on: SRA-023

Description:
Create persistence layer for paper brokerage lifecycle.

Acceptance Criteria:
1. Alembic migration with indexes and FK integrity.
2. Snapshot model supports equity-curve reconstruction.
3. Seed script creates initial paper account.

---

### SRA-025 - Implement paper execution simulator (slippage, partial fills, rejection)

Labels: track:portfolio-execution, type:backend, priority:critical
Depends on: SRA-024

Description:
Simulate realistic execution behavior for paper trading.

Acceptance Criteria:
1. Fill engine supports full, partial, and rejected outcomes.
2. Slippage model configurable by liquidity and volatility.
3. Every fill stores fee and slippage breakdown.

---

### SRA-026 - Implement paper trading APIs

Labels: track:portfolio-execution, type:backend, priority:high
Depends on: SRA-025

Description:
Expose APIs for placing paper orders and viewing positions/performance.

Acceptance Criteria:
1. POST /api/v1/paper/orders validates risk checks before submission.
2. GET /api/v1/paper/positions returns live position snapshot.
3. GET /api/v1/paper/performance returns net metrics.

---

### SRA-027 - Implement risk engine controls (position, sector, daily loss, kill switch)

Labels: track:governance-risk, type:backend, priority:critical
Depends on: SRA-002, SRA-026

Description:
Enforce hard risk limits in order flow.

Acceptance Criteria:
1. Risk check failures block order placement.
2. Kill switch halts new orders and logs reason.
3. Breach events are queryable in audit logs.

---

### SRA-028 - Implement PnL, attribution, and cost-aware performance reports

Labels: track:portfolio-execution, type:backend, priority:high
Depends on: SRA-026

Description:
Calculate and expose performance attribution after all costs.

Acceptance Criteria:
1. Realized and unrealized PnL separated.
2. Fees, taxes, and slippage reported explicitly.
3. Daily and cumulative metrics available by strategy.

---

### SRA-029 - Build paper trading dashboard page

Labels: track:portfolio-execution, type:frontend, priority:high
Depends on: SRA-026, SRA-028

Description:
Add frontend page for paper account, positions, and performance.

Acceptance Criteria:
1. Account equity, drawdown, and open positions visible.
2. Orders and fills table with status filters.
3. Error/loading/empty states fully handled.

---

### SRA-030 - Add end-to-end paper replay tests

Labels: track:governance-risk, type:qa, priority:high
Depends on: SRA-027, SRA-029

Description:
Run deterministic replay tests from recommendation to order and fill.

Acceptance Criteria:
1. Replay suite validates risk blocks and normal flow.
2. Snapshot outcomes are reproducible across runs.
3. Regression thresholds alert on drift.

---

### SRA-031 - Add intraday schema and ingestion pipeline

Labels: track:intraday, type:data, priority:critical
Depends on: SRA-030

Description:
Store intraday bars and support incremental updates.

Acceptance Criteria:
1. intraday_prices schema with indexes by listing_id and timestamp.
2. Configurable intervals with validation.
3. Backfill and incremental modes available.

---

### SRA-032 - Implement intraday signal engine (breakout and VWAP pullback)

Labels: track:intraday, type:ml, priority:high
Depends on: SRA-031

Description:
Generate intraday signals under strict liquidity and volatility filters.

Acceptance Criteria:
1. Two strategies implemented with config-driven params.
2. Signals include confidence and rationale fields.
3. Signal generation latency within defined SLA.

---

### SRA-033 - Implement intraday session APIs

Labels: track:intraday, type:backend, priority:high
Depends on: SRA-032

Description:
Expose APIs to run and inspect intraday sessions.

Acceptance Criteria:
1. POST /api/v1/intraday/run-session starts a run.
2. GET /api/v1/intraday/signals returns latest signal stream.
3. GET /api/v1/intraday/session/{id} returns session-level results.

---

### SRA-034 - Implement intraday risk controls and session limits

Labels: track:intraday, type:backend, priority:critical
Depends on: SRA-027, SRA-033

Description:
Enforce intraday-specific risk constraints.

Acceptance Criteria:
1. Max trades/day and max daily loss limits enforced.
2. Time-of-day trading windows validated.
3. Auto-stop on breach with event logging.

---

### SRA-035 - Build intraday monitoring dashboard

Labels: track:intraday, type:frontend, priority:high
Depends on: SRA-033, SRA-034

Description:
Display intraday status, signals, fills, and risk events.

Acceptance Criteria:
1. Session PnL and drawdown widgets present.
2. Risk alert feed visible in UI.
3. Session history and drill-down available.

---

### SRA-036 - Produce intraday evaluation report and stability gate

Labels: track:intraday, type:qa, priority:high
Depends on: SRA-035

Description:
Evaluate intraday paper results and define pass/fail gate.

Acceptance Criteria:
1. Report includes win rate, payoff, drawdown, and slippage quality.
2. Failing strategies are disabled by default.
3. Stability gate result published for promotion review.

---

### SRA-037 - Build promotion gate dashboard for paper-to-live decision

Labels: track:governance-risk, type:frontend, priority:critical
Depends on: SRA-023, SRA-036

Description:
Create decision dashboard for live readiness.

Acceptance Criteria:
1. All non-negotiable gates displayed with pass/fail state.
2. Trend charts for alpha, drawdown, Sharpe, Sortino.
3. Drill-down links to source reports.

---

### SRA-038 - Implement broker adapter framework and dry-run live mode

Labels: track:portfolio-execution, type:backend, priority:critical
Depends on: SRA-037

Description:
Add production broker adapter framework that reuses paper interfaces.

Acceptance Criteria:
1. Broker adapter contract is stable and test-covered.
2. Dry-run mode sends no real orders.
3. Live adapter feature flag is disabled by default.

---

### SRA-039 - Add trading mode switch with live safeguards

Labels: track:governance-risk, type:infra, priority:critical
Depends on: SRA-038

Description:
Introduce explicit mode switch and safety checks for live mode.

Acceptance Criteria:
1. Mode can be PAPER or LIVE via secure config.
2. LIVE mode blocked unless gates are green.
3. Startup checks fail fast on unsafe configuration.

---

### SRA-040 - Write operational runbooks and incident playbooks

Labels: track:governance-risk, type:infra, priority:high
Depends on: SRA-039

Description:
Document operating procedures for normal and emergency scenarios.

Acceptance Criteria:
1. Runbooks for startup, shutdown, rollback, and recovery.
2. Incident playbooks for data failures and trading anomalies.
3. On-call checklist and escalation path documented.

---

### SRA-041 - Run final UAT and go/no-go review

Labels: track:governance-risk, type:qa, priority:critical
Depends on: SRA-040

Description:
Conduct full-system acceptance testing and decision review.

Acceptance Criteria:
1. UAT checklist completed with evidence links.
2. Go/no-go decision recorded with sign-off.
3. Open critical defects are zero.

---

### SRA-042 - Release v1 and enable post-launch monitoring

Labels: track:governance-risk, type:infra, priority:critical
Depends on: SRA-041

Description:
Cut v1 release and activate post-launch KPIs and alerts.

Acceptance Criteria:
1. Release notes and version tag created.
2. Monitoring dashboards and alerts active.
3. First 2-week post-launch report template ready.
