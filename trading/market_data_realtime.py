"""
Real Market Data Fetcher using yfinance
Supports global stocks: Indian (NSE/BSE), US (NYSE/NASDAQ), and international markets
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class MarketDataFetcher:
    """Fetch real market data using yfinance - UNLIMITED FREE DATA"""
    
    # Market identifiers for different exchanges
    MARKET_SUFFIXES = {
        'NSE': '.NS',      # National Stock Exchange (India)
        'BSE': '.BO',      # Bombay Stock Exchange (India)
        'NYSE': '',        # New York Stock Exchange
        'NASDAQ': '',      # NASDAQ
        'LSE': '.L',       # London Stock Exchange
        'TSE': '.T',       # Tokyo Stock Exchange
    }
    
    STOCK_SECTORS = {
        'INFY': 'Information Technology',
        'TCS': 'Information Technology',
        'RELIANCE': 'Energy',
        'HDFCBANK': 'Banking',
        'ICICIBANK': 'Banking',
        'SBIN': 'Banking',
        'WIPRO': 'Information Technology',
        'BAJAJFINSV': 'Financial Services',
        'LT': 'Conglomerates',
        'ITC': 'Consumer Goods',
        'AAPL': 'Technology',
        'GOOGL': 'Technology',
        'MSFT': 'Technology',
        'TSLA': 'Automotive',
        'AMZN': 'Retail',
    }
    
    @staticmethod
    def get_stock_data(symbol: str, market: str = 'NSE', period: str = '1y') -> Optional[Dict]:
        """
        Fetch real stock data from yfinance
        
        Args:
            symbol: Stock symbol (e.g., 'INFY', 'AAPL')
            market: Market code ('NSE', 'BSE', 'NYSE', 'NASDAQ', etc.)
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', etc.)
        
        Returns:
            Dictionary with stock data or None if failed
        """
        try:
            # Build ticker with market suffix
            suffix = MarketDataFetcher.MARKET_SUFFIXES.get(market, '')
            ticker = f"{symbol}{suffix}"
            
            logger.info(f"Fetching data for {ticker} ({market})")
            
            # Fetch data
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            info = stock.info
            
            if hist.empty:
                logger.warning(f"No data found for {ticker}")
                return None
            
            # Get latest data
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            return {
                'symbol': symbol,
                'market': market,
                'ticker': ticker,
                'name': info.get('longName', symbol),
                'sector': MarketDataFetcher.STOCK_SECTORS.get(symbol, info.get('sector', 'Unknown')),
                'industry': info.get('industry', 'Unknown'),
                'current_price': float(latest['Close']),
                'previous_close': float(previous['Close']),
                'open': float(latest['Open']),
                'high_52w': float(info.get('fiftyTwoWeekHigh', latest['Close'])),
                'low_52w': float(info.get('fiftyTwoWeekLow', latest['Close'])),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': float(info.get('trailingPE', 0)) if info.get('trailingPE') else None,
                'eps': float(info.get('trailingEps', 0)) if info.get('trailingEps') else None,
                'dividend_yield': float(info.get('dividendYield', 0)) if info.get('dividendYield') else None,
                'beta': float(info.get('beta', 0)) if info.get('beta') else None,
                'volume': int(latest['Volume']),
                'avg_volume': int(info.get('averageVolume', latest['Volume'])),
                'data_points': len(hist),
                'last_updated': datetime.now().isoformat(),
                'history': hist,
            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_historical_data(symbol: str, market: str = 'NSE', days: int = 365) -> Optional[pd.DataFrame]:
        """Get historical OHLCV data for technical analysis"""
        try:
            suffix = MarketDataFetcher.MARKET_SUFFIXES.get(market, '')
            ticker = f"{symbol}{suffix}"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f'{days}d')
            
            if hist.empty:
                return None
            
            # Add technical columns
            hist['Daily_Return'] = hist['Close'].pct_change()
            hist['Daily_Change'] = hist['Close'] - hist['Open']
            hist['High_Low'] = hist['High'] - hist['Low']
            
            return hist
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_intraday_data(symbol: str, market: str = 'NSE', interval: str = '1h') -> Optional[pd.DataFrame]:
        """
        Get intraday data for live trading
        
        Intervals: '1m', '5m', '15m', '30m', '60m', '90m', '1h'
        Note: Limited to last 60 days for free tier
        """
        try:
            suffix = MarketDataFetcher.MARKET_SUFFIXES.get(market, '')
            ticker = f"{symbol}{suffix}"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period='60d', interval=interval)
            
            if hist.empty:
                return None
            
            # Keep only today's data or last trading day
            hist = hist[hist.index.date == datetime.now().date()]
            if hist.empty:
                # Get previous trading day
                hist = stock.history(period='3d', interval=interval)
                hist = hist[hist.index.date == (datetime.now() - timedelta(days=1)).date()]
            
            return hist if not hist.empty else None
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_multiple_stocks(symbols: List[str], market: str = 'NSE') -> Dict[str, Dict]:
        """Fetch data for multiple stocks"""
        results = {}
        for symbol in symbols:
            data = MarketDataFetcher.get_stock_data(symbol, market)
            if data:
                results[symbol] = data
        return results
    
    @staticmethod
    def calculate_market_cap_category(market_cap: float) -> str:
        """Categorize market cap"""
        if market_cap >= 100000000000:  # ₹1 lakh crore
            return 'LARGE_CAP'
        elif market_cap >= 50000000000:
            return 'MID_CAP'
        elif market_cap >= 10000000000:
            return 'SMALL_CAP'
        else:
            return 'MICRO_CAP'


class TechnicalDataCalculator:
    """Calculate technical indicators from historical data"""
    
    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Simple Moving Average"""
        return data['Close'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int = 12) -> pd.Series:
        """Exponential Moving Average"""
        return data['Close'].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """MACD"""
        ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range for volatility"""
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return atr
    
    @staticmethod
    def calculate_all_indicators(symbol: str, market: str = 'NSE', days: int = 365) -> Optional[Dict]:
        """Calculate all technical indicators"""
        try:
            hist = MarketDataFetcher.get_historical_data(symbol, market, days)
            if hist is None or hist.empty:
                return None
            
            latest_idx = len(hist) - 1
            
            return {
                'symbol': symbol,
                'current_price': float(hist['Close'].iloc[latest_idx]),
                'sma_20': float(TechnicalDataCalculator.calculate_sma(hist, 20).iloc[latest_idx]) if len(hist) >= 20 else None,
                'sma_50': float(TechnicalDataCalculator.calculate_sma(hist, 50).iloc[latest_idx]) if len(hist) >= 50 else None,
                'sma_200': float(TechnicalDataCalculator.calculate_sma(hist, 200).iloc[latest_idx]) if len(hist) >= 200 else None,
                'ema_12': float(TechnicalDataCalculator.calculate_ema(hist, 12).iloc[latest_idx]) if len(hist) >= 12 else None,
                'ema_26': float(TechnicalDataCalculator.calculate_ema(hist, 26).iloc[latest_idx]) if len(hist) >= 26 else None,
                'rsi': float(TechnicalDataCalculator.calculate_rsi(hist, 14).iloc[latest_idx]) if len(hist) >= 14 else None,
                'atr': float(TechnicalDataCalculator.calculate_atr(hist, 14).iloc[latest_idx]) if len(hist) >= 14 else None,
                'macd': float(TechnicalDataCalculator.calculate_macd(hist)[0].iloc[latest_idx]) if len(hist) >= 26 else None,
                'bollinger_upper': float(TechnicalDataCalculator.calculate_bollinger_bands(hist, 20)[0].iloc[latest_idx]) if len(hist) >= 20 else None,
                'bollinger_middle': float(TechnicalDataCalculator.calculate_bollinger_bands(hist, 20)[1].iloc[latest_idx]) if len(hist) >= 20 else None,
                'bollinger_lower': float(TechnicalDataCalculator.calculate_bollinger_bands(hist, 20)[2].iloc[latest_idx]) if len(hist) >= 20 else None,
                '52w_high': float(hist['High'].max()),
                '52w_low': float(hist['Low'].min()),
                'volatility': float(hist['Daily_Return'].std() * 252 * 100),  # Annualized volatility
            }
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return None
