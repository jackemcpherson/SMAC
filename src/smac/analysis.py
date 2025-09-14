"""Core SMAC analysis functionality with modern Python patterns.

This module provides the main analysis interface using immutable dataclasses
and functional programming patterns. The analysis workflow is completely
stateless and returns immutable result objects.

Classes:
    SMACConfig: Immutable configuration for SMAC analysis
    SMACResult: Immutable results container with analysis data

Functions:
    run_smac_analysis: Execute complete SMAC analysis workflow
    analyze_ticker: Convenience function for ticker analysis
"""

import logging
from dataclasses import dataclass

import pandas as pd

from smac.data import fetch_stock_data
from smac.indicators import calculate_dual_sma, identify_crossover_signals

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SMACConfig:
    """Configuration for SMAC analysis."""

    ticker: str
    short_window: int
    long_window: int
    start_date: str | None = None
    end_date: str | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.short_window <= 0 or self.long_window <= 0:
            raise ValueError("Window periods must be positive integers")
        if self.short_window >= self.long_window:
            raise ValueError("Short window must be smaller than long window")


@dataclass(frozen=True)
class SMACResult:
    """Results of SMAC analysis."""

    config: SMACConfig
    data: pd.DataFrame
    buy_signals: pd.DataFrame
    sell_signals: pd.DataFrame

    @property
    def num_buy_signals(self) -> int:
        """Number of buy signals identified."""
        return len(self.buy_signals)

    @property
    def num_sell_signals(self) -> int:
        """Number of sell signals identified."""
        return len(self.sell_signals)

    @property
    def date_range(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        """Date range of the analysis."""
        return self.data.index.min(), self.data.index.max()

    def summary(self) -> dict:
        """Get a summary of the analysis results."""
        start_date, end_date = self.date_range
        return {
            "ticker": self.config.ticker,
            "short_window": self.config.short_window,
            "long_window": self.config.long_window,
            "data_points": len(self.data),
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
            },
            "signals": {
                "buy": self.num_buy_signals,
                "sell": self.num_sell_signals,
            },
        }


def run_smac_analysis(config: SMACConfig) -> SMACResult:
    """Run complete SMAC analysis with the given configuration.

    Args:
        config: SMAC analysis configuration.

    Returns:
        Complete SMAC analysis results.

    Raises:
        ValueError: If configuration is invalid.
        ConnectionError: If data fetching fails.
    """
    logger.info(
        "Starting SMAC analysis for %s with windows %d/%d",
        config.ticker,
        config.short_window,
        config.long_window,
    )

    stock_data = fetch_stock_data(config.ticker, config.start_date, config.end_date)
    sma_data = calculate_dual_sma(stock_data, config.short_window, config.long_window)
    analysis_data = identify_crossover_signals(sma_data)

    buy_signals = analysis_data[analysis_data["crossover"] == 1.0].copy()
    sell_signals = analysis_data[analysis_data["crossover"] == -1.0].copy()

    result = SMACResult(
        config=config,
        data=analysis_data,
        buy_signals=buy_signals,
        sell_signals=sell_signals,
    )

    logger.info(
        "SMAC analysis complete: %d buy signals, %d sell signals over %d data points",
        result.num_buy_signals,
        result.num_sell_signals,
        len(result.data),
    )

    return result


def analyze_ticker(
    ticker: str,
    short_window: int = 20,
    long_window: int = 50,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> SMACResult:
    """Convenience function to analyze a ticker with default parameters.

    Args:
        ticker: Stock ticker symbol.
        short_window: Short SMA window size.
        long_window: Long SMA window size.
        start_date: Analysis start date in YYYY-MM-DD format.
        end_date: Analysis end date in YYYY-MM-DD format.

    Returns:
        Complete SMAC analysis results.
    """
    config = SMACConfig(
        ticker=ticker,
        short_window=short_window,
        long_window=long_window,
        start_date=start_date,
        end_date=end_date,
    )
    return run_smac_analysis(config)
