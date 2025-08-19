import streamlit as st
import yfinance as yf
from datetime import date
import pandas as pd

# your domain logic
from src.signals import ma_signals
from src.backtest import run_backtest
from src.metrics import cagr, sharpe, max_drawdown

# theming + charts
from utils.theming import apply_base_css, PALETTE
import plotly.graph_objects as go

# ------------------ App setup ------------------
st.set_page_config(page_title="TrendEdge — MA Backtester", page_icon="📈", layout="wide")
st.sidebar.markdown("### TrendEdge")
st.sidebar.markdown('<span class="pill">v0.1</span>', unsafe_allow_html=True)

st.title("TrendEdge — Moving Average Strategy Backtester")
st.caption("Visualise MA crossover signals and compare strategy vs. buy & hold.")
#st.sidebar.write("Theme base:", st.get_option("theme.base"))
apply_base_css()
# ------------------ Helpers ------------------
@st.cache_data(show_spinner=False, ttl=60*30)
def fetch_prices(ticker: str, start: date | None, end: date | None) -> tuple[pd.Series, str | None]:
    """Return a price series and an optional error string."""
    try:
        # Normalize empty dates to None
        start = start or None
        end   = end or None

        # Use auto_adjust=True and fall back: Adj Close -> Close
        if start or end:
            df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False, threads=False)
        else:
            df = yf.download(ticker, period="max", auto_adjust=True, progress=False, threads=False)

        if df is None or df.empty:
            return pd.Series(dtype=float), "Empty dataframe from Yahoo (check ticker/dates/internet)."

        s = df["Adj Close"] if "Adj Close" in df.columns else df.get("Close")
        if s is None or s.dropna().empty:
            return pd.Series(dtype=float), "No Adj Close/Close column in response."

        return s.dropna(), None
    except Exception as e:
        return pd.Series(dtype=float), f"{type(e).__name__}: {e}"


def validate_params(fast: int, slow: int) -> list[str]:
    errs = []
    if fast < 1 or slow < 1:
        errs.append("MA window lengths must be positive integers.")
    if fast >= slow:
        errs.append("Fast MA must be **strictly smaller** than Slow MA.")
    if slow > 500:
        errs.append("Slow MA is too large (>500) for most symbols.")
    return errs

# ------------------ Controls ------------------
with st.sidebar:
    st.header("Parameters")
    ticker = st.text_input("Ticker", "SPY").strip().upper()
    fast   = st.number_input("Fast MA", min_value=1,  max_value=400, value=20, step=1)
    slow   = st.number_input("Slow MA", min_value=2,  max_value=800, value=50, step=1)
    colA, colB = st.columns(2)
    start  = colA.date_input("Start date", value=None, help="Leave empty for max history")
    end    = colB.date_input("End date", value=None, help="Optional — leave empty for today")
    run = st.button("▶️ Run backtest", use_container_width=True)

# ------------------ Run ------------------
if run:
    # Validate inputs
    errors = validate_params(int(fast), int(slow))
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    px, err = fetch_prices(ticker, start if start else None, end if end else None)
    if err or px.empty:
        st.error(f"No data found for that ticker/date range. {'' if err is None else 'Details: ' + err}")
        st.stop()

    # Ensure enough data to compute MAs
    if len(px) < max(int(fast), int(slow)) + 5:
        st.warning("Not enough data after the chosen start/end to compute both moving averages.")
        st.stop()

    with st.spinner("Running backtest…"):
        # Signals
        sig_df = ma_signals(px, int(fast), int(slow))

        # --- ensure Series ---
        # If px is a DataFrame, pick first col (or "Adj Close"/"Close" if you know the name)
        if isinstance(px, pd.DataFrame):
            if "Adj Close" in px.columns:
                px = px["Adj Close"]
            elif "Close" in px.columns:
                px = px["Close"]
            else:
                px = px.iloc[:, 0]

        # If signals is a DataFrame, pick the 'signal' col (or first col)
        if isinstance(sig_df, pd.DataFrame):
            if "signal" in sig_df.columns:
                sig = sig_df["signal"]
            else:
                sig = sig_df.iloc[:, 0]
        else:
            sig = sig_df


        # Backtest
        res = run_backtest(px, sig)


    # ------------------ Charts (Plotly) ------------------
    left, right = st.columns(2, gap="large")

    with left:
        st.subheader("Price & Moving Averages")
        ma_fast  = px.rolling(int(fast)).mean()
        ma_slow  = px.rolling(int(slow)).mean()

        fig1 = go.Figure()
        fig1.add_scatter(x=px.index, y=px, name=f"{ticker} Price",
                         line=dict(color=PALETTE['text'], width=2))
        fig1.add_scatter(x=px.index, y=ma_fast, name=f"MA {int(fast)}",
                         line=dict(color=PALETTE['accent'], width=2))
        fig1.add_scatter(x=px.index, y=ma_slow, name=f"MA {int(slow)}",
                         line=dict(color="#60a5fa", width=2))  # blue accent

        fig1.update_layout(height=420, margin=dict(l=30, r=20, t=10, b=30),
                           xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig1, use_container_width=True)

    with right:
        st.subheader("Equity Curves")
        fig2 = go.Figure()
        fig2.add_scatter(x=res.index, y=res["eq_strategy"], name="Strategy",
                         line=dict(color=PALETTE['accent'], width=3))
        fig2.add_scatter(x=res.index, y=res["eq_buyhold"], name="Buy & Hold",
                         line=dict(color="#9aa4b2", width=2, dash="dash"))  # muted gray
        fig2.update_layout(height=420, margin=dict(l=30, r=20, t=10, b=30),
                           xaxis_title="Date", yaxis_title="Equity")
        st.plotly_chart(fig2, use_container_width=True)

    # ------------------ Metrics ------------------
    mdd_val, dd_series = max_drawdown(res["eq_strategy"])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CAGR (Strategy)",  f"{cagr(res['eq_strategy']):.2%}")
    col2.metric("CAGR (Buy & Hold)", f"{cagr(res['eq_buyhold']):.2%}")
    col3.metric("Sharpe (Strategy)", f"{sharpe(res['ret_strategy']):.2f}")
    col4.metric("Max Drawdown",      f"{mdd_val:.2%}")

    st.divider()

    # ------------------ Downloads ------------------
    st.subheader("Downloads")
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

    # ------------------ Notes & Disclaimer ------------------
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

