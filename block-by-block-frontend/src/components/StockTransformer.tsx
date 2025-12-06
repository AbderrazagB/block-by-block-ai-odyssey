import { useState } from 'react';
import { TrendingUp, Calendar, DollarSign, Sparkles } from 'lucide-react';
import type { TransformerPredictionResponse } from '../types/transformer';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface StockTransformerProps {
  onGetPrediction: (ticker: string) => void;
  predictionData: TransformerPredictionResponse | null;
  isLoading: boolean;
  error: string | null;
}

const SUPPORTED_TICKERS = [
  'AAPL', 'ABBV', 'ADM', 'AES', 'AMZN', 'APH', 'ATO', 'AXP', 'BEN', 'BIDU',
  'CAH', 'CHRW', 'CMCSA', 'COST', 'CVX', 'DE', 'DLR', 'DOC', 'DOW', 'DVN',
  'ETR', 'EW', 'FCX', 'FFIV', 'FOXA', 'GD', 'GOOG', 'GOOGL', 'HAL', 'INTC',
  'INTU', 'MLM', 'MSFT', 'NFLX', 'NVDA', 'OMC', 'PNC', 'ROST', 'TAP', 'TCEHY',
  'TPR', 'TSLA', 'VICI'
];

export function StockTransformer({
  onGetPrediction,
  predictionData,
  isLoading,
  error,
}: StockTransformerProps) {
  const [ticker, setTicker] = useState('AAPL');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGetPrediction(ticker.toUpperCase());
  };

  const filteredTickers = ticker
    ? SUPPORTED_TICKERS.filter(t => t.includes(ticker.toUpperCase()))
    : SUPPORTED_TICKERS;

  const chartData = predictionData
    ? predictionData.forecast_dates.map((date, idx) => ({
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        price: predictionData.predictions_7d[idx],
      }))
    : [];

  const avgPrice = predictionData
    ? predictionData.predictions_7d.reduce((a, b) => a + b, 0) / predictionData.predictions_7d.length
    : 0;

  const priceChange = predictionData
    ? predictionData.predictions_7d[6] - predictionData.predictions_7d[0]
    : 0;

  const priceChangePercent = predictionData
    ? ((priceChange / predictionData.predictions_7d[0]) * 100)
    : 0;

  return (
    <div className="space-y-6">
      {/* Control Form */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
          <Sparkles className="w-6 h-6 text-teal-600" />
          <span>Stock Transformer - 7-Day Price Forecast</span>
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stock Ticker
            </label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => {
                setTicker(e.target.value.toUpperCase());
                setShowSuggestions(true);
              }}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all font-mono text-lg"
              placeholder="e.g., AAPL, MSFT, TSLA"
              required
            />

            {showSuggestions && filteredTickers.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                <div className="p-2 text-xs text-gray-500 border-b">
                  {filteredTickers.length} supported tickers
                </div>
                <div className="grid grid-cols-6 gap-1 p-2">
                  {filteredTickers.map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => {
                        setTicker(t);
                        setShowSuggestions(false);
                      }}
                      className="px-2 py-1.5 text-sm font-mono text-gray-700 hover:bg-teal-50 hover:text-teal-700 rounded transition-colors"
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
            <p className="text-sm text-gray-700">
              <strong>Model Info:</strong> Transformer-based deep learning model trained on 2015-2025 data with 23 technical indicators (MA, EMA, RSI, MACD, Bollinger Bands, etc.)
            </p>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-all shadow-sm hover:shadow"
          >
            {isLoading ? 'Generating Forecast...' : 'Get 7-Day Forecast'}
          </button>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-red-800 text-sm font-medium">{error}</p>
        </div>
      )}

      {/* Prediction Results */}
      {predictionData && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Current Forecast</p>
                <DollarSign className="w-5 h-5 text-teal-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                ${predictionData.predictions_7d[0].toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-1">Day 1 ({predictionData.forecast_dates[0]})</p>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">7-Day Target</p>
                <TrendingUp className="w-5 h-5 text-teal-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                ${predictionData.predictions_7d[6].toFixed(2)}
              </p>
              <p className={`text-sm font-medium mt-1 ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%)
              </p>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Average Price</p>
                <Calendar className="w-5 h-5 text-teal-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">
                ${avgPrice.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-1">7-day average</p>
            </div>
          </div>

          {/* Price Chart */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-6">
              {predictionData.ticker} - 7-Day Price Forecast
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="date"
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                />
                <YAxis
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                  domain={['dataMin - 2', 'dataMax + 2']}
                  tickFormatter={(value) => `$${value.toFixed(0)}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '14px',
                  }}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#0d9488"
                  strokeWidth={3}
                  dot={{ fill: '#0d9488', r: 5 }}
                  activeDot={{ r: 7 }}
                  name="Predicted Price"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Detailed Predictions Table */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Detailed Forecast</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Day</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Date</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Predicted Price</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Change</th>
                  </tr>
                </thead>
                <tbody>
                  {predictionData.predictions_7d.map((price, idx) => {
                    const prevPrice = idx > 0 ? predictionData.predictions_7d[idx - 1] : price;
                    const change = price - prevPrice;
                    const changePercent = idx > 0 ? ((change / prevPrice) * 100) : 0;

                    return (
                      <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 text-sm font-medium text-gray-900">
                          Day {idx + 1}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {new Date(predictionData.forecast_dates[idx]).toLocaleDateString('en-US', {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric',
                          })}
                        </td>
                        <td className="py-3 px-4 text-right text-sm font-bold text-gray-900">
                          ${price.toFixed(2)}
                        </td>
                        <td className="py-3 px-4 text-right text-sm">
                          {idx > 0 ? (
                            <span className={change >= 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                              {change >= 0 ? '+' : ''}{change.toFixed(2)} ({changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%)
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
