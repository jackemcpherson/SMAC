"""Tests for the SMACAnalyzer class."""

import pandas as pd
import pytest

from smac.analyzer import SMACAnalyzer


@pytest.fixture
def sample_analyzer() -> SMACAnalyzer:
    """Create a sample SMACAnalyzer for testing.

    Returns:
        SMACAnalyzer instance configured for AAPL with 40/100 day windows.
    """
    return SMACAnalyzer("AAPL", 40, 100)


def test_analyzer_initialization() -> None:
    """Test SMACAnalyzer initialization with various parameters."""
    analyzer = SMACAnalyzer("MSFT", 20, 50)
    assert analyzer.ticker == "MSFT"
    assert analyzer.short_window == 20
    assert analyzer.long_window == 50
    assert analyzer.data is None


def test_analyzer_initialization_validation() -> None:
    """Test SMACAnalyzer initialization validation."""
    with pytest.raises(ValueError, match="Window periods must be positive integers"):
        SMACAnalyzer("AAPL", -1, 50)

    with pytest.raises(
        ValueError, match="Short window must be smaller than long window"
    ):
        SMACAnalyzer("AAPL", 50, 20)


def test_fetch_data(sample_analyzer: SMACAnalyzer) -> None:
    """Test data fetching functionality.

    Args:
        sample_analyzer: SMACAnalyzer fixture.
    """
    sample_analyzer.fetch_data(start_date="2020-01-01", end_date="2020-01-10")
    assert "Adj Close" in sample_analyzer.data.columns
    assert isinstance(sample_analyzer.data, pd.DataFrame)


def test_calculate_sma(sample_analyzer: SMACAnalyzer) -> None:
    """Test SMA calculation functionality.

    Args:
        sample_analyzer: SMACAnalyzer fixture.
    """
    sample_analyzer.fetch_data(start_date="2020-01-01", end_date="2020-01-10")
    sample_analyzer.calculate_sma()
    assert "Short_SMA" in sample_analyzer.data.columns
    assert "Long_SMA" in sample_analyzer.data.columns


def test_calculate_sma_without_data() -> None:
    """Test that SMA calculation fails without data."""
    analyzer = SMACAnalyzer("AAPL", 20, 50)
    with pytest.raises(
        RuntimeError, match="Data must be fetched before calculating SMAs"
    ):
        analyzer.calculate_sma()


def test_identify_crossovers(sample_analyzer: SMACAnalyzer) -> None:
    """Test crossover identification functionality.

    Args:
        sample_analyzer: SMACAnalyzer fixture.
    """
    sample_analyzer.fetch_data(start_date="2020-01-01", end_date="2020-01-10")
    sample_analyzer.calculate_sma()
    sample_analyzer.identify_crossovers()
    assert "Signal" in sample_analyzer.data.columns
    assert "Crossover" in sample_analyzer.data.columns


def test_identify_crossovers_without_sma() -> None:
    """Test that crossover identification fails without SMAs."""
    analyzer = SMACAnalyzer("AAPL", 20, 50)
    with pytest.raises(
        RuntimeError, match="SMAs must be calculated before identifying crossovers"
    ):
        analyzer.identify_crossovers()


def test_identify_crossovers_invalid_sma_type(sample_analyzer: SMACAnalyzer) -> None:
    """Test crossover identification with invalid SMA type.

    Args:
        sample_analyzer: SMACAnalyzer fixture.
    """
    sample_analyzer.fetch_data(start_date="2020-01-01", end_date="2020-01-10")
    sample_analyzer.calculate_sma()

    with pytest.raises(ValueError, match="Invalid sma_type"):
        sample_analyzer.identify_crossovers(sma_type="Invalid_SMA")


def test_date_range(sample_analyzer: SMACAnalyzer) -> None:
    """Test that fetched data respects date range parameters.

    Args:
        sample_analyzer: SMACAnalyzer fixture.
    """
    sample_analyzer.fetch_data(start_date="2020-01-01", end_date="2020-01-10")
    assert sample_analyzer.data.index.min() >= pd.Timestamp("2020-01-01")
    assert sample_analyzer.data.index.max() <= pd.Timestamp("2020-01-10")
