# Generated migration for Groww Integration models

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0003_rename_trading_aie_related_idx_trading_aie_related_261b59_idx_and_more'),
    ]

    operations = [
        # GrowwAccount model
        migrations.CreateModel(
            name='GrowwAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groww_user_id', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('account_name', models.CharField(max_length=255)),
                ('account_type', models.CharField(choices=[('INDIVIDUAL', 'Individual'), ('JOINT', 'Joint'), ('HUF', 'HUF'), ('CORPORATE', 'Corporate')], max_length=50)),
                ('pan', models.CharField(blank=True, max_length=20)),
                ('is_verified', models.BooleanField(default=False)),
                ('verification_date', models.DateTimeField(blank=True, null=True)),
                ('last_synced', models.DateTimeField(blank=True, null=True)),
                ('sync_status', models.CharField(choices=[('PENDING', 'Pending'), ('SYNCING', 'Syncing'), ('SYNCED', 'Synced'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        # GrowwHolding model
        migrations.CreateModel(
            name='GrowwHolding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_symbol', models.CharField(max_length=20)),
                ('stock_name', models.CharField(max_length=255)),
                ('isin', models.CharField(blank=True, max_length=20)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('average_cost', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('current_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('total_invested', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('current_value', models.DecimalField(decimal_places=2, default=0, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('gain_loss', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('gain_loss_percent', models.FloatField(default=0)),
                ('sector', models.CharField(blank=True, max_length=100)),
                ('industry', models.CharField(blank=True, max_length=100)),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('is_favourite', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groww_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='holdings', to='trading.growwaccount')),
            ],
            options={
                'ordering': ['-current_value'],
                'unique_together': {('groww_account', 'stock_symbol')},
            },
        ),
        
        # GrowwMutualFund model
        migrations.CreateModel(
            name='GrowwMutualFund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mf_isin', models.CharField(max_length=20, unique=True)),
                ('mf_name', models.CharField(max_length=255)),
                ('mf_category', models.CharField(choices=[('EQUITY', 'Equity'), ('DEBT', 'Debt'), ('HYBRID', 'Hybrid'), ('LIQUID', 'Liquid'), ('GOLD', 'Gold'), ('INTERNATIONAL', 'International')], max_length=100)),
                ('units', models.DecimalField(decimal_places=4, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('nav', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invested_amount', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('current_value', models.DecimalField(decimal_places=2, default=0, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('gain_loss', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('gain_loss_percent', models.FloatField(default=0)),
                ('fund_house', models.CharField(blank=True, max_length=255)),
                ('expense_ratio', models.FloatField(default=0, help_text='Annual expense ratio %')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groww_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mutual_funds', to='trading.growwaccount')),
            ],
            options={
                'ordering': ['-current_value'],
                'unique_together': {('groww_account', 'mf_isin')},
            },
        ),
        
        # GrowwPortfolioSummary model
        migrations.CreateModel(
            name='GrowwPortfolioSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_invested', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('current_portfolio_value', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('total_gain_loss', models.DecimalField(decimal_places=2, max_digits=15)),
                ('total_gain_loss_percent', models.FloatField()),
                ('equity_value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('mutual_fund_value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('cash_balance', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_holdings', models.IntegerField(default=0)),
                ('total_mutual_funds', models.IntegerField(default=0)),
                ('portfolio_beta', models.FloatField(default=0)),
                ('volatility', models.FloatField(default=0)),
                ('sharpe_ratio', models.FloatField(default=0)),
                ('equity_allocation_percent', models.FloatField(default=0)),
                ('debt_allocation_percent', models.FloatField(default=0)),
                ('others_allocation_percent', models.FloatField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groww_account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_summary', to='trading.growwaccount')),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        
        # GrowwTransaction model
        migrations.CreateModel(
            name='GrowwTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('BUY', 'Buy'), ('SELL', 'Sell'), ('DIVIDEND', 'Dividend'), ('BONUS', 'Bonus'), ('SPLIT', 'Split')], max_length=20)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('transaction_date', models.DateField()),
                ('transaction_time', models.TimeField(blank=True, null=True)),
                ('brokerage', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('groww_holding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='trading.growwholding')),
            ],
            options={
                'ordering': ['-transaction_date'],
            },
        ),
        
        # GrowwImportLog model
        migrations.CreateModel(
            name='GrowwImportLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('import_type', models.CharField(choices=[('HOLDINGS', 'Holdings'), ('MUTUAL_FUNDS', 'Mutual Funds'), ('TRANSACTIONS', 'Transactions'), ('FULL', 'Full Sync')], max_length=50)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('SUCCESS', 'Success'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('records_imported', models.IntegerField(default=0)),
                ('records_updated', models.IntegerField(default=0)),
                ('records_failed', models.IntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('started_at', models.DateTimeField()),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('groww_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='import_logs', to='trading.growwaccount')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='growwholding',
            index=models.Index(fields=['groww_account', 'stock_symbol'], name='trading_gro_groww_a_idx'),
        ),
        migrations.AddIndex(
            model_name='growwholding',
            index=models.Index(fields=['stock_symbol'], name='trading_gro_stock_s_idx'),
        ),
        migrations.AddIndex(
            model_name='growwtransaction',
            index=models.Index(fields=['groww_holding', 'transaction_date'], name='trading_gro_groww_h_idx'),
        ),
    ]
