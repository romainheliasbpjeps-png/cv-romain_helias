/**
 * API Client
 * Handles all communication with the backend API
 */

import { API_CONFIG } from './config.js';

class APIClient {
    constructor() {
        this.baseUrl = API_CONFIG.baseUrl;
        this.apiPrefix = API_CONFIG.apiPrefix;
        this.timeout = API_CONFIG.timeout;
    }

    /**
     * Build full API URL
     */
    _buildUrl(endpoint) {
        return `${this.baseUrl}${this.apiPrefix}${endpoint}`;
    }

    /**
     * Handle API response
     */
    async _handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({
                error: `HTTP ${response.status}: ${response.statusText}`
            }));
            throw new Error(error.error || error.detail || 'API request failed');
        }
        return response.json();
    }

    /**
     * Extract PDF to JSON
     */
    async extractPDF(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('profile', options.profile || 'balanced');
        formData.append('ocr_mode', options.ocrMode || 'auto');
        formData.append('ocr_lang', options.ocrLang || 'fra');
        formData.append('detect_tables', options.detectTables !== false);
        formData.append('extract_images', options.extractImages || false);

        if (options.pageRange) {
            formData.append('page_range', options.pageRange);
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(this._buildUrl('/extract'), {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            return this._handleResponse(response);
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - PDF processing took too long');
            }
            throw error;
        }
    }

    /**
     * Get JSON schema
     */
    async getSchema() {
        const response = await fetch(this._buildUrl('/schema'));
        return this._handleResponse(response);
    }

    /**
     * Health check
     */
    async healthCheck() {
        const response = await fetch(this._buildUrl('/health'));
        return this._handleResponse(response);
    }

    /**
     * Get available OCR languages
     */
    async getOCRLanguages() {
        const response = await fetch(this._buildUrl('/ocr/languages'));
        return this._handleResponse(response);
    }

    /**
     * Get extraction profiles
     */
    async getProfiles() {
        const response = await fetch(this._buildUrl('/profiles'));
        return this._handleResponse(response);
    }
}

// Export singleton instance
export const apiClient = new APIClient();
