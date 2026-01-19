#!/bin/bash
# Setup and initialize KVK_8833_PROFIT system

echo "=========================================="
echo "  KVK_8833_PROFIT Setup Wizard"
echo "=========================================="
echo ""

# Create virtual environment
echo "1️⃣  Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "2️⃣  Installing dependencies..."
pip install -q --upgrade pip
pip install -q Django==4.2.8 djangorestframework==3.14.0 django-cors-headers==4.3.1

# Create migrations
echo "3️⃣  Creating database migrations..."
python3 manage.py makemigrations trading

# Apply migrations
echo "4️⃣  Applying migrations..."
python3 manage.py migrate

# Initialize sample data
echo "5️⃣  Loading sample data..."
python3 manage.py init_sample_data 2>/dev/null

echo ""
echo "=========================================="
echo "  Setup Complete! ✅"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Create admin user: python3 manage.py createsuperuser"
echo "3. Run server: ./run_server.sh"
echo ""
echo "Then visit:"
echo "- API: http://localhost:8000/api/"
echo "- Admin: http://localhost:8000/admin/"
echo "- Health: http://localhost:8000/health/"
echo ""
