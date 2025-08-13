'use client';

import React from 'react';
import { ContactForm } from '@/components/contacts/ContactForm';
import { Contact } from '@/services/contacts';

export default function ContactFormDemo() {
  const handleSuccess = (contact: Contact) => {
    console.log('Contact created:', contact);
    alert('Demo: Contact would be created successfully!');
  };

  const handleCancel = () => {
    console.log('Form cancelled');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      {/* Header */}
      <header className="bg-white shadow mb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-2xl font-bold text-gray-900">Contact Form Demo</h1>
            <p className="text-sm text-gray-600">
              This is a demo of the contact creation form. Backend validation is disabled for demo purposes.
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <ContactForm onSuccess={handleSuccess} onCancel={handleCancel} demoMode={true} />
      </main>
    </div>
  );
}