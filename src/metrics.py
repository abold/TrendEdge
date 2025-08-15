import numpy as np
import pandas as pd

def cagr(equity: pd.Series, periods_per_year=252):
    n = len(equity)
    if n < 2: return np.nan
    return equity.iloc[-1]**(periods_per_year/n) - 1

def sharpe(returns: pd.Series, periods_per_year=252, rf=0.0):
    if returns.std() == 0: return np.nan
    return (returns.mean() - rf/periods_per_year) / returns.std() * np.sqrt(periods_per_year)

def max_drawdown(equity: pd.Series):
    rollmax = equity.cummax()
    dd = equity/rollmax - 1
    return dd.min(), dd
