"""
Groww Integration Models for KVK Trading System
Handles Groww portfolio import and data synchronization
"""

from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime


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
    isin = models.CharField(max_length=20, blank=True)  # ISIN code
    
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
    
    def calculate_values(self):
        """Calculate current value and gains"""
        self.total_invested = self.quantity * self.average_cost
        self.current_value = self.quantity * self.current_price
        self.gain_loss = self.current_value - self.total_invested
        self.gain_loss_percent = (
            (self.gain_loss / self.total_invested * 100)
            if self.total_invested > 0 else 0
        )


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
    """Groww Portfolio Aggregated Summary"""
    
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
