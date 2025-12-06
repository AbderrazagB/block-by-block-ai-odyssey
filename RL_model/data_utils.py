"""
Data fetching and processing utilities.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from stockstats import StockDataFrame
import warnings
warnings.filterwarnings('ignore')

try:
    from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
    from finrl.meta.preprocessor.preprocessors import FeatureEngineer
    FINRL_AVAILABLE = True
except ImportError:
    FINRL_AVAILABLE = False


def safe_fetch_data(self):
    """Custom Yahoo downloader to handle multi-ticker data."""
    data = yf.download(
        tickers=self.ticker_list,
        start=self.start_date,
        end=self.end_date,
        auto_adjust=False,
        progress=False,
        threads=True,
    )
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join([str(c) for c in col]).strip() for col in data.columns.values]
    
    allowed = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    data = data[[col for col in data.columns if any(a in col for a in allowed)]]
    data.reset_index(inplace=True)
    return data


def make_finrl_ready(df, tickers):
    """Convert raw Yahoo data to FinRL long-format DataFrame."""
    df = df.copy()
    
    # Handle different column formats
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join([str(c) for c in col if c]).strip() for col in df.columns.values]
        df = df.reset_index()
    else:
        if 'Date' not in df.columns and 'date' not in df.columns:
            df = df.reset_index()
    
    # Ensure we have a date column
    if 'Date' in df.columns:
        df.rename(columns={'Date': 'date'}, inplace=True)
    elif 'index' in df.columns:
        df.rename(columns={'index': 'date'}, inplace=True)
    
    if 'date' not in df.columns:
        raise ValueError(f"No date column found. Available columns: {df.columns.tolist()}")
    
    df['date'] = pd.to_datetime(df['date'])
    
    if len(tickers) == 1:
        ticker = tickers[0]
        col_mapping = {}
        for base_col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
            possible_names = [f'{base_col}_{ticker}', base_col]
            for name in possible_names:
                if name in df.columns:
                    col_mapping[name] = base_col.lower().replace(' ', '_')
                    break
        
        df_long = df.rename(columns=col_mapping)
        df_long['tic'] = ticker
    else:
        df_long = pd.DataFrame()
        for ticker in tickers:
            ticker_cols = [c for c in df.columns if c.endswith(f'_{ticker}')]
            if not ticker_cols:
                print(f"⚠️  Warning: No columns found for {ticker}, skipping...")
                continue
                
            temp = df[['date'] + ticker_cols].copy()
            col_map = {c: c.replace(f'_{ticker}','').lower().replace(' ','_') for c in ticker_cols}
            temp.rename(columns=col_map, inplace=True)
            temp['tic'] = ticker
            df_long = pd.concat([df_long, temp], ignore_index=True)
    
    required_cols = ['date', 'tic', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
    
    # Check if all required columns exist
    missing_cols = [col for col in required_cols if col not in df_long.columns]
    if missing_cols:
        print(f"Warning: Missing columns {missing_cols}. Available: {df_long.columns.tolist()}")
        for col in missing_cols:
            if col not in ['date', 'tic']:
                df_long[col] = 0
    
    return df_long[required_cols]


def add_technical_indicators_simple(df, indicators_list):
    """Add technical indicators using stockstats."""
    df = df.copy()
    df = df.sort_values(['tic', 'date'])
    
    result_dfs = []
    for ticker in df['tic'].unique():
        ticker_df = df[df['tic'] == ticker].copy()
        ticker_df = ticker_df.sort_values('date')
        
        # Store the date and tic columns
        date_col = ticker_df['date'].copy()
        tic_col = ticker_df['tic'].copy()
        
        # Convert to StockDataFrame for technical indicators
        stock = StockDataFrame.retype(ticker_df.copy())
        
        # Add indicators
        for indicator in indicators_list:
            if indicator == 'macd':
                stock['macd']
            elif indicator == 'rsi_30':
                stock['rsi_30']
            elif indicator == 'cci_30':
                stock['cci_30']
            elif indicator == 'dx_30':
                stock['dx_30']
            elif indicator == 'close_30_sma':
                stock['close_30_sma']
            elif indicator == 'close_60_sma':
                stock['close_60_sma']
        
        # Restore date and tic columns
        stock['date'] = date_col.values
        stock['tic'] = tic_col.values
        
        result_dfs.append(stock)
    
    result = pd.concat(result_dfs, ignore_index=True)
    
    # Ensure date column exists
    if 'date' not in result.columns:
        result['date'] = df['date'].values
    
    return result


def fetch_recent_data(start_date, end_date, ticker_list, indicators_list):
    """Fetch and process recent stock data."""
    print(f"Fetching data from {start_date} to {end_date}...")
    
    if FINRL_AVAILABLE:
        # Use FinRL's downloader
        YahooDownloader.fetch_data = safe_fetch_data
        df = YahooDownloader(
            start_date=start_date,
            end_date=end_date,
            ticker_list=ticker_list
        ).fetch_data()
    else:
        # Use yfinance directly
        df = yf.download(
            tickers=ticker_list,
            start=start_date,
            end=end_date,
            auto_adjust=False,
            progress=False,
            threads=True,
        )
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join([str(c) for c in col]).strip() for col in df.columns.values]
        df.reset_index(inplace=True)
    
    # Convert to FinRL format
    df_finrl = make_finrl_ready(df, ticker_list)
    
    # Remove tickers with insufficient data
    tickers_with_data = df_finrl.groupby('tic').size()
    min_required_rows = 60  # Need at least 60 days for 60-day SMA
    valid_tickers = tickers_with_data[tickers_with_data >= min_required_rows].index.tolist()
    
    if len(valid_tickers) < len(ticker_list):
        missing_tickers = set(ticker_list) - set(valid_tickers)
        print(f"⚠️  Removing tickers with insufficient data: {missing_tickers}")
        df_finrl = df_finrl[df_finrl['tic'].isin(valid_tickers)].copy()
    
    # Add technical indicators
    if FINRL_AVAILABLE:
        fe = FeatureEngineer(
            use_technical_indicator=True,
            tech_indicator_list=indicators_list,
            use_vix=False,
            use_turbulence=False,
            user_defined_feature=False
        )
        processed_df = fe.preprocess_data(df_finrl).dropna()
    else:
        processed_df = add_technical_indicators_simple(df_finrl, indicators_list).dropna()
    
    print(f"✓ Successfully added technical indicators")
    
    # Filter to only keep dates where we have data for ALL valid tickers
    dates_with_all_tickers = processed_df.groupby('date')['tic'].nunique()
    complete_dates = dates_with_all_tickers[dates_with_all_tickers == len(valid_tickers)].index
    processed_df = processed_df[processed_df['date'].isin(complete_dates)].copy()
    
    # Sort by date and ticker
    processed_df = processed_df.sort_values(['date', 'tic']).reset_index(drop=True)
    
    print(f"✓ Fetched {len(processed_df)} rows across {processed_df['date'].nunique()} dates")
    print(f"✓ Using {len(valid_tickers)} tickers: {valid_tickers}")
    
    return processed_df, valid_tickers
