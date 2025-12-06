export interface Prediction {
  action: number;
  recommendation: string;
  current_price: number;
  estimated_shares: number;
  portfolio_allocation: number;
  confidence_level: string;
  risk_score: number;
  indicators: {
    macd: number;
    rsi_30: number;
    cci_30: number;
    dx_30: number;
    sma_30: number;
    sma_60: number;
  };
}

export interface PredictionsResponse {
  success: boolean;
  predictions: Record<string, Prediction>;
  date: string;
  market_summary: {
    buy_signals: number;
    sell_signals: number;
    hold_signals: number;
  };
  error?: string;
}

export interface StockMetrics {
  final_price: number;
  final_shares: number;
  position_value: number;
  total_trades: number;
  buy_trades: number;
  sell_trades: number;
  price_change: number;
  avg_action_strength: number;
  indicators: {
    macd: number;
    rsi_30: number;
    cci_30: number;
    dx_30: number;
  };
}

export interface TestResults {
  success: boolean;
  results: {
    initial_value: number;
    final_value: number;
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    dates: string[];
    account_values: number[];
    total_trades: number;
    stock_metrics: Record<string, StockMetrics>;
    tickers: string[];
    portfolio_positions: number[][];
  };
  error?: string;
}

export interface HealthResponse {
  model_loaded: boolean;
}

export interface ModelInfo {
  stock_count: number;
}

export interface TestParams {
  start_date: string;
  end_date: string;
  initial_amount: number;
  hmax: number;
  transaction_cost: number;
}
