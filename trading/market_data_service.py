"""
Real-time Market Data Service
Fetches live/delayed market data from free sources
Handles market hours, holidays, and data caching
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pytz
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# India Standard Time
IST = pytz.timezone('Asia/Kolkata')

# Market hours (IST)
MARKET_HOURS = {
    'open': 9,
    'open_minute': 15,
    'close': 15,
    'close_minute': 30
}

# National Holidays - India 2026
HOLIDAYS_2026 = [
    "2026-01-26",  # Republic Day
    "2026-03-25",  # Holi
    "2026-04-14",  # Ambedkar Jayanti
    "2026-04-17",  # Good Friday
    "2026-08-15",  # Independence Day
    "2026-09-02",  # Janmashtami
    "2026-10-02",  # Gandhi Jayanti
    "2026-10-25",  # Diwali
    "2026-11-01",  # Diwali (day 2)
    "2026-12-25",  # Christmas
]


class MarketCalendar:
    """Manage market calendar, hours, and holidays"""
    
    @staticmethod
    def is_market_open_now() -> Tuple[bool, str]:
        """
        Check if market is open now
        Returns: (is_open: bool, status: str)
        """
        now = datetime.now(IST)
        date_str = now.strftime("%Y-%m-%d")
        
        # Check if holiday
        if date_str in HOLIDAYS_2026:
            return False, "HOLIDAY"
        
        # Check if weekend
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False, "WEEKEND"
        
        # Check market hours
        market_open_time = now.replace(
            hour=MARKET_HOURS['open'],
            minute=MARKET_HOURS['open_minute'],
            second=0
        )
        market_close_time = now.replace(
            hour=MARKET_HOURS['close'],
            minute=MARKET_HOURS['close_minute'],
            second=0
        )
        
        if market_open_time <= now <= market_close_time:
            return True, "OPEN"
        elif now < market_open_time:
            return False, "PRE_MARKET"
        else:
            return False, "CLOSED"
    
    @staticmethod
    def get_last_market_close_time() -> datetime:
        """Get the time of last market close"""
        now = datetime.now(IST)
        
        # If market is open now, last close was yesterday or earlier
        is_open, status = MarketCalendar.is_market_open_now()
        
        if is_open:
            # Market is open, last close was today at 3:30 PM
            last_close = now.replace(
                hour=MARKET_HOURS['close'],
                minute=MARKET_HOURS['close_minute'],
                second=0
            )
        else:
            # Market is closed
            # Go back to yesterday and get close time
            yesterday = now - timedelta(days=1)
            
            # Check if yesterday was a market day
            attempts = 0
            while attempts < 10:
                if yesterday.weekday() < 5:  # Weekday
                    date_str = yesterday.strftime("%Y-%m-%d")
                    if date_str not in HOLIDAYS_2026:
                        last_close = yesterday.replace(
                            hour=MARKET_HOURS['close'],
                            minute=MARKET_HOURS['close_minute'],
                            second=0
                        )
                        break
                
                yesterday -= timedelta(days=1)
                attempts += 1
            else:
                # Fallback: today at close time (even if market not open)
                last_close = now.replace(
                    hour=MARKET_HOURS['close'],
                    minute=MARKET_HOURS['close_minute'],
                    second=0
                )
        
        return last_close
    
    @staticmethod
    def get_next_market_open_time() -> datetime:
        """Get the time of next market open"""
        now = datetime.now(IST)
        next_day = now + timedelta(days=1)
        
        # Find next market open day
        attempts = 0
        while attempts < 10:
            if next_day.weekday() < 5:  # Weekday
                date_str = next_day.strftime("%Y-%m-%d")
                if date_str not in HOLIDAYS_2026:
                    next_open = next_day.replace(
                        hour=MARKET_HOURS['open'],
                        minute=MARKET_HOURS['open_minute'],
                        second=0
                    )
                    return next_open
            
            next_day += timedelta(days=1)
            attempts += 1
        
        # Fallback
        return now + timedelta(days=1)


class MockMarketData:
    """Mock market data generator for testing when real data unavailable"""
    
    @staticmethod
    def get_mock_data(symbol: str, days: int = 60) -> Dict:
        """Generate realistic mock OHLCV data"""
        import random
        
        data = []
        price = 100.0
        
        for i in range(days):
            date = (datetime.now(IST) - timedelta(days=days - i)).strftime("%Y-%m-%d")
            
            # Generate realistic price movements
            change = random.uniform(-2, 2)
            open_price = price
            high_price = price * (1 + random.uniform(0, 1.5) / 100)
            low_price = price * (1 - random.uniform(0, 1.5) / 100)
            close_price = price * (1 + change / 100)
            volume = random.randint(500000, 5000000)
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
            })
            
            price = close_price
        
        return {
            'symbol': symbol,
            'data': data,
            'source': 'MOCK',
            'timestamp': datetime.now(IST).isoformat(),
        }


class RealMarketDataFetcher:
    """Fetch real market data from free APIs"""
    
    # Using Alpha Vantage as free data source
    # Note: In production, use multiple sources or paid APIs
    ALPHA_VANTAGE_KEY = "demo"  # Free tier key
    
    @staticmethod
    def fetch_from_alpha_vantage(symbol: str, interval: str = "daily") -> Optional[Dict]:
        """
        Fetch data from Alpha Vantage API
        Note: Free tier has rate limits (5 requests/min, 100/day)
        """
        try:
            # Map Indian stock symbols to valid formats if needed
            stock_symbol = symbol
            
            if interval == "daily":
                url = f"https://www.alphavantage.co/query"
                params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": stock_symbol,
                    "apikey": RealMarketDataFetcher.ALPHA_VANTAGE_KEY,
                    "outputsize": "full"
                }
            else:
                url = f"https://www.alphavantage.co/query"
                params = {
                    "function": "TIME_SERIES_INTRADAY",
                    "symbol": stock_symbol,
                    "interval": interval,
                    "apikey": RealMarketDataFetcher.ALPHA_VANTAGE_KEY,
                }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Alpha Vantage returned status {response.status_code}")
                return None
            
            data = response.json()
            
            # Check for errors in response
            if "Error Message" in data or "Note" in data:
                logger.warning(f"Alpha Vantage error: {data.get('Error Message', data.get('Note'))}")
                return None
            
            # Extract time series
            if interval == "daily":
                time_series = data.get("Time Series (Daily)", {})
            else:
                time_series = data.get(f"Time Series ({interval})", {})
            
            if not time_series:
                logger.warning("No time series data in response")
                return None
            
            # Convert to standard format
            ohlcv_data = []
            for date_str in sorted(time_series.keys(), reverse=True)[:60]:
                ohlc = time_series[date_str]
                ohlcv_data.append({
                    'date': date_str,
                    'open': float(ohlc['1. open']),
                    'high': float(ohlc['2. high']),
                    'low': float(ohlc['3. low']),
                    'close': float(ohlc['4. close']),
                    'volume': int(ohlc.get('5. volume', 0)),
                })
            
            return {
                'symbol': symbol,
                'data': list(reversed(ohlcv_data)),  # Reverse to ascending order
                'source': 'ALPHA_VANTAGE',
                'timestamp': datetime.now(IST).isoformat(),
            }
            
        except requests.Timeout:
            logger.error(f"Timeout fetching data for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error fetching from Alpha Vantage: {e}")
            return None
    
    @staticmethod
    def fetch_from_yfinance(symbol: str) -> Optional[Dict]:
        """
        Fetch data using yfinance (requires pip install yfinance)
        Free, no rate limits
        """
        try:
            import yfinance as yf
            
            # For Indian stocks, append .NS or .BO suffix
            if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
                symbol = f"{symbol}.NS"
            
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2mo")
            
            if hist.empty:
                return None
            
            ohlcv_data = []
            for date, row in hist.iterrows():
                ohlcv_data.append({
                    'date': date.strftime("%Y-%m-%d"),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                })
            
            return {
                'symbol': symbol.replace('.NS', ''),
                'data': ohlcv_data,
                'source': 'YFINANCE',
                'timestamp': datetime.now(IST).isoformat(),
            }
            
        except ImportError:
            logger.warning("yfinance not installed")
            return None
        except Exception as e:
            logger.error(f"Error fetching from yfinance: {e}")
            return None


class MarketDataCache:
    """Cache market data with TTL"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = 300  # 5 minutes cache TTL
    
    def get(self, key: str) -> Optional[Dict]:
        """Get data from cache if not expired"""
        if key not in self.cache:
            return None
        
        data, timestamp = self.cache[key]
        
        # Check if expired
        if datetime.now(IST).timestamp() - timestamp > self.ttl:
            del self.cache[key]
            return None
        
        return data
    
    def set(self, key: str, data: Dict):
        """Set data in cache with current timestamp"""
        self.cache[key] = (data, datetime.now(IST).timestamp())
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}


# Global cache instance
_market_data_cache = MarketDataCache()


class MarketDataService:
    """Main service for getting market data"""
    
    @staticmethod
    def get_market_data(symbol: str, use_cache: bool = True) -> Dict:
        """
        Get market data for a symbol
        Tries real data first, falls back to mock data
        """
        cache_key = f"market_data_{symbol}"
        
        # Try cache first
        if use_cache:
            cached = _market_data_cache.get(cache_key)
            if cached:
                cached['from_cache'] = True
                return cached
        
        # Try real data sources
        logger.info(f"Fetching market data for {symbol}")
        
        # Try Alpha Vantage first
        data = RealMarketDataFetcher.fetch_from_alpha_vantage(symbol)
        if data:
            _market_data_cache.set(cache_key, data)
            return data
        
        # Try yfinance
        data = RealMarketDataFetcher.fetch_from_yfinance(symbol)
        if data:
            _market_data_cache.set(cache_key, data)
            return data
        
        # Fallback to mock data
        logger.warning(f"Using mock data for {symbol}")
        data = MockMarketData.get_mock_data(symbol)
        _market_data_cache.set(cache_key, data)
        return data
    
    @staticmethod
    def get_market_status() -> Dict:
        """Get current market status"""
        is_open, status = MarketCalendar.is_market_open_now()
        now = datetime.now(IST)
        
        market_info = {
            'is_open': is_open,
            'status': status,
            'current_time': now.isoformat(),
            'timezone': 'IST',
        }
        
        if status == "OPEN":
            market_info['next_close_time'] = MarketCalendar.get_last_market_close_time().isoformat()
        else:
            market_info['next_open_time'] = MarketCalendar.get_next_market_open_time().isoformat()
        
        return market_info
    
    @staticmethod
    def validate_data_for_analysis(data: Dict) -> Tuple[bool, str]:
        """
        Validate market data before analysis
        Returns: (is_valid: bool, reason: str)
        """
        if not data or 'data' not in data:
            return False, "No data available"
        
        if len(data['data']) < 20:
            return False, "Insufficient data points (need at least 20)"
        
        # Check if data is too old
        if 'source' in data and data['source'] == 'MOCK':
            return True, "Using simulated data"
        
        # Validate OHLC structure
        latest = data['data'][-1]
        required_fields = ['open', 'high', 'low', 'close', 'volume']
        
        for field in required_fields:
            if field not in latest or latest[field] is None:
                return False, f"Missing or invalid {field} data"
        
        return True, "Data valid"
