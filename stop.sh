#!/bin/bash

echo "🛑 Arrêt de PDF to JSON Converter"
echo "=================================="

if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Arrêt du backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Arrêt du frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm frontend.pid
fi

echo "✅ Application arrêtée"

