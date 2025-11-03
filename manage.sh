#!/bin/bash

# Migraine Prediction System - Quick Start Script

echo "🏥 Migraine Prediction System"
echo "=============================="
echo ""

# Function to check if Docker is running
check_docker() {
    if ! sudo docker info >/dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to start services
start_services() {
    echo ""
    echo "🚀 Starting all services..."
    sudo docker-compose up -d
    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "✅ Services are starting up!"
    echo ""
    echo "📊 Access Points:"
    echo "  🎨 Streamlit UI:  http://localhost:8501"
    echo "  🔌 API:           http://localhost:8000"
    echo "  📚 API Docs:      http://localhost:8000/docs"
    echo "  📈 MLflow:        http://localhost:5000"
    echo ""
}

# Function to stop services
stop_services() {
    echo ""
    echo "🛑 Stopping all services..."
    sudo docker-compose down
    echo "✅ All services stopped"
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Container Status:"
    sudo docker-compose ps
    echo ""
}

# Function to show logs
show_logs() {
    echo ""
    echo "📋 Recent Logs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Streamlit UI Logs:"
    sudo docker logs migraine-streamlit --tail 20
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "API Logs:"
    sudo docker logs migraine-api --tail 20
    echo ""
}

# Function to rebuild services
rebuild_services() {
    echo ""
    echo "🔨 Rebuilding all services..."
    sudo docker-compose down
    sudo docker-compose build --no-cache
    sudo docker-compose up -d
    echo "✅ Services rebuilt and started"
}

# Main menu
check_docker

if [ $# -eq 0 ]; then
    echo "Usage: $0 {start|stop|status|logs|rebuild|restart}"
    echo ""
    echo "Commands:"
    echo "  start    - Start all services"
    echo "  stop     - Stop all services"
    echo "  status   - Show container status"
    echo "  logs     - Show recent logs"
    echo "  rebuild  - Rebuild and restart all services"
    echo "  restart  - Restart all services"
    exit 1
fi

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    rebuild)
        rebuild_services
        ;;
    restart)
        echo "🔄 Restarting services..."
        sudo docker-compose restart
        echo "✅ Services restarted"
        show_status
        ;;
    *)
        echo "Invalid command: $1"
        echo "Usage: $0 {start|stop|status|logs|rebuild|restart}"
        exit 1
        ;;
esac
