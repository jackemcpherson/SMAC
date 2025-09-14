import argparse
from datetime import datetime
import sys

from smac.analyzer import SMACAnalyzer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Simple Moving Average Crossover (SMAC) Analysis"
    )
    
    parser.add_argument(
        "ticker",
        type=str,
        help="Stock ticker symbol (e.g., AAPL, MSFT, GOOG)"
    )
    
    parser.add_argument(
        "--short-window", "-s",
        type=int,
        default=20,
        help="Short window period for SMA calculation (default: 20)"
    )
    
    parser.add_argument(
        "--long-window", "-l",
        type=int,
        default=50,
        help="Long window period for SMA calculation (default: 50)"
    )
    
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date for analysis (format: YYYY-MM-DD, default: 1 year ago)"
    )
    
    parser.add_argument(
        "--end-date",
        type=str,
        help="End date for analysis (format: YYYY-MM-DD, default: today)"
    )
    
    parser.add_argument(
        "--sma-type",
        type=str,
        default="Short_SMA",
        choices=["Short_SMA", "Long_SMA"],
        help="SMA type to use for crossover identification (default: Short_SMA)"
    )
    
    return parser.parse_args()


def validate_args(args):
    """Validate command line arguments."""
    # Validate short and long window values
    if args.short_window <= 0:
        print("Error: Short window must be a positive integer")
        return False
    
    if args.long_window <= 0:
        print("Error: Long window must be a positive integer")
        return False
    
    if args.short_window >= args.long_window:
        print("Error: Short window must be smaller than long window")
        return False
    
    # Validate date formats if provided
    if args.start_date:
        try:
            datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            print("Error: Start date must be in YYYY-MM-DD format")
            return False
    
    if args.end_date:
        try:
            datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            print("Error: End date must be in YYYY-MM-DD format")
            return False
    
    return True


def main():
    """Main function to run the SMAC analysis from command line."""
    args = parse_args()
    
    if not validate_args(args):
        sys.exit(1)
    
    # Initialize the analyzer
    analyzer = SMACAnalyzer(
        ticker=args.ticker,
        short_window=args.short_window,
        long_window=args.long_window
    )
    
    try:
        # Fetch data
        analyzer.fetch_data(start_date=args.start_date, end_date=args.end_date)
        
        # Calculate SMAs
        analyzer.calculate_sma()
        
        # Identify crossovers
        analyzer.identify_crossovers(sma_type=args.sma_type)
        
        # Plot the data
        analyzer.plot_data(sma_type=args.sma_type)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

