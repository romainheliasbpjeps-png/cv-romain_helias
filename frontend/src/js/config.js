/**
 * Application Configuration
 * Centralized configuration management
 */

export const API_CONFIG = {
    baseUrl: window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : window.location.origin,
    apiPrefix: '/api/v1',
    timeout: 300000, // 5 minutes
};

export const UPLOAD_CONFIG = {
    maxSizeMB: 50,
    maxSizeBytes: 50 * 1024 * 1024,
    allowedExtensions: ['.pdf'],
    acceptMimeTypes: 'application/pdf',
};

export const PDF_CONFIG = {
    workerSrc: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js',
    pdfJsSrc: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js',
};

export const EXTRACTION_PROFILES = {
    fast: {
        label: 'Rapide',
        description: 'Extraction rapide, texte natif uniquement'
    },
    balanced: {
        label: 'Équilibré',
        description: 'Bon compromis vitesse/qualité'
    },
    accurate: {
        label: 'Précis',
        description: 'Extraction haute qualité avec OCR'
    }
};

export const OCR_LANGUAGES = {
    fra: 'Français',
    eng: 'English',
    spa: 'Español',
    deu: 'Deutsch',
    ita: 'Italiano',
    por: 'Português'
};

export const OCR_MODES = {
    auto: 'Automatique',
    on: 'Activé',
    off: 'Désactivé'
};
