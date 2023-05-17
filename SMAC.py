import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
import seaborn as sns


class SMACStock:
    def __init__(self, ticker, long_lb=120, short_lb=50):
        self.ticker = ticker
        self.long_lb = long_lb
        self.short_lb = short_lb
        self.input_data = yf.download(self.ticker)
        self.signal_df = self.calculate_signals()

    def calculate_signals(self):
        signal_df = pd.DataFrame(index=self.input_data.index)
        signal_df["signal"] = 0.0
        signal_df["short_mav"] = (
            self.input_data["Adj Close"]
            .rolling(window=self.short_lb, center=False, min_periods=1)
            .mean()
        )
        signal_df["long_mav"] = (
            self.input_data["Adj Close"]
            .rolling(window=self.long_lb, center=False, min_periods=1)
            .mean()
        )
        signal_df["signal"][self.short_lb :] = np.where(
            signal_df["short_mav"][self.short_lb :]
            > signal_df["long_mav"][self.short_lb :],
            1.0,
            0.0,
        )
        signal_df["positions"] = signal_df["signal"].diff()
        return signal_df

    def plot(self, show_actual=False):
        plt.figure(figsize=(12, 8))
        sns.set(context="notebook", style="darkgrid", palette="Blues_d")
        plt1 = sns.lineplot(data=self.signal_df[["short_mav", "long_mav"]])
        if show_actual:
            plt1.plot(self.input_data["Adj Close"])
        plt1.plot(
            self.signal_df.loc[self.signal_df.positions == -1.0].index,
            self.signal_df.short_mav[self.signal_df.positions == -1.0],
            "v",
            markersize=10,
            color="k",
        )
        plt1.plot(
            self.signal_df.loc[self.signal_df.positions == 1.0].index,
            self.signal_df.short_mav[self.signal_df.positions == 1.0],
            "^",
            markersize=10,
            color="r",
        )
        plt.title(self.ticker)
        plt.show()


if __name__ == "__main__":
    ticker = input("Enter the ticker symbol: ")
    long_lb = int(input("Enter the long lookback period: "))
    short_lb = int(input("Enter the short lookback period: "))

    smac = SMACStock(ticker, long_lb=long_lb, short_lb=short_lb)
    smac.plot(show_actual=True)
