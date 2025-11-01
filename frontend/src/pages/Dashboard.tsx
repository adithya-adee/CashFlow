import { useEffect, useState } from 'react';
import { getDashboardStats } from '../api/dashboard';
import type { DashboardStats, SuperDashboardQuery } from '../types/dashboard';
import { DashboardOverview } from '../components/DashboardOverview';
import { BalanceChart } from '../components/BalanceChart';
import { RecentTransactions } from '../components/RecentTransactions';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const query: SuperDashboardQuery = {};
        const data = await getDashboardStats(query);
        console.log(data);
        setStats(data);
        toast.success('Dashboard loaded');
      } catch (e) {
        console.error(e);
        toast.error('Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading)
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="animate-spin" size={32} />
      </div>
    );
  if (!stats) return <div>No data available</div>;

  return (
    <div className="space-y-6">
      <DashboardOverview stats={stats} />
      <BalanceChart stats={stats} />
      <RecentTransactions transactions={stats.recent_transactions} />
    </div>
  );
}
