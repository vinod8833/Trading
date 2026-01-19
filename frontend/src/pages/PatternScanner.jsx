import React, { useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";
import { technicalAnalysisApi } from "../api/endpoints";
import { marketStatus, formatters } from "../utils/tradingEngine";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input, Select } from "../components/ui/Input";
import { Badge, Stat, Progress, Alert } from "../components/ui/Common";
import { Tabs } from "../components/ui/Layouts";

export default function PatternScanner() {
  const [symbol, setSymbol] = useState("INFY");
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("patterns");
  const [marketOpen, setMarketOpen] = useState(false);
  const [selectedCapital, setSelectedCapital] = useState(100000);
  const [confidentPatterns, setConfidentPatterns] = useState([]);
  const [timeframe, setTimeframe] = useState("1D");
  const [selectedPattern, setSelectedPattern] = useState(null);

  useEffect(() => {
    const updateMarketStatus = () => {
      const isOpen = marketStatus.isMarketOpen();
      setMarketOpen(isOpen);
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
      const response = await technicalAnalysisApi.analyzeTechnical(symbol, timeframe, marketOpen);
      setAnalysis(response.data);

      const allPatterns = [];

      if (response.data.candlestick_patterns && Array.isArray(response.data.candlestick_patterns)) {
        allPatterns.push(
          ...response.data.candlestick_patterns.map((p) => ({
            ...p,
            type: p.type || "candlestick",
          }))
        );
      }
      if (response.data.chart_patterns && Array.isArray(response.data.chart_patterns)) {
        allPatterns.push(
          ...response.data.chart_patterns.map((p) => ({
            ...p,
            name: p.pattern || p.name,
            type: p.type || "chart",
          }))
        );
      }

      const highConfidence = allPatterns.filter((p) => {
        const conf = p.confidence || 50;
        return parseInt(conf) >= 60;
      });

      setConfidentPatterns(highConfidence);

      if (highConfidence.length > 0) {
        toast.success(`✅ Found ${highConfidence.length} high-confidence patterns`);
      } else if (allPatterns.length > 0) {
        toast.info(`📊 Found ${allPatterns.length} patterns (lower confidence)`);
      } else {
        toast.info(`Scan complete for ${symbol}`);
      }
    } catch (error) {
      toast.error(
        error.response?.data?.detail || error.response?.data?.error || "Scan failed"
      );
      console.error(error);
      setConfidentPatterns([]);
    } finally {
      setIsLoading(false);
    }
  }, [symbol, timeframe, marketOpen]);

  useEffect(() => {
    if (symbol) {
      handleScanStock();
    }
  }, []);

  const getPatternColor = (type) => {
    const types = {
      bullish: "success",
      bearish: "danger",
      neutral: "warning",
      candlestick: "primary",
      chart: "info",
    };
    return types[type?.toLowerCase()] || "default";
  };

  const getConfidenceVariant = (confidence) => {
    if (confidence >= 80) return "success";
    if (confidence >= 60) return "warning";
    return "danger";
  };

  const stats = analysis ? {
    totalPatterns: confidentPatterns.length,
    bullishPatterns: confidentPatterns.filter(
      (p) => p.direction === "BULLISH" || p.type?.includes("bullish")
    ).length,
    bearishPatterns: confidentPatterns.filter(
      (p) => p.direction === "BEARISH" || p.type?.includes("bearish")
    ).length,
    avgConfidence: (
      confidentPatterns.reduce((a, p) => a + (p.confidence || 0), 0) /
      confidentPatterns.length
    ).toFixed(0),
  } : null;

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pattern Scanner</h1>
          <p className="text-gray-600 mt-1">Advanced technical pattern recognition and analysis</p>
        </div>
      </div>

      {!marketOpen && (
        <Alert
          type="info"
          title="Market Closed"
          message="Showing data from the last trading session. Patterns are based on historical data."
          icon="🕐"
        />
      )}

      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Input
              label="Stock Symbol"
              placeholder="e.g., INFY"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === "Enter" && handleScanStock()}
              icon="📊"
            />
            <Select
              label="Timeframe"
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              options={[
                { value: "5M", label: "5 Minutes" },
                { value: "15M", label: "15 Minutes" },
                { value: "1H", label: "1 Hour" },
                { value: "1D", label: "1 Day" },
                { value: "1W", label: "1 Week" },
              ]}
            />
            <Input
              label="Capital (₹)"
              type="number"
              value={selectedCapital}
              onChange={(e) => setSelectedCapital(Number(e.target.value))}
              icon="💰"
            />
            <div className="flex items-end gap-2">
              <Button
                onClick={handleScanStock}
                isLoading={isLoading}
                className="flex-1"
              >
                🔍 Scan
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Stat
            label="Total Patterns"
            value={stats.totalPatterns}
            icon="📊"
          />
          <Stat
            label="Bullish"
            value={stats.bullishPatterns}
            changeType="up"
            icon="📈"
          />
          <Stat
            label="Bearish"
            value={stats.bearishPatterns}
            changeType="down"
            icon="📉"
          />
          <Stat
            label="Avg Confidence"
            value={`${stats.avgConfidence}%`}
            icon="🎯"
          />
        </div>
      )}

      {confidentPatterns.length > 0 && (
        <Tabs
          tabs={[
            {
              id: "patterns",
              label: `All Patterns (${confidentPatterns.length})`,
              icon: "📊",
              content: (
                <div className="space-y-4">
                  {confidentPatterns.map((pattern, idx) => (
                    <Card
                      key={idx}
                      className="hover:shadow-md transition cursor-pointer"
                      onClick={() =>
                        setSelectedPattern(
                          selectedPattern?.name === pattern.name ? null : pattern
                        )
                      }
                    >
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-gray-500 uppercase font-semibold">Pattern</p>
                          <p className="text-lg font-bold text-gray-900 mt-1">
                            {pattern.name || pattern.pattern || "Unknown"}
                          </p>
                          <Badge variant={getPatternColor(pattern.direction || pattern.type)} className="mt-2">
                            {pattern.direction || pattern.type}
                          </Badge>
                        </div>

                        <div>
                          <p className="text-xs text-gray-500 uppercase font-semibold">Confidence</p>
                          <Progress value={pattern.confidence || 0} className="mt-2" />
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          {pattern.strength && (
                            <div>
                              <p className="text-xs text-gray-500 font-semibold">Strength</p>
                              <p className="text-lg font-bold text-gray-900 mt-1">
                                {pattern.strength}
                              </p>
                            </div>
                          )}
                          {pattern.probability && (
                            <div>
                              <p className="text-xs text-gray-500 font-semibold">Probability</p>
                              <p className="text-lg font-bold text-gray-900 mt-1">
                                {pattern.probability}%
                              </p>
                            </div>
                          )}
                        </div>

                        <div className="flex justify-end items-end">
                          <Button size="sm" variant="primary">
                            📋
                          </Button>
                        </div>
                      </div>

                      {selectedPattern?.name === pattern.name && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {pattern.description && (
                              <div className="bg-gray-50 p-3 rounded-lg">
                                <p className="text-xs text-gray-600 font-medium">Description</p>
                                <p className="text-sm text-gray-900 mt-2">{pattern.description}</p>
                              </div>
                            )}
                            {pattern.prediction && (
                              <div className="bg-gray-50 p-3 rounded-lg">
                                <p className="text-xs text-gray-600 font-medium">Prediction</p>
                                <p className="text-sm text-gray-900 mt-2">{pattern.prediction}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              ),
            },
            {
              id: "bullish",
              label: `Bullish (${stats?.bullishPatterns || 0})`,
              icon: "📈",
              content: (
                <div className="space-y-4">
                  {confidentPatterns
                    .filter((p) => p.direction === "BULLISH" || p.type?.includes("bullish"))
                    .map((pattern, idx) => (
                      <Card key={idx}>
                        <div className="flex justify-between items-center">
                          <div>
                            <Badge variant="success" className="mb-2">
                              Bullish
                            </Badge>
                            <p className="font-bold text-gray-900">{pattern.name}</p>
                            <p className="text-sm text-gray-600 mt-1">
                              Confidence: {pattern.confidence}%
                            </p>
                          </div>
                          <Button size="sm" variant="success">
                            💚 Buy Signal
                          </Button>
                        </div>
                      </Card>
                    ))}
                </div>
              ),
            },
            {
              id: "bearish",
              label: `Bearish (${stats?.bearishPatterns || 0})`,
              icon: "📉",
              content: (
                <div className="space-y-4">
                  {confidentPatterns
                    .filter((p) => p.direction === "BEARISH" || p.type?.includes("bearish"))
                    .map((pattern, idx) => (
                      <Card key={idx}>
                        <div className="flex justify-between items-center">
                          <div>
                            <Badge variant="danger" className="mb-2">
                              Bearish
                            </Badge>
                            <p className="font-bold text-gray-900">{pattern.name}</p>
                            <p className="text-sm text-gray-600 mt-1">
                              Confidence: {pattern.confidence}%
                            </p>
                          </div>
                          <Button size="sm" variant="danger">
                            ❤️ Sell Signal
                          </Button>
                        </div>
                      </Card>
                    ))}
                </div>
              ),
            },
          ]}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
      )}

      {/* Empty State */}
      {!isLoading && confidentPatterns.length === 0 && analysis && (
        <Card className="text-center py-12">
          <p className="text-xl text-gray-600 mb-2">📭 No patterns found</p>
          <p className="text-gray-500">Try different timeframe or stock symbol</p>
        </Card>
      )}

      {isLoading && (
        <Card className="text-center py-12">
          <p className="text-gray-600">Scanning patterns...</p>
        </Card>
      )}
    </div>
  );
}
