import { useEffect, useState } from 'react';
import {
  listCashFlow,
  addCashFlow,
  editCashFlow,
  deleteCashFlow,
} from '@/api/cashflow';
import type { CashFlow, CashFlowCreate, CashFlowEdit } from '@/types/cash_flow';
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

const PAGE_SIZE = 10;

export function CashFlowPage() {
  const [transactions, setTransactions] = useState<CashFlow[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);

  // Filter states
  const [filters, setFilters] = useState({
    account_id: '',
    txn_type: '',
    category: '',
  });

  const [form, setForm] = useState<CashFlowCreate>({
    account_id: 0,
    txn_type: 'credit',
    amount: 0,
    category: '',
    description: '',
  });

  const [editId, setEditId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<CashFlowEdit>({});

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * PAGE_SIZE;
      const response = await listCashFlow({}, skip, PAGE_SIZE);
      console.log(response);

      // Apply client-side filtering
      let filteredData = response.data;

      if (filters.account_id) {
        filteredData = filteredData.filter(
          (tx: CashFlow) => tx.account_id.toString() === filters.account_id
        );
      }

      if (filters.txn_type) {
        filteredData = filteredData.filter(
          (tx: CashFlow) => tx.txn_type === filters.txn_type
        );
      }

      if (filters.category) {
        filteredData = filteredData.filter((tx: CashFlow) =>
          tx.category?.toLowerCase().includes(filters.category.toLowerCase())
        );
      }

      setTransactions(filteredData);
      setTotal(response.total_count);
    } catch {
      toast.error('Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [page]);

  useEffect(() => {
    // Reset to page 1 when filters change
    if (page === 1) {
      fetchTransactions();
    } else {
      setPage(1);
    }
  }, [filters]);

  const handleAdd = async () => {
    try {
      await addCashFlow(form);
      toast.success('Transaction created');
      setForm({
        account_id: 0,
        txn_type: 'credit',
        amount: 0,
        category: '',
        description: '',
      });
      setIsCreateOpen(false);
      setPage(1);
      fetchTransactions();
    } catch {
      toast.error('Failed to create transaction');
    }
  };

  const handleEdit = async () => {
    if (editId === null) return;
    try {
      await editCashFlow(editId, editForm);
      toast.success('Transaction updated');
      setEditId(null);
      setEditForm({});
      fetchTransactions();
    } catch {
      toast.error('Failed to update transaction');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteCashFlow(id);
      toast.success('Transaction deleted');
      fetchTransactions();
    } catch {
      toast.error('Failed to delete transaction');
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      account_id: '',
      txn_type: '',
      category: '',
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
            placeholder="Account ID"
            value={filters.account_id}
            onChange={(e) => handleFilterChange('account_id', e.target.value)}
            className="border rounded px-3 py-2 w-32"
          />
          <select
            value={filters.txn_type}
            onChange={(e) => handleFilterChange('txn_type', e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="">All Types</option>
            <option value="credit">Credit</option>
            <option value="debit">Debit</option>
          </select>
          <input
            type="text"
            placeholder="Category"
            value={filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
            className="border rounded px-3 py-2 flex-1"
          />
          <Button onClick={clearFilters} variant="outline">
            Clear
          </Button>
          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button variant="default">
                <Plus size={18} className="mr-2" /> Create Transaction
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Transaction</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Account ID
                  </label>
                  <input
                    type="number"
                    placeholder="Account ID"
                    value={form.account_id}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        account_id: Number(e.target.value),
                      }))
                    }
                    className="border rounded px-3 py-2 w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Transaction Type
                  </label>
                  <select
                    value={form.txn_type}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        txn_type: e.target.value as 'credit' | 'debit',
                      }))
                    }
                    className="border rounded px-3 py-2 w-full"
                  >
                    <option value="credit">Credit</option>
                    <option value="debit">Debit</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Amount
                  </label>
                  <input
                    type="number"
                    placeholder="Amount"
                    value={form.amount}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, amount: Number(e.target.value) }))
                    }
                    className="border rounded px-3 py-2 w-full"
                    step="0.01"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Category
                  </label>
                  <input
                    type="text"
                    placeholder="Category"
                    value={form.category}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, category: e.target.value }))
                    }
                    className="border rounded px-3 py-2 w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Description
                  </label>
                  <textarea
                    placeholder="Description"
                    value={form.description}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, description: e.target.value }))
                    }
                    className="border rounded px-3 py-2 w-full resize-none"
                    rows={3}
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

      {/* Transactions Table */}
      <Card className="p-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Account ID</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {transactions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-gray-500">
                  No transactions found
                </TableCell>
              </TableRow>
            ) : (
              transactions.map((tx) => (
                <TableRow key={tx.id}>
                  <TableCell>{tx.account_id}</TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                        tx.txn_type === 'credit'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {tx.txn_type}
                    </span>
                  </TableCell>
                  <TableCell>
                    <span
                      className={
                        tx.txn_type === 'credit'
                          ? 'text-green-600 font-medium'
                          : 'text-red-600 font-medium'
                      }
                    >
                      {tx.txn_type === 'credit' ? '+' : '-'}
                      {tx.amount.toLocaleString()}
                    </span>
                  </TableCell>
                  <TableCell>{tx.category}</TableCell>
                  <TableCell className="max-w-xs truncate">
                    {tx.description}
                  </TableCell>
                  <TableCell>
                    {new Date(tx.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setEditId(tx.id);
                          setEditForm(tx);
                        }}
                      >
                        <Pencil size={16} />
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDelete(tx.id)}
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
              <DialogTitle>Edit Transaction</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Account ID
                </label>
                <input
                  type="number"
                  placeholder="Account ID"
                  value={editForm.account_id ?? 0}
                  onChange={(e) =>
                    setEditForm((f) => ({
                      ...f,
                      account_id: Number(e.target.value),
                    }))
                  }
                  className="border rounded px-3 py-2 w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Transaction Type
                </label>
                <select
                  value={editForm.txn_type ?? 'credit'}
                  onChange={(e) =>
                    setEditForm((f) => ({
                      ...f,
                      txn_type: e.target.value as 'credit' | 'debit',
                    }))
                  }
                  className="border rounded px-3 py-2 w-full"
                >
                  <option value="credit">Credit</option>
                  <option value="debit">Debit</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Amount</label>
                <input
                  type="number"
                  placeholder="Amount"
                  value={editForm.amount ?? 0}
                  onChange={(e) =>
                    setEditForm((f) => ({
                      ...f,
                      amount: Number(e.target.value),
                    }))
                  }
                  className="border rounded px-3 py-2 w-full"
                  step="0.01"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Category
                </label>
                <input
                  type="text"
                  placeholder="Category"
                  value={editForm.category ?? ''}
                  onChange={(e) =>
                    setEditForm((f) => ({ ...f, category: e.target.value }))
                  }
                  className="border rounded px-3 py-2 w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Description
                </label>
                <textarea
                  placeholder="Description"
                  value={editForm.description ?? ''}
                  onChange={(e) =>
                    setEditForm((f) => ({ ...f, description: e.target.value }))
                  }
                  className="border rounded px-3 py-2 w-full resize-none"
                  rows={3}
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
