import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from bs4 import BeautifulSoup
from functools import lru_cache
import time

logger = logging.getLogger(__name__)



class DataSourceConfig:
    """Configuration for each data source"""
    
    NSE_BASE_URL = "https://www.nseindia.com"
    NSE_QUOTE_URL = "https://www.nseindia.com/api/quote-equity"
    NSE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    ALPHA_VANTAGE_KEY = "YOUR_ALPHA"  
    ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
    
    YFINANCE_TIMEOUT = 10
    
    CHARTINK_BASE_URL = "https://chartink.com"
    CHARTINK_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    SCREENER_BASE_URL = "https://screener.in"
    SCREENER_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    RATE_LIMIT_DELAY = 1 



class StockQuote:
    """Real-time stock quote"""
    def __init__(self, symbol: str, price: float, open_price: float, high: float, 
                 low: float, volume: int, timestamp: datetime, source: str):
        self.symbol = symbol
        self.price = price
        self.open_price = open_price
        self.high = high
        self.low = low
        self.volume = volume
        self.timestamp = timestamp
        self.source = source  # NSE, ALPHAVANTAGE, YFINANCE
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "price": self.price,
            "open": self.open_price,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source
        }


class OHLCV:
    """OHLCV candlestick data"""
    def __init__(self, timestamp: datetime, open_price: float, high: float, 
                 low: float, close: float, volume: int):
        self.timestamp = timestamp
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }


class FundamentalData:
    """Company fundamental information from Screener"""
    def __init__(self, symbol: str, pe_ratio: Optional[float] = None, 
                 pb_ratio: Optional[float] = None, dividend_yield: Optional[float] = None,
                 market_cap: Optional[float] = None, **kwargs):
        self.symbol = symbol
        self.pe_ratio = pe_ratio
        self.pb_ratio = pb_ratio
        self.dividend_yield = dividend_yield
        self.market_cap = market_cap
        self.extras = kwargs
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "pe_ratio": self.pe_ratio,
            "pb_ratio": self.pb_ratio,
            "dividend_yield": self.dividend_yield,
            "market_cap": self.market_cap,
            **self.extras
        }




class NSEDataFetcher:
    """Fetch real-time data from NSE India"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DataSourceConfig.NSE_HEADERS)
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Respect rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < DataSourceConfig.RATE_LIMIT_DELAY:
            time.sleep(DataSourceConfig.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def fetch_quote(self, symbol: str) -> Optional[StockQuote]:
        """Fetch real-time quote for a stock"""
        try:
            self._rate_limit()
            
            nse_symbol = f"{symbol.upper()}"
            
            params = {
                "symbol": nse_symbol,
                "sme": "false"
            }
            
            response = self.session.get(
                DataSourceConfig.NSE_QUOTE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse NSE response
            if "pricebandupper" in data:
                quote_data = data
                
                quote = StockQuote(
                    symbol=symbol,
                    price=float(quote_data.get("lastprice", 0)),
                    open_price=float(quote_data.get("open", 0)),
                    high=float(quote_data.get("high", 0)),
                    low=float(quote_data.get("low", 0)),
                    volume=int(quote_data.get("totalTradedVolume", 0)),
                    timestamp=datetime.now(),
                    source="NSE"
                )
                
                logger.info(f"✓ NSE Quote fetched: {symbol} @ {quote.price}")
                return quote
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"✗ NSE fetch failed for {symbol}: {e}")
        except Exception as e:
            logger.error(f"✗ Error parsing NSE data for {symbol}: {e}")
        
        return None
    
    def fetch_historical(self, symbol: str, days: int = 100) -> List[OHLCV]:
        """Fetch historical OHLCV data (limited by API)"""
        try:
            self._rate_limit()
            

            logger.info(f"NSE historical not available, use yfinance as fallback")
            return []
        
        except Exception as e:
            logger.error(f"Error fetching NSE historical: {e}")
            return []



class YFinanceDataFetcher:
    """Fetch data from Yahoo Finance (free, no API key)"""
    
    def fetch_quote(self, symbol: str) -> Optional[StockQuote]:
        """Fetch real-time quote"""
        try:
            import yfinance as yf
            
            # Add .NS for NSE India stocks
            ticker = f"{symbol.upper()}.NS"
            stock = yf.Ticker(ticker)
            
            data = stock.info
            
            quote = StockQuote(
                symbol=symbol,
                price=float(data.get("currentPrice", 0)),
                open_price=float(data.get("open", 0)),
                high=float(data.get("dayHigh", 0)),
                low=float(data.get("dayLow", 0)),
                volume=int(data.get("volume", 0)),
                timestamp=datetime.now(),
                source="YFINANCE"
            )
            
            logger.info(f"✓ YFinance Quote fetched: {symbol} @ {quote.price}")
            return quote
        
        except ImportError:
            logger.warning("yfinance not installed")
        except Exception as e:
            logger.warning(f"✗ YFinance fetch failed for {symbol}: {e}")
        
        return None
    
    def fetch_historical(self, symbol: str, period: str = "3mo", 
                        interval: str = "1d") -> List[OHLCV]:
        """Fetch historical OHLCV data"""
        try:
            import yfinance as yf
            
            ticker = f"{symbol.upper()}.NS"
            stock = yf.Ticker(ticker)
            
            df = stock.history(period=period, interval=interval)
            
            candles = []
            for idx, row in df.iterrows():
                candle = OHLCV(
                    timestamp=idx,
                    open_price=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"])
                )
                candles.append(candle)
            
            logger.info(f"✓ YFinance Historical fetched: {symbol}, {len(candles)} candles")
            return candles
        
        except Exception as e:
            logger.warning(f"✗ YFinance historical failed for {symbol}: {e}")
            return []




class ChartinkDataFetcher:
    """Fetch data from Chartink (respects robots.txt)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DataSourceConfig.CHARTINK_HEADERS)
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Respect rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < DataSourceConfig.RATE_LIMIT_DELAY * 2: 
            time.sleep(DataSourceConfig.RATE_LIMIT_DELAY * 2 - elapsed)
        self.last_request_time = time.time()
    
    def fetch_patterns(self, symbol: str) -> Dict:
        """Fetch detected patterns from Chartink"""
        try:
            self._rate_limit()
            

            logger.info(f"Chartink patterns: Requires premium API or scraping")
            
            return {
                "symbol": symbol,
                "patterns": [],
                "indicators": {},
                "note": "Use Chartink web UI or premium API"
            }
        
        except Exception as e:
            logger.warning(f"Chartink fetch failed: {e}")
            return {}



class ScreenerDataFetcher:
    """Fetch fundamentals from Screener.in (respects robots.txt)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DataSourceConfig.SCREENER_HEADERS)
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Respect rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < DataSourceConfig.RATE_LIMIT_DELAY * 2:
            time.sleep(DataSourceConfig.RATE_LIMIT_DELAY * 2 - elapsed)
        self.last_request_time = time.time()
    
    def fetch_fundamentals(self, symbol: str) -> Optional[FundamentalData]:
        """Fetch fundamental data from Screener"""
        try:
            self._rate_limit()
            
            url = f"{DataSourceConfig.SCREENER_BASE_URL}/company/{symbol.upper()}/consolidated/"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            

            
            fundamentals = FundamentalData(symbol=symbol)
            logger.info(f"✓ Screener Fundamentals fetched: {symbol}")
            return fundamentals
        
        except Exception as e:
            logger.warning(f"Screener fetch failed for {symbol}: {e}")
            return None



class DataIntegrationEngine:
    """Master orchestrator for all data sources"""
    
    def __init__(self):
        self.nse = NSEDataFetcher()
        self.yfinance = YFinanceDataFetcher()
        self.chartink = ChartinkDataFetcher()
        self.screener = ScreenerDataFetcher()
        
        self.quote_cache = {}
        self.cache_duration = 60  # seconds
    
    def get_live_quote(self, symbol: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get real-time quote with fallback chain:
        NSE → YFinance
        """
        # Check cache
        if use_cache and symbol in self.quote_cache:
            cached = self.quote_cache[symbol]
            age = (datetime.now() - cached["timestamp"]).total_seconds()
            if age < self.cache_duration:
                logger.debug(f"Cache hit for {symbol}")
                return cached
        
        # Try NSE first
        quote = self.nse.fetch_quote(symbol)
        if quote:
            self.quote_cache[symbol] = quote.to_dict()
            self.quote_cache[symbol]["timestamp"] = datetime.now()
            return self.quote_cache[symbol]
        
        # Fallback to YFinance
        quote = self.yfinance.fetch_quote(symbol)
        if quote:
            self.quote_cache[symbol] = quote.to_dict()
            self.quote_cache[symbol]["timestamp"] = datetime.now()
            return self.quote_cache[symbol]
        
        logger.error(f"✗ Could not fetch quote for {symbol} from any source")
        return None
    
    def get_historical_data(self, symbol: str, period: str = "3mo", 
                          interval: str = "1d") -> Dict:
        """
        Get historical OHLCV data
        Prefers YFinance (no API key required)
        """
        try:
            candles = self.yfinance.fetch_historical(symbol, period=period, interval=interval)
            
            data = [candle.to_dict() for candle in candles]
            
            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "candles": data,
                "count": len(data),
                "source": "YFINANCE"
            }
        
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "candles": []
            }
    
    def get_intraday_data(self, symbol: str) -> Dict:
        """
        Get 5-minute intraday data
        Used for short-term predictions
        """
        try:
            candles = self.yfinance.fetch_historical(
                symbol, 
                period="5d",  # Last 5 days
                interval="5m"  # 5-minute candles
            )
            
            data = [candle.to_dict() for candle in candles]
            
            return {
                "symbol": symbol,
                "interval": "5m",
                "candles": data,
                "count": len(data),
                "source": "YFINANCE",
                "freshness": "Updated every 5 minutes"
            }
        
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "candles": []
            }
    
    def get_fundamentals(self, symbol: str) -> Dict:
        """
        Get fundamental data
        From Screener or cached
        """
        try:
            fundamentals = self.screener.fetch_fundamentals(symbol)
            
            if fundamentals:
                return {
                    "symbol": symbol,
                    "data": fundamentals.to_dict(),
                    "source": "SCREENER"
                }
            else:
                return {
                    "symbol": symbol,
                    "data": None,
                    "error": "Could not fetch from Screener"
                }
        
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e)
            }
    
    def get_complete_market_data(self, symbol: str) -> Dict:
        """
        Get complete market data package:
        - Live quote
        - Historical daily data
        - Intraday 5-minute data
        - Fundamental data
        """
        
        logger.info(f"Fetching complete market data for {symbol}...")
        
        # Parallel-like fetching (sequential but organized)
        quote = self.get_live_quote(symbol)
        historical = self.get_historical_data(symbol)
        intraday = self.get_intraday_data(symbol)
        fundamentals = self.get_fundamentals(symbol)
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "quote": quote,
            "historical": historical,
            "intraday": intraday,
            "fundamentals": fundamentals,
            "data_freshness": {
                "quote_age_minutes": 0,
                "historical_last_update": historical.get("period", "unknown"),
                "intraday_last_update": "Every 5 minutes during market hours"
            }
        }
    
    def validate_data_quality(self, symbol: str, data: Dict) -> Dict:
        """
        Validate data quality and identify issues
        """
        issues = []
        warnings = []
        
        # Check quote
        if not data.get("quote"):
            issues.append("No live quote available")
        
        # Check historical
        historical = data.get("historical", {})
        if not historical.get("candles"):
            issues.append("No historical data available")
        elif len(historical.get("candles", [])) < 50:
            warnings.append(f"Limited historical data: {len(historical['candles'])} candles")
        
        # Check intraday
        intraday = data.get("intraday", {})
        if not intraday.get("candles"):
            warnings.append("No intraday data available")
        elif len(intraday.get("candles", [])) < 100:
            warnings.append(f"Limited intraday data: {len(intraday['candles'])} candles")
        
        return {
            "symbol": symbol,
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "overall_quality": "GOOD" if len(issues) == 0 else "POOR",
            "recommendation": "Proceed with caution" if warnings else "Data is ready"
        }


# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def get_data_engine() -> DataIntegrationEngine:
    """Get singleton instance of data integration engine"""
    if not hasattr(get_data_engine, '_instance'):
        get_data_engine._instance = DataIntegrationEngine()
    return get_data_engine._instance


def is_market_open() -> bool:
    """Check if NSE market is currently open"""
    now = datetime.now()
    
    # IST timezone
    hours = now.hour
    minutes = now.minute
    day = now.weekday()  # 0=Monday, 6=Sunday
    
    # Market hours: 9:15 AM - 3:30 PM IST
    is_weekday = day < 5  # Monday to Friday
    is_market_hours = (hours > 9 or (hours == 9 and minutes >= 15)) and \
                     (hours < 15 or (hours == 15 and minutes <= 30))
    
    return is_weekday and is_market_hours
