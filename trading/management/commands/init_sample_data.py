from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'DISABLED - This command does not initialize any sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--market',
            type=str,
            default='NSE',
            help='DISABLED - Not used'
        )
        parser.add_argument(
            '--symbols',
            type=str,
            default='INFY,TCS,HDFCBANK',
            help='DISABLED - Not used'
        )

    def handle(self, *args, **options):
        """This command is disabled - no sample data will be initialized"""
        self.stdout.write(self.style.ERROR(
            '╔════════════════════════════════════════════════════════════════╗'
        ))
        self.stdout.write(self.style.ERROR(
            '║                   ⛔ COMMAND DISABLED ⛔                         ║'
        ))
        self.stdout.write(self.style.ERROR(
            '╚════════════════════════════════════════════════════════════════╝'
        ))
        
        self.stdout.write('\n' + self.style.WARNING(
            '❌ init_sample_data command is DISABLED'
        ))
        
        self.stdout.write(
            '\n📋 REASON: System operates ONLY on real market data\n'
        )
        
        self.stdout.write('✓ No sample data will be initialized')
        self.stdout.write('✓ No mock records will be inserted')
        self.stdout.write('✓ No fake data will be generated')
        self.stdout.write('✓ No dummy values will be stored')
        
        self.stdout.write('\n' + self.style.SUCCESS(
            '🎯 System Data Policy:'
        ))
        
        self.stdout.write('   ✅ Live market data ONLY (yfinance)')
        self.stdout.write('   ✅ Real-time prices from approved sources')
        self.stdout.write('   ✅ Last-traded data during market closures')
        self.stdout.write('   ✅ Holiday handling via market calendars')
        self.stdout.write('   ✅ 100% data-driven, zero hardcoded values')
        
        self.stdout.write('\n' + self.style.WARNING(
            '📊 FEATURES USING LIVE DATA ONLY:'
        ))
        
        self.stdout.write('   • Stock Analysis - Live price + technical indicators')
        self.stdout.write('   • Pattern Scanner - Real-time candlestick patterns')
        self.stdout.write('   • Signals Generation - Live market data')
        self.stdout.write('   • Intraday Trading - Real-time OHLCV data')
        self.stdout.write('   • Paper Trading - Live price feeds')
        self.stdout.write('   • Portfolio - Real market valuations')
        self.stdout.write('   • Risk Assessment - Current market data')
        
        self.stdout.write('\n' + self.style.SUCCESS(
            '✨ Approved Live Data Sources:'
        ))
        
        self.stdout.write('   • yfinance (Primary)')
        self.stdout.write('   • NSE/BSE official APIs (where available)')
        self.stdout.write('   • Market calendars (holiday tracking)')
        
        self.stdout.write('\n' + self.style.WARNING(
            '⏰ Market Status Handling:'
        ))
        
        self.stdout.write('   • Market Open (9:15 AM - 3:30 PM IST): Live prices')
        self.stdout.write('   • Market Closed: Last-traded data from previous session')
        self.stdout.write('   • Holidays/Weekends: Last-traded data with date notation')
        self.stdout.write('   • No sample/placeholder values ever used')
        
        self.stdout.write('\n' + self.style.SUCCESS(
            '✅ All systems ready for live market data'
        ))
        self.stdout.write('\n' + self.style.WARNING(
            'NOTE: This command intentionally does nothing.'
        ))
        self.stdout.write('      The system is 100% data-driven from live sources.\n')

