from queue import Queue
from data.fetcher import fetch_ohlcv
from engine.backtest import BacktestEngine
from engine.events import MarketEvent
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy

def test_momentum_runs_without_error():
    bars = fetch_ohlcv("AAPL", "2021-01-01", "2021-12-31")
    engine = BacktestEngine(bars, MomentumStrategy, initial_capital = 100_000)
    portfolio = engine.run()
    assert len(portfolio.equity_curve) > 0

def test_mean_reversion_runs_without_error():
    bars = fetch_ohlcv("AAPL", "2021-01-01", "2021-12-31")
    engine = BacktestEngine(bars, MeanReversionStrategy, initial_capital = 100_000)
    portfolio = engine.run()
    assert len(portfolio.equity_curve) > 0

# want the momentum strategy to generate some signals and actually trade, otherwise it's not really doing anything.
# we are doing this on a full years worth of data to give it more chances to generate signals.
def test_momentum_generates_signals_and_trades():
    bars = fetch_ohlcv("AAPL", "2021-01-01", "2021-12-31")
    engine = BacktestEngine(bars, MomentumStrategy, initial_capital = 100_000)
    portfolio = engine.run()
    traded = (portfolio.positions.get("AAPL", 0) != 0) or (portfolio.cash != 100_000)
    assert traded

# WE are testing to see if the RSI values computed by the MeanReversionStrategy are within the valid range of 0 to 100,
# which is a fundamental property of the RSI indicator.
# This helps ensure that our RSI calculation is implemented correctly and that we are not generating invalid signals based on incorrect RSI values.
def test_rsi_values_in_valid_range():
    queue = Queue()
    strategy = MeanReversionStrategy(queue)
    bars = fetch_ohlcv("AAPL", "2021-01-01", "2021-12-31")
    for bar in bars:
        from engine.events import MarketEvent
        strategy._record_price(MarketEvent(bar = bar))
        rsi = strategy._compute_rsi()
        if rsi is not None:
            assert 0 <= rsi <= 100