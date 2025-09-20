"""Tests for data fetching utilities."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
from yfinance.exceptions import YFRateLimitError

from smac.data import fetch_stock_data, validate_date_format, validate_ticker_symbol


class TestValidateTickerSymbol:
    """Tests for ticker symbol validation."""

    def test_valid_ticker_symbols(self) -> None:
        """Test that valid ticker symbols are accepted."""
        assert validate_ticker_symbol("AAPL") == "AAPL"
        assert validate_ticker_symbol("aapl") == "AAPL"
        assert validate_ticker_symbol(" msft ") == "MSFT"
        assert validate_ticker_symbol("BRK.B") == "BRK.B"

    def test_invalid_ticker_symbols(self) -> None:
        """Test that invalid ticker symbols raise errors."""
        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            validate_ticker_symbol("")

        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            validate_ticker_symbol(None)

        with pytest.raises(ValueError, match="Invalid ticker format"):
            validate_ticker_symbol("AA@PL")


class TestValidateDateFormat:
    """Tests for date format validation."""

    def test_valid_dates(self) -> None:
        """Test that valid dates pass validation."""
        assert validate_date_format("2023-01-01") is True
        assert validate_date_format("2020-12-31") is True

    def test_invalid_dates(self) -> None:
        """Test that invalid dates fail validation."""
        assert validate_date_format("2023-1-1") is False
        assert validate_date_format("01-01-2023") is False
        assert validate_date_format("invalid") is False
        assert validate_date_format("2023-13-01") is False


class TestFetchStockData:
    """Tests for stock data fetching."""

    @patch("smac.data.yf.download")
    def test_successful_data_fetch_multiindex(self, mock_download: Mock) -> None:
        """Test successful data fetching with MultiIndex columns (new format)."""
        # Mock MultiIndex response (new yfinance format)
        columns = pd.MultiIndex.from_tuples([
            ("Close", "AAPL"), ("Volume", "AAPL")
        ])
        mock_data = pd.DataFrame(
            [[100.0, 1000], [101.0, 1100], [102.0, 1200]],
            columns=columns,
            index=pd.date_range("2023-01-01", periods=3),
        )
        mock_download.return_value = mock_data

        result = fetch_stock_data("AAPL", "2023-01-01", "2023-01-03")

        assert len(result) == 3
        assert "price" in result.columns
        assert result["price"].iloc[0] == 100.0
        mock_download.assert_called_once_with(
            "AAPL", start="2023-01-01", end="2023-01-03", progress=False
        )

    @patch("smac.data.yf.download")
    def test_successful_data_fetch_legacy(self, mock_download: Mock) -> None:
        """Test successful data fetching with legacy single-level columns."""
        # Mock legacy single-level response
        mock_data = pd.DataFrame(
            {"Close": [100.0, 101.0, 102.0], "Volume": [1000, 1100, 1200]},
            index=pd.date_range("2023-01-01", periods=3),
        )
        mock_download.return_value = mock_data

        result = fetch_stock_data("AAPL", "2023-01-01", "2023-01-03")

        assert len(result) == 3
        assert "price" in result.columns
        assert result["price"].iloc[0] == 100.0

    @patch("smac.data.yf.download")
    def test_successful_data_fetch_adj_close_fallback(
        self, mock_download: Mock
    ) -> None:
        """Test successful data fetching with Adj Close fallback."""
        # Mock legacy response with Adj Close
        mock_data = pd.DataFrame(
            {"Adj Close": [100.0, 101.0, 102.0], "Volume": [1000, 1100, 1200]},
            index=pd.date_range("2023-01-01", periods=3),
        )
        mock_download.return_value = mock_data

        result = fetch_stock_data("AAPL", "2023-01-01", "2023-01-03")

        assert len(result) == 3
        assert "price" in result.columns
        assert result["price"].iloc[0] == 100.0

    @patch("smac.data.yf.download")
    def test_empty_data_raises_error(self, mock_download: Mock) -> None:
        """Test that empty data raises appropriate error."""
        mock_download.return_value = pd.DataFrame()

        with pytest.raises(ValueError, match="No data found for ticker AAPL"):
            fetch_stock_data("AAPL")

    @patch("smac.data.yf.download")
    def test_missing_close_columns_raises_error(self, mock_download: Mock) -> None:
        """Test that missing Close columns raises error."""
        mock_data = pd.DataFrame({"Open": [100.0, 101.0], "Volume": [1000, 1100]})
        mock_download.return_value = mock_data

        with pytest.raises(
            ValueError, match="Expected 'Close' or 'Adj Close' column not found"
        ):
            fetch_stock_data("AAPL")

    @patch("smac.data.yf.download")
    def test_missing_close_multiindex_raises_error(self, mock_download: Mock) -> None:
        """Test that missing Close column in MultiIndex raises error."""
        columns = pd.MultiIndex.from_tuples([("Open", "AAPL"), ("Volume", "AAPL")])
        mock_data = pd.DataFrame(
            [[100.0, 1000], [101.0, 1100]],
            columns=columns
        )
        mock_download.return_value = mock_data

        with pytest.raises(ValueError, match="Expected 'Close' column not found"):
            fetch_stock_data("AAPL")

    def test_invalid_ticker_raises_error(self) -> None:
        """Test that invalid ticker raises error."""
        with pytest.raises(ValueError, match="Ticker symbol cannot be empty"):
            fetch_stock_data("")

    @patch("smac.data.yf.download")
    def test_rate_limit_error_handling(self, mock_download: Mock) -> None:
        """Test that YFRateLimitError is properly converted to ConnectionError."""
        mock_download.side_effect = YFRateLimitError()

        with pytest.raises(ConnectionError, match="Rate limited by Yahoo Finance"):
            fetch_stock_data("AAPL")

    @patch("smac.data.yf.download")
    def test_generic_exception_handling(self, mock_download: Mock) -> None:
        """Test that generic exceptions are converted to ConnectionError."""
        mock_download.side_effect = Exception("Network error")

        with pytest.raises(ConnectionError, match="Unable to fetch data for AAPL"):
            fetch_stock_data("AAPL")
