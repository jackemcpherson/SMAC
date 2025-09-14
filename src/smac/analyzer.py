import logging
from typing import Optional

import matplotlib.pyplot as plt
import yfinance as yf

logger = logging.getLogger(__name__)


class SMACAnalyzer:
    def __init__(self, ticker: str, short_window: int, long_window: int) -> None:
        """
        Initialize the SMACAnalyzer object with basic configurations.

        Args:
            ticker: The stock ticker symbol.
            short_window: The short window period for SMA calculation.
            long_window: The long window period for SMA calculation.

        Raises:
            ValueError: If windows are not positive integers or short >= long.
        """
        if short_window <= 0 or long_window <= 0:
            raise ValueError("Window periods must be positive integers")
        if short_window >= long_window:
            raise ValueError("Short window must be smaller than long window")

        self.ticker = ticker.upper()
        self.short_window = short_window
        self.long_window = long_window
        self.data = None

        logger.info(
            "Initialized SMACAnalyzer for %s with windows %d/%d",
            self.ticker,
            short_window,
            long_window,
        )

    def fetch_data(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> None:
        """
        Fetch stock data for the given date range.

        Args:
            start_date: Start date in YYYY-MM-DD format. If None, uses yfinance default.
            end_date: End date in YYYY-MM-DD format. If None, uses yfinance default.

        Raises:
            ValueError: If no data is retrieved or data is invalid.
            ConnectionError: If unable to connect to data source.
        """
        logger.info(
            "Fetching data for %s from %s to %s",
            self.ticker,
            start_date or "default",
            end_date or "default",
        )

        try:
            raw_data = yf.download(
                self.ticker, start=start_date, end=end_date, progress=False
            )

            if raw_data.empty:
                raise ValueError(f"No data found for ticker {self.ticker}")

            if "Adj Close" not in raw_data.columns:
                raise ValueError(
                    f"Expected 'Adj Close' column not found in data for {self.ticker}"
                )

            self.data = raw_data[["Adj Close"]].copy()

            logger.info(
                "Successfully fetched %d data points for %s",
                len(self.data),
                self.ticker,
            )

        except Exception as e:
            logger.error("Failed to fetch data for %s: %s", self.ticker, str(e))
            raise ConnectionError(
                f"Unable to fetch data for {self.ticker}: {str(e)}"
            ) from e

    def calculate_sma(self) -> None:
        """
        Calculate the Simple Moving Averages for the stock data.

        Raises:
            RuntimeError: If data has not been fetched yet.
            ValueError: If insufficient data points for SMA calculation.
        """
        if self.data is None:
            raise RuntimeError("Data must be fetched before calculating SMAs")

        if len(self.data) < self.long_window:
            raise ValueError(
                f"Insufficient data points ({len(self.data)}) for long window ({self.long_window})"
            )

        logger.info(
            "Calculating SMAs with windows %d/%d", self.short_window, self.long_window
        )

        self.data["Short_SMA"] = (
            self.data["Adj Close"].rolling(window=self.short_window).mean()
        )
        self.data["Long_SMA"] = (
            self.data["Adj Close"].rolling(window=self.long_window).mean()
        )

        logger.info("Successfully calculated SMAs")

    def identify_crossovers(self, sma_type: str = "Short_SMA") -> None:
        """
        Identify crossover events based on the SMA type.

        Args:
            sma_type: The type of SMA to use for crossover detection.
                     Must be either 'Short_SMA' or 'Long_SMA'.

        Raises:
            RuntimeError: If SMAs have not been calculated yet.
            ValueError: If sma_type is not valid.
        """
        if self.data is None or "Short_SMA" not in self.data.columns:
            raise RuntimeError("SMAs must be calculated before identifying crossovers")

        if sma_type not in ["Short_SMA", "Long_SMA"]:
            raise ValueError(
                f"Invalid sma_type: {sma_type}. Must be 'Short_SMA' or 'Long_SMA'"
            )

        logger.info("Identifying crossovers using %s", sma_type)

        self.data["Signal"] = 0.0
        mask = self.data["Adj Close"] > self.data[sma_type]
        self.data.loc[mask, "Signal"] = 1.0
        self.data["Crossover"] = self.data["Signal"].diff()

        buy_signals = (self.data["Crossover"] == 1.0).sum()
        sell_signals = (self.data["Crossover"] == -1.0).sum()

        logger.info(
            "Identified %d buy signals and %d sell signals", buy_signals, sell_signals
        )

    def plot_data(self, sma_type: str = "Short_SMA") -> None:
        """
        Plot the stock data along with the SMA lines and crossover markers.

        Args:
            sma_type: The type of SMA to use for crossover display.
                     Must be either 'Short_SMA' or 'Long_SMA'.

        Raises:
            RuntimeError: If crossovers have not been identified yet.
            ValueError: If sma_type is not valid.
        """
        if self.data is None or "Crossover" not in self.data.columns:
            raise RuntimeError("Crossovers must be identified before plotting")

        if sma_type not in ["Short_SMA", "Long_SMA"]:
            raise ValueError(
                f"Invalid sma_type: {sma_type}. Must be 'Short_SMA' or 'Long_SMA'"
            )

        logger.info("Creating plot for %s with %s crossovers", self.ticker, sma_type)

        self._create_base_plot()
        self._add_signal_markers()
        self._finalize_plot()

        logger.info("Plot created successfully")

    def _create_base_plot(self) -> None:
        """Create the base plot with price and SMA lines."""
        plt.figure(figsize=(12, 6))
        plt.plot(self.data["Adj Close"], label="Price", linewidth=1.5)
        plt.plot(
            self.data["Short_SMA"],
            label=f"Short {self.short_window} Days SMA",
            linewidth=1,
        )
        plt.plot(
            self.data["Long_SMA"],
            label=f"Long {self.long_window} Days SMA",
            linewidth=1,
        )

    def _add_signal_markers(self) -> None:
        """Add buy and sell signal markers to the plot."""
        buy_signals = self.data[self.data["Crossover"] == 1.0]
        sell_signals = self.data[self.data["Crossover"] == -1.0]

        if not buy_signals.empty:
            plt.scatter(
                buy_signals.index,
                buy_signals["Adj Close"],
                marker="^",
                color="green",
                label="Buy Signal",
                s=60,
                zorder=5,
            )

        if not sell_signals.empty:
            plt.scatter(
                sell_signals.index,
                sell_signals["Adj Close"],
                marker="v",
                color="red",
                label="Sell Signal",
                s=60,
                zorder=5,
            )

    def _finalize_plot(self) -> None:
        """Add labels, title, and display the plot."""
        plt.title(f"SMAC Analysis for {self.ticker}", fontsize=14, fontweight="bold")
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Price ($)", fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
