"""
Utility functions for KVK Trading System
"""

from decimal import Decimal
from typing import List, Dict
import datetime


class PriceFormatter:
    """Format prices for display"""
    
    @staticmethod
    def format_price(price: Decimal, currency: str = "₹") -> str:
        return f"{currency}{price:.2f}"
    
    @staticmethod
    def format_percent(value: float, decimals: int = 2) -> str:
        return f"{value:.{decimals}f}%"


class DateTimeHelper:
    """Date and time utilities"""
    
    MARKET_OPEN_TIME = datetime.time(9, 15)
    MARKET_CLOSE_TIME = datetime.time(15, 30)
    
    @staticmethod
    def is_market_open(dt: datetime.datetime) -> bool:
        """Check if market is open"""
        if dt.weekday() >= 5:  # Weekend
            return False
        
        current_time = dt.time()
        return DateTimeHelper.MARKET_OPEN_TIME <= current_time <= DateTimeHelper.MARKET_CLOSE_TIME
    
    @staticmethod
    def get_trading_day_minutes_elapsed(dt: datetime.datetime) -> int:
        """Get minutes elapsed since market open"""
        market_open = datetime.datetime.combine(
            dt.date(), DateTimeHelper.MARKET_OPEN_TIME
        )
        if dt < market_open:
            return 0
        
        delta = dt - market_open
        return int(delta.total_seconds() / 60)


class ValidationHelper:
    """Input validation utilities"""
    
    @staticmethod
    def validate_price(price: float) -> bool:
        return price > 0

    @staticmethod
    def validate_quantity(qty: int) -> bool:
        return qty > 0 and isinstance(qty, int)

    @staticmethod
    def validate_capital(capital: Decimal) -> bool:
        return capital > 0

    @staticmethod
    def validate_entry_sl_target(entry: Decimal, sl: Decimal, target: Decimal) -> bool:
        """Validate entry, stop loss, and target relationship"""
        return (entry > sl and entry < target) or (entry < sl and entry > target)


class ReportGenerator:
    """Generate trading reports"""
    
    @staticmethod
    def generate_trade_summary(recommendation: Dict) -> str:
        """Generate text summary of recommendation"""
        
        template = f"""
TRADE RECOMMENDATION
====================
Signal: {recommendation['signal']}
Trading Style: {recommendation['trading_style']}

PRICE LEVELS
============
Entry: {recommendation['entry_price']}
Stop Loss: {recommendation['stop_loss']}
Target 1: {recommendation['target_1']}
Target 2: {recommendation.get('target_2', 'N/A')}
Target 3: {recommendation.get('target_3', 'N/A')}
Target 4: {recommendation.get('target_4', 'N/A')}

RISK METRICS
============
Risk %: {recommendation.get('risk_percent', 0):.2f}%
Profit %: {recommendation.get('profit_percent', 0):.2f}%
Risk-Reward Ratio: {recommendation.get('risk_reward_ratio', 0):.2f}
Confidence: {recommendation.get('confidence', 0):.0f}%
Win Probability: {recommendation.get('win_probability', 0):.0f}%

POSITION
========
Quantity: {recommendation.get('quantity', 0)}
Capital Allocated: {recommendation.get('capital_allocated', 0)}
Risk Amount: {recommendation.get('risk_amount', 0)}
"""
        return template.strip()
