from SMAC import SMACStock

if __name__ == "__main__":
    stock_ticker = input("Ticker: ")
    SMACStock.plot(ticker=stock_ticker)
