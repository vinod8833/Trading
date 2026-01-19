import React, { useState, useEffect } from "react";
import { intradayApi, recommendationApi } from "../api/endpoints";
import { useTradingStore } from "../store";
import toast from "react-hot-toast";
import { riskManagement, marketStatus, formatters } from "../utils/tradingEngine";

export default function Signals() {
  const [signals, setSignals] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("all");
  const [selectedMode] = useTradingStore((s) => [s.selectedMode]);
  const [marketOpen, setMarketOpen] = useState(false);
  const [defaultCapital, setDefaultCapital] = useState(100000);

  useEffect(() => {
    fetchSignals();
  }, [activeTab]);

  useEffect(() => {
    const updateMarketStatus = () => {
      setMarketOpen(marketStatus.isMarketOpen());
    };

    updateMarketStatus();
    const timer = setInterval(updateMarketStatus, 60000);
    return () => clearInterval(timer);
  }, []);

  const fetchSignals = async () => {
    setIsLoading(true);
    try {
      let response;
      let apiError = null;

      try {
        response =
          activeTab === "intraday"
            ? await intradayApi.getIntradaySignals()
            : await recommendationApi.getActiveSignals();
      } catch (err) {
        console.error("API Error fetching signals:", err);
        apiError = err;
        
        if (err.response?.status === 404) {
          toast.error("Signals endpoint not found. Please analyze stocks first.");
        } else if (err.response?.status === 401) {
          toast.error("Authentication failed. Please log in again.");
        } else if (err.response?.status >= 500) {
          toast.error("Server error. Try again in a moment.");
        } else if (err.message === 'Network Error') {
          toast.error("Network error. Check your connection.");
        } else {
          toast.error("Failed to load signals. Using analysis mode.");
        }
        
        response = { data: [] };
      }

      const signalList = Array.isArray(response.data) 
        ? response.data 
        : response.data?.results || [];

      const enhancedSignals = (signalList || []).map(signal => {
        const hasValidPrices = signal.entry_price && signal.target_1 && signal.stop_loss;
        
        return {
          ...signal,
          market_status: marketOpen ? 'LIVE' : 'HISTORICAL',
          riskReward: hasValidPrices
            ? riskManagement.calculateRiskReward(signal.entry_price, signal.target_1, signal.stop_loss)
            : 0,
          expectedProfit: signal.entry_price && signal.target_1
            ? ((signal.target_1 - signal.entry_price) / signal.entry_price * 100).toFixed(2)
            : 0,
          expectedLoss: signal.entry_price && signal.stop_loss
            ? ((signal.stop_loss - signal.entry_price) / signal.entry_price * 100).toFixed(2)
            : 0,
          pnlData: hasValidPrices
            ? riskManagement.calculatePnL(
                defaultCapital,
                signal.entry_price,
                [signal.target_1, signal.target_2, signal.target_3],
                signal.stop_loss
              )
            : null,
          isValid: hasValidPrices,
          marketWarning: !marketOpen ? 'Market closed - Historical analysis' : null
        };
      });

      setSignals(enhancedSignals);

      if (enhancedSignals.length === 0) {
        if (apiError) {
          toast.info("No signals fetched. " + (marketOpen 
            ? "Generate new signals from Stock Analysis."
            : "Signals will be available when market opens."));
        } else {
          toast.info("No signals available. Analyze stocks to generate recommendations.");
        }
      } else {
        const validCount = enhancedSignals.filter(s => s.isValid).length;
        toast.success(`Loaded ${validCount} signal(s). ${marketOpen ? 'Live market.' : 'Market closed - Analysis mode.'}`);
      }
    } catch (error) {
      console.error("Signal fetch error:", error);
      
      const errorMsg = error.response?.data?.detail 
        || error.message 
        || "Failed to fetch signals";
      
      toast.error("Unable to load signals: " + errorMsg);
      setSignals([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getSignalColor = (signal) => {
    switch (signal) {
      case "BUY":
        return "text-green-600 bg-green-50 border-green-300";
      case "SELL":
        return "text-red-600 bg-red-50 border-red-300";
      case "HOLD":
        return "text-yellow-600 bg-yellow-50 border-yellow-300";
      default:
        return "text-gray-600 bg-gray-50 border-gray-300";
    }
  };

  const getSignalIcon = (signal) => {
    switch (signal) {
      case "BUY":
        return "🟢";
      case "SELL":
        return "🔴";
      case "HOLD":
        return "🟡";
      default:
        return "⚪";
    }
  };

  return (
    <div className="space-y-6">
      {marketOpen ? (
        <div className="bg-green-50 border-l-4 border-green-400 rounded-lg p-4">
          <p className="font-semibold text-green-900">🟢 Market Open - Live Signals</p>
          <p className="text-sm text-green-700 mt-1">Showing real-time signals with calculated risk/reward</p>
        </div>
      ) : (
        <div className="bg-blue-50 border-l-4 border-blue-400 rounded-lg p-4">
          <p className="font-semibold text-blue-900">📊 Market Closed - Analysis Mode</p>
          <p className="text-sm text-blue-700 mt-1">Showing historical signals and last available analysis</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Capital for Risk Calculation</label>
        <input
          type="number"
          value={defaultCapital}
          onChange={(e) => setDefaultCapital(parseInt(e.target.value))}
          placeholder="₹100,000"
          min="1000"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
        />
        <p className="text-xs text-gray-500 mt-1">Used to calculate position sizing and expected P&L</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab("all")}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            activeTab === "all"
              ? "bg-primary text-white"
              : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
          }`}
        >
          All Signals
        </button>
        <button
          onClick={() => setActiveTab("intraday")}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            activeTab === "intraday"
              ? "bg-primary text-white"
              : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
          }`}
        >
          ⚡ Intraday
        </button>
      </div>

      {isLoading ? (
        <div className="bg-blue-50 rounded-lg shadow-md p-12 text-center border border-blue-200">
          <div className="inline-block animate-spin text-4xl">⏳</div>
          <p className="text-blue-600 mt-4 font-semibold">Loading signals...</p>
          <p className="text-blue-500 text-sm mt-2">Fetching latest trade recommendations</p>
        </div>
      ) : signals.length === 0 ? (
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg shadow-md p-12 text-center border-2 border-dashed border-gray-300">
          <p className="text-3xl mb-4">🎯</p>
          <p className="text-gray-800 text-xl font-semibold">No Signals Available Yet</p>
          <p className="text-gray-600 mt-3">Signals are generated based on stock analysis</p>
          <div className="mt-6 text-sm text-gray-600 space-y-2">
            <p><span className="font-semibold">✓</span> Visit Stock Analysis page</p>
            <p><span className="font-semibold">✓</span> Generate recommendations</p>
            <p><span className="font-semibold">✓</span> Return here to see signals</p>
          </div>
          <div className="mt-6 pt-6 border-t border-gray-300">
            <p className="text-xs text-gray-500">Signals are available {marketOpen ? "now (live market)" : "when you generate new recommendations"}</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {signals.map((signal) => (
            <div
              key={signal.id}
              className={`rounded-lg shadow-md p-6 border-l-4 ${getSignalColor(signal.signal)}`}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-2xl font-bold">{getSignalIcon(signal.signal)} {signal.stock_symbol}</h3>
                  <p className="text-sm text-gray-600">{signal.created_at}</p>
                </div>
                <span className="text-xl font-bold bg-white bg-opacity-70 px-3 py-1 rounded">
                  {signal.signal}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2 mb-4 pb-4 border-b">
                <div className="bg-white bg-opacity-60 p-2 rounded">
                  <p className="text-xs text-gray-600">Entry</p>
                  <p className="font-bold">₹{signal.entry_price}</p>
                </div>
                <div className="bg-white bg-opacity-60 p-2 rounded">
                  <p className="text-xs text-gray-600">Stop Loss</p>
                  <p className="font-bold">₹{signal.stop_loss}</p>
                </div>
                <div className="bg-white bg-opacity-60 p-2 rounded">
                  <p className="text-xs text-gray-600">Target 1</p>
                  <p className="font-bold">₹{signal.target_1}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4 pb-4 border-b">
                <div className="bg-white bg-opacity-60 p-3 rounded text-center">
                  <p className="text-xs text-gray-600">Risk/Reward</p>
                  <p className="text-lg font-bold text-blue-600">1:{signal.riskReward}</p>
                </div>
                <div className="bg-white bg-opacity-60 p-3 rounded text-center">
                  <p className="text-xs text-gray-600">Win Probability</p>
                  <p className="text-lg font-bold text-purple-600">{signal.win_probability}%</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-green-100 bg-opacity-50 p-3 rounded">
                  <p className="text-xs text-gray-600">Expected Profit (if target)</p>
                  <p className="text-lg font-bold text-green-700">{signal.expectedProfit}%</p>
                </div>
                <div className="bg-red-100 bg-opacity-50 p-3 rounded">
                  <p className="text-xs text-gray-600">Max Loss (if stopped)</p>
                  <p className="text-lg font-bold text-red-700">{signal.expectedLoss}%</p>
                </div>
              </div>

              {signal.pnlData && signal.pnlData.valid && (
                <div className="bg-blue-100 bg-opacity-50 p-3 rounded mb-4">
                  <p className="text-xs text-gray-600">Position Size (1% Rule)</p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="font-bold">{signal.pnlData.position} units</span>
                    <span className="text-sm text-gray-700">Max Risk: ₹{signal.pnlData.maxRisk.toFixed(0)}</span>
                  </div>
                </div>
              )}

              {selectedMode === "pro" && (
                <div className="bg-white bg-opacity-60 p-3 rounded border-t pt-3 mt-3">
                  <p className="text-xs font-semibold text-gray-700 mb-2">Advanced Metrics</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <p className="text-gray-600">Target 2</p>
                      <p className="font-bold">₹{signal.target_2}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Target 3</p>
                      <p className="font-bold">₹{signal.target_3}</p>
                    </div>
                  </div>
                </div>
              )}

              <button className="w-full mt-4 bg-primary text-white py-2 rounded-lg hover:shadow-lg transition font-medium disabled:opacity-50"
                disabled={!marketOpen}>
                {marketOpen ? "Execute Trade" : "Market Closed"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
