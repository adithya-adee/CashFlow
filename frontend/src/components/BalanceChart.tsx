import type { DashboardStats } from '../types/dashboard';
import { Card } from '@/components/ui/card';
// If shadcn chart is not installed, run: bunx --bun shadcn@latest add chart
import { ChartContainer } from '@/components/ui/chart';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export function BalanceChart({ stats }: { stats: DashboardStats }) {
  // Example chart data
  const data = [
    { name: 'Income', value: stats.total_income },
    { name: 'Expense', value: stats.total_expense },
  ];

  return (
    <Card className="p-4">
      <div className="text-lg font-bold mb-2">Balance Chart</div>
      <ChartContainer config={{}}>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#3b82f6" name="Income" />
            <Bar dataKey="value" fill="#ef4444" name="Expense" />
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>
    </Card>
  );
}
