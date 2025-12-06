import { Activity, TrendingUp, Cpu } from 'lucide-react';

interface StatusBarProps {
  serverStatus: string;
  isOnline: boolean;
  stockCount: number;
}

export function StatusBar({ serverStatus, isOnline, stockCount }: StatusBarProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-teal-600 rounded-lg">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Server Status</p>
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <p className="text-base font-semibold text-gray-900">{serverStatus}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-teal-600 rounded-lg">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Stocks Tracked</p>
            <p className="text-base font-semibold text-gray-900">{stockCount || '-'}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-teal-600 rounded-lg">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Model Type</p>
            <p className="text-base font-semibold text-gray-900">PPO</p>
          </div>
        </div>
      </div>
    </div>
  );
}
