from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, time
import pytz
from trading.models import TradeOrder, Stock
from trading.market_data import MarketDataFetcher
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Automatically square off all intraday positions at market close'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force square off even outside market hours (for testing)',
        )

    def handle(self, *args, **options):
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        current_time = now.time()
        
        market_close_start = time(15, 30)
        market_close_end = time(15, 35)
        
        is_market_close = (market_close_start <= current_time <= market_close_end) or options['force']
        
        if not is_market_close:
            self.stdout.write(
                self.style.WARNING(
                    f'⏰ Not market close time. Current IST time: {current_time}. '
                    f'Use --force to override.'
                )
            )
            return
        
        active_intraday = TradeOrder.objects.filter(
            is_intraday=True,
            auto_square_off=True,
            status='EXECUTED',
            exit_time__isnull=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🔄 Found {active_intraday.count()} intraday positions to square off'
            )
        )
        
        closed_count = 0
        total_pnl = Decimal('0')
        
        for order in active_intraday:
            try:
                live_data = MarketDataFetcher.get_stock_price(order.stock.symbol)
                
                if not live_data:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Could not fetch price for {order.stock.symbol}, '
                            f'using entry price as exit'
                        )
                    )
                    exit_price = order.actual_entry_price or order.entry_price
                else:
                    exit_price = Decimal(str(live_data['price']))

                pnl = (exit_price - order.entry_price) * order.quantity
                pnl_percent = float((pnl / (order.entry_price * order.quantity)) * 100) \
                    if order.entry_price > 0 else 0
                
                order.exit_time = datetime.now(ist)
                order.profit_loss = pnl
                order.profit_loss_percent = pnl_percent
                order.status = 'CLOSED'
                order.save()
                
                closed_count += 1
                total_pnl += pnl
                
                status_icon = '✅' if pnl > 0 else '❌'
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{status_icon} Closed {order.stock.symbol}: '
                        f'{order.quantity} units @ ₹{exit_price} | '
                        f'P&L: ₹{float(pnl):.2f} ({pnl_percent:.2f}%)'
                    ) if pnl > 0 else self.style.WARNING(
                        f'{status_icon} Closed {order.stock.symbol}: '
                        f'{order.quantity} units @ ₹{exit_price} | '
                        f'P&L: ₹{float(pnl):.2f} ({pnl_percent:.2f}%)'
                    )
                )
                
                logger.info(
                    f'Auto square-off: {order.stock.symbol} - '
                    f'Qty: {order.quantity}, Entry: ₹{order.entry_price}, '
                    f'Exit: ₹{exit_price}, P&L: ₹{pnl}'
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error closing {order.stock.symbol}: {str(e)}'
                    )
                )
                logger.error(f'Auto square-off error for {order.stock.symbol}: {str(e)}')
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 MARKET CLOSE SUMMARY\n'
                f'{"="*50}\n'
                f'Total Positions Closed: {closed_count}\n'
                f'Total P&L: ₹{float(total_pnl):.2f}\n'
                f'{"="*50}'
            )
        )
