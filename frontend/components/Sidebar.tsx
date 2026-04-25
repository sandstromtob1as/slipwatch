'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import {
  Warning,
  Dashboard,
  ListAlt,
  Settings,
} from '@mui/icons-material';

interface SidebarProps {
  activePage?: 'overview' | 'alerts' | 'settings';
}

const Sidebar: React.FC<SidebarProps> = ({ activePage }) => {
  const pathname = usePathname();
  const currentPage =
    activePage ??
    (pathname?.startsWith('/alerts')
      ? 'alerts'
      : pathname?.startsWith('/settings')
      ? 'settings'
      : 'overview');

  return (
    <div className="w-64 sticky top-0 h-screen bg-gray-800 border-r border-gray-700 flex flex-col">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Warning className="text-red-500" />
          SlipWatch
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          <li>
            <a
              href="/"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200 ${
                currentPage === 'overview'
                  ? 'text-white bg-gray-700'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <Dashboard fontSize="small" />
              Overview
            </a>
          </li>
          <li>
            <a
              href="/alerts"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200 ${
                currentPage === 'alerts'
                  ? 'text-white bg-gray-700'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <ListAlt fontSize="small" />
              Alert Log
            </a>
          </li>
          <li>
            <a
              href="/settings"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200 ${
                currentPage === 'settings'
                  ? 'text-white bg-gray-700'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <Settings fontSize="small" />
              Settings
            </a>
          </li>
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700">
        <p className="text-xs text-gray-500 text-center">
          Fall Detection System
        </p>
      </div>
    </div>
  );
};

export default Sidebar;