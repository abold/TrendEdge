# app.py
import streamlit as st
import yfinance as yf
from datetime import date
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# theming
from utils.theming import apply_base_css, PALETTE

# domain logic
from src.signals import ma_signals
from src.backtest import run_backtest
from src.metrics import cagr, sharpe, max_drawdown


# ------------------ Page setup ------------------
st.set_page_config(
    page_title="TrendEdge — Backtesting Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_base_css()

# ------------------ Header ------------------
top_l, top_r = st.columns([1, 1])
with top_l:
    st.markdown('<span class="pill">Python · Streamlit</span>', unsafe_allow_html=True)
    st.title("TrendEdge")
    st.caption("Backtests, analytics, and research — mobile-friendly dashboard.")
with top_r:
    pass  # reserved for future profile/settings


# ------------------ Sidebar (Parameters) ------------------
with st.sidebar:
    st.header("Parameters")
    ticker = st.text_input("Ticker", "SPY").strip().upper()
    fast   = st.number_input("Fast MA", min_value=1, max_value=400, value=20, step=1)
    slow   = st.number_input("Slow MA", min_value=2, max_value=800, value=50, step=1)
    colA, colB = st.columns(2)
    start  = colA.date_input("Start date", value=None, help="Leave empty for max history")
    end    = colB.date_input("End date", value=None, help="Optional — leave empty for today")
    run = st.button("▶️ Run backtest", use_container_width=True)


# ------------------ Helpers ------------------
@st.cache_data(show_spinner=False, ttl=60*30)
def fetch_prices(ticker: str, start: date | None, end: date | None) -> tuple[pd.DataFrame, str | None]:
    """
    Return a DataFrame with whatever Yahoo gives among:
    Open, High, Low, Close, Adj Close, Volume.
    Robust to missing 'Adj Close' or 'Close'.
    """
    try:
        kw = dict(auto_adjust=False, progress=False, threads=False)
        if start or end:
            df = yf.download(ticker, start=start or None, end=end or None, **kw)
        else:
            df = yf.download(ticker, period="max", **kw)

        if df is None or df.empty:
            return pd.DataFrame(), "Empty dataframe from Yahoo (check ticker/dates/internet)."

        # keep only known columns that actually exist
        cols = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns]
        if not cols:
            return pd.DataFrame(), "No usable OHLC/Adj Close columns returned."
        df = df[cols].copy()

        # choose a 'close-like' series safely
        close_series = df.get("Adj Close", df.get("Close"))
        if close_series is None:
            return pd.DataFrame(), "No Close or Adj Close column returned."

        # drop rows where our chosen close is NaN (use its index to filter)
        df = df.loc[close_series.dropna().index]

        return df, None
    except Exception as e:
        return pd.DataFrame(), f"{type(e).__name__}: {e}"


def validate_params(fast: int, slow: int) -> list[str]:
    errs = []
    if fast < 1 or slow < 1:
        errs.append("MA window lengths must be positive integers.")
    if fast >= slow:
        errs.append("Fast MA must be strictly smaller than Slow MA.")
    if slow > 500:
        errs.append("Slow MA is too large (>500) for most symbols.")
    return errs


def plot_candles(df: pd.DataFrame, ticker: str, cols=None) -> go.Figure:
    """
    df: DataFrame with OHLC columns (any names or even MultiIndex flattened)
    """
    cols = cols or {}

    # robust column finder: works even if labels are tuples
    def pick(name: str):
        # explicit mapping takes priority
        if name in cols:
            return cols[name]
        # exact case-insensitive match
        for c in df.columns:
            if str(c).lower() == name:
                return c
        # substring match (e.g., "('Open','SPY')" -> 'open')
        for c in df.columns:
            if name in str(c).lower():
                return c
        return None

    open_col  = pick("open")
    high_col  = pick("high")
    low_col   = pick("low")
    close_col = pick("close")

    missing = [n for n, v in {"Open": open_col, "High": high_col, "Low": low_col, "Close": close_col}.items() if v is None]
    if missing:
        raise ValueError(f"plot_candles: missing columns: {', '.join(missing)}")

    fig = go.Figure([
        go.Candlestick(
            x=df.index,
            open=df[open_col],
            high=df[high_col],
            low=df[low_col],
            close=df[close_col],
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444",
            name=f"{ticker} OHLC",
        )
    ])
    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=30, r=20, t=10, b=30),
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
    )
    return fig

def flashy_metric(label, value, delta=None, color="violet"):
    """Render a styled metric with flashy colors (uses CSS classes defined in theming.py)."""
    st.markdown(
        f"""
        <div data-testid="stMetric">
          <div data-testid="stMetricLabel"><div>{label}</div></div>
          <div data-testid="stMetricValue"><div class="{color}">{value}</div></div>
          {f'<div data-testid="stMetricDelta">{delta}</div>' if delta else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------ Tabs (Dashboard layout) ------------------
tab_overview, tab_strategy, tab_research, tab_data, tab_settings = st.tabs(
    ["Overview", "Strategy", "Research (ML)", "Data", "Settings"]
)

# ------------------ Click to run ------------------
if not run:
    with tab_overview:
        st.info("Set parameters in the sidebar and click **Run backtest** to begin.")
else:
    # Validate inputs
    errors = validate_params(int(fast), int(slow))
    if errors:
        with tab_overview:
            for e in errors:
                st.error(e)
        st.stop()

    # Fetch data (DataFrame)
    data, err = fetch_prices(ticker, start if start else None, end if end else None)
    if err or data.empty:
        with tab_overview:
            st.error(f"No data found for that ticker/date range. {'' if err is None else 'Details: ' + err}")
        st.stop()
    # If Yahoo returned MultiIndex columns (e.g., multiple tickers), pick the current ticker
    if isinstance(data.columns, pd.MultiIndex):
        # try last level as ticker first (yfinance usual: level0=field, level1=symbol)
        if ticker in data.columns.get_level_values(-1):
            data = data.xs(ticker, axis=1, level=-1)
        elif ticker in data.columns.get_level_values(0):
            data = data.xs(ticker, axis=1, level=0)
        else:
            # fallback to first available symbol
            first_sym = data.columns.get_level_values(-1)[0]
            data = data.xs(first_sym, axis=1, level=-1)

    # pick price series for MA/backtest (prefer Adj Close if present)
    px = data.get("Adj Close", data.get("Close")).dropna()

    # build OHLC for candlesticks (real if available; else synthesize from px)
    if all(c in data.columns for c in ["Open", "High", "Low", "Close"]):
        ohlc = data[["Open", "High", "Low", "Close"]].copy()
        # align to px index in case some rows were dropped by px
        ohlc = ohlc.reindex(px.index).dropna()
    else:
        c = px
        ohlc = pd.DataFrame(index=c.index)
        ohlc["Open"]  = c.shift(1).fillna(c)
        ohlc["High"]  = pd.concat([ohlc["Open"], c], axis=1).max(axis=1)
        ohlc["Low"]   = pd.concat([ohlc["Open"], c], axis=1).min(axis=1)
        ohlc["Close"] = c

    # Ensure enough data for MAs
    if len(px) < max(int(fast), int(slow)) + 5:
        with tab_overview:
            st.warning("Not enough data after the chosen start/end to compute both moving averages.")
        st.stop()

    with st.spinner("Running backtest…"):
        sig_raw = ma_signals(px, int(fast), int(slow))

        # If a tuple was returned (e.g., (signals, extra)), take the first element
        if isinstance(sig_raw, tuple) and len(sig_raw) > 0:
            sig_raw = sig_raw[0]

        if isinstance(sig_raw, pd.Series):
            sig = sig_raw
        elif isinstance(sig_raw, pd.DataFrame):
            # Prefer a 'signal' column; otherwise take the first column
            sig = sig_raw["signal"] if "signal" in sig_raw.columns else sig_raw.iloc[:, 0]
        else:
            # NumPy array / list / other -> flatten to 1-D
            arr = np.asarray(sig_raw).squeeze()
            if arr.ndim != 1:
                raise ValueError(f"ma_signals returned array with shape {arr.shape}, expected 1-D")
            # Align to px index (handle length mismatches gracefully)
            idx = px.index
            if len(arr) == len(idx):
                sig = pd.Series(arr, index=idx)
            else:
                # place shorter arrays at the end (most common for indicator lookbacks)
                sig = pd.Series(arr, index=idx[-len(arr):]).reindex(idx)

        # Final cleanup/alignment
        sig = pd.Series(sig).reindex(px.index).fillna(0)

        res = run_backtest(px, sig)


    # ------------------ Overview ------------------
    with tab_overview:
        k1, k2, k3, k4 = st.columns(4)
        mdd_val, dd_series = max_drawdown(res["eq_strategy"])

        with k1:
            flashy_metric("CAGR (Strategy)",  f"{cagr(res['eq_strategy']):.2%}", color="green")
        with k2:
            flashy_metric("CAGR (Buy & Hold)", f"{cagr(res['eq_buyhold']):.2%}", color="violet")
        with k3:
            flashy_metric("Sharpe",            f"{sharpe(res['ret_strategy']):.2f}", color="green")
        with k4:
            flashy_metric("Max Drawdown",      f"{mdd_val:.2%}", color="red")

        st.divider()

        c1, c2 = st.columns(2)

        # Price + MAs
        with c1:
            st.subheader("Price & Moving Averages")
            ma_fast = px.rolling(int(fast)).mean()
            ma_slow = px.rolling(int(slow)).mean()
            fig1 = go.Figure()
            fig1.add_scatter(x=px.index, y=px, name=f"{ticker} Price",
                             line=dict(color=PALETTE["text"], width=2))
            fig1.add_scatter(x=px.index, y=ma_fast, name=f"MA {int(fast)}",
                             line=dict(color=PALETTE["accent"], width=2))
            fig1.add_scatter(x=px.index, y=ma_slow, name=f"MA {int(slow)}",
                             line=dict(color="#60a5fa", width=2))
            fig1.update_layout(height=420, margin=dict(l=30, r=20, t=10, b=30),
                               xaxis_title="Date", yaxis_title="Price")
            st.plotly_chart(fig1, use_container_width=True)

        # Equity curves
        with c2:
            st.subheader("Equity Curves")
            fig2 = go.Figure()
            fig2.add_scatter(x=res.index, y=res["eq_strategy"], name="Strategy",
                             line=dict(color=PALETTE["accent"], width=3))
            fig2.add_scatter(x=res.index, y=res["eq_buyhold"], name="Buy & Hold",
                             line=dict(color="#9aa4b2", width=2, dash="dash"))
            fig2.update_layout(height=420, margin=dict(l=30, r=20, t=10, b=30),
                               xaxis_title="Date", yaxis_title="Equity")
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Downloads")
        out = res.copy()
        out["signal"] = sig.reindex(res.index).fillna(0).astype(int)
        st.download_button(
            label="⬇️ Download results (CSV)",
            data=out.to_csv(index=True).encode("utf-8"),
            file_name=f"trendedge_{ticker}_{fast}_{slow}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.subheader(f"{ticker} Candlestick Chart")
        st.plotly_chart(plot_candles(ohlc, ticker), use_container_width=True)
        st.caption(f"Data source: Yahoo Finance — {ticker}")

    # ------------------ Strategy ------------------
    with tab_strategy:
        st.write("**Signals preview** (1 = long, 0 = flat):")
        prev = pd.DataFrame({
            "price": px,
            f"MA{int(fast)}": px.rolling(int(fast)).mean(),
            f"MA{int(slow)}": px.rolling(int(slow)).mean(),
            "signal": sig
        }).dropna().tail(200)
        st.dataframe(prev, use_container_width=True, height=360)

    # ------------------ Research (ML) ------------------
    with tab_research:
        st.caption("Prototype: simple ML classification of next-day up/down based on MA features.")
        df = pd.DataFrame({"close": px})
        df["ret1"] = df["close"].pct_change()
        df[f"ma{int(fast)}"] = df["close"].rolling(int(fast)).mean()
        df[f"ma{int(slow)}"] = df["close"].rolling(int(slow)).mean()
        df["xover"] = (df[f"ma{int(fast)}"] > df[f"ma{int(slow)}"]).astype(int)
        df["target_up"] = (df["close"].shift(-1) > df["close"]).astype(int)
        df = df.dropna()

        if len(df) > 100:
            from sklearn.model_selection import train_test_split
            from sklearn.linear_model import LogisticRegression
            X = df[[f"ma{int(fast)}", f"ma{int(slow)}", "xover", "ret1"]]
            y = df["target_up"]
            Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size=0.25, shuffle=False)
            clf = LogisticRegression(max_iter=200)
            clf.fit(Xtrain, ytrain)
            acc = clf.score(Xtest, ytest)
            st.metric("Prototype accuracy (holdout)", f"{acc*100:.1f}%")

            prob = pd.Series(clf.predict_proba(Xtest)[:, 1], index=Xtest.index, name="prob_up").tail(200)
            fig3 = go.Figure()
            fig3.add_scatter(x=prob.index, y=prob, mode="lines", name="P(up next day)",
                             line=dict(color=PALETTE["accent"], width=2))
            fig3.update_layout(height=300, margin=dict(l=30, r=20, t=10, b=30), yaxis_range=[0, 1])
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Not enough data for the demo model yet. Try a longer date range.")

    # ------------------ Data ------------------
    with tab_data:
        st.dataframe(pd.DataFrame({"Price": px}).tail(1000), use_container_width=True, height=420)

    # ------------------ Settings ------------------
    with tab_settings:
        st.write("Theme follows `.streamlit/config.toml`. You can also change the theme from the ☰ menu → Settings.")
        st.code(
            "[theme]\n"
            "base='dark'\nprimaryColor='#8b5cf6'\nbackgroundColor='#0b1220'\n"
            "secondaryBackgroundColor='#0f172a'\ntextColor='#e5e7eb'\nfont='sans serif'",
            language="toml"
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
