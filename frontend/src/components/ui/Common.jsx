import React from 'react';

export const Badge = ({ children, variant = 'default', className = '', ...props }) => {
  const variants = {
    default: 'bg-gray-200 text-gray-800',
    primary: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    info: 'bg-cyan-100 text-cyan-800',
  };

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`} {...props}>
      {children}
    </span>
  );
};

export const Stat = ({ label, value, change, changeType = 'neutral', icon = null, className = '' }) => (
  <div className={`bg-white rounded-lg p-4 border border-gray-200 ${className}`}>
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <p className="text-sm text-gray-600 font-medium">{label}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        {change && (
          <p className={`text-xs mt-2 font-medium ${
            changeType === 'up' ? 'text-green-600' : 
            changeType === 'down' ? 'text-red-600' : 
            'text-gray-600'
          }`}>
            {changeType === 'up' ? '↑' : changeType === 'down' ? '↓' : ''} {change}
          </p>
        )}
      </div>
      {icon && (
        <div className="text-3xl opacity-20 ml-2">
          {icon}
        </div>
      )}
    </div>
  </div>
);

export const Alert = ({ type = 'info', title, message, icon = null, onClose, className = '' }) => {
  const colors = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    error: 'bg-red-50 border-red-200 text-red-800',
  };

  return (
    <div className={`rounded-lg border p-4 flex items-start gap-3 ${colors[type]} ${className}`}>
      {icon && <span className="text-lg mt-0.5">{icon}</span>}
      <div className="flex-1">
        {title && <p className="font-semibold text-sm">{title}</p>}
        {message && <p className="text-sm mt-1">{message}</p>}
      </div>
      {onClose && (
        <button onClick={onClose} className="ml-2 hover:opacity-70 transition">
          ✕
        </button>
      )}
    </div>
  );
};

export const Progress = ({ value = 0, label = null, className = '' }) => (
  <div className={className}>
    {label && <p className="text-sm font-medium text-gray-700 mb-2">{label}</p>}
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div 
        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
        style={{ width: `${Math.min(100, value)}%` }}
      />
    </div>
    <p className="text-xs text-gray-500 mt-1">{Math.round(value)}%</p>
  </div>
);

export const Skeleton = ({ className = '' }) => (
  <div className={`bg-gray-200 animate-pulse rounded ${className}`} />
);
