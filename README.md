# TrendEdge — Moving Average Strategy Backtester

Interactive Streamlit app to explore moving-average crossover strategies with clean visuals, key metrics, and CSV export.

**Live demo:** [trendedge.streamlit.app](https://trendedge.streamlit.app)  
**Code:** [github.com/abold/TrendEdge](https://github.com/abold/TrendEdge)

## Quickstart - if you want to run the app locally :rocket:
```bash
# 1) Create & activate a venv (Python 3.11 recommended)
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run the app
streamlit run app.py
```
**Features**
  - MA crossover signals with next-bar execution (no look-ahead).

  - Equity curves: Strategy vs Buy & Hold.

  - Metrics: CAGR, Sharpe, Max Drawdown.

  - Validated inputs and optional date range.

  - Price + MA overlay and candlestick chart.

  - Signals preview table (1 = long, 0 = flat).

  - Cached data downloads (faster reruns).

  - One-click CSV export of results.
 
  - (Optional prototype in the app: simple ML classifier for P(up next day).)

  - Notes & educational disclaimer included.
  



**Screenshots**
Main View
## Screenshots
![Main Screenshot](assets/trendedge.png)

**Each term is explained below:**
### CAGR — Compound Annual Growth Rate

**What it is:** The steady yearly rate that would turn your **starting equity** into your **ending equity** if growth were perfectly smooth.

**Why it matters:** Lets you compare strategies that ran for **different lengths of time** on the same scale (per year).

**Formula:**

**Example:** Start = 100, End = 150, Years = 3  
`CAGR = (150/100)^(1/3) − 1 ≈ 14.47%`

**How to read it:** Higher is better. Compare your **Strategy CAGR** vs **Buy-&-Hold CAGR** to judge value added.
- **CAGR:** annualized growth rate assuming smooth compounding; makes runs of different lengths comparable.
## CAGR — Strategy vs. Buy & Hold

**Strategy CAGR:** Annualized growth of the **strategy’s equity curve** (`eq_strategy`).  
Reflects being in/out of the market per the moving-average signals, with **next-bar execution** and **no fees/slippage**.

**Buy-&-Hold CAGR:** Annualized growth if you **buy at the start and hold to the end** (`eq_buyhold`).  
Uses **Adjusted Close** when available (so dividends/splits are included).

**Why show both?**  
Puts the strategy’s return on the same per-year scale as a simple benchmark. If Strategy CAGR > Buy-&-Hold CAGR, the rules outperformed buy-and-hold over this date range (pair with Sharpe & Max Drawdown to judge risk).

**How it’s computed**
*Both curves are normalized to the same starting value so the comparison is fair.*

**Example**
- Start capital = 100  
- Strategy ends at 180 after 3.0 years → `CAGR_strategy = (180/100)^(1/3) − 1 ≈ 22.9%`  
- Buy-&-Hold ends at 150 after 3.0 years → `CAGR_bh = (150/100)^(1/3) − 1 ≈ 14.5%`

**Notes**
- Same ticker and date range for both.
- Strategy is flat (0% return) when out of the market.
- Transaction costs, slippage, and taxes are **not** included (educational use).
