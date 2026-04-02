from typing import List, Callable, Type
from dataclasses import dataclass
from data.models import DataBar
from engine.backtest import BacktestEngine
from analytics.performance import PerformanceAnalyzer

@dataclass
class WalkForwardResult:
    """
    These are the results from a single walk-forward window.
    """
    window_num : int
    in_sample_sharpe : float
    out_of_sample_sharpe : float
    in_sample_return : float
    out_of_sample_return : float
    degradation : float

class WalkForwardTester:
    """
    This splits the data into rolling in-sample / out-of-sample windows.
    Trains and optimizes on IS data, tests on OOS data
    Then it compares IS vs OOS performance to detect overfitting.
    A robust strategy should have similar Sharpe ratios in both windows.
    A large IS vs OOS gap = the strategy memorized the past.
    """


    """
    bars represents the full historical bar list
    strategy_class represents the strategy to test
    in_sample_pct represents the fraction of each window used for training
    n_windows represents how many walk-forward windows to run
    """
    def __init__(self, bars : List[DataBar], strategy_class : Type, in_sample_pct : float = 0.7, n_windows : int = 3,):
        self.bars = bars
        self.strategy_class = strategy_class
        self.in_sample_pct = in_sample_pct
        self.n_windows = n_windows
    
    def run_window(self, bars : List[DataBar]) -> float:
        """
        This runs a backtest ona slice of bars, and returns the sharpe ratio
        """
        if len(bars) < 40:
            return 0.0
        engine = BacktestEngine(bars, self.strategy_class, initial_capital = 100_000)
        portfolio = engine.run()
        if len(portfolio.equity_curve) < 2:
            return 0.0
        try:
            analyzer = PerformanceAnalyzer(portfolio.equity_curve)
            return analyzer.sharpe_ratio()
        except Exception:
            return 0.0
    
    def run(self) -> List[WalkForwardResult]:
        """
        This function splits the bar into n_windows chuncks, runs IS + OOS backtest on each, and returns a result for every window.
        """
        results = []
        window_size = len(self.bars) // self.n_windows
        for i in range(self.n_windows):
            start = i * window_size
            end = start + window_size if i < self.n_windows - 1 else len(self.bars)
            window_bars = self.bars[start:end]
            split = int(len(window_bars) * self.in_sample_pct)
            is_bars = window_bars[:split]
            oos_bars = window_bars[split:]
            is_sharpe = self.run_window(is_bars)
            oos_sharpe = self.run_window(oos_bars)
            def get_return(bars):
                if len(bars) < 2:
                    return 0.0
                engine = BacktestEngine(bars, self.strategy_class, initial_capital = 100_000)
                portfolio = engine.run()
                if len(portfolio.equity_curve) < 2:
                    return 0.0
                try:
                    return PerformanceAnalyzer(portfolio.equity_curve).total_return()
                except Exception:
                    return 0.0
            results.append(WalkForwardResult(
                window_num = i + 1,
                in_sample_sharpe = is_sharpe,
                out_of_sample_sharpe = oos_sharpe,
                in_sample_return = get_return(is_bars),
                out_of_sample_return = get_return(oos_bars),
                degradation = is_sharpe - oos_sharpe,
            ))
        return results

    def print_report(self, results : List[WalkForwardResult], strategy_name : str = "Strategy"):
        """
        Prints a walk-forward summary with overfitting diagnosis.
        """
        print("\n" + "=" * 60)
        print(f"  WALK-FORWARD REPORT — {strategy_name}")
        print("=" * 60)
        print(f"  {'Window':<8} {'IS Sharpe':>10} {'OOS Sharpe':>12} {'Degradation':>13}")
        print("-" * 60)

        for r in results:
            flag = " ⚠ overfit" if r.degradation > 1.0 else ""
            print(f"  {r.window_num:<8} {r.in_sample_sharpe:>10.2f} "
                  f"{r.out_of_sample_sharpe:>12.2f} "
                  f"{r.degradation:>13.2f}{flag}")

        avg_deg = sum(r.degradation for r in results) / len(results)
        avg_oos = sum(r.out_of_sample_sharpe for r in results) / len(results)

        print("-" * 60)
        print(f"  Avg OOS Sharpe : {avg_oos:.2f}")
        print(f"  Avg degradation: {avg_deg:.2f}")

        if avg_deg > 1.0:
            print("\n  DIAGNOSIS: High degradation — strategy may be overfit.")
            print("  Consider: wider param ranges, fewer parameters, more data.")
        elif avg_oos > 0.5:
            print("\n  DIAGNOSIS: Strategy shows genuine out-of-sample edge.")
        else:
            print("\n  DIAGNOSIS: Weak OOS performance — strategy needs work.")

        print("=" * 60 + "\n")