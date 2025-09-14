"""Legacy compatibility layer for the old SMACAnalyzer class interface.

This module provides backward compatibility with the original stateful
SMACAnalyzer class while using the modern functional implementation
internally. New code should use the functional API directly.

Classes:
    SMACAnalyzer: Compatibility wrapper maintaining the old interface
"""

from __future__ import annotations

import logging

from smac.analysis import SMACConfig, run_smac_analysis
from smac.visualization import plot_analysis

logger = logging.getLogger(__name__)


class SMACAnalyzer:
    """Legacy compatibility wrapper for the old stateful SMACAnalyzer interface.

    This class maintains backward compatibility with the old API while using
    the modern functional implementation under the hood.

    For new code, use the functional API in smac.analysis directly.
    """

    def __init__(self, ticker: str, short_window: int, long_window: int) -> None:
        """Initialize the SMACAnalyzer with configuration parameters.

        Args:
            ticker: Stock ticker symbol.
            short_window: Short window period for SMA calculation.
            long_window: Long window period for SMA calculation.

        Raises:
            ValueError: If windows are invalid.
        """
        self._config = SMACConfig(
            ticker=ticker,
            short_window=short_window,
            long_window=long_window,
        )
        self._result = None

        # Legacy properties for backward compatibility
        self.ticker = self._config.ticker
        self.short_window = self._config.short_window
        self.long_window = self._config.long_window
        self.data = None

        logger.info(
            "Initialized legacy SMACAnalyzer for %s with windows %d/%d",
            self.ticker,
            short_window,
            long_window,
        )

    def fetch_data(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> None:
        """Fetch stock data and run the complete analysis.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
        """
        config = SMACConfig(
            ticker=self._config.ticker,
            short_window=self._config.short_window,
            long_window=self._config.long_window,
            start_date=start_date,
            end_date=end_date,
        )

        self._result = run_smac_analysis(config)

        # Set legacy data attribute for backward compatibility
        self.data = self._result.data.copy()
        # Rename columns to match old format
        self.data = self.data.rename(
            columns={
                "price": "Adj Close",
                "short_sma": "Short_SMA",
                "long_sma": "Long_SMA",
                "signal": "Signal",
                "crossover": "Crossover",
            }
        )

    def calculate_sma(self) -> None:
        """Calculate SMAs - no-op since this is done automatically in fetch_data."""
        if self._result is None:
            raise RuntimeError("Data must be fetched before calculating SMAs")
        logger.debug("SMAs already calculated during data fetch")

    def identify_crossovers(self, sma_type: str = "Short_SMA") -> None:
        """Identify crossovers - no-op since this is done automatically in fetch_data.

        Args:
            sma_type: Legacy parameter for compatibility (ignored).
        """
        if self._result is None:
            raise RuntimeError("SMAs must be calculated before identifying crossovers")
        logger.debug("Crossovers already identified during data fetch")

    def plot_data(self, sma_type: str = "Short_SMA") -> None:
        """Plot the SMAC analysis results.

        Args:
            sma_type: Legacy parameter for compatibility (ignored).
        """
        if self._result is None:
            raise RuntimeError("Analysis must be completed before plotting")

        plot_analysis(self._result, show=True)

    @property
    def result(self):
        """Access to the modern SMACResult object."""
        return self._result
