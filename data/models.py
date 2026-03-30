from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen = True)
class DataBar:
    """
    A single OHLCV (Open High Low Close Volume) bar - The atomic unit of market data.
    frozen = True makes it immmutable (safe to pass around without copying)
    frozen = True This is because we will get wrong results with no error if it is mutable, so Freezing makes it safe.
    """

    ticker : str
    timestamp : datetime
    open: float
    high : float
    low : float
    close : float
    volume : float

    def __post_init__(self):
        # A bar is invalid if any of these conditions are true:
        if not (self.low <= self.open <= self.high):
            raise ValueError(f"Invalid bar: open {self.open} outside [low={self.low}, high={self.high}]")
        if not (self.low <= self.close <= self.high):
            raise ValueError(f"Invalid bar: close {self.close} outside [low={self.low}, high={self.high}]")
        if self.volume < 0:
            raise ValueError(f"Invalid bar: negative volume {self.volume}")