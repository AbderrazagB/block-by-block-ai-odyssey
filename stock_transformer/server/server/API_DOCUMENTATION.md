# Stock Transformer API Documentation

## Overview

This API provides 7-day stock price predictions using a Transformer-based deep learning model trained on historical stock data with technical indicators.

**Base URL:** `http://127.0.0.1:8080`

**Version:** 1.0

---

## Authentication

Currently, no authentication is required.

---

## Endpoints

### Get 7-Day Price Forecast

Retrieves predicted closing prices for the next 7 market days for a specified stock ticker.

**Endpoint:** `GET /predict/{ticker}`

**Parameters:**

| Parameter | Type   | Location | Required | Description                           |
|-----------|--------|----------|----------|---------------------------------------|
| ticker    | string | path     | Yes      | Stock ticker symbol (e.g., AAPL, MSFT)|

**Supported Tickers:**

The model supports the following 37 stock tickers:

```
AAPL, ABBV, ADM, AES, AMZN, APH, ATO, AXP, BEN, BIDU, CAH, CHRW, 
CMCSA, COST, CVX, DE, DLR, DOC, DOW, DVN, ETR, EW, FCX, FFIV, 
FOXA, GD, GOOG, GOOGL, HAL, INTC, INTU, MLM, MSFT, NFLX, NVDA, 
OMC, PNC, ROST, TAP, TCEHY, TPR, TSLA, VICI
```

**Request Example:**

```bash
curl -X GET "http://127.0.0.1:8080/predict/AAPL"
```

```javascript
// JavaScript fetch example
fetch('http://127.0.0.1:8080/predict/AAPL')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

```python
# Python requests example
import requests

response = requests.get('http://127.0.0.1:8080/predict/AAPL')
data = response.json()
print(data)
```

**Success Response:**

**Code:** `200 OK`

**Content:**

```json
{
  "ticker": "AAPL",
  "predictions_7d": [
    195.4523,
    196.7834,
    197.2156,
    198.0034,
    197.8912,
    198.5634,
    199.1245
  ],
  "forecast_dates": [
    "2025-12-08",
    "2025-12-09",
    "2025-12-10",
    "2025-12-11",
    "2025-12-12",
    "2025-12-13",
    "2025-12-16"
  ],
  "unit": "USD Close Price"
}
```

**Response Fields:**

| Field           | Type          | Description                                      |
|----------------|---------------|--------------------------------------------------|
| ticker         | string        | The requested stock ticker symbol                |
| predictions_7d | array[number] | Array of 7 predicted closing prices (USD)        |
| forecast_dates | array[string] | Array of 7 future trading dates (YYYY-MM-DD)     |
| unit           | string        | Price unit (always "USD Close Price")            |

**Note:** Forecast dates exclude weekends and use business day frequency.

---

### Error Responses

#### Ticker Not Found

**Code:** `404 Not Found`

**Content:**

```json
{
  "detail": "Ticker 'XYZ' not in the trained list. Scaler missing."
}
```

**Scenario:** The requested ticker was not included in the model's training data.

---

#### Data Download Failed

**Code:** `400 Bad Request`

**Content:**

```json
{
  "detail": "Could not download recent data for ticker 'AAPL'."
}
```

**Scenario:** Unable to fetch live data from Yahoo Finance (ticker may be delisted or invalid).

---

#### Internal Server Error

**Code:** `500 Internal Server Error`

**Content:**

```json
{
  "detail": "An internal server error occurred: {error_message}"
}
```

**Scenario:** Unexpected error during prediction computation (e.g., model failure, scaling issues).

---

## Model Information

### Architecture
- **Type:** Transformer Encoder with Multi-Head Attention
- **Input:** 10-day historical sequences with 23 technical features
- **Output:** Single-step closing price prediction
- **Forecast Method:** Recursive 7-day prediction

### Features Used
The model uses 23 technical indicators including:
- Moving Averages (MA_5, MA_10, MA_20)
- Exponential Moving Averages (EMA_12)
- Relative Strength Index (RSI)
- MACD and MACD Signal
- Bollinger Bands (Upper, Middle, Lower)
- Volatility and Momentum
- Volume indicators
- Price ranges (High-Low differences)

### Data Source
Live historical data is fetched from Yahoo Finance (last 60 days) to compute features and generate predictions.

---

## Rate Limiting

Currently, no rate limiting is enforced. However, excessive requests may impact performance.

---

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is not explicitly configured. If accessing from a browser-based front-end, you may need to add CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Usage Examples

### React/Next.js Example

```typescript
import { useEffect, useState } from 'react';

interface PredictionData {
  ticker: string;
  predictions_7d: number[];
  forecast_dates: string[];
  unit: string;
}

function StockPrediction({ ticker }: { ticker: string }) {
  const [data, setData] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPrediction = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`http://127.0.0.1:8080/predict/${ticker}`);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to fetch prediction');
        }
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, [ticker]);

  if (loading) return <div>Loading predictions...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return null;

  return (
    <div>
      <h2>{data.ticker} - 7-Day Forecast</h2>
      <ul>
        {data.predictions_7d.map((price, idx) => (
          <li key={idx}>
            {data.forecast_dates[idx]}: ${price.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <div>
    <h2>{{ ticker }} - 7-Day Forecast</h2>
    <div v-if="loading">Loading predictions...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <ul v-else-if="data">
      <li v-for="(price, idx) in data.predictions_7d" :key="idx">
        {{ data.forecast_dates[idx] }}: ${{ price.toFixed(2) }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  props: ['ticker'],
  data() {
    return {
      data: null,
      loading: false,
      error: null
    };
  },
  async mounted() {
    this.loading = true;
    try {
      const response = await fetch(`http://127.0.0.1:8080/predict/${this.ticker}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }
      this.data = await response.json();
    } catch (err) {
      this.error = err.message;
    } finally {
      this.loading = false;
    }
  }
};
</script>
```

### Chart.js Visualization Example

```javascript
async function renderPredictionChart(ticker) {
  const response = await fetch(`http://127.0.0.1:8080/predict/${ticker}`);
  const data = await response.json();

  const ctx = document.getElementById('predictionChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.forecast_dates,
      datasets: [{
        label: `${ticker} Predicted Price`,
        data: data.predictions_7d,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: `${ticker} - 7 Day Price Forecast`
        }
      },
      scales: {
        y: {
          title: {
            display: true,
            text: 'Price (USD)'
          }
        }
      }
    }
  });
}
```

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** `http://127.0.0.1:8080/docs`
- **ReDoc:** `http://127.0.0.1:8080/redoc`

These interfaces allow you to test API endpoints directly in the browser.

---

## Deployment Notes

### Development Server

```bash
uvicorn app:app --reload --port 8080
```

### Production Server

```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --workers 4
```

**Note:** Ensure the `model/` directory contains the required artifacts:
- `transformer_stock_weights.h5` - Model weights
- `all_scalers.pkl` - MinMaxScaler objects for each ticker
- `feature_cols.pkl` - List of feature column names

---

## Support & Contact

For issues or questions regarding the API, please contact the development team or file an issue in the project repository.

**Model Training Date:** December 2025  
**Training Data Period:** 2015-2025  
**Framework:** FastAPI + TensorFlow/Keras
