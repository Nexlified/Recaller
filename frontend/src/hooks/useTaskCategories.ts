import { useState, useMemo } from 'react';
import { useTasks } from './useTasks';
import { TaskCategory, CreateCategoryInput } from '../types/Task';

/**
 * Hook for managing task categories
 */
export const useTaskCategories = () => {
  const { categories, createCategory, updateCategory, deleteCategory, tasks } = useTasks();
  const [isManaging, setIsManaging] = useState(false);
  
  const getCategoryById = (id: number): TaskCategory | undefined => 
    categories.find(cat => cat.id === id);
  
  const getCategoryColor = (id: number): string => 
    getCategoryById(id)?.color || '#6B7280';
  
  const getTaskCountByCategory = (categoryId: number): number => {
    return tasks.filter(task => 
      task.categories.some(cat => cat.id === categoryId)
    ).length;
  };
  
  const createCategoryWithDefaults = async (name: string, color?: string): Promise<TaskCategory> => {
    return await createCategory({
      name,
      color: color || generateRandomColor(),
      description: '',
    });
  };
  
  // Get categories sorted by usage
  const categoriesByUsage = useMemo(() => {
    return [...categories].sort((a, b) => {
      const aCount = getTaskCountByCategory(a.id);
      const bCount = getTaskCountByCategory(b.id);
      return bCount - aCount; // Descending order
    });
  }, [categories, tasks]);
  
  // Get categories with task counts
  const categoriesWithCounts = useMemo(() => {
    return categories.map(category => ({
      ...category,
      taskCount: getTaskCountByCategory(category.id),
    }));
  }, [categories, tasks]);
  
  // Get unused categories
  const unusedCategories = useMemo(() => {
    return categories.filter(category => getTaskCountByCategory(category.id) === 0);
  }, [categories, tasks]);
  
  return {
    categories,
    categoriesByUsage,
    categoriesWithCounts,
    unusedCategories,
    isManaging,
    setIsManaging,
    getCategoryById,
    getCategoryColor,
    getTaskCountByCategory,
    createCategory: createCategoryWithDefaults,
    updateCategory,
    deleteCategory,
  };
};

/**
 * Generate a random color for categories
 */
function generateRandomColor(): string {
  const colors = [
    '#EF4444', // red
    '#F97316', // orange
    '#EAB308', // yellow
    '#22C55E', // green
    '#06B6D4', // cyan
    '#3B82F6', // blue
    '#6366F1', // indigo
    '#8B5CF6', // violet
    '#EC4899', // pink
    '#F59E0B', // amber
    '#10B981', // emerald
    '#14B8A6', // teal
    '#6366F1', // indigo
    '#8B5CF6', // violet
    '#D946EF', // fuchsia
  ];
  
  return colors[Math.floor(Math.random() * colors.length)];
}

/**
 * Hook for category selection in forms
 */
export const useCategorySelection = (initialSelectedIds: number[] = []) => {
  const { categories } = useTaskCategories();
  const [selectedCategoryIds, setSelectedCategoryIds] = useState<number[]>(initialSelectedIds);
  
  const selectedCategories = useMemo(() => {
    return categories.filter(cat => selectedCategoryIds.includes(cat.id));
  }, [categories, selectedCategoryIds]);
  
  const availableCategories = useMemo(() => {
    return categories.filter(cat => !selectedCategoryIds.includes(cat.id));
  }, [categories, selectedCategoryIds]);
  
  const toggleCategory = (categoryId: number) => {
    setSelectedCategoryIds(prev => 
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };
  
  const addCategory = (categoryId: number) => {
    setSelectedCategoryIds(prev => 
      prev.includes(categoryId) ? prev : [...prev, categoryId]
    );
  };
  
  const removeCategory = (categoryId: number) => {
    setSelectedCategoryIds(prev => prev.filter(id => id !== categoryId));
  };
  
  const clearSelection = () => {
    setSelectedCategoryIds([]);
  };
  
  const selectAll = () => {
    setSelectedCategoryIds(categories.map(cat => cat.id));
  };
  
  return {
    selectedCategoryIds,
    selectedCategories,
    availableCategories,
    setSelectedCategoryIds,
    toggleCategory,
    addCategory,
    removeCategory,
    clearSelection,
    selectAll,
    hasSelection: selectedCategoryIds.length > 0,
    isSelected: (categoryId: number) => selectedCategoryIds.includes(categoryId),
  };
};

/**
 * Hook for managing category colors
 */
export const useCategoryColors = () => {
  const predefinedColors = [
    { name: 'Red', value: '#EF4444' },
    { name: 'Orange', value: '#F97316' },
    { name: 'Yellow', value: '#EAB308' },
    { name: 'Green', value: '#22C55E' },
    { name: 'Cyan', value: '#06B6D4' },
    { name: 'Blue', value: '#3B82F6' },
    { name: 'Indigo', value: '#6366F1' },
    { name: 'Violet', value: '#8B5CF6' },
    { name: 'Pink', value: '#EC4899' },
    { name: 'Amber', value: '#F59E0B' },
    { name: 'Emerald', value: '#10B981' },
    { name: 'Teal', value: '#14B8A6' },
    { name: 'Fuchsia', value: '#D946EF' },
    { name: 'Gray', value: '#6B7280' },
    { name: 'Slate', value: '#64748B' },
  ];
  
  const getColorName = (colorValue: string): string => {
    const color = predefinedColors.find(c => c.value === colorValue);
    return color?.name || 'Custom';
  };
  
  const isValidColor = (color: string): boolean => {
    return /^#[0-9A-F]{6}$/i.test(color);
  };
  
  const getContrastColor = (backgroundColor: string): string => {
    // Convert hex to RGB
    const hex = backgroundColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    // Calculate luminance
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    
    // Return black or white based on luminance
    return luminance > 0.5 ? '#000000' : '#FFFFFF';
  };
  
  return {
    predefinedColors,
    getColorName,
    isValidColor,
    getContrastColor,
    generateRandomColor,
  };
};