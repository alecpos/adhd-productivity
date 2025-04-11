import { useState, useMemo } from 'react';

import type { Task } from '../app/types/task';

type FilterType = 'All' | 'Completed' | 'Pending';
type SortField = 'due_date' | 'urgency' | 'impact' | 'effort';
type SortOrder = 'asc' | 'desc';

export const useTaskFilters = (tasks: Task[]) => {
  const [filter, setFilter] = useState<FilterType>('All');
  const [sortField, setSortField] = useState<SortField>('due_date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      if (filter === 'Completed') return task.completed;
      if (filter === 'Pending') return !task.completed;
      return true;
    });
  }, [tasks, filter]);

  const sortedTasks = useMemo(() => {
    return [...filteredTasks].sort((a, b) => {
      let comparison = 0;

      switch (sortField) {
        case 'due_date':
          comparison = new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
          break;
        case 'urgency':
          comparison = (a.urgency || 0) - (b.urgency || 0);
          break;
        case 'impact':
          comparison = (a.impact || 0) - (b.impact || 0);
          break;
        case 'effort':
          comparison = (a.effort || 0) - (b.effort || 0);
          break;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });
  }, [filteredTasks, sortField, sortOrder]);

  const toggleSortOrder = () => {
    setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
  };

  return {
    filter,
    setFilter,
    sortField,
    setSortField,
    sortOrder,
    toggleSortOrder,
    sortedTasks,
  };
};
