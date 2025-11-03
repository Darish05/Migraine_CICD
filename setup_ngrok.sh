#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   STREAMLIT CLOUD DEPLOYMENT - QUICK SETUP                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if services are running
echo "📋 Step 1: Checking if API is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is running on port 8000"
else
    echo "❌ API is NOT running!"
    echo ""
    echo "Starting services with docker-compose..."
    cd /home/rhemi/IA3/Dar_mlops/Migraine_CICD
    sudo docker-compose up -d
    echo "⏳ Waiting 30 seconds for services to start..."
    sleep 30
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📋 Step 2: Install and setup ngrok"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if ngrok is installed
if command -v ngrok &> /dev/null; then
    echo "✅ ngrok is already installed"
else
    echo "📥 Installing ngrok..."
    cd /tmp
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar xzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok-v3-stable-linux-amd64.tgz
    echo "✅ ngrok installed successfully"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🔑 Step 3: Configure ngrok authtoken"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "2. Sign up/login (free account)"
echo "3. Copy your authtoken"
echo ""
read -p "Enter your ngrok authtoken (or press Enter to skip): " authtoken

if [ ! -z "$authtoken" ]; then
    ngrok config add-authtoken $authtoken
    echo "✅ Authtoken configured"
else
    echo "⚠️  Skipped authtoken configuration"
    echo "   You'll need to run: ngrok config add-authtoken YOUR_TOKEN"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🚀 Step 4: Starting ngrok tunnel"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Starting ngrok on port 8000..."
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Copy the HTTPS URL from ngrok output below"
echo "   - Use it in Streamlit Cloud secrets as API_URL"
echo "   - Keep this terminal running!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
sleep 2

# Start ngrok
ngrok http 8000
