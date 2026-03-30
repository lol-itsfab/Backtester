from queue import Queue
from engine.events import SignalEvent, FillEvent, OrderEvent, Direction

class Portfolio:
    """
    Tracks the cash, open positions, and the total equity over time.
    When it receives a SignalEvent, it generates an OrderEvent based on the signal and the current portfolio state.
    When it receives a FillEvent, it updates the cash and positions based on the fill details.
    """

    
    def __init__(self, event_queue : Queue, initial_capital : float = 100_000.0):
        """
        the self.positions dictionary maps ticker symbols to the number of shares currently held (positive for long, negative for short).
        the equity_curve is a list of tuples (timestamp, equity) that tracks the total value of the portfolio over time, which is used to calculate performance metrics later.
        """
        self.event_queue = event_queue
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions : dict[str, int] = {}
        self.equity_curve : list[tuple] = []
        
    def on_signal(self, signal : SignalEvent, current_price : float):
        """
        This method converts a SignalEvent into an OrderEvent. For simplicity, we will always order 100 shares per signal.
        """
        quantity = 100
        order = OrderEvent(
            ticker = signal.ticker,
            direction = signal.direction,
            quantity = quantity,
        )
        self.event_queue.put(order)
    
    def on_fill(self, fill : FillEvent):
        """
        This method updates the portfolio's cash and positions based on a FillEvent.
        """
        ticker = fill.ticker
        cost = fill.fill_price * fill.quantity + fill.commission
        if fill.direction == Direction.LONG:
            self.cash -= cost
            self.positions[ticker] = self.positions.get(ticker, 0) + fill.quantity
        else:
            self.cash += (fill.fill_price * fill.quantity - fill.commission)
            self.positions[ticker] = self.positions.get(ticker, 0) - fill.quantity
    
    def update_equity(self, timestamp, current_prices : dict[str, float]):
        """
        This method calculates the total equity of the portfolio at a given timestamp,
        which is the sum of cash and the market value of all open positions.
        """
        market_value = sum(
            self.positions.get(ticker, 0) * price
            for ticker, price in current_prices.items()
        )
        total = self.cash + market_value
        self.equity_curve.append((timestamp, total))