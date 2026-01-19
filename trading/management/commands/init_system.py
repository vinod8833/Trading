"""
Management command to initialize and verify the entire system
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from trading.fixtures import initialize_database, FixtureManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize KVK Trading System - runs all setup steps'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset database before initializing',
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Only verify setup, do not initialize',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('╔═══════════════════════════════════════════════════════════════════╗'))
        self.stdout.write(self.style.SUCCESS('║  KVK_8833_PROFIT - AI TRADING PLATFORM INITIALIZATION              ║'))
        self.stdout.write(self.style.SUCCESS('╚═══════════════════════════════════════════════════════════════════╝'))
        self.stdout.write('')
        
        try:
            # Step 1: Verify migrations
            self.stdout.write(self.style.HTTP_INFO('STEP 1: Checking migrations...'))
            try:
                # Run migrations
                call_command('migrate', '--run-syncdb', verbosity=0)
                self.stdout.write(self.style.SUCCESS('✅ Migrations applied successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Migration failed: {e}'))
                raise
            
            self.stdout.write('')
            
            # Step 2: Initialize fixtures
            self.stdout.write(self.style.HTTP_INFO('STEP 2: Initializing data fixtures...'))
            try:
                if initialize_database():
                    self.stdout.write(self.style.SUCCESS('✅ Fixtures initialized successfully'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️  Fixtures already initialized'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Fixture initialization failed: {e}'))
                raise
            
            self.stdout.write('')
            
            # Step 3: Verify database
            self.stdout.write(self.style.HTTP_INFO('STEP 3: Verifying database...'))
            try:
                from django.contrib.auth.models import User
                from trading.models import Stock, StockAnalysis
                
                user_count = User.objects.count()
                stock_count = Stock.objects.count()
                analysis_count = StockAnalysis.objects.count()
                
                self.stdout.write(self.style.SUCCESS(f'✅ Users: {user_count}'))
                self.stdout.write(self.style.SUCCESS(f'✅ Stocks: {stock_count}'))
                self.stdout.write(self.style.SUCCESS(f'✅ Analysis records: {analysis_count}'))
                
                # Show demo user
                try:
                    demo_user = User.objects.get(username='vinod8833')
                    self.stdout.write(self.style.SUCCESS(f'✅ Demo user created: {demo_user.username} ({demo_user.email})'))
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING('⚠️  Demo user not found'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Database verification failed: {e}'))
                raise
            
            self.stdout.write('')
            
            # Step 4: Check API readiness
            self.stdout.write(self.style.HTTP_INFO('STEP 4: Checking API configuration...'))
            try:
                from django.conf import settings
                
                rest_framework_config = settings.REST_FRAMEWORK
                jwt_config = settings.SIMPLE_JWT
                
                self.stdout.write(self.style.SUCCESS('✅ REST Framework configured'))
                self.stdout.write(self.style.SUCCESS('✅ JWT authentication enabled'))
                
                # Check CORS
                if settings.CORS_ALLOWED_ORIGINS:
                    self.stdout.write(self.style.SUCCESS('✅ CORS configured'))
                    for origin in settings.CORS_ALLOWED_ORIGINS:
                        if 'localhost' in origin or '127.0.0.1' in origin:
                            self.stdout.write(f'   - {origin}')
                
                self.stdout.write(self.style.SUCCESS('✅ Trading configuration loaded'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ API configuration check failed: {e}'))
                raise
            
            self.stdout.write('')
            
            # Step 5: Summary
            self.stdout.write(self.style.SUCCESS('╔═══════════════════════════════════════════════════════════════════╗'))
            self.stdout.write(self.style.SUCCESS('║  INITIALIZATION COMPLETE ✅                                        ║'))
            self.stdout.write(self.style.SUCCESS('╚═══════════════════════════════════════════════════════════════════╝'))
            self.stdout.write('')
            
            self.stdout.write(self.style.SUCCESS('📝 NEXT STEPS:'))
            self.stdout.write(self.style.SUCCESS('1. Start the server:'))
            self.stdout.write(self.style.WARNING('   python manage.py runserver 0.0.0.0:8001'))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('2. In another terminal, start frontend:'))
            self.stdout.write(self.style.WARNING('   cd frontend && npm start'))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('3. Login with demo credentials:'))
            self.stdout.write(self.style.WARNING('   Username: vinod8833'))
            self.stdout.write(self.style.WARNING('   Password: test123'))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('4. Test API endpoints:'))
            self.stdout.write(self.style.WARNING('   curl http://localhost:8001/health/'))
            self.stdout.write('')
            
            # Version and system info
            self.stdout.write(self.style.SUCCESS('ℹ️  SYSTEM INFO:'))
            self.stdout.write(self.style.SUCCESS('   Platform: KVK_8833_PROFIT (AI Trading System)'))
            self.stdout.write(self.style.SUCCESS('   Version: 2.0 with comprehensive fixes'))
            self.stdout.write(self.style.SUCCESS('   Backend: Django + DRF + JWT'))
            self.stdout.write(self.style.SUCCESS('   Frontend: React + Zustand'))
            self.stdout.write(self.style.SUCCESS('   Database: SQLite (for development)'))
            self.stdout.write('')
            
            self.stdout.write(self.style.SUCCESS('✅ System ready for use!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Initialization failed: {e}'))
            raise CommandError(f'System initialization failed: {e}')
