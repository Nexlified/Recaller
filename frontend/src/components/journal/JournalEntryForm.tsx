import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import {
  JournalEntry,
  JournalEntryCreate,
  JournalEntryUpdate,
  JournalEntryMood,
  JournalTagCreate,
} from '../../types/Journal';
import '@uiw/react-md-editor/markdown-editor.css';
import '@uiw/react-markdown-preview/markdown.css';

// Dynamically import the markdown editor to avoid SSR issues
const MDEditor = dynamic(
  () => import('@uiw/react-md-editor'),
  { ssr: false }
);

interface JournalEntryFormProps {
  entry?: JournalEntry;
  onSave: (entry: JournalEntryCreate | JournalEntryUpdate) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

const moodOptions = [
  { value: JournalEntryMood.VERY_HAPPY, label: '😄 Very Happy', color: 'text-green-600' },
  { value: JournalEntryMood.HAPPY, label: '😊 Happy', color: 'text-green-500' },
  { value: JournalEntryMood.CONTENT, label: '😌 Content', color: 'text-green-400' },
  { value: JournalEntryMood.NEUTRAL, label: '😐 Neutral', color: 'text-gray-500' },
  { value: JournalEntryMood.ANXIOUS, label: '😰 Anxious', color: 'text-yellow-500' },
  { value: JournalEntryMood.SAD, label: '😢 Sad', color: 'text-blue-500' },
  { value: JournalEntryMood.VERY_SAD, label: '😭 Very Sad', color: 'text-blue-600' },
  { value: JournalEntryMood.ANGRY, label: '😠 Angry', color: 'text-red-500' },
  { value: JournalEntryMood.EXCITED, label: '🤩 Excited', color: 'text-purple-500' },
  { value: JournalEntryMood.GRATEFUL, label: '🙏 Grateful', color: 'text-pink-500' },
];

export const JournalEntryForm: React.FC<JournalEntryFormProps> = ({
  entry,
  onSave,
  onCancel,
  isLoading = false,
}) => {
  const [title, setTitle] = useState(entry?.title || '');
  const [content, setContent] = useState(entry?.content || '');
  const [entryDate, setEntryDate] = useState(
    entry?.entry_date || new Date().toISOString().split('T')[0]
  );
  const [mood, setMood] = useState<JournalEntryMood | undefined>(entry?.mood);
  const [location, setLocation] = useState(entry?.location || '');
  const [weather, setWeather] = useState(entry?.weather || '');
  const [isPrivate, setIsPrivate] = useState(entry?.is_private ?? true);
  const [tags, setTags] = useState<JournalTagCreate[]>(
    entry?.tags?.map(tag => ({ tag_name: tag.tag_name, tag_color: tag.tag_color })) || []
  );
  const [newTagName, setNewTagName] = useState('');
  const [newTagColor, setNewTagColor] = useState('#3B82F6');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      alert('Please enter some content for your journal entry.');
      return;
    }

    const entryData = {
      title: title.trim() || undefined,
      content: content.trim(),
      entry_date: entryDate,
      mood,
      location: location.trim() || undefined,
      weather: weather.trim() || undefined,
      is_private: isPrivate,
      tags: tags.length > 0 ? tags : undefined,
    };

    await onSave(entryData);
  };

  const addTag = () => {
    if (newTagName.trim() && !tags.some(tag => tag.tag_name === newTagName.trim())) {
      setTags([...tags, { tag_name: newTagName.trim(), tag_color: newTagColor }]);
      setNewTagName('');
    }
  };

  const removeTag = (tagName: string) => {
    setTags(tags.filter(tag => tag.tag_name !== tagName));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.target === e.currentTarget) {
      e.preventDefault();
      addTag();
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">
            {entry ? 'Edit Journal Entry' : 'New Journal Entry'}
          </h1>
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !content.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Saving...' : 'Save Entry'}
            </button>
          </div>
        </div>

        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              Title (Optional)
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Give your entry a title..."
            />
          </div>

          <div>
            <label htmlFor="entryDate" className="block text-sm font-medium text-gray-700">
              Entry Date
            </label>
            <input
              type="date"
              id="entryDate"
              value={entryDate}
              onChange={(e) => setEntryDate(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              required
            />
          </div>
        </div>

        {/* Mood and Context */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label htmlFor="mood" className="block text-sm font-medium text-gray-700">
              Mood
            </label>
            <select
              id="mood"
              value={mood || ''}
              onChange={(e) => setMood(e.target.value as JournalEntryMood || undefined)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">Select mood...</option>
              {moodOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700">
              Location (Optional)
            </label>
            <input
              type="text"
              id="location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Where are you?"
            />
          </div>

          <div>
            <label htmlFor="weather" className="block text-sm font-medium text-gray-700">
              Weather (Optional)
            </label>
            <input
              type="text"
              id="weather"
              value={weather}
              onChange={(e) => setWeather(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Sunny, rainy, etc..."
            />
          </div>
        </div>

        {/* Privacy Setting */}
        <div className="flex items-center">
          <input
            id="isPrivate"
            type="checkbox"
            checked={isPrivate}
            onChange={(e) => setIsPrivate(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="isPrivate" className="ml-2 block text-sm text-gray-900">
            Keep this entry private
          </label>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags
          </label>
          <div className="flex flex-wrap gap-2 mb-3">
            {tags.map((tag) => (
              <span
                key={tag.tag_name}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white"
                style={{ backgroundColor: tag.tag_color || '#3B82F6' }}
              >
                {tag.tag_name}
                <button
                  type="button"
                  onClick={() => removeTag(tag.tag_name)}
                  className="ml-1.5 inline-flex items-center justify-center w-4 h-4 text-white hover:bg-white hover:bg-opacity-20 rounded-full"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Add a tag..."
              className="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
            <input
              type="color"
              value={newTagColor}
              onChange={(e) => setNewTagColor(e.target.value)}
              className="w-12 h-8 border border-gray-300 rounded cursor-pointer"
            />
            <button
              type="button"
              onClick={addTag}
              disabled={!newTagName.trim()}
              className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add
            </button>
          </div>
        </div>

        {/* Content Editor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Content *
          </label>
          <div className="border border-gray-300 rounded-md overflow-hidden">
            <MDEditor
              value={content}
              onChange={(val) => setContent(val || '')}
              preview="edit"
              height={400}
              data-color-mode="light"
            />
          </div>
          <p className="mt-1 text-sm text-gray-500">
            Write your journal entry using Markdown for formatting.
          </p>
        </div>
      </form>
    </div>
  );
};