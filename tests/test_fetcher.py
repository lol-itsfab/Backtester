import pytest
from data.fetcher import fetch_ohlcv
from data.models import DataBar

def test_fetch_returns_databars():
    bars = fetch_ohlcv("AAPL", "2021-01-01", "2021-03-01")
    assert len(bars) > 0
    assert all(isinstance(b, DataBar) for b in bars)

def test_bars_are_sorted():
    bars = fetch_ohlcv("AAPL", "2021-01-01", "2021-03-01")
    timestamps = [b.timestamp for b in bars]
    assert timestamps == sorted(timestamps)

def test_ohlcv_validity():
    bars = fetch_ohlcv("SPY", "2021-01-01", "2021-03-01")
    for bar in bars:
        assert bar.low <= bar.open <= bar.high
        assert bar.low <= bar.close <= bar.high
        assert bar.volume >= 0

def test_invalid_ticker_raises():
    with pytest.raises(ValueError):
        fetch_ohlcv("XXXXINVALIDTICKER", "2021-01-01", "2021-03-01")