from queue import Queue
from engine.events import MarketEvent, SignalEvent, Direction
from strategies.base import BaseStrategy

class MomentumStrategy(BaseStrategy):
    """
    This is a Simple Moving Average (SMA) crossover strategy.
    It generates a long signal when the fast SMA crosses above the slow SMA,
    and a short signal when the fast SMA crosses below the slow SMA.
    This is because when the fast SMA is above the slow SMA, it indicates that recent prices are higher than the longer-term average, suggesting upward momentum.
    The same can be applied when the fast SMA is below the slow SMA, it indicates that recent prices are lower than the longer-term average, which ultimately
    suggests downward momentum.

    Since this is a momentum strategy, it is designed to capture recent trends in the market.
    So momentum strategies bet that recent trends continue, rather than reverse.
    """

    def __init__(self, event_queue : Queue, fast_window : int = 10, slow_window : int = 30):
        super().__init__(event_queue)
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.position = 0 # 1 for long, -1 for short, 0 for flat
    
    def _sma(self, window : int) -> float | None : # returns a float if it can be computed otherwise a None
        if len(self.prices) < window:
            return None
        return sum(self.prices[-window:]) / window
    
    def on_market(self, event : MarketEvent):
        self._record_price(event)
        fast = self._sma(self.fast_window)
        slow = self._sma(self.slow_window)
        if fast is None or slow is None:
            return
        ticker = event.bar.ticker
        timestamp = event.bar.timestamp
        if fast > slow and self.position != 1:
            self.event_queue.put(SignalEvent(
                ticker = ticker,
                direction = Direction.LONG,
                timestamp = timestamp,
            ))
            self.position = 1
        elif fast < slow and self.position != -1:
            self.event_queue.put(SignalEvent(
                ticker = ticker,
                direction = Direction.SHORT,
                timestamp = timestamp,
            ))
            self.position = -1

