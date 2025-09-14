"""
SMAC - Simple Moving Average Crossover Analysis

A package for performing simple moving average crossover analysis on stock data.
"""

# Import the main class from the analyzer module
from smac.analyzer import SMACAnalyzer

# Import the CLI module
from smac import cli

# Export the SMACAnalyzer class and CLI module to make them available when importing the package
__all__ = ['SMACAnalyzer', 'cli']

__version__ = "0.1.0"
