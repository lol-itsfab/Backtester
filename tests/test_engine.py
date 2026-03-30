from queue import Queue
from data.fetcher import fetch_ohlcv
from engine.backtest import BacktestEngine
from engine.events import MarketEvent, SignalEvent, Direction, EventType

class BuyAndHoldStrategy:
    """
    Uses a simple test case where you just buy and hold and never sell.
    """
    def __init__(self, event_queue : Queue):
        self.event_queue = event_queue
        self.bought = False
    
    def on_market(self, event : MarketEvent):
        if not self.bought:
            self.event_queue.put(SignalEvent(
                ticker = event.bar.ticker,
                direction = Direction.LONG,
                timestamp = event.bar.timestamp,
            ))
            self.bought = True
    
def test_engine_runs_and_produce_equity_curve():
    bars = fetch_ohlcv("AAPL", "2021-01-01", "2021-06-01")
    engine = BacktestEngine(bars, BuyAndHoldStrategy, initial_capital = 100_000)
    portfolio = engine.run()
    assert len(portfolio.equity_curve) > 0
    assert portfolio.equity_curve[0][1] == 100_000 # this makes it so we start at the initial capital which is 100_000
    
def test_but_and_hold_increases_position():
    bars = fetch_ohlcv("AAPL", "2021-01-01", "2021-06-01")
    engine = BacktestEngine(bars, BuyAndHoldStrategy, initial_capital = 100_000)
    portfolio = engine.run()
    assert portfolio.positions.get("AAPL", 0) == 100 #buying 100 shares of AAPL
    assert portfolio.cash < 100_000 # cash should decrease after buying the shares
