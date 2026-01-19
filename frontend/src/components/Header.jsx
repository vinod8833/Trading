import React, { useState, useEffect } from "react";
import { useAuthStore } from "../store";
import { useNavigate } from "react-router-dom";
import { Dropdown } from "./ui/Layouts";
import toast from "react-hot-toast";

export default function Header({ onMenuClick }) {
  const { user, logout } = useAuthStore((s) => ({
    user: s.user,
    logout: s.logout,
  }));
  const navigate = useNavigate();
  const [marketStatus, setMarketStatus] = useState("CLOSED");
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const updateMarketStatus = () => {
      const now = new Date();
      const hours = now.getHours();
      const minutes = now.getMinutes();
      const dayOfWeek = now.getDay();

      const isWeekday = dayOfWeek > 0 && dayOfWeek < 6;
      const isMarketHours = (hours > 9 || (hours === 9 && minutes >= 15)) &&
                            (hours < 15 || (hours === 15 && minutes <= 30));

      if (isWeekday && isMarketHours) {
        setMarketStatus("OPEN");
      } else if (!isWeekday) {
        setMarketStatus("WEEKEND");
      } else {
        setMarketStatus("CLOSED");
      }

      setCurrentTime(now);
    };

    updateMarketStatus();
    const interval = setInterval(updateMarketStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleNavigate = (path) => {
    try {
      navigate(path);
    } catch (error) {
      console.error(`Navigation error to ${path}:`, error);
      toast.error("Failed to navigate");
    }
  };

  const handleLogout = async () => {
    try {
      logout();
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      sessionStorage.clear();
      
      toast.success("Logged out successfully!");
      navigate("/login", { replace: true });
    } catch (error) {
      console.error("Logout error:", error);
      toast.error("Logout failed. Clearing data anyway.");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      navigate("/login", { replace: true });
    }
  };

  const getMarketStatusColor = () => {
    switch (marketStatus) {
      case "OPEN":
        return "bg-green-100 text-green-800 border-green-200";
      case "WEEKEND":
        return "bg-gray-100 text-gray-800 border-gray-200";
      default:
        return "bg-red-100 text-red-800 border-red-200";
    }
  };

  const getMarketStatusIcon = () => {
    switch (marketStatus) {
      case "OPEN":
        return "";
      case "WEEKEND":
        return "⏸";
      default:
        return "";
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-30">
      <div className="max-w-full px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-1">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition text-gray-600"
          >
            <span className="text-2xl">☰</span>
          </button>

          <div className="hidden sm:block">
            <h2 className="text-xl font-bold text-gray-900">
              Welcome, <span className="text-blue-600">{user?.username || "Trader"}</span>
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              {currentTime.toLocaleDateString("en-US", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 lg:gap-4">
          <div className={`px-3 py-1.5 rounded-full text-xs font-semibold border flex items-center gap-2 ${getMarketStatusColor()}`}>
            <span className="text-lg">{getMarketStatusIcon()}</span>
            <span className="hidden sm:inline">{marketStatus}</span>
          </div>

          <button className="p-2 hover:bg-gray-100 rounded-lg transition text-gray-600 hover:text-gray-900 relative">
            <span className="text-xl">🔔</span>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          <Dropdown
            trigger={
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-gray-100 transition cursor-pointer">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white text-sm font-bold">
                  {user?.username?.charAt(0).toUpperCase() || "U"}
                </div>
                <span className="hidden sm:inline text-sm font-medium text-gray-700">{user?.username || "User"}</span>
                <span className="text-gray-400">▼</span>
              </div>
            }
            items={[
              {
                icon: "👤",
                label: "Profile",
                onClick: () => handleNavigate("/profile"),
              },
              {
                icon: "⚙️",
                label: "Settings",
                onClick: () => handleNavigate("/settings"),
              },
              {
                icon: "📊",
                label: "Analytics",
                onClick: () => handleNavigate("/analytics"),
              },
              {
                icon: "🚪",
                label: "Logout",
                onClick: handleLogout,
              },
            ]}
          />
        </div>
      </div>
    </header>
  );
}
