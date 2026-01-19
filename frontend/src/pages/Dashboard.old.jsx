import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { recommendationApi } from "../api/endpoints";

export default function Dashboard() {
  const [stockInput, setStockInput] = useState("");
  const [selectedStock, setSelectedStock] = useState("");
  const [tradingStyle, setTradingStyle] = useState("SWING");
  const [capital, setCapital] = useState("100000");
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [marketStatus, setMarketStatus] = useState("CLOSED");
  const [dataType, setDataType] = useState("PREVIOUS");
  const [error, setError] = useState(null);

  useEffect(() => {
    const detectMarketStatus = () => {
      const now = new Date();
      const hours = now.getHours();
      const minutes = now.getMinutes();
      const dayOfWeek = now.getDay(); 
      const isWeekday = dayOfWeek > 0 && dayOfWeek < 6;
      const isMarketHours = (hours > 9 || (hours === 9 && minutes >= 15)) &&
                            (hours < 15 || (hours === 15 && minutes <= 30));

      const holidays = [
        "2026-01-26", 
        "2026-03-25", 
        "2026-04-14", 
        "2026-08-15", 
        "2026-09-02", 
        "2026-10-02", 
        "2026-10-25", 
        "2026-12-25", 
      ];

      const today = now.toISOString().split("T")[0];
      const isHoliday = holidays.includes(today);

      if (isHoliday) {
        setMarketStatus("HOLIDAY");
        setDataType("PREVIOUS");
      } else if (isWeekday && isMarketHours) {
        setMarketStatus("OPEN");
        setDataType("LIVE");
      } else {
        setMarketStatus("CLOSED");
        setDataType("PREVIOUS");
      }
    };

    detectMarketStatus();
    const interval = setInterval(detectMarketStatus, 60000);
    return () => clearInterval(interval);
  }, []);

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
      const recommendationResponse = await recommendationApi.generateRecommendation({
        stock_symbol: stock,
        trading_style: tradingStyle,
        capital: parseFloat(capital),
      });

      const recommendation = recommendationResponse.data;

      const completeAnalysis = {
        ...recommendation,
        marketStatus,
        dataType,
        timestamp: new Date().toLocaleString("en-IN"),
        capitalRisk: (parseFloat(capital) * 0.01).toFixed(2), 
      };

      setAnalysis(completeAnalysis);
      toast.success(`✅ Analysis complete for ${stock}`);
    } catch (err) {
      const message = err.response?.data?.error || err.message || "Analysis failed";
      setError(message);
      toast.error(`❌ ${message}`);
      console.error("Analysis error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const getMarketStatusColor = () => {
    switch (marketStatus) {
      case "OPEN":
        return "bg-green-100 text-green-800 border-green-300";
      case "CLOSED":
        return "bg-red-100 text-red-800 border-red-300";
      case "HOLIDAY":
        return "bg-orange-100 text-orange-800 border-orange-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getMarketStatusIcon = () => {
    switch (marketStatus) {
      case "OPEN":
        return "🟢";
      case "CLOSED":
        return "🔴";
      case "HOLIDAY":
        return "🟠";
      default:
        return "⚪";
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="bg-gradient-to-r from-primary to-secondary text-white rounded-lg p-6 shadow-lg">
        <h1 className="text-3xl font-bold">📊 Trading Dashboard</h1>
        <p className="text-gray-100 mt-2">AI-Powered Stock Analysis & Trading Recommendations</p>
      </div>

      <div className={`border-2 rounded-lg p-4 ${getMarketStatusColor()}`}>
        <div className="flex justify-between items-center">
          <div>
            <p className="font-bold text-lg">
              {getMarketStatusIcon()} Market Status: {marketStatus}
            </p>
            <p className="text-sm opacity-75">
              Data Type: {dataType === "LIVE" ? "🔴 LIVE" : "📊 PREVIOUS SESSION"}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs opacity-75">Last Updated:</p>
            <p className="text-sm font-mono">{new Date().toLocaleTimeString("en-IN")}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">🔍 Stock Analysis</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Stock Symbol
            </label>
            <input
              type="text"
              value={stockInput}
              onChange={(e) => setStockInput(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === "Enter" && handleAnalyze()}
              placeholder="Enter stock symbol (e.g., INFY, TCS, HDFCBANK)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary uppercase"
            />
            <p className="text-xs text-gray-500 mt-1">
              💡 Type any stock symbol and press Enter or click Analyze
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Trading Style
            </label>
            <select
              value={tradingStyle}
              onChange={(e) => setTradingStyle(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
            >
              <option value="INTRADAY">⚡ Intraday (Same Day)</option>
              <option value="SWING">📈 Swing (2-5 Days)</option>
              <option value="POSITIONAL">📊 Positional (Weeks)</option>
              <option value="INVESTMENT">💼 Investment (Months+)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Trading Capital (₹)
            </label>
            <input
              type="number"
              value={capital}
              onChange={(e) => setCapital(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              min="10000"
              step="10000"
            />
            <p className="text-xs text-gray-500 mt-1">
              Max Risk (1%): ₹{(parseFloat(capital) * 0.01).toFixed(0)}
            </p>
          </div>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={isLoading || !stockInput.trim()}
          className="w-full bg-gradient-to-r from-primary to-secondary text-white font-bold py-3 rounded-lg hover:shadow-lg transition disabled:opacity-50"
        >
          {isLoading ? "🔄 Analyzing..." : "📊 Analyze & Generate Recommendation"}
        </button>

        {error && (
          <div className="mt-4 bg-red-50 border border-red-300 text-red-700 p-4 rounded-lg">
            <p className="font-semibold">❌ Error:</p>
            <p className="text-sm">{error}</p>
            <p className="text-xs mt-2 text-gray-600">
              💡 Make sure you selected a valid stock (INFY, TCS, HDFCBANK)
            </p>
          </div>
        )}
      </div>

      {analysis && (
        <div className="space-y-6">
          <div className="bg-blue-50 border border-blue-300 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>ℹ️ Market Status Impact:</strong>{" "}
              {marketStatus === "CLOSED" &&
                "Market is closed. Displaying last available data from previous session."}
              {marketStatus === "HOLIDAY" &&
                "Market is closed for holiday. Analysis based on last available data."}
              {marketStatus === "OPEN" &&
                "Market is open. Displaying real-time data and live predictions."}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              {analysis.stock.symbol} - {analysis.stock.name}
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-xs text-gray-600">Current Price</p>
                <p className="text-2xl font-bold text-primary">
                  ₹{parseFloat(analysis.analysis.current_price || 0).toFixed(2)}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-xs text-gray-600">Previous Close</p>
                <p className="text-2xl font-bold text-secondary">
                  ₹{parseFloat(analysis.stock.previous_close || 0).toFixed(2)}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-xs text-gray-600">Trend</p>
                <p className="text-2xl font-bold">
                  {analysis.analysis.trend === "BULLISH" ? "🟢 Bullish" : "🔴 Bearish"}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-xs text-gray-600">Probability</p>
                <p className="text-2xl font-bold text-blue-600">
                  {(analysis.analysis.trend_probability || 0).toFixed(0)}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">💡 Trading Recommendation</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className={`p-6 rounded-lg text-white ${
                analysis.signal === "BUY"
                  ? "bg-gradient-to-r from-green-500 to-green-600"
                  : analysis.signal === "SELL"
                  ? "bg-gradient-to-r from-red-500 to-red-600"
                  : "bg-gradient-to-r from-yellow-500 to-yellow-600"
              }`}>
                <p className="text-sm opacity-90">Signal</p>
                <p className="text-4xl font-bold">{analysis.signal || "HOLD"}</p>
                <p className="text-xs mt-2 opacity-90">{analysis.reasoning || "No reasoning available"}</p>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-red-50 p-6 rounded-lg border-2 border-orange-200">
                <p className="font-bold text-gray-900 mb-2">⚠️ Risk Management</p>
                <div className="space-y-1 text-sm">
                  <p>
                    <strong>Max Risk (1%):</strong> ₹{analysis.capitalRisk}
                  </p>
                  <p>
                    <strong>Risk/Reward:</strong> 1:{(analysis.risk_reward_ratio || 1.5).toFixed(1)}
                  </p>
                  <p>
                    <strong>Position Size:</strong>{" "}
                    {analysis.position_size || Math.round(parseFloat(capital) / parseFloat(analysis.analysis.current_price || 1))} shares
                  </p>
                  <p className="text-xs text-gray-600 mt-2">
                    ✓ All recommendations follow strict 1% risk per trade rule
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">🎯 Trading Levels</h3>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                <p className="text-xs text-gray-600 font-semibold">ENTRY</p>
                <p className="text-xl font-bold text-blue-600 mt-1">
                  ₹{parseFloat(analysis.entry_price || 0).toFixed(2)}
                </p>
              </div>

              {[
                { label: "TARGET 1", key: "target_1", color: "green" },
                { label: "TARGET 2", key: "target_2", color: "green" },
                { label: "TARGET 3", key: "target_3", color: "green" },
              ].map((target) => (
                <div
                  key={target.key}
                  className={`bg-${target.color}-50 p-4 rounded-lg border-l-4 border-${target.color}-500`}
                >
                  <p className="text-xs text-gray-600 font-semibold">{target.label}</p>
                  <p className={`text-xl font-bold text-${target.color}-600 mt-1`}>
                    ₹{parseFloat(analysis[target.key] || 0).toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    +{(
                      ((parseFloat(analysis[target.key] || 0) - parseFloat(analysis.entry_price || 0)) /
                        parseFloat(analysis.entry_price || 1)) *
                      100
                    ).toFixed(1)}
                    %
                  </p>
                </div>
              ))}

              <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                <p className="text-xs text-gray-600 font-semibold">STOP LOSS</p>
                <p className="text-xl font-bold text-red-600 mt-1">
                  ₹{parseFloat(analysis.stop_loss || 0).toFixed(2)}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {(
                    ((parseFloat(analysis.stop_loss || 0) - parseFloat(analysis.entry_price || 0)) /
                      parseFloat(analysis.entry_price || 1)) *
                    100
                  ).toFixed(1)}
                  %
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">⭐ Pro+ Technical Analysis</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-semibold text-gray-900 mb-2">Support & Resistance</p>
                <p className="text-sm">
                  <strong>Support:</strong> ₹
                  {parseFloat(analysis.analysis.support_level || 0).toFixed(2)}
                </p>
                <p className="text-sm">
                  <strong>Resistance:</strong> ₹
                  {parseFloat(analysis.analysis.resistance_level || 0).toFixed(2)}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-semibold text-gray-900 mb-2">RSI (14)</p>
                <p className="text-3xl font-bold text-primary">
                  {parseFloat(analysis.analysis.rsi || 0).toFixed(0)}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  {analysis.analysis.rsi > 70
                    ? "⚠️ Overbought"
                    : analysis.analysis.rsi < 30
                    ? "✅ Oversold"
                    : "➡️ Neutral"}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-semibold text-gray-900 mb-2">Volume Analysis</p>
                <p className="text-2xl font-bold text-secondary">
                  {((analysis.analysis.volume || 0) / 1000000).toFixed(1)}M
                </p>
                <p className="text-xs text-gray-600 mt-1">{analysis.analysis.volume_trend || "Normal"}</p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-semibold text-gray-900 mb-2">Moving Averages</p>
                <p className="text-sm">
                  <strong>EMA 12:</strong> ₹{parseFloat(analysis.analysis.ema_12 || 0).toFixed(2)}
                </p>
                <p className="text-sm">
                  <strong>EMA 26:</strong> ₹{parseFloat(analysis.analysis.ema_26 || 0).toFixed(2)}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-semibold text-gray-900 mb-2">Bollinger Bands</p>
                <p className="text-xs">
                  Upper: ₹{parseFloat(analysis.analysis.bollinger_upper || 0).toFixed(2)}
                </p>
                <p className="text-xs">
                  Mid: ₹{parseFloat(analysis.analysis.bollinger_middle || 0).toFixed(2)}
                </p>
                <p className="text-xs">
                  Lower: ₹{parseFloat(analysis.analysis.bollinger_lower || 0).toFixed(2)}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-semibold text-gray-900 mb-2">VWAP</p>
                <p className="text-2xl font-bold text-blue-600">
                  ₹{parseFloat(analysis.analysis.vwap || 0).toFixed(2)}
                </p>
                <p className="text-xs text-gray-600 mt-1">Volume Weighted Avg Price</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">💼 Investment Options</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                <p className="font-semibold text-blue-900">Direct Equity</p>
                <p className="text-sm text-gray-600 mt-2">
                  Trade {analysis.stock.symbol} directly for maximum returns
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                <p className="font-semibold text-green-900">Index Funds</p>
                <p className="text-sm text-gray-600 mt-2">
                  Balanced portfolio with lower risk through Nifty/Sensex ETFs
                </p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
                <p className="font-semibold text-purple-900">Mutual Funds</p>
                <p className="text-sm text-gray-600 mt-2">
                  Professional fund management with diversified holdings
                </p>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
            <p className="text-xs text-yellow-800">
              <strong>⚖️ Disclaimer:</strong> This analysis is for educational purposes only. Always
              conduct your own research and consult a financial advisor before trading. Past
              performance does not guarantee future results.
            </p>
          </div>
        </div>
      )}

      {!analysis && !isLoading && (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <p className="text-2xl font-bold text-gray-900">👋 Welcome to Trading Dashboard</p>
          <p className="text-gray-600 mt-2">
            Select a stock, set your trading parameters, and click "Analyze" to get started
          </p>
          <p className="text-sm text-gray-500 mt-4">
            💡 Tip: The AI uses live market data when the market is open, and previous session data
            when closed
          </p>
        </div>
      )}
    </div>
  );
}
