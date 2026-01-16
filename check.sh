#!/bin/bash

echo "🔍 Vérification de l'application"
echo "================================"
echo ""

# Vérifier backend
echo "Backend (http://localhost:8000):"
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "  ✅ Backend actif"
    curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
else
    echo "  ❌ Backend non accessible"
fi

echo ""

# Vérifier frontend
echo "Frontend (http://localhost:8080):"
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "  ✅ Frontend actif"
else
    echo "  ❌ Frontend non accessible"
fi

echo ""
echo "📊 Processus:"
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "  Backend PID: $BACKEND_PID (✅ actif)"
    else
        echo "  Backend PID: $BACKEND_PID (❌ arrêté)"
    fi
fi

if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "  Frontend PID: $FRONTEND_PID (✅ actif)"
    else
        echo "  Frontend PID: $FRONTEND_PID (❌ arrêté)"
    fi
fi

