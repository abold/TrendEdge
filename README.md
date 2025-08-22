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


