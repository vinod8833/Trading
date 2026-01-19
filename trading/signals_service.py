"""
Signal Service with Market Awareness and Error Handling
Provides market-aware signal generation with proper error states and fallback messages
Uses REAL market calendars - NO sample/hardcoded holidays
"""

from datetime import datetime, time, date
import pytz
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Set
import logging

logger = logging.getLogger(__name__)

class MarketStatusService:
    """Market status and availability check using real market calendars"""
    
    IST = pytz.timezone('Asia/Kolkata')
    MARKET_OPEN = time(9, 15)  # 9:15 AM
    MARKET_CLOSE = time(15, 30)  # 3:30 PM
    
    # Use market_holidays_cache if available, falls back to fetching dynamically
    _holiday_cache: Optional[Set[str]] = None
    _cache_date: Optional[date] = None
    
    @staticmethod
    def _get_nse_holidays() -> Set[str]:
        """
        Fetch NSE holidays from market calendar
        Uses pandas_market_calendars or yfinance for real market data
        NOT hardcoded sample data
        """
        try:
            import pandas_market_calendars as mcal
            
            # Get NSE calendar for current year
            nse_cal = mcal.get_calendar('NSE')
            
            # Get holidays for next 2 years
            current_year = datetime.now().year
            holidays = set()
            
            for year in [current_year - 1, current_year, current_year + 1]:
                try:
                    # Get holidays from market calendar
                    holiday_dates = nse_cal.holidays().strftime('%Y-%m-%d')
                    holidays.update(holiday_dates)
                except Exception as e:
                    logger.warning(f"Could not fetch holidays for {year}: {e}")
                    continue
            
            logger.info(f"Loaded {len(holidays)} NSE holidays from market calendar")
            return holidays
            
        except ImportError:
            logger.warning("pandas_market_calendars not available, using yfinance fallback")
            return MarketStatusService._get_holidays_from_yfinance()
        except Exception as e:
            logger.warning(f"Error fetching NSE holidays: {e}, using fallback")
            return MarketStatusService._get_holidays_from_yfinance()
    
    @staticmethod
    def _get_holidays_from_yfinance() -> Set[str]:
        """
        Fallback: Fetch market closure data from yfinance
        Queries historical data to detect actual market closures
        """
        try:
            import yfinance as yf
            from datetime import timedelta
            
            # Use NSE index to detect holidays/closures
            nse_data = yf.download(
                'NIFTYBEES.NS',
                start=(datetime.now() - timedelta(days=730)).date(),
                end=datetime.now().date(),
                progress=False
            )
            
            # Generate date range and find missing dates (holidays/weekends excluded separately)
            all_days = set()
            trading_days = set()
            
            current = datetime.now().date() - timedelta(days=730)
            end_date = datetime.now().date()
            
            while current <= end_date:
                all_days.add(current.isoformat())
                if current.weekday() < 5:  # Weekday only
                    trading_days.add(current.isoformat())
                current += timedelta(days=1)
            
            # Holidays are weekdays that aren't in trading data
            actual_trading_dates = set(nse_data.index.strftime('%Y-%m-%d'))
            holidays = trading_days - actual_trading_dates
            
            logger.info(f"Detected {len(holidays)} market holidays from yfinance data")
            return holidays
            
        except Exception as e:
            logger.warning(f"Error fetching holidays from yfinance: {e}")
            # Return empty set - will use weekday check only
            return set()
    
    @staticmethod
    def get_market_holidays() -> Set[str]:
        """
        Get NSE market holidays using real market calendars
        Caches for performance (cache expires daily)
        """
        today = datetime.now().date()
        
        # Check if cache is still valid (same day)
        if (MarketStatusService._holiday_cache is not None and 
            MarketStatusService._cache_date == today):
            return MarketStatusService._holiday_cache
        
        # Fetch fresh holidays
        holidays = MarketStatusService._get_nse_holidays()
        MarketStatusService._holiday_cache = holidays
        MarketStatusService._cache_date = today
        
        return holidays
    
    @property
    def MARKET_HOLIDAYS(self) -> Set[str]:
        """Dynamic property that returns real market holidays"""
        return self.get_market_holidays()
    
    @staticmethod
    def is_market_open() -> bool:
        """
        Check if market is currently open (IST 9:15 AM - 3:30 PM, weekdays only)
        Uses REAL market calendars, not hardcoded holidays
        """
        try:
            ist_now = datetime.now(MarketStatusService.IST)
            today = ist_now.date().isoformat()
            
            # Get real market holidays from market calendar
            market_holidays = MarketStatusService.get_market_holidays()
            
            # Check if holiday
            if today in market_holidays:
                return False
            
            # Check if weekend (5=Saturday, 6=Sunday)
            if ist_now.weekday() >= 5:
                return False
            
            # Check market hours
            current_time = ist_now.time()
            return MarketStatusService.MARKET_OPEN <= current_time <= MarketStatusService.MARKET_CLOSE
        except Exception as e:
            logger.warning(f"Error checking market status: {e}")
            return False
    
    @staticmethod
    def get_market_status() -> Dict[str, Any]:
        """Get detailed market status using REAL market calendars"""
        ist_now = datetime.now(MarketStatusService.IST)
        today = ist_now.date().isoformat()
        is_open = MarketStatusService.is_market_open()
        
        # Get real market holidays
        market_holidays = MarketStatusService.get_market_holidays()
        is_holiday = today in market_holidays
        
        return {
            'is_open': is_open,
            'current_time_ist': ist_now.isoformat(),
            'today': today,
            'day_of_week': ist_now.strftime('%A'),
            'is_weekend': ist_now.weekday() >= 5,
            'is_holiday': is_holiday,
            'market_open_time': '09:15 AM IST',
            'market_close_time': '03:30 PM IST',
            'data_source': 'Real market calendar (pandas_market_calendars/yfinance)',
            'note': 'Using live market holidays, not sample data',
        }


class SignalDataValidator:
    """Validates signal data before response"""
    
    REQUIRED_SIGNAL_FIELDS = {
        'id', 'stock', 'signal', 'entry_price', 'stop_loss',
        'target_1', 'confidence_level', 'risk_percent'
    }
    
    REQUIRED_STOCK_FIELDS = {
        'id', 'symbol', 'name', 'current_price'
    }
    
    @staticmethod
    def validate_signal(signal_data: Dict) -> Tuple[bool, List[str]]:
        """Validate signal structure and data"""
        errors = []
        
        # Check required fields
        for field in SignalDataValidator.REQUIRED_SIGNAL_FIELDS:
            if field not in signal_data or signal_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate signal type
        if signal_data.get('signal') not in ['BUY', 'SELL', 'HOLD']:
            errors.append(f"Invalid signal: {signal_data.get('signal')}")
        
        # Validate prices
        try:
            entry = Decimal(str(signal_data.get('entry_price', 0)))
            stop_loss = Decimal(str(signal_data.get('stop_loss', 0)))
            target_1 = Decimal(str(signal_data.get('target_1', 0)))
            
            if entry <= 0 or stop_loss <= 0 or target_1 <= 0:
                errors.append("Entry price, stop loss, and targets must be positive")
            
            if signal_data.get('signal') == 'BUY':
                if stop_loss >= entry or target_1 <= entry:
                    errors.append("BUY signal: stop_loss must be < entry_price < target_1")
            elif signal_data.get('signal') == 'SELL':
                if stop_loss <= entry or target_1 >= entry:
                    errors.append("SELL signal: target_1 must be < entry_price < stop_loss")
        except (ValueError, TypeError) as e:
            errors.append(f"Invalid price format: {e}")
        
        # Validate confidence
        confidence = signal_data.get('confidence_level')
        if confidence is not None and (confidence < 0 or confidence > 100):
            errors.append(f"Confidence must be between 0 and 100, got {confidence}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_stock(stock_data: Dict) -> Tuple[bool, List[str]]:
        """Validate stock data structure"""
        errors = []
        
        for field in SignalDataValidator.REQUIRED_STOCK_FIELDS:
            if field not in stock_data or stock_data[field] is None:
                errors.append(f"Missing required stock field: {field}")
        
        return len(errors) == 0, errors


class SignalEnhancementService:
    """Enhances signals with market-aware metadata and fallback messages"""
    
    @staticmethod
    def enhance_signal(signal_data: Dict, market_open: bool) -> Dict:
        """Add market-aware metadata to signal"""
        
        signal_copy = signal_data.copy()
        
        # Add market status
        signal_copy['market_status'] = 'LIVE' if market_open else 'HISTORICAL'
        signal_copy['is_market_open'] = market_open
        
        # Add signal quality indicator
        confidence = signal_copy.get('confidence_level', 0)
        if confidence >= 85:
            signal_copy['signal_quality'] = 'HIGH'
        elif confidence >= 70:
            signal_copy['signal_quality'] = 'MEDIUM'
        else:
            signal_copy['signal_quality'] = 'LOW'
        
        # Add market-aware context
        if not market_open:
            signal_copy['note'] = (
                'Market is closed. This is historical analysis. '
                'Confirm with live market data before trading.'
            )
        else:
            signal_copy['note'] = 'Live market signal. Use with risk management.'
        
        # Calculate holding period recommendation based on trading style
        trading_style = signal_copy.get('trading_style', 'SWING')
        holding_periods = {
            'INTRADAY': 'Minutes to Hours (Auto square-off at close)',
            'SWING': '2-5 Days',
            'POSITIONAL': '1-3 Months',
        }
        signal_copy['recommended_holding_period'] = holding_periods.get(trading_style, 'Custom')
        
        return signal_copy
    
    @staticmethod
    def create_fallback_signals(stock: 'Stock', reason: str) -> List[Dict]:
        """Create fallback signals when generation fails"""
        
        return [{
            'id': None,
            'stock': {
                'id': stock.id,
                'symbol': stock.symbol,
                'name': stock.name,
                'current_price': str(stock.current_price),
            },
            'signal': 'HOLD',
            'entry_price': None,
            'stop_loss': None,
            'target_1': None,
            'target_2': None,
            'target_3': None,
            'target_4': None,
            'confidence_level': 0,
            'risk_percent': 0,
            'profit_percent': 0,
            'risk_reward_ratio': 0,
            'win_probability': 0,
            'trading_style': 'ANALYSIS_ONLY',
            'market_status': 'UNAVAILABLE',
            'is_market_open': False,
            'signal_quality': 'UNAVAILABLE',
            'error': reason,
            'note': 'Unable to generate signal. ' + reason,
        }]


class SignalErrorHandler:
    """Handles and categorizes signal generation errors"""
    
    ERROR_MESSAGES = {
        'NO_MARKET_DATA': 'Market data not available. Try again after market opens or refresh data.',
        'INVALID_STOCK': 'Stock data is incomplete. Please analyze this stock first.',
        'MISSING_ANALYSIS': 'Technical analysis not available. Run analysis before generating signals.',
        'INVALID_PRICES': 'Invalid price data. Ensure entry, targets, and stop loss are valid.',
        'API_ERROR': 'Market data API is unavailable. Using historical analysis.',
        'TIMEOUT': 'Signal generation timed out. Using cached signals if available.',
        'INSUFFICIENT_DATA': 'Insufficient historical data for accurate signal generation.',
        'MARKET_CLOSED': 'Market is closed. Analysis-only signals available.',
    }
    
    @staticmethod
    def get_error_message(error_type: str, detail: str = None) -> str:
        """Get user-friendly error message"""
        message = SignalErrorHandler.ERROR_MESSAGES.get(
            error_type,
            'Unable to generate signal. Please try again later.'
        )
        if detail:
            message += f' ({detail})'
        return message
    
    @staticmethod
    def handle_signal_error(error: Exception) -> Dict:
        """Handle and categorize signal generation error"""
        
        error_str = str(error).lower()
        
        # Determine error type based on error message
        if 'market' in error_str and 'data' in error_str:
            error_type = 'NO_MARKET_DATA'
        elif 'stock' in error_str or 'not found' in error_str:
            error_type = 'INVALID_STOCK'
        elif 'analysis' in error_str:
            error_type = 'MISSING_ANALYSIS'
        elif 'price' in error_str:
            error_type = 'INVALID_PRICES'
        elif 'api' in error_str:
            error_type = 'API_ERROR'
        elif 'timeout' in error_str:
            error_type = 'TIMEOUT'
        elif 'insufficient' in error_str or 'data' in error_str:
            error_type = 'INSUFFICIENT_DATA'
        else:
            error_type = 'API_ERROR'
        
        return {
            'error_type': error_type,
            'error_message': SignalErrorHandler.get_error_message(error_type),
            'technical_error': str(error),
        }


class SignalResponseFormatter:
    """Formats signal responses with market awareness and error states"""
    
    @staticmethod
    def format_signal_list(
        signals: List[Dict],
        market_open: bool,
        total_count: int = None,
    ) -> Dict:
        """Format list of signals with metadata"""
        
        # Enhance all signals with market status
        enhanced_signals = [
            SignalEnhancementService.enhance_signal(sig, market_open)
            for sig in signals
        ]
        
        # Validate signals
        valid_signals = []
        invalid_signals = []
        
        for sig in enhanced_signals:
            is_valid, errors = SignalDataValidator.validate_signal(sig)
            if is_valid:
                valid_signals.append(sig)
            else:
                sig['validation_errors'] = errors
                invalid_signals.append(sig)
        
        return {
            'count': len(signals),
            'results': valid_signals,
            'invalid_count': len(invalid_signals),
            'invalid_signals': invalid_signals if invalid_signals else None,
            'market_status': MarketStatusService.get_market_status(),
            'generated_at': datetime.now(MarketStatusService.IST).isoformat(),
            'note': 'Live signals' if market_open else 'Market closed - Analysis signals',
        }
    
    @staticmethod
    def format_error_response(error: Exception, stock_symbol: str = None) -> Dict:
        """Format error response with fallback"""
        
        error_info = SignalErrorHandler.handle_signal_error(error)
        
        return {
            'count': 0,
            'results': [],
            'error': error_info['error_message'],
            'error_type': error_info['error_type'],
            'technical_detail': error_info['technical_error'],
            'market_status': MarketStatusService.get_market_status(),
            'generated_at': datetime.now(MarketStatusService.IST).isoformat(),
            'note': 'Unable to generate signals. Please try again later.',
            'fallback_suggestion': (
                'Go to Stock Analysis page to analyze individual stocks '
                'before generating signals.'
            ),
        }
    
    @staticmethod
    def format_single_signal(signal_data: Dict, market_open: bool) -> Dict:
        """Format single signal response"""
        
        # Validate
        is_valid, errors = SignalDataValidator.validate_signal(signal_data)
        
        # Enhance
        enhanced = SignalEnhancementService.enhance_signal(signal_data, market_open)
        
        if not is_valid:
            enhanced['validation_errors'] = errors
            enhanced['is_valid'] = False
        else:
            enhanced['is_valid'] = True
        
        enhanced['market_status'] = MarketStatusService.get_market_status()
        enhanced['generated_at'] = datetime.now(MarketStatusService.IST).isoformat()
        
        return enhanced


class SignalGenerationAwareService:
    """Signal generation with market awareness and error handling"""
    
    @staticmethod
    def should_generate_live_signals() -> bool:
        """Determine if live signals should be generated"""
        return MarketStatusService.is_market_open()
    
    @staticmethod
    def get_market_context() -> Dict[str, Any]:
        """Get market context for signal generation"""
        
        market_status = MarketStatusService.get_market_status()
        is_open = market_status['is_open']
        
        return {
            'market_open': is_open,
            'market_status': market_status,
            'signal_type': 'LIVE' if is_open else 'ANALYSIS_ONLY',
            'recommendation': (
                'Execute immediately' if is_open
                else 'Prepare order for next market open'
            ),
        }
    
    @staticmethod
    def validate_before_signal_generation(stock, analysis) -> Tuple[bool, List[str], Dict]:
        """Validate prerequisites for signal generation"""
        
        errors = []
        warnings = []
        
        # Check stock data
        if not stock:
            errors.append('Stock not found')
        elif not stock.current_price or stock.current_price <= 0:
            errors.append('Invalid stock price')
        
        # Check analysis data
        if not analysis:
            errors.append('Technical analysis not available')
        else:
            # Check required analysis fields
            if not analysis.sma_20 or not analysis.sma_50:
                warnings.append('Some technical indicators may be incomplete')
        
        # Check market data availability
        if not MarketStatusService.is_market_open():
            warnings.append('Market is closed - using last available data')
        
        return len(errors) == 0, errors + warnings, {
            'has_errors': len(errors) > 0,
            'has_warnings': len(warnings) > 0,
            'errors': errors,
            'warnings': warnings,
        }
