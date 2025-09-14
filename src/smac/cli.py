"""Command-line interface for SMAC analysis.

This module provides a command-line interface that uses the modern functional
API internally while maintaining backward compatibility with the original
CLI arguments and behavior.

Functions:
    parse_args: Parse command line arguments
    validate_args: Validate parsed arguments
    main: Main CLI entry point
"""

import argparse
import logging
import sys
from datetime import datetime

from smac.analysis import analyze_ticker
from smac.visualization import plot_analysis

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Simple Moving Average Crossover (SMAC) Analysis"
    )

    parser.add_argument(
        "ticker", type=str, help="Stock ticker symbol (e.g., AAPL, MSFT, GOOG)"
    )

    parser.add_argument(
        "--short-window",
        "-s",
        type=int,
        default=20,
        help="Short window period for SMA calculation (default: 20)",
    )

    parser.add_argument(
        "--long-window",
        "-l",
        type=int,
        default=50,
        help="Long window period for SMA calculation (default: 50)",
    )

    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date for analysis (format: YYYY-MM-DD, default: 1 year ago)",
    )

    parser.add_argument(
        "--end-date",
        type=str,
        help="End date for analysis (format: YYYY-MM-DD, default: today)",
    )

    parser.add_argument(
        "--sma-type",
        type=str,
        default="Short_SMA",
        choices=["Short_SMA", "Long_SMA"],
        help="SMA type to use for crossover identification (default: Short_SMA)",
    )

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> bool:
    """Validate command line arguments.

    Args:
        args: Parsed command line arguments.

    Returns:
        True if all arguments are valid, False otherwise.
    """
    if args.short_window <= 0:
        logger.error(
            "Short window must be a positive integer, got: %d", args.short_window
        )
        print("Error: Short window must be a positive integer")
        return False

    if args.long_window <= 0:
        logger.error(
            "Long window must be a positive integer, got: %d", args.long_window
        )
        print("Error: Long window must be a positive integer")
        return False

    if args.short_window >= args.long_window:
        logger.error(
            "Short window (%d) must be smaller than long window (%d)",
            args.short_window,
            args.long_window,
        )
        print("Error: Short window must be smaller than long window")
        return False

    if args.start_date and not _is_valid_date(args.start_date):
        logger.error("Invalid start date format: %s", args.start_date)
        print("Error: Start date must be in YYYY-MM-DD format")
        return False

    if args.end_date and not _is_valid_date(args.end_date):
        logger.error("Invalid end date format: %s", args.end_date)
        print("Error: End date must be in YYYY-MM-DD format")
        return False

    return True


def _is_valid_date(date_string: str) -> bool:
    """Check if date string is in valid YYYY-MM-DD format.

    Args:
        date_string: Date string to validate.

    Returns:
        True if valid date format, False otherwise.
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def main() -> None:
    """Main function to run the SMAC analysis from command line."""
    _setup_logging()
    logger.info("Starting SMAC CLI analysis")

    args = parse_args()

    if not validate_args(args):
        logger.error("Argument validation failed")
        sys.exit(1)

    try:
        _run_analysis(args)
        logger.info("SMAC analysis completed successfully")

    except Exception as e:
        logger.error("Analysis failed: %s", str(e))
        print(f"Error: {e}")
        sys.exit(1)


def _setup_logging() -> None:
    """Configure logging for the CLI application."""
    import os

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("logs/smac_cli.log"), logging.StreamHandler()],
    )


def _run_analysis(args: argparse.Namespace) -> None:
    """Execute the complete SMAC analysis workflow.

    Args:
        args: Command line arguments.
    """
    result = analyze_ticker(
        ticker=args.ticker,
        short_window=args.short_window,
        long_window=args.long_window,
        start_date=args.start_date,
        end_date=args.end_date,
    )

    logger.debug(
        "Using functional API for analysis "
        "(sma_type parameter ignored for compatibility)"
    )
    plot_analysis(result, show=True)


if __name__ == "__main__":
    main()
