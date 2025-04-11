import { useState, useEffect, useMemo } from 'react';

import type { Task } from '@/app/types/task';

export const useTaskSearch = (tasks: Task[]) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Task[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  const searchTasks = useMemo(() => {
    if (!searchQuery.trim()) return tasks;

    const query = searchQuery.toLowerCase();
    return tasks.filter(task => {
      const titleMatch = task.title.toLowerCase().includes(query);
      const descriptionMatch = task.description?.toLowerCase().includes(query);
      return titleMatch || descriptionMatch;
    });
  }, [tasks, searchQuery]);

  useEffect(() => {
    setSearchResults(searchTasks);
  }, [searchTasks]);

  const addToRecentSearches = (query: string) => {
    if (!query.trim()) return;
    setRecentSearches(prev => {
      const updated = [query, ...prev.filter(q => q !== query)].slice(0, 5);
      return updated;
    });
  };

  const clearRecentSearches = () => {
    setRecentSearches([]);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      addToRecentSearches(query);
    }
  };

  return {
    searchQuery,
    searchResults,
    recentSearches,
    handleSearch,
    clearRecentSearches,
  };
};
