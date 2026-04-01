import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List
from data.models import DataBar

def fetch_ohlcv (
        ticker : str,
        start: str,
        end: str,
        interval: str = "1d",
) -> List[DataBar]:
    
    """
    Fetch Only High Low Close Volume (OHLCV) data for a ticker and return clean DataBar objects.
    
    Arguments:
    ticker: The stock symbol to fetch data for ("AAPL", "SPY", "VOO", etc.)
    start: "YYYY-MM-DD"
    end: "YYYY-MM-DD
    interval: "1d"
    
    Returns:
    A sorted list of DataBar objects, where the oldest appears first.
    """

    raw: pd.DataFrame = yf.download (
        ticker,
        start = start,
        end = end,
        interval = interval,
        auto_adjust = True,
        progress = False,
        multi_level_index = False, # falttens colums for single ticker (otherwise we get a multiindex with the ticker as the top level, which is annoying to work with).
    )
    # We set auto_adjust to True to get adjusted prices, which account for stock splits.
    # This gives us a more accurate price historically.

    if raw.empty:
        raise ValueError(f"No data returned for {ticker} between {start} and {end}")
    
    raw.columns = [c.strip().title() for c in raw.columns]
    bars = []
    for ts, row in raw.iterrows():
        if row[["Open", "High", "Low", "Close", "Volume"]].isnull().any():
            continue
        try:
            bar = DataBar (
                ticker = ticker,
                timestamp = ts.to_pydatetime(),
                open = float(row["Open"]),
                high = float(row["High"]),
                low = float(row["Low"]),
                close = float(row["Close"]),
                volume = float(row["Volume"]),
            )
            bars.append(bar)
        except ValueError as e:
            print (f"[Warning] Skipping invalid bar at {ts} for {ticker}: {e}")
            """
            This logs bad bars but does not crash the entire fetch.
            This makes it so we know when there is a prblem with the data.
            """
    return sorted(bars, key = lambda b : b.timestamp)
    
