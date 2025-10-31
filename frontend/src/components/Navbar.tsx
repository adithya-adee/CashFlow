import { Link, useLocation } from 'react-router-dom';
import { Home, List, DollarSign, Wallet } from 'lucide-react';
import { cn } from '../lib/utils';

export function Navbar() {
  const location = useLocation();
  return (
    <nav className="bg-card border-b">
      <div className="max-w-7xl mx-auto px-6 py-3 flex gap-6 items-center">
        <Link to="/" className="flex items-center gap-2 mr-4 font-bold text-lg">
          <Wallet size={24} className="text-primary" />
          <span>CashFlow</span>
        </Link>
        <Link
          to="/"
          className={cn(
            'flex items-center gap-2 text-sm',
            location.pathname === '/' && 'font-bold text-primary'
          )}
        >
          <Home size={18} /> Dashboard
        </Link>
        <Link
          to="/accounts"
          className={cn(
            'flex items-center gap-2 text-sm',
            location.pathname === '/accounts' && 'font-bold text-primary'
          )}
        >
          <List size={18} /> Accounts
        </Link>
        <Link
          to="/cashflow"
          className={cn(
            'flex items-center gap-2 text-sm',
            location.pathname === '/cashflow' && 'font-bold text-primary'
          )}
        >
          <DollarSign size={18} /> CashFlow
        </Link>
      </div>
    </nav>
  );
}
