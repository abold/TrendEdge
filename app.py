import streamlit as st, yfinance as yf
from datetime import date
from src.signals import ma_signals
from src.backtest import run_backtest
from src.metrics import cagr, sharpe, max_drawdown
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="TrendEdge — MA Backtester", page_icon="📈", layout="wide")
st.title("TrendEdge — Moving Average Strategy Backtester")
st.caption("Visualise MA crossover signals and compare strategy vs. buy & hold.")

# ---------- Helpers ----------
@st.cache_data(show_spinner=False, ttl=60*30)  # cache for 30 minutes
def fetch_prices(ticker: str, start: date | None, end: date | None) -> pd.Series:
    if start and end and start >= end:
        return pd.Series(dtype=float)
    data = yf.download(ticker, start=start, end=end) if start or end else yf.download(ticker, period="max")
    if data is None or data.empty or "Adj Close" not in data.columns:
        return pd.Series(dtype=float)
    return data["Adj Close"].dropna()

def validate_params(fast: int, slow: int) -> list[str]:
    errs = []
    if fast < 1 or slow < 1:
        errs.append("MA window lengths must be positive integers.")
    if fast >= slow:
        errs.append("Fast MA must be **strictly smaller** than Slow MA.")
    if slow > 500:
        errs.append("Slow MA is too large (>500) for most symbols.")
    return errs

# ---------- Controls ----------
with st.sidebar:
    st.header("Parameters")
    ticker = st.text_input("Ticker", "SPY").strip().upper()
    fast   = st.number_input("Fast MA", min_value=1, max_value=400, value=20, step=1)
    slow   = st.number_input("Slow MA", min_value=2, max_value=800, value=50, step=1)
    colA, colB = st.columns(2)
    start  = colA.date_input("Start date", value=None, help="Leave empty for max history")
    end    = colB.date_input("End date", value=None, help="Optional — leave empty for today")
    run = st.button("▶️ Run backtest", use_container_width=True)

# ---------- Run ----------
if run:
    # Validate inputs
    errors = validate_params(int(fast), int(slow))
    if errors:
        for e in errors: st.error(e)
        st.stop()

    px = fetch_prices(ticker, start if start else None, end if end else None)
    if px.empty:
        st.error("No data found for that ticker/date range.")
        st.stop()

    # Ensure enough data to compute MAs
    if len(px) < max(int(fast), int(slow)) + 5:
        st.warning("Not enough data after the chosen start/end to compute both moving averages.")
        st.stop()

    sig = ma_signals(px, int(fast), int(slow))
    res = run_backtest(px, sig)

    # ---------- Charts ----------
    left, right = st.columns(2)

    with left:
        st.subheader("Price & Moving Averages")
        fig1, ax1 = plt.subplots()
        ax1.plot(px.index, px.values, label=f"{ticker} Price")
        ax1.plot(px.index, px.rolling(int(fast)).mean(), label=f"MA{int(fast)}")
        ax1.plot(px.index, px.rolling(int(slow)).mean(), label=f"MA{int(slow)}")
        ax1.legend()
        st.pyplot(fig1, clear_figure=True)

    with right:
        st.subheader("Equity Curves")
        fig2, ax2 = plt.subplots()
        ax2.plot(res.index, res["eq_strategy"], label="Strategy")
        ax2.plot(res.index, res["eq_buyhold"], label="Buy & Hold")
        ax2.legend()
        st.pyplot(fig2, clear_figure=True)

    # ---------- Metrics ----------
    mdd_val, dd_series = max_drawdown(res["eq_strategy"])
    kpis = {
        "CAGR (Strategy)": f"{cagr(res['eq_strategy']):.2%}",
        "CAGR (Buy & Hold)": f"{cagr(res['eq_buyhold']):.2%}",
        "Sharpe (Strategy)": f"{sharpe(res['ret_strategy']):.2f}",
        "Max Drawdown (Strategy)": f"{mdd_val:.2%}",
    }
    st.subheader("Key Metrics")
    st.write(kpis)

    # ---------- Downloads ----------
    st.subheader("Downloads")
    # Package results into a single DataFrame
    out = res.copy()
    out["signal"] = sig.reindex(res.index).fillna(0).astype(int)
    csv_bytes = out.to_csv(index=True).encode("utf-8")
    st.download_button(
        label="⬇️ Download results (CSV)",
        data=csv_bytes,
        file_name=f"trendedge_{ticker}_{fast}_{slow}.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ---------- Notes & Disclaimer ----------
    with st.expander("Notes & Disclaimer"):
        st.markdown(
            """
- Signals use **next-day execution** (`signal.shift(1)`), i.e., trade on the bar after the crossover.
- Transaction costs, slippage, and taxes **are not included**.
- Past performance does **not** guarantee future results. Educational use only.
            """
        )

else:
    st.info("Set parameters in the sidebar and click **Run backtest**.")
