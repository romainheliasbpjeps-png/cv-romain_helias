# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-16

### Added
- ✅ Initial release
- ✅ Professional backend API with FastAPI
- ✅ PDF extraction with PyMuPDF and pdfplumber
- ✅ OCR support with Tesseract
- ✅ Table detection
- ✅ Bounding box extraction
- ✅ Three extraction profiles (fast, balanced, accurate)
- ✅ Multi-language OCR support (fra, eng, spa, deu, ita, por)
- ✅ Modern modular frontend with ES6+
- ✅ Docker support with docker-compose
- ✅ Comprehensive documentation
- ✅ API documentation with Swagger UI
- ✅ Health check endpoints
- ✅ Structured logging
- ✅ Error handling and validation
- ✅ File hash calculation (SHA-256)
- ✅ Complete metadata extraction
- ✅ Element type classification
- ✅ Page range selection
- ✅ Responsive UI design
- ✅ Demo Python client
- ✅ Makefile for easy development
- ✅ Quickstart guide

### Features
- **Backend**
  - FastAPI 0.109+ with async support
  - Pydantic models for validation
  - Dependency injection
  - CORS configuration
  - Request timeout handling
  - Multi-worker support
  - JSON structured logging
  - Configuration via environment variables

- **Frontend**
  - Vanilla JavaScript ES6+ modules
  - State management pattern
  - API client abstraction
  - UI/UX manager
  - CSS custom properties
  - Drag & drop file upload
  - Real-time preview
  - JSON output viewer
  - Download functionality

- **PDF Extraction**
  - Native text extraction (PyMuPDF)
  - Table detection (pdfplumber)
  - OCR processing (Tesseract)
  - Automatic scanned page detection
  - Element type classification (heading, paragraph, list, table)
  - Bounding box coordinates
  - Font information extraction
  - Page metadata

### Technical
- Python 3.11+
- FastAPI 0.109+
- PyMuPDF 1.23+
- pdfplumber 0.11+
- Tesseract OCR 5.0+
- Docker & Docker Compose
- Nginx for frontend serving

### Documentation
- Comprehensive README
- Quickstart guide
- API documentation
- Code comments
- Docker setup guide
- Development guide

## [Unreleased]

### Planned
- [ ] Batch processing API endpoint
- [ ] WebSocket support for real-time progress
- [ ] Image extraction from PDFs
- [ ] PDF form field extraction
- [ ] Export to multiple formats (CSV, XML, YAML)
- [ ] Authentication/Authorization
- [ ] Rate limiting
- [ ] Caching layer (Redis)
- [ ] Async task queue (Celery)
- [ ] Database storage for results
- [ ] Admin dashboard
- [ ] User management
- [ ] API key management
- [ ] Usage analytics
- [ ] PDF preview in browser
- [ ] Advanced table parsing
- [ ] Header/footer detection
- [ ] Multi-column layout detection
- [ ] Mathematical formula extraction
- [ ] Code block detection
- [ ] Citation extraction
- [ ] Custom extraction rules
- [ ] Plugin system
- [ ] REST client libraries (Python, JavaScript, Go)
