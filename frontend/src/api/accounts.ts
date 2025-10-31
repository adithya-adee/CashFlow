import type { Account, AccountCreate, AccountEdit } from '../types/account';

const BASE_URL = import.meta.env.VITE_BASE_URL
const API_BASE = `${BASE_URL}/accounts`;

export async function listAccounts(skip = 0, limit = 20): Promise<Account[]> {
  const res = await fetch(`${API_BASE}/list?skip=${skip}&limit=${limit}`);
  return res.json();
}

export async function getAccount(id: number): Promise<Account> {
  const res = await fetch(`${API_BASE}/${id}`);
  return res.json();
}

export async function addAccount(data: AccountCreate): Promise<Account> {
  const res = await fetch(`${API_BASE}/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function editAccount(
  id: number,
  data: AccountEdit
): Promise<Account> {
  const res = await fetch(`${API_BASE}/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteAccount(id: number): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
  return res.json();
}
