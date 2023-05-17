from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yfinance as yf


class SMACStock:
    def __init__(self, ticker, start_date, end_date, long_lb=120, short_lb=50):
        self.ticker = ticker
        self.long_lb = long_lb
        self.short_lb = short_lb
        self.input_data = yf.download(self.ticker, start=start_date, end=end_date)
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
    long_lb = input("Enter the long lookback period (default is 200): ")
    short_lb = input("Enter the short lookback period (default is 50): ")
    show_actual = input(
        "Display actual price? Enter 0 for No, 1 for Yes (default is Yes): "
    )

    long_lb = 200 if long_lb == "" else int(long_lb)
    short_lb = 50 if short_lb == "" else int(short_lb)
    show_actual = True if show_actual == "" or int(show_actual) else False

    print("Choose a time range for the stock data:")
    print("1. 1 Month")
    print("2. 3 Months")
    print("3. 6 Months")
    print("4. 1 Year")
    print("5. 3 Years")
    print("6. 5 Years")

    time_range = int(input("Enter the number corresponding to your choice: "))

    end_date = datetime.now()
    if time_range == 1:
        start_date = end_date - timedelta(days=30)
    elif time_range == 2:
        start_date = end_date - timedelta(days=90)
    elif time_range == 3:
        start_date = end_date - timedelta(days=180)
    elif time_range == 4:
        start_date = end_date - timedelta(days=365)
    elif time_range == 5:
        start_date = end_date - timedelta(days=3 * 365)
    elif time_range == 6:
        start_date = end_date - timedelta(days=5 * 365)
    else:
        print("Invalid choice. Defaulting to 1 year data.")
        start_date = end_date - timedelta(days=365)

    smac = SMACStock(ticker, start_date, end_date, long_lb=long_lb, short_lb=short_lb)
    smac.plot(show_actual=show_actual)
