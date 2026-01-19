# KVK AI Trading Platform

Production-grade AI-powered trading and investment analysis system with Django backend and React frontend.

## Quick Start

```bash
git clone <repo> && cd kvk-trading
make quick-start
```

Then open `http://localhost:3000` and log in with:
- Username: `vinod8833`
- Password: `test123`

## Requirements

- Python 3.10+
- Node.js 16+
- Make
- Git

## What This Is

- **Backend**: Django 4.2 + DRF REST API
- **Frontend**: React 18 + Zustand state management
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Data Sources**: NSE India, YFinance, Screener.in
- **ML/AI**: Scikit-learn, Pandas, NumPy for signal generation

## Core Features

- Real-time stock data integration from multiple sources
- 30+ technical indicators (EMA, RSI, MACD, ATR, VWAP, etc.)
- AI-powered signal generation with 5-minute predictions
- Automatic position sizing and risk management
- Paper trading for strategy testing
- Portfolio tracking and P&L analysis
- Candlestick pattern recognition

## Architecture

```
backend/
├── trading/                    # Main Django app
│   ├── data_integration.py    # NSE, YFinance, Screener integration
│   ├── technical_indicators.py # 30+ indicator calculations
│   ├── prediction_engine.py    # ML signal generation
│   ├── signal_generation.py    # Signal orchestration
│   ├── models.py              # Database schemas
│   ├── views.py               # REST endpoints
│   └── serializers.py         # Data serialization
├── kvk_trading/               # Django config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── requirements.txt

frontend/
├── src/
│   ├── pages/                 # Dashboard, Signals, Analysis, etc.
│   ├── components/            # Reusable React components
│   ├── api/                   # API client & endpoints
│   ├── store/                 # Zustand state management
│   └── utils/                 # Helper functions
├── package.json
└── tailwind.config.js
```

## Installation

### Option 1: One Command (Recommended)
```bash
make quick-start
```

### Option 2: Manual Setup
```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py init_sample_data

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

## Development

**Start backend** (port 8001):
```bash
make serve
```

**Start frontend** (port 3000, separate terminal):
```bash
make frontend-start
```

**Run tests**:
```bash
make test
```

**Database migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

**Create admin user**:
```bash
python manage.py createsuperuser
```

## API Endpoints

### AI Trading Signals
```
POST   /api/ai/generate-signal/        Generate trading signal
GET    /api/ai/market-status/          Check if market is open
GET    /api/ai/market-data/            Fetch live + historical data
POST   /api/ai/calculate-indicators/   Calculate technical indicators
POST   /api/ai/predict-movement/       Predict 5-min price movement
GET    /api/ai/data-quality/           Validate data quality
```

### Example: Generate a signal
```bash
curl -X POST http://localhost:8001/api/ai/generate-signal/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "INFY",
    "capital": 100000,
    "trader_type": "SWING"
  }'
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
ALPHA_VANTAGE_KEY=your-api-key
```

## Deployment

### Local Production Build
```bash
make frontend-build
python manage.py collectstatic
python manage.py runserver --nothreading --insecure
```

### Docker (if available)
```bash
docker-compose up
```

### Production Checklist
- [ ] Set `DEBUG=False` in settings
- [ ] Configure proper `SECRET_KEY`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up environment variables securely
- [ ] Run migrations
- [ ] Collect static files
- [ ] Use Gunicorn or uWSGI for serving

## Common Issues

### Port Already in Use
```bash
# Kill process on port 8001
lsof -i :8001 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Kill process on port 3000
lsof -i :3000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9
```

### ModuleNotFoundError: No module named 'django'
```bash
# Activate venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend can't connect to backend
- Verify backend is running on `http://localhost:8001`
- Check CORS settings in `settings.py`
- Verify API endpoint in `frontend/src/api/endpoints.js`
- Check browser console for specific errors

### Database migration errors
```bash
make reset  # Reset database to initial state
```

## Configuration

Key settings in `kvk_trading/settings.py`:

```python
TRADING_CONFIG = {
    'MAX_RISK_PER_TRADE': 0.005,      # 0.5%
    'DEFAULT_STOP_LOSS_PERCENT': 2.0,
    'INTRADAY_HOLDING_HOURS': 6,
}
```

Technical indicator parameters in `trading/technical_indicators.py`.

## Testing

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test trading.tests

# Run with verbose output
python manage.py test -v 2
```

## Performance

- Dashboard load: <500ms
- Signal generation: <2s
- API response: <200ms (p90)
- Database queries optimized with indexing

## Security

- CSRF protection enabled
- SQL injection prevention via ORM
- XSS protection in React
- Password hashing (PBKDF2)
- API rate limiting
- Secrets managed via environment variables

## Make Commands

```bash
make quick-start         # Install + run everything
make full-install        # Install backend + frontend
make full-stack          # Run both servers
make serve              # Backend only (port 8001)
make frontend-start     # Frontend only (port 3000)
make test               # Run tests
make migrate            # Apply database migrations
make admin              # Create superuser
make sample-data        # Load sample data
make reset              # Reset database
make clean              # Clean venv and node_modules
make help               # Show all commands
```

## URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8001/api/ |
| Admin Panel | http://localhost:8001/admin/ |
| Health Check | http://localhost:8001/health/ |

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test: `make test`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Open pull request

## Code Style

- Python: PEP 8 (checked via `flake8`)
- JavaScript: ESLint + Prettier
- Database: Migrations required for schema changes

## Monitoring

Check system health:
```bash
curl http://localhost:8001/health/
```

View logs:
```bash
make logs
```

## License

Proprietary - KVK_8833_PROFIT Trading System

## Disclaimer

For educational purposes only. Always conduct your own research and consult a financial advisor before trading. Past performance does not guarantee future results.
# Trading
