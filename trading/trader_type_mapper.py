"""
Trader Type Mapper
Maps optimal formulas to different trader types
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class TraderType(Enum):
    """Different trader/investor types"""
    INTRADAY = "intraday"
    SWING = "swing"
    POSITIONAL = "positional"
    LONG_TERM = "long_term"
    OPTIONS = "options"
    AI_ALGO = "ai_algo"
    INVESTOR = "investor"


@dataclass
class TraderProfile:
    """Trader profile with formula preferences"""
    trader_type: TraderType
    time_horizon: str
    risk_tolerance: str
    primary_formulas: List[str]
    secondary_formulas: List[str]
    avoid_formulas: List[str]
    holding_period: str
    max_risk_per_trade: float
    ideal_market_conditions: List[str]
    description: str


class TraderTypeMapper:
    """Map trader types to recommended formulas and strategies"""
    
    TRADER_PROFILES = {
        TraderType.INTRADAY: TraderProfile(
            trader_type=TraderType.INTRADAY,
            time_horizon="Minutes to Hours",
            risk_tolerance="High",
            primary_formulas=["EMA", "VWAP", "RSI", "ATR"],
            secondary_formulas=["ROC", "VOLUME", "OBV"],
            avoid_formulas=["P/E", "ROE", "SMA50", "MACD"],
            holding_period="< 1 Day",
            max_risk_per_trade=1.0,
            ideal_market_conditions=["STRONG_UPTREND", "DOWNTREND", "BREAKOUT", "RANGE_BOUND"],
            description="High-frequency trader focusing on quick profits from intraday price movements"
        ),
        
        TraderType.SWING: TraderProfile(
            trader_type=TraderType.SWING,
            time_horizon="Days to Weeks",
            risk_tolerance="Medium-High",
            primary_formulas=["RSI", "MACD", "EMA", "OBV"],
            secondary_formulas=["BOLLINGER_BANDS", "ATR", "VOLUME"],
            avoid_formulas=["P/E", "ROE", "VWAP"],
            holding_period="2-20 Days",
            max_risk_per_trade=1.5,
            ideal_market_conditions=["UPTREND", "DOWNTREND", "RANGE_BOUND", "BREAKOUT"],
            description="Medium-term trader capturing price swings over days/weeks"
        ),
        
        TraderType.POSITIONAL: TraderProfile(
            trader_type=TraderType.POSITIONAL,
            time_horizon="Weeks to Months",
            risk_tolerance="Medium",
            primary_formulas=["SMA", "EMA", "RSI", "MACD"],
            secondary_formulas=["ROE", "P/E", "OBV", "VOLUME"],
            avoid_formulas=["VWAP", "ROC"],
            holding_period="3-90 Days",
            max_risk_per_trade=1.5,
            ideal_market_conditions=["UPTREND", "WEAK_UPTREND", "NEUTRAL"],
            description="Medium to medium-long term trader holding positions for weeks/months"
        ),
        
        TraderType.LONG_TERM: TraderProfile(
            trader_type=TraderType.LONG_TERM,
            time_horizon="Months to Years",
            risk_tolerance="Low-Medium",
            primary_formulas=["SMA50", "SMA200", "ROE", "P/E", "DEBT_EQUITY"],
            secondary_formulas=["SHARPE", "MAX_DRAWDOWN", "LOG_RETURNS"],
            avoid_formulas=["VWAP", "RSI_OVERBOUGHT", "ROC"],
            holding_period="> 90 Days",
            max_risk_per_trade=2.0,
            ideal_market_conditions=["UPTREND", "NEUTRAL"],
            description="Long-term investor focused on fundamental value and compound growth"
        ),
        
        TraderType.OPTIONS: TraderProfile(
            trader_type=TraderType.OPTIONS,
            time_horizon="Days to Weeks",
            risk_tolerance="High",
            primary_formulas=["BOLLINGER_BANDS", "RSI", "ATR", "IMPLIED_VOLATILITY"],
            secondary_formulas=["MACD", "ROC", "VOLUME"],
            avoid_formulas=["SMA50", "P/E"],
            holding_period="< 60 Days",
            max_risk_per_trade=2.0,
            ideal_market_conditions=["HIGH_VOLATILITY", "RANGE_BOUND", "BREAKOUT"],
            description="Options trader using volatility and probability-based strategies"
        ),
        
        TraderType.AI_ALGO: TraderProfile(
            trader_type=TraderType.AI_ALGO,
            time_horizon="Real-time to Days",
            risk_tolerance="Medium",
            primary_formulas=["SHARPE", "SORTINO", "LOG_RETURNS", "EMA", "ATR"],
            secondary_formulas=["RSI", "MACD", "VOLUME", "ROC"],
            avoid_formulas=["P/E", "ROE"],  # These change slowly
            holding_period="Minutes to Days",
            max_risk_per_trade=1.0,
            ideal_market_conditions=["ALL"],
            description="Algorithmic trader using ML and quantitative metrics"
        ),
        
        TraderType.INVESTOR: TraderProfile(
            trader_type=TraderType.INVESTOR,
            time_horizon="Years",
            risk_tolerance="Low",
            primary_formulas=["P/E", "ROE", "DEBT_EQUITY", "EPS_GROWTH"],
            secondary_formulas=["SMA200", "SHARPE", "MAX_DRAWDOWN"],
            avoid_formulas=["VWAP", "RSI_OVERBOUGHT", "ROC", "BOLLINGER_BANDS"],
            holding_period="> 1 Year",
            max_risk_per_trade=2.0,
            ideal_market_conditions=["NEUTRAL"],
            description="Conservative long-term investor focused on fundamentals and dividends"
        )
    }
    
    @staticmethod
    def get_profile(trader_type: TraderType) -> TraderProfile:
        """Get trader profile"""
        return TraderTypeMapper.TRADER_PROFILES.get(trader_type)
    
    @staticmethod
    def recommend_formulas(trader_type: TraderType, 
                          market_condition: str,
                          available_indicators: List[str]) -> Dict[str, List[str]]:
        """Recommend formulas based on trader type and market condition"""
        
        profile = TraderTypeMapper.get_profile(trader_type)
        if not profile:
            return {"error": f"Unknown trader type: {trader_type}"}
        
        # Get formulas that are available
        primary = [f for f in profile.primary_formulas if f in available_indicators]
        secondary = [f for f in profile.secondary_formulas if f in available_indicators]
        
        # Check market condition compatibility
        is_ideal_market = market_condition in profile.ideal_market_conditions
        
        return {
            "trader_type": trader_type.value,
            "time_horizon": profile.time_horizon,
            "max_risk_per_trade": profile.max_risk_per_trade,
            "primary_formulas": primary,
            "secondary_formulas": secondary,
            "avoid_formulas": profile.avoid_formulas,
            "ideal_for_market": is_ideal_market,
            "market_condition": market_condition,
            "holding_period": profile.holding_period,
            "description": profile.description
        }
    
    @staticmethod
    def get_position_size_guidelines(trader_type: TraderType) -> Dict:
        """Get position sizing guidelines for trader type"""
        
        profile = TraderTypeMapper.get_profile(trader_type)
        
        return {
            "trader_type": trader_type.value,
            "max_risk_per_trade": profile.max_risk_per_trade,
            "typical_portfolio_allocation": {
                TraderType.INTRADAY: "5-10%",
                TraderType.SWING: "5-10%",
                TraderType.POSITIONAL: "5-15%",
                TraderType.LONG_TERM: "2-5%",
                TraderType.OPTIONS: "2-5%",
                TraderType.AI_ALGO: "5-10%",
                TraderType.INVESTOR: "2-5%"
            }.get(trader_type, "5%"),
            "max_position_size": {
                TraderType.INTRADAY: "20% of portfolio",
                TraderType.SWING: "15% of portfolio",
                TraderType.POSITIONAL: "10% of portfolio",
                TraderType.LONG_TERM: "5% of portfolio",
                TraderType.OPTIONS: "3% of portfolio",
                TraderType.AI_ALGO: "10% of portfolio",
                TraderType.INVESTOR: "5% of portfolio"
            }.get(trader_type, "10% of portfolio"),
            "holding_period": profile.holding_period,
            "recommended_stop_loss": {
                TraderType.INTRADAY: "0.5-1% from entry",
                TraderType.SWING: "1-2% from entry",
                TraderType.POSITIONAL: "2-3% from entry",
                TraderType.LONG_TERM: "5-10% from entry",
                TraderType.OPTIONS: "Close spread width",
                TraderType.AI_ALGO: "1-1.5% from entry",
                TraderType.INVESTOR: "10-15% from entry"
            }.get(trader_type, "2% from entry"),
            "recommended_target": {
                TraderType.INTRADAY: "1:1 to 1:2 Risk-Reward",
                TraderType.SWING: "1:2 to 1:3 Risk-Reward",
                TraderType.POSITIONAL: "1:3 to 1:5 Risk-Reward",
                TraderType.LONG_TERM: "Open-ended hold",
                TraderType.OPTIONS: "Spread-specific targets",
                TraderType.AI_ALGO: "1:2 to 1:3 Risk-Reward",
                TraderType.INVESTOR: "Long-term capital appreciation"
            }.get(trader_type, "1:2 Risk-Reward")
        }
    
    @staticmethod
    def detect_trader_type(profile_data: Dict) -> Optional[TraderType]:
        """Detect trader type from user profile"""
        
        # Check indicators from profile
        if profile_data.get("trading_style") == "intraday":
            return TraderType.INTRADAY
        elif profile_data.get("trading_style") == "swing":
            return TraderType.SWING
        elif profile_data.get("trading_style") == "positional":
            return TraderType.POSITIONAL
        elif profile_data.get("trading_style") == "long_term":
            return TraderType.LONG_TERM
        elif profile_data.get("trading_style") == "options":
            return TraderType.OPTIONS
        elif profile_data.get("trading_style") == "ai":
            return TraderType.AI_ALGO
        else:
            return TraderType.SWING  # Default
    
    @staticmethod
    def get_all_profiles() -> Dict[str, TraderProfile]:
        """Get all trader profiles for reference"""
        return TraderTypeMapper.TRADER_PROFILES
    
    @staticmethod
    def get_formula_by_trader_type(trader_type: TraderType) -> Dict[str, List[str]]:
        """Get formula groups by trader type"""
        profile = TraderTypeMapper.get_profile(trader_type)
        
        return {
            "trader_type": trader_type.value,
            "trend_formulas": [f for f in profile.primary_formulas if f in ["SMA", "EMA", "VWAP"]],
            "momentum_formulas": [f for f in profile.primary_formulas if f in ["RSI", "MACD", "ROC"]],
            "volatility_formulas": [f for f in profile.primary_formulas if f in ["ATR", "BOLLINGER_BANDS"]],
            "volume_formulas": [f for f in profile.primary_formulas if f in ["OBV", "VOLUME"]],
            "fundamental_formulas": [f for f in profile.primary_formulas if f in ["P/E", "ROE", "DEBT_EQUITY"]],
            "risk_formulas": [f for f in profile.primary_formulas if f in ["POSITION_SIZE", "RISK_REWARD"]],
            "ai_metrics": [f for f in profile.primary_formulas if f in ["SHARPE", "SORTINO", "MAX_DRAWDOWN"]],
        }
