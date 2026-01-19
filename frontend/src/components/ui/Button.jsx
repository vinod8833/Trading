import React from 'react';

export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  ...props 
}) => {
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900',
    success: 'bg-green-600 hover:bg-green-700 text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    ghost: 'bg-transparent hover:bg-gray-100 text-gray-700',
    outline: 'border border-gray-300 hover:bg-gray-50 text-gray-700',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`
        font-medium rounded-lg transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        flex items-center justify-center gap-2
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <span className="animate-spin">⏳</span>}
      {children}
    </button>
  );
};

export const IconButton = ({ icon, variant = 'ghost', className = '', ...props }) => (
  <button
    className={`
      p-2 rounded-lg transition-colors
      ${variant === 'ghost' ? 'hover:bg-gray-100' : 'hover:bg-blue-50'}
      ${className}
    `}
    {...props}
  >
    {icon}
  </button>
);
