/**
 * Application State Management
 * Simple reactive state manager
 */

class StateManager {
    constructor() {
        this.state = {
            currentFile: null,
            extractionResult: null,
            currentPage: 0,
            isProcessing: false,
            error: null,
            progress: { current: 0, total: 0, message: '' }
        };
        this.listeners = new Map();
    }

    /**
     * Get current state
     */
    getState() {
        return { ...this.state };
    }

    /**
     * Update state
     */
    setState(updates) {
        const oldState = { ...this.state };
        this.state = { ...this.state, ...updates };
        this._notifyListeners(oldState, this.state);
    }

    /**
     * Subscribe to state changes
     */
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, []);
        }
        this.listeners.get(key).push(callback);

        // Return unsubscribe function
        return () => {
            const callbacks = this.listeners.get(key);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        };
    }

    /**
     * Notify listeners of state changes
     */
    _notifyListeners(oldState, newState) {
        for (const [key, callbacks] of this.listeners.entries()) {
            if (oldState[key] !== newState[key]) {
                callbacks.forEach(callback => callback(newState[key], oldState[key]));
            }
        }
    }

    /**
     * Reset state
     */
    reset() {
        this.setState({
            currentFile: null,
            extractionResult: null,
            currentPage: 0,
            isProcessing: false,
            error: null,
            progress: { current: 0, total: 0, message: '' }
        });
    }
}

// Export singleton instance
export const stateManager = new StateManager();
