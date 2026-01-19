import React from 'react';

export const Tabs = ({ tabs, activeTab, onTabChange, className = '' }) => (
  <div className={className}>
    <div className="flex border-b border-gray-200 gap-1">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`
            px-4 py-3 text-sm font-medium transition-colors border-b-2
            ${activeTab === tab.id
              ? 'text-blue-600 border-blue-600'
              : 'text-gray-600 border-transparent hover:text-gray-900 hover:border-gray-300'
            }
          `}
        >
          {tab.icon && <span className="mr-2">{tab.icon}</span>}
          {tab.label}
        </button>
      ))}
    </div>
    <div className="mt-4">
      {tabs.find(t => t.id === activeTab)?.content}
    </div>
  </div>
);

export const Modal = ({ isOpen, onClose, title, children, footer, size = 'md', className = '' }) => {
  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />
      <div className={`relative bg-white rounded-xl shadow-xl ${sizes[size]} w-full mx-4 ${className}`}>
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">
            ✕
          </button>
        </div>
        <div className="p-6">
          {children}
        </div>
        {footer && (
          <div className="p-6 border-t border-gray-200 flex gap-3 justify-end">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

export const Tooltip = ({ children, content, position = 'top', className = '' }) => (
  <div className={`group relative inline-block ${className}`}>
    {children}
    <div className={`
      absolute left-1/2 -translate-x-1/2 hidden group-hover:block
      bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap
      ${position === 'top' ? 'bottom-full mb-2' : 'top-full mt-2'}
      z-10
    `}>
      {content}
      <div className={`
        absolute w-2 h-2 bg-gray-900 rotate-45
        left-1/2 -translate-x-1/2
        ${position === 'top' ? 'top-full -mt-1' : 'bottom-full mb-1'}
      `} />
    </div>
  </div>
);

export const Dropdown = ({ trigger, items = [], className = '' }) => {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <div className={`relative inline-block ${className}`}>
      <button onClick={() => setIsOpen(!isOpen)}>
        {trigger}
      </button>
      {isOpen && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-40">
            {items.map((item, idx) => (
              <button
                key={idx}
                onClick={() => {
                  item.onClick?.();
                  setIsOpen(false);
                }}
                className={`
                  block w-full text-left px-4 py-2 hover:bg-gray-100 transition
                  ${idx > 0 ? 'border-t border-gray-200' : ''}
                  text-sm text-gray-700
                `}
              >
                {item.icon && <span className="mr-2">{item.icon}</span>}
                {item.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
