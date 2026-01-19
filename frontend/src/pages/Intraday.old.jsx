import React, { useState, useEffect } from "react";
import { intradayApi, recommendationApi } from "../api/endpoints";
import toast from "react-hot-toast";
import { marketStatus, predictionControl, riskManagement, formatters } from "../utils/tradingEngine";

export default function Intraday() {
  const [symbol, setSymbol] = useState("INFY");
  const [tradingStyle, setTradingStyle] = useState("INTRADAY");
  const [capital, setCapital] = useState(50000);
  const [signal, setSignal] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [openTrades, setOpenTrades] = useState([]);
  const [marketOpen, setMarketOpen] = useState(false);
  const [marketStatusInfo, setMarketStatusInfo] = useState(null);
  const [predictionMode, setPredictionMode] = useState(null);
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [sessionTime, setSessionTime] = useState("OPENING");
  const [lastPrice, setLastPrice] = useState(null);
  const [priceChange, setPriceChange] = useState(null);
  const [refreshTimer, setRefreshTimer] = useState(60);

  useEffect(() => {
    const updateMarketStatus = () => {
      const isOpen = marketStatus.isMarketOpen();
      const status = marketStatus.getMarketStatus();
      setMarketOpen(isOpen);
      setMarketStatusInfo(status);
      setPredictionMode(predictionControl.getPredictionMode(isOpen));

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
          capital
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
    e.preventDefault();

    if (!marketOpen) {
      toast.error("⏰ Market is closed. Intraday signals available during market hours (9:15 AM - 3:30 PM)");
      return;
    }

    if (!symbol || symbol.length === 0) {
      toast.error("Please enter a stock symbol");
      return;
    }

    if (capital < 10000) {
      toast.error("Minimum capital required is ₹10,000");
      return;
    }

    setIsLoading(true);

    try {
      const response = await intradayApi.generateIntradaySignal({
        stock_symbol: symbol.toUpperCase(),
        capital: capital,
      });

      const signalData = response.data;
      
      if (signalData.validation && !signalData.validation.valid) {
        if (signalData.validation.errors && signalData.validation.errors.length > 0) {
          signalData.validation.errors.forEach(error => {
            toast.error(error);
          });
        }
      }
      
      if (signalData.validation && signalData.validation.warnings && signalData.validation.warnings.length > 0) {
        signalData.validation.warnings.forEach(warning => {
          toast.error(warning);
        });
      }
      
      setSignal(signalData);
      setLastPrice(signalData.current_price);

      if (signalData.entry_price && signalData.stop_loss) {
        const pnlData = riskManagement.calculatePnL(
          capital,
          signalData.entry_price,
          [signalData.target_1, signalData.target_2, signalData.target_3],
          signalData.stop_loss,
          signalData.quantity
        );
        setRiskAssessment(pnlData);

        const warnings = riskManagement.assessRisk(
          capital,
          signalData.entry_price,
          signalData.stop_loss,
          [signalData.target_1]
        );

        if (warnings.warnings && warnings.warnings.length > 0) {
          warnings.warnings.forEach(w => toast.error(w));
        } else if (!signalData.validation || signalData.validation.valid) {
          toast.success("Intraday signal generated - Review risk details before executing!");
        }
      }
    } catch (error) {
      console.error("Signal generation error:", error);
      
      if (error.response?.status === 400 && error.response?.data?.validation) {
        const validation = error.response.data.validation;
        if (validation.errors && validation.errors.length > 0) {
          validation.errors.forEach(err => toast.error(err));
        }
      } else {
        toast.error(error.response?.data?.error || "Failed to generate signal");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleExecuteTrade = async () => {
    if (!signal) return;

    if (!marketOpen) {
      toast.error("Market is closed. Cannot execute trades outside market hours.");
      return;
    }

    try {
      const capitalRequired = signal.quantity * signal.entry_price;
      if (capitalRequired > capital) {
        toast.error(`Insufficient capital. Required: ₹${capitalRequired.toFixed(0)}, Available: ₹${capital}`);
        return;
      }

      await recommendationApi.executeRecommendation(signal.id);
      
      const newTrade = {
        ...signal,
        entry_time: new Date(),
        status: 'ACTIVE',
        current_price: signal.entry_price
      };
      
      setOpenTrades([...openTrades, newTrade]);
      toast.success("Trade executed successfully!");
      setSignal(null);
      setRiskAssessment(null);
    } catch (error) {
      console.error("Trade execution error:", error);
      toast.error(error.response?.data?.error || "Failed to execute trade");
    }
  };

  const handleCloseTrade = async (tradeIndex) => {
    const trade = openTrades[tradeIndex];
    
    if (!lastPrice) {
      toast.error("Unable to close trade - no price data available");
      return;
    }

    try {
      const updatedTrades = openTrades.filter((_, idx) => idx !== tradeIndex);
      setOpenTrades(updatedTrades);
      
      const pnl = (lastPrice - trade.entry_price) * trade.quantity;
      const pnlPercent = ((lastPrice - trade.entry_price) / trade.entry_price) * 100;
      
      if (pnl > 0) {
        toast.success(`Trade closed with profit: ₹${pnl.toFixed(0)} (${pnlPercent.toFixed(2)}%)`);
      } else {
        toast.error(`Trade closed with loss: ₹${pnl.toFixed(0)} (${pnlPercent.toFixed(2)}%)`);
      }
    } catch (error) {
      toast.error("Failed to close trade");
    }
  };

  const getSessionColor = (session) => {
    switch (session) {
      case "OPENING":
        return "bg-orange-100 text-orange-800";
      case "MID_DAY":
        return "bg-blue-100 text-blue-800";
      case "CLOSING":
        return "bg-red-100 text-red-800";
      case "CLOSED":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getSignalColor = (signalType) => {
    switch (signalType) {
      case "BUY":
        return "text-green-600 bg-green-50 border-green-500";
      case "SELL":
        return "text-red-600 bg-red-50 border-red-500";
      case "HOLD":
        return "text-yellow-600 bg-yellow-50 border-yellow-500";
      default:
        return "text-gray-600 bg-gray-50 border-gray-500";
    }
  };

  const formatCurrency = (value) => {
    if (!value) return "₹0";
    return `₹${parseFloat(value).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  };

  return (
    <div className="space-y-6">
      {marketStatusInfo && (
        <div className={`${marketStatusInfo.color} rounded-lg p-4 border border-gray-200`}>
          <div className="flex justify-between items-center">
            <div>
              <p className="font-semibold text-gray-900">{marketStatusInfo.label}</p>
              <p className="text-sm text-gray-600 mt-1">
                {marketOpen ? "Intraday trading available" : "🔒 Trading disabled - market closed"}
              </p>
            </div>
            <span className="text-3xl">
              {marketOpen ? '🟢' : '🔒'}
            </span>
          </div>
        </div>
      )}

      {!marketOpen && (
        <div className="bg-gray-50 border-l-4 border-gray-400 p-4 rounded">
          <div className="flex items-start">
            <span className="text-2xl mr-3">📅</span>
            <div>
              <h3 className="font-bold text-gray-900">Market Closed - Analysis Mode</h3>
              <p className="text-sm text-gray-700 mt-1">Intraday signals are disabled when the market is closed.</p>
              {(() => {
                const timeLeft = marketStatus.getTimeUntilMarketOpen();
                return (
                  <p className="text-xs text-blue-600 font-semibold mt-2">
                    ⏰ Market opens in {timeLeft.hoursUntil}h {timeLeft.minutesUntil}m (9:15 AM IST)
                  </p>
                );
              })()}
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">⚡ Intraday Trading</h1>
            <p className="text-gray-600 mt-2">High-frequency trading signals with tight risk management</p>
          </div>
          <div className={`px-4 py-2 rounded-lg font-semibold text-sm ${getSessionColor(sessionTime)}`}>
            {sessionTime === "OPENING" && "📈 Morning Session (9:15-12:00)"}
            {sessionTime === "MID_DAY" && "📊 Mid Day (12:00-3:30 PM)"}
            {sessionTime === "CLOSING" && "📉 Closing (3:00-3:30 PM)"}
            {sessionTime === "CLOSED" && "🔒 Market Closed"}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleGenerateSignal} className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Stock Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="e.g., INFY"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Capital (₹)</label>
            <input
              type="number"
              value={capital}
              onChange={(e) => setCapital(parseInt(e.target.value))}
              min="10000"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Session</label>
            <select
              value={sessionTime}
              disabled
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600"
            >
              <option value={sessionTime}>{sessionTime}</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={isLoading || sessionTime === "CLOSED"}
              className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold py-2 rounded-lg hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Generating..." : "Generate Signal"}
            </button>
          </div>

          <div className="flex items-end">
            <button
              type="button"
              onClick={() => setSignal(null)}
              className="w-full bg-gray-300 text-gray-700 font-semibold py-2 rounded-lg hover:shadow-lg transition"
            >
              Clear
            </button>
          </div>
        </form>
      </div>

      {signal && (
        <div className={`rounded-lg shadow-md p-8 border-l-4 ${getSignalColor(signal.signal)}`}>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2 font-semibold">Signal</p>
              <p className={`text-4xl font-bold ${signal.signal === 'BUY' ? 'text-green-600' : signal.signal === 'SELL' ? 'text-red-600' : 'text-yellow-600'}`}>
                {signal.signal}
              </p>
              <p className="text-xs text-gray-600 mt-2">Strength: {signal.signal_strength || 'STANDARD'}</p>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2 font-semibold">Entry Price</p>
              <p className="text-4xl font-bold text-purple-600">{formatCurrency(signal.entry_price)}</p>
              <p className="text-xs text-gray-600 mt-2">Live: {formatCurrency(signal.current_price)}</p>
            </div>

            <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2 font-semibold">Stop Loss</p>
              <p className="text-4xl font-bold text-red-600">{formatCurrency(signal.stop_loss)}</p>
              <p className="text-xs text-gray-600 mt-2">Risk: {signal.risk_percent.toFixed(2)}%</p>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2 font-semibold">Confidence</p>
              <p className="text-4xl font-bold text-green-600">{signal.confidence_level?.toFixed(0) || signal.confidence_level || '0'}%</p>
              <p className="text-xs text-gray-600 mt-2">Win: {signal.win_probability?.toFixed(0) || '0'}%</p>
            </div>

            <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2 font-semibold">Position</p>
              <p className="text-3xl font-bold text-orange-600">{signal.quantity} units</p>
              <p className="text-xs text-gray-600 mt-2">Capital: {formatCurrency(signal.capital_required)}</p>
            </div>
          </div>

          {signal.technical_indicators && (
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-6">
              <h3 className="font-bold text-gray-900 mb-3">📊 Technical Indicators</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                {signal.technical_indicators.vwap && (
                  <div className="bg-white p-3 rounded border border-blue-200">
                    <p className="text-xs text-gray-600">VWAP</p>
                    <p className="font-bold text-blue-600">{signal.technical_indicators.vwap.value?.toFixed(2)}</p>
                    <p className="text-xs mt-1">{signal.technical_indicators.vwap.signal}</p>
                  </div>
                )}
                {signal.technical_indicators.ema && (
                  <div className="bg-white p-3 rounded border border-purple-200">
                    <p className="text-xs text-gray-600">EMA Signal</p>
                    <p className="font-bold text-purple-600">{signal.technical_indicators.ema.signal}</p>
                    <p className="text-xs mt-1">12/26 Cross</p>
                  </div>
                )}
                {signal.technical_indicators.rsi && (
                  <div className="bg-white p-3 rounded border border-red-200">
                    <p className="text-xs text-gray-600">RSI</p>
                    <p className="font-bold text-red-600">{signal.technical_indicators.rsi.value?.toFixed(1)}</p>
                    <p className="text-xs mt-1">{signal.technical_indicators.rsi.signal}</p>
                  </div>
                )}
                {signal.technical_indicators.volume && (
                  <div className="bg-white p-3 rounded border border-green-200">
                    <p className="text-xs text-gray-600">Volume</p>
                    <p className="font-bold text-green-600">{signal.technical_indicators.volume.signal}</p>
                    <p className="text-xs mt-1">Ratio: {signal.technical_indicators.volume.ratio}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {riskAssessment && riskAssessment.valid && (
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 mb-6">
              <h3 className="font-bold text-gray-900 mb-3">💰 Position Sizing & Risk (0.5% Rule)</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
                <div className="bg-white p-3 rounded">
                  <p className="text-xs text-gray-600">Max Risk (0.5%)</p>
                  <p className="font-bold text-green-600">{formatCurrency(riskAssessment.maxRisk)}</p>
                </div>
                <div className="bg-white p-3 rounded">
                  <p className="text-xs text-gray-600">Position Size</p>
                  <p className="font-bold text-blue-600">{riskAssessment.position} units</p>
                </div>
                <div className="bg-white p-3 rounded">
                  <p className="text-xs text-gray-600">Actual Risk</p>
                  <p className="font-bold text-orange-600">{formatCurrency(riskAssessment.riskAmount)}</p>
                </div>
                <div className="bg-white p-3 rounded">
                  <p className="text-xs text-gray-600">Risk/Reward</p>
                  <p className="font-bold text-purple-600">1:{signal.risk_reward_ratio?.toFixed(2) || '0'}</p>
                </div>
                <div className="bg-white p-3 rounded">
                  <p className="text-xs text-gray-600">Session Close</p>
                  <p className="font-bold text-red-600">Auto Square-off</p>
                </div>
              </div>
            </div>
          )}

          {riskAssessment && riskAssessment.valid && (() => {
            const warnings = riskManagement.assessRisk(
              capital,
              signal.entry_price,
              signal.stop_loss,
              [signal.target_1]
            );
            return warnings.warnings && warnings.warnings.length > 0 ? (
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded">
                <h4 className="font-bold text-yellow-900 mb-2">⚠️ Risk Alerts</h4>
                <ul className="text-sm text-yellow-800 space-y-1">
                  {warnings.warnings.map((w, i) => <li key={i}>• {w}</li>)}
                </ul>
              </div>
            ) : null;
          })()}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 pb-6 border-b">
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Target 1</p>
              <p className="text-3xl font-bold text-green-600">{formatCurrency(signal.target_1)}</p>
              <p className="text-xs text-gray-600 mt-2">+{((signal.target_1 - signal.entry_price) / signal.entry_price * 100).toFixed(2)}%</p>
            </div>
            <div className="bg-emerald-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Target 2</p>
              <p className="text-3xl font-bold text-emerald-600">{formatCurrency(signal.target_2)}</p>
              <p className="text-xs text-gray-600 mt-2">+{((signal.target_2 - signal.entry_price) / signal.entry_price * 100).toFixed(2)}%</p>
            </div>
            <div className="bg-teal-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Target 3</p>
              <p className="text-3xl font-bold text-teal-600">{formatCurrency(signal.target_3)}</p>
              <p className="text-xs text-gray-600 mt-2">+{((signal.target_3 - signal.entry_price) / signal.entry_price * 100).toFixed(2)}%</p>
            </div>
            <div className="bg-cyan-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Target 4</p>
              <p className="text-3xl font-bold text-cyan-600">{formatCurrency(signal.target_4)}</p>
              <p className="text-xs text-gray-600 mt-2">+{((signal.target_4 - signal.entry_price) / signal.entry_price * 100).toFixed(2)}%</p>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={handleExecuteTrade}
              disabled={!marketOpen}
              className="flex-1 bg-green-600 text-white font-semibold py-3 rounded-lg hover:bg-green-700 hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
               Execute Trade
            </button>
            <button
              onClick={() => setSignal(null)}
              className="flex-1 bg-gray-300 text-gray-700 font-semibold py-3 rounded-lg hover:bg-gray-400 hover:shadow-lg transition"
            >
               Discard
            </button>
          </div>
        </div>
      )}

      {openTrades.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">📊 Open Intraday Trades ({openTrades.length})</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Symbol</th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Signal</th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Entry</th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Target 1</th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Stop Loss</th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Qty</th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">P&L</th>
                  <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {openTrades.map((trade, idx) => {
                  const pnl = (lastPrice - trade.entry_price) * trade.quantity;
                  const pnlPercent = ((lastPrice - trade.entry_price) / trade.entry_price) * 100;
                  return (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-semibold text-gray-900">{trade.stock || 'N/A'}</td>
                      <td className={`px-4 py-3 font-bold ${trade.signal === "BUY" ? "text-green-600" : "text-red-600"}`}>
                        {trade.signal}
                      </td>
                      <td className="px-4 py-3 text-gray-700">{formatCurrency(trade.entry_price)}</td>
                      <td className="px-4 py-3 text-gray-700">{formatCurrency(trade.target_1)}</td>
                      <td className="px-4 py-3 text-gray-700">{formatCurrency(trade.stop_loss)}</td>
                      <td className="px-4 py-3 text-gray-700">{trade.quantity}</td>
                      <td className={`px-4 py-3 font-bold ${pnl > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(pnl)} ({pnlPercent.toFixed(2)}%)
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => handleCloseTrade(idx)}
                          className="text-red-600 hover:text-red-800 font-semibold hover:bg-red-50 px-3 py-1 rounded"
                        >
                          Close
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {sessionTime === "CLOSING" && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6 text-center">
          <p className="text-orange-800 font-semibold text-lg">⏰ Closing Session</p>
          <p className="text-orange-700 mt-2">All intraday positions will be automatically squared off at market close (3:30 PM)</p>
        </div>
      )}

      {!signal && openTrades.length === 0 && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <p className="text-gray-600 text-lg">🚀 Generate a signal to see intraday trading recommendations</p>
          <p className="text-gray-400 mt-2">Signals use VWAP, EMA, and volume analysis for precise entry/exit points</p>
        </div>
      )}
    </div>
  );
}
