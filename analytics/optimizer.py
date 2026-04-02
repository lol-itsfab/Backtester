from typing import List, Type, Dict, Any
from dataclasses import dataclass
from data.models import DataBar
from engine.backtest import BacktestEngine
from analytics.performance import PerformanceAnalyzer

@dataclass
class OptimizationResult:
    params : Dict[str, Any]
    sharpe : float
    total_return : float
    max_drawdown : float

def optimize_strategy(bars : List[DataBar], strategy_class : Type, param_grid : Dict[str, List[Any]], initial_capital : float = 100_000,) -> List[OptimizationResult]:
    """
    This function will test every combination in param_grid on the given bars
    and returns a sorted by Sharpe ratio with the best being first.
    bars represent the historical bars to opimize on
    strategy_class represents the type of strategy
    param_grid represents the grid and whether its a slow or fast window
    """
    import itertools
    
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    combinations = list(itertools.product(*values))
    results = []
    for combo in combinations:
        params = dict(zip(keys, combo))
        if "fast_window" in params and "slow_window" in params:
            if params["fast_window"] >= params["slow_window"]:
                continue
        try:
            class ParameterizedStrategy(strategy_class):
                def __init__(self, event_queue):
                    super().__init__(event_queue, **params)
            engine = BacktestEngine(bars, ParameterizedStrategy, initial_capital = initial_capital)
            portfolio = engine.run()
            if len(portfolio.equity_curve) < 2:
                continue
            analyzer = PerformanceAnalyzer(portfolio.equity_curve)
            results.append(OptimizationResult(params = params, sharpe = analyzer.sharpe_ratio(), total_return = analyzer.total_return(), max_drawdown = analyzer.max_drawdown(), ))
        except Exception as e:
            continue
    return sorted(results, key = lambda r : r.sharpe, reverse = True)

def print_optimization_results(results: List[OptimizationResult], top_n: int = 5):
    """
    Prints the top N parameter combinations.
    """
    print("\n" + "=" * 65)
    print("  OPTIMIZATION RESULTS — Top Combinations by Sharpe")
    print("=" * 65)
    print(f"  {'Params':<30} {'Sharpe':>8} {'Return':>10} {'Drawdown':>10}")
    print("-" * 65)

    for r in results[:top_n]:
        param_str = ", ".join(f"{k}={v}" for k, v in r.params.items())
        print(f"  {param_str:<30} {r.sharpe:>8.2f} "
              f"{r.total_return:>10.2%} {r.max_drawdown:>10.2%}")

    print("=" * 65 + "\n")
