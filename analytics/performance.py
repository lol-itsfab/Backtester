import math
from typing import List, Tuple
from datetime import datetime

class PerformanceAnalyzer:
    """
    This class provides methods to compute various performance metrics for a trading strategy based on its equity curve.
    """

    def __init__(self, equity_curve : List[Tuple[datetime, float]]):
        """
        Equity_curve is a list of (timestamp, total_equity) tuples produced by the Portfolio.equity_curve.
        """

        if len(equity_curve) < 2:
            raise ValueError("Need at least 2 data points to compute performance metrics.")
        self.equity_curve = equity_curve
        self.timestamps = [t for t, _ in equity_curve]
        self.equity = [e for _, e in equity_curve]
        self.returns = self._compute_returns()
    
    def _compute_returns(self) -> List[float]:
        """
        Daily returns: (today - yesterday) / yesterday
        """
        return [
            (self.equity[i] - self.equity[i-1]) / self.equity[i-1]
            for i in range(1, len(self.equity))
        ]
    
    def total_return(self) -> float:
        """
        Total percent return over the entire period: (final equity - initial equity) / initial equity
        """
        return (self.equity[-1] - self.equity[0]) / self.equity[0]
    
    def cagr(self) -> float:
        """
        Compound Annual Growth Rate (CAGR):
        What consistent yearly return would produce this result? CAGR = (final equity / initial equity)^(1/years) - 1
        """

        start = self.timestamps[0]
        end = self.timestamps[-1]
        years = (end - start).days / 365.25
        if years <= 0:
            return 0.0
        return (self.equity[-1] / self.equity[0]) ** (1 / years) - 1
    
    def sharpe_ratio(self, risk_free_rate : float = 0.05) -> float:
        """
        Sharpe Ratio = (mean return - risk free rate) / std deviation of returns
        Annualized assuming daily returns: 252 trading days per year.

        if < 0 then the strategy underperformed the risk free rate,
        if 0 - 1 then it performed better than risk free but not great,
        if 1 - 2 then it performed decently,
        if > 2 then it performed very well.
        if > 3 then it performed exceptionally well.

        The risk free rate is an annual rate (0.05 for 5%), so we need to convert it to a daily rate for the calculation.
        """
        if not self.returns:
            return 0.0
        daily_rf = risk_free_rate / 252
        excess = [r - daily_rf for r in self.returns]
        mean_excess = sum(excess) / len(excess)
        variance = sum((r - mean_excess) ** 2 for r in excess) / len(excess)
        std = math.sqrt(variance)
        if std == 0:
            return 0.0
        return (mean_excess / std) * math.sqrt(252)
    
    def sortino_ratio(self, risk_free_rate : float = 0.05) -> float:
        """
        This penalizes only the volatility of negative returns, which is often more relevant for investors who are more concerned about downside risk.
        Thus upside volatility does not reduce the Sortino ratio, while it would reduce the Sharpe ratio.
        """
        if not self.returns:
            return 0.0
        daily_rf = risk_free_rate / 252
        excess = [r - daily_rf for r in self.returns]
        mean_excess = sum(excess) / len(excess)
        downside = [r for r in excess if r < 0]
        if not downside:
            return float("inf") # There are no losing days, so the Sortino ratio is infinite.
        downside_var = sum(r ** 2 for r in downside) / len(excess)
        downside_std = math.sqrt(downside_var)
        if downside_std == 0:
            return 0.0
        return (mean_excess / downside_std) * math.sqrt(252)
    
    def max_drawdown(self) -> float:
        """
        Maximum peak-to-trough decline in the equity curve.
        This is a measure of risk, as it shows the worst loss an investor would have experienced.
        Probably the most important risk metric for a trading strategy, as it captures the worst-case scenario.
        An example would be like if you started with 20 dollars went to 40 then dropped to 10, then the max drawdown would be (40 - 10) / 40 = 75%.

        if < 10% then the strategy has very low drawdown and is very safe meaning it has a controlled risk profile,
        if between 10 - 20% then it has moderate drawdown and is relatively safe,
        if > 30% then it has high drawdown and is risky.
        if > 50% then it has very high drawdown and is extremely risky.
        """
        peak = self.equity[0]
        max_dd = 0.0
        for e in self.equity:
            if e > peak:
                peak = e
            drawdown = (peak - e) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        return max_dd
    
    def summary(self) -> dict:
        """
        This returns a dictionary of all the performance metrics for easy reporting.
        """
        return {
            "total_return" : self.total_return(),
            "cagr" : self.cagr(),
            "sharpe_ratio" : self.sharpe_ratio(),
            "sortino_ratio" : self.sortino_ratio(),
            "max_drawdown" : self.max_drawdown(),
            "num_bars" : len(self.equity),
        }
