from queue import Queue
from datetime import datetime
from engine.events import OrderEvent, FillEvent, Direction

class SimulatedBroker:
    """ 
    simulates order execution with slippage and commission.
    slippage is the difference between the expected price of a trade and the actual price at which the trade is executed,
    which can occur due to market volatility or delays in order processing.
    Commission is the fee charged by the broker for executing a trade.
    """

    def __init__(self, event_queue : Queue, slippage : float = 0.001, commission : float = 1.0):
        """
        event_queue: The queue to which the broker will send FillEvents after executing orders.
        slippage: The percentage slippage to apply to the fill price (e.g. 0.001 for 0.1% slippage).
        commission: The fixed commission to charge per trade (e.g. $1.0 per trade).
        """
        self.event_queue = event_queue
        self.slippage = slippage
        self.commission = commission

    def execute_order(self, order : OrderEvent, current_price : float, timestamp : datetime):
        """
        This takes an OrderEvent, simulates the execution by applying slippage and commission, and then puts a FillEvent on the event queue.
        It buys fill slighly above the current price for long orders, and sells slightly below the current price for short orders, to simulate slippage.
        """
        if order.direction == Direction.LONG:
            fill_price = current_price * (1 + self.slippage)
        else:
            fill_price = current_price * (1 - self.slippage)
        fill = FillEvent(
            ticker = order.ticker,
            direction = order.direction,
            quantity= order.quantity,
            fill_price = fill_price,
            commission = self.commission,
            timestamp = timestamp,
        )
        self.event_queue.put(fill)
