# src/backtest.py
import numpy as np
import pandas as pd

def _to_series(x, fallback_index=None, name=None):
    """Coerce x to a 1-D pandas Series and keep/restore a sensible index."""
    # If already a Series, just ensure 1-D
    if isinstance(x, pd.Series):
        s = x.squeeze()
        s.name = s.name or name
        return s

    # If DataFrame, take first column
    if isinstance(x, pd.DataFrame):
        s = x.iloc[:, 0].squeeze()
        s.name = s.name or name
        return s

    # NumPy / list / scalar
    arr = np.asarray(x).squeeze()
    if arr.ndim == 0:
        # Scalar -> length-1 series (will be aligned later)
        return pd.Series([arr], name=name)
    if arr.ndim != 1:
        raise ValueError(f"Expected 1-D data, got shape {arr.shape}")

    if fallback_index is not None and len(fallback_index) == len(arr):
        return pd.Series(arr, index=fallback_index, name=name)
    return pd.Series(arr, name=name)


def run_backtest(prices, signal):
    """
    prices: price series (pd.Series preferred)
    signal: 0/1 or -1/1 positions aligned to prices.index (next-day execution applied inside)
    Returns a DataFrame with columns:
      price, ret_buyhold, ret_strategy, eq_buyhold, eq_strategy
    """
    # --- Coerce to 1-D Series and align ---
    px_idx = getattr(prices, "index", None)
    px = _to_series(prices, fallback_index=px_idx, name="price").astype(float).dropna()

    sig = _to_series(signal, fallback_index=getattr(signal, "index", None), name="signal")
    # Align to price index and clean
    sig = sig.reindex(px.index)
    # If signal length is shorter (common with lookbacks), right-align it
    if sig.isna().all() and len(sig) != len(px):
        sig = _to_series(signal, fallback_index=None, name="signal")
        sig = sig.reindex(px.index[-len(sig):]).reindex(px.index)
    sig = sig.fillna(0).astype(float)

    # --- Returns (next-day execution) ---
    ret_buyhold = px.pct_change().fillna(0)
    ret_strategy = ret_buyhold * sig.shift(1).fillna(0)

    # --- Build DataFrame with explicit index to avoid scalar issues ---
    df = pd.DataFrame(
        {
            "price": px.values,
            "ret_buyhold": ret_buyhold.values,
            "ret_strategy": ret_strategy.values,
        },
        index=px.index,
    )

    # --- Equity curves ---
    df["eq_buyhold"]  = (1.0 + df["ret_buyhold"]).cumprod()
    df["eq_strategy"] = (1.0 + df["ret_strategy"]).cumprod()

    return df
