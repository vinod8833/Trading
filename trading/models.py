"""
Django Models for KVK Trading System
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime


class Stock(models.Model):
    """Stock Information Model"""
    
    MARKET_CAP_CHOICES = [
        ('LARGE_CAP', 'Large Cap (>50B)'),
        ('MID_CAP', 'Mid Cap (5B-50B)'),
        ('SMALL_CAP', 'Small Cap (500M-5B)'),
        ('MICRO_CAP', 'Micro Cap (<500M)'),
    ]
    
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    market_cap = models.BigIntegerField(null=True, blank=True)
    market_cap_category = models.CharField(max_length=20, choices=MARKET_CAP_CHOICES)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    previous_close = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['symbol']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['market_cap_category']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"


class StockAnalysis(models.Model):
    """Technical Analysis Results"""
    
    TREND_CHOICES = [
        ('STRONG_BULLISH', 'Strong Bullish'),
        ('BULLISH', 'Bullish'),
        ('NEUTRAL', 'Neutral'),
        ('BEARISH', 'Bearish'),
        ('STRONG_BEARISH', 'Strong Bearish'),
    ]
    
    stock = models.OneToOneField(Stock, on_delete=models.CASCADE, related_name='analysis')
    
    # Price Levels
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    support_level = models.DecimalField(max_digits=10, decimal_places=2)
    resistance_level = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Technical Indicators
    rsi = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    bollinger_upper = models.DecimalField(max_digits=10, decimal_places=2)
    bollinger_middle = models.DecimalField(max_digits=10, decimal_places=2)
    bollinger_lower = models.DecimalField(max_digits=10, decimal_places=2)
    
    vwap = models.DecimalField(max_digits=10, decimal_places=2)
    sma_20 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    sma_50 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    sma_200 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    ema_12 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    ema_26 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Trend Analysis
    trend = models.CharField(max_length=20, choices=TREND_CHOICES)
    trend_probability = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Volume Analysis
    volume = models.BigIntegerField()
    average_volume_20 = models.BigIntegerField()
    volume_trend = models.CharField(
        max_length=20,
        choices=[('INCREASING', 'Increasing'), ('DECREASING', 'Decreasing'), ('STABLE', 'Stable')]
    )
    
    # Fibonacci Levels
    fib_0_236 = models.DecimalField(max_digits=10, decimal_places=2)
    fib_0_382 = models.DecimalField(max_digits=10, decimal_places=2)
    fib_0_500 = models.DecimalField(max_digits=10, decimal_places=2)
    fib_0_618 = models.DecimalField(max_digits=10, decimal_places=2)
    
    analyzed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-analyzed_at']
    
    def __str__(self):
        return f"Analysis: {self.stock.symbol} - {self.trend}"


class TradeRecommendation(models.Model):
    """Trade Recommendations"""
    
    TRADING_STYLE_CHOICES = [
        ('INTRADAY', 'Intraday'),
        ('SWING', 'Swing'),
        ('POSITIONAL', 'Positional'),
        ('LONG_TERM', 'Long-Term'),
    ]
    
    SIGNAL_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('HOLD', 'Hold'),
        ('AVOID', 'Avoid'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='recommendations')
    analysis = models.ForeignKey(StockAnalysis, on_delete=models.CASCADE)
    
    trading_style = models.CharField(max_length=20, choices=TRADING_STYLE_CHOICES)
    signal = models.CharField(max_length=20, choices=SIGNAL_CHOICES)
    
    # Entry and Exit
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    stop_loss = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Multiple Targets
    target_1 = models.DecimalField(max_digits=10, decimal_places=2)
    target_2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    target_3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    target_4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Risk Management
    risk_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    profit_percent = models.FloatField(validators=[MinValueValidator(0)])
    risk_reward_ratio = models.FloatField()
    
    # Confidence
    confidence_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    win_probability = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Session Info
    valid_from_session = models.CharField(max_length=50, blank=True)
    valid_until_session = models.CharField(max_length=50, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock', '-created_at']),
            models.Index(fields=['signal']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.signal} ({self.trading_style})"


class TradeOrder(models.Model):
    """Executed Trade Orders"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('EXECUTED', 'Executed'),
        ('PARTIAL', 'Partially Executed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    recommendation = models.ForeignKey(
        TradeRecommendation,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='orders')
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    actual_entry_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    stop_loss = models.DecimalField(max_digits=10, decimal_places=2)
    target = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    
    profit_loss = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    profit_loss_percent = models.FloatField(null=True)
    
    capital_allocated = models.DecimalField(max_digits=12, decimal_places=2)
    risk_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Intraday-specific fields
    is_intraday = models.BooleanField(default=False)
    auto_square_off = models.BooleanField(default=False)
    square_off_time = models.TimeField(null=True, blank=True)  # 3:30 PM by default for intraday
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_intraday', 'auto_square_off']),
        ]
    
    def __str__(self):
        return f"Order: {self.stock.symbol} - {self.quantity} @ {self.entry_price}" + (" (INTRADAY)" if self.is_intraday else "")


class Portfolio(models.Model):
    """User Portfolio"""
    
    name = models.CharField(max_length=255)
    total_capital = models.DecimalField(max_digits=15, decimal_places=2)
    available_capital = models.DecimalField(max_digits=15, decimal_places=2)
    invested_capital = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    max_risk_per_trade = models.FloatField(default=0.5)  # 0.5%
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class RiskAssessment(models.Model):
    """Risk Assessment for Trades"""
    
    RISK_LEVEL_CHOICES = [
        ('VERY_LOW', 'Very Low (<0.5%)'),
        ('LOW', 'Low (0.5%-1%)'),
        ('MODERATE', 'Moderate (1%-2%)'),
        ('HIGH', 'High (2%-3%)'),
        ('VERY_HIGH', 'Very High (>3%)'),
    ]
    
    recommendation = models.OneToOneField(
        TradeRecommendation,
        on_delete=models.CASCADE,
        related_name='risk_assessment'
    )
    
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    risk_percentage = models.FloatField()
    
    # Risk Factors
    volatility_score = models.FloatField(help_text="0-100 volatility score")
    liquidity_score = models.FloatField(help_text="0-100 liquidity score")
    market_condition_score = models.FloatField(help_text="0-100 market condition score")
    
    # Mitigations
    max_position_size = models.IntegerField(help_text="Maximum shares to buy")
    recommended_stop_loss = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Report
    assessment_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Risk Assessment: {self.recommendation.stock.symbol}"


class AlternativeInvestment(models.Model):
    """Alternative Investment Suggestions"""
    
    INVESTMENT_TYPE_CHOICES = [
        ('ETF', 'ETF'),
        ('MUTUAL_FUND', 'Mutual Fund'),
        ('BOND', 'Bond'),
        ('EQUITY', 'Equity'),
        ('INDEX', 'Index Fund'),
    ]
    
    recommendation = models.ForeignKey(
        TradeRecommendation,
        on_delete=models.CASCADE,
        related_name='alternatives'
    )
    
    name = models.CharField(max_length=255)
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPE_CHOICES)
    
    description = models.TextField()
    expected_return = models.FloatField()
    risk_level = models.CharField(max_length=20)
    liquidity = models.CharField(max_length=20)
    
    reason = models.TextField(help_text="Why this is a good alternative")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.investment_type})"

class PaperTrade(models.Model):
    """Paper Trading - Practice trades without real money"""
    
    SIDE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    EXIT_TYPE_CHOICES = [
        ('TARGET', 'Target Hit'),
        ('STOPLOSS', 'Stop Loss Hit'),
        ('MANUAL', 'Manual Close'),
        ('PENDING', 'Pending'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='paper_trades')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='paper_trades')
    
    # Trade Details
    side = models.CharField(max_length=10, choices=SIDE_CHOICES, default='BUY')
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    entry_date = models.DateTimeField()
    entry_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # quantity * entry_price
    
    # Risk Management
    stop_loss = models.DecimalField(max_digits=10, decimal_places=2)
    target_1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Exit Details
    exit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    exit_date = models.DateTimeField(null=True, blank=True)
    exit_type = models.CharField(max_length=20, choices=EXIT_TYPE_CHOICES, default='PENDING')
    
    # Performance (calculated with real market prices)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Latest market price
    unrealized_pnl = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Live P&L
    profit_loss = models.DecimalField(max_digits=12, decimal_places=2, null=True)  # Closed P&L
    profit_loss_percent = models.FloatField(null=True)
    
    # Costs
    entry_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exit_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status and Tags
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    notes = models.TextField(blank=True)
    
    # Risk Metrics
    risk_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Entry to stop loss
    risk_percent = models.FloatField(default=0)  # Risk as % of capital
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['portfolio', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['portfolio', 'status']),
        ]
    
    def __str__(self):
        return f"Paper Trade: {self.side} {self.quantity} {self.stock.symbol} @ {self.entry_price}"


class SmartAlert(models.Model):
    """Smart Alerts for price, volume, and trend changes"""
    
    ALERT_TYPE_CHOICES = [
        ('PRICE_LEVEL', 'Price Level'),
        ('VOLUME_SPIKE', 'Volume Spike'),
        ('TREND_CHANGE', 'Trend Change'),
        ('SUPPORT_BREAK', 'Support Break'),
        ('RESISTANCE_BREAK', 'Resistance Break'),
        ('BOLLINGER_BAND', 'Bollinger Band'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRIGGERED', 'Triggered'),
        ('DISMISSED', 'Dismissed'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='smart_alerts')
    
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    condition = models.CharField(max_length=255, help_text="e.g., 'Price > 500' or 'Volume > 5M'")
    
    # Alert Thresholds
    target_value = models.FloatField()
    trigger_value = models.FloatField(null=True, blank=True, help_text="Actual value when triggered")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    triggered_at = models.DateTimeField(null=True, blank=True)
    
    # User Notification
    send_email = models.BooleanField(default=True)
    send_notification = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock', 'status']),
            models.Index(fields=['alert_type']),
        ]
    
    def __str__(self):
        return f"Alert: {self.stock.symbol} - {self.alert_type} ({self.status})"


class MarketSummary(models.Model):
    """Daily Market Summary with trend and sentiment analysis"""
    
    SENTIMENT_CHOICES = [
        ('VERY_BULLISH', 'Very Bullish'),
        ('BULLISH', 'Bullish'),
        ('NEUTRAL', 'Neutral'),
        ('BEARISH', 'Bearish'),
        ('VERY_BEARISH', 'Very Bearish'),
    ]
    
    market_date = models.DateField(unique=True, db_index=True)
    
    # Market Overview
    gainers_count = models.IntegerField(default=0)
    losers_count = models.IntegerField(default=0)
    unchanged_count = models.IntegerField(default=0)
    
    # Market Indices (BSE Sensex, Nifty 50, etc.)
    market_trend = models.CharField(max_length=20)  # UP, DOWN, FLAT
    market_sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES)
    
    # Key Metrics
    average_volume = models.BigIntegerField()
    volatility_index = models.FloatField(null=True, blank=True)
    sector_performance = models.JSONField(default=dict)  # {'IT': 1.5, 'FINANCE': -0.5, ...}
    
    # Analysis
    summary_text = models.TextField(help_text="Market summary explanation")
    key_levels = models.JSONField(default=dict)  # {'support': [100, 200], 'resistance': [300, 400]}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-market_date']
        indexes = [models.Index(fields=['-market_date'])]
    
    def __str__(self):
        return f"Market Summary: {self.market_date}"


class PortfolioHealth(models.Model):
    """Portfolio health analysis including risk, diversification, performance"""
    
    HEALTH_SCORE_CHOICES = [
        ('EXCELLENT', 'Excellent (>90)'),
        ('GOOD', 'Good (70-90)'),
        ('FAIR', 'Fair (50-70)'),
        ('POOR', 'Poor (30-50)'),
        ('CRITICAL', 'Critical (<30)'),
    ]
    
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE, related_name='health')
    
    # Overall Score
    health_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    health_status = models.CharField(max_length=20, choices=HEALTH_SCORE_CHOICES)
    
    # Performance Metrics
    total_profit_loss = models.DecimalField(max_digits=15, decimal_places=2)
    profit_loss_percent = models.FloatField()
    
    win_rate = models.FloatField(help_text="Percentage of winning trades")
    average_win = models.DecimalField(max_digits=12, decimal_places=2)
    average_loss = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Risk Metrics
    risk_level = models.CharField(max_length=20)
    max_drawdown = models.FloatField(help_text="Maximum peak-to-trough decline")
    sharpe_ratio = models.FloatField(null=True, blank=True)
    
    # Diversification
    sector_concentration = models.FloatField(help_text="Concentration in top sector (0-100)")
    number_of_holdings = models.IntegerField()
    largest_position_percent = models.FloatField()
    
    # Health Warnings
    warnings = models.JSONField(default=list)  # ['High concentration in IT', 'Large drawdown risk', ...]
    recommendations = models.JSONField(default=list)  # ['Diversify into finance', 'Take profits', ...]
    
    analyzed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-analyzed_at']
    
    def __str__(self):
        return f"Portfolio Health: {self.portfolio.name} ({self.health_status})"


class TradingMistake(models.Model):
    """Trading mistakes detected for learning"""
    
    MISTAKE_CATEGORY_CHOICES = [
        ('ENTRY_TIMING', 'Poor Entry Timing'),
        ('EXIT_TIMING', 'Poor Exit Timing'),
        ('POSITION_SIZE', 'Wrong Position Size'),
        ('RISK_MANAGEMENT', 'Risk Management Failure'),
        ('DISCIPLINE', 'Discipline Violation'),
        ('EMOTIONAL', 'Emotional Decision'),
        ('ANALYSIS_ERROR', 'Analysis Error'),
        ('MARKET_CONDITION', 'Ignored Market Condition'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low Impact'),
        ('MEDIUM', 'Medium Impact'),
        ('HIGH', 'High Impact'),
        ('CRITICAL', 'Critical Impact'),
    ]
    
    trade_order = models.ForeignKey(
        TradeOrder,
        on_delete=models.CASCADE,
        related_name='detected_mistakes'
    )
    
    mistake_category = models.CharField(max_length=30, choices=MISTAKE_CATEGORY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    description = models.TextField()
    impact = models.DecimalField(max_digits=12, decimal_places=2, help_text="Loss amount")
    
    lesson_learned = models.TextField(help_text="What to do next time")
    prevention_tip = models.CharField(max_length=255)
    
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-detected_at']
        indexes = [models.Index(fields=['trade_order', '-detected_at'])]
    
    def __str__(self):
        return f"{self.mistake_category}: {self.trade_order.stock.symbol}"


class AIExplanation(models.Model):
    """AI Explanations for transparency"""
    
    EXPLANATION_TYPE_CHOICES = [
        ('SIGNAL_GENERATION', 'Signal Generation'),
        ('RISK_ANALYSIS', 'Risk Analysis'),
        ('PORTFOLIO_DECISION', 'Portfolio Decision'),
        ('ALERT_TRIGGER', 'Alert Trigger'),
        ('MISTAKE_DETECTION', 'Mistake Detection'),
        ('MARKET_SENTIMENT', 'Market Sentiment'),
    ]
    
    # Reference
    related_model = models.CharField(max_length=50)  # 'TradeRecommendation', 'PortfolioHealth', etc.
    related_id = models.IntegerField()
    
    explanation_type = models.CharField(max_length=30, choices=EXPLANATION_TYPE_CHOICES)
    
    # Explanation Content
    simple_explanation = models.TextField(help_text="Beginner-friendly explanation")
    detailed_explanation = models.TextField(help_text="Detailed technical explanation for pros")
    
    # Decision Factors
    key_factors = models.JSONField(default=list)  # ['RSI > 70', 'Volume spike', ...]
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Links to Indicators
    indicators_used = models.JSONField(default=list)  # ['RSI', 'VWAP', 'Bollinger Bands']
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['related_model', 'related_id']),
            models.Index(fields=['explanation_type']),
        ]
    
    def __str__(self):
        return f"Explanation: {self.explanation_type}"


class InvestmentPlan(models.Model):
    """Investment plan suggestions based on user goals"""
    
    INVESTMENT_GOAL_CHOICES = [
        ('WEALTH_CREATION', 'Wealth Creation'),
        ('RETIREMENT', 'Retirement Planning'),
        ('EDUCATION', 'Education Fund'),
        ('HOME_PURCHASE', 'Home Purchase'),
        ('EMERGENCY_FUND', 'Emergency Fund'),
        ('SHORT_TERM_GAINS', 'Short-Term Gains'),
    ]
    
    TIME_HORIZON_CHOICES = [
        ('3_MONTHS', '3 Months'),
        ('6_MONTHS', '6 Months'),
        ('1_YEAR', '1 Year'),
        ('3_YEARS', '3 Years'),
        ('5_YEARS', '5 Years'),
        ('10PLUS_YEARS', '10+ Years'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='investment_plans')
    
    goal = models.CharField(max_length=30, choices=INVESTMENT_GOAL_CHOICES)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    time_horizon = models.CharField(max_length=20, choices=TIME_HORIZON_CHOICES)
    
    # Risk Appetite
    risk_tolerance = models.CharField(max_length=20)  # LOW, MEDIUM, HIGH
    
    # Recommended Allocation
    equity_percent = models.FloatField()
    debt_percent = models.FloatField()
    alternatives_percent = models.FloatField()
    
    # Stock Suggestions
    recommended_stocks = models.JSONField(default=list)  # [{'symbol': 'RELIANCE', 'reason': '...', 'weight': 20}]
    
    # Plan Details
    plan_description = models.TextField()
    expected_returns = models.FloatField(help_text="Annual return expectation %")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Plan: {self.goal} - {self.target_amount}"


# ============================================================================
# GROWW INTEGRATION MODELS
# ============================================================================

class GrowwAccount(models.Model):
    """Groww Account Integration"""
    
    # Account identification
    groww_user_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Account info
    account_name = models.CharField(max_length=255)
    account_type = models.CharField(
        max_length=50,
        choices=[
            ('INDIVIDUAL', 'Individual'),
            ('JOINT', 'Joint'),
            ('HUF', 'HUF'),
            ('CORPORATE', 'Corporate'),
        ]
    )
    
    # Pan and verification
    pan = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Sync tracking
    last_synced = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SYNCING', 'Syncing'),
            ('SYNCED', 'Synced'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.account_name} ({self.groww_user_id})"


class GrowwHolding(models.Model):
    """Groww Stock Holdings"""
    
    # Account reference
    groww_account = models.ForeignKey(
        GrowwAccount,
        on_delete=models.CASCADE,
        related_name='holdings'
    )
    
    # Stock details
    stock_symbol = models.CharField(max_length=20)
    stock_name = models.CharField(max_length=255)
    isin = models.CharField(max_length=20, blank=True)
    
    # Holding details
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    average_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    current_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    
    # P&L tracking
    total_invested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gain_loss_percent = models.FloatField(default=0)
    
    # Additional info
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    
    # Metadata
    is_favourite = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('groww_account', 'stock_symbol')
        ordering = ['-current_value']
        indexes = [
            models.Index(fields=['groww_account', 'stock_symbol']),
            models.Index(fields=['stock_symbol']),
        ]
    
    def __str__(self):
        return f"{self.groww_account.account_name} - {self.stock_symbol}"


class GrowwMutualFund(models.Model):
    """Groww Mutual Fund Holdings"""
    
    # Account reference
    groww_account = models.ForeignKey(
        GrowwAccount,
        on_delete=models.CASCADE,
        related_name='mutual_funds'
    )
    
    # MF details
    mf_isin = models.CharField(max_length=20, unique=True)
    mf_name = models.CharField(max_length=255)
    mf_category = models.CharField(
        max_length=100,
        choices=[
            ('EQUITY', 'Equity'),
            ('DEBT', 'Debt'),
            ('HYBRID', 'Hybrid'),
            ('LIQUID', 'Liquid'),
            ('GOLD', 'Gold'),
            ('INTERNATIONAL', 'International'),
        ]
    )
    
    # Holding details
    units = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    nav = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Investment value
    invested_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gain_loss_percent = models.FloatField(default=0)
    
    # Fund details
    fund_house = models.CharField(max_length=255, blank=True)
    expense_ratio = models.FloatField(default=0, help_text="Annual expense ratio %")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('groww_account', 'mf_isin')
        ordering = ['-current_value']
    
    def __str__(self):
        return f"{self.groww_account.account_name} - {self.mf_name}"


class GrowwPortfolioSummary(models.Model):
    """Groww Portfolio Summary"""
    
    groww_account = models.OneToOneField(
        GrowwAccount,
        on_delete=models.CASCADE,
        related_name='portfolio_summary'
    )
    
    # Holdings summary
    total_invested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    current_portfolio_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_gain_loss = models.DecimalField(max_digits=15, decimal_places=2)
    total_gain_loss_percent = models.FloatField()
    
    # Breakdown
    equity_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mutual_fund_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Holdings count
    total_holdings = models.IntegerField(default=0)
    total_mutual_funds = models.IntegerField(default=0)
    
    # Risk metrics
    portfolio_beta = models.FloatField(default=0)
    volatility = models.FloatField(default=0)
    sharpe_ratio = models.FloatField(default=0)
    
    # Allocation
    equity_allocation_percent = models.FloatField(default=0)
    debt_allocation_percent = models.FloatField(default=0)
    others_allocation_percent = models.FloatField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Portfolio Summary - {self.groww_account.account_name}"


class GrowwTransaction(models.Model):
    """Groww Buy/Sell Transactions"""
    
    TRANSACTION_TYPE = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('DIVIDEND', 'Dividend'),
        ('BONUS', 'Bonus'),
        ('SPLIT', 'Split'),
    ]
    
    groww_holding = models.ForeignKey(
        GrowwHolding,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    transaction_date = models.DateField()
    transaction_time = models.TimeField(null=True, blank=True)
    
    # Additional details
    brokerage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['groww_holding', 'transaction_date']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.groww_holding.stock_symbol} on {self.transaction_date}"


class GrowwImportLog(models.Model):
    """Log for Groww data imports"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    
    groww_account = models.ForeignKey(
        GrowwAccount,
        on_delete=models.CASCADE,
        related_name='import_logs'
    )
    
    import_type = models.CharField(
        max_length=50,
        choices=[
            ('HOLDINGS', 'Holdings'),
            ('MUTUAL_FUNDS', 'Mutual Funds'),
            ('TRANSACTIONS', 'Transactions'),
            ('FULL', 'Full Sync'),
        ]
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Import details
    records_imported = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.groww_account.account_name} - {self.import_type} ({self.status})"


# ========== MARKET DATA MODELS ==========

class StockPriceSnapshot(models.Model):
    """Current and historical stock price snapshots"""
    
    DATA_SOURCE_CHOICES = [
        ('YFINANCE', 'Yahoo Finance'),
        ('NSE', 'NSE Official'),
        ('BSE', 'BSE Official'),
    ]
    
    symbol = models.CharField(max_length=20, db_index=True)
    
    # Price data
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    previous_close = models.DecimalField(max_digits=10, decimal_places=2)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Volume and value
    volume = models.BigIntegerField(default=0)
    traded_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Additional metrics
    market_cap = models.BigIntegerField(null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Meta data
    data_source = models.CharField(max_length=20, choices=DATA_SOURCE_CHOICES, default='YFINANCE')
    data_freshness = models.CharField(
        max_length=20,
        choices=[
            ('LIVE', 'Live'),
            ('DELAYED', 'Delayed'),
            ('EOD', 'End of Day'),
        ],
        default='EOD'
    )
    market_status = models.CharField(
        max_length=20,
        choices=[
            ('OPEN', 'Market Open'),
            ('CLOSED', 'Market Closed'),
            ('HOLIDAY', 'Holiday'),
        ],
        default='CLOSED'
    )
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['symbol', '-timestamp']),
            models.Index(fields=['data_freshness', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - {self.current_price} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


class MarketIndex(models.Model):
    """Major market indices"""
    
    INDEX_CHOICES = [
        ('SENSEX', 'BSE Sensex'),
        ('NIFTY50', 'Nifty 50'),
        ('NIFTYNXT50', 'Nifty Next 50'),
        ('MIDCAP50', 'Nifty Midcap 50'),
        ('SMALLCAP50', 'Nifty Smallcap 50'),
        ('INDIAVIX', 'India VIX'),
    ]
    
    index_name = models.CharField(max_length=50, choices=INDEX_CHOICES, unique=True)
    symbol = models.CharField(max_length=20, unique=True)
    
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    previous_close = models.DecimalField(max_digits=15, decimal_places=2)
    change_points = models.DecimalField(max_digits=10, decimal_places=2)
    change_percent = models.DecimalField(max_digits=8, decimal_places=2)
    
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['index_name']
    
    def __str__(self):
        return f"{self.index_name}: {self.current_value}"


class SectorPerformance(models.Model):
    """Sector-wise market performance"""
    
    SECTOR_CHOICES = [
        ('IT', 'Information Technology'),
        ('PHARMA', 'Pharmaceuticals'),
        ('BANK', 'Banking'),
        ('FINANCE', 'Financial Services'),
        ('FMCG', 'Consumer Goods'),
        ('REALTY', 'Real Estate'),
        ('ENERGY', 'Energy'),
        ('METALS', 'Metals'),
        ('AUTO', 'Automobile'),
        ('TELECOM', 'Telecom'),
    ]
    
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES, unique=True)
    index_symbol = models.CharField(max_length=50)
    
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    change_percent = models.DecimalField(max_digits=8, decimal_places=2)
    
    top_gainers = models.JSONField(default=list, blank=True)  # List of symbol:change pairs
    top_losers = models.JSONField(default=list, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sector']
        verbose_name_plural = "Sector Performances"
    
    def __str__(self):
        return f"{self.sector}: {self.change_percent}%"


# ========== AI SIGNAL MODELS ==========

class TradeSignal(models.Model):
    """AI-generated trading signals with confidence metrics"""
    
    SIGNAL_CHOICES = [
        ('STRONG_BUY', 'Strong Buy'),
        ('BUY', 'Buy'),
        ('NEUTRAL', 'Neutral'),
        ('SELL', 'Sell'),
        ('STRONG_SELL', 'Strong Sell'),
    ]
    
    QUALITY_CHOICES = [
        ('HIGH', 'High Quality'),
        ('ADEQUATE', 'Adequate'),
        ('LOW', 'Low Quality'),
        ('FAILED', 'Analysis Failed'),
    ]
    
    symbol = models.CharField(max_length=20, db_index=True)
    signal = models.CharField(max_length=20, choices=SIGNAL_CHOICES)
    
    # Confidence metrics
    confidence = models.DecimalField(max_digits=4, decimal_places=3)  # 0.000 - 1.000
    confidence_min = models.DecimalField(max_digits=4, decimal_places=3)
    confidence_max = models.DecimalField(max_digits=4, decimal_places=3)
    
    # Trading levels
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    stop_loss = models.DecimalField(max_digits=10, decimal_places=2)
    risk_reward_ratio = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Analysis factors
    technical_patterns = models.JSONField(default=list)
    volume_signal = models.CharField(max_length=20, default='NEUTRAL')
    trend = models.CharField(max_length=20, default='NEUTRAL')
    momentum = models.CharField(max_length=20, default='NEUTRAL')
    volatility = models.CharField(max_length=20, default='MODERATE')
    
    # Probability analysis
    uptrend_probability = models.DecimalField(max_digits=4, decimal_places=3, default=0.5)
    breakout_probability = models.DecimalField(max_digits=4, decimal_places=3, default=0.5)
    support_hold_probability = models.DecimalField(max_digits=4, decimal_places=3, default=0.5)
    
    # Risk warnings
    warning_flags = models.JSONField(default=list)
    
    # Quality metrics
    data_quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='ADEQUATE')
    confidence_reason = models.TextField()
    disclaimer = models.TextField(
        default='This is a probability-based analysis, NOT a guarantee. Always use stop-losses.'
    )
    
    # Timestamps
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['symbol', '-generated_at']),
            models.Index(fields=['signal', '-generated_at']),
        ]
        unique_together = ('symbol', 'generated_at')  # One signal per symbol per time
    
    def __str__(self):
        return f"{self.symbol} - {self.signal} ({self.confidence})"


class SignalHistory(models.Model):
    """Track signal accuracy and performance over time"""
    
    signal = models.ForeignKey(TradeSignal, on_delete=models.CASCADE, related_name='history')
    
    # Entry tracking
    entry_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entry_time = models.DateTimeField(null=True, blank=True)
    
    # Exit tracking
    exit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    exit_reason = models.CharField(
        max_length=50,
        choices=[
            ('TARGET_HIT', 'Target Hit'),
            ('STOP_LOSS_HIT', 'Stop Loss Hit'),
            ('MANUAL_EXIT', 'Manual Exit'),
            ('PENDING', 'Pending'),
        ],
        default='PENDING'
    )
    
    # Performance metrics
    profit_loss_rupees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit_loss_percent = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Signal accuracy
    signal_accuracy = models.BooleanField(null=True, blank=True)  # True if predicted direction was correct
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.signal.symbol} - {self.exit_reason}"


class DataSource(models.Model):
    """Track data source quality and availability"""
    
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    
    # Data types provided
    provides_price = models.BooleanField(default=False)
    provides_fundamentals = models.BooleanField(default=False)
    provides_technical = models.BooleanField(default=False)
    provides_news = models.BooleanField(default=False)
    provides_corporate_actions = models.BooleanField(default=False)
    
    # Availability
    is_free = models.BooleanField(default=True)
    requires_api_key = models.BooleanField(default=False)
    
    # Data freshness
    update_frequency = models.CharField(
        max_length=50,
        choices=[
            ('REAL_TIME', 'Real Time'),
            ('INTRADAY', 'Intraday'),
            ('END_OF_DAY', 'End of Day'),
            ('WEEKLY', 'Weekly'),
            ('MONTHLY', 'Monthly'),
        ],
        default='END_OF_DAY'
    )
    
    # Health tracking
    last_checked = models.DateTimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    availability_percent = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name