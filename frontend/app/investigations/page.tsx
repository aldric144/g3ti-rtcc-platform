'use client';

import { useState } from 'react';
import { Search, Filter, Plus, FileText, Clock, User } from 'lucide-react';
import { SearchBar } from '@/app/components/investigations/SearchBar';
import { SearchResults } from '@/app/components/investigations/SearchResults';
import { SearchFilters } from '@/app/components/investigations/SearchFilters';

/**
 * Investigations search page.
 * 
 * Provides:
 * - Full-text search across all entities
 * - Advanced filtering
 * - Search result display
 * - Quick actions
 */
export default function InvestigationsPage() {
  const [query, setQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const handleSearch = async (searchQuery: string) => {
    setQuery(searchQuery);
    setIsSearching(true);
    
    // Placeholder - would call API
    setTimeout(() => {
      setResults([]);
      setIsSearching(false);
    }, 500);
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Investigations
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Search and manage investigative cases
          </p>
        </div>
        
        <button className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Investigation
        </button>
      </div>

      {/* Search section */}
      <div className="card">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <SearchBar
              value={query}
              onChange={setQuery}
              onSearch={handleSearch}
              placeholder="Search persons, vehicles, incidents, addresses..."
            />
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-outline flex items-center gap-2 ${showFilters ? 'bg-gray-100' : ''}`}
          >
            <Filter className="h-4 w-4" />
            Filters
          </button>
        </div>

        {/* Filters panel */}
        {showFilters && (
          <div className="mt-4 border-t pt-4">
            <SearchFilters />
          </div>
        )}
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="card flex items-center gap-4">
          <div className="rounded-lg bg-blue-100 p-3">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">89</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Open Cases</p>
          </div>
        </div>
        
        <div className="card flex items-center gap-4">
          <div className="rounded-lg bg-orange-100 p-3">
            <Clock className="h-6 w-6 text-orange-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">12</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Pending Review</p>
          </div>
        </div>
        
        <div className="card flex items-center gap-4">
          <div className="rounded-lg bg-green-100 p-3">
            <User className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">5</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Assigned to You</p>
          </div>
        </div>
      </div>

      {/* Search results */}
      <SearchResults
        results={results}
        isLoading={isSearching}
        query={query}
      />
    </div>
  );
}
