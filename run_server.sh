#!/bin/bash
# KVK_8833_PROFIT - Development Server Startup Script

echo "=========================================="
echo "  KVK_8833_PROFIT Trading System"
echo "  Starting Development Server"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Check migrations
echo "🔄 Checking database migrations..."
python3 manage.py makemigrations 2>/dev/null

# Apply migrations
echo "🔄 Applying migrations..."
python3 manage.py migrate --run-syncdb 2>/dev/null

echo "✅ Database ready"
echo ""

# Display startup info
echo "=========================================="
echo "  API Endpoints"
echo "=========================================="
echo "📊 Stocks:        http://localhost:8000/api/stocks/"
echo "📈 Recommendations: http://localhost:8000/api/recommendations/"
echo "💼 Portfolio:     http://localhost:8000/api/portfolio/"
echo "⚠️  Risk:         http://localhost:8000/api/risk/"
echo "🏥 Health:       http://localhost:8000/health/"
echo "🔧 Admin:        http://localhost:8000/admin/"
echo "=========================================="
echo ""

# Start server
echo "🚀 Starting Django development server..."
echo "Press Ctrl+C to stop"
echo ""

python3 manage.py runserver 0.0.0.0:8000
