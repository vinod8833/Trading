import React, { useState, useEffect } from "react";
import { intradayApi, recommendationApi } from "../api/endpoints";
import toast from "react-hot-toast";
import { marketStatus, predictionControl, riskManagement, formatters } from "../utils/tradingEngine";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input, Select } from "../components/ui/Input";
import { Badge, Stat, Alert, Progress } from "../components/ui/Common";
import { Tabs } from "../components/ui/Layouts";

export default function Intraday() {
  const [symbol, setSymbol] = useState("INFY");
  const [tradingStyle, setTradingStyle] = useState("INTRADAY");
  const [capital, setCapital] = useState(50000);
  const [signal, setSignal] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [openTrades, setOpenTrades] = useState([]);
  const [marketOpen, setMarketOpen] = useState(false);
  const [marketStatusInfo, setMarketStatusInfo] = useState(null);
  const [sessionTime, setSessionTime] = useState("OPENING");
  const [lastPrice, setLastPrice] = useState(null);
  const [priceChange, setPriceChange] = useState(null);
  const [activeTab, setActiveTab] = useState("signal");

  useEffect(() => {
    const updateMarketStatus = () => {
      const isOpen = marketStatus.isMarketOpen();
      const status = marketStatus.getMarketStatus();
      setMarketOpen(isOpen);
      setMarketStatusInfo(status);

      const now = new Date();
      const hour = now.getHours();
      if (hour >= 9 && hour < 12) {
        setSessionTime("OPENING");
      } else if (hour >= 12 && hour < 15) {
        setSessionTime("MID_DAY");
      } else if (hour >= 15 && hour < 16) {
        setSessionTime("CLOSING");
      } else {
        setSessionTime("CLOSED");
      }
    };

    updateMarketStatus();
    const timer = setInterval(updateMarketStatus, 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!marketOpen || !symbol) return;

    const refreshPrice = async () => {
      try {
        const response = await recommendationApi.generateRecommendation({
          stock_symbol: symbol,
          trading_style: "INTRADAY",
          capital,
        });

        if (response.data) {
          setLastPrice(response.data.entry_price);
          if (signal) {
            setPriceChange(response.data.entry_price - signal.entry_price);
          }
        }
      } catch (error) {
      }
    };

    const priceTimer = setInterval(refreshPrice, 30000);
    return () => clearInterval(priceTimer);
  }, [marketOpen, symbol, capital, signal]);

  const handleGenerateSignal = async (e) => {
    e?.preventDefault?.();

    if (!marketOpen) {
      toast.error("⏰ Market hours: 9:15 AM - 3:30 PM");
      return;
    }

    if (!symbol || symbol.length === 0) {
      toast.error("Please enter a stock symbol");
      return;
    }

    if (capital < 10000) {
      toast.error("Minimum capital: ₹10,000");
      return;
    }

    setIsLoading(true);

    try {
      const response = await intradayApi.generateIntradaySignal({
        stock_symbol: symbol,
        capital,
      });

      const newSignal = {
        ...response.data,
        timestamp: new Date().toLocaleTimeString("en-IN"),
      };

      setSignal(newSignal);
      setOpenTrades((prev) => [...prev, newSignal]);
      toast.success(`✅ Signal generated for ${symbol}`);
    } catch (error) {
      toast.error(error.response?.data?.error || "Signal generation failed");
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getSessionColor = (session) => {
    switch (session) {
      case "OPENING":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "MID_DAY":
        return "bg-green-100 text-green-800 border-green-200";
      case "CLOSING":
        return "bg-orange-100 text-orange-800 border-orange-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const riskRewardRatio = signal
    ? (signal.target_1 - signal.entry_price) / (signal.entry_price - signal.stop_loss)
    : 0;

  const profitLoss = priceChange
    ? (priceChange / (signal?.entry_price || 1)) * 100
    : 0;

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Intraday Trading</h1>
          <p className="text-gray-600 mt-1">Real-time intraday signals and live trading</p>
        </div>
        <div className={`px-4 py-2 rounded-lg border font-semibold text-sm ${getSessionColor(sessionTime)}`}>
          {sessionTime}
        </div>
      </div>

      {!marketOpen ? (
        <Alert
          type="warning"
          title="Market Closed"
          message="Intraday signals available during market hours (9:15 AM - 3:30 PM IST)"
          icon="🕐"
        />
      ) : (
        <Alert
          type="success"
          title="Market Open"
          message={`Market is live. Last updated: ${new Date().toLocaleTimeString("en-IN")}`}
          icon="🟢"
        />
      )}

      <Card>
        <CardHeader>
          <CardTitle>Generate Trading Signal</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
            <Input
              label="Stock Symbol"
              placeholder="e.g., INFY"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === "Enter" && handleGenerateSignal()}
              icon="📊"
            />
            <Input
              label="Capital (₹)"
              type="number"
              value={capital}
              onChange={(e) => setCapital(Number(e.target.value))}
              min="10000"
              step="5000"
              icon="💰"
            />
            <Select
              label="Risk Level"
              options={[
                { value: "low", label: "Low Risk (0.5%)" },
                { value: "medium", label: "Medium Risk (1%)" },
                { value: "high", label: "High Risk (2%)" },
              ]}
            />
            <div className="flex items-end gap-2">
              <Button
                onClick={handleGenerateSignal}
                isLoading={isLoading}
                className="flex-1"
              >
                ⚡ Generate
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {signal && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Stat
              label="Entry Price"
              value={`₹${signal.entry_price?.toFixed(2)}`}
              change={lastPrice ? `Current: ₹${lastPrice.toFixed(2)}` : ""}
              icon="📍"
            />
            <Stat
              label="Target 1"
              value={`₹${signal.target_1?.toFixed(2)}`}
              change={`+${((signal.target_1 - signal.entry_price) / signal.entry_price * 100).toFixed(2)}%`}
              changeType="up"
              icon="🎯"
            />
            <Stat
              label="Stop Loss"
              value={`₹${signal.stop_loss?.toFixed(2)}`}
              change={`${((signal.stop_loss - signal.entry_price) / signal.entry_price * 100).toFixed(2)}%`}
              changeType="down"
              icon="⛔"
            />
            <Stat
              label="Risk/Reward"
              value={riskRewardRatio.toFixed(2)}
              icon="⚖️"
            />
            <Stat
              label="P&L (Est)"
              value={priceChange ? `${profitLoss.toFixed(2)}%` : "—"}
              change={priceChange ? `₹${priceChange.toFixed(2)}` : ""}
              changeType={profitLoss > 0 ? "up" : profitLoss < 0 ? "down" : "neutral"}
              icon="💹"
            />
          </div>

          <Tabs
            activeTab={activeTab}
            onTabChange={setActiveTab}
            tabs={[
              {
                id: "signal",
                label: "Signal Details",
                icon: "📊",
                content: (
                  <Card>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h3 className="font-semibold text-gray-900 mb-4">Signal Information</h3>
                          <div className="space-y-3">
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Signal Type:</span>
                              <Badge variant={signal.signal_type === "BUY" ? "success" : "danger"}>
                                {signal.signal_type}
                              </Badge>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Confidence:</span>
                              <div className="flex items-center gap-2">
                                <span className="font-semibold">{signal.confidence}%</span>
                              </div>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Time Frame:</span>
                              <span className="font-semibold">Intraday</span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Generated:</span>
                              <span className="font-semibold text-sm">{signal.timestamp}</span>
                            </div>
                          </div>
                        </div>

                        <div>
                          <h3 className="font-semibold text-gray-900 mb-4">Risk Management</h3>
                          <div className="space-y-3">
                            <div>
                              <div className="flex justify-between items-center mb-2">
                                <span className="text-gray-600 text-sm">Capital Risk (1%):</span>
                                <span className="font-semibold">₹{(capital * 0.01).toFixed(0)}</span>
                              </div>
                            </div>
                            <div>
                              <div className="flex justify-between items-center mb-2">
                                <span className="text-gray-600 text-sm">Potential Profit:</span>
                                <span className="font-semibold text-green-600">
                                  ₹{((capital * 0.01) * riskRewardRatio).toFixed(0)}
                                </span>
                              </div>
                            </div>
                            <div>
                              <div className="flex justify-between items-center mb-2">
                                <span className="text-gray-600 text-sm">Max Loss:</span>
                                <span className="font-semibold text-red-600">
                                  ₹{(capital * 0.01).toFixed(0)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ),
              },
              {
                id: "trades",
                label: `Open Trades (${openTrades.length})`,
                icon: "📈",
                content: (
                  <div className="space-y-3">
                    {openTrades.length > 0 ? (
                      openTrades.map((trade, idx) => (
                        <Card key={idx}>
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-bold text-gray-900">{trade.stock_symbol || symbol}</p>
                              <p className="text-sm text-gray-600 mt-1">
                                Entry: ₹{trade.entry_price?.toFixed(2)} | Target: ₹{trade.target_1?.toFixed(2)}
                              </p>
                            </div>
                            <div className="text-right">
                              <Badge variant={trade.signal_type === "BUY" ? "success" : "danger"}>
                                {trade.signal_type}
                              </Badge>
                              <p className="text-sm text-gray-600 mt-2">{trade.timestamp}</p>
                            </div>
                          </div>
                        </Card>
                      ))
                    ) : (
                      <p className="text-gray-500 text-center py-8">No open trades</p>
                    )}
                  </div>
                ),
              },
            ]}
          />

          <div className="flex gap-3 flex-wrap">
            <Button onClick={handleGenerateSignal} variant="primary">
              🔄 Refresh Signal
            </Button>
            <Button
              variant="success"
              onClick={() => {
                toast.success("Trade executed (Paper Trading)");
                setOpenTrades([]);
              }}
            >
              ✅ Execute Trade
            </Button>
            <Button
              variant="danger"
              onClick={() => {
                setSignal(null);
                setOpenTrades([]);
                toast.success("Signal cleared");
              }}
            >
              ✕ Clear
            </Button>
          </div>
        </div>
      )}

      {!signal && !isLoading && (
        <Card className="text-center py-12">
          <p className="text-xl text-gray-600 mb-2">⚡ Generate your first intraday signal</p>
          <p className="text-gray-500">Enter a stock symbol and capital to get started</p>
        </Card>
      )}

      {isLoading && (
        <Card className="text-center py-12">
          <p className="text-gray-600">Generating signal...</p>
        </Card>
      )}
    </div>
  );
}
