"""Technical indicators for SMAC analysis.

This module contains pure functions for calculating technical indicators
and identifying trading signals. All functions operate on pandas DataFrames
and return new DataFrames without modifying input data.

Functions:
    calculate_sma: Calculate Simple Moving Average for a given window
    calculate_dual_sma: Calculate both short and long SMAs
    identify_crossover_signals: Identify price/SMA crossover points
    get_crossover_points: Extract buy/sell signal points from analysis
"""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def calculate_sma(data: pd.DataFrame, window: int, column: str = "price") -> pd.Series:
    """Calculate Simple Moving Average for a given window.

    Args:
        data: DataFrame containing price data.
        window: Window size for SMA calculation.
        column: Column name to calculate SMA for.

    Returns:
        Series containing SMA values.

    Raises:
        ValueError: If window is invalid or insufficient data.
    """
    if window <= 0:
        raise ValueError(f"Window must be positive, got {window}")

    if len(data) < window:
        raise ValueError(
            f"Insufficient data points ({len(data)}) for window ({window})"
        )

    if column not in data.columns:
        raise ValueError(f"Column '{column}' not found in data")

    logger.debug("Calculating SMA with window %d for %d data points", window, len(data))
    return data[column].rolling(window=window).mean()


def calculate_dual_sma(
    data: pd.DataFrame, short_window: int, long_window: int, column: str = "price"
) -> pd.DataFrame:
    """Calculate both short and long SMAs for the data.

    Args:
        data: DataFrame containing price data.
        short_window: Window size for short SMA.
        long_window: Window size for long SMA.
        column: Column name to calculate SMAs for.

    Returns:
        DataFrame with original data plus short and long SMAs.

    Raises:
        ValueError: If windows are invalid.
    """
    if short_window >= long_window:
        raise ValueError("Short window must be smaller than long window")

    logger.info("Calculating dual SMAs with windows %d/%d", short_window, long_window)

    result = data.copy()
    result["short_sma"] = calculate_sma(data, short_window, column)
    result["long_sma"] = calculate_sma(data, long_window, column)

    logger.info("Successfully calculated dual SMAs")
    return result


def identify_crossover_signals(
    data: pd.DataFrame,
    price_col: str = "price",
    sma_col: str = "short_sma",
) -> pd.DataFrame:
    """Identify crossover signals where price crosses above/below SMA.

    Args:
        data: DataFrame containing price and SMA data.
        price_col: Column name for price data.
        sma_col: Column name for SMA data to compare against.

    Returns:
        DataFrame with added signal and crossover columns.

    Raises:
        ValueError: If required columns are missing.
    """
    required_cols = [price_col, sma_col]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    logger.info("Identifying crossover signals using %s vs %s", price_col, sma_col)

    result = data.copy()

    result["signal"] = (result[price_col] > result[sma_col]).astype(float)

    result["crossover"] = result["signal"].diff()

    buy_signals = (result["crossover"] == 1.0).sum()
    sell_signals = (result["crossover"] == -1.0).sum()

    logger.info(
        "Identified %d buy signals and %d sell signals", buy_signals, sell_signals
    )
    return result


def get_crossover_points(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extract buy and sell signal points from crossover data.

    Args:
        data: DataFrame containing crossover analysis.

    Returns:
        Tuple of (buy_signals, sell_signals) DataFrames.

    Raises:
        ValueError: If crossover column is missing.
    """
    if "crossover" not in data.columns:
        raise ValueError("Crossover analysis must be performed first")

    buy_signals = data[data["crossover"] == 1.0].copy()
    sell_signals = data[data["crossover"] == -1.0].copy()

    return buy_signals, sell_signals
