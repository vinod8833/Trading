import React from 'react';

export const Input = ({ 
  label, 
  error, 
  helperText,
  icon,
  className = '',
  ...props 
}) => (
  <div className="w-full">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
    )}
    <div className="relative">
      {icon && (
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          {icon}
        </span>
      )}
      <input
        className={`
          w-full px-4 py-2.5 rounded-lg border-2 transition-colors
          ${icon ? 'pl-10' : ''}
          ${error 
            ? 'border-red-300 focus:border-red-500 focus:ring-1 focus:ring-red-500' 
            : 'border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
          }
          text-gray-900 placeholder-gray-400
          ${className}
        `}
        {...props}
      />
    </div>
    {helperText && (
      <p className={`text-sm mt-1 ${error ? 'text-red-600' : 'text-gray-500'}`}>
        {helperText}
      </p>
    )}
  </div>
);

export const Select = ({ label, error, helperText, options = [], className = '', ...props }) => (
  <div className="w-full">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
    )}
    <select
      className={`
        w-full px-4 py-2.5 rounded-lg border-2 transition-colors
        ${error 
          ? 'border-red-300 focus:border-red-500' 
          : 'border-gray-300 focus:border-blue-500'
        }
        text-gray-900 bg-white
        ${className}
      `}
      {...props}
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
    {helperText && (
      <p className={`text-sm mt-1 ${error ? 'text-red-600' : 'text-gray-500'}`}>
        {helperText}
      </p>
    )}
  </div>
);

export const Textarea = ({ label, error, helperText, className = '', ...props }) => (
  <div className="w-full">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
    )}
    <textarea
      className={`
        w-full px-4 py-2.5 rounded-lg border-2 transition-colors
        ${error 
          ? 'border-red-300 focus:border-red-500' 
          : 'border-gray-300 focus:border-blue-500'
        }
        text-gray-900 placeholder-gray-400
        resize-vertical
        ${className}
      `}
      {...props}
    />
    {helperText && (
      <p className={`text-sm mt-1 ${error ? 'text-red-600' : 'text-gray-500'}`}>
        {helperText}
      </p>
    )}
  </div>
);
