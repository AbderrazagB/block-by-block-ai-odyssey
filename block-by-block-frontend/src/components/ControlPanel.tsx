import { useState } from 'react';
import { Play, Sparkles, RotateCcw, Settings } from 'lucide-react';

interface ControlPanelProps {
  onTest: (params: {
    startDate: string;
    endDate: string;
    initialAmount: number;
    hmax: number;
    transactionCost: number;
  }) => void;
  onPredict: (endDate: string) => void;
  isLoading: boolean;
}

export function ControlPanel({ onTest, onPredict, isLoading }: ControlPanelProps) {
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() - 2);
    return date.toISOString().split('T')[0];
  });
  const [initialAmount, setInitialAmount] = useState(100000);
  const [hmax, setHmax] = useState(100);
  const [transactionCost, setTransactionCost] = useState(0.1);

  const handleReset = () => {
    setStartDate('2024-01-01');
    const date = new Date();
    date.setDate(date.getDate() - 2);
    setEndDate(date.toISOString().split('T')[0]);
    setInitialAmount(100000);
    setHmax(100);
    setTransactionCost(0.1);
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-8">
      <div className="flex items-center space-x-2 mb-6">
        <Settings className="w-5 h-5 text-teal-600" />
        <h3 className="text-lg font-semibold text-gray-900">Trading Configuration</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-5 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Start Date
          </label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            End Date
          </label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Initial Portfolio ($)
          </label>
          <input
            type="number"
            value={initialAmount}
            onChange={(e) => setInitialAmount(Number(e.target.value))}
            min="1000"
            step="1000"
            className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Max Shares per Trade
          </label>
          <input
            type="number"
            value={hmax}
            onChange={(e) => setHmax(Number(e.target.value))}
            min="1"
            step="10"
            title="Maximum number of shares to buy/sell in a single trade"
            className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transaction Cost (%)
          </label>
          <input
            type="number"
            value={transactionCost}
            onChange={(e) => setTransactionCost(Number(e.target.value))}
            min="0"
            max="5"
            step="0.05"
            title="Percentage cost per transaction"
            className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-colors"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          onClick={() =>
            onTest({
              startDate,
              endDate,
              initialAmount,
              hmax,
              transactionCost: transactionCost / 100,
            })
          }
          disabled={isLoading}
          className="flex items-center space-x-2 px-5 py-2.5 text-sm font-medium bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow"
        >
          <Play className="w-4 h-4" />
          <span>Test Model</span>
        </button>

        <button
          onClick={() => onPredict(endDate)}
          disabled={isLoading}
          className="flex items-center space-x-2 px-5 py-2.5 text-sm font-medium bg-slate-600 text-white rounded-lg hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow"
        >
          <Sparkles className="w-4 h-4" />
          <span>Get Predictions</span>
        </button>

        <button
          onClick={handleReset}
          className="flex items-center space-x-2 px-5 py-2.5 text-sm font-medium bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all shadow-sm hover:shadow"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset</span>
        </button>
      </div>
    </div>
  );
}
