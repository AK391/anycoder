# anycoder

An open source AI-powered coding app with code generation, document processing, web search, and OCR capabilities. Available in both Python (full-featured) and TypeScript (lightweight) versions.

## 🚀 Try Online

**[Try anycoder live on Hugging Face Spaces](https://huggingface.co/spaces/akhaliq/anycoder)**

No installation required! Access the full Python app directly in your browser.

## Features

- **AI-powered code generation** with multiple models (OpenAI, Anthropic, Hugging Face)
- **Document processing** (PDF, DOCX) and OCR for images
- **Web scraping and search** capabilities
- **Modern responsive UI** with dark/light themes
- **Interactive Gradio interface** (Python) or browser-based UI (TypeScript)

---

## 🐍 Python Version (Full-Featured)

The complete implementation with advanced document processing and OCR capabilities.

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR engine

#### Install System Dependencies

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install tesseract-ocr
```

**Windows:**
- Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH environment variable

### Installation

```bash
# Clone repository
git clone <repository-url>
cd anycoder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Set up your API keys as environment variables:

```bash
export HF_TOKEN="your_huggingface_token"
export TAVILY_API_KEY="your_tavily_api_key"
```

### Running

```bash
python app.py
```

Access at: http://127.0.0.1:7860

---

## 🟦 TypeScript Version (Lightweight)

A browser-based implementation focusing on core AI code generation with modern UI.

### Prerequisites

- Node.js 16+ and npm
- Modern web browser

### Installation

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Start development server
npm start
```

Access at: http://localhost:8000

### Development

```bash
# Watch for changes
npm run dev

# Build for production
npm run build
```

## API Configuration

Both versions support multiple AI providers:

- **Hugging Face**: Free tier available (default)
- **OpenAI**: Requires API key
- **Anthropic**: Requires API key

Set API keys in the UI settings or as environment variables.

## 🔄 Version Comparison

| Feature | Python | TypeScript |
|---------|--------|------------|
| AI Code Generation | ✅ | ✅ |
| Modern UI | ✅ | ✅ |
| File Upload | ✅ | ✅ |
| OCR Processing | ✅ | ❌ |
| PDF/DOCX Support | ✅ | ❌ |
| Web Scraping | ✅ | ❌* |
| Deployment Options | Gradio/HF Spaces | Static hosting |
| Startup Time | Slower | ⚡ Faster |
| Mobile Experience | Good | 📱 Better |

*Limited by CORS in browser

## 🚀 Deployment

### Python Version
- **Hugging Face Spaces**: Ready for deployment
- **Local/Server**: Run `python app.py`

### TypeScript Version
- **Static hosting**: Netlify, Vercel, GitHub Pages
- **Docker**: Included Dockerfile
- **CDN**: Any static file service

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test both versions if applicable
4. Submit pull request


## 🔧 Troubleshooting

**Python Version:**
- Ensure Tesseract is in PATH
- Verify API keys are set correctly
- Check `pip install -r requirements.txt` completed

**TypeScript Version:**
- Check browser console for errors
- Verify API keys in settings
- Test with different browsers

---

Made with ❤️ using Python, TypeScript, and AI APIs