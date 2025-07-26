import os
import re
from http import HTTPStatus
from typing import Dict, List, Optional, Tuple
import base64
import mimetypes
import PyPDF2
import docx
import cv2
import numpy as np
from PIL import Image
import pytesseract
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import html2text
import json
import time
import webbrowser
import urllib.parse

import gradio as gr
from huggingface_hub import InferenceClient
from tavily import TavilyClient
from huggingface_hub import HfApi
import tempfile

# Gradio supported languages for syntax highlighting
GRADIO_SUPPORTED_LANGUAGES = [
    "python", "c", "cpp", "markdown", "latex", "json", "html", "css", "javascript", "jinja2", "typescript", "yaml", "dockerfile", "shell", "r", "sql", "sql-msSQL", "sql-mySQL", "sql-mariaDB", "sql-sqlite", "sql-cassandra", "sql-plSQL", "sql-hive", "sql-pgSQL", "sql-gql", "sql-gpSQL", "sql-sparkSQL", "sql-esper", None
]

def get_gradio_language(language):
    return language if language in GRADIO_SUPPORTED_LANGUAGES else None

# Search/Replace Constants
SEARCH_START = "<<<<<<< SEARCH"
DIVIDER = "======="
REPLACE_END = ">>>>>>> REPLACE"

# Configuration
HTML_SYSTEM_PROMPT = """ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. MAKE IT RESPONSIVE USING MODERN CSS. Use as much as you can modern CSS for the styling, if you can't do something with modern CSS, then use custom CSS. Also, try to elaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE

For website redesign tasks:
- Use the provided original HTML code as the starting point for redesign
- Preserve all original content, structure, and functionality
- Keep the same semantic HTML structure but enhance the styling
- Reuse all original images and their URLs from the HTML code
- Create a modern, responsive design with improved typography and spacing
- Use modern CSS frameworks and design patterns
- Ensure accessibility and mobile responsiveness
- Maintain the same navigation and user flow
- Enhance the visual design while keeping the original layout structure

If an image is provided, analyze it and use the visual information to better understand the user's requirements.

Always respond with code that can be executed or rendered directly.

Always output only the HTML code inside a ```html ... ``` code block, and do not include any explanations or extra text. Do NOT add the language name at the top of the code output."""

TRANSFORMERS_JS_SYSTEM_PROMPT = """You are an expert web developer creating a transformers.js application. You will generate THREE separate files: index.html, index.js, and style.css.

IMPORTANT: You MUST output ALL THREE files in the following format:

```html
<!-- index.html content here -->
```

```javascript
// index.js content here
```

```css
/* style.css content here */
```

Requirements:
1. Create a modern, responsive web application using transformers.js
2. Use the transformers.js library for AI/ML functionality
3. Create a clean, professional UI with good user experience
4. Make the application fully responsive for mobile devices
5. Use modern CSS practices and JavaScript ES6+ features
6. Include proper error handling and loading states
7. Follow accessibility best practices

The index.html should contain the basic HTML structure and link to the CSS and JS files.
The index.js should contain all the JavaScript logic including transformers.js integration.
The style.css should contain all the styling for the application.

Always output only the three code blocks as shown above, and do not include any explanations or extra text."""

SVELTE_SYSTEM_PROMPT = """You are an expert Svelte developer creating a modern Svelte application. You will generate ONLY the custom files that need user-specific content for the user's requested application.

IMPORTANT: You MUST output files in the following format. Generate ONLY the files needed for the user's specific request:

```svelte
<!-- src/App.svelte content here -->
```

```css
/* src/app.css content here */
```

If you need additional components for the user's specific app, add them like:
```svelte
<!-- src/lib/ComponentName.svelte content here -->
```

Requirements:
1. Create a modern, responsive Svelte application based on the user's specific request
2. Use TypeScript for better type safety
3. Create a clean, professional UI with good user experience
4. Make the application fully responsive for mobile devices
5. Use modern CSS practices and Svelte best practices
6. Include proper error handling and loading states
7. Follow accessibility best practices
8. Use Svelte's reactive features effectively
9. Include proper component structure and organization
10. Generate ONLY components that are actually needed for the user's requested application

Files you should generate:
- src/App.svelte: Main application component (ALWAYS required)
- src/app.css: Global styles (ALWAYS required)
- src/lib/[ComponentName].svelte: Additional components (ONLY if needed for the user's specific app)

The other files (index.html, package.json, vite.config.ts, tsconfig files, svelte.config.js, src/main.ts, src/vite-env.d.ts) are provided by the Svelte template and don't need to be generated.

Always output only the two code blocks as shown above, and do not include any explanations or extra text."""

SVELTE_SYSTEM_PROMPT_WITH_SEARCH = """You are an expert Svelte developer creating a modern Svelte application. You have access to real-time web search. When needed, use web search to find the latest information, best practices, or specific Svelte technologies.

You will generate ONLY the custom files that need user-specific content.

IMPORTANT: You MUST output ONLY the custom files in the following format:

```svelte
<!-- src/App.svelte content here -->
```

```css
/* src/app.css content here -->
```

Requirements:
1. Create a modern, responsive Svelte application
2. Use TypeScript for better type safety
3. Create a clean, professional UI with good user experience
4. Make the application fully responsive for mobile devices
5. Use modern CSS practices and Svelte best practices
6. Include proper error handling and loading states
7. Follow accessibility best practices
8. Use Svelte's reactive features effectively
9. Include proper component structure and organization
10. Use web search to find the latest Svelte patterns, libraries, and best practices

The files you generate are:
- src/App.svelte: Main application component (your custom app logic)
- src/app.css: Global styles (your custom styling)

The other files (index.html, package.json, vite.config.ts, tsconfig files, svelte.config.js, src/main.ts, src/vite-env.d.ts) are provided by the Svelte template and don't need to be generated.

Always output only the two code blocks as shown above, and do not include any explanations or extra text."""

TRANSFORMERS_JS_SYSTEM_PROMPT_WITH_SEARCH = """You are an expert web developer creating a transformers.js application. You have access to real-time web search. When needed, use web search to find the latest information, best practices, or specific technologies for transformers.js.

You will generate THREE separate files: index.html, index.js, and style.css.

IMPORTANT: You MUST output ALL THREE files in the following format:

```html
<!-- index.html content here -->
```

```javascript
// index.js content here
```

```css
/* style.css content here */
```

Requirements:
1. Create a modern, responsive web application using transformers.js
2. Use the transformers.js library for AI/ML functionality
3. Use web search to find current best practices and latest transformers.js features
4. Create a clean, professional UI with good user experience
5. Make the application fully responsive for mobile devices
6. Use modern CSS practices and JavaScript ES6+ features
7. Include proper error handling and loading states
8. Follow accessibility best practices

The index.html should contain the basic HTML structure and link to the CSS and JS files.
The index.js should contain all the JavaScript logic including transformers.js integration.
The style.css should contain all the styling for the application.

Always output only the three code blocks as shown above, and do not include any explanations or extra text."""

GENERIC_SYSTEM_PROMPT = """You are an expert {language} developer. Write clean, idiomatic, and runnable {language} code for the user's request. If possible, include comments and best practices. Output ONLY the code inside a ``` code block, and do not include any explanations or extra text. If the user provides a file or other context, use it as a reference. If the code is for a script or app, make it as self-contained as possible. Do NOT add the language name at the top of the code output."""

# System prompt with search capability
HTML_SYSTEM_PROMPT_WITH_SEARCH = """ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. MAKE IT RESPONSIVE USING MODERN CSS. Use as much as you can modern CSS for the styling, if you can't do something with modern CSS, then use custom CSS. Also, try to elaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE

You have access to real-time web search. When needed, use web search to find the latest information, best practices, or specific technologies.

For website redesign tasks:
- Use the provided original HTML code as the starting point for redesign
- Preserve all original content, structure, and functionality
- Keep the same semantic HTML structure but enhance the styling
- Reuse all original images and their URLs from the HTML code
- Use web search to find current design trends and best practices for the specific type of website
- Create a modern, responsive design with improved typography and spacing
- Use modern CSS frameworks and design patterns
- Ensure accessibility and mobile responsiveness
- Maintain the same navigation and user flow
- Enhance the visual design while keeping the original layout structure

If an image is provided, analyze it and use the visual information to better understand the user's requirements.

Always respond with code that can be executed or rendered directly.

Always output only the HTML code inside a ```html ... ``` code block, and do not include any explanations or extra text. Do NOT add the language name at the top of the code output."""

GENERIC_SYSTEM_PROMPT_WITH_SEARCH = """You are an expert {language} developer. You have access to real-time web search. When needed, use web search to find the latest information, best practices, or specific technologies for {language}.

Write clean, idiomatic, and runnable {language} code for the user's request. If possible, include comments and best practices. Output ONLY the code inside a ``` code block, and do not include any explanations or extra text. If the user provides a file or other context, use it as a reference. If the code is for a script or app, make it as self-contained as possible. Do NOT add the language name at the top of the code output."""

# Follow-up system prompt for modifying existing HTML files
FollowUpSystemPrompt = f"""You are an expert web developer modifying an existing HTML file.
The user wants to apply changes based on their request.
You MUST output ONLY the changes required using the following SEARCH/REPLACE block format. Do NOT output the entire file.
Explain the changes briefly *before* the blocks if necessary, but the code changes THEMSELVES MUST be within the blocks.
Format Rules:
1. Start with {SEARCH_START}
2. Provide the exact lines from the current code that need to be replaced.
3. Use {DIVIDER} to separate the search block from the replacement.
4. Provide the new lines that should replace the original lines.
5. End with {REPLACE_END}
6. You can use multiple SEARCH/REPLACE blocks if changes are needed in different parts of the file.
7. To insert code, use an empty SEARCH block (only {SEARCH_START} and {DIVIDER} on their lines) if inserting at the very beginning, otherwise provide the line *before* the insertion point in the SEARCH block and include that line plus the new lines in the REPLACE block.
8. To delete code, provide the lines to delete in the SEARCH block and leave the REPLACE block empty (only {DIVIDER} and {REPLACE_END} on their lines).
9. IMPORTANT: The SEARCH block must *exactly* match the current code, including indentation and whitespace.
Example Modifying Code:
```
Some explanation...
{SEARCH_START}
    <h1>Old Title</h1>
{DIVIDER}
    <h1>New Title</h1>
{REPLACE_END}
{SEARCH_START}
  </body>
{DIVIDER}
    <script>console.log("Added script");</script>
  </body>
{REPLACE_END}
```
Example Deleting Code:
```
Removing the paragraph...
{SEARCH_START}
  <p>This paragraph will be deleted.</p>
{DIVIDER}
{REPLACE_END}
```"""

# Follow-up system prompt for modifying existing transformers.js applications
TransformersJSFollowUpSystemPrompt = f"""You are an expert web developer modifying an existing transformers.js application.
The user wants to apply changes based on their request.
You MUST output ONLY the changes required using the following SEARCH/REPLACE block format. Do NOT output the entire file.
Explain the changes briefly *before* the blocks if necessary, but the code changes THEMSELVES MUST be within the blocks.

The transformers.js application consists of three files: index.html, index.js, and style.css.
When making changes, specify which file you're modifying by starting your search/replace blocks with the file name.

Format Rules:
1. Start with {SEARCH_START}
2. Provide the exact lines from the current code that need to be replaced.
3. Use {DIVIDER} to separate the search block from the replacement.
4. Provide the new lines that should replace the original lines.
5. End with {REPLACE_END}
6. You can use multiple SEARCH/REPLACE blocks if changes are needed in different parts of the file.
7. To insert code, use an empty SEARCH block (only {SEARCH_START} and {DIVIDER} on their lines) if inserting at the very beginning, otherwise provide the line *before* the insertion point in the SEARCH block and include that line plus the new lines in the REPLACE block.
8. To delete code, provide the lines to delete in the SEARCH block and leave the REPLACE block empty (only {DIVIDER} and {REPLACE_END} on their lines).
9. IMPORTANT: The SEARCH block must *exactly* match the current code, including indentation and whitespace.

Example Modifying HTML:
```
Changing the title in index.html...
{SEARCH_START}
    <title>Old Title</title>
{DIVIDER}
    <title>New Title</title>
{REPLACE_END}
```

Example Modifying JavaScript:
```
Adding a new function to index.js...
{SEARCH_START}
// Existing code
{DIVIDER}
// Existing code

function newFunction() {{
    console.log("New function added");
}}
{REPLACE_END}
```

Example Modifying CSS:
```
Changing background color in style.css...
{SEARCH_START}
body {{
    background-color: white;
}}
{DIVIDER}
body {{
    background-color: #f0f0f0;
}}
{REPLACE_END}
```"""

# Available models
AVAILABLE_MODELS = [
    {
        "name": "Moonshot Kimi-K2",
        "id": "moonshotai/Kimi-K2-Instruct",
        "description": "Moonshot AI Kimi-K2-Instruct model for code generation and general tasks"
    },
    {
        "name": "DeepSeek V3",
        "id": "deepseek-ai/DeepSeek-V3-0324",
        "description": "DeepSeek V3 model for code generation"
    },
    {
        "name": "DeepSeek R1", 
        "id": "deepseek-ai/DeepSeek-R1-0528",
        "description": "DeepSeek R1 model for code generation"
    },
    {
        "name": "ERNIE-4.5-VL",
        "id": "baidu/ERNIE-4.5-VL-424B-A47B-Base-PT",
        "description": "ERNIE-4.5-VL model for multimodal code generation with image support"
    },
    {
        "name": "MiniMax M1",
        "id": "MiniMaxAI/MiniMax-M1-80k",
        "description": "MiniMax M1 model for code generation and general tasks"
    },
    {
        "name": "Qwen3-235B-A22B",
        "id": "Qwen/Qwen3-235B-A22B",
        "description": "Qwen3-235B-A22B model for code generation and general tasks"
    },
    {
        "name": "SmolLM3-3B",
        "id": "HuggingFaceTB/SmolLM3-3B",
        "description": "SmolLM3-3B model for code generation and general tasks"
    },
    {
        "name": "GLM-4.1V-9B-Thinking",
        "id": "THUDM/GLM-4.1V-9B-Thinking",
        "description": "GLM-4.1V-9B-Thinking model for multimodal code generation with image support"
    },
    {
        "name": "Qwen3-235B-A22B-Instruct-2507",
        "id": "Qwen/Qwen3-235B-A22B-Instruct-2507",
        "description": "Qwen3-235B-A22B-Instruct-2507 model for code generation and general tasks"
    },
    {
        "name": "Qwen3-Coder-480B-A35B",
        "id": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
        "description": "Qwen3-Coder-480B-A35B-Instruct model for advanced code generation and programming tasks"
    },
    {
        "name": "Qwen3-32B",
        "id": "Qwen/Qwen3-32B",
        "description": "Qwen3-32B model for code generation and general tasks"
    },
    {
        "name": "Qwen3-235B-A22B-Thinking",
        "id": "Qwen/Qwen3-235B-A22B-Thinking-2507",
        "description": "Qwen3-235B-A22B-Thinking model with advanced reasoning capabilities"
    }
]

DEMO_LIST = [
    {
        "title": "Todo App",
        "description": "Create a simple todo application with add, delete, and mark as complete functionality"
    },
    {
        "title": "Calculator",
        "description": "Build a basic calculator with addition, subtraction, multiplication, and division"
    },
    {
        "title": "Chat Interface",
        "description": "Build a chat interface with message history and user input"
    },
    {
        "title": "E-commerce Product Card",
        "description": "Create a product card component for an e-commerce website"
    },
    {
        "title": "Login Form",
        "description": "Build a responsive login form with validation"
    },
    {
        "title": "Dashboard Layout",
        "description": "Create a dashboard layout with sidebar navigation and main content area"
    },
    {
        "title": "Data Table",
        "description": "Build a data table with sorting and filtering capabilities"
    },
    {
        "title": "Image Gallery",
        "description": "Create an image gallery with lightbox functionality and responsive grid layout"
    },
    {
        "title": "UI from Image",
        "description": "Upload an image of a UI design and I'll generate the HTML/CSS code for it"
    },
    {
        "title": "Extract Text from Image",
        "description": "Upload an image containing text and I'll extract and process the text content"
    },
    {
        "title": "Website Redesign",
        "description": "Enter a website URL to extract its content and redesign it with a modern, responsive layout"
    },
    {
        "title": "Modify HTML",
        "description": "After generating HTML, ask me to modify it with specific changes using search/replace format"
    },
    {
        "title": "Search/Replace Example",
        "description": "Generate HTML first, then ask: 'Change the title to My New Title' or 'Add a blue background to the body'"
    },
    {
        "title": "Transformers.js App",
        "description": "Create a transformers.js application with AI/ML functionality using the transformers.js library"
    },
    {
        "title": "Svelte App",
        "description": "Create a modern Svelte application with TypeScript, Vite, and responsive design"
    }
]

# HF Inference Client
HF_TOKEN = os.getenv('HF_TOKEN')
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN environment variable is not set. Please set it to your Hugging Face API token.")

def get_inference_client(model_id, provider="auto"):
    """Return an InferenceClient with provider based on model_id and user selection."""
    if model_id == "moonshotai/Kimi-K2-Instruct":
        provider = "groq"
    elif model_id == "Qwen/Qwen3-235B-A22B":
        provider = "cerebras"
    elif model_id == "Qwen/Qwen3-32B":
        provider = "cerebras"
    elif model_id == "Qwen/Qwen3-235B-A22B-Thinking-2507":
        provider = "auto"  # Let HuggingFace handle provider selection
    return InferenceClient(
        provider=provider,
        api_key=HF_TOKEN,
        bill_to="huggingface"
    )

# Type definitions
History = List[Tuple[str, str]]
Messages = List[Dict[str, str]]

# Tavily Search Client
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
tavily_client = None
if TAVILY_API_KEY:
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Tavily client: {e}")
        tavily_client = None

def history_to_messages(history: History, system: str) -> Messages:
    messages = [{'role': 'system', 'content': system}]
    for h in history:
        # Handle multimodal content in history
        user_content = h[0]
        if isinstance(user_content, list):
            # Extract text from multimodal content
            text_content = ""
            for item in user_content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content += item.get("text", "")
            user_content = text_content if text_content else str(user_content)
        
        messages.append({'role': 'user', 'content': user_content})
        messages.append({'role': 'assistant', 'content': h[1]})
    return messages

def messages_to_history(messages: Messages) -> Tuple[str, History]:
    assert messages[0]['role'] == 'system'
    history = []
    for q, r in zip(messages[1::2], messages[2::2]):
        # Extract text content from multimodal messages for history
        user_content = q['content']
        if isinstance(user_content, list):
            text_content = ""
            for item in user_content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content += item.get("text", "")
            user_content = text_content if text_content else str(user_content)
        
        history.append([user_content, r['content']])
    return history

def history_to_chatbot_messages(history: History) -> List[Dict[str, str]]:
    """Convert history tuples to chatbot message format"""
    messages = []
    for user_msg, assistant_msg in history:
        # Handle multimodal content
        if isinstance(user_msg, list):
            text_content = ""
            for item in user_msg:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content += item.get("text", "")
            user_msg = text_content if text_content else str(user_msg)
        
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    return messages

def remove_code_block(text):
    # Try to match code blocks with language markers
    patterns = [
        r'```(?:html|HTML)\n([\s\S]+?)\n```',  # Match ```html or ```HTML
        r'```\n([\s\S]+?)\n```',               # Match code blocks without language markers
        r'```([\s\S]+?)```'                      # Match code blocks without line breaks
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            # Remove a leading language marker line (e.g., 'python') if present
            if extracted.split('\n', 1)[0].strip().lower() in ['python', 'html', 'css', 'javascript', 'json', 'c', 'cpp', 'markdown', 'latex', 'jinja2', 'typescript', 'yaml', 'dockerfile', 'shell', 'r', 'sql', 'sql-mssql', 'sql-mysql', 'sql-mariadb', 'sql-sqlite', 'sql-cassandra', 'sql-plSQL', 'sql-hive', 'sql-pgsql', 'sql-gql', 'sql-gpsql', 'sql-sparksql', 'sql-esper']:
                return extracted.split('\n', 1)[1] if '\n' in extracted else ''
            return extracted
    # If no code block is found, check if the entire text is HTML
    if text.strip().startswith('<!DOCTYPE html>') or text.strip().startswith('<html') or text.strip().startswith('<'):
        return text.strip()
    # Special handling for python: remove python marker
    if text.strip().startswith('```python'):
        return text.strip()[9:-3].strip()
    # Remove a leading language marker line if present (fallback)
    lines = text.strip().split('\n', 1)
    if lines[0].strip().lower() in ['python', 'html', 'css', 'javascript', 'json', 'c', 'cpp', 'markdown', 'latex', 'jinja2', 'typescript', 'yaml', 'dockerfile', 'shell', 'r', 'sql', 'sql-mssql', 'sql-mysql', 'sql-mariadb', 'sql-sqlite', 'sql-cassandra', 'sql-plSQL', 'sql-hive', 'sql-pgsql', 'sql-gql', 'sql-gpsql', 'sql-sparksql', 'sql-esper']:
        return lines[1] if len(lines) > 1 else ''
    return text.strip()

def parse_transformers_js_output(text):
    """Parse transformers.js output and extract the three files (index.html, index.js, style.css)"""
    files = {
        'index.html': '',
        'index.js': '',
        'style.css': ''
    }
    
    # Patterns to match the three code blocks
    html_pattern = r'```html\s*\n([\s\S]+?)\n```'
    js_pattern = r'```javascript\s*\n([\s\S]+?)\n```'
    css_pattern = r'```css\s*\n([\s\S]+?)\n```'
    
    # Extract HTML content
    html_match = re.search(html_pattern, text, re.IGNORECASE)
    if html_match:
        files['index.html'] = html_match.group(1).strip()
    
    # Extract JavaScript content
    js_match = re.search(js_pattern, text, re.IGNORECASE)
    if js_match:
        files['index.js'] = js_match.group(1).strip()
    
    # Extract CSS content
    css_match = re.search(css_pattern, text, re.IGNORECASE)
    if css_match:
        files['style.css'] = css_match.group(1).strip()
    
    # Fallback: support === index.html === format if any file is missing
    if not (files['index.html'] and files['index.js'] and files['style.css']):
        # Use regex to extract sections
        html_fallback = re.search(r'===\s*index\.html\s*===\n([\s\S]+?)(?=\n===|$)', text, re.IGNORECASE)
        js_fallback = re.search(r'===\s*index\.js\s*===\n([\s\S]+?)(?=\n===|$)', text, re.IGNORECASE)
        css_fallback = re.search(r'===\s*style\.css\s*===\n([\s\S]+?)(?=\n===|$)', text, re.IGNORECASE)
        if html_fallback:
            files['index.html'] = html_fallback.group(1).strip()
        if js_fallback:
            files['index.js'] = js_fallback.group(1).strip()
        if css_fallback:
            files['style.css'] = css_fallback.group(1).strip()
    
    return files

def format_transformers_js_output(files):
    """Format the three files into a single display string"""
    output = []
    output.append("=== index.html ===")
    output.append(files['index.html'])
    output.append("\n=== index.js ===")
    output.append(files['index.js'])
    output.append("\n=== style.css ===")
    output.append(files['style.css'])
    return '\n'.join(output)

def parse_svelte_output(text):
    """Parse Svelte output to extract individual files"""
    files = {
        'src/App.svelte': '',
        'src/app.css': ''
    }
    
    import re
    
    # First try to extract using code block patterns
    svelte_pattern = r'```svelte\s*\n([\s\S]+?)\n```'
    css_pattern = r'```css\s*\n([\s\S]+?)\n```'
    
    # Extract svelte block for App.svelte
    svelte_match = re.search(svelte_pattern, text, re.IGNORECASE)
    css_match = re.search(css_pattern, text, re.IGNORECASE)
    
    if svelte_match:
        files['src/App.svelte'] = svelte_match.group(1).strip()
    if css_match:
        files['src/app.css'] = css_match.group(1).strip()
    
    # Fallback: support === filename === format if any file is missing
    if not (files['src/App.svelte'] and files['src/app.css']):
        # Use regex to extract sections
        app_svelte_fallback = re.search(r'===\s*src/App\.svelte\s*===\n([\s\S]+?)(?=\n===|$)', text, re.IGNORECASE)
        app_css_fallback = re.search(r'===\s*src/app\.css\s*===\n([\s\S]+?)(?=\n===|$)', text, re.IGNORECASE)
        
        if app_svelte_fallback:
            files['src/App.svelte'] = app_svelte_fallback.group(1).strip()
        if app_css_fallback:
            files['src/app.css'] = app_css_fallback.group(1).strip()
    
    return files

def format_svelte_output(files):
    """Format Svelte files into a single display string"""
    output = []
    output.append("=== src/App.svelte ===")
    output.append(files['src/App.svelte'])
    output.append("\n=== src/app.css ===")
    output.append(files['src/app.css'])
    return '\n'.join(output)

def history_render(history: History):
    return gr.update(visible=True), history

def clear_history():
    return [], [], None, ""  # Empty lists for both tuple format and chatbot messages, None for file, empty string for website URL

def update_image_input_visibility(model):
    """Update image input visibility based on selected model"""
    is_ernie_vl = model.get("id") == "baidu/ERNIE-4.5-VL-424B-A47B-Base-PT"
    is_glm_vl = model.get("id") == "THUDM/GLM-4.1V-9B-Thinking"
    return gr.update(visible=is_ernie_vl or is_glm_vl)

def process_image_for_model(image):
    """Convert image to base64 for model input"""
    if image is None:
        return None
    
    # Convert numpy array to PIL Image if needed
    import io
    import base64
    import numpy as np
    from PIL import Image
    
    # Handle numpy array from Gradio
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def create_multimodal_message(text, image=None):
    """Create a multimodal message with text and optional image"""
    if image is None:
        return {"role": "user", "content": text}
    
    content = [
        {
            "type": "text",
            "text": text
        },
        {
            "type": "image_url",
            "image_url": {
                "url": process_image_for_model(image)
            }
        }
    ]
    
    return {"role": "user", "content": content}

def apply_search_replace_changes(original_content: str, changes_text: str) -> str:
    """Apply search/replace changes to content (HTML, Python, etc.)"""
    if not changes_text.strip():
        return original_content
    
    # Split the changes text into individual search/replace blocks
    blocks = []
    current_block = ""
    lines = changes_text.split('\n')
    
    for line in lines:
        if line.strip() == SEARCH_START:
            if current_block.strip():
                blocks.append(current_block.strip())
            current_block = line + '\n'
        elif line.strip() == REPLACE_END:
            current_block += line + '\n'
            blocks.append(current_block.strip())
            current_block = ""
        else:
            current_block += line + '\n'
    
    if current_block.strip():
        blocks.append(current_block.strip())
    
    modified_content = original_content
    
    for block in blocks:
        if not block.strip():
            continue
            
        # Parse the search/replace block
        lines = block.split('\n')
        search_lines = []
        replace_lines = []
        in_search = False
        in_replace = False
        
        for line in lines:
            if line.strip() == SEARCH_START:
                in_search = True
                in_replace = False
            elif line.strip() == DIVIDER:
                in_search = False
                in_replace = True
            elif line.strip() == REPLACE_END:
                in_replace = False
            elif in_search:
                search_lines.append(line)
            elif in_replace:
                replace_lines.append(line)
        
        # Apply the search/replace
        if search_lines:
            search_text = '\n'.join(search_lines).strip()
            replace_text = '\n'.join(replace_lines).strip()
            
            if search_text in modified_content:
                modified_content = modified_content.replace(search_text, replace_text)
            else:
                print(f"Warning: Search text not found in content: {search_text[:100]}...")
    
    return modified_content

def apply_transformers_js_search_replace_changes(original_formatted_content: str, changes_text: str) -> str:
    """Apply search/replace changes to transformers.js formatted content (three files)"""
    if not changes_text.strip():
        return original_formatted_content
    
    # Parse the original formatted content to get the three files
    files = parse_transformers_js_output(original_formatted_content)
    
    # Split the changes text into individual search/replace blocks
    blocks = []
    current_block = ""
    lines = changes_text.split('\n')
    
    for line in lines:
        if line.strip() == SEARCH_START:
            if current_block.strip():
                blocks.append(current_block.strip())
            current_block = line + '\n'
        elif line.strip() == REPLACE_END:
            current_block += line + '\n'
            blocks.append(current_block.strip())
            current_block = ""
        else:
            current_block += line + '\n'
    
    if current_block.strip():
        blocks.append(current_block.strip())
    
    # Process each block and apply changes to the appropriate file
    for block in blocks:
        if not block.strip():
            continue
            
        # Parse the search/replace block
        lines = block.split('\n')
        search_lines = []
        replace_lines = []
        in_search = False
        in_replace = False
        target_file = None
        
        for line in lines:
            if line.strip() == SEARCH_START:
                in_search = True
                in_replace = False
            elif line.strip() == DIVIDER:
                in_search = False
                in_replace = True
            elif line.strip() == REPLACE_END:
                in_replace = False
            elif in_search:
                search_lines.append(line)
            elif in_replace:
                replace_lines.append(line)
        
        # Determine which file this change targets based on the search content
        if search_lines:
            search_text = '\n'.join(search_lines).strip()
            replace_text = '\n'.join(replace_lines).strip()
            
            # Check which file contains the search text
            if search_text in files['index.html']:
                target_file = 'index.html'
            elif search_text in files['index.js']:
                target_file = 'index.js'
            elif search_text in files['style.css']:
                target_file = 'style.css'
            
            # Apply the change to the target file
            if target_file and search_text in files[target_file]:
                files[target_file] = files[target_file].replace(search_text, replace_text)
            else:
                print(f"Warning: Search text not found in any transformers.js file: {search_text[:100]}...")
    
    # Reformat the modified files
    return format_transformers_js_output(files)

# Updated for faster Tavily search and closer prompt usage
# Uses 'advanced' search_depth and auto_parameters=True for speed and relevance

def perform_web_search(query: str, max_results: int = 5, include_domains=None, exclude_domains=None) -> str:
    """Perform web search using Tavily with default parameters"""
    if not tavily_client:
        return "Web search is not available. Please set the TAVILY_API_KEY environment variable."
    
    try:
        # Use Tavily defaults with advanced search depth for better results
        search_params = {
            "search_depth": "advanced",
            "max_results": min(max(1, max_results), 20)
        }
        if include_domains is not None:
            search_params["include_domains"] = include_domains
        if exclude_domains is not None:
            search_params["exclude_domains"] = exclude_domains

        response = tavily_client.search(query, **search_params)
        
        search_results = []
        for result in response.get('results', []):
            title = result.get('title', 'No title')
            url = result.get('url', 'No URL')
            content = result.get('content', 'No content')
            search_results.append(f"Title: {title}\nURL: {url}\nContent: {content}\n")
        
        if search_results:
            return "Web Search Results:\n\n" + "\n---\n".join(search_results)
        else:
            return "No search results found."
            
    except Exception as e:
        return f"Search error: {str(e)}"

def enhance_query_with_search(query: str, enable_search: bool) -> str:
    """Enhance the query with web search results if search is enabled"""
    if not enable_search or not tavily_client:
        return query
    
    # Perform search to get relevant information
    search_results = perform_web_search(query)
    
    # Combine original query with search results
    enhanced_query = f"""Original Query: {query}

{search_results}

Please use the search results above to help create the requested application with the most up-to-date information and best practices."""
    
    return enhanced_query

def send_to_sandbox(code):
    # Add a wrapper to inject necessary permissions and ensure full HTML
    wrapped_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <script>
            // Safe localStorage polyfill
            const safeStorage = {{
                _data: {{}},
                getItem: function(key) {{ return this._data[key] || null; }},
                setItem: function(key, value) {{ this._data[key] = value; }},
                removeItem: function(key) {{ delete this._data[key]; }},
                clear: function() {{ this._data = {{}}; }}
            }};
            Object.defineProperty(window, 'localStorage', {{
                value: safeStorage,
                writable: false
            }});
            window.onerror = function(message, source, lineno, colno, error) {{
                console.error('Error:', message);
            }};
        </script>
    </head>
    <body>
        {code}
    </body>
    </html>
    """
    encoded_html = base64.b64encode(wrapped_code.encode('utf-8')).decode('utf-8')
    data_uri = f"data:text/html;charset=utf-8;base64,{encoded_html}"
    iframe = f'<iframe src="{data_uri}" width="100%" height="920px" sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals allow-presentation" allow="display-capture"></iframe>'
    return iframe

def demo_card_click(e: gr.EventData):
    try:
        # Get the index from the event data
        if hasattr(e, '_data') and e._data:
            # Try different ways to get the index
            if 'index' in e._data:
                index = e._data['index']
            elif 'component' in e._data and 'index' in e._data['component']:
                index = e._data['component']['index']
            elif 'target' in e._data and 'index' in e._data['target']:
                index = e._data['target']['index']
            else:
                # If we can't get the index, try to extract it from the card data
                index = 0
        else:
            index = 0
        
        # Ensure index is within bounds
        if index >= len(DEMO_LIST):
            index = 0
            
        return DEMO_LIST[index]['description']
    except (KeyError, IndexError, AttributeError) as e:
        # Return the first demo description as fallback
        return DEMO_LIST[0]['description']

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        # Check if tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            return "Error: Tesseract OCR is not installed. Please install Tesseract to extract text from images. See install_tesseract.md for instructions."
        
        # Read image using OpenCV
        image = cv2.imread(image_path)
        if image is None:
            return "Error: Could not read image file"
        
        # Convert to RGB (OpenCV uses BGR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Preprocess image for better OCR results
        # Convert to grayscale
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extract text using pytesseract
        text = pytesseract.image_to_string(binary, config='--psm 6')
        
        return text.strip() if text.strip() else "No text found in image"
        
    except Exception as e:
        return f"Error extracting text from image: {e}"

def extract_text_from_file(file_path):
    if not file_path:
        return ""
    mime, _ = mimetypes.guess_type(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".docx":
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        elif ext.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp"]:
            return extract_text_from_image(file_path)
        else:
            return ""
    except Exception as e:
        return f"Error extracting text: {e}"

def extract_website_content(url: str) -> str:
    """Extract HTML code and content from a website URL"""
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "https://" + url
            parsed_url = urlparse(url)
        
        if not parsed_url.netloc:
            return "Error: Invalid URL provided"
        
        # Set comprehensive headers to mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Create a session to maintain cookies and handle redirects
        session = requests.Session()
        session.headers.update(headers)
        
        # Make the request with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = session.get(url, timeout=15, allow_redirects=True)
                response.raise_for_status()
                break
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403 and attempt < max_retries - 1:
                    # Try with different User-Agent on 403
                    session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    continue
                else:
                    raise
        
        # Get the raw HTML content with proper encoding
        try:
            # Try to get the content with automatic encoding detection
            response.encoding = response.apparent_encoding
            raw_html = response.text
        except:
            # Fallback to UTF-8 if encoding detection fails
            raw_html = response.content.decode('utf-8', errors='ignore')
        
        # Debug: Check if we got valid HTML
        if not raw_html.strip().startswith('<!DOCTYPE') and not raw_html.strip().startswith('<html'):
            print(f"Warning: Response doesn't look like HTML. First 200 chars: {raw_html[:200]}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response encoding: {response.encoding}")
            print(f"Apparent encoding: {response.apparent_encoding}")
            
            # Try alternative approaches
            try:
                raw_html = response.content.decode('latin-1', errors='ignore')
                print("Tried latin-1 decoding")
            except:
                try:
                    raw_html = response.content.decode('utf-8', errors='ignore')
                    print("Tried UTF-8 decoding")
                except:
                    raw_html = response.content.decode('cp1252', errors='ignore')
                    print("Tried cp1252 decoding")
        
        # Parse HTML content for analysis
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Check if this is a JavaScript-heavy site
        script_tags = soup.find_all('script')
        if len(script_tags) > 10:
            print(f"Warning: This site has {len(script_tags)} script tags - it may be a JavaScript-heavy site")
            print("The content might be loaded dynamically and not available in the initial HTML")
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title found"
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        # Extract main content areas for analysis
        content_sections = []
        main_selectors = [
            'main', 'article', '.content', '.main-content', '.post-content',
            '#content', '#main', '.entry-content', '.post-body'
        ]
        
        for selector in main_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if len(text) > 100:  # Only include substantial content
                    content_sections.append(text)
        
        # Extract navigation links for analysis
        nav_links = []
        nav_elements = soup.find_all(['nav', 'header'])
        for nav in nav_elements:
            links = nav.find_all('a')
            for link in links:
                link_text = link.get_text().strip()
                link_href = link.get('href', '')
                if link_text and link_href:
                    nav_links.append(f"{link_text}: {link_href}")
        
        # Extract and fix image URLs in the HTML
        img_elements = soup.find_all('img')
        for img in img_elements:
            src = img.get('src', '')
            if src:
                # Handle different URL formats
                if src.startswith('//'):
                    # Protocol-relative URL
                    absolute_src = 'https:' + src
                    img['src'] = absolute_src
                elif src.startswith('/'):
                    # Root-relative URL
                    absolute_src = urljoin(url, src)
                    img['src'] = absolute_src
                elif not src.startswith(('http://', 'https://')):
                    # Relative URL
                    absolute_src = urljoin(url, src)
                    img['src'] = absolute_src
                # If it's already absolute, keep it as is
                
                # Also check for data-src (lazy loading) and other common attributes
                data_src = img.get('data-src', '')
                if data_src and not src:
                    # Use data-src if src is empty
                    if data_src.startswith('//'):
                        absolute_data_src = 'https:' + data_src
                        img['src'] = absolute_data_src
                    elif data_src.startswith('/'):
                        absolute_data_src = urljoin(url, data_src)
                        img['src'] = absolute_data_src
                    elif not data_src.startswith(('http://', 'https://')):
                        absolute_data_src = urljoin(url, data_src)
                        img['src'] = absolute_data_src
                    else:
                        img['src'] = data_src
        
        # Also fix background image URLs in style attributes
        elements_with_style = soup.find_all(attrs={'style': True})
        for element in elements_with_style:
            style_attr = element.get('style', '')
            # Find and replace relative URLs in background-image
            import re
            bg_pattern = r'background-image:\s*url\(["\']?([^"\']+)["\']?\)'
            matches = re.findall(bg_pattern, style_attr, re.IGNORECASE)
            for match in matches:
                if match:
                    if match.startswith('//'):
                        absolute_bg = 'https:' + match
                        style_attr = style_attr.replace(match, absolute_bg)
                    elif match.startswith('/'):
                        absolute_bg = urljoin(url, match)
                        style_attr = style_attr.replace(match, absolute_bg)
                    elif not match.startswith(('http://', 'https://')):
                        absolute_bg = urljoin(url, match)
                        style_attr = style_attr.replace(match, absolute_bg)
            element['style'] = style_attr
        
        # Fix background images in <style> tags
        style_elements = soup.find_all('style')
        for style in style_elements:
            if style.string:
                style_content = style.string
                # Find and replace relative URLs in background-image
                bg_pattern = r'background-image:\s*url\(["\']?([^"\']+)["\']?\)'
                matches = re.findall(bg_pattern, style_content, re.IGNORECASE)
                for match in matches:
                    if match:
                        if match.startswith('//'):
                            absolute_bg = 'https:' + match
                            style_content = style_content.replace(match, absolute_bg)
                        elif match.startswith('/'):
                            absolute_bg = urljoin(url, match)
                            style_content = style_content.replace(match, absolute_bg)
                        elif not match.startswith(('http://', 'https://')):
                            absolute_bg = urljoin(url, match)
                            style_content = style_content.replace(match, absolute_bg)
                style.string = style_content
        
        # Extract images for analysis (after fixing URLs)
        images = []
        img_elements = soup.find_all('img')
        for img in img_elements:
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                images.append({'src': src, 'alt': alt})
        
        # Debug: Print some image URLs to see what we're getting
        print(f"Found {len(images)} images:")
        for i, img in enumerate(images[:5]):  # Show first 5 images
            print(f"  {i+1}. {img['alt'] or 'No alt'} - {img['src']}")
        
        # Test a few image URLs to see if they're accessible
        def test_image_url(img_url):
            try:
                test_response = requests.head(img_url, timeout=5, allow_redirects=True)
                return test_response.status_code == 200
            except:
                return False
        
        # Test first few images
        working_images = []
        for img in images[:10]:  # Test first 10 images
            if test_image_url(img['src']):
                working_images.append(img)
            else:
                print(f"  ❌ Broken image: {img['src']}")
        
        print(f"Working images: {len(working_images)} out of {len(images)}")
        
        # Get the modified HTML with absolute URLs
        modified_html = str(soup)
        
        # Clean and format the HTML for better readability
        # Remove unnecessary whitespace and comments
        import re
        cleaned_html = re.sub(r'<!--.*?-->', '', modified_html, flags=re.DOTALL)  # Remove HTML comments
        cleaned_html = re.sub(r'\s+', ' ', cleaned_html)  # Normalize whitespace
        cleaned_html = re.sub(r'>\s+<', '><', cleaned_html)  # Remove whitespace between tags
        
        # Limit HTML size to avoid token limits (keep first 15000 chars)
        if len(cleaned_html) > 15000:
            cleaned_html = cleaned_html[:15000] + "\n<!-- ... HTML truncated for length ... -->"
        
                # Check if we got any meaningful content
        if not title_text or title_text == "No title found":
            title_text = url.split('/')[-1] or url.split('/')[-2] or "Website"
        
        # If we couldn't extract any meaningful content, provide a fallback
        if len(cleaned_html.strip()) < 100:
            website_content = f"""
WEBSITE REDESIGN - EXTRACTION FAILED
====================================

URL: {url}
Title: {title_text}

ERROR: Could not extract meaningful HTML content from this website. This could be due to:
1. The website uses heavy JavaScript to load content dynamically
2. The website has anti-bot protection
3. The website requires authentication
4. The website is using advanced compression or encoding

FALLBACK APPROACH:
Please create a modern, responsive website design for a {title_text.lower()} website. Since I couldn't extract the original content, you can:

1. Create a typical layout for this type of website
2. Use placeholder content that would be appropriate
3. Include modern design elements and responsive features
4. Use a clean, professional design with good typography
5. Make it mobile-friendly and accessible

The website appears to be: {title_text}
"""
            return website_content.strip()
        
        # Compile the extracted content with the actual HTML code
        website_content = f"""
WEBSITE REDESIGN - ORIGINAL HTML CODE
=====================================

URL: {url}
Title: {title_text}
Description: {description}

PAGE ANALYSIS:
- This appears to be a {title_text.lower()} website
- Contains {len(content_sections)} main content sections
- Has {len(nav_links)} navigation links
- Includes {len(images)} images

IMAGES FOUND (use these exact URLs in your redesign):
{chr(10).join([f"• {img['alt'] or 'Image'} - {img['src']}" for img in working_images[:20]]) if working_images else "No working images found"}

ALL IMAGES (including potentially broken ones):
{chr(10).join([f"• {img['alt'] or 'Image'} - {img['src']}" for img in images[:20]]) if images else "No images found"}

ORIGINAL HTML CODE (use this as the base for redesign):
```html
{cleaned_html}
```

REDESIGN INSTRUCTIONS:
Please redesign this website with a modern, responsive layout while:
1. Preserving all the original content and structure
2. Maintaining the same navigation and functionality
3. Using the original images and their URLs (listed above)
4. Creating a modern, clean design with improved typography and spacing
5. Making it fully responsive for mobile devices
6. Using modern CSS frameworks and best practices
7. Keeping the same semantic structure but with enhanced styling

IMPORTANT: All image URLs in the HTML code above have been converted to absolute URLs and are ready to use. Make sure to preserve these exact image URLs in your redesigned version.

The HTML code above contains the complete original website structure with all images properly linked. Use it as your starting point and create a modernized version.
"""
        
        return website_content.strip()
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return f"Error: Website blocked access (403 Forbidden). This website may have anti-bot protection. Try a different website or provide a description of what you want to build instead."
        elif e.response.status_code == 404:
            return f"Error: Website not found (404). Please check the URL and try again."
        elif e.response.status_code >= 500:
            return f"Error: Website server error ({e.response.status_code}). Please try again later."
        else:
            return f"Error accessing website: HTTP {e.response.status_code} - {str(e)}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The website may be slow or unavailable."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the website. Please check your internet connection and the URL."
    except requests.exceptions.RequestException as e:
        return f"Error accessing website: {str(e)}"
    except Exception as e:
        return f"Error extracting website content: {str(e)}"

def generation_code(query: Optional[str], image: Optional[gr.Image], file: Optional[str], website_url: Optional[str], _setting: Dict[str, str], _history: Optional[History], _current_model: Dict, enable_search: bool = False, language: str = "html", provider: str = "auto"):
    if query is None:
        query = ''
    if _history is None:
        _history = []
    # Ensure _history is always a list of lists with at least 2 elements per item
    if not isinstance(_history, list):
        _history = []
    _history = [h for h in _history if isinstance(h, list) and len(h) == 2]

    # Check if there's existing content in history to determine if this is a modification request
    has_existing_content = False
    last_assistant_msg = ""
    if _history and len(_history[-1]) > 1:
        last_assistant_msg = _history[-1][1]
        # Check for various content types that indicate an existing project
        if ('<!DOCTYPE html>' in last_assistant_msg or 
            '<html' in last_assistant_msg or
            'import gradio' in last_assistant_msg or
            'import streamlit' in last_assistant_msg or
            'def ' in last_assistant_msg and 'app' in last_assistant_msg or
            'IMPORTED PROJECT FROM HUGGING FACE SPACE' in last_assistant_msg or
            '=== index.html ===' in last_assistant_msg or
            '=== index.js ===' in last_assistant_msg or
            '=== style.css ===' in last_assistant_msg or
            '=== src/App.svelte ===' in last_assistant_msg):
            has_existing_content = True

    # Choose system prompt based on context
    if has_existing_content:
        # Use follow-up prompt for modifying existing content
        if language == "transformers.js":
            system_prompt = TransformersJSFollowUpSystemPrompt
        elif language == "svelte":
            system_prompt = FollowUpSystemPrompt  # Use generic follow-up for Svelte
        else:
            system_prompt = FollowUpSystemPrompt
    else:
        # Use language-specific prompt
        if language == "html":
            system_prompt = HTML_SYSTEM_PROMPT_WITH_SEARCH if enable_search else HTML_SYSTEM_PROMPT
        elif language == "transformers.js":
            system_prompt = TRANSFORMERS_JS_SYSTEM_PROMPT_WITH_SEARCH if enable_search else TRANSFORMERS_JS_SYSTEM_PROMPT
        elif language == "svelte":
            system_prompt = SVELTE_SYSTEM_PROMPT_WITH_SEARCH if enable_search else SVELTE_SYSTEM_PROMPT
        else:
            system_prompt = GENERIC_SYSTEM_PROMPT_WITH_SEARCH.format(language=language) if enable_search else GENERIC_SYSTEM_PROMPT.format(language=language)

    messages = history_to_messages(_history, system_prompt)

    # Extract file text and append to query if file is present
    file_text = ""
    if file:
        file_text = extract_text_from_file(file)
        if file_text:
            file_text = file_text[:5000]  # Limit to 5000 chars for prompt size
            query = f"{query}\n\n[Reference file content below]\n{file_text}"

    # Extract website content and append to query if website URL is present
    website_text = ""
    if website_url and website_url.strip():
        website_text = extract_website_content(website_url.strip())
        if website_text and not website_text.startswith("Error"):
            website_text = website_text[:8000]  # Limit to 8000 chars for prompt size
            query = f"{query}\n\n[Website content to redesign below]\n{website_text}"
        elif website_text.startswith("Error"):
            # Provide helpful guidance when website extraction fails
            fallback_guidance = """
Since I couldn't extract the website content, please provide additional details about what you'd like to build:

1. What type of website is this? (e.g., e-commerce, blog, portfolio, dashboard)
2. What are the main features you want?
3. What's the target audience?
4. Any specific design preferences? (colors, style, layout)

This will help me create a better design for you."""
            query = f"{query}\n\n[Error extracting website: {website_text}]{fallback_guidance}"

    # Enhance query with search if enabled
    enhanced_query = enhance_query_with_search(query, enable_search)

    # Use dynamic client based on selected model
    client = get_inference_client(_current_model["id"], provider)

    if image is not None:
        messages.append(create_multimodal_message(enhanced_query, image))
    else:
        messages.append({'role': 'user', 'content': enhanced_query})
    try:
        completion = client.chat.completions.create(
            model=_current_model["id"],
            messages=messages,
            stream=True,
            max_tokens=20000
        )
        content = ""
        for chunk in completion:
            # Only process if chunk.choices is non-empty
            if (
                hasattr(chunk, "choices") and chunk.choices and 
                hasattr(chunk.choices[0], "delta") and 
                hasattr(chunk.choices[0].delta, "content") and 
                chunk.choices[0].delta.content is not None
            ):
                content += chunk.choices[0].delta.content
                search_status = " (with web search)" if enable_search and tavily_client else ""
                
                # Handle transformers.js output differently
                if language == "transformers.js":
                    files = parse_transformers_js_output(content)
                    if files['index.html'] and files['index.js'] and files['style.css']:
                        # Model returned complete transformers.js output
                        formatted_output = format_transformers_js_output(files)
                        yield {
                            code_output: gr.update(value=formatted_output, language="html"),
                            history_output: history_to_chatbot_messages(_history),
                            sandbox: send_to_sandbox(files['index.html']) if files['index.html'] else "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your code using the download button above.</div>",
                        }
                    elif has_existing_content:
                        # Model is returning search/replace changes for transformers.js - apply them
                        last_content = _history[-1][1] if _history and len(_history[-1]) > 1 else ""
                        modified_content = apply_transformers_js_search_replace_changes(last_content, content)
                        yield {
                            code_output: gr.update(value=modified_content, language="html"),
                            history_output: history_to_chatbot_messages(_history),
                            sandbox: send_to_sandbox(parse_transformers_js_output(modified_content)['index.html']) if parse_transformers_js_output(modified_content)['index.html'] else "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your code using the download button above.</div>",
                        }
                    else:
                        # Still streaming, show partial content
                        yield {
                            code_output: gr.update(value=content, language="html"),
                            history_output: history_to_chatbot_messages(_history),
                            sandbox: "<div style='padding:1em;color:#888;text-align:center;'>Generating transformers.js app...</div>",
                        }
                elif language == "svelte":
                    # For Svelte, just show the content as it streams
                    # We'll parse it properly in the final response
                    yield {
                        code_output: gr.update(value=content, language="html"),
                        history_output: history_to_chatbot_messages(_history),
                        sandbox: "<div style='padding:1em;color:#888;text-align:center;'>Generating Svelte app...</div>",
                    }
                else:
                    clean_code = remove_code_block(content)
                    if has_existing_content:
                        # Handle modification of existing content
                        if clean_code.strip().startswith("<!DOCTYPE html>") or clean_code.strip().startswith("<html"):
                            # Model returned a complete HTML file
                            yield {
                                code_output: gr.update(value=clean_code, language=get_gradio_language(language)),
                                history_output: history_to_chatbot_messages(_history),
                                sandbox: send_to_sandbox(clean_code) if language == "html" else "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your code using the download button above.</div>",
                            }
                        else:
                            # Model returned search/replace changes - apply them
                            last_content = _history[-1][1] if _history and len(_history[-1]) > 1 else ""
                            modified_content = apply_search_replace_changes(last_content, clean_code)
                            clean_content = remove_code_block(modified_content)
                            yield {
                                code_output: gr.update(value=clean_content, language=get_gradio_language(language)),
                                history_output: history_to_chatbot_messages(_history),
                                sandbox: send_to_sandbox(clean_content) if language == "html" else "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your code using the download button above.</div>",
                            }
                    else:
                        yield {
                            code_output: gr.update(value=clean_code, language=get_gradio_language(language)),
                            history_output: history_to_chatbot_messages(_history),
                            sandbox: send_to_sandbox(clean_code) if language == "html" else "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your code using the download button above.</div>",
                        }
            # Skip chunks with empty choices (end of stream)
            # Do not treat as error
        # Handle response based on whether this is a modification or new generation
        if language == "transformers.js":
            # Handle transformers.js output
            files = parse_transformers_js_output(content)
            if files['index.html'] and files['index.js'] and files['style.css']:
                # Model returned complete transformers.js output
                formatted_output = format_transformers_js_output(files)
                _history.append([query, formatted_output])
                yield {
                    code_output: formatted_output,
                    history: _history,
                    sandbox: send_to_sandbox(files['index.html']),
                    history_output: history_to_chatbot_messages(_history),
                }
            elif has_existing_content:
                # Model returned search/replace changes for transformers.js - apply them
                last_content = _history[-1][1] if _history and len(_history[-1]) > 1 else ""
                modified_content = apply_transformers_js_search_replace_changes(last_content, content)
                _history.append([query, modified_content])
                yield {
                    code_output: modified_content,
                    history: _history,
                    sandbox: send_to_sandbox(parse_transformers_js_output(modified_content)['index.html']),
                    history_output: history_to_chatbot_messages(_history),
                }
            else:
                # Fallback if parsing failed
                _history.append([query, content])
                yield {
                    code_output: content,
                    history: _history,
                    sandbox: "<div style='padding:1em;color:#888;text-align:center;'>Error parsing transformers.js output. Please try again.</div>",
                    history_output: history_to_chatbot_messages(_history),
                }
        elif language == "svelte":
            # Handle Svelte output
            files = parse_svelte_output(content)
            if files['src/App.svelte'] and files['src/app.css']:
                # Model returned complete Svelte output
                formatted_output = format_svelte_output(files)
                _history.append([query, formatted_output])
                yield {
                    code_output: formatted_output,
                    history: _history,
                    sandbox: "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your Svelte code using the download button above.</div>",
                    history_output: history_to_chatbot_messages(_history),
                }
            elif has_existing_content:
                # Model returned search/replace changes for Svelte - apply them
                last_content = _history[-1][1] if _history and len(_history[-1]) > 1 else ""
                modified_content = apply_search_replace_changes(last_content, content)
                _history.append([query, modified_content])
                yield {
                    code_output: modified_content,
                    history: _history,
                    sandbox: "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your Svelte code using the download button above.</div>",
                    history_output: history_to_chatbot_messages(_history),
                }
            else:
                # Fallback if parsing failed - just use the raw content
                _history.append([query, content])
                yield {
                    code_output: content,
                    history: _history,
                    sandbox: "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your Svelte code using the download button above.</div>",
                    history_output: history_to_chatbot_messages(_history),
                }
        elif has_existing_content:
            # Handle modification of existing content
            final_code = remove_code_block(content)
            if final_code.strip().startswith("<!DOCTYPE html>") or final_code.strip().startswith("<html"):
                # Model returned a complete HTML file
                clean_content = final_code
            else:
                # Model returned search/replace changes - apply them
                last_content = _history[-1][1] if _history and len(_history[-1]) > 1 else ""
                modified_content = apply_search_replace_changes(last_content, final_code)
                clean_content = remove_code_block(modified_content)
            # Update history with the cleaned content
            _history.append([query, clean_content])
            yield {
                code_output: clean_content,
                history: _history,
                sandbox: send_to_sandbox(clean_content) if language == "html" else "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your code using the download button above.</div>",
                history_output: history_to_chatbot_messages(_history),
            }
        else:
            # Regular generation - use the content as is
            _history.append([query, content])
            yield {
                code_output: remove_code_block(content),
                history: _history,
                sandbox: send_to_sandbox(remove_code_block(content)),
                history_output: history_to_chatbot_messages(_history),
            }
    except Exception as e:
        error_message = f"Error: {str(e)}"
        yield {
            code_output: error_message,
            history_output: history_to_chatbot_messages(_history),
        }

# Deploy to Spaces logic

def wrap_html_in_gradio_app(html_code):
    # Escape triple quotes for safe embedding
    safe_html = html_code.replace('"""', r'\"\"\"')
    return (
        'import gradio as gr\n\n'
        'def show_html():\n'
        f'    return """{safe_html}"""\n\n'
        'demo = gr.Interface(fn=show_html, inputs=None, outputs=gr.HTML())\n\n'
        'if __name__ == "__main__":\n'
        '    demo.launch()\n'
    )

def deploy_to_spaces(code):
    if not code or not code.strip():
        return  # Do nothing if code is empty
    # Wrap the HTML code in a Gradio app
    app_py = wrap_html_in_gradio_app(code.strip())
    base_url = "https://huggingface.co/new-space"
    params = urllib.parse.urlencode({
        "name": "new-space",
        "sdk": "gradio"
    })
    # Use urlencode for file params
    files_params = urllib.parse.urlencode({
        "files[0][path]": "app.py",
        "files[0][content]": app_py
    })
    full_url = f"{base_url}?{params}&{files_params}"
    webbrowser.open_new_tab(full_url)

def wrap_html_in_static_app(html_code):
    # For static Spaces, just use the HTML code as-is
    return html_code

def deploy_to_spaces_static(code):
    if not code or not code.strip():
        return  # Do nothing if code is empty
    # Use the HTML code directly for static Spaces
    app_html = wrap_html_in_static_app(code.strip())
    base_url = "https://huggingface.co/new-space"
    params = urllib.parse.urlencode({
        "name": "new-space",
        "sdk": "static"
    })
    files_params = urllib.parse.urlencode({
        "files[0][path]": "index.html",
        "files[0][content]": app_html
    })
    full_url = f"{base_url}?{params}&{files_params}"
    webbrowser.open_new_tab(full_url)

def check_hf_space_url(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Check if URL is a valid Hugging Face Spaces URL and extract username/project"""
    import re
    
    # Pattern to match HF Spaces URLs
    url_pattern = re.compile(
        r'^(https?://)?(huggingface\.co|hf\.co)/spaces/([\w-]+)/([\w-]+)$',
        re.IGNORECASE
    )
    
    match = url_pattern.match(url.strip())
    if match:
        username = match.group(3)
        project_name = match.group(4)
        return True, username, project_name
    return False, None, None

def fetch_hf_space_content(username: str, project_name: str) -> str:
    """Fetch content from a Hugging Face Space"""
    try:
        import requests
        from huggingface_hub import HfApi
        
        # Try to get space info first
        api = HfApi()
        space_info = api.space_info(f"{username}/{project_name}")
        
        # Try to fetch the main file based on SDK
        sdk = space_info.sdk
        main_file = None
        
        if sdk == "static":
            main_file = "index.html"
        elif sdk == "gradio":
            main_file = "app.py"
        elif sdk == "streamlit":
            main_file = "streamlit_app.py"
        else:
            # Try common files
            for file in ["app.py", "index.html", "streamlit_app.py", "main.py"]:
                try:
                    content = api.hf_hub_download(
                        repo_id=f"{username}/{project_name}",
                        filename=file,
                        repo_type="space"
                    )
                    main_file = file
                    break
                except:
                    continue
        
        if main_file:
            content = api.hf_hub_download(
                repo_id=f"{username}/{project_name}",
                filename=main_file,
                repo_type="space"
            )
            
            # Read the file content
            with open(content, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            return f"""IMPORTED PROJECT FROM HUGGING FACE SPACE
==============================================

Space: {username}/{project_name}
SDK: {sdk}
Main File: {main_file}

{file_content}"""
        else:
            return f"Error: Could not find main file in space {username}/{project_name}"
            
    except Exception as e:
        return f"Error fetching space content: {str(e)}"

def load_project_from_url(url: str) -> Tuple[str, str]:
    """Load project from Hugging Face Space URL"""
    # Validate URL
    is_valid, username, project_name = check_hf_space_url(url)
    
    if not is_valid:
        return "Error: Please enter a valid Hugging Face Spaces URL.\n\nExpected format: https://huggingface.co/spaces/username/project", ""
    
    # Fetch content
    content = fetch_hf_space_content(username, project_name)
    
    if content.startswith("Error:"):
        return content, ""
    
    # Extract the actual code content by removing metadata
    lines = content.split('\n')
    code_start = 0
    for i, line in enumerate(lines):
        # Skip metadata lines and find the start of actual code
        if (line.strip() and 
            not line.startswith('=') and 
            not line.startswith('IMPORTED PROJECT') and
            not line.startswith('Space:') and
            not line.startswith('SDK:') and
            not line.startswith('Main File:')):
            code_start = i
            break
    
    code_content = '\n'.join(lines[code_start:])
    
    return f"✅ Successfully imported project from {username}/{project_name}", code_content

# Main application
with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="blue",
        secondary_hue="gray",
        neutral_hue="gray",
        font=gr.themes.GoogleFont("Inter"),
        font_mono=gr.themes.GoogleFont("JetBrains Mono"),
        text_size=gr.themes.sizes.text_md,
        spacing_size=gr.themes.sizes.spacing_md,
        radius_size=gr.themes.sizes.radius_md
    ),
    title="AnyCoder - AI Code Generator"
) as demo:
    history = gr.State([])
    setting = gr.State({
        "system": HTML_SYSTEM_PROMPT,
    })
    current_model = gr.State(AVAILABLE_MODELS[0])  # Moonshot Kimi-K2
    open_panel = gr.State(None)
    last_login_state = gr.State(None)

    with gr.Sidebar():
        login_button = gr.LoginButton()
        
        # Add Load Project section
        gr.Markdown("📥 Load Existing Project")
        load_project_url = gr.Textbox(
            label="Hugging Face Space URL",
            placeholder="https://huggingface.co/spaces/username/project",
            lines=1
        )
        load_project_btn = gr.Button("Import Project", variant="secondary", size="sm")
        load_project_status = gr.Markdown(visible=False)
        
        gr.Markdown("---")
        
        input = gr.Textbox(
            label="What would you like to build?",
            placeholder="Describe your application...",
            lines=3,
            visible=True
        )
        # Language dropdown for code generation
        language_choices = [
            "html", "python", "transformers.js", "svelte", "c", "cpp", "markdown", "latex", "json", "css", "javascript", "jinja2", "typescript", "yaml", "dockerfile", "shell", "r", "sql", "sql-msSQL", "sql-mySQL", "sql-mariaDB", "sql-sqlite", "sql-cassandra", "sql-plSQL", "sql-hive", "sql-pgSQL", "sql-gql", "sql-gpSQL", "sql-sparkSQL", "sql-esper"
        ]
        language_dropdown = gr.Dropdown(
            choices=language_choices,
            value="html",
            label="Code Language",
            visible=True
        )
        website_url_input = gr.Textbox(
            label="website for redesign",
            placeholder="https://example.com",
            lines=1,
            visible=True
        )
        file_input = gr.File(
            label="Reference file",
            file_types=[".pdf", ".txt", ".md", ".csv", ".docx", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp"],
            visible=True
        )
        image_input = gr.Image(
            label="UI design image",
            visible=False
        )
        with gr.Row():
            btn = gr.Button("Generate", variant="primary", size="lg", scale=2, visible=True)
            clear_btn = gr.Button("Clear", variant="secondary", size="sm", scale=1, visible=True)
        # --- Move deploy/app name/sdk here, right before web search ---
        space_name_input = gr.Textbox(
            label="app name (e.g. my-cool-app)",
            placeholder="Enter your app name",
            lines=1,
            visible=False
        )
        sdk_choices = [
            ("Gradio (Python)", "gradio"),
            ("Streamlit (Python)", "streamlit"),
            ("Static (HTML)", "static"),
            ("Transformers.js", "transformers.js"),
            ("Svelte", "svelte")
        ]
        sdk_dropdown = gr.Dropdown(
            choices=[x[0] for x in sdk_choices],
            value="Static (HTML)",
            label="App SDK",
            visible=False
        )
        deploy_btn = gr.Button("🚀 Deploy App", variant="primary", visible=False)
        deploy_status = gr.Markdown(visible=False, label="Deploy status")
        # --- End move ---
        search_toggle = gr.Checkbox(
            label="🔍 Web search",
            value=False,
            visible=True
        )
        model_dropdown = gr.Dropdown(
            choices=[model['name'] for model in AVAILABLE_MODELS],
            value=AVAILABLE_MODELS[0]['name'],
            label="Model",
            visible=True
        )
        provider_state = gr.State("auto")
        gr.Markdown("**Quick start**", visible=True)
        with gr.Column(visible=True) as quick_examples_col:
            for i, demo_item in enumerate(DEMO_LIST[:3]):
                demo_card = gr.Button(
                    value=demo_item['title'], 
                    variant="secondary",
                    size="sm"
                )
                demo_card.click(
                    fn=lambda idx=i: gr.update(value=DEMO_LIST[idx]['description']),
                    outputs=input
                )
        if not tavily_client:
            gr.Markdown("⚠️ Web search unavailable", visible=True)
        # Remove model display and web search available line
        def on_model_change(model_name):
            for m in AVAILABLE_MODELS:
                if m['name'] == model_name:
                    return m, update_image_input_visibility(m)
            return AVAILABLE_MODELS[0], update_image_input_visibility(AVAILABLE_MODELS[0])
        def save_prompt(input):
            return {setting: {"system": input}}
        model_dropdown.change(
            lambda model_name: on_model_change(model_name),
            inputs=model_dropdown,
            outputs=[current_model, image_input]
        )
        # --- Remove deploy/app name/sdk from bottom column ---
        # (delete the gr.Column() block containing space_name_input, sdk_dropdown, deploy_btn, deploy_status)

    with gr.Column():
        with gr.Tabs():
            with gr.Tab("Code"):
                code_output = gr.Code(
                    language="html", 
                    lines=25, 
                    interactive=True,
                    label="Generated code"
                )
            with gr.Tab("Preview"):
                sandbox = gr.HTML(label="Live preview")
            with gr.Tab("History"):
                history_output = gr.Chatbot(show_label=False, height=400, type="messages")

    # Load project function
    def handle_load_project(url):
        if not url.strip():
            return gr.update(value="Please enter a URL.", visible=True)
        
        status, code = load_project_from_url(url)
        
        if code:
            # Extract space info for deployment
            is_valid, username, project_name = check_hf_space_url(url)
            space_info = f"{username}/{project_name}" if is_valid else ""
            
            # Success - update the code output and show success message
            # Also update history to include the loaded project
            loaded_history = [[f"Loaded project from {url}", code]]
            return [
                gr.update(value=status, visible=True),
                gr.update(value=code, language="html"),
                gr.update(value=send_to_sandbox(code) if code.strip().startswith('<!DOCTYPE html>') or code.strip().startswith('<html') else "<div style='padding:1em;color:#888;text-align:center;'>Preview not available for this file type.</div>"),
                gr.update(value=""),
                loaded_history,
                history_to_chatbot_messages(loaded_history),
                gr.update(value=space_info, visible=True),  # Update space name with loaded project
                gr.update(value="Update Existing Space", visible=True)  # Change button text
            ]
        else:
            # Error - just show error message
            return [
                gr.update(value=status, visible=True),
                gr.update(),
                gr.update(),
                gr.update(),
                [],
                [],
                gr.update(value="", visible=False),
                gr.update(value="🚀 Deploy App", visible=False)
            ]

    # Event handlers
    def update_code_language(language):
        return gr.update(language=get_gradio_language(language))

    def update_sdk_based_on_language(language):
        if language == "transformers.js":
            return gr.update(value="Transformers.js")
        elif language == "svelte":
            return gr.update(value="Svelte")
        elif language == "html":
            return gr.update(value="Static (HTML)")
        else:
            return gr.update(value="Gradio (Python)")

    language_dropdown.change(update_code_language, inputs=language_dropdown, outputs=code_output)
    language_dropdown.change(update_sdk_based_on_language, inputs=language_dropdown, outputs=sdk_dropdown)

    def preview_logic(code, language):
        if language == "html":
            return send_to_sandbox(code)
        elif language == "transformers.js":
            # For transformers.js, extract the HTML part for preview
            files = parse_transformers_js_output(code)
            if files['index.html']:
                return send_to_sandbox(files['index.html'])
            else:
                return "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your code using the download button above.</div>"
        elif language == "svelte":
            # For Svelte, we can't preview the compiled app, so show a message
            return "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your Svelte code and deploy it to see the result.</div>"
        else:
            return "<div style='padding:1em;color:#888;text-align:center;'>Preview is only available for HTML. Please download your code using the download button above.</div>"

    def show_deploy_components(*args):
        return [gr.Textbox(visible=True), gr.Dropdown(visible=True), gr.Button(visible=True)]

    def hide_deploy_components(*args):
        return [gr.Textbox(visible=False), gr.Dropdown(visible=False), gr.Button(visible=False)]

    # Load project button event
    load_project_btn.click(
        handle_load_project,
        inputs=[load_project_url],
        outputs=[load_project_status, code_output, sandbox, load_project_url, history, history_output, space_name_input, deploy_btn]
    )

    btn.click(
        generation_code,
        inputs=[input, image_input, file_input, website_url_input, setting, history, current_model, search_toggle, language_dropdown, provider_state],
        outputs=[code_output, history, sandbox, history_output]
    ).then(
        show_deploy_components,
        None,
        [space_name_input, sdk_dropdown, deploy_btn]
    )
    # Update preview when code or language changes
    code_output.change(preview_logic, inputs=[code_output, language_dropdown], outputs=sandbox)
    language_dropdown.change(preview_logic, inputs=[code_output, language_dropdown], outputs=sandbox)
    clear_btn.click(clear_history, outputs=[history, history_output, file_input, website_url_input])
    clear_btn.click(hide_deploy_components, None, [space_name_input, sdk_dropdown, deploy_btn])
    # Reset space name and button text when clearing
    clear_btn.click(
        lambda: [gr.update(value=""), gr.update(value="🚀 Deploy App")],
        outputs=[space_name_input, deploy_btn]
    )

    # Deploy to Spaces logic

    def deploy_to_user_space(
        code, 
        space_name, 
        sdk_name,  # new argument
        profile: gr.OAuthProfile | None = None, 
        token: gr.OAuthToken | None = None
    ):
        import shutil
        if not code or not code.strip():
            return gr.update(value="No code to deploy.", visible=True)
        if profile is None or token is None:
            return gr.update(value="Please log in with your Hugging Face account to deploy to your own Space. Otherwise, use the default deploy (opens in new tab).", visible=True)
        
        # Check if token has write permissions
        if not token.token or token.token == "hf_":
            return gr.update(value="Error: Invalid token. Please log in again with your Hugging Face account to get a valid write token.", visible=True)
        
        # Check if this is an update to an existing space (contains /)
        is_update = "/" in space_name.strip()
        if is_update:
            # This is an existing space, use the provided space_name as repo_id
            repo_id = space_name.strip()
            # Extract username from repo_id for permission check
            space_username = repo_id.split('/')[0]
            if space_username != profile.username:
                return gr.update(value=f"Error: You can only update your own spaces. This space belongs to {space_username}.", visible=True)
            
            # Verify the user has write access to this space
            try:
                api = HfApi(token=token.token)
                # Try to get space info to verify access
                space_info = api.space_info(repo_id)
                if not space_info:
                    return gr.update(value=f"Error: Could not access space {repo_id}. Please check your permissions.", visible=True)
            except Exception as e:
                return gr.update(value=f"Error: No write access to space {repo_id}. Please ensure you have the correct permissions. Error: {str(e)}", visible=True)
        else:
            # This is a new space, create repo_id with current user
            username = profile.username
            repo_id = f"{username}/{space_name.strip()}"
        # Map SDK name to HF SDK slug
        sdk_map = {
            "Gradio (Python)": "gradio",
            "Streamlit (Python)": "docker",  # Use 'docker' for Streamlit Spaces
            "Static (HTML)": "static",
            "Transformers.js": "static",  # Transformers.js uses static SDK
            "Svelte": "static"  # Svelte uses static SDK
        }
        sdk = sdk_map.get(sdk_name, "gradio")
        
        # Create API client with user's token for proper authentication
        api = HfApi(token=token.token)
        # Only create the repo for new spaces (not updates) and non-Transformers.js, non-Streamlit, and non-Svelte SDKs
        if not is_update and sdk != "docker" and sdk_name not in ["Transformers.js", "Svelte"]:
            try:
                api.create_repo(
                    repo_id=repo_id,  # e.g. username/space_name
                    repo_type="space",
                    space_sdk=sdk,  # Use selected SDK
                    exist_ok=True  # Don't error if it already exists
                )
            except Exception as e:
                return gr.update(value=f"Error creating Space: {e}", visible=True)
        # Streamlit/docker logic
        if sdk == "docker" and not is_update:
            try:
                # Use duplicate_space to create a Streamlit template space
                from huggingface_hub import duplicate_space
                
                # Duplicate the streamlit template space
                duplicated_repo = duplicate_space(
                    from_id="streamlit/streamlit-template-space",
                    to_id=space_name.strip(),
                    token=token.token,
                    exist_ok=True
                )
                
                # Upload the user's code to the duplicated space
                import tempfile
                with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                    f.write(code)
                    temp_path = f.name
                
                try:
                    api.upload_file(
                        path_or_fileobj=temp_path,
                        path_in_repo="src/streamlit_app.py",
                        repo_id=repo_id,
                        repo_type="space"
                    )
                    space_url = f"https://huggingface.co/spaces/{repo_id}"
                    action_text = "Updated" if is_update else "Deployed"
                    return gr.update(value=f"✅ {action_text}! [Open your Space here]({space_url})", visible=True)
                except Exception as e:
                    error_msg = str(e)
                    if "403 Forbidden" in error_msg and "write token" in error_msg:
                        return gr.update(value=f"Error: Permission denied. Please ensure you have write access to {repo_id} and your token has the correct permissions.", visible=True)
                    else:
                        return gr.update(value=f"Error uploading Streamlit app: {e}", visible=True)
                finally:
                    import os
                    os.unlink(temp_path)
                    
            except Exception as e:
                return gr.update(value=f"Error duplicating Streamlit space: {e}", visible=True)
        # Transformers.js logic
        elif sdk_name == "Transformers.js" and not is_update:
            try:
                # Use duplicate_space to create a transformers.js template space
                from huggingface_hub import duplicate_space
                
                # Duplicate the transformers.js template space
                duplicated_repo = duplicate_space(
                    from_id="static-templates/transformers.js",
                    to_id=space_name.strip(),
                    token=token.token,
                    exist_ok=True
                )
                print("Duplicated repo result:", duplicated_repo, type(duplicated_repo))
                # Parse the transformers.js output to get the three files
                files = parse_transformers_js_output(code)
                
                if not files['index.html'] or not files['index.js'] or not files['style.css']:
                    return gr.update(value="Error: Could not parse transformers.js output. Please regenerate the code.", visible=True)
                
                # Upload the three files to the duplicated space
                import tempfile
                
                # Upload index.html
                with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
                    f.write(files['index.html'])
                    temp_path = f.name
                
                try:
                    api.upload_file(
                        path_or_fileobj=temp_path,
                        path_in_repo="index.html",
                        repo_id=repo_id,
                        repo_type="space"
                    )
                except Exception as e:
                    error_msg = str(e)
                    if "403 Forbidden" in error_msg and "write token" in error_msg:
                        return gr.update(value=f"Error: Permission denied. Please ensure you have write access to {repo_id} and your token has the correct permissions.", visible=True)
                    else:
                        return gr.update(value=f"Error uploading index.html: {e}", visible=True)
                finally:
                    import os
                    os.unlink(temp_path)
                
                # Upload index.js
                with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
                    f.write(files['index.js'])
                    temp_path = f.name
                
                try:
                    api.upload_file(
                        path_or_fileobj=temp_path,
                        path_in_repo="index.js",
                        repo_id=repo_id,
                        repo_type="space"
                    )
                except Exception as e:
                    error_msg = str(e)
                    if "403 Forbidden" in error_msg and "write token" in error_msg:
                        return gr.update(value=f"Error: Permission denied. Please ensure you have write access to {repo_id} and your token has the correct permissions.", visible=True)
                    else:
                        return gr.update(value=f"Error uploading index.js: {e}", visible=True)
                finally:
                    import os
                    os.unlink(temp_path)
                
                # Upload style.css
                with tempfile.NamedTemporaryFile("w", suffix=".css", delete=False) as f:
                    f.write(files['style.css'])
                    temp_path = f.name
                
                try:
                    api.upload_file(
                        path_or_fileobj=temp_path,
                        path_in_repo="style.css",
                        repo_id=repo_id,
                        repo_type="space"
                    )
                    space_url = f"https://huggingface.co/spaces/{repo_id}"
                    action_text = "Updated" if is_update else "Deployed"
                    return gr.update(value=f"✅ {action_text}! [Open your Transformers.js Space here]({space_url})", visible=True)
                except Exception as e:
                    error_msg = str(e)
                    if "403 Forbidden" in error_msg and "write token" in error_msg:
                        return gr.update(value=f"Error: Permission denied. Please ensure you have write access to {repo_id} and your token has the correct permissions.", visible=True)
                    else:
                        return gr.update(value=f"Error uploading style.css: {e}", visible=True)
                finally:
                    import os
                    os.unlink(temp_path)
                    
            except Exception as e:
                # Handle potential RepoUrl object errors
                error_msg = str(e)
                if "'url'" in error_msg or "RepoUrl" in error_msg:
                    return gr.update(value=f"Error duplicating Transformers.js space: RepoUrl handling error. Please try again. Details: {error_msg}", visible=True)
                return gr.update(value=f"Error duplicating Transformers.js space: {error_msg}", visible=True)
        # Svelte logic
        elif sdk_name == "Svelte" and not is_update:
            try:
                # Use duplicate_space to create a Svelte template space
                from huggingface_hub import duplicate_space
                
                # Duplicate the Svelte template space
                duplicated_repo = duplicate_space(
                    from_id="static-templates/svelte",
                    to_id=repo_id,  # Use the full repo_id (username/space_name)
                    token=token.token,
                    exist_ok=True
                )
                print("Duplicated Svelte repo result:", duplicated_repo, type(duplicated_repo))
                
                # Extract the actual repo ID from the duplicated space
                # The duplicated_repo is a RepoUrl object, convert to string and extract the repo ID
                try:
                    duplicated_repo_str = str(duplicated_repo)
                    # Extract username and repo name from the URL
                    if "/spaces/" in duplicated_repo_str:
                        parts = duplicated_repo_str.split("/spaces/")[-1].split("/")
                        if len(parts) >= 2:
                            actual_repo_id = f"{parts[0]}/{parts[1]}"
                        else:
                            actual_repo_id = repo_id  # Fallback to original
                    else:
                        actual_repo_id = repo_id  # Fallback to original
                except Exception as e:
                    print(f"Error extracting repo ID from duplicated_repo: {e}")
                    actual_repo_id = repo_id  # Fallback to original
                print("Actual repo ID for Svelte uploads:", actual_repo_id)
                
                # Parse the Svelte output to get the custom files
                files = parse_svelte_output(code)
                
                if not files['src/App.svelte']:
                    return gr.update(value="Error: Could not parse Svelte output. Please regenerate the code.", visible=True)
                
                # Upload only the custom Svelte files to the duplicated space
                import tempfile
                
                # Upload src/App.svelte (required)
                with tempfile.NamedTemporaryFile("w", suffix=".svelte", delete=False) as f:
                    f.write(files['src/App.svelte'])
                    temp_path = f.name
                
                try:
                    api.upload_file(
                        path_or_fileobj=temp_path,
                        path_in_repo="src/App.svelte",
                        repo_id=actual_repo_id,
                        repo_type="space"
                                        )
                except Exception as e:
                    error_msg = str(e)
                    if "403 Forbidden" in error_msg and "write token" in error_msg:
                        return gr.update(value=f"Error: Permission denied. Please ensure you have write access to {actual_repo_id} and your token has the correct permissions.", visible=True)
                    else:
                        return gr.update(value=f"Error uploading src/App.svelte: {e}", visible=True)
                finally:
                    import os
                    os.unlink(temp_path)
                
                # Upload src/app.css (optional)
                if files['src/app.css']:
                    with tempfile.NamedTemporaryFile("w", suffix=".css", delete=False) as f:
                        f.write(files['src/app.css'])
                        temp_path = f.name
                    
                    try:
                        api.upload_file(
                            path_or_fileobj=temp_path,
                            path_in_repo="src/app.css",
                            repo_id=actual_repo_id,
                            repo_type="space"
                        )
                    except Exception as e:
                        error_msg = str(e)
                        if "403 Forbidden" in error_msg and "write token" in error_msg:
                            return gr.update(value=f"Error: Permission denied. Please ensure you have write access to {actual_repo_id} and your token has the correct permissions.", visible=True)
                        else:
                            return gr.update(value=f"Error uploading src/app.css: {e}", visible=True)
                    finally:
                        import os
                        os.unlink(temp_path)
                
                # Success - all files uploaded
                space_url = f"https://huggingface.co/spaces/{actual_repo_id}"
                action_text = "Updated" if is_update else "Deployed"
                return gr.update(value=f"✅ {action_text}! [Open your Svelte Space here]({space_url})", visible=True)
                    
            except Exception as e:
                # Handle potential RepoUrl object errors
                error_msg = str(e)
                if "'url'" in error_msg or "RepoUrl" in error_msg:
                    return gr.update(value=f"Error duplicating Svelte space: RepoUrl handling error. Please try again. Details: {error_msg}", visible=True)
                return gr.update(value=f"Error duplicating Svelte space: {error_msg}", visible=True)
        # Other SDKs (existing logic)
        if sdk == "static":
            import time
            file_name = "index.html"
            # Wait and retry logic after repo creation
            max_attempts = 3
            for attempt in range(max_attempts):
                import tempfile
                with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
                    f.write(code)
                    temp_path = f.name
                try:
                    api.upload_file(
                        path_or_fileobj=temp_path,
                        path_in_repo=file_name,
                        repo_id=repo_id,
                        repo_type="space"
                    )
                    space_url = f"https://huggingface.co/spaces/{repo_id}"
                    action_text = "Updated" if is_update else "Deployed"
                    return gr.update(value=f"✅ {action_text}! [Open your Space here]({space_url})", visible=True)
                except Exception as e:
                    error_msg = str(e)
                    if "403 Forbidden" in error_msg and "write token" in error_msg:
                        return gr.update(value=f"Error: Permission denied. Please ensure you have write access to {repo_id} and your token has the correct permissions.", visible=True)
                    elif attempt < max_attempts - 1:
                        time.sleep(2)  # Wait before retrying
                    else:
                        return gr.update(value=f"Error uploading file after {max_attempts} attempts: {e}. Please check your permissions and try again.", visible=True)
                finally:
                    import os
                    os.unlink(temp_path)
        else:
            file_name = "app.py"
            import tempfile
            with tempfile.NamedTemporaryFile("w", suffix=f".{file_name.split('.')[-1]}", delete=False) as f:
                f.write(code)
                temp_path = f.name
            try:
                api.upload_file(
                    path_or_fileobj=temp_path,
                    path_in_repo=file_name,
                    repo_id=repo_id,
                    repo_type="space"
                )
                space_url = f"https://huggingface.co/spaces/{repo_id}"
                action_text = "Updated" if is_update else "Deployed"
                return gr.update(value=f"✅ {action_text}! [Open your Space here]({space_url})", visible=True)
            except Exception as e:
                error_msg = str(e)
                if "403 Forbidden" in error_msg and "write token" in error_msg:
                    return gr.update(value=f"Error: Permission denied. Please ensure you have write access to {repo_id} and your token has the correct permissions.", visible=True)
                else:
                    return gr.update(value=f"Error uploading file: {e}", visible=True)
            finally:
                import os
                os.unlink(temp_path)

    # Connect the deploy button to the new function
    deploy_btn.click(
        deploy_to_user_space,
        inputs=[code_output, space_name_input, sdk_dropdown],
        outputs=deploy_status
    )
    # Keep the old deploy method as fallback (if not logged in, user can still use the old method)
    # Optionally, you can keep the old deploy_btn.click for the default method as a secondary button.

if __name__ == "__main__":
    demo.queue(api_open=False, default_concurrency_limit=20).launch(show_api=False, ssr_mode=True, mcp_server=False)