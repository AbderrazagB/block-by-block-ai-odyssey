import { useEffect, useState } from 'react';
import { TrendingUp, BarChart3, Activity, Rocket, Banknote, Sparkles } from 'lucide-react';
import { tradingApi, monteCarloApi, startupApi, willowTreeApi, transformerApi } from './services/api';
import type { PredictionsResponse, TestResults } from './types/trading';
import type { SimulateResponse } from './types/montecarlo';
import type { SearchResponse, AnalysisResponse, JobStatus, IndustrySuggestion } from './types/startup';
import type { TransformerPredictionResponse } from './types/transformer';
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
} from './types/willowtree';
import { ControlPanel } from './components/ControlPanel';
import { PredictionsSection } from './components/PredictionsSection';
import { PerformanceMetrics } from './components/PerformanceMetrics';
import { PortfolioChart } from './components/PortfolioChart';
import { HoldingsChart } from './components/HoldingsChart';
import { StockAnalysis } from './components/StockAnalysis';
import { MonteCarloSimulation } from './components/MonteCarloSimulation';
import { StartupFinder } from './components/StartupFinder';
import { WillowTreeFinancial } from './components/WillowTreeFinancial';
import { StockTransformer } from './components/StockTransformer';

type TabType = 'trading' | 'montecarlo' | 'startup' | 'willowtree' | 'transformer';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('trading');
  
  // Trading Model State
  const [tradingOnline, setTradingOnline] = useState(false);
  const [predictions, setPredictions] = useState<PredictionsResponse | null>(null);
  const [testResults, setTestResults] = useState<TestResults | null>(null);
  const [isLoadingPredictions, setIsLoadingPredictions] = useState(false);
  const [isLoadingTest, setIsLoadingTest] = useState(false);
  const [predictionsError, setPredictionsError] = useState<string | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  // Monte Carlo State
  const [monteCarloOnline, setMonteCarloOnline] = useState(false);
  const [monteCarloData, setMonteCarloData] = useState<SimulateResponse | null>(null);
  const [isLoadingMonteCarlo, setIsLoadingMonteCarlo] = useState(false);
  const [monteCarloError, setMonteCarloError] = useState<string | null>(null);

  // Startup Finder State
  const [startupOnline, setStartupOnline] = useState(false);
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [isLoadingSearch, setIsLoadingSearch] = useState(false);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [industrySuggestions, setIndustrySuggestions] = useState<IndustrySuggestion[]>([]);

  // Willow Tree Financial State
  const [willowTreeOnline, setWillowTreeOnline] = useState(false);
  const [marketData, setMarketData] = useState<MarketDataResponse | null>(null);
  const [optionPrice, setOptionPrice] = useState<OptionPriceResponse | null>(null);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetricsResponse | null>(null);
  const [hedgeRecommend, setHedgeRecommend] = useState<HedgeRecommendResponse | null>(null);
  const [scenarioAnalysis, setScenarioAnalysis] = useState<ScenarioAnalysisResponse | null>(null);
  const [impliedVolatility, setImpliedVolatility] = useState<ImpliedVolatilityResponse | null>(null);
  const [strategyBuild, setStrategyBuild] = useState<StrategyBuildResponse | null>(null);
  const [backtest, setBacktest] = useState<BacktestResponse | null>(null);
  const [alert, setAlert] = useState<AlertCreateResponse | null>(null);
  const [isLoadingWillowTree, setIsLoadingWillowTree] = useState(false);
  const [willowTreeError, setWillowTreeError] = useState<string | null>(null);

  // Stock Transformer State
  const [transformerOnline, setTransformerOnline] = useState(false);
  const [transformerData, setTransformerData] = useState<TransformerPredictionResponse | null>(null);
  const [isLoadingTransformer, setIsLoadingTransformer] = useState(false);
  const [transformerError, setTransformerError] = useState<string | null>(null);

  useEffect(() => {
    checkTradingHealth();
    getModelInfo();
    checkMonteCarloHealth();
    checkStartupHealth();
    checkWillowTreeHealth();
    checkTransformerHealth();
    loadIndustrySuggestions();
  }, []);

  // Trading Model Functions
  const checkTradingHealth = async () => {
    try {
      const data = await tradingApi.checkHealth();
      setTradingOnline(data.model_loaded);
    } catch {
      setTradingOnline(false);
    }
  };

  const getModelInfo = async () => {
    try {
      await tradingApi.getModelInfo();
    } catch (_error) {
      console.error('Error fetching model info:', _error);
    }
  };

  // Monte Carlo Functions
  const checkMonteCarloHealth = async () => {
    try {
      const data = await monteCarloApi.checkHealth();
      setMonteCarloOnline(data.status === 'healthy');
    } catch {
      setMonteCarloOnline(false);
    }
  };

  // Startup Finder Functions
  const checkStartupHealth = async () => {
    try {
      const data = await startupApi.checkHealth();
      setStartupOnline(data.status === 'healthy');
    } catch {
      setStartupOnline(false);
    }
  };

  const loadIndustrySuggestions = async () => {
    try {
      const data = await startupApi.getIndustrySuggestions();
      setIndustrySuggestions(data.suggestions);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const handleGetPredictions = async (endDate: string) => {
    setIsLoadingPredictions(true);
    setPredictionsError(null);
    try {
      const data = await tradingApi.getPredictions(endDate);
      if (data.success) {
        setPredictions(data);
      } else {
        setPredictionsError(data.error || 'Failed to get predictions');
      }
    } catch (error) {
      setPredictionsError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingPredictions(false);
    }
  };

  const handleTestModel = async (params: {
    startDate: string;
    endDate: string;
    initialAmount: number;
    hmax: number;
    transactionCost: number;
  }) => {
    setIsLoadingTest(true);
    setTestError(null);
    try {
      const data = await tradingApi.testModel({
        start_date: params.startDate,
        end_date: params.endDate,
        initial_amount: params.initialAmount,
        hmax: params.hmax,
        transaction_cost: params.transactionCost,
      });
      if (data.success) {
        setTestResults(data);
      } else {
        setTestError(data.error || 'Failed to test model');
      }
    } catch (error) {
      setTestError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingTest(false);
    }
  };

  const handleMonteCarloSimulation = async (params: {
    ticker: string;
    period: string;
    forecast_days: number;
    num_simulations: number;
    analyze_jumps: boolean;
    include_prediction: boolean;
  }) => {
    setIsLoadingMonteCarlo(true);
    setMonteCarloError(null);
    try {
      const data = await monteCarloApi.simulate(params);
      setMonteCarloData(data);
    } catch (error) {
      setMonteCarloError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingMonteCarlo(false);
    }
  };

  const handleStartupSearch = async (params: {
    industry: string;
    num_queries?: number;
    max_results?: number;
  }) => {
    setIsLoadingSearch(true);
    setSearchError(null);
    setSearchData(null);
    try {
      const data = await startupApi.searchStartups(params);
      setSearchData(data);
    } catch (error) {
      setSearchError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingSearch(false);
    }
  };

  const handleStartupAnalysis = async (params: {
    industry: string;
    top_n?: number;
    num_queries?: number;
    max_results?: number;
  }) => {
    setIsLoadingAnalysis(true);
    setAnalysisError(null);
    setAnalysisData(null);
    try {
      const data = await startupApi.analyzeIndustry(params);
      setAnalysisData(data);
    } catch (error) {
      setAnalysisError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const handleAsyncAnalysis = async (params: { industry: string; top_n?: number }) => {
    setIsLoadingAnalysis(true);
    setAnalysisError(null);
    setAnalysisData(null);
    setJobStatus(null);
    try {
      const job = await startupApi.startAsyncAnalysis(params);
      setJobStatus({ ...job, progress: null, result: null, error: null });
      
      // Poll for completion
      const finalStatus = await startupApi.waitForJob(job.job_id, (status) => {
        setJobStatus(status);
      });

      if (finalStatus.status === 'completed' && finalStatus.result) {
        // Convert result to AnalysisResponse format
        setAnalysisData({
          industry: finalStatus.result.industry,
          total_startups_found: finalStatus.result.total_startups_found,
          startups_analyzed: finalStatus.result.startups_analyzed,
          analysis_timestamp: finalStatus.result.analysis_timestamp,
          analyses: finalStatus.result.analyses.map(a => ({
            name: a.name,
            linkedin_url: a.linkedin_url,
            website_url: a.website_url,
            analysis: a.analysis,
            stock_data: null, // Simplified result doesn't include full stock data
          })),
          recommendations: finalStatus.result.recommendations,
        });
      }
    } catch (error) {
      setAnalysisError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  // Willow Tree Financial Functions
  const checkWillowTreeHealth = async () => {
    try {
      const data = await willowTreeApi.checkHealth();
      setWillowTreeOnline(data.status === 'ok' || data.status === 'healthy');
    } catch {
      setWillowTreeOnline(false);
    }
  };

  // Stock Transformer Functions
  const checkTransformerHealth = async () => {
    try {
      const data = await transformerApi.checkHealth();
      setTransformerOnline(data.status === 'healthy');
    } catch {
      setTransformerOnline(false);
    }
  };

  const handleGetTransformerPrediction = async (ticker: string) => {
    setIsLoadingTransformer(true);
    setTransformerError(null);
    setTransformerData(null);
    try {
      const data = await transformerApi.getPrediction(ticker);
      setTransformerData(data);
    } catch (error) {
      setTransformerError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingTransformer(false);
    }
  };

  const handleGetMarketData = async (ticker: string, explain: boolean) => {
    setIsLoadingWillowTree(true);
    setWillowTreeError(null);
    setMarketData(null);
    try {
      const data = await willowTreeApi.getMarketData(ticker, explain);
      setMarketData(data);
    } catch (error) {
      setWillowTreeError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingWillowTree(false);
    }
  };

  const handlePriceOption = async (params: any) => {
    setIsLoadingWillowTree(true);
    setWillowTreeError(null);
    setOptionPrice(null);
    try {
      const data = await willowTreeApi.priceOption(params);
      setOptionPrice(data);
    } catch (error) {
      setWillowTreeError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingWillowTree(false);
    }
  };

  const handleGetRiskMetrics = async (params: any) => {
    setIsLoadingWillowTree(true);
    setWillowTreeError(null);
    setRiskMetrics(null);
    try {
      const data = await willowTreeApi.getRiskMetrics(params);
      setRiskMetrics(data);
    } catch (error) {
      setWillowTreeError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingWillowTree(false);
    }
  };

  const handleGetHedgeRecommendation = async (params: any) => {
    setIsLoadingWillowTree(true);
    setWillowTreeError(null);
    setHedgeRecommend(null);
    try {
      const data = await willowTreeApi.getHedgeRecommendation(params);
      setHedgeRecommend(data);
    } catch (error) {
      setWillowTreeError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingWillowTree(false);
    }
  };

  const handleAnalyzeScenario = async (params: any) => {
    setIsLoadingWillowTree(true);
    setWillowTreeError(null);
    setScenarioAnalysis(null);
    try {
      const data = await willowTreeApi.analyzeScenario(params);
      setScenarioAnalysis(data);
    } catch (error) {
      setWillowTreeError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingWillowTree(false);
    }
  };

  const handleCalculateImpliedVolatility = async (params: any) => {
    setIsLoadingWillowTree(true);
    setWillowTreeError(null);
    setImpliedVolatility(null);
    try {
      const data = await willowTreeApi.calculateImpliedVolatility(params);
      setImpliedVolatility(data);
    } catch (error) {
      setWillowTreeError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingWillowTree(false);
    }
  };

  const handleBuildStrategy = async (params: any) => {
    setIsLoadingWillowTree(true);
    setWillowTreeError(null);
    setStrategyBuild(null);
    try {
      const data = await willowTreeApi.buildStrategy(params);
      setStrategyBuild(data);
    } catch (error) {
      setWillowTreeError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingWillowTree(false);
    }
  };

  const handleRunBacktest = async (params: any) => {
    setIsLoadingWillowTree(true);
    setWillowTreeError(null);
    setBacktest(null);
    try {
      const data = await willowTreeApi.runBacktest(params);
      setBacktest(data);
    } catch (error) {
      setWillowTreeError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingWillowTree(false);
    }
  };

  const handleCreateAlert = async (params: any) => {
    setIsLoadingWillowTree(true);
    setWillowTreeError(null);
    setAlert(null);
    try {
      const data = await willowTreeApi.createAlert(params);
      setAlert(data);
    } catch (error) {
      setWillowTreeError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setIsLoadingWillowTree(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 overflow-x-hidden">
      <div className="w-full max-w-[1800px] mx-auto px-6 sm:px-8 lg:px-12 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <TrendingUp className="w-10 h-10 text-teal-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-teal-600 to-slate-700 bg-clip-text text-transparent">
              Block by Block
            </h1>
          </div>
          <p className="text-gray-600 ml-14 text-lg">
            Advanced financial analytics and investment intelligence
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm mb-8">
          <div className="flex border-b border-gray-200 overflow-x-auto">
            <button
              onClick={() => setActiveTab('trading')}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === 'trading'
                  ? 'text-teal-600 border-b-2 border-teal-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Trading Model</span>
              <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                tradingOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {tradingOnline ? 'Online' : 'Offline'}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('montecarlo')}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === 'montecarlo'
                  ? 'text-teal-600 border-b-2 border-teal-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Monte Carlo</span>
              <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                monteCarloOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {monteCarloOnline ? 'Online' : 'Offline'}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('startup')}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === 'startup'
                  ? 'text-teal-600 border-b-2 border-teal-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Rocket className="w-4 h-4" />
              <span>Startup Finder</span>
              <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                startupOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {startupOnline ? 'Online' : 'Offline'}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('willowtree')}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === 'willowtree'
                  ? 'text-teal-600 border-b-2 border-teal-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Banknote className="w-4 h-4" />
              <span>Willow Tree</span>
              <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                willowTreeOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {willowTreeOnline ? 'Online' : 'Offline'}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('transformer')}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === 'transformer'
                  ? 'text-teal-600 border-b-2 border-teal-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>Stock Transformer</span>
              <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                transformerOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {transformerOnline ? 'Online' : 'Offline'}
              </span>
            </button>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'trading' && (
          <>
            {/* Control Panel */}
            <ControlPanel
              onTest={handleTestModel}
              onPredict={handleGetPredictions}
              isLoading={isLoadingPredictions || isLoadingTest}
            />

            {/* Predictions Section */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Trading Predictions</h2>
              <PredictionsSection
                data={predictions}
                isLoading={isLoadingPredictions}
                error={predictionsError}
              />
            </div>

            {/* Performance Metrics */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Portfolio Performance</h2>
              <PerformanceMetrics data={testResults} isLoading={isLoadingTest} error={testError} />
            </div>

            {/* Charts */}
            {testResults?.results && (
              <>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                  <PortfolioChart data={testResults} isLoading={isLoadingTest} />
                  <HoldingsChart data={testResults} isLoading={isLoadingTest} />
                </div>

                {/* Stock Analysis */}
                <StockAnalysis data={testResults} isLoading={isLoadingTest} />
              </>
            )}
          </>
        )}

        {activeTab === 'montecarlo' && (
          <MonteCarloSimulation
            onSimulate={handleMonteCarloSimulation}
            data={monteCarloData}
            isLoading={isLoadingMonteCarlo}
            error={monteCarloError}
          />
        )}

        {activeTab === 'startup' && (
          <StartupFinder
            onSearch={handleStartupSearch}
            onAnalyze={handleStartupAnalysis}
            onAsyncAnalyze={handleAsyncAnalysis}
            searchData={searchData}
            analysisData={analysisData}
            jobStatus={jobStatus}
            isLoadingSearch={isLoadingSearch}
            isLoadingAnalysis={isLoadingAnalysis}
            searchError={searchError}
            analysisError={analysisError}
            suggestions={industrySuggestions}
          />
        )}

        {activeTab === 'willowtree' && (
          <WillowTreeFinancial
            onGetMarketData={handleGetMarketData}
            onPriceOption={handlePriceOption}
            onGetRiskMetrics={handleGetRiskMetrics}
            onGetHedgeRecommendation={handleGetHedgeRecommendation}
            onAnalyzeScenario={handleAnalyzeScenario}
            onCalculateImpliedVolatility={handleCalculateImpliedVolatility}
            onBuildStrategy={handleBuildStrategy}
            onRunBacktest={handleRunBacktest}
            onCreateAlert={handleCreateAlert}
            marketData={marketData}
            optionPrice={optionPrice}
            riskMetrics={riskMetrics}
            hedgeRecommend={hedgeRecommend}
            scenarioAnalysis={scenarioAnalysis}
            impliedVolatility={impliedVolatility}
            strategyBuild={strategyBuild}
            backtest={backtest}
            alert={alert}
            isLoading={isLoadingWillowTree}
            error={willowTreeError}
          />
        )}

        {activeTab === 'transformer' && (
          <StockTransformer
            onGetPrediction={handleGetTransformerPrediction}
            predictionData={transformerData}
            isLoading={isLoadingTransformer}
            error={transformerError}
          />
        )}
      </div>
    </div>
  );
}

export default App;