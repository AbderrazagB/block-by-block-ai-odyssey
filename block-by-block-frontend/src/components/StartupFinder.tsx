import { useState } from 'react';
import { Search, TrendingUp, Briefcase, DollarSign, Building2, ExternalLink, Sparkles, Clock, CheckCircle, XCircle } from 'lucide-react';
import type { SearchResponse, AnalysisResponse, JobStatus, IndustrySuggestion } from '../types/startup';
import ReactMarkdown from 'react-markdown';

interface StartupFinderProps {
  onSearch: (params: { industry: string; num_queries?: number; max_results?: number }) => void;
  onAnalyze: (params: { industry: string; top_n?: number; num_queries?: number; max_results?: number }) => void;
  onAsyncAnalyze: (params: { industry: string; top_n?: number }) => void;
  searchData: SearchResponse | null;
  analysisData: AnalysisResponse | null;
  jobStatus: JobStatus | null;
  isLoadingSearch: boolean;
  isLoadingAnalysis: boolean;
  searchError: string | null;
  analysisError: string | null;
  suggestions: IndustrySuggestion[];
}

export function StartupFinder({
  onSearch,
  onAnalyze,
  onAsyncAnalyze,
  searchData,
  analysisData,
  jobStatus,
  isLoadingSearch,
  isLoadingAnalysis,
  searchError,
  analysisError,
  suggestions,
}: StartupFinderProps) {
  const [industry, setIndustry] = useState('');
  const [searchNumQueries, setSearchNumQueries] = useState(3);
  const [searchMaxResults, setSearchMaxResults] = useState(10);
  const [analysisTopN, setAnalysisTopN] = useState(5);
  const [analysisNumQueries, setAnalysisNumQueries] = useState(3);
  const [analysisMaxResults, setAnalysisMaxResults] = useState(15);
  const [useAsync, setUseAsync] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      industry,
      num_queries: searchNumQueries,
      max_results: searchMaxResults,
    });
  };

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    if (useAsync || analysisTopN > 5) {
      onAsyncAnalyze({
        industry,
        top_n: analysisTopN,
      });
    } else {
      onAnalyze({
        industry,
        top_n: analysisTopN,
        num_queries: analysisNumQueries,
        max_results: analysisMaxResults,
      });
    }
  };

  const getJobStatusIcon = () => {
    if (!jobStatus) return null;
    switch (jobStatus.status) {
      case 'pending':
      case 'running':
        return <Clock className="w-5 h-5 text-teal-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
    }
  };

  const getJobStatusColor = () => {
    if (!jobStatus) return '';
    switch (jobStatus.status) {
      case 'pending':
      case 'running':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'completed':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'failed':
        return 'bg-red-50 border-red-200 text-red-800';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Left Column - Search Tool */}
      <div className="space-y-6 border-r border-gray-200 pr-8">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
            <Search className="w-6 h-6 text-teal-600" />
            <span>Quick Search</span>
          </h2>

          <form onSubmit={handleSearch} className="space-y-5">
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Industry
              </label>
              <input
                type="text"
                value={industry}
                onChange={(e) => {
                  setIndustry(e.target.value);
                  setShowSuggestions(true);
                }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all"
                placeholder="e.g., fintech, healthtech, AI"
                required
              />
              
              {showSuggestions && industry.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
                  {suggestions
                    .filter(s => s.name.toLowerCase().includes(industry.toLowerCase()) || s.description.toLowerCase().includes(industry.toLowerCase()))
                    .slice(0, 5)
                    .map((suggestion, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => {
                          setIndustry(suggestion.name);
                          setShowSuggestions(false);
                        }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                      >
                        <div className="font-medium text-gray-900">{suggestion.name}</div>
                        <div className="text-sm text-gray-600">{suggestion.description}</div>
                      </button>
                    ))}
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Queries</label>
                <input
                  type="number"
                  value={searchNumQueries}
                  onChange={(e) => setSearchNumQueries(Number(e.target.value))}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all"
                  min="1"
                  max="10"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Max Results</label>
                <input
                  type="number"
                  value={searchMaxResults}
                  onChange={(e) => setSearchMaxResults(Number(e.target.value))}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all"
                  min="1"
                  max="50"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoadingSearch}
              className="w-full bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 transition-all disabled:bg-gray-400 disabled:cursor-not-allowed font-medium shadow-sm hover:shadow"
            >
              {isLoadingSearch ? 'Searching...' : 'Search Startups'}
            </button>
          </form>
        </div>

        {/* Search Error */}
        {searchError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-red-800 text-sm">{searchError}</p>
          </div>
        )}

        {/* Search Results */}
        {searchData && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              Search Results: {searchData.industry}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Found {searchData.total_found} startups, {searchData.unique_startups} unique
            </p>
            <div className="space-y-3">
              {searchData.startups.map((startup, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="font-bold text-sm text-gray-900 flex items-center space-x-2">
                        <Building2 className="w-3 h-3 text-teal-600" />
                        <span>{startup.name}</span>
                      </h4>
                      <p className="text-xs text-gray-700 mt-1">{startup.description}</p>
                    </div>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      {(startup.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  {startup.funding_info && (
                    <p className="text-xs text-gray-600 flex items-center space-x-1 mb-2">
                      <DollarSign className="w-3 h-3" />
                      <span>{startup.funding_info}</span>
                    </p>
                  )}
                  <div className="flex space-x-3 text-xs">
                    <a
                      href={startup.website_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-teal-600 hover:underline flex items-center space-x-1"
                    >
                      <ExternalLink className="w-3 h-3" />
                      <span>{startup.website_url}</span>
                    </a>
                    {startup.linkedin_url && (
                      <a
                        href={startup.linkedin_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-teal-600 hover:underline flex items-center space-x-1"
                      >
                        <ExternalLink className="w-3 h-3" />
                        <span>LinkedIn</span>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Right Column - AI Analysis Tool */}
      <div className="space-y-6 pl-8">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-slate-600" />
            <span>AI Investment Analysis</span>
          </h2>

          <form onSubmit={handleAnalyze} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Top N</label>
                <input
                  type="number"
                  value={analysisTopN}
                  onChange={(e) => setAnalysisTopN(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  min="1"
                  max="20"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Queries</label>
                <input
                  type="number"
                  value={analysisNumQueries}
                  onChange={(e) => setAnalysisNumQueries(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  min="1"
                  max="10"
                />
              </div>
            </div>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useAsync || analysisTopN > 5}
                onChange={(e) => setUseAsync(e.target.checked)}
                disabled={analysisTopN > 5}
                className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
              />
              <span className="text-sm text-gray-700">
                Async {analysisTopN > 5 && <span className="text-teal-600">(Required)</span>}
              </span>
            </label>

            <button
              type="submit"
              disabled={isLoadingAnalysis}
              className="w-full bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 transition-all shadow-sm hover:shadow disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {isLoadingAnalysis ? 'Analyzing...' : 'Analyze Industry'}
            </button>
          </form>
        </div>

        {/* Job Status */}
        {jobStatus && (
          <div className={`border rounded-lg p-4 shadow-sm ${getJobStatusColor()}`}>
            <div className="flex items-center space-x-3">
              {getJobStatusIcon()}
              <div className="flex-1">
                <p className="font-bold text-sm">Job: {jobStatus.job_id}</p>
                <p className="text-xs">Status: {jobStatus.status}</p>
                {jobStatus.progress && <p className="text-xs">{jobStatus.progress}</p>}
                {jobStatus.error && <p className="text-xs text-red-700">Error: {jobStatus.error}</p>}
              </div>
            </div>
          </div>
        )}

        {/* Analysis Error */}
        {analysisError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-red-800 text-sm">{analysisError}</p>
          </div>
        )}
        {/* Analysis Results */}
        {analysisData && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                Analysis: {analysisData.industry}
              </h3>
              <p className="text-sm text-gray-600">
                Found {analysisData.total_startups_found} startups, analyzed {analysisData.startups_analyzed}
              </p>
            </div>

            {/* Recommendations */}
            {analysisData.recommendations && analysisData.recommendations.length > 0 && (
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  <span>Top Recommendations</span>
                </h3>
                <div className="space-y-3">
                  {analysisData.recommendations.map((rec, idx) => (
                    <div key={idx} className="border-l-4 border-green-500 bg-gray-50 p-3 rounded">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <span className="inline-block px-2 py-1 bg-green-600 text-white text-xs rounded mr-2">
                            #{rec.rank}
                          </span>
                          <span className="font-bold text-sm text-gray-900">{rec.name}</span>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                        <div>
                          <p className="text-gray-600">Followers: {rec.linkedin_metrics.followers?.toLocaleString() ?? 'N/A'}</p>
                          <p className="text-gray-600">Employees: {rec.linkedin_metrics.employees ?? 'N/A'}</p>
                        </div>
                        <div>
                          {rec.stock_metrics.ticker && (
                            <>
                              <p className="text-gray-600">Ticker: ${rec.stock_metrics.ticker}</p>
                              <p className="text-gray-600">Cap: ${(rec.stock_metrics.market_cap ?? 0 / 1e9).toFixed(2)}B</p>
                            </>
                          )}
                        </div>
                      </div>
                      <p className="text-xs text-gray-700 line-clamp-3">{rec.summary}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed Analyses */}
            {analysisData.analyses.map((startup, idx) => (
              <div key={idx} className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 flex items-center space-x-2">
                      <Briefcase className="w-4 h-4 text-teal-600" />
                      <span>{startup.name}</span>
                    </h3>
                    <div className="flex space-x-3 text-xs mt-1">
                      <a
                        href={startup.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-teal-600 hover:underline flex items-center space-x-1"
                      >
                        <ExternalLink className="w-3 h-3" />
                        <span>{startup.website_url}</span>
                      </a>
                      {startup.linkedin_url && (
                        <a
                          href={startup.linkedin_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-teal-600 hover:underline flex items-center space-x-1"
                        >
                          <ExternalLink className="w-3 h-3" />
                          <span>LinkedIn</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>

                {/* Stock Data */}
                {startup.stock_data && (
                  <div className="grid grid-cols-4 gap-2 mb-3 p-3 bg-gray-50 rounded">
                    <div>
                      <p className="text-xs text-gray-600">Ticker</p>
                      <p className="font-bold text-sm text-gray-900">{startup.stock_data.ticker}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Price</p>
                      <p className="font-bold text-sm text-gray-900">${startup.stock_data.current_price?.toFixed(2) ?? 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Market Cap</p>
                      <p className="font-bold text-sm text-gray-900">
                        ${startup.stock_data.market_cap ? (startup.stock_data.market_cap / 1e9).toFixed(2) + 'B' : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Rating</p>
                      <p className="font-bold text-sm text-gray-900">{startup.stock_data.analyst_rating?.toUpperCase() ?? 'N/A'}</p>
                    </div>
                  </div>
                )}

                {/* AI Analysis */}
                <div className="prose prose-sm max-w-none text-sm">
                  <ReactMarkdown>{startup.analysis}</ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
