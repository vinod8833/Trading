export const marketStatus = {
  isMarketOpen: () => {
    const now = new Date();
    const istTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    const hours = istTime.getHours();
    const minutes = istTime.getMinutes();
    const day = istTime.getDay();

    const isWeekday = day >= 1 && day <= 5;
    const isWithinHours = (hours === 9 && minutes >= 15) || (hours > 9 && hours < 15) || (hours === 15 && minutes <= 30);

    return isWeekday && isWithinHours;
  },

  getMarketStatus: () => {
    const now = new Date();
    const istTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    const hours = istTime.getHours();
    const minutes = istTime.getMinutes();
    const day = istTime.getDay();

    const isWeekday = day >= 1 && day <= 5;

    if (!isWeekday) {
      return { status: 'CLOSED', label: 'Market Closed (Weekend)', color: 'bg-gray-100' };
    }

    if (hours < 9 || (hours === 9 && minutes < 15)) {
      return { status: 'PRE_MARKET', label: 'Pre-Market (Before 9:15 AM)', color: 'bg-blue-100' };
    }

    if (hours === 9 && minutes >= 15) {
      return { status: 'OPENING', label: 'Opening Session (9:15-12:00)', color: 'bg-orange-100' };
    }

    if (hours >= 10 && hours < 12) {
      return { status: 'OPENING', label: 'Opening Session (9:15-12:00)', color: 'bg-orange-100' };
    }

    if (hours >= 12 && hours < 15) {
      return { status: 'MID_DAY', label: 'Mid-Day Session (12:00-3:30 PM)', color: 'bg-blue-100' };
    }

    if ((hours === 15 && minutes <= 30) || (hours === 15 && minutes < 60)) {
      return { status: 'CLOSING', label: 'Closing Session (3:00-3:30 PM)', color: 'bg-red-100' };
    }

    return { status: 'CLOSED', label: 'Market Closed', color: 'bg-gray-100' };
  },

  getTimeUntilMarketOpen: () => {
    const now = new Date();
    const istTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    const nextOpen = new Date(istTime);

    const hours = istTime.getHours();
    const minutes = istTime.getMinutes();
    const day = istTime.getDay();

    if (day === 5 && hours >= 15 && minutes > 30) {
      nextOpen.setDate(nextOpen.getDate() + 3);
      nextOpen.setHours(9, 15, 0);
    } else if (day === 6) {
      nextOpen.setDate(nextOpen.getDate() + 2);
      nextOpen.setHours(9, 15, 0);
    } else if (day === 0) {
      nextOpen.setDate(nextOpen.getDate() + 1);
      nextOpen.setHours(9, 15, 0);
    } else {
      if (hours < 9 || (hours === 9 && minutes < 15)) {
        nextOpen.setHours(9, 15, 0);
      } else if (hours > 15 || (hours === 15 && minutes > 30)) {
        nextOpen.setDate(nextOpen.getDate() + 1);
        nextOpen.setHours(9, 15, 0);
      }
    }

    const diff = nextOpen - istTime;
    const hoursUntil = Math.floor(diff / (1000 * 60 * 60));
    const minutesUntil = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    return { hoursUntil, minutesUntil };
  }
};


export const predictionControl = {
  canShowLivePredictions: (marketOpen = true, userIntent = true) => {
    return marketOpen && userIntent;
  },

  getPredictionMode: (marketOpen) => {
    if (!marketOpen) {
      return {
        mode: 'ANALYSIS_ONLY',
        label: 'Analysis Mode (Market Closed)',
        showLive: false,
        showHistorical: true,
        showCalculated: true,
        riskLevel: 'LOW', 
        description: 'Market is closed. Showing calculated analysis and historical data only.'
      };
    }

    return {
      mode: 'LIVE_ANALYSIS',
      label: 'Live Analysis Mode (Market Open)',
      showLive: true,
      showHistorical: true,
      showCalculated: true,
      riskLevel: 'MEDIUM',
      description: 'Market is open. Live predictions enabled with real-time data.'
    };
  }
};

export const riskManagement = {
  calculatePositionSize: (capital, entryPrice, stopLoss) => {
    if (!capital || !entryPrice || !stopLoss) return 0;

    const maxRisk = capital * 0.01; 
    const riskPerShare = Math.abs(entryPrice - stopLoss);

    if (riskPerShare === 0) return 0;

    return Math.floor(maxRisk / riskPerShare);
  },


  calculatePnL: (capital, entryPrice, targets, stopLoss, quantity = null) => {
    if (!capital || !entryPrice || !stopLoss) return null;

    const maxRisk = capital * 0.01;
    const position = quantity || this.calculatePositionSize(capital, entryPrice, stopLoss);

    const riskAmount = Math.abs(position * (entryPrice - stopLoss));
    const riskPercent = (riskAmount / capital) * 100;

    if (riskAmount > maxRisk * 1.1) {
      return {
        valid: false,
        error: 'RISK_TOO_HIGH',
        message: `Position size would risk ₹${riskAmount.toFixed(0)} (${riskPercent.toFixed(2)}%) - Max allowed: ₹${maxRisk.toFixed(0)} (1%)`
      };
    }

    const scenarios = [];

    scenarios.push({
      name: 'Worst Case (Stop Loss)',
      price: stopLoss,
      quantity: position,
      totalValue: position * stopLoss,
      pnl: position * (stopLoss - entryPrice),
      pnlPercent: ((stopLoss - entryPrice) / entryPrice) * 100,
      type: 'loss'
    });

    if (Array.isArray(targets)) {
      targets.forEach((target, idx) => {
        if (target && target > entryPrice) {
          const profitAmount = position * (target - entryPrice);
          scenarios.push({
            name: `Target ${idx + 1}`,
            price: target,
            quantity: position,
            totalValue: position * target,
            pnl: profitAmount,
            pnlPercent: ((target - entryPrice) / entryPrice) * 100,
            type: 'profit'
          });
        }
      });
    }

    return {
      valid: true,
      capital,
      position,
      entryPrice,
      stopLoss,
      maxRisk,
      riskAmount,
      riskPercent,
      scenarios
    };
  },

  calculateRiskReward: (entryPrice, target, stopLoss) => {
    if (!entryPrice || !target || !stopLoss) return 0;

    const risk = Math.abs(entryPrice - stopLoss);
    const reward = Math.abs(target - entryPrice);

    if (risk === 0) return 0;

    return (reward / risk).toFixed(2);
  },

  estimateWinProbability: (rsi, volumeTrend, trend) => {
    let probability = 50; 


    if (rsi < 30) probability += 15; 
    else if (rsi > 70) probability -= 15; 

    if (trend === 'UPTREND') probability += 10;
    else if (trend === 'DOWNTREND') probability -= 10;

    if (volumeTrend === 'INCREASING') probability += 8;
    else if (volumeTrend === 'DECREASING') probability -= 8;

    return Math.min(Math.max(probability, 20), 80); 
  },

 
  assessRisk: (capital, entryPrice, stopLoss, targets) => {
    const riskPercent = Math.abs((entryPrice - stopLoss) / entryPrice) * 100;

    const warnings = [];
    const recommendations = [];

    if (riskPercent > 5) {
      warnings.push('⚠️ HIGH RISK: Stop loss is more than 5% away from entry');
      recommendations.push('Consider tightening stop loss or reducing position size');
    }

    if (riskPercent < 0.5) {
      warnings.push('⚠️ TIGHT STOP: Stop loss is too close (< 0.5%)');
      recommendations.push('May get stopped out too easily - consider widening');
    }

    if (targets && targets[0]) {
      const rr = this.calculateRiskReward(entryPrice, targets[0], stopLoss);
      if (rr < 1) {
        warnings.push(`⚠️ LOW REWARD: Risk/Reward ratio is ${rr}:1 (Target should be higher)`);
        recommendations.push('Adjust target price higher for better risk/reward');
      }
    }

    return { warnings, recommendations };
  }
};


export const chartAnalysis = {
  detectTrend: (prices) => {
    if (!prices || prices.length < 2) return 'NEUTRAL';

    const sma20 = this.calculateSMA(prices, 20);
    const sma50 = this.calculateSMA(prices, 50);

    if (sma20 > sma50) return 'UPTREND';
    if (sma20 < sma50) return 'DOWNTREND';
    return 'NEUTRAL';
  },

  calculateSMA: (prices, period) => {
    if (prices.length < period) return prices[prices.length - 1];
    const sum = prices.slice(-period).reduce((a, b) => a + b, 0);
    return sum / period;
  },

  detectSupport: (prices) => {
    if (!prices || prices.length < 2) return prices[prices.length - 1];
    return Math.min(...prices.slice(-20));
  },

  detectResistance: (prices) => {
    if (!prices || prices.length < 2) return prices[prices.length - 1];
    return Math.max(...prices.slice(-20));
  }
};


export const timeBasedGuidance = {
  getTradeHoldTime: (tradingStyle) => {
    const times = {
      INTRADAY: { min: '15 minutes', max: '1 trading day', bestWindow: '9:15 AM - 2:30 PM' },
      SWING: { min: '2 days', max: '5 days', bestWindow: 'Any time' },
      POSITIONAL: { min: '1 week', max: '4 weeks', bestWindow: 'Any time' },
      INVESTMENT: { min: '1 month', max: '1+ years', bestWindow: 'Any time' }
    };

    return times[tradingStyle] || times.SWING;
  },

  getStopPlacementTime: (tradingStyle) => {
    const times = {
      INTRADAY: '2-5 minutes after entry',
      SWING: 'Within 30 minutes',
      POSITIONAL: 'Within 1 hour',
      INVESTMENT: 'Within 1 day'
    };

    return times[tradingStyle] || times.SWING;
  }
};


export const formatters = {
  formatCurrency: (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(value);
  },

  formatPercent: (value, decimals = 2) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
  },

  formatPrice: (price, decimals = 2) => {
    return `₹${price.toFixed(decimals)}`;
  }
};

export const validators = {
  isValidSymbol: (symbol) => {
    return /^[A-Z]{1,5}$/.test(symbol);
  },

  isValidPrice: (price) => {
    return price > 0 && price < 1000000;
  },

  isValidCapital: (capital) => {
    return capital >= 1000 && capital <= 10000000;
  }
};

const tradingEngineUtils = {
  marketStatus,
  predictionControl,
  riskManagement,
  chartAnalysis,
  timeBasedGuidance,
  formatters,
  validators
};

export default tradingEngineUtils;
