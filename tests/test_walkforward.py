from data.fetcher import fetch_ohlcv
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from analytics.walkforward import WalkForwardTester
from analytics.optimizer import optimize_strategy

def test_walk_forward_returns_correct_window_count():
    bars = fetch_ohlcv("AAPL", "2020-01-01", "2024-01-01")
    tester = WalkForwardTester(bars, MomentumStrategy, n_windows = 3)
    results = tester.run()
    assert len(results) == 3

def test_walk_forward_result_fields():
    bars = fetch_ohlcv("AAPL", "2020-01-01", "2024-01-01")
    tester = WalkForwardTester(bars, MomentumStrategy, n_windows = 2)
    results = tester.run()
    for r in results:
        assert hasattr(r, "in_sample_sharpe")
        assert hasattr(r, "out_of_sample_sharpe")
        assert hasattr(r, "degradation")
        assert r.window_num > 0

def test_optimizer_returns_sorted_results():
    bars = fetch_ohlcv("AAPL", "2022-01-01", "2024-01-01")
    param_grid = {
        "fast_window" : [5, 10, 20],
        "slow_window" : [30, 50],
    }
    results = optimize_strategy(bars, MomentumStrategy, param_grid)
    assert len(results) > 0
    sharpes = [r.sharpe for r in results]
    assert sharpes == sorted(sharpes, reverse = True)

def test_optimizer_skips_invalid_params():
    """
    This is method that tests that if fast_window >= the slow_window then
    it should be skipped automatically.
    """
    bars = fetch_ohlcv("AAPL", "2022-01-01", "2024-01-01")
    param_grid = {
        "fast_window" : [50],
        "slow_window" : [10],
    }
    results = optimize_strategy(bars, MomentumStrategy, param_grid)
    assert len(results) == 0