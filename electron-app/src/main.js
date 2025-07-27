/**
 * Uranus-AI Editor - Electron Main Process
 * Manages the desktop application lifecycle and backend integration
 */

const { app, BrowserWindow, Menu, dialog, shell, ipcMain } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const WebSocket = require('ws');
const log = require('electron-log');

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'debug';

class UranusAIApp {
    constructor() {
        this.mainWindow = null;
        this.backendProcess = null;
        this.backendPort = 8000;
        this.isDev = process.argv.includes('--dev');
        this.isBackendReady = false;
        
        // Paths
        this.appPath = app.getAppPath();
        this.resourcesPath = process.resourcesPath || this.appPath;
        this.backendPath = path.join(this.resourcesPath, 'backend', 'uranus-ai-backend.exe');
        this.vscodePath = path.join(this.resourcesPath, 'vscode');
        
        log.info('🚀 Uranus-AI Editor starting...');
        log.info(`App path: ${this.appPath}`);
        log.info(`Resources path: ${this.resourcesPath}`);
        log.info(`Backend path: ${this.backendPath}`);
        log.info(`VSCode path: ${this.vscodePath}`);
        log.info(`Development mode: ${this.isDev}`);
    }

    async initialize() {
        // Set app user model ID for Windows
        if (process.platform === 'win32') {
            app.setAppUserModelId('com.uranusai.editor');
        }

        // Handle app events
        app.whenReady().then(() => this.onReady());
        app.on('window-all-closed', () => this.onWindowAllClosed());
        app.on('activate', () => this.onActivate());
        app.on('before-quit', () => this.onBeforeQuit());

        // Handle IPC messages
        this.setupIPC();
    }

    async onReady() {
        log.info('📱 Electron app ready');
        
        // Create application menu
        this.createMenu();
        
        // Start backend
        await this.startBackend();
        
        // Create main window
        this.createMainWindow();
        
        // Wait for backend to be ready
        await this.waitForBackend();
        
        // Load the application
        this.loadApplication();
    }

    createMainWindow() {
        log.info('🖼️ Creating main window');
        
        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 800,
            minHeight: 600,
            icon: path.join(__dirname, '../build/icon.png'),
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js'),
                webSecurity: !this.isDev
            },
            titleBarStyle: 'default',
            show: false // Don't show until ready
        });

        // Handle window events
        this.mainWindow.once('ready-to-show', () => {
            log.info('✅ Main window ready to show');
            this.mainWindow.show();
            
            if (this.isDev) {
                this.mainWindow.webContents.openDevTools();
            }
        });

        this.mainWindow.on('closed', () => {
            log.info('🔴 Main window closed');
            this.mainWindow = null;
        });

        // Handle external links
        this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });
    }

    async startBackend() {
        log.info('🔧 Starting backend process...');
        
        try {
            if (this.isDev) {
                // In development, start Python backend directly
                const pythonPath = 'python';
                const backendScript = path.join(this.appPath, '..', 'ai-backend', 'app', 'main.py');
                
                log.info(`Starting development backend: ${pythonPath} ${backendScript}`);
                
                this.backendProcess = spawn(pythonPath, [backendScript], {
                    cwd: path.join(this.appPath, '..', 'ai-backend'),
                    env: { ...process.env, PORT: this.backendPort.toString() }
                });
            } else {
                // In production, use compiled executable
                if (!fs.existsSync(this.backendPath)) {
                    throw new Error(`Backend executable not found: ${this.backendPath}`);
                }
                
                log.info(`Starting production backend: ${this.backendPath}`);
                
                this.backendProcess = spawn(this.backendPath, [], {
                    env: { ...process.env, PORT: this.backendPort.toString() }
                });
            }

            this.backendProcess.stdout.on('data', (data) => {
                log.info(`Backend stdout: ${data}`);
            });

            this.backendProcess.stderr.on('data', (data) => {
                log.warn(`Backend stderr: ${data}`);
            });

            this.backendProcess.on('close', (code) => {
                log.info(`Backend process exited with code ${code}`);
                this.isBackendReady = false;
            });

            this.backendProcess.on('error', (error) => {
                log.error(`Backend process error: ${error}`);
                this.showErrorDialog('Backend Error', `Failed to start backend: ${error.message}`);
            });

            log.info('✅ Backend process started');
            
        } catch (error) {
            log.error(`Failed to start backend: ${error}`);
            this.showErrorDialog('Startup Error', `Failed to start backend: ${error.message}`);
        }
    }

    async waitForBackend() {
        log.info('⏳ Waiting for backend to be ready...');
        
        const maxAttempts = 30;
        const delay = 1000;
        
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                const response = await fetch(`http://localhost:${this.backendPort}/health`);
                if (response.ok) {
                    log.info('✅ Backend is ready');
                    this.isBackendReady = true;
                    return;
                }
            } catch (error) {
                log.debug(`Backend not ready (attempt ${attempt}/${maxAttempts}): ${error.message}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, delay));
        }
        
        log.error('❌ Backend failed to start within timeout');
        this.showErrorDialog('Backend Error', 'Backend failed to start. Please check the logs.');
    }

    loadApplication() {
        log.info('📂 Loading application...');
        
        if (this.isDev) {
            // In development, load from development server
            this.mainWindow.loadURL('http://localhost:3000');
        } else {
            // In production, load from local files
            const indexPath = path.join(this.vscodePath, 'index.html');
            if (fs.existsSync(indexPath)) {
                this.mainWindow.loadFile(indexPath);
            } else {
                // Fallback to simple HTML page
                this.mainWindow.loadURL(`data:text/html,
                    <html>
                        <head><title>Uranus-AI Editor</title></head>
                        <body style="font-family: Arial, sans-serif; padding: 20px;">
                            <h1>🪐 Uranus-AI Editor</h1>
                            <p>Backend Status: <span id="status">Checking...</span></p>
                            <p>Backend URL: <a href="http://localhost:${this.backendPort}" target="_blank">http://localhost:${this.backendPort}</a></p>
                            <p>API Documentation: <a href="http://localhost:${this.backendPort}/docs" target="_blank">http://localhost:${this.backendPort}/docs</a></p>
                            <script>
                                fetch('http://localhost:${this.backendPort}/health')
                                    .then(r => r.json())
                                    .then(data => {
                                        document.getElementById('status').textContent = '✅ Running';
                                        document.getElementById('status').style.color = 'green';
                                    })
                                    .catch(e => {
                                        document.getElementById('status').textContent = '❌ Error';
                                        document.getElementById('status').style.color = 'red';
                                    });
                            </script>
                        </body>
                    </html>
                `);
            }
        }
    }

    createMenu() {
        const template = [
            {
                label: 'File',
                submenu: [
                    {
                        label: 'New File',
                        accelerator: 'CmdOrCtrl+N',
                        click: () => this.sendToRenderer('menu-new-file')
                    },
                    {
                        label: 'Open File',
                        accelerator: 'CmdOrCtrl+O',
                        click: () => this.sendToRenderer('menu-open-file')
                    },
                    {
                        label: 'Save',
                        accelerator: 'CmdOrCtrl+S',
                        click: () => this.sendToRenderer('menu-save')
                    },
                    { type: 'separator' },
                    {
                        label: 'Exit',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => app.quit()
                    }
                ]
            },
            {
                label: 'Edit',
                submenu: [
                    { role: 'undo' },
                    { role: 'redo' },
                    { type: 'separator' },
                    { role: 'cut' },
                    { role: 'copy' },
                    { role: 'paste' },
                    { role: 'selectall' }
                ]
            },
            {
                label: 'AI Assistant',
                submenu: [
                    {
                        label: 'Toggle AI Panel',
                        accelerator: 'CmdOrCtrl+Shift+A',
                        click: () => this.sendToRenderer('menu-toggle-ai')
                    },
                    {
                        label: 'Explain Code',
                        accelerator: 'CmdOrCtrl+Shift+E',
                        click: () => this.sendToRenderer('menu-explain-code')
                    },
                    {
                        label: 'Refactor Code',
                        accelerator: 'CmdOrCtrl+Shift+R',
                        click: () => this.sendToRenderer('menu-refactor-code')
                    },
                    { type: 'separator' },
                    {
                        label: 'AI Settings',
                        click: () => this.sendToRenderer('menu-ai-settings')
                    }
                ]
            },
            {
                label: 'View',
                submenu: [
                    { role: 'reload' },
                    { role: 'forceReload' },
                    { role: 'toggleDevTools' },
                    { type: 'separator' },
                    { role: 'resetZoom' },
                    { role: 'zoomIn' },
                    { role: 'zoomOut' },
                    { type: 'separator' },
                    { role: 'togglefullscreen' }
                ]
            },
            {
                label: 'Help',
                submenu: [
                    {
                        label: 'About Uranus-AI',
                        click: () => this.showAboutDialog()
                    },
                    {
                        label: 'Documentation',
                        click: () => shell.openExternal('https://github.com/alezzanderg/Uranus-AI')
                    },
                    {
                        label: 'Report Issue',
                        click: () => shell.openExternal('https://github.com/alezzanderg/Uranus-AI/issues')
                    }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    setupIPC() {
        ipcMain.handle('get-backend-status', async () => {
            return {
                isReady: this.isBackendReady,
                port: this.backendPort,
                url: `http://localhost:${this.backendPort}`
            };
        });

        ipcMain.handle('restart-backend', async () => {
            log.info('🔄 Restarting backend...');
            await this.stopBackend();
            await this.startBackend();
            await this.waitForBackend();
            return this.isBackendReady;
        });

        ipcMain.handle('open-backend-logs', () => {
            const logPath = log.transports.file.getFile().path;
            shell.showItemInFolder(logPath);
        });
    }

    sendToRenderer(channel, ...args) {
        if (this.mainWindow && !this.mainWindow.isDestroyed()) {
            this.mainWindow.webContents.send(channel, ...args);
        }
    }

    showAboutDialog() {
        dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'About Uranus-AI Editor',
            message: 'Uranus-AI Editor',
            detail: `Version: 1.2.0
AI-Enhanced Code Editor with native multi-model support

Built with:
- Code-OSS (VS Code Open Source)
- FastAPI Backend
- PostgreSQL Database
- Multi-Model AI Integration

© 2025 Uranus-AI Team`,
            buttons: ['OK']
        });
    }

    showErrorDialog(title, message) {
        dialog.showErrorBox(title, message);
    }

    async stopBackend() {
        if (this.backendProcess) {
            log.info('🛑 Stopping backend process...');
            this.backendProcess.kill();
            this.backendProcess = null;
            this.isBackendReady = false;
        }
    }

    onWindowAllClosed() {
        if (process.platform !== 'darwin') {
            app.quit();
        }
    }

    onActivate() {
        if (BrowserWindow.getAllWindows().length === 0) {
            this.createMainWindow();
        }
    }

    async onBeforeQuit() {
        log.info('🔴 Application quitting...');
        await this.stopBackend();
    }
}

// Create and initialize the application
const uranusApp = new UranusAIApp();
uranusApp.initialize();

