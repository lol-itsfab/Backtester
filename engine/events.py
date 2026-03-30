from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from data.models import DataBar

class EventType(Enum):
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"

class Direction(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

@dataclass
class MarketEvent:
    # Tells the strategy to look at the latest market data and generate signals.
    type : EventType = field(default = EventType.MARKET, init = False)
    bar : DataBar = None

@dataclass
class SignalEvent:
    # From the strategy we either long or short a ticker.
    type : EventType = field(default = EventType.SIGNAL, init = False)
    ticker : str = ""
    direction : Direction = Direction.LONG
    timestamp : datetime = None

@dataclass
class OrderEvent:
    # The portfolio generates an order based on the signal, and sends it to the execution system.
    type : EventType = field(default = EventType.ORDER, init = False)
    ticker : str = ""
    direction : Direction = Direction.LONG
    quantity : int = 0

@dataclass
class FillEvent:
    # The broker executes the order and sends a fill event back to the portfolio, which updates the portfolio's positions and cash, this basically confirms the execution.
    type : EventType = field(default = EventType.FILL, init = False)
    ticker : str = ""
    direction : Direction = Direction.LONG
    quantity : int = 0
    fill_price : float = 0.0
    commission : float = 0.0
    timestamp : datetime = None
