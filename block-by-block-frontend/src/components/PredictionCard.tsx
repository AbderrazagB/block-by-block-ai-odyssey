import { TrendingUp, TrendingDown, Minus, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import type { Prediction } from '../types/trading';
import { useState } from 'react';

interface PredictionCardProps {
  ticker: string;
  prediction: Prediction;
}

export function PredictionCard({ ticker, prediction }: PredictionCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  
  const getRecommendationClass = () => {
    const rec = prediction.recommendation.toLowerCase();
    if (rec === 'buy') return 'border-green-200 bg-green-50';
    if (rec === 'sell') return 'border-red-200 bg-red-50';
    return 'border-amber-200 bg-amber-50';
  };

  const getRecommendationColor = () => {
    const rec = prediction.recommendation.toLowerCase();
    if (rec === 'buy') return 'text-green-600';
    if (rec === 'sell') return 'text-red-600';
    return 'text-amber-600';
  };

  const getIcon = () => {
    const rec = prediction.recommendation.toLowerCase();
    if (rec === 'buy') return <TrendingUp className="w-5 h-5" />;
    if (rec === 'sell') return <TrendingDown className="w-5 h-5" />;
    return <Minus className="w-5 h-5" />;
  };

  const getRiskColor = () => {
    if (prediction.risk_score > 70) return 'text-red-600';
    if (prediction.risk_score > 50) return 'text-amber-600';
    return 'text-green-600';
  };

  const getExplanation = () => {
    if (prediction.action > 0.5) {
      return `Strong Buy Signal: Model suggests buying up to ${prediction.estimated_shares} shares. High confidence in upward movement.`;
    } else if (prediction.action > 0.1) {
      return `Moderate Buy: Consider buying ${prediction.estimated_shares} shares. Positive indicators detected.`;
    } else if (prediction.action > -0.1) {
      return `Hold Position: No significant trading signal. Maintain current position.`;
    } else if (prediction.action > -0.5) {
      return `Moderate Sell: Consider selling ${prediction.estimated_shares} shares. Negative indicators detected.`;
    } else {
      return `Strong Sell Signal: Model suggests selling up to ${prediction.estimated_shares} shares. High confidence in downward movement.`;
    }
  };

  const getIndicatorInsight = () => {
    const insights = [];
    const { rsi_30, sma_30, sma_60, macd } = prediction.indicators;
    const price = prediction.current_price;

    if (rsi_30 > 70) insights.push('Overbought (RSI > 70)');
    else if (rsi_30 < 30) insights.push('Oversold (RSI < 30)');

    if (price > sma_30 && sma_30 > sma_60) insights.push('Bullish trend (above SMAs)');
    else if (price < sma_30 && sma_30 < sma_60) insights.push('Bearish trend (below SMAs)');

    if (macd > 0) insights.push('Positive MACD');
    else insights.push('Negative MACD');

    return insights.length > 0 ? insights.join(' • ') : 'Neutral indicators';
  };

  const actionAbs = Math.abs(prediction.action);
  const strengthPercent = Math.min(actionAbs * 100, 100);

  return (
    <div className={`border rounded-lg p-4 hover:shadow-md transition-shadow ${getRecommendationClass()}`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-xl font-bold text-gray-900">{ticker}</h3>
        <div className={`flex items-center space-x-1 ${getRecommendationColor()}`}>
          {getIcon()}
        </div>
      </div>

      <div className={`text-lg font-bold uppercase mb-2 ${getRecommendationColor()}`}>
        {prediction.recommendation}
      </div>

      <p className="text-sm text-gray-600 mb-3">
        Current Price: <span className="font-semibold">${prediction.current_price.toFixed(2)}</span>
      </p>

      <div className="bg-white rounded-lg p-3 mb-3">
        <div className="flex justify-between text-xs text-gray-600 mb-1.5">
          <span>Signal Strength</span>
          <span className="font-semibold">{(actionAbs * 100).toFixed(1)}%</span>
        </div>
        <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all ${
              prediction.recommendation.toLowerCase() === 'buy'
                ? 'bg-green-500'
                : prediction.recommendation.toLowerCase() === 'sell'
                ? 'bg-red-500'
                : 'bg-amber-500'
            }`}
            style={{ width: `${strengthPercent}%` }}
          />
        </div>

        <div className="grid grid-cols-2 gap-2 mt-3">
          <div>
            <span className="text-xs text-gray-500">Confidence</span>
            <p className="font-semibold text-xs">{prediction.confidence_level}</p>
          </div>
          <div>
            <span className="text-xs text-gray-500">Allocation</span>
            <p className="font-semibold text-xs">{prediction.portfolio_allocation.toFixed(1)}%</p>
          </div>
        </div>

        <div className="mt-2 p-2 bg-gray-100 rounded">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-gray-500" />
              <span className="text-xs text-gray-600">Risk Score</span>
            </div>
            <span className={`text-xs font-semibold ${getRiskColor()}`}>
              {prediction.risk_score}/100
            </span>
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-600 mb-2">{getExplanation()}</p>

      <button
        onClick={() => setShowDetails(!showDetails)}
        className="flex items-center justify-between w-full text-xs text-teal-600 hover:text-blue-700 font-medium"
      >
        <span>Technical Indicators</span>
        {showDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>

      {showDetails && (
        <div className="mt-2 p-3 bg-white rounded border border-gray-200">
          <div className="grid grid-cols-2 gap-3 text-sm text-gray-600">
            <div>
              MACD: <span className="font-semibold text-gray-900">{prediction.indicators.macd.toFixed(2)}</span>
            </div>
            <div>
              RSI: <span className="font-semibold text-gray-900">{prediction.indicators.rsi_30.toFixed(1)}</span>
            </div>
            <div>
              CCI: <span className="font-semibold text-gray-900">{prediction.indicators.cci_30.toFixed(1)}</span>
            </div>
            <div>
              DX: <span className="font-semibold text-gray-900">{prediction.indicators.dx_30.toFixed(1)}</span>
            </div>
            <div>
              SMA(30): <span className="font-semibold text-gray-900">${prediction.indicators.sma_30.toFixed(2)}</span>
            </div>
            <div>
              SMA(60): <span className="font-semibold text-gray-900">${prediction.indicators.sma_60.toFixed(2)}</span>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-600">
            {getIndicatorInsight()}
          </div>
        </div>
      )}
    </div>
  );
}
