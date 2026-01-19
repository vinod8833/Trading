import React, { useState, useEffect } from "react";
import { intradayApi, recommendationApi } from "../api/endpoints";
import { useTradingStore } from "../store";
import toast from "react-hot-toast";
import { riskManagement, marketStatus, formatters } from "../utils/tradingEngine";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge, Stat, Progress, Alert } from "../components/ui/Common";
import { Tabs } from "../components/ui/Layouts";

export default function Signals() {
  const [signals, setSignals] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("all");
  const [selectedMode] = useTradingStore((s) => [s.selectedMode]);
  const [marketOpen, setMarketOpen] = useState(false);
  const [marketStatus_info, setMarketStatusInfo] = useState(null);
  const [defaultCapital, setDefaultCapital] = useState(100000);
  const [selectedSignal, setSelectedSignal] = useState(null);
  const [dataSource, setDataSource] = useState("LIVE");

  useEffect(() => {
    fetchSignals();
    const timer = setInterval(fetchSignals, 5 * 60 * 1000); 
    return () => clearInterval(timer);
  }, [activeTab]);

  useEffect(() => {
    const updateMarketStatus = () => {
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

      let status = "CLOSED";
      let source = "HISTORICAL";

      if (isHoliday) {
        status = "HOLIDAY";
        source = "HISTORICAL";
      } else if (isWeekday && isMarketHours) {
        status = "OPEN";
        source = "LIVE";
      } else {
        status = "CLOSED";
        source = "HISTORICAL";
      }

      setMarketOpen(status === "OPEN");
      setMarketStatusInfo(status);
      setDataSource(source);
    };

    updateMarketStatus();
    const timer = setInterval(updateMarketStatus, 60000);
    return () => clearInterval(timer);
  }, []);

  const isValidSignal = (signal) => {
    const entry = Number(signal.entry_price) || 0;
    const target = Number(signal.target_1) || 0;
    const stop = Number(signal.stop_loss) || 0;
    const confidence = Number(signal.confidence) || 0;

    if (!entry || !target || !stop) return false;

    const validRange = (stop < entry && entry < target) || (target < entry && entry < stop);
    if (!validRange) return false;

    if (confidence <= 0 || confidence > 100) return false;

    if (!signal.signal_type || !['BUY', 'SELL'].includes(signal.signal_type)) return false;

    return true;
  };

  const fetchSignals = async () => {
    setIsLoading(true);
    try {
      let response;
      try {
        response =
          activeTab === "intraday"
            ? await intradayApi.getIntradaySignals()
            : await recommendationApi.getActiveSignals();
      } catch (err) {
        console.error("API Error fetching signals:", err);

        if (err.response?.status === 404) {
          setSignals([]);
          return;
        } else if (err.response?.status === 401) {
          toast.error("Session expired. Please login again.");
        }

        setSignals([]);
        return;
      }

      const signalList = Array.isArray(response.data)
        ? response.data
        : response.data?.results || response.data?.data || [];

      const validSignals = (signalList || []).filter(isValidSignal);

      const enhancedSignals = validSignals.map((signal) => {
        const entry = Number(signal.entry_price) || 0;
        const target = Number(signal.target_1) || 0;
        const stop = Number(signal.stop_loss) || 0;
        const confidence = Number(signal.confidence) || 0;

        const riskAmount = Math.abs(entry - stop);
        const rewardAmount = Math.abs(target - entry);
        const riskReward = riskAmount > 0 ? rewardAmount / riskAmount : 0;

        return {
          ...signal,
          entry_price: entry,
          target_1: target,
          stop_loss: stop,
          confidence: Math.min(100, Math.max(0, confidence)),
          market_status: marketOpen ? "LIVE" : "HISTORICAL",
          riskReward: riskReward.toFixed(2),
          expectedProfit: ((rewardAmount / entry) * 100).toFixed(2),
          validated: true,
          timestamp: new Date().toLocaleString("en-IN"),
        };
      });

      setSignals(enhancedSignals);
    } finally {
      setIsLoading(false);
    }
  };

  const getSignalTypeColor = (type) => {
    return type === "BUY" ? "success" : type === "SELL" ? "danger" : "warning";
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return "success";
    if (confidence >= 60) return "warning";
    return "danger";
  };

  const buySignals = signals.filter((s) => s.signal_type === "BUY");
  const sellSignals = signals.filter((s) => s.signal_type === "SELL");
  const intradaySignals = signals.filter((s) => s.signal_type === "INTRADAY");
  
  const totalSignals = signals.length;
  const avgConfidence = totalSignals > 0
    ? (signals.reduce((sum, s) => sum + (s.confidence || 0), 0) / totalSignals).toFixed(0)
    : 0;

  const filteredSignals = signals.filter((signal) => {
    if (activeTab === "buy") return signal.signal_type === "BUY";
    if (activeTab === "sell") return signal.signal_type === "SELL";
    if (activeTab === "intraday") return signal.signal_type === "INTRADAY";
    return true;
  });

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Trade Signals</h1>
          <p className="text-gray-600 mt-1">Real-time AI-powered trading signals and recommendations</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={fetchSignals} isLoading={isLoading} variant="primary">
            Refresh
          </Button>
          <Button variant="secondary">Export</Button>
        </div>
      </div>

      {marketStatus_info && (
        <Alert
          type={marketOpen ? "success" : marketStatus_info === "HOLIDAY" ? "warning" : "info"}
          title={marketStatus_info === "HOLIDAY" ? "Market Holiday" : marketOpen ? "Market Open" : "Market Closed"}
          message={
            marketStatus_info === "HOLIDAY"
              ? "Today is a market holiday. Showing data from previous trading session."
              : marketOpen
              ? "Market is currently OPEN. Signals are LIVE."
              : "Market is currently CLOSED. Showing data from last trading session."
          }
          icon={marketStatus_info === "HOLIDAY" ? "📅" : marketOpen ? "🟢" : "🔴"}
        />
      )}

      {totalSignals > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Stat
            label="Total Signals"
            value={totalSignals}
            change={`Today's signals`}
            icon="📊"
          />
          <Stat
            label="Buy Signals"
            value={buySignals.length}
            change={totalSignals > 0 ? `${((buySignals.length / totalSignals) * 100).toFixed(0)}%` : "0%"}
            changeType="up"
            icon="📈"
          />
          <Stat
            label="Sell Signals"
            value={sellSignals.length}
            change={totalSignals > 0 ? `${((sellSignals.length / totalSignals) * 100).toFixed(0)}%` : "0%"}
            changeType="down"
            icon="📉"
          />
          <Stat
            label="Avg Confidence"
            value={`${avgConfidence}%`}
            change={avgConfidence >= 70 ? "Strong" : "Moderate"}
            changeType={avgConfidence >= 70 ? "up" : "warning"}
            icon="🎯"
          />
        </div>
      ) : null}
      <Tabs
        tabs={[
          { 
            id: "all", 
            label: `All Signals (${totalSignals})`, 
            icon: "📊",
            badge: totalSignals > 0 ? totalSignals : null
          },
          { 
            id: "buy", 
            label: `Buy (${buySignals.length})`, 
            icon: "📈",
            badge: buySignals.length > 0 ? buySignals.length : null
          },
          { 
            id: "sell", 
            label: `Sell (${sellSignals.length})`, 
            icon: "📉",
            badge: sellSignals.length > 0 ? sellSignals.length : null
          },
          { 
            id: "intraday", 
            label: `Intraday (${intradaySignals.length})`, 
            icon: "⚡",
            badge: intradaySignals.length > 0 ? intradaySignals.length : null
          },
        ]}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <div className="space-y-4">
        {isLoading ? (
          <Card className="text-center py-12">
            <p className="text-gray-600">Loading signals...</p>
          </Card>
        ) : filteredSignals.length > 0 ? (
          filteredSignals.map((signal, index) => (
            <Card
              key={`${signal.stock_symbol}-${index}`}
              className="hover:shadow-md transition cursor-pointer border-l-4"
              style={{
                borderLeftColor: signal.signal_type === "BUY" ? "#10b981" : "#ef4444"
              }}
              onClick={() => setSelectedSignal(selectedSignal?.stock_symbol === signal.stock_symbol ? null : signal)}
            >
              <div className="grid grid-cols-1 lg:grid-cols-6 gap-4">
                <div className="lg:col-span-1">
                  <p className="text-xs text-gray-500 uppercase font-semibold">Stock</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {signal.stock_symbol || "N/A"}
                  </p>
                  <Badge 
                    variant={getSignalTypeColor(signal.signal_type)} 
                    className="mt-2"
                  >
                    {signal.signal_type}
                  </Badge>
                  <div className="mt-2">
                    <Badge 
                      variant={signal.market_status === "LIVE" ? "success" : "warning"}
                      className="text-xs"
                    >
                      {signal.market_status}
                    </Badge>
                  </div>
                </div>

                <div className="lg:col-span-2 grid grid-cols-3 gap-3">
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold">Entry</p>
                    <p className="text-lg font-bold text-gray-900 mt-1">
                      ₹{(Number(signal.entry_price) || 0).toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold">Target</p>
                    <p className="text-lg font-bold text-green-600 mt-1">
                      ₹{(Number(signal.target_1) || 0).toFixed(2)}
                    </p>
                    <p className="text-xs text-green-600 mt-0.5">
                      +{Number(signal.expectedProfit || 0).toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold">Stop</p>
                    <p className="text-lg font-bold text-red-600 mt-1">
                      ₹{(Number(signal.stop_loss) || 0).toFixed(2)}
                    </p>
                  </div>
                </div>

                <div className="lg:col-span-2">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500 uppercase font-semibold mb-2">Confidence</p>
                      <div className="flex items-center gap-2">
                        <Progress
                          value={Number(signal.confidence || 0)}
                          className="flex-1 text-sm"
                        />
                        <span className="font-bold text-sm w-12 text-right">
                          {Number(signal.confidence || 0).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase font-semibold mb-1">R:R Ratio</p>
                      <p className="text-2xl font-bold text-blue-600">
                        1:{Number(signal.riskReward || 0).toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="lg:col-span-1 flex items-end justify-end gap-2">
                  <Button
                    size="sm"
                    variant="primary"
                    onClick={(e) => {
                      e.stopPropagation();
                      toast.success(`Added ${signal.stock_symbol} to watchlist`);
                    }}
                  >
                    ⭐
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      toast.success(`Copied signal details`);
                    }}
                  >
                    📋
                  </Button>
                </div>
              </div>

              {selectedSignal?.stock_symbol === signal.stock_symbol && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600 font-medium">Signal Generated</p>
                      <p className="text-sm font-semibold text-gray-900 mt-1">
                        {signal.timestamp || new Date().toLocaleString("en-IN")}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600 font-medium">Confidence Strength</p>
                      <Badge 
                        variant={getConfidenceColor(signal.confidence || 0)}
                        className="mt-1"
                      >
                        {signal.confidence >= 80 ? "Very High" : signal.confidence >= 60 ? "High" : "Moderate"}
                      </Badge>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600 font-medium">Data Source</p>
                      <p className="text-lg font-semibold text-gray-900 mt-1">
                        {dataSource}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600 font-medium">Validation</p>
                      <Badge variant="success" className="mt-1">
                        ✓ Valid
                      </Badge>
                    </div>
                  </div>
                </div>
              )}
            </Card>
          ))
        ) : (
          <Card className="text-center py-12">
            <p className="text-xl text-gray-600 mb-2">
              {activeTab === "intraday" ? "⚡ No intraday signals" : "📭 No signals yet"}
            </p>
            <p className="text-gray-500">
              {totalSignals === 0
                ? "Generate stock analyses to get trading signals"
                : `No ${activeTab} signals at the moment`}
            </p>
            {totalSignals === 0 && (
              <Button 
                className="mt-4" 
                onClick={() => window.location.href = "/dashboard"}
              >
                Go to Dashboard
              </Button>
            )}
          </Card>
        )}
      </div>
    </div>
  );
}
