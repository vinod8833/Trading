import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store";

export default function Sidebar({ isOpen, onClose, isCollapsed = false, onCollapsedChange }) {
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);
  const location = useLocation();

  const navSections = [
    {
      label: "Main",
      items: [
        { id: "dashboard", label: "Dashboard", icon: "📊", path: "/dashboard" },
        { id: "analysis", label: "Analysis", icon: "📈", path: "/analysis" },
      ]
    },
    {
      label: "Trading",
      items: [
        { id: "signals", label: "Signals", icon: "🎯", path: "/signals" },
        { id: "scanner", label: "Scanner", icon: "🔍", path: "/scanner" },
        { id: "intraday", label: "Intraday", icon: "⚡", path: "/intraday" },
        { id: "paper", label: "Paper Trading", icon: "📝", path: "/paper-trading" },
      ]
    }
  ];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <>
      <aside className={`
        hidden lg:flex flex-col h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white
        transition-all duration-300 z-40
        ${isCollapsed ? 'w-20' : 'w-64'}
        border-r border-slate-700
      `}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          {!isCollapsed && (
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                KVK
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">Trading Platform</p>
            </div>
          )}
          <button
            onClick={() => onCollapsedChange?.(!isCollapsed)}
            className="p-1.5 hover:bg-slate-700 rounded-lg transition"
            title={isCollapsed ? "Expand" : "Collapse"}
          >
            {isCollapsed ? '→' : '←'}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-3 space-y-4">
          {navSections.map((section) => (
            <div key={section.label}>
              {!isCollapsed && (
                <p className="text-xs font-semibold text-slate-400 px-3 mb-2 uppercase tracking-wider">
                  {section.label}
                </p>
              )}
              <div className="space-y-1">
                {section.items.map((item) => {
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.id}
                      to={item.path}
                      className={`
                        flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all
                        ${isActive
                          ? 'bg-blue-600 text-white shadow-lg'
                          : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                        }
                      `}
                      title={isCollapsed ? item.label : ''}
                    >
                      <span className="text-lg flex-shrink-0">{item.icon}</span>
                      {!isCollapsed && (
                        <span className="text-sm font-medium">{item.label}</span>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-slate-700 p-3">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-300 hover:bg-red-900 hover:text-white rounded-lg transition-colors text-sm font-medium"
            title={isCollapsed ? "Logout" : ''}
          >
            <span className="text-lg">🚪</span>
            {!isCollapsed && <span>Logout</span>}
          </button>
        </div>
      </aside>

      <div className={`
        fixed inset-y-0 left-0 w-64 bg-gradient-to-b from-slate-900 to-slate-800 text-white
        transition-transform duration-300 z-40 lg:hidden flex flex-col
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              KVK
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">Trading Platform</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-slate-700 rounded-lg transition"
          >
            ✕
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-3 space-y-4">
          {navSections.map((section) => (
            <div key={section.label}>
              <p className="text-xs font-semibold text-slate-400 px-3 mb-2 uppercase tracking-wider">
                {section.label}
              </p>
              <div className="space-y-1">
                {section.items.map((item) => {
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.id}
                      to={item.path}
                      onClick={onClose}
                      className={`
                        flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all
                        ${isActive
                          ? 'bg-blue-600 text-white shadow-lg'
                          : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                        }
                      `}
                    >
                      <span className="text-lg">{item.icon}</span>
                      <span className="text-sm font-medium">{item.label}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-slate-700 p-3">
          <button
            onClick={() => {
              handleLogout();
              onClose();
            }}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-300 hover:bg-red-900 hover:text-white rounded-lg transition-colors text-sm font-medium"
          >
            <span className="text-lg">🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </div>
    </>
  );
}
