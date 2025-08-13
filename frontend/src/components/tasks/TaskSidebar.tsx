'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string | number;
}

// Icon Components
const HomeIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
  </svg>
);

const ListBulletIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
  </svg>
);

const PlusIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const TagIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
  </svg>
);

const ArrowPathIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

const CalendarDaysIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
);

const ViewColumnsIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2H9a2 2 0 00-2 2v10z" />
  </svg>
);

// Navigation Item Component
const NavigationItem: React.FC<NavigationItem> = ({ name, href, icon: Icon, badge }) => {
  const pathname = usePathname();
  const isActive = pathname === href || (href !== '/tasks' && pathname?.startsWith(href));

  return (
    <li>
      <Link
        href={href}
        className={`group flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
          isActive
            ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-400'
            : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700'
        }`}
      >
        <Icon
          className={`mr-3 h-5 w-5 flex-shrink-0 ${
            isActive
              ? 'text-indigo-500 dark:text-indigo-400'
              : 'text-gray-400 group-hover:text-gray-500 dark:text-gray-400 dark:group-hover:text-gray-300'
          }`}
        />
        <span className="flex-1">{name}</span>
        {badge && (
          <span className={`ml-2 inline-block py-0.5 px-2 text-xs rounded-full ${
            isActive
              ? 'bg-indigo-200 text-indigo-800 dark:bg-indigo-800 dark:text-indigo-200'
              : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
          }`}>
            {badge}
          </span>
        )}
      </Link>
    </li>
  );
};

// Sidebar Section Component
const SidebarSection: React.FC<{
  title: string;
  children: React.ReactNode;
}> = ({ title, children }) => (
  <div className="mb-6">
    <h3 className="px-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
      {title}
    </h3>
    <ul className="space-y-1">
      {children}
    </ul>
  </div>
);

// Main TaskSidebar Component
export const TaskSidebar: React.FC<{ 
  className?: string;
  taskCounts?: {
    total: number;
    pending: number;
    inProgress: number;
    completed: number;
    overdue: number;
    recurring: number;
  };
  categoryCounts?: Array<{
    id: number;
    name: string;
    count: number;
    color?: string;
  }>;
}> = ({ 
  className = '',
  taskCounts = {
    total: 0,
    pending: 0,
    inProgress: 0,
    completed: 0,
    overdue: 0,
    recurring: 0,
  },
  categoryCounts = []
}) => {
  const taskNavigation: NavigationItem[] = [
    { name: 'Dashboard', href: '/tasks', icon: HomeIcon },
    { name: 'All Tasks', href: '/tasks/list', icon: ListBulletIcon, badge: taskCounts.total || undefined },
    { name: 'Create Task', href: '/tasks/create', icon: PlusIcon },
    { name: 'Categories', href: '/tasks/categories', icon: TagIcon },
    { name: 'Recurring', href: '/tasks/recurring', icon: ArrowPathIcon, badge: taskCounts.recurring || undefined },
    { name: 'Calendar', href: '/tasks/calendar', icon: CalendarDaysIcon },
    { name: 'Board', href: '/tasks/board', icon: ViewColumnsIcon },
  ];

  const statusNavigation: NavigationItem[] = [
    { name: 'Pending', href: '/tasks/list?status=pending', icon: ListBulletIcon, badge: taskCounts.pending || undefined },
    { name: 'In Progress', href: '/tasks/list?status=in_progress', icon: ListBulletIcon, badge: taskCounts.inProgress || undefined },
    { name: 'Completed', href: '/tasks/list?status=completed', icon: ListBulletIcon, badge: taskCounts.completed || undefined },
  ];

  return (
    <nav className={`w-64 bg-white dark:bg-gray-800 shadow-sm border-r border-gray-200 dark:border-gray-700 flex-shrink-0 ${className}`}>
      <div className="h-full flex flex-col">
        {/* Sidebar Header */}
        <div className="flex items-center h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Tasks</h2>
        </div>

        {/* Sidebar Content */}
        <div className="flex-1 overflow-y-auto py-4">
          {/* Main Navigation */}
          <SidebarSection title="Navigation">
            {taskNavigation.map((item) => (
              <NavigationItem key={item.name} {...item} />
            ))}
          </SidebarSection>

          {/* Status Filters */}
          <SidebarSection title="By Status">
            {statusNavigation.map((item) => (
              <NavigationItem key={item.name} {...item} />
            ))}
          </SidebarSection>

          {/* Overdue Tasks */}
          {taskCounts.overdue > 0 && (
            <SidebarSection title="Alerts">
              <NavigationItem
                name="Overdue"
                href="/tasks/list?overdue=true"
                icon={({ className }) => (
                  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
                badge={taskCounts.overdue}
              />
            </SidebarSection>
          )}

          {/* Categories */}
          {categoryCounts.length > 0 && (
            <SidebarSection title="Categories">
              {categoryCounts.slice(0, 5).map((category) => (
                <li key={category.id}>
                  <Link
                    href={`/tasks/list?category=${category.id}`}
                    className="group flex items-center px-4 py-2 text-sm font-medium rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700 transition-colors"
                  >
                    <span
                      className="mr-3 h-3 w-3 flex-shrink-0 rounded-full"
                      style={{ backgroundColor: category.color || '#6B7280' }}
                    />
                    <span className="flex-1 truncate">{category.name}</span>
                    <span className="ml-2 inline-block py-0.5 px-2 text-xs rounded-full bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                      {category.count}
                    </span>
                  </Link>
                </li>
              ))}
              {categoryCounts.length > 5 && (
                <li>
                  <Link
                    href="/tasks/categories"
                    className="group flex items-center px-4 py-2 text-sm font-medium rounded-md text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 dark:text-indigo-400 dark:hover:text-indigo-300 dark:hover:bg-indigo-900/20 transition-colors"
                  >
                    <span className="text-center flex-1">
                      View all {categoryCounts.length} categories
                    </span>
                  </Link>
                </li>
              )}
            </SidebarSection>
          )}
        </div>

        {/* Sidebar Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
            <div className="flex justify-between">
              <span>Total Tasks:</span>
              <span className="font-medium">{taskCounts.total}</span>
            </div>
            <div className="flex justify-between">
              <span>Completed:</span>
              <span className="font-medium text-green-600 dark:text-green-400">{taskCounts.completed}</span>
            </div>
            {taskCounts.overdue > 0 && (
              <div className="flex justify-between">
                <span>Overdue:</span>
                <span className="font-medium text-red-600 dark:text-red-400">{taskCounts.overdue}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};