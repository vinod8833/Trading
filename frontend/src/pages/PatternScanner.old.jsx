import React, { useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";
import { technicalAnalysisApi } from "../api/endpoints";
import { marketStatus, formatters } from "../utils/tradingEngine";

export default function TechnicalPatternScanner() {
  const [symbol, setSymbol] = useState("INFY");
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("patterns");
  const [marketOpen, setMarketOpen] = useState(false);
  const [marketStatusInfo, setMarketStatusInfo] = useState(null);
  const [selectedCapital, setSelectedCapital] = useState(100000);
  const [confidentPatterns, setConfidentPatterns] = useState([]);

  useEffect(() => {
    const updateMarketStatus = () => {
      const isOpen = marketStatus.isMarketOpen();
      const status = marketStatus.getMarketStatus();
      setMarketOpen(isOpen);
      setMarketStatusInfo(status);
    };

    updateMarketStatus();
    const timer = setInterval(updateMarketStatus, 60000);
    
    return () => clearInterval(timer);
  }, []);

  const handleScanStock = useCallback(async (e) => {
    if (e) e.preventDefault();
    
    if (!symbol.trim()) {
      toast.error("Please enter a stock symbol");
      return;
    }
    
    setIsLoading(true);

    try {
      const response = await technicalAnalysisApi.analyzeTechnical(symbol, "1D", marketOpen);
      setAnalysis(response.data);
      
      const allPatterns = [];
      
      if (response.data.candlestick_patterns && Array.isArray(response.data.candlestick_patterns)) {
        allPatterns.push(...response.data.candlestick_patterns.map(p => ({
          ...p,
          type: p.type || 'candlestick'
        })));
      }
      if (response.data.chart_patterns && Array.isArray(response.data.chart_patterns)) {
        allPatterns.push(...response.data.chart_patterns.map(p => ({
          ...p,
          name: p.pattern || p.name,
          type: p.type || 'chart'
        })));
      }
      
      const highConfidence = allPatterns.filter(p => {
        const conf = p.confidence || 50;
        return parseInt(conf) >= 60;
      });
      
      setConfidentPatterns(highConfidence);
      
      if (highConfidence.length > 0) {
        toast.success(`✅ Scan complete - Found ${highConfidence.length} patterns`);
      } else if (allPatterns.length > 0) {
        toast.info(`📊 Found ${allPatterns.length} patterns with lower confidence`);
      } else {
        toast.info(`📊 Scan complete for ${symbol} - No patterns detected yet`);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || error.response?.data?.error || "Failed to scan stock");
      console.error(error);
      setConfidentPatterns([]);
    } finally {
      setIsLoading(false);
    }
  }, [symbol, marketOpen]);

  useEffect(() => {
    if (symbol) {
      handleScanStock();
    }
  }, [symbol, marketOpen, handleScanStock]);

  const PatternCard = ({ pattern, type = "bullish", capital }) => {
    const bgColor = type === "bullish" ? "bg-green-50 border-green-500" : "bg-red-50 border-red-500";
    const textColor = type === "bullish" ? "text-green-700" : "text-red-700";
    const icon = type === "bullish" ? "📈" : "📉";
    const confidence = parseInt(pattern.confidence || 50);

    return (
      <div className={`border-l-4 ${bgColor} p-4 rounded-lg mb-3`}>
        <div className="flex justify-between items-start mb-3">
          <div>
            <h4 className={`text-lg font-bold ${textColor}`}>{icon} {pattern.name || pattern.pattern}</h4>
            <p className="text-gray-700 text-sm mt-1">{pattern.signal || 'Pattern detected'}</p>
          </div>
          <div className="text-right">
            <span className={`text-sm font-bold px-3 py-1 rounded ${textColor} bg-opacity-10 bg-${type === 'bullish' ? 'green' : 'red'}-100`}>
              {confidence}% Confidence
            </span>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-white bg-opacity-60 p-2 rounded">
              <p className="text-gray-600">Reward Potential</p>
              <p className="font-bold">{confidence > 70 ? '🟢 High' : confidence > 50 ? '🟡 Medium' : '🔴 Low'}</p>
            </div>
            <div className="bg-white bg-opacity-60 p-2 rounded">
              <p className="text-gray-600">Risk Level</p>
              <p className="font-bold">{confidence > 70 ? '🟢 Moderate' : confidence > 50 ? '🟡 Medium' : '🔴 High'}</p>
            </div>
          </div>
        </div>

        {capital && (
          <div className="mt-3 bg-white bg-opacity-50 p-2 rounded text-xs text-gray-700">
            <p>Max Risk: {formatters.formatCurrency(capital * 0.01)} (1% rule)</p>
          </div>
        )}
      </div>
    );
  };

  const IndicatorDisplay = ({ indicators }) => {
    if (!indicators) return null;

    const getRSIColor = (rsi) => {
      if (rsi > 70) return "text-red-600";
      if (rsi < 30) return "text-green-600";
      return "text-yellow-600";
    };

    const getRSISignal = (rsi) => {
      if (rsi > 70) return "⚠️ Overbought";
      if (rsi < 30) return "✅ Oversold";
      return "➡️ Neutral";
    };

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="font-bold text-gray-900 mb-3">RSI (14)</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Value:</span>
              <span className={`text-2xl font-bold ${getRSIColor(indicators.rsi)}`}>
                {indicators.rsi?.toFixed(1)}
              </span>
            </div>
            <div className="bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full"
                style={{ width: `${Math.min(100, indicators.rsi)}%` }}
              />
            </div>
            <p className={`text-sm font-semibold ${getRSIColor(indicators.rsi)}`}>
              {getRSISignal(indicators.rsi)}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="font-bold text-gray-900 mb-3">VWAP</h4>
          <div className="space-y-2">
            <p className="text-2xl font-bold text-primary">
              ₹{indicators.vwap?.toFixed(2)}
            </p>
            <p className="text-sm text-gray-600">
              Volume Weighted Average Price
            </p>
            <p className="text-xs text-gray-500 mt-2">
              💡 Buy above VWAP (Intraday)
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="font-bold text-gray-900 mb-3">Moving Averages</h4>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">EMA 20:</p>
              <p className="text-xl font-bold text-blue-600">
                ₹{indicators.ema_20?.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">EMA 50:</p>
              <p className="text-xl font-bold text-purple-600">
                ₹{indicators.ema_50?.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="font-bold text-gray-900 mb-3">Bollinger Bands (20, 2)</h4>
          <div className="space-y-2">
            {indicators.bollinger_bands && (
              <>
                <div>
                  <p className="text-xs text-red-600">Upper:</p>
                  <p className="font-bold">₹{indicators.bollinger_bands.upper?.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Middle (SMA):</p>
                  <p className="font-bold">₹{indicators.bollinger_bands.middle?.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs text-blue-600">Lower:</p>
                  <p className="font-bold">₹{indicators.bollinger_bands.lower?.toFixed(2)}</p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    );
  };

  const TradingLevels = ({ levels }) => {
    if (!levels) return null;

    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">🎯 Trading Levels</h3>

        <div className="mb-6">
          <h4 className="font-semibold text-gray-900 mb-3">Support & Resistance</h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
              <p className="text-xs text-gray-600">Support</p>
              <p className="text-2xl font-bold text-blue-600">
                ₹{levels.support?.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-1">Buying zone</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
              <p className="text-xs text-gray-600">Resistance</p>
              <p className="text-2xl font-bold text-red-600">
                ₹{levels.resistance?.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-1">Selling zone</p>
            </div>
          </div>
        </div>

        {levels.fibonacci && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">📊 Fibonacci Retracement</h4>
            <div className="space-y-2 bg-gray-50 p-4 rounded-lg">
              {Object.entries(levels.fibonacci).map(([level, price]) => (
                <div key={level} className="flex justify-between items-center py-1 border-b">
                  <span className="text-sm text-gray-600">{level}</span>
                  <span className="font-semibold text-gray-900">₹{price?.toFixed(2)}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2 italic">
              💡 Use Fibonacci levels for entry zones and profit targets
            </p>
          </div>
        )}
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
                {marketOpen 
                  ? "🟢 Live Analysis Active - Real-time pattern detection with current market data" 
                  : "📊 Historical Analysis Mode - Patterns based on last available market data"}
              </p>
            </div>
            <span className="text-3xl">
              {marketOpen ? '📈' : '📊'}
            </span>
          </div>
        </div>
      )}

      {!marketOpen && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
          <p className="text-blue-900 font-semibold">📊 Analysis Mode Active</p>
          <p className="text-sm text-blue-700 mt-1">Market is closed. Patterns shown are based on historical data and technical analysis.</p>
        </div>
      )}
      <div className="bg-gradient-to-r from-primary to-secondary rounded-lg shadow-md p-6 text-white">
        <h1 className="text-3xl font-bold">🔍 Technical Pattern Scanner</h1>
        <p className="text-gray-100 mt-2">Auto-detect candlestick patterns, chart formations, and trading signals</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleScanStock} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Stock Symbol</label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="Enter stock symbol (e.g., INFY)"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Capital (For Risk Calc)</label>
              <input
                type="number"
                value={selectedCapital}
                onChange={(e) => setSelectedCapital(parseInt(e.target.value))}
                min="1000"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              />
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-primary to-secondary text-white font-semibold py-2 rounded-lg hover:shadow-lg transition disabled:opacity-50"
              >
                {isLoading ? "Scanning..." : "Scan"}
              </button>
            </div>
          </div>
        </form>
      </div>

      {confidentPatterns.length > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg shadow p-4 border border-green-200">
          <h3 className="text-lg font-bold text-green-900 mb-3">🎯 High Confidence Patterns Detected!</h3>
          <p className="text-sm text-green-800 mb-3">
            Found {confidentPatterns.length} patterns with 70%+ confidence. These have higher probability of success.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {confidentPatterns.slice(0, 3).map((p, i) => (
              <div key={i} className="bg-white rounded p-3 border-l-4 border-green-500">
                <p className="font-semibold text-gray-900">{p.name || p.pattern}</p>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">{p.confidence}% Confidence</span>
                  <span className="text-sm font-bold">{p.type === 'Bearish' ? '📉' : '📈'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {analysis && (
        <>
          <div className="flex gap-2 bg-white rounded-lg shadow-md overflow-hidden">
            {[
              { key: "patterns", label: "🔹 Candlestick Patterns" },
              { key: "charts", label: "📊 Chart Patterns" },
              { key: "indicators", label: "📈 Indicators" },
              { key: "levels", label: "🎯 Trading Levels" }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex-1 py-3 px-4 font-medium transition ${
                  activeTab === tab.key
                    ? "bg-primary text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            {activeTab === "patterns" && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">🔹 Candlestick Patterns</h2>
                {analysis.candlestick_patterns && analysis.candlestick_patterns.length > 0 ? (
                  analysis.candlestick_patterns.map((pattern, idx) => (
                    <PatternCard
                      key={idx}
                      pattern={pattern}
                      type={pattern.type === "Bearish" ? "bearish" : "bullish"}
                      capital={selectedCapital}
                    />
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-8">No significant candlestick patterns detected</p>
                )}
              </div>
            )}

            {activeTab === "charts" && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">📊 Chart Patterns</h2>
                {analysis.chart_patterns && analysis.chart_patterns.length > 0 ? (
                  analysis.chart_patterns.map((pattern, idx) => (
                    <PatternCard
                      key={idx}
                      pattern={pattern}
                      type={pattern.type === "Bearish" ? "bearish" : "bullish"}
                      capital={selectedCapital}
                    />
                  ))
                ) : (
                  <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                    <p className="text-gray-600 text-lg">📊 No chart patterns detected for {symbol}</p>
                    <p className="text-gray-500 text-sm mt-2">Try another stock or check candlestick patterns tab</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === "indicators" && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">📈 Technical Indicators</h2>
                <IndicatorDisplay indicators={analysis.indicators} />
              </div>
            )}

            {activeTab === "levels" && (
              <div>
                <TradingLevels levels={analysis.trading_levels} />
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-green-50 rounded-lg shadow-md p-6 border-l-4 border-green-500">
              <h3 className="text-lg font-bold text-green-800 mb-4">✅ Bullish Signals</h3>
              <ul className="space-y-2">
                {analysis.candlestick_patterns
                  ?.filter((p) => p.type !== "Bearish")
                  .map((p, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-green-700">
                      <span>✓</span> {p.name}
                    </li>
                  ))}
                {analysis.chart_patterns
                  ?.filter((p) => p.type === "Bullish")
                  .map((p, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-green-700">
                      <span>✓</span> {p.pattern}
                    </li>
                  ))}
              </ul>
            </div>

            <div className="bg-red-50 rounded-lg shadow-md p-6 border-l-4 border-red-500">
              <h3 className="text-lg font-bold text-red-800 mb-4">⚠️ Bearish Signals</h3>
              <ul className="space-y-2">
                {analysis.candlestick_patterns
                  ?.filter((p) => p.type === "Bearish")
                  .map((p, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-red-700">
                      <span>✗</span> {p.name}
                    </li>
                  ))}
                {analysis.chart_patterns
                  ?.filter((p) => p.type === "Bearish")
                  .map((p, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-red-700">
                      <span>✗</span> {p.pattern}
                    </li>
                  ))}
              </ul>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <h3 className="text-lg font-bold text-blue-800 mb-4">💡 Scanner Tips</h3>
            <ul className="space-y-2 text-sm text-blue-700">
              <li>✓ <strong>Candlestick Patterns:</strong> Hammer, Doji, Engulfing - used for entry signals</li>
              <li>✓ <strong>Chart Patterns:</strong> Triangles, Double Tops/Bottoms - predict breakouts</li>
              <li>✓ <strong>VWAP:</strong> Buy above for intraday, sell below</li>
              <li>✓ <strong>EMA:</strong> 20/50 crossover = trend change signal</li>
              <li>✓ <strong>Fibonacci:</strong> Use for entry zones and profit targets</li>
              <li>✓ <strong>RSI:</strong> Above 70 = Overbought, Below 30 = Oversold</li>
            </ul>
          </div>
        </>
      )}

      {!analysis && !isLoading && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <p className="text-gray-600 text-lg">Enter a stock symbol to start scanning</p>
          <p className="text-gray-400 mt-2">The scanner will detect patterns and provide trading signals</p>
        </div>
      )}
    </div>
  );
}
