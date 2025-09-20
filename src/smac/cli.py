"""Modern command-line interface for SMAC analysis using typer.

This module provides a user-friendly CLI with rich output formatting,
better error handling, and progress feedback.
"""

from __future__ import annotations

import logging
import typing
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from smac.analysis import analyze_ticker
from smac.data import validate_date_format
from smac.visualization import plot_analysis

if typing.TYPE_CHECKING:
    from smac.analysis import SMACResult

app = typer.Typer(
    name="smac",
    help="🔍 Simple Moving Average Crossover (SMAC) Analysis Tool",
    add_completion=False,
)

console = Console()
logger = logging.getLogger(__name__)


def version_callback(value: bool) -> None:
    """Show version information."""
    if value:
        from smac import __version__
        console.print(f"SMAC version: [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()


@app.command()
def analyze(
    ticker: Annotated[
        str,
        typer.Argument(
            help="Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)",
            show_default=False,
        ),
    ],
    short_window: Annotated[
        int,
        typer.Option(
            "--short-window",
            "-s",
            help="Short-term moving average window period",
            min=1,
            max=200,
        ),
    ] = 20,
    long_window: Annotated[
        int,
        typer.Option(
            "--long-window",
            "-l",
            help="Long-term moving average window period",
            min=2,
            max=500,
        ),
    ] = 50,
    start_date: Annotated[
        str | None,
        typer.Option(
            "--start-date",
            "-f",
            help="Start date for analysis (YYYY-MM-DD format). Defaults to 1 year ago.",
        ),
    ] = None,
    end_date: Annotated[
        str | None,
        typer.Option(
            "--end-date",
            "-t",
            help="End date for analysis (YYYY-MM-DD format). Defaults to today.",
        ),
    ] = None,
    save_path: Annotated[
        str | None,
        typer.Option(
            "--save",
            "-o",
            help="Path to save the analysis chart (optional)",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose logging output",
        ),
    ] = False,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version information",
        ),
    ] = None,
) -> None:
    """Analyze stock price trends using Simple Moving Average Crossover strategy.

    This tool fetches stock data and identifies buy/sell signals based on
    short and long-term moving average crossovers.
    """
    _setup_logging(verbose)

    # Validate inputs
    ticker = ticker.upper().strip()
    if not ticker:
        console.print("[red]❌ Error: Ticker symbol cannot be empty[/red]")
        raise typer.Exit(code=1)

    if short_window >= long_window:
        console.print(
            f"[red]❌ Error: Short window ({short_window}) must be smaller than "
            f"long window ({long_window})[/red]"
        )
        raise typer.Exit(code=1)

    # Validate dates
    if start_date and not validate_date_format(start_date):
        console.print("[red]❌ Error: Start date must be in YYYY-MM-DD format[/red]")
        raise typer.Exit(code=1)

    if end_date and not validate_date_format(end_date):
        console.print("[red]❌ Error: End date must be in YYYY-MM-DD format[/red]")
        raise typer.Exit(code=1)

    # Show analysis configuration
    _show_analysis_config(ticker, short_window, long_window, start_date, end_date)

    try:
        # Run analysis with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                "Fetching data and running analysis...", total=None
            )

            result = analyze_ticker(
                ticker=ticker,
                short_window=short_window,
                long_window=long_window,
                start_date=start_date,
                end_date=end_date,
            )

            progress.update(task, description="Generating visualization...")
            plot_analysis(result, save_path=save_path, show=True)

        # Show results summary
        _show_results_summary(result, save_path)

        console.print("\n[green]✅ Analysis completed successfully![/green]")
        logger.info("SMAC analysis completed successfully for %s", ticker)

    except ValueError as e:
        console.print(f"[red]❌ Data Error: {e}[/red]")
        logger.error("Data error during analysis: %s", str(e))
        raise typer.Exit(code=1) from None

    except ConnectionError as e:
        console.print(f"[red]❌ Connection Error: {e}[/red]")
        logger.error("Connection error during analysis: %s", str(e))
        raise typer.Exit(code=1) from None

    except Exception as e:
        console.print(f"[red]❌ Unexpected Error: {e}[/red]")
        logger.error("Unexpected error during analysis: %s", str(e))
        raise typer.Exit(code=1) from None


def _setup_logging(verbose: bool) -> None:
    """Configure logging for the CLI application.

    Args:
        verbose: Enable verbose logging if True.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(logs_dir / "smac_cli.log"),
            logging.StreamHandler() if verbose else logging.NullHandler(),
        ],
    )

    logger.info("Starting SMAC CLI analysis")


def _show_analysis_config(
    ticker: str,
    short_window: int,
    long_window: int,
    start_date: str | None,
    end_date: str | None,
) -> None:
    """Display analysis configuration in a nice table.

    Args:
        ticker: Stock ticker symbol.
        short_window: Short-term window period.
        long_window: Long-term window period.
        start_date: Analysis start date.
        end_date: Analysis end date.
    """
    table = Table(title=f"📊 SMAC Analysis Configuration for {ticker}")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="bold")

    table.add_row("Ticker Symbol", ticker)
    table.add_row("Short Window", f"{short_window} days")
    table.add_row("Long Window", f"{long_window} days")
    table.add_row("Start Date", start_date or "1 year ago")
    table.add_row("End Date", end_date or "Today")

    console.print("\n")
    console.print(table)
    console.print("")


def _show_results_summary(result: SMACResult, save_path: str | None = None) -> None:
    """Show analysis results summary.

    Args:
        result: SMAC analysis result object.
        save_path: Path where chart was saved, if any.
    """
    from smac.visualization import print_analysis_summary

    # Use the existing summary function
    print_analysis_summary(result)

    if save_path:
        console.print(f"📁 Chart saved to: [cyan]{save_path}[/cyan]")


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
