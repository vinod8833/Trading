import React, { useState, useEffect } from "react";
import { useAuthStore } from "../store";
import { tradingApi } from "../api/endpoints";
import toast from "react-hot-toast";

export default function Analytics() {
  const user = useAuthStore((s) => s.user);
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setIsLoading(true);
        const portfolioResponse = await tradingApi.getPortfolios();
        const recommendationsResponse = await tradingApi.getRecommendations();

        const portfolios = portfolioResponse.data || [];
        const recommendations = recommendationsResponse.data || [];

        const totalCapital = portfolios.reduce((sum, p) => sum + (p.capital || 0), 0);
        const totalInvested = portfolios.reduce((sum, p) => sum + (p.invested_amount || 0), 0);
        const totalReturns = portfolios.reduce((sum, p) => sum + (p.profit_loss || 0), 0);
        const totalTrades = recommendations.length;
        const winningTrades = recommendations.filter((r) => r.status === "EXECUTED" && r.profit > 0).length;
        const winRate = totalTrades > 0 ? ((winningTrades / totalTrades) * 100).toFixed(2) : 0;

        setAnalytics({
          totalCapital,
          totalInvested,
          totalReturns,
          returnPercentage: totalInvested > 0 ? ((totalReturns / totalInvested) * 100).toFixed(2) : 0,
          totalTrades,
          winningTrades,
          winRate,
          portfolios: portfolios.length,
          activePositions: portfolios.filter((p) => p.status === "ACTIVE").length,
        });
      } catch {
        console.error("Failed to fetch analytics");
        toast.error("Failed to load analytics data");
        setAnalytics({
          totalCapital: 0,
          totalInvested: 0,
          totalReturns: 0,
          returnPercentage: 0,
          totalTrades: 0,
          winningTrades: 0,
          winRate: 0,
          portfolios: 0,
          activePositions: 0,
        });
      } finally {
        setIsLoading(false);
      }
    };

    if (user?.id) {
      fetchAnalytics();
    }
  }, [user?.id]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-5xl mb-4">📊</div>
          <p className="text-gray-600">No analytics data available</p>
        </div>
      </div>
    );
  }

  const StatCard = ({ icon, label, value, unit = "", color = "blue" }) => {
    const colorClasses = {
      blue: "bg-blue-50 border-blue-200",
      green: "bg-green-50 border-green-200",
      purple: "bg-purple-50 border-purple-200",
      orange: "bg-orange-50 border-orange-200",
    };

    return (
      <div className={`${colorClasses[color]} border rounded-lg p-6`}>
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 mb-2">{label}</p>
            <p className="text-2xl font-bold text-gray-900">
              {typeof value === "number" ? value.toLocaleString() : value}
              {unit && <span className="text-lg ml-1">{unit}</span>}
            </p>
          </div>
          <span className="text-3xl">{icon}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 Analytics</h1>
        <p className="text-gray-600">Your trading performance and portfolio statistics</p>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">💰 Portfolio Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon="💵"
            label="Total Capital"
            value={analytics.totalCapital}
            unit="₹"
            color="blue"
          />
          <StatCard
            icon="📈"
            label="Invested"
            value={analytics.totalInvested}
            unit="₹"
            color="purple"
          />
          <StatCard
            icon="📊"
            label="Total Returns"
            value={analytics.totalReturns}
            unit="₹"
            color={analytics.totalReturns >= 0 ? "green" : "orange"}
          />
          <StatCard
            icon="📉"
            label="Return %"
            value={analytics.returnPercentage}
            unit="%"
            color={analytics.returnPercentage >= 0 ? "green" : "orange"}
          />
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">🎯 Trading Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon="🔄"
            label="Total Trades"
            value={analytics.totalTrades}
            color="blue"
          />
          <StatCard
            icon="✅"
            label="Winning Trades"
            value={analytics.winningTrades}
            color="green"
          />
          <StatCard
            icon="📊"
            label="Win Rate"
            value={analytics.winRate}
            unit="%"
            color="green"
          />
          <StatCard
            icon="🏢"
            label="Active Positions"
            value={analytics.activePositions}
            color="blue"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">📁 Portfolios</h3>
          <div className="text-center py-8">
            <p className="text-4xl font-bold text-blue-600 mb-2">{analytics.portfolios}</p>
            <p className="text-gray-600">Total portfolios created</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">📈 Performance Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Win Rate:</span>
              <span className="font-semibold text-gray-900">{analytics.winRate}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Profit Factor:</span>
              <span className="font-semibold text-gray-900">
                {analytics.totalTrades > 0 ? (analytics.winningTrades / analytics.totalTrades).toFixed(2) : "N/A"}
              </span>
            </div>
            <div className="flex justify-between items-center pt-3 border-t">
              <span className="text-gray-600 font-medium">Total P&L:</span>
              <span
                className={`font-bold text-lg ${
                  analytics.totalReturns >= 0 ? "text-green-600" : "text-red-600"
                }`}
              >
                {analytics.totalReturns >= 0 ? "+" : ""}₹{analytics.totalReturns.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-3">💡 Analytics Information</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>✓ Analytics are updated in real-time from your portfolio</li>
          <li>✓ All figures are calculated from your active and closed positions</li>
          <li>✓ Win rate includes only executed trades with profit/loss data</li>
          <li>✓ Returns are shown in both absolute (₹) and percentage (%) terms</li>
          <li>✓ You can drill down into individual portfolio details for more information</li>
        </ul>
      </div>
    </div>
  );
}
