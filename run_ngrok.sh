#!/bin/bash

# Simple script to run ngrok for exposing the API to Streamlit Cloud
# Run this AFTER the Jenkins pipeline completes successfully

echo "═══════════════════════════════════════"
echo "   Starting ngrok tunnel for API"
echo "═══════════════════════════════════════"
echo ""

# Check if API is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ ERROR: API is not running on port 8000"
    echo "   Please run the Jenkins pipeline first to start the services."
    exit 1
fi

echo "✅ API is running on port 8000"
echo ""
echo "🚀 Starting ngrok tunnel..."
echo ""
echo "📝 Note: Keep this terminal open to maintain the tunnel"
echo "   Press Ctrl+C to stop ngrok when done"
echo ""
echo "═══════════════════════════════════════"
echo ""

# Start ngrok (foreground - will show URL directly)
exec ngrok http 8000

