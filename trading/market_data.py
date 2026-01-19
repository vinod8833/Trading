"""
Market Data Fetching Service
Integrates with multiple free and trusted financial data sources:
- yfinance (Yahoo Finance) - Live prices, historical data, fundamentals
- NSE/BSE - Indian stock exchange data
- Public APIs - Economic indicators, news
"""

import requests
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import logging
from decimal import Decimal
import pytz

logger = logging.getLogger(__name__)


class MarketDataFetcher:
    """Fetches market data from multiple reliable sources"""
    
    # Data sources configuration
    SOURCES = {
        'yfinance': 'Yahoo Finance - Live prices, 20+ years history',
        'nse_bhavcopy': 'NSE Bhavcopy - Official Indian stock data',
        'india_vix': 'India VIX - Market volatility index',
    }
    
    NSE_SUFFIX = '.NS'  # NSE suffix for Indian stocks
    BSE_SUFFIX = '.BO'  # BSE suffix for Indian stocks
    
    # Indian holidays (simplified)
    INDIAN_HOLIDAYS = {
        '2024-01-26', '2024-03-08', '2024-03-25', '2024-04-11', '2024-04-17',
        '2024-05-23', '2024-08-15', '2024-08-26', '2024-09-16', '2024-10-02',
        '2024-10-12', '2024-10-31', '2024-11-01', '2024-11-15', '2024-12-25',
        '2025-01-26', '2025-03-14', '2025-04-18', '2025-08-15', '2025-10-02',
    }
    
    NSE_MARKET_HOURS = {
        'open': '09:15',    # 9:15 AM IST
        'close': '15:30',   # 3:30 PM IST
    }
    
    @classmethod
    def get_stock_price(cls, symbol: str, source: str = 'yfinance') -> Optional[Dict]:
        """
        Fetch current stock price and intraday data
        
        Returns: {
            'symbol': 'INFY',
            'price': 1650.50,
            'previous_close': 1645.00,
            'open': 1648.00,
            'high': 1655.00,
            'low': 1640.00,
            'volume': 1500000,
            'timestamp': datetime,
            'market_status': 'OPEN' | 'CLOSED' | 'HOLIDAY',
            'data_freshness': 'LIVE' | 'DELAYED' | 'EOD',
        }
        """
        try:
            # Add NSE suffix if not present
            if '.' not in symbol:
                symbol_with_suffix = symbol + cls.NSE_SUFFIX
            else:
                symbol_with_suffix = symbol
            
            # Fetch using yfinance
            ticker = yf.Ticker(symbol_with_suffix)
            data = ticker.info
            
            # Fetch latest quote
            hist = ticker.history(period='1d')
            
            if hist.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            latest = hist.iloc[-1]
            
            market_status = cls._get_market_status()
            data_freshness = 'LIVE' if market_status == 'OPEN' else 'EOD'
            
            return {
                'symbol': symbol.replace(cls.NSE_SUFFIX, '').replace(cls.BSE_SUFFIX, ''),
                'price': float(latest.get('Close', data.get('currentPrice', 0))),
                'previous_close': float(data.get('previousClose', 0)),
                'open': float(latest.get('Open', 0)),
                'high': float(latest.get('High', 0)),
                'low': float(latest.get('Low', 0)),
                'volume': int(latest.get('Volume', 0)),
                'market_cap': int(data.get('marketCap', 0)),
                'pe_ratio': float(data.get('trailingPE', 0) or 0),
                'sector': data.get('sector', 'N/A'),
                'industry': data.get('industry', 'N/A'),
                'timestamp': datetime.now(),
                'market_status': market_status,
                'data_freshness': data_freshness,
                'source': 'yfinance',
            }
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return None
    
    @classmethod
    def get_historical_data(
        cls, 
        symbol: str, 
        period: str = '1y',
        interval: str = '1d'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data
        
        Period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'
        Interval: '1m', '5m', '15m', '30m', '60m', '1d', '1wk', '1mo'
        
        Returns DataFrame with columns: Open, High, Low, Close, Volume, Dividends, Stock Splits
        """
        try:
            if '.' not in symbol:
                symbol = symbol + cls.NSE_SUFFIX
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                logger.warning(f"No historical data for {symbol}")
                return None
            
            return hist
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    @classmethod
    def get_fundamental_data(cls, symbol: str) -> Optional[Dict]:
        """
        Fetch fundamental analysis data
        
        Returns: {
            'pe_ratio': float,
            'pb_ratio': float,
            'peg_ratio': float,
            'debt_to_equity': float,
            'roe': float,  # Return on Equity
            'roa': float,  # Return on Assets
            'current_ratio': float,
            'profit_margin': float,
            'revenue': int,
            'earnings': int,
            'earnings_per_share': float,
            'book_value': float,
            'dividend_yield': float,
        }
        """
        try:
            if '.' not in symbol:
                symbol = symbol + cls.NSE_SUFFIX
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'pe_ratio': float(info.get('trailingPE', 0) or 0),
                'pb_ratio': float(info.get('priceToBook', 0) or 0),
                'peg_ratio': float(info.get('pegRatio', 0) or 0),
                'debt_to_equity': float(info.get('debtToEquity', 0) or 0),
                'roe': float(info.get('returnOnEquity', 0) or 0),
                'roa': float(info.get('returnOnAssets', 0) or 0),
                'current_ratio': float(info.get('currentRatio', 0) or 0),
                'profit_margin': float(info.get('profitMargins', 0) or 0),
                'revenue': int(info.get('totalRevenue', 0) or 0),
                'earnings': int(info.get('netIncomeToCommon', 0) or 0),
                'eps': float(info.get('trailingEps', 0) or 0),
                'book_value': float(info.get('bookValue', 0) or 0),
                'dividend_yield': float(info.get('dividendYield', 0) or 0),
                'beta': float(info.get('beta', 1.0) or 1.0),
                '52_week_high': float(info.get('fiftyTwoWeekHigh', 0) or 0),
                '52_week_low': float(info.get('fiftyTwoWeekLow', 0) or 0),
            }
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {str(e)}")
            return None
    
    @classmethod
    def get_market_indices(cls) -> Dict[str, Dict]:
        """
        Fetch major Indian market indices
        
        Returns: {
            'SENSEX': {'value': 70000, 'change': 250, 'change_percent': 0.36},
            'NIFTY50': {...},
            'MIDCAP50': {...},
            'SMALLCAP50': {...},
            'INDIA_VIX': {...},
        }
        """
        indices = {}
        index_symbols = {
            'SENSEX': '^BSESN',
            'NIFTY50': '^NSEI',
            'MIDCAP50': '^NSMIDCP',
            'SMALLCAP50': '^NSSMCP',
            'INDIA_VIX': '^INDIAVIX',
        }
        
        try:
            for name, symbol in index_symbols.items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period='1d')
                    
                    if not data.empty:
                        latest = data.iloc[-1]
                        current = float(latest['Close'])
                        previous = float(ticker.info.get('previousClose', current))
                        change = current - previous
                        change_percent = (change / previous * 100) if previous != 0 else 0
                        
                        indices[name] = {
                            'value': current,
                            'change': change,
                            'change_percent': change_percent,
                            'timestamp': datetime.now(),
                        }
                except Exception as e:
                    logger.warning(f"Could not fetch {name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching indices: {str(e)}")
        
        return indices
    
    @classmethod
    def get_sector_performance(cls) -> Dict[str, Dict]:
        """
        Get sector-wise market performance
        
        Returns: {
            'IT': {'companies': int, 'top_gainers': [...], 'performance': float},
            ...
        }
        """
        # Popular NSE sector indices
        sector_indices = {
            'IT': 'NIFTY_IT.NS',
            'PHARMA': 'NIFTY_PHARMA.NS',
            'BANK': 'NIFTY_BANK.NS',
            'FINANCE': 'NIFTY_FINANCIAL_SERVICES.NS',
            'FMCG': 'NIFTY_FMCG.NS',
            'REALTY': 'NIFTY_REALTY.NS',
            'ENERGY': 'NIFTY_ENERGY.NS',
            'METALS': 'NIFTY_METALS.NS',
        }
        
        sectors = {}
        try:
            for sector_name, symbol in sector_indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='1d')
                    
                    if not hist.empty:
                        latest = hist.iloc[-1]
                        current = float(latest['Close'])
                        previous = float(ticker.info.get('previousClose', current))
                        change_percent = ((current - previous) / previous * 100) if previous != 0 else 0
                        
                        sectors[sector_name] = {
                            'value': current,
                            'change_percent': change_percent,
                            'timestamp': datetime.now(),
                        }
                except Exception as e:
                    logger.warning(f"Could not fetch {sector_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching sector data: {str(e)}")
        
        return sectors
    
    @classmethod
    def _get_market_status(cls) -> str:
        """
        Determine current market status: OPEN, CLOSED, HOLIDAY
        NSE trading: 09:15 - 15:30 IST, Mon-Fri (except holidays)
        """
        from datetime import datetime, timezone
        import pytz
        
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        
        # Check if holiday
        today_str = now_ist.strftime('%Y-%m-%d')
        if today_str in cls.INDIAN_HOLIDAYS:
            return 'HOLIDAY'
        
        # Check if weekend
        if now_ist.weekday() >= 5:  # Saturday=5, Sunday=6
            return 'CLOSED'
        
        # Check if within market hours
        market_open = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
        
        if market_open <= now_ist <= market_close:
            return 'OPEN'
        else:
            return 'CLOSED'
    
    @classmethod
    def validate_data_quality(cls, data: Dict) -> Tuple[bool, str]:
        """Validate data quality and freshness"""
        try:
            # Check required fields
            required = ['symbol', 'price', 'volume', 'timestamp']
            if not all(k in data for k in required):
                return False, 'Missing required fields'
            
            # Check price validity
            if data['price'] <= 0:
                return False, 'Invalid price'
            
            # Check data freshness (should be within last hour for live data)
            if data.get('data_freshness') == 'LIVE':
                age = datetime.now() - data['timestamp']
                if age > timedelta(hours=1):
                    return False, 'Data too old'
            
            return True, 'Data valid'
        except Exception as e:
            return False, str(e)


class DataCacheManager:
    """Manages data caching to reduce API calls"""
    
    _cache = {}
    CACHE_VALIDITY = {
        'intraday': 300,      # 5 minutes
        'daily': 3600,        # 1 hour
        'fundamentals': 86400,  # 1 day
        'indices': 300,       # 5 minutes
    }
    
    @classmethod
    def get(cls, key: str, data_type: str = 'daily') -> Optional[Dict]:
        """Get data from cache if valid"""
        if key not in cls._cache:
            return None
        
        cached_data, timestamp = cls._cache[key]
        age = (datetime.now() - timestamp).total_seconds()
        
        if age > cls.CACHE_VALIDITY.get(data_type, 3600):
            del cls._cache[key]
            return None
        
        return cached_data
    
    @classmethod
    def set(cls, key: str, data: Dict) -> None:
        """Store data in cache"""
        cls._cache[key] = (data, datetime.now())
    
    @classmethod
    def clear(cls) -> None:
        """Clear all cache"""
        cls._cache.clear()
