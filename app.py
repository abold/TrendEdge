import streamlit as st, yfinance as yf
from src.signals import ma_signals
from src.backtest import run_backtest
from src.metrics import cagr, sharpe, max_drawdown
import matplotlib.pyplot as plt

st.set_page_config(page_title="TrendEdge — MA Backtester", page_icon="📈", layout="wide")
st.title("TrendEdge — Moving Average Strategy Backtester")
st.caption("Visualise MA crossover signals and compare strategy vs. buy & hold.")

col1, col2, col3 = st.columns(3)
ticker = col1.text_input("Ticker", "SPY")
fast   = col2.number_input("Fast MA", 5, 200, 20)
slow   = col3.number_input("Slow MA", 10, 400, 50)
start  = st.date_input("Start date", value=None, help="Leave empty for max history")

if st.button("Run backtest"):
    data = yf.download(ticker, period="max" if not start else None, start=start)
    if data.empty:
        st.error("No data found for that ticker/date range.")
        st.stop()
    px = data["Adj Close"].dropna()
    sig = ma_signals(px, fast, slow)
    res = run_backtest(px, sig)

    st.subheader("Price & Moving Averages")
    fig1, ax1 = plt.subplots()
    ax1.plot(px.index, px.values, label="Price")
    ax1.plot(px.index, px.rolling(fast).mean(), label=f"MA{fast}")
    ax1.plot(px.index, px.rolling(slow).mean(), label=f"MA{slow}")
    ax1.legend(); st.pyplot(fig1)

    st.subheader("Equity Curves")
    fig2, ax2 = plt.subplots()
    ax2.plot(res.index, res["eq_strategy"], label="Strategy")
    ax2.plot(res.index, res["eq_buyhold"], label="Buy & Hold")
    ax2.legend(); st.pyplot(fig2)

    mdd_val, dd_series = max_drawdown(res["eq_strategy"])
    kpis = {
        "CAGR (Strategy)": f"{cagr(res['eq_strategy']):.2%}",
        "CAGR (Buy&Hold)": f"{cagr(res['eq_buyhold']):.2%}",
        "Sharpe (Strategy)": f"{sharpe(res['ret_strategy']):.2f}",
        "Max Drawdown (Strategy)": f"{mdd_val:.2%}",
    }
    st.subheader("Key Metrics")
    st.write(kpis)
