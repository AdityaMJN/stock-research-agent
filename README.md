# Stock Research Agent

## Overview

Stock Research Agent is a data-driven stock screening, ranking, and research platform built around a PostgreSQL market database and a Python analytics engine.

The project is designed to maintain its own market data infrastructure rather than relying on external screening websites. All indicators, screeners, rankings, and backtests are generated from internally stored historical data.

The long-term vision is to evolve the platform into a complete stock intelligence system capable of:

* Technical Analysis
* Fundamental Analysis
* Market Breadth Analysis
* Sector Rotation Analysis
* Backtesting
* Portfolio Research
* AI-Assisted Investment Research

---

# Current Status

## Data Layer

### Companies

Stores master company information.

Current Records:

* ~2164 NSE companies

### Listings

Stores exchange-specific trading information.

Current Records:

* ~2364 listings

### Daily Prices

Stores historical OHLCV data.

Fields:

* Listing ID
* Trade Date
* Open
* High
* Low
* Close
* Adjusted Close
* Volume

Current Size:

* 2,363,884 rows

Data Source:

* Yahoo Finance

Coverage:

* Approximately 5 years of historical data

### Technical Indicators

Stores calculated technical indicators.

Indicators:

* SMA20
* SMA50
* SMA200
* RSI14

Current Size:

* 2,363,820 rows

Coverage:

* ~2359 actively calculated listings

### Screener Results

Stores ranked screener outputs.

Fields:

* Screener Name
* Listing ID
* Trade Date
* Score
* Created At

Purpose:

Acts as a cached ranking layer for stock selection.

---

# Architecture

```text
Companies
    ↓
Listings
    ↓
Daily Prices
    ↓
Technical Indicators
    ↓
Views
    ├── latest_stock_snapshot
    ├── stock_52w_stats
    └── golden_cross_candidates
    ↓
Screeners
    ├── Momentum
    ├── Strong Uptrend
    ├── 52 Week High
    └── Golden Cross
    ↓
Combined Ranking
    ↓
Backtesting
```

---

# Data Ingestion Pipeline

## NSE Universe Import

Source:

* NSE Equity Master List

Imported Data:

* Company Name
* Symbol
* ISIN

Result:

* ~2164 companies imported

---

## Historical Price Import

Source:

* Yahoo Finance

Process:

1. Load listings
2. Download historical data
3. Store in daily_prices
4. Skip duplicates automatically

Result:

* ~2364 listings processed
* ~98% success rate

---

## Daily Incremental Price Update

Implemented:

```text
ingestion/daily_price_update.py
```

Features:

* Detects latest stored trade date
* Downloads only missing data
* Avoids duplicate inserts
* Suitable for daily automation

---

# Technical Indicator Engine

Implemented Indicators:

* SMA20
* SMA50
* SMA200
* RSI14

Files:

```text
calculations/
├── calculate_all_indicators.py
└── update_indicators.py
```

### Full Rebuild

```text
calculate_all_indicators.py
```

Recalculates the entire indicator database.

### Incremental Update

```text
update_indicators.py
```

Updates only newly available indicator records.

Used by the daily pipeline.

---

# Database Views

## latest_stock_snapshot

Provides one latest row per stock containing:

* Close Price
* SMA20
* SMA50
* SMA200
* RSI14

Purpose:

Fast screening layer.

---

## stock_52w_stats

Provides:

* 52 Week High

Purpose:

Used by breakout screeners.

---

## golden_cross_candidates

Provides:

* Historical SMA50 / SMA200 crossover events

Purpose:

Used by Golden Cross screening.

---

# Screening Engine

## Momentum Screener

Measures medium-term price strength.

Scoring:

```text
40% × 3 Month Return
60% × 6 Month Return
```

Output:

* Top 100 stocks

Purpose:

Identify stocks with strongest momentum.

---

## Strong Uptrend Screener

Conditions:

```text
Close > SMA20
SMA20 > SMA50
SMA50 > SMA200
RSI14 > 60
```

Current Results:

* ~180 stocks

Purpose:

Identify established uptrends.

---

## 52 Week High Screener

Condition:

```text
Close >= 95% of 52 Week High
```

Current Results:

* ~165 stocks

Purpose:

Identify breakout candidates and market leaders.

---

## Golden Cross Screener

Condition:

```text
Yesterday:
SMA50 <= SMA200

Today:
SMA50 > SMA200
```

Purpose:

Identify emerging long-term uptrends.

---

# Combined Ranking Engine

The platform combines multiple independent signals.

Current Weighting:

```text
Momentum            35
Strong Uptrend      30
52 Week High        20
Golden Cross        15
----------------------
Maximum Score      100
```

Output:

```text
COMBINED_RANKING
```

Purpose:

Generate a ranked list of the strongest stocks in the market.

---

# Daily Automation Pipeline

Implemented:

```text
jobs/daily_update.py
```

Single Command:

```bash
python -m jobs.daily_update
```

Pipeline:

```text
Update Prices
    ↓
Update Indicators
    ↓
Momentum Screener
    ↓
Strong Uptrend Screener
    ↓
52 Week High Screener
    ↓
Golden Cross Screener
    ↓
Combined Ranking
```

---

# Backtesting Framework

Implemented:

```text
backtesting/
├── utils.py
└── backtest_strong_uptrend.py
```

Purpose:

Validate whether screening strategies actually outperform over historical periods.

## First Backtest Results

Strategy:

* Strong Uptrend
* Top 20 Stocks
* Monthly Rebalance
* 90 Day Holding Period

Results:

```text
Periods Tested : 23
Average Return : 28.04%
Median Return  : 26.78%
Best Return    : 113.52%
Worst Return   : -28.83%
Win Rate       : 91.30%
```

Note:

These results are preliminary and require additional validation against survivorship bias and other backtesting artifacts.

---

# Current Project Milestones

Completed:

* NSE Universe Import
* Historical Price Database
* Daily Price Updater
* Technical Indicator Engine
* Momentum Screener
* Strong Uptrend Screener
* 52 Week High Screener
* Golden Cross Screener
* Combined Ranking Engine
* Daily Automated Pipeline
* Backtesting Framework V1

---

# Next Development Targets

## Phase 1 – Backtesting Expansion

* Momentum Backtest
* 52 Week High Backtest
* Combined Ranking Backtest
* CAGR Calculation
* Drawdown Analysis
* Benchmark Comparison
* Equity Curve Generation

---

## Phase 2 – Fundamental Data Layer

New Data Sources:

* Financial Statements
* Balance Sheets
* Cash Flows
* Shareholding Patterns

Metrics:

* ROE
* ROCE
* Debt/Equity
* Revenue Growth
* Profit Growth
* Earnings Growth
* Free Cash Flow

---

## Phase 3 – Technical + Fundamental Ranking

Combine:

Technical Score

* Momentum
* Trend
* Breakout Strength

Fundamental Score

* Quality
* Growth
* Valuation

Output:

* Unified Stock Score

---

## Phase 4 – AI Research Layer

AI will assist by:

* Explaining rankings
* Summarizing companies
* Identifying strengths
* Highlighting risks
* Generating research reports

AI acts as a research assistant, not a decision maker.

---

# Long-Term Vision

The final platform will function as a complete stock intelligence system capable of:

* Market Data Collection
* Technical Analysis
* Fundamental Analysis
* Screening
* Ranking
* Backtesting
* Portfolio Research
* AI-Assisted Stock Research

The core asset of the platform is the proprietary market database, ranking engine, and research framework built entirely in-house.
