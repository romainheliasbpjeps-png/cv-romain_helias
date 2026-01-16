/**
 * UI Components and Rendering
 * Manages all UI updates and component rendering
 */

import { stateManager } from './state.js';
import { EXTRACTION_PROFILES, OCR_LANGUAGES, OCR_MODES } from './config.js';

export class UIManager {
    constructor() {
        this.elements = this._getElements();
        this._setupStateListeners();
    }

    /**
     * Get all DOM elements
     */
    _getElements() {
        return {
            uploadZone: document.getElementById('uploadZone'),
            convertBtn: document.getElementById('convertBtn'),
            alertBox: document.getElementById('alertBox'),
            previewArea: document.getElementById('previewArea'),
            jsonOutput: document.getElementById('jsonOutput'),
            statsContainer: document.getElementById('statsContainer'),
            downloadBtns: document.getElementById('downloadBtns'),
            progressBar: document.getElementById('progressBar'),
            progressFill: document.getElementById('progressFill'),
            processingStatus: document.getElementById('processingStatus'),
            profileSelect: document.getElementById('profile'),
            ocrModeSelect: document.getElementById('ocrMode'),
            ocrLangSelect: document.getElementById('ocrLang')
        };
    }

    /**
     * Setup state listeners
     */
    _setupStateListeners() {
        stateManager.subscribe('currentFile', (file) => {
            if (file) {
                this.updateUploadZone(file);
                this.elements.convertBtn.disabled = false;
            }
        });

        stateManager.subscribe('extractionResult', (result) => {
            if (result) {
                this.renderPreview(result);
                this.renderJSON(result);
                this.renderDownloadButtons();
            }
        });

        stateManager.subscribe('isProcessing', (processing) => {
            this.elements.convertBtn.disabled = processing;
            this.elements.convertBtn.textContent = processing
                ? '⏳ Traitement en cours...'
                : '🚀 Convertir en JSON';
        });

        stateManager.subscribe('error', (error) => {
            if (error) {
                this.showAlert(error, 'error');
            }
        });

        stateManager.subscribe('progress', (progress) => {
            if (progress.total > 0) {
                this.updateProgress(progress);
            }
        });
    }

    /**
     * Update upload zone with file info
     */
    updateUploadZone(file) {
        const sizeMB = (file.size / 1024 / 1024).toFixed(2);
        this.elements.uploadZone.innerHTML = `
            <div class="upload-icon">📄</div>
            <div class="upload-text">${file.name}</div>
            <div class="upload-hint">${sizeMB} MB</div>
        `;
        this.showAlert('✅ PDF chargé! Cliquez sur "Convertir" pour l\'analyser', 'success');
    }

    /**
     * Show alert message
     */
    showAlert(message, type = 'info') {
        this.elements.alertBox.innerHTML = `
            <div class="alert alert-${type}">${message}</div>
        `;

        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                this.elements.alertBox.innerHTML = '';
            }, 5000);
        }
    }

    /**
     * Update progress bar
     */
    updateProgress(progress) {
        const percent = progress.total > 0
            ? (progress.current / progress.total) * 100
            : 0;

        this.elements.progressBar.style.display = 'block';
        this.elements.progressFill.style.width = `${percent}%`;
        this.elements.processingStatus.style.display = 'block';
        this.elements.processingStatus.textContent = progress.message;
    }

    /**
     * Hide progress indicators
     */
    hideProgress() {
        this.elements.progressBar.style.display = 'none';
        this.elements.progressFill.style.width = '0%';
        this.elements.processingStatus.style.display = 'none';
    }

    /**
     * Render extraction preview
     */
    renderPreview(result) {
        this.renderStats(result);
        this.renderPage(result, stateManager.getState().currentPage);
    }

    /**
     * Render statistics
     */
    renderStats(result) {
        const totalElements = result.pages.reduce(
            (sum, p) => sum + p.elements.length,
            0
        );

        this.elements.statsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${result.document.page_count}</div>
                    <div class="stat-label">Pages</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${totalElements}</div>
                    <div class="stat-label">Éléments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${result.artifacts.ocr_used ? 'OUI' : 'NON'}</div>
                    <div class="stat-label">OCR</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${result.artifacts.extraction_profile.toUpperCase()}</div>
                    <div class="stat-label">Profil</div>
                </div>
            </div>
        `;
    }

    /**
     * Render single page
     */
    renderPage(result, pageIndex) {
        const page = result.pages[pageIndex];
        if (!page) return;

        // Page tabs
        let tabs = '<div class="page-tabs">';
        result.pages.forEach((p, i) => {
            tabs += `
                <div class="page-tab ${i === pageIndex ? 'active' : ''}"
                     onclick="window.changePage(${i})">
                    Page ${i + 1}
                </div>
            `;
        });
        tabs += '</div>';

        // Page info
        const pageInfo = `
            <div class="page-info">
                <strong>Page ${pageIndex + 1}</strong> —
                ${page.width.toFixed(0)} × ${page.height.toFixed(0)} pts •
                ${page.elements.length} éléments
                ${page.is_scanned ? ' • <span style="color: #f59e0b;">Scanné</span>' : ''}
            </div>
        `;

        // Elements
        let elements = '';
        page.elements.forEach((elem, i) => {
            const confPercent = (elem.confidence * 100).toFixed(0);
            const textPreview = elem.text
                ? (elem.text.length > 100 ? elem.text.substring(0, 100) + '...' : elem.text)
                : '[No text]';

            elements += `
                <div class="element">
                    <div class="element-header" onclick="window.toggleElement(${i})">
                        <span class="element-type">${elem.type}</span>
                        <div class="element-meta">
                            <span class="badge badge-source">${elem.source_method}</span>
                            <span class="badge badge-confidence">${confPercent}%</span>
                        </div>
                    </div>
                    <div class="element-content" id="elem-${i}">
                        ${elem.text ? `<div class="element-text">${elem.text}</div>` : ''}
                        ${elem.bbox ? `
                            <div class="element-bbox">
                                bbox: (${elem.bbox.x0.toFixed(1)}, ${elem.bbox.y0.toFixed(1)}) →
                                      (${elem.bbox.x1.toFixed(1)}, ${elem.bbox.y1.toFixed(1)})
                            </div>
                        ` : ''}
                        ${elem.font_size ? `
                            <div class="element-bbox">
                                Font: ${elem.font_name || 'N/A'} ${elem.font_size.toFixed(1)}pt
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        this.elements.previewArea.innerHTML = tabs + pageInfo + elements;
    }

    /**
     * Render JSON output
     */
    renderJSON(result) {
        this.elements.jsonOutput.textContent = JSON.stringify(result, null, 2);
    }

    /**
     * Render download buttons
     */
    renderDownloadButtons() {
        this.elements.downloadBtns.innerHTML = `
            <div class="download-btns">
                <button class="btn-download btn-json" onclick="window.downloadJSON()">
                    ⬇️ Télécharger JSON
                </button>
                <button class="btn-download btn-schema" onclick="window.downloadSchema()">
                    ⬇️ Télécharger Schéma
                </button>
            </div>
        `;
    }

    /**
     * Get extraction options from form
     */
    getExtractionOptions() {
        return {
            profile: this.elements.profileSelect.value,
            ocrMode: this.elements.ocrModeSelect.value,
            ocrLang: this.elements.ocrLangSelect.value,
            detectTables: true,
            extractImages: false
        };
    }
}

// Export singleton instance
export const uiManager = new UIManager();
