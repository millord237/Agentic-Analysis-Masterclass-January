"""
AI Data Analysis Web App with Web Search
Executes Python scripts based on user queries using AI API
"""
from flask import Flask, request, jsonify
import os
import subprocess
import sys
import json

app = Flask(__name__)

# Configuration
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
SCRIPTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')

# Ensure data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return '''<!DOCTYPE html>
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
            <span class="quick-query" onclick="setQuery('top brands by sales')">Top Brands</span>
            <span class="quick-query" onclick="setQuery('compare regions')">Compare Regions</span>
            <span class="quick-query" onclick="setQuery('sales trends over time')">Trends</span>
            <span class="quick-query" onclick="setQuery('profit analysis')">Profits</span>
        </div>
        <div class="chat-area" id="chatArea">
            <div class="message assistant">
                <div class="bubble">Welcome! I'm your AI Assistant.

<b>Data Analysis Mode:</b>
- Select files from sidebar, then ask questions
- "summary", "top brands", "compare", "trends", "profits"

<b>Web Search Mode:</b>
- Click "Web Search" to search the internet
- Get real-time information with sources</div>
            </div>
        </div>
        <div class="input-area">
            <textarea id="queryInput" placeholder="Ask anything about your data..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();submitQuery();}"></textarea>
            <button id="submitBtn" onclick="submitQuery()">Analyze</button>
        </div>
    </div>

    <script>
    var selectedFiles = [];
    var currentMode = 'data';

    function setMode(mode) {
        currentMode = mode;
        document.getElementById('dataBtn').className = 'mode-btn' + (mode === 'data' ? ' active' : '');
        document.getElementById('webBtn').className = 'mode-btn' + (mode === 'web' ? ' active' : '');

        var btn = document.getElementById('submitBtn');
        var input = document.getElementById('queryInput');
        var filesDiv = document.getElementById('selectedFiles');
        var quickDiv = document.getElementById('quickQueries');

        if (mode === 'web') {
            btn.textContent = 'Search';
            btn.className = 'web-btn';
            input.placeholder = 'Search the web...';
            filesDiv.style.display = 'none';
            quickDiv.innerHTML = '<span class="quick-query web" onclick="setQuery(\\x27latest AI news\\x27)">AI News</span>' +
                '<span class="quick-query web" onclick="setQuery(\\x27python best practices 2024\\x27)">Python Tips</span>' +
                '<span class="quick-query web" onclick="setQuery(\\x27data science trends\\x27)">Data Science</span>' +
                '<span class="quick-query web" onclick="setQuery(\\x27machine learning tutorials\\x27)">ML Tutorials</span>';
        } else {
            btn.textContent = 'Analyze';
            btn.className = '';
            input.placeholder = 'Ask anything about your data...';
            filesDiv.style.display = 'block';
            quickDiv.innerHTML = '<span class="quick-query" onclick="setQuery(\\x27summary\\x27)">Summary</span>' +
                '<span class="quick-query" onclick="setQuery(\\x27top brands by sales\\x27)">Top Brands</span>' +
                '<span class="quick-query" onclick="setQuery(\\x27compare regions\\x27)">Compare Regions</span>' +
                '<span class="quick-query" onclick="setQuery(\\x27sales trends over time\\x27)">Trends</span>' +
                '<span class="quick-query" onclick="setQuery(\\x27profit analysis\\x27)">Profits</span>';
        }
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function loadFiles() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/api/files', true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var files = JSON.parse(xhr.responseText);
                var html = '';
                if (files.length === 0) {
                    html = '<div style="color: #888; padding: 10px;">No files in data folder</div>';
                } else {
                    for (var i = 0; i < files.length; i++) {
                        var f = files[i];
                        var isSelected = selectedFiles.indexOf(f.name) >= 0;
                        html += '<div class="file-item' + (isSelected ? ' selected' : '') + '" onclick="toggleFile(\\x27'+f.name+'\\x27)">';
                        html += '<input type="checkbox"' + (isSelected ? ' checked' : '') + '>';
                        html += '<span class="file-name">' + f.name + '</span>';
                        html += '<span class="file-size">' + formatSize(f.size) + '</span>';
                        html += '</div>';
                    }
                }
                document.getElementById('fileList').innerHTML = html;
                updateSelected();
            }
        };
        xhr.send();
    }

    function toggleFile(name) {
        var idx = selectedFiles.indexOf(name);
        if (idx >= 0) {
            selectedFiles.splice(idx, 1);
        } else {
            selectedFiles.push(name);
        }
        loadFiles();
    }

    function updateSelected() {
        var el = document.getElementById('selectedFiles');
        if (selectedFiles.length === 0) {
            el.textContent = 'No files selected - Select files from the sidebar';
        } else {
            el.textContent = 'Selected: ' + selectedFiles.join(', ');
        }
    }

    function uploadFiles(files) {
        var uploaded = 0;
        for (var i = 0; i < files.length; i++) {
            var formData = new FormData();
            formData.append('file', files[i]);
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/upload', true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    uploaded++;
                    if (uploaded === files.length) {
                        loadFiles();
                    }
                }
            };
            xhr.send(formData);
        }
    }

    function setQuery(q) {
        document.getElementById('queryInput').value = q;
    }

    function submitQuery() {
        if (currentMode === 'web') {
            webSearch();
        } else {
            analyze();
        }
    }

    function analyze() {
        var query = document.getElementById('queryInput').value.trim();
        if (!query) return;
        if (selectedFiles.length === 0) {
            alert('Please select at least one data file from the sidebar');
            return;
        }

        var btn = document.getElementById('submitBtn');
        var chatArea = document.getElementById('chatArea');

        var userDiv = document.createElement('div');
        userDiv.className = 'message user';
        userDiv.innerHTML = '<div class="bubble">' + query.replace(/</g, '&lt;') + '</div>';
        chatArea.appendChild(userDiv);

        var loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant';
        loadingDiv.id = 'loadingMsg';
        loadingDiv.innerHTML = '<div class="bubble">Analyzing with AI... <span class="loading"></span></div>';
        chatArea.appendChild(loadingDiv);
        chatArea.scrollTop = chatArea.scrollHeight;

        btn.disabled = true;
        document.getElementById('queryInput').value = '';

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/analyze', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                var loading = document.getElementById('loadingMsg');
                if (loading) loading.remove();

                var result = '';
                var script = 'N/A';
                try {
                    var data = JSON.parse(xhr.responseText);
                    result = data.result || data.error || 'No response';
                    script = data.script || 'N/A';
                } catch(e) {
                    result = 'Error: ' + e.message;
                }

                var respDiv = document.createElement('div');
                respDiv.className = 'message assistant';
                respDiv.innerHTML = '<div class="bubble">' + result.replace(/</g, '&lt;') + '</div><div class="script-info">Script: ' + script + '</div>';
                chatArea.appendChild(respDiv);
                chatArea.scrollTop = chatArea.scrollHeight;
                btn.disabled = false;
            }
        };
        xhr.send(JSON.stringify({query: query, files: selectedFiles}));
    }

    function webSearch() {
        var query = document.getElementById('queryInput').value.trim();
        if (!query) return;

        var btn = document.getElementById('submitBtn');
        var chatArea = document.getElementById('chatArea');

        var userDiv = document.createElement('div');
        userDiv.className = 'message user';
        userDiv.innerHTML = '<div class="bubble">[Web Search] ' + query.replace(/</g, '&lt;') + '</div>';
        chatArea.appendChild(userDiv);

        var loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant';
        loadingDiv.id = 'loadingMsg';
        loadingDiv.innerHTML = '<div class="bubble web-result">Searching the web... <span class="loading"></span></div>';
        chatArea.appendChild(loadingDiv);
        chatArea.scrollTop = chatArea.scrollHeight;

        btn.disabled = true;
        document.getElementById('queryInput').value = '';

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/web-search', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                var loading = document.getElementById('loadingMsg');
                if (loading) loading.remove();

                var result = '';
                try {
                    var data = JSON.parse(xhr.responseText);
                    result = data.result || data.error || 'No response';
                } catch(e) {
                    result = 'Error: ' + e.message;
                }

                var respDiv = document.createElement('div');
                respDiv.className = 'message assistant';
                respDiv.innerHTML = '<div class="bubble web-result">' + result.replace(/</g, '&lt;') + '</div><div class="script-info">Source: Perplexity Web Search</div>';
                chatArea.appendChild(respDiv);
                chatArea.scrollTop = chatArea.scrollHeight;
                btn.disabled = false;
            }
        };
        xhr.send(JSON.stringify({query: query}));
    }

    // Drag and drop
    var uploadZone = document.getElementById('uploadZone');
    uploadZone.ondragover = function(e) { e.preventDefault(); this.style.background = 'rgba(233, 69, 96, 0.2)'; };
    uploadZone.ondragleave = function(e) { e.preventDefault(); this.style.background = ''; };
    uploadZone.ondrop = function(e) { e.preventDefault(); this.style.background = ''; uploadFiles(e.dataTransfer.files); };

    // Load files on start
    loadFiles();
    </script>
</body>
</html>'''


@app.route('/api/files')
def list_files():
    """List available data files"""
    files = []
    if os.path.exists(DATA_FOLDER):
        for f in os.listdir(DATA_FOLDER):
            if f.endswith(('.csv', '.xlsx', '.xls')):
                path = os.path.join(DATA_FOLDER, f)
                files.append({
                    'name': f,
                    'size': os.path.getsize(path)
                })
    return jsonify(sorted(files, key=lambda x: x['name']))


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a data file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file.filename.endswith(('.csv', '.xlsx', '.xls')):
        filepath = os.path.join(DATA_FOLDER, file.filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': file.filename})

    return jsonify({'error': 'Invalid file type'}), 400


def detect_query_type(query):
    """Detect the type of analysis needed based on query keywords"""
    query_lower = query.lower()

    if any(word in query_lower for word in ['summary', 'overview', 'describe', 'what is this', 'about']):
        return 'summary', 'summary_analysis.py'
    if any(word in query_lower for word in ['top', 'best', 'highest', 'most', 'largest', 'greatest', 'leading']):
        return 'top', 'top_analysis.py'
    if any(word in query_lower for word in ['compare', 'versus', 'vs', 'difference', 'between']):
        return 'compare', 'compare_analysis.py'
    if any(word in query_lower for word in ['trend', 'time', 'over time', 'growth', 'change', 'monthly', 'yearly', 'pattern']):
        return 'trend', 'trend_analysis.py'
    if any(word in query_lower for word in ['profit', 'margin', 'earnings', 'revenue', 'income', 'cost']):
        return 'profit', 'profit_analysis.py'
    if any(word in query_lower for word in ['region', 'location', 'geography', 'state', 'city', 'country', 'area']):
        return 'region', 'region_analysis.py'
    return 'custom', 'custom_query.py'


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze data using appropriate Python script"""
    data = request.json
    query = data.get('query', '')
    files = data.get('files', [])

    if not query:
        return jsonify({'error': 'No query provided', 'script': 'N/A'})

    if not files:
        return jsonify({'error': 'No files selected', 'script': 'N/A'})

    file_paths = [os.path.join(DATA_FOLDER, f) for f in files]

    for fp in file_paths:
        if not os.path.exists(fp):
            return jsonify({'error': 'File not found: ' + fp, 'script': 'N/A'})

    query_type, script_name = detect_query_type(query)
    script_path = os.path.join(SCRIPTS_FOLDER, script_name)

    if query_type == 'summary':
        cmd = [sys.executable, script_path] + file_paths
    else:
        cmd = [sys.executable, script_path, query] + file_paths

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        output = result.stdout.strip()
        if result.returncode != 0:
            error_msg = result.stderr or 'Script execution failed'
            return jsonify({'error': error_msg, 'script': script_name})

        try:
            output_data = json.loads(output)
            return jsonify({
                'result': output_data.get('result', output),
                'title': output_data.get('title', 'Analysis'),
                'success': output_data.get('success', True),
                'script': script_name
            })
        except json.JSONDecodeError:
            return jsonify({'result': output, 'script': script_name})

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Analysis timed out (2 min limit)', 'script': script_name})
    except Exception as e:
        return jsonify({'error': str(e), 'script': script_name})


@app.route('/api/web-search', methods=['POST'])
def web_search():
    """Perform web search using Perplexity API"""
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'No query provided'})

    script_path = os.path.join(SCRIPTS_FOLDER, 'web_search.py')
    cmd = [sys.executable, script_path, query]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        output = result.stdout.strip()
        if result.returncode != 0:
            error_msg = result.stderr or 'Web search failed'
            return jsonify({'error': error_msg})

        try:
            output_data = json.loads(output)
            return jsonify(output_data)
        except json.JSONDecodeError:
            return jsonify({'result': output})

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Web search timed out'})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    print("\n" + "="*50)
    print("  AI Data Analyst with Web Search")
    print("  Running on: http://localhost:3000")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=3000, debug=True)
