# Stock Research Agent - Execution Sprint Board

Last updated: 2026-11-17

## Mission

Build an AI-first stock research and trading platform that:

1. Maintains a local, high-quality market intelligence database.
2. Generates explainable recommendations from technical, fundamental, promoter, and news/event signals.
3. Supports positional and intraday paper trading for 2-3 months.
4. Transitions to live trading only after strict risk and performance gates are met.

## Non-Negotiable Gates

Paper-to-live promotion is allowed only if ALL conditions are true over a rolling 8-12 week period:

1. Positive net return after all costs and slippage.
2. Positive alpha vs benchmark (NIFTY 50 or chosen benchmark).
3. Max drawdown <= 10% (configurable).
4. Sharpe >= 1.2 and Sortino >= 1.5 (configurable).
5. No unresolved critical execution or data-quality incidents.
6. Intraday strategy pass rate and execution quality within limits.

## Program Tracks

1. Data Platform Track
2. AI Intelligence Track
3. Portfolio and Execution Track
4. Intraday Track
5. Governance, Risk, and Monitoring Track

## 12-Week Sprint Plan

## Sprint 1 (Weeks 1-2): Platform Hardening and API Completion

### Objectives

1. Replace static API payloads with database-backed responses.
2. Finalize roadmap baseline APIs for stock details and historical prices.
3. Strengthen job reliability and tests.

### Deliverables

1. Backend APIs:
   1. GET /api/v1/stocks
   2. GET /api/v1/stocks/{symbol}
   3. GET /api/v1/stocks/{symbol}/history?interval=1d&from=YYYY-MM-DD&to=YYYY-MM-DD
2. Frontend pages:
   1. /stocks list (existing, DB-backed)
   2. /stocks/:symbol detail page with core metrics
3. Jobs:
   1. Retry policy for failed jobs
   2. Structured job logs with run_id

### Data Model Additions

1. stock_profiles
   1. listing_id (fk)
   2. sector
   3. industry
   4. market_cap
   5. shares_outstanding
   6. updated_at
2. job_runs
   1. run_id
   2. job_name
   3. started_at
   4. ended_at
   5. status
   6. error_summary

### Acceptance Criteria

1. No hardcoded sample data in production API mode.
2. Stock detail page loads from backend for any valid symbol.
3. History endpoint serves candlestick-ready data with validation.
4. Integration tests pass for all new APIs.

## Sprint 2 (Weeks 3-4): Market Intelligence Data Layer

### Objectives

1. Ingest promoter/founder and ownership signals.
2. Ingest news from multiple sources.
3. Build event tagging and sentiment enrichment.

### Deliverables

1. Ingestion jobs:
   1. promoter_holdings_ingestion
   2. insider_trades_ingestion
   3. news_ingestion_multi_source
2. NLP pipeline:
   1. entity extraction (company, promoter, sector, policy)
   2. sentiment scoring
   3. event tagging
3. API:
   1. GET /api/v1/stocks/{symbol}/news
   2. GET /api/v1/stocks/{symbol}/ownership

### Data Model Additions

1. promoter_snapshots
   1. listing_id
   2. as_of_date
   3. promoter_holding_pct
   4. pledge_pct
2. insider_trades
   1. listing_id
   2. person_name
   3. txn_type
   4. quantity
   5. price
   6. txn_date
3. news_articles
   1. article_id
   2. source
   3. published_at
   4. title
   5. body
   6. url
4. news_signals
   1. article_id
   2. listing_id_nullable
   3. sentiment_score
   4. relevance_score
   5. event_type
   6. confidence

### Acceptance Criteria

1. Data freshness SLA defined and monitored for each source.
2. At least 90% of ingested articles receive sentiment + event tags.
3. Stock detail page shows latest ownership and top relevant news.

## Sprint 3 (Weeks 5-6): AI Recommendation Engine v1

### Objectives

1. Build explainable hybrid scoring engine.
2. Add recommendation API with confidence and rationale.
3. Persist model features and outputs for audit.

### Deliverables

1. Feature store tables and materialized views.
2. Scoring engine:
   1. technical_score
   2. ownership_score
   3. news_event_score
   4. regime_score
3. API:
   1. GET /api/v1/recommendations?universe=TOP500
   2. GET /api/v1/recommendations/{symbol}

### Data Model Additions

1. feature_snapshots
   1. listing_id
   2. trade_date
   3. feature_json
   4. feature_version
2. recommendation_snapshots
   1. listing_id
   2. trade_date
   3. horizon (intraday, swing, position)
   4. action (buy, hold, reduce, exit)
   5. confidence
   6. rationale_json
   7. model_version

### Acceptance Criteria

1. Every recommendation has explainability payload.
2. Offline walk-forward validation report generated.
3. Baseline model beats equal-weight screener baseline net of costs in backtest.

## Sprint 4 (Weeks 7-8): Paper Trading Simulator and Risk Engine

### Objectives

1. Run full paper brokerage simulation with realistic frictions.
2. Add portfolio risk controls and session limits.
3. Build PnL and attribution reporting.

### Deliverables

1. Simulator enhancements:
   1. slippage model
   2. partial fills
   3. order rejection states
2. Risk controls:
   1. max position size
   2. max sector exposure
   3. daily loss limit
   4. kill switch
3. APIs:
   1. POST /api/v1/paper/orders
   2. GET /api/v1/paper/positions
   3. GET /api/v1/paper/performance

### Data Model Additions

1. paper_accounts
   1. account_id
   2. cash_balance
   3. created_at
2. paper_orders
   1. order_id
   2. account_id
   3. listing_id
   4. side
   5. qty
   6. order_type
   7. status
   8. submitted_at
3. paper_fills
   1. fill_id
   2. order_id
   3. fill_price
   4. fill_qty
   5. fees
   6. slippage
   7. fill_time
4. portfolio_snapshots
   1. account_id
   2. snapshot_time
   3. cash
   4. equity
   5. total_value
   6. drawdown

### Acceptance Criteria

1. End-to-end paper execution is reproducible and auditable.
2. Performance report includes net returns after costs.
3. Risk limits enforce hard blocks on invalid orders.

## Sprint 5 (Weeks 9-10): Intraday Trading PoC

### Objectives

1. Add intraday market data storage and retrieval.
2. Implement 1-2 intraday strategies with strict limits.
3. Evaluate intraday paper performance and stability.

### Deliverables

1. Intraday ingestion jobs for selected universe.
2. Intraday strategy module:
   1. breakout with volume confirmation
   2. VWAP pullback variant
3. APIs:
   1. GET /api/v1/intraday/signals
   2. POST /api/v1/intraday/run-session
   3. GET /api/v1/intraday/session/{id}

### Data Model Additions

1. intraday_prices
   1. listing_id
   2. ts
   3. open
   4. high
   5. low
   6. close
   7. volume
   8. interval
2. intraday_signals
   1. listing_id
   2. ts
   3. strategy
   4. signal
   5. confidence
3. intraday_sessions
   1. session_id
   2. start_time
   3. end_time
   4. pnl
   5. max_drawdown

### Acceptance Criteria

1. Intraday strategy completes sessions without data or execution failures.
2. Session-level risk limits are never breached.
3. Performance and execution quality metrics are logged per session.

## Sprint 6 (Weeks 11-12): Promotion Review and Live-Readiness

### Objectives

1. Run formal paper-trading review for 2-3 month progression trajectory.
2. Validate live broker integration behind existing interface.
3. Prepare controlled live rollout checklist.

### Deliverables

1. Promotion dashboard:
   1. alpha
   2. drawdown
   3. Sharpe
   4. Sortino
   5. trade quality
2. Broker integration adapter (disabled by default).
3. Runbook:
   1. incident response
   2. stop-trading procedures
   3. rollback to paper mode

### Acceptance Criteria

1. Live mode remains locked unless all gates pass.
2. Live and paper share the same order abstraction.
3. Dry-run live execution tests pass in non-trading mode.

## API Contract Summary

### Core Research

1. GET /api/v1/stocks
2. GET /api/v1/stocks/{symbol}
3. GET /api/v1/stocks/{symbol}/history
4. GET /api/v1/stocks/{symbol}/news
5. GET /api/v1/stocks/{symbol}/ownership

### AI and Recommendations

1. GET /api/v1/recommendations
2. GET /api/v1/recommendations/{symbol}

### Paper Trading

1. POST /api/v1/paper/orders
2. GET /api/v1/paper/positions
3. GET /api/v1/paper/performance

### Intraday

1. GET /api/v1/intraday/signals
2. POST /api/v1/intraday/run-session
3. GET /api/v1/intraday/session/{id}

## Weekly Operating Cadence

1. Daily:
   1. Data freshness check
   2. Job failure review
   3. Risk breach review
2. Weekly:
   1. Model drift report
   2. Strategy attribution review
   3. Parameter and rule-change review
3. Monthly:
   1. Gate scorecard update
   2. Promotion readiness review

## Initial Task Queue for Next 10 Working Days

1. Implement GET /api/v1/stocks/{symbol} in backend.
2. Implement GET /api/v1/stocks/{symbol}/history in backend.
3. Create stock detail page /stocks/:symbol in frontend.
4. Add Alembic migration for stock_profiles and job_runs.
5. Add integration tests for stock detail and history endpoints.
6. Replace remaining static dashboard payload segments with DB-backed queries.
7. Finalize risk gate config file and defaults.

## Risk Warning

This plan reduces risk but cannot eliminate it. Market behavior is non-stationary and model performance can degrade quickly. Capital protection and strict risk controls must remain higher priority than return targets.
