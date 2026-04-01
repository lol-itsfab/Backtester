from abc import ABC, abstractmethod
from queue import Queue
from engine.events import MarketEvent

class BaseStrategy(ABC):
    """
    All the strategies must inherit from this base class and implement the on_market method,
    which will be called with each new MarketEvent. Using the abstract base class it forces
    the contract"""

    def __init__(self, event_queue: Queue):
        self.event_queue = event_queue
        self.prices : list[float] = []
    
    """
    This method is called with each new MarketEvent.
    If the conditions are met to generate a trading signal,
    it should create a SignalEvent and put it on the event queue for the portfolio to process.
    """
    @abstractmethod
    def on_market(self, event: MarketEvent):
        raise NotImplementedError
    
    """
    This method is a helper function that records the closing price from each MarketEvent.
    It appends the closing price to the self.prices list and returns the price.
    This can be useful for strategies that need to analyze historical prices to make trading decisions.
    """
    def _record_price(self, event : MarketEvent) -> float:
        price = event.bar.close
        self.prices.append(price)
        return price