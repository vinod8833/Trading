import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { recommendationApi } from "../api/endpoints";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import { Button, IconButton } from "../components/ui/Button";
import { Input, Select } from "../components/ui/Input";
import { Badge, Stat, Alert } from "../components/ui/Common";
import { Tabs } from "../components/ui/Layouts";

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
  const [activeTab, setActiveTab] = useState("overview");

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
        "2026-01-26", "2026-03-25", "2026-04-14", "2026-08-15",
        "2026-09-02", "2026-10-02", "2026-10-25", "2026-12-25",
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
        marketStatus: marketStatus,
        dataType: dataType,
        timestamp: new Date().toLocaleString("en-IN"),
        capitalRisk: (parseFloat(capital) * 0.01).toFixed(2),
        isValidData: response.data?.success !== false,
      };

      setAnalysis(completeAnalysis);
      toast.success(`Analysis complete for ${stock}`);
    } catch (err) {
      let message = "Analysis failed";
      if (err.response?.data?.message) {
        message = err.response.data.message;
      } else if (err.response?.data?.error) {
        message = err.response.data.error;
      } else if (err.message) {
        message = err.message;
      }
      
      setError(message);
      toast.error(`❌ ${message}`);
      console.error("Analysis error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAnalysis = (symbol) => {
    setStockInput(symbol);
    setSelectedStock(symbol);
  };

  const suggestedStocks = [
    { symbol: "INFY", name: "Infosys", sector: "IT" },
    { symbol: "TCS", name: "Tata Consultancy", sector: "IT" },
    { symbol: "RELIANCE", name: "Reliance Industries", sector: "Energy" },
    { symbol: "HDFC", name: "HDFC Bank", sector: "Banking" },
    { symbol: "WIPRO", name: "Wipro Limited", sector: "IT" },
    { symbol: "MARUTI", name: "Maruti Suzuki", sector: "Auto" },
  ];

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Real-time market analysis and trading recommendations</p>
      </div>

      {marketStatus !== "OPEN" && (
        <Alert
          type={marketStatus === "HOLIDAY" ? "warning" : "info"}
          title={marketStatus === "HOLIDAY" ? "Market Holiday" : "Market Closed"}
          message={
            marketStatus === "HOLIDAY"
              ? "Today is a market holiday. Showing data from previous trading session."
              : "Market is currently closed. Data shown is from the last trading session."
          }
          icon={marketStatus === "HOLIDAY" ? "📅" : "🕐"}
        />
      )}

      <Card>
        <CardHeader>
          <CardTitle>Stock Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Input
              label="Stock Symbol"
              placeholder="e.g., INFY, TCS, RELIANCE"
              value={stockInput}
              onChange={(e) => setStockInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleAnalyze()}
              icon="📊"
            />
            <Select
              label="Trading Style"
              value={tradingStyle}
              onChange={(e) => setTradingStyle(e.target.value)}
              options={[
                { value: "SWING", label: "Swing Trading (2-5 days)" },
                { value: "POSITIONAL", label: "Positional (Weeks)" },
                { value: "INTRADAY", label: "Intraday (Same day)" },
                { value: "SCALPING", label: "Scalping (Minutes)" },
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
            <div className="flex items-end">
              <Button
                onClick={handleAnalyze}
                isLoading={isLoading}
                className="w-full"
              >
                🔍 Analyze
              </Button>
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">Or select a popular stock:</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              {suggestedStocks.map((stock) => (
                <button
                  key={stock.symbol}
                  onClick={() => {
                    setStockInput(stock.symbol);
                    handleQuickAnalysis(stock.symbol);
                  }}
                  className="p-3 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg transition text-center"
                >
                  <p className="font-semibold text-sm text-gray-900">{stock.symbol}</p>
                  <p className="text-xs text-gray-500 mt-1">{stock.sector}</p>
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {analysis && (
        <div className="space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">📊 Key Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Stat
                label="Entry Price"
                value={`₹${analysis.entry_price?.toFixed(2)}`}
                icon="📍"
              />
              <Stat
                label="Target Price"
                value={`₹${analysis.target_1?.toFixed(2)}`}
                change={`+${((analysis.target_1 - analysis.entry_price) / analysis.entry_price * 100).toFixed(2)}%`}
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
                label="Risk/Reward Ratio"
                value={((analysis.target_1 - analysis.entry_price) / (analysis.entry_price - analysis.stop_loss)).toFixed(2)}
                icon="⚖️"
              />
            </div>
          </div>

          <Tabs
            tabs={[
              {
                id: "overview",
                label: "Overview",
                icon: "📈",
                content: (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card>
                      <CardHeader>
                        <CardTitle>Signal Details</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Signal Type:</span>
                          <Badge variant={analysis.signal_type === "BUY" ? "success" : "danger"}>
                            {analysis.signal_type}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Confidence:</span>
                          <span className="font-semibold">{analysis.confidence}%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Time Horizon:</span>
                          <span className="font-semibold">{tradingStyle}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Data Type:</span>
                          <Badge variant={dataType === "LIVE" ? "primary" : "warning"}>
                            {dataType}
                          </Badge>
                        </div>
                        <div className="pt-3 border-t">
                          <span className="text-gray-600 text-sm">Analyzed at: {analysis.timestamp}</span>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Risk Management</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Capital at Risk (1%):</span>
                          <span className="font-semibold">₹{analysis.capitalRisk}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Potential Profit:</span>
                          <span className="font-semibold text-green-600">
                            ₹{(parseFloat(analysis.capitalRisk) * ((analysis.target_1 - analysis.entry_price) / (analysis.entry_price - analysis.stop_loss))).toFixed(2)}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Risk/Reward Ratio:</span>
                          <span className="font-semibold">
                            1:{((analysis.target_1 - analysis.entry_price) / (analysis.entry_price - analysis.stop_loss)).toFixed(2)}
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ),
              },
              {
                id: "technical",
                label: "Technical",
                icon: "📊",
                content: (
                  <Card>
                    <CardHeader>
                      <CardTitle>Technical Indicators</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {analysis.technical_indicators && Object.entries(analysis.technical_indicators).map(([key, value]) => (
                          <div key={key} className="p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-600 capitalize">{key.replace(/_/g, " ")}</p>
                            <p className="text-lg font-semibold text-gray-900 mt-1">
                              {typeof value === "number" ? value.toFixed(2) : value}
                            </p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ),
              },
            ]}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />

          <div className="flex gap-3 flex-wrap">
            <Button onClick={handleAnalyze} variant="primary">
              🔄 Refresh Analysis
            </Button>
            <Button variant="secondary" onClick={() => setAnalysis(null)}>
              Clear Results
            </Button>
          </div>
        </div>
      )}

      {!analysis && !isLoading && (
        <Card className="text-center py-12">
          <p className="text-gray-600 mb-4">Enter a stock symbol to get started with analysis</p>
          <p className="text-sm text-gray-500">Real-time technical analysis with AI-powered recommendations</p>
        </Card>
      )}
    </div>
  );
}
