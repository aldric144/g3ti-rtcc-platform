'use client';

import { useState, FormEvent } from 'react';
import { Search, Loader2, Sparkles } from 'lucide-react';

interface AISearchBarProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

const exampleQueries = [
  'Show me vehicles connected to gunfire within the last 30 days near Broadway',
  'Find all incidents involving repeat offenders in the downtown area',
  'What vehicles have been spotted near 123 Main St in the past week?',
  'Show me patterns of late-night crime activity in Zone 3',
  'Find connections between recent LPR hits and open investigations',
];

export function AISearchBar({ onSearch, isLoading }: AISearchBarProps) {
  const [query, setQuery] = useState('');
  const [showExamples, setShowExamples] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch(query.trim());
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
    setShowExamples(false);
    onSearch(example);
  };

  return (
    <div className="relative">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin text-indigo-500" />
            ) : (
              <Search className="h-5 w-5 text-gray-400" />
            )}
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowExamples(true)}
            onBlur={() => setTimeout(() => setShowExamples(false), 200)}
            placeholder="Ask a natural language question about your data..."
            className="block w-full rounded-lg border border-gray-300 bg-white py-4 pl-12 pr-32 text-gray-900 placeholder-gray-500 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400"
            disabled={isLoading}
          />
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            <button
              type="submit"
              disabled={!query.trim() || isLoading}
              className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Sparkles className="h-4 w-4" />
              Analyze
            </button>
          </div>
        </div>
      </form>

      {showExamples && (
        <div className="absolute z-10 mt-2 w-full rounded-lg border border-gray-200 bg-white p-4 shadow-lg dark:border-gray-700 dark:bg-gray-800">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Example queries
          </p>
          <ul className="space-y-2">
            {exampleQueries.map((example, index) => (
              <li key={index}>
                <button
                  type="button"
                  onClick={() => handleExampleClick(example)}
                  className="w-full rounded-md px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  {example}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
