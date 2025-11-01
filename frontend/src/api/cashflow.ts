import type {
  CashFlow,
  CashFlowCreate,
  CashFlowEdit,
  CashFlowList,
} from '../types/cash_flow';

const BASE_URL = import.meta.env.VITE_BASE_URL;
const API_BASE = `${BASE_URL}/cashflow`;

export async function listCashFlow(
  filters: Record<string, string | null> = {},
  skip = 0,
  limit = 20
): Promise<CashFlowList> {
  const params = new URLSearchParams({
    ...filters,
    skip: String(skip),
    limit: String(limit),
  });
  const res = await fetch(`${API_BASE}/list?${params}`);
  return res.json();
}

export async function getCashFlow(id: number): Promise<CashFlow> {
  const res = await fetch(`${API_BASE}/${id}`);
  return res.json();
}

export async function addCashFlow(data: CashFlowCreate): Promise<CashFlow> {
  const res = await fetch(`${API_BASE}/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function editCashFlow(
  id: number,
  data: CashFlowEdit
): Promise<CashFlow> {
  const res = await fetch(`${API_BASE}/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteCashFlow(id: number): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
  return res.json();
}
