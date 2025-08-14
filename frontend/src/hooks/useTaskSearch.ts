import { useState, useEffect, useMemo, useCallback } from 'react';
import { useTasks } from './useTasks';
import { Task } from '../types/Task';

/**
 * Hook for task search functionality with debouncing
 */
export const useTaskSearch = () => {
  const { tasks } = useTasks();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Task[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  
  // Debounced search function
  const debouncedSearch = useMemo(
    () => {
      const searchFn = (query: string) => {
        setIsSearching(true);
        const results = searchTasks(tasks, query);
        setSearchResults(results);
        setIsSearching(false);
      };
      return debounce(searchFn, 300);
    },
    [tasks]
  );
  
  useEffect(() => {
    if (searchQuery.trim()) {
      debouncedSearch(searchQuery);
    } else {
      setSearchResults([]);
      setIsSearching(false);
    }
    
    // Cleanup on unmount
    return () => {
      debouncedSearch.cancel?.();
    };
  }, [searchQuery, debouncedSearch]);
  
  const clearSearch = useCallback(() => {
    setSearchQuery('');
    setSearchResults([]);
    setIsSearching(false);
  }, []);
  
  return {
    searchQuery,
    setSearchQuery,
    searchResults,
    isSearching,
    clearSearch,
    hasResults: searchResults.length > 0,
    hasQuery: searchQuery.trim().length > 0,
  };
};

/**
 * Search tasks by query string
 */
function searchTasks(tasks: Task[], query: string): Task[] {
  if (!query.trim()) return [];
  
  const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
  
  return tasks.filter(task => {
    const searchableContent = [
      task.title,
      task.description || '',
      ...task.categories.map(cat => cat.name),
      ...task.contacts.map(contact => `${contact.first_name} ${contact.last_name}`),
      task.status,
      task.priority,
    ].join(' ').toLowerCase();
    
    // All search terms must be found in the content
    return searchTerms.every(term => searchableContent.includes(term));
  }).sort((a, b) => {
    // Sort by relevance (title matches first)
    const aTitle = a.title.toLowerCase();
    const bTitle = b.title.toLowerCase();
    const queryLower = query.toLowerCase();
    
    const aStartsWithQuery = aTitle.startsWith(queryLower);
    const bStartsWithQuery = bTitle.startsWith(queryLower);
    
    if (aStartsWithQuery && !bStartsWithQuery) return -1;
    if (!aStartsWithQuery && bStartsWithQuery) return 1;
    
    const aIncludesQuery = aTitle.includes(queryLower);
    const bIncludesQuery = bTitle.includes(queryLower);
    
    if (aIncludesQuery && !bIncludesQuery) return -1;
    if (!aIncludesQuery && bIncludesQuery) return 1;
    
    // Sort by creation date (newest first) if equal relevance
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
}

/**
 * Debounce function with proper typing
 */
function debounce(func: (query: string) => void, delay: number) {
  let timeoutId: NodeJS.Timeout;
  
  const debouncedFunction = (query: string) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(query), delay);
  };
  
  debouncedFunction.cancel = () => {
    clearTimeout(timeoutId);
  };
  
  return debouncedFunction;
}

/**
 * Hook for advanced task search with filters
 */
export const useAdvancedTaskSearch = () => {
  const { tasks } = useTasks();
  const [searchConfig, setSearchConfig] = useState({
    query: '',
    includeCategories: true,
    includeContacts: true,
    includeDescription: true,
    caseSensitive: false,
    exactMatch: false,
  });
  const [searchResults, setSearchResults] = useState<Task[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  
  const performSearch = useCallback(() => {
    if (!searchConfig.query.trim()) {
      setSearchResults([]);
      return;
    }
    
    setIsSearching(true);
    
    const results = tasks.filter(task => {
      const { query, includeCategories, includeContacts, includeDescription, caseSensitive, exactMatch } = searchConfig;
      
      let searchableContent = task.title;
      
      if (includeDescription && task.description) {
        searchableContent += ' ' + task.description;
      }
      
      if (includeCategories) {
        searchableContent += ' ' + task.categories.map(cat => cat.name).join(' ');
      }
      
      if (includeContacts) {
        searchableContent += ' ' + task.contacts.map(contact => `${contact.first_name} ${contact.last_name}`).join(' ');
      }
      
      const content = caseSensitive ? searchableContent : searchableContent.toLowerCase();
      const searchQuery = caseSensitive ? query : query.toLowerCase();
      
      if (exactMatch) {
        return content.includes(searchQuery);
      } else {
        const searchTerms = searchQuery.split(' ').filter(term => term.length > 0);
        return searchTerms.every(term => content.includes(term));
      }
    });
    
    setSearchResults(results);
    setIsSearching(false);
  }, [tasks, searchConfig]);
  
  useEffect(() => {
    const timeoutId = setTimeout(performSearch, 300);
    return () => clearTimeout(timeoutId);
  }, [performSearch]);
  
  const updateSearchConfig = useCallback((updates: Partial<typeof searchConfig>) => {
    setSearchConfig(prev => ({ ...prev, ...updates }));
  }, []);
  
  const clearSearch = useCallback(() => {
    setSearchConfig(prev => ({ ...prev, query: '' }));
    setSearchResults([]);
  }, []);
  
  return {
    searchConfig,
    updateSearchConfig,
    searchResults,
    isSearching,
    clearSearch,
    hasResults: searchResults.length > 0,
    hasQuery: searchConfig.query.trim().length > 0,
  };
};