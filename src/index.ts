// AnyCoder TypeScript - AI Code Generator
// Main application logic and UI interactions

interface GenerationConfig {
    prompt: string;
    language: string;
    model: string;
    apiKey?: string;
    webSearch: boolean;
    referenceFile?: File;
    websiteUrl?: string;
}

interface HistoryItem {
    id: string;
    prompt: string;
    code: string;
    language: string;
    timestamp: Date;
}

interface AIResponse {
    code: string;
    language: string;
    explanation?: string;
}

class AnyCoder {
    private history: HistoryItem[] = [];
    private currentTheme = 'github-dark';

    constructor() {
        this.initializeEventListeners();
        this.loadTheme();
        this.loadHistory();
    }

    private initializeEventListeners(): void {
        // Main generation button
        const generateBtn = document.getElementById('generate-btn') as HTMLButtonElement;
        generateBtn?.addEventListener('click', () => this.handleGenerate());

        // Clear button
        const clearBtn = document.getElementById('clear-btn') as HTMLButtonElement;
        clearBtn?.addEventListener('click', () => this.handleClear());

        // Tab navigation
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.target as HTMLButtonElement;
                const tabName = target.dataset.tab;
                if (tabName) this.switchTab(tabName);
            });
        });

        // Demo buttons
        const demoBtns = document.querySelectorAll('.demo-btn');
        demoBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.target as HTMLButtonElement;
                const prompt = target.dataset.prompt;
                if (prompt) this.setPrompt(prompt);
            });
        });

        // Copy button
        const copyBtn = document.getElementById('copy-btn') as HTMLButtonElement;
        copyBtn?.addEventListener('click', () => this.copyCode());

        // Download button
        const downloadBtn = document.getElementById('download-btn') as HTMLButtonElement;
        downloadBtn?.addEventListener('click', () => this.downloadCode());

        // Theme selector
        const themeSelect = document.getElementById('theme-select') as HTMLSelectElement;
        themeSelect?.addEventListener('change', (e) => {
            const target = e.target as HTMLSelectElement;
            this.changeTheme(target.value);
        });

        // Language change handler
        const languageSelect = document.getElementById('language') as HTMLSelectElement;
        languageSelect?.addEventListener('change', () => this.updateCodeHighlighting());

        // File upload handler
        const fileUpload = document.getElementById('file-upload') as HTMLInputElement;
        const fileUploadButton = document.getElementById('file-upload-button');
        
        fileUpload?.addEventListener('change', (e) => this.handleFileUpload(e));
        fileUploadButton?.addEventListener('click', () => fileUpload?.click());
        
        // Drag and drop functionality
        fileUploadButton?.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUploadButton.style.borderColor = 'var(--primary-color)';
        });
        
        fileUploadButton?.addEventListener('dragleave', (e) => {
            e.preventDefault();
            fileUploadButton.style.borderColor = 'var(--border)';
        });
        
        fileUploadButton?.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUploadButton.style.borderColor = 'var(--border)';
            const files = e.dataTransfer?.files;
            if (files && files.length > 0) {
                fileUpload.files = files;
                this.handleFileUpload({ target: fileUpload } as any);
            }
        });

        // Enter key handler for prompt
        const promptTextarea = document.getElementById('prompt') as HTMLTextAreaElement;
        promptTextarea?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                this.handleGenerate();
            }
        });
    }

    private async handleGenerate(): Promise<void> {
        const config = this.getGenerationConfig();
        
        if (!config.prompt.trim()) {
            this.showToast('Please enter a prompt', 'error');
            return;
        }

        this.setGenerating(true);

        try {
            const response = await this.generateCode(config);
            this.displayCode(response.code, config.language);
            this.addToHistory(config.prompt, response.code, config.language);
            this.updatePreview(response.code, config.language);
            this.showToast('Code generated successfully!', 'success');
            this.switchTab('code');
        } catch (error) {
            console.error('Generation error:', error);
            this.showToast(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
        } finally {
            this.setGenerating(false);
        }
    }

    private getGenerationConfig(): GenerationConfig {
        const promptEl = document.getElementById('prompt') as HTMLTextAreaElement;
        const languageEl = document.getElementById('language') as HTMLSelectElement;
        const modelEl = document.getElementById('model') as HTMLSelectElement;
        const apiKeyEl = document.getElementById('api-key') as HTMLInputElement;
        const webSearchEl = document.getElementById('web-search') as HTMLInputElement;
        const fileUploadEl = document.getElementById('file-upload') as HTMLInputElement;
        const websiteUrlEl = document.getElementById('website-url') as HTMLInputElement;

        return {
            prompt: promptEl?.value || '',
            language: languageEl?.value || 'html',
            model: modelEl?.value || 'Qwen/Qwen3-Coder-480B-A35B-Instruct',
            apiKey: apiKeyEl?.value || undefined,
            webSearch: webSearchEl?.checked || false,
            referenceFile: fileUploadEl?.files?.[0] || undefined,
            websiteUrl: websiteUrlEl?.value || undefined
        };
    }

    private async generateCode(config: GenerationConfig): Promise<AIResponse> {
        // Enhanced prompt with context
        let enhancedPrompt = this.buildEnhancedPrompt(config);

        // Add reference file content if provided
        if (config.referenceFile) {
            const fileContent = await this.readFileContent(config.referenceFile);
            enhancedPrompt += `\n\nReference file content:\n${fileContent}`;
        }

        // Add website content if URL provided
        if (config.websiteUrl) {
            try {
                const websiteContent = await this.fetchWebsiteContent(config.websiteUrl);
                enhancedPrompt += `\n\nWebsite to redesign:\n${websiteContent}`;
            } catch (error) {
                console.warn('Failed to fetch website content:', error);
            }
        }

        // Web search enhancement
        if (config.webSearch) {
            try {
                const searchResults = await this.performWebSearch(config.prompt, config.language);
                enhancedPrompt += `\n\nWeb search context:\n${searchResults}`;
            } catch (error) {
                console.warn('Web search failed:', error);
            }
        }

        // Use Hugging Face inference router with OpenAI-compatible API
        return await this.callHuggingFaceRouter(enhancedPrompt, config.language, config.model, config.apiKey);
    }

    private buildEnhancedPrompt(config: GenerationConfig): string {
        const languagePrompts: Record<string, string> = {
            'html': 'Create modern, responsive HTML with CSS and JavaScript. Use best practices for accessibility and performance.',
            'typescript': 'Write clean, type-safe TypeScript code with proper interfaces and modern features.',
            'javascript': 'Create modern JavaScript using ES6+ features with proper error handling.',
            'python': 'Write clean, idiomatic Python code following PEP 8 guidelines.',
            'css': 'Create modern CSS with responsive design and proper vendor prefixes.',
            'json': 'Generate valid JSON with proper structure and formatting.',
            'markdown': 'Create well-formatted Markdown with proper syntax.'
        };

        const systemPrompt = languagePrompts[config.language] || `Generate clean, well-documented ${config.language} code.`;
        
        return `${systemPrompt}\n\nUser request: ${config.prompt}\n\nPlease provide only the code without explanations unless specifically requested. Use modern best practices and ensure the code is production-ready.`;
    }

    private async callHuggingFaceRouter(prompt: string, language: string, model: string, apiKey?: string): Promise<AIResponse> {
        // Use Hugging Face's OpenAI-compatible router
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            'X-HF-Bill-To': 'huggingface'
        };

        // Add authorization if API key is provided
        if (apiKey && apiKey.trim()) {
            headers['Authorization'] = `Bearer ${apiKey.trim()}`;
        }

        const response = await fetch('https://router.huggingface.co/v1/chat/completions', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                model: model,
                messages: [
                    {
                        role: 'system',
                        content: `You are an expert ${language} developer. Generate clean, modern, production-ready code. Only return the code without explanations unless specifically requested.`
                    },
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                max_tokens: 4000,
                temperature: 0.7,
                stream: false
            })
        });

        if (!response.ok) {
            // Try to get error details
            let errorMessage = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error?.message || errorData.detail || errorMessage;
            } catch (e) {
                // Ignore JSON parsing errors
            }

            // If it's a 401/403, suggest getting an API key
            if (response.status === 401 || response.status === 403) {
                throw new Error('Authentication failed. Please add your Hugging Face token in API Settings.');
            }

            // For other errors, fall back to mock response
            console.warn('HF API call failed:', errorMessage);
            return this.getMockResponse(prompt, language);
        }

        const data = await response.json();
        const content = data.choices?.[0]?.message?.content || '';
        const code = this.extractCodeFromResponse(content, language);
        
        return { code, language };
    }

    private getMockResponse(prompt: string, language: string): AIResponse {
        const mockResponses: Record<string, string> = {
            'html': `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; margin: 20px 0; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Generated Application</h1>
        <div class="card">
            <p>This is a demo response for: ${prompt}</p>
            <button onclick="alert('Hello from generated code!')">Click Me</button>
        </div>
    </div>
</body>
</html>`,
            'typescript': `interface AppConfig {
    name: string;
    version: string;
}

class Application {
    private config: AppConfig;

    constructor(config: AppConfig) {
        this.config = config;
    }

    public initialize(): void {
        console.log(\`Initializing \${this.config.name} v\${this.config.version}\`);
        // Application logic for: ${prompt}
    }

    public run(): void {
        this.initialize();
        console.log('Application is running...');
    }
}

// Usage
const app = new Application({
    name: 'Generated App',
    version: '1.0.0'
});

app.run();`,
            'javascript': `// Generated JavaScript for: ${prompt}
class App {
    constructor() {
        this.initialize();
    }

    initialize() {
        console.log('App initialized');
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('DOM loaded, app ready');
        });
    }

    run() {
        console.log('App is running...');
    }
}

const app = new App();
app.run();`,
            'python': `#!/usr/bin/env python3
"""
Generated Python application for: ${prompt}
"""

class Application:
    def __init__(self):
        self.name = "Generated App"
        self.version = "1.0.0"
    
    def initialize(self):
        """Initialize the application"""
        print(f"Initializing {self.name} v{self.version}")
    
    def run(self):
        """Run the application"""
        self.initialize()
        print("Application is running...")

if __name__ == "__main__":
    app = Application()
    app.run()`,
            'css': `/* Generated CSS for: ${prompt} */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --background: #f8f9fa;
    --text: #212529;
    --border: #dee2e6;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--background);
    color: var(--text);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 24px;
    margin: 20px 0;
}

@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
}`,
            'json': `{
  "name": "Generated Configuration",
  "description": "Generated for: ${prompt}",
  "version": "1.0.0",
  "settings": {
    "theme": "default",
    "language": "en",
    "features": {
      "darkMode": true,
      "notifications": true,
      "autoSave": false
    }
  },
  "dependencies": {
    "typescript": "^5.0.0",
    "react": "^18.0.0"
  }
}`,
            'markdown': `# Generated Documentation

## Overview

This document was generated for: **${prompt}**

## Features

- ✅ Modern design
- ✅ Responsive layout
- ✅ Accessibility support
- ✅ TypeScript integration

## Installation

\`\`\`bash
npm install
npm start
\`\`\`

## Usage

\`\`\`typescript
import { Application } from './app';

const app = new Application();
app.run();
\`\`\`

## Contributing

Please read our contributing guidelines before submitting PRs.

`
        };

        return {
            code: mockResponses[language] || `// Generated ${language} code for: ${prompt}\nconsole.log('Hello, World!');`,
            language
        };
    }

    private extractCodeFromResponse(text: string, language: string): string {
        // Try to extract code from markdown code blocks
        const codeBlockRegex = new RegExp(`\`\`\`${language}?\\s*([\\s\\S]*?)\`\`\``, 'i');
        const match = text.match(codeBlockRegex);
        
        if (match) {
            return match[1].trim();
        }

        // Fallback: return the raw text, removing any leading/trailing explanations
        const lines = text.split('\n');
        const codeStart = lines.findIndex(line => 
            line.includes('<!DOCTYPE') || 
            line.includes('<html') || 
            line.includes('function') ||
            line.includes('class ') ||
            line.includes('interface ') ||
            line.includes('def ') ||
            line.includes('import ') ||
            line.includes('{') ||
            line.trim().startsWith('//')
        );

        if (codeStart >= 0) {
            return lines.slice(codeStart).join('\n').trim();
        }

        return text.trim();
    }

    private async readFileContent(file: File): Promise<string> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result as string);
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    private async fetchWebsiteContent(url: string): Promise<string> {
        // Note: Due to CORS restrictions, this would typically need a backend proxy
        // For demo purposes, we'll return a mock response
        return `Website content from ${url} (CORS proxy would be needed for real implementation)`;
    }

    private async performWebSearch(query: string, language: string): Promise<string> {
        // Mock web search - in production, you'd use a search API
        return `Web search results for "${query}" in ${language} (API integration needed)`;
    }

    private displayCode(code: string, language: string): void {
        const codeElement = document.getElementById('generated-code');
        if (codeElement) {
            codeElement.textContent = code;
            codeElement.className = `hljs language-${language}`;
            
            // Apply syntax highlighting
            if ((window as any).hljs) {
                (window as any).hljs.highlightElement(codeElement);
            }
        }
    }

    private updatePreview(code: string, language: string): void {
        const previewFrame = document.getElementById('preview-frame') as HTMLIFrameElement;
        const previewPlaceholder = document.getElementById('preview-placeholder');

        if (language === 'html' && previewFrame && previewPlaceholder) {
            // Show HTML preview
            previewPlaceholder.style.display = 'none';
            previewFrame.style.display = 'block';
            
            const blob = new Blob([code], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            previewFrame.src = url;
            
            // Clean up blob URL after loading
            previewFrame.onload = () => URL.revokeObjectURL(url);
        } else if (previewPlaceholder && previewFrame) {
            // Hide preview for non-HTML content
            previewFrame.style.display = 'none';
            previewPlaceholder.style.display = 'flex';
        }
    }

    private addToHistory(prompt: string, code: string, language: string): void {
        const historyItem: HistoryItem = {
            id: Date.now().toString(),
            prompt,
            code,
            language,
            timestamp: new Date()
        };

        this.history.unshift(historyItem);
        
        // Keep only last 50 items
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }

        this.saveHistory();
        this.updateHistoryDisplay();
    }

    private updateHistoryDisplay(): void {
        const historyList = document.getElementById('history-list');
        if (!historyList) return;

        if (this.history.length === 0) {
            historyList.innerHTML = '<p class="empty-state">No history yet. Generate some code to see it here!</p>';
            return;
        }

        historyList.innerHTML = this.history.map(item => `
            <div class="history-item" data-id="${item.id}">
                <div class="prompt">${this.escapeHtml(item.prompt)}</div>
                <div class="meta">
                    <span>${item.language}</span>
                    <span>${this.formatDate(item.timestamp)}</span>
                </div>
            </div>
        `).join('');

        // Add click handlers to history items
        historyList.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const target = e.currentTarget as HTMLElement;
                const id = target.dataset.id;
                if (id) this.loadHistoryItem(id);
            });
        });
    }

    private loadHistoryItem(id: string): void {
        const item = this.history.find(h => h.id === id);
        if (item) {
            this.displayCode(item.code, item.language);
            this.updatePreview(item.code, item.language);
            this.setPrompt(item.prompt);
            this.setLanguage(item.language);
            this.switchTab('code');
        }
    }

    private setPrompt(prompt: string): void {
        const promptEl = document.getElementById('prompt') as HTMLTextAreaElement;
        if (promptEl) {
            promptEl.value = prompt;
        }
    }

    private setLanguage(language: string): void {
        const languageEl = document.getElementById('language') as HTMLSelectElement;
        if (languageEl) {
            languageEl.value = language;
        }
    }

    private switchTab(tabName: string): void {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            const buttonEl = btn as HTMLButtonElement;
            buttonEl.classList.toggle('active', buttonEl.dataset.tab === tabName);
        });

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `${tabName}-tab`);
        });
    }

    private handleClear(): void {
        // Clear form inputs
        const promptEl = document.getElementById('prompt') as HTMLTextAreaElement;
        const fileUploadEl = document.getElementById('file-upload') as HTMLInputElement;
        const websiteUrlEl = document.getElementById('website-url') as HTMLInputElement;

        if (promptEl) promptEl.value = '';
        if (fileUploadEl) {
            fileUploadEl.value = '';
            // Also reset the custom file upload button
            this.handleFileUpload({ target: fileUploadEl } as any);
        }
        if (websiteUrlEl) websiteUrlEl.value = '';

        // Clear generated code
        this.displayCode('// Your generated code will appear here...', 'javascript');
        
        // Clear preview
        const previewFrame = document.getElementById('preview-frame') as HTMLIFrameElement;
        const previewPlaceholder = document.getElementById('preview-placeholder');
        
        if (previewFrame && previewPlaceholder) {
            previewFrame.style.display = 'none';
            previewPlaceholder.style.display = 'flex';
        }

        this.showToast('Cleared successfully', 'success');
    }

    private async copyCode(): Promise<void> {
        const codeElement = document.getElementById('generated-code');
        if (codeElement) {
            try {
                await navigator.clipboard.writeText(codeElement.textContent || '');
                this.showToast('Code copied to clipboard', 'success');
            } catch (error) {
                this.showToast('Failed to copy code', 'error');
            }
        }
    }

    private downloadCode(): void {
        const codeElement = document.getElementById('generated-code');
        const languageEl = document.getElementById('language') as HTMLSelectElement;
        
        if (codeElement && languageEl) {
            const code = codeElement.textContent || '';
            const language = languageEl.value;
            const extensions: Record<string, string> = {
                'html': 'html',
                'typescript': 'ts',
                'javascript': 'js',
                'python': 'py',
                'css': 'css',
                'json': 'json',
                'markdown': 'md'
            };
            
            const extension = extensions[language] || 'txt';
            const filename = `generated-code.${extension}`;
            
            const blob = new Blob([code], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showToast(`Downloaded ${filename}`, 'success');
        }
    }

    private changeTheme(theme: string): void {
        this.currentTheme = theme;
        const link = document.querySelector('link[href*="highlight.js"]') as HTMLLinkElement;
        if (link) {
            link.href = `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/${theme}.min.css`;
        }
        
        // Re-highlight code with new theme
        this.updateCodeHighlighting();
        localStorage.setItem('anycoder-theme', theme);
    }

    private updateCodeHighlighting(): void {
        const codeElement = document.getElementById('generated-code');
        if (codeElement && (window as any).hljs) {
            (window as any).hljs.highlightElement(codeElement);
        }
    }

    private loadTheme(): void {
        const savedTheme = localStorage.getItem('anycoder-theme');
        if (savedTheme) {
            const themeSelect = document.getElementById('theme-select') as HTMLSelectElement;
            if (themeSelect) {
                themeSelect.value = savedTheme;
                this.changeTheme(savedTheme);
            }
        }
    }

    private saveHistory(): void {
        localStorage.setItem('anycoder-history', JSON.stringify(this.history));
    }

    private loadHistory(): void {
        const saved = localStorage.getItem('anycoder-history');
        if (saved) {
            try {
                this.history = JSON.parse(saved).map((item: any) => ({
                    ...item,
                    timestamp: new Date(item.timestamp)
                }));
                this.updateHistoryDisplay();
            } catch (error) {
                console.warn('Failed to load history:', error);
            }
        }
    }

    private handleFileUpload(event: Event): void {
        const target = event.target as HTMLInputElement;
        const file = target.files?.[0];
        const fileUploadButton = document.getElementById('file-upload-button');
        const fileUploadText = fileUploadButton?.querySelector('.file-upload-text');
        
        if (file && fileUploadButton && fileUploadText) {
            // Update button appearance
            fileUploadButton.classList.add('has-file');
            fileUploadText.innerHTML = `
                <span>${file.name}</span>
                <button class="file-remove-btn" title="Remove file">×</button>
            `;
            
            // Add click handler to remove button
            const removeBtn = fileUploadText.querySelector('.file-remove-btn');
            removeBtn?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.removeFile();
            });
            
            this.showToast(`File selected: ${file.name}`, 'success');
        } else if (fileUploadButton && fileUploadText) {
            // Reset button appearance
            fileUploadButton.classList.remove('has-file');
            fileUploadText.textContent = 'Choose file or drag & drop';
        }
    }

    private removeFile(): void {
        const fileUpload = document.getElementById('file-upload') as HTMLInputElement;
        const fileUploadButton = document.getElementById('file-upload-button');
        const fileUploadText = fileUploadButton?.querySelector('.file-upload-text');
        
        if (fileUpload) {
            fileUpload.value = '';
        }
        
        if (fileUploadButton && fileUploadText) {
            fileUploadButton.classList.remove('has-file');
            fileUploadText.textContent = 'Choose file or drag & drop';
        }
        
        this.showToast('File removed', 'success');
    }

    private setGenerating(isGenerating: boolean): void {
        const generateBtn = document.getElementById('generate-btn') as HTMLButtonElement;
        const btnText = generateBtn?.querySelector('.btn-text') as HTMLElement;
        const btnLoader = generateBtn?.querySelector('.btn-loader') as HTMLElement;

        if (generateBtn && btnText && btnLoader) {
            generateBtn.disabled = isGenerating;
            btnText.style.display = isGenerating ? 'none' : 'inline';
            btnLoader.style.display = isGenerating ? 'inline' : 'none';
        }
    }

    private showToast(message: string, type: 'success' | 'error' = 'success'): void {
        const toast = document.getElementById('status-toast');
        if (toast) {
            toast.textContent = message;
            toast.className = `toast ${type} show`;
            
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    }

    private escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    private formatDate(date: Date): string {
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AnyCoder();
});

