#!/bin/bash
# ===========================================
# Quick start script for uni-ai-starter backend
# ===========================================

cd "$(dirname "$0")/../backend"

# Check .env
if [ ! -f .env ]; then
    echo "❌ .env not found! Copy .env.example to .env and fill in your API keys."
    echo "   cp .env.example .env"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+."
    exit 1
fi

PY=$(command -v python3 || command -v python)

# Install dependencies
echo "📦 Installing dependencies..."
$PY -m pip install -r requirements.txt -q

# Start server
echo "🚀 Starting server..."
$PY main.py
