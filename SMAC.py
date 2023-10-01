import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yfinance as yf


class DataFetcher:
    def __init__(self, ticker: str, start_date: str, end_date: str):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.fetch_data()

    def fetch_data(self) -> pd.DataFrame:
        """Fetch stock data using yfinance."""
        return yf.download(self.ticker, start=self.start_date, end=self.end_date)

    def set_time_range(self, start_date: str, end_date: str):
        """Set time range for the data."""
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.fetch_data()


class SignalCalculator:
    def __init__(self, data: pd.DataFrame, long_lb: int = 120, short_lb: int = 50):
        self.data = data
        self.long_lb = long_lb
        self.short_lb = short_lb
        self.signal_data = self.calculate_signals()

    def calculate_short_mav(self) -> pd.Series:
        """Calculate short moving average."""
        return (
            self.data["Adj Close"]
            .rolling(window=self.short_lb, center=False, min_periods=1)
            .mean()
        )

    def calculate_long_mav(self) -> pd.Series:
        """Calculate long moving average."""
        return (
            self.data["Adj Close"]
            .rolling(window=self.long_lb, center=False, min_periods=1)
            .mean()
        )

    def calculate_signals(self) -> pd.DataFrame:
        """Calculate buy/sell signals based on moving averages."""
        signal_df = pd.DataFrame(index=self.data.index)
        signal_df["short_mav"] = self.calculate_short_mav()
        signal_df["long_mav"] = self.calculate_long_mav()
        signal_df["signal"] = 0.0
        signal_df["signal"][self.short_lb :] = np.where(
            signal_df["short_mav"][self.short_lb :]
            > signal_df["long_mav"][self.short_lb :],
            1.0,
            0.0,
        )
        signal_df["positions"] = signal_df["signal"].diff()
        return signal_df


class StockPlotter:
    def __init__(self, data: pd.DataFrame, signal_data: pd.DataFrame):
        self.data = data
        self.signal_data = signal_data

    def setup_plot(self):
        """Setup plot style and size."""
        plt.figure(figsize=(12, 8))
        sns.set(context="notebook", style="darkgrid", palette="Blues_d")

    def plot_data(self, show_actual: bool = False):
        """Plot stock data and signals."""
        self.setup_plot()
        sns.lineplot(data=self.signal_data[["short_mav", "long_mav"]])
        if show_actual:
            plt.plot(self.data["Adj Close"])
        plt.plot(
            self.signal_data.loc[self.signal_data.positions == -1.0].index,
            self.signal_data.short_mav[self.signal_data.positions == -1.0],
            "v",
            markersize=10,
        )


class SMACStock:
    def __init__(self, ticker: str, start_date: str, end_date: str):
        self.data_fetcher = DataFetcher(ticker, start_date, end_date)
        self.signal_calculator = SignalCalculator(self.data_fetcher.data)
        self.stock_plotter = StockPlotter(
            self.data_fetcher.data, self.signal_calculator.signal_data
        )

    def run_analysis(self, show_actual: bool = False):
        """Run the entire analysis pipeline."""
        self.stock_plotter.plot_data(show_actual)
