# Stock Research Agent
Current Status (Completed)

✅ NSE company universe imported
✅ Historical prices downloaded
✅ Technical indicators calculated
✅ Momentum screener implemented
✅ Results persistence implemented

Current Database Size:
- daily_prices: 2,363,884 rows
- technical_indicators: 2,363,820 rows
- screener_results: 100 Momentum rankings


## Project Vision

The goal of this project is to build a complete stock research and screening platform capable of identifying investment opportunities for:

* Long-term investing
* Swing trading
* Position trading
* Intraday trading (future phase)

The project is designed as a data-first platform. Instead of relying on third-party screeners, all market data, indicators, rankings, and screening logic are generated and stored within our own PostgreSQL database.

The long-term objective is to build an intelligent stock-selection engine that combines:

* Technical Analysis
* Fundamental Analysis
* Market Breadth
* Sector Rotation
* News and Sentiment
* AI-based Ranking and Explanation

The current system focuses on building a strong technical-analysis foundation before moving into fundamentals and AI.

---

# Current Architecture

## Data Layer

### Companies

Stores the master company information.

Fields:

* Company ID
* Company Name
* ISIN
* Sector (future)
* Industry (future)

Purpose:

A company exists only once regardless of the exchange on which it trades.

---

### Listings

Stores exchange-specific information.

Fields:

* Listing ID
* Company ID
* Exchange
* Symbol
* Yahoo Symbol

Examples:

* TCS → NSE:TCS
* TCS → BSE:532540

Purpose:

Allows support for multiple exchanges while keeping a single company record.

---

### Daily Prices

Stores historical market data.

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

Yahoo Finance

Coverage:

Approximately 5 years of historical data for the NSE universe.

---

### Technical Indicators

Stores calculated technical indicators.

Fields:

* Listing ID
* Trade Date
* SMA20
* SMA50
* SMA200
* RSI14

Current Size:

* 2,363,820 rows

Purpose:

Allows fast screening without recalculating indicators repeatedly.

---

### Screener Results

Stores outputs from various screeners.

Fields:

* Screener Name
* Listing ID
* Trade Date
* Score

Current Use:

Momentum Screener

Purpose:

Acts as a cache layer for ranked stocks.

---

# Data Ingestion Pipeline

## Company Import

Source:

NSE Equity Master CSV

Imported:

* Company Name
* Symbol
* ISIN

Result:

Approximately 2164 companies loaded.

---

## Historical Price Download

Source:

Yahoo Finance

Process:

1. Read all listings.
2. Download historical data.
3. Store into daily_prices.
4. Handle failures separately.

Results:

* 2364 listings processed.
* 40 failures.
* 98%+ success rate.

Total Download Time:

~47 minutes.

---

## Indicator Calculation

Indicators Calculated:

* SMA20
* SMA50
* SMA200
* RSI14

Method:

1. Load prices for one stock.
2. Calculate indicators using Python.
3. Bulk insert results into PostgreSQL.

Coverage:

* 2359 listings.
* 2.36 million indicator records.

---

# Current Screening Engine

## Momentum Screener

Current Formula:

Momentum Score =
40% × 3-Month Return +
60% × 6-Month Return

Filters:

* Minimum history = 126 trading days
* Current price > ₹20
* Price 6 months ago > ₹20

Output:

Top 100 stocks stored in screener_results.

Purpose:

Identify stocks with the strongest medium-term price appreciation.

---

# What Has Been Achieved

The project has successfully moved beyond simple data collection.

We now have:

* Historical price database
* Technical indicator engine
* Momentum ranking engine
* Persistent screener results

This allows us to generate stock candidates directly from our own database without relying on external screening websites.

---

# Next Development Targets

## Phase 1 – Advanced Technical Screening

### Strong Uptrend Screener

Conditions:

* Close > SMA20
* SMA20 > SMA50
* SMA50 > SMA200
* RSI > 60

Goal:

Identify stocks in confirmed uptrends.

---

### Golden Cross Screener

Condition:

SMA50 > SMA200

Goal:

Identify long-term trend reversals.

---

### 52 Week High Screener

Condition:

Price within 5% of 52-week high.

Goal:

Identify potential breakout candidates.

---

### Oversold Screener

Condition:

RSI < 30

Goal:

Identify potential recovery candidates.

---

### Relative Strength Ranking

Rank stocks using:

* 3 Month Return
* 6 Month Return
* 12 Month Return

Goal:

Create market-wide strength rankings.

---

## Phase 2 – Market Snapshot Layer

Create a consolidated snapshot containing one row per stock.

Fields:

* Symbol
* Company Name
* Close Price
* SMA20
* SMA50
* SMA200
* RSI14
* 3M Return
* 6M Return
* Momentum Score

Purpose:

Allow all screeners to run against a single optimized dataset.

---

## Phase 3 – Fundamental Analysis

New Tables:

* annual_financials
* quarterly_financials
* balance_sheet
* cash_flow
* shareholding_pattern

Metrics:

* ROE
* ROCE
* Debt/Equity
* Revenue Growth
* Profit Growth
* Earnings Growth
* Free Cash Flow

Goal:

Build a quality ranking engine.

---

## Phase 4 – Combined Ranking Engine

Combine:

Technical Score

* Momentum
* Trend
* Relative Strength

Fundamental Score

* ROE
* ROCE
* Growth
* Debt

Output:

Unified Stock Score

Goal:

Generate a ranked investment universe.

---

## Phase 5 – AI Layer

AI will not choose stocks directly.

Instead it will:

* Explain rankings
* Identify strengths
* Identify risks
* Summarize company performance
* Explain why a stock appears in a screener

Goal:

AI becomes an analyst rather than a decision maker.

---

# Long-Term Vision

The final system should function as a complete stock intelligence platform capable of:

* Data Collection
* Technical Analysis
* Fundamental Analysis
* Ranking
* Screening
* Backtesting
* AI-Based Research Assistance

The database and ranking engine are the core assets of the platform. AI serves as an enhancement layer on top of a reliable and independently maintained market data infrastructure.
