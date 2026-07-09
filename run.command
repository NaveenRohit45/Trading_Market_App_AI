#!/bin/bash

cd "$(dirname "$0")"

echo "========================================"
echo " ADA Market Intelligence V1"
echo "========================================"

# Create virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Upgrade pip
python3 -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env if missing
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Stop any old ADA server using port 8000
OLD_PID=$(lsof -ti :8000)

if [ -n "$OLD_PID" ]; then
    echo "Stopping old server on port 8000..."
    kill -9 $OLD_PID
    sleep 1
fi

echo ""
echo "Starting server..."
echo ""

python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
SERVER_PID=$!

sleep 3

# Open browser
open http://127.0.0.1:8000

wait $SERVER_PID