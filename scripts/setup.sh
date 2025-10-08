#!/bin/bash
# 🌱 Transcendence Setup Script - Cross Platform
# Automated installation and configuration for local development

echo "🌱 Starting Transcendence Setup..."
echo "============================================"

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    if [[ $PYTHON_VERSION =~ Python\ 3\.([0-9]+) ]]; then
        MINOR_VERSION=${BASH_REMATCH[1]}
        if [ $MINOR_VERSION -ge 11 ]; then
            echo "✅ $PYTHON_VERSION found"
        else
            echo "❌ Python 3.11+ required, found $PYTHON_VERSION"
            exit 1
        fi
    fi
else
    echo "❌ Python3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    if [[ $NODE_VERSION =~ v([0-9]+) ]]; then
        MAJOR_VERSION=${BASH_REMATCH[1]}
        if [ $MAJOR_VERSION -ge 18 ]; then
            echo "✅ Node.js $NODE_VERSION found"
        else
            echo "❌ Node.js 18+ required, found $NODE_VERSION"
            exit 1
        fi
    fi
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version 2>&1)
    echo "✅ npm $NPM_VERSION found"
else
    echo "❌ npm not found. Please install npm"
    exit 1
fi

echo ""
echo "🐍 Setting up Python backend..."

# Create and activate Python virtual environment
cd backend
if [ -d ".venv" ]; then
    echo "🔄 Removing existing virtual environment..."
    rm -rf .venv
fi

echo "📦 Creating Python virtual environment..."
python3 -m venv .venv

echo "🚀 Activating virtual environment..."
source .venv/bin/activate

echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating backend .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your AWS credentials"
fi

echo "✅ Python backend setup complete!"

echo ""
echo "⚛️  Setting up React frontend..."
cd ../frontend

echo "📥 Installing Node.js dependencies..."
npm install

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating frontend .env file..."
    cp .env.example .env
fi

echo "✅ React frontend setup complete!"

echo ""
echo "🎯 Setup Summary:"
echo "============================================"
echo "✅ Python virtual environment created in backend/.venv"
echo "✅ Python dependencies installed"
echo "✅ Node.js dependencies installed"
echo "✅ Environment files created"

echo ""
echo "🚀 Next Steps:"
echo "1. Edit backend/.env with your AWS Mistral credentials (optional for mock mode)"
echo "2. Run: ./scripts/seed.sh to populate sample data"
echo "3. Start backend: cd backend && source .venv/bin/activate && python -m uvicorn app.main:app --reload --port 8000"
echo "4. Start frontend: cd frontend && npm run dev"
echo "5. Open: http://localhost:5173"

echo ""
echo "🌱 Happy green job hunting!"

cd ..