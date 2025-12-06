import { Loader2, TrendingUp } from 'lucide-react';
import type { PredictionsResponse } from '../types/trading';
import { PredictionCard } from './PredictionCard';

interface PredictionsSectionProps {
  data: PredictionsResponse | null;
  isLoading: boolean;
  error: string | null;
}

export function PredictionsSection({ data, isLoading, error }: PredictionsSectionProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-12">
        <div className="flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-10 h-10 text-teal-600 animate-spin" />
          <p className="text-sm text-gray-600">Fetching predictions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
          Error: {error}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-12">
        <div className="text-center text-gray-500">
          <TrendingUp className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-sm">Click "Get Predictions" to see trading recommendations</p>
        </div>
      </div>
    );
  }

  const sorted = Object.entries(data.predictions).sort(
    (a, b) => Math.abs(b[1].action) - Math.abs(a[1].action)
  );

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <div className="bg-teal-600 text-white rounded-lg p-5 mb-5">
        <h3 className="text-lg font-bold mb-1">Predictions for {data.date}</h3>
        <p className="text-sm opacity-90 mb-3">Based on technical indicators and market conditions</p>
        {data.market_summary && (
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center space-x-1.5">
              <div className="w-2 h-2 bg-green-300 rounded-full"></div>
              <span><strong>{data.market_summary.buy_signals}</strong> Buy</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-2 h-2 bg-red-300 rounded-full"></div>
              <span><strong>{data.market_summary.sell_signals}</strong> Sell</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-2 h-2 bg-amber-300 rounded-full"></div>
              <span><strong>{data.market_summary.hold_signals}</strong> Hold</span>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {sorted.map(([ticker, prediction]) => (
          <PredictionCard key={ticker} ticker={ticker} prediction={prediction} />
        ))}
      </div>
    </div>
  );
}
