"""
Tests for KVK Trading System
"""

from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal

from trading.models import Stock, StockAnalysis, TradeRecommendation, Portfolio
from trading.services import (
    TechnicalAnalysisService,
    RiskManagementService,
    TradeRecommendationService
)


class StockTestCase(TestCase):
    def setUp(self):
        Stock.objects.create(
            symbol='TEST',
            name='Test Company',
            market_cap=1000000000,
            market_cap_category='MID_CAP',
            current_price=100.00,
            previous_close=99.00
        )

    def test_stock_creation(self):
        stock = Stock.objects.get(symbol='TEST')
        self.assertEqual(stock.name, 'Test Company')
        self.assertEqual(stock.market_cap_category, 'MID_CAP')


class TechnicalAnalysisTestCase(TestCase):
    def test_bollinger_bands(self):
        prices = [100, 102, 101, 103, 102, 104, 103, 105, 104, 106,
                  105, 107, 106, 108, 107, 109, 108, 110, 109, 111]
        
        upper, middle, lower = TechnicalAnalysisService.calculate_bollinger_bands(prices, 20)
        
        self.assertIsNotNone(upper)
        self.assertIsNotNone(middle)
        self.assertIsNotNone(lower)
        self.assertGreater(upper, middle)
        self.assertGreater(middle, lower)

    def test_rsi(self):
        prices = [44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42,
                  45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.00, 46.03]
        
        rsi = TechnicalAnalysisService.calculate_rsi(prices, 14)
        
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)

    def test_moving_average(self):
        prices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        ma = TechnicalAnalysisService.calculate_moving_average(prices, 5)
        
        self.assertEqual(ma, 8.0)

    def test_fibonacci_levels(self):
        levels = TechnicalAnalysisService.calculate_fibonacci_levels(100, 80)
        
        self.assertEqual(levels['0'], 100)
        self.assertEqual(levels['1'], 80)
        self.assertGreater(levels['0.618'], levels['0.382'])


class RiskManagementTestCase(TestCase):
    def test_quantity_calculation(self):
        capital = Decimal('100000')
        entry_price = Decimal('500')
        stop_loss = Decimal('490')
        
        quantity = RiskManagementService.calculate_quantity(
            capital, entry_price, stop_loss
        )
        
        self.assertGreater(quantity, 0)
        self.assertLess(quantity, 100)

    def test_risk_level_assessment(self):
        self.assertEqual(RiskManagementService.assess_risk_level(0.3), 'VERY_LOW')
        self.assertEqual(RiskManagementService.assess_risk_level(0.7), 'LOW')
        self.assertEqual(RiskManagementService.assess_risk_level(1.5), 'MODERATE')
        self.assertEqual(RiskManagementService.assess_risk_level(2.5), 'HIGH')
        self.assertEqual(RiskManagementService.assess_risk_level(3.5), 'VERY_HIGH')

    def test_risk_reward_ratio(self):
        entry = Decimal('100')
        stop_loss = Decimal('95')
        target = Decimal('110')
        
        ratio = RiskManagementService.calculate_risk_reward_ratio(
            entry, stop_loss, target
        )
        
        self.assertEqual(ratio, 2.0)


class PortfolioTestCase(TestCase):
    def setUp(self):
        Portfolio.objects.create(
            name='Test Portfolio',
            total_capital=Decimal('100000'),
            available_capital=Decimal('100000')
        )

    def test_portfolio_creation(self):
        portfolio = Portfolio.objects.get(name='Test Portfolio')
        self.assertEqual(portfolio.total_capital, Decimal('100000'))
        self.assertEqual(portfolio.available_capital, Decimal('100000'))
        self.assertEqual(portfolio.invested_capital, Decimal('0'))
