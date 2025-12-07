'use client';

import { User, Car, FileText, MapPin, Clock } from 'lucide-react';

interface SearchResult {
  id: string;
  type: 'person' | 'vehicle' | 'incident' | 'address';
  title: string;
  description: string;
  score: number;
  timestamp?: string;
}

interface SearchResultsProps {
  results: SearchResult[];
  isLoading: boolean;
  query: string;
}

const typeIcons = {
  person: User,
  vehicle: Car,
  incident: FileText,
  address: MapPin,
};

const typeColors = {
  person: 'bg-blue-100 text-blue-600',
  vehicle: 'bg-orange-100 text-orange-600',
  incident: 'bg-red-100 text-red-600',
  address: 'bg-green-100 text-green-600',
};

/**
 * Search results display component.
 */
export function SearchResults({ results, isLoading, query }: SearchResultsProps) {
  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-rtcc-accent border-t-transparent" />
            <p className="mt-4 text-gray-500">Searching...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!query) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-300" />
            <p className="mt-4 text-gray-500">
              Enter a search query to find persons, vehicles, incidents, and more
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-300" />
            <p className="mt-4 text-gray-500">No results found for "{query}"</p>
            <p className="mt-2 text-sm text-gray-400">Try adjusting your search terms or filters</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {results.length} results for "{query}"
        </p>
      </div>

      <div className="space-y-3">
        {results.map((result) => {
          const Icon = typeIcons[result.type];

          return (
            <div
              key={result.id}
              className="flex cursor-pointer items-start gap-4 rounded-lg border p-4 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700"
            >
              <div className={`rounded-lg p-2 ${typeColors[result.type]}`}>
                <Icon className="h-5 w-5" />
              </div>

              <div className="min-w-0 flex-1">
                <h3 className="font-medium text-gray-900 dark:text-white">{result.title}</h3>
                <p className="truncate text-sm text-gray-600 dark:text-gray-400">
                  {result.description}
                </p>
                {result.timestamp && (
                  <div className="mt-2 flex items-center gap-1 text-xs text-gray-500">
                    <Clock className="h-3 w-3" />
                    {new Date(result.timestamp).toLocaleDateString()}
                  </div>
                )}
              </div>

              <div className="text-right">
                <span className="text-xs text-gray-500">
                  {Math.round(result.score * 100)}% match
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
