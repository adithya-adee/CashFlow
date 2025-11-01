import { useEffect, useState } from 'react';
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
import { toast } from 'sonner';
import { Loader2, Pencil, Trash2, Plus } from 'lucide-react';

export function Accounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
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

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const data = await listAccounts();
      console.log(data);
      setAccounts(data);
    } catch {
      toast.error('Failed to fetch accounts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

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

  if (loading)
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="animate-spin" size={32} />
      </div>
    );

  return (
    <div className="space-y-6">
      <Card className="p-4">
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            placeholder="Account No."
            value={form.bank_account_no}
            onChange={(e) =>
              setForm((f) => ({ ...f, bank_account_no: e.target.value }))
            }
            className="border rounded px-2 py-1"
          />
          <input
            type="text"
            placeholder="Bank Name"
            value={form.bank_name}
            onChange={(e) =>
              setForm((f) => ({ ...f, bank_name: e.target.value }))
            }
            className="border rounded px-2 py-1"
          />
          <select
            value={form.account_type}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                account_type: e.target.value as Account['account_type'],
              }))
            }
            className="border rounded px-2 py-1"
          >
            <option value="savings">Savings</option>
            <option value="current_account">Current</option>
            <option value="fd_account">FD</option>
            <option value="rd_account">RD</option>
            <option value="demat_account">Demat</option>
          </select>
          <input
            type="text"
            placeholder="Holder Name"
            value={form.holder_name}
            onChange={(e) =>
              setForm((f) => ({ ...f, holder_name: e.target.value }))
            }
            className="border rounded px-2 py-1"
          />
          <select
            value={form.currency}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                currency: e.target.value as Account['currency'],
              }))
            }
            className="border rounded px-2 py-1"
          >
            <option value="INR">INR</option>
            <option value="USD">USD</option>
          </select>
          <input
            type="number"
            placeholder="Balance"
            value={form.balance}
            onChange={(e) =>
              setForm((f) => ({ ...f, balance: Number(e.target.value) }))
            }
            className="border rounded px-2 py-1"
          />
          <Button onClick={handleAdd} variant="default">
            <Plus size={18} /> Add
          </Button>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
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
            {accounts.map((acc) => (
              <TableRow key={acc.id}>
                <TableCell>{acc.bank_account_no}</TableCell>
                <TableCell>{acc.bank_name}</TableCell>
                <TableCell>{acc.account_type}</TableCell>
                <TableCell>{acc.holder_name}</TableCell>
                <TableCell>{acc.currency}</TableCell>
                <TableCell>${acc.balance.toLocaleString()}</TableCell>
                <TableCell>
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
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
      {editId !== null && (
        <Card className="p-4">
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              placeholder="Account No."
              value={editForm.bank_account_no ?? ''}
              onChange={(e) =>
                setEditForm((f) => ({ ...f, bank_account_no: e.target.value }))
              }
              className="border rounded px-2 py-1"
            />
            <input
              type="text"
              placeholder="Bank Name"
              value={editForm.bank_name ?? ''}
              onChange={(e) =>
                setEditForm((f) => ({ ...f, bank_name: e.target.value }))
              }
              className="border rounded px-2 py-1"
            />
            <select
              value={editForm.account_type ?? 'savings'}
              onChange={(e) =>
                setEditForm((f) => ({
                  ...f,
                  account_type: e.target.value as Account['account_type'],
                }))
              }
              className="border rounded px-2 py-1"
            >
              <option value="savings">Savings</option>
              <option value="current_account">Current</option>
              <option value="fd_account">FD</option>
              <option value="rd_account">RD</option>
              <option value="demat_account">Demat</option>
            </select>
            <input
              type="text"
              placeholder="Holder Name"
              value={editForm.holder_name ?? ''}
              onChange={(e) =>
                setEditForm((f) => ({ ...f, holder_name: e.target.value }))
              }
              className="border rounded px-2 py-1"
            />
            <select
              value={editForm.currency ?? 'INR'}
              onChange={(e) =>
                setEditForm((f) => ({
                  ...f,
                  currency: e.target.value as Account['currency'],
                }))
              }
              className="border rounded px-2 py-1"
            >
              <option value="INR">INR</option>
              <option value="USD">USD</option>
            </select>
            <input
              type="number"
              placeholder="Balance"
              value={editForm.balance ?? 0}
              onChange={(e) =>
                setEditForm((f) => ({ ...f, balance: Number(e.target.value) }))
              }
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
