"""Tests for the modern SMAC analysis functionality."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from smac.analysis import SMACConfig, SMACResult, analyze_ticker, run_smac_analysis


class TestSMACConfig:
    """Tests for SMACConfig dataclass."""

    def test_valid_config_creation(self) -> None:
        """Test creating valid configuration."""
        config = SMACConfig("AAPL", 20, 50)
        assert config.ticker == "AAPL"
        assert config.short_window == 20
        assert config.long_window == 50

    def test_invalid_window_periods(self) -> None:
        """Test that invalid window periods raise errors."""
        with pytest.raises(
            ValueError, match="Window periods must be positive integers"
        ):
            SMACConfig("AAPL", 0, 50)

        with pytest.raises(
            ValueError, match="Window periods must be positive integers"
        ):
            SMACConfig("AAPL", -10, 50)

    def test_short_window_larger_than_long(self) -> None:
        """Test that short >= long window raises error."""
        with pytest.raises(
            ValueError, match="Short window must be smaller than long window"
        ):
            SMACConfig("AAPL", 50, 20)

        with pytest.raises(
            ValueError, match="Short window must be smaller than long window"
        ):
            SMACConfig("AAPL", 30, 30)


class TestSMACResult:
    """Tests for SMACResult dataclass."""

    def create_sample_result(self) -> SMACResult:
        """Create a sample SMACResult for testing."""
        config = SMACConfig("AAPL", 5, 10)

        # Create sample data with some crossovers
        data = pd.DataFrame(
            {
                "price": [100, 101, 102, 99, 98, 103, 105, 104, 106, 107],
                "short_sma": [
                    100,
                    100.5,
                    101,
                    100.5,
                    100,
                    100.5,
                    101.5,
                    102.5,
                    103,
                    104,
                ],
                "long_sma": [
                    100,
                    100.2,
                    100.5,
                    100.3,
                    100.1,
                    100.3,
                    100.8,
                    101.2,
                    101.8,
                    102.5,
                ],
                "signal": [0, 1, 1, 0, 0, 1, 1, 1, 1, 1],
                "crossover": [0, 1, 0, -1, 0, 1, 0, 0, 0, 0],
            },
            index=pd.date_range("2023-01-01", periods=10),
        )

        buy_signals = data[data["crossover"] == 1.0]
        sell_signals = data[data["crossover"] == -1.0]

        return SMACResult(config, data, buy_signals, sell_signals)

    def test_result_properties(self) -> None:
        """Test SMACResult properties."""
        result = self.create_sample_result()

        assert result.num_buy_signals == 2
        assert result.num_sell_signals == 1

        start_date, end_date = result.date_range
        assert start_date == pd.Timestamp("2023-01-01")
        assert end_date == pd.Timestamp("2023-01-10")

    def test_result_summary(self) -> None:
        """Test SMACResult summary method."""
        result = self.create_sample_result()
        summary = result.summary()

        assert summary["ticker"] == "AAPL"
        assert summary["short_window"] == 5
        assert summary["long_window"] == 10
        assert summary["data_points"] == 10
        assert summary["signals"]["buy"] == 2
        assert summary["signals"]["sell"] == 1


class TestAnalysisFunctions:
    """Tests for analysis functions."""

    @patch("smac.analysis.fetch_stock_data")
    @patch("smac.analysis.calculate_dual_sma")
    @patch("smac.analysis.identify_crossover_signals")
    def test_run_smac_analysis(
        self, mock_signals: Mock, mock_sma: Mock, mock_fetch: Mock
    ) -> None:
        """Test the run_smac_analysis function."""
        # Setup mocks
        mock_stock_data = pd.DataFrame({"price": [100, 101, 102]})
        mock_sma_data = mock_stock_data.copy()
        mock_sma_data["short_sma"] = [100, 100.5, 101]
        mock_sma_data["long_sma"] = [100, 100.2, 100.5]

        mock_analysis_data = mock_sma_data.copy()
        mock_analysis_data["signal"] = [0, 1, 1]
        mock_analysis_data["crossover"] = [0, 1, 0]

        mock_fetch.return_value = mock_stock_data
        mock_sma.return_value = mock_sma_data
        mock_signals.return_value = mock_analysis_data

        config = SMACConfig("AAPL", 5, 10)
        result = run_smac_analysis(config)

        assert isinstance(result, SMACResult)
        assert result.config == config
        assert len(result.data) == 3

        # Verify function calls
        mock_fetch.assert_called_once_with("AAPL", None, None)
        mock_sma.assert_called_once_with(mock_stock_data, 5, 10)
        mock_signals.assert_called_once_with(mock_sma_data)

    @patch("smac.analysis.run_smac_analysis")
    def test_analyze_ticker_convenience_function(self, mock_run_analysis: Mock) -> None:
        """Test the analyze_ticker convenience function."""
        mock_result = Mock(spec=SMACResult)
        mock_run_analysis.return_value = mock_result

        result = analyze_ticker("AAPL", 20, 50, "2023-01-01", "2023-12-31")

        assert result == mock_result

        # Verify the config was created correctly
        call_args = mock_run_analysis.call_args[0][0]
        assert call_args.ticker == "AAPL"
        assert call_args.short_window == 20
        assert call_args.long_window == 50
        assert call_args.start_date == "2023-01-01"
        assert call_args.end_date == "2023-12-31"
