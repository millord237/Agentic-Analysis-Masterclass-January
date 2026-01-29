"""
Vercel Serverless API for AI Data Analyst
"""
from flask import Flask, request, jsonify
import os
import json
import requests
import pandas as pd
from io import StringIO

app = Flask(__name__)

# Get API keys from environment variables
OPENANALYST_API_KEY = os.environ.get('OPENANALYST_API_KEY', '')
OPENANALYST_API_URL = "https://api.openanalyst.com/api/ai/chat"
OPENANALYST_MODEL = "anthropic/claude-sonnet-4"

PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY', '')
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "llama-3.1-sonar-small-128k-online"

# In-memory storage for uploaded files (for demo - use cloud storage in production)
uploaded_files = {}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Data Analyst</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; min-height: 100vh; display: flex; }
        .sidebar { width: 300px; background: rgba(22, 33, 62, 0.9); padding: 20px; border-right: 1px solid #e94560; display: flex; flex-direction: column; }
        .sidebar h2 { color: #e94560; margin-bottom: 20px; }
        .upload-zone { border: 2px dashed #e94560; border-radius: 10px; padding: 30px 20px; text-align: center; cursor: pointer; margin-bottom: 20px; transition: 0.3s; }
        .upload-zone:hover { background: rgba(233, 69, 96, 0.1); }
        .file-list { flex: 1; overflow-y: auto; }
        .file-item { display: flex; align-items: center; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px; margin-bottom: 8px; cursor: pointer; }
        .file-item:hover { background: rgba(233, 69, 96, 0.2); }
        .file-item.selected { background: rgba(233, 69, 96, 0.3); border: 1px solid #e94560; }
        .file-item input { margin-right: 10px; accent-color: #e94560; }
        .file-name { flex: 1; font-size: 0.9em; word-break: break-all; }
        .file-size { font-size: 0.8em; color: #888; }
        .main-content { flex: 1; display: flex; flex-direction: column; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .header h1 { color: #e94560; }
        .mode-toggle { display: flex; gap: 5px; }
        .mode-btn { padding: 8px 16px; border: 1px solid #e94560; background: transparent; color: #fff; border-radius: 20px; cursor: pointer; font-size: 0.85em; transition: 0.3s; }
        .mode-btn:hover { background: rgba(233, 69, 96, 0.2); }
        .mode-btn.active { background: linear-gradient(135deg, #e94560, #ff6b6b); border-color: transparent; }
        .selected-files { background: rgba(233, 69, 96, 0.1); padding: 10px 15px; border-radius: 8px; margin-bottom: 15px; }
        .quick-queries { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }
        .quick-query { background: rgba(233, 69, 96, 0.2); border: 1px solid rgba(233, 69, 96, 0.4); padding: 6px 12px; border-radius: 15px; cursor: pointer; color: #fff; font-size: 0.85em; }
        .quick-query:hover { background: rgba(233, 69, 96, 0.4); }
        .quick-query.web { background: rgba(100, 200, 255, 0.2); border-color: rgba(100, 200, 255, 0.4); }
        .quick-query.web:hover { background: rgba(100, 200, 255, 0.4); }
        .chat-area { flex: 1; background: rgba(0,0,0,0.2); border-radius: 15px; padding: 20px; overflow-y: auto; margin-bottom: 20px; }
        .message { margin-bottom: 20px; }
        .message.user { text-align: right; }
        .message.user .bubble { background: linear-gradient(135deg, #e94560, #ff6b6b); display: inline-block; padding: 12px 18px; border-radius: 18px 18px 4px 18px; max-width: 70%; }
        .message.assistant .bubble { background: rgba(255,255,255,0.1); padding: 15px 20px; border-radius: 18px; max-width: 85%; border-left: 3px solid #e94560; line-height: 1.6; white-space: pre-wrap; }
        .message.assistant .bubble.web-result { border-left-color: #64c8ff; }
        .script-info { font-size: 0.75em; color: #888; margin-top: 8px; }
        .input-area { display: flex; gap: 10px; }
        .input-area textarea { flex: 1; background: rgba(255,255,255,0.1); border: 1px solid rgba(233, 69, 96, 0.3); border-radius: 12px; padding: 15px; color: #fff; font-size: 1em; resize: none; height: 60px; }
        .input-area textarea:focus { outline: none; border-color: #e94560; }
        .input-area button { background: linear-gradient(135deg, #e94560, #ff6b6b); border: none; border-radius: 12px; padding: 0 25px; color: #fff; font-weight: bold; cursor: pointer; }
        .input-area button.web-btn { background: linear-gradient(135deg, #64c8ff, #36a5eb); }
        .input-area button:disabled { opacity: 0.5; }
        .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: #fff; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>Data Files</h2>
        <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
            <div>Drop CSV/Excel files here</div>
            <div style="margin-top: 10px; font-size: 0.9em; color: #888;">or click to upload</div>
        </div>
        <input type="file" id="fileInput" multiple accept=".csv,.xlsx,.xls" style="display: none;" onchange="uploadFiles(this.files)">
        <div class="file-list" id="fileList">Loading files...</div>
    </div>
    <div class="main-content">
        <div class="header">
            <h1>AI Data Analyst</h1>
            <div class="mode-toggle">
                <button class="mode-btn active" id="dataBtn" onclick="setMode('data')">Data Analysis</button>
                <button class="mode-btn" id="webBtn" onclick="setMode('web')">Web Search</button>
            </div>
        </div>
        <div class="selected-files" id="selectedFiles">No files selected - Select files from the sidebar</div>
        <div class="quick-queries" id="quickQueries">
            <span class="quick-query" onclick="setQuery('summary')">Summary</span>
            <span class="quick-query" onclick="setQuery('top performers')">Top Performers</span>
            <span class="quick-query" onclick="setQuery('compare categories')">Compare</span>
            <span class="quick-query" onclick="setQuery('trends over time')">Trends</span>
        </div>
        <div class="chat-area" id="chatArea">
            <div class="message assistant">
                <div class="bubble">Welcome! I'm your AI Assistant.

Data Analysis: Select files and ask questions
Web Search: Click "Web Search" to search the internet</div>
            </div>
        </div>
        <div class="input-area">
            <textarea id="queryInput" placeholder="Ask anything..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();submitQuery();}"></textarea>
            <button id="submitBtn" onclick="submitQuery()">Analyze</button>
        </div>
    </div>
    <script>
    var selectedFiles = [];
    var currentMode = 'data';
    var fileData = {};

    function setMode(mode) {
        currentMode = mode;
        document.getElementById('dataBtn').className = 'mode-btn' + (mode === 'data' ? ' active' : '');
        document.getElementById('webBtn').className = 'mode-btn' + (mode === 'web' ? ' active' : '');
        var btn = document.getElementById('submitBtn');
        btn.textContent = mode === 'web' ? 'Search' : 'Analyze';
        btn.className = mode === 'web' ? 'web-btn' : '';
        document.getElementById('selectedFiles').style.display = mode === 'web' ? 'none' : 'block';
    }

    function loadFiles() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/api/files', true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var files = JSON.parse(xhr.responseText);
                var html = files.length === 0 ? '<div style="color:#888;padding:10px;">No files uploaded</div>' : '';
                for (var i = 0; i < files.length; i++) {
                    var f = files[i];
                    var sel = selectedFiles.indexOf(f.name) >= 0;
                    html += '<div class="file-item'+(sel?' selected':'')+'" onclick="toggleFile(\\''+f.name+'\\')">';
                    html += '<input type="checkbox"'+(sel?' checked':'')+'><span class="file-name">'+f.name+'</span></div>';
                }
                document.getElementById('fileList').innerHTML = html;
                updateSelected();
            }
        };
        xhr.send();
    }

    function toggleFile(name) {
        var idx = selectedFiles.indexOf(name);
        if (idx >= 0) selectedFiles.splice(idx, 1);
        else selectedFiles.push(name);
        loadFiles();
    }

    function updateSelected() {
        var el = document.getElementById('selectedFiles');
        el.textContent = selectedFiles.length === 0 ? 'No files selected' : 'Selected: ' + selectedFiles.join(', ');
    }

    function uploadFiles(files) {
        for (var i = 0; i < files.length; i++) {
            var reader = new FileReader();
            reader.onload = (function(file) {
                return function(e) {
                    var formData = new FormData();
                    formData.append('file', file);
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '/api/upload', true);
                    xhr.onreadystatechange = function() { if (xhr.readyState === 4) loadFiles(); };
                    xhr.send(formData);
                };
            })(files[i]);
            reader.readAsText(files[i]);
        }
    }

    function setQuery(q) { document.getElementById('queryInput').value = q; }

    function submitQuery() {
        var query = document.getElementById('queryInput').value.trim();
        if (!query) return;
        if (currentMode === 'data' && selectedFiles.length === 0) {
            alert('Please select a file first');
            return;
        }
        var btn = document.getElementById('submitBtn');
        var chatArea = document.getElementById('chatArea');
        chatArea.innerHTML += '<div class="message user"><div class="bubble">'+query+'</div></div>';
        chatArea.innerHTML += '<div class="message assistant" id="loadingMsg"><div class="bubble'+(currentMode==='web'?' web-result':'')+'">Processing... <span class="loading"></span></div></div>';
        btn.disabled = true;
        document.getElementById('queryInput').value = '';

        var xhr = new XMLHttpRequest();
        xhr.open('POST', currentMode === 'web' ? '/api/web-search' : '/api/analyze', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                document.getElementById('loadingMsg').remove();
                var data = JSON.parse(xhr.responseText);
                var result = data.result || data.error || 'No response';
                chatArea.innerHTML += '<div class="message assistant"><div class="bubble'+(currentMode==='web'?' web-result':'')+'">'+result+'</div></div>';
                chatArea.scrollTop = chatArea.scrollHeight;
                btn.disabled = false;
            }
        };
        xhr.send(JSON.stringify({query: query, files: selectedFiles}));
    }

    var uploadZone = document.getElementById('uploadZone');
    uploadZone.ondragover = function(e) { e.preventDefault(); };
    uploadZone.ondrop = function(e) { e.preventDefault(); uploadFiles(e.dataTransfer.files); };
    loadFiles();
    </script>
</body>
</html>'''


def call_openanalyst_api(prompt, system_message="You are a data analyst expert."):
    """Call OpenAnalyst API"""
    if not OPENANALYST_API_KEY:
        return "Error: OpenAnalyst API key not configured"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENANALYST_API_KEY}"
    }

    payload = {
        "model": OPENANALYST_MODEL,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(OPENANALYST_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0].get("message", {}).get("content", "No response")
        return "No response generated"
    except Exception as e:
        return f"API Error: {str(e)}"


def call_perplexity_api(query):
    """Call Perplexity API for web search"""
    if not PERPLEXITY_API_KEY:
        return "Error: Perplexity API key not configured"

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": "Provide accurate, well-sourced information from the web."},
            {"role": "user", "content": query}
        ],
        "max_tokens": 2048
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    except Exception as e:
        return f"Perplexity API Error: {str(e)}"


@app.route('/')
def index():
    return HTML_TEMPLATE


@app.route('/api/files')
def list_files():
    return jsonify([{"name": name, "size": len(data)} for name, data in uploaded_files.items()])


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename:
        uploaded_files[file.filename] = file.read().decode('utf-8', errors='ignore')
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid file'}), 400


@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    query = data.get('query', '')
    files = data.get('files', [])

    if not query or not files:
        return jsonify({'error': 'Missing query or files'})

    # Build context from files
    context = ""
    for filename in files:
        if filename in uploaded_files:
            try:
                df = pd.read_csv(StringIO(uploaded_files[filename]))
                context += f"\\n--- {filename} ---\\n"
                context += f"Columns: {list(df.columns)}\\n"
                context += f"Shape: {df.shape}\\n"
                context += f"Sample:\\n{df.head(20).to_string()}\\n"
                context += f"Stats:\\n{df.describe().to_string()}\\n"
            except:
                context += f"\\n{filename}: Could not parse\\n"

    prompt = f"Data:\\n{context}\\n\\nQuestion: {query}"
    result = call_openanalyst_api(prompt)
    return jsonify({'result': result})


@app.route('/api/web-search', methods=['POST'])
def web_search():
    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'No query'})
    result = call_perplexity_api(query)
    return jsonify({'result': result})


# Vercel handler
app = app
