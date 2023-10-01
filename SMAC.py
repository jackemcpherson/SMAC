import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


class SMACAnalyzer:
    def __init__(self, ticker: str, short_window: int, long_window: int):
        self.ticker = ticker
        self.short_window = short_window
        self.long_window = long_window

    def fetch_data(self):
        raw_data = yf.download(self.ticker)
        self.data = raw_data[
            ["Adj Close"]
        ].copy()  # Use a copy to avoid SettingWithCopyWarning
        self.data["Adj Close"] = pd.to_numeric(
            self.data["Adj Close"], errors="coerce"
        )  # Convert to numeric

    def calculate_sma(self):
        self.data["Short_SMA"] = (
            self.data["Adj Close"].rolling(window=self.short_window).mean()
        )
        self.data["Long_SMA"] = (
            self.data["Adj Close"].rolling(window=self.long_window).mean()
        )

    def plot_data(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.data["Adj Close"], label="Price")
        plt.plot(self.data["Short_SMA"], label=f"Short {self.short_window} Days SMA")
        plt.plot(self.data["Long_SMA"], label=f"Long {self.long_window} Days SMA")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    analyzer = SMACAnalyzer("AAPL", 40, 100)
    analyzer.fetch_data()
    analyzer.calculate_sma()
    analyzer.plot_data()
