# 🚀 Quickstart Guide - PDF to JSON Converter

Guide de démarrage rapide en 5 minutes.

## Option 1: Docker (Le plus simple)

### Prérequis
- Docker
- Docker Compose

### Étapes

```bash
# 1. Cloner le projet
git clone <repo-url>
cd cv-romain_helias

# 2. Copier la configuration
cp .env.example .env

# 3. Lancer
docker-compose up -d

# 4. Ouvrir dans le navigateur
# http://localhost:8080
```

C'est tout! L'application est prête.

### Vérifier que tout fonctionne

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Devrait retourner:
# {"status":"healthy","services":{"ocr":"available","pdf_extraction":"available"}}
```

### Arrêter

```bash
docker-compose down
```

---

## Option 2: Installation locale

### Prérequis
- Python 3.11+
- Tesseract OCR

### Installer Tesseract

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
Télécharger depuis: https://github.com/UB-Mannheim/tesseract/wiki

### Lancer l'application

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. Frontend (nouveau terminal)
cd frontend/src
python -m http.server 8080
```

Ouvrir: http://localhost:8080

---

## Option 3: Avec Makefile (Linux/Mac)

```bash
# Installer les dépendances
make install

# Lancer en dev
make dev

# Ou avec Docker
make start
```

---

## Test Rapide

### Via l'interface web

1. Ouvrir http://localhost:8080
2. Glisser-déposer un PDF
3. Cliquer sur "Convertir en JSON"
4. Télécharger le résultat

### Via l'API

```bash
# Test avec curl
curl -X POST http://localhost:8000/api/v1/extract \
  -F "file=@votre-document.pdf" \
  -F "profile=balanced"
```

### Via Python

```python
import requests

with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/extract',
        files={'file': f},
        data={'profile': 'balanced'}
    )

result = response.json()
print(f"Succès: {result['success']}")
print(f"Pages: {result['result']['document']['page_count']}")
```

---

## Résolution de problèmes

### Le backend ne démarre pas

```bash
# Vérifier Python
python --version  # Doit être 3.11+

# Vérifier les dépendances
cd backend
pip install -r requirements.txt

# Vérifier Tesseract
tesseract --version
```

### L'OCR ne fonctionne pas

```bash
# Vérifier Tesseract
tesseract --list-langs

# Devrait afficher fra, eng, etc.
# Si absent, installer les langues:
# Ubuntu: sudo apt-get install tesseract-ocr-fra
# macOS: brew install tesseract-lang
```

### Docker ne démarre pas

```bash
# Vérifier Docker
docker --version
docker-compose --version

# Voir les logs
docker-compose logs backend
docker-compose logs frontend
```

### Le frontend ne se connecte pas au backend

Vérifier que le backend est bien sur http://localhost:8000

Modifier si besoin dans `frontend/src/js/config.js`:
```javascript
export const API_CONFIG = {
    baseUrl: 'http://localhost:8000',  // <- Vérifier cette URL
    // ...
};
```

---

## Prochaines étapes

1. **Lire la documentation complète** - [README.md](README.md)
2. **Explorer l'API** - http://localhost:8000/docs
3. **Tester différents profils** - fast, balanced, accurate
4. **Essayer l'OCR** - avec des PDFs scannés
5. **Détecter des tableaux** - avec des PDFs contenant des tableaux

---

## Support

Problèmes? Ouvrir une issue sur GitHub!

**Bon démarrage! 🚀**
