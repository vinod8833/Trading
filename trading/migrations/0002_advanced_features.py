# Generated migration for advanced features

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaperTrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('entry_date', models.DateTimeField()),
                ('exit_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('exit_date', models.DateTimeField(blank=True, null=True)),
                ('profit_loss', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('profit_loss_percent', models.FloatField(null=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('CLOSED', 'Closed'), ('CANCELLED', 'Cancelled')], default='ACTIVE', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paper_trades', to='trading.portfolio')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paper_trades', to='trading.stock')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SmartAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_type', models.CharField(choices=[('PRICE_LEVEL', 'Price Level'), ('VOLUME_SPIKE', 'Volume Spike'), ('TREND_CHANGE', 'Trend Change'), ('SUPPORT_BREAK', 'Support Break'), ('RESISTANCE_BREAK', 'Resistance Break'), ('BOLLINGER_BAND', 'Bollinger Band')], max_length=30)),
                ('condition', models.CharField(help_text="e.g., 'Price > 500' or 'Volume > 5M'", max_length=255)),
                ('target_value', models.FloatField()),
                ('trigger_value', models.FloatField(blank=True, help_text='Actual value when triggered', null=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('TRIGGERED', 'Triggered'), ('DISMISSED', 'Dismissed')], default='ACTIVE', max_length=20)),
                ('triggered_at', models.DateTimeField(blank=True, null=True)),
                ('send_email', models.BooleanField(default=True)),
                ('send_notification', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='smart_alerts', to='trading.stock')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MarketSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('market_date', models.DateField(unique=True)),
                ('gainers_count', models.IntegerField(default=0)),
                ('losers_count', models.IntegerField(default=0)),
                ('unchanged_count', models.IntegerField(default=0)),
                ('market_trend', models.CharField(max_length=20)),
                ('market_sentiment', models.CharField(choices=[('VERY_BULLISH', 'Very Bullish'), ('BULLISH', 'Bullish'), ('NEUTRAL', 'Neutral'), ('BEARISH', 'Bearish'), ('VERY_BEARISH', 'Very Bearish')], max_length=20)),
                ('average_volume', models.BigIntegerField()),
                ('volatility_index', models.FloatField(blank=True, null=True)),
                ('sector_performance', models.JSONField(default=dict)),
                ('summary_text', models.TextField(help_text='Market summary explanation')),
                ('key_levels', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-market_date'],
            },
        ),
        migrations.CreateModel(
            name='PortfolioHealth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('health_score', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('health_status', models.CharField(choices=[('EXCELLENT', 'Excellent (>90)'), ('GOOD', 'Good (70-90)'), ('FAIR', 'Fair (50-70)'), ('POOR', 'Poor (30-50)'), ('CRITICAL', 'Critical (<30)')], max_length=20)),
                ('total_profit_loss', models.DecimalField(decimal_places=2, max_digits=15)),
                ('profit_loss_percent', models.FloatField()),
                ('win_rate', models.FloatField(help_text='Percentage of winning trades')),
                ('average_win', models.DecimalField(decimal_places=2, max_digits=12)),
                ('average_loss', models.DecimalField(decimal_places=2, max_digits=12)),
                ('risk_level', models.CharField(max_length=20)),
                ('max_drawdown', models.FloatField(help_text='Maximum peak-to-trough decline')),
                ('sharpe_ratio', models.FloatField(blank=True, null=True)),
                ('sector_concentration', models.FloatField(help_text='Concentration in top sector (0-100)')),
                ('number_of_holdings', models.IntegerField()),
                ('largest_position_percent', models.FloatField()),
                ('warnings', models.JSONField(default=list)),
                ('recommendations', models.JSONField(default=list)),
                ('analyzed_at', models.DateTimeField(auto_now=True)),
                ('portfolio', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='health', to='trading.portfolio')),
            ],
            options={
                'ordering': ['-analyzed_at'],
            },
        ),
        migrations.CreateModel(
            name='TradingMistake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mistake_category', models.CharField(choices=[('ENTRY_TIMING', 'Poor Entry Timing'), ('EXIT_TIMING', 'Poor Exit Timing'), ('POSITION_SIZE', 'Wrong Position Size'), ('RISK_MANAGEMENT', 'Risk Management Failure'), ('DISCIPLINE', 'Discipline Violation'), ('EMOTIONAL', 'Emotional Decision'), ('ANALYSIS_ERROR', 'Analysis Error'), ('MARKET_CONDITION', 'Ignored Market Condition')], max_length=30)),
                ('severity', models.CharField(choices=[('LOW', 'Low Impact'), ('MEDIUM', 'Medium Impact'), ('HIGH', 'High Impact'), ('CRITICAL', 'Critical Impact')], max_length=20)),
                ('description', models.TextField()),
                ('impact', models.DecimalField(decimal_places=2, help_text='Loss amount', max_digits=12)),
                ('lesson_learned', models.TextField(help_text='What to do next time')),
                ('prevention_tip', models.CharField(max_length=255)),
                ('detected_at', models.DateTimeField(auto_now_add=True)),
                ('trade_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detected_mistakes', to='trading.tradeorder')),
            ],
            options={
                'ordering': ['-detected_at'],
            },
        ),
        migrations.CreateModel(
            name='InvestmentPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goal', models.CharField(choices=[('WEALTH_CREATION', 'Wealth Creation'), ('RETIREMENT', 'Retirement Planning'), ('EDUCATION', 'Education Fund'), ('HOME_PURCHASE', 'Home Purchase'), ('EMERGENCY_FUND', 'Emergency Fund'), ('SHORT_TERM_GAINS', 'Short-Term Gains')], max_length=30)),
                ('target_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('time_horizon', models.CharField(choices=[('3_MONTHS', '3 Months'), ('6_MONTHS', '6 Months'), ('1_YEAR', '1 Year'), ('3_YEARS', '3 Years'), ('5_YEARS', '5 Years'), ('10PLUS_YEARS', '10+ Years')], max_length=20)),
                ('risk_tolerance', models.CharField(max_length=20)),
                ('equity_percent', models.FloatField()),
                ('debt_percent', models.FloatField()),
                ('alternatives_percent', models.FloatField()),
                ('recommended_stocks', models.JSONField(default=list)),
                ('plan_description', models.TextField()),
                ('expected_returns', models.FloatField(help_text='Annual return expectation %')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investment_plans', to='trading.portfolio')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIExplanation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('related_model', models.CharField(max_length=50)),
                ('related_id', models.IntegerField()),
                ('explanation_type', models.CharField(choices=[('SIGNAL_GENERATION', 'Signal Generation'), ('RISK_ANALYSIS', 'Risk Analysis'), ('PORTFOLIO_DECISION', 'Portfolio Decision'), ('ALERT_TRIGGER', 'Alert Trigger'), ('MISTAKE_DETECTION', 'Mistake Detection'), ('MARKET_SENTIMENT', 'Market Sentiment')], max_length=30)),
                ('simple_explanation', models.TextField(help_text='Beginner-friendly explanation')),
                ('detailed_explanation', models.TextField(help_text='Detailed technical explanation for pros')),
                ('key_factors', models.JSONField(default=list)),
                ('confidence_score', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('indicators_used', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='papertrade',
            index=models.Index(fields=['portfolio', '-created_at'], name='trading_pap_portfol_idx'),
        ),
        migrations.AddIndex(
            model_name='papertrade',
            index=models.Index(fields=['status'], name='trading_pap_status_idx'),
        ),
        migrations.AddIndex(
            model_name='smartalert',
            index=models.Index(fields=['stock', 'status'], name='trading_sma_stock_idx'),
        ),
        migrations.AddIndex(
            model_name='smartalert',
            index=models.Index(fields=['alert_type'], name='trading_sma_alert_type_idx'),
        ),
        migrations.AddIndex(
            model_name='marketsummary',
            index=models.Index(fields=['-market_date'], name='trading_mar_market_date_idx'),
        ),
        migrations.AddIndex(
            model_name='tradingmistake',
            index=models.Index(fields=['trade_order', '-detected_at'], name='trading_tra_trade_order_idx'),
        ),
        migrations.AddIndex(
            model_name='aiexplanation',
            index=models.Index(fields=['related_model', 'related_id'], name='trading_aie_related_idx'),
        ),
        migrations.AddIndex(
            model_name='aiexplanation',
            index=models.Index(fields=['explanation_type'], name='trading_aie_explanation_type_idx'),
        ),
    ]
