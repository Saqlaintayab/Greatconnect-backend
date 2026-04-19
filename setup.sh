#!/bin/bash
echo "=========================================="
echo "  GreatConnect - Backend Setup"
echo "=========================================="

# Virtual environment
echo ""
echo "1️⃣  Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Dependencies
echo ""
echo "2️⃣  Installing Python packages..."
pip install -r requirements.txt

# Migrations
echo ""
echo "3️⃣  Creating database tables..."
python manage.py makemigrations accounts
python manage.py makemigrations posts
python manage.py makemigrations friends
python manage.py makemigrations chat
python manage.py makemigrations notifications
python manage.py makemigrations stories
python manage.py migrate

# Superuser
echo ""
echo "4️⃣  Create admin superuser:"
python manage.py createsuperuser

echo ""
echo "✅ Backend ready!"
echo ""
echo "▶️  Start with:"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "🌐 Backend: http://localhost:8000"
echo "🔧 Admin:   http://localhost:8000/admin"
