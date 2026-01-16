.PHONY: help install dev start stop clean test docker-build docker-up docker-down

# Default target
help:
	@echo "📄 PDF to JSON Converter - Available commands:"
	@echo ""
	@echo "  make install       - Install dependencies (local)"
	@echo "  make dev          - Start development servers"
	@echo "  make start        - Start with Docker"
	@echo "  make stop         - Stop Docker containers"
	@echo "  make clean        - Clean temporary files"
	@echo "  make test         - Run tests"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop and remove Docker containers"
	@echo ""

# Install dependencies locally
install:
	@echo "📦 Installing backend dependencies..."
	cd backend && python -m venv venv && \
		. venv/bin/activate && \
		pip install -r requirements.txt
	@echo "✅ Installation complete!"
	@echo "ℹ️  Don't forget to install Tesseract OCR separately"

# Start development servers
dev:
	@echo "🚀 Starting development servers..."
	@echo "Backend will be at http://localhost:8000"
	@echo "Frontend will be at http://localhost:8080"
	@echo ""
	@echo "Press Ctrl+C to stop"
	@trap 'kill 0' EXIT; \
		cd backend && . venv/bin/activate && \
		uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
		cd frontend/src && python -m http.server 8080

# Start with Docker
start: docker-up

# Stop Docker containers
stop: docker-down

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/uploads/* backend/temp/* 2>/dev/null || true
	@echo "✅ Clean complete!"

# Run tests
test:
	@echo "🧪 Running tests..."
	cd backend && . venv/bin/activate && pytest -v

# Build Docker images
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

# Start Docker containers
docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Containers started!"
	@echo "Frontend: http://localhost:8080"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Stop and remove Docker containers
docker-down:
	@echo "🐳 Stopping Docker containers..."
	docker-compose down
	@echo "✅ Containers stopped!"

# Show logs
logs:
	docker-compose logs -f

# Health check
health:
	@echo "🏥 Checking API health..."
	@curl -s http://localhost:8000/api/v1/health | python -m json.tool || \
		echo "❌ API not responding"
