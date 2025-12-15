'use client';

import { useState } from 'react';
import { Users, Plus, Trash2, Clock } from 'lucide-react';

interface Operator {
  id: string;
  username: string;
  name: string;
  role: string;
  assigned_at: string;
}

const ROLES = [
  { value: 'operator', label: 'Operator' },
  { value: 'supervisor', label: 'Supervisor' },
  { value: 'analyst', label: 'Analyst' },
];

interface OperatorListPanelProps {
  refreshKey: number;
}

export function OperatorListPanel({ refreshKey }: OperatorListPanelProps) {
  const [operators, setOperators] = useState<Operator[]>([
    {
      id: '1',
      username: 'jsmith',
      name: 'John Smith',
      role: 'operator',
      assigned_at: new Date(Date.now() - 4 * 60 * 60000).toISOString(),
    },
    {
      id: '2',
      username: 'mjohnson',
      name: 'Maria Johnson',
      role: 'analyst',
      assigned_at: new Date(Date.now() - 3 * 60 * 60000).toISOString(),
    },
    {
      id: '3',
      username: 'rwilliams',
      name: 'Robert Williams',
      role: 'operator',
      assigned_at: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
    },
  ]);

  const [showForm, setShowForm] = useState(false);
  const [newOperator, setNewOperator] = useState({
    username: '',
    name: '',
    role: 'operator',
  });

  const handleAddOperator = (e: React.FormEvent) => {
    e.preventDefault();
    
    const operator: Operator = {
      id: Date.now().toString(),
      ...newOperator,
      assigned_at: new Date().toISOString(),
    };

    setOperators([...operators, operator]);
    setNewOperator({ username: '', name: '', role: 'operator' });
    setShowForm(false);
  };

  const removeOperator = (operatorId: string) => {
    setOperators(operators.filter(o => o.id !== operatorId));
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'supervisor':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400';
      case 'analyst':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="border-b border-gray-200 p-4 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white">
            <Users className="h-5 w-5" />
            Personnel on Duty ({operators.length})
          </h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-1 rounded-lg bg-rtcc-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-rtcc-primary/90"
          >
            <Plus className="h-4 w-4" />
            Add
          </button>
        </div>
      </div>

      {/* Add Form */}
      {showForm && (
        <div className="border-b border-gray-200 p-4 dark:border-gray-700">
          <form onSubmit={handleAddOperator} className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                  Username
                </label>
                <input
                  type="text"
                  value={newOperator.username}
                  onChange={(e) => setNewOperator({ ...newOperator, username: e.target.value })}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                  Full Name
                </label>
                <input
                  type="text"
                  value={newOperator.name}
                  onChange={(e) => setNewOperator({ ...newOperator, name: e.target.value })}
                  required
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                Role
              </label>
              <select
                value={newOperator.role}
                onChange={(e) => setNewOperator({ ...newOperator, role: e.target.value })}
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
              >
                {ROLES.map((role) => (
                  <option key={role.value} value={role.value}>
                    {role.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="rounded-lg bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-lg bg-rtcc-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-rtcc-primary/90"
              >
                Add Operator
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Operator List */}
      <div className="max-h-80 overflow-y-auto p-4">
        <div className="space-y-2">
          {operators.map((operator) => (
            <div
              key={operator.id}
              className="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-700/50"
            >
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-medium text-gray-900 dark:text-white">
                    {operator.name}
                  </p>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getRoleColor(operator.role)}`}>
                    {operator.role}
                  </span>
                </div>
                <div className="mt-1 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                  <span>@{operator.username}</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(operator.assigned_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
              <button
                onClick={() => removeOperator(operator.id)}
                className="rounded-lg p-1 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
