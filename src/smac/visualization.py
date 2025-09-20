"""Visualization utilities for SMAC analysis.

This module provides functions for creating professional-quality plots
and summaries of SMAC analysis results. All visualization functions
are stateless and accept SMACResult objects as input.

Functions:
    create_smac_plot: Generate comprehensive SMAC analysis plot
    plot_analysis: Display or save SMAC analysis visualization
    create_summary_table: Generate analysis summary as DataFrame
    print_analysis_summary: Print formatted analysis summary
"""

from __future__ import annotations

import logging

import matplotlib.pyplot as plt
import pandas as pd

from smac.analysis import SMACResult

logger = logging.getLogger(__name__)


def create_smac_plot(
    result: SMACResult,
    figsize: tuple[int, int] = (12, 8),
    show_signals: bool = True,
) -> plt.Figure:
    """Create a comprehensive SMAC analysis plot.

    Args:
        result: SMAC analysis results.
        figsize: Figure size as (width, height).
        show_signals: Whether to show buy/sell signal markers.

    Returns:
        Matplotlib figure object.
    """
    logger.info("Creating SMAC plot for %s", result.config.ticker)

    fig, ax = plt.subplots(figsize=figsize)

    data = result.data
    ax.plot(data.index, data["price"], label="Price", linewidth=2, color="blue")
    ax.plot(
        data.index,
        data["short_sma"],
        label=f"SMA {result.config.short_window}",
        linewidth=1.5,
        color="orange",
        alpha=0.8,
    )
    ax.plot(
        data.index,
        data["long_sma"],
        label=f"SMA {result.config.long_window}",
        linewidth=1.5,
        color="red",
        alpha=0.8,
    )

    if show_signals:
        _add_signal_markers(ax, result)

    _customize_plot(ax, result)

    plt.tight_layout()
    logger.info("SMAC plot created successfully")

    return fig


def _add_signal_markers(ax: plt.Axes, result: SMACResult) -> None:
    """Add buy and sell signal markers to the plot.

    Args:
        ax: Matplotlib axes object.
        result: SMAC analysis results.
    """
    if not result.buy_signals.empty:
        ax.scatter(
            result.buy_signals.index,
            result.buy_signals["price"],
            marker="^",
            color="green",
            s=100,
            label=f"Buy ({result.num_buy_signals})",
            zorder=5,
            alpha=0.8,
        )

    if not result.sell_signals.empty:
        ax.scatter(
            result.sell_signals.index,
            result.sell_signals["price"],
            marker="v",
            color="red",
            s=100,
            label=f"Sell ({result.num_sell_signals})",
            zorder=5,
            alpha=0.8,
        )


def _customize_plot(ax: plt.Axes, result: SMACResult) -> None:
    """Customize plot appearance with labels, grid, etc.

    Args:
        ax: Matplotlib axes object.
        result: SMAC analysis results.
    """
    ax.set_title(
        f"SMAC Analysis: {result.config.ticker} "
        f"({result.config.short_window}/{result.config.long_window})",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price ($)", fontsize=12)

    ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
    ax.legend(loc="upper left", frameon=True, fancybox=True, shadow=True)

    fig = ax.get_figure()
    if fig is not None:
        fig.autofmt_xdate()


def plot_analysis(
    result: SMACResult,
    save_path: str | None = None,
    show: bool = True,
) -> plt.Figure | None:
    """Create and display/save SMAC analysis plot.

    Args:
        result: SMAC analysis results.
        save_path: Optional path to save the plot.
        show: Whether to display the plot.

    Returns:
        Figure object if not showing, None otherwise.
    """
    fig = create_smac_plot(result)

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        logger.info("Plot saved to %s", save_path)

    if show:
        plt.show()
        return None
    else:
        return fig


def create_summary_table(result: SMACResult) -> pd.DataFrame:
    """Create a summary table of SMAC analysis results.

    Args:
        result: SMAC analysis results.

    Returns:
        DataFrame containing summary statistics.
    """
    summary = result.summary()

    table_data = [
        ["Ticker", summary["ticker"]],
        ["Short Window", summary["short_window"]],
        ["Long Window", summary["long_window"]],
        ["Data Points", summary["data_points"]],
        ["Start Date", summary["date_range"]["start"]],
        ["End Date", summary["date_range"]["end"]],
        ["Buy Signals", summary["signals"]["buy"]],
        ["Sell Signals", summary["signals"]["sell"]],
    ]

    return pd.DataFrame(table_data, columns=["Metric", "Value"])


def print_analysis_summary(result: SMACResult) -> None:
    """Print a formatted summary of the analysis results.

    Args:
        result: SMAC analysis results.
    """
    summary = result.summary()
    print(f"\n{'=' * 50}")
    print(f"SMAC Analysis Summary: {summary['ticker']}")
    print(f"{'=' * 50}")
    print(f"Windows: {summary['short_window']}/{summary['long_window']} days")
    print(f"Period: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"Data Points: {summary['data_points']}")
    print(f"Buy Signals: {summary['signals']['buy']}")
    print(f"Sell Signals: {summary['signals']['sell']}")
    print(f"{'=' * 50}\n")
