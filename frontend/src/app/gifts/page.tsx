'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import authService from '@/services/auth';
import giftsService from '@/services/gifts';
import { contactsService } from '@/services/contacts';
import { Gift, GiftIdea, GiftAnalytics } from '@/types/Gift';
import { Contact } from '@/services/contacts';
import type { User } from '@/services/auth';
import { GiftList, GiftIdeaList } from '@/components/gifts';

// Dashboard Components
const GiftSummaryCards = ({ gifts, ideas }: { gifts: Gift[]; ideas: GiftIdea[] }) => {
  const totalGifts = gifts.length;
  const totalIdeas = ideas.length;
  const giftsGiven = gifts.filter(g => g.status === 'given').length;
  const upcomingOccasions = gifts.filter(g => {
    if (!g.occasion_date) return false;
    const occasionDate = new Date(g.occasion_date);
    const today = new Date();
    const diffTime = occasionDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays >= 0 && diffDays <= 30; // Next 30 days
  }).length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Gifts</h3>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalGifts}</p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Gift Ideas</h3>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalIdeas}</p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Gifts Given</h3>
        <p className="text-2xl font-bold text-green-600 dark:text-green-400">{giftsGiven}</p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Upcoming Occasions</h3>
        <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{upcomingOccasions}</p>
      </div>
    </div>
  );
};

const UpcomingOccasions = ({ gifts }: { gifts: Gift[] }) => {
  const upcomingGifts = gifts
    .filter(g => g.occasion_date && g.status !== 'given')
    .sort((a, b) => {
      if (!a.occasion_date || !b.occasion_date) return 0;
      return new Date(a.occasion_date).getTime() - new Date(b.occasion_date).getTime();
    })
    .slice(0, 5);

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Upcoming Occasions</h3>
      {upcomingGifts.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400">No upcoming occasions</p>
      ) : (
        <div className="space-y-3">
          {upcomingGifts.map(gift => (
            <div key={gift.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">{gift.title}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {gift.recipient_name} • {gift.occasion}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {gift.occasion_date ? giftsService.formatOccasionDate(gift.occasion_date) : 'No date'}
                </p>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  gift.status === 'idea' ? 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200' :
                  gift.status === 'planned' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400' :
                  gift.status === 'purchased' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
                  'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
                }`}>
                  {gift.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const QuickActions = ({ 
  onAddGift, 
  onAddIdea 
}: { 
  onAddGift: () => void; 
  onAddIdea: () => void; 
}) => {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Quick Actions</h3>
      <div className="space-y-3">
        <button
          onClick={onAddGift}
          className="w-full px-4 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
        >
          <div className="flex items-center justify-center space-x-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span>Add New Gift</span>
          </div>
        </button>
        <button
          onClick={onAddIdea}
          className="w-full px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
        >
          <div className="flex items-center justify-center space-x-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span>Add Gift Idea</span>
          </div>
        </button>
      </div>
    </div>
  );
};

const RecentGifts = ({ gifts }: { gifts: Gift[] }) => {
  const recentGifts = gifts
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 3);

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Gifts</h3>
      {recentGifts.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400">No gifts yet</p>
      ) : (
        <div className="space-y-4">
          {recentGifts.map(gift => (
            <div key={gift.id} className="border-l-4 border-indigo-400 pl-4">
              <p className="font-medium text-gray-900 dark:text-white">{gift.title}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {gift.recipient_name && `For ${gift.recipient_name}`}
                {gift.budget_amount && ` • ${giftsService.formatCurrency(gift.budget_amount, gift.currency)}`}
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500">
                {new Date(gift.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default function GiftsDashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [gifts, setGifts] = useState<Gift[]>([]);
  const [giftIdeas, setGiftIdeas] = useState<GiftIdea[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'gifts' | 'ideas'>('dashboard');

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      window.location.href = '/login';
      return;
    }
    setUser(currentUser);
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load gifts, ideas, and contacts
      const [giftsData, ideasData, contactsData] = await Promise.all([
        giftsService.getGifts(0, 100),
        giftsService.getGiftIdeas(0, 100),
        contactsService.getContacts()
      ]);
      
      setGifts(giftsData);
      setGiftIdeas(ideasData);
      setContacts(contactsData);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    window.location.href = '/login';
  };

  const handleAddGift = () => {
    // Navigate to add gift page (will be implemented)
    console.log('Navigate to add gift');
  };

  const handleAddIdea = () => {
    // Navigate to add idea page (will be implemented)
    console.log('Navigate to add idea');
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
      <Header user={user} title="Gift Management" onLogout={handleLogout} />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Page Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Gift Management</h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Manage your gifts and gift ideas
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="mb-6">
            <nav className="flex space-x-8" aria-label="Tabs">
              {[
                { key: 'dashboard', label: 'Dashboard' },
                { key: 'gifts', label: 'Gifts' },
                { key: 'ideas', label: 'Gift Ideas' },
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="space-y-6">
              <div className="animate-pulse">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                  ))}
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                  <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {activeTab === 'dashboard' && (
                <>
                  {/* Summary Cards */}
                  <GiftSummaryCards gifts={gifts} ideas={giftIdeas} />

                  {/* Main Dashboard Content */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Left Column */}
                    <div className="space-y-6">
                      <UpcomingOccasions gifts={gifts} />
                      <RecentGifts gifts={gifts} />
                    </div>

                    {/* Right Column */}
                    <div className="space-y-6">
                      <QuickActions onAddGift={handleAddGift} onAddIdea={handleAddIdea} />
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'gifts' && (
                <GiftList
                  gifts={gifts}
                  onRefresh={loadDashboardData}
                  showFilters={true}
                  showViewModeToggle={true}
                />
              )}

              {activeTab === 'ideas' && (
                <GiftIdeaList
                  giftIdeas={giftIdeas}
                  contacts={contacts}
                  onRefresh={loadDashboardData}
                  showFilters={true}
                />
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}