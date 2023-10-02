from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


class SMACAnalyzer:
    def __init__(self, ticker: str, short_window: int, long_window: int) -> None:
        """
        Initialize the SMACAnalyzer object with basic configurations.

        Parameters:
            ticker (str): The stock ticker.
            short_window (int): The short window period for SMA.
            long_window (int): The long window period for SMA.
        """
        self.ticker = ticker
        self.short_window = short_window
        self.long_window = long_window

    def fetch_data(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> None:
        """
        Fetch stock data for the given date range.

        Parameters:
            start_date (Optional[str]): The start date for data fetching.
            end_date (Optional[str]): The end date for data fetching.

        Returns:
            None
        """
        raw_data = yf.download(self.ticker, start=start_date, end=end_date)
        self.data = raw_data[["Adj Close"]].copy()
        self.data["Adj Close"] = pd.to_numeric(self.data["Adj Close"], errors="coerce")

    def calculate_sma(self) -> None:
        """
        Calculate the Simple Moving Averages for the stock data.

        Parameters:
            None

        Returns:
            None
        """
        self.data["Short_SMA"] = (
            self.data["Adj Close"].rolling(window=self.short_window).mean()
        )
        self.data["Long_SMA"] = (
            self.data["Adj Close"].rolling(window=self.long_window).mean()
        )

    def identify_crossovers(self, sma_type: str = "Short_SMA") -> None:
        """
        Identify crossover events based on the SMA type.

        Parameters:
            sma_type (str): The type of SMA to use ('Short_SMA' or 'Long_SMA').

        Returns:
            None
        """
        self.data["Signal"] = 0.0
        self.data["Signal"][self.data["Adj Close"] > self.data[sma_type]] = 1.0
        self.data["Crossover"] = self.data["Signal"].diff()

    def plot_data(self, sma_type: str = "Short_SMA") -> None:
        """
        Plot the stock data along with the SMA lines and crossover markers.

        Parameters:
            sma_type (str): The type of SMA to use ('Short_SMA' or 'Long_SMA').

        Returns:
            None
        """
        plt.figure(figsize=(12, 6))
        plt.plot(self.data["Adj Close"], label="Price")
        plt.plot(self.data["Short_SMA"], label=f"Short {self.short_window} Days SMA")
        plt.plot(self.data["Long_SMA"], label=f"Long {self.long_window} Days SMA")

        if sma_type in self.data.columns:
            buy_signals = self.data[self.data["Crossover"] == 1.0]
            sell_signals = self.data[self.data["Crossover"] == -1.0]
            plt.scatter(
                buy_signals.index,
                buy_signals["Adj Close"],
                marker="^",
                color="g",
                label="Buy Signal",
                alpha=1,
            )
            plt.scatter(
                sell_signals.index,
                sell_signals["Adj Close"],
                marker="v",
                color="r",
                label="Sell Signal",
                alpha=1,
            )

        plt.legend()
        plt.show()
