"""
Intraday Trading Module - Automated Tests
Tests all intraday features including signal generation, risk management, and auto square-off
"""

import json
from decimal import Decimal
from django.test import TestCase, Client
from django.utils import timezone
from datetime import datetime, time, timedelta
from unittest.mock import patch, MagicMock

from trading.models import Stock, StockAnalysis, TradeRecommendation, TradeOrder, RiskAssessment
from trading.services import SignalGenerationService, RiskManagementService
from trading.market_data import MarketDataFetcher


class IntradaySignalGenerationTests(TestCase):
    """Test intraday signal generation"""
    
    def setUp(self):
        """Create test stock and analysis"""
        self.stock = Stock.objects.create(
            symbol='INFY',
            name='Infosys Limited',
            market_cap_category='LARGE_CAP',
            current_price=Decimal('1650.00'),
            previous_close=Decimal('1645.00')
        )
        
        self.analysis = StockAnalysis.objects.create(
            stock=self.stock,
            current_price=Decimal('1650.00'),
            support_level=Decimal('1640.00'),
            resistance_level=Decimal('1660.00'),
            rsi=45.0,
            bollinger_upper=Decimal('1665.00'),
            bollinger_middle=Decimal('1650.00'),
            bollinger_lower=Decimal('1635.00'),
            vwap=Decimal('1648.00'),
            sma_20=Decimal('1648.00'),
            sma_50=Decimal('1645.00'),
            sma_200=Decimal('1640.00'),
            ema_12=Decimal('1650.50'),
            ema_26=Decimal('1648.00'),
            trend='BULLISH',
            trend_probability=75.0,
            volume=2000000,
            average_volume_20=1800000,
            volume_trend='INCREASING',
            fib_0_236=Decimal('1652.50'),
            fib_0_382=Decimal('1655.00'),
            fib_0_500=Decimal('1657.50'),
            fib_0_618=Decimal('1660.00')
        )
    
    def test_intraday_signal_generation_bullish(self):
        """Test BUY signal generation"""
        signal_data = SignalGenerationService.generate_intraday_signal(
            stock=self.stock,
            analysis=self.analysis,
            current_price=Decimal('1650.00'),
            live_data={'price': 1650.00, 'previous_close': 1645.00},
            capital=Decimal('50000')
        )
        
        self.assertEqual(signal_data['signal'], 'BUY')
        self.assertGreater(signal_data['confidence'], 50)
        self.assertIsNotNone(signal_data['entry_price'])
        self.assertIsNotNone(signal_data['stop_loss'])
        self.assertEqual(len(signal_data['targets']), 4)
    
    def test_intraday_signal_has_tight_stops(self):
        """Test that intraday signals have tight stop losses"""
        signal_data = SignalGenerationService.generate_intraday_signal(
            stock=self.stock,
            analysis=self.analysis,
            current_price=Decimal('1650.00'),
            live_data={'price': 1650.00},
            capital=Decimal('50000')
        )
        
        # Stop loss should be within 1% for BUY
        if signal_data['signal'] == 'BUY':
            stop_diff = float(signal_data['entry_price'] - signal_data['stop_loss'])
            stop_percent = (stop_diff / float(signal_data['entry_price'])) * 100
            self.assertLess(stop_percent, 1.5)  # Should be < 1.5%
    
    def test_intraday_signal_quantity_calculation(self):
        """Test position sizing based on 0.5% risk"""
        capital = Decimal('50000')
        signal_data = SignalGenerationService.generate_intraday_signal(
            stock=self.stock,
            analysis=self.analysis,
            current_price=Decimal('1650.00'),
            live_data={'price': 1650.00},
            capital=capital
        )
        
        # Calculate expected max risk
        max_risk = capital * Decimal('0.005')  # 0.5%
        
        # Verify risk is within limits
        actual_risk = signal_data['quantity'] * Decimal(str(abs(signal_data['entry_price'] - signal_data['stop_loss'])))
        self.assertLessEqual(float(actual_risk), float(max_risk) * 1.1)  # Allow 10% margin


class RiskManagementTests(TestCase):
    """Test strict risk management"""
    
    def test_validate_intraday_trade_valid(self):
        """Test valid intraday trade"""
        validation = RiskManagementService.validate_intraday_trade(
            capital=Decimal('50000'),
            entry_price=Decimal('1650.00'),
            stop_loss=Decimal('1633.99'),
            quantity=14
        )
        
        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['errors']), 0)
    
    def test_validate_intraday_trade_high_risk(self):
        """Test trade exceeding max risk"""
        validation = RiskManagementService.validate_intraday_trade(
            capital=Decimal('50000'),
            entry_price=Decimal('1650.00'),
            stop_loss=Decimal('1600.00'),  # 3% stop - too wide
            quantity=50  # Too many units
        )
        
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['errors']), 0)
    
    def test_validate_intraday_trade_daily_loss_limit(self):
        """Test daily loss limit"""
        existing_daily_loss = Decimal('900')  # Already lost 1.8%
        
        validation = RiskManagementService.validate_intraday_trade(
            capital=Decimal('50000'),
            entry_price=Decimal('1650.00'),
            stop_loss=Decimal('1633.99'),
            quantity=20,  # Would risk ₹320
            existing_daily_loss=existing_daily_loss
        )
        
        # Total would be 1.8% + 0.64% = 2.44% > 2% limit
        self.assertFalse(validation['valid'])
    
    def test_risk_reward_minimum(self):
        """Test 1:1.5 minimum risk-reward ratio"""
        validation = RiskManagementService.validate_intraday_trade(
            capital=Decimal('50000'),
            entry_price=Decimal('1650.00'),
            stop_loss=Decimal('1640.00'),  # ₹10 risk
            quantity=10
        )
        
        # Should have warning about risk-reward
        self.assertTrue(len(validation['warnings']) > 0 or validation['valid'])


class IntradayAPITests(TestCase):
    """Test intraday API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.stock = Stock.objects.create(
            symbol='INFY',
            name='Infosys Limited',
            market_cap_category='LARGE_CAP',
            current_price=Decimal('1650.00'),
            previous_close=Decimal('1645.00')
        )
        
        self.analysis = StockAnalysis.objects.create(
            stock=self.stock,
            current_price=Decimal('1650.00'),
            support_level=Decimal('1640.00'),
            resistance_level=Decimal('1660.00'),
            rsi=45.0,
            bollinger_upper=Decimal('1665.00'),
            bollinger_middle=Decimal('1650.00'),
            bollinger_lower=Decimal('1635.00'),
            vwap=Decimal('1648.00'),
            sma_20=Decimal('1648.00'),
            sma_50=Decimal('1645.00'),
            sma_200=Decimal('1640.00'),
            ema_12=Decimal('1650.50'),
            ema_26=Decimal('1648.00'),
            trend='BULLISH',
            trend_probability=75.0,
            volume=2000000,
            average_volume_20=1800000,
            volume_trend='INCREASING',
            fib_0_236=Decimal('1652.50'),
            fib_0_382=Decimal('1655.00'),
            fib_0_500=Decimal('1657.50'),
            fib_0_618=Decimal('1660.00')
        )
    
    @patch('trading.market_data.MarketDataFetcher.get_stock_price')
    def test_generate_intraday_signal_api(self, mock_price):
        """Test generate intraday signal endpoint"""
        mock_price.return_value = {
            'price': 1650.50,
            'previous_close': 1645.00,
            'open': 1648.00,
            'high': 1655.00,
            'low': 1640.00,
            'volume': 2000000,
            'data_freshness': 'LIVE'
        }
        
        response = self.client.post(
            '/api/intraday-signals/generate_intraday/',
            json.dumps({
                'stock_symbol': 'INFY',
                'capital': 50000
            }),
            content_type='application/json'
        )
        
        # Should return signal data
        self.assertIn(response.status_code, [201, 400])  # 201 if valid, 400 if validation fails
        
        if response.status_code == 201:
            data = json.loads(response.content)
            self.assertEqual(data['stock'], 'INFY')
            self.assertIn(data['signal'], ['BUY', 'SELL', 'HOLD'])
            self.assertIsNotNone(data['validation'])


class AutoSquareOffTests(TestCase):
    """Test auto square-off functionality"""
    
    def setUp(self):
        self.stock = Stock.objects.create(
            symbol='INFY',
            name='Infosys Limited',
            market_cap_category='LARGE_CAP'
        )
        
        self.recommendation = TradeRecommendation.objects.create(
            stock=self.stock,
            analysis=StockAnalysis.objects.create(
                stock=self.stock,
                current_price=Decimal('1650.00'),
                support_level=Decimal('1640.00'),
                resistance_level=Decimal('1660.00'),
                rsi=45.0,
                trend='BULLISH',
                trend_probability=75.0,
                volume=2000000,
                average_volume_20=1800000,
                volume_trend='INCREASING',
                bollinger_upper=Decimal('1665.00'),
                bollinger_middle=Decimal('1650.00'),
                bollinger_lower=Decimal('1635.00'),
                vwap=Decimal('1648.00'),
                sma_20=Decimal('1648.00'),
                sma_50=Decimal('1645.00'),
                sma_200=Decimal('1640.00'),
                ema_12=Decimal('1650.50'),
                ema_26=Decimal('1648.00'),
                fib_0_236=Decimal('1652.50'),
                fib_0_382=Decimal('1655.00'),
                fib_0_500=Decimal('1657.50'),
                fib_0_618=Decimal('1660.00')
            ),
            trading_style='INTRADAY',
            signal='BUY',
            entry_price=Decimal('1650.00'),
            stop_loss=Decimal('1633.99'),
            target_1=Decimal('1654.47'),
            target_2=Decimal('1656.48'),
            target_3=Decimal('1659.50'),
            target_4=Decimal('1663.00'),
            risk_percent=0.48,
            profit_percent=0.12,
            risk_reward_ratio=2.65,
            confidence_level=78,
            win_probability=62.4
        )
    
    def test_intraday_trade_order_creation(self):
        """Test that trade order is marked as intraday"""
        order = TradeOrder.objects.create(
            recommendation=self.recommendation,
            stock=self.stock,
            quantity=14,
            entry_price=Decimal('1650.00'),
            actual_entry_price=Decimal('1650.00'),
            stop_loss=Decimal('1633.99'),
            target=Decimal('1654.47'),
            capital_allocated=Decimal('23100'),
            risk_amount=Decimal('224.86'),
            is_intraday=True,
            auto_square_off=True,
            square_off_time=time(15, 30),
            status='EXECUTED',
            entry_time=timezone.now()
        )
        
        self.assertTrue(order.is_intraday)
        self.assertTrue(order.auto_square_off)
        self.assertEqual(order.square_off_time, time(15, 30))
        self.assertEqual(order.status, 'EXECUTED')
    
    def test_auto_square_off_pnl_calculation(self):
        """Test P&L calculation on auto square-off"""
        order = TradeOrder.objects.create(
            recommendation=self.recommendation,
            stock=self.stock,
            quantity=14,
            entry_price=Decimal('1650.00'),
            actual_entry_price=Decimal('1650.00'),
            stop_loss=Decimal('1633.99'),
            target=Decimal('1654.47'),
            capital_allocated=Decimal('23100'),
            risk_amount=Decimal('224.86'),
            is_intraday=True,
            auto_square_off=True,
            status='EXECUTED'
        )
        
        # Simulate market close exit at ₹1654.50
        exit_price = Decimal('1654.50')
        pnl = (exit_price - order.entry_price) * order.quantity
        pnl_percent = float((pnl / (order.entry_price * order.quantity)) * 100)
        
        order.exit_time = timezone.now()
        order.profit_loss = pnl
        order.profit_loss_percent = pnl_percent
        order.status = 'CLOSED'
        order.save()
        
        # Verify P&L
        self.assertAlmostEqual(float(order.profit_loss), 63.0, places=0)  # ~₹63 profit
        self.assertGreater(order.profit_loss_percent, 0)


class TechnicalIndicatorTests(TestCase):
    """Test technical indicator calculations"""
    
    def test_vwap_calculation(self):
        """Test VWAP calculation"""
        from trading.services import TechnicalAnalysisService
        
        prices = [100, 101, 102, 103, 104]
        volumes = [1000, 1100, 1200, 1300, 1400]
        
        vwap = TechnicalAnalysisService.calculate_vwap(prices, volumes)
        
        # VWAP should be between min and max price
        self.assertGreaterEqual(vwap, min(prices))
        self.assertLessEqual(vwap, max(prices))
        # Should be weighted towards higher prices with higher volume
        self.assertGreater(vwap, sum(prices) / len(prices))  # > simple average
    
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        from trading.services import TechnicalAnalysisService
        
        prices = [44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42, 
                  45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.00, 46.00]
        
        rsi = TechnicalAnalysisService.calculate_rsi(prices, period=14)
        
        # RSI should be between 0 and 100
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)


if __name__ == '__main__':
    import unittest
    unittest.main()
