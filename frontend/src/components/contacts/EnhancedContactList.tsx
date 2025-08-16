import React, { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import { Contact } from '../../services/contacts';
import contactRelationshipService from '../../services/contactRelationships';
import { ContactRelationship } from '../../types/ContactRelationship';

interface EnhancedContactListProps {
  contacts: Contact[];
  currentUserId?: number;
  isOwner: boolean;
  title: string;
  loadingContacts: boolean;
  onEdit?: (contact: Contact) => void;
  onDelete?: (contact: Contact) => void;
  onVisibilityChange?: (contact: Contact, visibility: string) => void;
}

interface ContactWithRelationships extends Contact {
  relationshipCount: number;
  relationshipCategories: string[];
  recentRelationships: ContactRelationship[];
}

type ViewMode = 'list' | 'grid' | 'family' | 'professional';
type FilterType = 'all' | 'family' | 'professional' | 'social' | 'romantic' | 'no-relationships';
type SortType = 'name' | 'recent' | 'relationships' | 'company';

export const EnhancedContactList: React.FC<EnhancedContactListProps> = ({
  contacts,
  currentUserId,
  isOwner,
  title,
  loadingContacts,
  onEdit,
  onDelete,
  onVisibilityChange
}) => {
  const [contactsWithRelationships, setContactsWithRelationships] = useState<ContactWithRelationships[]>([]);
  const [isLoadingRelationships, setIsLoadingRelationships] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [sortType, setSortType] = useState<SortType>('name');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadRelationshipData();
  }, [contacts]);

  const loadRelationshipData = async () => {
    if (contacts.length === 0) return;

    setIsLoadingRelationships(true);
    try {
      const contactsWithRelData: ContactWithRelationships[] = await Promise.all(
        contacts.map(async (contact) => {
          try {
            const relationships = await contactRelationshipService.getContactRelationships(contact.id);
            const categories = [...new Set(relationships.map(rel => rel.relationship_category))];
            
            return {
              ...contact,
              relationshipCount: relationships.length,
              relationshipCategories: categories,
              recentRelationships: relationships.slice(0, 3) // Get 3 most recent
            };
          } catch (error) {
            console.error(`Error loading relationships for contact ${contact.id}:`, error);
            return {
              ...contact,
              relationshipCount: 0,
              relationshipCategories: [],
              recentRelationships: []
            };
          }
        })
      );

      setContactsWithRelationships(contactsWithRelData);
    } catch (error) {
      console.error('Error loading relationship data:', error);
    } finally {
      setIsLoadingRelationships(false);
    }
  };

  const filteredAndSortedContacts = useMemo(() => {
    let filtered = contactsWithRelationships;

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(contact =>
        `${contact.first_name} ${contact.last_name}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contact.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contact.company?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply relationship filter
    if (filterType !== 'all') {
      if (filterType === 'no-relationships') {
        filtered = filtered.filter(contact => contact.relationshipCount === 0);
      } else {
        filtered = filtered.filter(contact => 
          contact.relationshipCategories.includes(filterType)
        );
      }
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortType) {
        case 'name':
          return `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`);
        case 'relationships':
          return b.relationshipCount - a.relationshipCount;
        case 'company':
          return (a.company || '').localeCompare(b.company || '');
        case 'recent':
        default:
          return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
      }
    });

    return filtered;
  }, [contactsWithRelationships, searchQuery, filterType, sortType]);

  const groupedContacts = useMemo(() => {
    if (viewMode === 'family') {
      const groups = new Map<string, ContactWithRelationships[]>();
      
      filteredAndSortedContacts.forEach(contact => {
        const familyMembers = contact.recentRelationships.filter(rel => 
          rel.relationship_category === 'family'
        );
        
        if (familyMembers.length > 0) {
          // Group by last name as a simple family grouping
          const familyName = contact.last_name || 'Unknown Family';
          if (!groups.has(familyName)) {
            groups.set(familyName, []);
          }
          groups.get(familyName)?.push(contact);
        } else {
          // Individual contacts without family relationships
          const key = 'Individual Contacts';
          if (!groups.has(key)) {
            groups.set(key, []);
          }
          groups.get(key)?.push(contact);
        }
      });
      
      return groups;
    } else if (viewMode === 'professional') {
      const groups = new Map<string, ContactWithRelationships[]>();
      
      filteredAndSortedContacts.forEach(contact => {
        const company = contact.company || 'Unknown Company';
        if (!groups.has(company)) {
          groups.set(company, []);
        }
        groups.get(company)?.push(contact);
      });
      
      return groups;
    }
    
    return new Map([['All Contacts', filteredAndSortedContacts]]);
  }, [filteredAndSortedContacts, viewMode]);

  const getCategoryIcon = (category: string) => {
    const icons = {
      family: '👨‍👩‍👧‍👦',
      professional: '💼',
      social: '🤝',
      romantic: '💕'
    };
    return icons[category as keyof typeof icons] || '👤';
  };

  const renderContactCard = (contact: ContactWithRelationships) => {
    return (
      <div
        key={contact.id}
        className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow duration-200"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3 flex-1">
            <div className="flex-shrink-0">
              <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-lg">
                  {contact.first_name.charAt(0)}{contact.last_name?.charAt(0) || ''}
                </span>
              </div>
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                <Link
                  href={`/contacts/${contact.id}`}
                  className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  {contact.first_name} {contact.last_name}
                </Link>
              </div>
              
              {contact.job_title && (
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {contact.job_title}
                  {contact.company && ` at ${contact.company}`}
                </div>
              )}
              
              {contact.email && (
                <div className="text-sm text-gray-500 dark:text-gray-500">
                  {contact.email}
                </div>
              )}
            </div>
          </div>
          
          {/* Relationship indicators */}
          <div className="flex flex-col items-end space-y-2">
            {contact.relationshipCount > 0 && (
              <div className="flex items-center space-x-1">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {contact.relationshipCount}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-500">
                  relationship{contact.relationshipCount !== 1 ? 's' : ''}
                </span>
              </div>
            )}
            
            <div className="flex items-center space-x-1">
              {contact.relationshipCategories.slice(0, 3).map(category => (
                <span
                  key={category}
                  className="text-lg"
                  title={category}
                >
                  {getCategoryIcon(category)}
                </span>
              ))}
              {contact.relationshipCategories.length > 3 && (
                <span className="text-xs text-gray-500 dark:text-gray-500">
                  +{contact.relationshipCategories.length - 3}
                </span>
              )}
            </div>
          </div>
        </div>
        
        {/* Quick actions */}
        {isOwner && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <Link
              href={`/contacts/${contact.id}`}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              View Details →
            </Link>
            
            <div className="flex items-center space-x-2">
              {onEdit && (
                <button
                  onClick={() => onEdit(contact)}
                  className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
                >
                  Edit
                </button>
              )}
              {onDelete && (
                <button
                  onClick={() => onDelete(contact)}
                  className="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                >
                  Delete
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderContactRow = (contact: ContactWithRelationships) => {
    return (
      <tr key={contact.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="flex items-center">
            <div className="flex-shrink-0 h-10 w-10">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {contact.first_name.charAt(0)}{contact.last_name?.charAt(0) || ''}
                </span>
              </div>
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                <Link
                  href={`/contacts/${contact.id}`}
                  className="hover:text-blue-600 dark:hover:text-blue-400"
                >
                  {contact.first_name} {contact.last_name}
                </Link>
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {contact.email}
              </div>
            </div>
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
          {contact.job_title || '-'}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
          {contact.company || '-'}
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {contact.relationshipCount}
            </span>
            <div className="flex items-center space-x-1">
              {contact.relationshipCategories.slice(0, 2).map(category => (
                <span key={category} className="text-sm" title={category}>
                  {getCategoryIcon(category)}
                </span>
              ))}
            </div>
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <div className="flex items-center justify-end space-x-2">
            <Link
              href={`/contacts/${contact.id}`}
              className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
            >
              View
            </Link>
            {isOwner && onEdit && (
              <button
                onClick={() => onEdit(contact)}
                className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
              >
                Edit
              </button>
            )}
            {isOwner && onDelete && (
              <button
                onClick={() => onDelete(contact)}
                className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
              >
                Delete
              </button>
            )}
          </div>
        </td>
      </tr>
    );
  };

  if (loadingContacts || isLoadingRelationships) {
    return (
      <div className="text-center py-8">
        <div className="text-lg text-gray-600 dark:text-gray-400">
          Loading {title.toLowerCase()}...
        </div>
      </div>
    );
  }

  if (contacts.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500 dark:text-gray-400">
          No {title.toLowerCase()} found.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <input
              type="text"
              placeholder="Search contacts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Filter */}
          <div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as FilterType)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Relationships</option>
              <option value="family">👨‍👩‍👧‍👦 Family</option>
              <option value="professional">💼 Professional</option>
              <option value="social">🤝 Social</option>
              <option value="romantic">💕 Romantic</option>
              <option value="no-relationships">No Relationships</option>
            </select>
          </div>

          {/* Sort */}
          <div>
            <select
              value={sortType}
              onChange={(e) => setSortType(e.target.value as SortType)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="name">Sort by Name</option>
              <option value="relationships">Sort by Relationships</option>
              <option value="company">Sort by Company</option>
              <option value="recent">Sort by Recent</option>
            </select>
          </div>

          {/* View Mode */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md ${viewMode === 'list' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/20' : 'text-gray-600 dark:text-gray-400'}`}
              title="List View"
            >
              📝
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/20' : 'text-gray-600 dark:text-gray-400'}`}
              title="Grid View"
            >
              📊
            </button>
            <button
              onClick={() => setViewMode('family')}
              className={`p-2 rounded-md ${viewMode === 'family' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/20' : 'text-gray-600 dark:text-gray-400'}`}
              title="Family Groups"
            >
              👨‍👩‍👧‍👦
            </button>
            <button
              onClick={() => setViewMode('professional')}
              className={`p-2 rounded-md ${viewMode === 'professional' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/20' : 'text-gray-600 dark:text-gray-400'}`}
              title="Company Groups"
            >
              🏢
            </button>
          </div>
        </div>
      </div>

      {/* Results summary */}
      <div className="text-sm text-gray-600 dark:text-gray-400">
        Showing {filteredAndSortedContacts.length} of {contactsWithRelationships.length} contacts
      </div>

      {/* Content */}
      {viewMode === 'list' ? (
        // Table view
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Job Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Relationships
                </th>
                <th className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredAndSortedContacts.map(renderContactRow)}
            </tbody>
          </table>
        </div>
      ) : viewMode === 'grid' ? (
        // Grid view
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAndSortedContacts.map(renderContactCard)}
        </div>
      ) : (
        // Grouped views (family/professional)
        <div className="space-y-6">
          {Array.from(groupedContacts.entries()).map(([groupName, groupContacts]) => (
            <div key={groupName} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-6 py-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  {groupName} ({groupContacts.length})
                </h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {groupContacts.map(renderContactCard)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EnhancedContactList;