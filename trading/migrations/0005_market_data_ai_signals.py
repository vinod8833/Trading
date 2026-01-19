"""
Migration to add Market Data and Trading Signal models
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0004_groww_integration'),
    ]

    operations = [
        # StockPriceSnapshot
        migrations.CreateModel(
            name='StockPriceSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(db_index=True, max_length=20)),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('previous_close', models.DecimalField(decimal_places=2, max_digits=10)),
                ('open_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('high_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('low_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('volume', models.BigIntegerField(default=0)),
                ('traded_value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('market_cap', models.BigIntegerField(blank=True, null=True)),
                ('pe_ratio', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('data_source', models.CharField(choices=[('YFINANCE', 'Yahoo Finance'), ('NSE', 'NSE Official'), ('BSE', 'BSE Official')], default='YFINANCE', max_length=20)),
                ('data_freshness', models.CharField(choices=[('LIVE', 'Live'), ('DELAYED', 'Delayed'), ('EOD', 'End of Day')], default='EOD', max_length=20)),
                ('market_status', models.CharField(choices=[('OPEN', 'Market Open'), ('CLOSED', 'Market Closed'), ('HOLIDAY', 'Holiday')], default='CLOSED', max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        # MarketIndex
        migrations.CreateModel(
            name='MarketIndex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_name', models.CharField(choices=[('SENSEX', 'BSE Sensex'), ('NIFTY50', 'Nifty 50'), ('NIFTYNXT50', 'Nifty Next 50'), ('MIDCAP50', 'Nifty Midcap 50'), ('SMALLCAP50', 'Nifty Smallcap 50'), ('INDIAVIX', 'India VIX')], max_length=50, unique=True)),
                ('symbol', models.CharField(max_length=20, unique=True)),
                ('current_value', models.DecimalField(decimal_places=2, max_digits=15)),
                ('previous_close', models.DecimalField(decimal_places=2, max_digits=15)),
                ('change_points', models.DecimalField(decimal_places=2, max_digits=10)),
                ('change_percent', models.DecimalField(decimal_places=2, max_digits=8)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['index_name'],
            },
        ),
        # SectorPerformance
        migrations.CreateModel(
            name='SectorPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sector', models.CharField(choices=[('IT', 'Information Technology'), ('PHARMA', 'Pharmaceuticals'), ('BANK', 'Banking'), ('FINANCE', 'Financial Services'), ('FMCG', 'Consumer Goods'), ('REALTY', 'Real Estate'), ('ENERGY', 'Energy'), ('METALS', 'Metals'), ('AUTO', 'Automobile'), ('TELECOM', 'Telecom')], max_length=50, unique=True)),
                ('index_symbol', models.CharField(max_length=50)),
                ('current_value', models.DecimalField(decimal_places=2, max_digits=15)),
                ('change_percent', models.DecimalField(decimal_places=2, max_digits=8)),
                ('top_gainers', models.JSONField(blank=True, default=list)),
                ('top_losers', models.JSONField(blank=True, default=list)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Sector Performances',
                'ordering': ['sector'],
            },
        ),
        # TradeSignal
        migrations.CreateModel(
            name='TradeSignal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(db_index=True, max_length=20)),
                ('signal', models.CharField(choices=[('STRONG_BUY', 'Strong Buy'), ('BUY', 'Buy'), ('NEUTRAL', 'Neutral'), ('SELL', 'Sell'), ('STRONG_SELL', 'Strong Sell')], max_length=20)),
                ('confidence', models.DecimalField(decimal_places=3, max_digits=4)),
                ('confidence_min', models.DecimalField(decimal_places=3, max_digits=4)),
                ('confidence_max', models.DecimalField(decimal_places=3, max_digits=4)),
                ('entry_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('target_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stop_loss', models.DecimalField(decimal_places=2, max_digits=10)),
                ('risk_reward_ratio', models.DecimalField(decimal_places=2, max_digits=8)),
                ('technical_patterns', models.JSONField(default=list)),
                ('volume_signal', models.CharField(default='NEUTRAL', max_length=20)),
                ('trend', models.CharField(default='NEUTRAL', max_length=20)),
                ('momentum', models.CharField(default='NEUTRAL', max_length=20)),
                ('volatility', models.CharField(default='MODERATE', max_length=20)),
                ('uptrend_probability', models.DecimalField(decimal_places=3, default=0.5, max_digits=4)),
                ('breakout_probability', models.DecimalField(decimal_places=3, default=0.5, max_digits=4)),
                ('support_hold_probability', models.DecimalField(decimal_places=3, default=0.5, max_digits=4)),
                ('warning_flags', models.JSONField(default=list)),
                ('data_quality', models.CharField(choices=[('HIGH', 'High Quality'), ('ADEQUATE', 'Adequate'), ('LOW', 'Low Quality'), ('FAILED', 'Analysis Failed')], default='ADEQUATE', max_length=20)),
                ('confidence_reason', models.TextField()),
                ('disclaimer', models.TextField(default='This is a probability-based analysis, NOT a guarantee. Always use stop-losses.')),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-generated_at'],
            },
        ),
        # SignalHistory
        migrations.CreateModel(
            name='SignalHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('entry_time', models.DateTimeField(blank=True, null=True)),
                ('exit_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('exit_time', models.DateTimeField(blank=True, null=True)),
                ('exit_reason', models.CharField(choices=[('TARGET_HIT', 'Target Hit'), ('STOP_LOSS_HIT', 'Stop Loss Hit'), ('MANUAL_EXIT', 'Manual Exit'), ('PENDING', 'Pending')], default='PENDING', max_length=50)),
                ('profit_loss_rupees', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('profit_loss_percent', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('signal_accuracy', models.BooleanField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('signal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='trading.tradesignal')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        # DataSource
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('url', models.URLField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('provides_price', models.BooleanField(default=False)),
                ('provides_fundamentals', models.BooleanField(default=False)),
                ('provides_technical', models.BooleanField(default=False)),
                ('provides_news', models.BooleanField(default=False)),
                ('provides_corporate_actions', models.BooleanField(default=False)),
                ('is_free', models.BooleanField(default=True)),
                ('requires_api_key', models.BooleanField(default=False)),
                ('update_frequency', models.CharField(choices=[('REAL_TIME', 'Real Time'), ('INTRADAY', 'Intraday'), ('END_OF_DAY', 'End of Day'), ('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly')], default='END_OF_DAY', max_length=50)),
                ('last_checked', models.DateTimeField(blank=True, null=True)),
                ('is_available', models.BooleanField(default=True)),
                ('availability_percent', models.DecimalField(decimal_places=2, default=100.0, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='tradesignal',
            index=models.Index(fields=['symbol', '-generated_at'], name='trading_tra_symbol_idx'),
        ),
        migrations.AddIndex(
            model_name='tradesignal',
            index=models.Index(fields=['signal', '-generated_at'], name='trading_tra_signal_idx'),
        ),
        migrations.AddIndex(
            model_name='stockpricesnapshot',
            index=models.Index(fields=['symbol', '-timestamp'], name='trading_sto_symbol_idx'),
        ),
        migrations.AddIndex(
            model_name='stockpricesnapshot',
            index=models.Index(fields=['data_freshness', '-timestamp'], name='trading_sto_freshne_idx'),
        ),
    ]
