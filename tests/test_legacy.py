"""Tests for backward compatibility with the legacy SMACAnalyzer interface."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from smac.analysis import SMACConfig, SMACResult
from smac.legacy import SMACAnalyzer


class TestLegacySMACAnalyzer:
    """Tests for the legacy SMACAnalyzer compatibility wrapper."""

    def test_initialization(self) -> None:
        """Test that legacy initialization works correctly."""
        analyzer = SMACAnalyzer("AAPL", 20, 50)

        assert analyzer.ticker == "AAPL"
        assert analyzer.short_window == 20
        assert analyzer.long_window == 50
        assert analyzer.data is None

    def test_initialization_validation(self) -> None:
        """Test that initialization validation still works."""
        with pytest.raises(
            ValueError, match="Window periods must be positive integers"
        ):
            SMACAnalyzer("AAPL", -1, 50)

        with pytest.raises(
            ValueError, match="Short window must be smaller than long window"
        ):
            SMACAnalyzer("AAPL", 50, 20)

    @patch("smac.legacy.run_smac_analysis")
    def test_fetch_data_runs_complete_analysis(self, mock_run_analysis: Mock) -> None:
        """Test that fetch_data runs the complete modern analysis."""
        # Create mock result
        config = SMACConfig("AAPL", 20, 50)
        sample_data = pd.DataFrame(
            {
                "price": [100, 101, 102],
                "short_sma": [100, 100.5, 101],
                "long_sma": [100, 100.2, 100.5],
                "signal": [0, 1, 1],
                "crossover": [0, 1, 0],
            },
            index=pd.date_range("2023-01-01", periods=3),
        )

        buy_signals = sample_data[sample_data["crossover"] == 1.0]
        sell_signals = sample_data[sample_data["crossover"] == -1.0]

        mock_result = SMACResult(config, sample_data, buy_signals, sell_signals)
        mock_run_analysis.return_value = mock_result

        analyzer = SMACAnalyzer("AAPL", 20, 50)
        analyzer.fetch_data("2023-01-01", "2023-12-31")

        # Verify the modern analysis was called with correct config
        call_args = mock_run_analysis.call_args[0][0]
        assert call_args.ticker == "AAPL"
        assert call_args.short_window == 20
        assert call_args.long_window == 50
        assert call_args.start_date == "2023-01-01"
        assert call_args.end_date == "2023-12-31"

        # Verify legacy data format is maintained
        assert analyzer.data is not None
        assert "Adj Close" in analyzer.data.columns
        assert "Short_SMA" in analyzer.data.columns
        assert "Long_SMA" in analyzer.data.columns
        assert "Signal" in analyzer.data.columns
        assert "Crossover" in analyzer.data.columns

    def test_calculate_sma_no_op_after_fetch(self) -> None:
        """Test that calculate_sma is a no-op after fetch_data."""
        analyzer = SMACAnalyzer("AAPL", 20, 50)

        # Should raise error if called before fetch_data
        with pytest.raises(
            RuntimeError, match="Data must be fetched before calculating SMAs"
        ):
            analyzer.calculate_sma()

        # Mock the analysis
        with patch("smac.legacy.run_smac_analysis") as mock_analysis:
            mock_result = Mock(spec=SMACResult)
            mock_result.data = pd.DataFrame(
                {
                    "price": [100],
                    "short_sma": [100],
                    "long_sma": [100],
                    "signal": [0],
                    "crossover": [0],
                }
            )
            mock_analysis.return_value = mock_result

            analyzer.fetch_data()
            analyzer.calculate_sma()  # Should not raise error

    def test_identify_crossovers_no_op_after_fetch(self) -> None:
        """Test that identify_crossovers is a no-op after fetch_data."""
        analyzer = SMACAnalyzer("AAPL", 20, 50)

        # Should raise error if called before fetch_data
        with pytest.raises(
            RuntimeError, match="SMAs must be calculated before identifying crossovers"
        ):
            analyzer.identify_crossovers()

        # Mock the analysis
        with patch("smac.legacy.run_smac_analysis") as mock_analysis:
            mock_result = Mock(spec=SMACResult)
            mock_result.data = pd.DataFrame(
                {
                    "price": [100],
                    "short_sma": [100],
                    "long_sma": [100],
                    "signal": [0],
                    "crossover": [0],
                }
            )
            mock_analysis.return_value = mock_result

            analyzer.fetch_data()
            analyzer.identify_crossovers("Short_SMA")  # Should not raise error

    @patch("smac.legacy.plot_analysis")
    def test_plot_data_calls_modern_visualization(self, mock_plot: Mock) -> None:
        """Test that plot_data calls the modern visualization function."""
        analyzer = SMACAnalyzer("AAPL", 20, 50)

        # Should raise error if called before analysis
        with pytest.raises(
            RuntimeError, match="Analysis must be completed before plotting"
        ):
            analyzer.plot_data()

        # Mock the analysis
        with patch("smac.legacy.run_smac_analysis") as mock_analysis:
            mock_result = Mock(spec=SMACResult)
            mock_result.data = pd.DataFrame()
            mock_analysis.return_value = mock_result

            analyzer.fetch_data()
            analyzer.plot_data("Short_SMA")

            # Verify modern plot function was called
            mock_plot.assert_called_once_with(mock_result, show=True)

    def test_result_property_access(self) -> None:
        """Test that the modern result can be accessed via property."""
        analyzer = SMACAnalyzer("AAPL", 20, 50)

        # Should be None before analysis
        assert analyzer.result is None

        # Mock the analysis
        with patch("smac.legacy.run_smac_analysis") as mock_analysis:
            mock_result = Mock(spec=SMACResult)
            mock_result.data = pd.DataFrame()
            mock_analysis.return_value = mock_result

            analyzer.fetch_data()

            # Should return the modern result object
            assert analyzer.result == mock_result
