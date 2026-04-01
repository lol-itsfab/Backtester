from queue import Queue
from engine.events import MarketEvent, SignalEvent, Direction
from strategies.base import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    """
    This is a Relative Strength Index (RSI) based mean reversion strategy. This means that it generates trading signals based on the RSI indicator,
    which measures the speed and change of price movements. The RSI is typically used to identify overbought or oversold conditions in a market.
    For our logic we will use 30 and 70 as thresholds.
    When the RSI is above 70, it indicates that the asset is overbought, which likely suggets that the price will regulate or fall back down, so we will generate a short signal.
    When the RSI is below 30, it indicates that the asset is oversold, which likely suggests that the price will bounce back up, so we will generate a long signal.

    For this strategy specifically it is designed to capture the current price and bet that it will revert back to its historical average.
    """

    def __init__(self, event_queue : Queue, rsi_window : int = 14, oversold : float = 30.0, overbought : float = 70.0):
        super().__init__(event_queue)
        self.rsi_window = rsi_window
        self.oversold = oversold
        self.overbought = overbought
        self.position = 0
    
    def _compute_rsi(self) -> float | None:
        """
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss over the specified period (rsi_window)
        just like the momentum strategy, if we don't have enough prices to compute the RSI, we return None.
        """
        if len(self.prices) < self.rsi_window + 1:
            return None
        
        deltas = [self.prices[i] - self.prices[i - 1] for i in range(-self.rsi_window, 0)]
        gains = [delta for delta in deltas if delta > 0]
        losses = [abs(delta) for delta in deltas if delta < 0]
        average_gain = sum(gains) / self.rsi_window if gains else 0.0
        average_loss = sum(losses) / self.rsi_window if losses else 0.0
        if average_loss == 0:
            return 100.0
        rs = average_gain / average_loss
        return 100 - (100 / (1 + rs))
    
    def on_market(self, event: MarketEvent):
        self._record_price(event)
        rsi = self._compute_rsi()
        if rsi is None:
            return
        ticker = event.bar.ticker
        timestamp = event.bar.timestamp
        if rsi < self.oversold and self.position != 1:
            self.event_queue.put(SignalEvent(
                ticker = ticker,
                direction = Direction.LONG,
                timestamp = timestamp,
            ))
            self.position = 1
        elif rsi > self.overbought and self.position != -1:
            self.event_queue.put(SignalEvent(
                ticker = ticker,
                direction = Direction.SHORT,
                timestamp = timestamp,
            ))
            self.position = -1