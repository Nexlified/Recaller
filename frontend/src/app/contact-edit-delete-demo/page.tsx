'use client';

import React, { useState } from 'react';
import { ContactForm } from '@/components/contacts/ContactForm';
import { ConfirmDialog } from '@/components/contacts/ConfirmDialog';
import { Contact, ContactVisibility } from '@/services/contacts';

export default function ContactEditDeleteDemo() {
  const [contacts, setContacts] = useState<Contact[]>([
    {
      id: 1,
      tenant_id: 1,
      created_by_user_id: 1,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com',
      phone: '555-1234',
      job_title: 'Software Engineer',
      organization_id: 1,
      notes: 'Met at conference',
      visibility: ContactVisibility.PRIVATE,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      tenant_id: 1,
      created_by_user_id: 1,
      first_name: 'Jane',
      last_name: 'Smith',
      email: 'jane.smith@example.com',
      phone: '555-5678',
      job_title: 'Product Manager',
      organization_id: 2,
      notes: 'Potential collaboration',
      visibility: ContactVisibility.PUBLIC,
      is_active: true,
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    },
  ]);

  const [showForm, setShowForm] = useState(false);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);
  const [deleteDialog, setDeleteDialog] = useState<{
    isOpen: boolean;
    contact: Contact | null;
    isDeleting: boolean;
  }>({
    isOpen: false,
    contact: null,
    isDeleting: false,
  });

  const handleContactSaved = (savedContact: Contact) => {
    if (editingContact) {
      // Update existing contact
      setContacts(prev => prev.map(contact => 
        contact.id === editingContact.id ? savedContact : contact
      ));
      setEditingContact(null);
      alert('Demo: Contact updated successfully!');
    } else {
      // Add new contact
      setContacts(prev => [savedContact, ...prev]);
      alert('Demo: Contact created successfully!');
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

    // Simulate async delete
    setTimeout(() => {
      setContacts(prev => prev.filter(contact => contact.id !== deleteDialog.contact!.id));
      setDeleteDialog({ isOpen: false, contact: null, isDeleting: false });
      alert('Demo: Contact deleted successfully!');
    }, 1000);
  };

  const cancelDelete = () => {
    setDeleteDialog({ isOpen: false, contact: null, isDeleting: false });
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingContact(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      {/* Header */}
      <header className="bg-white shadow mb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-2xl font-bold text-gray-900">Contact Edit & Delete Demo</h1>
            <p className="text-sm text-gray-600">
              Demo of contact management with edit and delete functionality. All operations are simulated.
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {showForm ? (
          <ContactForm
            onSuccess={handleContactSaved}
            onCancel={handleFormCancel}
            editingContact={editingContact}
            demoMode={true}
          />
        ) : (
          <div>
            {/* Contacts Header */}
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Sample Contacts</h2>
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

            {/* Contacts List */}
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
                        {/* Visibility toggle for demo */}
                        <select
                          value={contact.visibility}
                          onChange={(e) => {
                            const newVisibility = e.target.value as ContactVisibility;
                            setContacts(prev => prev.map(c => 
                              c.id === contact.id ? { ...c, visibility: newVisibility } : c
                            ));
                            alert(`Demo: Contact visibility changed to ${newVisibility}`);
                          }}
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
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
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