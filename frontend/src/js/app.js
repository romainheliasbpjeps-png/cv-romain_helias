/**
 * Main Application Controller
 * Orchestrates the entire PDF to JSON conversion application
 */

import { stateManager } from './state.js';
import { uiManager } from './ui.js';
import { apiClient } from './api.js';
import { UPLOAD_CONFIG } from './config.js';

class Application {
    constructor() {
        this.fileInput = null;
        this.init();
    }

    /**
     * Initialize application
     */
    async init() {
        console.log('🚀 Initializing PDF to JSON Converter...');

        // Create hidden file input
        this.createFileInput();

        // Setup event listeners
        this.setupEventListeners();

        // Check API health
        await this.checkAPIHealth();

        console.log('✅ Application ready');
    }

    /**
     * Create hidden file input element
     */
    createFileInput() {
        this.fileInput = document.createElement('input');
        this.fileInput.type = 'file';
        this.fileInput.accept = UPLOAD_CONFIG.acceptMimeTypes;
        this.fileInput.style.display = 'none';
        document.body.appendChild(this.fileInput);

        this.fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFile(file);
            }
        });
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        const uploadZone = document.getElementById('uploadZone');
        const convertBtn = document.getElementById('convertBtn');

        // Upload zone click
        uploadZone.addEventListener('click', () => {
            this.fileInput.click();
        });

        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('active');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('active');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('active');
            const file = e.dataTransfer.files[0];
            if (file) {
                this.handleFile(file);
            }
        });

        // Convert button
        convertBtn.addEventListener('click', () => {
            this.convertPDF();
        });

        // Expose global functions for HTML onclick handlers
        window.toggleElement = this.toggleElement.bind(this);
        window.changePage = this.changePage.bind(this);
        window.downloadJSON = this.downloadJSON.bind(this);
        window.downloadSchema = this.downloadSchema.bind(this);
    }

    /**
     * Handle file selection
     */
    handleFile(file) {
        console.log('📄 File selected:', file.name);

        // Validate file type
        if (!file.name.endsWith('.pdf')) {
            uiManager.showAlert('❌ Veuillez sélectionner un fichier PDF valide', 'error');
            return;
        }

        // Validate file size
        if (file.size > UPLOAD_CONFIG.maxSizeBytes) {
            uiManager.showAlert(
                `❌ Fichier trop volumineux (max ${UPLOAD_CONFIG.maxSizeMB}MB)`,
                'error'
            );
            return;
        }

        // Update state
        stateManager.setState({ currentFile: file, error: null });
    }

    /**
     * Convert PDF to JSON
     */
    async convertPDF() {
        const { currentFile } = stateManager.getState();
        if (!currentFile) {
            uiManager.showAlert('❌ Veuillez d\'abord sélectionner un fichier', 'error');
            return;
        }

        console.log('🔄 Starting conversion...');

        // Update state
        stateManager.setState({
            isProcessing: true,
            error: null,
            extractionResult: null
        });

        uiManager.hideProgress();

        try {
            // Get extraction options
            const options = uiManager.getExtractionOptions();
            console.log('Options:', options);

            // Show progress
            stateManager.setState({
                progress: { current: 0, total: 100, message: 'Envoi du fichier au serveur...' }
            });

            // Call API
            const response = await apiClient.extractPDF(currentFile, options);

            if (!response.success) {
                throw new Error(response.error || 'Extraction failed');
            }

            console.log('✅ Extraction completed');

            // Update state with result
            stateManager.setState({
                extractionResult: response.result,
                isProcessing: false,
                currentPage: 0
            });

            uiManager.hideProgress();

            // Calculate stats
            const { result } = response;
            const totalElements = result.pages.reduce((sum, p) => sum + p.elements.length, 0);
            const processingTime = result.meta.processing_time_seconds;

            uiManager.showAlert(
                `✅ Extraction réussie! ${result.document.page_count} page(s), ` +
                `${totalElements} élément(s) extraits en ${processingTime}s`,
                'success'
            );

        } catch (error) {
            console.error('❌ Extraction failed:', error);
            stateManager.setState({
                error: error.message,
                isProcessing: false
            });
            uiManager.hideProgress();
        }
    }

    /**
     * Toggle element details visibility
     */
    toggleElement(index) {
        const elem = document.getElementById(`elem-${index}`);
        if (elem) {
            elem.classList.toggle('show');
        }
    }

    /**
     * Change current page
     */
    changePage(pageIndex) {
        const { extractionResult } = stateManager.getState();
        if (!extractionResult) return;

        stateManager.setState({ currentPage: pageIndex });
        uiManager.renderPage(extractionResult, pageIndex);
    }

    /**
     * Download JSON result
     */
    downloadJSON() {
        const { extractionResult } = stateManager.getState();
        if (!extractionResult) return;

        const blob = new Blob(
            [JSON.stringify(extractionResult, null, 2)],
            { type: 'application/json' }
        );
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${extractionResult.document.file_name.replace('.pdf', '')}_extraction.json`;
        a.click();
        URL.revokeObjectURL(url);

        uiManager.showAlert('✅ JSON téléchargé avec succès!', 'success');
    }

    /**
     * Download JSON schema
     */
    async downloadSchema() {
        try {
            const schema = await apiClient.getSchema();
            const blob = new Blob(
                [JSON.stringify(schema, null, 2)],
                { type: 'application/json' }
            );
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'extraction-schema.json';
            a.click();
            URL.revokeObjectURL(url);

            uiManager.showAlert('✅ Schéma téléchargé avec succès!', 'success');
        } catch (error) {
            uiManager.showAlert('❌ Impossible de télécharger le schéma', 'error');
        }
    }

    /**
     * Check API health
     */
    async checkAPIHealth() {
        try {
            const health = await apiClient.healthCheck();
            console.log('API Health:', health);

            if (health.services.ocr !== 'available') {
                console.warn('⚠️ OCR service not available');
            }
        } catch (error) {
            console.error('⚠️ API health check failed:', error);
            uiManager.showAlert(
                '⚠️ Backend API non disponible. Vérifiez que le serveur est démarré.',
                'error'
            );
        }
    }
}

// Initialize application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new Application();
    });
} else {
    new Application();
}

export default Application;
