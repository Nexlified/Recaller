'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import authService from '@/services/auth';
import { ContactForm } from '@/components/contacts/ContactForm';
import { ConfirmDialog } from '@/components/contacts/ConfirmDialog';
import contactsService, { Contact, ContactVisibility } from '@/services/contacts';
import type { User } from '@/services/auth';

export default function ContactsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [ownContacts, setOwnContacts] = useState<Contact[]>([]);
  const [publicContacts, setPublicContacts] = useState<Contact[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);
  const [loadingContacts, setLoadingContacts] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState<{
    isOpen: boolean;
    contact: Contact | null;
    isDeleting: boolean;
  }>({
    isOpen: false,
    contact: null,
    isDeleting: false,
  });

  useEffect(() => {
    // Check if user is authenticated
    const currentUser = authService.getCurrentUser();
    setUser(currentUser);
    setIsLoading(false);

    // Load contacts if user is authenticated
    if (currentUser) {
      loadContacts();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadContacts = async () => {
    try {
      setLoadingContacts(true);
      
      // Load all contacts (owned + public)
      const allContacts = await contactsService.getContacts();
      
      // Separate own contacts from public contacts
      const own = allContacts.filter(contact => contact.created_by_user_id === user?.id);
      const otherPublic = allContacts.filter(contact => 
        contact.created_by_user_id !== user?.id && contact.visibility === ContactVisibility.PUBLIC
      );
      
      setOwnContacts(own);
      setPublicContacts(otherPublic);
    } catch (error) {
      console.error('Error loading contacts:', error);
    } finally {
      setLoadingContacts(false);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
  };

  const handleContactCreated = (newContact: Contact) => {
    if (editingContact) {
      // Update existing contact
      setOwnContacts(prev => prev.map(contact => 
        contact.id === editingContact.id ? newContact : contact
      ));
      setEditingContact(null);
      alert('Contact updated successfully!');
    } else {
      // Add new contact to own contacts
      setOwnContacts(prev => [newContact, ...prev]);
      alert('Contact created successfully!');
    }
    setShowForm(false);
  };

  const handleEditContact = (contact: Contact) => {
    setEditingContact(contact);
    setShowForm(true);
  };

  const handleDeleteContact = (contact: Contact) => {
    setDeleteDialog({
      isOpen: true,
      contact,
      isDeleting: false,
    });
  };

  const confirmDeleteContact = async () => {
    if (!deleteDialog.contact) return;

    setDeleteDialog(prev => ({ ...prev, isDeleting: true }));

    try {
      await contactsService.deleteContact(deleteDialog.contact.id);
      setOwnContacts(prev => prev.filter(contact => contact.id !== deleteDialog.contact!.id));
      setDeleteDialog({ isOpen: false, contact: null, isDeleting: false });
      alert('Contact deleted successfully!');
    } catch (error) {
      console.error('Error deleting contact:', error);
      alert('Failed to delete contact. Please try again.');
      setDeleteDialog(prev => ({ ...prev, isDeleting: false }));
    }
  };

  const cancelDelete = () => {
    setDeleteDialog({ isOpen: false, contact: null, isDeleting: false });
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingContact(null);
  };

  const handleVisibilityChange = async (contact: Contact, newVisibility: ContactVisibility) => {
    try {
      const updatedContact = await contactsService.updateContactVisibility(contact.id, newVisibility);
      
      // Update the contact in the appropriate list
      setOwnContacts(prev => prev.map(c => 
        c.id === contact.id ? updatedContact : c
      ));
      
      alert('Contact visibility updated successfully!');
    } catch (error) {
      console.error('Error updating contact visibility:', error);
      alert('Failed to update contact visibility. Please try again.');
    }
  };

  const renderContactList = (contacts: Contact[], isOwner: boolean, title: string) => {
    if (loadingContacts) {
      return (
        <div className="text-center py-8">
          <div className="text-lg text-gray-600">Loading {title.toLowerCase()}...</div>
        </div>
      );
    }

    if (contacts.length === 0) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-500">No {title.toLowerCase()} found.</div>
        </div>
      );
    }

    return (
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <ul className="divide-y divide-gray-200">
          {contacts.map((contact) => (
            <li key={contact.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-700">
                        {contact.first_name.charAt(0)}{contact.last_name?.charAt(0) || ''}
                      </span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-sm font-medium text-gray-900">
                      {contact.first_name} {contact.last_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {contact.email && <span>{contact.email}</span>}
                      {contact.email && contact.phone && <span> • </span>}
                      {contact.phone && <span>{contact.phone}</span>}
                    </div>
                    {contact.job_title && (
                      <div className="text-sm text-gray-500">
                        {contact.job_title}
                      </div>
                    )}
                    {/* Visibility indicator */}
                    <div className="mt-1">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        contact.visibility === ContactVisibility.PUBLIC 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {contact.visibility === ContactVisibility.PUBLIC ? '🌍 Public' : '🔒 Private'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {isOwner && (
                    <>
                      {/* Visibility toggle */}
                      <select
                        value={contact.visibility}
                        onChange={(e) => handleVisibilityChange(contact, e.target.value as ContactVisibility)}
                        className="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
                      >
                        <option value={ContactVisibility.PRIVATE}>Private</option>
                        <option value={ContactVisibility.PUBLIC}>Public</option>
                      </select>
                      <button 
                        onClick={() => handleEditContact(contact)}
                        className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                      >
                        Edit
                      </button>
                      <button 
                        onClick={() => handleDeleteContact(contact)}
                        className="text-red-600 hover:text-red-900 text-sm font-medium"
                      >
                        Delete
                      </button>
                    </>
                  )}
                  {!isOwner && (
                    <span className="text-gray-400 text-sm">View only</span>
                  )}
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!user) {
    // User not authenticated - redirect to login
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 text-center">
          <div>
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              Access Denied
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Please sign in to access your contacts
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-2xl font-bold text-gray-900 hover:text-gray-700">
                Recaller
              </Link>
              <span className="text-gray-400">|</span>
              <h1 className="text-xl font-semibold text-gray-900">Contacts</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user.full_name || user.email}</span>
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {showForm ? (
            <ContactForm
              onSuccess={handleContactCreated}
              onCancel={handleFormCancel}
              editingContact={editingContact}
            />
          ) : (
            <div>
              {/* Contacts Header */}
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Your Contacts</h2>
                <button
                  onClick={() => setShowForm(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add New Contact
                </button>
              </div>

              {/* Your Contacts Section */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Contacts</h3>
                {renderContactList(ownContacts, true, "Your Contacts")}
              </div>

              {/* Public Contacts Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Public Contacts</h3>
                {renderContactList(publicContacts, false, "Public Contacts")}
              </div>

              {/* Show empty state only if both lists are empty and not loading */}
              {!loadingContacts && ownContacts.length === 0 && publicContacts.length === 0 && (
                <div className="text-center py-12">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No contacts</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Get started by creating a new contact.
                  </p>
                  <div className="mt-6">
                    <button
                      onClick={() => setShowForm(true)}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    >
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Add New Contact
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteDialog.isOpen}
        title="Delete Contact"
        message={`Are you sure you want to delete ${deleteDialog.contact?.first_name} ${deleteDialog.contact?.last_name}? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDeleteContact}
        onCancel={cancelDelete}
        isLoading={deleteDialog.isDeleting}
      />
    </div>
  );
}