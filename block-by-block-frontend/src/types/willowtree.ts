// Willow Tree Financial API Types

export type Ticker = string;
export type OptionType = "call" | "put";
export type ExerciseStyle = "european" | "american";
export type HedgeType = "delta_neutral" | "protective_put" | "collar";
export type AlertType = "price_above" | "price_below" | "volatility_spike" | 
                        "delta_change" | "gamma_risk" | "theta_decay" | "iv_rank";
export type StrategyName = "bull_call_spread" | "bear_put_spread" | "iron_condor" | 
                           "butterfly" | "straddle" | "strangle" | "collar" | 
                           "calendar_spread" | "ratio_spread";
export type BacktestStrategy = "buy_and_hold" | "covered_call" | "protective_put" | "iron_condor";

export interface AIExplanation {
  explanation: string;
  tokens_used: number;
  model: string;
}

// Market Data
export interface MarketDataResponse {
  ticker: string;
  current_price: number;
  historical_volatility: number;
  risk_free_rate: number;
  dividend_yield: number | null;
  timestamp: string;
  ai_explanation?: AIExplanation;
}

// Option Pricing
export interface OptionPriceRequest {
  ticker: string;
  strike: number;
  days_to_expiry: number;
  option_type: OptionType;
  exercise_style: ExerciseStyle;
  explain?: boolean;
}

export interface OptionPriceResponse {
  ticker: string;
  strike: number;
  spot_price: number;
  option_type: string;
  exercise_style: string;
  price: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
  time_to_expiry: number;
  volatility: number;
  ai_explanation?: AIExplanation;
}

// Risk Metrics
export interface RiskMetricsRequest {
  ticker: string;
  position_size: number;
  days_lookback?: number;
  confidence_level?: number;
  explain?: boolean;
}

export interface RiskMetricsResponse {
  ticker: string;
  position_size: number;
  current_price: number;
  portfolio_value: number;
  var_1day: number;
  cvar_1day: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  annualized_return: number;
  annualized_volatility: number;
  ai_explanation?: AIExplanation;
}

// Hedging
export interface HedgeRecommendRequest {
  ticker: string;
  shares: number;
  hedge_type: HedgeType;
  protection_level?: number;
  explain?: boolean;
}

export interface HedgeRecommendResponse {
  ticker: string;
  current_price: number;
  shares: number;
  hedge_type: string;
  recommendation: string;
  cost: number;
  protected_downside: number | null;
  upside_cap: number | null;
  total_portfolio_delta: number;
  ai_explanation?: AIExplanation;
}

// Scenario Analysis
export interface OptionPosition {
  strike: number;
  expiry: number;
  type: OptionType;
  quantity: number;
}

export interface ScenarioAnalysisRequest {
  ticker: string;
  position_shares?: number;
  option_positions?: OptionPosition[];
  price_changes?: number[];
  vol_changes?: number[];
  days_forward?: number;
  explain?: boolean;
}

export interface Scenario {
  price_change: number;
  vol_change: number;
  new_price: number;
  portfolio_value: number;
  pnl: number;
  pnl_pct: number;
}

export interface ScenarioAnalysisResponse {
  ticker: string;
  current_price: number;
  current_volatility: number;
  scenarios: Scenario[];
  best_case: Scenario;
  worst_case: Scenario;
  base_case: Scenario;
  ai_explanation?: AIExplanation;
}

// Implied Volatility
export interface ImpliedVolatilityRequest {
  ticker: string;
  strike: number;
  days_to_expiry: number;
  option_price: number;
  option_type: OptionType;
  explain?: boolean;
}

export interface ImpliedVolatilityResponse {
  ticker: string;
  strike: number;
  spot_price: number;
  option_type: string;
  market_price: number;
  implied_volatility: number;
  historical_volatility: number;
  iv_hv_spread: number;
  iv_rank: number;
  ai_explanation?: AIExplanation;
}

// Strategy Builder
export interface StrategyBuildRequest {
  ticker: string;
  strategy_name: StrategyName;
  strikes: number[];
  days_to_expiry?: number;
  explain?: boolean;
}

export interface StrategyBuildResponse {
  ticker: string;
  strategy_name: string;
  spot_price: number;
  net_premium: number;
  max_profit: number;
  max_loss: number;
  breakeven_points: number[];
  risk_reward_ratio: number;
  delta: number;
  theta: number;
  vega: number;
  ai_explanation?: AIExplanation;
}

// Backtesting
export interface BacktestRequest {
  ticker: string;
  strategy_name: BacktestStrategy;
  start_date: string;
  end_date: string;
  initial_capital?: number;
  explain?: boolean;
}

export interface BacktestResponse {
  ticker: string;
  strategy_name: string;
  period: string;
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  benchmark_return: number;
  alpha: number;
  ai_explanation?: AIExplanation;
}

// Alerts
export interface AlertCreateRequest {
  ticker: string;
  alert_type: AlertType;
  threshold: number;
  position_size?: number;
  explain?: boolean;
}

export interface AlertCreateResponse {
  ticker: string;
  alert_type: string;
  threshold: number;
  current_value: number;
  triggered: boolean;
  message: string;
  ai_explanation?: AIExplanation;
}
