"""SMAC - Simple Moving Average Crossover Analysis.

A package for performing simple moving average crossover analysis on stock data.

Modern functional API:
    from smac.analysis import analyze_ticker, run_smac_analysis, SMACConfig
    from smac.visualization import plot_analysis

Legacy class-based API (for backward compatibility):
    from smac import SMACAnalyzer
"""

from smac import cli
from smac.analysis import SMACConfig, SMACResult, analyze_ticker, run_smac_analysis
from smac.legacy import SMACAnalyzer
from smac.visualization import plot_analysis

__all__ = [
    # Legacy API
    "SMACAnalyzer",
    "cli",
    # Modern functional API
    "analyze_ticker",
    "run_smac_analysis",
    "plot_analysis",
    "SMACConfig",
    "SMACResult",
]
__version__ = "0.1.0"
