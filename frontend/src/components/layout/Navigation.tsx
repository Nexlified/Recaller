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

const UsersIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
  </svg>
);

const CalendarIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
);

const CheckSquareIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const BuildingOfficeIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
  </svg>
);

const ChartBarIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

const ActivityIcon = ({ className = '' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
  </svg>
);

// Navigation Item Component
const NavigationItem: React.FC<NavigationItem> = ({ name, href, icon: Icon, badge }) => {
  const pathname = usePathname();
  const isActive = pathname === href || pathname?.startsWith(href + '/');

  return (
    <Link
      href={href}
      className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
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
  );
};

// Main Navigation Component
export const Navigation: React.FC<{
  className?: string;
  taskCount?: number;
  contactCount?: number;
  eventCount?: number;
  organizationCount?: number;
  activityCount?: number;
}> = ({ 
  className = '',
  taskCount,
  contactCount,
  eventCount,
  organizationCount,
  activityCount
}) => {
  const mainNavigation: NavigationItem[] = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Contacts', href: '/contacts', icon: UsersIcon, badge: contactCount },
    { name: 'Activities', href: '/activities', icon: ActivityIcon, badge: activityCount },
    { name: 'Events', href: '/events', icon: CalendarIcon, badge: eventCount },
    { name: 'Tasks', href: '/tasks', icon: CheckSquareIcon, badge: taskCount },
    { name: 'Organizations', href: '/organizations', icon: BuildingOfficeIcon, badge: organizationCount },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  ];

  return (
    <nav className={`space-y-1 ${className}`}>
      {mainNavigation.map((item) => (
        <NavigationItem key={item.name} {...item} />
      ))}
    </nav>
  );
};

// Sidebar Navigation Component (for use in app layout)
export const SidebarNavigation: React.FC<{
  className?: string;
  taskCount?: number;
  contactCount?: number;
  eventCount?: number;
  organizationCount?: number;
  activityCount?: number;
}> = ({ 
  className = '',
  taskCount,
  contactCount,
  eventCount,
  organizationCount,
  activityCount
}) => {
  const pathname = usePathname();
  const isTasksSection = pathname?.startsWith('/tasks');

  // Don't show main navigation in tasks section as it has its own sidebar
  if (isTasksSection) {
    return null;
  }

  return (
    <div className={`w-64 bg-white dark:bg-gray-800 shadow-sm border-r border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="h-full flex flex-col">
        {/* Navigation Header */}
        <div className="flex items-center h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          <Link href="/" className="text-xl font-bold text-gray-900 dark:text-white">
            Recaller
          </Link>
        </div>

        {/* Navigation Content */}
        <div className="flex-1 overflow-y-auto py-4 px-3">
          <Navigation
            taskCount={taskCount}
            contactCount={contactCount}
            eventCount={eventCount}
            organizationCount={organizationCount}
            activityCount={activityCount}
          />
        </div>

        {/* Navigation Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            <p>Recaller v1.0.0</p>
            <p>Privacy-first personal assistant</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Mobile Navigation Component
export const MobileNavigation: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  taskCount?: number;
  contactCount?: number;
  eventCount?: number;
  organizationCount?: number;
  activityCount?: number;
}> = ({ 
  isOpen, 
  onClose,
  taskCount,
  contactCount,
  eventCount,
  organizationCount,
  activityCount
}) => {
  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Mobile menu */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out lg:hidden
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
            <Link href="/" className="text-xl font-bold text-gray-900 dark:text-white">
              Recaller
            </Link>
            <button
              onClick={onClose}
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Navigation */}
          <div className="flex-1 overflow-y-auto py-4 px-3">
            <Navigation
              taskCount={taskCount}
              contactCount={contactCount}
              eventCount={eventCount}
              organizationCount={organizationCount}
              activityCount={activityCount}
            />
          </div>
        </div>
      </div>
    </>
  );
};