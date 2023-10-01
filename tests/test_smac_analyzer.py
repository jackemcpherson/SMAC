import pytest
import pandas as pd
from SMAC import SMACAnalyzer


@pytest.fixture
def sample_analyzer():
    return SMACAnalyzer("AAPL", 40, 100)


def test_fetch_data(sample_analyzer):
    sample_analyzer.fetch_data(start_date="2020-01-01", end_date="2020-01-10")
    assert "Adj Close" in sample_analyzer.data.columns
    assert isinstance(sample_analyzer.data, pd.DataFrame)


def test_calculate_sma(sample_analyzer):
    sample_analyzer.fetch_data(start_date="2020-01-01", end_date="2020-01-10")
    sample_analyzer.calculate_sma()
    assert "Short_SMA" in sample_analyzer.data.columns
    assert "Long_SMA" in sample_analyzer.data.columns


def test_identify_crossovers(sample_analyzer):
    sample_analyzer.fetch_data(start_date="2020-01-01", end_date="2020-01-10")
    sample_analyzer.calculate_sma()
    sample_analyzer.identify_crossovers()
    assert "Signal" in sample_analyzer.data.columns
    assert "Crossover" in sample_analyzer.data.columns


def test_date_range(sample_analyzer):
    sample_analyzer.fetch_data(start_date="2020-01-01", end_date="2020-01-10")
    assert sample_analyzer.data.index.min() >= pd.Timestamp("2020-01-01")
    assert sample_analyzer.data.index.max() <= pd.Timestamp("2020-01-10")
