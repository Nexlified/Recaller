'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import authService from '@/services/auth';
import { Header } from '@/components/layout/Header';
import { RelationshipManager } from '@/components/contacts/RelationshipManager';
import { RelationshipNetwork } from '@/components/contacts/RelationshipNetwork';
import { RelationshipTimeline } from '@/components/contacts/RelationshipTimeline';
import contactsService, { Contact } from '@/services/contacts';
import type { User } from '@/services/auth';

interface ContactDetailPageProps {
  params: {
    id: string;
  };
}

export default function ContactDetailPage({ params }: ContactDetailPageProps) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [contact, setContact] = useState<Contact | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'details' | 'relationships' | 'network' | 'timeline'>('details');

  const contactId = parseInt(params.id);

  useEffect(() => {
    // Check if user is authenticated
    const currentUser = authService.getCurrentUser();
    setUser(currentUser);

    if (currentUser && contactId) {
      loadContact();
    } else {
      setIsLoading(false);
    }
  }, [contactId, loadContact]);

  const loadContact = useCallback(async () => {
    try {
      setIsLoading(true);
      const contacts = await contactsService.getContacts();
      const foundContact = contacts.find(c => c.id === contactId);
      
      if (!foundContact) {
        router.push('/contacts');
        return;
      }
      
      setContact(foundContact);
    } catch (error) {
      console.error('Error loading contact:', error);
      router.push('/contacts');
    } finally {
      setIsLoading(false);
    }
  }, [contactId, router]);

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    router.push('/login');
  };

  const handleRelationshipChange = () => {
    // Refresh contact data if needed
    loadContact();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-lg text-gray-600 dark:text-gray-400">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 text-center">
          <div>
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
              Access Denied
            </h2>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Please sign in to access contact details
            </p>
          </div>
          <Link
            href="/login"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Sign In
          </Link>
        </div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header user={user} title="Contact Not Found" onLogout={handleLogout} />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0 text-center">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Contact Not Found</h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              The contact you&apos;re looking for doesn&apos;t exist or you don&apos;t have access to it.
            </p>
            <Link
              href="/contacts"
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Back to Contacts
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} title={`${contact.first_name} ${contact.last_name || ''}`} onLogout={handleLogout} />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header with navigation */}
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Link
                  href="/contacts"
                  className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  ← Back to Contacts
                </Link>
                <div className="h-6 w-px bg-gray-300 dark:bg-gray-600"></div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {contact.first_name} {contact.last_name}
                </h1>
              </div>
            </div>

            {/* Tab navigation */}
            <div className="mt-4 border-b border-gray-200 dark:border-gray-700">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('details')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'details'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Details
                </button>
                <button
                  onClick={() => setActiveTab('relationships')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'relationships'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Relationships
                </button>
                <button
                  onClick={() => setActiveTab('network')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'network'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Network
                </button>
                <button
                  onClick={() => setActiveTab('timeline')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'timeline'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Timeline
                </button>
              </nav>
            </div>
          </div>

          {/* Tab content */}
          <div className="mt-6">
            {activeTab === 'details' && (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-6 py-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Contact Information</h3>
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        First Name
                      </label>
                      <div className="mt-1 text-sm text-gray-900 dark:text-white">
                        {contact.first_name}
                      </div>
                    </div>
                    
                    {contact.last_name && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Last Name
                        </label>
                        <div className="mt-1 text-sm text-gray-900 dark:text-white">
                          {contact.last_name}
                        </div>
                      </div>
                    )}
                    
                    {contact.email && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Email
                        </label>
                        <div className="mt-1 text-sm text-gray-900 dark:text-white">
                          <a href={`mailto:${contact.email}`} className="text-blue-600 hover:text-blue-700 dark:text-blue-400">
                            {contact.email}
                          </a>
                        </div>
                      </div>
                    )}
                    
                    {contact.phone && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Phone
                        </label>
                        <div className="mt-1 text-sm text-gray-900 dark:text-white">
                          <a href={`tel:${contact.phone}`} className="text-blue-600 hover:text-blue-700 dark:text-blue-400">
                            {contact.phone}
                          </a>
                        </div>
                      </div>
                    )}
                    
                    {contact.job_title && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Job Title
                        </label>
                        <div className="mt-1 text-sm text-gray-900 dark:text-white">
                          {contact.job_title}
                        </div>
                      </div>
                    )}
                    
                    {contact.company && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Company
                        </label>
                        <div className="mt-1 text-sm text-gray-900 dark:text-white">
                          {contact.company}
                        </div>
                      </div>
                    )}
                    
                    {contact.notes && (
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Notes
                        </label>
                        <div className="mt-1 text-sm text-gray-900 dark:text-white">
                          {contact.notes}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'relationships' && (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <RelationshipManager
                  contactId={contactId}
                  onRelationshipChange={handleRelationshipChange}
                />
              </div>
            )}

            {activeTab === 'network' && (
              <RelationshipNetwork contactId={contactId} width={800} height={500} />
            )}

            {activeTab === 'timeline' && (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <RelationshipTimeline contactId={contactId} />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}