// Startup Finder API Types

export interface StartupSearchRequest {
  industry: string;
  num_queries?: number;
  max_results?: number;
}

export interface SearchResponse {
  industry: string;
  total_found: number;
  unique_startups: number;
  startups: StartupInfo[];
  search_timestamp: string;
}

export interface StartupInfo {
  name: string;
  website_url: string;
  linkedin_url: string | null;
  description: string;
  funding_info: string | null;
  confidence_score: number;
}

export interface StartupAnalysisRequest {
  industry: string;
  top_n?: number;
  num_queries?: number;
  max_results?: number;
}

export interface AnalysisResponse {
  industry: string;
  total_startups_found: number;
  startups_analyzed: number;
  analysis_timestamp: string;
  analyses: StartupAnalysis[];
  recommendations: Recommendation[] | null;
}

export interface StartupAnalysis {
  name: string;
  linkedin_url: string | null;
  website_url: string;
  analysis: string;
  stock_data: StockData | null;
}

export interface StockData {
  ticker: string;
  current_price: number | null;
  market_cap: number | null;
  pe_ratio: number | null;
  revenue: number | null;
  revenue_growth: number | null;
  price_change_1mo: number | null;
  analyst_rating: string | null;
  target_price: number | null;
}

export interface Recommendation {
  rank: number;
  name: string;
  linkedin_url: string | null;
  website: string;
  linkedin_metrics: {
    followers: number | null;
    employees: string | null;
    industry: string | null;
  };
  stock_metrics: {
    ticker: string | null;
    market_cap: number | null;
    current_price: number | null;
    analyst_rating: string | null;
  };
  summary: string;
}

export interface AsyncJobResponse {
  job_id: string;
  status: 'pending';
  message: string;
  check_status_url: string;
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: string | null;
  result: AnalysisResult | null;
  error: string | null;
}

export interface AnalysisResult {
  industry: string;
  total_startups_found: number;
  startups_analyzed: number;
  analysis_timestamp: string;
  report_file: string;
  analyses: Array<{
    name: string;
    linkedin_url: string | null;
    website_url: string;
    analysis: string;
    has_stock_data: boolean;
  }>;
  recommendations: Recommendation[];
}

export interface ReportsListResponse {
  reports: ReportMetadata[];
}

export interface ReportMetadata {
  filename: string;
  industry: string | null;
  startups_analyzed: number | null;
  timestamp: string | null;
  error?: string;
}

export interface IndustrySuggestionsResponse {
  suggestions: IndustrySuggestion[];
}

export interface IndustrySuggestion {
  name: string;
  description: string;
}

export interface HealthResponse {
  status: string;
  config_valid?: boolean;
  service?: string;
  version?: string;
  timestamp: string;
}
