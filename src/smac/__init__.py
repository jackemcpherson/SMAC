"""SMAC - Simple Moving Average Crossover Analysis.

A package for performing simple moving average crossover analysis on stock data.

API Usage:
    from smac.analysis import analyze_ticker, run_smac_analysis, SMACConfig
    from smac.visualization import plot_analysis
"""

from smac import cli
from smac.analysis import SMACConfig, SMACResult, analyze_ticker, run_smac_analysis
from smac.visualization import plot_analysis

__all__ = [
    "cli",
    "analyze_ticker",
    "run_smac_analysis",
    "plot_analysis",
    "SMACConfig",
    "SMACResult",
]
__version__ = "0.1.0"
