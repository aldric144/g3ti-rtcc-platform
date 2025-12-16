'use client';

import React from 'react';

interface TextInputProps {
  label: string;
  name: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
  type?: 'text' | 'email' | 'url' | 'password';
  error?: string;
}

export function TextInput({
  label,
  name,
  value,
  onChange,
  required = false,
  disabled = false,
  placeholder,
  type = 'text',
  error,
}: TextInputProps) {
  return (
    <div className="space-y-1">
      <label htmlFor={name} className="block text-sm font-medium text-gray-300">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        disabled={disabled}
        placeholder={placeholder}
        className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 ${
          error ? 'border-red-500' : 'border-gray-600'
        }`}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

interface NumberInputProps {
  label: string;
  name: string;
  value: number | string;
  onChange: (value: number) => void;
  required?: boolean;
  disabled?: boolean;
  min?: number;
  max?: number;
  step?: number;
  error?: string;
}

export function NumberInput({
  label,
  name,
  value,
  onChange,
  required = false,
  disabled = false,
  min,
  max,
  step = 1,
  error,
}: NumberInputProps) {
  return (
    <div className="space-y-1">
      <label htmlFor={name} className="block text-sm font-medium text-gray-300">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        type="number"
        id={name}
        name={name}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        required={required}
        disabled={disabled}
        min={min}
        max={max}
        step={step}
        className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 ${
          error ? 'border-red-500' : 'border-gray-600'
        }`}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

interface SelectOption {
  value: string;
  label: string;
}

interface DropdownSelectProps {
  label: string;
  name: string;
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
  error?: string;
}

export function DropdownSelect({
  label,
  name,
  value,
  onChange,
  options,
  required = false,
  disabled = false,
  placeholder = 'Select...',
  error,
}: DropdownSelectProps) {
  return (
    <div className="space-y-1">
      <label htmlFor={name} className="block text-sm font-medium text-gray-300">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <select
        id={name}
        name={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        disabled={disabled}
        className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 ${
          error ? 'border-red-500' : 'border-gray-600'
        }`}
      >
        <option value="">{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

interface ToggleSwitchProps {
  label: string;
  name: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  description?: string;
}

export function ToggleSwitch({
  label,
  name,
  checked,
  onChange,
  disabled = false,
  description,
}: ToggleSwitchProps) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <label htmlFor={name} className="block text-sm font-medium text-gray-300">
          {label}
        </label>
        {description && <p className="text-xs text-gray-500">{description}</p>}
      </div>
      <button
        type="button"
        id={name}
        role="switch"
        aria-checked={checked}
        onClick={() => !disabled && onChange(!checked)}
        disabled={disabled}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 ${
          checked ? 'bg-blue-600' : 'bg-gray-600'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
}

interface TextAreaProps {
  label: string;
  name: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
  rows?: number;
  error?: string;
}

export function TextArea({
  label,
  name,
  value,
  onChange,
  required = false,
  disabled = false,
  placeholder,
  rows = 4,
  error,
}: TextAreaProps) {
  return (
    <div className="space-y-1">
      <label htmlFor={name} className="block text-sm font-medium text-gray-300">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <textarea
        id={name}
        name={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        disabled={disabled}
        placeholder={placeholder}
        rows={rows}
        className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 resize-none ${
          error ? 'border-red-500' : 'border-gray-600'
        }`}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

interface FileUploadProps {
  label: string;
  name: string;
  onChange: (file: File | null) => void;
  accept?: string;
  required?: boolean;
  disabled?: boolean;
  currentFile?: string;
  error?: string;
}

export function FileUpload({
  label,
  name,
  onChange,
  accept = '*/*',
  required = false,
  disabled = false,
  currentFile,
  error,
}: FileUploadProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    onChange(file);
  };

  return (
    <div className="space-y-1">
      <label htmlFor={name} className="block text-sm font-medium text-gray-300">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <div className="flex items-center gap-2">
        <input
          ref={inputRef}
          type="file"
          id={name}
          name={name}
          onChange={handleChange}
          accept={accept}
          required={required && !currentFile}
          disabled={disabled}
          className="hidden"
        />
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={disabled}
          className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white hover:bg-gray-600 disabled:opacity-50"
        >
          Choose File
        </button>
        <span className="text-sm text-gray-400 truncate">
          {currentFile || 'No file selected'}
        </span>
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

interface MultiSelectProps {
  label: string;
  name: string;
  value: string[];
  onChange: (value: string[]) => void;
  options: SelectOption[];
  required?: boolean;
  disabled?: boolean;
  error?: string;
}

export function MultiSelect({
  label,
  name,
  value,
  onChange,
  options,
  required = false,
  disabled = false,
  error,
}: MultiSelectProps) {
  const toggleOption = (optValue: string) => {
    if (value.includes(optValue)) {
      onChange(value.filter((v) => v !== optValue));
    } else {
      onChange([...value, optValue]);
    }
  };

  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-300">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <div className={`p-2 bg-gray-800 border rounded-lg max-h-40 overflow-y-auto ${
        error ? 'border-red-500' : 'border-gray-600'
      }`}>
        {options.map((opt) => (
          <label
            key={opt.value}
            className="flex items-center gap-2 p-1 hover:bg-gray-700 rounded cursor-pointer"
          >
            <input
              type="checkbox"
              checked={value.includes(opt.value)}
              onChange={() => !disabled && toggleOption(opt.value)}
              disabled={disabled}
              className="rounded border-gray-600 bg-gray-700 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">{opt.label}</span>
          </label>
        ))}
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

interface StatusBadgeProps {
  status: string;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'default';
}

export function StatusBadge({ status, variant = 'default' }: StatusBadgeProps) {
  const colors = {
    success: 'bg-green-900/50 text-green-400 border-green-700',
    warning: 'bg-yellow-900/50 text-yellow-400 border-yellow-700',
    error: 'bg-red-900/50 text-red-400 border-red-700',
    info: 'bg-blue-900/50 text-blue-400 border-blue-700',
    default: 'bg-gray-700/50 text-gray-400 border-gray-600',
  };

  return (
    <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${colors[variant]}`}>
      {status}
    </span>
  );
}

export function getStatusVariant(status: string): 'success' | 'warning' | 'error' | 'info' | 'default' {
  const statusLower = status.toLowerCase();
  if (['active', 'online', 'operational', 'approved', 'completed'].includes(statusLower)) {
    return 'success';
  }
  if (['pending', 'maintenance', 'warning', 'in_progress'].includes(statusLower)) {
    return 'warning';
  }
  if (['inactive', 'offline', 'error', 'failed', 'critical'].includes(statusLower)) {
    return 'error';
  }
  if (['new', 'scheduled', 'info'].includes(statusLower)) {
    return 'info';
  }
  return 'default';
}
