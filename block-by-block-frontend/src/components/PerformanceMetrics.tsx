import { DollarSign, TrendingUp, Activity, Target, AlertTriangle, Award, Calendar, BarChart3, Loader2 } from 'lucide-react';
import type { TestResults } from '../types/trading';

interface PerformanceMetricsProps {
  data: TestResults | null;
  isLoading?: boolean;
  error?: string | null;
}

export function PerformanceMetrics({ data, isLoading, error }: PerformanceMetricsProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-12">
        <div className="flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-10 h-10 text-teal-600 animate-spin" />
          <p className="text-sm text-gray-600">Testing model... This may take a minute</p>
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

  if (!data?.results) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-12">
        <div className="text-center text-gray-500">
          <Activity className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-sm">Click "Test Model" to see portfolio performance</p>
        </div>
      </div>
    );
  }

  const metrics = [
    {
      label: 'Initial Value',
      value: `$${data.results.initial_value.toLocaleString()}`,
      icon: DollarSign,
    },
    {
      label: 'Final Value',
      value: `$${data.results.final_value.toLocaleString()}`,
      icon: Target,
    },
    {
      label: 'Total Return',
      value: `${data.results.total_return.toFixed(2)}%`,
      icon: TrendingUp,
    },
    {
      label: 'Sharpe Ratio',
      value: data.results.sharpe_ratio.toFixed(2),
      icon: Award,
    },
    {
      label: 'Max Drawdown',
      value: `${data.results.max_drawdown.toFixed(2)}%`,
      icon: AlertTriangle,
    },
    {
      label: 'Win Rate',
      value: `${data.results.win_rate.toFixed(1)}%`,
      icon: Activity,
    },
    {
      label: 'Trading Days',
      value: data.results.dates.length.toString(),
      icon: Calendar,
    },
    {
      label: 'Total Trades',
      value: (data.results.total_trades || 0).toString(),
      icon: BarChart3,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <div
            key={metric.label}
            className="bg-white rounded-xl border border-gray-200 shadow-sm p-5"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="p-2 bg-teal-600 rounded-lg">
                <Icon className="w-4 h-4 text-white" />
              </div>
            </div>
            <p className="text-xs text-gray-500 mb-1">{metric.label}</p>
            <p className="text-xl font-bold text-gray-900">{metric.value}</p>
          </div>
        );
      })}
    </div>
  );
}
