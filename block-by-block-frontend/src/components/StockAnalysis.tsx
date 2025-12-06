import { ChevronDown, ChevronUp, TrendingUp, TrendingDown, Activity, Loader2 } from 'lucide-react';
import type { TestResults } from '../types/trading';
import { useState } from 'react';

interface StockAnalysisProps {
  data: TestResults | null;
  isLoading?: boolean;
}

export function StockAnalysis({ data, isLoading }: StockAnalysisProps) {
  const [expandedStock, setExpandedStock] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-12">
        <div className="flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-10 h-10 text-teal-600 animate-spin" />
          <p className="text-sm text-gray-600">Analyzing stocks...</p>
        </div>
      </div>
    );
  }

  if (!data?.results?.stock_metrics) {
    return null;
  }

  const sorted = Object.entries(data.results.stock_metrics).sort(
    (a, b) => b[1].position_value - a[1].position_value
  );

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <h3 className="text-base font-semibold text-gray-900 mb-4">Stock-by-Stock Performance</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {sorted.map(([ticker, metrics]) => {
          const isExpanded = expandedStock === ticker;
          const priceChangeColor = metrics.price_change >= 0 ? 'text-green-600' : 'text-red-600';
          const rsi = metrics.indicators.rsi_30;
          const rsiStatus =
            rsi > 70 ? 'Overbought' : rsi < 30 ? 'Oversold' : 'Neutral';
          const rsiColor =
            rsi > 70 ? 'text-red-600' : rsi < 30 ? 'text-green-600' : 'text-amber-600';

          return (
            <div
              key={ticker}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
            >
              <div className="flex justify-between items-start mb-2">
                <h4 className="text-lg font-bold text-teal-600">{ticker}</h4>
                <div className={`flex items-center space-x-1 ${priceChangeColor}`}>
                  {metrics.price_change >= 0 ? (
                    <TrendingUp className="w-4 h-4" />
                  ) : (
                    <TrendingDown className="w-4 h-4" />
                  )}
                  <span className="font-semibold text-sm">
                    {metrics.price_change.toFixed(2)}%
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                <div>
                  <p className="text-gray-500">Final Price</p>
                  <p className="font-bold text-gray-900">${metrics.final_price.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-gray-500">Shares Held</p>
                  <p className="font-bold text-gray-900">{metrics.final_shares}</p>
                </div>
                <div>
                  <p className="text-gray-500">Position Value</p>
                  <p className="font-bold text-gray-900">
                    ${metrics.position_value.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">Total Trades</p>
                  <p className="font-bold text-gray-900">{metrics.total_trades}</p>
                </div>
              </div>

              <div className="bg-blue-50 rounded p-3 mb-3">
                <div className="text-xs text-gray-600 mb-2">Trading Activity</div>
                <div className="flex justify-between text-xs">
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span>Buys: {metrics.buy_trades}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                    <span>Sells: {metrics.sell_trades}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Activity className="w-3 h-3 text-gray-500" />
                    <span>Avg: {(metrics.avg_action_strength * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setExpandedStock(isExpanded ? null : ticker)}
                className="flex items-center justify-between w-full text-xs text-teal-600 hover:text-blue-700 font-medium"
              >
                <span>Technical Indicators</span>
                {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {isExpanded && (
                <div className="mt-2 p-3 bg-gray-50 rounded border border-gray-200">
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 mb-2">
                    <div>
                      RSI: <span className="font-semibold text-gray-900">{rsi.toFixed(1)}</span>
                    </div>
                    <div>
                      MACD:{' '}
                      <span className="font-semibold text-gray-900">
                        {metrics.indicators.macd.toFixed(2)}
                      </span>
                    </div>
                    <div>
                      CCI:{' '}
                      <span className="font-semibold text-gray-900">
                        {metrics.indicators.cci_30.toFixed(1)}
                      </span>
                    </div>
                    <div>
                      DX:{' '}
                      <span className="font-semibold text-gray-900">
                        {metrics.indicators.dx_30.toFixed(1)}
                      </span>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-gray-200">
                    <span className={`text-xs font-semibold ${rsiColor}`}>
                      {rsiStatus}
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
