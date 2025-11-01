import type { DashboardStats, SuperDashboardQuery } from '../types/dashboard';

const BASE_URL = import.meta.env.VITE_BASE_URL;
const API_BASE = `${BASE_URL}/dashboard`;

export async function getDashboardStats(
  query: SuperDashboardQuery
): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/super`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(query),
  });
  return res.json();
}
