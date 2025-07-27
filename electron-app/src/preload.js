/**
 * Uranus-AI Editor - Electron Preload Script
 * Provides secure communication between renderer and main process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Backend management
    getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
    restartBackend: () => ipcRenderer.invoke('restart-backend'),
    openBackendLogs: () => ipcRenderer.invoke('open-backend-logs'),
    
    // Menu events
    onMenuAction: (callback) => {
        const channels = [
            'menu-new-file',
            'menu-open-file', 
            'menu-save',
            'menu-toggle-ai',
            'menu-explain-code',
            'menu-refactor-code',
            'menu-ai-settings'
        ];
        
        channels.forEach(channel => {
            ipcRenderer.on(channel, callback);
        });
        
        // Return cleanup function
        return () => {
            channels.forEach(channel => {
                ipcRenderer.removeListener(channel, callback);
            });
        };
    },
    
    // System information
    platform: process.platform,
    versions: process.versions,
    
    // Utility functions
    log: (level, message) => {
        console[level](`[Uranus-AI] ${message}`);
    }
});

// Expose Uranus-AI specific APIs
contextBridge.exposeInMainWorld('uranusAI', {
    version: '1.2.0',
    name: 'Uranus-AI Editor',
    
    // AI Assistant integration
    ai: {
        isAvailable: async () => {
            try {
                const status = await ipcRenderer.invoke('get-backend-status');
                return status.isReady;
            } catch (error) {
                console.error('Failed to check AI availability:', error);
                return false;
            }
        },
        
        getBackendUrl: async () => {
            try {
                const status = await ipcRenderer.invoke('get-backend-status');
                return status.url;
            } catch (error) {
                console.error('Failed to get backend URL:', error);
                return 'http://localhost:8000';
            }
        }
    },
    
    // Configuration
    config: {
        isDevelopment: process.env.NODE_ENV === 'development',
        platform: process.platform,
        arch: process.arch
    }
});

// Log that preload script has loaded
console.log('🔧 Uranus-AI preload script loaded');

// Handle uncaught errors
window.addEventListener('error', (event) => {
    console.error('Uncaught error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});

