from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


class SMACAnalyzer:
    def __init__(self, ticker: str, short_window: int, long_window: int):
        self.ticker = ticker
        self.short_window = short_window
        self.long_window = long_window

    def fetch_data(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ):
        raw_data = yf.download(self.ticker, start=start_date, end=end_date)
        self.data = raw_data[["Adj Close"]].copy()
        self.data["Adj Close"] = pd.to_numeric(self.data["Adj Close"], errors="coerce")

    def calculate_sma(self):
        self.data["Short_SMA"] = (
            self.data["Adj Close"].rolling(window=self.short_window).mean()
        )
        self.data["Long_SMA"] = (
            self.data["Adj Close"].rolling(window=self.long_window).mean()
        )

    def identify_crossovers(self, sma_type: str = "Short_SMA"):
        self.data["Signal"] = 0.0
        self.data["Signal"][self.data["Adj Close"] > self.data[sma_type]] = 1.0
        self.data["Crossover"] = self.data["Signal"].diff()

    def plot_data(self, sma_type: str = "Short_SMA"):
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


if __name__ == "__main__":
    analyzer = SMACAnalyzer("AAPL", 40, 100)
    analyzer.fetch_data(start_date="2020-01-01", end_date="2021-01-01")
    analyzer.calculate_sma()
    analyzer.identify_crossovers()
    analyzer.plot_data()
