'use client';

import React, { useState } from 'react';
import { JournalEntryForm } from '../../components/journal/JournalEntryForm';
import { JournalEntryView } from '../../components/journal/JournalEntryView';
import { JournalEntryList } from '../../components/journal/JournalEntryList';
import { 
  JournalEntry, 
  JournalEntryCreate, 
  JournalEntryUpdate, 
  JournalEntrySummary, 
  JournalEntryMood 
} from '../../types/Journal';

// Mock data for demo
const mockEntries: JournalEntrySummary[] = [
  {
    id: 1,
    title: "My First Journal Entry",
    entry_date: "2024-01-15",
    mood: JournalEntryMood.HAPPY,
    is_private: true,
    is_archived: false,
    created_at: "2024-01-15T10:30:00Z",
    tag_count: 2,
    attachment_count: 0,
  },
  {
    id: 2,
    title: "Reflections on the week",
    entry_date: "2024-01-14",
    mood: JournalEntryMood.CONTENT,
    is_private: false,
    is_archived: false,
    created_at: "2024-01-14T18:45:00Z",
    tag_count: 1,
    attachment_count: 1,
  },
  {
    id: 3,
    title: undefined,
    entry_date: "2024-01-13",
    mood: JournalEntryMood.GRATEFUL,
    is_private: true,
    is_archived: false,
    created_at: "2024-01-13T09:15:00Z",
    tag_count: 3,
    attachment_count: 0,
  },
];

const mockEntry: JournalEntry = {
  id: 1,
  tenant_id: 1,
  user_id: 1,
  title: "My First Journal Entry",
  content: `# Welcome to My Journal

This is my **first journal entry** using the new markdown editor! I'm really excited about this feature.

## What I accomplished today:
- ✅ Completed the journal frontend implementation
- ✅ Added markdown editing capabilities
- ✅ Created a beautiful UI with Tailwind CSS

## Reflections

Today was a *great day* for productivity. The new journal feature will help me:

1. **Document my thoughts** more effectively
2. **Track my mood** and emotional patterns
3. **Organize my experiences** with tags and categories

> "The unexamined life is not worth living." - Socrates

I'm looking forward to using this journal feature regularly!

### Code Example
\`\`\`javascript
const journalEntry = {
  title: "My thoughts",
  content: "Today I learned something new!",
  mood: "happy"
};
\`\`\`

---

This journal supports **full markdown** with _emphasis_, [links](https://example.com), and much more!`,
  entry_date: "2024-01-15",
  mood: JournalEntryMood.HAPPY,
  location: "Home Office",
  weather: "Sunny",
  is_private: true,
  is_archived: false,
  entry_version: 1,
  parent_entry_id: undefined,
  is_encrypted: false,
  created_at: "2024-01-15T10:30:00Z",
  updated_at: "2024-01-15T10:30:00Z",
  tags: [
    {
      id: 1,
      journal_entry_id: 1,
      tag_name: "productivity",
      tag_color: "#3B82F6",
      created_at: "2024-01-15T10:30:00Z",
    },
    {
      id: 2,
      journal_entry_id: 1,
      tag_name: "coding",
      tag_color: "#059669",
      created_at: "2024-01-15T10:30:00Z",
    },
  ],
  attachments: [],
};

export default function JournalDemoPage() {
  const [activeView, setActiveView] = useState<'list' | 'create' | 'view'>('list');
  const [entries] = useState<JournalEntrySummary[]>(mockEntries);
  const [currentEntry] = useState<JournalEntry>(mockEntry);

  const handleSave = async (entryData: JournalEntryCreate | JournalEntryUpdate) => {
    console.log('Saving entry:', entryData);
    alert('Journal entry saved! (This is a demo - no actual save occurred)');
    setActiveView('view');
  };

  const handleCancel = () => {
    setActiveView('list');
  };

  const handleEdit = () => {
    setActiveView('create');
  };

  const handleDelete = () => {
    alert('Delete functionality demo - entry would be deleted');
  };

  const handleArchive = () => {
    alert('Archive functionality demo - entry would be archived');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Journal Demo</h1>
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveView('list')}
                className={`px-4 py-2 text-sm font-medium rounded-md ${
                  activeView === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                List View
              </button>
              <button
                onClick={() => setActiveView('create')}
                className={`px-4 py-2 text-sm font-medium rounded-md ${
                  activeView === 'create'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Create/Edit
              </button>
              <button
                onClick={() => setActiveView('view')}
                className={`px-4 py-2 text-sm font-medium rounded-md ${
                  activeView === 'view'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                View Entry
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="py-6">
        {activeView === 'list' && (
          <div className="max-w-4xl mx-auto px-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Journal Entries</h2>
              <p className="text-gray-600">View and manage your journal entries</p>
            </div>
            <JournalEntryList 
              entries={entries} 
              onEntryClick={(id) => {
                console.log('Clicked entry:', id);
                setActiveView('view');
              }}
            />
          </div>
        )}

        {activeView === 'create' && (
          <JournalEntryForm
            entry={currentEntry}
            onSave={handleSave}
            onCancel={handleCancel}
            isLoading={false}
          />
        )}

        {activeView === 'view' && (
          <JournalEntryView
            entry={currentEntry}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onArchive={handleArchive}
            showActions={true}
          />
        )}
      </div>
    </div>
  );
}