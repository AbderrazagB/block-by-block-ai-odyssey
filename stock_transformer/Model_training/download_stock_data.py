"""
Download stock data from 2015 to today using yfinance
Saves individual CSV files for each ticker in the Input file/ directory
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Define tickers
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
           'GD', 'DE', 'CHRW', 'ABBV', 'CAH', 'EW', 'INTU',
           'FFIV', 'APH', 'ETR', 'ATO', 'AES', 'BEN', 'AXP',
           'PNC', 'DOW', 'MLM', 'FCX', 'ROST', 'TPR',
           'DLR', 'DOC', 'VICI', 'OMC', 'FOXA', 'CMCSA',
           'ADM', 'TAP', 'COST', 'CVX', 'HAL', 'DVN']

# Remove duplicate TSLA (appears twice in original list)
TICKERS = list(set(TICKERS))
TICKERS.sort()

# Date range
START_DATE = "2015-01-01"
END_DATE = datetime.today().strftime('%Y-%m-%d')

# Create output directory if it doesn't exist
OUTPUT_DIR = "./Input file"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Downloading stock data from {START_DATE} to {END_DATE}")
print(f"Total tickers: {len(TICKERS)}")
print("-" * 60)

# Download data for each ticker
successful = []
failed = []

for i, ticker in enumerate(TICKERS, 1):
    try:
        print(f"[{i}/{len(TICKERS)}] Downloading {ticker}...", end=" ")
        
        # Download data
        stock_data = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)
        
        if stock_data.empty:
            print(f"❌ No data available")
            failed.append(ticker)
            continue
        
        # Reset index to make Date a column
        stock_data.reset_index(inplace=True)
        
        # Ensure column names are clean (remove multi-level index from yfinance)
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.get_level_values(0)
        
        # Save to CSV
        output_path = os.path.join(OUTPUT_DIR, f"{ticker}.csv")
        stock_data.to_csv(output_path, index=False)
        
        print(f"✓ Saved {len(stock_data)} rows")
        successful.append(ticker)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        failed.append(ticker)

print("-" * 60)
print(f"\n✅ Successfully downloaded: {len(successful)}/{len(TICKERS)} tickers")

if failed:
    print(f"\n❌ Failed tickers ({len(failed)}): {', '.join(failed)}")

print(f"\nFiles saved to: {os.path.abspath(OUTPUT_DIR)}/")
