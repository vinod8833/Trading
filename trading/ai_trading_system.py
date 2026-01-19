

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
from decimal import Decimal
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataQualityLevel(Enum):
    """Data quality assessment levels"""
    PRISTINE = "pristine"      
    CLEAN = "clean"           
    ACCEPTABLE = "acceptable"  
    DEGRADED = "degraded"      
    UNUSABLE = "unusable"      


@dataclass
class DataQualityReport:
    """Comprehensive data quality assessment"""
    level: DataQualityLevel
    completeness: float  
    freshness_minutes: int 
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    is_safe_for_trading: bool = False
    confidence_penalty: float = 0.0  
    
    def can_proceed(self) -> bool:
        """Check if data is safe for analysis"""
        return self.level in [DataQualityLevel.PRISTINE, DataQualityLevel.CLEAN] and \
               self.completeness >= 95 and \
               self.is_safe_for_trading


@dataclass
class ValidatedOHLCData:
    """Validated OHLC data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate data integrity"""
        errors = []
        
        if self.open <= 0 or self.high <= 0 or self.low <= 0 or self.close <= 0:
            errors.append("All prices must be positive")
        
        if self.high < max(self.open, self.close):
            errors.append(f"High ({self.high}) cannot be less than Open/Close")
        
        if self.low > min(self.open, self.close):
            errors.append(f"Low ({self.low}) cannot be greater than Open/Close")
        
        if self.volume < 0:
            errors.append("Volume cannot be negative")
        
        if self.high == self.low and self.open != self.close:
            errors.append("Inconsistent price data: High=Low but Open≠Close")
        
        return len(errors) == 0, errors


class DataIntakeEngine:
    """
    Complete data validation and cleaning system
    Ensures all input data is verified before analysis
    """
    
    MIN_CANDLES_REQUIRED = 50
    MAX_DATA_AGE_HOURS = 24
    STALE_DATA_AGE_HOURS = 4
    
    @staticmethod
    def validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
        """Validate stock symbol format and mapping"""
        if not symbol or not isinstance(symbol, str):
            return False, "Invalid symbol format"
        
        symbol = symbol.strip().upper()
        
        if len(symbol) < 1 or len(symbol) > 10:
            return False, f"Symbol length must be 1-10 characters, got {len(symbol)}"
        
        if not all(c.isalnum() or c == '-' for c in symbol):
            return False, "Symbol contains invalid characters"
        
        indian_nifty_50 = {
            'INFY', 'TCS', 'RELIANCE', 'HDFC', 'WIPRO', 'MARUTI', 'BAJAJFINSV',
            'LT', 'ICICIBANK', 'AXISBANK', 'HDFCBANK', 'SBIN', 'HINDUSTAN',
            'BAJAJ-AUTO', 'NESTLEIND', 'POWERGRID', 'SUNPHARMA', 'TECHM',
            'ITC', 'BHARTIARTL', 'JSWSTEEL', 'HEROMOTOCO', 'ASIANPAINT',
            'ONGC', 'DRREDDY', 'ADANIPORTS', 'GAIL', 'ULTRACEMCO', 'HINDALCO',
            'INDIGO', 'TITAN', 'M&M', 'BPCL', 'COALINDIA', 'APOLLO',
            'EICHERMOT', 'NTPC', 'TATAMOTORS', 'TATASTEEL', 'CIPLA'
        }
        
        if symbol not in indian_nifty_50:
            logger.warning(f"Symbol {symbol} not in known NIFTY50 list, proceeding with caution")
        
        return True, symbol
    
    @staticmethod
    def validate_ohlc_series(
        prices: List[float],
        volumes: List[int],
        highs: List[float],
        lows: List[float],
        labels: Optional[List[str]] = None
    ) -> Tuple[bool, List[str], List[float], List[int], List[float], List[float]]:
        """
        Validate and clean OHLC data series
        Returns (is_valid, errors, cleaned_prices, cleaned_volumes, cleaned_highs, cleaned_lows)
        """
        errors = []
        
        if not prices or len(prices) < DataIntakeEngine.MIN_CANDLES_REQUIRED:
            errors.append(f"Minimum {DataIntakeEngine.MIN_CANDLES_REQUIRED} candles required, got {len(prices) if prices else 0}")
            return False, errors, [], [], [], []
        
        if not (len(prices) == len(volumes) == len(highs) == len(lows)):
            errors.append("Prices, volumes, highs, and lows must have equal length")
            return False, errors, [], [], [], []
        
        cleaned_prices = []
        cleaned_volumes = []
        cleaned_highs = []
        cleaned_lows = []
        removed_indices = []
        
        for i in range(len(prices)):
            try:
                p = float(prices[i])
                v = int(volumes[i]) if volumes[i] else 0
                h = float(highs[i])
                l = float(lows[i])
                
                if p <= 0 or h <= 0 or l <= 0:
                    removed_indices.append(i)
                    continue
                
                if h < max(p, l) or l > min(p, h):
                    removed_indices.append(i)
                    continue
                
                if i > 0 and p > cleaned_prices[-1] * 50 or p < cleaned_prices[-1] / 50:
                    logger.warning(f"Extreme price movement at candle {i}: {cleaned_prices[-1]} -> {p}")
                    removed_indices.append(i)
                    continue
                
                cleaned_prices.append(p)
                cleaned_volumes.append(v)
                cleaned_highs.append(h)
                cleaned_lows.append(l)
                
            except (ValueError, TypeError) as e:
                removed_indices.append(i)
                logger.warning(f"Invalid data at candle {i}: {e}")
        
        if removed_indices:
            errors.append(f"Removed {len(removed_indices)} invalid candles: {removed_indices[:10]}")
        
        if len(cleaned_prices) < DataIntakeEngine.MIN_CANDLES_REQUIRED:
            errors.append(f"After cleaning, only {len(cleaned_prices)} valid candles remain")
            return False, errors, [], [], [], []
        
        return True, errors, cleaned_prices, cleaned_volumes, cleaned_highs, cleaned_lows
    
    @staticmethod
    def assess_data_quality(
        data: pd.DataFrame,
        symbol: str,
        market_open: bool,
        last_update: datetime
    ) -> DataQualityReport:
        """Comprehensive data quality assessment"""
        issues = []
        warnings = []
        
        total_rows = len(data)
        missing_price = data['close'].isna().sum()
        missing_volume = data['volume'].isna().sum()
        completeness = ((total_rows - max(missing_price, missing_volume)) / total_rows * 100) if total_rows > 0 else 0
        
        now = datetime.now()
        data_age = (now - last_update).total_seconds() / 60  
        
        if 'timestamp' in data.columns:
            time_diffs = data['timestamp'].diff()
            irregular_gaps = (time_diffs > timedelta(hours=1)).sum()
            if irregular_gaps > 0:
                warnings.append(f"Found {irregular_gaps} irregular time gaps in data")
        
        if 'timestamp' in data.columns:
            duplicates = data.duplicated(subset=['timestamp']).sum()
            if duplicates > 0:
                issues.append(f"Found {duplicates} duplicate timestamps")
        
        if market_open and data_age < 5:
            level = DataQualityLevel.PRISTINE
        elif data_age < 60 and completeness >= 95:
            level = DataQualityLevel.CLEAN
        elif data_age < 240 and completeness >= 90:
            level = DataQualityLevel.ACCEPTABLE
        elif data_age < DataIntakeEngine.MAX_DATA_AGE_HOURS * 60:
            level = DataQualityLevel.DEGRADED
        else:
            level = DataQualityLevel.UNUSABLE
            issues.append(f"Data is {data_age/60:.1f} hours old, exceeds {DataIntakeEngine.MAX_DATA_AGE_HOURS}h limit")
        
        stale_minutes = max(0, data_age - DataIntakeEngine.STALE_DATA_AGE_HOURS * 60)
        freshness_penalty = min(20, stale_minutes / 60)  
        
        is_safe = level in [DataQualityLevel.PRISTINE, DataQualityLevel.CLEAN] and \
                  completeness >= 95 and \
                  not any('duplicate' in issue.lower() for issue in issues)
        
        return DataQualityReport(
            level=level,
            completeness=round(completeness, 1),
            freshness_minutes=int(data_age),
            issues=issues,
            warnings=warnings,
            is_safe_for_trading=is_safe,
            confidence_penalty=freshness_penalty
        )



class MarketState(Enum):
    """Market operational states"""
    OPEN = "open"
    CLOSED = "closed"
    HOLIDAY = "holiday"
    LOW_LIQUIDITY = "low_liquidity"
    CIRCUIT_BREAKER = "circuit_breaker"


@dataclass
class MarketStatus:
    """Current market status and context"""
    state: MarketState
    is_trading_allowed: bool
    data_type: str  
    confidence_applicable: bool  
    message: str
    next_open_time: Optional[datetime] = None
    
    def get_recommendation(self) -> str:
        """Get user-facing recommendation"""
        if self.state == MarketState.OPEN:
            return "Market is OPEN. Execute signals immediately with market orders."
        elif self.state == MarketState.CLOSED:
            return "Market is CLOSED. Prepare orders for next market open. Use limit orders."
        elif self.state == MarketState.HOLIDAY:
            return "Market HOLIDAY. No trading today. Resume tomorrow."
        elif self.state == MarketState.LOW_LIQUIDITY:
            return "LOW LIQUIDITY detected. Use larger spreads, consider smaller position size."
        elif self.state == MarketState.CIRCUIT_BREAKER:
            return "CIRCUIT BREAKER triggered. Trading halted. Wait for market to resume."
        return "Unknown market state"


class MarketStateDetector:
    """
    Detect real-time market state and data freshness
    Ensures appropriate data source and signal confidence
    """
    
    IST_MARKET_OPEN = (9, 15)     
    IST_MARKET_CLOSE = (15, 30)   
    
    NIFTY_HOLIDAYS_2026 = {
        "2026-01-26",  
        "2026-03-25",  
        "2026-04-14",  
        "2026-08-15",  
        "2026-09-02",  
        "2026-10-02",  
        "2026-10-25",  
        "2026-12-25",  
    }
    
    @staticmethod
    def get_market_status() -> MarketStatus:
        """Get current market status with IST timezone awareness"""
        from datetime import timezone
        
        now = datetime.now()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_time = now + ist_offset
        
        today_str = ist_time.strftime("%Y-%m-%d")
        if today_str in MarketStateDetector.NIFTY_HOLIDAYS_2026:
            return MarketStatus(
                state=MarketState.HOLIDAY,
                is_trading_allowed=False,
                data_type="HISTORICAL",
                confidence_applicable=False,
                message="Market holiday - Use data from previous trading session"
            )
        
        if ist_time.weekday() >= 5:  
            next_open = ist_time + timedelta(days=(7 - ist_time.weekday()))
            next_open = next_open.replace(hour=9, minute=15, second=0, microsecond=0)
            return MarketStatus(
                state=MarketState.CLOSED,
                is_trading_allowed=False,
                data_type="HISTORICAL",
                confidence_applicable=False,
                message="Market closed (weekend)",
                next_open_time=next_open
            )
        
        is_weekday = ist_time.weekday() < 5
        hour, minute = ist_time.hour, ist_time.minute
        open_hour, open_minute = MarketStateDetector.IST_MARKET_OPEN
        close_hour, close_minute = MarketStateDetector.IST_MARKET_CLOSE
        
        current_time = hour * 60 + minute
        open_time = open_hour * 60 + open_minute
        close_time = close_hour * 60 + close_minute
        
        is_market_hours = is_weekday and open_time <= current_time <= close_time
        
        if is_market_hours:
            return MarketStatus(
                state=MarketState.OPEN,
                is_trading_allowed=True,
                data_type="LIVE",
                confidence_applicable=True,
                message="✓ Market is OPEN - Using LIVE data"
            )
        else:
            if hour < open_hour or (hour == open_hour and minute < open_minute):
                next_open = ist_time.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)
            elif hour >= close_hour:
                next_open = ist_time + timedelta(days=1)
                next_open = next_open.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)
            else:
                next_open = ist_time.replace(hour=close_hour, minute=close_minute, second=0, microsecond=0)
            
            return MarketStatus(
                state=MarketState.CLOSED,
                is_trading_allowed=False,
                data_type="HISTORICAL",
                confidence_applicable=False,
                message="✗ Market is CLOSED - Using last session data",
                next_open_time=next_open
            )
    
    @staticmethod
    def assess_liquidity(volume: int, avg_volume: float) -> Tuple[bool, float]:
        """
        Assess trading liquidity
        Returns (is_liquid, liquidity_score 0-100)
        """
        if avg_volume <= 0:
            return False, 0.0
        
        volume_ratio = volume / avg_volume
        
        if volume_ratio < 0.3:
            return False, volume_ratio * 100
        elif volume_ratio < 0.7:
            return False, volume_ratio * 100
        else:
            return True, min(100, volume_ratio * 100)




@dataclass
class TraderRuleAssessment:
    """Results of applying senior trader rules"""
    passes_rules: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    risk_score: float = 0.0  
    position_size_multiplier: float = 1.0  


class SeniorTraderRulesEngine:
    """
    Senior trader rules for signal validation
    Ensures capital protection and risk management
    """
    
    @staticmethod
    def validate_signal_setup(
        entry_price: float,
        stop_loss: float,
        target_1: float,
        target_2: Optional[float],
        current_price: float,
        capital: float,
        risk_percent: float = 1.0,
        signal_type: str = "BUY"
    ) -> TraderRuleAssessment:
        """
        Apply senior trader rules to validate signal setup
        """
        violations = []
        warnings = []
        
        risk_amount = abs(entry_price - stop_loss)
        reward_amount = abs(target_1 - entry_price)
        
        if risk_amount <= 0:
            violations.append("Risk amount must be positive (Entry ≠ Stop Loss)")
            return TraderRuleAssessment(passes_rules=False, violations=violations)
        
        risk_reward = reward_amount / risk_amount
        if risk_reward < 1.5:
            violations.append(f"Risk/Reward ratio too low: 1:{risk_reward:.2f} (minimum 1:1.5 required)")
        elif risk_reward < 2.0:
            warnings.append(f"Risk/Reward ratio: 1:{risk_reward:.2f} (ideal 1:2+)")
        
        distance_pct = abs(entry_price - current_price) / current_price * 100
        if distance_pct > 3:
            warnings.append(f"Entry price {distance_pct:.1f}% away from current price - slippage risk")
        
        if signal_type == "BUY":
            if stop_loss >= entry_price:
                violations.append("Stop loss must be below entry price for BUY signal")
            if target_1 <= entry_price:
                violations.append("Target must be above entry price for BUY signal")
        else:  
            if stop_loss <= entry_price:
                violations.append("Stop loss must be above entry price for SELL signal")
            if target_1 >= entry_price:
                violations.append("Target must be below entry price for SELL signal")
        
        position_cost = abs(entry_price - stop_loss) * capital / 100
        if position_cost > capital * (risk_percent / 100):
            position_multiplier = (capital * risk_percent / 100) / position_cost
            warnings.append(f"Position size needs {position_multiplier:.2f}x adjustment")
        else:
            position_multiplier = 1.0
        
        max_loss_in_rupees = capital * (risk_percent / 100)
        if max_loss_in_rupees < 100:
            violations.append(f"Maximum loss amount too low: ₹{max_loss_in_rupees:.0f} (minimum ₹100 suggested)")
        
        if target_2 is None or target_2 <= target_1:
            warnings.append("Multiple targets recommended (target_1, target_2, target_3) for better P&L management")
        
        risk_score = min(100, max(0,
            (100 - risk_reward * 10) +  
            (distance_pct * 2) +        
            (50 if risk_reward < 1.5 else 0)  
        ))
        
        passes_rules = len(violations) == 0
        
        return TraderRuleAssessment(
            passes_rules=passes_rules,
            violations=violations,
            warnings=warnings,
            risk_score=risk_score,
            position_size_multiplier=position_multiplier
        )
    
    @staticmethod
    def validate_market_conditions(
        market_status: MarketStatus,
        volatility_high: bool,
        volume_adequate: bool,
        trend_strength: float
    ) -> TraderRuleAssessment:
        """Validate if market conditions are suitable for trading"""
        violations = []
        warnings = []
        
        if market_status.state == MarketState.CLOSED:
            violations.append("Market is closed - signals are analysis only, not executable")
        elif market_status.state == MarketState.HOLIDAY:
            violations.append("Market is closed for holiday - no trading possible")
        elif market_status.state == MarketState.LOW_LIQUIDITY:
            violations.append("Low liquidity detected - execution may be difficult")
        
        if not volume_adequate:
            violations.append("Insufficient volume - execution risk too high")
        
        if volatility_high:
            warnings.append("High volatility - consider wider stops or smaller positions")
        
        if trend_strength < 0.5:
            warnings.append("Trend strength weak - wait for stronger setup")
        
        passes_rules = len(violations) == 0 and market_status.is_trading_allowed
        
        return TraderRuleAssessment(
            passes_rules=passes_rules,
            violations=violations,
            warnings=warnings
        )


@dataclass
class TradingSignal:
    """
    Validated trading signal with full transparency
    Every output is traceable to verified input data
    """
    symbol: str
    signal_type: str  
    confidence: float  
    
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: Optional[float] = None
    target_3: Optional[float] = None
    
    risk_reward_ratio: float = 0.0
    position_size: int = 0
    max_risk_amount: float = 0.0
    
    data_quality: DataQualityLevel = DataQualityLevel.CLEAN
    market_status: MarketState = MarketState.CLOSED
    data_type: str = "HISTORICAL"
    
    formulas_used: List[str] = field(default_factory=list)
    confidence_reasons: List[str] = field(default_factory=list)
    confidence_penalties: Dict[str, float] = field(default_factory=dict)
    

    is_executable: bool = False
    is_valid: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    generated_at: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to API response format"""
        return {
            'symbol': self.symbol,
            'signal': self.signal_type,
            'confidence': round(self.confidence, 1),
            'entry_price': round(self.entry_price, 2),
            'stop_loss': round(self.stop_loss, 2),
            'target_1': round(self.target_1, 2),
            'target_2': round(self.target_2, 2) if self.target_2 else None,
            'target_3': round(self.target_3, 2) if self.target_3 else None,
            'risk_reward': round(self.risk_reward_ratio, 2),
            'position_size': self.position_size,
            'data_quality': self.data_quality.value,
            'market_status': self.market_status.value,
            'data_type': self.data_type,
            'formulas_used': self.formulas_used,
            'confidence_reasons': self.confidence_reasons,
            'is_executable': self.is_executable,
            'market_recommendation': self._get_market_recommendation(),
            'generated_at': self.generated_at.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
        }
    
    def _get_market_recommendation(self) -> str:
        """Get execution recommendation based on market state"""
        if not self.is_executable:
            return "⚠ Signal not executable - review errors below"
        
        if self.market_status == MarketState.OPEN:
            return "✓ Market OPEN - Execute at market or limit price immediately"
        elif self.market_status == MarketState.CLOSED:
            return "✗ Market CLOSED - Set alert and execute at next market open"
        else:
            return "⚠ Market condition not ideal - proceed with caution"


class SignalGenerationEngine:
    """
    Generate trading signals with complete validation
    Outputs only reliable, traceable signals
    """
    
    @staticmethod
    def generate_signal(
        symbol: str,
        prices: List[float],
        volumes: List[int],
        highs: List[float],
        lows: List[float],
        current_price: float,
        capital: float,
        trader_type: str = "SWING",
        indicator_analysis: Dict = None,
        market_data_age_minutes: int = 0
    ) -> TradingSignal:
        """
        Generate a trading signal with complete validation
        Returns signal with full transparency on confidence and reliability
        """
        
        signal = TradingSignal(
            symbol=symbol,
            signal_type="HOLD",  
            confidence=0.0,
            entry_price=current_price,
            stop_loss=current_price * 0.98,
            target_1=current_price * 1.02
        )
        
        try:
            logger.info(f"Generating signal for {symbol}")
            
            valid, errors, clean_prices, clean_vols, clean_highs, clean_lows = \
                DataIntakeEngine.validate_ohlc_series(prices, volumes, highs, lows)
            
            if not valid:
                signal.errors = errors
                signal.is_valid = False
                logger.error(f"Data validation failed for {symbol}: {errors}")
                return signal
            
            signal.formulas_used.append("DATA_VALIDATION")
            
            market_status = MarketStateDetector.get_market_status()
            signal.market_status = market_status.state
            signal.data_type = market_status.data_type
            
            if not market_status.is_trading_allowed:
                signal.warnings.append(market_status.message)
                signal.is_executable = False
            
            df = pd.DataFrame({
                'close': clean_prices,
                'volume': clean_vols,
                'high': clean_highs,
                'low': clean_lows
            })
            
            quality_report = DataIntakeEngine.assess_data_quality(
                df, symbol, market_status.is_trading_allowed,
                datetime.now() - timedelta(minutes=market_data_age_minutes)
            )
            
            signal.data_quality = quality_report.level
            signal.warnings.extend(quality_report.warnings)
            
            if not quality_report.can_proceed():
                signal.errors = quality_report.issues
                signal.confidence_penalties['data_quality'] = 50.0  
            
            if indicator_analysis is None:
                indicator_analysis = {}
            
            signal_votes = indicator_analysis.get('signal_votes', {'BUY': 0, 'SELL': 0, 'HOLD': 0})
            total_votes = sum(signal_votes.values())
            
            if total_votes == 0:
                signal.signal_type = "HOLD"
                signal.confidence = 0.0
                signal.errors.append("No valid indicator signals generated")
                return signal
            
            buy_pct = signal_votes.get('BUY', 0) / total_votes * 100
            sell_pct = signal_votes.get('SELL', 0) / total_votes * 100
            
            if buy_pct > sell_pct and buy_pct >= 40:
                signal.signal_type = "BUY"
                signal.confidence = buy_pct
                signal.formulas_used.extend(['SMA', 'EMA', 'RSI', 'MACD'])
            elif sell_pct > buy_pct and sell_pct >= 40:
                signal.signal_type = "SELL"
                signal.confidence = sell_pct
                signal.formulas_used.extend(['SMA', 'EMA', 'RSI', 'MACD'])
            else:
                signal.signal_type = "HOLD"
                signal.confidence = 0.0
                signal.formulas_used.append('INCONCLUSIVE')
            
            atr = indicator_analysis.get('atr', current_price * 0.02)  
            support = indicator_analysis.get('support', current_price * 0.95)
            resistance = indicator_analysis.get('resistance', current_price * 1.05)
            
            if signal.signal_type == "BUY":
                signal.entry_price = current_price
                signal.stop_loss = support
                signal.target_1 = resistance
                signal.target_2 = current_price + (resistance - current_price) * 1.5
                signal.target_3 = current_price + (resistance - current_price) * 2.0
            elif signal.signal_type == "SELL":
                signal.entry_price = current_price
                signal.stop_loss = resistance
                signal.target_1 = support
                signal.target_2 = current_price - (current_price - support) * 1.5
                signal.target_3 = current_price - (current_price - support) * 2.0
            
            rules_assessment = SeniorTraderRulesEngine.validate_signal_setup(
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                target_1=signal.target_1,
                target_2=signal.target_2,
                current_price=current_price,
                capital=capital,
                signal_type=signal.signal_type
            )
            
            signal.errors.extend(rules_assessment.violations)
            signal.warnings.extend(rules_assessment.warnings)
            signal.risk_reward_ratio = abs(signal.target_1 - signal.entry_price) / abs(signal.entry_price - signal.stop_loss) if signal.stop_loss != signal.entry_price else 0
            
            if quality_report.confidence_penalty > 0:
                signal.confidence_penalties['data_freshness'] = quality_report.confidence_penalty
            
            if signal.data_quality != DataQualityLevel.PRISTINE:
                freshness_penalty = quality_report.confidence_penalty
                signal.confidence *= (1 - freshness_penalty / 100)
            
            signal.is_valid = len(signal.errors) == 0 and signal.confidence > 0
            signal.is_executable = signal.is_valid and market_status.is_trading_allowed
            
            signal.confidence_reasons.append(f"Indicator consensus: {buy_pct:.0f}% BUY, {sell_pct:.0f}% SELL")
            signal.confidence_reasons.append(f"Data quality: {quality_report.level.value}")
            signal.confidence_reasons.append(f"Risk/Reward: 1:{signal.risk_reward_ratio:.2f}")
            
            if signal.market_status == MarketState.OPEN:
                signal.valid_until = datetime.now() + timedelta(hours=4)  
            else:
                signal.valid_until = datetime.now() + timedelta(days=1)  
            
            logger.info(f"Signal generated for {symbol}: {signal.signal_type} @ {signal.confidence:.0f}% confidence")
            
            return signal
            
        except Exception as e:
            logger.exception(f"Error generating signal for {symbol}: {e}")
            signal.errors.append(f"Signal generation error: {str(e)}")
            signal.is_valid = False
            signal.confidence = 0.0
            return signal



class UserFacingOutput:
    """
    Convert complex internal analysis to simple, actionable user guidance
    """
    
    @staticmethod
    def simplify_signal(signal: TradingSignal) -> Dict:
        """
        Convert technical signal to user-friendly output
        Hidden complexity, clear action items
        """
        
        if not signal.is_valid or signal.confidence <= 0:
            return {
                'status': 'NO_TRADE',
                'message': '❌ No trade opportunity right now',
                'reason': signal.errors[0] if signal.errors else 'Data not suitable for trading',
                'next_review': 'Check again in 1 hour',
                'confidence': 0,
                'data_quality': signal.data_quality.value
            }
        
        if not signal.is_executable:
            return {
                'status': 'WAITING',
                'message': '⏳ Signal ready but market is closed',
                'action': 'Set reminder for next market open',
                'signal': signal.signal_type,
                'confidence': round(signal.confidence, 0),
                'entry_price': signal.entry_price,
                'target_price': signal.target_1,
                'stop_loss': signal.stop_loss,
                'data_quality': signal.data_quality.value
            }
        
        if signal.signal_type == "HOLD":
            return {
                'status': 'WAITING',
                'message': '⏸ Waiting for clearer signal',
                'reason': 'Mixed market signals, insufficient conviction',
                'confidence': round(signal.confidence, 0),
                'recommendation': 'Wait for trend clarity'
            }
        
        if signal.signal_type == "BUY":
            action_verb = "BUY"
            icon = "📈"
        else:
            action_verb = "SELL"
            icon = "📉"
        
        confidence_level = "HIGH" if signal.confidence >= 75 else "MEDIUM" if signal.confidence >= 50 else "LOW"
        
        return {
            'status': 'READY',
            'message': f'{icon} {action_verb} Signal - {confidence_level} Confidence ({signal.confidence:.0f}%)',
            'action': f'{action_verb.lower().capitalize()} at ₹{signal.entry_price:.2f}',
            'target': f'Target: ₹{signal.target_1:.2f} ({((signal.target_1 - signal.entry_price) / signal.entry_price * 100):.1f}%)',
            'stop': f'Stop Loss: ₹{signal.stop_loss:.2f}',
            'risk_reward': f'Risk/Reward: 1:{signal.risk_reward_ratio:.2f}',
            'market_status': signal.data_type,
            'execution_timing': 'IMMEDIATE' if signal.market_status == MarketState.OPEN else 'ON_NEXT_OPEN',
            'confidence_reasons': signal.confidence_reasons,
            'warnings': signal.warnings if signal.warnings else None
        }


class AITradingSystem:
    """
    Master orchestrator for the complete AI trading system
    Integrates data validation, market awareness, trading logic, and signal generation
    """
    
    @staticmethod
    def process_trade_request(
        symbol: str,
        capital: float,
        trader_type: str = "SWING",
        market_data: Dict = None
    ) -> Dict:
        """
        Complete processing pipeline
        Input: Stock symbol, capital, trader type, market data
        Output: Clear, reliable trading guidance
        """
        
        try:
            is_valid_symbol, symbol_error = DataIntakeEngine.validate_symbol(symbol)
            if not is_valid_symbol:
                return {
                    'status': 'ERROR',
                    'message': f'Invalid symbol: {symbol_error}',
                    'confidence': 0
                }
            
            market_status = MarketStateDetector.get_market_status()
            
            if not market_data or 'prices' not in market_data:
                return {
                    'status': 'ERROR',
                    'message': 'No market data provided',
                    'confidence': 0
                }
            
            is_valid_data, errors, prices, volumes, highs, lows = \
                DataIntakeEngine.validate_ohlc_series(
                    market_data.get('prices', []),
                    market_data.get('volumes', []),
                    market_data.get('highs', []),
                    market_data.get('lows', [])
                )
            
            if not is_valid_data:
                return {
                    'status': 'ERROR',
                    'message': f'Data quality issues: {errors[0]}',
                    'confidence': 0,
                    'details': errors
                }
            
            signal = SignalGenerationEngine.generate_signal(
                symbol=symbol,
                prices=prices,
                volumes=volumes,
                highs=highs,
                lows=lows,
                current_price=market_data.get('current_price', prices[-1]),
                capital=capital,
                trader_type=trader_type,
                indicator_analysis=market_data.get('indicators', {}),
                market_data_age_minutes=market_data.get('age_minutes', 0)
            )
            
            user_output = UserFacingOutput.simplify_signal(signal)
            
            user_output['technical'] = signal.to_dict()
            
            return user_output
            
        except Exception as e:
            logger.exception(f"Error processing trade request for {symbol}: {e}")
            return {
                'status': 'ERROR',
                'message': 'System error while processing request',
                'confidence': 0
            }
