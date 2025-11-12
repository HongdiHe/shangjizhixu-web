#!/bin/bash

# Setup script for question processing system
set -e

echo "=========================================="
echo "Question Processing System - Setup"
echo "=========================================="
echo ""

# Check if we're in the backend directory
if [ ! -f "app/main.py" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# 1. Start Docker services
echo "Step 1: Starting Docker services (PostgreSQL, Redis, MinIO)..."
docker-compose up -d
echo "✓ Docker services started"
echo ""

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5
echo "✓ PostgreSQL should be ready"
echo ""

# 2. Initialize database
echo "Step 2: Initializing database..."
python scripts/init_db.py
echo ""

# 3. Create initial users
echo "Step 3: Creating initial users..."
python scripts/create_initial_users.py
echo ""

# Done
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start FastAPI:  python -m app.main"
echo "2. Start Celery:   celery -A app.tasks.celery worker --loglevel=info"
echo "3. Start Frontend: cd ../frontend && npm run dev"
echo ""
echo "Access the system at: http://localhost:3000"
echo ""
