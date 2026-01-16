# 📄 PDF to JSON Converter

**Convertisseur professionnel de PDF en JSON** avec extraction structurée, OCR et détection de tableaux.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Fonctionnalités

### Extraction Avancée
- ✅ **Texte natif** - Extraction rapide via PyMuPDF
- ✅ **OCR intégré** - Tesseract pour PDFs scannés
- ✅ **Détection de tableaux** - Extraction structurée avec pdfplumber
- ✅ **Bounding boxes** - Coordonnées précises de chaque élément
- ✅ **Métadonnées complètes** - Traçabilité totale

### Modes d'Extraction
- 🚀 **Rapide** - Extraction texte natif uniquement
- ⚖️ **Équilibré** - Texte + tableaux + OCR auto (recommandé)
- 🎯 **Précis** - Extraction haute qualité avec OCR forcé

### Technologies
- **Backend** - Python 3.11 + FastAPI + uvicorn
- **Extraction PDF** - PyMuPDF (fitz) + pdfplumber
- **OCR** - Tesseract 5.0+
- **Frontend** - Vanilla JavaScript ES6+ (modulaire)
- **Déploiement** - Docker + docker-compose

## 📋 Table des matières

- [Installation](#-installation)
- [Démarrage Rapide](#-démarrage-rapide)
- [Architecture](#-architecture)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Développement](#-développement)
- [Production](#-production)

---

## 🚀 Installation

### Prérequis

- **Python 3.11+**
- **Tesseract OCR** (optionnel mais recommandé)
- **Docker & Docker Compose** (pour déploiement conteneurisé)

### Option 1: Installation avec Docker (Recommandé)

```bash
# Cloner le repository
git clone <repository-url>
cd cv-romain_helias

# Copier le fichier d'environnement
cp .env.example .env

# Lancer avec Docker Compose
docker-compose up -d

# Accéder à l'application
# Frontend: http://localhost:8080
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Installation Locale

#### Backend

```bash
# Naviguer vers le backend
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Installer Tesseract OCR
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng

# macOS
brew install tesseract tesseract-lang

# Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
# Naviguer vers le frontend
cd frontend/src

# Option 1: Python simple server
python -m http.server 8080

# Option 2: Node.js http-server
npx http-server -p 8080

# Ouvrir dans le navigateur
# http://localhost:8080
```

---

## 🎯 Démarrage Rapide

### 1. Interface Web

1. Ouvrez http://localhost:8080
2. Glissez-déposez un PDF ou cliquez pour parcourir
3. Configurez les options (profil, OCR, langue)
4. Cliquez sur "Convertir en JSON"
5. Téléchargez le résultat

### 2. API cURL

```bash
# Extraire un PDF
curl -X POST http://localhost:8000/api/v1/extract \
  -F "file=@document.pdf" \
  -F "profile=balanced" \
  -F "ocr_mode=auto" \
  -F "ocr_lang=fra"

# Health check
curl http://localhost:8000/api/v1/health
```

### 3. Python Client

```python
import requests

with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/extract',
        files={'file': f},
        data={'profile': 'balanced', 'ocr_mode': 'auto'}
    )
    result = response.json()
```

---

## 🏗 Architecture

### Structure du Projet

```
cv-romain_helias/
├── backend/                    # API Backend
│   ├── app/
│   │   ├── api/               # Endpoints REST
│   │   ├── models/            # Modèles Pydantic
│   │   ├── services/          # Services métier
│   │   ├── utils/             # Utilitaires
│   │   ├── config.py          # Configuration
│   │   └── main.py            # Point d'entrée
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Interface Web
│   ├── src/
│   │   ├── css/              # Styles modulaires
│   │   ├── js/               # JavaScript ES6+
│   │   └── index.html
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 📚 API Documentation

### POST `/api/v1/extract`

Extrait le contenu structuré d'un PDF.

**Paramètres:**
- `file` - Fichier PDF (max 50MB)
- `profile` - `fast`, `balanced`, `accurate`
- `ocr_mode` - `auto`, `on`, `off`
- `ocr_lang` - `fra`, `eng`, `spa`, `deu`, `ita`, `por`
- `page_range` - Pages à extraire (ex: "1-5")
- `detect_tables` - Activer détection tableaux

**Documentation interactive:** http://localhost:8000/docs

---

## ⚙ Configuration

Variables d'environnement dans `.env`:

```bash
ENVIRONMENT=production
DEBUG=false
API_PORT=8000
MAX_UPLOAD_SIZE=52428800
DEFAULT_OCR_LANG=fra
LOG_LEVEL=INFO
```

---

## 💻 Développement

```bash
# Backend avec hot-reload
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend/src
python -m http.server 8080
```

---

## 🚢 Production

```bash
# Lancer avec Docker
docker-compose up -d --build

# Vérifier les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

---

## 📖 Caractéristiques Techniques

### Backend
- ✅ Architecture modulaire avec séparation des concerns
- ✅ Validation automatique via Pydantic
- ✅ Gestion d'erreurs robuste
- ✅ Logging structuré (JSON)
- ✅ CORS configuré
- ✅ Health checks
- ✅ Documentation OpenAPI auto-générée

### Frontend
- ✅ JavaScript ES6+ modulaire
- ✅ Gestion d'état réactive
- ✅ API client séparé
- ✅ UI/UX moderne
- ✅ CSS variables pour thème cohérent
- ✅ Responsive design

### Extraction PDF
- ✅ Multi-extractors (PyMuPDF + pdfplumber)
- ✅ OCR intelligent avec Tesseract
- ✅ Détection de tableaux
- ✅ Classification automatique des éléments
- ✅ Extraction de métadonnées complètes
- ✅ Calcul de hash SHA-256
- ✅ Bounding boxes précises

---

## 🤝 Contribution

Les contributions sont bienvenues! Ouvrez une issue ou une PR.

---

## 📝 License

MIT License

---

**Fait avec ❤️ - PDF to JSON Converter v1.0.0**
