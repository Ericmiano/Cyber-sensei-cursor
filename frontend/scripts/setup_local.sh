#!/bin/bash
# Local setup script for Cyber Sensei frontend

set -e

echo "🚀 Setting up Cyber Sensei Frontend (Local Development)"

# Check Node.js version
echo "📋 Checking Node.js version..."
if command -v node &> /dev/null; then
    node_version=$(node --version | cut -d'v' -f2)
    required_major=18
    current_major=$(echo $node_version | cut -d'.' -f1)
    
    if [ "$current_major" -lt "$required_major" ]; then
        echo "❌ Node.js 18+ required. Found: $node_version"
        exit 1
    fi
    echo "✅ Node.js $node_version found"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check npm
echo "📋 Checking npm..."
if command -v npm &> /dev/null; then
    npm_version=$(npm --version)
    echo "✅ npm $npm_version found"
else
    echo "❌ npm not found"
    exit 1
fi

# Install dependencies
echo "📥 Installing dependencies..."
npm install
echo "✅ Dependencies installed"

# Check for .env file (optional for frontend)
echo "⚙️  Checking configuration..."
if [ ! -f ".env" ]; then
    echo "ℹ️  No .env file needed for frontend (using vite.config.ts proxy)"
else
    echo "✅ .env file exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start development server: npm run dev"
echo "2. Access frontend: http://localhost:5173"
echo "3. Make sure backend is running on http://localhost:8000"
