import pandas as pd

def run_backtest(prices: pd.Series, signal: pd.Series) -> pd.DataFrame:
    returns = prices.pct_change().fillna(0.0)
    strat_ret = returns * signal.shift(1).fillna(0)  # enter at next day
    df = pd.DataFrame({
        "price": prices,
        "ret_buyhold": returns,
        "ret_strategy": strat_ret
    })
    df["eq_buyhold"] = (1 + df["ret_buyhold"]).cumprod()
    df["eq_strategy"] = (1 + df["ret_strategy"]).cumprod()
    return df
