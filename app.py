"""
Simple Data Analysis Web App - Local AI Analysis Engine
"""
import os
import json
import pandas as pd
import numpy as np
from flask import Flask, render_template_string, request, jsonify
import requests
import re

app = Flask(__name__)

# Configuration
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
API_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.openanalyst.com")
API_KEY = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")

# Ensure data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Analysis App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; height: 100vh; display: flex; }

        .sidebar { width: 280px; background: #16213e; padding: 20px; border-right: 1px solid #0f3460; display: flex; flex-direction: column; }
        .sidebar h2 { color: #e94560; margin-bottom: 20px; font-size: 18px; }
        .upload-zone { border: 2px dashed #0f3460; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 20px; cursor: pointer; transition: all 0.3s; }
        .upload-zone:hover { border-color: #e94560; background: rgba(233, 69, 96, 0.1); }
        .upload-zone input { display: none; }

        .file-list { flex: 1; overflow-y: auto; }
        .file-item { display: flex; align-items: center; padding: 10px; margin: 5px 0; background: #0f3460; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
        .file-item:hover { background: #1a4a7a; }
        .file-item.selected { background: #e94560; }
        .file-item input { margin-right: 10px; }
        .file-name { flex: 1; font-size: 13px; word-break: break-all; }
        .file-size { font-size: 11px; color: #888; }

        .main { flex: 1; display: flex; flex-direction: column; }
        .header { padding: 20px; background: #16213e; border-bottom: 1px solid #0f3460; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; color: #e94560; }
        .mode-toggle { display: flex; gap: 10px; }
        .mode-btn { padding: 8px 16px; border: 1px solid #0f3460; background: transparent; color: #888; border-radius: 6px; cursor: pointer; font-size: 12px; }
        .mode-btn.active { background: #e94560; color: white; border-color: #e94560; }

        .content { flex: 1; display: flex; flex-direction: column; padding: 20px; overflow: hidden; }

        .selected-files { margin-bottom: 15px; padding: 10px; background: #16213e; border-radius: 8px; }
        .selected-files span { display: inline-block; background: #e94560; padding: 4px 10px; border-radius: 4px; margin: 3px; font-size: 12px; }

        .chat-area { flex: 1; display: flex; flex-direction: column; background: #16213e; border-radius: 8px; overflow: hidden; }
        .messages { flex: 1; overflow-y: auto; padding: 20px; }
        .message { margin-bottom: 15px; padding: 12px 16px; border-radius: 8px; max-width: 85%; }
        .message.user { background: #e94560; margin-left: auto; }
        .message.assistant { background: #0f3460; }
        .message pre { white-space: pre-wrap; font-family: inherit; margin: 0; line-height: 1.5; }

        .input-area { display: flex; padding: 15px; background: #0f3460; gap: 10px; }
        .input-area textarea { flex: 1; padding: 12px; border: none; border-radius: 6px; background: #1a1a2e; color: #eee; resize: none; font-family: inherit; font-size: 14px; }
        .input-area textarea:focus { outline: 2px solid #e94560; }
        .input-area button { padding: 12px 24px; background: #e94560; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: all 0.2s; }
        .input-area button:hover { background: #ff6b6b; }
        .input-area button:disabled { background: #666; cursor: not-allowed; }

        .loading { display: inline-block; width: 20px; height: 20px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>Data Files</h2>
        <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" accept=".csv,.xlsx,.xls" multiple onchange="uploadFiles(this.files)">
            <p>Click or drag files here</p>
            <p style="font-size: 12px; color: #888; margin-top: 5px;">CSV, Excel supported</p>
        </div>
        <div class="file-list" id="fileList"></div>
    </div>

    <div class="main">
        <div class="header">
            <h1>AI Data Analyst</h1>
            <div class="mode-toggle">
                <button class="mode-btn active" id="localBtn" onclick="setMode('local')">Local Analysis</button>
                <button class="mode-btn" id="apiBtn" onclick="setMode('api')">API Mode</button>
            </div>
        </div>
        <div class="content">
            <div class="selected-files" id="selectedFiles">
                <strong>Selected:</strong> <span style="background: #666;">None - Select files from sidebar</span>
            </div>
            <div class="chat-area">
                <div class="messages" id="messages">
                    <div class="message assistant">
                        <pre>Welcome! Upload data files and select them from the sidebar.

Ask me anything:
- "summary" - Get full data overview
- "top brands/products/regions" - Find top performers
- "compare X vs Y" - Compare categories
- "trends" - Analyze patterns over time
- "profit analysis" - Profitability insights
- Or ask any custom question!

Select files and start asking questions.</pre>
                    </div>
                </div>
                <div class="input-area">
                    <textarea id="userInput" placeholder="Ask about your data..." rows="2" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); analyze(); }"></textarea>
                    <button id="analyzeBtn" onclick="analyze()">Analyze</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedFiles = new Set();
        let analysisMode = 'local';

        loadFiles();

        function setMode(mode) {
            analysisMode = mode;
            document.getElementById('localBtn').classList.toggle('active', mode === 'local');
            document.getElementById('apiBtn').classList.toggle('active', mode === 'api');
        }

        async function loadFiles() {
            const res = await fetch('/api/files');
            const files = await res.json();
            const list = document.getElementById('fileList');
            list.innerHTML = files.map(f => `
                <div class="file-item ${selectedFiles.has(f.name) ? 'selected' : ''}" onclick="toggleFile('${f.name}', this)">
                    <input type="checkbox" ${selectedFiles.has(f.name) ? 'checked' : ''} onclick="event.stopPropagation(); toggleFile('${f.name}', this.parentElement)">
                    <span class="file-name">${f.name}</span>
                    <span class="file-size">${formatSize(f.size)}</span>
                </div>
            `).join('');
            updateSelectedDisplay();
        }

        function toggleFile(name, el) {
            if (selectedFiles.has(name)) {
                selectedFiles.delete(name);
                el.classList.remove('selected');
                el.querySelector('input').checked = false;
            } else {
                selectedFiles.add(name);
                el.classList.add('selected');
                el.querySelector('input').checked = true;
            }
            updateSelectedDisplay();
        }

        function updateSelectedDisplay() {
            const div = document.getElementById('selectedFiles');
            if (selectedFiles.size === 0) {
                div.innerHTML = '<strong>Selected:</strong> <span style="background: #666;">None - Select files from sidebar</span>';
            } else {
                div.innerHTML = '<strong>Selected:</strong> ' + Array.from(selectedFiles).map(f => `<span>${f}</span>`).join('');
            }
        }

        async function uploadFiles(files) {
            for (let file of files) {
                const formData = new FormData();
                formData.append('file', file);
                await fetch('/api/upload', { method: 'POST', body: formData });
            }
            loadFiles();
            addMessage('assistant', `Uploaded ${files.length} file(s) successfully!`);
        }

        async function analyze() {
            const input = document.getElementById('userInput');
            const btn = document.getElementById('analyzeBtn');
            const query = input.value.trim();

            if (!query) return;
            if (selectedFiles.size === 0) {
                addMessage('assistant', 'Please select at least one file from the sidebar first.');
                return;
            }

            addMessage('user', query);
            input.value = '';
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span>';

            const thinkingId = addMessage('assistant', 'Analyzing your data...');

            try {
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        files: Array.from(selectedFiles),
                        query: query,
                        mode: analysisMode
                    })
                });
                const data = await res.json();
                document.getElementById(thinkingId).remove();

                if (data.error) {
                    addMessage('assistant', 'Error: ' + data.error);
                } else {
                    addMessage('assistant', data.response);
                }
            } catch (err) {
                document.getElementById(thinkingId).remove();
                addMessage('assistant', 'Error: ' + err.message);
            }

            btn.disabled = false;
            btn.innerHTML = 'Analyze';
        }

        function addMessage(role, text) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            div.id = 'msg-' + Date.now();
            div.innerHTML = `<pre>${escapeHtml(text)}</pre>`;
            document.getElementById('messages').appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
            return div.id;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function formatSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }

        document.querySelector('.upload-zone').addEventListener('dragover', e => {
            e.preventDefault();
            e.currentTarget.style.borderColor = '#e94560';
        });
        document.querySelector('.upload-zone').addEventListener('dragleave', e => {
            e.currentTarget.style.borderColor = '#0f3460';
        });
        document.querySelector('.upload-zone').addEventListener('drop', e => {
            e.preventDefault();
            e.currentTarget.style.borderColor = '#0f3460';
            uploadFiles(e.dataTransfer.files);
        });
    </script>
</body>
</html>
"""

def clean_numeric(series):
    """Clean numeric columns by removing $, commas, % etc."""
    if series.dtype == 'object':
        cleaned = series.astype(str).str.replace(r'[\$,\"%]', '', regex=True).str.strip()
        try:
            return pd.to_numeric(cleaned, errors='coerce')
        except:
            return series
    return series

def load_dataframe(filepath):
    """Load a dataframe and clean it."""
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)

    # Clean numeric columns
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if it looks numeric
            sample = df[col].dropna().head(10).astype(str)
            if sample.str.contains(r'^\s*[\$]?[\d,]+\.?\d*\s*%?\s*$', regex=True).mean() > 0.5:
                df[col + '_clean'] = clean_numeric(df[col])

    return df

def analyze_locally(dataframes, query):
    """Perform intelligent local analysis based on the query."""
    query_lower = query.lower()
    results = []

    for filename, df in dataframes.items():
        result = f"\n{'='*50}\nFILE: {filename}\n{'='*50}\n"

        # Basic info
        result += f"Rows: {len(df):,} | Columns: {len(df.columns)}\n"

        # Detect numeric columns
        numeric_cols = []
        for col in df.columns:
            if '_clean' in col:
                continue
            clean_col = col + '_clean'
            if clean_col in df.columns:
                numeric_cols.append((col, clean_col))
            elif df[col].dtype in ['int64', 'float64']:
                numeric_cols.append((col, col))

        # Detect categorical columns
        cat_cols = [col for col in df.columns if df[col].dtype == 'object' and '_clean' not in col]

        # SUMMARY / OVERVIEW
        if any(word in query_lower for word in ['summary', 'overview', 'describe', 'info', 'about']):
            result += f"\nCOLUMNS: {', '.join(df.columns[:15])}"
            if len(df.columns) > 15:
                result += f" ... (+{len(df.columns)-15} more)"

            result += "\n\nNUMERIC SUMMARY:\n"
            for display_col, data_col in numeric_cols[:6]:
                series = df[data_col].dropna()
                if len(series) > 0:
                    result += f"  {display_col}: Sum={series.sum():,.2f}, Avg={series.mean():,.2f}, Min={series.min():,.2f}, Max={series.max():,.2f}\n"

            result += "\nCATEGORICAL BREAKDOWN:\n"
            for col in cat_cols[:5]:
                unique = df[col].nunique()
                top = df[col].value_counts().head(3)
                result += f"  {col}: {unique} unique values. Top: {', '.join([f'{k}({v})' for k,v in top.items()])}\n"

        # TOP / BEST / HIGHEST
        elif any(word in query_lower for word in ['top', 'best', 'highest', 'most', 'largest', 'leading']):
            # Find what to group by
            group_col = None
            for col in cat_cols:
                col_lower = col.lower()
                if any(term in query_lower for term in [col_lower, col_lower.replace(' ', ''), col_lower[:4]]):
                    group_col = col
                    break
            if not group_col and cat_cols:
                # Try to find relevant column
                for col in cat_cols:
                    if any(term in col.lower() for term in ['brand', 'product', 'name', 'category', 'region', 'retailer']):
                        group_col = col
                        break
                if not group_col:
                    group_col = cat_cols[0]

            # Find metric column
            metric_col = None
            for display_col, data_col in numeric_cols:
                col_lower = display_col.lower()
                if any(term in col_lower for term in ['sales', 'revenue', 'total', 'profit', 'amount']):
                    metric_col = (display_col, data_col)
                    break
            if not metric_col and numeric_cols:
                metric_col = numeric_cols[0]

            if group_col and metric_col:
                grouped = df.groupby(group_col)[metric_col[1]].sum().sort_values(ascending=False).head(10)
                result += f"\nTOP 10 {group_col.upper()} BY {metric_col[0].upper()}:\n"
                for i, (name, value) in enumerate(grouped.items(), 1):
                    pct = (value / grouped.sum()) * 100
                    result += f"  {i}. {name}: {value:,.2f} ({pct:.1f}%)\n"

        # COMPARE
        elif any(word in query_lower for word in ['compare', 'versus', 'vs', 'difference', 'between']):
            for col in cat_cols:
                if df[col].nunique() <= 10:
                    result += f"\nCOMPARISON BY {col.upper()}:\n"
                    for display_col, data_col in numeric_cols[:4]:
                        grouped = df.groupby(col)[data_col].agg(['sum', 'mean', 'count'])
                        result += f"\n  {display_col}:\n"
                        for idx, row in grouped.iterrows():
                            result += f"    {idx}: Total={row['sum']:,.2f}, Avg={row['mean']:,.2f}, Count={int(row['count'])}\n"
                    break

        # TREND / TIME / PATTERN
        elif any(word in query_lower for word in ['trend', 'time', 'pattern', 'over time', 'monthly', 'daily', 'growth']):
            # Find date column
            date_col = None
            for col in df.columns:
                if any(term in col.lower() for term in ['date', 'time', 'day', 'month', 'year']):
                    date_col = col
                    break

            if date_col:
                try:
                    df['_date'] = pd.to_datetime(df[date_col], errors='coerce')
                    df['_month'] = df['_date'].dt.to_period('M')

                    result += f"\nTRENDS OVER TIME (by {date_col}):\n"
                    for display_col, data_col in numeric_cols[:3]:
                        monthly = df.groupby('_month')[data_col].sum()
                        if len(monthly) > 1:
                            result += f"\n  {display_col} by Month:\n"
                            for period, value in monthly.tail(12).items():
                                result += f"    {period}: {value:,.2f}\n"
                except:
                    result += "\nCould not parse date column for trend analysis.\n"
            else:
                result += "\nNo date column found for trend analysis.\n"

        # PROFIT / MARGIN
        elif any(word in query_lower for word in ['profit', 'margin', 'profitable', 'earnings']):
            profit_cols = [(d, c) for d, c in numeric_cols if any(term in d.lower() for term in ['profit', 'margin', 'earning'])]

            if profit_cols:
                result += "\nPROFITABILITY ANALYSIS:\n"
                for display_col, data_col in profit_cols:
                    series = df[data_col].dropna()
                    result += f"\n  {display_col}:\n"
                    result += f"    Total: {series.sum():,.2f}\n"
                    result += f"    Average: {series.mean():,.2f}\n"
                    result += f"    Min: {series.min():,.2f}\n"
                    result += f"    Max: {series.max():,.2f}\n"

                # By category if available
                for col in cat_cols[:2]:
                    if df[col].nunique() <= 15:
                        result += f"\n  By {col}:\n"
                        for display_col, data_col in profit_cols[:1]:
                            grouped = df.groupby(col)[data_col].sum().sort_values(ascending=False)
                            for name, value in grouped.items():
                                result += f"    {name}: {value:,.2f}\n"
            else:
                result += "\nNo profit/margin columns found.\n"

        # REGION / LOCATION / GEOGRAPHY
        elif any(word in query_lower for word in ['region', 'location', 'geography', 'state', 'city', 'area']):
            geo_cols = [col for col in cat_cols if any(term in col.lower() for term in ['region', 'state', 'city', 'country', 'location', 'area'])]

            if geo_cols:
                result += "\nGEOGRAPHIC ANALYSIS:\n"
                for geo_col in geo_cols[:2]:
                    result += f"\n  By {geo_col}:\n"
                    for display_col, data_col in numeric_cols[:2]:
                        grouped = df.groupby(geo_col)[data_col].sum().sort_values(ascending=False).head(10)
                        result += f"\n    {display_col}:\n"
                        for name, value in grouped.items():
                            result += f"      {name}: {value:,.2f}\n"
            else:
                result += "\nNo geographic columns found.\n"

        # DEFAULT - General analysis
        else:
            result += "\nDATA ANALYSIS:\n"

            # Show key metrics
            result += "\nKey Metrics:\n"
            for display_col, data_col in numeric_cols[:5]:
                series = df[data_col].dropna()
                if len(series) > 0:
                    result += f"  {display_col}: Total={series.sum():,.2f}, Avg={series.mean():,.2f}\n"

            # Show breakdown by first categorical
            if cat_cols:
                col = cat_cols[0]
                if df[col].nunique() <= 15:
                    result += f"\nBreakdown by {col}:\n"
                    if numeric_cols:
                        display_col, data_col = numeric_cols[0]
                        grouped = df.groupby(col)[data_col].sum().sort_values(ascending=False)
                        for name, value in grouped.items():
                            result += f"  {name}: {value:,.2f}\n"

        results.append(result)

    return '\n'.join(results)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/files')
def list_files():
    """List all data files."""
    files = []
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
    """Upload a file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filepath = os.path.join(DATA_FOLDER, file.filename)
    file.save(filepath)
    return jsonify({'success': True, 'filename': file.filename})

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """Analyze selected files."""
    data = request.json
    files = data.get('files', [])
    query = data.get('query', '')
    mode = data.get('mode', 'local')

    if not files:
        return jsonify({'error': 'No files selected'})

    # Load all dataframes
    dataframes = {}
    for filename in files:
        filepath = os.path.join(DATA_FOLDER, filename)
        if os.path.exists(filepath):
            try:
                dataframes[filename] = load_dataframe(filepath)
            except Exception as e:
                return jsonify({'error': f'Error loading {filename}: {str(e)}'})

    # Try API mode first if selected, fallback to local
    if mode == 'api':
        try:
            response = call_ai_api(dataframes, query)
            return jsonify({'response': response})
        except Exception as e:
            # Fallback to local
            response = analyze_locally(dataframes, query)
            response = f"[API unavailable, using local analysis]\n{response}"
            return jsonify({'response': response})
    else:
        # Local analysis
        response = analyze_locally(dataframes, query)
        return jsonify({'response': response})

def call_ai_api(dataframes, user_query):
    """Call the OpenAnalyst API."""
    context_text = ""
    for filename, df in dataframes.items():
        context_text += f"\n--- {filename} ---\n"
        context_text += f"Rows: {len(df)}, Columns: {list(df.columns)}\n"
        context_text += f"Sample:\n{df.head(10).to_string()}\n"
        context_text += f"Stats:\n{df.describe(include='all').to_string()}\n"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "system": "You are a data analyst. Provide clear, specific insights with numbers.",
        "messages": [{"role": "user", "content": f"Data:\n{context_text}\n\nQuestion: {user_query}"}]
    }

    response = requests.post(f"{API_BASE_URL}/v1/messages", headers=headers, json=payload, timeout=120)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")

    return response.json()['content'][0]['text']

if __name__ == '__main__':
    print("=" * 50)
    print("Data Analysis App Starting...")
    print(f"Data folder: {DATA_FOLDER}")
    print("Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)
