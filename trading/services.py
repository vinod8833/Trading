"""
Business Logic Services for KVK Trading System
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Optional
import math
from .models import (
    Stock, StockAnalysis, TradeRecommendation, Portfolio,
    RiskAssessment, AlternativeInvestment, TradeOrder
)
from django.conf import settings
from .stock_universe import StockUniverseManager


class TechnicalAnalysisService:
    """Technical Analysis Calculations"""
    
    @staticmethod
    def calculate_bollinger_bands(data: List[float], period: int = 20) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands (upper, middle, lower)"""
        if len(data) < period:
            return None, None, None
        
        recent = data[-period:]
        middle = sum(recent) / period
        variance = sum((x - middle) ** 2 for x in recent) / period
        std_dev = math.sqrt(variance)
        
        return middle + (2 * std_dev), middle, middle - (2 * std_dev)
    
    @staticmethod
    def calculate_rsi(data: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(data) < period + 1:
            return 50.0
        
        deltas = [data[i] - data[i-1] for i in range(1, len(data))]
        seed = deltas[:period]
        up = sum(x for x in seed if x > 0) / period
        down = -sum(x for x in seed if x < 0) / period
        
        rs = up / down if down != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_moving_average(data: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(data) < period:
            return None
        return sum(data[-period:]) / period
    
    @staticmethod
    def calculate_fibonacci_levels(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci Retracement Levels"""
        diff = high - low
        return {
            '0': high,
            '0.236': high - (diff * 0.236),
            '0.382': high - (diff * 0.382),
            '0.5': high - (diff * 0.5),
            '0.618': high - (diff * 0.618),
            '1': low
        }
    
    @staticmethod
    def calculate_vwap(prices: List[float], volumes: List[int]) -> float:
        """Calculate Volume Weighted Average Price"""
        if not prices or not volumes:
            return None
        
        cumulative_pv = sum(p * v for p, v in zip(prices, volumes))
        cumulative_volume = sum(volumes)
        return cumulative_pv / cumulative_volume if cumulative_volume > 0 else prices[-1]


class RiskManagementService:
    """Risk Management Calculations - Strict 0.5% max risk per trade"""
    
    # Strict intraday risk limits
    MAX_RISK_INTRADAY = 0.5  # 0.5% per trade
    MAX_LOSS_PER_DAY = 2.0   # 2% max daily loss
    MAX_POSITIONS = 3        # Max 3 concurrent positions
    
    @staticmethod
    def calculate_quantity(
        capital: Decimal,
        entry_price: Decimal,
        stop_loss: Decimal,
        max_risk_percent: float = 0.5,
        trading_style: str = 'INTRADAY'
    ) -> int:
        """
        Calculate quantity with strict risk management
        For INTRADAY: max 0.5% risk per trade
        For SWING: max 1% risk per trade
        For POSITIONAL: max 1.5% risk per trade
        """
        
        # Set max risk based on trading style
        if trading_style == 'INTRADAY':
            max_risk_percent = 0.5  # Non-negotiable for intraday
        elif trading_style == 'SWING':
            max_risk_percent = min(1.0, max_risk_percent)
        elif trading_style == 'POSITIONAL':
            max_risk_percent = min(1.5, max_risk_percent)
        
        max_risk_amount = capital * Decimal(str(max_risk_percent / 100))
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        quantity = int(max_risk_amount / price_risk)
        return max(1, quantity)
    
    @staticmethod
    def calculate_position_size(
        portfolio_capital: Decimal,
        max_risk_per_trade: float = 0.5,
        trading_style: str = 'INTRADAY'
    ) -> Decimal:
        """Calculate maximum position size based on trading style"""
        
        if trading_style == 'INTRADAY':
            max_risk_per_trade = 0.5
        elif trading_style == 'SWING':
            max_risk_per_trade = min(1.0, max_risk_per_trade)
        
        return portfolio_capital * Decimal(str(max_risk_per_trade / 100))
    
    @staticmethod
    def validate_intraday_trade(
        capital: Decimal,
        entry_price: Decimal,
        stop_loss: Decimal,
        quantity: int,
        existing_daily_loss: Decimal = Decimal('0')
    ) -> Dict:
        """
        Validate intraday trade against strict risk rules
        Returns: {'valid': bool, 'errors': [], 'warnings': []}
        """
        
        validation = {'valid': True, 'errors': [], 'warnings': []}
        
        # Calculate risk
        risk_amount = quantity * abs(entry_price - stop_loss)
        risk_percent = (risk_amount / float(capital)) * 100 if capital > 0 else 0
        
        # Check 1: Max 0.5% risk per trade
        if risk_percent > 0.5:
            validation['errors'].append(
                f'❌ Risk per trade ({risk_percent:.2f}%) exceeds 0.5% limit. '
                f'Reduce position size to {int(quantity * 0.5 / (risk_percent / 0.5))} units.'
            )
        
        # Check 2: Max 2% daily loss (including this trade)
        projected_daily_loss = existing_daily_loss + risk_amount
        daily_loss_percent = (projected_daily_loss / float(capital)) * 100 if capital > 0 else 0
        
        if daily_loss_percent > 2.0:
            validation['errors'].append(
                f'❌ Daily loss ({daily_loss_percent:.2f}%) would exceed 2% limit. '
                f'Maximum remaining risk today: ₹{float(capital * Decimal("0.02") - existing_daily_loss):.0f}'
            )
        
        # Check 3: Warn if risk-reward < 1:1.5
        if entry_price != stop_loss:
            risk = abs(entry_price - stop_loss)
            reward = risk * Decimal('1.5')  # Minimum 1:1.5 ratio required
            
            if reward < risk:
                validation['warnings'].append(
                    f'⚠️  Risk-Reward ratio is unfavorable. Consider increasing target prices.'
                )
        
        # Check 4: Warn on tight stops
        stop_percent = (abs(entry_price - stop_loss) / entry_price * 100)
        if stop_percent < 0.5:
            validation['warnings'].append(
                f'⚠️  Stop loss is very tight ({stop_percent:.2f}%). '
                f'May get stopped out by normal volatility.'
            )
        elif stop_percent > 2.5:
            validation['warnings'].append(
                f'⚠️  Stop loss is very wide ({stop_percent:.2f}%). '
                f'Consider tighter risk management.'
            )
        
        validation['valid'] = len(validation['errors']) == 0
        return validation
    
    @staticmethod
    def assess_risk_level(risk_percent: float) -> str:
        """Assess risk level based on percentage"""
        if risk_percent < 0.5:
            return 'VERY_LOW'
        elif risk_percent < 1.0:
            return 'LOW'
        elif risk_percent < 2.0:
            return 'MODERATE'
        elif risk_percent < 3.0:
            return 'HIGH'
        else:
            return 'VERY_HIGH'
    
    @staticmethod
    def calculate_risk_reward_ratio(
        entry_price: Decimal,
        stop_loss: Decimal,
        target_price: Decimal
    ) -> float:
        """Calculate risk-reward ratio"""
        risk = abs(entry_price - stop_loss)
        reward = abs(target_price - entry_price)
        
        if risk == 0:
            return 0
        
        return float(reward / risk)



class TradeRecommendationService:
    """Trade Recommendation Generation"""
    
    @staticmethod
    def generate_recommendation(
        stock: Stock,
        analysis: StockAnalysis,
        trading_style: str,
        capital: Decimal
    ) -> Dict:
        """Generate comprehensive trade recommendation"""
        
        # Determine signal based on trend
        signal = TradeRecommendationService._determine_signal(analysis)
        
        # Calculate entry and exit levels
        if signal == 'BUY':
            entry_price = Decimal(str(analysis.support_level))
            stop_loss = entry_price * Decimal('0.98')
        elif signal == 'SELL':
            entry_price = Decimal(str(analysis.resistance_level))
            stop_loss = entry_price * Decimal('1.02')
        else:
            return None
        
        # Calculate targets based on trading style
        targets = TradeRecommendationService._calculate_targets(
            entry_price, stop_loss, signal, trading_style
        )
        
        # Risk calculations
        quantity = RiskManagementService.calculate_quantity(
            capital, entry_price, stop_loss
        )
        
        risk_amount = quantity * float(abs(entry_price - stop_loss))
        risk_percent = (risk_amount / float(capital)) * 100 if capital > 0 else 0
        
        profit_percent = TradeRecommendationService._calculate_profit(
            entry_price, targets[0], quantity, capital
        )
        
        risk_reward = RiskManagementService.calculate_risk_reward_ratio(
            entry_price, stop_loss, targets[0]
        )
        
        # Confidence calculation
        confidence = TradeRecommendationService._calculate_confidence(analysis)
        
        return {
            'signal': signal,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'targets': targets,
            'quantity': quantity,
            'risk_percent': risk_percent,
            'profit_percent': profit_percent,
            'risk_reward_ratio': risk_reward,
            'confidence': confidence,
            'win_probability': TradeRecommendationService._calculate_win_probability(
                analysis, confidence
            )
        }
    
    @staticmethod
    def _determine_signal(analysis: StockAnalysis) -> str:
        """Determine BUY/SELL signal from analysis"""
        if analysis.trend in ['STRONG_BULLISH', 'BULLISH']:
            return 'BUY'
        elif analysis.trend in ['STRONG_BEARISH', 'BEARISH']:
            return 'SELL'
        else:
            return 'HOLD'
    
    @staticmethod
    def _calculate_targets(
        entry_price: Decimal,
        stop_loss: Decimal,
        signal: str,
        trading_style: str
    ) -> List[Decimal]:
        """Calculate profit targets based on style"""
        
        risk = abs(entry_price - stop_loss)
        multipliers = {
            'INTRADAY': [1.5, 2.5, 3.5, 4.5],
            'SWING': [2.0, 3.0, 4.0, 5.0],
            'POSITIONAL': [2.5, 4.0, 5.5, 7.0],
            'LONG_TERM': [3.0, 5.0, 7.0, 10.0]
        }
        
        multiplier_list = multipliers.get(trading_style, [2.0, 3.0, 4.0, 5.0])
        
        if signal == 'BUY':
            targets = [entry_price + (risk * Decimal(str(m))) for m in multiplier_list]
        else:
            targets = [entry_price - (risk * Decimal(str(m))) for m in multiplier_list]
        
        return targets
    
    @staticmethod
    def _calculate_profit(
        entry: Decimal,
        target: Decimal,
        quantity: int,
        capital: Decimal
    ) -> float:
        """Calculate profit percentage"""
        if quantity == 0 or capital == 0:
            return 0
        
        profit = (target - entry) * quantity
        return float((profit / capital) * 100)
    
    @staticmethod
    def _calculate_confidence(analysis: StockAnalysis) -> float:
        """Calculate confidence level"""
        confidence = float(analysis.trend_probability)
        
        # Adjust based on indicators
        if 30 < analysis.rsi < 70:
            confidence += 10
        elif analysis.rsi < 30 or analysis.rsi > 70:
            confidence -= 5
        
        if analysis.volume_trend == 'INCREASING':
            confidence += 5
        
        return min(100, max(0, confidence))
    
    @staticmethod
    def _calculate_win_probability(analysis: StockAnalysis, confidence: float) -> float:
        """Calculate win probability"""
        base_prob = confidence
        
        # Adjust based on volume
        if analysis.volume > analysis.average_volume_20 * 1.2:
            base_prob += 5
        
        # Adjust based on RSI extremes
        if analysis.rsi < 30:
            base_prob += 10
        elif analysis.rsi > 70:
            base_prob -= 10
        
        return min(100, max(0, base_prob))


class AlternativeInvestmentService:
    """Suggest Alternative Investments"""
    
    ALTERNATIVES = {
        'BUY': {
            'INTRADAY': [
                {
                    'name': 'Nifty 50 ETF',
                    'type': 'ETF',
                    'expected_return': 2.5,
                    'risk': 'LOW',
                    'liquidity': 'HIGH'
                },
                {
                    'name': 'Bank Nifty ETF',
                    'type': 'ETF',
                    'expected_return': 3.0,
                    'risk': 'MODERATE',
                    'liquidity': 'HIGH'
                }
            ],
            'SWING': [
                {
                    'name': 'HDFC Index Fund',
                    'type': 'MUTUAL_FUND',
                    'expected_return': 10.0,
                    'risk': 'LOW',
                    'liquidity': 'HIGH'
                },
                {
                    'name': 'Mid-Cap ETF',
                    'type': 'ETF',
                    'expected_return': 12.0,
                    'risk': 'MODERATE',
                    'liquidity': 'HIGH'
                }
            ]
        },
        'SELL': {
            'INTRADAY': [
                {
                    'name': 'Gold ETF',
                    'type': 'ETF',
                    'expected_return': 1.5,
                    'risk': 'LOW',
                    'liquidity': 'HIGH'
                }
            ]
        }
    }
    
    @staticmethod
    def get_alternatives(signal: str, trading_style: str) -> List[Dict]:
        """Get alternative investment suggestions"""
        return AlternativeInvestmentService.ALTERNATIVES.get(signal, {}).get(
            trading_style, []
        )


class MarketSessionService:
    """Market Session Management"""
    
    SESSIONS = {
        'pre_open': ('09:15', '09:15'),
        'opening': ('09:16', '10:30'),
        'mid_session': ('10:31', '14:30'),
        'closing': ('14:31', '15:30'),
        'post_close': ('15:31', '16:00')
    }
    
    @staticmethod
    def get_current_session(hour: int, minute: int) -> str:
        """Get current market session"""
        time_minutes = hour * 60 + minute
        
        if 9 * 60 + 15 <= time_minutes <= 9 * 60 + 15:
            return 'pre_open'
        elif 9 * 60 + 16 <= time_minutes <= 10 * 60 + 30:
            return 'opening'
        elif 10 * 60 + 31 <= time_minutes <= 14 * 60 + 30:
            return 'mid_session'
        elif 14 * 60 + 31 <= time_minutes <= 15 * 60 + 30:
            return 'closing'
        elif 15 * 60 + 31 <= time_minutes <= 16 * 60:
            return 'post_close'
        else:
            return 'market_closed'

class SignalGenerationService:
    """Generate trading signals with Beginner and Pro modes"""
    
    @staticmethod
    def generate_intraday_signal(
        stock: Stock,
        analysis: StockAnalysis,
        current_price: Decimal,
        live_data: Dict,
        capital: Decimal
    ) -> Dict:
        """
        Generate intraday-specific signal with VWAP, EMA, and volume analysis
        Includes tight risk management and auto square-off settings
        """
        
        # Get technical values
        ema_12 = float(analysis.ema_12) if analysis.ema_12 else float(current_price)
        ema_26 = float(analysis.ema_26) if analysis.ema_26 else float(current_price)
        vwap = float(analysis.vwap)
        rsi = float(analysis.rsi)
        volume = analysis.volume
        avg_volume_20 = analysis.average_volume_20
        
        # VWAP Signal (Primary for intraday)
        vwap_diff = float(current_price) - vwap
        vwap_percent = (vwap_diff / vwap) * 100
        vwap_signal = 1 if vwap_diff > 0 else -1
        
        # EMA Crossover Signal
        ema_diff = ema_12 - ema_26
        ema_signal = 1 if ema_12 > ema_26 else -1
        
        # Volume Signal
        volume_ratio = volume / avg_volume_20
        volume_signal = 1 if volume_ratio > 1.1 else (-1 if volume_ratio < 0.9 else 0)
        
        # RSI Signal (Intraday momentum)
        if rsi < 30:
            rsi_signal = 1  # Oversold - Buy opportunity
        elif rsi > 70:
            rsi_signal = -1  # Overbought - Sell opportunity
        else:
            rsi_signal = 0  # Neutral
        
        # Combined Signal Score
        signal_score = vwap_signal * 2 + ema_signal + volume_signal + rsi_signal
        
        # Determine BUY/SELL/HOLD
        if signal_score >= 2:
            signal = 'BUY'
            entry_price = current_price
            stop_loss = current_price * Decimal('0.99')  # Tight 1% stop for intraday
            target_mult = [1.003, 1.005, 1.008, 1.010]  # 0.3%, 0.5%, 0.8%, 1.0% targets
        elif signal_score <= -2:
            signal = 'SELL'
            entry_price = current_price
            stop_loss = current_price * Decimal('1.01')  # Tight 1% stop for intraday
            target_mult = [0.997, 0.995, 0.992, 0.990]  # 0.3%, 0.5%, 0.8%, 1.0% targets
        else:
            signal = 'HOLD'
            entry_price = current_price
            stop_loss = current_price
            target_mult = [1.0, 1.0, 1.0, 1.0]
        
        # Calculate targets
        targets = [Decimal(str(float(entry_price) * m)) for m in target_mult]
        
        # Position sizing with STRICT 0.5% risk per trade
        risk_per_trade = capital * Decimal('0.005')  # 0.5% MAXIMUM risk
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk > 0:
            quantity = int(risk_per_trade / price_risk)
        else:
            quantity = int(capital / entry_price * Decimal('0.01'))  # 1% of capital as backup
        
        quantity = max(1, quantity)
        
        # Validate trade against strict intraday rules
        validation = RiskManagementService.validate_intraday_trade(
            capital=capital,
            entry_price=entry_price,
            stop_loss=stop_loss,
            quantity=quantity
        )
        
        # Calculate metrics
        risk_amount = quantity * float(abs(entry_price - stop_loss))
        risk_percent = (risk_amount / float(capital)) * 100 if capital > 0 else 0
        
        profit_amount = quantity * float(targets[0] - entry_price)
        profit_percent = (profit_amount / float(capital)) * 100 if capital > 0 else 0
        
        risk_reward = float(abs(targets[0] - entry_price) / abs(entry_price - stop_loss)) if price_risk > 0 else 0
        
        # Confidence calculation
        confidence = 50
        if abs(vwap_percent) > 0.5:
            confidence += 15
        if volume_ratio > 1.2:
            confidence += 15
        if ema_signal == vwap_signal:
            confidence += 10
        if 30 < rsi < 70:
            confidence += 10
        
        confidence = min(100, max(0, confidence))
        
        # Win probability (for intraday, based on signal strength)
        win_prob = confidence * 0.8
        
        return {
            'signal': signal,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'targets': targets,
            'quantity': quantity,
            'risk_percent': risk_percent,
            'profit_percent': profit_percent,
            'risk_reward_ratio': risk_reward,
            'confidence': confidence,
            'win_probability': win_prob,
            'valid_until': 'End of Day',
            'auto_square_off': True,
            'validation': validation,
            'indicators': {
                'vwap': {
                    'value': vwap,
                    'price_vs_vwap': float(vwap_diff),
                    'signal': 'BULLISH' if vwap_signal > 0 else 'BEARISH'
                },
                'ema': {
                    'ema_12': ema_12,
                    'ema_26': ema_26,
                    'crossover': 'BULLISH' if ema_signal > 0 else 'BEARISH'
                },
                'rsi': {
                    'value': rsi,
                    'signal': 'OVERSOLD' if rsi < 30 else ('OVERBOUGHT' if rsi > 70 else 'NEUTRAL')
                },
                'volume': {
                    'current': volume,
                    'average': avg_volume_20,
                    'ratio': round(volume_ratio, 2),
                    'signal': 'STRONG' if volume_signal > 0 else ('WEAK' if volume_signal < 0 else 'NORMAL')
                }
            }
        }
    
    @staticmethod
    def generate_beginner_signal(analysis: StockAnalysis) -> Dict:
        """
        Generate simple Beginner Mode signal
        Only shows BUY/SELL/HOLD with simple explanation
        """
        signal_data = {
            'signal': 'HOLD',
            'confidence': 'NEUTRAL',
            'simple_explanation': '',
            'action': 'NO_ACTION'
        }
        
        if analysis.rsi < 30 and analysis.trend in ['BULLISH', 'STRONG_BULLISH']:
            signal_data['signal'] = 'BUY'
            signal_data['confidence'] = 'HIGH' if analysis.trend_probability > 70 else 'MEDIUM'
            signal_data['simple_explanation'] = (
                f"Price is oversold (RSI: {analysis.rsi:.0f}), trend is bullish. "
                f"Good time to buy. Set stop loss at support level ({analysis.support_level:.2f})."
            )
            signal_data['action'] = 'BUY_NOW'
        
        elif analysis.rsi > 70 and analysis.trend in ['BEARISH', 'STRONG_BEARISH']:
            signal_data['signal'] = 'SELL'
            signal_data['confidence'] = 'HIGH' if analysis.trend_probability > 70 else 'MEDIUM'
            signal_data['simple_explanation'] = (
                f"Price is overbought (RSI: {analysis.rsi:.0f}), trend is bearish. "
                f"Good time to sell or avoid. Set stop loss at resistance ({analysis.resistance_level:.2f})."
            )
            signal_data['action'] = 'SELL_NOW'
        
        elif analysis.trend in ['BULLISH', 'STRONG_BULLISH'] and analysis.volume_trend == 'INCREASING':
            signal_data['signal'] = 'BUY'
            signal_data['confidence'] = 'MEDIUM'
            signal_data['simple_explanation'] = (
                f"Price is in uptrend with increasing volume. "
                f"Buy above {analysis.support_level:.2f}, sell at {analysis.resistance_level:.2f}."
            )
            signal_data['action'] = 'BUY_ON_DIPS'
        
        else:
            signal_data['signal'] = 'HOLD'
            signal_data['confidence'] = 'NEUTRAL'
            signal_data['simple_explanation'] = (
                "Market is in neutral phase. Wait for clear direction. "
                "Don't trade in confusion."
            )
            signal_data['action'] = 'WAIT'
        
        return signal_data
    
    @staticmethod
    def generate_pro_signal(analysis: StockAnalysis, recommendation: 'TradeRecommendation' = None) -> Dict:
        """
        Generate detailed Pro Mode signal with all indicators
        Shows detailed analysis with multiple indicators
        """
        signal_data = {
            'signal': '',
            'confidence': 0,
            'indicators': {},
            'detailed_analysis': ''
        }
        
        # RSI Analysis
        rsi_signal = 'BEARISH' if analysis.rsi > 70 else ('BULLISH' if analysis.rsi < 30 else 'NEUTRAL')
        signal_data['indicators']['rsi'] = {
            'value': analysis.rsi,
            'signal': rsi_signal,
            'interpretation': f"RSI at {analysis.rsi:.2f} - {rsi_signal}"
        }
        
        # VWAP Analysis
        vwap_signal = 'BULLISH' if float(analysis.current_price) > float(analysis.vwap) else 'BEARISH'
        signal_data['indicators']['vwap'] = {
            'value': float(analysis.vwap),
            'signal': vwap_signal,
            'interpretation': f"Price {'above' if vwap_signal == 'BULLISH' else 'below'} VWAP ({analysis.vwap:.2f})"
        }
        
        # Bollinger Bands Analysis
        bb_position = 'OVERBOUGHT' if float(analysis.current_price) > float(analysis.bollinger_upper) else (
            'OVERSOLD' if float(analysis.current_price) < float(analysis.bollinger_lower) else 'NEUTRAL'
        )
        signal_data['indicators']['bollinger_bands'] = {
            'upper': float(analysis.bollinger_upper),
            'middle': float(analysis.bollinger_middle),
            'lower': float(analysis.bollinger_lower),
            'position': bb_position,
            'interpretation': f"Price is {bb_position} relative to Bollinger Bands"
        }
        
        # Volume Analysis
        signal_data['indicators']['volume'] = {
            'current': analysis.volume,
            'average_20': analysis.average_volume_20,
            'trend': analysis.volume_trend,
            'spike': 'YES' if analysis.volume > analysis.average_volume_20 * 1.5 else 'NO',
            'interpretation': f"Volume trend: {analysis.volume_trend}, Spike detected: {'YES' if analysis.volume > analysis.average_volume_20 * 1.5 else 'NO'}"
        }
        
        # Trend Analysis
        signal_data['indicators']['trend'] = {
            'trend': analysis.trend,
            'probability': analysis.trend_probability,
            'interpretation': f"{analysis.trend} ({analysis.trend_probability:.1f}% probability)"
        }
        
        # Fibonacci Levels
        signal_data['indicators']['fibonacci'] = {
            'levels': {
                '0.236': float(analysis.fib_0_236),
                '0.382': float(analysis.fib_0_382),
                '0.5': float(analysis.fib_0_500),
                '0.618': float(analysis.fib_0_618),
            }
        }
        
        # Moving Averages
        signal_data['indicators']['moving_averages'] = {
            'sma_20': float(analysis.sma_20) if analysis.sma_20 else None,
            'sma_50': float(analysis.sma_50) if analysis.sma_50 else None,
            'sma_200': float(analysis.sma_200) if analysis.sma_200 else None,
        }
        
        # Overall Signal Determination
        bullish_count = sum([
            rsi_signal == 'BULLISH',
            vwap_signal == 'BULLISH',
            analysis.trend in ['BULLISH', 'STRONG_BULLISH'],
            analysis.volume_trend == 'INCREASING'
        ])
        
        if bullish_count >= 3:
            signal_data['signal'] = 'STRONG_BUY'
            signal_data['confidence'] = 90
        elif bullish_count == 2:
            signal_data['signal'] = 'BUY'
            signal_data['confidence'] = 70
        elif bullish_count == 0:
            signal_data['signal'] = 'STRONG_SELL'
            signal_data['confidence'] = 90
        elif bullish_count == 1:
            signal_data['signal'] = 'SELL'
            signal_data['confidence'] = 70
        else:
            signal_data['signal'] = 'HOLD'
            signal_data['confidence'] = 50
        
        return signal_data


class RiskAnalyzerService:
    """Advanced risk analysis with automatic capital checks"""
    
    @staticmethod
    def analyze_risk(
        portfolio: 'Portfolio',
        stock: Stock,
        entry_price: Decimal,
        stop_loss: Decimal,
        quantity: int,
        capital_available: Decimal
    ) -> Dict:
        """
        Perform comprehensive risk analysis
        Warns if risk is too high based on available capital
        """
        capital_for_trade = entry_price * quantity
        risk_amount = abs(entry_price - stop_loss) * quantity
        risk_percent = (risk_amount / portfolio.total_capital) * 100 if portfolio.total_capital > 0 else 0
        
        # Check if capital is sufficient
        capital_check = {
            'available': float(capital_available),
            'required': float(capital_for_trade),
            'sufficient': capital_available >= capital_for_trade,
            'message': (
                f"Sufficient capital available" if capital_available >= capital_for_trade
                else f"⚠️ Insufficient capital! Need {capital_for_trade}, have {capital_available}"
            )
        }
        
        # Risk Level Assessment
        risk_level = RiskManagementService.assess_risk_level(risk_percent)
        
        # Warnings
        warnings = []
        if risk_percent > portfolio.max_risk_per_trade:
            warnings.append(f"⚠️ Risk exceeds max ({risk_percent:.2f}% > {portfolio.max_risk_per_trade}%)")
        if not capital_check['sufficient']:
            warnings.append("⚠️ Insufficient capital for this trade")
        if risk_level in ['HIGH', 'VERY_HIGH']:
            warnings.append(f"⚠️ Risk level is {risk_level} - Consider reducing position size")
        
        return {
            'risk_amount': float(risk_amount),
            'risk_percent': risk_percent,
            'risk_level': risk_level,
            'capital_check': capital_check,
            'warnings': warnings,
            'recommendation': (
                'PROCEED' if not warnings else ('CAUTION' if len(warnings) <= 1 else 'REJECT')
            )
        }


class MarketSummaryService:
    """Generate daily market summary with sentiment analysis"""
    
    @staticmethod
    def analyze_market_sentiment(gainers: int, losers: int) -> str:
        """Determine market sentiment"""
        total = gainers + losers
        if total == 0:
            return 'NEUTRAL'
        
        gainer_percent = (gainers / total) * 100
        
        if gainer_percent >= 70:
            return 'VERY_BULLISH'
        elif gainer_percent >= 55:
            return 'BULLISH'
        elif gainer_percent >= 45:
            return 'NEUTRAL'
        elif gainer_percent >= 30:
            return 'BEARISH'
        else:
            return 'VERY_BEARISH'
    
    @staticmethod
    def generate_summary(
        gainers_count: int,
        losers_count: int,
        sector_performance: Dict,
        volatility: float = None
    ) -> Dict:
        """Generate comprehensive market summary"""
        
        total_stocks = gainers_count + losers_count
        sentiment = MarketSummaryService.analyze_market_sentiment(gainers_count, losers_count)
        
        top_sectors = sorted(sector_performance.items(), key=lambda x: x[1], reverse=True)[:3]
        bottom_sectors = sorted(sector_performance.items(), key=lambda x: x[1])[:3]
        
        summary_text = f"""
        📊 Market Summary
        
        • Total Gainers: {gainers_count} ({(gainers_count/total_stocks*100):.1f}%)
        • Total Losers: {losers_count} ({(losers_count/total_stocks*100):.1f}%)
        • Market Sentiment: {sentiment}
        
        🔝 Top Performing Sectors: {', '.join([f"{s[0]} ({s[1]:+.2f}%)" for s in top_sectors])}
        🔻 Bottom Sectors: {', '.join([f"{s[0]} ({s[1]:+.2f}%)" for s in bottom_sectors])}
        """
        
        return {
            'gainers': gainers_count,
            'losers': losers_count,
            'sentiment': sentiment,
            'top_sectors': dict(top_sectors),
            'bottom_sectors': dict(bottom_sectors),
            'summary': summary_text.strip(),
            'volatility': volatility
        }


class TradingMistakeDetectorService:
    """Detect and report common trading mistakes"""
    
    MISTAKE_RULES = {
        'ENTRY_TIMING': {
            'condition': 'entry_rsi_extreme',
            'description': 'Entered at extreme RSI levels (>75 or <25) without confirmation',
            'lesson': 'Wait for confirmation from other indicators before entering at extremes'
        },
        'POSITION_SIZE': {
            'condition': 'oversized_position',
            'description': 'Position size too large for capital risk rules',
            'lesson': 'Always follow 0.5% max risk per trade rule'
        },
        'EXIT_TIMING': {
            'condition': 'no_stop_loss',
            'description': 'Traded without stop loss protection',
            'lesson': 'Always set stop loss BEFORE entering a trade'
        },
        'EMOTIONAL': {
            'condition': 'revenge_trading',
            'description': 'Took trade to recover previous loss (revenge trading)',
            'lesson': 'Take breaks after losses. Only trade planned setups.'
        }
    }
    
    @staticmethod
    def analyze_trade(
        entry_price: Decimal,
        exit_price: Decimal,
        stop_loss: Decimal,
        quantity: int,
        capital: Decimal,
        rsi_at_entry: float,
        holding_time: int,  # minutes
        is_loss: bool,
        previous_was_loss: bool
    ) -> List[Dict]:
        """Detect mistakes in completed trades"""
        
        mistakes = []
        
        # Check for position sizing error
        risk_amount = abs(entry_price - stop_loss) * quantity
        risk_percent = (risk_amount / capital) * 100
        if risk_percent > 1.0:
            mistakes.append({
                'category': 'POSITION_SIZE',
                'severity': 'HIGH' if risk_percent > 2.0 else 'MEDIUM',
                'description': f'Position size risk was {risk_percent:.2f}% (max 0.5%)',
                'lesson_learned': 'Reduce position size to comply with risk management rules',
                'prevention_tip': 'Use automatic position sizing calculator'
            })
        
        # Check for entry timing mistakes
        if rsi_at_entry > 75 or rsi_at_entry < 25:
            mistakes.append({
                'category': 'ENTRY_TIMING',
                'severity': 'MEDIUM',
                'description': f'Entered at extreme RSI ({rsi_at_entry:.0f}) without waiting for reversal',
                'lesson_learned': 'Wait for RSI to normalize before entering extreme moves',
                'prevention_tip': 'Use RSI divergence for better entries at extremes'
            })
        
        # Check for revenge trading
        if is_loss and previous_was_loss:
            mistakes.append({
                'category': 'EMOTIONAL',
                'severity': 'HIGH',
                'description': 'Took trade immediately after previous loss (revenge trading)',
                'lesson_learned': 'Take a break after losses. Emotional decisions lose money.',
                'prevention_tip': 'Set a 30-minute minimum break after each loss'
            })
        
        # Check for holding time issues
        if is_loss and holding_time < 5:  # Closed in less than 5 minutes
            mistakes.append({
                'category': 'DISCIPLINE',
                'severity': 'MEDIUM',
                'description': 'Closed trade too quickly due to small loss',
                'lesson_learned': 'Give trades time to work as per plan',
                'prevention_tip': 'Respect your planned holding period'
            })
        
        return mistakes


class AIExplainerService:
    """Provide transparent AI explanations for decisions"""
    
    @staticmethod
    def explain_signal(analysis: StockAnalysis, signal: str) -> Dict:
        """Explain why a signal was generated"""
        
        simple_explanation = ""
        detailed_explanation = ""
        key_factors = []
        confidence = 0
        
        if signal == 'BUY':
            key_factors = [
                f"RSI is {analysis.rsi:.0f} - below 50 (bullish zone)",
                f"Trend is {analysis.trend} with {analysis.trend_probability:.0f}% probability",
                f"Price is above VWAP ({analysis.current_price} > {analysis.vwap})",
                f"Volume trend is {analysis.volume_trend}"
            ]
            
            simple_explanation = (
                f"The stock shows strong buy signals because: "
                f"(1) Price is in uptrend ({analysis.trend}), "
                f"(2) RSI indicates room to move up, "
                f"(3) Volume is {analysis.volume_trend}."
            )
            
            detailed_explanation = (
                f"Technical Analysis shows: "
                f"RSI={analysis.rsi:.2f} (oversold zone <30), "
                f"Price above VWAP={analysis.vwap:.2f}, "
                f"Bollinger Band position shows {analysis.bollinger_upper:.2f} resistance, "
                f"Volume trend: {analysis.volume_trend}. "
                f"This combination suggests bullish momentum."
            )
            
            confidence = analysis.trend_probability if analysis.trend_probability > 50 else 60
        
        elif signal == 'SELL':
            key_factors = [
                f"RSI is {analysis.rsi:.0f} - above 50 (bearish zone)",
                f"Trend is {analysis.trend}",
                f"Price is below resistance level",
                f"Volume trend is {analysis.volume_trend}"
            ]
            
            simple_explanation = (
                f"The stock shows sell signals because: "
                f"(1) Price is in downtrend ({analysis.trend}), "
                f"(2) RSI is overbought, "
                f"(3) Resistance is near."
            )
            
            detailed_explanation = (
                f"Technical Analysis shows: "
                f"RSI={analysis.rsi:.2f} (overbought zone >70), "
                f"Approaching resistance={analysis.resistance_level:.2f}, "
                f"Bollinger Bands showing exhaustion, "
                f"Volume trend: {analysis.volume_trend}."
            )
            
            confidence = analysis.trend_probability if analysis.trend_probability > 50 else 60
        
        else:  # HOLD
            simple_explanation = (
                "The market is unclear. Signals are mixed. "
                "Wait for a clear trend direction before entering."
            )
            detailed_explanation = (
                "No dominant signal. RSI is in neutral zone (30-70), "
                "trend is undefined. Wait for clearer market structure."
            )
            key_factors = ["No strong signal", "Wait for confirmation"]
            confidence = 40
        
        return {
            'signal': signal,
            'simple_explanation': simple_explanation,
            'detailed_explanation': detailed_explanation,
            'key_factors': key_factors,
            'confidence_score': min(100, max(0, confidence))
        }


class PaperTradingService:
    """Manage paper trading with live market data and strict risk management"""
    
    COMMISSION_RATE = Decimal('0.0005')  # 0.05% per side = 0.1% round trip
    SLIPPAGE_BUY = Decimal('0.0005')  # 0.05% slippage on buy
    SLIPPAGE_SELL = Decimal('0.0005')  # 0.05% slippage on sell
    
    @staticmethod
    def create_paper_trade(
        portfolio: 'Portfolio',
        stock: Stock,
        side: str,
        entry_price: Decimal,
        quantity: int,
        stop_loss: Decimal,
        target_1: Decimal = None,
        target_2: Decimal = None,
        target_3: Decimal = None,
        target_4: Decimal = None,
        capital: Decimal = None
    ) -> Dict:
        """
        Create a paper trade with live price, risk management validation, and commission calculation
        
        Returns: {success: bool, trade: PaperTrade or None, errors: [], warnings: []}
        """
        from .models import PaperTrade
        from datetime import datetime
        from decimal import Decimal as D
        
        errors = []
        warnings = []
        
        # Fetch real market price
        try:
            market_data = MarketDataFetcher.get_stock_price(stock.symbol)
            live_price = D(str(market_data['price']))
        except Exception as e:
            live_price = entry_price  # Fallback
            warnings.append(f"Using provided price (market data unavailable): {str(e)}")
        
        # Validate entry price is reasonable (within 2% of live price)
        if live_price:
            price_deviation = abs((entry_price - live_price) / live_price)
            if price_deviation > Decimal('0.02'):
                warnings.append(f"Entry price deviates {price_deviation*100:.1f}% from live price")
        
        # Calculate entry value and commission
        entry_value = quantity * entry_price
        entry_commission = entry_value * PaperTradingService.COMMISSION_RATE
        
        # Apply slippage
        if side == 'BUY':
            slippage = entry_price * PaperTradingService.SLIPPAGE_BUY
            actual_entry = entry_price + slippage
        else:  # SELL
            slippage = entry_price * PaperTradingService.SLIPPAGE_SELL
            actual_entry = entry_price - slippage
        
        adjusted_entry_value = quantity * actual_entry
        actual_commission = adjusted_entry_value * PaperTradingService.COMMISSION_RATE
        
        # Calculate risk
        if side == 'BUY':
            risk_amount = (actual_entry - stop_loss) * quantity
        else:  # SELL
            risk_amount = (stop_loss - actual_entry) * quantity
        
        # Validate risk
        if capital:
            risk_percent = (risk_amount / capital) * 100
            if risk_percent > 0.5:
                errors.append(f"Risk exceeds 0.5% limit: {risk_percent:.2f}%")
            if capital < adjusted_entry_value + actual_commission:
                errors.append(f"Insufficient capital. Required: ₹{(adjusted_entry_value + actual_commission):.2f}, Available: ₹{capital:.2f}")
        else:
            risk_percent = 0
        
        # Validate stop loss (should be tight for paper trading - 0.5% to 2%)
        if side == 'BUY':
            stop_percent = abs((actual_entry - stop_loss) / actual_entry) * 100
        else:
            stop_percent = abs((stop_loss - actual_entry) / actual_entry) * 100
        
        if stop_percent > 2.0:
            warnings.append(f"Stop loss is wide: {stop_percent:.2f}%. Recommended: 0.5% - 2%")
        elif stop_percent < 0.1:
            errors.append(f"Stop loss is too tight: {stop_percent:.2f}%. Minimum: 0.1%")
        
        if errors:
            return {
                'success': False,
                'trade': None,
                'errors': errors,
                'warnings': warnings,
                'validation': {'valid': False, 'errors': errors, 'warnings': warnings}
            }
        
        # Create paper trade
        try:
            paper_trade = PaperTrade.objects.create(
                portfolio=portfolio,
                stock=stock,
                side=side,
                entry_price=actual_entry,
                quantity=quantity,
                entry_date=datetime.now(),
                entry_value=adjusted_entry_value,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                target_3=target_3,
                target_4=target_4,
                entry_commission=actual_commission,
                risk_amount=risk_amount,
                risk_percent=float(risk_percent),
                status='ACTIVE',
                current_price=live_price
            )
            
            return {
                'success': True,
                'trade': paper_trade,
                'errors': [],
                'warnings': warnings,
                'validation': {'valid': True, 'errors': [], 'warnings': warnings}
            }
        except Exception as e:
            errors.append(f"Failed to create trade: {str(e)}")
            return {
                'success': False,
                'trade': None,
                'errors': errors,
                'warnings': warnings,
                'validation': {'valid': False, 'errors': errors, 'warnings': warnings}
            }
    
    @staticmethod
    def close_paper_trade(
        paper_trade: 'PaperTrade',
        exit_price: Decimal = None,
        exit_type: str = 'MANUAL'
    ) -> Dict:
        """
        Close a paper trade with live market price, calculate final P&L including commissions
        
        Returns: {success: bool, trade: updated PaperTrade, result: {...}}
        """
        from datetime import datetime
        from decimal import Decimal as D
        
        # Fetch live price if exit_price not provided
        if not exit_price:
            try:
                market_data = MarketDataFetcher.get_stock_price(paper_trade.stock.symbol)
                exit_price = D(str(market_data['price']))
            except Exception as e:
                return {
                    'success': False,
                    'trade': paper_trade,
                    'error': f"Could not fetch live price: {str(e)}",
                    'result': {}
                }
        
        # Apply slippage on exit
        if paper_trade.side == 'BUY':
            slippage = exit_price * PaperTradingService.SLIPPAGE_SELL
            actual_exit = exit_price - slippage
        else:  # SELL
            slippage = exit_price * PaperTradingService.SLIPPAGE_BUY
            actual_exit = exit_price + slippage
        
        # Calculate exit value and commission
        exit_value = paper_trade.quantity * actual_exit
        exit_commission = exit_value * PaperTradingService.COMMISSION_RATE
        
        # Calculate P&L
        if paper_trade.side == 'BUY':
            profit_loss = (actual_exit - paper_trade.entry_price) * paper_trade.quantity
        else:  # SELL
            profit_loss = (paper_trade.entry_price - actual_exit) * paper_trade.quantity
        
        # Deduct commissions from P&L
        total_pnl = profit_loss - paper_trade.entry_commission - exit_commission
        profit_loss_percent = (total_pnl / paper_trade.entry_value) * 100 if paper_trade.entry_value > 0 else 0
        
        # Check if target hit
        hit_target = None
        if paper_trade.side == 'BUY' and paper_trade.target_1:
            if actual_exit >= paper_trade.target_1:
                hit_target = 1
                if paper_trade.target_2 and actual_exit >= paper_trade.target_2:
                    hit_target = 2
                    if paper_trade.target_3 and actual_exit >= paper_trade.target_3:
                        hit_target = 3
                        if paper_trade.target_4 and actual_exit >= paper_trade.target_4:
                            hit_target = 4
        elif paper_trade.side == 'SELL' and paper_trade.target_1:
            if actual_exit <= paper_trade.target_1:
                hit_target = 1
                if paper_trade.target_2 and actual_exit <= paper_trade.target_2:
                    hit_target = 2
                    if paper_trade.target_3 and actual_exit <= paper_trade.target_3:
                        hit_target = 3
                        if paper_trade.target_4 and actual_exit <= paper_trade.target_4:
                            hit_target = 4
        
        # Determine exit type
        if exit_type == 'STOPLOSS':
            final_exit_type = 'STOPLOSS'
        elif hit_target and exit_type != 'MANUAL':
            final_exit_type = 'TARGET'
        else:
            final_exit_type = exit_type
        
        # Update trade
        paper_trade.exit_price = actual_exit
        paper_trade.exit_date = datetime.now()
        paper_trade.exit_type = final_exit_type
        paper_trade.exit_commission = exit_commission
        paper_trade.profit_loss = total_pnl
        paper_trade.profit_loss_percent = float(profit_loss_percent)
        paper_trade.status = 'CLOSED'
        paper_trade.save()
        
        # Calculate hold time
        time_held = paper_trade.exit_date - paper_trade.entry_date
        hours_held = time_held.total_seconds() / 3600
        
        return {
            'success': True,
            'trade': paper_trade,
            'result': {
                'trade_id': paper_trade.id,
                'stock': paper_trade.stock.symbol,
                'side': paper_trade.side,
                'quantity': paper_trade.quantity,
                'entry': float(paper_trade.entry_price),
                'exit': float(actual_exit),
                'entry_value': float(paper_trade.entry_value),
                'exit_value': float(exit_value),
                'entry_commission': float(paper_trade.entry_commission),
                'exit_commission': float(exit_commission),
                'gross_pnl': float(profit_loss),
                'net_pnl': float(total_pnl),
                'pnl_percent': profit_loss_percent,
                'hit_target': hit_target,
                'exit_type': final_exit_type,
                'hours_held': hours_held,
                'status': 'CLOSED'
            }
        }
    
    @staticmethod
    def update_live_prices(portfolio: 'Portfolio') -> Dict:
        """
        Update live prices for all active paper trades and calculate unrealized P&L
        
        Returns: {updated: int, skipped: int, errors: []}
        """
        from decimal import Decimal as D
        
        active_trades = PaperTrade.objects.filter(portfolio=portfolio, status='ACTIVE')
        updated = 0
        skipped = 0
        errors = []
        
        for trade in active_trades:
            try:
                market_data = MarketDataFetcher.get_stock_price(trade.stock.symbol)
                current_price = D(str(market_data['price']))
                
                # Calculate unrealized P&L
                if trade.side == 'BUY':
                    unrealized_pnl = (current_price - trade.entry_price) * trade.quantity - trade.entry_commission
                else:  # SELL
                    unrealized_pnl = (trade.entry_price - current_price) * trade.quantity - trade.entry_commission
                
                # Check if stop loss or target hit
                stop_hit = False
                target_hit = False
                
                if trade.side == 'BUY':
                    if current_price <= trade.stop_loss:
                        stop_hit = True
                    if trade.target_1 and current_price >= trade.target_1:
                        target_hit = True
                else:  # SELL
                    if current_price >= trade.stop_loss:
                        stop_hit = True
                    if trade.target_1 and current_price <= trade.target_1:
                        target_hit = True
                
                trade.current_price = current_price
                trade.unrealized_pnl = unrealized_pnl
                trade.save(update_fields=['current_price', 'unrealized_pnl'])
                updated += 1
                
            except Exception as e:
                errors.append(f"{trade.stock.symbol}: {str(e)}")
                skipped += 1
        
        return {
            'updated': updated,
            'skipped': skipped,
            'errors': errors
        }
    
    @staticmethod
    def get_portfolio_stats(portfolio: 'Portfolio') -> Dict:
        """Calculate paper trading statistics for a portfolio"""
        
        all_trades = PaperTrade.objects.filter(portfolio=portfolio)
        active_trades = all_trades.filter(status='ACTIVE')
        closed_trades = all_trades.filter(status='CLOSED')
        
        # Active stats
        active_count = active_trades.count()
        active_value = sum(t.entry_value for t in active_trades)
        unrealized_pnl = sum(t.unrealized_pnl or 0 for t in active_trades)
        
        # Closed stats
        closed_count = closed_trades.count()
        total_pnl = sum(t.profit_loss or 0 for t in closed_trades)
        winners = closed_trades.filter(profit_loss__gt=0).count()
        losers = closed_trades.filter(profit_loss__lt=0).count()
        win_rate = (winners / closed_count * 100) if closed_count > 0 else 0
        
        # Avg trades
        avg_win = (closed_trades.filter(profit_loss__gt=0).aggregate(avg=models.Avg('profit_loss'))['avg'] or 0)
        avg_loss = (closed_trades.filter(profit_loss__lt=0).aggregate(avg=models.Avg('profit_loss'))['avg'] or 0)
        
        return {
            'total_trades': all_trades.count(),
            'active_trades': active_count,
            'closed_trades': closed_count,
            'active_value': float(active_value),
            'unrealized_pnl': float(unrealized_pnl),
            'total_realized_pnl': float(total_pnl),
            'total_pnl': float(unrealized_pnl + total_pnl),
            'winners': winners,
            'losers': losers,
            'win_rate': round(win_rate, 2),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0
        }


class InvestmentPlannerService:
    """Generate investment plans based on user goals with dynamic stock selection"""
    
    GOAL_TEMPLATES = {
        'WEALTH_CREATION': {
            'description': 'Build wealth over time through balanced investing',
            'equity_percent': 70,
            'debt_percent': 20,
            'alternatives_percent': 10,
            'expected_returns': 12.0,
            'selection_criteria': {
                'market': 'NSE',
                'sort_by': 'market_cap',
                'limit': 10,
                'min_market_cap': None
            }
        },
        'RETIREMENT': {
            'description': 'Conservative planning for retirement',
            'equity_percent': 40,
            'debt_percent': 50,
            'alternatives_percent': 10,
            'expected_returns': 8.0,
            'selection_criteria': {
                'market': 'NSE',
                'sectors': ['Banking', 'Financial Services'],
                'sort_by': 'market_cap',
                'limit': 5,
                'min_dividend_yield': 0.02
            }
        },
        'SHORT_TERM_GAINS': {
            'description': 'Aggressive strategy for quick returns',
            'equity_percent': 90,
            'debt_percent': 5,
            'alternatives_percent': 5,
            'expected_returns': 20.0,
            'selection_criteria': {
                'market': 'NSE',
                'sectors': ['Information Technology'],
                'sort_by': 'volume',
                'limit': 10
            }
        }
    }
    
    @staticmethod
    def create_investment_plan(
        goal: str,
        target_amount: Decimal,
        time_horizon: str,
        risk_tolerance: str
    ) -> Dict:
        """Create personalized investment plan with dynamic stock recommendations"""
        
        template = InvestmentPlannerService.GOAL_TEMPLATES.get(goal, {})
        
        # Adjust allocation based on risk tolerance
        if risk_tolerance == 'LOW':
            equity = max(template.get('equity_percent', 50) - 20, 20)
            debt = min(template.get('debt_percent', 40) + 20, 70)
        elif risk_tolerance == 'HIGH':
            equity = min(template.get('equity_percent', 50) + 20, 90)
            debt = max(template.get('debt_percent', 40) - 20, 10)
        else:
            equity = template.get('equity_percent', 50)
            debt = template.get('debt_percent', 40)
        
        alternatives = 100 - equity - debt
        
        # Get dynamic stock recommendations based on goal
        recommended_stocks = InvestmentPlannerService._get_recommended_stocks(goal)
        
        return {
            'goal': goal,
            'target_amount': float(target_amount),
            'time_horizon': time_horizon,
            'risk_tolerance': risk_tolerance,
            'allocation': {
                'equity': equity,
                'debt': debt,
                'alternatives': alternatives
            },
            'expected_annual_return': template.get('expected_returns', 10.0),
            'recommended_stocks': recommended_stocks,
            'description': template.get('description', '')
        }
    
    @staticmethod
    def _get_recommended_stocks(goal: str, limit: int = 10) -> List[Dict]:
        """
        Get dynamic stock recommendations based on goal
        
        Args:
            goal: Investment goal
            limit: Number of recommendations
        
        Returns:
            List of recommended stock data
        """
        
        criteria = InvestmentPlannerService.GOAL_TEMPLATES.get(goal, {}).get('selection_criteria', {})
        
        if not criteria:
            # Fallback: top stocks by market cap
            return StockUniverseManager.get_top_stocks('NSE', limit=limit)
        
        market = criteria.get('market', 'NSE')
        sectors = criteria.get('sectors')
        sort_by = criteria.get('sort_by', 'market_cap')
        limit = criteria.get('limit', limit)
        
        recommendations = []
        
        if sectors:
            # Get stocks from specific sectors
            for sector in sectors:
                filtered = StockUniverseManager.filter_stocks(
                    market=market,
                    sector=sector
                )
                
                # Sort and add to recommendations
                sorted_stocks = sorted(filtered.values(),
                                     key=lambda x: x.get(sort_by, 0),
                                     reverse=True)
                recommendations.extend(sorted_stocks[:limit // len(sectors)])
        else:
            # Get top stocks by criteria
            recommendations = StockUniverseManager.get_top_stocks(
                market=market,
                sort_by=sort_by,
                limit=limit
            )
        
        return recommendations[:limit]
    
    @staticmethod
    def get_goal_recommendations(goal: str) -> Dict:
        """
        Get goal-specific recommendations with additional analysis
        
        Args:
            goal: Investment goal
        
        Returns:
            Dict with goal analysis and recommendations
        """
        
        template = InvestmentPlannerService.GOAL_TEMPLATES.get(goal, {})
        recommendations = InvestmentPlannerService._get_recommended_stocks(goal)
        
        return {
            'goal': goal,
            'description': template.get('description', ''),
            'allocation': {
                'equity': template.get('equity_percent', 50),
                'debt': template.get('debt_percent', 40),
                'alternatives': template.get('alternatives_percent', 10)
            },
            'expected_returns': template.get('expected_returns', 10.0),
            'recommended_stocks': recommendations,
            'stocks_count': len(recommendations),
            'sector_distribution': InvestmentPlannerService._analyze_sector_distribution(recommendations)
        }
    
    @staticmethod
    def _analyze_sector_distribution(stocks: List[Dict]) -> Dict[str, int]:
        """Analyze sector distribution of recommended stocks"""
        
        distribution = {}
        
        for stock in stocks:
            sector = stock.get('sector', 'Unknown')
            distribution[sector] = distribution.get(sector, 0) + 1
        
        return distribution


class StockRecommendationService:
    """Dynamic stock recommendations based on various criteria"""
    
    @staticmethod
    def get_recommendations(
        market: str = 'NSE',
        category: str = 'large_cap',
        limit: int = 10,
        sector: Optional[str] = None
    ) -> List[Dict]:
        """
        Get stock recommendations by category
        
        Args:
            market: 'NSE', 'BSE', or 'ALL'
            category: 'large_cap', 'mid_cap', 'high_dividend', 'gainers'
            limit: Number of recommendations
            sector: Optional sector filter
        
        Returns:
            List of recommended stocks
        """
        
        if category == 'large_cap':
            return StockUniverseManager.get_large_cap_stocks(market, limit)
        elif category == 'mid_cap':
            return StockUniverseManager.get_mid_cap_stocks(market, limit)
        elif category == 'high_dividend':
            return StockUniverseManager.get_high_dividend_stocks(market, limit)
        elif category == 'gainers':
            return StockUniverseManager.get_top_gainers(market, limit)
        else:
            return StockUniverseManager.get_top_stocks(market, limit=limit)
    
    @staticmethod
    def get_sector_recommendations(
        sector: str,
        market: str = 'NSE',
        limit: int = 10,
        sort_by: str = 'market_cap'
    ) -> List[Dict]:
        """
        Get top stocks in a specific sector
        
        Args:
            sector: Sector name
            market: Market to search
            limit: Number of results
            sort_by: Sorting criteria
        
        Returns:
            List of stocks in sector
        """
        
        return StockUniverseManager.get_top_stocks(
            market=market,
            sort_by=sort_by,
            limit=limit,
            sector=sector
        )
    
    @staticmethod
    def get_all_sectors(market: str = 'NSE') -> List[str]:
        """Get all available sectors"""
        
        return StockUniverseManager.get_sectors(market)
    
    @staticmethod
    def search_recommendations(
        query: str,
        market: str = 'NSE',
        limit: int = 10
    ) -> List[Dict]:
        """
        Search for stock recommendations
        
        Args:
            query: Search query (symbol or name)
            market: Market to search
            limit: Max results
        
        Returns:
            List of matching stocks
        """
        
        results = StockUniverseManager.search_stocks(query, market)
        return list(results.values())[:limit]


class PatternScannerService:
    """Dynamic stock scanner using stock universe and technical analysis"""
    
    @staticmethod
    def scan_for_breakouts(
        market: str = 'NSE',
        sector: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scan for potential breakout stocks
        
        Uses high volume and price strength as indicators
        """
        
        if sector:
            stocks = StockUniverseManager.filter_stocks(market, sector=sector)
        else:
            stocks = StockUniverseManager.get_all_stocks(market)
        
        # Filter by volume and recent performance
        candidates = []
        
        for symbol, data in stocks.items():
            if data.get('error'):
                continue
            
            # High volume stocks with good price movement
            volume = data.get('average_volume', 0)
            price = data.get('price', 0)
            high_52w = data.get('week_52_high', 0)
            
            if volume > 0 and price > 0 and high_52w > 0:
                proximity_to_high = (price / high_52w) * 100
                
                # Near 52-week high + good volume = breakout candidate
                if proximity_to_high > 80:
                    candidates.append({
                        **data,
                        'proximity_to_high': proximity_to_high,
                        'signal': 'BREAKOUT',
                        'confidence': min(100, proximity_to_high + 20)
                    })
        
        # Sort by proximity to high
        candidates.sort(key=lambda x: x.get('proximity_to_high', 0), reverse=True)
        
        return candidates[:limit]
    
    @staticmethod
    def scan_for_reversals(
        market: str = 'NSE',
        sector: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scan for potential reversal stocks
        
        Uses proximity to 52-week low as indicator
        """
        
        if sector:
            stocks = StockUniverseManager.filter_stocks(market, sector=sector)
        else:
            stocks = StockUniverseManager.get_all_stocks(market)
        
        candidates = []
        
        for symbol, data in stocks.items():
            if data.get('error'):
                continue
            
            price = data.get('price', 0)
            low_52w = data.get('week_52_low', 0)
            volume = data.get('average_volume', 0)
            
            if price > 0 and low_52w > 0 and volume > 0:
                proximity_to_low = (price / low_52w) * 100
                
                # Near 52-week low + good volume = reversal candidate
                if proximity_to_low < 120:
                    candidates.append({
                        **data,
                        'proximity_to_low': proximity_to_low,
                        'signal': 'REVERSAL',
                        'confidence': min(100, 120 - proximity_to_low)
                    })
        
        # Sort by proximity to low
        candidates.sort(key=lambda x: x.get('proximity_to_low', 0))
        
        return candidates[:limit]
    
    @staticmethod
    def scan_dividend_stocks(
        market: str = 'NSE',
        min_yield: float = 0.02,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scan for dividend-paying stocks
        
        Args:
            market: Market to scan
            min_yield: Minimum dividend yield (default 2%)
            limit: Number of results
        
        Returns:
            List of dividend stocks
        """
        
        stocks = StockUniverseManager.filter_stocks(
            market=market,
            min_dividend_yield=min_yield
        )
        
        # Sort by dividend yield
        sorted_stocks = sorted(stocks.values(),
                             key=lambda x: x.get('dividend_yield', 0),
                             reverse=True)
        
        return sorted_stocks[:limit]
    
    @staticmethod
    def scan_by_criteria(
        market: str = 'NSE',
        sector: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_market_cap: Optional[int] = None,
        min_volume: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scan stocks by custom criteria
        
        Args:
            market: Market to scan
            sector: Optional sector filter
            min_price/max_price: Price range
            min_market_cap: Minimum market cap
            min_volume: Minimum volume
            limit: Number of results
        
        Returns:
            Filtered stocks
        """
        
        stocks = StockUniverseManager.filter_stocks(
            market=market,
            sector=sector,
            min_price=min_price,
            max_price=max_price,
            min_market_cap=min_market_cap,
            min_volume=min_volume
        )
        
        return list(stocks.values())[:limit]
    
    @staticmethod
    def scan_sector_performance(market: str = 'NSE') -> Dict[str, List[Dict]]:
        """
        Get top performers in each sector
        
        Args:
            market: Market to analyze
        
        Returns:
            Dict with top stocks per sector
        """
        
        by_sector = StockUniverseManager.get_by_sector(market)
        sector_performance = {}
        
        for sector, stocks in by_sector.items():
            # Sort by 52-week performance
            performers = []
            
            for stock in stocks:
                high = stock.get('week_52_high', 0)
                low = stock.get('week_52_low', 0)
                
                if high > 0 and low > 0:
                    performance = ((high - low) / low) * 100
                    stock['performance'] = performance
                    performers.append(stock)
            
            performers.sort(key=lambda x: x.get('performance', 0), reverse=True)
            sector_performance[sector] = performers[:3]  # Top 3 per sector
        
        return sector_performance


class StockAnalysisService:
    """Comprehensive stock analysis using dynamic stock universe"""
    
    @staticmethod
    def get_stock_profile(symbol: str, market: str = 'NSE') -> Dict:
        """
        Get complete stock profile
        
        Args:
            symbol: Stock symbol
            market: Market
        
        Returns:
            Comprehensive stock data
        """
        
        all_stocks = StockUniverseManager.get_all_stocks(market)
        
        if symbol not in all_stocks:
            return {'error': f'Stock {symbol} not found'}
        
        stock_data = all_stocks[symbol]
        
        return {
            'basic_info': {
                'symbol': symbol,
                'name': stock_data.get('name'),
                'sector': stock_data.get('sector'),
                'market': market
            },
            'valuation': {
                'current_price': stock_data.get('price'),
                'market_cap': stock_data.get('market_cap'),
                'pe_ratio': stock_data.get('pe_ratio'),
                'dividend_yield': stock_data.get('dividend_yield')
            },
            'performance': {
                '52w_high': stock_data.get('week_52_high'),
                '52w_low': stock_data.get('week_52_low'),
                'average_volume': stock_data.get('average_volume'),
                'last_updated': stock_data.get('updated')
            }
        }
    
    @staticmethod
    def compare_stocks(symbols: List[str], market: str = 'NSE') -> Dict[str, Dict]:
        """
        Compare multiple stocks
        
        Args:
            symbols: List of stock symbols
            market: Market
        
        Returns:
            Comparison data for all stocks
        """
        
        comparison = {}
        
        for symbol in symbols:
            profile = StockAnalysisService.get_stock_profile(symbol, market)
            if 'error' not in profile:
                comparison[symbol] = profile
        
        return comparison
    
    @staticmethod
    def get_sector_analysis(sector: str, market: str = 'NSE') -> Dict:
        """
        Analyze entire sector
        
        Args:
            sector: Sector name
            market: Market
        
        Returns:
            Sector analysis with top stocks
        """
        
        stocks = StockUniverseManager.get_top_stocks(
            market=market,
            sector=sector,
            limit=10
        )
        
        if not stocks:
            return {'error': f'Sector {sector} not found'}
        
        # Calculate sector statistics
        prices = [s.get('price', 0) for s in stocks if s.get('price')]
        market_caps = [s.get('market_cap', 0) for s in stocks if s.get('market_cap')]
        volumes = [s.get('average_volume', 0) for s in stocks if s.get('average_volume')]
        
        return {
            'sector': sector,
            'total_stocks': len(stocks),
            'top_stocks': stocks,
            'statistics': {
                'avg_price': sum(prices) / len(prices) if prices else 0,
                'total_market_cap': sum(market_caps),
                'avg_volume': sum(volumes) / len(volumes) if volumes else 0
            }
        }