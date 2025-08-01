# AnyCoder TypeScript

A minimal TypeScript version of AnyCoder - an AI-powered code generator with a modern web interface.

![AnyCoder TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?logo=typescript)
![License](https://img.shields.io/badge/license-MIT-green)

## 🚀 Features

- **AI Code Generation**: Generate code in multiple languages using various AI models
- **Modern UI**: Clean, responsive interface with dark/light themes
- **Multi-Language Support**: HTML, TypeScript, JavaScript, Python, CSS, JSON, Markdown
- **File Processing**: Upload reference files for context
- **Website Redesign**: Extract and redesign existing websites
- **Code Highlighting**: Syntax highlighting with multiple themes
- **History Management**: Save and revisit previous generations
- **Export Options**: Copy to clipboard or download generated code
- **Real-time Preview**: Live preview for HTML content

## 🛠️ Setup

### Prerequisites

- Node.js 16+ and npm
- Modern web browser
- API keys (optional, for advanced AI models)

### Installation

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd anycoder-typescript
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Build the TypeScript:**
   ```bash
   npm run build
   ```

4. **Start the development server:**
   ```bash
   npm start
   ```

   Or for development with auto-rebuild:
   ```bash
   npm run dev
   ```

5. **Open your browser:**
   Visit `http://localhost:8000` to use the application

## 📋 Usage

### Basic Code Generation

1. Enter a description of what you want to build in the prompt textarea
2. Select your target programming language
3. Choose an AI model (Hugging Face is free, others require API keys)
4. Click "Generate" to create your code

### Advanced Features

- **Reference Files**: Upload text files, code files, or documents for context
- **Website Redesign**: Enter a website URL to extract and redesign it
- **Web Search**: Enable web search for up-to-date information (requires implementation)
- **Themes**: Switch between different syntax highlighting themes
- **History**: View and reload previous generations

### API Configuration

For OpenAI or Anthropic models:

1. Get your API key from the respective provider
2. Click on "API Settings" in the sidebar
3. Enter your API key (stored locally only)
4. Select the desired model

## 🔧 Development

### Project Structure

```
anycoder-typescript/
├── src/
│   └── index.ts          # Main TypeScript application
├── dist/                 # Compiled JavaScript (generated)
├── index.html           # Main HTML interface
├── styles.css           # CSS styles and themes
├── package.json         # Node.js dependencies
├── tsconfig.json        # TypeScript configuration
└── README.md           # This file
```

### Building

```bash
# Compile TypeScript
npm run build

# Watch for changes (development)
npm run dev

# Start local server
npm run serve
```

### Customization

**Adding New Languages:**
1. Add the language to the dropdown in `index.html`
2. Add language-specific prompts in `src/index.ts`
3. Update file extensions in the download function

**Adding New AI Providers:**
1. Implement a new API call method in `src/index.ts`
2. Add the provider to the model dropdown
3. Handle authentication as needed

**Styling:**
- Modify `styles.css` for custom themes
- CSS variables at the top make color customization easy
- Responsive breakpoints are already configured

## 🔌 API Integration

### Hugging Face (Free)

The default model uses Hugging Face's free inference API. No setup required, but may have rate limits.

### OpenAI

```javascript
// Set your API key in the UI or modify the code:
const apiKey = 'your-openai-api-key';
```

### Anthropic Claude

```javascript
// Set your API key in the UI or modify the code:
const apiKey = 'your-anthropic-api-key';
```

### Custom APIs

To add your own AI API:

1. Create a new method like `callCustomAPI()` in `src/index.ts`
2. Add it to the model selection switch statement
3. Handle authentication and request formatting

## 🌐 Deployment

### Static Hosting

Since this is a client-side application, you can deploy it to any static hosting service:

**Netlify/Vercel:**
1. Build the project: `npm run build`
2. Deploy the entire folder

**GitHub Pages:**
1. Push to a GitHub repository
2. Enable GitHub Pages in settings
3. Set source to root folder

**Firebase Hosting:**
```bash
npm run build
firebase deploy
```

### Docker

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔒 Security Notes

- API keys are stored in browser localStorage only
- No server-side storage or logging
- CORS limitations apply to web scraping features
- Use HTTPS in production for API key security

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test
4. Commit: `git commit -am 'Add new feature'`
5. Push: `git push origin feature-name`
6. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆚 Differences from Python Version

This TypeScript version is a minimal implementation focusing on core functionality:

**Included:**
- ✅ AI code generation with multiple models
- ✅ Modern responsive UI
- ✅ File upload and processing
- ✅ Code highlighting and themes
- ✅ History management
- ✅ Download/copy functionality

**Simplified/Missing:**
- ❌ OCR image processing (would require additional libraries)
- ❌ PDF/DOCX parsing (simplified to text files)
- ❌ Web scraping (CORS limitations)
- ❌ Deployment to Hugging Face Spaces
- ❌ Advanced search integration

**Advantages:**
- ⚡ Faster startup and response
- 🌐 Runs entirely in browser
- 📱 Better mobile experience
- 🔧 Easier to customize and extend
- 🚀 Simple deployment options

## 🎯 Next Steps

To extend this application:

1. **Add backend services** for web scraping and file processing
2. **Implement real web search** using APIs like Tavily or Serper
3. **Add more AI providers** like Cohere, Together AI, etc.
4. **Enhance file processing** with libraries for PDF/DOCX
5. **Add collaborative features** with real-time sync
6. **Implement user accounts** and cloud storage

## 📞 Support

For issues and questions:
- Check the browser console for errors
- Ensure API keys are correctly set
- Verify network connectivity for API calls
- Test with different browsers if issues persist

---

Made with ❤️ using TypeScript, modern CSS, and AI APIs