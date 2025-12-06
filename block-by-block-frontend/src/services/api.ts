import type {
  HealthResponse,
  ModelInfo,
  PredictionsResponse,
  TestResults,
  TestParams,
} from '../types/trading';
import type {
  SimulateRequest,
  SimulateResponse,
  PredictRequest,
  JumpPrediction,
  AnalyzeJumpEventParams,
  AnalyzeJumpEventResponse,
  HealthResponse as MonteCarloHealthResponse,
} from '../types/montecarlo';
import type {
  StartupSearchRequest,
  SearchResponse,
  StartupAnalysisRequest,
  AnalysisResponse,
  AsyncJobResponse,
  JobStatus,
  ReportsListResponse,
  IndustrySuggestionsResponse,
  HealthResponse as StartupHealthResponse,
} from '../types/startup';
import type {
  MarketDataResponse,
  OptionPriceRequest,
  OptionPriceResponse,
  RiskMetricsRequest,
  RiskMetricsResponse,
  HedgeRecommendRequest,
  HedgeRecommendResponse,
  ScenarioAnalysisRequest,
  ScenarioAnalysisResponse,
  ImpliedVolatilityRequest,
  ImpliedVolatilityResponse,
  StrategyBuildRequest,
  StrategyBuildResponse,
  BacktestRequest,
  BacktestResponse,
  AlertCreateRequest,
  AlertCreateResponse,
} from '../types/willowtree';
import type {
  TransformerPredictionResponse,
  TransformerHealthResponse,
} from '../types/transformer';

const TRADING_API_BASE = 'http://localhost:5000/api';
const MONTECARLO_API_BASE = 'http://localhost:5004';
const STARTUP_API_BASE = 'http://localhost:8000';
const WILLOWTREE_API_BASE = 'http://localhost:8001';
const TRANSFORMER_API_BASE = 'http://localhost:8080';

// Trading Model API (existing server on port 5000)
export const tradingApi = {
  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${TRADING_API_BASE}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  },

  async getModelInfo(): Promise<ModelInfo> {
    const response = await fetch(`${TRADING_API_BASE}/model/info`);
    if (!response.ok) throw new Error('Failed to fetch model info');
    return response.json();
  },

  async getPredictions(date: string): Promise<PredictionsResponse> {
    const response = await fetch(`${TRADING_API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date }),
    });
    if (!response.ok) throw new Error('Failed to fetch predictions');
    return response.json();
  },

  async testModel(params: TestParams): Promise<TestResults> {
    const response = await fetch(`${TRADING_API_BASE}/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) throw new Error('Failed to test model');
    return response.json();
  },
};

// Monte Carlo Jump Diffusion API (new server on port 5004)
export const monteCarloApi = {
  async checkHealth(): Promise<MonteCarloHealthResponse> {
    const response = await fetch(`${MONTECARLO_API_BASE}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  },

  async simulate(params: SimulateRequest): Promise<SimulateResponse> {
    const response = await fetch(`${MONTECARLO_API_BASE}/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Simulation failed');
    }
    return response.json();
  },

  async predict(params: PredictRequest): Promise<JumpPrediction> {
    const response = await fetch(`${MONTECARLO_API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Prediction failed');
    }
    return response.json();
  },

  async analyzeJumpEvent(params: AnalyzeJumpEventParams): Promise<AnalyzeJumpEventResponse> {
    const queryParams = new URLSearchParams({
      ticker: params.ticker,
      date: params.date,
      return_pct: params.return_pct.toString(),
      crawl_news: (params.crawl_news ?? false).toString(),
    });
    const response = await fetch(`${MONTECARLO_API_BASE}/analyze-jump-event?${queryParams}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Jump analysis failed');
    }
    return response.json();
  },
};

// Startup Finder API (new server on port 8000)
export const startupApi = {
  async checkHealth(): Promise<StartupHealthResponse> {
    const response = await fetch(`${STARTUP_API_BASE}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  },

  async searchStartups(params: StartupSearchRequest): Promise<SearchResponse> {
    const response = await fetch(`${STARTUP_API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Search failed');
    }
    return response.json();
  },

  async analyzeIndustry(params: StartupAnalysisRequest): Promise<AnalysisResponse> {
    const response = await fetch(`${STARTUP_API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Analysis failed');
    }
    return response.json();
  },

  async startAsyncAnalysis(params: StartupAnalysisRequest): Promise<AsyncJobResponse> {
    const response = await fetch(`${STARTUP_API_BASE}/analyze/async`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start analysis');
    }
    return response.json();
  },

  async checkJobStatus(jobId: string): Promise<JobStatus> {
    const response = await fetch(`${STARTUP_API_BASE}/jobs/${jobId}`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to check job status');
    }
    return response.json();
  },

  async listJobs(): Promise<{ jobs: Array<{ job_id: string; status: string; progress: string | null }> }> {
    const response = await fetch(`${STARTUP_API_BASE}/jobs`);
    if (!response.ok) throw new Error('Failed to list jobs');
    return response.json();
  },

  async listReports(): Promise<ReportsListResponse> {
    const response = await fetch(`${STARTUP_API_BASE}/reports`);
    if (!response.ok) throw new Error('Failed to list reports');
    return response.json();
  },

  async getReport(filename: string): Promise<AnalysisResponse> {
    const response = await fetch(`${STARTUP_API_BASE}/reports/${filename}`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get report');
    }
    return response.json();
  },

  async getIndustrySuggestions(): Promise<IndustrySuggestionsResponse> {
    const response = await fetch(`${STARTUP_API_BASE}/industries/suggestions`);
    if (!response.ok) throw new Error('Failed to get suggestions');
    return response.json();
  },

  // Helper function to poll job status until completion
  async waitForJob(
    jobId: string,
    onProgress?: (status: JobStatus) => void
  ): Promise<JobStatus> {
    while (true) {
      const status = await this.checkJobStatus(jobId);
      onProgress?.(status);

      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }

      await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2 seconds
    }
  },
};

// Willow Tree Financial API (port 8001)
export const willowTreeApi = {
  async checkHealth(): Promise<{ status: string }> {
    try {
      const response = await fetch(`${WILLOWTREE_API_BASE}/`);
      if (!response.ok) throw new Error('Health check failed');
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async getMarketData(ticker: string, explain = false): Promise<MarketDataResponse> {
    try {
      const response = await fetch(
        `${WILLOWTREE_API_BASE}/api/market-data/${ticker}?explain=${explain}`
      );
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch market data');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async priceOption(params: OptionPriceRequest): Promise<OptionPriceResponse> {
    try {
      const response = await fetch(`${WILLOWTREE_API_BASE}/api/option/price`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to price option');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async getRiskMetrics(params: RiskMetricsRequest): Promise<RiskMetricsResponse> {
    try {
      const response = await fetch(`${WILLOWTREE_API_BASE}/api/risk/metrics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to calculate risk metrics');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async getHedgeRecommendation(params: HedgeRecommendRequest): Promise<HedgeRecommendResponse> {
    try {
      const response = await fetch(`${WILLOWTREE_API_BASE}/api/hedge/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get hedge recommendation');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async analyzeScenario(params: ScenarioAnalysisRequest): Promise<ScenarioAnalysisResponse> {
    try {
      const response = await fetch(`${WILLOWTREE_API_BASE}/api/scenario/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to analyze scenario');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async calculateImpliedVolatility(params: ImpliedVolatilityRequest): Promise<ImpliedVolatilityResponse> {
    try {
      const response = await fetch(`${WILLOWTREE_API_BASE}/api/iv/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to calculate implied volatility');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async buildStrategy(params: StrategyBuildRequest): Promise<StrategyBuildResponse> {
    try {
      const response = await fetch(`${WILLOWTREE_API_BASE}/api/strategy/build`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to build strategy');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async runBacktest(params: BacktestRequest): Promise<BacktestResponse> {
    try {
      const response = await fetch(`${WILLOWTREE_API_BASE}/api/backtest/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to run backtest');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async createAlert(params: AlertCreateRequest): Promise<AlertCreateResponse> {
    try {
      const response = await fetch(`${WILLOWTREE_API_BASE}/api/alerts/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create alert');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },
};

// Stock Transformer API (port 8080 on 192.162.1.101)
export const transformerApi = {
  async checkHealth(): Promise<TransformerHealthResponse> {
    try {
      const response = await fetch(`${TRANSFORMER_API_BASE}/`);
      if (!response.ok) throw new Error('Health check failed');
      return { status: 'healthy' };
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },

  async getPrediction(ticker: string): Promise<TransformerPredictionResponse> {
    try {
      const response = await fetch(`${TRANSFORMER_API_BASE}/predict/${ticker.toUpperCase()}`);
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get prediction');
      }
      return response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Unknown error');
    }
  },
};

// Legacy export for backward compatibility
export const api = tradingApi;
