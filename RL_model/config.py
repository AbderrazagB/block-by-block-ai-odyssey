"""
Configuration settings for the trading server.
"""

# Model and data paths
PROJECT_PATH = './FinRL_Trading_Results'
MODEL_PATH = f'{PROJECT_PATH}/trained_ppo_trading_model.zip'
TRAIN_END_DATE = '2023-01-01'

# Stock tickers
TICKER_LIST = [
    # Green Energy
    "NEE", "FSLR", "BEP", "PLUG",
    # Oil & Gas
    "XOM", "CVX", "COP", "SLB",
    # Banking & Finance
    "JPM", "BAC", "WFC", "GS", "MS",
    # Utilities / General Energy
    "DUK", "SO", "PCG", "EIX",
    # IT / Tech
    "AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "ORCL", "IBM"
]

# Technical indicators
INDICATORS_LIST = ['macd', 'rsi_30', 'cci_30', 'dx_30', 'close_30_sma', 'close_60_sma']

# Trading parameters
INITIAL_AMOUNT = 100000
TRANSACTION_COST_PCT = 0.001
REWARD_SCALING = 1e-4
DEFAULT_HMAX = 100

# Environment configuration
def get_env_kwargs(initial_amount=None, hmax=None, transaction_cost=None):
    """Generate environment kwargs for the trading environment."""
    stock_dimension = len(TICKER_LIST)
    state_space = 1 + 2*stock_dimension + len(INDICATORS_LIST)*stock_dimension
    
    return {
        "hmax": hmax or DEFAULT_HMAX,
        "initial_amount": initial_amount or INITIAL_AMOUNT,
        "num_stock_shares": [0] * stock_dimension,
        "buy_cost_pct": [transaction_cost or TRANSACTION_COST_PCT] * stock_dimension,
        "sell_cost_pct": [transaction_cost or TRANSACTION_COST_PCT] * stock_dimension,
        "state_space": state_space,
        "stock_dim": stock_dimension,
        "tech_indicator_list": INDICATORS_LIST,
        "action_space": stock_dimension,
        "reward_scaling": REWARD_SCALING
    }
