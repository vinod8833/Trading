"""
Paper Trading Module Test Suite
Comprehensive tests for paper trading functionality
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from trading.models import Stock, Portfolio, PaperTrade
from trading.services import PaperTradingService
from datetime import datetime


class PaperTradeModelTests(TestCase):
    """Test PaperTrade model"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.stock = Stock.objects.create(symbol='INFY', name='Infosys')
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            name='Test Portfolio',
            capital=Decimal('100000.00')
        )
    
    def test_create_paper_trade(self):
        """Test creating a paper trade"""
        trade = PaperTrade.objects.create(
            portfolio=self.portfolio,
            stock=self.stock,
            side='BUY',
            entry_price=Decimal('1500.00'),
            quantity=10,
            entry_date=datetime.now(),
            stop_loss=Decimal('1485.00'),
            target_1=Decimal('1530.00'),
            entry_value=Decimal('15000.00'),
            status='ACTIVE'
        )
        
        self.assertEqual(trade.stock.symbol, 'INFY')
        self.assertEqual(trade.quantity, 10)
        self.assertEqual(trade.status, 'ACTIVE')
        self.assertEqual(trade.side, 'BUY')
    
    def test_paper_trade_fields(self):
        """Test all paper trade fields"""
        trade = PaperTrade.objects.create(
            portfolio=self.portfolio,
            stock=self.stock,
            side='SELL',
            entry_price=Decimal('1600.00'),
            quantity=20,
            entry_date=datetime.now(),
            entry_value=Decimal('32000.00'),
            stop_loss=Decimal('1620.00'),
            target_1=Decimal('1570.00'),
            target_2=Decimal('1550.00'),
            target_3=Decimal('1530.00'),
            target_4=Decimal('1510.00'),
            entry_commission=Decimal('16.00'),
            risk_percent=1.25,
            status='ACTIVE'
        )
        
        self.assertEqual(trade.target_4, Decimal('1510.00'))
        self.assertEqual(trade.entry_commission, Decimal('16.00'))
        self.assertEqual(trade.risk_percent, 1.25)


class PaperTradingServiceTests(TestCase):
    """Test PaperTradingService methods"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.stock = Stock.objects.create(symbol='INFY', name='Infosys')
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            name='Test Portfolio',
            capital=Decimal('100000.00')
        )
    
    def test_create_paper_trade_success(self):
        """Test successful trade creation"""
        result = PaperTradingService.create_paper_trade(
            portfolio=self.portfolio,
            stock=self.stock,
            side='BUY',
            entry_price=Decimal('1500.00'),
            quantity=10,
            stop_loss=Decimal('1485.00'),
            target_1=Decimal('1530.00'),
            capital=Decimal('100000.00')
        )
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['trade'])
        self.assertEqual(result['trade'].quantity, 10)
    
    def test_create_paper_trade_insufficient_capital(self):
        """Test trade creation with insufficient capital"""
        result = PaperTradingService.create_paper_trade(
            portfolio=self.portfolio,
            stock=self.stock,
            side='BUY',
            entry_price=Decimal('20000.00'),
            quantity=100,
            stop_loss=Decimal('19000.00'),
            capital=Decimal('1000.00')
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Insufficient capital', ' '.join(result['errors']))
    
    def test_create_paper_trade_excessive_risk(self):
        """Test trade creation exceeding 0.5% risk limit"""
        result = PaperTradingService.create_paper_trade(
            portfolio=self.portfolio,
            stock=self.stock,
            side='BUY',
            entry_price=Decimal('1500.00'),
            quantity=500,  # Very large quantity to exceed risk
            stop_loss=Decimal('1400.00'),
            capital=Decimal('100000.00')
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Risk exceeds 0.5%', ' '.join(result['errors']))
    
    def test_close_paper_trade_buy(self):
        """Test closing a buy paper trade"""
        # Create trade
        trade = PaperTrade.objects.create(
            portfolio=self.portfolio,
            stock=self.stock,
            side='BUY',
            entry_price=Decimal('1500.00'),
            quantity=10,
            entry_date=datetime.now(),
            entry_value=Decimal('15000.00'),
            stop_loss=Decimal('1485.00'),
            entry_commission=Decimal('7.50'),
            status='ACTIVE'
        )
        
        # Close trade at profit
        result = PaperTradingService.close_paper_trade(
            paper_trade=trade,
            exit_price=Decimal('1550.00'),
            exit_type='TARGET'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['trade'].status, 'CLOSED')
        self.assertEqual(result['trade'].exit_type, 'TARGET')
        self.assertGreater(result['result']['net_pnl'], 0)
    
    def test_close_paper_trade_sell(self):
        """Test closing a sell paper trade"""
        trade = PaperTrade.objects.create(
            portfolio=self.portfolio,
            stock=self.stock,
            side='SELL',
            entry_price=Decimal('1600.00'),
            quantity=20,
            entry_date=datetime.now(),
            entry_value=Decimal('32000.00'),
            stop_loss=Decimal('1620.00'),
            entry_commission=Decimal('16.00'),
            status='ACTIVE'
        )
        
        result = PaperTradingService.close_paper_trade(
            paper_trade=trade,
            exit_price=Decimal('1550.00'),
            exit_type='TARGET'
        )
        
        self.assertTrue(result['success'])
        self.assertGreater(result['result']['net_pnl'], 0)
    
    def test_get_portfolio_stats(self):
        """Test getting portfolio statistics"""
        # Create and close some trades
        for i in range(5):
            trade = PaperTrade.objects.create(
                portfolio=self.portfolio,
                stock=self.stock,
                side='BUY',
                entry_price=Decimal('1500.00'),
                quantity=10,
                entry_date=datetime.now(),
                entry_value=Decimal('15000.00'),
                stop_loss=Decimal('1485.00'),
                entry_commission=Decimal('7.50'),
                exit_price=Decimal('1550.00') if i % 2 == 0 else Decimal('1450.00'),
                exit_commission=Decimal('7.50'),
                profit_loss=Decimal('500.00') if i % 2 == 0 else Decimal('-500.00'),
                status='CLOSED'
            )
        
        stats = PaperTradingService.get_portfolio_stats(self.portfolio)
        
        self.assertEqual(stats['total_trades'], 5)
        self.assertEqual(stats['closed_trades'], 5)
        self.assertEqual(stats['winners'], 3)
        self.assertEqual(stats['losers'], 2)


class PaperTradingAPITests(TestCase):
    """Test Paper Trading REST API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.stock = Stock.objects.create(symbol='INFY', name='Infosys')
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            name='Test Portfolio',
            capital=Decimal('100000.00')
        )
    
    def test_create_paper_trade_api(self):
        """Test create paper trade API endpoint"""
        response = self.client.post('/api/paper-trades/create_paper_trade/', {
            'portfolio_id': self.portfolio.id,
            'symbol': 'INFY',
            'side': 'BUY',
            'entry_price': 1500,
            'quantity': 10,
            'stop_loss': 1485,
            'target_1': 1530,
            'capital': 100000
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['success'])
    
    def test_active_trades_api(self):
        """Test active trades API endpoint"""
        # Create a trade
        PaperTrade.objects.create(
            portfolio=self.portfolio,
            stock=self.stock,
            side='BUY',
            entry_price=Decimal('1500.00'),
            quantity=10,
            entry_date=datetime.now(),
            entry_value=Decimal('15000.00'),
            stop_loss=Decimal('1485.00'),
            status='ACTIVE'
        )
        
        response = self.client.get(
            f'/api/paper-trades/active_trades/?portfolio_id={self.portfolio.id}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 1)
    
    def test_stats_api(self):
        """Test statistics API endpoint"""
        response = self.client.get(
            f'/api/paper-trades/stats/?portfolio_id={self.portfolio.id}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertIn('stats', response.data)


class PaperTradingValidationTests(TestCase):
    """Test paper trading validation logic"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.stock = Stock.objects.create(symbol='INFY', name='Infosys')
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            name='Test Portfolio',
            capital=Decimal('100000.00')
        )
    
    def test_stop_loss_too_tight(self):
        """Test validation for stop loss too tight"""
        result = PaperTradingService.create_paper_trade(
            portfolio=self.portfolio,
            stock=self.stock,
            side='BUY',
            entry_price=Decimal('1500.00'),
            quantity=10,
            stop_loss=Decimal('1499.50'),  # Only 0.03% away
            capital=Decimal('100000.00')
        )
        
        # Should have warning but still succeed
        self.assertTrue(result['success'])
    
    def test_stop_loss_too_wide(self):
        """Test validation for stop loss too wide"""
        result = PaperTradingService.create_paper_trade(
            portfolio=self.portfolio,
            stock=self.stock,
            side='BUY',
            entry_price=Decimal('1500.00'),
            quantity=10,
            stop_loss=Decimal('1350.00'),  # 10% away
            capital=Decimal('100000.00')
        )
        
        # Should have warning
        self.assertTrue(result['success'])
        self.assertGreater(len(result['warnings']), 0)


class PaperTradingIntegrationTests(TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.stock = Stock.objects.create(symbol='INFY', name='Infosys')
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            name='Test Portfolio',
            capital=Decimal('100000.00')
        )
    
    def test_complete_trading_lifecycle(self):
        """Test complete trade lifecycle: create, update, close"""
        # Step 1: Create trade
        create_result = PaperTradingService.create_paper_trade(
            portfolio=self.portfolio,
            stock=self.stock,
            side='BUY',
            entry_price=Decimal('1500.00'),
            quantity=10,
            stop_loss=Decimal('1485.00'),
            target_1=Decimal('1530.00'),
            capital=Decimal('100000.00')
        )
        self.assertTrue(create_result['success'])
        trade = create_result['trade']
        
        # Step 2: Update live price
        PaperTradingService.update_live_prices(self.portfolio)
        trade.refresh_from_db()
        self.assertIsNotNone(trade.current_price)
        
        # Step 3: Close trade
        close_result = PaperTradingService.close_paper_trade(
            paper_trade=trade,
            exit_price=Decimal('1520.00'),
            exit_type='MANUAL'
        )
        self.assertTrue(close_result['success'])
        self.assertEqual(close_result['trade'].status, 'CLOSED')
        
        # Step 4: Verify stats
        stats = PaperTradingService.get_portfolio_stats(self.portfolio)
        self.assertEqual(stats['total_trades'], 1)
        self.assertEqual(stats['closed_trades'], 1)
        self.assertEqual(stats['winners'], 1)
