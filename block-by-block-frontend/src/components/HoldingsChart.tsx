import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Loader2 } from 'lucide-react';
import type { TestResults } from '../types/trading';

interface HoldingsChartProps {
  data: TestResults | null;
  isLoading?: boolean;
}

export function HoldingsChart({ data, isLoading }: HoldingsChartProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h3 className="text-base font-semibold text-gray-900 mb-4">Top Holdings</h3>
        <div className="flex items-center justify-center h-[400px]">
          <div className="flex flex-col items-center space-y-2">
            <Loader2 className="w-8 h-8 text-teal-600 animate-spin" />
            <p className="text-sm text-gray-500">Loading chart...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!data?.results || !data.results.portfolio_positions.length) {
    return null;
  }

  const finalPositions = data.results.portfolio_positions[data.results.portfolio_positions.length - 1];
  const topHoldings = data.results.tickers
    .map((ticker, idx) => ({
      ticker,
      shares: finalPositions[idx],
    }))
    .sort((a, b) => b.shares - a.shares)
    .slice(0, 10);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <h3 className="text-base font-semibold text-gray-900 mb-4">Top Holdings</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={topHoldings}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="ticker"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickMargin={10}
          />
          <YAxis
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickMargin={10}
            label={{ value: 'Shares', angle: -90, position: 'insideLeft', fill: '#6b7280' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '8px 12px',
            }}
            formatter={(value: number) => [value, 'Shares']}
          />
          <Bar dataKey="shares" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
