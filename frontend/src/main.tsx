import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './pages/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { Accounts } from './pages/Accounts';
import { CashFlowPage } from './pages/CashFlow';
import { ThemeProvider } from './components/theme-provider';

createRoot(document.getElementById('root')!).render(
  <ThemeProvider>
    <StrictMode>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="accounts" element={<Accounts />} />
            <Route path="cashflow" element={<CashFlowPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </StrictMode>
  </ThemeProvider>
);
