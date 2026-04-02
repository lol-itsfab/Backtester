import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from analytics.performance import PerformanceAnalyzer

def print_tearsheet(analyzer : PerformanceAnalyzer, strategy_name : str = "Strategy"):
    """
    This function takes a performance analyzer object and prints out a simple tearsheet with key performance metrics
    so we can quickly evaluate how well a strategy performed.
    """
    m = analyzer.summary()
    print("\n" + "=" * 50)
    print(f" TEAR SHEER - {strategy_name}")
    print("=" * 50)
    print(f"  Total return   : {m['total_return']:>10.2%}")
    print(f"  CAGR           : {m['cagr']:>10.2%}")
    print(f"  Sharpe ratio   : {m['sharpe_ratio']:>10.2f}")
    print(f"  Sortino ratio  : {m['sortino_ratio']:>10.2f}")
    print(f"  Max drawdown   : {m['max_drawdown']:>10.2%}")
    print(f"  Bars processed : {m['num_bars']:>10,}")
    print("=" * 50 + "\n")

def plot_equity_curve(analyzer : PerformanceAnalyzer, strategy_name : str = "Strategy"):
    """
    This function plots the equity curve and drawdown curve of the strategy,
    which are important visual tools for understanding the performance and risk of a trading strategy.
    """
    timestamps = analyzer.timestamps
    equity = analyzer.equity
    peak = equity[0]
    drawdowns = []
    for e in equity:
        if e > peak:
            peak = e
        drawdowns.append(-(peak - e) / peak)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), gridspec_kw={"height_ratios": [3, 1]}, sharex = True)
    fig.suptitle(f"{strategy_name} - Backtest Results", fontsize = 14, fontweight = "bold")
    ax1.plot(timestamps, equity, color = "#2196F3", linewidth = 1.5, label = "Portfolio equity curve")
    ax1.axhline(equity[0], color="gray", linestyle="--", linewidth=0.8, label="Initial capital")
    ax1.set_ylabel("Portfolio Value ($)")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    # Drawdown
    ax2.fill_between(timestamps, drawdowns, 0, color="#F44336", alpha=0.4, label="Drawdown")
    ax2.set_ylabel("Drawdown")
    ax2.set_xlabel("Date")
    ax2.legend(loc="lower left")
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.tight_layout()
    plt.savefig("tearsheet.png", dpi=150, bbox_inches="tight")
    print("Chart saved to tearsheet.png")
    plt.show()

