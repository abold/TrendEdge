import pandas as pd

def ma_signals(prices: pd.Series, fast: int, slow: int) -> pd.Series:
    f = prices.rolling(fast).mean()
    s = prices.rolling(slow).mean()
    return (f > s).astype(int)  # 1=long, 0=flat
