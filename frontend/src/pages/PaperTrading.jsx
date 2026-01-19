import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { marketStatus } from "../utils/tradingEngine";
import axios from "axios";

const API_BASE = "http://localhost:8001/api";

export default function PaperTrading() {
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [activeTrades, setActiveTrades] = useState([]);
  const [closedTrades, setClosedTrades] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [marketOpen, setMarketOpen] = useState(false);
  const [marketStatusInfo, setMarketStatusInfo] = useState(null);
  const [showNewTrade, setShowNewTrade] = useState(false);
  const [refreshTimer, setRefreshTimer] = useState(30);

  const [newTrade, setNewTrade] = useState({
    symbol: "INFY",
    side: "BUY",
    quantity: 10,
    entry_price: 1500,
    stop_loss: 1485,
    target_1: 1530,
    target_2: 1550,
    target_3: 1570,
    target_4: 1590,
  });

  useEffect(() => {
    checkMarketStatus();
    loadPortfolios();
    const statusInterval = setInterval(checkMarketStatus, 60000);
    return () => clearInterval(statusInterval);
  }, []);

  useEffect(() => {
    if (!selectedPortfolio || !marketOpen) return;

    const refreshInterval = setInterval(() => {
      loadActiveTrades();
      setRefreshTimer(prev => prev === 0 ? 30 : prev - 1);
    }, 30000);

    return () => clearInterval(refreshInterval);
  }, [selectedPortfolio, marketOpen]);

  useEffect(() => {
    if (selectedPortfolio) {
      loadActiveTrades();
      loadClosedTrades();
      loadStats();
    }
  }, [selectedPortfolio]);

  const checkMarketStatus = () => {
    const status = marketStatus.getMarketStatus();
    setMarketOpen(status.isOpen);
    setMarketStatusInfo(status);
  };

  const loadPortfolios = async () => {
    try {
      const response = await axios.get(`${API_BASE}/portfolios/`);
      setPortfolios(response.data);
      if (response.data.length > 0) {
        setSelectedPortfolio(response.data[0].id);
      }
    } catch (error) {
      console.error("Error loading portfolios:", error);
      toast.error("Failed to load portfolios");
    }
  };

  const loadActiveTrades = async () => {
    if (!selectedPortfolio) return;
    try {
      const response = await axios.get(
        `${API_BASE}/paper-trades/active_trades/?portfolio_id=${selectedPortfolio}`
      );
      setActiveTrades(response.data.trades || []);
    } catch (error) {
      console.error("Error loading active trades:", error);
    }
  };

  const loadClosedTrades = async () => {
    if (!selectedPortfolio) return;
    try {
      const response = await axios.get(
        `${API_BASE}/paper-trades/closed_trades/?portfolio_id=${selectedPortfolio}`
      );
      setClosedTrades(response.data.trades || []);
    } catch (error) {
      console.error("Error loading closed trades:", error);
    }
  };

  const loadStats = async () => {
    if (!selectedPortfolio) return;
    try {
      const response = await axios.get(
        `${API_BASE}/paper-trades/stats/?portfolio_id=${selectedPortfolio}`
      );
      setStats(response.data.stats);
    } catch (error) {
      console.error("Error loading stats:", error);
    }
  };

  const handleCreateTrade = async (e) => {
    e.preventDefault();

    if (!marketOpen) {
      toast.error("Market is closed. Trading available: 9:15 AM - 3:30 PM IST");
      return;
    }

    if (!selectedPortfolio) {
      toast.error("Please select a portfolio");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE}/paper-trades/create_paper_trade/`,
        {
          portfolio_id: selectedPortfolio,
          symbol: newTrade.symbol,
          side: newTrade.side,
          entry_price: newTrade.entry_price,
          quantity: newTrade.quantity,
          stop_loss: newTrade.stop_loss,
          target_1: newTrade.target_1,
          target_2: newTrade.target_2,
          target_3: newTrade.target_3,
          target_4: newTrade.target_4,
          capital: portfolios.find(p => p.id === selectedPortfolio)?.capital,
        }
      );

      if (response.data.success) {
        toast.success(`Trade placed: ${newTrade.side} ${newTrade.quantity} ${newTrade.symbol}`);
        setNewTrade({
          symbol: "INFY",
          side: "BUY",
          quantity: 10,
          entry_price: 1500,
          stop_loss: 1485,
          target_1: 1530,
          target_2: 1550,
          target_3: 1570,
          target_4: 1590,
        });
        setShowNewTrade(false);
        loadActiveTrades();
        loadStats();
      } else {
        const errors = response.data.validation?.errors || [];
        const warnings = response.data.validation?.warnings || [];
        errors.forEach(e => toast.error(e));
        warnings.forEach(w => toast(w, { icon: "⚠️" }));
      }
    } catch (error) {
      toast.error(error.response?.data?.error || "Failed to create trade");
    } finally {
      setLoading(false);
    }
  };

  const handleCloseTrade = async (tradeId, exitPrice, exitType) => {
    try {
      const response = await axios.post(
        `${API_BASE}/paper-trades/${tradeId}/close_paper_trade/`,
        {
          exit_price: exitPrice,
          exit_type: exitType,
        }
      );

      if (response.data.success) {
        const result = response.data.result;
        toast.success(
          `Trade closed: ${result.pnl_percent > 0 ? "+" : ""}${result.pnl_percent.toFixed(2)}% | P&L: ₹${result.net_pnl.toFixed(0)}`
        );
        loadActiveTrades();
        loadClosedTrades();
        loadStats();
      }
    } catch (error) {
      toast.error(error.response?.data?.error || "Failed to close trade");
    }
  };

  const getTotalCapital = () => {
    const portfolio = portfolios.find(p => p.id === selectedPortfolio);
    return portfolio?.capital || 0;
  };

  const getActiveValue = () => {
    return activeTrades.reduce((sum, t) => sum + (t.entry_value || 0), 0);
  };

  const getUnrealizedPnL = () => {
    return activeTrades.reduce((sum, t) => sum + (t.unrealized_pnl || 0), 0);
  };

  const getTotalPnL = () => {
    const realized = closedTrades.reduce((sum, t) => sum + (t.profit_loss || 0), 0);
    return realized + getUnrealizedPnL();
  };

  const getWinRate = () => {
    if (closedTrades.length === 0) return 0;
    const winners = closedTrades.filter(t => (t.profit_loss || 0) > 0).length;
    return ((winners / closedTrades.length) * 100).toFixed(1);
  };

  return (
    <div className="space-y-6">
      {marketStatusInfo && (
        <div className={`rounded-lg shadow-md p-4 text-white ${marketOpen ? "bg-green-600" : "bg-red-600"}`}>
          <div className="flex justify-between items-center">
            <div className="text-lg font-semibold">
              {marketOpen ? "🟢 Market Open - Live Trading" : "🔒 Market Closed"}
            </div>
            <div className="text-sm">
              {marketOpen ? "Open: 9:15 AM - 3:30 PM (IST)" : `Opens: ${marketStatusInfo.timeUntilOpen || 'Tomorrow'}`}
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-900">📊 Paper Trading</h1>
        <p className="text-gray-600 mt-2">Practice trading with virtual capital - fully synced with live market prices</p>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Portfolio</label>
          <select
            value={selectedPortfolio || ""}
            onChange={(e) => setSelectedPortfolio(parseInt(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          >
            <option value="">Choose a portfolio...</option>
            {portfolios.map(p => (
              <option key={p.id} value={p.id}>{p.name} - ₹{(p.capital || 0).toLocaleString()}</option>
            ))}
          </select>
        </div>
      </div>

      {selectedPortfolio && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-white rounded-lg shadow-md p-4">
              <p className="text-sm text-gray-600 mb-1">Paper Capital</p>
              <p className="text-2xl font-bold text-gray-900">₹{getTotalCapital().toLocaleString()}</p>
              <p className="text-xs text-gray-500 mt-1">Available for trading</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4">
              <p className="text-sm text-gray-600 mb-1">Active Value</p>
              <p className="text-2xl font-bold text-blue-600">₹{getActiveValue().toLocaleString()}</p>
              <p className="text-xs text-gray-500 mt-1">{activeTrades.length} open trades</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4">
              <p className="text-sm text-gray-600 mb-1">Unrealized P&L</p>
              <p className={`text-2xl font-bold ${getUnrealizedPnL() >= 0 ? "text-green-600" : "text-red-600"}`}>
                {getUnrealizedPnL() >= 0 ? "+" : ""}₹{getUnrealizedPnL().toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 mt-1">Live trades</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4">
              <p className="text-sm text-gray-600 mb-1">Total P&L</p>
              <p className={`text-2xl font-bold ${getTotalPnL() >= 0 ? "text-green-600" : "text-red-600"}`}>
                {getTotalPnL() >= 0 ? "+" : ""}₹{getTotalPnL().toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 mt-1">All trades</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4">
              <p className="text-sm text-gray-600 mb-1">Win Rate</p>
              <p className="text-2xl font-bold text-primary">{getWinRate()}%</p>
              <p className="text-xs text-gray-500 mt-1">{closedTrades.length} closed</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setShowNewTrade(!showNewTrade)}
              disabled={!marketOpen || loading}
              className="bg-gradient-to-r from-primary to-secondary text-white font-semibold py-2 px-6 rounded-lg hover:shadow-lg transition disabled:opacity-50"
            >
              New Trade
            </button>
            <button
              onClick={loadActiveTrades}
              className="bg-blue-600 text-white font-semibold py-2 px-6 rounded-lg hover:shadow-lg transition"
            >
              🔄 Sync Prices ({refreshTimer}s)
            </button>
          </div>

          {showNewTrade && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Create New Paper Trade</h3>
              <form onSubmit={handleCreateTrade} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Symbol</label>
                    <input
                      type="text"
                      value={newTrade.symbol}
                      onChange={(e) => setNewTrade({ ...newTrade, symbol: e.target.value.toUpperCase() })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Side</label>
                    <select
                      value={newTrade.side}
                      onChange={(e) => setNewTrade({ ...newTrade, side: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    >
                      <option value="BUY">BUY</option>
                      <option value="SELL">SELL</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                    <input
                      type="number"
                      value={newTrade.quantity}
                      onChange={(e) => setNewTrade({ ...newTrade, quantity: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Entry Price (₹)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={newTrade.entry_price}
                      onChange={(e) => setNewTrade({ ...newTrade, entry_price: parseFloat(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Stop Loss (₹)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={newTrade.stop_loss}
                      onChange={(e) => setNewTrade({ ...newTrade, stop_loss: parseFloat(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Risk %</label>
                    <input
                      type="number"
                      disabled
                      value={((Math.abs(newTrade.entry_price - newTrade.stop_loss) / newTrade.entry_price) * 100).toFixed(2)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Profit Targets</h4>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {[1, 2, 3, 4].map((i) => (
                      <input
                        key={i}
                        type="number"
                        step="0.01"
                        placeholder={`T${i}`}
                        value={newTrade[`target_${i}`]}
                        onChange={(e) => setNewTrade({ ...newTrade, [`target_${i}`]: parseFloat(e.target.value) })}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary text-sm"
                      />
                    ))}
                  </div>
                </div>

                <div className="flex gap-2 pt-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-green-600 text-white font-semibold py-2 rounded-lg hover:shadow-lg transition disabled:opacity-50"
                  >
                    {loading ? "Creating..." : "Create Trade"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowNewTrade(false)}
                    className="flex-1 bg-gray-300 text-gray-700 font-semibold py-2 rounded-lg hover:shadow-lg transition"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {activeTrades.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">📈 Open Trades ({activeTrades.length})</h3>
              <div className="space-y-4">
                {activeTrades.map((trade) => (
                  <div key={trade.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="text-lg font-bold text-gray-900">
                          {trade.side === "BUY" ? "📈" : "📉"} {trade.stock.symbol} × {trade.quantity}
                        </h4>
                        <p className="text-sm text-gray-600">Entry: ₹{trade.entry_price.toFixed(2)} | Current: ₹{trade.current_price?.toFixed(2) || "N/A"}</p>
                      </div>
                      <span className={`text-2xl font-bold ${(trade.unrealized_pnl || 0) >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {(trade.unrealized_pnl || 0) >= 0 ? "+" : ""}₹{(trade.unrealized_pnl || 0).toFixed(0)}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-4 text-sm">
                      <div>
                        <p className="text-gray-600">Stop Loss</p>
                        <p className="font-semibold text-red-600">₹{trade.stop_loss.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Target 1</p>
                        <p className="font-semibold text-green-600">₹{trade.target_1?.toFixed(2) || "—"}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Target 2</p>
                        <p className="font-semibold text-green-600">₹{trade.target_2?.toFixed(2) || "—"}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Target 3</p>
                        <p className="font-semibold text-green-600">₹{trade.target_3?.toFixed(2) || "—"}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Target 4</p>
                        <p className="font-semibold text-green-600">₹{trade.target_4?.toFixed(2) || "—"}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Risk %</p>
                        <p className="font-semibold">{trade.risk_percent?.toFixed(2)}%</p>
                      </div>
                    </div>

                    <div className="flex gap-2 flex-wrap">
                      {trade.target_1 && (
                        <button
                          onClick={() => handleCloseTrade(trade.id, trade.target_1, "TARGET")}
                          className="bg-green-600 text-white font-semibold py-2 px-3 rounded text-sm hover:shadow-lg transition"
                        >
                          🎯 T1: ₹{trade.target_1.toFixed(2)}
                        </button>
                      )}
                      {trade.target_2 && (
                        <button
                          onClick={() => handleCloseTrade(trade.id, trade.target_2, "TARGET")}
                          className="bg-green-600 text-white font-semibold py-2 px-3 rounded text-sm hover:shadow-lg transition"
                        >
                          🎯 T2: ₹{trade.target_2.toFixed(2)}
                        </button>
                      )}
                      <button
                        onClick={() => handleCloseTrade(trade.id, trade.stop_loss, "STOPLOSS")}
                        className="bg-red-600 text-white font-semibold py-2 px-3 rounded text-sm hover:shadow-lg transition"
                      >
                        🛑 SL: ₹{trade.stop_loss.toFixed(2)}
                      </button>
                      <input
                        type="number"
                        step="0.01"
                        placeholder="Manual exit price"
                        id={`manual-exit-${trade.id}`}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm"
                      />
                      <button
                        onClick={() => {
                          const exitPrice = parseFloat(document.getElementById(`manual-exit-${trade.id}`).value);
                          if (exitPrice > 0) {
                            handleCloseTrade(trade.id, exitPrice, "MANUAL");
                          } else {
                            toast.error("Enter valid exit price");
                          }
                        }}
                        className="bg-blue-600 text-white font-semibold py-2 px-3 rounded text-sm hover:shadow-lg transition"
                      >
                        Exit
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {closedTrades.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">✅ Closed Trades ({closedTrades.length})</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left font-semibold">Stock</th>
                      <th className="px-4 py-2 text-left font-semibold">Side</th>
                      <th className="px-4 py-2 text-left font-semibold">Qty</th>
                      <th className="px-4 py-2 text-left font-semibold">Entry</th>
                      <th className="px-4 py-2 text-left font-semibold">Exit</th>
                      <th className="px-4 py-2 text-left font-semibold">Type</th>
                      <th className="px-4 py-2 text-left font-semibold">P&L</th>
                      <th className="px-4 py-2 text-left font-semibold">Return %</th>
                      <th className="px-4 py-2 text-left font-semibold">Commission</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {closedTrades.map((trade) => (
                      <tr key={trade.id} className="hover:bg-gray-50">
                        <td className="px-4 py-2 font-semibold">{trade.stock.symbol}</td>
                        <td className="px-4 py-2">{trade.side === "BUY" ? "📈 BUY" : "📉 SELL"}</td>
                        <td className="px-4 py-2">{trade.quantity}</td>
                        <td className="px-4 py-2">₹{trade.entry_price.toFixed(2)}</td>
                        <td className="px-4 py-2">₹{trade.exit_price?.toFixed(2)}</td>
                        <td className="px-4 py-2 text-xs">
                          {trade.exit_type === "TARGET" && "🎯 Target"}
                          {trade.exit_type === "STOPLOSS" && "🛑 Stop"}
                          {trade.exit_type === "MANUAL" && "✋ Manual"}
                        </td>
                        <td className={`px-4 py-2 font-semibold ${(trade.profit_loss || 0) >= 0 ? "text-green-600" : "text-red-600"}`}>
                          {(trade.profit_loss || 0) >= 0 ? "+" : ""}₹{(trade.profit_loss || 0).toFixed(0)}
                        </td>
                        <td className={`px-4 py-2 font-semibold ${(trade.profit_loss_percent || 0) >= 0 ? "text-green-600" : "text-red-600"}`}>
                          {(trade.profit_loss_percent || 0) >= 0 ? "+" : ""}{(trade.profit_loss_percent || 0).toFixed(2)}%
                        </td>
                        <td className="px-4 py-2 text-red-600">₹{((trade.entry_commission || 0) + (trade.exit_commission || 0)).toFixed(0)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg shadow-md p-6">
                <p className="text-sm text-gray-600 mb-2">Total Realized P&L</p>
                <p className={`text-3xl font-bold ${stats.total_realized_pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                  {stats.total_realized_pnl >= 0 ? "+" : ""}₹{stats.total_realized_pnl.toLocaleString()}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <p className="text-sm text-gray-600 mb-2">Profit Factor</p>
                <p className="text-3xl font-bold text-primary">{stats.profit_factor?.toFixed(2)}x</p>
                <p className="text-xs text-gray-500 mt-1">Avg Win / Avg Loss</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <p className="text-sm text-gray-600 mb-2">Winners / Losers</p>
                <p className="text-3xl font-bold text-primary">{stats.winners} / {stats.losers}</p>
                <p className="text-xs text-gray-500 mt-1">{stats.win_rate}% win rate</p>
              </div>
            </div>
          )}

          {activeTrades.length === 0 && closedTrades.length === 0 && (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <p className="text-gray-600 text-lg">No trades yet</p>
              <p className="text-gray-400">Open your first paper trade to start practicing</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
