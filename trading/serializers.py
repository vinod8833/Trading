"""
Serializers for KVK Trading System
"""

from rest_framework import serializers
from .models import (
    Stock, StockAnalysis, TradeRecommendation, TradeOrder,
    Portfolio, RiskAssessment, AlternativeInvestment,
    PaperTrade, SmartAlert, MarketSummary, PortfolioHealth,
    TradingMistake, AIExplanation, InvestmentPlan
)


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = [
            'id', 'symbol', 'name', 'market_cap', 'market_cap_category',
            'sector', 'industry', 'current_price', 'previous_close',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockAnalysisSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    
    class Meta:
        model = StockAnalysis
        fields = [
            'id', 'stock', 'current_price', 'support_level', 'resistance_level',
            'rsi', 'bollinger_upper', 'bollinger_middle', 'bollinger_lower',
            'vwap', 'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
            'trend', 'trend_probability', 'volume', 'average_volume_20',
            'volume_trend', 'fib_0_236', 'fib_0_382', 'fib_0_500', 'fib_0_618',
            'analyzed_at'
        ]
        read_only_fields = ['id', 'analyzed_at']


class AlternativeInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternativeInvestment
        fields = [
            'id', 'name', 'investment_type', 'description', 'expected_return',
            'risk_level', 'liquidity', 'reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'recommendation', 'risk_level', 'risk_percentage',
            'volatility_score', 'liquidity_score', 'market_condition_score',
            'max_position_size', 'recommended_stop_loss', 'assessment_notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TradeRecommendationSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    analysis = StockAnalysisSerializer(read_only=True)
    risk_assessment = RiskAssessmentSerializer(read_only=True)
    alternatives = AlternativeInvestmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = TradeRecommendation
        fields = [
            'id', 'stock', 'analysis', 'trading_style', 'signal',
            'entry_price', 'stop_loss', 'target_1', 'target_2', 'target_3', 'target_4',
            'risk_percent', 'profit_percent', 'risk_reward_ratio',
            'confidence_level', 'win_probability', 'valid_from_session', 'valid_until_session',
            'notes', 'risk_assessment', 'alternatives', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TradeOrderSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    recommendation = TradeRecommendationSerializer(read_only=True)
    
    class Meta:
        model = TradeOrder
        fields = [
            'id', 'recommendation', 'stock', 'quantity', 'entry_price',
            'actual_entry_price', 'stop_loss', 'target', 'status',
            'entry_time', 'exit_time', 'profit_loss', 'profit_loss_percent',
            'capital_allocated', 'risk_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = [
            'id', 'name', 'total_capital', 'available_capital', 'invested_capital',
            'current_value', 'total_profit_loss', 'max_risk_per_trade',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PaperTradeSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    
    class Meta:
        model = PaperTrade
        fields = [
            'id', 'portfolio', 'stock', 'side', 'entry_price', 'quantity',
            'entry_date', 'entry_value', 'stop_loss', 'target_1', 'target_2', 'target_3', 'target_4',
            'current_price', 'unrealized_pnl', 'exit_price', 'exit_date', 'exit_type',
            'profit_loss', 'profit_loss_percent', 'entry_commission', 'exit_commission',
            'risk_amount', 'risk_percent', 'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'unrealized_pnl', 'entry_commission', 'exit_commission']


class SmartAlertSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    
    class Meta:
        model = SmartAlert
        fields = [
            'id', 'stock', 'alert_type', 'condition', 'target_value',
            'trigger_value', 'status', 'triggered_at', 'send_email',
            'send_notification', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MarketSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSummary
        fields = [
            'id', 'market_date', 'gainers_count', 'losers_count', 'unchanged_count',
            'market_trend', 'market_sentiment', 'average_volume', 'volatility_index',
            'sector_performance', 'summary_text', 'key_levels', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PortfolioHealthSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer(read_only=True)
    
    class Meta:
        model = PortfolioHealth
        fields = [
            'id', 'portfolio', 'health_score', 'health_status',
            'total_profit_loss', 'profit_loss_percent', 'win_rate',
            'average_win', 'average_loss', 'risk_level', 'max_drawdown',
            'sharpe_ratio', 'sector_concentration', 'number_of_holdings',
            'largest_position_percent', 'warnings', 'recommendations', 'analyzed_at'
        ]
        read_only_fields = ['id', 'analyzed_at']


class TradingMistakeSerializer(serializers.ModelSerializer):
    trade_order = TradeOrderSerializer(read_only=True)
    
    class Meta:
        model = TradingMistake
        fields = [
            'id', 'trade_order', 'mistake_category', 'severity',
            'description', 'impact', 'lesson_learned', 'prevention_tip', 'detected_at'
        ]
        read_only_fields = ['id', 'detected_at']


class AIExplanationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIExplanation
        fields = [
            'id', 'related_model', 'related_id', 'explanation_type',
            'simple_explanation', 'detailed_explanation', 'key_factors',
            'confidence_score', 'indicators_used', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class InvestmentPlanSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer(read_only=True)
    
    class Meta:
        model = InvestmentPlan
        fields = [
            'id', 'portfolio', 'goal', 'target_amount', 'time_horizon',
            'risk_tolerance', 'equity_percent', 'debt_percent', 'alternatives_percent',
            'recommended_stocks', 'plan_description', 'expected_returns',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Response Serializers for API Endpoints

class SignalResponseSerializer(serializers.Serializer):
    """Response format for trading signals"""
    signal = serializers.CharField()
    confidence = serializers.CharField()
    simple_explanation = serializers.CharField()
    action = serializers.CharField()
    indicators = serializers.DictField(required=False)
    detailed_analysis = serializers.CharField(required=False)


class RiskAnalysisResponseSerializer(serializers.Serializer):
    """Response format for risk analysis"""
    risk_amount = serializers.FloatField()
    risk_percent = serializers.FloatField()
    risk_level = serializers.CharField()
    capital_check = serializers.DictField()
    warnings = serializers.ListField()
    recommendation = serializers.CharField()


class MarketSummaryResponseSerializer(serializers.Serializer):
    """Response format for market summary"""
    gainers = serializers.IntegerField()
    losers = serializers.IntegerField()
    sentiment = serializers.CharField()
    top_sectors = serializers.DictField()
    bottom_sectors = serializers.DictField()
    summary = serializers.CharField()
    volatility = serializers.FloatField(required=False)


class AIExplainerResponseSerializer(serializers.Serializer):
    """Response format for AI explanations"""
    signal = serializers.CharField()
    simple_explanation = serializers.CharField()
    detailed_explanation = serializers.CharField()
    key_factors = serializers.ListField()
    confidence_score = serializers.FloatField()


class PaperTradingResponseSerializer(serializers.Serializer):
    """Response format for paper trading operations"""
    trade_id = serializers.IntegerField(required=False)
    stock = serializers.CharField()
    quantity = serializers.IntegerField()
    entry = serializers.FloatField()
    exit = serializers.FloatField(required=False)
    profit_loss = serializers.FloatField()
    profit_loss_percent = serializers.FloatField()
    status = serializers.CharField()


class InvestmentPlanResponseSerializer(serializers.Serializer):
    """Response format for investment plans"""
    goal = serializers.CharField()
    target_amount = serializers.FloatField()
    time_horizon = serializers.CharField()
    risk_tolerance = serializers.CharField()
    allocation = serializers.DictField()
    expected_annual_return = serializers.FloatField()
    recommended_stocks = serializers.ListField()
    description = serializers.CharField()