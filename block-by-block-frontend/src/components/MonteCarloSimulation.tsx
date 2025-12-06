import { useState } from 'react';
import { Activity, TrendingUp, TrendingDown, AlertTriangle, Sparkles, Calendar } from 'lucide-react';
import type { SimulateResponse, JumpPrediction } from '../types/montecarlo';
import ReactMarkdown from 'react-markdown';

interface MonteCarloSimulationProps {
  onSimulate: (params: {
    ticker: string;
    period: string;
    forecast_days: number;
    num_simulations: number;
    analyze_jumps: boolean;
    include_prediction: boolean;
  }) => void;
  data: SimulateResponse | null;
  isLoading: boolean;
  error: string | null;
}

export function MonteCarloSimulation({ onSimulate, data, isLoading, error }: MonteCarloSimulationProps) {
  const [ticker, setTicker] = useState('AAPL');
  const [period, setPeriod] = useState('1y');
  const [forecastDays, setForecastDays] = useState(252);
  const [numSimulations, setNumSimulations] = useState(1000);
  const [analyzeJumps, setAnalyzeJumps] = useState(true);
  const [includePrediction, setIncludePrediction] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSimulate({
      ticker,
      period,
      forecast_days: forecastDays,
      num_simulations: numSimulations,
      analyze_jumps: analyzeJumps,
      include_prediction: includePrediction,
    });
  };

  return (
    <div className="space-y-6">
      {/* Control Form */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
          <Activity className="w-6 h-6 text-teal-600" />
          <span>Monte Carlo Jump Diffusion Simulation</span>
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                placeholder="AAPL"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              >
                <option value="1mo">1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="6mo">6 Months</option>
                <option value="1y">1 Year</option>
                <option value="2y">2 Years</option>
                <option value="5y">5 Years</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Forecast Days</label>
              <input
                type="number"
                value={forecastDays}
                onChange={(e) => setForecastDays(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                min="1"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Simulations</label>
              <input
                type="number"
                value={numSimulations}
                onChange={(e) => setNumSimulations(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                min="100"
                step="100"
              />
            </div>
            
            <div className="flex items-center space-x-6 md:col-span-2 pt-6">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={analyzeJumps}
                  onChange={(e) => setAnalyzeJumps(e.target.checked)}
                  className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
                />
                <span className="text-sm text-gray-700">Analyze Jumps</span>
              </label>
              
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includePrediction}
                  onChange={(e) => setIncludePrediction(e.target.checked)}
                  className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
                />
                <span className="text-sm text-gray-700">48h Prediction</span>
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 transition-all shadow-sm hover:shadow disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {isLoading ? 'Running Simulation...' : 'Run Simulation'}
          </button>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Results */}
      {data && (
        <div className="space-y-6">
          {/* Stock Data */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Stock Data</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Current Price</p>
                <p className="text-xl font-bold text-gray-900">${data.stock_data.current_price.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Data Points</p>
                <p className="text-xl font-bold text-gray-900">{data.stock_data.data_points}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Period Start</p>
                <p className="text-xl font-bold text-gray-900">{data.stock_data.period_start}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Period End</p>
                <p className="text-xl font-bold text-gray-900">{data.stock_data.period_end}</p>
              </div>
            </div>
          </div>

          {/* Model Parameters */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Jump-Diffusion Parameters</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div>
                <p className="text-sm text-gray-600">Drift (μ)</p>
                <p className="text-xl font-bold text-teal-600">{data.parameters.mu.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Volatility (σ)</p>
                <p className="text-xl font-bold text-teal-600">{data.parameters.sigma.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Jump Rate (λ)</p>
                <p className="text-xl font-bold text-teal-600">{data.parameters.Lambda.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Jump Mean (a)</p>
                <p className="text-xl font-bold text-teal-600">{data.parameters.a.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Jump Std (b)</p>
                <p className="text-xl font-bold text-teal-600">{data.parameters.b.toFixed(4)}</p>
              </div>
            </div>
          </div>

          {/* Monte Carlo Results */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Monte Carlo Results</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Simulated Mean</p>
                <p className="text-xl font-bold text-gray-900">{data.monte_carlo_results.simulated_mean.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Simulated Std</p>
                <p className="text-xl font-bold text-gray-900">{data.monte_carlo_results.simulated_std.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">95% CI Low</p>
                <p className="text-xl font-bold text-gray-900">{data.monte_carlo_results.ci_low.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">95% CI High</p>
                <p className="text-xl font-bold text-gray-900">{data.monte_carlo_results.ci_high.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Skewness</p>
                <p className="text-xl font-bold text-gray-900">{data.monte_carlo_results.skewness.toFixed(3)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Kurtosis</p>
                <p className="text-xl font-bold text-gray-900">{data.monte_carlo_results.kurtosis.toFixed(3)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Simulations</p>
                <p className="text-xl font-bold text-gray-900">{data.monte_carlo_results.n_simulations}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Time (ms)</p>
                <p className="text-xl font-bold text-gray-900">{data.monte_carlo_results.elapsed_time_ms.toFixed(0)}</p>
              </div>
            </div>
          </div>

          {/* AI Analysis */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-teal-600" />
              <span>AI Analysis</span>
            </h3>
            <div className="prose prose-sm max-w-none text-gray-800">
              <ReactMarkdown>{data.ai_analysis}</ReactMarkdown>
            </div>
          </div>

          {/* Jump Analysis */}
          {data.jump_analysis && data.jump_analysis.total_detected > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Jump Analysis ({data.jump_analysis.total_detected} jumps detected)
              </h3>
              <div className="space-y-4">
                {data.jump_analysis.analyzed_jumps.map((jump, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        {jump.direction === 'UP' ? (
                          <TrendingUp className="w-5 h-5 text-green-600" />
                        ) : (
                          <TrendingDown className="w-5 h-5 text-red-600" />
                        )}
                        <div>
                          <p className="font-bold text-gray-900">{jump.date}</p>
                          <p className="text-sm text-gray-600">
                            ${jump.prev_price.toFixed(2)} → ${jump.price.toFixed(2)}
                          </p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        jump.direction === 'UP' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {jump.return_pct > 0 ? '+' : ''}{jump.return_pct.toFixed(2)}%
                      </span>
                    </div>
                    <div className="prose prose-sm max-w-none text-gray-700 mb-2">
                      <ReactMarkdown>{jump.analysis}</ReactMarkdown>
                    </div>
                    {jump.news_sources.length > 0 && (
                      <div className="text-sm text-gray-600">
                        <p className="font-medium">News Sources:</p>
                        <ul className="list-disc list-inside">
                          {jump.news_sources.slice(0, 3).map((url, i) => (
                            <li key={i} className="truncate">
                              <a href={url} target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:underline">
                                {url}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 48h Prediction */}
          {data.jump_prediction_48h && (
            <JumpPredictionCard prediction={data.jump_prediction_48h} />
          )}
        </div>
      )}
    </div>
  );
}

function JumpPredictionCard({ prediction }: { prediction: JumpPrediction }) {
  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'HIGH_ALERT': return 'text-red-600 bg-red-50 border-red-200';
      case 'MONITOR': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'WATCH': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
        <AlertTriangle className="w-5 h-5 text-orange-600" />
        <span>48-Hour Jump Prediction</span>
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600">Jump Probability</p>
          <p className="text-2xl font-bold text-orange-600">{prediction.jump_probability.toFixed(1)}%</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Expected Magnitude</p>
          <p className="text-2xl font-bold text-gray-900">{prediction.expected_magnitude_pct.toFixed(2)}%</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Direction</p>
          <p className="text-2xl font-bold text-gray-900">{prediction.likely_direction}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Confidence</p>
          <p className="text-2xl font-bold text-gray-900">{(prediction.direction_confidence * 100).toFixed(0)}%</p>
        </div>
      </div>

      <div className={`border rounded-lg p-4 mb-4 ${getRecommendationColor(prediction.recommendation)}`}>
        <p className="font-bold text-lg">Recommendation: {prediction.recommendation}</p>
      </div>

      {prediction.upcoming_events.length > 0 && (
        <div className="mb-4">
          <h4 className="font-bold text-gray-900 mb-2 flex items-center space-x-2">
            <Calendar className="w-4 h-4" />
            <span>Upcoming Events</span>
          </h4>
          <div className="space-y-2">
            {prediction.upcoming_events.map((event, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-900">{event.type}</span>
                <span className="text-sm text-gray-600">{event.date}</span>
                <span className="text-xs font-medium text-gray-700">{event.importance}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {prediction.likely_triggers.length > 0 && (
        <div className="mb-4">
          <h4 className="font-bold text-gray-900 mb-2">Likely Triggers</h4>
          <ul className="list-disc list-inside space-y-1">
            {prediction.likely_triggers.map((trigger, idx) => (
              <li key={idx} className="text-sm text-gray-700">{trigger}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-teal-600" />
          <span>AI Analysis</span>
        </h4>
        <div className="prose prose-sm max-w-none text-gray-800">
          <ReactMarkdown>{prediction.ai_analysis}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
