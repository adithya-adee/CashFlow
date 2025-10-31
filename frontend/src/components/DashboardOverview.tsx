import type { DashboardStats } from '../types/dashboard';
import { Card } from '@/components/ui/card';
import { Banknote, TrendingUp, TrendingDown } from 'lucide-react';

export function DashboardOverview({ stats }: { stats: DashboardStats }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card className="flex items-center gap-4 p-4">
        <Banknote size={32} className="text-green-600" />
        <div>
          <div className="text-lg font-bold">Total Balance</div>
          <div className="text-2xl">
            ${stats.total_balance.toLocaleString()}
          </div>
        </div>
      </Card>
      <Card className="flex items-center gap-4 p-4">
        <TrendingUp size={32} className="text-blue-600" />
        <div>
          <div className="text-lg font-bold">Total Income</div>
          <div className="text-2xl">${stats.total_income.toLocaleString()}</div>
        </div>
      </Card>
      <Card className="flex items-center gap-4 p-4">
        <TrendingDown size={32} className="text-red-600" />
        <div>
          <div className="text-lg font-bold">Total Expense</div>
          <div className="text-2xl">
            ${stats.total_expense.toLocaleString()}
          </div>
        </div>
      </Card>
    </div>
  );
}
