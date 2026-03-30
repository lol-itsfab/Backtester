from queue import Queue, Empty
from typing import List, Type
from data.models import DataBar
from engine.events import MarketEvent, SignalEvent, OrderEvent, FillEvent, EventType
from engine.portfolio import Portfolio
from engine.broker import SimulatedBroker

class BacktestEngine:
    """
    This contains the core event loop. This will replay historical bars one at a time, 
    routing events between strategy, portfolio, and broker.
    """
    def __init__ (
            self,
            bars : List[DataBar],
            strategy_class,
            initial_capital : float = 100_000.0,
            slippage : float = 0.001,
            commission : float = 1.0,
    ):
        self.bars = bars
        self.event_queue = Queue()
        self.portfolio = Portfolio(self.event_queue, initial_capital)
        self.broker = SimulatedBroker(self.event_queue, slippage, commission)
        self.strategy = strategy_class(self.event_queue)
    
    def run(self):
        """
        This is the main event loop.
        it iterates bar by bar, putting a MarketEvent on the event queue for each bar,
        and then processes all events in the queue until it's empty before moving to the next bar.
        """
        for bar in self.bars:
            self.event_queue.put(MarketEvent(bar = bar))
            while not self.event_queue.empty():
                try:
                    event = self.event_queue.get(block = False)
                except Empty:
                    break
                if event.type == EventType.MARKET:
                    self.strategy.on_market(event)
                    self.portfolio.update_equity(bar.timestamp, {bar.ticker : bar.close})
                elif event.type == EventType.SIGNAL:
                    self.portfolio.on_signal(event, bar.close)
                elif event.type == EventType.ORDER:
                    self.broker.execute_order(event, bar.close, bar.timestamp)
                elif event.type == EventType.FILL:
                    self.portfolio.on_fill(event)
        return self.portfolio