import pytest
from datetime import datetime, timedelta
from analytics.performance import PerformanceAnalyzer

def make_curve(returns : list[float], initial : float = 100_000.0):
    """
    This is a helper function to build an equity curve from a list of returns, which we can use to test the PerformanceAnalyzer.
    """
    curve = []
    equity = initial
    base = datetime(2021, 1, 1)
    curve.append((base, equity))
    for i, r in enumerate(returns):
        equity *= (1 + r)
        curve.append((base + timedelta(days = i + 1), equity))
    return curve

def test_total_return_positive():
    curve = make_curve([0.01] * 100) # This is a 1% gain
    analyzer = PerformanceAnalyzer(curve)
    assert analyzer.total_return() > 0

def test_total_return_negative():
    curve = make_curve([-0.01] * 100) # This is a 1% loss
    analyzer = PerformanceAnalyzer(curve)
    assert analyzer.total_return() < 0

def test_max_drawdown_known_case():
    curve = make_curve([0.005] * 100 + [-0.01] * 100)
    analyzer = PerformanceAnalyzer(curve)
    dd = analyzer.max_drawdown()
    assert 0 < dd < 1

def test_max_drawdown_for_good_strategy():
    curve = make_curve([0.002] * 252)
    analyzer = PerformanceAnalyzer(curve)
    assert analyzer.sharpe_ratio() > 0

def test_max_drawdown_flat_curve():
    curve = make_curve([0.0] * 100)
    analyzer = PerformanceAnalyzer(curve)
    assert analyzer.max_drawdown() == 0.0

def test_summary_has_all_keys():
    curve = make_curve([0.001] * 252)
    analyzer = PerformanceAnalyzer(curve)
    keys = analyzer.summary().keys()
    for expected in ["total_return", "cagr", "sharpe_ratio", "sortino_ratio", "max_drawdown"]:
        assert expected in keys