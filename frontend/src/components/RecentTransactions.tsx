import type { CashFlow } from '../types/cash_flow';
import { Card } from './ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';

export function RecentTransactions({
  transactions,
}: {
  transactions: CashFlow[];
}) {
  return (
    <Card className="p-4">
      <div className="text-lg font-bold mb-2">Recent Transactions</div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Date</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Description</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {transactions.slice(0, 5).map((tx) => (
            <TableRow key={tx.id}>
              <TableCell>{tx.date}</TableCell>
              <TableCell>
                {tx.type === 'income' ? (
                  <ArrowUpRight className="text-green-600" size={18} />
                ) : (
                  <ArrowDownLeft className="text-red-600" size={18} />
                )}
                {tx.type.charAt(0).toUpperCase() + tx.type.slice(1)}
              </TableCell>
              <TableCell>${tx.amount.toLocaleString()}</TableCell>
              <TableCell>{tx.category}</TableCell>
              <TableCell>{tx.description || '-'}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
