import React, { useState } from "react";
import { recommendationApi } from "../api/endpoints";
import toast from "react-hot-toast";

export default function StockAnalysis() {
  const TRADING_STYLES = {
    INTRADAY: { label: "⚡ Intraday (Same Day)", desc: "VWAP focus, tight stops, quick profits" },
    SWING: { label: "📈 Swing (2-5 Days)", desc: "EMA + patterns, medium-term trends" },
    POSITIONAL: { label: "📊 Positional (Weeks)", desc: "Daily chart, trend structure" },
    INVESTMENT: { label: "💼 Investment (Months+)", desc: "200 EMA, long-term trends" },
  };

  const [stockInput, setStockInput] = useState("");
  const [selectedStock, setSelectedStock] = useState("");
  const [tradingStyle, setTradingStyle] = useState("SWING");
  const [capital, setCapital] = useState("100000");
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const handleAnalyze = async () => {
    const stock = stockInput.trim().toUpperCase();
    if (!stock) {
      toast.error("Please enter a stock symbol");
      return;
    }

    setSelectedStock(stock);
    setIsLoading(true);
    setError(null);

    try {
      const response = await recommendationApi.generateRecommendation({
        stock_symbol: stock,
        trading_style: tradingStyle,
        capital: parseFloat(capital),
      });

      setAnalysis({ ...response.data, timestamp: new Date().toLocaleString("en-IN") });
      toast.success(`Analysis complete for ${stock}`);
    } catch (err) {
      const message = err.response?.data?.error || "Analysis failed";
      setError(message);
      toast.error(`❌ ${message}`);
      console.error("Analysis error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const getTrendExplanation = (trend) => {
    if (trend === "BULLISH") {
      return { text: "Uptrend", color: "text-green-600", icon: "📈", meaning: "Buyers in control" };
    } else if (trend === "BEARISH") {
      return { text: "Downtrend", color: "text-red-600", icon: "📉", meaning: "Sellers in control" };
    }
    return { text: "Sideways", color: "text-gray-600", icon: "↔️", meaning: "Mixed signals" };
  };

  const getRSIInterpretation = (rsi) => {
    if (rsi > 70) return { text: "Overbought", color: "text-red-600" };
    if (rsi < 30) return { text: "Oversold", color: "text-green-600" };
    return { text: "Neutral", color: "text-blue-600" };
  };

  return (
    <div className="space-y-6 p-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6 shadow-lg">
        <h1 className="text-3xl font-bold">📊 Stock Analysis</h1>
        <p className="text-gray-100 mt-2">Complete technical analysis with trading strategy</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">🔍 Analysis Setup</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Stock Symbol</label>
            <input
              type="text"
              value={stockInput}
              onChange={(e) => setStockInput(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === "Enter" && handleAnalyze()}
              placeholder="Enter stock symbol (e.g., INFY, TCS, HDFCBANK)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 uppercase"
            />
            <p className="text-xs text-gray-500 mt-1">💡 Type any stock symbol</p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Trading Style</label>
            <select
              value={tradingStyle}
              onChange={(e) => setTradingStyle(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {Object.entries(TRADING_STYLES).map(([key, value]) => (
                <option key={key} value={key}>{value.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Trading Capital (₹)</label>
            <input
              type="number"
              value={capital}
              onChange={(e) => setCapital(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              min="10000"
              step="10000"
            />
          </div>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={isLoading || !stockInput.trim()}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 rounded-lg hover:shadow-lg transition disabled:opacity-50"
        >
          {isLoading ? "🔄 Analyzing..." : "📊 Generate Analysis"}
        </button>

        {error && (
          <div className="mt-4 bg-red-50 border border-red-300 text-red-700 p-4 rounded-lg">
            <p>❌ Error: {error}</p>
          </div>
        )}
      </div>

      {analysis && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-4 flex gap-2 overflow-x-auto">
            {[
              { id: "overview", label: "📌 Overview" },
              { id: "trend", label: "📈 Trend" },
              { id: "indicators", label: "⭐ Indicators" },
              { id: "levels", label: "🔑 Levels" },
              { id: "strategy", label: "💡 Strategy" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-semibold transition whitespace-nowrap ${
                  activeTab === tab.id ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === "overview" && (
            <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-xs text-gray-600">Stock</p>
                  <p className="text-lg font-bold text-blue-600 mt-1">{analysis.stock.symbol}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-xs text-gray-600">Price</p>
                  <p className="text-lg font-bold text-green-600 mt-1">₹{parseFloat(analysis.analysis.current_price).toFixed(2)}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-xs text-gray-600">Sector</p>
                  <p className="text-lg font-bold text-purple-600 mt-1">{analysis.stock.sector || "IT"}</p>
                </div>
                <div className={`${analysis.signal === "BUY" ? "bg-green-50" : "bg-red-50"} p-4 rounded-lg`}>
                  <p className="text-xs text-gray-600">Signal</p>
                  <p className={`text-lg font-bold mt-1 ${analysis.signal === "BUY" ? "text-green-600" : "text-red-600"}`}>
                    {analysis.signal}
                  </p>
                </div>
              </div>

              <div className={`p-6 rounded-lg text-white text-center ${analysis.signal === "BUY" ? "bg-green-600" : "bg-red-600"}`}>
                <p className="text-5xl font-bold">{analysis.signal}</p>
                <p className="mt-2 text-lg">Confidence: {analysis.win_probability}%</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-gray-600">Trend</p>
                  <p className="text-lg font-bold mt-1">{getTrendExplanation(analysis.analysis.trend).icon} {analysis.analysis.trend}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">RSI</p>
                  <p className={`text-lg font-bold mt-1 ${getRSIInterpretation(analysis.analysis.rsi).color}`}>
                    {parseFloat(analysis.analysis.rsi).toFixed(0)} - {getRSIInterpretation(analysis.analysis.rsi).text}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Entry</p>
                  <p className="text-lg font-bold text-blue-600 mt-1">₹{parseFloat(analysis.entry_price).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Risk/Reward</p>
                  <p className="text-lg font-bold text-blue-600 mt-1">1:{analysis.risk_reward_ratio.toFixed(1)}</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "trend" && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold mb-4">📈 Trend Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-green-50 p-6 rounded-lg border-l-4 border-green-500">
                  <p className="text-sm font-semibold text-green-900 mb-2">🟢 Support</p>
                  <p className="text-3xl font-bold text-green-600">₹{parseFloat(analysis.analysis.support_level).toFixed(2)}</p>
                  <p className="text-xs text-gray-600 mt-3">Price bounces up from here</p>
                </div>
                <div className="bg-red-50 p-6 rounded-lg border-l-4 border-red-500">
                  <p className="text-sm font-semibold text-red-900 mb-2">🔴 Resistance</p>
                  <p className="text-3xl font-bold text-red-600">₹{parseFloat(analysis.analysis.resistance_level).toFixed(2)}</p>
                  <p className="text-xs text-gray-600 mt-3">Price bounces down from here</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "indicators" && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold mb-4">⭐ Technical Indicators</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                  <p className="font-semibold mb-2">RSI (14)</p>
                  <p className="text-3xl font-bold text-blue-600">{parseFloat(analysis.analysis.rsi).toFixed(0)}</p>
                  <p className="text-xs text-gray-600 mt-2">{getRSIInterpretation(analysis.analysis.rsi).text}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
                  <p className="font-semibold mb-2">VWAP</p>
                  <p className="text-3xl font-bold text-purple-600">₹{parseFloat(analysis.analysis.vwap).toFixed(2)}</p>
                  <p className="text-xs text-gray-600 mt-2">Intraday support/resistance</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                  <p className="font-semibold mb-2">Volume</p>
                  <p className="text-3xl font-bold text-green-600">{(analysis.analysis.volume / 1000000).toFixed(1)}M</p>
                  <p className="text-xs text-gray-600 mt-2">{analysis.analysis.volume_trend}</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg border-l-4 border-orange-500">
                  <p className="font-semibold mb-2">EMAs</p>
                  <p className="text-sm">12: ₹{parseFloat(analysis.analysis.ema_12).toFixed(2)}</p>
                  <p className="text-sm">26: ₹{parseFloat(analysis.analysis.ema_26).toFixed(2)}</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "levels" && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold mb-4">🔑 Trading Levels</h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                  <p className="text-xs font-semibold">🎯 ENTRY</p>
                  <p className="text-2xl font-bold text-blue-600 mt-2">₹{parseFloat(analysis.entry_price).toFixed(2)}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                  <p className="text-xs font-semibold">📈 TARGET 1</p>
                  <p className="text-2xl font-bold text-green-600 mt-2">₹{parseFloat(analysis.target_1).toFixed(2)}</p>
                  <p className="text-xs text-gray-600 mt-1">+{(((parseFloat(analysis.target_1) - parseFloat(analysis.entry_price)) / parseFloat(analysis.entry_price)) * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                  <p className="text-xs font-semibold">📈 TARGET 2</p>
                  <p className="text-2xl font-bold text-green-600 mt-2">₹{parseFloat(analysis.target_2).toFixed(2)}</p>
                  <p className="text-xs text-gray-600 mt-1">+{(((parseFloat(analysis.target_2) - parseFloat(analysis.entry_price)) / parseFloat(analysis.entry_price)) * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                  <p className="text-xs font-semibold">📈 TARGET 3</p>
                  <p className="text-2xl font-bold text-green-600 mt-2">₹{parseFloat(analysis.target_3).toFixed(2)}</p>
                  <p className="text-xs text-gray-600 mt-1">+{(((parseFloat(analysis.target_3) - parseFloat(analysis.entry_price)) / parseFloat(analysis.entry_price)) * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                  <p className="text-xs font-semibold">🛡️ STOP LOSS</p>
                  <p className="text-2xl font-bold text-red-600 mt-2">₹{parseFloat(analysis.stop_loss).toFixed(2)}</p>
                  <p className="text-xs text-gray-600 mt-1">{(((parseFloat(analysis.stop_loss) - parseFloat(analysis.entry_price)) / parseFloat(analysis.entry_price)) * 100).toFixed(1)}%</p>
                </div>
              </div>

              <div className="bg-orange-50 p-6 rounded-lg border-l-4 border-orange-500">
                <p className="font-semibold mb-4">💰 Risk Management (1% Rule)</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs text-gray-600">Max Risk</p>
                    <p className="text-xl font-bold text-orange-600 mt-1">₹{(parseFloat(capital) * 0.01).toFixed(0)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Position Size</p>
                    <p className="text-xl font-bold text-orange-600 mt-1">
                      {Math.round((parseFloat(capital) * 0.01) / (parseFloat(analysis.entry_price) - parseFloat(analysis.stop_loss)))} shares
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Risk/Reward</p>
                    <p className="text-xl font-bold text-blue-600 mt-1">1:{analysis.risk_reward_ratio.toFixed(1)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Risk Level</p>
                    <p className="text-xl font-bold text-green-600 mt-1">Very Low ✅</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "strategy" && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold mb-4">💡 {TRADING_STYLES[tradingStyle].label}</h3>
              <p className="text-gray-700 mb-6">{TRADING_STYLES[tradingStyle].desc}</p>

              <div className="space-y-3">
                <div className="p-3 bg-gray-100 rounded-lg">
                  <p className="font-semibold">1️⃣ SETUP: Identify Entry</p>
                  <p className="text-sm text-gray-700">Entry at ₹{parseFloat(analysis.entry_price).toFixed(2)}</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <p className="font-semibold">2️⃣ WAIT: Confirm Signal</p>
                  <p className="text-sm text-gray-700">Wait for volume confirmation</p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <p className="font-semibold">3️⃣ ENTER: Buy Position</p>
                  <p className="text-sm text-gray-700">
                    Buy {Math.round((parseFloat(capital) * 0.01) / (parseFloat(analysis.entry_price) - parseFloat(analysis.stop_loss)))} shares
                  </p>
                </div>
                <div className="p-3 bg-yellow-100 rounded-lg">
                  <p className="font-semibold">4️⃣ PROTECT: Stop Loss</p>
                  <p className="text-sm text-gray-700">Set SL at ₹{parseFloat(analysis.stop_loss).toFixed(2)}</p>
                </div>
                <div className="p-3 bg-purple-100 rounded-lg">
                  <p className="font-semibold">5️⃣ PROFIT: Take Targets</p>
                  <p className="text-sm text-gray-700">T1: ₹{parseFloat(analysis.target_1).toFixed(2)} | T2: ₹{parseFloat(analysis.target_2).toFixed(2)} | T3: ₹{parseFloat(analysis.target_3).toFixed(2)}</p>
                </div>
              </div>

              <div className="mt-6 p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
                <p className="font-semibold text-red-900 mb-2">⚠️ Risk Warnings</p>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>✓ Never risk more than 1% of capital</li>
                  <li>✓ Always use stop loss</li>
                  <li>✓ Follow position size strictly</li>
                  <li>✓ Minimum risk/reward 1:2</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {!analysis && !isLoading && (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <p className="text-2xl font-bold text-gray-900">📊 Get Started</p>
          <p className="text-gray-600 mt-2">Select a stock and click "Generate Analysis"</p>
        </div>
      )}
    </div>
  );
}
