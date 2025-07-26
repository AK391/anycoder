# anycoder

An open source vibe coding app with AI-powered assistance, document processing, web search, and code generation capabilities.

## 🚀 Try Online

**[Try anycoder live on Hugging Face Spaces](https://huggingface.co/spaces/akhaliq/anycoder)**

No installation required! Access the full app directly in your browser.

## Features

- AI-powered code generation and assistance
- Document processing (PDF, DOCX)
- OCR (Optical Character Recognition) for images
- Web scraping and search capabilities
- Interactive Gradio web interface

## Prerequisites

### System Requirements

- Python 3.8 or higher
- Tesseract OCR engine

### Install System Dependencies

**On macOS:**
```bash
brew install tesseract
```

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**On Windows:**
- Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to your PATH environment variable

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd anycoder
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Set up your API keys as environment variables (add these to your `.env` file or export them):

```bash
# Required for AI functionality
export HF_TOKEN="your_huggingface_token"

# Required for web search
export TAVILY_API_KEY="your_tavily_api_key"
```

## Running the Application

Start the anycoder application:

```bash
python app.py
```

The application will launch a Gradio interface, typically accessible at:
- Local: http://127.0.0.1:7860
- Network: http://0.0.0.0:7860 (if sharing is enabled)

The terminal will display the exact URLs where the interface is available.

## Usage

Once the application is running:

1. Open your web browser to the provided URL
2. Use the interactive interface to:
   - Generate and edit code
   - Process documents (upload PDFs, DOCX files)
   - Perform OCR on images
   - Search the web for information
   - Get AI assistance with coding tasks

## Troubleshooting

- **Tesseract not found**: Ensure Tesseract is installed and added to your PATH
- **API errors**: Verify your API keys are correctly set as environment variables
- **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
- **Port conflicts**: If port 7860 is busy, Gradio will automatically try the next available port