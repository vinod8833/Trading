import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { recommendationApi } from "../api/endpoints";
import { marketStatus, predictionControl, riskManagement } from "../utils/tradingEngine";
import { getPopularStocks, getLastAvailablePopularStocks } from "../utils/marketDataService";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input, Select } from "../components/ui/Input";
import { Badge, Stat, Alert, Progress } from "../components/ui/Common";
import { Tabs } from "../components/ui/Layouts";

export default function StockAnalysis() {
  const [selectedStock, setSelectedStock] = useState("");
  const [stockInput, setStockInput] = useState("");
  const [tradingStyle, setTradingStyle] = useState("SWING");
  const [capital, setCapital] = useState("100000");
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [showStockSuggestions, setShowStockSuggestions] = useState(false);
  const [marketOpen, setMarketOpen] = useState(false);
  const [marketStatusInfo, setMarketStatusInfo] = useState(null);
  const [popularStocks, setPopularStocks] = useState([]);
  const [loadingPopularStocks, setLoadingPopularStocks] = useState(true);

  useEffect(() => {
    const loadPopularStocks = async () => {
      setLoadingPopularStocks(true);
      try {
        const stocks = await getPopularStocks();
        setPopularStocks(stocks);
      } catch (err) {
        console.error("Error loading popular stocks:", err);
        const fallbackStocks = getLastAvailablePopularStocks();
        setPopularStocks(fallbackStocks);
      } finally {
        setLoadingPopularStocks(false);
      }
    };

    loadPopularStocks();

    const refreshInterval = setInterval(loadPopularStocks, 5 * 60 * 1000);
    return () => clearInterval(refreshInterval);
  }, []);

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

  const handleStockInput = (value) => {
    setStockInput(value.toUpperCase());

    if (value.length > 0) {
      const filtered = popularStocks.filter(
        (stock) =>
          stock.symbol.includes(value.toUpperCase()) ||
          stock.name.toUpperCase().includes(value.toUpperCase())
      );
      setFilteredStocks(filtered);
      setShowStockSuggestions(true);
    } else {
      setShowStockSuggestions(false);
    }
  };

  const selectStock = (symbol) => {
    setStockInput(symbol);
    setSelectedStock(symbol);
    setShowStockSuggestions(false);
  };

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

      const data = response.data?.data || response.data;
      const normalizedData = {
        ...data,
        entry_price: parseFloat(data.entry_price) || 0,
        target_1: parseFloat(data.target_1) || 0,
        target_2: parseFloat(data.target_2) || 0,
        stop_loss: parseFloat(data.stop_loss) || 0,
        confidence: parseFloat(data.confidence) || 0,
        current_price: parseFloat(data.current_price) || 0,
      };

      const completeAnalysis = {
        ...normalizedData,
        marketOpen,
        timestamp: new Date().toLocaleString("en-IN"),
        capitalRisk: (parseFloat(capital) * 0.01).toFixed(2),
      };

      setAnalysis(completeAnalysis);
      toast.success(`✅ Analysis complete for ${stock}`);
    } catch (err) {
      const message = err.response?.data?.error || "Analysis failed";
      setError(message);
      toast.error(`❌ ${message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const riskRewardRatio = analysis
    ? (analysis.target_1 - analysis.entry_price) / (analysis.entry_price - analysis.stop_loss)
    : 0;

  const expectedProfit = analysis
    ? ((analysis.target_1 - analysis.entry_price) / analysis.entry_price) * 100
    : 0;

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Stock Analysis</h1>
          <p className="text-gray-600 mt-1">Comprehensive technical and fundamental analysis with AI insights</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Analyze Stock</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
            <div className="relative">
              <Input
                label="Stock Symbol"
                placeholder="e.g., INFY, TCS"
                value={stockInput}
                onChange={(e) => handleStockInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleAnalyze()}
                icon="📊"
              />
              {showStockSuggestions && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
                  {filteredStocks.length > 0 ? (
                    filteredStocks.map((stock) => (
                      <button
                        key={stock.symbol}
                        onClick={() => selectStock(stock.symbol)}
                        className="w-full text-left px-4 py-2 hover:bg-blue-50 transition border-b border-gray-100 last:border-b-0"
                      >
                        <p className="font-semibold text-gray-900">{stock.symbol}</p>
                        <p className="text-xs text-gray-600">{stock.name} • {stock.sector}</p>
                      </button>
                    ))
                  ) : (
                    <div className="p-4 text-center text-gray-500 text-sm">
                      No stocks found. You can still enter any symbol.
                    </div>
                  )}
                </div>
              )}
            </div>

            <Select
              label="Trading Style"
              value={tradingStyle}
              onChange={(e) => setTradingStyle(e.target.value)}
              options={[
                { value: "INTRADAY", label: "⚡ Intraday" },
                { value: "SWING", label: "📊 Swing (2-5 days)" },
                { value: "POSITIONAL", label: "📈 Positional (Weeks)" },
                { value: "INVESTMENT", label: "🏦 Investment (Months+)" },
              ]}
            />

            <Input
              label="Capital (₹)"
              type="number"
              value={capital}
              onChange={(e) => setCapital(e.target.value)}
              min="10000"
              step="10000"
              icon="💰"
            />

            <div className="flex items-end gap-2">
              <Button onClick={handleAnalyze} isLoading={isLoading} className="flex-1">
                🔍 Analyze
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setStockInput("");
                  setSelectedStock("");
                  setAnalysis(null);
                }}
              >
                ✕
              </Button>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-medium text-gray-700">Popular stocks (live market data):</p>
              {loadingPopularStocks && <span className="text-xs text-gray-500 animate-pulse">⟳ Loading...</span>}
            </div>
            <div className="flex flex-wrap gap-2">
              {popularStocks.slice(0, 8).map((stock) => (
                <button
                  key={stock.symbol}
                  onClick={() => {
                    setStockInput(stock.symbol);
                    setSelectedStock(stock.symbol);
                  }}
                  className="px-3 py-1.5 bg-gray-100 hover:bg-blue-100 text-gray-700 hover:text-blue-700 rounded-full text-xs font-medium transition group relative"
                  title={`${stock.name} - ${stock.sector} (${stock.change > 0 ? '+' : ''}${stock.change?.toFixed(2)}%)`}
                >
                  <span>{stock.symbol}</span>
                  {stock.change !== undefined && (
                    <span className={`text-xs ml-1 ${stock.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {stock.change > 0 ? '↑' : '↓'}
                    </span>
                  )}
                </button>
              ))}
              {popularStocks.length === 0 && !loadingPopularStocks && (
                <p className="text-xs text-gray-500 italic">No stocks available</p>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {marketOpen 
                ? "✓ Updated every 5 minutes during market hours" 
                : "✓ Showing last available data (market closed)"}
            </p>
          </div>
        </CardContent>
      </Card>

      {analysis && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Stat
              label="Entry Price"
              value={`₹${analysis.entry_price?.toFixed(2)}`}
              icon="📍"
            />
            <Stat
              label="Target Price"
              value={`₹${analysis.target_1?.toFixed(2)}`}
              change={`+${expectedProfit.toFixed(2)}%`}
              changeType="up"
              icon="🎯"
            />
            <Stat
              label="Stop Loss"
              value={`₹${analysis.stop_loss?.toFixed(2)}`}
              change={`${((analysis.stop_loss - analysis.entry_price) / analysis.entry_price * 100).toFixed(2)}%`}
              changeType="down"
              icon="⛔"
            />
            <Stat
              label="R:R Ratio"
              value={riskRewardRatio.toFixed(2)}
              icon="⚖️"
            />
            <Stat
              label="Confidence"
              value={`${analysis.confidence}%`}
              icon="🎯"
            />
          </div>

          <Tabs
            activeTab={activeTab}
            onTabChange={setActiveTab}
            tabs={[
              {
                id: "overview",
                label: "Overview",
                icon: "📊",
                content: (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <Card>
                      <CardHeader>
                        <CardTitle>Signal Information</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Signal:</span>
                          <Badge variant={analysis.signal_type === "BUY" ? "success" : "danger"}>
                            {analysis.signal_type}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Trading Style:</span>
                          <span className="font-semibold">{tradingStyle}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Time Horizon:</span>
                          <span className="font-semibold">
                            {tradingStyle === "INTRADAY" ? "Same Day" : tradingStyle === "SWING" ? "2-5 Days" : "Weeks+"}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Market Status:</span>
                          <Badge variant={marketOpen ? "success" : "warning"}>
                            {marketOpen ? "OPEN" : "CLOSED"}
                          </Badge>
                        </div>
                        <div className="pt-3 border-t text-xs text-gray-500">
                          Analyzed: {analysis.timestamp}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Risk Management</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-gray-600 text-sm">Capital at Risk (1%):</span>
                            <span className="font-semibold">₹{analysis.capitalRisk}</span>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-gray-600 text-sm">Max Profit Potential:</span>
                            <span className="font-semibold text-green-600">
                              ₹{(parseFloat(analysis.capitalRisk) * riskRewardRatio).toFixed(0)}
                            </span>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-gray-600 text-sm">Risk/Reward Ratio:</span>
                            <span className="font-semibold">1:{riskRewardRatio.toFixed(2)}</span>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-gray-600 text-sm">Position Size:</span>
                            <span className="font-semibold">
                              {(parseFloat(analysis.capitalRisk) / (analysis.entry_price - analysis.stop_loss)).toFixed(0)} shares
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ),
              },
              {
                id: "technical",
                label: "Technical",
                icon: "📈",
                content: (
                  <Card>
                    <CardHeader>
                      <CardTitle>Technical Indicators</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {analysis.technical_indicators ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {Object.entries(analysis.technical_indicators).map(([key, value]) => (
                            <div key={key} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                              <p className="text-sm text-gray-600 font-medium capitalize">
                                {key.replace(/_/g, " ")}
                              </p>
                              <p className="text-2xl font-bold text-gray-900 mt-2">
                                {typeof value === "number" ? value.toFixed(2) : value}
                              </p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-500 text-center py-8">No technical indicators available</p>
                      )}
                    </CardContent>
                  </Card>
                ),
              },
            ]}
          />

          <div className="flex gap-3 flex-wrap">
            <Button onClick={handleAnalyze} variant="primary">
              Refresh
            </Button>
            <Button variant="secondary" onClick={() => setAnalysis(null)}>
              Clear Results
            </Button>
            <Button variant="outline">⭐ Add to Watchlist</Button>
          </div>
        </div>
      )}

      {!analysis && !isLoading && (
        <Card className="text-center py-16">
          <p className="text-xl text-gray-600 mb-2">📊 Start analyzing stocks</p>
          <p className="text-gray-500">Enter a stock symbol to get comprehensive analysis</p>
        </Card>
      )}
    </div>
  );
}
