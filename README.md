# Agentic Analysis Masterclass (January)

AI-powered data analysis web app with local intelligent analysis engine.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENTIC ANALYSIS APP                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐      ┌──────────────────┐      ┌───────────────────┐    │
│   │   FRONTEND   │      │     BACKEND      │      │   DATA STORAGE    │    │
│   │  (Browser)   │◄────►│   (Flask API)    │◄────►│   (data/ folder)  │    │
│   └──────────────┘      └──────────────────┘      └───────────────────┘    │
│         │                       │                                           │
│         │                       ▼                                           │
│         │               ┌──────────────────┐                               │
│         │               │  ANALYSIS ENGINE │                               │
│         │               ├──────────────────┤                               │
│         │               │  ┌────────────┐  │                               │
│         │               │  │   LOCAL    │  │  ◄── Default (No API needed) │
│         │               │  │  ANALYSIS  │  │                               │
│         │               │  └────────────┘  │                               │
│         │               │        OR        │                               │
│         │               │  ┌────────────┐  │                               │
│         │               │  │  API MODE  │  │  ◄── Optional (OpenAnalyst)  │
│         │               │  │ (Fallback) │  │                               │
│         │               │  └────────────┘  │                               │
│         │               └──────────────────┘                               │
│         │                                                                   │
└─────────┴───────────────────────────────────────────────────────────────────┘
```

---

## User Flow

```
┌─────────────────┐
│   START         │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Clone Repo     │
│  git clone ...  │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Run Setup      │
│  python setup.py│
└────────┬────────┘
         ▼
┌─────────────────┐
│  App Starts     │
│  localhost:3000 │
└────────┬────────┘
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Upload Data    │────►│  Files saved to │
│  (CSV/Excel)    │     │  data/ folder   │
└────────┬────────┘     └─────────────────┘
         ▼
┌─────────────────┐
│  Select Files   │
│  from Sidebar   │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Ask Questions  │
│  in Chat Box    │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Get AI-Powered │
│  Insights       │
└────────┬────────┘
         ▼
┌─────────────────┐
│   END           │
└─────────────────┘
```

---

## Quick Start

### Option 1: Auto Setup (Recommended)

```bash
# Step 1: Clone the repository
git clone https://github.com/Anit-1to10x/Agentic-Analysis-Masterclass-January.git

# Step 2: Navigate to folder
cd Agentic-Analysis-Masterclass-January

# Step 3: Run auto-setup (installs deps + starts app)
python setup.py
```

### Option 2: Manual Setup

```bash
# Step 1: Clone the repository
git clone https://github.com/Anit-1to10x/Agentic-Analysis-Masterclass-January.git

# Step 2: Navigate to folder
cd Agentic-Analysis-Masterclass-January

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Start the app
python app.py
```

### Step 5: Open Browser

```
http://localhost:3000
```

---

## Features

| Feature | Description |
|---------|-------------|
| **File Upload** | Drag & drop CSV/Excel files |
| **Local Analysis** | Smart analysis without API (works offline) |
| **API Mode** | Optional OpenAnalyst API integration |
| **Multi-file** | Select multiple files for unified insights |
| **Interactive Chat** | Ask questions in natural language |

---

## Analysis Commands

```
┌────────────────────┬────────────────────────────────────┐
│     COMMAND        │           DESCRIPTION              │
├────────────────────┼────────────────────────────────────┤
│  summary           │  Full data overview with stats     │
│  top brands        │  Best performing products          │
│  top retailers     │  Top sellers by revenue            │
│  compare regions   │  Regional comparison               │
│  trends            │  Time-based patterns               │
│  profit analysis   │  Profitability breakdown           │
│  <any question>    │  Natural language query            │
└────────────────────┴────────────────────────────────────┘
```

---

## Project Structure

```
Agentic-Analysis-Masterclass-January/
│
├── app.py                 # Main Flask app (UI + Backend)
├── setup.py               # Auto-setup script
├── requirements.txt       # Python dependencies
├── CLAUDE.md              # Claude Code instructions
├── README.md              # This file
│
├── data/                  # Data files folder
│   ├── *.csv              # CSV data files
│   └── *.xlsx             # Excel data files
│
└── .claude/               # Claude Code settings
    └── settings.local.json
```

---

## Tech Stack

```
┌─────────────────────────────────────────────────┐
│                  TECH STACK                     │
├─────────────────────────────────────────────────┤
│                                                 │
│   Frontend:    HTML5 + CSS3 + JavaScript        │
│   Backend:     Python + Flask                   │
│   Analysis:    Pandas + NumPy                   │
│   API:         OpenAnalyst (Anthropic-style)    │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Environment Variables (Optional)

For API mode, set these environment variables:

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_BASE_URL = "https://api.openanalyst.com"
$env:ANTHROPIC_AUTH_TOKEN = "your-api-key"
```

**Linux/Mac:**
```bash
export ANTHROPIC_BASE_URL="https://api.openanalyst.com"
export ANTHROPIC_AUTH_TOKEN="your-api-key"
```

---

## Using with Claude Code

```
1. Clone the repo
2. Open folder in Claude Code: claude .
3. Say: "Run setup and start the app"
4. Claude will execute: python setup.py
5. Open http://localhost:3000
6. Start analyzing!
```

---

## License

MIT License

---

## Author

Created by **Anit** | Agentic Analysis Masterclass (January 2025)
