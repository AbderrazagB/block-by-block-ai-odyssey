import { useState } from 'react';
import { DollarSign, TrendingUp, Shield, Activity, Sparkles, LineChart, AlertTriangle, Target } from 'lucide-react';
import type {
  MarketDataResponse,
  OptionPriceResponse,
  RiskMetricsResponse,
  HedgeRecommendResponse,
  ScenarioAnalysisResponse,
  ImpliedVolatilityResponse,
  StrategyBuildResponse,
  BacktestResponse,
  AlertCreateResponse,
  OptionType,
  ExerciseStyle,
  HedgeType,
  AlertType,
  StrategyName,
  BacktestStrategy,
} from '../types/willowtree';
import ReactMarkdown from 'react-markdown';

interface WillowTreeFinancialProps {
  onGetMarketData: (ticker: string, explain: boolean) => void;
  onPriceOption: (params: any) => void;
  onGetRiskMetrics: (params: any) => void;
  onGetHedgeRecommendation: (params: any) => void;
  onAnalyzeScenario: (params: any) => void;
  onCalculateImpliedVolatility: (params: any) => void;
  onBuildStrategy: (params: any) => void;
  onRunBacktest: (params: any) => void;
  onCreateAlert: (params: any) => void;
  marketData: MarketDataResponse | null;
  optionPrice: OptionPriceResponse | null;
  riskMetrics: RiskMetricsResponse | null;
  hedgeRecommend: HedgeRecommendResponse | null;
  scenarioAnalysis: ScenarioAnalysisResponse | null;
  impliedVolatility: ImpliedVolatilityResponse | null;
  strategyBuild: StrategyBuildResponse | null;
  backtest: BacktestResponse | null;
  alert: AlertCreateResponse | null;
  isLoading: boolean;
  error: string | null;
}

export function WillowTreeFinancial({
  onGetMarketData,
  onPriceOption,
  onGetRiskMetrics,
  onGetHedgeRecommendation,
  onAnalyzeScenario,
  onCalculateImpliedVolatility,
  onBuildStrategy,
  onRunBacktest,
  onCreateAlert,
  marketData,
  optionPrice,
  riskMetrics,
  hedgeRecommend,
  scenarioAnalysis,
  impliedVolatility,
  strategyBuild,
  backtest,
  alert,
  isLoading,
  error,
}: WillowTreeFinancialProps) {
  const [activeTool, setActiveTool] = useState<string>('market-data');

  // Market Data state
  const [marketTicker, setMarketTicker] = useState('AAPL');
  const [marketExplain, setMarketExplain] = useState(false);

  // Option Pricing state
  const [optionTicker, setOptionTicker] = useState('AAPL');
  const [optionStrike, setOptionStrike] = useState(280);
  const [optionDays, setOptionDays] = useState(30);
  const [optionType, setOptionType] = useState<OptionType>('call');
  const [exerciseStyle, setExerciseStyle] = useState<ExerciseStyle>('european');
  const [optionExplain, setOptionExplain] = useState(false);

  // Risk Metrics state
  const [riskTicker, setRiskTicker] = useState('AAPL');
  const [positionSize, setPositionSize] = useState(100);
  const [riskExplain, setRiskExplain] = useState(false);

  // Hedging state
  const [hedgeTicker, setHedgeTicker] = useState('AAPL');
  const [hedgeShares, setHedgeShares] = useState(1000);
  const [hedgeType, setHedgeType] = useState<HedgeType>('protective_put');
  const [protectionLevel, setProtectionLevel] = useState(0.95);
  const [hedgeExplain, setHedgeExplain] = useState(false);

  // Scenario Analysis state
  const [scenarioTicker, setScenarioTicker] = useState('AAPL');
  const [scenarioShares, setScenarioShares] = useState(100);
  const [scenarioExplain, setScenarioExplain] = useState(false);

  // Implied Volatility state
  const [ivTicker, setIvTicker] = useState('AAPL');
  const [ivStrike, setIvStrike] = useState(280);
  const [ivDays, setIvDays] = useState(30);
  const [ivOptionPrice, setIvOptionPrice] = useState(10.0);
  const [ivOptionType, setIvOptionType] = useState<OptionType>('call');
  const [ivExplain, setIvExplain] = useState(false);

  // Strategy Builder state
  const [strategyTicker, setStrategyTicker] = useState('AAPL');
  const [strategyName, setStrategyName] = useState<StrategyName>('iron_condor');
  const [strategyStrikes, setStrategyStrikes] = useState('260,270,290,300');
  const [strategyDays, setStrategyDays] = useState(45);
  const [strategyExplain, setStrategyExplain] = useState(false);

  // Backtest state
  const [backtestTicker, setBacktestTicker] = useState('AAPL');
  const [backtestStrategy, setBacktestStrategy] = useState<BacktestStrategy>('covered_call');
  const [backtestStartDate, setBacktestStartDate] = useState('2024-01-01');
  const [backtestEndDate, setBacktestEndDate] = useState('2024-12-01');
  const [backtestExplain, setBacktestExplain] = useState(false);

  // Alert state
  const [alertTicker, setAlertTicker] = useState('AAPL');
  const [alertType, setAlertType] = useState<AlertType>('price_above');
  const [alertThreshold, setAlertThreshold] = useState(280);
  const [alertExplain, setAlertExplain] = useState(false);

  const handleMarketData = (e: React.FormEvent) => {
    e.preventDefault();
    onGetMarketData(marketTicker, marketExplain);
  };

  const handleOptionPrice = (e: React.FormEvent) => {
    e.preventDefault();
    onPriceOption({
      ticker: optionTicker,
      strike: optionStrike,
      days_to_expiry: optionDays,
      option_type: optionType,
      exercise_style: exerciseStyle,
      explain: optionExplain,
    });
  };

  const handleRiskMetrics = (e: React.FormEvent) => {
    e.preventDefault();
    onGetRiskMetrics({
      ticker: riskTicker,
      position_size: positionSize,
      explain: riskExplain,
    });
  };

  const handleHedgeRecommendation = (e: React.FormEvent) => {
    e.preventDefault();
    onGetHedgeRecommendation({
      ticker: hedgeTicker,
      shares: hedgeShares,
      hedge_type: hedgeType,
      protection_level: protectionLevel,
      explain: hedgeExplain,
    });
  };

  const handleScenarioAnalysis = (e: React.FormEvent) => {
    e.preventDefault();
    onAnalyzeScenario({
      ticker: scenarioTicker,
      position_shares: scenarioShares,
      explain: scenarioExplain,
    });
  };

  const handleImpliedVolatility = (e: React.FormEvent) => {
    e.preventDefault();
    onCalculateImpliedVolatility({
      ticker: ivTicker,
      strike: ivStrike,
      days_to_expiry: ivDays,
      option_price: ivOptionPrice,
      option_type: ivOptionType,
      explain: ivExplain,
    });
  };

  const handleStrategyBuild = (e: React.FormEvent) => {
    e.preventDefault();
    const strikes = strategyStrikes.split(',').map(s => parseFloat(s.trim()));
    onBuildStrategy({
      ticker: strategyTicker,
      strategy_name: strategyName,
      strikes,
      days_to_expiry: strategyDays,
      explain: strategyExplain,
    });
  };

  const handleBacktest = (e: React.FormEvent) => {
    e.preventDefault();
    onRunBacktest({
      ticker: backtestTicker,
      strategy_name: backtestStrategy,
      start_date: backtestStartDate,
      end_date: backtestEndDate,
      explain: backtestExplain,
    });
  };

  const handleAlert = (e: React.FormEvent) => {
    e.preventDefault();
    onCreateAlert({
      ticker: alertTicker,
      alert_type: alertType,
      threshold: alertThreshold,
      explain: alertExplain,
    });
  };

  const tools = [
    { id: 'market-data', name: 'Market Data', icon: Activity },
    { id: 'option-pricing', name: 'Option Pricing', icon: DollarSign },
    { id: 'risk-metrics', name: 'Risk Metrics', icon: TrendingUp },
    { id: 'hedging', name: 'Hedging', icon: Shield },
    { id: 'scenario', name: 'Scenario Analysis', icon: LineChart },
    { id: 'implied-vol', name: 'Implied Volatility', icon: Activity },
    { id: 'strategy', name: 'Strategy Builder', icon: Target },
    { id: 'backtest', name: 'Backtesting', icon: LineChart },
    { id: 'alerts', name: 'Alerts', icon: AlertTriangle },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Left Column - Tools */}
      <div className="space-y-6 border-r border-gray-200 pr-8">
        {/* Tool Selector */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-slate-600" />
            <span>Financial Engineering Tools</span>
          </h2>
          <div className="grid grid-cols-3 gap-3">
            {tools.map((tool) => {
              const Icon = tool.icon;
              return (
                <button
                  key={tool.id}
                  onClick={() => setActiveTool(tool.id)}
                  className={`p-3 rounded-lg border text-xs font-medium transition-all shadow-sm hover:shadow ${
                    activeTool === tool.id
                      ? 'bg-slate-600 text-white border-slate-600'
                      : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-4 h-4 mx-auto mb-1" />
                  {tool.name}
                </button>
              );
            })}
          </div>
        </div>

        {/* Market Data Tool */}
        {activeTool === 'market-data' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-5">Market Data</h3>
            <form onSubmit={handleMarketData} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Ticker</label>
                <input
                  type="text"
                  value={marketTicker}
                  onChange={(e) => setMarketTicker(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent transition-all"
                  placeholder="AAPL"
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={marketExplain}
                  onChange={(e) => setMarketExplain(e.target.checked)}
                  className="rounded"
                />
                <label className="text-sm text-gray-700">Get AI Explanation</label>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-slate-600 text-white py-2.5 rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-all shadow-sm hover:shadow font-medium"
              >
                {isLoading ? 'Loading...' : 'Fetch Market Data'}
              </button>
            </form>
          </div>
        )}

        {/* Option Pricing Tool */}
        {activeTool === 'option-pricing' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Option Pricing</h3>
            <form onSubmit={handleOptionPrice} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
                  <input
                    type="text"
                    value={optionTicker}
                    onChange={(e) => setOptionTicker(e.target.value.toUpperCase())}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Strike</label>
                  <input
                    type="number"
                    value={optionStrike}
                    onChange={(e) => setOptionStrike(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Days to Expiry</label>
                  <input
                    type="number"
                    value={optionDays}
                    onChange={(e) => setOptionDays(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Option Type</label>
                  <select
                    value={optionType}
                    onChange={(e) => setOptionType(e.target.value as OptionType)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="call">Call</option>
                    <option value="put">Put</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Exercise Style</label>
                  <select
                    value={exerciseStyle}
                    onChange={(e) => setExerciseStyle(e.target.value as ExerciseStyle)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="european">European</option>
                    <option value="american">American</option>
                  </select>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={optionExplain}
                  onChange={(e) => setOptionExplain(e.target.checked)}
                  className="rounded"
                />
                <label className="text-sm text-gray-700">Get AI Explanation</label>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-slate-600 text-white py-2.5 rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-all shadow-sm hover:shadow font-medium"
              >
                {isLoading ? 'Calculating...' : 'Price Option'}
              </button>
            </form>
          </div>
        )}

        {/* Risk Metrics Tool */}
        {activeTool === 'risk-metrics' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Risk Metrics</h3>
            <form onSubmit={handleRiskMetrics} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
                <input
                  type="text"
                  value={riskTicker}
                  onChange={(e) => setRiskTicker(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Position Size (shares)</label>
                <input
                  type="number"
                  value={positionSize}
                  onChange={(e) => setPositionSize(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={riskExplain}
                  onChange={(e) => setRiskExplain(e.target.checked)}
                  className="rounded"
                />
                <label className="text-sm text-gray-700">Get AI Explanation</label>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-slate-600 text-white py-2.5 rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-all shadow-sm hover:shadow font-medium"
              >
                {isLoading ? 'Calculating...' : 'Calculate Risk Metrics'}
              </button>
            </form>
          </div>
        )}

        {/* Hedging Tool */}
        {activeTool === 'hedging' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Hedging Recommendations</h3>
            <form onSubmit={handleHedgeRecommendation} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
                  <input
                    type="text"
                    value={hedgeTicker}
                    onChange={(e) => setHedgeTicker(e.target.value.toUpperCase())}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Shares</label>
                  <input
                    type="number"
                    value={hedgeShares}
                    onChange={(e) => setHedgeShares(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Hedge Type</label>
                  <select
                    value={hedgeType}
                    onChange={(e) => setHedgeType(e.target.value as HedgeType)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="delta_neutral">Delta Neutral</option>
                    <option value="protective_put">Protective Put</option>
                    <option value="collar">Collar</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Protection Level (0-1)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={protectionLevel}
                    onChange={(e) => setProtectionLevel(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={hedgeExplain}
                  onChange={(e) => setHedgeExplain(e.target.checked)}
                  className="rounded"
                />
                <label className="text-sm text-gray-700">Get AI Explanation</label>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-slate-600 text-white py-2.5 rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-all shadow-sm hover:shadow font-medium"
              >
                {isLoading ? 'Calculating...' : 'Get Hedge Recommendation'}
              </button>
            </form>
          </div>
        )}

        {/* Scenario Analysis Tool */}
        {activeTool === 'scenario' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Scenario Analysis</h3>
            <form onSubmit={handleScenarioAnalysis} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
                  <input
                    type="text"
                    value={scenarioTicker}
                    onChange={(e) => setScenarioTicker(e.target.value.toUpperCase())}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Position (shares)</label>
                  <input
                    type="number"
                    value={scenarioShares}
                    onChange={(e) => setScenarioShares(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={scenarioExplain}
                  onChange={(e) => setScenarioExplain(e.target.checked)}
                  className="rounded"
                />
                <label className="text-sm text-gray-700">Get AI Explanation</label>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-slate-600 text-white py-2.5 rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-all shadow-sm hover:shadow font-medium"
              >
                {isLoading ? 'Analyzing...' : 'Run Scenario Analysis'}
              </button>
            </form>
          </div>
        )}

        {/* Implied Volatility Tool */}
        {activeTool === 'implied-vol' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Implied Volatility Calculator</h3>
            <form onSubmit={handleImpliedVolatility} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
                  <input
                    type="text"
                    value={ivTicker}
                    onChange={(e) => setIvTicker(e.target.value.toUpperCase())}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Strike</label>
                  <input
                    type="number"
                    value={ivStrike}
                    onChange={(e) => setIvStrike(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Days to Expiry</label>
                  <input
                    type="number"
                    value={ivDays}
                    onChange={(e) => setIvDays(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Option Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={ivOptionPrice}
                    onChange={(e) => setIvOptionPrice(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Option Type</label>
                  <select
                    value={ivOptionType}
                    onChange={(e) => setIvOptionType(e.target.value as OptionType)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="call">Call</option>
                    <option value="put">Put</option>
                  </select>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={ivExplain}
                  onChange={(e) => setIvExplain(e.target.checked)}
                  className="rounded"
                />
                <label className="text-sm text-gray-700">Get AI Explanation</label>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-slate-600 text-white py-2.5 rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-all shadow-sm hover:shadow font-medium"
              >
                {isLoading ? 'Calculating...' : 'Calculate Implied Volatility'}
              </button>
            </form>
          </div>
        )}

        {/* Strategy Builder Tool */}
        {activeTool === 'strategy' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Strategy Builder</h3>
            <form onSubmit={handleStrategyBuild} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
                <input
                  type="text"
                  value={strategyTicker}
                  onChange={(e) => setStrategyTicker(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Strategy</label>
                <select
                  value={strategyName}
                  onChange={(e) => setStrategyName(e.target.value as StrategyName)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="bull_call_spread">Bull Call Spread</option>
                  <option value="bear_put_spread">Bear Put Spread</option>
                  <option value="iron_condor">Iron Condor</option>
                  <option value="butterfly">Butterfly</option>
                  <option value="straddle">Straddle</option>
                  <option value="strangle">Strangle</option>
                  <option value="collar">Collar</option>
                  <option value="calendar_spread">Calendar Spread</option>
                  <option value="ratio_spread">Ratio Spread</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Strikes (comma-separated)
                </label>
                <input
                  type="text"
                  value={strategyStrikes}
                  onChange={(e) => setStrategyStrikes(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="260,270,290,300"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Days to Expiry</label>
                <input
                  type="number"
                  value={strategyDays}
                  onChange={(e) => setStrategyDays(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={strategyExplain}
                  onChange={(e) => setStrategyExplain(e.target.checked)}
                  className="rounded"
                />
                <label className="text-sm text-gray-700">Get AI Explanation</label>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-slate-600 text-white py-2.5 rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-all shadow-sm hover:shadow font-medium"
              >
                {isLoading ? 'Building...' : 'Build Strategy'}
              </button>
            </form>
          </div>
        )}

        {/* Backtest Tool */}
        {activeTool === 'backtest' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Backtesting</h3>
            <form onSubmit={handleBacktest} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
                <input
                  type="text"
                  value={backtestTicker}
                  onChange={(e) => setBacktestTicker(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Strategy</label>
                <select
                  value={backtestStrategy}
                  onChange={(e) => setBacktestStrategy(e.target.value as BacktestStrategy)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="buy_and_hold">Buy and Hold</option>
                  <option value="covered_call">Covered Call</option>
                  <option value="protective_put">Protective Put</option>
                  <option value="iron_condor">Iron Condor</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={backtestStartDate}
                    onChange={(e) => setBacktestStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                  <input
                    type="date"
                    value={backtestEndDate}
                    onChange={(e) => setBacktestEndDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={backtestExplain}
                  onChange={(e) => setBacktestExplain(e.target.checked)}
                  className="rounded"
                />
                <label className="text-sm text-gray-700">Get AI Explanation</label>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-slate-600 text-white py-2.5 rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-all shadow-sm hover:shadow font-medium"
              >
                {isLoading ? 'Running...' : 'Run Backtest'}
              </button>
            </form>
          </div>
        )}

        {/* Alerts Tool */}
        {activeTool === 'alerts' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Alerts</h3>
            <form onSubmit={handleAlert} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ticker</label>
                <input
                  type="text"
                  value={alertTicker}
                  onChange={(e) => setAlertTicker(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Alert Type</label>
                <select
                  value={alertType}
                  onChange={(e) => setAlertType(e.target.value as AlertType)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="price_above">Price Above</option>
                  <option value="price_below">Price Below</option>
                  <option value="volatility_spike">Volatility Spike</option>
                  <option value="delta_change">Delta Change</option>
                  <option value="gamma_risk">Gamma Risk</option>
                  <option value="theta_decay">Theta Decay</option>
                  <option value="iv_rank">IV Rank</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Threshold</label>
                <input
                  type="number"
                  step="0.01"
                  value={alertThreshold}
                  onChange={(e) => setAlertThreshold(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={alertExplain}
                  onChange={(e) => setAlertExplain(e.target.checked)}
                  className="rounded"
                />
                <label className="text-sm text-gray-700">Get AI Explanation</label>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-slate-600 text-white py-2.5 rounded-lg hover:bg-slate-700 disabled:opacity-50 transition-all shadow-sm hover:shadow font-medium"
              >
                {isLoading ? 'Creating...' : 'Create Alert'}
              </button>
            </form>
          </div>
        )}
      </div>

      {/* Right Column - Results */}
      <div className="space-y-6 pl-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4">
            <p className="text-red-800 text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Market Data Results */}
        {marketData && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">{marketData.ticker} Market Data</h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-600">Current Price</p>
                <p className="text-lg font-bold">${marketData.current_price.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Historical Volatility</p>
                <p className="text-lg font-bold">{(marketData.historical_volatility * 100).toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Risk-Free Rate</p>
                <p className="text-lg font-bold">{(marketData.risk_free_rate * 100).toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Dividend Yield</p>
                <p className="text-lg font-bold">
                  {marketData.dividend_yield ? (marketData.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}
                </p>
              </div>
            </div>
            {marketData.ai_explanation && (
              <div className="border-t pt-4">
                <p className="text-xs font-medium text-gray-700 mb-2">AI Analysis:</p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{marketData.ai_explanation.explanation}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Option Pricing Results */}
        {optionPrice && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {optionPrice.ticker} {optionPrice.option_type.toUpperCase()} Option
            </h3>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-600">Price</p>
                <p className="text-lg font-bold text-green-600">${optionPrice.price.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Delta</p>
                <p className="text-lg font-bold">{optionPrice.delta.toFixed(3)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Gamma</p>
                <p className="text-lg font-bold">{optionPrice.gamma.toFixed(3)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Theta</p>
                <p className="text-lg font-bold">{optionPrice.theta.toFixed(3)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Vega</p>
                <p className="text-lg font-bold">{optionPrice.vega.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Rho</p>
                <p className="text-lg font-bold">{optionPrice.rho.toFixed(2)}</p>
              </div>
            </div>
            {optionPrice.ai_explanation && (
              <div className="border-t pt-4">
                <p className="text-xs font-medium text-gray-700 mb-2">AI Analysis:</p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{optionPrice.ai_explanation.explanation}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Risk Metrics Results */}
        {riskMetrics && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">{riskMetrics.ticker} Risk Analysis</h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-600">Portfolio Value</p>
                <p className="text-lg font-bold">${riskMetrics.portfolio_value.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">VaR (1-day, 95%)</p>
                <p className="text-lg font-bold text-red-600">${riskMetrics.var_1day.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">CVaR</p>
                <p className="text-lg font-bold text-red-600">${riskMetrics.cvar_1day.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Sharpe Ratio</p>
                <p className="text-lg font-bold">{riskMetrics.sharpe_ratio.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Sortino Ratio</p>
                <p className="text-lg font-bold">{riskMetrics.sortino_ratio.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Max Drawdown</p>
                <p className="text-lg font-bold text-red-600">{(riskMetrics.max_drawdown * 100).toFixed(2)}%</p>
              </div>
            </div>
            {riskMetrics.ai_explanation && (
              <div className="border-t pt-4">
                <p className="text-xs font-medium text-gray-700 mb-2">AI Analysis:</p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{riskMetrics.ai_explanation.explanation}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Hedge Recommendation Results */}
        {hedgeRecommend && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {hedgeRecommend.ticker} Hedge Strategy
            </h3>
            <div className="mb-4">
              <p className="text-sm text-gray-700">{hedgeRecommend.recommendation}</p>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-600">Cost</p>
                <p className="text-lg font-bold text-red-600">${hedgeRecommend.cost.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Portfolio Delta</p>
                <p className="text-lg font-bold">{hedgeRecommend.total_portfolio_delta.toFixed(2)}</p>
              </div>
              {hedgeRecommend.protected_downside && (
                <div>
                  <p className="text-xs text-gray-600">Protected Downside</p>
                  <p className="text-lg font-bold">${hedgeRecommend.protected_downside.toFixed(2)}</p>
                </div>
              )}
              {hedgeRecommend.upside_cap && (
                <div>
                  <p className="text-xs text-gray-600">Upside Cap</p>
                  <p className="text-lg font-bold">${hedgeRecommend.upside_cap.toFixed(2)}</p>
                </div>
              )}
            </div>
            {hedgeRecommend.ai_explanation && (
              <div className="border-t pt-4">
                <p className="text-xs font-medium text-gray-700 mb-2">AI Analysis:</p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{hedgeRecommend.ai_explanation.explanation}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Scenario Analysis Results */}
        {scenarioAnalysis && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {scenarioAnalysis.ticker} Scenario Analysis
            </h3>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-green-50 p-3 rounded">
                <p className="text-xs text-gray-600 mb-1">Best Case</p>
                <p className="text-lg font-bold text-green-600">
                  ${scenarioAnalysis.best_case.pnl.toFixed(2)}
                </p>
                <p className="text-xs text-gray-600">
                  ({(scenarioAnalysis.best_case.price_change * 100).toFixed(1)}% price change)
                </p>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-xs text-gray-600 mb-1">Base Case</p>
                <p className="text-lg font-bold text-gray-700">
                  ${scenarioAnalysis.base_case.pnl.toFixed(2)}
                </p>
                <p className="text-xs text-gray-600">
                  ({(scenarioAnalysis.base_case.price_change * 100).toFixed(1)}% price change)
                </p>
              </div>
              <div className="bg-red-50 p-3 rounded">
                <p className="text-xs text-gray-600 mb-1">Worst Case</p>
                <p className="text-lg font-bold text-red-600">
                  ${scenarioAnalysis.worst_case.pnl.toFixed(2)}
                </p>
                <p className="text-xs text-gray-600">
                  ({(scenarioAnalysis.worst_case.price_change * 100).toFixed(1)}% price change)
                </p>
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-xs font-medium text-gray-700">All Scenarios:</p>
              {scenarioAnalysis.scenarios.slice(0, 5).map((scenario, idx) => (
                <div key={idx} className="flex justify-between items-center text-sm border-b pb-2">
                  <span className="text-gray-600">
                    Price: ${scenario.new_price.toFixed(2)} ({(scenario.price_change * 100).toFixed(1)}%)
                  </span>
                  <span className={scenario.pnl >= 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
                    ${scenario.pnl.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
            {scenarioAnalysis.ai_explanation && (
              <div className="border-t pt-4 mt-4">
                <p className="text-xs font-medium text-gray-700 mb-2">AI Analysis:</p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{scenarioAnalysis.ai_explanation.explanation}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Implied Volatility Results */}
        {impliedVolatility && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {impliedVolatility.ticker} Implied Volatility
            </h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-600">Implied Volatility</p>
                <p className="text-lg font-bold text-slate-600">
                  {(impliedVolatility.implied_volatility * 100).toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Historical Volatility</p>
                <p className="text-lg font-bold">{(impliedVolatility.historical_volatility * 100).toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">IV-HV Spread</p>
                <p className="text-lg font-bold">{(impliedVolatility.iv_hv_spread * 100).toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">IV Rank</p>
                <p className="text-lg font-bold">{impliedVolatility.iv_rank.toFixed(1)}</p>
              </div>
            </div>
            {impliedVolatility.ai_explanation && (
              <div className="border-t pt-4">
                <p className="text-xs font-medium text-gray-700 mb-2">AI Analysis:</p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{impliedVolatility.ai_explanation.explanation}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Strategy Build Results */}
        {strategyBuild && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {strategyBuild.ticker} - {strategyBuild.strategy_name}
            </h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-600">Net Premium</p>
                <p className="text-lg font-bold">${strategyBuild.net_premium.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Max Profit</p>
                <p className="text-lg font-bold text-green-600">${strategyBuild.max_profit.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Max Loss</p>
                <p className="text-lg font-bold text-red-600">${strategyBuild.max_loss.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Risk/Reward</p>
                <p className="text-lg font-bold">{strategyBuild.risk_reward_ratio.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Delta</p>
                <p className="text-lg font-bold">{strategyBuild.delta.toFixed(3)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Theta</p>
                <p className="text-lg font-bold">{strategyBuild.theta.toFixed(2)}</p>
              </div>
            </div>
            <div className="mb-4">
              <p className="text-xs text-gray-600 mb-1">Breakeven Points:</p>
              <p className="text-sm font-medium">
                {strategyBuild.breakeven_points.map(bp => `$${bp.toFixed(2)}`).join(', ')}
              </p>
            </div>
            {strategyBuild.ai_explanation && (
              <div className="border-t pt-4">
                <p className="text-xs font-medium text-gray-700 mb-2">AI Analysis:</p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{strategyBuild.ai_explanation.explanation}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Backtest Results */}
        {backtest && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {backtest.ticker} - {backtest.strategy_name}
            </h3>
            <p className="text-xs text-gray-600 mb-4">{backtest.period}</p>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-600">Total Return</p>
                <p className="text-lg font-bold text-green-600">
                  {(backtest.total_return * 100).toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Annualized Return</p>
                <p className="text-lg font-bold">{(backtest.annualized_return * 100).toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Sharpe Ratio</p>
                <p className="text-lg font-bold">{backtest.sharpe_ratio.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Sortino Ratio</p>
                <p className="text-lg font-bold">{backtest.sortino_ratio.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Max Drawdown</p>
                <p className="text-lg font-bold text-red-600">{(backtest.max_drawdown * 100).toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Win Rate</p>
                <p className="text-lg font-bold">{(backtest.win_rate * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Total Trades</p>
                <p className="text-lg font-bold">{backtest.total_trades}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Alpha vs Benchmark</p>
                <p className="text-lg font-bold">{(backtest.alpha * 100).toFixed(2)}%</p>
              </div>
            </div>
            {backtest.ai_explanation && (
              <div className="border-t pt-4">
                <p className="text-xs font-medium text-gray-700 mb-2">AI Analysis:</p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{backtest.ai_explanation.explanation}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Alert Results */}
        {alert && (
          <div className={`rounded-lg border p-6 shadow-sm ${
            alert.triggered ? 'bg-red-50 border-red-200' : 'bg-white border-gray-200'
          }`}>
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {alert.ticker} Alert - {alert.alert_type}
            </h3>
            <div className="mb-4">
              <p className={`text-sm font-medium ${alert.triggered ? 'text-red-700' : 'text-gray-700'}`}>
                {alert.message}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-600">Current Value</p>
                <p className="text-lg font-bold">{alert.current_value.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Threshold</p>
                <p className="text-lg font-bold">{alert.threshold.toFixed(2)}</p>
              </div>
            </div>
            {alert.ai_explanation && (
              <div className="border-t pt-4 mt-4">
                <p className="text-xs font-medium text-gray-700 mb-2">AI Analysis:</p>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown>{alert.ai_explanation.explanation}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
