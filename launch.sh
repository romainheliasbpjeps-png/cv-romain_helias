#!/bin/bash

echo "🚀 Lancement de PDF to JSON Converter"
echo "======================================"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Backend
echo "📦 Installation du backend..."
cd backend

# Créer venv si nécessaire
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer venv
source venv/bin/activate

# Installer dépendances
echo "Installation des dépendances..."
pip install -q -r requirements.txt

# Lancer backend en arrière-plan
echo "🐍 Lancement du backend sur http://localhost:8000..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

# Attendre que le backend démarre
sleep 3

# Frontend
cd ../frontend/src
echo "🎨 Lancement du frontend sur http://localhost:8080..."
nohup python3 -m http.server 8080 > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../../frontend.pid

cd ../..

echo ""
echo "✅ Application lancée!"
echo "================================"
echo "📱 Frontend:     http://localhost:8080"
echo "🔧 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 Pour arrêter:"
echo "   ./stop.sh"
echo ""

