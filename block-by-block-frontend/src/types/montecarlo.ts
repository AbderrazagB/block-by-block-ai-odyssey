// Monte Carlo Jump Diffusion API Types

export interface SimulateRequest {
  ticker?: string;
  period?: string;
  forecast_days?: number;
  num_simulations?: number;
  seed?: number;
  analyze_jumps?: boolean;
  max_jumps?: number;
  include_prediction?: boolean;
}

export interface SimulateResponse {
  metadata: {
    generated_at: string;
    ticker: string;
    period: string;
    forecast_days: number;
    num_simulations: number;
  };
  stock_data: {
    current_price: number;
    data_points: number;
    period_start: string;
    period_end: string;
  };
  parameters: {
    mu: number;
    sigma: number;
    Lambda: number;
    a: number;
    b: number;
  };
  monte_carlo_results: {
    theoretical_mean: number;
    theoretical_variance: number;
    simulated_mean: number;
    simulated_variance: number;
    simulated_std: number;
    skewness: number;
    kurtosis: number;
    ci_low: number;
    ci_high: number;
    n_simulations: number;
    elapsed_time_ms: number;
  };
  ai_analysis: string;
  jump_analysis: JumpAnalysis | null;
  jump_prediction_48h: JumpPrediction | null;
}

export interface JumpAnalysis {
  total_detected: number;
  analyzed_jumps: AnalyzedJump[];
}

export interface AnalyzedJump {
  date: string;
  return_pct: number;
  price: number;
  prev_price: number;
  direction: 'UP' | 'DOWN';
  analysis: string;
  news_sources: string[];
}

export interface PredictRequest {
  ticker?: string;
  period?: string;
}

export interface JumpPrediction {
  ticker: string;
  current_price: number;
  prediction_window: string;
  jump_probability: number;
  expected_magnitude_pct: number;
  likely_direction: 'UP' | 'DOWN' | 'NEUTRAL';
  direction_confidence: number;
  volatility_regime: number;
  upcoming_events: UpcomingEvent[];
  likely_triggers: string[];
  recommendation: 'HIGH_ALERT' | 'MONITOR' | 'WATCH' | 'NORMAL';
  ai_analysis: string;
  timestamp: string;
}

export interface UpcomingEvent {
  type: string;
  date: string;
  importance: string;
}

export interface AnalyzeJumpEventParams {
  ticker: string;
  date: string;
  return_pct: number;
  crawl_news?: boolean;
}

export interface AnalyzeJumpEventResponse {
  ticker: string;
  date: string;
  return_pct: number;
  news_sources: NewsSource[];
  ai_analysis: string;
}

export interface NewsSource {
  title: string;
  link: string;
  snippet: string;
  content: string | null;
}

export interface HealthResponse {
  status: string;
}
