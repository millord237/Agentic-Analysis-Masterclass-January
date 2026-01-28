# Agentic Analysis Masterclass - Project Guide

## Auto-Setup Instructions

When this project is first opened, run the setup:

```bash
pip install -r requirements.txt && python app.py
```

## Project Overview

This is an AI-powered data analysis web app that runs on **http://localhost:3000**

### Key Files:
- `app.py` - Main Flask application with embedded UI (HTML/CSS/JS)
- `data/` - Folder for CSV/Excel data files
- `requirements.txt` - Python dependencies

### Features:
- Upload CSV/Excel files via drag-and-drop
- Local intelligent data analysis (no API required)
- Optional API mode with OpenAnalyst integration
- Multi-file selection for unified analysis

### Running the App:
```bash
python app.py
```
Then open http://localhost:3000

### Environment Variables (Optional for API mode):
```
ANTHROPIC_BASE_URL=https://api.openanalyst.com
ANTHROPIC_AUTH_TOKEN=your-api-key
```

## Analysis Capabilities

The app can answer queries like:
- "summary" - Full data overview
- "top brands/products" - Find top performers
- "compare regions" - Compare categories
- "trends" - Time-based patterns
- "profit analysis" - Profitability insights
