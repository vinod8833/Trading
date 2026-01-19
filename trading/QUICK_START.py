#!/usr/bin/env python3
"""
AI DATA INTEGRATION SYSTEM - QUICK START GUIDE
Fast setup and testing procedures
"""

import json

QUICK_START = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   AI DATA INTEGRATION SYSTEM - QUICK START                 ║
║                                                                            ║
║ Complete system for live market data, technical analysis, and signals     ║
╚════════════════════════════════════════════════════════════════════════════╝


📁 FILES CREATED
════════════════════════════════════════════════════════════════════════════

1. trading/data_integration.py (400+ lines)
   └─ DataIntegrationEngine: Fetches data from NSE, YFinance
   
2. trading/technical_indicators.py (500+ lines)
   └─ TechnicalIndicatorsEngine: Calculates 30+ indicators
   
3. trading/prediction_engine.py (400+ lines)
   └─ PredictionEngine: Predicts 5-minute price movements
   
4. trading/signal_generation.py (300+ lines)
   └─ SignalGenerationEngine: Complete signal generation
   
5. trading/ai_signals_views.py (400+ lines)
   └─ REST API endpoints for all operations
   
6. trading/ai_signals_urls.py (30 lines)
   └─ URL routing configuration


✅ SETUP INSTRUCTIONS
════════════════════════════════════════════════════════════════════════════

STEP 1: Install Dependencies
  $ pip install yfinance beautifulsoup4 requests
  
STEP 2: Django Configuration (Already Done ✓)
  - URLs registered in kvk_trading/urls.py
  - Endpoints available at /api/ai/*
  
STEP 3: Test the System
  - See API Testing section below


🚀 API TESTING (via cURL or Postman)
════════════════════════════════════════════════════════════════════════════

A. CHECK MARKET STATUS
   ─────────────────────────────────────────────────────────────────────
   curl http://localhost:8001/api/ai/market-status/
   
   Response:
   {
     "market_open": true,
     "message": "Market is OPEN",
     "data_type": "LIVE",
     "timestamp": "2026-01-19T14:30:00"
   }


B. GENERATE TRADING SIGNAL
   ─────────────────────────────────────────────────────────────────────
   curl -X POST http://localhost:8001/api/ai/generate-signal/ \\
     -H "Content-Type: application/json" \\
     -d '{
       "symbol": "INFY",
       "capital": 100000,
       "trader_type": "SWING"
     }'
   
   Expected Response:
   {
     "symbol": "INFY",
     "signal": {
       "type": "BUY",
       "confidence": 78.5,
       "is_executable": true
     },
     "execution": {
       "entry": 1680.50,
       "stop_loss": 1670.20,
       "target_1": 1695.80,
       "target_2": 1715.30
     },
     "market": {
       "status": "LIVE",
       "data_freshness_minutes": 2
     }
   }


C. FETCH MARKET DATA
   ─────────────────────────────────────────────────────────────────────
   curl http://localhost:8001/api/ai/market-data/?symbol=INFY&data_type=QUOTE
   
   Returns: Live quote with price, volume, open, high, low


D. CHECK DATA QUALITY
   ─────────────────────────────────────────────────────────────────────
   curl http://localhost:8001/api/ai/data-quality/?symbol=INFY
   
   Response tells you:
   - Is data valid for trading?
   - Any issues or warnings?
   - Overall quality score


E. CALCULATE INDICATORS
   ─────────────────────────────────────────────────────────────────────
   curl -X POST http://localhost:8001/api/ai/calculate-indicators/ \\
     -H "Content-Type: application/json" \\
     -d '{
       "symbol": "INFY",
       "candles": [ ... 50+ historical candles ... ]
     }'


F. PREDICT 5-MINUTE MOVEMENT
   ─────────────────────────────────────────────────────────────────────
   curl -X POST http://localhost:8001/api/ai/predict-movement/ \\
     -H "Content-Type: application/json" \\
     -d '{
       "symbol": "INFY",
       "candles": [ ... 50+ intraday candles ... ],
       "indicators": { ... calculated indicators ... },
       "current_price": 1680.50
     }'


📊 SIGNAL INTERPRETATION GUIDE
════════════════════════════════════════════════════════════════════════════

SIGNAL TYPE:
  BUY     → Go long, follow entry/target/stop
  SELL    → Go short, follow entry/target/stop
  HOLD    → No opportunity right now

CONFIDENCE (0-100):
  90-100  → Very strong, high conviction
  75-90   → Strong, follow signal
  60-75   → Moderate, use caution
  50-60   → Weak, consider waiting
  <50     → Very weak, skip signal

EXECUTION LEVELS:
  Entry       → Where to enter the trade
  Stop Loss   → Where to exit if wrong (MUST SET)
  Target 1-3  → Where to book profits
  
RISK/REWARD RATIO:
  1:2         → Risk ₹100 to make ₹200 (minimum)
  1:3         → Risk ₹100 to make ₹300 (good)
  1:5         → Risk ₹100 to make ₹500 (excellent)

MARKET STATUS:
  LIVE        → During market hours, use immediately
  HISTORICAL  → Market closed, for next session


🎯 FRONTEND INTEGRATION EXAMPLE
════════════════════════════════════════════════════════════════════════════

REACT COMPONENT: Get signal and display to user

import React, { useState, useEffect } from 'react';

function TradingSignal({ symbol }) {
  const [signal, setSignal] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const fetchSignal = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/ai/generate-signal/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          capital: 100000,
          trader_type: 'SWING'
        })
      });
      
      const data = await res.json();
      setSignal(data);
    } catch (error) {
      console.error('Error fetching signal:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchSignal();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchSignal, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [symbol]);
  
  if (loading) return <div>Loading...</div>;
  if (!signal) return <div>No signal available</div>;
  
  return (
    <div className="trading-signal">
      {/* Show signal type with color */}
      <div className={`signal-type ${signal.signal.type.toLowerCase()}`}>
        {signal.signal.type} ({signal.signal.confidence.toFixed(1)}%)
      </div>
      
      {/* Show execution levels */}
      <div className="levels">
        <div>Entry: ₹{signal.execution.entry.toFixed(2)}</div>
        <div>Stop: ₹{signal.execution.stop_loss.toFixed(2)}</div>
        <div>Target: ₹{signal.execution.target_1.toFixed(2)}</div>
      </div>
      
      {/* Show risk/reward */}
      <div>Risk/Reward: 1:{signal.risk.risk_reward_ratio.toFixed(1)}</div>
      
      {/* Show warnings if any */}
      {signal.metadata.warnings.length > 0 && (
        <div className="warnings">
          {signal.metadata.warnings.map((w, i) => (
            <div key={i}>{w}</div>
          ))}
        </div>
      )}
      
      {/* Action button */}
      {signal.signal.is_executable && (
        <button onClick={() => executeTrade(signal)}>
          Execute {signal.signal.type}
        </button>
      )}
    </div>
  );
}

export default TradingSignal;


📈 WHAT EACH INDICATOR MEANS
════════════════════════════════════════════════════════════════════════════

EMA (20, 50, 100, 200):
  • EMA20 > EMA50 > EMA100 > EMA200 = BULLISH
  • EMA20 < EMA50 < EMA100 < EMA200 = BEARISH
  • Price above EMA = Uptrend, below = Downtrend

RSI (Relative Strength Index):
  • >70 = OVERBOUGHT (potential pullback)
  • <30 = OVERSOLD (potential bounce)
  • 40-60 = NEUTRAL (no clear conviction)

MACD:
  • MACD > Signal = BULLISH
  • MACD < Signal = BEARISH
  • Histogram expands = Momentum strengthening

ATR (Average True Range):
  • Higher ATR = More volatility
  • Lower ATR = Less volatility
  • Use for stop loss placement

VWAP (Volume Weighted Average Price):
  • Price > VWAP = Bullish
  • Price < VWAP = Bearish

Volume:
  • Increasing = Confirmation of signal
  • Decreasing = Signal weakness


🔧 MONITORING & LOGGING
════════════════════════════════════════════════════════════════════════════

Enable logging to see what's happening:

import logging

logger = logging.getLogger('trading')
logging.basicConfig(level=logging.INFO)

Then check logs:
  tail -f /var/log/trading.log


Example log messages:
  ✓ NSE Quote fetched: INFY @ 1680.50
  ✓ YFinance Historical fetched: INFY, 100 candles
  ✓ Calculated indicators for INFY
  ✓ Prediction for INFY: UP (72.5% confidence)
  ✓ Signal generated for INFY: BUY (78.5%)


⚠️ IMPORTANT NOTES
════════════════════════════════════════════════════════════════════════════

1. DATA QUALITY
   • System only generates signals when data is valid
   • If data quality is poor, it will say "No signal available"
   • Always check data freshness (should be < 5 minutes)

2. MARKET HOURS
   • System knows when market is open (9:15 AM - 3:30 PM IST)
   • Signals are marked as LIVE or HISTORICAL
   • Use LIVE signals for immediate execution
   • Use HISTORICAL signals only for planning

3. RISK MANAGEMENT
   • ALWAYS set stop loss
   • Never risk more than 2% per trade
   • Position size is calculated automatically
   • Risk/Reward ratio must be >= 1:2

4. CONFIDENCE SCORES
   • 78% confidence ≠ 78% probability of profit
   • It means 78% of indicators/patterns agree
   • Past performance ≠ future results
   • No system can guarantee 100% accuracy

5. DATA SOURCES
   • NSE: Official data, most reliable
   • YFinance: Fallback source if NSE fails
   • Chartink: Requires premium API
   • Screener: Requires direct scraping


📞 QUICK TROUBLESHOOTING
════════════════════════════════════════════════════════════════════════════

Q: "Could not fetch market data"
A: Check internet connection, NSE server status

Q: "Insufficient data"  
A: Need at least 50 daily candles or 100 5-min candles

Q: "All signals are HOLD"
A: Market conditions poor or high volatility. Wait for better setup.

Q: "Confidence is low (20-30%)"
A: Mixed signals, not a good trade setup. Skip or wait for confirmation.

Q: "Market is closed - data is historical"
A: This is normal after 3:30 PM. Data is from yesterday's close.


✨ NEXT STEPS
════════════════════════════════════════════════════════════════════════════

1. Test APIs locally ✓ (Start here)
2. Connect frontend components
3. Add real-time updates with WebSocket
4. Set up alerts/notifications
5. Track signal performance (backtesting)
6. Deploy to production
7. Monitor in live market
8. Continuously improve confidence scoring


📚 DOCUMENTATION FILES
════════════════════════════════════════════════════════════════════════════

1. AI_DATA_INTEGRATION_COMPLETE.py → Full system documentation
2. trading/data_integration.py → Data fetching logic
3. trading/technical_indicators.py → Indicator calculations
4. trading/prediction_engine.py → ML prediction models
5. trading/signal_generation.py → Signal generation pipeline
6. trading/ai_signals_views.py → API endpoints


🎉 YOU'RE READY!
════════════════════════════════════════════════════════════════════════════

Start testing:
  $ python manage.py runserver 0.0.0.0:8001
  
Then in another terminal:
  $ curl http://localhost:8001/api/ai/market-status/

Connect frontend components to /api/ai/* endpoints

Happy trading! 📈
"""

print(QUICK_START)

# Save to file
with open('/tmp/AI_QUICK_START.txt', 'w') as f:
    f.write(QUICK_START)

print("\n✓ Quick start guide saved to: /tmp/AI_QUICK_START.txt")
