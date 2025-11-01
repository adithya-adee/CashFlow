import React, { useEffect, useState } from 'react';
import {
  listAccounts,
  addAccount,
  editAccount,
  deleteAccount,
} from '../api/accounts';
import type { Account, AccountCreate, AccountEdit } from '../types/account';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
import { toast } from 'sonner';
import { Loader2, Pencil, Trash2, Plus, Filter } from 'lucide-react';
import { CURRENCY_SYMBOLS, mapCurrencyToSymbol } from '@/utils/map-functions';

const PAGE_SIZE = 10;

export function Accounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);

  // Filter states
  const [filters, setFilters] = useState({
    bank_name: '',
    account_type: '',
    currency: '',
    holder_name: '',
  });

  const [form, setForm] = useState<AccountCreate>({
    bank_account_no: '',
    bank_name: '',
    account_type: 'savings',
    holder_name: '',
    currency: 'INR',
    balance: 0,
  });

  const [editId, setEditId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<AccountEdit>({});

  const fetchAccounts = React.useCallback(async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * PAGE_SIZE;
      const response = await listAccounts(skip, PAGE_SIZE);
      console.log(response);
      // Apply client-side filtering
      let filteredData = response.data;
      if (filters.bank_name) {
        filteredData = filteredData.filter((acc: Account) =>
          acc.bank_name.toLowerCase().includes(filters.bank_name.toLowerCase())
        );
      }
      if (filters.account_type) {
        filteredData = filteredData.filter(
          (acc: Account) => acc.account_type === filters.account_type
        );
      }
      if (filters.currency) {
        filteredData = filteredData.filter(
          (acc: Account) => acc.currency === filters.currency
        );
      }
      if (filters.holder_name) {
        filteredData = filteredData.filter((acc: Account) =>
          acc.holder_name
            .toLowerCase()
            .includes(filters.holder_name.toLowerCase())
        );
      }
      setAccounts(filteredData);
      setTotal(response.total_count);
    } catch {
      toast.error('Failed to fetch accounts');
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  useEffect(() => {
    fetchAccounts();
  }, [page, fetchAccounts]);

  useEffect(() => {
    // Reset to page 1 when filters change
    if (page === 1) {
      fetchAccounts();
    } else {
      setPage(1);
    }
  }, [filters, fetchAccounts, page]);

  const handleAdd = async () => {
    try {
      await addAccount(form);
      toast.success('Account created');
      setForm({
        bank_account_no: '',
        bank_name: '',
        account_type: 'savings',
        holder_name: '',
        currency: 'INR',
        balance: 0,
      });
      setIsCreateOpen(false);
      setPage(1);
      fetchAccounts();
    } catch {
      toast.error('Failed to create account');
    }
  };

  const handleEdit = async () => {
    if (editId === null) return;
    try {
      await editAccount(editId, editForm);
      toast.success('Account updated');
      setEditId(null);
      setEditForm({});
      fetchAccounts();
    } catch {
      toast.error('Failed to update account');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteAccount(id);
      toast.success('Account deleted');
      fetchAccounts();
    } catch {
      toast.error('Failed to delete account');
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      bank_name: '',
      account_type: '',
      currency: '',
      holder_name: '',
    });
  };

  if (loading)
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="animate-spin" size={32} />
      </div>
    );

  return (
    <div className="space-y-6">
      {/* Filters and Create Button */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={20} className="text-gray-500" />
          <input
            type="text"
            placeholder="Bank Name"
            value={filters.bank_name}
            onChange={(e) => handleFilterChange('bank_name', e.target.value)}
            className="border rounded px-3 py-2 flex-1"
          />
          <select
            value={filters.account_type}
            onChange={(e) => handleFilterChange('account_type', e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="">All Types</option>
            <option value="savings">Savings</option>
            <option value="current_account">Current</option>
            <option value="fd_account">FD</option>
            <option value="rd_account">RD</option>
            <option value="demat_account">Demat</option>
          </select>
          <select
            value={filters.currency}
            onChange={(e) => handleFilterChange('currency', e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="">All Currencies</option>
            {Object.keys(CURRENCY_SYMBOLS).map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Holder Name"
            value={filters.holder_name}
            onChange={(e) => handleFilterChange('holder_name', e.target.value)}
            className="border rounded px-3 py-2 flex-1"
          />
          <Button onClick={clearFilters} variant="outline">
            Clear
          </Button>
          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button variant="default">
                <Plus size={18} className="mr-2" /> Create Account
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Account</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Account Number
                  </label>
                  <input
                    type="text"
                    placeholder="Account No."
                    value={form.bank_account_no}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        bank_account_no: e.target.value,
                      }))
                    }
                    className="border rounded px-3 py-2 w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Bank Name
                  </label>
                  <input
                    type="text"
                    placeholder="Bank Name"
                    value={form.bank_name}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, bank_name: e.target.value }))
                    }
                    className="border rounded px-3 py-2 w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Account Type
                  </label>
                  <select
                    value={form.account_type}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        account_type: e.target.value as Account['account_type'],
                      }))
                    }
                    className="border rounded px-3 py-2 w-full"
                  >
                    <option value="savings">Savings</option>
                    <option value="current_account">Current</option>
                    <option value="fd_account">FD</option>
                    <option value="rd_account">RD</option>
                    <option value="demat_account">Demat</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Holder Name
                  </label>
                  <input
                    type="text"
                    placeholder="Holder Name"
                    value={form.holder_name}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, holder_name: e.target.value }))
                    }
                    className="border rounded px-3 py-2 w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Currency
                  </label>
                  <select
                    value={form.currency}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        currency: e.target.value as Account['currency'],
                      }))
                    }
                    className="border rounded px-3 py-2 w-full"
                  >
                    {Object.keys(CURRENCY_SYMBOLS).map((code) => (
                      <option key={code} value={code}>
                        {code}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Initial Balance
                  </label>
                  <input
                    type="number"
                    placeholder="Balance"
                    value={form.balance}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        balance: Number(e.target.value),
                      }))
                    }
                    className="border rounded px-3 py-2 w-full"
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button
                    onClick={() => setIsCreateOpen(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                  <Button onClick={handleAdd} variant="default">
                    Create
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </Card>

      {/* Accounts Table */}
      <Card className="p-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Account ID</TableHead>
              <TableHead>Account No.</TableHead>
              <TableHead>Bank Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Holder Name</TableHead>
              <TableHead>Currency</TableHead>
              <TableHead>Balance</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {accounts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-gray-500">
                  No accounts found
                </TableCell>
              </TableRow>
            ) : (
              accounts.map((acc) => (
                <TableRow key={acc.id}>
                  <TableCell>{acc.id}</TableCell>
                  <TableCell>{acc.bank_account_no}</TableCell>
                  <TableCell>{acc.bank_name}</TableCell>
                  <TableCell>{acc.account_type}</TableCell>
                  <TableCell>{acc.holder_name}</TableCell>
                  <TableCell>{acc.currency}</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center gap-1">
                      {mapCurrencyToSymbol(acc.currency)}{' '}
                      {acc.balance.toLocaleString()}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setEditId(acc.id);
                          setEditForm(acc);
                        }}
                      >
                        <Pencil size={16} />
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDelete(acc.id)}
                      >
                        <Trash2 size={16} />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        {/* Pagination */}
        {total > PAGE_SIZE && (
          <div className="mt-4">
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      if (page > 1) setPage(page - 1);
                    }}
                    className={
                      page <= 1 ? 'pointer-events-none opacity-50' : ''
                    }
                  />
                </PaginationItem>
                {Array.from({ length: Math.ceil(total / PAGE_SIZE) }).map(
                  (_, i) => {
                    const pageNum = i + 1;
                    if (
                      pageNum === 1 ||
                      pageNum === Math.ceil(total / PAGE_SIZE) ||
                      (pageNum >= page - 2 && pageNum <= page + 2)
                    ) {
                      return (
                        <PaginationItem key={pageNum}>
                          <PaginationLink
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              setPage(pageNum);
                            }}
                            isActive={page === pageNum}
                          >
                            {pageNum}
                          </PaginationLink>
                        </PaginationItem>
                      );
                    }
                    return null;
                  }
                )}
                <PaginationItem>
                  <PaginationNext
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      if (page < Math.ceil(total / PAGE_SIZE))
                        setPage(page + 1);
                    }}
                    className={
                      page >= Math.ceil(total / PAGE_SIZE)
                        ? 'pointer-events-none opacity-50'
                        : ''
                    }
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        )}
      </Card>

      {/* Edit Modal */}
      {editId !== null && (
        <Dialog open={editId !== null} onOpenChange={() => setEditId(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Account</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Account Number
                </label>
                <input
                  type="text"
                  placeholder="Account No."
                  value={editForm.bank_account_no ?? ''}
                  onChange={(e) =>
                    setEditForm((f) => ({
                      ...f,
                      bank_account_no: e.target.value,
                    }))
                  }
                  className="border rounded px-3 py-2 w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Bank Name
                </label>
                <input
                  type="text"
                  placeholder="Bank Name"
                  value={editForm.bank_name ?? ''}
                  onChange={(e) =>
                    setEditForm((f) => ({ ...f, bank_name: e.target.value }))
                  }
                  className="border rounded px-3 py-2 w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Account Type
                </label>
                <select
                  value={editForm.account_type ?? 'savings'}
                  onChange={(e) =>
                    setEditForm((f) => ({
                      ...f,
                      account_type: e.target.value as Account['account_type'],
                    }))
                  }
                  className="border rounded px-3 py-2 w-full"
                >
                  <option value="savings">Savings</option>
                  <option value="current_account">Current</option>
                  <option value="fd_account">FD</option>
                  <option value="rd_account">RD</option>
                  <option value="demat_account">Demat</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Holder Name
                </label>
                <input
                  type="text"
                  placeholder="Holder Name"
                  value={editForm.holder_name ?? ''}
                  onChange={(e) =>
                    setEditForm((f) => ({ ...f, holder_name: e.target.value }))
                  }
                  className="border rounded px-3 py-2 w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Currency
                </label>
                <select
                  value={editForm.currency ?? 'INR'}
                  onChange={(e) =>
                    setEditForm((f) => ({
                      ...f,
                      currency: e.target.value as Account['currency'],
                    }))
                  }
                  className="border rounded px-3 py-2 w-full"
                >
                  {Object.keys(CURRENCY_SYMBOLS).map((code) => (
                    <option key={code} value={code}>
                      {code}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Balance
                </label>
                <input
                  type="number"
                  placeholder="Balance"
                  value={editForm.balance ?? 0}
                  onChange={(e) =>
                    setEditForm((f) => ({
                      ...f,
                      balance: Number(e.target.value),
                    }))
                  }
                  className="border rounded px-3 py-2 w-full"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button onClick={() => setEditId(null)} variant="outline">
                  Cancel
                </Button>
                <Button onClick={handleEdit} variant="default">
                  Save Changes
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
