#!/bin/bash

cd "$(dirname "$0")"

echo "========================================"
echo " Trading Market AI"
echo "========================================"

# --------------------------------------------------
# CREATE PROJECT VIRTUAL ENVIRONMENT IF MISSING
# --------------------------------------------------

if [ ! -f ".venv/bin/python" ]; then

    echo "Creating virtual environment..."

    python3 -m venv .venv

fi


# --------------------------------------------------
# USE PROJECT PYTHON DIRECTLY
# --------------------------------------------------

VENV_PYTHON="$(pwd)/.venv/bin/python"

echo ""
echo "PROJECT PYTHON:"
"$VENV_PYTHON" -c "import sys; print(sys.executable); print(sys.version)"

echo ""


# --------------------------------------------------
# INSTALL DEPENDENCIES ONLY IF NEEDED
# --------------------------------------------------

if ! "$VENV_PYTHON" -c "import uvicorn, growwapi" 2>/dev/null; then

    echo "Installing project dependencies..."

    "$VENV_PYTHON" -m pip install --upgrade pip
    "$VENV_PYTHON" -m pip install -r requirements.txt

fi


# --------------------------------------------------
# CREATE .env IF MISSING
# --------------------------------------------------

if [ ! -f ".env" ]; then

    cp .env.example .env

fi


# --------------------------------------------------
# STOP OLD SERVER ON PORT 8000
# --------------------------------------------------

OLD_PID=$(lsof -ti :8000)

if [ -n "$OLD_PID" ]; then

    echo "Stopping old server on port 8000..."

    kill -9 $OLD_PID

    sleep 1

fi


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

echo ""
echo "Starting Trading Market AI..."
echo ""

"$VENV_PYTHON" -m uvicorn \
    backend.main:app \
    --host 127.0.0.1 \
    --port 8000 &

SERVER_PID=$!


sleep 3


# --------------------------------------------------
# OPEN DASHBOARD
# --------------------------------------------------

open http://127.0.0.1:8000


wait $SERVER_PID