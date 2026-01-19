import React from 'react';

export const Card = ({ children, className = '', ...props }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`} {...props}>
    {children}
  </div>
);

export const CardHeader = ({ children, className = '' }) => (
  <div className={`pb-4 border-b border-gray-200 mb-4 ${className}`}>
    {children}
  </div>
);

export const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold text-gray-900 ${className}`}>
    {children}
  </h3>
);

export const CardDescription = ({ children, className = '' }) => (
  <p className={`text-sm text-gray-500 mt-1 ${className}`}>
    {children}
  </p>
);

export const CardContent = ({ children, className = '' }) => (
  <div className={className}>
    {children}
  </div>
);

export const CardFooter = ({ children, className = '' }) => (
  <div className={`mt-6 pt-4 border-t border-gray-200 flex gap-3 ${className}`}>
    {children}
  </div>
);
