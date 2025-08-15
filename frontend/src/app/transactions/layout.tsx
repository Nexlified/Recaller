'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import authService from '@/services/auth';
import type { User } from '@/services/auth';

interface TransactionsLayoutProps {
  children: React.ReactNode;
}

export default function TransactionsLayout({ children }: TransactionsLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      router.push('/login');
      return;
    }
    setUser(currentUser);
  }, [router]);

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    router.push('/login');
  };

  const isActiveTab = (path: string) => {
    if (path === '/transactions') {
      return pathname === '/transactions' || pathname?.match(/^\/transactions\/\d+$/);
    }
    return pathname?.startsWith(path);
  };

  const getTabClassName = (path: string) => {
    const baseClasses = "py-4 px-1 border-b-2 whitespace-nowrap text-sm font-medium";
    const activeClasses = "border-blue-500 text-blue-600 dark:text-blue-400";
    const inactiveClasses = "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:border-gray-500";
    
    return `${baseClasses} ${isActiveTab(path) ? activeClasses : inactiveClasses}`;
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-lg text-gray-600 dark:text-gray-400">Redirecting to login...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} title="Transactions" onLogout={handleLogout} />

      {/* Navigation Tabs */}
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <Link
              href="/transactions"
              className={getTabClassName('/transactions')}
            >
              All Transactions
            </Link>
            <Link
              href="/transactions/create"
              className={getTabClassName('/transactions/create')}
            >
              Add Transaction
            </Link>
            <Link
              href="/transactions/categories"
              className={getTabClassName('/transactions/categories')}
            >
              Categories
            </Link>
            <Link
              href="/transactions/accounts"
              className={getTabClassName('/transactions/accounts')}
            >
              Accounts
            </Link>
            <Link
              href="/transactions/recurring"
              className={getTabClassName('/transactions/recurring')}
            >
              Recurring
            </Link>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}