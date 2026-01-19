import React, { useState, useEffect } from "react";
import { portfolioApi } from "../api/endpoints";
import toast from "react-hot-toast";
import { riskManagement, marketStatus } from "../utils/tradingEngine";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

export default function Portfolio() {
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPortfolioName, setNewPortfolioName] = useState("");
  const [addCapitalAmount, setAddCapitalAmount] = useState("");
  const [, setMarketOpen] = useState(false);

  const [riskMetrics, setRiskMetrics] = useState(null);

  useEffect(() => {
    fetchPortfolios();

    const updateMarketStatus = () => {
      setMarketOpen(marketStatus.isMarketOpen());
    };

    updateMarketStatus();
    const timer = setInterval(updateMarketStatus, 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (selectedPortfolio) {
      calculateRiskMetrics(selectedPortfolio);
    }
  }, [selectedPortfolio]);

  const fetchPortfolios = async () => {
    setIsLoading(true);
    try {
      const response = await portfolioApi.getPortfolios();
      setPortfolios(response.data);
      if (response.data.length > 0) {
        setSelectedPortfolio(response.data[0]);
      }
    } catch (error) {
      toast.error("Failed to fetch portfolios");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreatePortfolio = async (e) => {
    e.preventDefault();
    try {
      await portfolioApi.createPortfolio({ name: newPortfolioName });
      toast.success("Portfolio created!");
      setNewPortfolioName("");
      setShowCreateForm(false);
      fetchPortfolios();
    } catch (error) {
      toast.error("Failed to create portfolio");
      console.error(error);
    }
  };

  const handleAddCapital = async (e) => {
    e.preventDefault();
    if (!selectedPortfolio) return;

    try {
      await portfolioApi.addCapital(selectedPortfolio.id, parseFloat(addCapitalAmount));
      toast.success("Capital added!");
      setAddCapitalAmount("");
      fetchPortfolios();
    } catch (error) {
      toast.error("Failed to add capital");
      console.error(error);
    }
  };

  const calculateRiskMetrics = (portfolio) => {
    if (!portfolio.positions || portfolio.positions.length === 0) {
      setRiskMetrics(null);
      return;
    }

    const positions = portfolio.positions;
    const totalCapital = portfolio.total_capital || 100000;

    const positionRisks = positions.map((pos) => {
      const pnl = pos.current_price - pos.entry_price;
      const pnlPercent = (pnl / pos.entry_price) * 100;
      const positionValue = pos.quantity * pos.current_price;
      const portfolioPercent = (positionValue / totalCapital) * 100;

      const priceChange = Math.abs(pnl);
      const riskLevel = priceChange > pos.entry_price * 0.05 ? "HIGH" : priceChange > pos.entry_price * 0.02 ? "MEDIUM" : "LOW";

      return {
        symbol: pos.stock_symbol,
        quantity: pos.quantity,
        entry: pos.entry_price,
        current: pos.current_price,
        pnl,
        pnlPercent,
        positionValue,
        portfolioPercent: portfolioPercent.toFixed(2),
        riskLevel
      };
    });

    const totalInvested = positionRisks.reduce((sum, p) => sum + p.positionValue, 0);
    const totalUnrealized = positionRisks.reduce((sum, p) => sum + p.pnl * p.quantity, 0);
    const maxPositionPercent = Math.max(...positionRisks.map(p => parseFloat(p.portfolioPercent)));
    const highRiskCount = positionRisks.filter(p => p.riskLevel === "HIGH").length;

    const warnings = [];
    if (maxPositionPercent > 20) {
      warnings.push("⚠️ CONCENTRATION RISK: Largest position is > 20% of portfolio");
    }
    if (highRiskCount > 0) {
      warnings.push(`⚠️ HIGH VOLATILITY: ${highRiskCount} position(s) with > 5% movement`);
    }
    if (totalUnrealized / totalCapital < -0.05) {
      warnings.push("⚠️ DRAWDOWN: Portfolio is down > 5%");
    }

    const recommendations = [];
    if (maxPositionPercent > 15) {
      recommendations.push("💡 Consider reducing largest position to < 15%");
    }
    if (positionRisks.length < 3) {
      recommendations.push("💡 Add more stocks for diversification");
    }
    if (highRiskCount > 0) {
      recommendations.push("💡 Review high-risk positions and consider tightening stops");
    }

    setRiskMetrics({
      positions: positionRisks,
      totalCapital,
      totalInvested,
      totalUnrealized,
      maxPositionPercent,
      highRiskCount,
      warnings,
      recommendations,
      exposurePercent: ((totalInvested / totalCapital) * 100).toFixed(2),
      diversificationScore: Math.min(100, (positionRisks.length * 20))
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Portfolio Management</h1>
            <p className="text-gray-600 mt-2">Track your investments and positions</p>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-gradient-to-r from-primary to-secondary text-white font-semibold py-2 px-6 rounded-lg hover:shadow-lg transition"
          >
            ➕ New Portfolio
          </button>
        </div>
      </div>

      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <form onSubmit={handleCreatePortfolio} className="flex gap-4">
            <input
              type="text"
              value={newPortfolioName}
              onChange={(e) => setNewPortfolioName(e.target.value)}
              placeholder="Portfolio name (e.g., My Trading Account)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              required
            />
            <button
              type="submit"
              className="bg-primary text-white font-semibold py-2 px-6 rounded-lg hover:shadow-lg transition"
            >
              Create
            </button>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="bg-gray-300 text-gray-700 font-semibold py-2 px-6 rounded-lg hover:shadow-lg transition"
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      {portfolios.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-2">
          {portfolios.map((portfolio) => (
            <button
              key={portfolio.id}
              onClick={() => setSelectedPortfolio(portfolio)}
              className={`px-4 py-2 rounded-lg font-medium transition whitespace-nowrap ${
                selectedPortfolio?.id === portfolio.id
                  ? "bg-primary text-white"
                  : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
              }`}
            >
              💼 {portfolio.name}
            </button>
          ))}
        </div>
      )}

      {selectedPortfolio && (
        <div className="space-y-6">
          {riskMetrics && (riskMetrics.warnings.length > 0 || riskMetrics.recommendations.length > 0) && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 rounded-lg p-6">
              <h3 className="text-lg font-bold text-yellow-900 mb-3">⚠️ Portfolio Risk Assessment</h3>
              {riskMetrics.warnings.length > 0 && (
                <div className="mb-4">
                  <ul className="space-y-2 text-sm text-yellow-800">
                    {riskMetrics.warnings.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </div>
              )}
              {riskMetrics.recommendations.length > 0 && (
                <div className="pt-4 border-t border-yellow-200">
                  <p className="text-xs font-semibold text-yellow-900 mb-2">Recommendations:</p>
                  <ul className="space-y-1 text-sm text-yellow-800">
                    {riskMetrics.recommendations.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {riskMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow-md p-4">
                <p className="text-sm text-gray-600 mb-1">Portfolio Exposure</p>
                <p className="text-3xl font-bold text-blue-600">{riskMetrics.exposurePercent}%</p>
                <p className="text-xs text-gray-500 mt-2">Invested vs Total Capital</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-4">
                <p className="text-sm text-gray-600 mb-1">Max Position</p>
                <p className="text-3xl font-bold text-orange-600">{riskMetrics.maxPositionPercent.toFixed(1)}%</p>
                <p className="text-xs text-gray-500 mt-2">Largest single position</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-4">
                <p className="text-sm text-gray-600 mb-1">Diversification</p>
                <p className="text-3xl font-bold text-green-600">{riskMetrics.diversificationScore}%</p>
                <p className="text-xs text-gray-500 mt-2">Number of stocks</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-4">
                <p className="text-sm text-gray-600 mb-1">At-Risk Positions</p>
                <p className="text-3xl font-bold text-red-600">{riskMetrics.highRiskCount}</p>
                <p className="text-xs text-gray-500 mt-2">With > 5% movement</p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-md p-4">
              <p className="text-sm text-gray-600 mb-1">Total Capital</p>
              <p className="text-3xl font-bold text-gray-900">
                ₹{selectedPortfolio.total_capital?.toLocaleString()}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4">
              <p className="text-sm text-gray-600 mb-1">Invested Amount</p>
              <p className="text-3xl font-bold text-blue-600">
                ₹{selectedPortfolio.invested_amount?.toLocaleString()}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4">
              <p className="text-sm text-gray-600 mb-1">Cash Available</p>
              <p className="text-3xl font-bold text-green-600">
                ₹{(selectedPortfolio.total_capital - selectedPortfolio.invested_amount)?.toLocaleString()}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4">
              <p className="text-sm text-gray-600 mb-1">Total Returns</p>
              <p className={`text-3xl font-bold ${selectedPortfolio.total_returns >= 0 ? "text-green-600" : "text-red-600"}`}>
                {selectedPortfolio.total_returns >= 0 ? "+" : ""}
                {selectedPortfolio.total_returns?.toFixed(2)}%
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Add Capital</h3>
            <form onSubmit={handleAddCapital} className="flex gap-4">
              <input
                type="number"
                value={addCapitalAmount}
                onChange={(e) => setAddCapitalAmount(e.target.value)}
                placeholder="Amount to add (₹)"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                required
              />
              <button
                type="submit"
                className="bg-green-600 text-white font-semibold py-2 px-6 rounded-lg hover:shadow-lg transition"
              >
                Add Funds
              </button>
            </form>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Open Positions</h3>
            {selectedPortfolio.positions && selectedPortfolio.positions.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Symbol</th>
                      <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Quantity</th>
                      <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Entry Price</th>
                      <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Current Price</th>
                      <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">P&L</th>
                      <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">P&L %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {selectedPortfolio.positions.map((position) => {
                      const pnl = position.current_price - position.entry_price;
                      const pnlPercent = (pnl / position.entry_price) * 100;
                      return (
                        <tr key={position.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-semibold text-gray-900">{position.stock_symbol}</td>
                          <td className="px-4 py-3 text-gray-700">{position.quantity}</td>
                          <td className="px-4 py-3 text-gray-700">₹{position.entry_price}</td>
                          <td className="px-4 py-3 text-gray-700">₹{position.current_price}</td>
                          <td className={`px-4 py-3 font-semibold ${pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                            {pnl >= 0 ? "+" : ""}₹{pnl.toFixed(2)}
                          </td>
                          <td className={`px-4 py-3 font-semibold ${pnlPercent >= 0 ? "text-green-600" : "text-red-600"}`}>
                            {pnlPercent >= 0 ? "+" : ""}{pnlPercent.toFixed(2)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500">No open positions</p>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Portfolio Performance</h3>
            {selectedPortfolio.performance_history && selectedPortfolio.performance_history.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={selectedPortfolio.performance_history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#0088FE"
                    dot={false}
                    name="Portfolio Value"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500">No performance data available yet</p>
            )}
          </div>
        </div>
      )}

      {portfolios.length === 0 && !isLoading && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <p className="text-gray-600 text-lg">No portfolios yet</p>
          <p className="text-gray-400">Create your first portfolio to start tracking investments</p>
        </div>
      )}

      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin text-4xl">💼</div>
          <p className="text-gray-600 mt-4">Loading portfolios...</p>
        </div>
      )}
    </div>
  );
}
