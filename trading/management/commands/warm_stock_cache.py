
from django.core.management.base import BaseCommand
from django.utils import timezone
from trading.stock_universe import StockUniverseManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Warm the stock universe cache with NSE & BSE data'
    
    def add_arguments(self, parser):
        """Define command arguments"""
        
        parser.add_argument(
            '--market',
            type=str,
            default='ALL',
            choices=['NSE', 'BSE', 'ALL'],
            help='Which market to warm cache for (default: ALL)'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh cache even if recently updated'
        )
        
        parser.add_argument(
            '--verbose-output',
            action='store_true',
            help='Print detailed stock data'
        )
    
    def handle(self, *args, **options):
        """Execute the command"""
        
        market = options['market']
        force_refresh = options['force']
        verbose = options['verbose_output']
        verbosity = options['verbosity']
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🔄 Starting stock universe cache warming...')
        )
        self.stdout.write(f'Market: {market}')
        self.stdout.write(f'Force refresh: {force_refresh}')
        self.stdout.write(f'Time: {timezone.now().isoformat()}\n')
        
        try:
            # Warm cache for specified markets
            markets_to_warm = []
            if market == 'ALL':
                markets_to_warm = ['NSE', 'BSE']
            else:
                markets_to_warm = [market]
            
            total_stocks = 0
            
            for mkt in markets_to_warm:
                self.stdout.write(f'\n⏳ Warming {mkt} stocks...')
                
                try:
                    # Fetch and cache stocks
                    stocks = StockUniverseManager.get_all_stocks(mkt, force_refresh=force_refresh)
                    
                    if stocks:
                        count = len(stocks)
                        total_stocks += count
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ {mkt}: {count} stocks cached')
                        )
                        
                        # Get sectors for this market
                        sectors = StockUniverseManager.get_sectors(mkt)
                        self.stdout.write(f'  - Sectors: {len(sectors)}')
                        
                        if verbose and verbosity >= 2:
                            # Show sector distribution
                            by_sector = StockUniverseManager.get_by_sector(mkt)
                            for sector, sector_stocks in sorted(by_sector.items()):
                                self.stdout.write(f'    • {sector}: {len(sector_stocks)} stocks')
                        
                        # Show sample stocks
                        if verbosity >= 2:
                            sample_stocks = list(stocks.keys())[:5]
                            self.stdout.write(f'  Sample stocks: {", ".join(sample_stocks)}')
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⚠ {mkt}: No stocks returned')
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ {mkt}: Failed - {str(e)}')
                    )
                    logger.error(f'Failed to warm {mkt} cache: {str(e)}', exc_info=True)
            
            # Summary
            self.stdout.write(f'\n📊 Summary:')
            self.stdout.write(f'  Total stocks cached: {total_stocks}')
            self.stdout.write(f'  Completion time: {timezone.now().isoformat()}')
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ Cache warming completed successfully!\n')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Cache warming failed: {str(e)}\n')
            )
            logger.error(f'Cache warming error: {str(e)}', exc_info=True)
            raise


# Additional utility functions that can be called directly
def warm_nse_cache(force_refresh=False, verbose=False):
    """Warm NSE cache programmatically"""
    
    try:
        stocks = StockUniverseManager.get_all_stocks('NSE', force_refresh=force_refresh)
        logger.info(f'NSE cache warmed: {len(stocks)} stocks')
        return True
    except Exception as e:
        logger.error(f'Failed to warm NSE cache: {str(e)}')
        return False


def warm_bse_cache(force_refresh=False, verbose=False):
    """Warm BSE cache programmatically"""
    
    try:
        stocks = StockUniverseManager.get_all_stocks('BSE', force_refresh=force_refresh)
        logger.info(f'BSE cache warmed: {len(stocks)} stocks')
        return True
    except Exception as e:
        logger.error(f'Failed to warm BSE cache: {str(e)}')
        return False


def warm_all_caches(force_refresh=False):
    """Warm all market caches"""
    
    nse_success = warm_nse_cache(force_refresh)
    bse_success = warm_bse_cache(force_refresh)
    
    return nse_success and bse_success
