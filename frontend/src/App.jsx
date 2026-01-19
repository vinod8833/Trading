import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import StockAnalysis from "./pages/StockAnalysis";
import Signals from "./pages/Signals";
import Intraday from "./pages/Intraday";
import PaperTrading from "./pages/PaperTrading";
import PatternScanner from "./pages/PatternScanner";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import Analytics from "./pages/Analytics";
import MainLayout from "./layouts/MainLayout";
import { useAuthStore } from "./store";
import "./index.css";

export default function App() {
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

  useEffect(() => {
    const storedAccessToken = localStorage.getItem("access_token");
    const storedRefreshToken = localStorage.getItem("refresh_token");
    const storedUser = localStorage.getItem("user");

    if (storedAccessToken && storedRefreshToken) {
      setTokens(storedAccessToken, storedRefreshToken);
      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch (e) {
          console.error("Failed to parse stored user");
        }
      }
    }
  }, [setTokens, setUser]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<MainLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analysis" element={<StockAnalysis />} />
          <Route path="/signals" element={<Signals />} />
          <Route path="/intraday" element={<Intraday />} />
          <Route path="/paper-trading" element={<PaperTrading />} />
          <Route path="/scanner" element={<PatternScanner />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>

      <Toaster position="top-right" />
    </BrowserRouter>
  );
}
