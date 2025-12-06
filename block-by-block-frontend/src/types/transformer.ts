// Stock Transformer API Types

export interface TransformerPredictionResponse {
  ticker: string;
  predictions_7d: number[];
  forecast_dates: string[];
  unit: string;
}

export interface TransformerHealthResponse {
  status: string;
}
