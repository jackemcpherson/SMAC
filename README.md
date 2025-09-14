# S.M.A.C.

## A Simple Implementation of Simple Moving Average Crossover Analysis

I have been constantly re-writing the same code to do a quick [Simple Moving Average Crossover (SMAC)](https://en.m.wikipedia.org/wiki/Moving_average_crossover) analysis of a stock price for too long.

I've written this to produce either a SMAC dataset or a plot showing a simple implementation of this trading strategy.

## Installation

### Using pip

```bash
pip install smac
```

### From source

```bash
git clone https://github.com/username/smac.git
cd smac
uv sync
```

## Usage

```python
from smac import SMACAnalyzer

# Initialize the analyzer with a ticker and SMA windows
analyzer = SMACAnalyzer(ticker="AAPL", short_window=40, long_window=100)

# Fetch historical stock data
analyzer.fetch_data(start_date="2023-01-01", end_date="2023-12-31")

# Calculate SMAs
analyzer.calculate_sma()

# Identify crossover points
analyzer.identify_crossovers()

# Visualize the results
analyzer.plot_data()
```

## Development

Setup development environment:

```bash
uv sync --group dev
```

Run tests:

```bash
uv run pytest
```

Format code:

```bash
uv run shed
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
