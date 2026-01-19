
from decimal import Decimal
import math
from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta


class TrendFormulas:
    """Trend following formulas"""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int = 20) -> float:
        """Simple Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int = 12) -> float:
        """Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[-period:]) / period
        
        for price in prices[-period+1:]:
            ema = price * multiplier + ema * (1 - multiplier)
        
        return ema
    
    @staticmethod
    def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
        """Volume Weighted Average Price"""
        if not prices or not volumes or len(prices) != len(volumes):
            return prices[-1] if prices else 0
        
        tp = [p for p in prices]
        pv = [tp[i] * volumes[i] for i in range(len(tp))]
        
        return sum(pv) / sum(volumes) if sum(volumes) > 0 else prices[-1]
    
    @staticmethod
    def get_trend(current_price: float, sma20: float, sma50: float, 
                  ema12: float, ema26: float) -> str:
        """Determine trend direction"""
        bullish_signals = sum([
            current_price > sma20,
            sma20 > sma50,
            ema12 > ema26,
            current_price > ema12
        ])
        
        if bullish_signals >= 3:
            return "STRONG_UPTREND"
        elif bullish_signals == 2:
            return "UPTREND"
        elif bullish_signals == 1:
            return "WEAK_UPTREND"
        elif bullish_signals == 0 and current_price > sma50:
            return "NEUTRAL"
        else:
            return "DOWNTREND"


class MomentumFormulas:
    """Momentum indicators"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Relative Strength Index (0-100)"""
        if len(prices) < period + 1:
            return 50
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [abs(d) if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Tuple[float, float, float]:
        """MACD (12, 26, 9)
        Returns: (MACD, Signal, Histogram)
        """
        ema12 = TrendFormulas.calculate_ema(prices, 12)
        ema26 = TrendFormulas.calculate_ema(prices, 26)
        macd = ema12 - ema26

        signal = macd * 0.7 + (prices[-1] - prices[0]) * 0.3 if len(prices) > 1 else macd
        
        histogram = macd - signal
        return macd, signal, histogram
    
    @staticmethod
    def calculate_roc(prices: List[float], period: int = 12) -> float:
        """Rate of Change (%)"""
        if len(prices) < period + 1:
            return 0
        
        change = prices[-1] - prices[-(period + 1)]
        return (change / prices[-(period + 1)] * 100) if prices[-(period + 1)] > 0 else 0


class VolatilityFormulas:
    """Volatility indicators"""
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, 
                                  std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Bollinger Bands
        Returns: (Upper Band, Middle Band, Lower Band)
        """
        if len(prices) < period:
            mid = prices[-1]
            return mid + mid * 0.1, mid, mid - mid * 0.1
        
        sma = TrendFormulas.calculate_sma(prices, period)
        variance = sum([(p - sma) ** 2 for p in prices[-period:]]) / period
        std = math.sqrt(variance)
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return upper, sma, lower
    
    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], 
                     closes: List[float], period: int = 14) -> float:
        """Average True Range"""
        if len(closes) < 2:
            return 0
        
        true_ranges = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            true_ranges.append(tr)
        
        if len(true_ranges) < period:
            return sum(true_ranges) / len(true_ranges) if true_ranges else 0
        
        return sum(true_ranges[-period:]) / period


class VolumeFormulas:
    """Volume-based indicators"""
    
    @staticmethod
    def calculate_obv(prices: List[float], volumes: List[float]) -> float:
        """On-Balance Volume (cumulative)"""
        if len(prices) < 2 or len(volumes) < 2:
            return volumes[-1] if volumes else 0
        
        obv = 0
        for i in range(len(prices)):
            if i == 0:
                obv = volumes[i]
            elif prices[i] > prices[i-1]:
                obv += volumes[i]
            elif prices[i] < prices[i-1]:
                obv -= volumes[i]
        
        return obv
    
    @staticmethod
    def calculate_volume_oscillator(volumes: List[float], 
                                    short_period: int = 12,
                                    long_period: int = 26) -> float:
        """Volume Oscillator (%)
        (Short EMA - Long EMA) / Long EMA * 100
        """
        if len(volumes) < long_period:
            return 0
        
        short_avg = sum(volumes[-short_period:]) / short_period if len(volumes) >= short_period else 0
        long_avg = sum(volumes[-long_period:]) / long_period
        
        if long_avg == 0:
            return 0
        
        return (short_avg - long_avg) / long_avg * 100


class FundamentalFormulas:
    """Fundamental analysis formulas"""
    
    @staticmethod
    def calculate_pe_ratio(stock_price: float, eps: float) -> float:
        """Price-to-Earnings Ratio"""
        return stock_price / eps if eps > 0 else 0
    
    @staticmethod
    def calculate_pb_ratio(market_cap: float, book_value: float) -> float:
        """Price-to-Book Ratio"""
        return market_cap / book_value if book_value > 0 else 0
    
    @staticmethod
    def calculate_roe(net_income: float, equity: float) -> float:
        """Return on Equity (%)"""
        return (net_income / equity * 100) if equity > 0 else 0
    
    @staticmethod
    def calculate_debt_equity(total_debt: float, total_equity: float) -> float:
        """Debt-to-Equity Ratio"""
        return total_debt / total_equity if total_equity > 0 else 0
    
    @staticmethod
    def calculate_peg_ratio(pe_ratio: float, growth_rate: float) -> float:
        """Price/Earnings to Growth Ratio"""
        return pe_ratio / growth_rate if growth_rate > 0 else 0


class AIMetrics:
    """AI and quantitative metrics"""
    
    @staticmethod
    def calculate_log_returns(prices: List[float]) -> List[float]:
        """Log returns for each period"""
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                log_ret = math.log(prices[i] / prices[i-1])
                returns.append(log_ret)
        
        return returns
    
    @staticmethod
    def calculate_sharpe_ratio(prices: List[float], risk_free_rate: float = 0.05,
                               periods_per_year: int = 252) -> float:
        """Sharpe Ratio (risk-adjusted returns)"""
        returns = AIMetrics.calculate_log_returns(prices)
        
        if len(returns) < 2:
            return 0
        
        mean_return = sum(returns) / len(returns)
        std_dev = math.sqrt(sum([(r - mean_return) ** 2 for r in returns]) / len(returns))
        
        if std_dev == 0:
            return 0
        
        annual_return = mean_return * periods_per_year
        annual_std = std_dev * math.sqrt(periods_per_year)
        
        return (annual_return - risk_free_rate) / annual_std if annual_std > 0 else 0
    
    @staticmethod
    def calculate_sortino_ratio(prices: List[float], target_return: float = 0.0,
                                periods_per_year: int = 252) -> float:
        """Sortino Ratio (downside risk-adjusted)"""
        returns = AIMetrics.calculate_log_returns(prices)
        
        if len(returns) < 2:
            return 0
        
        mean_return = sum(returns) / len(returns)
        downside_returns = [r for r in returns if r < target_return]
        
        if not downside_returns:
            return mean_return * periods_per_year
        
        downside_std = math.sqrt(sum([(r - target_return) ** 2 for r in downside_returns]) / len(returns))
        
        if downside_std == 0:
            return 0
        
        return (mean_return * periods_per_year - target_return) / downside_std
    
    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> float:
        """Maximum Drawdown (%)"""
        if len(prices) < 2:
            return 0
        
        peak = prices[0]
        max_drawdown = 0
        
        for price in prices:
            if price > peak:
                peak = price
            
            drawdown = (peak - price) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown


class RiskFormulas:
    """Risk management formulas"""
    
    @staticmethod
    def calculate_position_size(capital: float, risk_percent: float, 
                                entry_price: float, stop_loss_price: float) -> int:
        """Calculate position size based on risk
        
        Position Size = (Capital × Risk%) / (Entry - Stop Loss)
        """
        if entry_price <= stop_loss_price or capital <= 0 or risk_percent <= 0:
            return 0
        
        risk_amount = capital * (risk_percent / 100)
        price_difference = abs(entry_price - stop_loss_price)
        
        position_size = int(risk_amount / price_difference)
        return max(1, position_size)
    
    @staticmethod
    def calculate_risk_reward_ratio(entry_price: float, stop_loss: float,
                                    target_price: float) -> float:
        """Risk-Reward Ratio"""
        risk = abs(entry_price - stop_loss)
        reward = abs(target_price - entry_price)
        
        if risk == 0:
            return 0
        
        return reward / risk
    
    @staticmethod
    def calculate_kelly_criterion(win_rate: float, avg_win: float, 
                                  avg_loss: float) -> float:
        """Kelly Criterion (optimal bet size)
        f* = (bp - q) / b
        where: b = odds, p = win rate, q = loss rate
        """
        if avg_loss == 0:
            return 0
        
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - win_rate
        
        f = (b * p - q) / b
        return max(0, min(f, 0.25))  
    
    @staticmethod
    def calculate_stop_loss_atr(entry_price: float, atr: float, 
                                multiplier: float = 2.0, 
                                direction: str = "SELL") -> float:
        """Calculate stop loss using ATR"""
        if direction == "BUY":
            return entry_price - (atr * multiplier)
        else: 
            return entry_price + (atr * multiplier)
    
    @staticmethod
    def calculate_target_rr(entry_price: float, stop_loss: float,
                            risk_reward_ratio: float = 2.0,
                            direction: str = "BUY") -> float:
        """Calculate target price based on Risk-Reward ratio"""
        risk = abs(entry_price - stop_loss)
        target_distance = risk * risk_reward_ratio
        
        if direction == "BUY":
            return entry_price + target_distance
        else:  
            return entry_price - target_distance


class FormulaScoreCalculator:
    """Calculate composite scores from formulas"""
    
    @staticmethod
    def calculate_trend_score(trend: str, current_price: float,
                             sma20: float, sma50: float,
                             ema12: float, ema26: float) -> float:
        """Trend score (0-100)"""
        score = 50  
        
        if trend == "STRONG_UPTREND":
            score = 85
        elif trend == "UPTREND":
            score = 70
        elif trend == "WEAK_UPTREND":
            score = 60
        elif trend == "NEUTRAL":
            score = 50
        else:
            score = 30
        
        distance_from_sma = (current_price - sma20) / sma20 * 100
        if distance_from_sma > 2: 
            score = min(score + 5, 100)
        elif distance_from_sma < -2:  
            score = max(score - 5, 0)
        
        return score
    
    @staticmethod
    def calculate_momentum_score(rsi: float, macd: float, signal: float, 
                                roc: float) -> float:
        """Momentum score (0-100)"""
        score = 50
        
        if rsi > 60:
            score += (rsi - 60) / 40 * 15
        elif rsi < 40:
            score -= (40 - rsi) / 40 * 15
        
        if macd > signal:
            score += 10
        else:
            score -= 10
        
        if roc > 0:
            score += min(roc / 5, 10)
        else:
            score -= min(abs(roc) / 5, 10)
        
        return max(0, min(score, 100))
    
    @staticmethod
    def calculate_volatility_score(upper_bb: float, lower_bb: float,
                                  current_price: float, atr: float,
                                  historical_atr: float) -> float:
        """Volatility score (0-100, higher = more volatile)"""
        bb_width = upper_bb - lower_bb
        midpoint = (upper_bb + lower_bb) / 2
        
        if bb_width == 0:
            bb_position = 50
        else:
            bb_position = (current_price - lower_bb) / bb_width * 100
        
        if historical_atr > 0:
            atr_expansion = min((atr / historical_atr - 1) * 100, 50)
        else:
            atr_expansion = 0
        
        return bb_position * 0.6 + atr_expansion * 0.4
    
    @staticmethod
    def calculate_volume_strength(obv: float, volume_oscillator: float,
                                 current_volume: float,
                                 average_volume: float) -> float:
        """Volume strength score (0-100)"""
        score = 50
        
        if obv > 0:
            score += 15
        
        if volume_oscillator > 5:
            score += 20
        elif volume_oscillator < -5:
            score -= 20
        
        if current_volume > average_volume * 1.5:
            score += 15
        elif current_volume < average_volume * 0.7:
            score -= 10
        
        return max(0, min(score, 100))


class FormulaMeta:
    """Metadata about each formula for AI explanation"""
    
    FORMULA_INFO = {
        "SMA": {
            "name": "Simple Moving Average",
            "category": "Trend",
            "description": "Average price over N periods",
            "best_for": ["SWING", "LONG_TERM"],
            "parameters": {"period": [20, 50, 200]},
            "signal_lag": "Medium",
            "best_market": ["TRENDING"]
        },
        "EMA": {
            "name": "Exponential Moving Average",
            "category": "Trend",
            "description": "Weighted average giving more weight to recent prices",
            "best_for": ["INTRADAY", "SWING", "AI_ALGO"],
            "parameters": {"period": [12, 26, 50]},
            "signal_lag": "Low",
            "best_market": ["TRENDING", "BREAKOUT"]
        },
        "VWAP": {
            "name": "Volume Weighted Average Price",
            "category": "Trend",
            "description": "Average price weighted by trading volume",
            "best_for": ["INTRADAY"],
            "parameters": {},
            "signal_lag": "Very Low",
            "best_market": ["INTRADAY"]
        },
        "RSI": {
            "name": "Relative Strength Index",
            "category": "Momentum",
            "description": "Overbought/Oversold indicator (0-100)",
            "best_for": ["INTRADAY", "SWING", "OPTIONS"],
            "parameters": {"period": 14},
            "signal_lag": "Low",
            "best_market": ["RANGE", "OSCILLATING"]
        },
        "MACD": {
            "name": "Moving Average Convergence Divergence",
            "category": "Momentum",
            "description": "Trend-following momentum indicator",
            "best_for": ["SWING", "LONG_TERM"],
            "parameters": {"fast": 12, "slow": 26, "signal": 9},
            "signal_lag": "Medium",
            "best_market": ["TRENDING"]
        },
        "ROC": {
            "name": "Rate of Change",
            "category": "Momentum",
            "description": "Percentage price change over period",
            "best_for": ["INTRADAY", "SWING"],
            "parameters": {"period": 12},
            "signal_lag": "Very Low",
            "best_market": ["ALL"]
        },
        "BOLLINGER_BANDS": {
            "name": "Bollinger Bands",
            "category": "Volatility",
            "description": "Price volatility and support/resistance levels",
            "best_for": ["SWING", "OPTIONS"],
            "parameters": {"period": 20, "std_dev": 2.0},
            "signal_lag": "Medium",
            "best_market": ["RANGE"]
        },
        "ATR": {
            "name": "Average True Range",
            "category": "Volatility",
            "description": "Market volatility measurement",
            "best_for": ["INTRADAY", "SWING", "ALL"],
            "parameters": {"period": 14},
            "signal_lag": "Medium",
            "best_market": ["ALL"]
        },
        "OBV": {
            "name": "On-Balance Volume",
            "category": "Volume",
            "description": "Cumulative volume tracking",
            "best_for": ["SWING", "LONG_TERM"],
            "parameters": {},
            "signal_lag": "Medium",
            "best_market": ["TRENDING"]
        },
        "P/E": {
            "name": "Price-to-Earnings Ratio",
            "category": "Fundamental",
            "description": "Stock valuation relative to earnings",
            "best_for": ["LONG_TERM"],
            "parameters": {},
            "signal_lag": "Very High",
            "best_market": ["FUNDAMENTAL"]
        },
        "ROE": {
            "name": "Return on Equity",
            "category": "Fundamental",
            "description": "Profitability relative to shareholder equity",
            "best_for": ["LONG_TERM"],
            "parameters": {},
            "signal_lag": "Very High",
            "best_market": ["FUNDAMENTAL"]
        },
        "SHARPE": {
            "name": "Sharpe Ratio",
            "category": "AI Metric",
            "description": "Risk-adjusted return",
            "best_for": ["AI_ALGO"],
            "parameters": {"periods": 252},
            "signal_lag": "High",
            "best_market": ["ALL"]
        },
        "POSITION_SIZE": {
            "name": "Position Sizing",
            "category": "Risk",
            "description": "Optimal position size based on risk",
            "best_for": ["ALL"],
            "parameters": {"max_risk": 0.02},
            "signal_lag": "None",
            "best_market": ["ALL"]
        }
    }
