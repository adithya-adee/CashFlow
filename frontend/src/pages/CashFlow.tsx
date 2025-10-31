import { useEffect, useState } from 'react';
import {
  listCashFlow,
  editCashFlow,
  deleteCashFlow,
} from '@/api/cashflow';
import type { CashFlow, CashFlowEdit } from '@/types/cash_flow';
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
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
import { toast } from 'sonner';
import { Loader2, Pencil, Trash2 } from 'lucide-react';

const PAGE_SIZE = 10;

export function CashFlowPage() {
  const [transactions, setTransactions] = useState<CashFlow[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const [editId, setEditId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<CashFlowEdit>({});
  const [page, setPage] = useState<number>(1);
  const [total, setTotal] = useState<number>(0);

  const fetchTransactions = async (pageNum: number = 1) => {
    setLoading(true);
    try {
      const skip = (pageNum - 1) * PAGE_SIZE;
      const data = await listCashFlow({}, skip, PAGE_SIZE);
      setTransactions(data);
      
      // If we got less than PAGE_SIZE items, we're on the last page
      if (data.length < PAGE_SIZE) {
        setTotal(skip + data.length);
      } else {
        // Estimate total by checking if there's more data
        const nextPageData = await listCashFlow({}, skip + PAGE_SIZE, 1);
        if (nextPageData.length === 0) {
          setTotal(skip + data.length);
        } else {
          // Conservative estimate: current page + at least one more page
          setTotal(skip + PAGE_SIZE + 1);
        }
      }
    } catch {
      toast.error('Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions(page);
  }, [page]);



  const handleEdit = async () => {
    if (editId === null) return;
    try {
      await editCashFlow(editId, editForm);
      toast.success('Transaction updated');
      setEditId(null);
      setEditForm({});
      fetchTransactions(page);
    } catch {
      toast.error('Failed to update transaction');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteCashFlow(id);
      toast.success('Transaction deleted');
      fetchTransactions(page);
    } catch {
      toast.error('Failed to delete transaction');
    }
  };

  if (loading)
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="animate-spin" size={32} />
      </div>
    );

  return (
    <div className="space-y-6">
      <Card className="p-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Account ID</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {transactions.map((tx) => (
              <TableRow key={tx.id}>
                <TableCell>{tx.account_id}</TableCell>
                <TableCell>{tx.txn_type}</TableCell>
                <TableCell>{tx.amount}</TableCell>
                <TableCell>{tx.category}</TableCell>
                <TableCell>{tx.description}</TableCell>
                <TableCell>
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
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <div className="mt-4 flex justify-center">
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious 
                  href="#"
                  onClick={e => {
                    e.preventDefault();
                    if (page > 1) setPage(page - 1);
                  }}
                  className={page <= 1 ? 'pointer-events-none opacity-50' : ''}
                />
              </PaginationItem>
              {Array.from({ length: Math.ceil(total / PAGE_SIZE) }).map((_, i) => {
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
                        onClick={e => {
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
              })}
              <PaginationItem>
                <PaginationNext 
                  href="#"
                  onClick={e => {
                    e.preventDefault();
                    if (page < Math.ceil(total / PAGE_SIZE)) setPage(page + 1);
                  }}
                  className={page >= Math.ceil(total / PAGE_SIZE) ? 'pointer-events-none opacity-50' : ''}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      </Card>
      {editId !== null && (
        <Card className="p-4">
          <div className="flex gap-2 mb-4">
            <input
              type="number"
              placeholder="Account ID"
              value={editForm.account_id ?? 0}
              onChange={e => setEditForm(f => ({ ...f, account_id: Number(e.target.value) }))}
              className="border rounded px-2 py-1"
            />
            <select
              value={editForm.txn_type ?? 'credit'}
              onChange={e => setEditForm(f => ({ ...f, txn_type: e.target.value as 'credit' | 'debit' }))}
              className="border rounded px-2 py-1"
            >
              <option value="credit">Credit</option>
              <option value="debit">Debit</option>
            </select>
            <input
              type="number"
              placeholder="Amount"
              value={editForm.amount ?? 0}
              onChange={e => setEditForm(f => ({ ...f, amount: Number(e.target.value) }))}
              className="border rounded px-2 py-1"
            />
            <input
              type="text"
              placeholder="Category"
              value={editForm.category ?? ''}
              onChange={e => setEditForm(f => ({ ...f, category: e.target.value }))}
              className="border rounded px-2 py-1"
            />
            <input
              type="text"
              placeholder="Description"
              value={editForm.description ?? ''}
              onChange={e => setEditForm(f => ({ ...f, description: e.target.value }))}
              className="border rounded px-2 py-1"
            />
            <Button onClick={handleEdit} variant="default">
              <Pencil size={18} /> Save
            </Button>
            <Button onClick={() => setEditId(null)} variant="outline">
              Cancel
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
