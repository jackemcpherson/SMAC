# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SMAC (Simple Moving Average Crossover) is a Python package for performing Simple Moving Average Crossover analysis on stock data. The project provides both a Python API and command-line interface for analyzing stock price trends using moving averages.

## Architecture

The codebase follows a clean, modern functional architecture:

- **Core Analysis**:
  - `src/smac/analysis.py` - Main analysis functions and data classes
  - `src/smac/data.py` - Stock data fetching via yfinance
  - `src/smac/indicators.py` - SMA calculation using pandas
  - `src/smac/visualization.py` - Matplotlib-based plotting

- **CLI Interface**: `src/smac/cli.py` provides command-line access with argument parsing and validation

- **Package Structure**: Standard Python package with `__init__.py` exposing the functional API

## Functional API Architecture

The project follows a pure functional approach (v2.0.0+) with immutable data classes:

### Core Data Classes
- `SMACConfig`: Immutable configuration container with validation
- `SMACResult`: Immutable results container with computed properties and summary methods

### Main API Functions
- `analyze_ticker()`: High-level convenience function for quick analysis
- `run_smac_analysis()`: Core analysis workflow function taking SMACConfig
- `plot_analysis()`: Visualization function for SMACResult objects

### Example Usage
```python
from smac import analyze_ticker, plot_analysis

# Simple analysis
result = analyze_ticker("AAPL", short_window=20, long_window=50)

# View summary
print(result.summary())

# Plot results
plot_analysis(result, save_path="aapl_analysis.png")
```

Note: The README.md contains outdated class-based examples (`SMACAnalyzer`) that were removed in v2.0.0.

## Development Commands

### Package Management
This project uses **uv** for dependency management with **hatch** for build system:
- Install dependencies: `uv sync`
- Install with dev dependencies: `uv sync --group dev`
- Add new dependency: `uv add <package>`
- Add dev dependency: `uv add --group dev <package>`

### Testing
- Run all tests: `uv run pytest`
- Run specific test: `uv run pytest tests/test_analysis.py::test_function_name`
- Run with coverage: `uv run pytest --cov=smac`
- Coverage is configured to require 80% minimum coverage and will fail builds if not met

### Code Quality
- Format code: `uv run ruff format`
- Lint code: `uv run ruff check`
- Fix linting issues: `uv run ruff check --fix`
- Type check: `uv run mypy src/smac`
- Run all quality checks: `uv run ruff check && uv run ruff format && uv run mypy src/smac`

### Build and Release
- Build package: `uv run hatch build`
- Build clean: `uv run hatch build --clean`
- Check built package: `uv run hatch envs run release:check`
- Publish to test PyPI: `uv run hatch envs run release:publish-test`
- Publish to PyPI: `uv run hatch envs run release:publish`

## Key Dependencies

### Runtime Dependencies
- **yfinance**: Stock data fetching via Yahoo Finance API
- **pandas**: Data manipulation and SMA calculations
- **matplotlib**: Core plotting functionality
- **numpy**: Numerical operations and array handling
- **seaborn**: Enhanced plotting styling
- **typer**: Modern CLI framework with rich output formatting
- **rich**: Rich text and progress indicators for CLI

### Development Dependencies
- **pytest**: Testing framework with coverage support (`pytest-cov`)
- **ruff**: Fast Python linter and formatter (replaces flake8, black, isort)
- **mypy**: Static type checker with strict configuration
- **hatch**: Modern Python packaging and build backend
- **pandas-stubs**: Type stubs for pandas
- **twine**: Package publishing to PyPI

## Testing Structure

Tests are located in `tests/` directory with separate files for each module:
- `tests/test_analysis.py` - Tests for analysis API
- `tests/test_data.py` - Tests for data fetching functionality
- Key test patterns: Use pytest fixtures, mock external APIs, comprehensive coverage

## CLI Usage

The package provides a modern command-line interface using Typer with rich output formatting:

```bash
# Using the installed command (after pip install)
smac AAPL --short-window 20 --long-window 50 --start-date 2023-01-01

# Using module execution during development
python -m smac.cli AAPL --short-window 20 --long-window 50 --start-date 2023-01-01

# Common CLI options
smac AAPL -s 20 -l 50 -f 2023-01-01 -t 2023-12-31 --save chart.png --verbose
```

### CLI Features
- Rich console output with tables and progress indicators
- Automatic chart visualization (displays and optionally saves)
- Comprehensive error handling with user-friendly messages
- Built-in help with `smac --help`
- Version information with `smac --version`

## Stack Migration Notes

The project uses a modern Python stack (v2.0.0+):
- **Build System**: Uses uv + hatch for fast dependency resolution and modern packaging
- **Code Quality**: Uses ruff for comprehensive linting and formatting
- **Type Checking**: Uses mypy with strict configuration for better code quality
- **Testing**: Enhanced pytest configuration with coverage reporting
- **Breaking Changes**: v2.0.0 removes legacy class-based API in favor of pure functional approach
- **GitHub Actions**: CI workflow may still reference old tools and should be updated