import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import {
  marketStatus,
  predictionControl,
  riskManagement,
  timeBasedGuidance,
  formatters
} from "../utils/tradingEngine";
import { recommendationApi } from "../api/endpoints";
import { apiClient } from "../api/client";

export default function StockAnalysisEnhanced() {
  const [selectedStock, setSelectedStock] = useState("");
  const [stockInput, setStockInput] = useState("");
  const [tradingStyle, setTradingStyle] = useState("SWING");
  const [capital, setCapital] = useState("100000");
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const [availableStocks, setAvailableStocks] = useState([]);
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [showStockSuggestions, setShowStockSuggestions] = useState(false);
  const [stocksLoading, setStocksLoading] = useState(false);

  const [marketOpen, setMarketOpen] = useState(false);
  const [marketStatusInfo, setMarketStatusInfo] = useState(null);

  const [predictionMode, setPredictionMode] = useState(null);

  const [showChartUpload, setShowChartUpload] = useState(false);
  const [chartFile, setChartFile] = useState(null);
  const [chartSymbol, setChartSymbol] = useState("");

  const [riskAssessment, setRiskAssessment] = useState(null);
  const [showRiskCalculator, setShowRiskCalculator] = useState(false);

  const TRADING_STYLES = [
    { value: "INTRADAY", label: "⚡ Intraday (Same Day)", desc: "Quick trades, high frequency" },
    { value: "SWING", label: "📊 Swing (2-5 Days)", desc: "Short-term trends" },
    { value: "POSITIONAL", label: "📈 Positional (Weeks)", desc: "Medium-term moves" },
    { value: "INVESTMENT", label: "🏦 Investment (Months+)", desc: "Long-term growth" }
  ];

  useEffect(() => {
    const updateMarketStatus = () => {
      const isOpen = marketStatus.isMarketOpen();
      const status = marketStatus.getMarketStatus();
      setMarketOpen(isOpen);
      setMarketStatusInfo(status);
      setPredictionMode(predictionControl.getPredictionMode(isOpen));
    };

    updateMarketStatus();
    const timer = setInterval(updateMarketStatus, 60000); 
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchAvailableStocks = async () => {
      try {
        setStocksLoading(true);
        const response = await apiClient.get("/api/stock-recommendations/get_all_sectors/?market=NSE");
        
        if (response.data?.sectors) {
          console.log("Available sectors:", response.data.sectors);
        }
        
        setAvailableStocks([
          "INFY", "TCS", "WIPRO", "HCLTECH", "TECHM", "LTIM",
          "RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "FEDERALBNK",
          "ASIANPAINT", "MARUTI", "M&M", "BOSCHLTD", "EICHERMOT",
          "SUNPHARMA", "DRREDDY", "CIPLA", "APOLLOHOSP",
          "LTIM", "LT", "SIEMENS", "ABB",
          "BRITANNIA", "NESTLEIND", "COLPAL",
          "BAJAJFINSV", "BAJAJHLDNG", "SBICARD", "SBILIFE"
        ].sort());
      } catch (error) {
        console.error("Failed to fetch sectors:", error);
        setAvailableStocks([
          "INFY", "TCS", "WIPRO", "HCLTECH", "TECHM", "LTIM",
          "RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK"
        ]);
      } finally {
        setStocksLoading(false);
      }
    };

    fetchAvailableStocks();
  }, []);

  const handleStockInputChange = (e) => {
    const value = e.target.value.toUpperCase();
    setStockInput(value);

    if (value.length > 0) {
      const filtered = availableStocks.filter(
        stock => stock.includes(value)
      );
      setFilteredStocks(filtered);
      setShowStockSuggestions(true);
    } else {
      setFilteredStocks([]);
      setShowStockSuggestions(false);
    }
  };

  const handleSelectStock = (stock) => {
    setSelectedStock(stock);
    setStockInput(stock);
    setShowStockSuggestions(false);
  };

  const handleStockBlur = () => {
    const upperInput = stockInput.toUpperCase().trim();
    if (upperInput.length > 0) {
      if (/^[A-Z&]{1,10}$/.test(upperInput)) {
        setSelectedStock(upperInput);
      } else {
        toast.error("Invalid stock symbol format (use letters and & only)");
        setSelectedStock("");
      }
    }
    setShowStockSuggestions(false);
  };

  const handleAnalyze = async (e) => {
    e?.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await recommendationApi.generateRecommendation({
        stock_symbol: selectedStock,
        trading_style: tradingStyle,
        capital: parseInt(capital)
      });

      setAnalysis(response.data);

      if (response.data.entry_price && response.data.stop_loss) {
        const pnlData = riskManagement.calculatePnL(
          parseInt(capital),
          response.data.entry_price,
          [response.data.target_1, response.data.target_2, response.data.target_3],
          response.data.stop_loss
        );
        setRiskAssessment(pnlData);

        const warnings = riskManagement.assessRisk(
          parseInt(capital),
          response.data.entry_price,
          response.data.stop_loss,
          [response.data.target_1]
        );

        if (warnings.warnings.length > 0) {
          warnings.warnings.forEach(w => toast.error(w));
        }
      }

      toast.success("Analysis complete - Review risk details below");
    } catch (error) {
      setError("Failed to analyze stock. Please try again.");
      toast.error("Failed to analyze stock");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChartUpload = async (e) => {
    e?.preventDefault();
    
    if (!chartFile) {
      toast.error("Please select a chart image");
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("image", chartFile);
      formData.append("symbol", chartSymbol);


      toast.success("📊 Chart upload feature - Backend integration needed");
      setShowChartUpload(false);
    } catch (error) {
      toast.error("Failed to analyze chart");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const RiskWarning = ({ warnings, recommendations }) => {
    if (!warnings || warnings.length === 0) return null;

    return (
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-2xl">⚠️</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">Risk Alerts</h3>
            <ul className="mt-2 text-sm text-yellow-700 space-y-1">
              {warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
            {recommendations && recommendations.length > 0 && (
              <div className="mt-3 pt-3 border-t border-yellow-200">
                <p className="text-xs font-semibold text-yellow-800 mb-1">Recommendations:</p>
                <ul className="text-xs text-yellow-700 space-y-1">
                  {recommendations.map((r, i) => (
                    <li key={i}>💡 {r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const RiskCalculator = ({ analysis }) => {
    if (!analysis || !riskAssessment) return null;

    return (
      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-gray-900">💰 Profit & Loss Scenarios</h3>
          {!riskAssessment.valid && (
            <span className="text-red-600 text-sm font-semibold">⚠️ Invalid Setup</span>
          )}
        </div>

        {!riskAssessment.valid && (
          <div className="bg-red-50 p-4 rounded border border-red-200">
            <p className="text-red-700 font-semibold">{riskAssessment.error}</p>
            <p className="text-red-600 text-sm mt-1">{riskAssessment.message}</p>
          </div>
        )}

        {riskAssessment.valid && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-xs text-gray-600">Available Capital</p>
                <p className="text-2xl font-bold text-blue-600">{formatters.formatCurrency(riskAssessment.capital)}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-xs text-gray-600">1% Risk Amount</p>
                <p className="text-2xl font-bold text-green-600">{formatters.formatCurrency(riskAssessment.maxRisk)}</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <p className="text-xs text-gray-600">Actual Risk</p>
                <p className="text-2xl font-bold text-orange-600">{formatters.formatCurrency(riskAssessment.riskAmount)}</p>
                <p className="text-xs text-orange-600 mt-1">{riskAssessment.riskPercent.toFixed(2)}%</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-xs text-gray-600">Position Size</p>
                <p className="text-2xl font-bold text-purple-600">{riskAssessment.position} units</p>
              </div>
            </div>

            <div className="border rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 text-left font-semibold">Scenario</th>
                    <th className="px-4 py-2 text-right font-semibold">Price</th>
                    <th className="px-4 py-2 text-right font-semibold">P&L (₹)</th>
                    <th className="px-4 py-2 text-right font-semibold">Return %</th>
                    <th className="px-4 py-2 text-center font-semibold">Impact</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {riskAssessment.scenarios.map((s, i) => (
                    <tr key={i} className={s.type === 'loss' ? 'bg-red-50' : 'bg-green-50'}>
                      <td className="px-4 py-2 font-medium">{s.name}</td>
                      <td className="px-4 py-2 text-right">{formatters.formatPrice(s.price)}</td>
                      <td className={`px-4 py-2 text-right font-semibold ${s.type === 'loss' ? 'text-red-600' : 'text-green-600'}`}>
                        {s.type === 'loss' ? '-' : '+'}₹{Math.abs(s.pnl).toFixed(0)}
                      </td>
                      <td className={`px-4 py-2 text-right font-semibold ${s.type === 'loss' ? 'text-red-600' : 'text-green-600'}`}>
                        {formatters.formatPercent(s.pnlPercent)}
                      </td>
                      <td className="px-4 py-2 text-center">
                        {s.type === 'loss' ? '🔴 Loss' : '🟢 Profit'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm font-semibold text-gray-900 mb-2">⏱️ Trading Duration for {tradingStyle}</p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                <div>
                  <p className="text-xs text-gray-600">Hold Time</p>
                  <p className="font-semibold text-gray-900">
                    {timeBasedGuidance.getTradeHoldTime(tradingStyle).min} - {timeBasedGuidance.getTradeHoldTime(tradingStyle).max}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Best Window</p>
                  <p className="font-semibold text-gray-900">{timeBasedGuidance.getTradeHoldTime(tradingStyle).bestWindow}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Stop Placement</p>
                  <p className="font-semibold text-gray-900">{timeBasedGuidance.getStopPlacementTime(tradingStyle)}</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    );
  };

  const PredictionModeWarning = () => {
    if (!predictionMode) return null;

    if (predictionMode.mode === 'ANALYSIS_ONLY') {
      return (
        <div className="bg-gray-50 border-l-4 border-gray-400 p-4 rounded mb-4">
          <div className="flex items-start">
            <span className="text-2xl mr-3">🔒</span>
            <div>
              <h3 className="font-bold text-gray-900">{predictionMode.label}</h3>
              <p className="text-sm text-gray-700 mt-1">{predictionMode.description}</p>
              <p className="text-xs text-gray-600 mt-2">
                ⏰ Market opens at 9:15 AM IST. Predictions will be enabled when market opens.
              </p>
              {(() => {
                const timeLeft = marketStatus.getTimeUntilMarketOpen();
                return (
                  <p className="text-xs text-blue-600 font-semibold mt-1">
                    Market opens in {timeLeft.hoursUntil}h {timeLeft.minutesUntil}m
                  </p>
                );
              })()}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded mb-4">
        <div className="flex items-start">
          <span className="text-2xl mr-3">✅</span>
          <div>
            <h3 className="font-bold text-green-900">{predictionMode.label}</h3>
            <p className="text-sm text-green-700 mt-1">{predictionMode.description}</p>
            <p className="text-xs text-green-600 font-semibold mt-1">
              🟢 Live predictions are enabled and based on real-time market data
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {marketStatusInfo && (
        <div className={`${marketStatusInfo.color} rounded-lg p-4 border border-gray-200`}>
          <div className="flex justify-between items-center">
            <div>
              <p className="font-semibold text-gray-900">{marketStatusInfo.label}</p>
              <p className="text-sm text-gray-600 mt-1">
                {marketOpen ? "✅ Live predictions available" : "🔒 Analysis mode only"}
              </p>
            </div>
            <span className="text-3xl">
              {marketStatusInfo.status === 'CLOSED' ? '🔒' : '🟢'}
            </span>
          </div>
        </div>
      )}

      <PredictionModeWarning />

      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-md p-6 text-white">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold">📊 Smart Stock Analysis</h1>
            <p className="text-blue-100 mt-2">Professional analysis with built-in risk control (1% rule)</p>
          </div>
          <button
            onClick={() => setShowChartUpload(!showChartUpload)}
            className="bg-white text-blue-600 font-semibold py-2 px-4 rounded-lg hover:bg-blue-50 transition"
          >
            📸 Upload Chart
          </button>
        </div>
      </div>

      {showChartUpload && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">📈 Chart Pattern Analysis</h3>
          <form onSubmit={handleChartUpload} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-2">Stock Symbol</label>
                <input
                  type="text"
                  value={chartSymbol}
                  onChange={(e) => {
                    const value = e.target.value.toUpperCase();
                    setChartSymbol(value);
                  }}
                  onBlur={() => {
                    const upperInput = chartSymbol.toUpperCase().trim();
                    if (upperInput.length > 0 && !/^[A-Z&]{1,10}$/.test(upperInput)) {
                      toast.error("Invalid stock symbol");
                      setChartSymbol("");
                    }
                  }}
                  placeholder="e.g., INFY or TCS"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 uppercase"
                  maxLength="10"
                />
                <p className="text-xs text-gray-500 mt-1">Enter any valid stock symbol</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Upload Chart Image</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setChartFile(e.target.files[0])}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={isLoading || !chartFile || !chartSymbol}
              className="w-full bg-blue-600 text-white font-semibold py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {isLoading ? "Analyzing..." : "Analyze Chart"}
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">Stock Symbol</label>
              <div className="relative">
                <input
                  type="text"
                  value={stockInput}
                  onChange={handleStockInputChange}
                  onFocus={() => {
                    if (stockInput.length > 0 && filteredStocks.length > 0) {
                      setShowStockSuggestions(true);
                    }
                  }}
                  onBlur={handleStockBlur}
                  placeholder="Enter stock symbol (e.g., INFY)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 uppercase"
                  maxLength="10"
                />
                {stocksLoading && (
                  <span className="absolute right-3 top-3 text-gray-400 text-sm">Loading...</span>
                )}
              </div>
              
              {showStockSuggestions && filteredStocks.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto">
                  {filteredStocks.map((stock) => (
                    <button
                      key={stock}
                      type="button"
                      onClick={() => handleSelectStock(stock)}
                      className="w-full text-left px-4 py-2 hover:bg-blue-50 transition text-gray-700"
                    >
                      <span className="font-semibold text-blue-600">{stock}</span>
                    </button>
                  ))}
                </div>
              )}

              {showStockSuggestions && stockInput.length > 0 && filteredStocks.length === 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 p-2">
                  <p className="text-xs text-gray-600 italic">
                    💡 No suggestions. You can enter any valid stock symbol (e.g., {stockInput})
                  </p>
                </div>
              )}

              <p className="text-xs text-gray-500 mt-1">
                ✓ Supports all NSE/BSE stocks
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Trading Style</label>
              <select
                value={tradingStyle}
                onChange={(e) => setTradingStyle(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {TRADING_STYLES.map((style) => (
                  <option key={style.value} value={style.value}>{style.label}</option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {TRADING_STYLES.find(s => s.value === tradingStyle)?.desc}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Capital (₹)</label>
              <input
                type="number"
                value={capital}
                onChange={(e) => setCapital(e.target.value)}
                min="1000"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-green-600 mt-1">
                ✓ Max risk: {formatters.formatCurrency(parseInt(capital) * 0.01)}
              </p>
            </div>

            <div className="flex flex-col justify-end">
              <button
                type="submit"
                disabled={isLoading || !marketOpen || !selectedStock}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-2 rounded-lg hover:shadow-lg transition disabled:opacity-50"
              >
                {isLoading ? "🔄 Analyzing..." : "✨ Analyze"}
              </button>
              {!selectedStock && (
                <p className="text-xs text-red-500 mt-1 text-center">
                  ⚠️ Select a stock symbol
                </p>
              )}
              {!marketOpen && (
                <p className="text-xs text-gray-500 mt-1 text-center">
                  Market closed - Use Analysis Mode
                </p>
              )}
            </div>
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {analysis && (
        <>
          <RiskCalculator analysis={analysis} />

          {riskAssessment && riskAssessment.valid && (
            <RiskWarning
              warnings={riskManagement.assessRisk(
                parseInt(capital),
                analysis.entry_price,
                analysis.stop_loss,
                [analysis.target_1]
              ).warnings}
              recommendations={riskManagement.assessRisk(
                parseInt(capital),
                analysis.entry_price,
                analysis.stop_loss,
                [analysis.target_1]
              ).recommendations}
            />
          )}

          <div className="flex gap-2 bg-white rounded-lg shadow-md overflow-x-auto">
            {["overview", "trend", "indicators", "levels", "strategy"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-shrink-0 py-3 px-4 font-medium transition ${
                  activeTab === tab
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {tab === "overview" && "📊 Overview"}
                {tab === "trend" && "📈 Trend"}
                {tab === "indicators" && "📉 Indicators"}
                {tab === "levels" && "🎯 Levels"}
                {tab === "strategy" && "🎬 Strategy"}
              </button>
            ))}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            {activeTab === "overview" && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className={`p-4 rounded-lg ${analysis.signal === 'BUY' ? 'bg-green-50' : analysis.signal === 'SELL' ? 'bg-red-50' : 'bg-yellow-50'}`}>
                    <p className="text-xs text-gray-600">Signal</p>
                    <p className="text-2xl font-bold">{analysis.signal}</p>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-xs text-gray-600">Entry Price</p>
                    <p className="text-2xl font-bold text-blue-600">{formatters.formatPrice(analysis.entry_price)}</p>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <p className="text-xs text-gray-600">Stop Loss</p>
                    <p className="text-2xl font-bold text-red-600">{formatters.formatPrice(analysis.stop_loss)}</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-xs text-gray-600">Win Probability</p>
                    <p className="text-2xl font-bold text-purple-600">{analysis.win_probability}%</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "trend" && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-gray-900">Support & Resistance Levels</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-600">
                    <p className="text-sm text-gray-600">Support Level</p>
                    <p className="text-2xl font-bold text-green-600">{formatters.formatPrice(analysis.support_level)}</p>
                    <p className="text-xs text-gray-600 mt-2">Buying zone / Strong support</p>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-600">
                    <p className="text-sm text-gray-600">Resistance Level</p>
                    <p className="text-2xl font-bold text-red-600">{formatters.formatPrice(analysis.resistance_level)}</p>
                    <p className="text-xs text-gray-600 mt-2">Selling zone / Strong resistance</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "indicators" && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-gray-900">Technical Indicators</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm font-semibold text-gray-900">RSI (14)</p>
                    <p className="text-3xl font-bold text-blue-600">{analysis.rsi?.toFixed(1)}</p>
                    <p className="text-xs text-gray-600 mt-2">
                      {analysis.rsi > 70 ? "⚠️ Overbought" : analysis.rsi < 30 ? "✅ Oversold" : "➡️ Neutral"}
                    </p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-sm font-semibold text-gray-900">VWAP</p>
                    <p className="text-3xl font-bold text-purple-600">{formatters.formatPrice(analysis.vwap)}</p>
                    <p className="text-xs text-gray-600 mt-2">Volume-weighted average price</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "levels" && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-gray-900">Trading Entry & Targets</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-xs text-gray-600">Entry</p>
                    <p className="text-xl font-bold text-blue-600">{formatters.formatPrice(analysis.entry_price)}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-xs text-gray-600">Target 1</p>
                    <p className="text-xl font-bold text-green-600">{formatters.formatPrice(analysis.target_1)}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-xs text-gray-600">Target 2</p>
                    <p className="text-xl font-bold text-green-600">{formatters.formatPrice(analysis.target_2)}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-xs text-gray-600">Target 3</p>
                    <p className="text-xl font-bold text-green-600">{formatters.formatPrice(analysis.target_3)}</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "strategy" && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-gray-900">💡 Trading Strategy for {tradingStyle}</h3>
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
                  <ol className="space-y-3">
                    <li className="flex gap-3">
                      <span className="text-xl font-bold text-blue-600">1️⃣</span>
                      <div>
                        <p className="font-semibold text-gray-900">Entry Execution</p>
                        <p className="text-sm text-gray-600">Enter on signal confirmation at {formatters.formatPrice(analysis.entry_price)}</p>
                      </div>
                    </li>
                    <li className="flex gap-3">
                      <span className="text-xl font-bold text-blue-600">2️⃣</span>
                      <div>
                        <p className="font-semibold text-gray-900">Stop Loss Placement</p>
                        <p className="text-sm text-gray-600">Place stop loss at {formatters.formatPrice(analysis.stop_loss)} within minutes of entry</p>
                      </div>
                    </li>
                    <li className="flex gap-3">
                      <span className="text-xl font-bold text-blue-600">3️⃣</span>
                      <div>
                        <p className="font-semibold text-gray-900">Target Management</p>
                        <p className="text-sm text-gray-600">Trail stop loss after reaching Target 1 ({formatters.formatPrice(analysis.target_1)})</p>
                      </div>
                    </li>
                    <li className="flex gap-3">
                      <span className="text-xl font-bold text-blue-600">4️⃣</span>
                      <div>
                        <p className="font-semibold text-gray-900">Partial Exit</p>
                        <p className="text-sm text-gray-600">Book profits at Target 2 & 3 or hold for maximum profit</p>
                      </div>
                    </li>
                    <li className="flex gap-3">
                      <span className="text-xl font-bold text-blue-600">5️⃣</span>
                      <div>
                        <p className="font-semibold text-gray-900">Risk Management</p>
                        <p className="text-sm text-gray-600">Never risk more than 1% of capital per trade (Max risk: {formatters.formatCurrency(parseInt(capital) * 0.01)})</p>
                      </div>
                    </li>
                  </ol>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {!analysis && !isLoading && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <p className="text-gray-600 text-lg">Select stock, style, and capital to begin analysis</p>
          <p className="text-gray-400 mt-2">Smart risk management and trade planning included</p>
        </div>
      )}
    </div>
  );
}
