"""Data fetching and processing utilities for SMAC analysis.

This module provides functions for fetching stock price data from external sources
and validating input parameters. All functions are pure and stateless.

Functions:
    fetch_stock_data: Retrieve stock price data from Yahoo Finance
    validate_date_format: Validate date strings in YYYY-MM-DD format
    validate_ticker_symbol: Validate and normalize ticker symbols
"""

from __future__ import annotations

import logging
import sys
from contextlib import redirect_stderr
from datetime import datetime
from io import StringIO

import pandas as pd
import yfinance as yf
from yfinance.exceptions import YFRateLimitError

logger = logging.getLogger(__name__)


def fetch_stock_data(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """Fetch stock price data from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT').
        start_date: Start date in YYYY-MM-DD format. If None, uses yfinance default.
        end_date: End date in YYYY-MM-DD format. If None, uses yfinance default.

    Returns:
        DataFrame with adjusted close prices indexed by date.

    Raises:
        ValueError: If ticker is invalid or no data is retrieved.
        ConnectionError: If unable to connect to data source.
    """
    ticker = ticker.upper().strip()
    if not ticker:
        raise ValueError("Ticker symbol cannot be empty")

    logger.info(
        "Fetching data for %s from %s to %s",
        ticker,
        start_date or "default",
        end_date or "default",
    )

    try:
        raw_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if raw_data.empty:
            raise ValueError(f"No data found for ticker {ticker}")

        # Handle MultiIndex columns (new yfinance format)
        if isinstance(raw_data.columns, pd.MultiIndex):
            # Look for Close column (auto_adjust=True means Close is already adjusted)
            close_cols = [col for col in raw_data.columns if col[0] == "Close"]
            if not close_cols:
                raise ValueError(
                    f"Expected 'Close' column not found in data for {ticker}"
                )
            adjusted_close_data: pd.DataFrame = raw_data[close_cols].copy()
            adjusted_close_data.columns = ["price"]
        else:
            # Handle single-level columns (legacy format)
            if "Close" in raw_data.columns:
                adjusted_close_data: pd.DataFrame = raw_data[["Close"]].copy()
            elif "Adj Close" in raw_data.columns:
                adjusted_close_data: pd.DataFrame = raw_data[["Adj Close"]].copy()
            else:
                raise ValueError(
                    f"Expected 'Close' or 'Adj Close' column not found in data for {ticker}"
                )
            adjusted_close_data.columns = ["price"]

        logger.info(
            "Successfully fetched %d data points for %s",
            len(adjusted_close_data),
            ticker,
        )
        return adjusted_close_data

    except YFRateLimitError as e:
        logger.warning("Rate limited by Yahoo Finance for %s", ticker)
        raise ConnectionError(
            "Rate limited by Yahoo Finance. Please wait a moment and try again."
        ) from e
    except (ValueError, ConnectionError):
        # Re-raise ValueError and ConnectionError as-is
        raise
    except Exception as e:
        logger.error("Failed to fetch data for %s: %s", ticker, str(e))
        raise ConnectionError(f"Unable to fetch data for {ticker}: {str(e)}") from e


def validate_date_format(date_str: str) -> bool:
    """Validate that a date string is in YYYY-MM-DD format.

    Args:
        date_str: Date string to validate.

    Returns:
        True if date is valid, False otherwise.
    """
    # Check exact format YYYY-MM-DD (10 characters)
    if len(date_str) != 10:
        return False

    # Check pattern manually for strict validation
    if not (date_str[4] == "-" and date_str[7] == "-"):
        return False

    try:
        # Additional validation that it's a real date
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_ticker_symbol(ticker: str) -> str:
    """Validate and normalize a ticker symbol.

    Args:
        ticker: Raw ticker symbol.

    Returns:
        Normalized ticker symbol (uppercase, stripped).

    Raises:
        ValueError: If ticker is invalid.
    """
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker must be a non-empty string")

    ticker = ticker.upper().strip()
    if not ticker.isalnum():
        if not all(c.isalnum() or c in ".-" for c in ticker):
            raise ValueError(f"Invalid ticker format: {ticker}")

    return ticker
