'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import authService from '@/services/auth';
import tasksService from '@/services/tasks';
import { Task, TaskCategory } from '@/types/Task';
import type { User } from '@/services/auth';

// Calendar Day Component
const CalendarDay = ({ 
  date, 
  tasks, 
  isToday, 
  isCurrentMonth, 
  onTaskClick 
}: {
  date: Date;
  tasks: Task[];
  isToday: boolean;
  isCurrentMonth: boolean;
  onTaskClick: (task: Task) => void;
}) => {
  const dayTasks = tasks.filter(task => {
    if (!task.due_date) return false;
    const taskDate = new Date(task.due_date);
    return taskDate.toDateString() === date.toDateString();
  });

  return (
    <div className={`min-h-[120px] border border-gray-200 dark:border-gray-700 p-2 ${
      !isCurrentMonth ? 'bg-gray-50 dark:bg-gray-800/50' : 'bg-white dark:bg-gray-800'
    } ${isToday ? 'ring-2 ring-indigo-500' : ''}`}>
      <div className={`text-sm font-medium mb-2 ${
        isToday ? 'text-indigo-600 dark:text-indigo-400' : 
        !isCurrentMonth ? 'text-gray-400 dark:text-gray-600' : 
        'text-gray-900 dark:text-white'
      }`}>
        {date.getDate()}
      </div>
      
      <div className="space-y-1">
        {dayTasks.slice(0, 3).map(task => (
          <button
            key={task.id}
            onClick={() => onTaskClick(task)}
            className={`w-full text-left p-1 rounded text-xs truncate ${
              task.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400' :
              task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
              'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
            } hover:opacity-80`}
            title={task.title}
          >
            {task.title}
          </button>
        ))}
        
        {dayTasks.length > 3 && (
          <div className="text-xs text-gray-500 dark:text-gray-400">
            +{dayTasks.length - 3} more
          </div>
        )}
      </div>
    </div>
  );
};

// Calendar Month View Component
const CalendarMonthView = ({ 
  currentDate, 
  tasks, 
  onTaskClick 
}: {
  currentDate: Date;
  tasks: Task[];
  onTaskClick: (task: Task) => void;
}) => {
  const today = new Date();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
  const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
  const firstDayOfWeek = firstDayOfMonth.getDay();
  const daysInMonth = lastDayOfMonth.getDate();

  // Generate calendar days (including previous/next month days for full weeks)
  const calendarDays: Date[] = [];
  
  // Add days from previous month
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(firstDayOfMonth);
    date.setDate(date.getDate() - (i + 1));
    calendarDays.push(date);
  }
  
  // Add days from current month
  for (let day = 1; day <= daysInMonth; day++) {
    calendarDays.push(new Date(currentDate.getFullYear(), currentDate.getMonth(), day));
  }
  
  // Add days from next month to complete the grid
  const remainingCells = 42 - calendarDays.length; // 6 weeks * 7 days
  for (let day = 1; day <= remainingCells; day++) {
    const date = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, day);
    calendarDays.push(date);
  }

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      {/* Weekday Headers */}
      <div className="grid grid-cols-7 bg-gray-50 dark:bg-gray-700">
        {weekDays.map(day => (
          <div key={day} className="px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 text-center">
            {day}
          </div>
        ))}
      </div>
      
      {/* Calendar Days */}
      <div className="grid grid-cols-7">
        {calendarDays.map((date, index) => (
          <CalendarDay
            key={index}
            date={date}
            tasks={tasks}
            isToday={date.toDateString() === today.toDateString()}
            isCurrentMonth={date.getMonth() === currentDate.getMonth()}
            onTaskClick={onTaskClick}
          />
        ))}
      </div>
    </div>
  );
};

// Task Detail Modal Component
const TaskDetailModal = ({ 
  task, 
  onClose 
}: {
  task: Task | null;
  onClose: () => void;
}) => {
  if (!task) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg max-w-md w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">{task.title}</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Task Details */}
          <div className="space-y-4">
            {task.description && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">{task.description}</p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</h4>
                <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                  task.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' :
                  task.status === 'in_progress' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400' :
                  'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
                }`}>
                  {task.status.replace('_', ' ')}
                </span>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</h4>
                <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                  task.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400' :
                  task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
                  'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                }`}>
                  {task.priority}
                </span>
              </div>
            </div>

            {task.due_date && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Due Date</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {new Date(task.due_date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
            )}

            {task.categories && task.categories.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Categories</h4>
                <div className="flex flex-wrap gap-1">
                  {task.categories.map(category => (
                    <span
                      key={category.id}
                      className="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
                      style={{
                        backgroundColor: category.color ? `${category.color}20` : '#6B728020',
                        color: category.color || '#6B7280'
                      }}
                    >
                      {category.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t dark:border-gray-700">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              Close
            </button>
            <Link
              href={`/tasks/${task.id}`}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700"
            >
              View Details
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

// Calendar Filters Component
const CalendarFilters = ({ 
  categories, 
  selectedCategories, 
  onCategoryChange,
  showCompletedTasks,
  onShowCompletedChange 
}: {
  categories: TaskCategory[];
  selectedCategories: number[];
  onCategoryChange: (categoryIds: number[]) => void;
  showCompletedTasks: boolean;
  onShowCompletedChange: (show: boolean) => void;
}) => {
  const toggleCategory = (categoryId: number) => {
    if (selectedCategories.includes(categoryId)) {
      onCategoryChange(selectedCategories.filter(id => id !== categoryId));
    } else {
      onCategoryChange([...selectedCategories, categoryId]);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
      <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Filter Tasks</h3>
      
      <div className="space-y-4">
        {/* Show Completed Toggle */}
        <div className="flex items-center">
          <input
            id="show-completed"
            type="checkbox"
            checked={showCompletedTasks}
            onChange={(e) => onShowCompletedChange(e.target.checked)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 dark:border-gray-600 rounded"
          />
          <label htmlFor="show-completed" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Show completed tasks
          </label>
        </div>

        {/* Category Filters */}
        {categories.length > 0 && (
          <div>
            <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">Categories</h4>
            <div className="flex flex-wrap gap-2">
              {categories.map(category => (
                <button
                  key={category.id}
                  onClick={() => toggleCategory(category.id)}
                  className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${
                    selectedCategories.includes(category.id)
                      ? 'border-transparent text-white'
                      : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700'
                  }`}
                  style={selectedCategories.includes(category.id) ? {
                    backgroundColor: category.color || '#6B7280'
                  } : {}}
                >
                  <span
                    className="w-2 h-2 rounded-full mr-2"
                    style={{ backgroundColor: category.color || '#6B7280' }}
                  ></span>
                  {category.name}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default function TaskCalendarPage() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<TaskCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [showCompletedTasks, setShowCompletedTasks] = useState(false);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      window.location.href = '/login';
      return;
    }
    setUser(currentUser);
    loadTaskData();
  }, []);

  useEffect(() => {
    // Apply filters
    let filtered = tasks;
    
    if (!showCompletedTasks) {
      filtered = filtered.filter(task => task.status !== 'completed');
    }
    
    if (selectedCategories.length > 0) {
      filtered = filtered.filter(task => 
        task.categories?.some(cat => selectedCategories.includes(cat.id))
      );
    }
    
    setFilteredTasks(filtered);
  }, [tasks, selectedCategories, showCompletedTasks]);

  const loadTaskData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [tasksData, categoriesData] = await Promise.all([
        tasksService.getTasks(0, 1000), // Get all tasks
        tasksService.getCategories()
      ]);
      
      // Filter tasks that have due dates
      const tasksWithDueDates = tasksData.filter(task => task.due_date);
      
      setTasks(tasksWithDueDates);
      setCategories(categoriesData);
    } catch (err) {
      console.error('Error loading calendar data:', err);
      setError('Failed to load calendar data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    window.location.href = '/login';
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-lg text-gray-600 dark:text-gray-400">Redirecting to login...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} title="Task Calendar" onLogout={handleLogout} />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Breadcrumb Navigation */}
          <nav className="flex mb-6" aria-label="Breadcrumb">
            <ol className="inline-flex items-center space-x-1 md:space-x-3">
              <li className="inline-flex items-center">
                <Link
                  href="/tasks"
                  className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
                >
                  Tasks
                </Link>
              </li>
              <li>
                <div className="flex items-center">
                  <svg
                    className="w-6 h-6 text-gray-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="ml-1 text-gray-500 dark:text-gray-400">Calendar</span>
                </div>
              </li>
            </ol>
          </nav>

          {/* Calendar Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
              </h1>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => navigateMonth('prev')}
                  className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button
                  onClick={() => navigateMonth('next')}
                  className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="mt-4 sm:mt-0 flex items-center space-x-3">
              <button
                onClick={goToToday}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Today
              </button>
              <Link 
                href="/tasks/create"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Task
              </Link>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Filters */}
          <CalendarFilters
            categories={categories}
            selectedCategories={selectedCategories}
            onCategoryChange={setSelectedCategories}
            showCompletedTasks={showCompletedTasks}
            onShowCompletedChange={setShowCompletedTasks}
          />

          {loading ? (
            <div className="animate-pulse">
              <div className="bg-gray-200 dark:bg-gray-700 rounded-lg h-96"></div>
            </div>
          ) : (
            <>
              {/* Calendar View */}
              <CalendarMonthView
                currentDate={currentDate}
                tasks={filteredTasks}
                onTaskClick={setSelectedTask}
              />

              {/* Task Summary */}
              {filteredTasks.length > 0 && (
                <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    Tasks for {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {filteredTasks.filter(t => t.status !== 'completed').length}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Pending Tasks</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {filteredTasks.filter(t => t.status === 'completed').length}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Completed Tasks</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                        {filteredTasks.filter(t => 
                          t.due_date && new Date(t.due_date) < new Date() && t.status !== 'completed'
                        ).length}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Overdue Tasks</div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {/* Task Detail Modal */}
          <TaskDetailModal
            task={selectedTask}
            onClose={() => setSelectedTask(null)}
          />
        </div>
      </main>
    </div>
  );
}

// Metadata handled by document head