// Stock Transformer API Types

export interface HistoricalDataPoint {
  date: string;
  price: number;
}

export interface TransformerPredictionResponse {
  ticker: string;
  historical_7d: HistoricalDataPoint[];
  predictions_7d: number[];
  forecast_dates: string[];
  last_actual_date: string;
  data_points_used: number;
}

export interface TransformerHealthResponse {
  status: string;
}
